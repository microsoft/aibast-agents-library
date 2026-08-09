from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "aibast-easy-mode" / "SKILL.md"


def test_easy_mode_skill_is_shared_entry_point_for_both_lanes():
    text = SKILL.read_text(encoding="utf-8")
    assert text.startswith("---\nname: aibast-easy-mode\n")
    assert "**Default:** Brainstem + Copilot personless harness" in text
    assert "Comparison lane — GitHub Copilot only" in text
    assert "without Brainstem" in text
    assert ".aibast/easy-mode-state.json" in text
    assert "Deploy it into Copilot Studio for me" in text


def test_easy_mode_skill_discovers_every_resource_autonomously():
    text = SKILL.read_text(encoding="utf-8")
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
        "real Copilot Studio front door",
    ):
        assert marker in text
    assert "Never ask the user to open a terminal" in text
    assert "Never publish" in text


def test_easy_mode_skill_never_contains_a_publish_command():
    text = SKILL.read_text(encoding="utf-8")
    assert "pac copilot publish" not in text
    assert "published: false" in text
