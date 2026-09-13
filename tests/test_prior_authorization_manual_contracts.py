from pathlib import Path

import pytest

from tools.promote_solution_draft import parse_yaml_scalar, render_settings, render_skill


PACKAGE = Path(__file__).resolve().parents[1] / "solutions/prior-authorization"


@pytest.mark.parametrize(
    ("skill", "required_lines"),
    [
        (
            "request-evidence",
            [
                "# Prior-Authorization Evidence Inventory",
                "## {request_id}: {service}",
                "Payer: {payer}",
                "Source-recorded workflow state: {source_status} ({source_date})",
                "Referenced policy: {policy_reference}",
                "{evidence_item}: {source_value}",
            ],
        ),
        (
            "criteria-evidence",
            [
                "# Criteria-to-Evidence Crosswalk",
                "## {request_id}: {policy_title}",
                "Synthetic effective date: {effective_date}",
                "Checklist only; presence does not establish medical necessity or authorization.",
                "Reviewer check: {requirement}",
            ],
        ),
        (
            "appeal-evidence-packet",
            [
                "# Reconsideration Evidence Draft",
                "## {request_id}: {service}",
                "A reviewer must confirm that reconsideration or appeal is appropriate and permitted.",
                "Source-recorded workflow state: {source_status} ({source_date})",
                "Referenced policy to verify: {policy_reference}",
                "Include only authorized, minimum-necessary evidence.",
                "{evidence_item}: {source_value}",
                "Human utilization reviewer owns rationale, completeness, and submission.",
            ],
        ),
    ],
)
def test_prior_manual_preserves_complete_output_line_templates(skill, required_lines):
    text = (PACKAGE / "manual/skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    assert "Render these as complete text lines; do not split them across table cells." in text
    template = text.split("```text\n", 1)[1].split("\n```", 1)[0].splitlines()
    assert all(line in template for line in required_lines)
    assert "source order" in text
    assert "Retain the global policy's exact terminal safety footer." in text


def test_prior_request_does_not_infer_workflow_state_rationale():
    text = (PACKAGE / "manual/skills/request-evidence/SKILL.md").read_text(encoding="utf-8")
    for clause in (
        "Treat workflow state and evidence presence as independent recorded facts.",
        "Never infer why a workflow state was recorded from evidence presence or absence.",
        "For a matched record, quote a workflow-state reason only when that record explicitly provides it.",
        "Otherwise include this source-limit line exactly once:",
        "The synthetic source does not state why this workflow state was recorded.",
        'Do not add a "Summary for Reviewer" or supply reviewer rationale.',
        "do not turn an evidence gap into a causal explanation, outcome, or recommendation.",
    ):
        assert clause in text


@pytest.mark.parametrize(
    "relative_path",
    [
        "GLOBAL-INSTRUCTIONS.md",
        "knowledge/aibast_prior-authorization-review-rules.md",
        "skills/request-evidence/SKILL.md",
        "skills/appeal-evidence-packet/SKILL.md",
    ],
)
def test_prior_rationale_and_evidence_boundaries_cover_every_state_response(relative_path):
    text = (PACKAGE / "manual" / relative_path).read_text(encoding="utf-8")
    assert "Treat workflow state and evidence presence as independent recorded facts." in text
    assert "Never infer why a workflow state was recorded from evidence presence or absence." in text
    assert "The synthetic source does not state why this workflow state was recorded." in text
    assert "Do not append advice, action requirements, or judgments to source-reported evidence values." in text


def test_prior_inventory_scope_does_not_follow_historical_capture_behavior():
    request = (PACKAGE / "manual/skills/request-evidence/SKILL.md").read_text(encoding="utf-8")
    rules = (PACKAGE / "manual/knowledge/aibast_prior-authorization-review-rules.md").read_text(encoding="utf-8")
    records = (PACKAGE / "manual/knowledge/aibast_prior-authorization-synthetic-records.md").read_text(encoding="utf-8")
    for text in (request, rules):
        assert "Only include criteria when the user explicitly requests it." in text
    assert "For inventory-only requests, stop after the inventory, source-limit line, citations, and terminal footer." in request
    assert "if criteria context is needed" not in request
    assert "strict PA-01 capture" not in rules
    assert "captured agentic loop also followed" not in records


@pytest.mark.parametrize("request_id", ["SYN-AUTH-001", "SYN-AUTH-002"])
def test_prior_source_records_explicitly_preserve_unknown_workflow_reasons(request_id):
    records = (PACKAGE / "manual/knowledge/aibast_prior-authorization-synthetic-records.md").read_text(encoding="utf-8")
    section = records.split(f"## Synthetic request: {request_id}\n", 1)[1].split("\n## ", 1)[0]
    assert "**Workflow-state rationale:** not stated in synthetic source" in section


def test_prior_manual_and_native_shared_sources_match():
    settings = (PACKAGE / "copilot-studio/settings.mcs.yml").read_text(encoding="utf-8")
    policy = (PACKAGE / "manual/GLOBAL-INSTRUCTIONS.md").read_text(encoding="utf-8")
    name = parse_yaml_scalar(settings, "displayName")
    schema = parse_yaml_scalar(settings, "schemaName")
    assert name and schema
    rendered = render_settings(name, schema, policy)
    assert settings == "\n".join(line.rstrip() for line in rendered.splitlines()) + "\n"
    for path in (PACKAGE / "manual/knowledge").glob("*.md"):
        mirror = PACKAGE / "copilot-studio/capabilities/knowledge/files" / path.name
        assert mirror.read_bytes() == path.read_bytes()


def test_prior_manual_and_native_skill_sources_match():
    skills = sorted((PACKAGE / "manual/skills").glob("*/SKILL.md"))
    assert len(skills) == 4
    for path in skills:
        content, fields = render_skill(path)
        mirror = PACKAGE / "copilot-studio/behaviors" / f"aibast_{fields['name']}.mcs.yml"
        expected = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
        assert mirror.read_text(encoding="utf-8") == expected
