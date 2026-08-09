from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BRAINSTEM_SKILL = (
    ROOT / "skills" / "aibast-easy-mode-brainstem" / "SKILL.md"
)
COPILOT_SKILL = (
    ROOT / "skills" / "aibast-easy-mode-copilot" / "SKILL.md"
)


def test_lane_selection_is_encoded_by_the_downloaded_skill():
    brainstem = BRAINSTEM_SKILL.read_text(encoding="utf-8")
    copilot = COPILOT_SKILL.read_text(encoding="utf-8")

    assert brainstem.startswith(
        "---\nname: aibast-easy-mode-brainstem\n"
    )
    assert copilot.startswith(
        "---\nname: aibast-easy-mode-copilot\n"
    )
    assert "personal, on-device training AI" in brainstem
    assert "use the Brainstem personless harness" in " ".join(
        brainstem.split()
    )
    compact = " ".join(copilot.split())
    assert "run the complete Easy Mode harness directly in Copilot" in compact
    assert "The user never needs to say “without Brainstem”" in compact


def test_both_skills_accept_the_same_short_messages():
    brainstem = BRAINSTEM_SKILL.read_text(encoding="utf-8")
    copilot = COPILOT_SKILL.read_text(encoding="utf-8")
    messages = (
        "Give me <solution> using Easy Mode and test it for me",
        "Deploy it into Copilot Studio for me",
    )
    for message in messages:
        assert message in brainstem
        assert message in copilot


def test_brainstem_skill_owns_engine_startup_and_handoffs():
    text = BRAINSTEM_SKILL.read_text(encoding="utf-8")
    for marker in (
        "http://localhost:7071/health",
        "~/.copilot/bin/brainstem start",
        "@aibast-agents-library/easy-mode",
        "POST http://localhost:7071/agents/import",
        "POST http://localhost:7071/chat",
        "real Copilot Studio front door",
        "status: complete",
    ):
        assert marker in text


def test_copilot_skill_discovers_every_resource_autonomously():
    text = COPILOT_SKILL.read_text(encoding="utf-8")
    for marker in (
        "one immutable commit SHA",
        "registry.json",
        "deployment.json",
        "export-manifest.json",
        "tests/demo_cases/<slug>.json",
        "must_include",
        "must_not_include",
        "Resolve the active PAC environment",
        "clone and reconnect automatically",
    ):
        assert marker in text


def test_neither_skill_can_publish_or_delegate_setup_to_the_user():
    for path in (BRAINSTEM_SKILL, COPILOT_SKILL):
        text = path.read_text(encoding="utf-8")
        assert "pac copilot publish" not in text
        assert "published: false" in text
        assert "Never ask the user" in text
        assert "Never publish" in text
