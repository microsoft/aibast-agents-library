from pathlib import Path

import pytest

from tools.promote_solution_draft import render_skill


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


def test_prior_manual_and_native_skill_sources_match():
    skills = sorted((PACKAGE / "manual/skills").glob("*/SKILL.md"))
    assert len(skills) == 4
    for path in skills:
        content, fields = render_skill(path)
        mirror = PACKAGE / "copilot-studio/behaviors" / f"aibast_{fields['name']}.mcs.yml"
        expected = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
        assert mirror.read_text(encoding="utf-8") == expected
