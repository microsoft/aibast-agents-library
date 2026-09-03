import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).parents[1]
    / "agents"
    / "experimental"
    / "scout"
    / "exchange.py"
)
SPEC = importlib.util.spec_from_file_location("scout_exchange", MODULE_PATH)
exchange = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exchange)


def test_agent_skill_agent_round_trip_is_byte_exact(tmp_path):
    agent = tmp_path / "hello_agent.py"
    original = b'''from agents.basic_agent import BasicAgent

class HelloAgent(BasicAgent):
    def __init__(self):
        self.name = "Hello"
        self.metadata = {
            "name": self.name,
            "description": "Says hello.",
            "parameters": {"type": "object", "properties": {}},
        }
        super().__init__()
'''
    agent.write_bytes(original)
    skill = tmp_path / "SKILL.md"
    restored = tmp_path / "restored_agent.py"

    exchange.agent_to_skill(agent, skill)
    exchange.skill_to_agent(skill, restored)

    assert restored.read_bytes() == original


def test_skill_agent_skill_round_trip_is_byte_exact(tmp_path):
    skill = tmp_path / "SKILL.md"
    original = (
        b"---\nname: hello-skill\ndescription: Say hello safely.\n---\n\n"
        b"# Hello\n\nFollow the user's request.\n"
    )
    skill.write_bytes(original)
    agent = tmp_path / "hello_agent.py"
    restored = tmp_path / "restored.md"

    exchange.skill_to_agent(skill, agent)
    exchange.agent_to_skill(agent, restored)

    assert restored.read_bytes() == original


def test_squad_skill_squad_round_trip_is_byte_exact(tmp_path):
    squad = tmp_path / ".squad"
    (squad / "agents" / "planner").mkdir(parents=True)
    (squad / "team.md").write_bytes(b"# Team\n")
    (squad / "agents" / "planner" / "charter.md").write_bytes(b"# Planner\n")
    skill = tmp_path / "squad-skill.md"
    restored = tmp_path / "restored"

    exchange.squad_to_skill(squad, skill)
    exchange.skill_to_squad(skill, restored)

    assert (restored / "team.md").read_bytes() == b"# Team\n"
    assert (
        restored / "agents" / "planner" / "charter.md"
    ).read_bytes() == b"# Planner\n"


def test_squad_restore_refuses_parent_traversal(tmp_path):
    source = exchange._source_record(b"bad", "application/octet-stream")
    envelope = {
        "schema": exchange.SCHEMA,
        "artifact": {
            "kind": "scout-squad",
            "name": "bad",
            "files": [{"path": "../escape.txt", **source}],
        },
        "mapping": {},
        "protocol": exchange.PROTOCOL,
    }
    skill = tmp_path / "bad.md"
    skill.write_bytes(exchange._envelope_comment(envelope))

    with pytest.raises(exchange.ExchangeError):
        exchange.skill_to_squad(skill, tmp_path / "output")
