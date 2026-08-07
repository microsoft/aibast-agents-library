#!/usr/bin/env python3
"""
run_demo_cases.py — replay a solution's locked demo cases against a live Brainstem.

The loop this supports: run the demo the way a customer would, watch where the
agent fails the business question, tune the agent.py, then LOCK the case here so
the next run proves it still behaves.

Only the agent files a case needs are hot-loaded. The Brainstem re-reads its
agents directory on every request, so loading is a copy and unloading is a
delete — no restart. Loading the whole catalogue at once makes tool selection
noisy and the model picks nothing, which is a property of the harness, not of
the agent, and it will make a good agent look broken.

    python tools/run_demo_cases.py                       # every locked case
    python tools/run_demo_cases.py building-permit       # one solution
    python tools/run_demo_cases.py --list

Exit code is 1 if any case fails, so this can gate a release.
"""

import argparse
import json
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CASES_DIR = REPO / "tests" / "demo_cases"
AGENTS_DIR = REPO / "agents" / "@aibast-agents-library"
BRAINSTEM = Path.home() / ".brainstem" / "src" / "rapp_brainstem" / "agents"
CHAT = "http://localhost:7071/chat"
HEALTH = "http://localhost:7071/health"


def brainstem_up():
    try:
        with urllib.request.urlopen(HEALTH, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def find_agent(stem):
    hits = list(AGENTS_DIR.rglob(f"{stem}.py"))
    return hits[0] if hits else None


def load(stems):
    """Copy in only these agents. Returns the installed paths."""
    installed = []
    for stem in stems:
        src = find_agent(stem)
        if not src:
            print(f"    !! no agent file named {stem}.py")
            continue
        dst = BRAINSTEM / src.name
        shutil.copy2(src, dst)
        installed.append(dst)
    time.sleep(1)  # let the next request pick them up
    return installed


def unload(paths):
    for p in paths:
        try:
            p.unlink()
        except FileNotFoundError:
            pass


def ask(prompt, timeout=180):
    body = json.dumps({"user_input": prompt, "conversation_history": [],
                       "session_id": "demo-case"}).encode()
    req = urllib.request.Request(CHAT, data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode()).get("response", "")
    except urllib.error.HTTPError as e:
        return f"__HTTP_{e.code}__ {e.read().decode()[:200]}"
    except Exception as e:
        return f"__ERROR__ {type(e).__name__}: {e}"


def run_case(case, answer):
    """Return (passed, [failure reasons])."""
    fails = []
    low = answer.lower()
    if answer.startswith("__"):
        return False, [f"transport failure: {answer[:120]}"]
    for needle in case.get("must_include", []):
        if needle.lower() not in low:
            fails.append(f"missing expected content: {needle!r}")
    for needle in case.get("must_not_include", []):
        if needle.lower() in low:
            fails.append(f"contains forbidden content: {needle!r}")
    minw = case.get("min_words", 0)
    if minw and len(answer.split()) < minw:
        fails.append(f"answer too short: {len(answer.split())} words < {minw}")
    maxw = case.get("max_words")
    if maxw and len(answer.split()) > maxw:
        fails.append(f"answer too long for one screen: {len(answer.split())} words > {maxw}")
    return not fails, fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("solution", nargs="?", help="substring of a case file name")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--verbose", "-v", action="store_true", help="print each answer")
    args = ap.parse_args()

    files = sorted(CASES_DIR.glob("*.json"))
    if args.solution:
        files = [f for f in files if args.solution.lower() in f.stem.lower()]
    if args.list:
        for f in files:
            doc = json.loads(f.read_text())
            print(f"{f.stem:<32} {len(doc['cases'])} case(s)  {doc['solution']}")
        return 0
    if not files:
        print("no demo cases found")
        return 1

    health = brainstem_up()
    if not health:
        print("Brainstem is not answering on localhost:7071 — start it with "
              "`cd rapp_brainstem && ./start.sh`")
        return 1
    print(f"Brainstem up · model {health.get('model', '?')} · "
          f"{len(health.get('agents', []))} agent(s) already loaded\n")

    total = passed = 0
    for f in files:
        doc = json.loads(f.read_text())
        print(f"── {doc['solution']}  (advertised #{doc.get('slot', '?')})")
        installed = load(doc["agent_files"])
        print(f"   hot-loaded: {', '.join(p.name for p in installed) or 'nothing'}")
        try:
            for case in doc["cases"]:
                total += 1
                answer = ask(case["prompt"], case.get("timeout", 180))
                ok, fails = run_case(case, answer)
                passed += ok
                mark = "PASS" if ok else "FAIL"
                print(f"   [{mark}] {case['id']} — {case.get('persona', '')}")
                print(f"          \"{case['prompt'][:96]}\"")
                for r in fails:
                    print(f"          · {r}")
                if args.verbose or not ok:
                    snippet = answer[:400].replace("\n", "\n          ")
                    print(f"          {snippet}")
        finally:
            unload(installed)   # always leave the Brainstem clean
        print()

    print(f"{passed}/{total} demo cases passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
