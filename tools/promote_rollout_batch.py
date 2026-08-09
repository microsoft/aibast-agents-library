#!/usr/bin/env python3
"""Sequentially initialize and push missing Copilot Studio Draft projects."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from promote_solution_draft import ROOT, display_name, parse_yaml_scalar, promote


PRESERVED_EVIDENCE_SLUGS = {
    "building-permit-processing",
    "product-line-optimization",
    "fs-regulatory-compliance",
    "inventory-rebalancing",
    "maintenance-scheduling",
}


def candidates(registry, refresh_existing=False):
    rows = []
    for agent in registry["agents"]:
        solution = agent.get("_solution")
        if not (solution and solution.get("has_onepager")):
            continue
        slug = (agent.get("_demo") or {}).get("slug") or agent["name"].split("/")[-1]
        if refresh_existing and slug in PRESERVED_EVIDENCE_SLUGS:
            continue
        package = ROOT / "solutions" / slug
        if not (package / "manual" / "GLOBAL-INSTRUCTIONS.md").exists():
            continue
        if not refresh_existing and (
            package / "copilot-studio" / "settings.mcs.yml"
        ).exists():
            continue
        rows.append((solution.get("slot") or 999, slug))
    return [slug for _, slug in sorted(rows)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--publisher-prefix", default="aibast")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--refresh-existing", action="store_true")
    parser.add_argument("--rename-existing", action="store_true")
    parser.add_argument("--results", type=Path)
    args = parser.parse_args()

    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
    results = []
    failures = []
    for slug in candidates(registry, args.refresh_existing):
        recipe = json.loads(
            (ROOT / "solutions" / slug / "deployment.json").read_text(
                encoding="utf-8"
            )
        )
        project_root = args.project_root.expanduser().resolve()
        source_settings = ROOT / "solutions" / slug / "copilot-studio" / "settings.mcs.yml"
        current_name = None
        if source_settings.exists():
            current_name = parse_yaml_scalar(
                source_settings.read_text(encoding="utf-8"),
                "displayName",
            )
        current_project = project_root / current_name if current_name else None
        project = (
            current_project
            if current_project and current_project.exists()
            else project_root / display_name(recipe)
        )
        try:
            result = promote(
                slug,
                project,
                args.environment,
                args.publisher_prefix,
                True,
                update_existing=args.refresh_existing and project.exists(),
                rename_existing=args.rename_existing and project.exists(),
            )
            results.append(result)
            print(f"[OK] {slug}: {result['push_output']}")
        except Exception as error:
            failures.append({"slug": slug, "error": str(error)})
            print(f"[FAIL] {slug}: {error}")
            if not args.continue_on_error:
                raise

    artifact = {"promoted": results, "failures": failures}
    if args.results:
        args.results.parent.mkdir(parents=True, exist_ok=True)
        args.results.write_text(
            json.dumps(artifact, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(artifact, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
