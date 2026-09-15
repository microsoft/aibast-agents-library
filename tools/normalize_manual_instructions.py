#!/usr/bin/env python3
"""Normalize real-skill routing without copying evaluation answers into policy."""

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.audit_academy import parse_front_matter


START = "<!-- locked-preview-anchors:start -->"
END = "<!-- locked-preview-anchors:end -->"
PRESERVED_EVIDENCE_SLUGS = {
    # Hand-authored and hash-pinned policies need an explicit reviewed revision.
    "building-permit-processing",
    "fs-customer-onboarding",
    "fs-regulatory-compliance",
    "inventory-rebalancing",
    "portfolio-rebalancing",
    "prior-authorization",
    "procurement-agent",
    "product-line-optimization",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def skill_routes(cases, skills_directory, current=""):
    names = set()
    by_operation = {}
    for path in sorted(skills_directory.glob("*/SKILL.md")):
        name = parse_front_matter(path.read_text(encoding="utf-8")).get("name")
        if not name or any(character in name for character in "`\r\n"):
            raise ValueError(f"{path}: missing or invalid skill name")
        if name in names:
            raise ValueError(f"{path}: duplicate skill name {name!r}")
        names.add(name)
        operation = path.parent.name.replace("-", "_")
        if operation in by_operation:
            raise ValueError(f"{path}: ambiguous operation directory {operation!r}")
        by_operation[operation] = name

    existing = {}
    for case_id, name in re.findall(
        r"^- `([^`\n]+)` uses skill `([^`\n]+)`\.$", current, re.MULTILINE
    ):
        if case_id in existing:
            raise ValueError(f"Duplicate skill route for {case_id}")
        existing[case_id] = name

    routes = {}
    for case in cases:
        case_id = case["id"]
        if case_id in routes:
            raise ValueError(f"Duplicate case ID {case_id}")
        declared = existing.get(case_id)
        if declared in names:
            routes[case_id] = declared
        else:
            operation = str(case.get("operation") or "").replace("-", "_")
            if operation not in by_operation:
                raise ValueError(
                    f"{case_id}: no verified skill route for operation {operation!r}"
                )
            routes[case_id] = by_operation[operation]
    return routes


def render_section(cases, routes):
    lines = [
        START,
        "## Skill routing map",
        "",
        "Route from the user's natural-language intent to the correct skill below. Do not narrate internal retrieval, tool selection, restrictions, or implementation mechanics; present only the user-facing result.",
        "",
    ]
    for case in cases:
        case_id = case["id"]
        name = routes.get(case_id)
        if not name:
            raise ValueError(f"{case_id}: a verified skill name is required")
        lines.append(f"- `{case_id}` uses skill `{name}`.")
    lines.extend(
        [
            "",
            "These skill names above are the ONLY valid skill identifiers. Never invent, guess, or reference any other skill name. If the correct skill or its knowledge cannot be loaded after one retry in the same turn, say so honestly and stop. Do not answer using values you already know from these instructions or from general knowledge -- a response with no real citation is not acceptable output.",
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
        routes = skill_routes(cases, instructions_path.parent / "skills", current)
        updated = update_text(current, render_section(cases, routes))
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
