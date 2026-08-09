#!/usr/bin/env python3
"""Report end-to-end evidence coverage for every advertised solution."""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def package_slug(agent):
    demo = agent.get("_demo") or {}
    return demo.get("slug") or agent["name"].split("/")[-1]


def stage(path):
    return path.exists()


def manual_status(package):
    path = package / "evals" / "manual-build-evidence.json"
    if not path.exists():
        return None
    evidence = read_json(path)
    if evidence.get("status") == "passed":
        return "passed"
    preview = evidence.get("canonical_preview")
    preview_passed = (
        preview.get("passed") is True
        if isinstance(preview, dict)
        else bool(preview) and all(case.get("passed") is True for case in preview)
    )
    publication = evidence.get("publication") or evidence.get("publication_gate") or {}
    if preview_passed and publication.get("published") is False:
        return "passed"
    return evidence.get("status")


def solution_row(agent):
    slug = package_slug(agent)
    package = ROOT / "solutions" / slug
    manual = package / "screenshots" / "manual"
    assisted = package / "screenshots" / "assisted"
    cases = ROOT / "tests" / "demo_cases" / f"{slug}.json"
    return {
        "name": agent["name"],
        "display_name": agent["_solution"]["advertised_name"],
        "slot": agent["_solution"].get("slot"),
        "slug": slug,
        "curated_copy": bool(agent["_solution"].get("curated_copy")),
        "demo_cases": stage(cases),
        "source_transcripts": stage(package / "evals" / "transcripts.json"),
        "deployment_recipe": stage(package / "deployment.json"),
        "onepager_map": stage(package / "evals" / "onepager-map.json"),
        "copilot_studio_source": stage(package / "copilot-studio" / "settings.mcs.yml"),
        "easy_evidence": stage(
            package / "evals" / "copilot-studio-preview-evidence.json"
        ) or stage(package / "evals" / "copilot-studio-transcripts.json"),
        "assisted_browserfilm": stage(assisted / "copilot-assisted-walkthrough.gif")
        or stage(package / "screenshots" / "copilot-assisted-walkthrough.gif"),
        "manual_tutorial": stage(package / "manual-tutorial.html"),
        "manual_evidence": manual_status(package),
        "manual_browserfilm": stage(manual / "manual-build-walkthrough.gif"),
        "export_manifest": stage(package / "export-manifest.json"),
        "source_bundle": any((package / "exports").glob("*.zip"))
        if (package / "exports").is_dir()
        else False,
    }


def is_complete(row):
    required = (
        "curated_copy",
        "demo_cases",
        "source_transcripts",
        "deployment_recipe",
        "onepager_map",
        "copilot_studio_source",
        "easy_evidence",
        "assisted_browserfilm",
        "manual_tutorial",
        "manual_browserfilm",
        "export_manifest",
        "source_bundle",
    )
    return all(row[key] for key in required) and row["manual_evidence"] == "passed"


def collect():
    registry = read_json(ROOT / "registry.json")
    rows = [
        solution_row(agent)
        for agent in registry["agents"]
        if agent.get("_solution") and agent["_solution"].get("has_onepager")
    ]
    rows.sort(key=lambda item: (item["slot"] is None, item["slot"] or 999, item["name"]))
    for row in rows:
        row["complete"] = is_complete(row)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rows = collect()
    if args.json:
        stages = stage_totals(rows)
        print(json.dumps({"stages": stages, "solutions": rows}, indent=2))
        return 0

    complete = sum(row["complete"] for row in rows)
    print(f"Advertised solution journeys: {complete}/{len(rows)} complete")
    for name, count in stage_totals(rows).items():
        print(f"  {name}: {count}/{len(rows)}")
    for row in rows:
        state = "COMPLETE" if row["complete"] else "PENDING"
        print(f"{state:8} {row['name']}")
    return 0


def stage_totals(rows):
    fields = (
        "curated_copy",
        "demo_cases",
        "source_transcripts",
        "deployment_recipe",
        "onepager_map",
        "copilot_studio_source",
        "easy_evidence",
        "assisted_browserfilm",
        "manual_tutorial",
        "manual_browserfilm",
        "export_manifest",
        "source_bundle",
        "complete",
    )
    return {
        field: sum(bool(row[field]) for row in rows)
        for field in fields
    }


if __name__ == "__main__":
    raise SystemExit(main())
