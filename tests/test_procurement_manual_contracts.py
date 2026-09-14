"""Source-only contracts; these checks do not establish native Preview acceptance."""

import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pytest

from tools.promote_solution_draft import (
    parse_frontmatter,
    parse_yaml_scalar,
    render_settings,
    render_skill,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "solutions/procurement-agent"
MANUAL = PACKAGE / "manual"
POLICY = "GLOBAL-INSTRUCTIONS.md"
RECORDS = "aibast_procurement-agent-synthetic-records.md"
RULES = "knowledge/aibast_procurement-agent-rules-and-guardrails.md"
PURCHASE = "skills/aibast_purchase-request_01/SKILL.md"
VENDOR = "skills/aibast_vendor-comparison_02/SKILL.md"
APPROVAL = "skills/aibast_approval-routing_03/SKILL.md"
SPEND = "skills/aibast_spend-analysis_04/SKILL.md"
FOOTER = (
    "Synthetic procurement evidence; decision support only. No approval, supplier "
    "action, purchase order, or spend commitment occurred."
)
FOOTER_ORDER = (
    "Put case-specific boundaries and citations before this footer; append nothing after it."
)
REVIEW_PARAGRAPH = (
    "Required human reviews remain unresolved: Finance for budget validation and "
    "reconciliation; procurement for request and supplier review; legal, security, "
    "competition, supplier diversity, conflicts of interest, business-owner, "
    "delegated-authority and explicit publication review by the corresponding "
    "authorized owners."
)
REVIEW_ORDER = (
    "Copy this paragraph verbatim once in every final answer, after all case-specific "
    "content and citations, immediately before the final safety footer. "
    "Never shorten, split, paraphrase or duplicate it."
)
REVIEW_CONTEXT = (
    "These controls are unresolved in this review, not a serial chain or a denial "
    "of recorded historical statuses."
)
SLA_LABEL = (
    "The SLA is a source label, not evidence that a review clock or approval started."
)
SKILLS = {
    PURCHASE: (
        "purchase-request",
        "Use when a procurement manager asks for request context and the applicable approval level.",
    ),
    VENDOR: (
        "vendor-comparison",
        "Use when a category buyer wants a neutral view of synthetic vendor ratings, terms, and tiers.",
    ),
    APPROVAL: (
        "approval-routing",
        "Use when a department approver asks which authorization threshold applies to a request.",
    ),
    SPEND: (
        "spend-analysis",
        "Use when a finance director asks which synthetic category is over budget or approaching a limit.",
    ),
}


def read_manual(relative):
    return (MANUAL / relative).read_text(encoding="utf-8")


def prose(relative):
    return " ".join(read_manual(relative).split())


def read_contract(relative, mirror):
    if not mirror:
        return read_manual(relative)
    studio = PACKAGE / "copilot-studio"
    if relative == POLICY:
        path = studio / "settings.mcs.yml"
    elif relative == RULES:
        path = studio / "capabilities/knowledge/files" / Path(RULES).name
    else:
        path = studio / "behaviors" / f"aibast_{SKILLS[relative][0]}.mcs.yml"
    return path.read_text(encoding="utf-8")


def source_table(heading):
    section = read_manual(f"knowledge/{RECORDS}").split(f"## {heading}\n", 1)[1]
    section = section.split("\n## ", 1)[0]
    rows = [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in section.splitlines()
        if line.startswith("|")
    ]
    return [dict(zip(rows[0], row)) for row in rows[2:]]


def money(value):
    return Decimal(value.split()[0].replace("$", "").replace(",", ""))


@pytest.mark.parametrize(
    ("relative", "sha256"),
    [
        (
            "solutions/procurement-agent/manual/knowledge/"
            "aibast_procurement-agent-synthetic-records.md",
            "f3ff24b900de86dc98e4630787cbda7df459bd4d713e7353c7efb3a4c7baaffe",
        ),
        (
            "solutions/procurement-agent/manual/skills/aibast_approval-routing_03/SKILL.md",
            "362b7e5b09ffbbd717ad4a4ed334ad6b7456996be9c2660555a57d1e8d63eb47",
        ),
        (
            "tests/demo_cases/procurement-agent.json",
            "30c70a4e75fe85ba0cad7f716256693e1987f75459bdc99664488b518048928e",
        ),
    ],
)
def test_frozen_records_approval_skill_and_locked_cases_are_byte_preserved(relative, sha256):
    content = (ROOT / relative).read_bytes()
    if relative == f"solutions/procurement-agent/manual/{APPROVAL}":
        # The authorized r3 contract extends, rather than rewrites, the frozen r2 skill.
        content = content.split(b"\n## Required response contract\n", 1)[0]
    assert hashlib.sha256(content).hexdigest() == sha256


def test_manual_inventory_and_skill_identities_are_stable():
    inputs = {path.relative_to(MANUAL).as_posix() for path in MANUAL.rglob("*.md")}
    assert inputs == {POLICY, RULES, f"knowledge/{RECORDS}", *SKILLS}
    for relative, (name, description) in SKILLS.items():
        text, fields = parse_frontmatter(MANUAL / relative)
        assert fields == {"name": name, "description": description}
        assert text.startswith(
            f"---\nname: {name}\ndescription: {description}\n---\n<!-- bic:source=blank -->\n"
        )
        assert text.count("<!-- bic:source=blank -->") == 1


@pytest.mark.parametrize("relative", [POLICY, RULES])
def test_common_policy_requires_actual_skill_and_both_uploaded_sources(relative):
    text = prose(relative)
    assert "Before answering, load the matching uploaded skill" in text
    assert "Require real read-only knowledge retrieval from both files and cite both." in text
    assert RECORDS in text
    assert Path(RULES).name in text
    for name, _description in SKILLS.values():
        assert f"`{name}`" in text
    assert "Do not browse" in text


@pytest.mark.parametrize("relative", list(SKILLS))
def test_affected_skills_require_real_sources_not_preloaded_answers(relative):
    text = prose(relative)
    assert f"Use this uploaded `{SKILLS[relative][0]}` skill" in text
    assert RECORDS in text
    assert Path(RULES).name in text
    assert "Retrieve and cite both." in text
    assert "Retain the global policy's exact terminal safety footer verbatim." in text
    assert FOOTER_ORDER in text


def test_global_policy_is_compact_and_does_not_embed_source_tables_or_prompts():
    policy = read_manual(POLICY)
    assert len(policy) <= 6500
    assert not any(line.startswith("|") for line in policy.splitlines())
    for amount in ("$340,000", "$285,000", "$4,350,000", "$496,500", "$890,000"):
        assert amount not in policy
    cases = json.loads((ROOT / "tests/demo_cases/procurement-agent.json").read_text())
    for case in cases["cases"]:
        assert case["prompt"] not in policy
        for anchor in case["must_include"]:
            assert anchor in policy


@pytest.mark.parametrize("relative", [POLICY, RULES, *SKILLS])
def test_common_footer_is_identical_terminal_and_not_a_competing_notice(relative):
    text = read_manual(relative)
    assert text.rstrip().endswith(FOOTER)
    assert text.count(FOOTER) == 1
    assert "exact final standalone paragraph, once." in prose(relative)
    assert FOOTER_ORDER in prose(relative)
    assert "Analysis only. No purchase order is created" not in text


@pytest.mark.parametrize("relative", [POLICY, RULES, *SKILLS])
@pytest.mark.parametrize("mirror", [False, True], ids=["manual", "studio"])
def test_every_response_source_requires_complete_verbatim_human_review_paragraph(relative, mirror):
    text = read_contract(relative, mirror)
    normalized = " ".join(text.split())
    assert text.count(REVIEW_PARAGRAPH) == 1
    assert REVIEW_ORDER in normalized
    assert REVIEW_CONTEXT in normalized
    assert (
        text.index("## Mandatory human-review paragraph")
        < text.index(REVIEW_PARAGRAPH)
        < text.index("## Shared final footer")
        < text.index(FOOTER)
    )
    assert text.count(FOOTER) == 1
    assert FOOTER_ORDER in normalized
    assert "Do not invent an approver for unspecified spend." in normalized


@pytest.mark.parametrize("relative", [POLICY, RULES, PURCHASE, SPEND])
def test_request_inclusion_requires_reconciliation_without_projected_budget_effects(relative):
    text = prose(relative)
    for clause in (
        "The snapshot has no request-to-commitment mapping.",
        "Finance reconciliation must establish whether a request is already included in commitments.",
        "Do not infer inclusion from matching amounts or request status.",
        "Do not calculate hypothetical revised balances or utilization, or assert "
        "incremental budget effects without that mapping.",
        "Preserve existing budget exceptions",
    ):
        assert clause in text
    if relative != POLICY:
        assert "Technology is already `At Risk`" in text


@pytest.mark.parametrize("relative", [POLICY, RULES, PURCHASE, APPROVAL, SPEND])
def test_approval_rule_retains_inclusive_caps_and_does_not_invent_a_chain(relative):
    text = prose(relative)
    assert "Choose the first threshold whose inclusive upper bound covers the request amount." in text
    assert "Retain its cap and the `Unlimited` / `CEO + Board` tier." in text
    assert "Do not invent dollar-only lower bounds or serial approval chains." in text
    assert "$100,001" not in text


@pytest.mark.parametrize("relative", [POLICY, RULES, PURCHASE, APPROVAL, SPEND])
@pytest.mark.parametrize("mirror", [False, True], ids=["manual", "studio"])
def test_approval_sla_and_review_are_not_promised_outcomes(relative, mirror):
    text = " ".join(read_contract(relative, mirror).split())
    assert SLA_LABEL in text
    assert "It is not a promise of approval." in text
    assert "The selected approver must review and decide; do not promise approval." in text
    assert "Do not invent an approver for unspecified spend." in text


@pytest.mark.parametrize("relative", [POLICY, RULES, SPEND])
def test_portfolio_contract_nets_each_category_once_and_preserves_unknowns(relative):
    text = prose(relative)
    for clause in (
        "available = budget - spent YTD - committed",
        "Sum all category balances once, including negative values.",
        "Never subtract a category deficit again.",
        "Category balances are not freely transferable.",
        "Do not invent periods, causal mappings or executed/reversible statuses.",
    ):
        assert clause in text


@pytest.mark.parametrize("relative", [RULES, VENDOR])
def test_cloud_vendor_contract_preserves_scope_and_uninterpreted_source_labels(relative):
    text = prose(relative)
    for clause in (
        "For the cloud-vendor request, compare only the `Cloud Infrastructure` rows: `AWS` and `Azure`.",
        "Keep ratings, tiers, contract status and contact roles as exact source labels.",
        "The rating scale, methodology and statistical significance are not supplied.",
        "Do not claim normal variance or qualification outcomes.",
        "`Strategic` does not prove passed qualification or enterprise approval.",
        "Contact roles do not establish service focus or guarantees.",
        "Annual spend is not commitment volume.",
        "Do not pick a winner.",
    ):
        assert clause in text
    assert "neutral view of all six catalog vendors" not in text


@pytest.mark.parametrize("relative", [POLICY, RULES, VENDOR])
@pytest.mark.parametrize("mirror", [False, True], ids=["manual", "studio"])
def test_negative_evidence_distinguishes_missing_agreements_from_supplied_terms(relative, mirror):
    text = " ".join(read_contract(relative, mirror).split())
    for clause in (
        "Payment terms are supplied; do not describe all contract terms as absent.",
        "Full agreements, detailed service commitments and pricing schedules are not supplied.",
        "Distinguish those gaps from supplied payment terms, `Active` contract-status "
        "labels, tier labels and contact roles.",
    ):
        assert clause in text


def test_vendor_final_output_check_reconciles_missing_evidence_with_supplied_net_30():
    text = prose(VENDOR)
    assert "Before sending, check every missing-evidence claim against supplied fields." in text
    assert "`AWS` and `Azure` both have supplied `Net 30` payment terms." in text
    cloud_vendors = [
        row for row in source_table("Vendor catalog") if row["Category"] == "Cloud Infrastructure"
    ]
    assert [row["Vendor"] for row in cloud_vendors] == ["AWS", "Azure"]
    for row in cloud_vendors:
        assert row["Payment terms"] == "Net 30"
        assert row["Contract status"] == "Active"
        assert row["Tier"] == "Strategic"
        assert row["Contact role"]


@pytest.mark.parametrize(
    ("relative", "headings", "anchors"),
    [
        (
            PURCHASE,
            ["# Purchase Request Review: {request_id}", "## Justification", "## Approval gate"],
            ["Purchase Request Review: PR-5001", "PR-5001", "$125,000", "CFO"],
        ),
        (
            VENDOR,
            ["# Vendor Comparison", "## Vendor Tiers"],
            ["AWS", "Azure", "not a supplier award"],
        ),
        (
            APPROVAL,
            ["# Approval Routing: {request_id}", "## Approval Thresholds"],
            [
                "Approval Routing: PR-5001",
                "PR-5001",
                "CFO",
                "48 hours",
                "This recommendation does not record an approval.",
            ],
        ),
        (
            SPEND,
            ["# Spend Analysis", "## By Category", "## Alerts"],
            ["Software category over budget by $60,000", "No purchase order is created."],
        ),
    ],
)
def test_affected_skills_require_exact_heading_order_and_case_boundaries(relative, headings, anchors):
    text = read_manual(relative)
    template = text.split("```text\n", 1)[1].split("\n```", 1)[0]
    assert template.splitlines() == headings
    assert "Use these headings in order, with exact wording and capitalization." in text
    for anchor in anchors:
        assert anchor in text
    assert text.index(anchors[-1]) < text.index("Retain the global policy's exact terminal safety footer")


@pytest.mark.parametrize("mirror", [False, True], ids=["manual", "studio"])
def test_purchase_final_output_check_rejects_title_case_heading(mirror):
    text = " ".join(read_contract(PURCHASE, mirror).split())
    assert (
        "Before sending, check the literal heading is `Approval gate` (lowercase `g`), "
        "not `Approval Gate`. Do not title-case or rename it."
    ) in text


@pytest.mark.parametrize("relative", [POLICY, RULES, APPROVAL])
def test_common_policy_preserves_approval_response_without_changing_its_skill(relative):
    text = prose(relative)
    for clause in (
        "Approval Routing: PR-5001",
        "Approval Thresholds",
        "all five source threshold rows",
        "CFO",
        "48 hours",
        "does not record an approval",
    ):
        assert clause in text


def test_approval_skill_requires_complete_threshold_table_and_request_specific_review():
    text = prose(APPROVAL)
    for clause in (
        "all five source threshold rows in source order",
        "Amount up to and including",
        "Required approver",
        "Approval SLA",
        "Include the request amount, selected tier with its inclusive amount cap and SLA",
    ):
        assert clause in text
    thresholds = source_table("Approval thresholds")
    assert len(thresholds) == 5
    assert list(thresholds[0]) == [
        "Amount up to and including", "Required approver", "Approval SLA"
    ]
    for amount, approver, sla, cap in (
        ("5000", "Direct Manager", "4 hours", "$5,000"),
        ("25000", "Department Head", "8 hours", "$25,000"),
        ("100000", "VP Finance", "24 hours", "$100,000"),
        ("125000", "CFO", "48 hours", "$500,000"),
        ("500000", "CFO", "48 hours", "$500,000"),
        ("500000.01", "CEO + Board", "120 hours", "Unlimited"),
    ):
        selected = next(
            row for row in thresholds
            if row["Amount up to and including"] == "Unlimited"
            or Decimal(amount) <= money(row["Amount up to and including"])
        )
        assert selected == {
            "Amount up to and including": cap,
            "Required approver": approver,
            "Approval SLA": sla,
        }


def test_spend_contract_requires_complete_category_and_portfolio_tables():
    text = prose(SPEND)
    for clause in (
        "do not replace the tables with prose.",
        "portfolio totals table with Total budget, Spent YTD, Committed and Available",
        "all five source category rows in source order",
        "Technology, Software, Office Supplies, Professional Services and Travel.",
        "Category, Budget, Spent YTD, Committed, Available, Utilization, Status and Trend.",
    ):
        assert clause in text


def test_frozen_budget_rows_reconcile_without_double_netting():
    categories = source_table("Spend categories")
    assert len(categories) == 5
    for row in categories:
        used = money(row["Spent YTD"]) + money(row["Committed"])
        available = money(row["Budget"]) - used
        assert money(row["Available"]) == available
        utilization = used / money(row["Budget"]) * 100
        rounded = utilization.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        assert row["Utilization"] == f"{rounded}%"
        status = "Over Budget" if available < 0 else "At Risk" if utilization > 85 else "On Track"
        assert row["Status"] == status
    totals = {row["Metric"]: money(row["Exact value"]) for row in source_table("Portfolio totals")}
    for column, metric in (
        ("Budget", "Total budget"),
        ("Spent YTD", "Spent YTD"),
        ("Committed", "Committed"),
        ("Available", "Available"),
    ):
        assert sum(money(row[column]) for row in categories) == totals[metric]
    assert totals["Available"] == Decimal("496500")
    assert totals["Available"] == totals["Total budget"] - totals["Spent YTD"] - totals["Committed"]
    assert sum(money(row["Available"]) for row in categories if money(row["Available"]) < 0) == -60000


@pytest.mark.parametrize("relative", [POLICY, RULES])
def test_shared_policy_preserves_human_gates_and_forbids_tool_side_effects(relative):
    text = prose(relative)
    for gate in (
        "budget", "legal", "security", "competition", "supplier diversity",
        "conflicts of interest", "business-owner", "delegated-authority",
        "explicit publication review",
    ):
        assert gate in text
    assert "No agent/tool side effects are permitted." in text
    assert "Finance owns budget validation and reconciliation" in text
    assert "publish" in text


def test_manual_and_studio_shared_sources_match_existing_renderer():
    settings = (PACKAGE / "copilot-studio/settings.mcs.yml").read_text(encoding="utf-8")
    name = parse_yaml_scalar(settings, "displayName")
    schema = parse_yaml_scalar(settings, "schemaName")
    assert (name, schema) == ("Procurement Pilot", "aibast_ProcurementPilot")
    rendered = render_settings(name, schema, read_manual(POLICY))
    assert settings == "\n".join(line.rstrip() for line in rendered.splitlines()) + "\n"
    for path in (MANUAL / "knowledge").glob("*.md"):
        mirror = PACKAGE / "copilot-studio/capabilities/knowledge/files" / path.name
        assert mirror.read_bytes() == path.read_bytes()


def test_manual_and_studio_skills_match_existing_renderer():
    mirrors = set((PACKAGE / "copilot-studio/behaviors").glob("*.mcs.yml"))
    assert len(mirrors) == len(SKILLS)
    for relative in SKILLS:
        content, fields = render_skill(MANUAL / relative)
        mirror = PACKAGE / "copilot-studio/behaviors" / f"aibast_{fields['name']}.mcs.yml"
        assert mirror in mirrors
        expected = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
        assert mirror.read_text(encoding="utf-8") == expected
