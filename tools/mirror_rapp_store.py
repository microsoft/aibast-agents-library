#!/usr/bin/env python3
"""Host a curated copy of the public RAPP Store catalog in this repository for the beta app.

usage: python tools/mirror_rapp_store.py --write [--source URL] | --check

Copies only the entries in ALLOWED (licensed for redistribution, business-neutral names, no run-time downloads from
personal repositories), downloads each file the
entry pins, verifies its sha256 against the upstream catalog, stores it under beta/store/<id>/, and writes
beta/store/index.json (schema rapp-store/1.0) with every URL pointing at this repository. --check verifies that
every stored file still matches the hash its index entry names.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "beta" / "store"
INDEX = STORE / "index.json"
SOURCE = "https://raw.githubusercontent.com/kody-w/RAPP_Store/main/index.json"
RAW = "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/beta/store/"
ALLOWED = (
    "agent_team", "project_tracker", "pii_scout", "json_doctor", "markdown_medic",
    "csv_surgeon", "log_detective",
)
LICENSES = ("MIT", "Apache-2.0")
FILES = ("singleton", "ui", "egg", "skill", "tools", "organ")


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "aibast-store-mirror"}), timeout=60) as r:
        return r.read()


def write(source: str) -> int:
    upstream = json.loads(fetch(source))
    entries = []
    for entry in upstream["rapplications"]:
        if entry.get("id") not in ALLOWED:
            continue
        if entry.get("access", "public") != "public" or entry.get("license") not in LICENSES:
            raise SystemExit(f"{entry['id']}: not public or not {LICENSES}")
        out = {k: v for k, v in entry.items() if not k.endswith("_url") and k not in ("private_repo", "repo_url", "homepage", "spec_post", "install")}
        out["mirrored_from"] = {"catalog": "RAPP Store", "id": entry["id"], "version": entry.get("version")}
        for kind in FILES:
            url, digest, name = entry.get(f"{kind}_url"), entry.get(f"{kind}_sha256"), entry.get(f"{kind}_filename")
            if not url:
                continue
            name = name or url.rstrip("/").rsplit("/", 1)[-1]
            body = fetch(url)
            if digest and hashlib.sha256(body).hexdigest() != digest:
                raise SystemExit(f"{entry['id']}: {kind} does not match its pinned sha256")
            if not digest:
                # The upstream catalog pins no hash for this file; record the hash of the copy taken here.
                out[f"{kind}_sha256"] = hashlib.sha256(body).hexdigest()
                out.setdefault("hashes_recorded_at_mirror", []).append(kind)
                out[f"{kind}_filename"] = name
            path = STORE / entry["id"] / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
            out[f"{kind}_url"] = f"{RAW}{entry['id']}/{name}"
        entries.append(out)
    missing = set(ALLOWED) - {e["id"] for e in entries}
    if missing:
        raise SystemExit(f"not in the upstream catalog: {sorted(missing)}")
    index = {"schema": "rapp-store/1.0", "name": "AIBAST beta store",
             "description": "A curated copy of public RAPP Store entries, hosted in this repository for the beta app. "
                            "Built by tools/mirror_rapp_store.py; every file is checked against its pinned sha256.",
             "rapplications": sorted(entries, key=lambda e: e["id"])}
    INDEX.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} entries")
    return 0


def check() -> int:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    problems = []
    for entry in index["rapplications"]:
        for kind in FILES:
            url = entry.get(f"{kind}_url")
            if not url:
                continue
            if not url.startswith(RAW):
                problems.append(f"{entry['id']}: {kind} url is not in this repository")
                continue
            path = STORE / url[len(RAW):]
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != entry.get(f"{kind}_sha256"):
                problems.append(f"{entry['id']}: {kind} file missing or changed")
    for line in problems:
        print(line, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--source", default=SOURCE)
    args = parser.parse_args()
    sys.exit(write(args.source) if args.write else check())
