import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "audit_solution_rollout.py"


def load_module():
    spec = importlib.util.spec_from_file_location("solution_rollout", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rollout_audit_tracks_every_advertised_onepager_solution():
    module = load_module()
    rows = module.collect()
    registry = module.read_json(ROOT / "registry.json")
    expected = {
        agent["name"]
        for agent in registry["agents"]
        if agent.get("_solution") and agent["_solution"].get("has_onepager")
    }
    assert {row["name"] for row in rows} == expected
    assert len(rows) == 51


def test_completed_journeys_pass_every_rollout_gate():
    module = load_module()
    rows = {row["name"]: row for row in module.collect()}
    completed = {
        "@aibast-agents-library/building-permit-processing",
        "@aibast-agents-library/production-line-optimization",
        "@aibast-agents-library/fs-regulatory-compliance",
        "@aibast-agents-library/inventory-rebalancing",
    }
    for name in completed:
        assert rows[name]["complete"] is True


def test_standard_manual_packages_include_global_instructions():
    module = load_module()
    for row in module.collect():
        if row["slug"] == "building-permit-processing":
            continue
        instructions = (
            ROOT
            / "solutions"
            / row["slug"]
            / "manual"
            / "GLOBAL-INSTRUCTIONS.md"
        )
        assert instructions.is_file(), instructions


def test_incomplete_manual_packages_contain_substantive_knowledge():
    frozen = {
        "building-permit-processing",
        "product-line-optimization",
        "fs-regulatory-compliance",
        "inventory-rebalancing",
        "maintenance-scheduling",
    }
    module = load_module()
    for row in module.collect():
        if row["slug"] in frozen:
            continue
        knowledge = sorted(
            (ROOT / "solutions" / row["slug"] / "manual" / "knowledge").glob(
                "*.md"
            )
        )
        assert len(knowledge) == 2, row["slug"]
        for path in knowledge:
            assert path.stat().st_size >= 2_000, path


def test_stage_totals_count_boolean_evidence():
    module = load_module()
    rows = module.collect()
    totals = module.stage_totals(rows)
    assert totals["curated_copy"] == len(rows)
    assert totals["complete"] == sum(row["complete"] for row in rows)
