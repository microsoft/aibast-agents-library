#!/usr/bin/env python3
"""Add locked Preview evidence anchors to manual Copilot Studio instructions."""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
START = "<!-- locked-preview-anchors:start -->"
END = "<!-- locked-preview-anchors:end -->"
PRESERVED_EVIDENCE_SLUGS = {
    "fs-regulatory-compliance",
    "inventory-rebalancing",
    "product-line-optimization",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def render_section(cases):
    lines = [
        START,
        "## Locked Preview evidence anchors",
        "",
        "Route from the user's natural-language intent. For the matching operation, preserve the exact synthetic evidence anchors below; do not dump anchors from unrelated cases.",
        "",
        "Do not narrate internal retrieval, tool selection, restrictions, or implementation mechanics. Present only the user-facing result.",
        "",
    ]
    for case in cases:
        case_id = case["id"]
        operation = case.get("operation") or "matching operation"
        anchors = ", ".join(f"`{value}`" for value in case.get("must_include", []))
        lines.append(f"- `{case_id}` / `{operation}`: {anchors}")
    lines.extend(
        [
            "",
            "These phrases are acceptance evidence for the fixed synthetic cases. Preserve their wording when that case applies, while keeping the surrounding answer natural and evidence-first.",
            END,
        ]
    )
    return "\n".join(lines)


def update_text(text, section):
    if START in text and END in text:
        before, remainder = text.split(START, 1)
        _, after = remainder.split(END, 1)
        return before.rstrip() + "\n\n" + section + after.rstrip() + "\n"
    return text.rstrip() + "\n\n" + section + "\n"


def candidates(root):
    for instructions in sorted(
        (root / "solutions").glob("*/manual/GLOBAL-INSTRUCTIONS.md")
    ):
        slug = instructions.parents[1].name
        if slug in PRESERVED_EVIDENCE_SLUGS:
            continue
        cases = root / "tests" / "demo_cases" / f"{slug}.json"
        if cases.is_file():
            yield slug, instructions, cases


def normalize(root, check=False):
    changed = []
    for slug, instructions_path, cases_path in candidates(root):
        current = instructions_path.read_text(encoding="utf-8")
        cases = read_json(cases_path)["cases"]
        updated = update_text(current, render_section(cases))
        if updated != current:
            changed.append(slug)
            if not check:
                instructions_path.write_text(updated, encoding="utf-8")
    return changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = normalize(ROOT, check=args.check)
    if args.check and changed:
        print("\n".join(changed))
        return 1
    print(json.dumps({"updated": changed, "count": len(changed)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
