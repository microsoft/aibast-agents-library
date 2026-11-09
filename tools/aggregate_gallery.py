#!/usr/bin/env python3
"""Inbound aggregation: carry Copilot Studio Gallery submissions in this library, unchanged.

For each slug in tools/gallery_inbound.json the tool copies metadata.json, README.md and the exploded
solution/ (or app/) from the gallery checkout at the commit pinned in tools/gallery_contract.json into
submissions/<slug>/ byte for byte, and writes library.json beside them with the provenance the site
shows ("from the Copilot Studio Gallery"), the source commit and the gallery's MIT licence. Nothing is
rewritten: the folder stays importable into the gallery exactly as it came out.

A slug that collides with one of ours (tools/gallery_submissions.json) is refused. `--check` verifies
every carried folder still matches the pinned commit. The gallery repository is read, never written.

    GALLERY_CHECKER_DIR=<existing clone> python tools/aggregate_gallery.py [--check]
"""
from __future__ import annotations

import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "tools" / "gallery_contract.json"
INBOUND = ROOT / "tools" / "gallery_inbound.json"
OURS = ROOT / "tools" / "gallery_submissions.json"
CARRIED = ("metadata.json", "README.md", "solution", "app")
SIDECAR_SCHEMA = "aibast-library-solution/1.0"


def gallery_checkout(contract: dict) -> Path:
    work = Path(os.environ.get("GALLERY_CHECKER_DIR") or tempfile.mkdtemp(prefix="csg-"))
    if not (work / ".git").is_dir():
        subprocess.run(["git", "clone", "--quiet", "--filter=blob:none", contract["repository"], str(work)], check=True)
    subprocess.run(["git", "-C", str(work), "fetch", "--quiet", "origin", contract["commit"]], check=False)
    subprocess.run(["git", "-C", str(work), "checkout", "--quiet", contract["commit"]], check=True)
    return work


def sidecar(slug: str, metadata: dict, contract: dict) -> dict:
    return {
        "schema": SIDECAR_SCHEMA,
        "slug": slug,
        "origin": {
            "name": "Copilot Studio Gallery",
            "url": f"https://microsoft.github.io/copilot-studio-gallery/submissions/{slug}/",
            "repository": contract["repository"],
            "commit": contract["commit"],
            "license": "MIT",
            "carried_on": datetime.now(timezone.utc).date().isoformat(),
        },
        "headline": None,
        "industries": [],
        "personas": [],
        "products": [],
        "requirements": [],
        "capabilities": [],
        "outcomes": [],
        "sample_prompts": [],
        "assets": {},
        "learn": {},
        "install": {},
        "tests": {"cases": None, "passed": None},
    }


def folders_match(src: Path, dst: Path) -> bool:
    for name in CARRIED:
        a, b = src / name, dst / name
        if a.exists() != b.exists():
            return False
        if a.is_file() and not filecmp.cmp(a, b, shallow=False):
            return False
        if a.is_dir():
            cmp = filecmp.dircmp(a, b)
            stack = [cmp]
            while stack:
                c = stack.pop()
                if c.left_only or c.right_only or c.diff_files or c.funny_files:
                    return False
                stack.extend(c.subdirs.values())
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--only", action="append", default=[])
    args = ap.parse_args(argv)
    contract = json.loads(CONTRACT.read_text())
    slugs = args.only or json.loads(INBOUND.read_text())["slugs"]
    ours = set(json.loads(OURS.read_text())["submissions"])
    if not slugs:
        print("gallery inbound: no slugs listed in tools/gallery_inbound.json; nothing to carry")
        return 0
    clash = sorted(set(slugs) & ours)
    if clash:
        print(f"refused: {', '.join(clash)} are our own slugs; a carried gallery entry cannot replace them")
        return 1
    work = gallery_checkout(contract)
    rc = 0
    for slug in slugs:
        src = work / "submissions" / slug
        dst = ROOT / "submissions" / slug
        if not (src / "metadata.json").is_file():
            print(f"{slug}: not in the gallery at {contract['commit'][:8]}")
            rc = 1
            continue
        if args.check:
            ok = dst.is_dir() and folders_match(src, dst) and (dst / "library.json").is_file()
            print(f"{'ok  ' if ok else 'DIFF'} {slug}")
            rc = rc or (0 if ok else 1)
            continue
        if dst.exists():
            shutil.rmtree(dst)
        dst.mkdir(parents=True)
        for name in CARRIED:
            if (src / name).is_dir():
                shutil.copytree(src / name, dst / name)
            elif (src / name).is_file():
                shutil.copy2(src / name, dst / name)
        metadata = json.loads((dst / "metadata.json").read_text())
        (dst / "library.json").write_text(json.dumps(sidecar(slug, metadata, contract), indent=2, ensure_ascii=False) + "\n")
        print(f"carried {slug} from the gallery at {contract['commit'][:8]}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
