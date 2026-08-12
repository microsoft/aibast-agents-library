"""Contract tests for the Microsoft first-party catalog and library view."""

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIRST_PARTY_FILE = REPO_ROOT / "first_party.json"
REGISTRY_FILE = REPO_ROOT / "registry.json"
LIBRARY_PAGE = REPO_ROOT / "library.html"

REQUIRED_FIELDS = {
    "id",
    "name",
    "product",
    "vertical",
    "deck_status",
    "description",
    "use_cases",
    "personas",
    "overview_url",
    "doc_status",
    "source_slide",
}
DECK_STATUSES = {"GA", "Preview"}
CURRENT_LIFECYCLES = {"Preview"}


@pytest.fixture(scope="module")
def catalog():
    return json.loads(FIRST_PARTY_FILE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def entries(catalog):
    return catalog["agents"]


@pytest.fixture(scope="module")
def by_id(entries):
    return {entry["id"]: entry for entry in entries}


@pytest.fixture(scope="module")
def registry():
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))


def test_schema_count_and_snapshot(catalog, entries):
    assert catalog["schema"] == "aibast-first-party/1.0"
    assert catalog["count"] == len(entries) == 14
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", catalog["snapshot_date"])
    assert catalog["links_verified_at"] == catalog["snapshot_date"]


def test_required_fields_and_identity(entries):
    ids = []
    names = []
    for entry in entries:
        assert REQUIRED_FIELDS.issubset(entry), (
            f"{entry.get('id')}: missing "
            f"{sorted(REQUIRED_FIELDS - set(entry))}"
        )
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry["id"])
        assert entry["source_slide"] in {1, 2}
        assert entry["doc_status"] == "dedicated"
        assert isinstance(entry["use_cases"], list)
        assert len(entry["use_cases"]) >= 3
        assert all(
            isinstance(value, str) and len(value.strip()) > 25
            for value in entry["use_cases"]
        )
        assert isinstance(entry["personas"], list) and entry["personas"]
        ids.append(entry["id"])
        names.append(entry["name"])
    assert len(ids) == len(set(ids))
    assert len(names) == len(set(names))


def test_deck_status_is_provenance_not_current_lifecycle(entries):
    assert sum(entry["deck_status"] == "GA" for entry in entries) == 10
    assert sum(entry["deck_status"] == "Preview" for entry in entries) == 4
    for entry in entries:
        assert entry["deck_status"] in DECK_STATUSES
        assert "status" not in entry, (
            f"{entry['id']}: source-deck status must not be presented as "
            "current lifecycle"
        )
        lifecycle = entry.get("lifecycle")
        if lifecycle is None:
            assert "lifecycle_source_url" not in entry
            continue
        assert lifecycle in CURRENT_LIFECYCLES
        assert entry["lifecycle_source_url"].startswith(
            "https://learn.microsoft.com/"
        )


def test_only_current_docs_explicitly_previewed_agents_are_labelled_preview(entries):
    preview_ids = {
        entry["id"]
        for entry in entries
        if entry.get("lifecycle") == "Preview"
    }
    assert preview_ids == {
        "sales-development-agent",
        "recommended-actions-agent",
    }


def test_only_exact_microsoft_learn_links_are_published(entries):
    for entry in entries:
        for key in (
            "overview_url",
            "configure_url",
            "lifecycle_source_url",
        ):
            if key not in entry:
                continue
            url = entry[key]
            assert isinstance(url, str) and url
            assert url.startswith("https://learn.microsoft.com/")


def test_known_bad_or_mismatched_links_are_absent(entries):
    serialized = json.dumps(entries)
    forbidden = {
        "configure-sales-opportunity-agent",
        "configure-data-enrichment-agent",
        "m365-admin-setting",
        "/use/use-intent-suggestions",
        "/administer/enable-intent-for-service-reps",
        "/implement/faq-rai-ai-agents",
        "/use/overview-ai-agents-copilot-features",
    }
    for token in forbidden:
        assert token not in serialized


def test_research_corrections_match_current_documentation(by_id):
    assert by_id["sales-agent-m365-copilot"]["name"] == "Sales agent"
    assert by_id["sales-agent-m365-copilot"]["configure_url"].endswith(
        "/set-up-sales-chat"
    )
    assert by_id["customer-intent-agent"]["configure_url"].endswith(
        "/manage-customer-intent-agent"
    )
    voice = by_id["customer-intent-agent-voice"]
    assert voice["name"] == "Customer Intent Agent for voice"
    assert voice["overview_url"].endswith(
        "/set-up-voice-agents-to-use-intents"
    )
    assert voice["configure_url"] == voice["overview_url"]


def test_newly_documented_quality_agents_are_linked(by_id):
    management = by_id["quality-management-agent"]
    assurance = by_id["quality-assurance-agent"]
    assert management["overview_url"].endswith(
        "/use/overview-quality-management"
    )
    assert "configure_url" not in management
    assert management["configure_note"]
    assert assurance["overview_url"].endswith(
        "/administer/use-quality-assurance-agent"
    )
    assert assurance["configure_url"].endswith(
        "/administer/configure-quality-coach"
    )


def test_case_management_does_not_claim_resolution_or_closure(by_id):
    entry = by_id["case-management-agent"]
    claims = " ".join([entry["description"], *entry["use_cases"]]).lower()
    for forbidden in (
        "resolve and close",
        "resolves cases",
        "closes cases",
        "end to end with no human",
    ):
        assert forbidden not in claims
    for required in ("create cases", "update configured case fields"):
        assert required in claims


def test_first_party_catalog_contains_no_custom_library_strategy(entries):
    for entry in entries:
        assert "related_repo_agents" not in entry
        assert "extension_opportunity" not in entry
        assert "build_vs_buy" not in entry


def test_no_roadmap_or_unannounced_product_claims(entries):
    banned = (
        "autopilot",
        "expected to",
        "will merge",
        "will become",
        "coming soon",
        "upcoming",
        "re-check at ga",
        "future release",
        "microsoft plans to",
    )
    for entry in entries:
        blob = json.dumps(entry).lower()
        for phrase in banned:
            assert phrase not in blob, (
                f"{entry['id']}: forward-looking phrase {phrase!r}"
            )


def test_registry_carries_first_party_separately(registry, entries):
    assert len(registry["first_party"]) == len(entries)
    assert registry["stats"]["total_first_party"] == len(entries)
    assert registry["stats"]["first_party_available"] == 12
    assert registry["stats"]["first_party_preview"] == 2
    assert registry["stats"]["first_party_documented"] == 14
    assert registry["stats"]["total_agents"] == len(registry["agents"])
    assert all(
        agent.get("_catalog_kind") != "first_party"
        for agent in registry["agents"]
    )


def test_registry_derived_fields(registry):
    for entry in registry["first_party"]:
        assert entry["_catalog_kind"] == "first_party"
        assert entry["_documented"] is True
        expected = entry.get("lifecycle") or "Available"
        assert entry["_availability_label"] == expected
        assert "_build_vs_buy" not in entry


def test_library_exposes_only_the_first_party_catalog_contract():
    page = LIBRARY_PAGE.read_text(encoding="utf-8")
    for token in (
        'data-view="first-party"',
        "registry.first_party",
        "function filteredFirstParty",
        "function firstPartyCard",
        "function openFirstParty",
        "Current use cases",
        "Microsoft Learn",
    ):
        assert token in page
    for forbidden in (
        "Where the library extends it",
        "Extend it with",
        "1P first, extend second",
        "related_repo_agents",
        "extension_opportunity",
    ):
        assert forbidden not in page


def test_library_filters_are_view_aware():
    page = LIBRARY_PAGE.read_text(encoding="utf-8")
    assert "function applyFilterOptions" in page
    assert 'const firstPartyView = state.view === "first-party"' in page
    handler = page.split(
        '} else if (action === "view") {', 1
    )[1].split("} else if", 1)[0]
    assert "buildFilters()" in handler


def test_first_party_verticals_are_labelled(entries):
    page = LIBRARY_PAGE.read_text(encoding="utf-8")
    for vertical in {entry["vertical"] for entry in entries}:
        assert f"{vertical}:" in page
