"""ms-rapp/1 stays a backward-compatible profile of rapp/1.

1. Every example Step loads with the Brainstem kernel's own BasicAgent and passes the profile checks.
2. A Step still behaves as a plain rapp/1 agent: to_tool() and perform() work with no ms-rapp/1 host.
3. The generated OpenAPI file matches the Steps, so a Foundry OpenAPI tool sees the same contract.
4. The profile notes pin the same upstream commit as the rest of the vault.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import build_ms_rapp1 as profile  # noqa: E402
from tools import build_rapp1_vault as vault  # noqa: E402


def test_openapi_matches_the_steps():
    assert profile.main(["--check"]) == 0


def test_steps_are_plain_rapp1_agents():
    steps = profile.steps()
    assert steps
    for module, agent in steps:
        tool = agent.to_tool()
        assert tool["type"] == "function"
        assert tool["function"]["name"] == agent.name
        assert isinstance(agent.perform(), str)


def test_example_step_result_matches_its_schema():
    module, agent = next((m, a) for m, a in profile.steps() if m.ROUTE == "action-items")
    out = json.loads(agent.perform(notes="Action: Dana: send the pricing sheet\n- TODO: book the follow-up\nnoise"))
    assert out == {"items": [{"owner": "Dana", "task": "send the pricing sheet"},
                             {"owner": "Unassigned", "task": "book the follow-up"}]}
    for key in module.RESULT_SCHEMA["required"]:
        assert key in out


def test_openapi_has_one_operation_per_step():
    doc = json.loads(profile.OPENAPI.read_text(encoding="utf-8"))
    routes = {"/api/lens/" + m.ROUTE for m, _ in profile.steps()}
    assert set(doc["paths"]) == routes
    for module, agent in profile.steps():
        op = doc["paths"]["/api/lens/" + module.ROUTE]["post"]
        assert op["requestBody"]["content"]["application/json"]["schema"] == agent.metadata["parameters"]


def test_profile_rejects_a_step_without_a_route(tmp_path):
    bad = tmp_path / "bad_agent.py"
    bad.write_text("from basic_agent import BasicAgent\n"
                   "class Bad(BasicAgent):\n"
                   "    def __init__(self):\n"
                   "        super().__init__(name='Bad', metadata={'name': 'Bad', 'description': 'd',"
                   " 'parameters': {'type': 'object', 'properties': {}}})\n", encoding="utf-8")
    module, agent = profile.load_step(bad)
    try:
        profile.check(module, agent, bad)
    except profile.ProfileError:
        return
    raise AssertionError("a Step without ROUTE was accepted")


def test_profile_notes_pin_the_vault_commit():
    overview = (vault.VAULT / "ms-rapp-1" / "ms-rapp-1 Overview.md").read_text(encoding="utf-8")
    meta, _ = vault.parse_frontmatter(overview)
    assert meta["upstream_commit"] == vault.UPSTREAM_COMMIT
