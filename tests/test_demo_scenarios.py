import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "solutions" / "_shared"
DEMO = SHARED / "m365-copilot-demo.html"
INDEX = SHARED / "demo-scenarios.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_the_committed_scenario_index_is_current():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "build_demo_scenarios.py"), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_every_library_demo_link_names_a_scenario_of_its_own_agent():
    scenarios = read_json(INDEX)["scenarios"]
    catalog = read_json(ROOT / "solutions" / "catalog.json")["solutions"]
    for agent_id, entry in catalog.items():
        for prompt in entry["sample_prompts"]:
            match = re.search(r"[?&]scenario=([a-z0-9-]+)", prompt["demo_url"])
            assert match, (agent_id, prompt["demo_url"])
            assert scenarios[match.group(1)]["agent_id"] == agent_id, prompt["demo_url"]


def test_every_recorded_scenario_plays_its_own_transcript():
    scenarios = read_json(INDEX)["scenarios"]
    for scenario_id, entry in scenarios.items():
        if not entry["recorded"]:
            continue
        artifact = read_json(ROOT / "solutions" / entry["folder"] / "evals" / "transcripts.json")
        cases = {item["case_id"] for item in artifact["transcripts"]}
        assert entry["case_id"] in cases, scenario_id


def test_almost_every_demo_link_is_recorded():
    summary = read_json(INDEX)["summary"]
    assert summary["not_recorded"] <= 10, summary


def test_the_demo_page_never_falls_back_to_another_agent():
    demo = DEMO.read_text(encoding="utf-8")
    assert 'getJSON("demo-scenarios.json")' in demo
    assert "SCENARIO_INDEX" not in demo
    assert "LEGACY_SCENARIOS" not in demo
    assert '|| "permit-backlog"' not in demo
    assert "This demo isn't recorded yet" in demo
    assert "api.github.com" not in demo
    assert "raw.githubusercontent.com" not in demo
