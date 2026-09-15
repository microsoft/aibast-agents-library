#!/usr/bin/env python3
"""Stamp the AIBAST design tokens into every published site page.

One source of truth, ``tools/design_tokens.py``, rendered into every page the
same way the Clarity tag is:

    python scripts/apply_design_tokens.py           # rewrite pages
    python scripts/apply_design_tokens.py --check   # exit 1 if any page is stale

The block lands before each page's own ``<style>``, so it sets the floor and
never overrides what a page already styles. See tools/design_tokens.py for why
a shared stylesheet cannot be used here.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.clarity_tag import public_pages  # noqa: E402
from tools.design_tokens import (  # noqa: E402
    END_MARK,
    START_MARK,
    render_tokens,
    stamp,
)

__all__ = [
    "END_MARK",
    "START_MARK",
    "main",
    "public_pages",
    "render_tokens",
    "stamp",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report stale pages, change nothing")
    parser.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    block = render_tokens()
    stale: list[str] = []
    pages = list(public_pages(root))
    for page in pages:
        html = page.read_text(encoding="utf-8")
        try:
            updated = stamp(html, block)
        except ValueError as exc:
            print(f"error: {page.relative_to(root)}: {exc}", file=sys.stderr)
            return 1
        if updated == html:
            continue
        stale.append(page.relative_to(root).as_posix())
        if not args.check:
            page.write_text(updated, encoding="utf-8")

    if args.check:
        if stale:
            print(
                f"error: {len(stale)} page(s) missing the current design tokens:",
                file=sys.stderr,
            )
            for name in stale[:20]:
                print(f"  {name}", file=sys.stderr)
            if len(stale) > 20:
                print(f"  ... and {len(stale) - 20} more", file=sys.stderr)
            print("run: python scripts/apply_design_tokens.py", file=sys.stderr)
            return 1
        print(f"Design tokens current on {len(pages)} pages")
        return 0

    if stale:
        print(f"Stamped design tokens on {len(stale)} page(s); {len(pages)} pages total")
    else:
        print(f"Design tokens already current on {len(pages)} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
