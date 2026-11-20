#!/usr/bin/env python3
"""The deploy standard's second target: the person's own Brainstem.

Same six verbs as the Copilot Studio deploy agent, so one solution moves between targets:

    python3 tools/brainstem_target.py <check|look|probe|plan|deploy|undo> <solution> [--yes]

It talks to a Brainstem only over its public addresses (/health, /chat, /agents). It
changes nothing unless --yes is given, and it never replaces an agent file it did not put there.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

VERBS = ("check", "look", "probe", "plan", "deploy", "undo")
DEFAULT_SOURCE = "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/"
DISCLAIMER = ("This is an experimental project managed by a v-team from the Artificial Intelligence Business Applications "
              "Specialist Team (AIBAST), not an officially supported Microsoft product.")


class TargetError(Exception):
    pass


def _fetch(rel: str, source: str) -> bytes:
    if "://" not in source:
        with open(os.path.join(source, rel), "rb") as fh:
            return fh.read()
    with urllib.request.urlopen(source.rstrip("/") + "/" + urllib.parse.quote(rel), timeout=60) as r:
        return r.read()


def _call(url: str, method: str = "GET", body: bytes | None = None, ctype: str = "", timeout: int = 180) -> dict:
    req = urllib.request.Request(url, data=body, method=method, headers={"Content-Type": ctype} if ctype else {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as exc:
        try:
            return {"_status": exc.code, **json.loads(exc.read() or b"{}")}
        except ValueError:
            return {"_status": exc.code, "error": str(exc)}
    except (urllib.error.URLError, OSError) as exc:
        raise TargetError(f"The Brainstem at {url.split('/')[2]} did not answer. Start it, then try again.") from exc


def _recipe(slug: str, source: str) -> dict:
    try:
        return json.loads(_fetch(f"solutions/{slug}/deployment.json", source))
    except Exception as exc:  # noqa: BLE001
        raise TargetError(f"The library has no solution called {slug}.") from exc


def _loaded(base: str) -> list:
    agents = _call(base + "/health").get("agents") or []
    return [a if isinstance(a, str) else a.get("name", "") for a in agents]


def check(base: str) -> dict:
    h = _call(base + "/health")
    return {"ok": h.get("status") == "ok", "brainstem": base, "agents": _loaded(base),
            "summary": "The Brainstem is running." if h.get("status") == "ok" else "The Brainstem answered but is not ready."}


def look(slug: str, base: str, source: str) -> dict:
    r = _recipe(slug, source)
    there = r["expected_tool"] in _loaded(base)
    return {"ok": True, "brainstem": base, "agent": r["display_name"], "already_installed": there,
            "recommend": "keep" if there else "add", "data": "sample", "disclaimer": DISCLAIMER,
            "summary": (f"{r['display_name']} is already in this Brainstem." if there else
                        f"{r['display_name']} is not in this Brainstem yet. It answers from sample data.")}


def plan(slug: str, base: str, source: str) -> dict:
    r = _recipe(slug, source)
    there = r["expected_tool"] in _loaded(base)
    return {"ok": False, "needs_confirmation": True, "brainstem": base, "agent": r["display_name"], "file": r["target_filename"],
            "already_installed": there, "disclaimer": DISCLAIMER,
            "steps": [f"Save {r['target_filename']} in the Brainstem's agents folder", "Ask it one question to prove it answers",
                      "Report the result and how to undo it"],
            "summary": "Nothing changed. Review the plan, then confirm to deploy."
                       + (" It is already installed: deploying again refreshes the same file." if there else "")}


def probe(slug: str, base: str, source: str) -> dict:
    """Asks the solution's own first question through chat and checks the answer carries what the library says it must."""
    r = _recipe(slug, source)
    test = r.get("smoke_test") or {}
    if r["expected_tool"] not in _loaded(base):
        return {"ok": False, "checked": False, "summary": f"{r['display_name']} is not in this Brainstem. Deploy it first."}
    out = _call(base + "/chat", "POST", json.dumps({"user_input": test.get("prompt", ""), "conversation_history": []}).encode(),
                "application/json", timeout=300)
    answer = out.get("response") or ""
    if not answer:
        return {"ok": False, "checked": False, "summary": "The Brainstem gave no answer. It may not be signed in. " + str(out.get("error", ""))[:200]}
    logs = str(out.get("agent_logs", ""))
    missing = [m for m in test.get("must_include", []) if m not in answer and m not in logs]
    called = r["expected_tool"] in logs
    return {"ok": called and not missing, "checked": True, "called_agent": called, "missing": missing, "answer_starts": answer[:200],
            "summary": "The agent answered its own first question." if called and not missing else
                       "The answer did not carry what the library says it must."}


def deploy(slug: str, base: str, source: str, confirm: bool) -> dict:
    r = _recipe(slug, source)
    if not confirm:
        return plan(slug, base, source)
    data = _fetch(r["source_path"], source)
    sha = hashlib.sha256(data).hexdigest()
    try:
        catalog = json.loads(_fetch("registry.json", source))
        want = next((a.get("_sha256") for a in catalog.get("agents", []) if a.get("name") == r["name"]), None)
    except Exception:  # noqa: BLE001
        want = None
    if want and want != sha:
        raise TargetError("The agent file does not match the catalog's fingerprint. Nothing was saved.")
    mark = uuid.uuid4().hex
    body = (f"--{mark}\r\nContent-Disposition: form-data; name=\"sha256\"\r\n\r\n{sha}\r\n"
            f"--{mark}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{r['target_filename']}\"\r\n"
            "Content-Type: text/x-python\r\n\r\n").encode() + data + f"\r\n--{mark}--\r\n".encode()
    out = _call(base + "/agents/import", "POST", body, f"multipart/form-data; boundary={mark}")
    if out.get("_status") or out.get("error"):
        raise TargetError(f"The Brainstem did not take the agent. Nothing else changed. {str(out.get('error', ''))[:200]}")
    there = r["expected_tool"] in _loaded(base)
    return {"ok": there, "brainstem": base, "agent": r["display_name"], "fingerprint_checked_against_catalog": bool(want),
            "test_question": (r.get("smoke_test") or {}).get("prompt", ""), "undo": f"undo {slug}", "disclaimer": DISCLAIMER,
            "summary": (f"{r['display_name']} is in the Brainstem and answers from sample data." if there else
                        "The file was saved but the Brainstem does not list the agent.")}


def undo(slug: str, base: str, source: str, confirm: bool) -> dict:
    r = _recipe(slug, source)
    if not confirm:
        return {"ok": False, "needs_confirmation": True, "summary": f"This removes {r['target_filename']} from the Brainstem. Confirm to remove."}
    out = _call(base + "/agents/" + urllib.parse.quote(r["target_filename"]), "DELETE")
    if out.get("_status") == 404:
        return {"ok": True, "summary": "It was not there. Nothing changed."}
    if out.get("_status") or out.get("error"):
        raise TargetError(f"The Brainstem did not remove it. {str(out.get('error', ''))[:200]}")
    return {"ok": r["expected_tool"] not in _loaded(base), "summary": f"Removed {r['display_name']} from the Brainstem."}


def run(kw: dict) -> dict:
    op, slug = kw.get("operation"), (kw.get("solution") or "").strip()
    base = (kw.get("url") or "http://localhost:7071").rstrip("/")
    source = kw.get("source") or os.environ.get("AIBAST_DEPLOY_SOURCE") or DEFAULT_SOURCE
    try:
        if op == "check":
            return check(base)
        if op not in VERBS:
            return {"ok": False, "summary": f"Unknown step. Use one of: {', '.join(VERBS)}."}
        if not slug:
            return {"ok": False, "summary": "Say which solution."}
        if op == "look":
            return look(slug, base, source)
        if op == "probe":
            return probe(slug, base, source)
        if op == "plan":
            return plan(slug, base, source)
        if op == "deploy":
            return deploy(slug, base, source, bool(kw.get("confirm")))
        return undo(slug, base, source, bool(kw.get("confirm")))
    except TargetError as exc:
        return {"ok": False, "summary": str(exc)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("operation", choices=list(VERBS))
    ap.add_argument("solution", nargs="?", default="")
    ap.add_argument("--url", default="http://localhost:7071")
    ap.add_argument("--source", default="")
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args(argv)
    out = run({"operation": a.operation, "solution": a.solution, "url": a.url, "source": a.source, "confirm": a.yes})
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") or out.get("needs_confirmation") else 1


if __name__ == "__main__":
    sys.exit(main())
