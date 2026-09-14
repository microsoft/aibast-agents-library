import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "normalize_manual_instructions.py"


def load_module():
    spec = importlib.util.spec_from_file_location("normalize_manual_instructions", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_render_section_routes_to_real_skills_without_leaking_answers():
    module = load_module()
    section = module.render_section(
        [
            {
                "id": "EX-01",
                "operation": "evidence_review",
                "must_include": ["Record A", "Evidence boundary"],
            }
        ],
        {"EX-01": "example-evidence-review"},
    )
    assert "`EX-01` uses skill `example-evidence-review`" in section
    assert "Record A" not in section
    assert "Evidence boundary" not in section
    assert "Do not narrate internal retrieval" in section
    assert "a response with no real citation is not acceptable" in section


def test_normalize_is_idempotent(tmp_path):
    module = load_module()
    instructions = (
        tmp_path
        / "solutions"
        / "example"
        / "manual"
        / "GLOBAL-INSTRUCTIONS.md"
    )
    instructions.parent.mkdir(parents=True)
    instructions.write_text("# Role\n\nSynthetic only.\n", encoding="utf-8")
    skill = instructions.parent / "skills/review/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: example-review\ndescription: Review source evidence.\n---\n",
        encoding="utf-8",
    )
    cases = tmp_path / "tests" / "demo_cases" / "example.json"
    cases.parent.mkdir(parents=True)
    cases.write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "id": "EX-01",
                        "operation": "review",
                        "must_include": ["Record A"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    catalog = tmp_path / "solutions" / "catalog.json"
    catalog.write_text(
        json.dumps({"solutions": {"@aibast-agents-library/example": {}}}),
        encoding="utf-8",
    )

    assert module.normalize(tmp_path) == ["example"]
    first = instructions.read_text(encoding="utf-8")
    assert module.normalize(tmp_path) == []
    assert instructions.read_text(encoding="utf-8") == first


@pytest.mark.parametrize(
    "slug",
    [
        "building-permit-processing",
        "fs-customer-onboarding",
        "portfolio-rebalancing",
        "prior-authorization",
        "procurement-agent",
    ],
)
def test_normalization_preserves_hand_authored_and_frozen_policies(tmp_path, slug):
    module = load_module()
    relative = Path("solutions") / slug / "manual/GLOBAL-INSTRUCTIONS.md"
    original = (ROOT / relative).read_bytes()
    instructions = tmp_path / relative
    instructions.parent.mkdir(parents=True)
    instructions.write_bytes(original)
    cases = tmp_path / "tests/demo_cases" / f"{slug}.json"
    cases.parent.mkdir(parents=True)
    cases.write_bytes((ROOT / "tests/demo_cases" / f"{slug}.json").read_bytes())

    assert module.normalize(tmp_path, check=True) == []
    assert module.normalize(tmp_path) == []
    assert instructions.read_bytes() == original


def test_skill_route_uses_metadata_not_an_invented_identifier(tmp_path):
    module = load_module()
    skill = tmp_path / "skills/evidence-review/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: actual-evidence-review\ndescription: Review evidence.\n---\n",
        encoding="utf-8",
    )
    cases = [{"id": "EX-01", "operation": "evidence_review"}]
    assert module.skill_routes(
        cases, tmp_path / "skills",
        "- `EX-01` uses skill `invented-evidence-review`.",
    ) == {"EX-01": "actual-evidence-review"}


def test_unknown_operation_and_missing_routes_fail_explicitly(tmp_path):
    module = load_module()
    cases = [{"id": "EX-01", "operation": "unknown"}]
    with pytest.raises(ValueError, match="no verified skill route"):
        module.skill_routes(cases, tmp_path)
    with pytest.raises(ValueError, match="a verified skill name is required"):
        module.render_section(cases, {})
