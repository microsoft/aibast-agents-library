"""Contract tests for the curated partner agent catalog and library view."""

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PARTNERS_FILE = REPO_ROOT / "partners.json"
REGISTRY_FILE = REPO_ROOT / "registry.json"
LIBRARY_PAGE = REPO_ROOT / "library.html"

REQUIRED_AGENT_FIELDS = {
    "id", "partner_id", "name", "category", "product",
    "description", "source_url",
}


@pytest.fixture(scope="module")
def catalog():
    return json.loads(PARTNERS_FILE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def partners(catalog):
    return catalog["partners"]


@pytest.fixture(scope="module")
def entries(catalog):
    return catalog["agents"]


@pytest.fixture(scope="module")
def registry():
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))


def test_schema_and_count(catalog, entries):
    assert catalog["schema"] == "aibast-partners/1.0"
    assert catalog["count"] == len(entries)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", catalog["snapshot_date"])


def test_partners_are_identified_and_linked(partners):
    ids = [p["id"] for p in partners]
    assert len(ids) == len(set(ids))
    for partner in partners:
        assert partner["url"].startswith("http")
        assert partner["name"]


def test_required_fields_and_identity(entries, partners):
    partner_ids = {p["id"] for p in partners}
    ids = []
    names = []
    for entry in entries:
        assert REQUIRED_AGENT_FIELDS.issubset(entry), (
            f"{entry.get('id')}: missing "
            f"{sorted(REQUIRED_AGENT_FIELDS - set(entry))}"
        )
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry["id"])
        assert entry["partner_id"] in partner_ids
        assert entry["source_url"].startswith("http")
        assert len(entry["description"].strip()) > 20
        ids.append(entry["id"])
        names.append(entry["name"])
    assert len(ids) == len(set(ids))
    assert len(names) == len(set(names))


def test_descriptions_are_not_copied_marketing_headlines(entries):
    # Guards against verbatim reuse of the partner site's own promotional
    # headline copy instead of a paraphrased, factual summary.
    banned_phrases = (
        "real-time answers, smarter sales on the go",
        "unleash revenue with ai agents",
    )
    for entry in entries:
        blob = entry["description"].lower()
        for phrase in banned_phrases:
            assert phrase not in blob, f"{entry['id']}: verbatim partner headline reused"


# Exact wording confirmed from https://congruentx.com/ai-agents-library/ at
# fetch time. Any drift here should be re-verified against the source before
# being changed, since these are quoted as the partner's own stated numbers.
KNOWN_PARTNER_OUTCOMES = {
    "congruentx-buyer-intent-enrichment": "20\u201350% higher campaign ROI vs broad programs",
    "congruentx-hyper-targeted-market-segmentation": "+5\u201315% marketing ROI, reduced spend on low-impact segments",
    "congruentx-dynamic-journey-orchestration": "10\u201315% lift in journey revenue",
    "congruentx-event-webinar-persona-journeys": "+10\u201320% higher MQL\u2192SQL conversion on event leads",
    "congruentx-first-impact-claims-portal": "+5\u201310 NPS points post-claim, better retention",
    "congruentx-icp-targeting-by-line": "10\u201315% higher win rate",
    "congruentx-dormant-account-reactivation": "10\u201320% of dormant accounts reactivated",
    "congruentx-service-contracts-attach-rate": "10\u201330% higher attach rate",
    "congruentx-target-accounts-buying-committee": "Higher win rate, larger average deal size (5\u201315%)",
    "congruentx-thought-leadership-orchestration": "Strong influence on pipeline; higher engagement, 5\u201310% more opps sourced",
}


def test_partner_reported_outcomes_match_verified_source_text(entries):
    by_id = {entry["id"]: entry for entry in entries}
    for agent_id, expected in KNOWN_PARTNER_OUTCOMES.items():
        assert by_id[agent_id]["partner_reported_outcome"] == expected
    # Every other entry must not have an outcome invented for it.
    for entry in entries:
        if entry["id"] not in KNOWN_PARTNER_OUTCOMES:
            assert "partner_reported_outcome" not in entry


def test_no_partner_agent_duplicates_an_existing_aibast_agent(entries):
    # This catalog exists to show breadth beyond AIBAST's own lineup, not a
    # relabeled copy of it, so no entry should carry a mapping/comparison
    # back to an AIBAST agent.
    for entry in entries:
        assert "aibast_equivalent" not in entry


def test_partner_agents_have_rich_detail(entries):
    for entry in entries:
        assert entry.get("what_it_does"), f"{entry['id']}: missing what_it_does"
        assert entry.get("problem_it_solves"), f"{entry['id']}: missing problem_it_solves"
        assert entry.get("who_it_helps"), f"{entry['id']}: missing who_it_helps"
        for field in ("what_it_does", "problem_it_solves", "who_it_helps"):
            assert isinstance(entry[field], list) and entry[field]
            assert all(isinstance(v, str) and v.strip() for v in entry[field])


def test_registry_carries_partner_agents_separately(registry, entries, partners):
    assert len(registry["partner_agents"]) == len(entries)
    assert registry["partners"] == partners
    assert registry["stats"]["total_partner_agents"] == len(entries)
    assert registry["stats"]["partner_list"] == sorted({p["name"] for p in partners})
    assert all(
        agent.get("_catalog_kind") != "partner"
        for agent in registry["agents"]
    ), "partner agents must never be merged into the repo-owned agents array"
    assert registry["stats"]["total_agents"] == len(registry["agents"])


def test_registry_derived_fields(registry):
    for entry in registry["partner_agents"]:
        assert entry["_catalog_kind"] == "partner"


def test_library_exposes_the_partners_tab_and_contract():
    page = LIBRARY_PAGE.read_text(encoding="utf-8")
    for token in (
        'data-view="partners"',
        "registry.partner_agents",
        "registry.partners",
        "function filteredPartnerAgents",
        "function partnerAgentCard",
        "function openPartnerAgent",
        "Partner listing",
        "Partner-reported",
        "What it does",
        "Problem it solves",
        "Who it helps",
        "not independently verified by AIBAST",
    ):
        assert token in page
    for forbidden in (
        "function aibastEquivalentOf",
        "aibast_equivalent",
        "compare approaches",
        "Build it yourself with AIBAST",
        "Buy vs. build",
        "See AIBAST's agent",
    ):
        assert forbidden not in page


def test_partner_agents_link_back_to_source(entries):
    for entry in entries:
        assert entry["source_url"].startswith("https://congruentx.com/") or entry["partner_id"] != "congruentx"
