"""Every solution says where it came from: the original catalog, or the field (a customer AIdeate or RAPP session).

Wheel metrics split usage on it, so the tag must be on every solution, reach the registry, and reconcile in metrics.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_metrics  # noqa: E402

FIELD = {
    # Added 2026-10-08 from customer sessions worldwide.
    "benefits-enrollment-assistant", "briefing-pack-builder", "build-materials-compliance",
    "engineering-standards-advisor", "field-permit-to-work", "ma-target-sourcing", "order-entry-validation",
    "payments-operations", "public-correspondence-response", "reporting-package-validation",
    "solution-design-review", "staffing-territory-planning", "supplier-claim-engagement", "warranty-registration",
    # Added 2026-10-23: Telecom, Media & Gaming.
    "campaign-delivery-optimizer", "content-launch-clearance", "first-time-fix", "live-event-launch-planner",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog():
    return read_json(ROOT / "solutions" / "catalog.json")["solutions"]


def test_every_solution_has_a_source():
    for name, entry in catalog().items():
        assert entry.get("source") in {"catalog", "field"}, name
        if entry["source"] == "field":
            assert entry.get("origin") in {"aideate", "rapp_session", "both"}, name
        else:
            assert "origin" not in entry, name


def test_field_solutions_are_the_customer_session_ones():
    field = {name.split("/", 1)[1] for name, entry in catalog().items() if entry["source"] == "field"}
    assert field == FIELD


def test_registry_carries_the_source():
    registry = read_json(ROOT / "registry.json")
    cat = catalog()
    for agent in registry["agents"]:
        if agent.get("name") in cat:
            solution = agent.get("_solution") or {}
            assert solution.get("source") == cat[agent["name"]]["source"], agent["name"]
            assert solution.get("origin") == cat[agent["name"]].get("origin"), agent["name"]


def test_workshop_metrics_split_by_source_and_reconcile():
    workshops = [
        {"catalog_key": "@x/a", "slug": "a", "display_name": "A", "quest_url": "a", "path_rules": [], "source": "field", "origin": "both"},
        {"catalog_key": "@x/b", "slug": "b", "display_name": "B", "quest_url": "b", "path_rules": [], "source": "catalog", "origin": None},
        {"catalog_key": "@x/c", "slug": "c", "display_name": "C", "quest_url": "c", "path_rules": [], "source": "catalog", "origin": None},
    ]
    downloads = {
        "a": {"file_downloads": 5, "bundle_downloads": 1},
        "b": {"file_downloads": 2, "bundle_downloads": 0},
        "c": {"file_downloads": 3, "bundle_downloads": 4},
    }
    out = build_metrics.build_workshop_metrics(workshops, download_counts=downloads)
    by = out["by_source"]
    assert by["field"]["solutions"] == 1 and by["catalog"]["solutions"] == 2
    assert by["field"]["file_downloads"] == 5 and by["catalog"]["file_downloads"] == 5
    assert by["catalog"]["bundle_downloads"] == 4
    assert sum(group["file_downloads"] for group in by.values()) == out["totals"]["file_downloads"]
    assert {row["slug"]: row["source"] for row in out["rows"]} == {"a": "field", "b": "catalog", "c": "catalog"}
