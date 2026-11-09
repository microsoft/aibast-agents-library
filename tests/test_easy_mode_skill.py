from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BRAINSTEM_SKILL = (
    ROOT / "skills" / "aibast-easy-mode-brainstem" / "SKILL.md"
)
COPILOT_SKILL = (
    ROOT / "skills" / "aibast-easy-mode-copilot" / "SKILL.md"
)
EASY_SKILL = ROOT / "skills" / "aibast-easy-mode" / "SKILL.md"


def test_old_skills_are_aliases_with_preserved_names():
    brainstem = BRAINSTEM_SKILL.read_text(encoding="utf-8")
    copilot = COPILOT_SKILL.read_text(encoding="utf-8")

    assert brainstem.startswith(
        "---\nname: aibast-easy-mode-brainstem\n"
    )
    assert copilot.startswith(
        "---\nname: aibast-easy-mode-copilot\n"
    )
    for text in (brainstem, copilot):
        assert "description: Alias" in text
        assert "This file is an alias of `aibast-easy-mode`" in text
        assert "main/skills/aibast-easy-mode/SKILL.md" in text
    assert "brainstem" not in copilot.lower()


def test_one_skill_accepts_the_same_short_messages():
    text = EASY_SKILL.read_text(encoding="utf-8")
    messages = (
        "Give me <solution> using Easy Mode and test it for me",
        "Deploy it into Copilot Studio for me",
    )
    for message in messages:
        assert message in text


def test_brainstem_skill_owns_engine_startup_and_handoffs():
    text = EASY_SKILL.read_text(encoding="utf-8")
    for marker in (
        "http://localhost:7071/health",
        "~/.copilot/bin/brainstem start",
        "@aibast-agents-library/workshop",
        "POST http://localhost:7071/agents/import",
        "POST http://localhost:7071/chat",
        "real Copilot Studio front door",
        "status: complete",
    ):
        assert marker in text


def test_copilot_skill_discovers_every_resource_autonomously():
    text = EASY_SKILL.read_text(encoding="utf-8")
    compact = " ".join(text.split())
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
        assert marker in compact


def test_copilot_skill_bootstraps_official_studio_plugin_and_pac():
    text = EASY_SKILL.read_text(encoding="utf-8")
    compact = " ".join(text.split())
    for marker in (
        "python3 tools/easy_mode_preflight.py --json",
        "repository-owned, fail-closed setup step",
        "microsoft/copilot-studio-plugin",
        "copilot plugin marketplace add microsoft/copilot-studio-plugin",
        "copilot plugin install mcs-assistant@copilot-studio-plugin",
        "dotnet tool update --global Microsoft.PowerApps.CLI.Tool",
        "newer than 2.9.3",
        "pac --version",
        "manage, describe,",
        "plugin architect",
        "plugin manager to push the Draft",
        "Do not continue to deployment",
    ):
        assert marker in compact
    assert "Never deploy through the direct engine without the verified Microsoft" in text
    assert "Stop when it exits nonzero or reports `passed: false`" in compact


def test_neither_skill_can_publish_or_delegate_setup_to_the_user():
    for path in (EASY_SKILL,):
        text = path.read_text(encoding="utf-8")
        assert "pac copilot publish" not in text
        assert "published: false" in text
        assert "Never ask the user" in text
        assert "Never publish" in text


def test_lane_skills_pull_workshops_from_the_canonical_source():
    """Pages renders the public source lines to the serving ring."""
    for path in (EASY_SKILL,):
        text = path.read_text(encoding="utf-8")
        assert "- Repository: `microsoft/aibast-agents-library`\n- Workshop branch: `main`\n" in text
        assert "easy-mode-copilot-chat-pilot" not in text
        assert "kody-w" not in text


def test_both_lane_skills_offer_the_library_and_let_the_user_pick():
    for path in (EASY_SKILL,):
        compact = " ".join(path.read_text(encoding="utf-8").split())
        assert "## Choose from the library" in compact
        assert "Show me the AIBAST library, then give me the workshop I pick using Easy Mode and test it for me" in compact
        assert "`_catalog_kind` is `solution`" in compact
        assert "`display_name — description`" in compact
        assert "Never choose for the user, and never download a workshop before they choose." in compact
        assert "Ask HR" not in compact
