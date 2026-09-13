from pathlib import Path

from tools.promote_solution_draft import (
    parse_yaml_scalar,
    render_settings,
    render_skill,
)


PACKAGE = Path(__file__).resolve().parents[1] / "solutions/portfolio-rebalancing"


def normalized(text):
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def test_portfolio_manual_and_native_source_contracts_match():
    manual = PACKAGE / "manual"
    native = PACKAGE / "copilot-studio"
    settings = (native / "settings.mcs.yml").read_text(encoding="utf-8")
    expected = render_settings(
        parse_yaml_scalar(settings, "displayName"),
        parse_yaml_scalar(settings, "schemaName"),
        (manual / "GLOBAL-INSTRUCTIONS.md").read_text(encoding="utf-8"),
    )
    assert settings == normalized(expected)

    skills = sorted((manual / "skills").glob("*/SKILL.md"))
    assert len(skills) == 6
    for path in skills:
        content, fields = render_skill(path)
        mirror = native / "behaviors" / f"aibast_{fields['name']}.mcs.yml"
        assert mirror.read_text(encoding="utf-8") == normalized(content)

    knowledge = sorted((manual / "knowledge").glob("*.md"))
    assert len(knowledge) == 2
    for path in knowledge:
        mirror = native / "capabilities/knowledge/files" / path.name
        assert mirror.read_bytes() == path.read_bytes()


def test_portfolio_repaired_skills_keep_the_explicit_review_contracts():
    skills = PACKAGE / "manual/skills"
    tax = (skills / "aibast_tax-impact_03/SKILL.md").read_text(encoding="utf-8")
    assert "Entire VTI position cost basis: $3,800,000." in tax
    assert "20.0% long-term capital gains + 3.8% NIIT = 23.8%" in tax
    assert "whole-position versus reduction scopes" in tax

    loss = (skills / "aibast_tax-loss-harvest_04/SKILL.md").read_text(encoding="utf-8")
    assert "Wash-sale exposure: a qualified tax professional must review it." in loss
    assert "Reproduce these source control sentences without elaboration" in loss

    execution = (skills / "aibast_execution-plan_06/SKILL.md").read_text(encoding="utf-8")
    assert "Confirm available cash and settlement timing in the approved trading system." in execution
    assert "reduction proceeds alone are not the source's funding condition" in execution
    assert "no post-trade tolerance is supplied" in execution
    assert "No order has been created, routed, or executed." in execution


def test_portfolio_tax_review_is_bounded_and_calculations_keep_exact_inputs():
    tax = (
        PACKAGE / "manual/skills/aibast_tax-impact_03/SKILL.md"
    ).read_text(encoding="utf-8")
    assert "Exact reduction fraction: $622,500 / $4,357,500 = 1/7." in tax
    assert "unrounded proportional gain in the tax calculation" in tax
    assert "required review block below, reproduced without elaboration" in tax
    review = tax.split("## Required review block\n", 1)[1].split(
        "\nDo not expand this block", 1
    )[0]
    assert "These are required human reviews, not completed approvals:" in review
    assert review.count("\n- ") == 4
    assert "- Tax lots and holding periods: a qualified tax professional must validate them." in review
    assert "- Account type and rate applicability, including NIIT: a qualified tax professional must validate them." in review
    assert "- Client suitability: a licensed financial advisor must review it." in review
    assert "- Actual eligibility and tax outcomes remain unknown." in review
    assert "Do not expand this block into account-category examples" in tax
