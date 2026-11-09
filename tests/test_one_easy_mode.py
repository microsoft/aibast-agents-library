from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = "skills/aibast-easy-mode/SKILL.md"
PACKAGES = sorted((ROOT / "solutions").glob("*/deployment.json"))


def test_one_skill_owns_both_build_and_deploy_contracts():
    text = (ROOT / SKILL_PATH).read_text(encoding="utf-8")
    assert text.startswith("---\nname: aibast-easy-mode\n")
    assert "## Pick the engine" in text
    build, deploy = text.split("## Build and test", 1)[1].split("## Deploy", 1)
    for section in (build, deploy):
        assert "With engine `brainstem`:" in section
        assert "With engine `copilot`:" in section
    for marker in (
        "http://localhost:7071/agents/import",
        "http://localhost:7071/chat",
        "tools/easy_mode_preflight.py --json",
        "Execute every locked case",
        "must_include",
        "must_not_include",
        "Use the plugin manager to push the Draft",
        "Run every",
    ):
        assert marker.lower() in text.lower()
    assert "published: false" in text
    assert "Never publish" in text
    assert "Never ask the user to choose an engine" in text


@pytest.mark.parametrize("name", ["brainstem", "copilot"])
def test_old_skill_names_remain_aliases(name):
    text = (ROOT / f"skills/aibast-easy-mode-{name}/SKILL.md").read_text()
    assert text.startswith(f"---\nname: aibast-easy-mode-{name}\n")
    assert f"https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/{SKILL_PATH}" in text
    assert "This file is an alias of `aibast-easy-mode`" in text
    if name == "copilot":
        assert "brainstem" not in text.lower()


@pytest.mark.parametrize("deployment", PACKAGES, ids=lambda path: path.parent.name)
def test_every_workshop_has_one_guide_and_one_learning_path(deployment):
    package = deployment.parent
    guide = (package / "EASY-MODE.md").read_text()
    assert SKILL_PATH in guide
    assert "aibast-easy-mode" in guide
    assert re.search(r"Give me .+ using Easy Mode and test it for me\.", guide)
    assert "Deploy it into Copilot Studio for me." in guide
    assert "published: false" in guide
    for name in ("EASY-MODE-PERSONLESS.md", "EASY-MODE-COPILOT-CHAT.md"):
        alias = (package / name).read_text()
        assert "[EASY-MODE.md](EASY-MODE.md)" in alias
        assert 3 <= len(alias.splitlines()) <= 6
        assert re.search(r"Give me .+ using Easy Mode and test it for me\.", alias)
        assert "Deploy it into Copilot Studio for me." in alias
    quest = (package / "quest.html").read_text()
    assert "data-easy-lane" not in quest
    assert "engine-label" not in quest
    assert quest.count('download="SKILL.md"') == 1
    assert SKILL_PATH in quest
    assert 'data-achievements-path="easy"' in quest
