import importlib.util
import json
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
ONEPAGERS = json.loads(
    (ROOT / "state" / "onepager_content.json").read_text(encoding="utf-8")
)["onepagers"]

SOLUTIONS = {
    "inventory-rebalancing": {
        "name": "@aibast-agents-library/inventory-rebalancing",
        "source": ROOT
        / "agents/@aibast-agents-library/manufacturing_stacks/"
        "inventory_rebalancing_stack/inventory_rebalancing_agent.py",
        "class": "InventoryRebalancingAgent",
        "agent_file": "inventory_rebalancing_agent",
        "constants": [
            "WAREHOUSES",
            "SKU_INVENTORY",
            "DEMAND_FORECASTS",
            "REORDER_POINTS",
            "PORTFOLIO_CLASSIFICATIONS",
            "TRANSFER_COSTS_PER_KG",
        ],
        "operations": {
            "inventory_snapshot": ["Dallas Fulfillment Center", "SKU-4406"],
            "rebalance_recommendation": ["SKU-4402", "SLOW-MOVING"],
            "transfer_plan": ["SKU-4401", "No inventory has been reserved"],
            "cost_analysis": ["Total annual holding cost", "synthetic planning estimates"],
        },
        "onepager": "Inventory Rebalancing Agent one-pager.pptx",
        "forbidden_claims": ["inventory has been moved", "transfer was executed"],
    },
    "maintenance-scheduling": {
        "name": "@aibast-agents-library/maintenance-scheduling",
        "source": ROOT
        / "agents/@aibast-agents-library/manufacturing_stacks/"
        "maintenance_scheduling_stack/maintenance_scheduling_agent.py",
        "class": "MaintenanceSchedulingAgent",
        "agent_file": "maintenance_scheduling_agent",
        "constants": [
            "EQUIPMENT",
            "SENSOR_READINGS",
            "FAILURE_PROBABILITIES",
            "TECHNICIANS",
            "MAINTENANCE_HISTORY",
            "DOWNTIME_COST_PER_HOUR",
            "PARTS_READINESS",
            "BACKUP_READINESS",
        ],
        "operations": {
            "schedule_overview": ["EQ-INJ-01", "Technician Availability"],
            "predictive_alerts": ["EQ-INJ-01", "Barrel heater band failure"],
            "work_order_plan": ["EQ-INJ-01", "No work order is created or dispatched"],
            "downtime_analysis": [
                "Modeled avoided-cost opportunity",
                "synthetic planning estimates",
            ],
        },
        "onepager": "Maintenance Scheduling Agent one-pager.pptx",
        "forbidden_claims": ["technician assigned", "work order dispatched"],
    },
    "supplier-risk-monitoring": {
        "name": "@aibast-agents-library/supplier-risk-monitoring",
        "source": ROOT
        / "agents/@aibast-agents-library/manufacturing_stacks/"
        "supplier_risk_monitoring_stack/supplier_risk_monitoring_agent.py",
        "class": "SupplierRiskMonitoringAgent",
        "agent_file": "supplier_risk_monitoring_agent",
        "constants": [
            "SUPPLIERS",
            "RECENT_INCIDENTS",
            "BACKUP_SUPPLIERS",
        ],
        "operations": {
            "risk_dashboard": ["TechnoCore Semiconductor", "CRITICAL"],
            "supplier_scorecard": ["SUP-101", "Geopolitical"],
            "disruption_alerts": ["SUP-104", "force majeure"],
            "alternative_sourcing": ["Murata Electronics", "No supplier was contacted"],
        },
        "onepager": "Supply Risk Monitoring Agent one-pager.pptx",
        "forbidden_claims": ["we contacted the supplier", "we selected the supplier"],
    },
    "order-status-communication": {
        "name": "@aibast-agents-library/order-status-communication",
        "source": ROOT
        / "agents/@aibast-agents-library/manufacturing_stacks/"
        "order_status_communication_stack/order_status_communication_agent.py",
        "class": "OrderStatusCommunicationAgent",
        "agent_file": "order_status_communication_agent",
        "constants": [
            "ORDERS",
            "SHIPMENTS",
            "DELAY_REASONS",
            "CUSTOMER_CONTACTS",
        ],
        "operations": {
            "order_lookup": ["ORD-7813", "DELAYED"],
            "shipment_tracking": ["ORD-7812", "XPO-884291047"],
            "delay_notification": ["ORD-7813", "Recorded synthetic recovery options"],
            "customer_update": ["Customer Update Drafts", "No email, EDI message"],
        },
        "onepager": "44. Order Status Communications Agent one-pager.pptx",
        "forbidden_claims": ["customer update was sent", "email was sent"],
    },
}

HARDENED_SOLUTIONS = {
    slug: config
    for slug, config in SOLUTIONS.items()
    if slug in {"supplier-risk-monitoring", "order-status-communication"}
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_agent(slug, config):
    spec = importlib.util.spec_from_file_location(slug.replace("-", "_"), config["source"])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, getattr(module, config["class"])()


def normalize_source_value(value):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if isinstance(key, tuple):
                key = " -> ".join(str(part) for part in key)
            else:
                key = str(key)
            result[key] = normalize_source_value(item)
        return result
    if isinstance(value, (list, tuple)):
        return [normalize_source_value(item) for item in value]
    return value


@pytest.mark.parametrize(("slug", "config"), SOLUTIONS.items())
def test_deterministic_source_covers_each_persona_case_safely(slug, config):
    _, agent = load_agent(slug, config)
    operation = agent.metadata["parameters"]["properties"]["operation"]
    assert operation["enum"] == list(config["operations"])
    assert "never" in agent.metadata["description"].lower()

    for name, expected in config["operations"].items():
        output = agent.perform(operation=name)
        assert "synthetic" in output.lower()
        for value in expected:
            assert value in output
        for forbidden in config["forbidden_claims"]:
            assert forbidden not in output.lower()


@pytest.mark.parametrize(("slug", "config"), SOLUTIONS.items())
def test_package_maps_onepager_cases_knowledge_and_skills(slug, config):
    package = ROOT / "solutions" / slug
    cases = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")["cases"]
    promise_map = read_json(package / "evals" / "onepager-map.json")
    source = ONEPAGERS[config["onepager"]]

    assert (package / "README.md").exists()
    assert (package / "deployment.json").exists()
    assert (package / "evals" / "source-audit.json").exists()
    assert promise_map["solution"] == config["name"]
    assert promise_map["source_slide_sha256"] == source["source_sha256"]
    assert {case["operation"] for case in cases} == set(config["operations"])
    assert all(case["persona"] and case["prompt"] for case in cases)
    case_contract = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")
    assert case_contract["agent_files"] == [config["agent_file"]]
    assert len(list((package / "manual" / "knowledge").glob("*.md"))) == 2

    skills = list((package / "manual" / "skills").glob("*/SKILL.md"))
    assert len(skills) == len(config["operations"])
    assert all(path.read_text(encoding="utf-8").startswith("---\n") for path in skills)


@pytest.mark.parametrize(("slug", "config"), SOLUTIONS.items())
def test_deployment_is_manual_and_recommendation_only(slug, config):
    deployment = read_json(ROOT / "solutions" / slug / "deployment.json")
    studio = deployment["copilot_studio"]
    assert deployment["name"] == config["name"]
    assert deployment["expected_tool"] == config["class"]
    assert studio["authoring_mode"] == "manual-upload"
    assert studio["status"] == "not_initialized"
    assert studio["publish_requires_confirmation"] is True
    assert studio["manual_skill_count"] == len(config["operations"])
    assert "never" in deployment["safety_boundary"].lower()


def test_solution_public_copy_is_qualitative():
    for slug in SOLUTIONS:
        readme = (ROOT / "solutions" / slug / "README.md").read_text(encoding="utf-8")
        public_scope = readme.split("## Proven now")[0].split(
            "## Manual Copilot Studio preparation"
        )[0]
        assert "%" not in public_scope
        assert not re.search(r"\b\d+(?:\.\d+)?\b", public_scope)


@pytest.mark.parametrize(("slug", "config"), HARDENED_SOLUTIONS.items())
def test_knowledge_is_complete_not_placeholder_and_matches_source(slug, config):
    package = ROOT / "solutions" / slug
    records_path = next((package / "manual" / "knowledge").glob("*synthetic-records.md"))
    rules_path = next((package / "manual" / "knowledge").glob("*review-rules.md"))
    records = records_path.read_text(encoding="utf-8")
    rules = rules_path.read_text(encoding="utf-8")
    module, agent = load_agent(slug, config)

    assert len(records) > 4_000
    assert len(rules) > 6_000
    assert records.count("\n## ") >= len(config["constants"]) + 2
    assert rules.count("\n### `") == len(config["operations"])
    assert "```json" in records
    assert "```markdown" in rules
    assert not re.search(r"\b(?:TODO|PLACEHOLDER|SCHEMA[- ]ONLY)\b", records + rules, re.I)

    for constant_name in config["constants"]:
        source_value = normalize_source_value(getattr(module, constant_name))
        exact_json = json.dumps(source_value, indent=2, ensure_ascii=False)
        assert f"`{constant_name}`" in records
        assert exact_json in records

    for operation in config["operations"]:
        assert agent.perform(operation=operation) in rules


@pytest.mark.parametrize(("slug", "config"), HARDENED_SOLUTIONS.items())
def test_knowledge_and_skills_reproduce_locked_transcript_evidence(slug, config):
    package = ROOT / "solutions" / slug
    knowledge = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((package / "manual" / "knowledge").glob("*.md"))
    )
    cases = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")["cases"]
    transcript = read_json(package / "evals" / "transcripts.json")
    captured = {item["case_id"]: item for item in transcript["transcripts"]}

    assert transcript["strict_isolation"] is True
    assert set(captured) == {case["id"] for case in cases}
    for case in cases:
        item = captured[case["id"]]
        assert item["passed"] is True
        assert item["prompt"] == case["prompt"]
        assert case["prompt"] in knowledge
        assert f"`{case['operation']}`" in knowledge
        for evidence in case["must_include"]:
            assert evidence in knowledge

        skill = (
            package
            / "manual"
            / "skills"
            / f"aibast_{case['operation']}"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        assert case["prompt"] in skill
        assert all(evidence in skill for evidence in case["must_include"])
        assert "external action that was not performed" in skill
