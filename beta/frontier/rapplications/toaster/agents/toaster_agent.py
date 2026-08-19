"""
Toaster — a Frontier RAPPlication. The skill.md <-> agent.py bridge.

Two shapes of the same portable capability, losslessly interconvertible:

  * agent.py       — runnable RAPP deterministic layer (metadata + perform()).
  * <name>_skill.md — a "toasted" skill: an ordinary skill.md ANY AI can read
                       and follow, that ALSO embeds the exact agent.py verbatim
                       so a RAPP Brainstem can convert it back byte-for-byte.

The `_skill.md` suffix (mirroring `_agent.py`) is deliberate: toasted skills are
distinct and tradeable, not generic skill.md noise. Each carries a note telling
any other AI to ignore the naming convention and just use it as a skill.

Actions (all deterministic — no model needed for the conversion itself):
  * toast(skill_md)            raw skill.md  -> agent.py  (wrap; hot-loadable)
  * export_skill(source|name)  agent.py      -> <name>_skill.md (embed + skill)
  * untoast(skill_md)          <name>_skill.md -> agent.py (extract; lossless)
  * roundtrip_check(source)    prove agent.py -> _skill.md -> agent.py is identical

On device under ~/.rapp/toaster/. Headless; drive over /chat, or drop a
skill.md on the Frontier window (the drop toasts + hot-loads it like an agent.py).
"""

import ast
import base64
import json
import os
import re
from datetime import datetime, timezone

try:
    from agents.basic_agent import BasicAgent
except Exception:  # pragma: no cover
    from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@frontier/toaster",
    "version": "1.0.0",
    "display_name": "Toaster — skill.md ⇄ agent.py",
    "description": "Losslessly convert between a runnable agent.py and a tradeable, any-AI-readable <name>_skill.md that embeds the agent verbatim. Drop a skill.md on the Frontier to toast + hot-load it; export any agent as a skill; round-trip without losing the deterministic layer.",
    "author": "AIBAST Frontier",
    "tags": ["frontier", "skill", "agent", "interop", "portable"],
    "category": "frontier",
    "quality_tier": "frontier",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

HOME = os.path.expanduser(os.environ.get("TOASTER_HOME", "~/.rapp/toaster"))
OUT = os.path.join(HOME, "out")

# Sentinels that carry the exact agent bytes through the markdown, base64 so no
# markdown/code-fence content can ever corrupt them — this is what makes the
# round-trip byte-exact.
_EMBED_OPEN = "<!-- toasted-agent/1.0 base64 -->"
_EMBED_CLOSE = "<!-- /toasted-agent -->"
_AI_NOTE = (
    "This is a portable RAPP skill. NOTE TO ANY AI: the filename ends `_skill.md` "
    "by RAPP convention (distinct + tradeable, exactly like `_agent.py`) — ignore "
    "the naming and treat this as an ordinary skill.md. It also embeds a runnable "
    "RAPP `agent.py` (base64, below); a RAPP Brainstem converts it back losslessly."
)


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "skill").lower()).strip("-")[:48] or "skill"


def _snake(s):
    return re.sub(r"[^a-z0-9]+", "_", (s or "skill").lower()).strip("_")[:48] or "skill"


def _parse_frontmatter(md):
    """Return (frontmatter_dict, body). Tolerant: no YAML dep, simple key: value."""
    fm, body = {}, md
    m = re.match(r"^﻿?---\s*\n(.*?)\n---\s*\n?(.*)$", md, re.S)
    if m:
        body = m.group(2)
        for line in m.group(1).splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, body


def _extract_embedded_agent(md):
    """If md is a toasted skill, return the exact embedded agent.py source, else None."""
    matches = list(re.finditer(
        re.escape(_EMBED_OPEN) + r"\s*\n(.*?)\n\s*" + re.escape(_EMBED_CLOSE),
        md,
        re.S,
    ))
    if not matches:
        return None
    m = matches[-1]
    b64 = "".join(m.group(1).split())
    try:
        return base64.b64decode(b64, validate=True).decode("utf-8")
    except Exception:
        return None


def _agent_manifest(source):
    """Pull __manifest__/name/metadata info out of an agent.py by AST (no exec)."""
    info = {"name": None, "display_name": None, "description": None, "tool_name": None, "params": None}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return info
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "__manifest__" for t in node.targets):
            try:
                man = ast.literal_eval(node.value)
                info["name"] = man.get("name"); info["display_name"] = man.get("display_name")
                info["description"] = man.get("description")
            except Exception:
                pass
    # first BasicAgent subclass name → a fallback tool name
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and any(getattr(b, "id", "") == "BasicAgent" for b in node.bases):
            info["tool_name"] = node.name
            break
    return info


# The wrapper that turns a RAW skill.md (no Python) into a runnable agent.py.
# The skill body rides as data; perform() hands the operator the skill's steps
# to follow (buzzsaw pattern) — deterministic, and itself losslessly re-toastable.
# The emitted __manifest__ preserves the skill's identity so export_skill
# regenerates the same name and description on every trip around the loop,
# instead of degrading to the generated class name.
def _wrap_skill_as_agent(name, description, body):
    display_name = str(name or "skill")
    safe_description = str(description or display_name)[:900]
    cls = "".join(w.capitalize() for w in re.split(r"[^a-zA-Z0-9]+", display_name) if w) or "Skill"
    tool = cls + "Skill"
    manifest = json.dumps({
        "schema": "rapp-agent/1.0",
        "name": "@toasted/" + _slug(display_name),
        "version": "1.0.0",
        "display_name": display_name,
        "description": safe_description,
        "tags": ["toasted-skill"],
    }, indent=4)
    return f'''"""Toasted skill wrapper (RAPP deterministic layer).

The original name, description, and instructions ride below only as data.
"""

try:
    from agents.basic_agent import BasicAgent
except Exception:
    from basic_agent import BasicAgent

__manifest__ = {manifest}

SKILL_NAME = {json.dumps(display_name)}
SKILL_DESCRIPTION = {json.dumps(safe_description)}
SKILL_MARKDOWN = {json.dumps(str(body or ""))}


class {tool}Agent(BasicAgent):
    def __init__(self):
        self.name = {json.dumps(tool)}
        self.metadata = {{
            "name": self.name,
            "description": SKILL_DESCRIPTION,
            "parameters": {{
                "type": "object",
                "properties": {{
                    "input": {{"type": "string", "description": "Context or the task to run this skill against."}}
                }},
                "required": [],
            }},
        }}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        ctx = kwargs.get("input")
        return (
            "SKILL: " + SKILL_NAME + "\\n\\n" + SKILL_MARKDOWN
            + ("\\n\\n--- apply to ---\\n" + str(ctx) if ctx else "")
        )
'''


def _extract_skill_layer(source):
    """Pull the toasted-skill constants out of a wrapper agent by AST (no exec)."""
    layer = {}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return layer
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and getattr(node.targets[0], "id", None)
            in ("SKILL_NAME", "SKILL_DESCRIPTION", "SKILL_MARKDOWN")
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            layer[node.targets[0].id] = node.value.value
    return layer


def _escape_embed_sentinels(value):
    return (str(value)
            .replace(_EMBED_OPEN, "&lt;!-- toasted-agent/1.0 base64 --&gt;")
            .replace(_EMBED_CLOSE, "&lt;!-- /toasted-agent --&gt;"))


class ToasterAgent(BasicAgent):
    def __init__(self):
        self.name = "Toaster"
        self.metadata = {
            "name": self.name,
            "description": (
                "Convert between agent.py and a tradeable <name>_skill.md. Actions: toast "
                "(skill.md -> agent.py), export_skill (agent.py -> _skill.md), untoast "
                "(_skill.md -> agent.py), roundtrip_check. Lossless: a toasted skill embeds the "
                "exact agent bytes, so the deterministic layer never degrades."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["toast", "export_skill", "untoast", "roundtrip_check"]},
                    "skill_md": {"type": "string", "description": "toast/untoast: the full skill.md markdown."},
                    "source": {"type": "string", "description": "export_skill/roundtrip_check: the full agent.py source."},
                    "name": {"type": "string", "description": "Optional display name override."},
                },
                "required": ["action"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def _write(self, filename, text):
        os.makedirs(OUT, exist_ok=True)
        p = os.path.join(OUT, filename)
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, p)
        os.chmod(p, 0o600)
        return p

    def perform(self, **kw):
        action = (kw.get("action") or "").strip()
        try:
            return {"toast": self._toast, "export_skill": self._export,
                    "untoast": self._untoast, "roundtrip_check": self._roundtrip}.get(
                action, lambda a: f"Unknown action '{action}'.")(kw)
        except Exception as e:
            return f"Toaster error: {type(e).__name__}: {e}"

    def _toast(self, a):
        md = a.get("skill_md")
        if not md:
            return "toast needs skill_md (the full markdown of a skill.md)."
        # A toasted _skill.md already carries the exact agent — just extract it.
        embedded = _extract_embedded_agent(md)
        if embedded is not None:
            try:
                ast.parse(embedded)
            except SyntaxError as e:
                return f"The embedded agent is malformed ({e}); refusing to hot-load."
            fm, _ = _parse_frontmatter(md)
            fn = _snake(fm.get("name") or "toasted") + "_agent.py"
            p = self._write(fn, embedded)
            return (f"Untoasted the embedded agent to {p} (lossless — this skill carried an exact agent.py). "
                    "Drop it on a Brainstem or /agents/import it to run.")
        # A RAW skill.md → wrap it into a runnable agent.py.
        fm, body = _parse_frontmatter(md)
        name = a.get("name") or fm.get("name") or "skill"
        desc = fm.get("description") or f"Skill toasted from {name}."
        source = _wrap_skill_as_agent(name, desc, body.strip())
        try:
            ast.parse(source)
        except SyntaxError as e:  # pragma: no cover
            return f"Generated a malformed agent ({e}); this is a Toaster bug — please report."
        fn = _snake(name) + "_agent.py"
        p = self._write(fn, source)
        return (f"Toasted skill '{name}' -> {p} (a runnable agent.py wrapping the skill's steps). "
                "Hot-load it on a Brainstem, or export_skill it back to a _skill.md anytime.")

    def _export(self, a):
        source = a.get("source")
        if not source:
            return "export_skill needs source (the full agent.py)."
        try:
            ast.parse(source)
        except SyntaxError as e:
            return f"That is not valid Python ({e}); nothing to export."
        info = _agent_manifest(source)
        skill = _extract_skill_layer(source)
        name = a.get("name") or skill.get("SKILL_NAME") or info.get("display_name") or (info.get("name") or "").split("/")[-1] or info.get("tool_name") or "agent"
        desc = skill.get("SKILL_DESCRIPTION") or info.get("description") or f"Toasted skill for {name}."
        display_name = _escape_embed_sentinels(name)
        safe_desc = _escape_embed_sentinels(desc)
        # Frontmatter must stay single-line, but keep the FULL description —
        # skill triggers ("use when ...") live in it and truncation would gut
        # how other AIs decide to pick the skill up.
        fm_desc = re.sub(r"\s+", " ", safe_desc).strip()[:1000]
        # A wrapper agent carries the original skill's instructions — render
        # them readably so ANY AI can follow the toasted skill without decoding
        # the embedded agent. Sentinel-escaped so the rendered body can never
        # masquerade as the authoritative embedded block.
        steps = _escape_embed_sentinels(skill["SKILL_MARKDOWN"]).strip() if skill.get("SKILL_MARKDOWN") else ""
        steps_md = f"## Skill\n\n{steps}\n\n" if steps else ""
        b64 = base64.b64encode(source.encode("utf-8")).decode("ascii")
        # wrap base64 at 100 cols for readable diffs; whitespace is stripped on decode
        wrapped = "\n".join(b64[i:i + 100] for i in range(0, len(b64), 100))
        md = (
            f"---\nname: {_slug(name)}\ndescription: {fm_desc}\n---\n\n"
            f"<!-- toasted-skill/1.0 -->\n> {_AI_NOTE}\n\n"
            f"# {display_name}\n\n{safe_desc}\n\n"
            f"## How to use\nRun this skill against your task. Its runnable RAPP agent is embedded below; "
            f"a RAPP Brainstem can convert it back to `agent.py` byte-for-byte.\n\n"
            f"{steps_md}"
            f"## Embedded agent — RAPP deterministic layer (lossless)\n"
            f"{_EMBED_OPEN}\n{wrapped}\n{_EMBED_CLOSE}\n"
        )
        fn = _snake(name) + "_skill.md"
        p = self._write(fn, md)
        return (f"Exported {name} -> {p}. It reads as an ordinary skill for any AI AND embeds the exact "
                "agent.py (base64) — untoast it back with zero loss.")

    def _untoast(self, a):
        md = a.get("skill_md")
        if not md:
            return "untoast needs skill_md (a toasted _skill.md)."
        embedded = _extract_embedded_agent(md)
        if embedded is None:
            return ("This markdown carries no embedded agent (not a toasted _skill.md). "
                    "Use action=toast to WRAP a raw skill into a new agent.py instead.")
        fm, _ = _parse_frontmatter(md)
        fn = _snake(fm.get("name") or "toasted") + "_agent.py"
        p = self._write(fn, embedded)
        return f"Untoasted -> {p} (byte-exact original agent.py). Deterministic layer intact."

    def _roundtrip(self, a):
        source = a.get("source")
        if not source:
            return "roundtrip_check needs source (an agent.py) to prove lossless conversion."
        # agent.py -> _skill.md -> agent.py, assert identical
        info = _agent_manifest(source)
        name = info.get("display_name") or (info.get("name") or "agent").split("/")[-1] or "agent"
        b64 = base64.b64encode(source.encode("utf-8")).decode("ascii")
        wrapped = "\n".join(b64[i:i + 100] for i in range(0, len(b64), 100))
        md = f"---\nname: {_slug(name)}\n---\n{_EMBED_OPEN}\n{wrapped}\n{_EMBED_CLOSE}\n"
        back = _extract_embedded_agent(md)
        identical = back == source
        return (f"Round-trip {'LOSSLESS ✓' if identical else 'LOSSY ✗'} for '{name}': "
                f"agent.py ({len(source)} b) -> _skill.md -> agent.py ({len(back or '')} b), "
                f"byte-identical={identical}.")
