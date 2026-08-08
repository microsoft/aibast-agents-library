import importlib.util
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AGENT_PATH = (
    ROOT
    / "solutions"
    / "time-entry-billing"
    / "easy"
    / "time_entry_billing_workshop_agent.py"
)


def load_module():
    brainstem_agents = ROOT / "rapp_brainstem" / "agents"
    if str(brainstem_agents) not in sys.path:
        sys.path.insert(0, str(brainstem_agents))
    spec = importlib.util.spec_from_file_location(
        "time_entry_billing_workshop_agent",
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
    agent = module.TimeEntryBillingWorkshop(
        raw_base=ROOT.as_uri() + "/",
        workshop_home=tmp_path / "workshop",
        agents_dir=agents_dir,
    )
    return module, agent, agents_dir


def test_personless_harness_hotloads_and_proves_every_local_case(tmp_path):
    _module, agent, agents_dir = build_agent(tmp_path)

    result = json.loads(
        agent.perform(
            operation="run_workshop",
            deploy_to_studio=False,
        )
    )

    assert result["status"] == "local_proof_passed"
    assert result["engine"] == "RAPP Brainstem"
    assert result["target_agent"]["tool"] == "TimeEntryBillingAgent"
    assert result["target_agent"]["hot_loaded"] is True
    assert Path(result["target_agent"]["installed_to"]) == (
        agents_dir / "time_entry_billing_agent.py"
    )
    assert result["local_validation"]["passed"] == 5
    assert result["local_validation"]["total"] == 5
    assert all(case["passed"] for case in result["local_validation"]["cases"])
    assert result["copilot_studio"] == {
        "status": "not_requested",
        "published": False,
    }
    assert result["published"] is False


def test_personless_harness_closes_loop_from_front_door_evidence(tmp_path):
    _module, agent, _agents_dir = build_agent(tmp_path)
    started = json.loads(
        agent.perform(
            operation="run_workshop",
            deploy_to_studio=False,
        )
    )
    assert started["status"] == "local_proof_passed"

    transcripts = json.loads(
        (ROOT / "solutions/time-entry-billing/evals/transcripts.json").read_text(
            encoding="utf-8"
        )
    )
    evidence = {
        "status": "Draft",
        "published": False,
        "cases": [
            {
                "case_id": item["case_id"],
                "response": item["agent_logs"],
            }
            for item in transcripts["transcripts"]
        ],
    }
    completed = json.loads(
        agent.perform(
            operation="complete_workshop",
            preview_evidence=json.dumps(evidence),
        )
    )

    assert completed["status"] == "complete"
    assert completed["front_door_validation"]["passed"] == 5
    assert completed["front_door_validation"]["total"] == 5
    assert completed["published"] is False
    assert "Personless workshop complete" in completed["verdict"]


def test_personless_harness_accepts_captured_marker_contract(tmp_path):
    _module, agent, _agents_dir = build_agent(tmp_path)
    agent.perform(
        operation="run_workshop",
        deploy_to_studio=False,
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

    completed = json.loads(
        agent.perform(
            operation="complete_workshop",
            preview_evidence=json.dumps(evidence),
        )
    )

    assert completed["status"] == "complete"
    assert completed["front_door_validation"]["passed"] == 5


def test_personless_harness_returns_copilot_front_door_handoff(
    tmp_path,
    monkeypatch,
):
    _module, agent, _agents_dir = build_agent(tmp_path)
    monkeypatch.setattr(
        agent,
        "_deploy_draft",
        lambda _source_root, _environment_id: {
            "display_name": "Time Entry and Billing Pilot",
            "schema_name": "aibast_TimeEntryandBillingPilot",
            "environment_id": "ee67a404-325c-e726-a18a-886fe708ca0b",
            "status": "Draft",
            "published": False,
        },
    )

    result = json.loads(
        agent.perform(
            operation="run_workshop",
            deploy_to_studio=True,
        )
    )

    assert result["status"] == "awaiting_front_door_validation"
    assert result["copilot_studio"]["status"] == "Draft"
    assert result["copilot_studio"]["published"] is False
    handoff = result["copilot_handoff"]
    assert handoff["executor"] == "GitHub Copilot Agent mode"
    assert len(handoff["cases"]) == 5
    assert "real Copilot Studio front door" in handoff["instruction"]
    assert "complete_workshop" in handoff["instruction"]


def test_personless_harness_auto_clones_recorded_draft(
    tmp_path,
    monkeypatch,
):
    _module, agent, _agents_dir = build_agent(tmp_path)
    source_root = tmp_path / "source"
    package = source_root / "solutions" / "time-entry-billing"
    package.mkdir(parents=True)
    (source_root / "tools").mkdir()
    (source_root / "tools" / "promote_solution_draft.py").write_text(
        "# fixture\n",
        encoding="utf-8",
    )
    environment = "ee67a404-325c-e726-a18a-886fe708ca0b"
    deployment = {
        "display_name": "Time Entry and Billing Agent",
        "copilot_studio": {
            "validated_pilot": {
                "display_name": "Time Entry and Billing Pilot",
                "schema_name": "aibast_TimeEntryandBillingPilot",
                "environment_id": environment,
            }
        },
    }
    (package / "deployment.json").write_text(
        json.dumps(deployment),
        encoding="utf-8",
    )
    monkeypatch.setattr(agent, "_find_pac", lambda: "/usr/bin/true")
    monkeypatch.setattr(
        agent,
        "_resolve_environment",
        lambda _pac, _explicit: (environment, "active-pac-profile"),
    )
    commands = []

    def fake_run(command, **_kwargs):
        commands.append(command)
        if "clone" in command:
            project = (
                agent.workshop_home
                / "copilot-studio-projects"
                / "Time Entry and Billing Pilot"
            )
            (project / ".mcs").mkdir(parents=True)
            (project / ".mcs" / "conn.json").write_text(
                "{}",
                encoding="utf-8",
            )
            return "Clone complete"
        return json.dumps(
            {
                "display_name": "Time Entry and Billing Pilot",
                "schema_name": "aibast_TimeEntryandBillingPilot",
                "pushed": True,
            }
        )

    monkeypatch.setattr(agent, "_run_command", fake_run)

    result = agent._deploy_draft(source_root, "")

    assert commands[0][1:3] == ["copilot", "clone"]
    assert "aibast_TimeEntryandBillingPilot" in commands[0]
    assert "--update-existing" in commands[1]
    assert result["environment_id"] == environment
    assert result["published"] is False


def test_personless_harness_never_contains_a_publish_command():
    source = AGENT_PATH.read_text(encoding="utf-8")
    assert "pac copilot publish" not in source
    assert '"--publish"' not in source
    assert "Never publish" in source
