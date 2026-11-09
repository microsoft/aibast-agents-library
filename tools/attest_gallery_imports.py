#!/usr/bin/env python3
"""Fresh-environment import attestation for every submission, the way the Copilot Studio Gallery's
pull-request template words it: "imported the submitted solution into a fresh environment containing
only its documented prerequisites, without skipping dependency checks."

Imports each submissions/<slug>/ download (the exact ZIP a visitor gets) with the Power Platform CLI,
no --skip-dependency-check, no --force-overwrite, and records the result per slug in
state/gallery_import_attestation.json. The record carries the environment, the ZIP's sha256, the
duration and the CLI's last line; never a token or a connection string.

    python tools/attest_gallery_imports.py --environment https://<org>.crm.dynamics.com/ [--only slug] [--resume]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "gallery_import_attestation.json"
sys.path.insert(0, str(ROOT))
from tools.build_gallery_submissions import discover_submissions, gallery_zip_path  # noqa: E402


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"schema": "aibast-gallery-import-attestation/1.0",
            "note": "One record per submission: the gallery's fresh-environment import attestation, run by tools/attest_gallery_imports.py.",
            "imports": {}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--environment", required=True)
    ap.add_argument("--environment-name", default=None, help="display name recorded beside the URL")
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--resume", action="store_true", help="skip slugs already recorded as imported in this environment")
    ap.add_argument("--max-wait", type=int, default=20, help="minutes per import")
    args = ap.parse_args(argv)
    state = load_state()
    slugs = args.only or discover_submissions(ROOT)
    failures = 0
    for slug in slugs:
        rec = state["imports"].get(slug)
        if args.resume and rec and rec.get("environment") == args.environment and rec.get("imported"):
            continue
        zip_path = ROOT / gallery_zip_path(slug)
        if not zip_path.exists():
            state["imports"][slug] = {"imported": False, "error": "no download ZIP", "checked_at": datetime.now(timezone.utc).isoformat()}
            failures += 1
            continue
        started = time.time()
        for attempt in range(3):
            proc = subprocess.run(["pac", "solution", "import", "--path", str(zip_path), "--environment", args.environment,
                                   "--async", "--max-async-wait-time", str(args.max_wait)],
                                  capture_output=True, text=True)
            text = (proc.stdout + proc.stderr).lower()
            ok = proc.returncode == 0 and ("imported successfully" in text or "succeeded" in text)
            transient = not ok and ("connection reset" in text or "ssl connection" in text or "timed out" in text or "503" in text)
            if ok or not transient:
                break
            time.sleep(15 * (attempt + 1))
        tail = [line.strip() for line in (proc.stdout + proc.stderr).splitlines() if line.strip()][-1:]
        state["imports"][slug] = {
            "imported": ok,
            "environment": args.environment,
            "environment_name": args.environment_name,
            "zip": gallery_zip_path(slug),
            "zip_sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
            "seconds": round(time.time() - started),
            "dependency_check_skipped": False,
            "cli_last_line": tail[0] if tail else "",
            "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        if not ok:
            failures += 1
            state["imports"][slug]["error"] = (proc.stderr or proc.stdout).strip()[-600:]
        STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
        print(f"{'ok  ' if ok else 'FAIL'} {slug} ({state['imports'][slug]['seconds']}s) {tail[0] if tail else ''}", flush=True)
    done = sum(1 for r in state["imports"].values() if r.get("imported"))
    print(f"attestation: {done} of {len(slugs)} imported; {failures} failures this run")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
