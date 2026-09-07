"""ClaudeCompat -- make the Brainstem speak every Claude Code / Anthropic dialect
(Agent Skills, plugins, slash commands, subagents, hooks, MCP servers) from ONE
agent file, without teaching the kernel any of it.

Why an agent and not a kernel feature: the kernel stays "engine, not experience".
Everything Anthropic-shaped is a cartridge you can drop in, delete, or replace.

What it does better than the originals:
  * Progressive disclosure that actually fits: a capped, cached catalog goes into
    the system prompt each turn so skills auto-trigger, but the body only loads
    on demand (action="load"), and bundled references only on action="read".
  * Skills are first-class tools: action="promote" compiles any SKILL.md into a
    standalone <slug>_agent.py that the Brainstem loads like any other agent, and
    action="export" turns any agent into a SKILL.md folder Claude Code can read.
  * Slash commands, subagent personas and hooks are all plain files; here they are
    all discoverable, loadable and runnable with the same four verbs.
  * MCP servers from .mcp.json / ~/.claude.json are callable directly (stdio and
    streamable-HTTP) -- no host process required.

Everything is stdlib-only. Every subprocess has a timeout. Paths handed in by the
model are confined to the skill/plugin directory they belong to.

Environment (all optional):
  CLAUDE_COMPAT_HOME      Claude home to scan (default ~/.claude)
  CLAUDE_COMPAT_PROJECT   project dir whose .claude/ and .mcp.json are scanned
                          (default: current working directory)
  CLAUDE_COMPAT_ROOTS     extra colon-separated dirs containing */SKILL.md
  CLAUDE_COMPAT_STORE     where installed plugins live (default ~/.brainstem/claude_compat)
  CLAUDE_COMPAT_CONTEXT_CHARS  cap on the per-turn catalog (default 6000; 0 disables)
  CLAUDE_COMPAT_TIMEOUT   default subprocess timeout in seconds (default 120)
"""

import glob
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
import urllib.request

from agents.basic_agent import BasicAgent

# ── configuration ───────────────────────────────────────────────────────────

def _env(name, default):
    v = os.getenv(name)
    return v if v not in (None, "") else default


def _claude_home():
    return os.path.expanduser(_env("CLAUDE_COMPAT_HOME", "~/.claude"))


def _project_dir():
    return os.path.abspath(_env("CLAUDE_COMPAT_PROJECT", os.getcwd()))


def _store_dir():
    return os.path.expanduser(_env("CLAUDE_COMPAT_STORE", "~/.brainstem/claude_compat"))


def _default_timeout():
    try:
        return int(_env("CLAUDE_COMPAT_TIMEOUT", "120"))
    except ValueError:
        return 120


def _context_chars():
    try:
        return int(_env("CLAUDE_COMPAT_CONTEXT_CHARS", "6000"))
    except ValueError:
        return 6000


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
    """Return (meta_dict, body). Handles scalars, one-level nested maps,
    block lists and folded/literal strings well enough for SKILL.md / commands."""
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
            meta[key] = (" " if rest.startswith(">") else "\n").join(x for x in buf).strip()
            continue
        if rest == "":
            # nested map or list
            sub = {}
            lst = []
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


# ── discovery ───────────────────────────────────────────────────────────────

_SKILL_SUBDIRS = ("scripts", "references", "assets", "templates", "examples")


def _safe_read(path, limit=None):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read() if limit is None else f.read(limit)
    except OSError:
        return ""


def _plugin_manifest(pdir):
    for cand in (os.path.join(pdir, ".claude-plugin", "plugin.json"), os.path.join(pdir, "plugin.json")):
        if os.path.isfile(cand):
            try:
                return json.loads(_safe_read(cand)), cand
            except ValueError:
                # cache layout is <marketplace>/<plugin>/<version>; name the plugin, not its version dir
                base = os.path.basename(pdir.rstrip(os.sep))
                if re.match(r"^[0-9a-f.\-]+$", base):
                    base = os.path.basename(os.path.dirname(pdir.rstrip(os.sep)))
                return {"name": base, "_error": f"invalid JSON in {cand}"}, cand
    return None, None


def _tree_mtime(paths):
    """Cheap change signal: mtimes of the root dirs and their immediate children."""
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


class _Catalog:
    """Everything Claude-shaped that is reachable from this machine."""

    def __init__(self):
        self.skills = {}     # name -> dict(path, dir, meta, source, plugin)
        self.commands = {}   # name -> dict(path, meta, plugin)
        self.agents = {}     # name -> dict(path, meta, plugin)
        self.plugins = {}    # name -> dict(dir, manifest, components...)
        self.hooks = []      # list of dict(plugin/source, event, matcher, command, cwd)
        self.mcp = {}        # name -> dict(config, source, cwd)
        self.errors = []
        self.roots = []

    # -- roots ---------------------------------------------------------------
    def skill_roots(self):
        home, proj = _claude_home(), _project_dir()
        roots = [os.path.join(proj, ".claude", "skills"), os.path.join(home, "skills")]
        extra = _env("CLAUDE_COMPAT_ROOTS", "")
        roots += [os.path.expanduser(r) for r in extra.split(os.pathsep) if r.strip()]
        return [r for r in roots if os.path.isdir(r)]

    def plugin_dirs(self):
        """(plugin_dir, source) for every installed/cached plugin."""
        found = []
        seen = set()
        home = _claude_home()

        def add(d, src):
            d = os.path.abspath(d)
            if d in seen or not os.path.isdir(d):
                return
            seen.add(d)
            found.append((d, src))

        inst = os.path.join(home, "plugins", "installed_plugins.json")
        if os.path.isfile(inst):
            try:
                data = json.loads(_safe_read(inst))
                for key, entries in (data.get("plugins") or {}).items():
                    for e in entries if isinstance(entries, list) else [entries]:
                        ip = e.get("installPath")
                        if ip:
                            add(ip, f"installed:{e.get('scope', '?')}")
            except ValueError:
                self.errors.append(f"invalid JSON: {inst}")
        for d in glob.glob(os.path.join(home, "plugins", "cache", "*", "*", "*")):
            if _plugin_manifest(d)[0] is not None:
                add(d, "cache")
        for d in glob.glob(os.path.join(_store_dir(), "plugins", "*")):
            if _plugin_manifest(d)[0] is not None:
                add(d, "brainstem-store")
        return found

    # -- scanning ------------------------------------------------------------
    def _add_skill(self, skill_md, source, plugin=None):
        meta, body = _parse_frontmatter(_safe_read(skill_md, 200_000))
        sdir = os.path.dirname(skill_md)
        name = str(meta.get("name") or os.path.basename(sdir)).strip()
        if plugin:
            qualified = f"{plugin}:{name}"
        else:
            qualified = name
        if qualified in self.skills:
            # first wins (project > user > plugins), mirror Claude Code precedence
            return
        desc = str(meta.get("description") or body.strip().split("\n", 1)[0][:200]).strip()
        self.skills[qualified] = {
            "kind": "skill", "name": qualified, "short": name, "path": skill_md, "dir": sdir,
            "description": desc, "meta": meta, "source": source, "plugin": plugin,
        }

    def _scan_skill_root(self, root, source, plugin=None):
        for skill_md in sorted(glob.glob(os.path.join(root, "*", "SKILL.md"))):
            self._add_skill(skill_md, source, plugin)
        # nested skills (skills/<group>/<name>/SKILL.md) are allowed by the spec
        for skill_md in sorted(glob.glob(os.path.join(root, "*", "*", "SKILL.md"))):
            self._add_skill(skill_md, source, plugin)

    def _scan_md_dir(self, root, bucket, kind, source, plugin=None):
        for path in sorted(glob.glob(os.path.join(root, "**", "*.md"), recursive=True)):
            meta, body = _parse_frontmatter(_safe_read(path, 200_000))
            rel = os.path.relpath(path, root)[:-3].replace(os.sep, ":")
            name = str(meta.get("name") or rel)
            qualified = f"{plugin}:{name}" if plugin else name
            if qualified in bucket:
                continue
            desc = str(meta.get("description") or body.strip().split("\n", 1)[0][:200]).strip()
            bucket[qualified] = {
                "kind": kind, "name": qualified, "short": name, "path": path, "dir": os.path.dirname(path),
                "description": desc, "meta": meta, "source": source, "plugin": plugin,
            }

    def _scan_hooks(self, hooks_json, source, plugin_root):
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
                for h in (g.get("hooks") or []) if isinstance(g, dict) else []:
                    if h.get("type", "command") != "command":
                        continue
                    self.hooks.append({
                        "source": source, "event": event, "matcher": g.get("matcher", ""),
                        "command": h.get("command", ""), "timeout": h.get("timeout"),
                        "cwd": plugin_root, "file": hooks_json,
                    })

    def _scan_mcp(self, path, source, cwd, key="mcpServers"):
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
                self.mcp[name] = {"config": cfg, "source": source, "cwd": cwd, "file": path}

    def scan(self):
        home, proj = _claude_home(), _project_dir()
        self.roots = self.skill_roots()
        for root in self.roots:
            self._scan_skill_root(root, "project" if root.startswith(proj) else "user")
        for root, bucket, kind in (
            (os.path.join(proj, ".claude", "commands"), self.commands, "command"),
            (os.path.join(home, "commands"), self.commands, "command"),
            (os.path.join(proj, ".claude", "agents"), self.agents, "agent"),
            (os.path.join(home, "agents"), self.agents, "agent"),
        ):
            if os.path.isdir(root):
                self._scan_md_dir(root, bucket, kind, "project" if root.startswith(proj) else "user")
        for pdir, source in self.plugin_dirs():
            manifest, mpath = _plugin_manifest(pdir)
            if manifest is None:
                # installed_plugins.json can point at a plugin folder with no manifest
                # (skills-only marketplaces do this); treat it as a bare plugin named
                # after its plugin directory, not its version directory.
                base = os.path.basename(pdir.rstrip(os.sep))
                if re.match(r"^[0-9a-f.\-]+$", base):
                    base = os.path.basename(os.path.dirname(pdir.rstrip(os.sep)))
                manifest, mpath = {"name": base, "_bare": True}, None
            pname = str(manifest.get("name") or os.path.basename(pdir))
            if "_error" in manifest:
                self.errors.append(manifest["_error"])
            if pname in self.plugins:
                continue
            entry = {"name": pname, "dir": pdir, "manifest": manifest, "manifest_path": mpath, "source": source,
                     "skills": [], "commands": [], "agents": [], "hooks": 0, "mcp": []}
            self.plugins[pname] = entry
            before = set(self.skills)
            for sroot in (os.path.join(pdir, "skills"),):
                if os.path.isdir(sroot):
                    self._scan_skill_root(sroot, f"plugin:{source}", pname)
            entry["skills"] = sorted(set(self.skills) - before)
            before = set(self.commands)
            if os.path.isdir(os.path.join(pdir, "commands")):
                self._scan_md_dir(os.path.join(pdir, "commands"), self.commands, "command", f"plugin:{source}", pname)
            entry["commands"] = sorted(set(self.commands) - before)
            before = set(self.agents)
            if os.path.isdir(os.path.join(pdir, "agents")):
                self._scan_md_dir(os.path.join(pdir, "agents"), self.agents, "agent", f"plugin:{source}", pname)
            entry["agents"] = sorted(set(self.agents) - before)
            nh = len(self.hooks)
            for hj in (os.path.join(pdir, "hooks", "hooks.json"), os.path.join(pdir, "hooks.json")):
                if os.path.isfile(hj):
                    self._scan_hooks(hj, f"plugin:{pname}", pdir)
                    break
            entry["hooks"] = len(self.hooks) - nh
            before = set(self.mcp)
            mcp_file = manifest.get("mcpServers") if isinstance(manifest.get("mcpServers"), str) else ".mcp.json"
            mp = os.path.join(pdir, mcp_file)
            if os.path.isfile(mp):
                self._scan_mcp(mp, f"plugin:{pname}", pdir)
            elif isinstance(manifest.get("mcpServers"), dict):
                for n, cfg in manifest["mcpServers"].items():
                    self.mcp.setdefault(n, {"config": cfg, "source": f"plugin:{pname}", "cwd": pdir, "file": mpath})
            entry["mcp"] = sorted(set(self.mcp) - before)
        # project + user MCP and project hooks
        if os.path.isfile(os.path.join(proj, ".mcp.json")):
            self._scan_mcp(os.path.join(proj, ".mcp.json"), "project", proj)
        user_cfg = os.path.join(os.path.dirname(home.rstrip(os.sep)), ".claude.json") if os.path.basename(home.rstrip(os.sep)) == ".claude" else os.path.join(home, ".claude.json")
        if os.path.isfile(user_cfg):
            self._scan_mcp(user_cfg, "user", proj)
        for sj in (os.path.join(proj, ".claude", "settings.json"), os.path.join(proj, ".claude", "settings.local.json")):
            if os.path.isfile(sj):
                self._scan_hooks(sj, "project-settings", proj)
        return self

    def find(self, name):
        """Resolve a name across skills, commands and agents (exact, then short, then fuzzy)."""
        if not name:
            return None
        n = name.strip().lstrip("/")
        for bucket in (self.skills, self.commands, self.agents):
            if n in bucket:
                return bucket[n]
        for bucket in (self.skills, self.commands, self.agents):
            for item in bucket.values():
                if item["short"] == n:
                    return item
        low = n.lower()
        for bucket in (self.skills, self.commands, self.agents):
            for key, item in bucket.items():
                if low == key.lower() or low == item["short"].lower():
                    return item
        return None


_catalog_cache = {"sig": None, "catalog": None, "built": 0.0}
_catalog_lock = threading.Lock()


def _get_catalog(force=False):
    home, proj = _claude_home(), _project_dir()
    sig_paths = [os.path.join(home, "skills"), os.path.join(home, "plugins"), os.path.join(home, "commands"),
                 os.path.join(home, "agents"), os.path.join(proj, ".claude"), os.path.join(_store_dir(), "plugins")]
    sig = (home, proj, _env("CLAUDE_COMPAT_ROOTS", ""), _tree_mtime(sig_paths))
    with _catalog_lock:
        if not force and _catalog_cache["catalog"] is not None and _catalog_cache["sig"] == sig \
                and time.time() - _catalog_cache["built"] < 300:
            return _catalog_cache["catalog"]
        cat = _Catalog().scan()
        _catalog_cache.update({"sig": sig, "catalog": cat, "built": time.time()})
        return cat


# ── helpers ────────────────────────────────────────────────────────────────

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
    extra = max(0, len(out) - limit)
    return out[:limit], extra


def _substitute_arguments(body, args):
    """Claude Code slash-command substitution: $ARGUMENTS, $1..$9, ${CLAUDE_*}."""
    if isinstance(args, (list, tuple)):
        parts = [str(a) for a in args]
    elif args is None:
        parts = []
    else:
        parts = shlex.split(str(args)) if str(args).strip() else []
    joined = " ".join(parts)
    out = body.replace("$ARGUMENTS", joined)
    for i in range(1, 10):
        out = out.replace(f"${i}", parts[i - 1] if len(parts) >= i else "")
    return out


def _expand_cmd(cmd, plugin_root):
    """Expand ${CLAUDE_PLUGIN_ROOT} plus any ${VAR} / ${VAR:-default} from the environment,
    the way Claude Code expands .mcp.json and hooks."""
    out = (cmd.replace("${CLAUDE_PLUGIN_ROOT}", plugin_root or "")
              .replace("$CLAUDE_PLUGIN_ROOT", plugin_root or ""))

    def sub(m):
        var, default = m.group(1), m.group(3)
        return os.environ.get(var, default if default is not None else m.group(0))

    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(:-([^}]*))?\}", sub, out)


def _run_subprocess(argv, cwd, timeout, stdin_text=None, env_extra=None, shell=False):
    env = dict(os.environ)
    env.update({k: str(v) for k, v in (env_extra or {}).items()})
    started = time.time()
    try:
        proc = subprocess.run(
            argv, cwd=cwd, input=stdin_text, capture_output=True, text=True, timeout=timeout,
            env=env, shell=shell,
        )
        return {"exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr,
                "seconds": round(time.time() - started, 2)}
    except subprocess.TimeoutExpired as e:
        return {"exit": None, "stdout": (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""),
                "stderr": f"timed out after {timeout}s", "seconds": timeout}
    except FileNotFoundError as e:
        return {"exit": 127, "stdout": "", "stderr": str(e), "seconds": 0}


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


# ── MCP client (stdio + streamable HTTP) ───────────────────────────────────

_MCP_PROTOCOL = "2025-06-18"


class _McpClient:
    def __init__(self, name, entry, timeout):
        self.name = name
        self.cfg = entry["config"]
        self.cwd = entry.get("cwd") or None
        self.timeout = timeout
        self.proc = None
        self._id = 0
        self._lines = []
        self._reader = None
        self._lock = threading.Lock()
        self.kind = (self.cfg.get("type") or ("http" if self.cfg.get("url") else "stdio")).lower()
        self.session_id = None

    # -- transport -----------------------------------------------------------
    def _start_stdio(self):
        command = _expand_cmd(str(self.cfg.get("command", "")), self.cwd)
        args = [_expand_cmd(str(a), self.cwd) for a in (self.cfg.get("args") or [])]
        env = dict(os.environ)
        env.update({k: _expand_cmd(str(v), self.cwd) for k, v in (self.cfg.get("env") or {}).items()})
        self.proc = subprocess.Popen(
            [command] + args, cwd=self.cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1,
        )

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
        if self.kind == "stdio":
            return self._rpc_stdio(msg, notify)
        return self._rpc_http(msg, notify)

    def _rpc_stdio(self, msg, notify):
        if self.proc is None:
            self._start_stdio()
        if self.proc.poll() is not None:
            err = self.proc.stderr.read() if self.proc.stderr else ""
            raise RuntimeError(f"MCP server {self.name!r} exited early: {err[:500]}")
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        if notify:
            return None
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            with self._lock:
                pending, self._lines = self._lines, []
            for line in pending:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                if obj.get("id") == msg["id"]:
                    if "error" in obj:
                        raise RuntimeError(f"MCP error from {self.name!r}: {json.dumps(obj['error'])[:800]}")
                    return obj.get("result")
            if self.proc.poll() is not None:
                err = self.proc.stderr.read() if self.proc.stderr else ""
                raise RuntimeError(f"MCP server {self.name!r} exited: {err[:500]}")
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
        payloads = []
        if "text/event-stream" in ctype:
            for line in raw.splitlines():
                if line.startswith("data:"):
                    payloads.append(line[5:].strip())
        else:
            payloads.append(raw)
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

    # -- protocol ------------------------------------------------------------
    def initialize(self):
        res = self._rpc("initialize", {
            "protocolVersion": _MCP_PROTOCOL, "capabilities": {},
            "clientInfo": {"name": "rapp-brainstem-claude-compat", "version": "1.0"},
        })
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


# ── promoted-agent template (skill -> native brainstem tool) ───────────────

_PROMOTED_TEMPLATE = '''"""{class_name} -- Claude Code skill {skill_name!r} promoted into a native RAPP agent.

Generated by ClaudeCompat (action="promote"). Self-contained: the SKILL.md body is
embedded, and bundled scripts still run from the original skill directory when it
exists. Regenerate with ClaudeCompat rather than editing the embedded body.
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

class ClaudeCompatAgent(BasicAgent):
    def __init__(self):
        self.name = "ClaudeCompat"
        self.metadata = {
            "name": self.name,
            "description": (
                "Bridge to everything Claude Code / Anthropic-shaped on this machine: Agent Skills (SKILL.md), "
                "plugins, slash commands, subagent personas, hooks and MCP servers. Use action='list' to see what "
                "exists, action='load' to pull a skill/command/persona's instructions into the conversation before "
                "doing that kind of work, action='read' for a bundled reference file, action='run' to execute a "
                "skill's bundled script, action='mcp_tools'/'mcp_call' to use an MCP server's tools, "
                "action='install' to add a plugin from a local path or git URL, action='promote' to compile a skill "
                "into a native Brainstem agent, action='export' to turn an agent into a SKILL.md, action='hook' to "
                "fire a plugin hook, and action='doctor' for a health report."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "load", "read", "run", "hook", "mcp_tools", "mcp_call",
                                 "install", "uninstall", "promote", "export", "doctor", "refresh"],
                        "description": "What to do.",
                    },
                    "name": {"type": "string", "description": "Skill / command / persona / plugin / MCP server / agent name (plugin-qualified 'plugin:name' allowed)."},
                    "kind": {"type": "string", "enum": ["all", "skills", "plugins", "commands", "agents", "hooks", "mcp"],
                             "description": "For list: which catalog to show (default all)."},
                    "query": {"type": "string", "description": "For list: substring filter on name/description."},
                    "path": {"type": "string", "description": "For read/run: file path relative to the skill or plugin directory."},
                    "args": {"type": "string", "description": "For load (slash-command $ARGUMENTS), run (script arguments), or hook (matcher/tool name)."},
                    "stdin": {"type": "string", "description": "For run/hook: text (usually JSON) sent to the process on stdin."},
                    "tool": {"type": "string", "description": "For mcp_call: the MCP tool name."},
                    "arguments": {"type": "object", "description": "For mcp_call: the tool's arguments object."},
                    "source": {"type": "string", "description": "For install: local directory path or git URL of a plugin (or a bare skill folder)."},
                    "timeout": {"type": "integer", "description": "Seconds to allow a script/hook/MCP call (default 120)."},
                },
                "required": ["action"],
            },
        }
        super().__init__()

    # -- system prompt catalog (progressive disclosure, capped) --------------
    def system_context(self):
        cap = _context_chars()
        if cap <= 0:
            return None
        try:
            cat = _get_catalog()
        except Exception as e:  # never break /chat
            return f"<claude_compat>catalog unavailable: {e}</claude_compat>"
        if not (cat.skills or cat.commands or cat.agents or cat.mcp):
            return None
        head = (
            "<claude_compat>\nClaude Code skills, commands, personas and MCP servers are available through the "
            "ClaudeCompat tool. When a task matches an entry below, call ClaudeCompat(action=\"load\", name=...) "
            "FIRST and follow the returned instructions; use action=\"list\" with a query for the full catalog.\n"
        )
        tail = "</claude_compat>"
        budget = cap - len(head) - len(tail) - 64  # 64 keeps the "+N more" trailer inside the cap

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
            section("Slash commands", cat.commands)
            section("Subagent personas", cat.agents)
            if cat.mcp:
                lines.append(f"MCP servers ({len(cat.mcp)}): " + ", ".join(sorted(cat.mcp)) +
                             "  (action=\"mcp_tools\" then \"mcp_call\")")
            return lines

        # Degrade gracefully: full descriptions -> short -> names only -> drop entries.
        # Dropping is the last resort because a dropped skill can never auto-trigger.
        out = None
        for desc_len in (90, 50, 0):
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
    def perform(self, action="list", **kw):
        handler = getattr(self, f"_do_{action}", None)
        if handler is None:
            return f"Unknown action {action!r}. Valid: list, load, read, run, hook, mcp_tools, mcp_call, install, uninstall, promote, export, doctor, refresh."
        try:
            return handler(**kw)
        except Exception as e:
            return f"ClaudeCompat {action} failed: {type(e).__name__}: {e}"

    def _timeout(self, kw):
        t = kw.get("timeout")
        try:
            t = int(t) if t is not None else _default_timeout()
        except (TypeError, ValueError):
            t = _default_timeout()
        return max(1, min(t, 600))

    # -- list ----------------------------------------------------------------
    def _do_list(self, kind="all", query="", **_):
        cat = _get_catalog()
        q = (query or "").lower().strip()
        kind = (kind or "all").lower()

        def match(item):
            if not q:
                return True
            return q in item["name"].lower() or q in item.get("description", "").lower()

        out = []
        if kind in ("all", "skills"):
            rows = [i for i in cat.skills.values() if match(i)]
            out.append(f"## Skills ({len(rows)})")
            out += [f"- {i['name']} [{i['source']}] — {_one_line(i['description'])[:160]}" for i in rows]
        if kind in ("all", "commands"):
            rows = [i for i in cat.commands.values() if match(i)]
            out.append(f"\n## Slash commands ({len(rows)})")
            out += [f"- /{i['name']} [{i['source']}] — {_one_line(i['description'])[:160]}" for i in rows]
        if kind in ("all", "agents"):
            rows = [i for i in cat.agents.values() if match(i)]
            out.append(f"\n## Subagent personas ({len(rows)})")
            out += [f"- {i['name']} [{i['source']}] — {_one_line(i['description'])[:160]}" for i in rows]
        if kind in ("all", "plugins"):
            rows = [p for p in cat.plugins.values() if not q or q in p["name"].lower()
                    or q in str(p["manifest"].get("description", "")).lower()]
            out.append(f"\n## Plugins ({len(rows)})")
            for p in rows:
                m = p["manifest"]
                out.append(f"- {p['name']} v{m.get('version', '?')} [{p['source']}] — {str(m.get('description', ''))[:140]}"
                           f" | skills={len(p['skills'])} commands={len(p['commands'])} agents={len(p['agents'])}"
                           f" hooks={p['hooks']} mcp={len(p['mcp'])}")
        if kind in ("all", "hooks"):
            rows = [h for h in cat.hooks if not q or q in h["event"].lower() or q in h["command"].lower() or q in h["source"].lower()]
            out.append(f"\n## Hooks ({len(rows)})")
            out += [f"- {h['event']}" + (f"[{h['matcher']}]" if h['matcher'] else "") + f" ({h['source']}): {h['command'][:120]}" for h in rows]
        if kind in ("all", "mcp"):
            rows = {n: e for n, e in cat.mcp.items() if not q or q in n.lower()}
            out.append(f"\n## MCP servers ({len(rows)})")
            for n, e in rows.items():
                c = e["config"]
                what = c.get("url") or " ".join([str(c.get("command", ""))] + [str(a) for a in c.get("args", [])])
                out.append(f"- {n} [{e['source']}] {c.get('type') or ('http' if c.get('url') else 'stdio')}: {what[:120]}")
        if cat.errors:
            out.append("\n## Parse errors")
            out += [f"- {e}" for e in cat.errors[:20]]
        return "\n".join(out).strip() or "Nothing Claude-shaped found."

    # -- load ----------------------------------------------------------------
    def _do_load(self, name="", args="", **_):
        cat = _get_catalog()
        item = cat.find(name)
        if item is None:
            near = [k for k in list(cat.skills) + list(cat.commands) + list(cat.agents)
                    if name and name.lower().replace("/", "") in k.lower()][:8]
            return f"No skill/command/persona named {name!r}." + (f" Close matches: {', '.join(near)}" if near else " Try action='list'.")
        meta, body = _parse_frontmatter(_safe_read(item["path"], 400_000))
        body = body.strip()
        if item["kind"] == "command":
            body = _substitute_arguments(body, args)
        lines = [f"# {item['kind'].capitalize()}: {item['name']}", f"Source: {item['path']}"]
        if item.get("plugin"):
            lines.append(f"Plugin: {item['plugin']}")
        for k in ("allowed-tools", "tools", "model", "argument-hint", "compatibility", "license"):
            if meta.get(k):
                lines.append(f"{k}: {meta[k]}")
        if item["kind"] == "agent":
            lines.append("Use this as a persona: adopt the instructions below for the current task, then answer as that agent.")
        elif item["kind"] == "command":
            lines.append("This is a slash-command prompt; treat the text below as the user's instruction.")
        if item["kind"] == "skill":
            files, extra = _resource_index(item["dir"])
            if files:
                lines.append("Bundled files (action='read' path=<file> for references, action='run' path=<script> to execute): "
                             + ", ".join(files) + (f", +{extra} more" if extra else ""))
        return "\n".join(lines) + "\n\n" + _clip(body, 60_000)

    # -- read ----------------------------------------------------------------
    def _resolve_dir(self, name):
        cat = _get_catalog()
        item = cat.find(name)
        if item is not None:
            return item["dir"], item
        p = cat.plugins.get((name or "").strip())
        if p:
            return p["dir"], p
        raise ValueError(f"unknown skill/command/persona/plugin {name!r}")

    def _do_read(self, name="", path="", **_):
        base, _item = self._resolve_dir(name)
        target = _confine(base, path)
        if os.path.isdir(target):
            entries = sorted(os.listdir(target))
            return f"Directory {path or '.'} in {name}:\n" + "\n".join(entries[:200])
        if not os.path.isfile(target):
            return f"No file {path!r} in {name}."
        return _clip(_safe_read(target, 400_000), 60_000)

    # -- run -----------------------------------------------------------------
    def _do_run(self, name="", path="", args="", stdin=None, **kw):
        base, item = self._resolve_dir(name)
        if not path:
            files, _ = _resource_index(base)
            scripts = [f for f in files if f.startswith("scripts" + os.sep) or f.endswith((".py", ".sh", ".js", ".ts"))]
            return "Pass path=<script>. Runnable files: " + (", ".join(scripts) if scripts else "none found")
        target = _confine(base, path)
        if not os.path.isfile(target):
            return f"No script {path!r} in {name}."
        argv = [target] + (shlex.split(args) if isinstance(args, str) and args.strip() else [str(a) for a in (args or [])] if isinstance(args, (list, tuple)) else [])
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
                              env_extra={"CLAUDE_PLUGIN_ROOT": plugin_root, "CLAUDE_SKILL_DIR": base})
        return json.dumps({"command": " ".join(shlex.quote(a) for a in argv), "cwd": base, "exit": res["exit"],
                           "seconds": res["seconds"], "stdout": _clip(res["stdout"], 20_000),
                           "stderr": _clip(res["stderr"], 6_000)}, indent=2)

    # -- hooks ---------------------------------------------------------------
    def _do_hook(self, name="", args="", stdin=None, **kw):
        """Fire hooks for an event (name) optionally filtered by matcher (args). Plugin hooks only."""
        cat = _get_catalog()
        event = (name or "").strip()
        if not event:
            return "Pass name=<event> (e.g. Stop, PreToolUse, PostToolUse, UserPromptSubmit, SessionStart)."
        want = [h for h in cat.hooks if h["event"].lower() == event.lower()]
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
                                  env_extra={"CLAUDE_PLUGIN_ROOT": h["cwd"]}, shell=True)
            results.append({"source": h["source"], "event": h["event"], "matcher": h["matcher"], "command": cmd,
                            "exit": res["exit"], "stdout": _clip(res["stdout"], 8000), "stderr": _clip(res["stderr"], 3000)})
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
            lines.append(f"- {t.get('name')}: {_one_line(t.get('description', ''))[:160]}"
                         + (f"  args: {', '.join(props[:12])}" if props else ""))
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
        parts = []
        for c in res.get("content") or []:
            if c.get("type") == "text":
                parts.append(c.get("text", ""))
            else:
                parts.append(f"[{c.get('type')} content omitted]")
        text = "\n".join(parts) if parts else json.dumps(res.get("structuredContent", res), indent=2)
        prefix = "ERROR from tool: " if res.get("isError") else ""
        return prefix + _clip(text, 40_000)

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
        manifest, _ = _plugin_manifest(src)
        if manifest is None:
            if os.path.isfile(os.path.join(src, "SKILL.md")):
                # bare skill: wrap it as a one-skill plugin
                meta, _b = _parse_frontmatter(_safe_read(os.path.join(src, "SKILL.md")))
                sname = str(meta.get("name") or os.path.basename(src.rstrip(os.sep)))
                pname = name or sname
                dest = os.path.join(store, pname)
                shutil.rmtree(dest, ignore_errors=True)
                os.makedirs(os.path.join(dest, "skills"), exist_ok=True)
                shutil.copytree(src, os.path.join(dest, "skills", sname))
                with open(os.path.join(dest, "plugin.json"), "w") as f:
                    json.dump({"name": pname, "version": "0.0.0", "description": str(meta.get("description", ""))[:300],
                               "_wrapped_by": "ClaudeCompat"}, f, indent=2)
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
        return (f"Installed plugin {pname!r} v{manifest.get('version', '?')} at {dest}: "
                f"skills={len(p.get('skills', []))} commands={len(p.get('commands', []))} agents={len(p.get('agents', []))} "
                f"hooks={p.get('hooks', 0)} mcp={len(p.get('mcp', []))}")

    def _do_uninstall(self, name="", **_):
        dest = os.path.join(_store_dir(), "plugins", (name or "").strip())
        if not name or not os.path.isdir(dest):
            return f"No Brainstem-installed plugin named {name!r} (only plugins installed via action='install' can be removed here)."
        shutil.rmtree(dest)
        _get_catalog(force=True)
        return f"Removed plugin {name!r} from {dest}"

    # -- promote (skill -> native agent) -------------------------------------
    def _do_promote(self, name="", **_):
        cat = _get_catalog()
        item = cat.find(name)
        if item is None or item["kind"] != "skill":
            return f"No skill named {name!r}."
        meta, body = _parse_frontmatter(_safe_read(item["path"], 400_000))
        slug = _slug(item["short"])
        tool_name = "Skill" + _camel(slug)
        class_name = tool_name + "Agent"
        desc = re.sub(r"\s+", " ", item["description"]).strip()[:900] or f"Claude Code skill {item['short']}"
        agents_dir = os.path.dirname(os.path.abspath(__file__))
        out_path = os.path.join(agents_dir, f"skill_{slug}_agent.py")
        sha = hashlib.sha256(_safe_read(item["path"]).encode()).hexdigest()
        code = _PROMOTED_TEMPLATE.format(
            class_name=class_name, skill_name=item["short"], sha=sha, skill_dir=item["dir"],
            body=body.strip(), meta={k: v for k, v in meta.items() if isinstance(v, (str, int, float, bool, list, dict))},
            tool_name=tool_name, description=desc,
        )
        compile(code, out_path, "exec")  # never write an agent that cannot load
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(code)
        return f"Promoted skill {item['name']!r} to native agent {tool_name} at {out_path}. It is live on the next /chat."

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
            # match by tool name declared in the file
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
        desc = ""
        if m_desc:
            desc = " ".join(re.findall(r"['\"]([^'\"]*)['\"]", m_desc.group(1)))
        skill_name = _slug(tool).replace("_", "-")
        out_root = os.path.expanduser(path) if path else os.path.join(_store_dir(), "exported_skills")
        sdir = os.path.join(out_root, skill_name)
        os.makedirs(os.path.join(sdir, "scripts"), exist_ok=True)
        shutil.copy(agent_file, os.path.join(sdir, "scripts", "agent.py"))
        runner = (
            "#!/usr/bin/env python3\n\"\"\"Run the bundled RAPP agent: python3 run.py --json '{...}'\"\"\"\n"
            "import importlib.util, json, os, sys, types\n"
            "here = os.path.dirname(os.path.abspath(__file__))\n"
            "# stand-in for the Brainstem's agents.basic_agent import\n"
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
            "print(cls().perform(**args))\n"
        )
        with open(os.path.join(sdir, "scripts", "run.py"), "w") as f:
            f.write(runner)
        sha = hashlib.sha256(src.encode()).hexdigest()
        fm_desc = (desc or f"RAPP agent {tool} exported from the Brainstem.").replace('"', "'")[:1000]
        skill_md = (
            "---\n"
            f"name: \"{skill_name}\"\n"
            f"description: \"{fm_desc}\"\n"
            "license: \"MIT\"\n"
            "compatibility: \"Requires python3 (3.11+).\"\n"
            "metadata:\n"
            f"  rapp-tool: \"{tool}\"\n"
            f"  agent-sha256: \"{sha}\"\n"
            "  source: \"rapp-brainstem ClaudeCompat export\"\n"
            "---\n\n"
            f"# {tool}\n\n{desc or 'A RAPP single-file agent.'}\n\n"
            "## Run\n\n"
            "This skill carries the agent verbatim in `scripts/agent.py`. Execute it with:\n\n"
            "```bash\npython3 scripts/run.py --json '{\"...\": \"...\"}'\n```\n\n"
            "Pass the agent's parameters as the JSON object. To run it server-side, drop `scripts/agent.py` into a RAPP Brainstem `agents/` folder.\n"
        )
        with open(os.path.join(sdir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(skill_md)
        return f"Exported {tool} to skill {skill_name!r} at {sdir} (SKILL.md, scripts/agent.py, scripts/run.py)."

    # -- doctor / refresh ----------------------------------------------------
    def _do_doctor(self, **_):
        cat = _get_catalog(force=True)
        lines = [
            "ClaudeCompat doctor",
            f"claude home: {_claude_home()} ({'ok' if os.path.isdir(_claude_home()) else 'missing'})",
            f"project dir: {_project_dir()}",
            f"store: {_store_dir()}",
            f"skill roots: {', '.join(cat.roots) or 'none'}",
            f"skills={len(cat.skills)} commands={len(cat.commands)} personas={len(cat.agents)} plugins={len(cat.plugins)} hooks={len(cat.hooks)} mcp={len(cat.mcp)}",
            f"catalog context budget: {_context_chars()} chars; current: {len(self.system_context() or '')} chars",
            f"python: {sys.executable}; git: {'yes' if shutil.which('git') else 'no'}; node: {'yes' if shutil.which('node') else 'no'}",
        ]
        if cat.errors:
            lines.append("errors:")
            lines += [f"  - {e}" for e in cat.errors[:30]]
        return "\n".join(lines)

    def _do_refresh(self, **_):
        cat = _get_catalog(force=True)
        return f"Catalog rebuilt: skills={len(cat.skills)} commands={len(cat.commands)} personas={len(cat.agents)} plugins={len(cat.plugins)} hooks={len(cat.hooks)} mcp={len(cat.mcp)}"
