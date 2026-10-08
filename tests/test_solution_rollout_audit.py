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
    assert len(rows) == 66


def test_completed_journeys_pass_every_rollout_gate():
    module = load_module()
    rows = {row["name"]: row for row in module.collect()}
    completed = {
        "@aibast-agents-library/building-permit-processing",
        "@aibast-agents-library/production-line-optimization",
        "@aibast-agents-library/inventory-rebalancing",
    }
    for name in completed:
        assert rows[name]["complete"] is True


def test_recaptured_manual_repairs_pass_the_rollout_completion_gate_on_current_evidence():
    # These two packages were once preserved repairs that stayed below the
    # completion gate. They were re-shot in the real Copilot Studio UI, so the
    # gate may pass only because the CURRENT manual evidence passes every
    # locked case, never because of the historical capture.
    module = load_module()
    rows = {row["slug"]: row for row in module.collect()}
    for slug in ("fs-customer-onboarding", "fs-regulatory-compliance"):
        assert rows[slug]["manual_evidence"] == "passed"
        assert rows[slug]["complete"] is True
        evidence = module.read_json(
            ROOT / "solutions" / slug / "evals/manual-build-evidence.json"
        )
        assert evidence["status"] == "passed"
        cases = module.read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")["cases"]
        preview = {case["case_id"]: case for case in evidence["canonical_preview"]}
        assert set(preview) == {case["id"] for case in cases}
        assert all(case["passed"] is True for case in preview.values())


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
