#!/usr/bin/env python3
"""aibast: one command for the library's routine jobs. Each subcommand wraps the existing step.

  python tools/aibast.py api build        rebuild api/ and llms.txt (tools/build_library_api.py)
  python tools/aibast.py api check        fail if api/ or llms.txt does not match its sources
  python tools/aibast.py media verify     check every file in the media map against its sha256
  python tools/aibast.py media verify --live
                                          the same, fetched from the raw base in api/registry.json
  python tools/aibast.py pages size       build the Pages artifact into _site and print its size
  python tools/aibast.py demo check <slug> [--base URL]
                                          confirm a solution's demo docs and narration clips exist
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(*args: str) -> int:
    return subprocess.run([PY, *args], cwd=ROOT).returncode


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def media_items() -> list[dict]:
    index = load("api/v1/media/index.json")
    return [item for group in index["groups"] for item in load(group["doc"])["items"]]


def media_verify(live: bool) -> int:
    raw = load("api/registry.json")["raw"]
    bad = 0
    items = media_items()
    for item in items:
        if live:
            with urllib.request.urlopen(raw + item["path"], timeout=60) as response:
                data = response.read()
        else:
            data = (ROOT / item["path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != item["sha256"]:
            bad += 1
            print(f"mismatch: {item['path']}")
    print(f"media: {len(items) - bad} of {len(items)} match their sha256" + (f" ({raw})" if live else ""))
    return 1 if bad else 0


def pages_size() -> int:
    ref = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    code = run("scripts/build_pages_site.py", "--root", ".", "--out", "_site",
               "--owner", "microsoft", "--repo", "aibast-agents-library", "--ref", ref)
    if code:
        return code
    files = [p for p in (ROOT / "_site").rglob("*") if p.is_file()]
    print(f"pages: {len(files)} files, {sum(p.stat().st_size for p in files) / 1e6:.1f} MB in _site")
    return 0


def demo_check(slug: str, base: str | None) -> int:
    def get(path: str) -> dict:
        if base:
            with urllib.request.urlopen(base.rstrip("/") + "/" + path, timeout=60) as response:
                return json.load(response)
        return load(path)

    solution = get(f"api/v1/solutions/{slug}.json")
    scenarios = [s for s in solution["try"]["scenarios"] if s.get("doc")]
    clips = 0
    for scenario in scenarios:
        doc = get(scenario["doc"])
        for segment in (doc.get("narration") or {}).get("segments", []):
            if segment.get("media"):
                clips += 1
                if not base and not (ROOT / segment["media"]["url"]).is_file():
                    print(f"missing clip: {segment['media']['url']}")
                    return 1
    print(f"demo {slug}: {len(scenarios)} recorded scenarios, {clips} narration clips")
    return 0 if scenarios else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aibast", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="area", required=True)
    api = sub.add_parser("api").add_subparsers(dest="action", required=True)
    api.add_parser("build")
    api.add_parser("check")
    media = sub.add_parser("media").add_subparsers(dest="action", required=True)
    verify = media.add_parser("verify")
    verify.add_argument("--live", action="store_true")
    pages = sub.add_parser("pages").add_subparsers(dest="action", required=True)
    pages.add_parser("size")
    demo = sub.add_parser("demo").add_subparsers(dest="action", required=True)
    check = demo.add_parser("check")
    check.add_argument("slug")
    check.add_argument("--base")
    args = parser.parse_args(argv)

    if args.area == "api":
        return run("tools/build_library_api.py", *(["--check"] if args.action == "check" else []))
    if args.area == "media":
        return media_verify(args.live)
    if args.area == "pages":
        return pages_size()
    return demo_check(args.slug, args.base)


if __name__ == "__main__":
    sys.exit(main())
