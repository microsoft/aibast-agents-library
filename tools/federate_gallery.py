#!/usr/bin/env python3
"""Federation fetch: read the other libraries named in tools/gallery_federation.json at build time.

For each enabled source: a shallow, submissions-only checkout of its branch (read-only; this tool
has no push path) and its published catalog (solutions.json, for their own download links). The
result lands in <out>/<key>/ with a `.federation.json` beside it (commit, when, catalog rows).
tools/build_site.py --federation <out> then lists their solutions beside ours, rendered from their
files unchanged.

Fail-soft by design: if a source cannot be reached the build goes on without it and says so. Our
site never fails because someone else's is down.

    python tools/federate_gallery.py --out <dir>
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "tools" / "gallery_federation.json"


def sources(root: Path = ROOT) -> list[dict]:
    path = root / "tools" / "gallery_federation.json"
    if not path.exists():
        return []
    return [s for s in json.loads(path.read_text())["sources"] if s.get("enabled")]


def fetch_source(source: dict, out: Path) -> dict | None:
    target = out / source["key"]
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(["git", "clone", "--quiet", "--depth", "1", "--filter=blob:none", "--sparse",
                        "--branch", source["branch"], source["repository"], str(target)], check=True, timeout=300)
        subprocess.run(["git", "-C", str(target), "sparse-checkout", "set", "submissions"], check=True, timeout=300)
        commit = subprocess.run(["git", "-C", str(target), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    except (subprocess.SubprocessError, OSError) as error:
        print(f"federation: {source['key']} unreachable ({type(error).__name__}); building without it", file=sys.stderr)
        shutil.rmtree(target, ignore_errors=True)
        return None
    catalog = []
    if source.get("catalog"):
        try:
            request = urllib.request.Request(source["catalog"], headers={"User-Agent": "aibast-agents-library-site-build"})
            with urllib.request.urlopen(request, timeout=30) as response:
                catalog = json.loads(response.read().decode("utf-8"))
        except Exception as error:  # their catalog is optional; the tree is the source
            print(f"federation: {source['key']} catalog not read ({type(error).__name__}); downloads fall back to built packages", file=sys.stderr)
    record = {
        "schema": "aibast-gallery-federation-fetch/1.0",
        "key": source["key"],
        "commit": commit,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "downloads": {row["slug"]: (row.get("download") or {}).get("url") for row in catalog if isinstance(row, dict) and row.get("slug")},
    }
    (target / ".federation.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    for source in sources():
        record = fetch_source(source, args.out)
        if record:
            folders = sum(1 for p in (args.out / source["key"] / "submissions").iterdir() if (p / "metadata.json").is_file())
            print(f"federation: {source['key']} at {record['commit'][:8]}, {folders} folders, {sum(1 for v in record['downloads'].values() if v)} published downloads")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
