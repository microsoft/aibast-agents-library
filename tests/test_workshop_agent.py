import importlib.util
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AGENT_PATH = (
    ROOT
    / "agents"
    / "@aibast-agents-library"
    / "templates"
    / "workshop_agent.py"
)


def load_module():
    templates = AGENT_PATH.parent
    if str(templates) not in sys.path:
        sys.path.insert(0, str(templates))
    spec = importlib.util.spec_from_file_location(
        "aibast_workshop_agent",
        AGENT_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_agent(tmp_path):
    module = load_module()
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    shutil.copy2(
        ROOT / "rapp_brainstem" / "agents" / "basic_agent.py",
        agents_dir / "basic_agent.py",
    )
    agent = module.AIBASTWorkshopAgent(
        raw_base=ROOT.as_uri() + "/",
        state_path=tmp_path / "workshop-state.json",
        agents_dir=agents_dir,
    )
    return module, agent, agents_dir


def test_generic_engine_builds_and_tests_time_entry_billing(tmp_path):
    _module, agent, agents_dir = build_agent(tmp_path)

    result = json.loads(
        agent.perform(
            operation="build_and_test",
            solution="Time Entry and Billing",
        )
    )

    assert result["status"] == "tested"
    assert result["active_agent"] == (
        "@aibast-agents-library/time-entry-billing"
    )
    assert result["active_solution"] == "time-entry-billing"
    assert result["local_validation"]["passed"] == 5
    assert result["local_validation"]["total"] == 5
    assert result["target_agent"]["tool"] == "TimeEntryBillingAgent"
    assert (agents_dir / "time_entry_billing_agent.py").exists()
    assert (
        Path(result["workspace"])
        / "tests"
        / "demo_cases"
        / "time-entry-billing.json"
    ).exists()
    assert result["next_prompt"] == "Deploy it into Copilot Studio for me."
    context = agent.system_context()
    assert "do not ask what 'it' means" in context
    assert "never offer or recommend publication" in context


def test_same_engine_adapts_to_inventory_rebalancing(tmp_path):
    _module, agent, agents_dir = build_agent(tmp_path)

    result = json.loads(
        agent.perform(
            operation="build_and_test",
            solution="Inventory Rebalancing",
        )
    )

    assert result["status"] == "tested"
    assert result["active_agent"] == (
        "@aibast-agents-library/inventory-rebalancing"
    )
    assert result["active_solution"] == "inventory-rebalancing"
    assert result["local_validation"]["passed"] == 4
    assert result["local_validation"]["total"] == 4
    assert result["target_agent"]["tool"] == "InventoryRebalancingAgent"
    assert (agents_dir / "inventory_rebalancing_agent.py").exists()


def test_generic_engine_returns_front_door_handoff(tmp_path, monkeypatch):
    _module, agent, _agents_dir = build_agent(tmp_path)
    monkeypatch.setattr(
        agent,
        "_deploy_draft",
        lambda _solution, _source, _deployment, _environment: {
            "display_name": "Time Entry and Billing Pilot",
            "schema_name": "aibast_TimeEntryandBillingPilot",
            "environment_id": "ee67a404-325c-e726-a18a-886fe708ca0b",
            "status": "Draft",
            "published": False,
        },
    )

    result = json.loads(
        agent.perform(
            operation="deploy",
            solution="Time Entry and Billing",
        )
    )

    assert result["status"] == "awaiting_front_door_validation"
    assert result["copilot_studio"]["published"] is False
    handoff = result["copilot_handoff"]
    assert handoff["solution"] == (
        "@aibast-agents-library/time-entry-billing"
    )
    assert len(handoff["cases"]) == 5
    assert "real Copilot Studio front door" in handoff["instruction"]


def test_generic_engine_closes_marker_only_front_door_evidence(tmp_path):
    _module, agent, _agents_dir = build_agent(tmp_path)
    agent.perform(
        operation="build_and_test",
        solution="Time Entry and Billing",
    )
    cases = json.loads(
        (ROOT / "tests/demo_cases/time-entry-billing.json").read_text(
            encoding="utf-8"
        )
    )["cases"]
    evidence = {
        "status": "Draft",
        "published": False,
        "cases": [
            {
                "case_id": case["id"],
                "must_include": case["must_include"],
                "must_not_include": case["must_not_include"],
                "passed": True,
            }
            for case in cases
        ],
    }

    result = json.loads(
        agent.perform(
            operation="complete",
            preview_evidence=json.dumps(evidence),
        )
    )

    assert result["status"] == "complete"
    assert result["front_door_validation"]["passed"] == 5
    assert result["front_door_validation"]["total"] == 5
    assert result["published"] is False
    assert "generic engine" in result["verdict"]


def test_workshop_agent_is_registry_ready_and_never_publishes():
    module = load_module()
    source = AGENT_PATH.read_text(encoding="utf-8")
    assert module.__manifest__["name"] == (
        "@aibast-agents-library/workshop"
    )
    assert module.__manifest__["quality_tier"] == "pilot"
    assert "pac copilot publish" not in source
    assert '"--publish"' not in source
    assert "Never publish" in source
