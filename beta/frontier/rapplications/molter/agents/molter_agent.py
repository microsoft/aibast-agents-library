"""
Capability Forge — a Frontier RAPPlication.

Gives the Brainstem autonomous, headless capability acquisition + agent
evolution. When the Brainstem lacks a capability, it can:

  1. SEARCH the AIBAST RAR (the full microsoft/aibast-agents-library catalog)
     for an agent.py of a shape SIMILAR to the request.
  2. ACQUIRE the closest match — sha256-verified — and hot-load it as the
     base generation (molt 0).
  3. MUTATE that base to fit the user's exact use case, or GENERATE a new
     agent from scratch when the RAR has no relevant match.
  4. MOLT: every generation is archived on device. A generation that verifies
     becomes the live agent; a CATASTROPHIC one is refused, rolled back to the
     last good molt, and its failure LESSON is returned as chat data-exhaust so
     the next mutation learns and adjusts in real time.

Architecture (buzzsaw / personless-harness law): THIS agent does only the
deterministic, safe work — search, sha-verified fetch, fail-closed verification
(compile + isolated smoke-load in a timeout-bounded subprocess), molt archive,
rollback, and lesson capture. The BRAINSTEM's own LLM does the creative work
(writing the mutated/generated source), guided by the lessons this agent hands
back. No subprocess-invoked model, ever.

Everything is on device under ~/.rapp/molter/. Headless: the whole
loop is driven over /chat by the Brainstem itself.
"""

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from hashlib import sha256

try:
    from agents.basic_agent import BasicAgent
except Exception:  # pragma: no cover
    from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@frontier/molter",
    "version": "1.0.0",
    "display_name": "Capability Forge",
    "description": "Autonomously acquire a capability the Brainstem lacks: search the AIBAST RAR for a shape-similar agent, hot-load it, then mutate it (or generate from scratch) to fit the request — archiving each generation as a molt with rollback and lesson-carrying evolution.",
    "author": "AIBAST Frontier",
    "tags": ["frontier", "capability", "evolution", "rar", "self-improving"],
    "category": "frontier",
    "quality_tier": "frontier",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

HOME = os.path.expanduser(os.environ.get("MOLTER_HOME", "~/.rapp/molter"))
MOLTS = os.path.join(HOME, "molts")
STATE_FILE = os.path.join(HOME, "state.json")
# The full AIBAST catalog (the RAR the Brainstem searches for a base agent).
AIBAST_REGISTRY = os.environ.get(
    "MOLTER_RAR",
    "https://microsoft.github.io/aibast-agents-library/registry.json")
AIBAST_RAW = "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/"
# Where a verified generation is hot-loaded so the kernel discovers it: the
# forge's own agents dir (i.e. THIS Brainstem's AGENTS_PATH).
LIVE_DIR = os.path.dirname(os.path.abspath(__file__))
VERIFY_TIMEOUT = 20


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "capability").lower()).strip("-")[:48] or "capability"


def _tokens(s):
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))


def _fetch(url, as_bytes=False, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "molter"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    return data if as_bytes else json.loads(data.decode("utf-8"))


def _load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"capabilities": {}}


def _save_state(st):
    os.makedirs(HOME, exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(st, fh, indent=2)
    os.replace(tmp, STATE_FILE)


def _safe_agent_name(name, fallback):
    base = os.path.basename(str(name or ""))
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_]{0,60}_agent\.py", base):
        base = f"{_slug(fallback).replace('-', '_')}_agent.py"
    return base


# ── fail-closed verification: a candidate must compile AND smoke-load in an
# isolated, timeout-bounded loader before the trusted parent admits it ────────
#
# Trust boundary: this loader runs the UNTRUSTED candidate's module-level code, so
# it holds no secret and emits no verdict. It only *imports and instantiates* the
# candidate in a disposable process and reports success/failure through its EXIT
# STATUS (0 = clean, non-zero = failed, with a human reason on stderr). The pass/
# fail decision is made by the trusted parent from a static AST analysis it does
# itself (see _ast_agent_verdict); the parent never trusts a byte this process
# writes for that decision. There is deliberately no privileged report channel for
# a candidate to hijack.
_LOADER_HARNESS = r'''
import importlib.util
import sys

def main():
    path = sys.argv[1]
    try:
        from agents.basic_agent import BasicAgent

        spec = importlib.util.spec_from_file_location("_forge_candidate", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)          # runs module-level code (isolated proc)

        agent_cls = None
        for value in vars(mod).values():
            if (isinstance(value, type)
                    and value is not BasicAgent
                    and getattr(value, "__module__", None) == mod.__name__
                    and issubclass(value, BasicAgent)):
                agent_cls = value
        if agent_cls is None:
            sys.stderr.write("no BasicAgent subclass was defined")
            raise SystemExit(1)

        inst = agent_cls()
        md = getattr(inst, "metadata", None)
        if not isinstance(md, dict):
            sys.stderr.write("metadata is missing or is not a dict")
            raise SystemExit(1)
        name = md.get("name")
        if not isinstance(name, str) or not name.strip():
            sys.stderr.write("metadata has no valid string name")
            raise SystemExit(1)
        if not isinstance(md.get("parameters"), dict):
            sys.stderr.write("metadata has no parameters dict")
            raise SystemExit(1)
        if not callable(getattr(inst, "perform", None)):
            sys.stderr.write("perform() is not callable")
            raise SystemExit(1)
        # Advisory only (display label): the agent's own registered name. The parent
        # uses this for a label, NEVER for the pass/fail verdict, so forging it is
        # inert — the verdict is already decided by the parent's AST analysis.
        display_name = getattr(inst, "name", None) or name
        sys.stdout.write(str(display_name)[:200])
        sys.stdout.flush()
        raise SystemExit(0)
    except SystemExit:
        raise
    except BaseException as e:
        sys.stderr.write("{0}: {1}".format(type(e).__name__, e))
        raise SystemExit(1)

if __name__ == "__main__":
    main()
'''


def _ast_extract_tool_name(class_node):
    """Best-effort: read the tool name from a `metadata = {... "name": "X" ...}`
    dict literal in the class body or __init__. Returns None when the name is not a
    plain string literal (the class name is used as a harmless display fallback)."""
    for node in ast.walk(class_node):
        if isinstance(node, ast.Assign):
            is_metadata = any(
                (isinstance(t, ast.Name) and t.id == "metadata")
                or (isinstance(t, ast.Attribute) and t.attr == "metadata")
                for t in node.targets)
            if is_metadata and isinstance(node.value, ast.Dict):
                for key, val in zip(node.value.keys, node.value.values):
                    if (isinstance(key, ast.Constant) and key.value == "name"
                            and isinstance(val, ast.Constant)
                            and isinstance(val.value, str) and val.value.strip()):
                        return val.value
    return None


def _ast_agent_verdict(source):
    """The trusted, parent-side verdict — it PARSES the candidate, never executes
    it, so it cannot be forged by anything the candidate does at import time
    (including os._exit/SystemExit tricks that would fake a clean subprocess load).
    A source passes only if it statically (a) imports BasicAgent from the kernel
    base module and never rebinds that name — so the base is the genuine kernel
    class, not a `BasicAgent = object` decoy — (b) defines a class subclassing it,
    and (c) that class defines its own perform() — a molt that cannot act is a
    sterile molt and is refused. Returns (ok, reason_or_None, info_or_None)."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} at line {e.lineno}", None

    imported_basic_agent = False
    rebinds_basic_agent = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").endswith("basic_agent"):
            if any(alias.name == "BasicAgent" for alias in node.names):
                imported_basic_agent = True
        elif isinstance(node, ast.Import):
            if any(alias.name.endswith("basic_agent") for alias in node.names):
                imported_basic_agent = True
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == "BasicAgent" for t in targets):
                rebinds_basic_agent = True

    agent_cls = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                name = base.attr if isinstance(base, ast.Attribute) else getattr(base, "id", None)
                if name == "BasicAgent":
                    agent_cls = node
    if agent_cls is None:
        return False, "no BasicAgent subclass is defined", None
    if not imported_basic_agent or rebinds_basic_agent:
        return False, ("BasicAgent must be imported from agents.basic_agent and its name "
                       "never reassigned (the base must be the real kernel class)"), None
    if not any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "perform"
               for n in agent_cls.body):
        return False, f"{agent_cls.name} does not define perform() — a molt must be able to act", None

    tool_name = _ast_extract_tool_name(agent_cls)  # None when not a static literal
    return True, None, {"agent_class": agent_cls.name, "tool_name": tool_name}


def _verify(source):
    """Return (ok, detail). The pass/fail VERDICT is decided by the trusted parent
    from a static AST analysis of the source (never executed here). A disposable
    subprocess additionally confirms the source imports and instantiates cleanly —
    a *correctness* signal read only from the child's EXIT STATUS, never from any
    byte the child writes — so a candidate cannot forge a pass by what it prints,
    by pre-empting a report channel, or by calling os._exit(). Fail-closed."""
    ok, reason, info = _ast_agent_verdict(source)
    if not ok:
        return False, {"stage": "ast", "lesson": reason}

    def fail(lesson):
        one_line = " ".join(str(lesson).split()) or "verification failed"
        return False, {"stage": "smoke", "lesson": one_line[:600]}

    with tempfile.TemporaryDirectory() as td:
        cand = os.path.join(td, "candidate_agent.py")
        with open(cand, "w", encoding="utf-8") as fh:
            fh.write(source)
        pkg = os.path.join(td, "agents"); os.makedirs(pkg, exist_ok=True)
        open(os.path.join(pkg, "__init__.py"), "w").close()
        with open(os.path.join(pkg, "basic_agent.py"), "w", encoding="utf-8") as fh:
            fh.write('# minimal BasicAgent stub so any agent loads for schema/verify regardless of env\nclass BasicAgent:\n    def __init__(self, name=None, metadata=None):\n        if name is not None: self.name = name\n        if metadata is not None: self.metadata = metadata\n')
        with open(os.path.join(td, "basic_agent.py"), "w", encoding="utf-8") as fh:
            fh.write("from agents.basic_agent import BasicAgent\n")
        loader = os.path.join(td, "loader.py")
        with open(loader, "w", encoding="utf-8") as fh:
            fh.write(_LOADER_HARNESS)
        env = dict(os.environ)
        # basic_agent must resolve; expose the same shim path the kernel uses
        env["PYTHONPATH"] = os.pathsep.join(
            [td, LIVE_DIR, os.path.dirname(LIVE_DIR)] + env.get("PYTHONPATH", "").split(os.pathsep))
        try:
            r = subprocess.run([sys.executable, loader, cand], capture_output=True,
                               timeout=VERIFY_TIMEOUT, env=env)
        except subprocess.TimeoutExpired:
            return fail(
                f"candidate did not finish loading within {VERIFY_TIMEOUT}s "
                "(likely an infinite loop or blocking call at import time)")
        except OSError as e:
            return fail(f"loader could not start: {type(e).__name__}: {e}")

        if r.returncode != 0:
            stderr = (r.stderr or b"").decode("utf-8", "replace").strip()
            return fail(f"candidate failed to load cleanly: {stderr[-400:]}"
                        if stderr else "candidate failed to load cleanly")

        # Advisory display label from the verified child — never gates the verdict.
        runtime_name = (r.stdout or b"").decode("utf-8", "replace").strip()[:200]

    return True, {
        "ok": True,
        "agent_class": info["agent_class"],
        "tool_name": info["tool_name"] or runtime_name or info["agent_class"],
    }


class MolterAgent(BasicAgent):
    def __init__(self):
        self.name = "Molter"
        self.metadata = {
            "name": self.name,
            "description": (
                "Autonomously acquire/evolve a Brainstem capability. Actions: search_capability "
                "(find shape-similar agents in the AIBAST RAR), acquire (sha-verified hot-load a base "
                "as molt 0), mutate (verify+install an LLM-written mutation of the current source, or "
                "return its failure lesson), generate (same, from scratch when the RAR has no match), "
                "rollback (restore the last good molt), molt_log, status. Headless — drive it over /chat."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": [
                        "search_capability", "acquire", "mutate", "generate",
                        "rollback", "molt_log", "status"]},
                    "request": {"type": "string", "description": "The capability the user needs, in plain words (search_capability/generate)."},
                    "capability": {"type": "string", "description": "A short slug naming the capability being forged (acquire/mutate/generate)."},
                    "agent_name": {"type": "string", "description": "acquire: the RAR agent name to pull as the base (from search_capability results)."},
                    "source": {"type": "string", "description": "mutate/generate: the FULL agent.py source the Brainstem's LLM produced. This agent verifies it before it ever goes live."},
                    "note": {"type": "string", "description": "mutate/generate: one line on what this generation changed/attempts (recorded on the molt)."},
                    "to_generation": {"type": "integer", "description": "rollback: molt generation to restore (default: the last good one before the current)."},
                    "top_k": {"type": "integer", "description": "search_capability: how many candidates to return (default 5)."},
                },
                "required": ["action"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    # ---- helpers -----------------------------------------------------------
    def _cap_dir(self, cap):
        return os.path.join(MOLTS, _slug(cap))

    def _record_molt(self, cap, source, verdict, note, parent, kind):
        d = self._cap_dir(cap)
        st = _load_state()
        entry = st["capabilities"].setdefault(_slug(cap), {"live_generation": None, "molts": []})
        gen = len(entry["molts"])
        gdir = os.path.join(d, f"gen-{gen:03d}")
        os.makedirs(gdir, exist_ok=True)
        with open(os.path.join(gdir, "agent.py"), "w", encoding="utf-8") as fh:
            fh.write(source)
        meta = {"generation": gen, "kind": kind, "note": (note or "").strip(),
                "parent": parent, "at": _now(), "verdict": "verified" if verdict[0] else "catastrophic",
                "detail": verdict[1], "sha256": sha256(source.encode()).hexdigest()}
        with open(os.path.join(gdir, "molt.json"), "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=2)
        entry["molts"].append(meta)
        _save_state(st)
        return gen, meta

    @staticmethod
    def _is_sacred_brainstem(d):
        """Refuse unless this is provably the current isolated twin's agents dir."""
        marker = (os.environ.get("BRAINSTEM_BETA_TWIN") or "").strip()
        if not marker or marker in (".", "..") or os.path.basename(marker) != marker:
            return True
        parts = os.path.realpath(d).replace("\\", "/").rstrip("/").split("/")
        return len(parts) < 3 or parts[-3:] != ["twins", marker, "agents"]

    def _go_live(self, cap, source, tool_name, generation):
        if self._is_sacred_brainstem(LIVE_DIR):
            raise RuntimeError(
                "Refusing to install a molt outside a proven isolated twin agents dir. "
                "Molting happens only when BRAINSTEM_BETA_TWIN matches the real "
                ".../twins/<id>/agents path. The molt is archived on device."
            )
        """Install a specific verified generation as the live agent the kernel
        discovers. The generation is passed explicitly — a rollback installs an
        OLD molt's source, so live_generation must be that molt, never the
        newest one on the pile."""
        filename = _safe_agent_name(f"{_slug(cap)}_agent.py", cap)
        live_path = os.path.join(LIVE_DIR, filename)
        tmp = live_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(source)
        os.replace(tmp, live_path)
        os.chmod(live_path, 0o600)
        st = _load_state()
        entry = st["capabilities"][_slug(cap)]
        entry["live_generation"] = generation
        entry["live_file"] = filename
        entry["live_tool"] = tool_name
        _save_state(st)
        return live_path

    def _lessons(self, cap):
        st = _load_state()
        entry = st["capabilities"].get(_slug(cap), {})
        return [f"gen {m['generation']} ({m['kind']}): {m['detail'].get('lesson', m['verdict'])}"
                for m in entry.get("molts", []) if m["verdict"] == "catastrophic"]

    # ---- actions -----------------------------------------------------------
    def perform(self, **kw):
        action = (kw.get("action") or "").strip()
        try:
            return {
                "search_capability": self._search, "acquire": self._acquire,
                "mutate": lambda a: self._forge(a, kind="mutation"),
                "generate": lambda a: self._forge(a, kind="generation"),
                "rollback": self._rollback, "molt_log": self._molt_log,
                "status": self._status,
            }.get(action, lambda a: f"Unknown action '{action}'.")(kw)
        except Exception as e:
            return f"Molter error: {type(e).__name__}: {e}"

    def _search(self, a):
        request = (a.get("request") or "").strip()
        if not request:
            return "search_capability needs a 'request' — the capability you need, in plain words."
        top_k = int(a.get("top_k") or 5)
        try:
            reg = _fetch(AIBAST_REGISTRY)
        except Exception as e:
            return f"Could not reach the AIBAST RAR ({AIBAST_REGISTRY}): {e}"
        want = _tokens(request)
        scored = []
        for ag in reg.get("agents", []):
            if not ag.get("_file") or not ag.get("_sha256"):
                continue
            hay = _tokens(" ".join([ag.get("display_name", ""), ag.get("description", ""),
                                    ag.get("category", ""), " ".join(ag.get("tags", []))]))
            overlap = len(want & hay)
            if overlap:
                scored.append((overlap / max(1, len(want)), overlap, ag))
        scored.sort(key=lambda x: (-x[0], -x[1]))
        top = scored[:top_k]
        if not top:
            return (f"No shape-similar agent in the AIBAST RAR for '{request}'. "
                    "There is nothing to mutate from — use action=generate with a from-scratch "
                    "agent.py written for this request (I will verify and molt it).")
        lines = [f"AIBAST RAR candidates for '{request}' (closest shape first):"]
        for sim, ov, ag in top:
            lines.append(f"- {ag['name']} · {ag.get('display_name','')} — {int(sim*100)}% shape match "
                         f"({ov} shared concepts). {ag.get('description','')[:80]}")
        lines.append("Pick the closest with action=acquire, agent_name='<name>', capability='<slug>'. "
                     "I hot-load it as molt 0; then write a mutation with action=mutate.")
        return "\n".join(lines)

    def _acquire(self, a):
        name = (a.get("agent_name") or "").strip()
        cap = (a.get("capability") or name.split("/")[-1]).strip()
        if not name:
            return "acquire needs agent_name (from search_capability) and a capability slug."
        try:
            reg = _fetch(AIBAST_REGISTRY)
        except Exception as e:
            return f"Could not reach the AIBAST RAR: {e}"
        ag = next((x for x in reg.get("agents", []) if x.get("name") == name), None)
        if not ag:
            return f"'{name}' is not in the AIBAST RAR. Run action=search_capability first."
        url = AIBAST_RAW + "/".join(urllib.request.quote(p) for p in ag["_file"].split("/"))
        try:
            data = _fetch(url, as_bytes=True)
        except Exception as e:
            return f"Could not fetch {name} bytes: {e}"
        digest = sha256(data).hexdigest()
        if digest != ag["_sha256"].lower():
            return (f"REFUSED: {name} bytes hash {digest[:12]}… but the RAR pins {ag['_sha256'][:12]}… "
                    "— not acquiring an unverified base.")
        source = data.decode("utf-8")
        verdict = _verify(source)
        gen, meta = self._record_molt(cap, source, verdict, f"acquired base {name} (sha {digest[:12]})",
                                      parent=None, kind="acquisition")
        if not verdict[0]:
            return (f"Acquired {name} as molt {gen} but it did NOT smoke-load here "
                    f"(lesson: {verdict[1].get('lesson')}). It is archived but NOT live. "
                    "You can still mutate from its source with action=mutate.")
        live = self._go_live(cap, source, verdict[1].get("tool_name", cap), gen)
        return (f"Grew + hot-loaded {name} as molt {gen} for capability '{_slug(cap)}' "
                f"(tool '{verdict[1].get('tool_name')}', sha {digest[:12]}). It is LIVE now — usable "
                "on the next message. To fit it to the exact request, write a mutation with "
                "action=mutate, capability='" + _slug(cap) + "', source=<full mutated agent.py>.")

    def _forge(self, a, kind):
        cap = (a.get("capability") or "").strip()
        source = a.get("source")
        note = a.get("note") or ""
        if not cap or not source:
            base_hint = ""
            if kind == "mutation":
                base_hint = (" Provide the FULL mutated agent.py in 'source' — start from the current "
                             "live/base source and change it to fit the request.")
            return (f"{kind} needs capability='<slug>' and source=<full agent.py>." + base_hint)
        lessons = self._lessons(cap)
        verdict = _verify(source)
        parent = None
        st = _load_state()
        entry = st["capabilities"].get(_slug(cap))
        if entry and entry.get("molts"):
            parent = entry.get("live_generation", len(entry["molts"]) - 1)
        gen, meta = self._record_molt(cap, source, verdict, note, parent=parent, kind=kind)
        if verdict[0]:
            self._go_live(cap, source, verdict[1].get("tool_name", cap), gen)
            return (f"Generation {gen} VERIFIED and now LIVE for '{_slug(cap)}' "
                    f"(tool '{verdict[1].get('tool_name')}'). {('Note: ' + note) if note else ''}\n"
                    "Molt archived on device; roll back anytime with action=rollback.")
        # Catastrophic: refuse to go live, roll back to last good, hand back the lesson.
        rolled = self._restore_last_good(cap)
        exhaust = [f"Generation {gen} was CATASTROPHIC — refused, not installed.",
                   f"Lesson (stage {verdict[1].get('stage','smoke')}): {verdict[1].get('lesson')}"]
        if verdict[1].get("trace"):
            exhaust.append(f"trace tail: {verdict[1]['trace'][-300:]}")
        exhaust.append(f"Rolled back to {rolled}." if rolled else "No earlier good molt to roll back to; capability stays unset.")
        if lessons:
            exhaust.append("Prior lessons this run: " + " | ".join(lessons[-3:]))
        exhaust.append("Write the NEXT mutation with action=" + ("mutate" if kind == "mutation" else "generate")
                       + " addressing that lesson — this feedback is your data to adjust from.")
        return "\n".join(exhaust)

    def _restore_last_good(self, cap):
        st = _load_state()
        entry = st["capabilities"].get(_slug(cap))
        if not entry:
            return None
        for m in reversed(entry["molts"][:-1]):   # skip the just-failed one
            if m["verdict"] == "verified":
                gdir = os.path.join(self._cap_dir(cap), f"gen-{m['generation']:03d}")
                src = open(os.path.join(gdir, "agent.py"), encoding="utf-8").read()
                self._go_live(cap, src, m["detail"].get("tool_name", cap), m["generation"])
                return f"generation {m['generation']}"
        # nothing good before it — remove any live file so a broken cap isn't served
        if entry.get("live_file"):
            try:
                os.remove(os.path.join(LIVE_DIR, entry["live_file"]))
            except OSError:
                pass
            entry["live_generation"] = None
            _save_state(st)
        return None

    def _rollback(self, a):
        cap = (a.get("capability") or "").strip()
        st = _load_state()
        entry = st["capabilities"].get(_slug(cap))
        if not entry or not entry["molts"]:
            return f"No molts for '{_slug(cap)}' to roll back to."
        target = a.get("to_generation")
        candidates = [m for m in entry["molts"] if m["verdict"] == "verified"]
        if target is not None:
            m = next((x for x in entry["molts"] if x["generation"] == int(target)), None)
            if not m or m["verdict"] != "verified":
                return f"Generation {target} is not a verified molt; pick a verified one from molt_log."
        else:
            m = candidates[-2] if len(candidates) >= 2 else (candidates[-1] if candidates else None)
        if not m:
            return f"No verified molt to roll back to for '{_slug(cap)}'."
        gdir = os.path.join(self._cap_dir(cap), f"gen-{m['generation']:03d}")
        src = open(os.path.join(gdir, "agent.py"), encoding="utf-8").read()
        self._go_live(cap, src, m["detail"].get("tool_name", cap), m["generation"])
        return f"Rolled '{_slug(cap)}' back to generation {m['generation']} (tool '{m['detail'].get('tool_name')}'). It is LIVE."

    def _molt_log(self, a):
        cap = (a.get("capability") or "").strip()
        st = _load_state()
        entry = st["capabilities"].get(_slug(cap))
        if not entry:
            caps = list(st["capabilities"].keys())
            return f"No molts for '{_slug(cap)}'. Capabilities on device: {caps or 'none'}."
        lines = [f"Molt history for '{_slug(cap)}' (live = generation {entry.get('live_generation')}):"]
        for m in entry["molts"]:
            live = " ← LIVE" if m["generation"] == entry.get("live_generation") else ""
            lesson = f" — {m['detail'].get('lesson')}" if m["verdict"] == "catastrophic" else ""
            lines.append(f"  gen {m['generation']} [{m['kind']}] {m['verdict']}{live}: {m['note'] or ''}{lesson}")
        return "\n".join(lines)

    def _status(self, a):
        st = _load_state()
        caps = {k: {"live_generation": v.get("live_generation"), "molts": len(v["molts"]),
                    "live_tool": v.get("live_tool")}
                for k, v in st["capabilities"].items()}
        return json.dumps({"forge_home": HOME, "live_dir": LIVE_DIR, "rar": AIBAST_REGISTRY,
                           "capabilities": caps}, indent=2)
