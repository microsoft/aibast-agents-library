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
    / "easy_mode_agent.py"
)


def load_module():
    templates = AGENT_PATH.parent
    if str(templates) not in sys.path:
        sys.path.insert(0, str(templates))
    spec = importlib.util.spec_from_file_location(
        "aibast_easy_mode_agent",
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
    agent = module.AIBASTEasyModeAgent(
        raw_base=ROOT.as_uri() + "/",
        state_path=tmp_path / "easy-mode-state.json",
        agents_dir=agents_dir,
    )
    return module, agent, agents_dir


def test_easy_mode_prepares_task_cartridge_from_solution_name(tmp_path):
    _module, agent, agents_dir = build_agent(tmp_path)

    result = json.loads(
        agent.perform(
            operation="prepare",
            solution="Time Entry and Billing",
        )
    )

    assert result["status"] == "ready"
    assert result["active_solution"] == "time-entry-billing"
    assert result["hot_loaded"] is True
    assert Path(result["workshop_agent"]) == (
        agents_dir / "time_entry_billing_workshop_agent.py"
    )
    assert result["next_prompt"] == (
        "Give me Time Entry and Billing using the Easy Mode agent and test it "
        "for me."
    )


def test_easy_mode_start_step_is_ready_without_a_named_solution(tmp_path):
    _module, agent, _agents_dir = build_agent(tmp_path)

    result = json.loads(agent.perform(operation="prepare"))

    assert result == {
        "schema": "aibast-easy-mode-state/1.0",
        "status": "ready",
        "active_solution": None,
        "available_solutions": ["Time Entry and Billing"],
        "next_prompt": (
            "Give me Time Entry and Billing using the Easy Mode agent and test "
            "it for me."
        ),
        "published": False,
    }


def test_easy_mode_builds_and_tests_named_solution_personlessly(tmp_path):
    _module, agent, agents_dir = build_agent(tmp_path)

    result = json.loads(
        agent.perform(
            operation="build_and_test",
            solution="Time Entry and Billing",
        )
    )

    assert result["status"] == "tested"
    assert result["active_solution"] == "time-entry-billing"
    assert result["local_validation"]["passed"] == 5
    assert result["local_validation"]["total"] == 5
    assert result["target_agent"]["hot_loaded"] is True
    assert (agents_dir / "time_entry_billing_agent.py").exists()
    assert result["next_prompt"] == "Deploy it into Copilot Studio for me."
    assert result["published"] is False


def test_easy_mode_deploy_returns_continuation_handoff(tmp_path, monkeypatch):
    _module, agent, agents_dir = build_agent(tmp_path)
    agent.perform(
        operation="prepare",
        solution="Time Entry and Billing",
    )

    class FakeRunner:
        def perform(self, **_kwargs):
            return json.dumps(
                {
                    "status": "awaiting_front_door_validation",
                    "target_agent": {"tool": "TimeEntryBillingAgent"},
                    "local_validation": {"passed": 5, "total": 5},
                    "copilot_studio": {
                        "status": "Draft",
                        "published": False,
                    },
                    "copilot_handoff": {
                        "executor": "GitHub Copilot Agent mode",
                        "cases": [{"case_id": "TEB-01"}],
                    },
                }
            )

    monkeypatch.setattr(
        agent,
        "_load_workshop",
        lambda _slug, _workshop: (
            agents_dir / "time_entry_billing_workshop_agent.py",
            FakeRunner(),
        ),
    )

    result = json.loads(agent.perform(operation="deploy"))

    assert result["status"] == "awaiting_front_door_validation"
    assert result["copilot_studio"]["status"] == "Draft"
    assert result["copilot_studio"]["published"] is False
    assert "do not stop until" in result["continue_until"]
    assert result["published"] is False


def test_easy_mode_agent_is_registry_ready_and_never_publishes():
    module = load_module()
    source = AGENT_PATH.read_text(encoding="utf-8")
    assert module.__manifest__["name"] == "@aibast-agents-library/easy-mode"
    assert module.__manifest__["quality_tier"] == "pilot"
    assert "pac copilot publish" not in source
    assert '"--publish"' not in source
    assert "Never publish" in source
