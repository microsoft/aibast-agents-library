#!/usr/bin/env python3
"""
validate_agent.py — check an agent file against the AIBAST Agent Constitution.

Covers the mechanically checkable articles (II-V). Article I (does it implement
an advertised one-pager) and Article VI (do the locked demo cases pass live) are
checked by a human reading solutions.json and by tools/run_demo_cases.py.

    python tools/validate_agent.py path/to/agent.py
    python tools/validate_agent.py --all

Exit code is 1 if any agent has a violation.
"""

import argparse
import ast
import importlib.util
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGENTS = REPO / "agents" / "@aibast-agents-library"
TOOL_NAME = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def manifest_of(tree):
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "__manifest__":
            try:
                return ast.literal_eval(n.value)
            except (ValueError, TypeError):
                return None
    return None


def agent_class(tree):
    return next((n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)
                 and any(getattr(b, "id", "") == "BasicAgent" for b in n.bases)), None)


def check(path):
    """Return (violations, warnings)."""
    v, w = [], []
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [f"II: does not parse — {e}"], []

    # -- Article II: it must load ------------------------------------------
    if not path.name.endswith("_agent.py"):
        v.append("II.2: filename must end in _agent.py or the Brainstem never discovers it")
    cls = agent_class(tree)
    if not cls:
        v.append("II.3: no class subclassing BasicAgent")

    m = re.search(r"self\.name\s*=\s*['\"]([^'\"]+)['\"]", src)
    if not m:
        v.append("II.1: self.name is not set to a literal")
    elif not TOOL_NAME.match(m.group(1)):
        v.append(f"II.1: self.name {m.group(1)!r} is not a legal tool name "
                 f"(^[A-Za-z0-9_-]{{1,64}}$) — this agent CANNOT be loaded")

    man = manifest_of(tree)
    if man is None:
        v.append("I.3: no parseable __manifest__")
    else:
        for field in ("name", "display_name", "description", "category", "version"):
            if not man.get(field):
                v.append(f"I.3: __manifest__ missing {field}")

    if cls and not any(isinstance(n, ast.FunctionDef) and n.name == "perform"
                       for n in cls.body):
        v.append("II.4: no perform() method")

    # -- Article III: reachable in conversation -----------------------------
    if '"parameters"' not in src and "'parameters'" not in src:
        v.append("III.1: no parameters schema — the model can only ever call the "
                 "default operation, every other operation is unreachable from chat")
    ops = re.search(r'"enum"\s*:\s*\[([^\]]+)\]', src)
    op_names = re.findall(r'"([a-z_]{3,40})"', ops.group(1)) if ops else []
    if not op_names:
        w.append("III.3: no operation enum found — is this a single-operation agent?")

    # the tool description must be routing prose, not just the marketing line
    # III.2 is checked at runtime below, by comparing the tool description the
    # model actually receives against the advertised manifest summary.

    if op_names and not re.search(r'"description"\s*:\s*\(?\s*"?[^"]*'
                                 + re.escape(op_names[0]), src):
        w.append("III.3: operations may lack per-operation routing descriptions")

    # -- Article IV: the data plane ----------------------------------------
    if "date.today()" not in src and "datetime.now()" not in src:
        w.append("IV.3: no run-date anchor — check for hard-coded dates that will go stale")
    hard_dates = re.findall(r'"(20\d\d-\d\d-\d\d)"', src)
    if hard_dates:
        w.append(f"IV.3: {len(hard_dates)} hard-coded date literal(s) e.g. {hard_dates[0]} — "
                 f"these freeze the demo")
    if re.search(r"requests\.|urllib\.request|httpx|aiohttp", src):
        v.append("IV.1/VII.3: makes network calls — the data plane must be static and offline")

    # IV.1/IV.5: a scaffold that was never filled in. "circuit": "circuit 3" or
    # "TODO real cause" is structurally valid and semantically empty, which no
    # amount of AST checking would otherwise catch.
    placeholder = re.findall(r'"(\w+)"\s*:\s*"(?:TODO[^"]*|\1[ _-]?\d+)"', src)
    if placeholder:
        v.append(f"IV.1/IV.5: {len(placeholder)} placeholder value(s) e.g. "
                 f"{placeholder[0]!r} — the data plane must carry real domain shapes, "
                 f"not field names with numbers")
    imports = {n.module.split(".")[0] for n in ast.walk(tree)
               if isinstance(n, ast.ImportFrom) and n.module}
    imports |= {a.name.split(".")[0] for n in ast.walk(tree)
                if isinstance(n, ast.Import) for a in n.names}
    third_party = imports - {"os", "sys", "json", "re", "datetime", "math", "random",
                             "collections", "typing", "basic_agent", "dataclasses",
                             "itertools", "functools", "textwrap", "statistics"}
    if third_party:
        v.append(f"VII.3: imports outside the standard library: {sorted(third_party)}")

    # -- Article V: the output ---------------------------------------------
    if cls:
        returns_str = any(
            isinstance(n, ast.FunctionDef) and n.name == "perform"
            and isinstance(getattr(n, "returns", None), ast.Name) and n.returns.id == "str"
            for n in cls.body)
        if not returns_str:
            w.append("II.4: perform() is not annotated -> str")

    if "__main__" not in src:
        w.append("VI: no __main__ block — cannot be exercised standalone")

    # -- does it run? -------------------------------------------------------
    try:
        spec = importlib.util.spec_from_file_location("candidate", path)
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(AGENTS / "templates"))
        spec.loader.exec_module(mod)
        cls_obj = next((getattr(mod, n) for n in dir(mod)
                        if isinstance(getattr(mod, n), type)
                        and getattr(mod, n).__name__ == (cls.name if cls else "")), None)
        if cls_obj:
            inst = cls_obj()
            tool_desc = (inst.metadata or {}).get("description", "")
            if man and tool_desc.strip() == (man.get("description") or "").strip():
                v.append("III.2: the tool description IS the manifest's advertised summary. "
                         "That is marketing copy; the model routes on this string and will "
                         "miss questions phrased in the user's own words")
            elif len(tool_desc.split()) < 25:
                w.append(f"III.2: tool description is only {len(tool_desc.split())} words — "
                         f"it is the entire contract the model sees")
            if not (inst.metadata or {}).get("parameters", {}).get("properties"):
                v.append("III.1: parameters schema has no properties — nothing can be passed")
            for op in (op_names or [None]):
                out = inst.perform(**({"operation": op} if op else {}))
                if not isinstance(out, str) or not out.strip():
                    v.append(f"II.4: operation {op!r} returned {type(out).__name__}, not text")
                elif len(out.split()) < 20:
                    w.append(f"IV.4: operation {op!r} returned only {len(out.split())} words — stub?")
                elif op and not re.search(r"[A-Z]{2,}[-–]?\d|[A-Z]-\d{3,}", out) and "|" not in out:
                    w.append(f"V.1: operation {op!r} names no identifier and has no table")
    except Exception as e:
        v.append(f"II: failed to execute — {type(e).__name__}: {e}")
    finally:
        if str(AGENTS / "templates") in sys.path:
            sys.path.remove(str(AGENTS / "templates"))

    return v, w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--quiet", "-q", action="store_true", help="violations only")
    args = ap.parse_args()

    targets = ([p for p in AGENTS.rglob("*_agent.py")] if args.all
               else [Path(p) for p in args.paths])
    if not targets:
        print("nothing to validate"); return 1

    bad = 0
    for p in sorted(targets):
        v, w = check(p)
        if v or (w and not args.quiet):
            print(f"\n{p.relative_to(REPO) if p.is_absolute() else p}")
        for x in v:
            print(f"  VIOLATION  {x}")
        if not args.quiet:
            for x in w:
                print(f"  warn       {x}")
        bad += bool(v)

    print(f"\n{len(targets) - bad}/{len(targets)} agents pass the constitution")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
