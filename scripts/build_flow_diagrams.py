#!/usr/bin/env python3
"""
Flow Diagram Builder — Renders a Mermaid process-flow diagram per solution.

Reads the canonical, universally-present case contract at
tests/demo_cases/<slug>.json (every solution package has one — see
solutions/<slug>/README.md "Canonical capture contract" row) and renders
its ordered `cases` list as a Mermaid flowchart: one node per case, in file
order, labeled with the operation and persona.

This is purely additive: it only writes a new file,
solutions/<slug>/FLOW.md, per solution. It never modifies any existing
solution file (README.md, FIELD-GUIDE.md, quest.html, deployment.json,
evals/*, etc.).

Run manually:   python scripts/build_flow_diagrams.py
Run for one:    python scripts/build_flow_diagrams.py account-intelligence
"""

import json
import re
import sys
from pathlib import Path

DEMO_CASES_DIR = Path("tests/demo_cases")
SOLUTIONS_DIR = Path("solutions")
SKIP_SLUGS = {"_shared"}


def slugs() -> list:
    if not SOLUTIONS_DIR.is_dir():
        return []
    return sorted(
        p.name for p in SOLUTIONS_DIR.iterdir()
        if p.is_dir() and p.name not in SKIP_SLUGS
    )


def mermaid_id(raw: str) -> str:
    """Sanitize a case id into a safe Mermaid node identifier."""
    return "n_" + re.sub(r"[^A-Za-z0-9_]", "_", raw)


def escape_label(text: str) -> str:
    """Mermaid node labels use quotes; escape embedded quotes."""
    return text.replace('"', "&quot;")


def build_diagram(slug: str) -> str:
    """Return rendered Markdown (with an embedded Mermaid flowchart) for one solution, or None if no case contract exists."""
    case_file = DEMO_CASES_DIR / f"{slug}.json"
    if not case_file.is_file():
        return None

    doc = json.loads(case_file.read_text(encoding="utf-8"))
    cases = doc.get("cases") or []
    if not cases:
        return None

    solution_name = doc.get("solution", slug)
    lines = [
        f"# {solution_name} — flow diagram",
        "",
        "Auto-generated from the ordered case contract at "
        f"`tests/demo_cases/{slug}.json`. Each node is one locked case, in "
        "file order, labeled with its persona and operation. This is a "
        "process-flow view of the scenario, not an implementation "
        "architecture diagram (see `README.md` for architecture).",
        "",
        "```mermaid",
        "flowchart TD",
    ]

    node_ids = []
    for case in cases:
        case_id = str(case.get("id", "case"))
        node_id = mermaid_id(case_id)
        node_ids.append(node_id)
        operation = case.get("operation", "")
        persona = case.get("persona", "")
        bullet = case.get("onepager_bullet") or case.get("prompt", "")
        # Keep node labels short; the persona/operation identify the step,
        # the bullet gives the value/why in one clipped line.
        clipped = (bullet[:70] + "…") if len(bullet) > 70 else bullet
        label_top = f"{case_id}: {operation}" if operation else case_id
        label = f"{label_top}<br/><small>{persona}</small>" if persona else label_top
        if clipped:
            label = f"{label}<br/><small>{clipped}</small>"
        lines.append(f'    {node_id}["{escape_label(label)}"]')

    for a, b in zip(node_ids, node_ids[1:]):
        lines.append(f"    {a} --> {b}")

    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main():
    only = sys.argv[1:] or None
    targets = only if only else slugs()

    written, skipped = [], []
    for slug in targets:
        content = build_diagram(slug)
        if content is None:
            skipped.append(slug)
            continue
        out_path = SOLUTIONS_DIR / slug / "FLOW.md"
        out_path.write_text(content, encoding="utf-8")
        written.append(str(out_path))

    print(f"Wrote {len(written)} flow diagram(s):")
    for path in written:
        print(f"  {path}")
    if skipped:
        print(f"Skipped {len(skipped)} (no case contract found): {', '.join(skipped)}")


if __name__ == "__main__":
    main()
