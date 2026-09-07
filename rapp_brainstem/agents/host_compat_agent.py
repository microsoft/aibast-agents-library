"""HostCompat -- make the Brainstem speak every agent-host dialect (Claude Code,
GitHub Copilot CLI, and the open Agent Skills layout) from ONE agent file,
without teaching the kernel any of it.

Why an agent and not a kernel feature: the kernel stays "engine, not experience".
Everything host-shaped (skills, plugins, slash commands / prompts, subagent
personas, hooks, MCP servers, instruction files, session transcripts) is a
cartridge you can drop in, delete, or replace.

Hosts are data, not code: each adapter below is a table of where that host keeps
things. Adding a host is adding an entry (or a JSON file via HOST_COMPAT_HOSTS).

What it does better than the originals:
  * One catalog across hosts. A skill installed for Copilot CLI is usable from a
    Brainstem chat, and vice versa. Duplicates (same folder reachable from two
    hosts) are collapsed.
  * Progressive disclosure that fits: a capped, cached catalog goes into the
    system prompt each turn so skills auto-trigger; bodies load on demand; the
    catalog degrades (full -> short -> names-only) before it drops anything.
  * Skills are first-class tools: action="promote" compiles any SKILL.md into a
    native <slug>_agent.py; action="export" turns any agent into a SKILL.md
    folder every host can read.
  * MCP servers from every host config are callable directly (stdio and
    streamable-HTTP), no host process required.
  * Local transcript search across BOTH hosts' session history (Claude Code
    ~/.claude/projects/*.jsonl, Copilot CLI ~/.copilot/session-state/*/events.jsonl)
    through an incremental SQLite FTS index -- "what did I tell Copilot about X
    last week" answered from the Brainstem.

Everything is stdlib-only. Every subprocess has a timeout. Paths handed in by the
model are confined to the skill/plugin directory they belong to.

Environment (all optional):
  HOST_COMPAT_CLAUDE_HOME     default ~/.claude
  HOST_COMPAT_COPILOT_HOME    default ~/.copilot
  HOST_COMPAT_PROJECT         project dir scanned for .claude/ .github/ .agents/ (default cwd)
  HOST_COMPAT_ROOTS           extra colon-separated dirs containing */SKILL.md
  HOST_COMPAT_HOSTS           JSON file with extra/override host adapters
  HOST_COMPAT_STORE           installed plugins + transcript index (default ~/.brainstem/host_compat)
  HOST_COMPAT_CONTEXT_CHARS   cap on the per-turn catalog (default 6000; 0 disables)
  HOST_COMPAT_TIMEOUT         default subprocess timeout seconds (default 120)
  HOST_COMPAT_TRANSCRIPT_DAYS how far back transcripts are indexed (default 30)
  HOST_COMPAT_INDEX_BUDGET    seconds of indexing a search call may spend (default 15)
"""

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@kody-w/host_compat_agent",
    "version": "1.0.0",
    "display_name": "Host Compat",
    "description": "Makes a Brainstem speak every agent-host dialect from one file: Claude Code, GitHub Copilot CLI and open Agent Skills — skills, plugins, slash commands/prompts, subagent personas, hooks, MCP servers, instruction files — plus cross-host search of your local Claude Code and Copilot CLI session transcripts.",
    "author": "kody-w",
    "tags": ["skills", "plugins", "claude-code", "copilot-cli", "agent-skills", "mcp", "hooks", "transcripts", "interop", "compat"],
    "category": "devtools",
    "quality_tier": "community",
    "requires_env": [],
    "dependencies": ["@rapp/basic_agent"],
}

import ast
import glob
import hashlib
import json
import os
import re
import shlex
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.request

try:
    from agents.basic_agent import BasicAgent
except ImportError:  # pragma: no cover - standalone / registry contract use
    try:
        from basic_agent import BasicAgent
    except ImportError:
        class BasicAgent:
            def __init__(self, name=None, metadata=None):
                self.name = getattr(self, "name", name or "BasicAgent")
                self.metadata = getattr(self, "metadata", metadata or {})

            def perform(self, **kwargs):
                return "Not implemented."

            def system_context(self):
                return None

            def to_tool(self):
                return {"type": "function", "function": {"name": self.name,
                        "description": self.metadata.get("description", ""),
                        "parameters": self.metadata.get("parameters", {"type": "object", "properties": {}})}}

# ── configuration ───────────────────────────────────────────────────────────

def _env(name, default):
    v = os.getenv(name)
    return v if v not in (None, "") else default


def _int_env(name, default):
    try:
        return int(_env(name, str(default)))
    except ValueError:
        return default


def _project_dir():
    return os.path.abspath(_env("HOST_COMPAT_PROJECT", os.getcwd()))


def _store_dir():
    return os.path.expanduser(_env("HOST_COMPAT_STORE", "~/.brainstem/host_compat"))


# ── host adapters (data, not code) ─────────────────────────────────────────
# Path templates use {home} (that host's home) and {project}. Globs allowed.

HOSTS = {
    "claude-code": {
        "display": "Claude Code",
        "home_env": "HOST_COMPAT_CLAUDE_HOME", "home": "~/.claude",
        "skills": ["{project}/.claude/skills", "{home}/skills"],
        "commands": [{"dir": "{project}/.claude/commands", "suffix": ".md"},
                     {"dir": "{home}/commands", "suffix": ".md"}],
        "agents": [{"dir": "{project}/.claude/agents", "suffix": ".md"},
                   {"dir": "{home}/agents", "suffix": ".md"}],
        "plugins": {"installed_json": "{home}/plugins/installed_plugins.json",
                    "dirs": ["{home}/plugins/cache/*/*/*"],
                    "manifests": [".claude-plugin/plugin.json", "plugin.json"],
                    "skills_subdir": "skills", "commands_subdir": "commands", "agents_subdir": "agents",
                    "hooks_files": ["hooks/hooks.json", "hooks.json"], "mcp_file": ".mcp.json"},
        "hooks": ["{project}/.claude/settings.json", "{project}/.claude/settings.local.json"],
        "mcp": [{"file": "{project}/.mcp.json", "key": "mcpServers"},
                {"file": "{home}/../.claude.json", "key": "mcpServers"}],
        "instructions": ["{project}/CLAUDE.md", "{project}/.claude/CLAUDE.md", "{home}/CLAUDE.md"],
        "transcripts": {"glob": "{home}/projects/*/*.jsonl", "format": "claude-jsonl"},
    },
    "copilot-cli": {
        "display": "GitHub Copilot CLI",
        "home_env": "HOST_COMPAT_COPILOT_HOME", "home": "~/.copilot",
        "skills": ["{project}/.github/skills", "{home}/skills"],
        "commands": [{"dir": "{project}/.github/prompts", "suffix": ".prompt.md"}],
        "agents": [{"dir": "{project}/.github/agents", "suffix": ".agent.md"},
                   {"dir": "{project}/.github/agents", "suffix": ".md"},
                   {"dir": "{home}/agents", "suffix": ".md"}],
        "plugins": {"installed_json": None,
                    "dirs": ["{home}/installed-plugins/*/*", "{home}/installed-plugins/_direct/*"],
                    "manifests": ["plugin.json", ".claude-plugin/plugin.json"],
                    "skills_subdir": "skills", "commands_subdir": "prompts", "agents_subdir": "agents",
                    "hooks_files": ["hooks/hooks.json", "hooks.json"], "mcp_file": ".mcp.json"},
        "hooks": ["{project}/.github/hooks/*.json", "{home}/hooks/*.json"],
        "mcp": [{"file": "{home}/mcp-config.json", "key": "mcpServers"},
                {"file": "{project}/.copilot/mcp-config.json", "key": "mcpServers"},
                {"file": "{project}/.vscode/mcp.json", "key": "servers"}],
        "instructions": ["{project}/AGENTS.md", "{project}/.github/copilot-instructions.md",
                         "{project}/.github/instructions/*.instructions.md"],
        "transcripts": {"glob": "{home}/session-state/*/events.jsonl", "format": "copilot-events"},
    },
    "agent-skills": {
        "display": "Open Agent Skills layout",
        "home_env": "HOST_COMPAT_AGENTS_HOME", "home": "~/.agents",
        "skills": ["{project}/.agents/skills", "{home}/skills"],
        "commands": [], "agents": [], "plugins": None, "hooks": [], "mcp": [],
        "instructions": ["{project}/AGENTS.md"], "transcripts": None,
    },
}


def _hosts():
    hosts = {k: dict(v) for k, v in HOSTS.items()}
    extra = _env("HOST_COMPAT_HOSTS", "")
    if extra and os.path.isfile(os.path.expanduser(extra)):
        try:
            for k, v in json.loads(_safe_read(os.path.expanduser(extra))).items():
                hosts.setdefault(k, {}).update(v)
        except ValueError:
            pass
    return hosts


def _host_home(host):
    return os.path.expanduser(_env(host.get("home_env", ""), host.get("home", "")))


def _fill(tpl, host):
    return os.path.normpath(os.path.expanduser(tpl.replace("{home}", _host_home(host)).replace("{project}", _project_dir())))


def _expand_paths(tpl, host):
    p = _fill(tpl, host)
    return sorted(glob.glob(p)) if any(ch in p for ch in "*?[") else [p]


# ── tiny YAML-subset frontmatter parser (no PyYAML dependency) ──────────────

_FM_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?", re.S)


def _unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        inner = s[1:-1]
        if s[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\n", "\n")
        return inner
    if s in ("true", "True"):
        return True
    if s in ("false", "False"):
        return False
    if s in ("null", "~", ""):
        return None
    if s.startswith("[") and s.endswith("]"):
        return [_unquote(x) for x in s[1:-1].split(",") if x.strip()]
    return s


def _parse_frontmatter(text):
    """Return (meta_dict, body). Scalars, one-level nested maps, block lists and
    folded/literal strings -- enough for SKILL.md, prompts, agents and commands."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    block, body = m.group(1), text[m.end():]
    meta = {}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        km = re.match(r"^([A-Za-z0-9_\-\.]+)\s*:\s*(.*)$", line)
        if not km:
            i += 1
            continue
        key, rest = km.group(1), km.group(2)
        if rest in (">", "|", ">-", "|-"):
            buf = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
                buf.append(lines[i].strip())
                i += 1
            meta[key] = (" " if rest.startswith(">") else "\n").join(buf).strip()
            continue
        if rest == "":
            sub, lst = {}, []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t")):
                s = lines[i].strip()
                if s.startswith("- "):
                    lst.append(_unquote(s[2:]))
                else:
                    sm = re.match(r"^([A-Za-z0-9_\-\.]+)\s*:\s*(.*)$", s)
                    if sm:
                        sub[sm.group(1)] = _unquote(sm.group(2))
                i += 1
            meta[key] = lst if lst else sub
            continue
        meta[key] = _unquote(rest)
        i += 1
    return meta, body


# ── helpers ────────────────────────────────────────────────────────────────

_SKILL_SUBDIRS = ("scripts", "references", "assets", "templates", "examples")


def _safe_read(path, limit=None):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read() if limit is None else f.read(limit)
    except OSError:
        return ""


def _one_line(s):
    return re.sub(r"\s+", " ", s or "").strip()


def _clip(s, n=12000):
    s = s or ""
    return s if len(s) <= n else s[:n] + f"\n... [{len(s) - n} more chars clipped]"


def _slug(name):
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return s or "skill"


def _camel(slug):
    return "".join(p.capitalize() for p in slug.split("_")) or "Skill"


def _confine(base, rel):
    """Resolve rel inside base; refuse anything that escapes."""
    base = os.path.realpath(base)
    target = os.path.realpath(os.path.join(base, rel or ""))
    if target != base and not target.startswith(base + os.sep):
        raise ValueError(f"path {rel!r} escapes {base}")
    return target


def _resource_index(sdir, limit=60):
    out = []
    for sub in _SKILL_SUBDIRS:
        p = os.path.join(sdir, sub)
        if os.path.isdir(p):
            for path in sorted(glob.glob(os.path.join(p, "**", "*"), recursive=True)):
                if os.path.isfile(path):
                    out.append(os.path.relpath(path, sdir))
    for path in sorted(glob.glob(os.path.join(sdir, "*"))):
        if os.path.isfile(path) and os.path.basename(path) != "SKILL.md":
            out.append(os.path.relpath(path, sdir))
    return out[:limit], max(0, len(out) - limit)


def _substitute_arguments(body, args):
    """Slash-command / prompt substitution: $ARGUMENTS, $1..$9, ${input:name}."""
    if isinstance(args, (list, tuple)):
        parts = [str(a) for a in args]
    elif args is None:
        parts = []
    else:
        parts = shlex.split(str(args)) if str(args).strip() else []
    joined = " ".join(parts)
    out = body.replace("$ARGUMENTS", joined).replace("${input}", joined)
    out = re.sub(r"\$\{input:([^}:]+)(?::[^}]*)?\}", joined, out)
    for i in range(1, 10):
        out = out.replace(f"${i}", parts[i - 1] if len(parts) >= i else "")
    return out


def _expand_cmd(cmd, plugin_root):
    """Expand ${CLAUDE_PLUGIN_ROOT} / ${COPILOT_PLUGIN_ROOT} plus ${VAR} / ${VAR:-default}
    from the environment, the way hosts expand .mcp.json and hooks."""
    out = cmd
    for var in ("CLAUDE_PLUGIN_ROOT", "COPILOT_PLUGIN_ROOT", "PLUGIN_ROOT"):
        out = out.replace("${" + var + "}", plugin_root or "").replace("$" + var, plugin_root or "")

    def sub(m):
        var, default = m.group(1), m.group(3)
        return os.environ.get(var, default if default is not None else m.group(0))

    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(:-([^}]*))?\}", sub, out)


def _run_subprocess(argv, cwd, timeout, stdin_text=None, env_extra=None, shell=False):
    env = dict(os.environ)
    env.update({k: str(v) for k, v in (env_extra or {}).items()})
    started = time.time()
    try:
        proc = subprocess.run(argv, cwd=cwd, input=stdin_text, capture_output=True, text=True,
                              timeout=timeout, env=env, shell=shell)
        return {"exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr,
                "seconds": round(time.time() - started, 2)}
    except subprocess.TimeoutExpired as e:
        so = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        return {"exit": None, "stdout": so, "stderr": f"timed out after {timeout}s", "seconds": timeout}
    except FileNotFoundError as e:
        return {"exit": 127, "stdout": "", "stderr": str(e), "seconds": 0}


def _tree_mtime(paths):
    sig = 0.0
    for p in paths:
        try:
            sig = max(sig, os.stat(p).st_mtime)
            for child in os.listdir(p):
                try:
                    sig = max(sig, os.stat(os.path.join(p, child)).st_mtime)
                except OSError:
                    pass
        except OSError:
            pass
    return sig


# ── discovery ───────────────────────────────────────────────────────────────

class _Catalog:
    """Everything host-shaped reachable from this machine, across all hosts."""

    def __init__(self):
        self.skills, self.commands, self.agents, self.plugins = {}, {}, {}, {}
        self.hooks, self.mcp, self.instructions = [], {}, []
        self.errors, self.roots = [], []
        self._seen_paths = set()

    # -- generic item registration --------------------------------------------
    def _register(self, bucket, kind, path, host, source, plugin=None, name_hint=None):
        real = os.path.realpath(path)
        if real in self._seen_paths:
            return
        meta, body = _parse_frontmatter(_safe_read(path, 200_000))
        name = str(meta.get("name") or name_hint or os.path.basename(os.path.dirname(path))).strip()
        qualified = f"{plugin}:{name}" if plugin else name
        if qualified in bucket:
            # first wins (project > user > plugins, claude before copilot) -- mirror host precedence
            return
        self._seen_paths.add(real)
        desc = str(meta.get("description") or body.strip().split("\n", 1)[0][:200]).strip()
        bucket[qualified] = {"kind": kind, "name": qualified, "short": name, "path": path,
                             "dir": os.path.dirname(path), "description": desc, "meta": meta,
                             "source": source, "plugin": plugin, "host": host}

    def _scan_skill_root(self, root, host, source, plugin=None):
        if not os.path.isdir(root):
            return
        for depth in ("*", "*/*"):
            for skill_md in sorted(glob.glob(os.path.join(root, depth, "SKILL.md"))):
                self._register(self.skills, "skill", skill_md, host, source, plugin)

    def _scan_md_dir(self, root, suffix, bucket, kind, host, source, plugin=None):
        if not os.path.isdir(root):
            return
        for path in sorted(glob.glob(os.path.join(root, "**", "*" + suffix), recursive=True)):
            rel = os.path.relpath(path, root)[: -len(suffix)].replace(os.sep, ":")
            self._register(bucket, kind, path, host, source, plugin, name_hint=rel)

    def _scan_hooks(self, hooks_json, source, plugin_root, host):
        try:
            data = json.loads(_safe_read(hooks_json))
        except ValueError:
            self.errors.append(f"invalid JSON: {hooks_json}")
            return
        hooks = data.get("hooks", data) if isinstance(data, dict) else {}
        for event, groups in (hooks or {}).items():
            if not isinstance(groups, list):
                continue
            for g in groups:
                if not isinstance(g, dict):
                    continue
                inner = g.get("hooks") if isinstance(g.get("hooks"), list) else [g] if g.get("command") else []
                for h in inner:
                    if not isinstance(h, dict) or h.get("type", "command") != "command" or not h.get("command"):
                        continue
                    self.hooks.append({"host": host, "source": source, "event": event,
                                       "matcher": g.get("matcher", ""), "command": h["command"],
                                       "timeout": h.get("timeout"), "cwd": plugin_root, "file": hooks_json})

    def _scan_mcp(self, path, source, cwd, host, key="mcpServers"):
        try:
            data = json.loads(_safe_read(path))
        except ValueError:
            self.errors.append(f"invalid JSON: {path}")
            return
        servers = data.get(key) if isinstance(data, dict) else None
        if not isinstance(servers, dict):
            return
        for name, cfg in servers.items():
            if isinstance(cfg, dict) and name not in self.mcp:
                self.mcp[name] = {"config": cfg, "source": source, "cwd": cwd, "file": path, "host": host}

    def _scan_plugins(self, hkey, host):
        spec = host.get("plugins")
        if not spec:
            return
        found, seen = [], set()

        def add(d, src):
            d = os.path.abspath(d)
            if d in seen or not os.path.isdir(d):
                return
            seen.add(d)
            found.append((d, src))

        inst = spec.get("installed_json")
        if inst:
            inst = _fill(inst, host)
            if os.path.isfile(inst):
                try:
                    data = json.loads(_safe_read(inst))
                    for entries in (data.get("plugins") or {}).values():
                        for e in entries if isinstance(entries, list) else [entries]:
                            if isinstance(e, dict) and e.get("installPath"):
                                add(e["installPath"], f"installed:{e.get('scope', '?')}")
                except ValueError:
                    self.errors.append(f"invalid JSON: {inst}")
        for tpl in spec.get("dirs", []):
            for d in _expand_paths(tpl, host):
                if any(os.path.isfile(os.path.join(d, m)) for m in spec["manifests"]):
                    add(d, "cache")
        for d in sorted(glob.glob(os.path.join(_store_dir(), "plugins", "*"))):
            if any(os.path.isfile(os.path.join(d, m)) for m in ("plugin.json", ".claude-plugin/plugin.json")):
                add(d, "brainstem-store")

        for pdir, source in found:
            manifest, mpath = None, None
            for m in list(spec["manifests"]) + ["plugin.json", ".claude-plugin/plugin.json"]:
                cand = os.path.join(pdir, m)
                if os.path.isfile(cand):
                    try:
                        manifest, mpath = json.loads(_safe_read(cand)), cand
                    except ValueError:
                        manifest, mpath = {"_error": f"invalid JSON in {cand}"}, cand
                    break
            base = os.path.basename(pdir.rstrip(os.sep))
            if re.match(r"^[0-9a-f.\-]+$", base):  # <marketplace>/<plugin>/<version> layout
                base = os.path.basename(os.path.dirname(pdir.rstrip(os.sep)))
            if manifest is None:
                manifest = {"name": base, "_bare": True}
            if "_error" in manifest:
                self.errors.append(manifest["_error"])
            pname = str(manifest.get("name") or base)
            if pname in self.plugins:
                if os.path.realpath(pdir) != os.path.realpath(self.plugins[pname]["dir"]):
                    pname = f"{pname}@{hkey}"
                    if pname in self.plugins:
                        continue
                else:
                    continue
            entry = {"name": pname, "dir": pdir, "manifest": manifest, "manifest_path": mpath, "source": source,
                     "host": hkey, "skills": [], "commands": [], "agents": [], "hooks": 0, "mcp": []}
            self.plugins[pname] = entry
            before = set(self.skills)
            self._scan_skill_root(os.path.join(pdir, spec["skills_subdir"]), hkey, f"plugin:{source}", pname)
            entry["skills"] = sorted(set(self.skills) - before)
            before = set(self.commands)
            for sub, suf in ((spec["commands_subdir"], ".md"), ("commands", ".md"), ("prompts", ".prompt.md")):
                self._scan_md_dir(os.path.join(pdir, sub), suf, self.commands, "command", hkey, f"plugin:{source}", pname)
            entry["commands"] = sorted(set(self.commands) - before)
            before = set(self.agents)
            for suf in (".agent.md", ".md"):
                self._scan_md_dir(os.path.join(pdir, spec["agents_subdir"]), suf, self.agents, "agent", hkey, f"plugin:{source}", pname)
            entry["agents"] = sorted(set(self.agents) - before)
            nh = len(self.hooks)
            for hf in spec["hooks_files"]:
                if os.path.isfile(os.path.join(pdir, hf)):
                    self._scan_hooks(os.path.join(pdir, hf), f"plugin:{pname}", pdir, hkey)
                    break
            entry["hooks"] = len(self.hooks) - nh
            before = set(self.mcp)
            mcp_file = manifest.get("mcpServers") if isinstance(manifest.get("mcpServers"), str) else spec["mcp_file"]
            mp = os.path.join(pdir, mcp_file)
            if os.path.isfile(mp):
                self._scan_mcp(mp, f"plugin:{pname}", pdir, hkey)
            elif isinstance(manifest.get("mcpServers"), dict):
                for n, cfg in manifest["mcpServers"].items():
                    self.mcp.setdefault(n, {"config": cfg, "source": f"plugin:{pname}", "cwd": pdir, "file": mpath, "host": hkey})
            entry["mcp"] = sorted(set(self.mcp) - before)

    def scan(self):
        proj = _project_dir()
        for hkey, host in _hosts().items():
            for tpl in host.get("skills", []):
                root = _fill(tpl, host)
                if os.path.isdir(root):
                    self.roots.append(root)
                    self._scan_skill_root(root, hkey, "project" if root.startswith(proj) else "user")
            for spec in host.get("commands", []):
                root = _fill(spec["dir"], host)
                self._scan_md_dir(root, spec["suffix"], self.commands, "command", hkey, "project" if root.startswith(proj) else "user")
            for spec in host.get("agents", []):
                root = _fill(spec["dir"], host)
                self._scan_md_dir(root, spec["suffix"], self.agents, "agent", hkey, "project" if root.startswith(proj) else "user")
            self._scan_plugins(hkey, host)
            for tpl in host.get("hooks", []):
                for f in _expand_paths(tpl, host):
                    if os.path.isfile(f):
                        self._scan_hooks(f, f"{hkey}:{os.path.relpath(f, proj) if f.startswith(proj) else os.path.basename(f)}", os.path.dirname(f), hkey)
            for spec in host.get("mcp", []):
                f = _fill(spec["file"], host)
                if os.path.isfile(f):
                    self._scan_mcp(f, "project" if f.startswith(proj) else f"user:{hkey}", proj, hkey, spec.get("key", "mcpServers"))
            for tpl in host.get("instructions", []):
                for f in _expand_paths(tpl, host):
                    if os.path.isfile(f) and os.path.realpath(f) not in {os.path.realpath(x["path"]) for x in self.instructions}:
                        self.instructions.append({"host": hkey, "path": f, "size": os.path.getsize(f)})
        extra = _env("HOST_COMPAT_ROOTS", "")
        for r in [os.path.expanduser(r) for r in extra.split(os.pathsep) if r.strip()]:
            if os.path.isdir(r):
                self.roots.append(r)
                self._scan_skill_root(r, "extra", "extra")
        return self

    def find(self, name, host=None):
        if not name:
            return None
        n = name.strip().lstrip("/")
        buckets = (self.skills, self.commands, self.agents)
        for pred in (lambda k, it: k == n, lambda k, it: it["short"] == n,
                     lambda k, it: k.lower() == n.lower() or it["short"].lower() == n.lower()):
            for bucket in buckets:
                for key, item in bucket.items():
                    if pred(key, item) and (not host or item["host"] == host):
                        return item
        return None


_catalog_cache = {"sig": None, "catalog": None, "built": 0.0}
_catalog_lock = threading.Lock()


def _get_catalog(force=False):
    sig_paths = []
    for host in _hosts().values():
        home = _host_home(host)
        sig_paths += [home, os.path.join(home, "skills"), os.path.join(home, "plugins"), os.path.join(home, "installed-plugins")]
    proj = _project_dir()
    sig_paths += [os.path.join(proj, ".claude"), os.path.join(proj, ".github"), os.path.join(proj, ".agents"),
                  os.path.join(_store_dir(), "plugins")]
    sig = (proj, _env("HOST_COMPAT_ROOTS", ""), _tree_mtime(sig_paths))
    with _catalog_lock:
        if not force and _catalog_cache["catalog"] is not None and _catalog_cache["sig"] == sig \
                and time.time() - _catalog_cache["built"] < 300:
            return _catalog_cache["catalog"]
        cat = _Catalog().scan()
        _catalog_cache.update({"sig": sig, "catalog": cat, "built": time.time()})
        return cat


# ── MCP client (stdio + streamable HTTP) ───────────────────────────────────

_MCP_PROTOCOL = "2025-06-18"


class _McpClient:
    def __init__(self, name, entry, timeout):
        self.name, self.cfg, self.timeout = name, entry["config"], timeout
        self.cwd = entry.get("cwd") or None
        self.proc, self._id, self._lines, self._reader = None, 0, [], None
        self._lock = threading.Lock()
        kind = (self.cfg.get("type") or ("http" if self.cfg.get("url") else "stdio")).lower()
        self.kind = "stdio" if kind in ("local", "stdio") else "http"  # copilot says "local"
        self.session_id = None

    def _start_stdio(self):
        command = _expand_cmd(str(self.cfg.get("command", "")), self.cwd)
        args = [_expand_cmd(str(a), self.cwd) for a in (self.cfg.get("args") or [])]
        env = dict(os.environ)
        env.update({k: _expand_cmd(str(v), self.cwd) for k, v in (self.cfg.get("env") or {}).items()})
        self.proc = subprocess.Popen([command] + args, cwd=self.cwd, env=env, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        def pump():
            for line in self.proc.stdout:
                with self._lock:
                    self._lines.append(line)

        self._reader = threading.Thread(target=pump, daemon=True)
        self._reader.start()

    def _rpc(self, method, params=None, notify=False):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            self._id += 1
            msg["id"] = self._id
        return self._rpc_stdio(msg, notify) if self.kind == "stdio" else self._rpc_http(msg, notify)

    def _rpc_stdio(self, msg, notify):
        if self.proc is None:
            self._start_stdio()
        if self.proc.poll() is not None:
            raise RuntimeError(f"MCP server {self.name!r} exited early: {(self.proc.stderr.read() or '')[:500]}")
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        if notify:
            return None
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            with self._lock:
                pending, self._lines = self._lines, []
            for line in pending:
                try:
                    obj = json.loads(line.strip()) if line.strip() else None
                except ValueError:
                    continue
                if obj and obj.get("id") == msg["id"]:
                    if "error" in obj:
                        raise RuntimeError(f"MCP error from {self.name!r}: {json.dumps(obj['error'])[:800]}")
                    return obj.get("result")
            if self.proc.poll() is not None:
                raise RuntimeError(f"MCP server {self.name!r} exited: {(self.proc.stderr.read() or '')[:500]}")
            time.sleep(0.02)
        raise RuntimeError(f"MCP server {self.name!r} did not answer {msg['method']} within {self.timeout}s")

    def _rpc_http(self, msg, notify):
        url = _expand_cmd(str(self.cfg.get("url", "")), self.cwd)
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        headers.update({k: _expand_cmd(str(v), self.cwd) for k, v in (self.cfg.get("headers") or {}).items()})
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        req = urllib.request.Request(url, data=json.dumps(msg).encode(), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            self.session_id = resp.headers.get("Mcp-Session-Id") or self.session_id
            raw = resp.read().decode("utf-8", "replace")
            ctype = resp.headers.get("Content-Type", "")
        if notify:
            return None
        payloads = [ln[5:].strip() for ln in raw.splitlines() if ln.startswith("data:")] if "text/event-stream" in ctype else [raw]
        for p in payloads:
            try:
                obj = json.loads(p)
            except ValueError:
                continue
            if obj.get("id") == msg["id"]:
                if "error" in obj:
                    raise RuntimeError(f"MCP error from {self.name!r}: {json.dumps(obj['error'])[:800]}")
                return obj.get("result")
        raise RuntimeError(f"MCP server {self.name!r}: no response for {msg['method']}")

    def initialize(self):
        res = self._rpc("initialize", {"protocolVersion": _MCP_PROTOCOL, "capabilities": {},
                                       "clientInfo": {"name": "rapp-brainstem-host-compat", "version": "1.0"}})
        self._rpc("notifications/initialized", {}, notify=True)
        return res or {}

    def list_tools(self):
        tools, cursor = [], None
        for _ in range(20):
            res = self._rpc("tools/list", {"cursor": cursor} if cursor else {}) or {}
            tools.extend(res.get("tools") or [])
            cursor = res.get("nextCursor")
            if not cursor:
                break
        return tools

    def call_tool(self, tool, arguments):
        return self._rpc("tools/call", {"name": tool, "arguments": arguments or {}}) or {}

    def close(self):
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=3)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass


# ── transcript index (both hosts, incremental, FTS5 when available) ────────

_MSG_CAP = 6000


def _iter_claude_jsonl(path):
    """Yield (role, ts, cwd, text, title) from a Claude Code session file."""
    title = ""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            # "type" is rarely the first key in Claude's lines; a whole-line substring test is
            # still far cheaper than json.loads on every tool-result line.
            if not any(k in line for k in ('"type":"user"', '"type":"assistant"', '"type":"summary"',
                                           '"type": "user"', '"type": "assistant"', '"type": "summary"')):
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            t = d.get("type")
            if t == "summary":
                title = str(d.get("summary") or title)
                continue
            if t not in ("user", "assistant") or d.get("isMeta"):
                continue
            content = (d.get("message") or {}).get("content")
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text = "\n".join(str(c.get("text", "")) for c in content
                                 if isinstance(c, dict) and c.get("type") == "text")
            else:
                text = ""
            text = text.strip()
            if not text or text.startswith("<command-name>") or text.startswith("<local-command-stdout>"):
                continue
            yield t, str(d.get("timestamp", "")), str(d.get("cwd", "")), text[:_MSG_CAP], title


def _iter_copilot_events(path):
    """Yield (role, ts, cwd, text, title) from a Copilot CLI events.jsonl."""
    cwd, title = "", ""
    ws = os.path.join(os.path.dirname(path), "workspace.yaml")
    for line in _safe_read(ws, 4000).splitlines():
        if line.startswith("cwd:"):
            cwd = line[4:].strip()
        elif line.startswith("name:"):
            title = line[5:].strip()
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            head = line[:60]
            if '"user.message"' not in head and '"assistant.message"' not in head and '"session.start"' not in head:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            t, data = d.get("type"), d.get("data") or {}
            if t == "session.start":
                cwd = cwd or str((data.get("context") or {}).get("cwd", ""))
                continue
            text = str(data.get("content") or "").strip()
            if not text:
                continue
            role = "user" if t == "user.message" else "assistant"
            yield role, str(d.get("timestamp", "")), cwd, text[:_MSG_CAP], title


_TRANSCRIPT_FORMATS = {"claude-jsonl": _iter_claude_jsonl, "copilot-events": _iter_copilot_events}


class _TranscriptIndex:
    def __init__(self, db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db = sqlite3.connect(db_path, timeout=30)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, host TEXT, session TEXT, mtime REAL, size INTEGER, cwd TEXT, title TEXT, messages INTEGER)")
        try:
            self.db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS msgs USING fts5(text, host UNINDEXED, session UNINDEXED, role UNINDEXED, ts UNINDEXED, cwd UNINDEXED, path UNINDEXED, title UNINDEXED)")
            self.fts = True
        except sqlite3.OperationalError:
            self.db.execute("CREATE TABLE IF NOT EXISTS msgs (text, host, session, role, ts, cwd, path, title)")
            self.fts = False
        self.db.commit()

    def candidates(self, days):
        """Newest-first list of (path, host, fmt, mtime, size) inside the window."""
        cutoff = time.time() - days * 86400
        out = []
        for hkey, host in _hosts().items():
            spec = host.get("transcripts")
            if not spec:
                continue
            fmt = spec["format"]
            for p in _expand_paths(spec["glob"], host):
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                if st.st_mtime >= cutoff and st.st_size > 0:
                    out.append((p, hkey, fmt, st.st_mtime, st.st_size))
        # newest-first PER HOST, then interleaved, so a host with few large files (Claude Code)
        # is never starved by a host with tens of thousands of small ones (Copilot CLI).
        by_host = {}
        for r in sorted(out, key=lambda r: -r[3]):
            by_host.setdefault(r[1], []).append(r)
        merged, queues = [], list(by_host.values())
        while queues:
            for q in list(queues):
                merged.append(q.pop(0))
                if not q:
                    queues.remove(q)
        return merged

    def refresh(self, days, budget_seconds):
        """Index changed/new files newest-first until the time budget runs out."""
        started = time.time()
        cands = self.candidates(days)
        known = {r[0]: (r[1], r[2]) for r in self.db.execute("SELECT path, mtime, size FROM files")}
        todo = [c for c in cands if known.get(c[0]) != (c[3], c[4])]
        done = 0
        for path, hkey, fmt, mtime, size in todo:
            if time.time() - started > budget_seconds:
                break
            session = os.path.basename(os.path.dirname(path)) if fmt == "copilot-events" else os.path.basename(path)[:-6]
            rows, cwd, title = [], "", ""
            try:
                for role, ts, c, text, t in _TRANSCRIPT_FORMATS[fmt](path):
                    cwd, title = c or cwd, t or title
                    rows.append((text, hkey, session, role, ts, cwd, path, title))
            except OSError:
                continue
            rows = [(r[0], r[1], r[2], r[3], r[4], r[5] or cwd, r[6], title) for r in rows]
            with self.db:
                self.db.execute("DELETE FROM msgs WHERE path = ?", (path,))
                self.db.executemany("INSERT INTO msgs (text, host, session, role, ts, cwd, path, title) VALUES (?,?,?,?,?,?,?,?)", rows)
                self.db.execute("INSERT OR REPLACE INTO files VALUES (?,?,?,?,?,?,?,?)",
                                (path, hkey, session, mtime, size, cwd, title, len(rows)))
            done += 1
        return {"indexed_now": done, "pending": max(0, len(todo) - done), "in_window": len(cands),
                "seconds": round(time.time() - started, 1)}

    def stats(self):
        files = self.db.execute("SELECT host, COUNT(*), COALESCE(SUM(messages),0) FROM files GROUP BY host").fetchall()
        return {h: {"sessions": n, "messages": m} for h, n, m in files}

    def search(self, query, host=None, role=None, cwd=None, limit=20, since_iso=None):
        where, params = [], []
        if since_iso:
            where.append("ts >= ?")
            params.append(since_iso)
        if host:
            where.append("host = ?")
            params.append(host)
        if role:
            where.append("role = ?")
            params.append(role)
        if cwd:
            where.append("cwd LIKE ?")
            params.append(f"%{cwd}%")
        if self.fts:
            toks = [t for t in re.findall(r"[\w'\-]+", query) if t]
            match = " ".join('"' + t.replace('"', '""') + '"' for t in toks) or '""'
            sql = ("SELECT host, session, role, ts, cwd, path, title, snippet(msgs, 0, '>>', '<<', ' … ', 24) "
                   "FROM msgs WHERE msgs MATCH ? " + "".join(" AND " + w for w in where) + " ORDER BY ts DESC LIMIT ?")
            params = [match] + params + [limit]
        else:
            like = f"%{query}%"
            sql = ("SELECT host, session, role, ts, cwd, path, title, substr(text, 1, 240) FROM msgs WHERE text LIKE ? "
                   + "".join(" AND " + w for w in where) + " ORDER BY ts DESC LIMIT ?")
            params = [like] + params + [limit]
        return self.db.execute(sql, params).fetchall()

    def session(self, session, limit=200):
        rows = self.db.execute("SELECT role, ts, text, cwd, title, host, path FROM msgs WHERE session LIKE ? ORDER BY ts LIMIT ?",
                               (session + "%", limit)).fetchall()
        return rows

    def close(self):
        self.db.close()


# ── promoted-agent template (skill -> native brainstem tool) ───────────────

_PROMOTED_TEMPLATE = '''"""{class_name} -- skill {skill_name!r} promoted into a native RAPP agent.

Generated by HostCompat (action="promote"). Self-contained: the SKILL.md body is
embedded, and bundled scripts still run from the original skill directory when it
exists. Regenerate with HostCompat rather than editing the embedded body.
Skill sha256: {sha}
"""

import json
import os
import shlex
import subprocess

from agents.basic_agent import BasicAgent

SKILL_DIR = {skill_dir!r}
SKILL_BODY = {body!r}
SKILL_META = {meta!r}


class {class_name}(BasicAgent):
    def __init__(self):
        self.name = {tool_name!r}
        self.metadata = {{
            "name": self.name,
            "description": {description!r},
            "parameters": {{
                "type": "object",
                "properties": {{
                    "task": {{"type": "string", "description": "What the user wants done with this skill (free text)."}},
                    "script": {{"type": "string", "description": "Optional: relative path of a bundled script to run (e.g. scripts/x.py)."}},
                    "args": {{"type": "string", "description": "Optional shell-style arguments for the script."}},
                    "read": {{"type": "string", "description": "Optional: relative path of a bundled reference file to return."}}
                }},
                "required": []
            }}
        }}
        super().__init__()

    def _confine(self, rel):
        base = os.path.realpath(SKILL_DIR)
        target = os.path.realpath(os.path.join(base, rel))
        if target != base and not target.startswith(base + os.sep):
            raise ValueError("path escapes the skill directory")
        return target

    def perform(self, task="", script="", args="", read="", **_):
        if read:
            try:
                with open(self._confine(read), "r", encoding="utf-8", errors="replace") as f:
                    return f.read()[:40000]
            except (OSError, ValueError) as e:
                return "Cannot read " + read + ": " + str(e)
        if script:
            try:
                path = self._confine(script)
            except ValueError as e:
                return str(e)
            argv = [path] + shlex.split(args or "")
            if path.endswith(".py"):
                argv = ["python3"] + argv
            elif path.endswith(".sh"):
                argv = ["bash"] + argv
            try:
                p = subprocess.run(argv, cwd=SKILL_DIR, capture_output=True, text=True, timeout=120)
                return json.dumps({{"exit": p.returncode, "stdout": p.stdout[-8000:], "stderr": p.stderr[-2000:]}}, indent=2)
            except subprocess.TimeoutExpired:
                return "script timed out after 120s"
        resources = []
        if os.path.isdir(SKILL_DIR):
            for root, _dirs, files in os.walk(SKILL_DIR):
                for fn in files:
                    if fn != "SKILL.md":
                        resources.append(os.path.relpath(os.path.join(root, fn), SKILL_DIR))
        header = "# Skill: " + {skill_name!r} + "\\n"
        if task:
            header += "User task: " + task + "\\n"
        if resources:
            header += "Bundled files (pass read=<path> or script=<path>): " + ", ".join(sorted(resources)[:40]) + "\\n"
        return header + "\\n" + SKILL_BODY
'''


# ── the agent ──────────────────────────────────────────────────────────────

_ACTIONS = ["list", "load", "read", "run", "hook", "mcp_tools", "mcp_call", "install", "uninstall",
            "promote", "export", "instructions", "transcripts", "transcript", "index", "doctor", "refresh"]


class HostCompatAgent(BasicAgent):
    def __init__(self):
        self.name = "HostCompat"
        self.metadata = {
            "name": self.name,
            "description": (
                "Bridge to everything agent-host-shaped on this machine, across Claude Code, GitHub Copilot CLI and "
                "the open Agent Skills layout: skills (SKILL.md), plugins, slash commands / prompts, subagent personas, "
                "hooks, MCP servers, instruction files (CLAUDE.md, AGENTS.md, copilot-instructions.md) and local "
                "session transcripts. action='list' shows what exists; 'load' pulls a skill/command/persona's "
                "instructions into the conversation before doing that kind of work; 'read' returns a bundled file; "
                "'run' executes a skill's bundled script; 'mcp_tools'/'mcp_call' use an MCP server; 'install' adds a "
                "plugin from a path or git URL; 'promote' compiles a skill into a native Brainstem agent; 'export' "
                "turns an agent into a SKILL.md; 'hook' fires a hook; 'instructions' returns the project's instruction "
                "files; 'transcripts' searches the user's own past CODING-ASSISTANT CHAT HISTORY — Claude Code and "
                "GitHub Copilot CLI session logs on this machine — across both hosts at once (query=...; this is the "
                "tool for 'what did I ask Claude/Copilot about X', 'find my earlier session where...', NOT for meeting "
                "or call transcripts); 'transcript' reads one session by id; 'index' backfills the session index; "
                "'doctor' is a health report."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": _ACTIONS, "description": "What to do."},
                    "name": {"type": "string", "description": "Skill / command / persona / plugin / MCP server / agent / session id (plugin-qualified 'plugin:name' allowed)."},
                    "host": {"type": "string", "enum": ["all", "claude-code", "copilot-cli", "agent-skills"],
                             "description": "Restrict to one host's catalog or transcripts (default all)."},
                    "kind": {"type": "string", "enum": ["all", "skills", "plugins", "commands", "agents", "hooks", "mcp", "instructions"],
                             "description": "For list: which catalog to show (default all)."},
                    "query": {"type": "string", "description": "For list: substring filter. For transcripts: the search terms (all must match)."},
                    "path": {"type": "string", "description": "For read/run: file path relative to the skill or plugin directory. For export: output directory."},
                    "args": {"type": "string", "description": "For load ($ARGUMENTS), run (script args), or hook (matcher / tool name)."},
                    "stdin": {"type": "string", "description": "For run/hook: text (usually JSON) sent on stdin."},
                    "tool": {"type": "string", "description": "For mcp_call: the MCP tool name."},
                    "arguments": {"type": "object", "description": "For mcp_call: the tool's arguments object."},
                    "source": {"type": "string", "description": "For install: local directory path or git URL of a plugin (or a bare skill folder)."},
                    "role": {"type": "string", "enum": ["user", "assistant"], "description": "For transcripts: only messages from this role."},
                    "cwd": {"type": "string", "description": "For transcripts: only sessions whose working directory contains this text."},
                    "days": {"type": "integer", "description": "For transcripts/index: how many days back to index (default 30)."},
                    "limit": {"type": "integer", "description": "For transcripts/transcript: max results (default 20 / 200)."},
                    "timeout": {"type": "integer", "description": "Seconds to allow a script/hook/MCP call or an index pass (default 120)."},
                },
                "required": ["action"],
            },
        }
        super().__init__()

    # -- system prompt catalog (progressive disclosure, capped, degrades gracefully)
    def system_context(self):
        cap = _int_env("HOST_COMPAT_CONTEXT_CHARS", 6000)
        if cap <= 0:
            return None
        try:
            cat = _get_catalog()
        except Exception as e:  # never break /chat
            return f"<host_compat>catalog unavailable: {e}</host_compat>"
        if not (cat.skills or cat.commands or cat.agents or cat.mcp):
            return None
        head = ("<host_compat>\nSkills, commands, personas and MCP servers from Claude Code and GitHub Copilot CLI are "
                "available through the HostCompat tool. When a task matches an entry below, call "
                "HostCompat(action=\"load\", name=...) FIRST and follow the returned instructions; action=\"list\" "
                "with a query shows the full catalog. For questions about the user's PAST CLAUDE CODE OR COPILOT CLI "
                "CHATS (\"what did I ask Copilot about X\", \"find my session where...\"), call "
                "HostCompat(action=\"transcripts\", query=...) — it searches both hosts' session logs at once.\n")
        tail = "</host_compat>"
        budget = cap - len(head) - len(tail) - 64

        def render(desc_len):
            lines = []

            def section(label, items):
                if not items:
                    return
                if desc_len == 0:
                    lines.append(f"{label} ({len(items)}): " + ", ".join(items))
                    return
                lines.append(f"{label} ({len(items)}):")
                for key, item in items.items():
                    d = _one_line(item.get("description", "")).split(". ")[0][:desc_len]
                    lines.append(f"- {key}: {d}" if d else f"- {key}")

            section("Skills", cat.skills)
            section("Slash commands / prompts", cat.commands)
            section("Subagent personas", cat.agents)
            if cat.mcp:
                lines.append(f"MCP servers ({len(cat.mcp)}): " + ", ".join(sorted(cat.mcp)) + "  (action=\"mcp_tools\" then \"mcp_call\")")
            return lines

        out = None
        for desc_len in (90, 50, 0):  # a dropped skill can never auto-trigger, so drop last
            lines = render(desc_len)
            if sum(len(ln) + 1 for ln in lines) <= budget:
                out = lines
                break
        if out is None:
            out, used, dropped = [], 0, 0
            for ln in lines:
                if used + len(ln) + 1 > budget:
                    dropped += 1
                    continue
                out.append(ln)
                used += len(ln) + 1
            if dropped:
                out.append(f"(+{dropped} more entries; use action=\"list\" to see them)")
        return head + "\n".join(out) + "\n" + tail

    # -- dispatch ------------------------------------------------------------
    def perform(self, action="list", operation=None, **kw):
        action = operation or action or "list"  # RAR convention is `operation`; both work
        handler = getattr(self, f"_do_{action}", None)
        if handler is None:
            return f"Unknown action {action!r}. Valid: {', '.join(_ACTIONS)}."
        try:
            return handler(**kw)
        except Exception as e:
            return f"HostCompat {action} failed: {type(e).__name__}: {e}"

    def _timeout(self, kw, cap=600):
        try:
            t = int(kw.get("timeout")) if kw.get("timeout") is not None else _int_env("HOST_COMPAT_TIMEOUT", 120)
        except (TypeError, ValueError):
            t = _int_env("HOST_COMPAT_TIMEOUT", 120)
        return max(1, min(t, cap))

    @staticmethod
    def _host_filter(host):
        return None if not host or host == "all" else host

    # -- list ----------------------------------------------------------------
    def _do_list(self, kind="all", query="", host="", **_):
        cat = _get_catalog()
        q, hf = (query or "").lower().strip(), self._host_filter(host)
        kind = (kind or "all").lower()

        def ok(item):
            if hf and item.get("host") != hf:
                return False
            return not q or q in item["name"].lower() or q in item.get("description", "").lower()

        def row(i, prefix=""):
            return f"- {prefix}{i['name']} [{i['host']}/{i['source']}] — {_one_line(i['description'])[:160]}"

        out = []
        if kind in ("all", "skills"):
            rows = [i for i in cat.skills.values() if ok(i)]
            out.append(f"## Skills ({len(rows)})")
            out += [row(i) for i in rows]
        if kind in ("all", "commands"):
            rows = [i for i in cat.commands.values() if ok(i)]
            out.append(f"\n## Slash commands / prompts ({len(rows)})")
            out += [row(i, "/") for i in rows]
        if kind in ("all", "agents"):
            rows = [i for i in cat.agents.values() if ok(i)]
            out.append(f"\n## Subagent personas ({len(rows)})")
            out += [row(i) for i in rows]
        if kind in ("all", "plugins"):
            rows = [p for p in cat.plugins.values() if (not hf or p["host"] == hf) and
                    (not q or q in p["name"].lower() or q in str(p["manifest"].get("description", "")).lower())]
            out.append(f"\n## Plugins ({len(rows)})")
            for p in rows:
                m = p["manifest"]
                out.append(f"- {p['name']} v{m.get('version', '?')} [{p['host']}/{p['source']}] — {str(m.get('description', ''))[:140]}"
                           f" | skills={len(p['skills'])} commands={len(p['commands'])} agents={len(p['agents'])} hooks={p['hooks']} mcp={len(p['mcp'])}")
        if kind in ("all", "hooks"):
            rows = [h for h in cat.hooks if (not hf or h["host"] == hf) and
                    (not q or q in h["event"].lower() or q in h["command"].lower() or q in h["source"].lower())]
            out.append(f"\n## Hooks ({len(rows)})")
            out += [f"- {h['event']}" + (f"[{h['matcher']}]" if h["matcher"] else "") + f" ({h['host']}/{h['source']}): {h['command'][:120]}" for h in rows]
        if kind in ("all", "mcp"):
            rows = {n: e for n, e in cat.mcp.items() if (not hf or e["host"] == hf) and (not q or q in n.lower())}
            out.append(f"\n## MCP servers ({len(rows)})")
            for n, e in rows.items():
                c = e["config"]
                what = c.get("url") or " ".join([str(c.get("command", ""))] + [str(a) for a in c.get("args", [])])
                out.append(f"- {n} [{e['host']}/{e['source']}] {c.get('type') or ('http' if c.get('url') else 'stdio')}: {what[:120]}")
        if kind in ("all", "instructions"):
            rows = [i for i in cat.instructions if (not hf or i["host"] == hf) and (not q or q in i["path"].lower())]
            out.append(f"\n## Instruction files ({len(rows)})")
            out += [f"- {i['path']} [{i['host']}] {i['size']} bytes" for i in rows]
        if cat.errors:
            out.append("\n## Parse errors")
            out += [f"- {e}" for e in cat.errors[:20]]
        return "\n".join(out).strip() or "Nothing host-shaped found."

    # -- load ----------------------------------------------------------------
    def _do_load(self, name="", args="", host="", **_):
        cat = _get_catalog()
        item = cat.find(name, self._host_filter(host))
        if item is None:
            near = [k for k in list(cat.skills) + list(cat.commands) + list(cat.agents)
                    if name and name.lower().replace("/", "") in k.lower()][:8]
            return f"No skill/command/persona named {name!r}." + (f" Close matches: {', '.join(near)}" if near else " Try action='list'.")
        meta, body = _parse_frontmatter(_safe_read(item["path"], 400_000))
        body = body.strip()
        if item["kind"] == "command":
            body = _substitute_arguments(body, args)
        lines = [f"# {item['kind'].capitalize()}: {item['name']}", f"Host: {item['host']}", f"Source: {item['path']}"]
        if item.get("plugin"):
            lines.append(f"Plugin: {item['plugin']}")
        for k in ("allowed-tools", "tools", "model", "argument-hint", "mode", "compatibility", "license"):
            if meta.get(k):
                lines.append(f"{k}: {meta[k]}")
        if item["kind"] == "agent":
            lines.append("Use this as a persona: adopt the instructions below for the current task, then answer as that agent.")
        elif item["kind"] == "command":
            lines.append("This is a slash-command / prompt file; treat the text below as the user's instruction.")
        else:
            files, extra = _resource_index(item["dir"])
            if files:
                lines.append("Bundled files (action='read' path=<file> for references, action='run' path=<script> to execute): "
                             + ", ".join(files) + (f", +{extra} more" if extra else ""))
        return "\n".join(lines) + "\n\n" + _clip(body, 60_000)

    # -- read / run ----------------------------------------------------------
    def _resolve_dir(self, name, host=""):
        cat = _get_catalog()
        item = cat.find(name, self._host_filter(host))
        if item is not None:
            return item["dir"], item
        p = cat.plugins.get((name or "").strip())
        if p:
            return p["dir"], p
        raise ValueError(f"unknown skill/command/persona/plugin {name!r}")

    def _do_read(self, name="", path="", host="", **_):
        base, _item = self._resolve_dir(name, host)
        target = _confine(base, path)
        if os.path.isdir(target):
            return f"Directory {path or '.'} in {name}:\n" + "\n".join(sorted(os.listdir(target))[:200])
        if not os.path.isfile(target):
            return f"No file {path!r} in {name}."
        return _clip(_safe_read(target, 400_000), 60_000)

    def _do_run(self, name="", path="", args="", stdin=None, host="", **kw):
        base, item = self._resolve_dir(name, host)
        if not path:
            files, _ = _resource_index(base)
            scripts = [f for f in files if f.startswith("scripts" + os.sep) or f.endswith((".py", ".sh", ".js", ".ts"))]
            return "Pass path=<script>. Runnable files: " + (", ".join(scripts) if scripts else "none found")
        target = _confine(base, path)
        if not os.path.isfile(target):
            return f"No script {path!r} in {name}."
        extra = shlex.split(args) if isinstance(args, str) and args.strip() else [str(a) for a in args] if isinstance(args, (list, tuple)) else []
        argv = [target] + extra
        if target.endswith(".py"):
            argv = [sys.executable] + argv
        elif target.endswith(".sh"):
            argv = ["bash"] + argv
        elif target.endswith((".js", ".mjs")):
            argv = ["node"] + argv
        elif not os.access(target, os.X_OK):
            argv = ["bash"] + argv
        plugin_root = base
        if isinstance(item, dict) and item.get("plugin"):
            plugin_root = _get_catalog().plugins.get(item["plugin"], {}).get("dir", base)
        res = _run_subprocess(argv, cwd=base, timeout=self._timeout(kw), stdin_text=stdin,
                              env_extra={"CLAUDE_PLUGIN_ROOT": plugin_root, "COPILOT_PLUGIN_ROOT": plugin_root,
                                         "CLAUDE_SKILL_DIR": base, "SKILL_DIR": base})
        return json.dumps({"command": " ".join(shlex.quote(a) for a in argv), "cwd": base, "exit": res["exit"],
                           "seconds": res["seconds"], "stdout": _clip(res["stdout"], 20_000),
                           "stderr": _clip(res["stderr"], 6_000)}, indent=2)

    # -- hooks ---------------------------------------------------------------
    def _do_hook(self, name="", args="", stdin=None, host="", **kw):
        cat = _get_catalog()
        event, hf = (name or "").strip(), self._host_filter(host)
        if not event:
            return "Pass name=<event> (e.g. Stop, PreToolUse, PostToolUse, UserPromptSubmit, SessionStart)."
        want = [h for h in cat.hooks if h["event"].lower() == event.lower() and (not hf or h["host"] == hf)]
        if args:
            want = [h for h in want if not h["matcher"] or re.search(h["matcher"], str(args))]
        if not want:
            return f"No hooks registered for event {event!r}" + (f" matching {args!r}" if args else "") + "."
        payload = stdin if stdin is not None else json.dumps({"hook_event_name": event, "session_id": "brainstem",
                                                              "cwd": _project_dir(), "tool_name": args or ""})
        results = []
        for h in want:
            cmd = _expand_cmd(h["command"], h["cwd"])
            t = h.get("timeout") or self._timeout(kw)
            res = _run_subprocess(cmd, cwd=h["cwd"], timeout=min(int(t), 600), stdin_text=payload,
                                  env_extra={"CLAUDE_PLUGIN_ROOT": h["cwd"], "COPILOT_PLUGIN_ROOT": h["cwd"]}, shell=True)
            results.append({"host": h["host"], "source": h["source"], "event": h["event"], "matcher": h["matcher"],
                            "command": cmd, "exit": res["exit"], "stdout": _clip(res["stdout"], 8000), "stderr": _clip(res["stderr"], 3000)})
        return json.dumps(results, indent=2)

    # -- MCP -----------------------------------------------------------------
    def _mcp(self, name, kw):
        cat = _get_catalog()
        entry = cat.mcp.get((name or "").strip())
        if entry is None:
            return None, f"No MCP server named {name!r}. Known: {', '.join(sorted(cat.mcp)) or 'none'}."
        return _McpClient(name, entry, self._timeout(kw)), None

    def _do_mcp_tools(self, name="", **kw):
        client, err = self._mcp(name, kw)
        if err:
            return err
        try:
            info = client.initialize()
            tools = client.list_tools()
        finally:
            client.close()
        si = info.get("serverInfo", {})
        lines = [f"MCP server {name} ({si.get('name', '?')} {si.get('version', '')}) — {len(tools)} tool(s):"]
        for t in tools:
            props = list(((t.get("inputSchema") or {}).get("properties") or {}).keys())
            lines.append(f"- {t.get('name')}: {_one_line(t.get('description', ''))[:160]}" + (f"  args: {', '.join(props[:12])}" if props else ""))
        return "\n".join(lines)

    def _do_mcp_call(self, name="", tool="", arguments=None, **kw):
        if not tool:
            return "Pass tool=<name> (see action='mcp_tools')."
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments) if arguments.strip() else {}
            except ValueError:
                return "arguments must be a JSON object"
        client, err = self._mcp(name, kw)
        if err:
            return err
        try:
            client.initialize()
            res = client.call_tool(tool, arguments or {})
        finally:
            client.close()
        parts = [c.get("text", "") if c.get("type") == "text" else f"[{c.get('type')} content omitted]" for c in (res.get("content") or [])]
        text = "\n".join(parts) if parts else json.dumps(res.get("structuredContent", res), indent=2)
        return ("ERROR from tool: " if res.get("isError") else "") + _clip(text, 40_000)

    # -- install / uninstall -------------------------------------------------
    def _do_install(self, source="", name="", **kw):
        if not source:
            return "Pass source=<local path or git URL>."
        store = os.path.join(_store_dir(), "plugins")
        os.makedirs(store, exist_ok=True)
        src = os.path.expanduser(source)
        if re.match(r"^(https?://|git@|ssh://)", source) or source.endswith(".git"):
            tmp = os.path.join(_store_dir(), "tmp_clone_" + hashlib.sha1(source.encode()).hexdigest()[:8])
            shutil.rmtree(tmp, ignore_errors=True)
            res = _run_subprocess(["git", "clone", "--depth", "1", source, tmp], cwd=_store_dir(), timeout=self._timeout(kw))
            if res["exit"] != 0:
                return f"git clone failed: {res['stderr'][:500]}"
            src = tmp
        if not os.path.isdir(src):
            return f"Source {source!r} is not a directory."
        manifest = None
        for m in (".claude-plugin/plugin.json", "plugin.json"):
            if os.path.isfile(os.path.join(src, m)):
                try:
                    manifest = json.loads(_safe_read(os.path.join(src, m)))
                except ValueError:
                    return f"{os.path.join(src, m)} is not valid JSON."
                break
        if manifest is None:
            if os.path.isfile(os.path.join(src, "SKILL.md")):
                meta, _b = _parse_frontmatter(_safe_read(os.path.join(src, "SKILL.md")))
                sname = str(meta.get("name") or os.path.basename(src.rstrip(os.sep)))
                pname = name or sname
                dest = os.path.join(store, pname)
                shutil.rmtree(dest, ignore_errors=True)
                os.makedirs(os.path.join(dest, "skills"), exist_ok=True)
                shutil.copytree(src, os.path.join(dest, "skills", sname))
                with open(os.path.join(dest, "plugin.json"), "w") as f:
                    json.dump({"name": pname, "version": "0.0.0", "description": str(meta.get("description", ""))[:300],
                               "_wrapped_by": "HostCompat"}, f, indent=2)
                _get_catalog(force=True)
                return f"Installed bare skill {sname!r} as plugin {pname!r} at {dest}"
            return f"{src} has no plugin.json/.claude-plugin/plugin.json and no SKILL.md."
        pname = name or str(manifest.get("name") or os.path.basename(src.rstrip(os.sep)))
        dest = os.path.join(store, pname)
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__", ".in_use"))
        if src.startswith(os.path.join(_store_dir(), "tmp_clone_")):
            shutil.rmtree(src, ignore_errors=True)
        cat = _get_catalog(force=True)
        p = cat.plugins.get(pname, {})
        return (f"Installed plugin {pname!r} v{manifest.get('version', '?')} at {dest}: skills={len(p.get('skills', []))} "
                f"commands={len(p.get('commands', []))} agents={len(p.get('agents', []))} hooks={p.get('hooks', 0)} mcp={len(p.get('mcp', []))}")

    def _do_uninstall(self, name="", **_):
        dest = os.path.join(_store_dir(), "plugins", (name or "").strip())
        if not name or not os.path.isdir(dest):
            return f"No Brainstem-installed plugin named {name!r} (only plugins installed via action='install' can be removed here)."
        shutil.rmtree(dest)
        _get_catalog(force=True)
        return f"Removed plugin {name!r} from {dest}"

    # -- promote (skill -> native agent) -------------------------------------
    def _do_promote(self, name="", host="", **_):
        cat = _get_catalog()
        item = cat.find(name, self._host_filter(host))
        if item is None or item["kind"] != "skill":
            return f"No skill named {name!r}."
        meta, body = _parse_frontmatter(_safe_read(item["path"], 400_000))
        slug = _slug(item["short"])
        tool_name = "Skill" + _camel(slug)
        class_name = tool_name + "Agent"
        desc = _one_line(item["description"])[:900] or f"Skill {item['short']}"
        agents_dir = os.path.dirname(os.path.abspath(__file__))
        out_path = os.path.join(agents_dir, f"skill_{slug}_agent.py")
        sha = hashlib.sha256(_safe_read(item["path"]).encode()).hexdigest()
        code = _PROMOTED_TEMPLATE.format(
            class_name=class_name, skill_name=item["short"], sha=sha, skill_dir=item["dir"], body=body.strip(),
            meta={k: v for k, v in meta.items() if isinstance(v, (str, int, float, bool, list, dict))},
            tool_name=tool_name, description=desc)
        ast.parse(code, filename=out_path)  # never write an agent that cannot parse
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(code)
        return f"Promoted skill {item['name']!r} ({item['host']}) to native agent {tool_name} at {out_path}. It is live on the next /chat."

    # -- export (agent -> SKILL.md) ------------------------------------------
    def _do_export(self, name="", path="", **_):
        agents_dir = os.path.dirname(os.path.abspath(__file__))
        cand = (name or "").strip()
        if not cand:
            return "Pass name=<agent file or tool name>."
        agent_file = None
        for fp in sorted(glob.glob(os.path.join(agents_dir, "*_agent.py"))):
            base = os.path.basename(fp)
            if cand in (base, base[:-3], base[:-9]) or cand.lower() == base[:-9].replace("_", "").lower():
                agent_file = fp
                break
        if agent_file is None:
            for fp in sorted(glob.glob(os.path.join(agents_dir, "*_agent.py"))):
                if re.search(r"self\.name\s*=\s*['\"]" + re.escape(cand) + r"['\"]", _safe_read(fp)):
                    agent_file = fp
                    break
        if agent_file is None:
            return f"No agent file matching {cand!r} in {agents_dir}."
        src = _safe_read(agent_file)
        m_name = re.search(r"self\.name\s*=\s*['\"]([^'\"]+)['\"]", src)
        m_desc = re.search(r"['\"]description['\"]\s*:\s*\(?\s*((?:['\"][^'\"]*['\"]\s*)+)", src)
        tool = m_name.group(1) if m_name else os.path.basename(agent_file)[:-9]
        desc = " ".join(re.findall(r"['\"]([^'\"]*)['\"]", m_desc.group(1))) if m_desc else ""
        skill_name = _slug(tool).replace("_", "-")
        out_root = os.path.expanduser(path) if path else os.path.join(_store_dir(), "exported_skills")
        sdir = os.path.join(out_root, skill_name)
        os.makedirs(os.path.join(sdir, "scripts"), exist_ok=True)
        shutil.copy(agent_file, os.path.join(sdir, "scripts", "agent.py"))
        runner = (
            "#!/usr/bin/env python3\n\"\"\"Run the bundled RAPP agent: python3 run.py --json '{...}'\"\"\"\n"
            "import importlib.util, json, os, sys, types\n"
            "here = os.path.dirname(os.path.abspath(__file__))\n"
            "pkg = types.ModuleType('agents'); pkg.__path__ = []\n"
            "ba = types.ModuleType('agents.basic_agent')\n"
            "class BasicAgent:\n"
            "    def __init__(self, name=None, metadata=None):\n"
            "        self.name = getattr(self, 'name', name or 'BasicAgent')\n"
            "        self.metadata = getattr(self, 'metadata', metadata or {})\n"
            "    def perform(self, **kw): return 'Not implemented.'\n"
            "    def system_context(self): return None\n"
            "ba.BasicAgent = BasicAgent; pkg.basic_agent = ba\n"
            "sys.modules.setdefault('agents', pkg); sys.modules.setdefault('agents.basic_agent', ba)\n"
            "spec = importlib.util.spec_from_file_location('skill_agent', os.path.join(here, 'agent.py'))\n"
            "mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)\n"
            "cls = next(c for c in vars(mod).values() if isinstance(c, type) and c is not BasicAgent and hasattr(c, 'perform') and c.__module__ == mod.__name__)\n"
            "args = json.loads(sys.argv[sys.argv.index('--json') + 1]) if '--json' in sys.argv else {}\n"
            "print(cls().perform(**args))\n")
        with open(os.path.join(sdir, "scripts", "run.py"), "w") as f:
            f.write(runner)
        sha = hashlib.sha256(src.encode()).hexdigest()
        fm_desc = (desc or f"RAPP agent {tool} exported from the Brainstem.").replace('"', "'")[:1000]
        skill_md = (
            "---\n"
            f"name: \"{skill_name}\"\n"
            f"description: \"{fm_desc}\"\n"
            "license: \"MIT\"\n"
            "compatibility: \"Requires python3 (3.11+). Works in Claude Code, GitHub Copilot CLI and any Agent Skills host.\"\n"
            "metadata:\n"
            f"  rapp-tool: \"{tool}\"\n"
            f"  agent-sha256: \"{sha}\"\n"
            "  source: \"rapp-brainstem HostCompat export\"\n"
            "---\n\n"
            f"# {tool}\n\n{desc or 'A RAPP single-file agent.'}\n\n"
            "## Run\n\n"
            "This skill carries the agent verbatim in `scripts/agent.py`. Execute it with:\n\n"
            "```bash\npython3 scripts/run.py --json '{\"...\": \"...\"}'\n```\n\n"
            "Pass the agent's parameters as the JSON object. To run it server-side, drop `scripts/agent.py` into a RAPP Brainstem `agents/` folder.\n"
            "Install: copy this folder to `~/.claude/skills/`, `~/.copilot/skills/`, `<project>/.github/skills/` or `<project>/.agents/skills/`.\n")
        with open(os.path.join(sdir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(skill_md)
        return f"Exported {tool} to skill {skill_name!r} at {sdir} (SKILL.md, scripts/agent.py, scripts/run.py)."

    # -- instructions --------------------------------------------------------
    def _do_instructions(self, host="", name="", **_):
        cat = _get_catalog()
        hf = self._host_filter(host)
        rows = [i for i in cat.instructions if (not hf or i["host"] == hf) and (not name or name.lower() in i["path"].lower())]
        if not rows:
            return "No instruction files (CLAUDE.md, AGENTS.md, .github/copilot-instructions.md, .github/instructions/*.instructions.md) found."
        out, total = [], 0
        for i in rows:
            body = _safe_read(i["path"], 200_000)
            out.append(f"===== {i['path']} [{i['host']}] =====\n{_clip(body, 20_000)}")
            total += len(body)
            if total > 60_000:
                out.append("... (remaining instruction files omitted; pass name=<filename> to read one)")
                break
        return "\n\n".join(out)

    # -- transcripts ---------------------------------------------------------
    def _index(self):
        return _TranscriptIndex(os.path.join(_store_dir(), "transcripts.db"))

    def _do_index(self, days=None, **kw):
        days = int(days or _int_env("HOST_COMPAT_TRANSCRIPT_DAYS", 30))
        idx = self._index()
        try:
            r = idx.refresh(days, self._timeout(kw))
            return (f"Transcript index: indexed {r['indexed_now']} session file(s) this pass in {r['seconds']}s; "
                    f"{r['pending']} still pending of {r['in_window']} in the last {days} days. "
                    + ("Call action='index' again to continue. " if r["pending"] else "Index is complete. ")
                    + f"Totals: {json.dumps(idx.stats())}")
        finally:
            idx.close()

    def _do_transcripts(self, query="", host="", role="", cwd="", days=None, limit=20, **kw):
        if not (query or "").strip():
            return "Pass query=<search terms>. Optional: host=claude-code|copilot-cli, role=user|assistant, cwd=<path fragment>, days=N."
        days = int(days or _int_env("HOST_COMPAT_TRANSCRIPT_DAYS", 30))
        idx = self._index()
        try:
            r = idx.refresh(days, min(self._timeout(kw), _int_env("HOST_COMPAT_INDEX_BUDGET", 15)))
            since = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - days * 86400))
            hits = idx.search(query, self._host_filter(host), role or None, cwd or None,
                              max(1, min(int(limit or 20), 100)), since_iso=since)
            lines = [f"Transcript search for {query!r}: {len(hits)} hit(s)"
                     + (f"; index still catching up ({r['pending']} session files pending, run action='index')" if r["pending"] else "")]
            for h, session, rl, ts, c, path, title, snip in hits:
                lines.append(f"- [{h}] {ts[:19]} {rl} session={session[:8]}… cwd={c or '?'}" + (f" title={title!r}" if title else "")
                             + f"\n    {_one_line(snip)[:300]}")
            if not hits:
                lines.append("No matches. Try fewer/other terms, a larger days=, or host='all'.")
            lines.append("Read a session with action='transcript' name=<session id prefix>.")
            return "\n".join(lines)
        finally:
            idx.close()

    def _do_transcript(self, name="", limit=200, days=None, **kw):
        if not name:
            return "Pass name=<session id or prefix>."
        days = int(days or _int_env("HOST_COMPAT_TRANSCRIPT_DAYS", 30))
        idx = self._index()
        try:
            idx.refresh(days, min(self._timeout(kw), _int_env("HOST_COMPAT_INDEX_BUDGET", 15)))
            rows = idx.session(name.strip(), max(1, min(int(limit or 200), 1000)))
        finally:
            idx.close()
        if not rows:
            return f"No indexed session matching {name!r} (search first with action='transcripts', or run action='index')."
        head = rows[0]
        out = [f"Session {name} [{head[5]}] cwd={head[3]}" + (f" title={head[4]!r}" if head[4] else "") + f"\nFile: {head[6]}\n"]
        total = 0
        for role, ts, text, *_r in rows:
            piece = f"[{ts[:19]}] {role.upper()}: {text}"
            total += len(piece)
            if total > 50_000:
                out.append("... (clipped; raise limit= or read the file directly)")
                break
            out.append(piece)
        return "\n\n".join(out)

    # -- doctor / refresh ----------------------------------------------------
    def _do_doctor(self, **_):
        cat = _get_catalog(force=True)
        lines = ["HostCompat doctor"]
        for hkey, host in _hosts().items():
            home = _host_home(host)
            n_sk = sum(1 for i in cat.skills.values() if i["host"] == hkey)
            n_pl = sum(1 for p in cat.plugins.values() if p["host"] == hkey)
            n_mcp = sum(1 for e in cat.mcp.values() if e["host"] == hkey)
            tr = host.get("transcripts")
            n_tr = len(_expand_paths(tr["glob"], host)) if tr else 0
            lines.append(f"- {host.get('display', hkey)} [{hkey}]: home={home} ({'ok' if os.path.isdir(home) else 'missing'}) "
                         f"skills={n_sk} plugins={n_pl} mcp={n_mcp} transcript files={n_tr}")
        lines += [f"project dir: {_project_dir()}", f"store: {_store_dir()}",
                  f"skill roots: {', '.join(cat.roots) or 'none'}",
                  f"totals: skills={len(cat.skills)} commands={len(cat.commands)} personas={len(cat.agents)} plugins={len(cat.plugins)} "
                  f"hooks={len(cat.hooks)} mcp={len(cat.mcp)} instruction files={len(cat.instructions)}",
                  f"catalog context budget: {_int_env('HOST_COMPAT_CONTEXT_CHARS', 6000)} chars; current: {len(self.system_context() or '')} chars"]
        try:
            idx = self._index()
            lines.append(f"transcript index: {'FTS5' if idx.fts else 'LIKE fallback'} at {os.path.join(_store_dir(), 'transcripts.db')}; {json.dumps(idx.stats())}")
            idx.close()
        except Exception as e:
            lines.append(f"transcript index unavailable: {e}")
        lines.append(f"python: {sys.executable}; git: {'yes' if shutil.which('git') else 'no'}; node: {'yes' if shutil.which('node') else 'no'}")
        if cat.errors:
            lines.append("errors:")
            lines += [f"  - {e}" for e in cat.errors[:30]]
        return "\n".join(lines)

    def _do_refresh(self, **_):
        cat = _get_catalog(force=True)
        return (f"Catalog rebuilt: skills={len(cat.skills)} commands={len(cat.commands)} personas={len(cat.agents)} "
                f"plugins={len(cat.plugins)} hooks={len(cat.hooks)} mcp={len(cat.mcp)} instruction files={len(cat.instructions)}")


if __name__ == "__main__":
    # Standalone use: python host_compat_agent.py [action] [key=value ...]
    _argv = sys.argv[1:]
    _action = _argv[0] if _argv and "=" not in _argv[0] else "doctor"
    _kw = dict(a.split("=", 1) for a in _argv if "=" in a)
    print(HostCompatAgent().perform(action=_action, **_kw))
