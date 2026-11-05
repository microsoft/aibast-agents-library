#!/usr/bin/env python3
"""Stamp the Microsoft Clarity tracking tag into every public site page.

The Clarity project ID lives in one place, ``clarity.json`` at the repository
root. This script renders the tag from that file and inserts it (or replaces the
existing copy) right before ``</head>`` on every published HTML page, so the
whole site is updated with one command:

    python scripts/apply_clarity_tag.py           # rewrite pages
    python scripts/apply_clarity_tag.py --check   # exit 1 if any page is stale

The rendering itself lives in ``tools/clarity_tag.py`` so the solution scaffold
emits the identical block; see docs/CLARITY.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.clarity_tag import (  # noqa: E402
    END_MARK,
    PROJECT_ID_RE,
    START_MARK,
    load_config,
    public_pages,
    render_tag,
    stamp,
)

__all__ = [
    "END_MARK",
    "PROJECT_ID_RE",
    "START_MARK",
    "load_config",
    "main",
    "public_pages",
    "render_tag",
    "stamp",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report stale pages, change nothing")
    parser.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    try:
        config = load_config(root / "clarity.json")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    tag = render_tag(config["project_id"])

    stale: list[str] = []
    for page in public_pages(root):
        html = page.read_text(encoding="utf-8")
        try:
            updated = stamp(html, tag)
        except ValueError as exc:
            print(f"error: {page.relative_to(root)}: {exc}", file=sys.stderr)
            return 1
        if updated == html:
            continue
        stale.append(page.relative_to(root).as_posix())
        if not args.check:
            page.write_text(updated, encoding="utf-8")

    label = config["project_id"] or "(no project ID yet; loader stays inert)"
    if args.check:
        if stale:
            print(f"error: {len(stale)} page(s) missing the current Clarity tag:", file=sys.stderr)
            for relative in stale:
                print(f"  {relative}", file=sys.stderr)
            print("run: python scripts/apply_clarity_tag.py", file=sys.stderr)
            return 1
        print(f"Clarity tag current on {len(public_pages(root))} pages; project {label}")
        return 0
    print(f"Stamped Clarity tag on {len(stale)} page(s); project {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
