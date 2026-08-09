import re
import subprocess
from pathlib import Path

from tools.scaffold_solution_journey import (
    DARK_THEME_VARIABLES,
    THEME_SCRIPT,
    THEME_VARIABLES,
    WORKSHOP_ENGINE_SCRIPT,
)


ROOT = Path(__file__).resolve().parent.parent
SETTINGS = ROOT / "solutions/_shared/workshop-settings.html"
QUEST = ROOT / "solutions/time-entry-billing/quest.html"
MANUAL = ROOT / "solutions/time-entry-billing/manual-tutorial.html"


def test_global_workshop_settings_default_to_copilot_and_persist():
    text = SETTINGS.read_text(encoding="utf-8")
    assert THEME_SCRIPT in text
    assert THEME_VARIABLES in text
    assert DARK_THEME_VARIABLES in text
    assert 'const key = "aibast:workshop-engine"' in text
    assert '? "brainstem"' in text
    assert ': "copilot"' in text
    assert 'value="copilot"' in text
    assert 'value="brainstem"' in text
    assert "GitHub Copilot only" in text
    assert "GitHub Copilot + Brainstem" in text
    assert "applies to every AIBAST workshop" in text
    assert "localStorage.setItem(key" in text


def test_quest_renders_only_the_global_engine_and_links_settings():
    text = QUEST.read_text(encoding="utf-8")
    assert WORKSHOP_ENGINE_SCRIPT in text
    assert "aibast:workshop-engine" in text
    assert "data-easy-lane-button" not in text
    assert "Choose your Easy-mode lane" not in text
    assert "Compare and contrast while you build" not in text
    assert "Workshop settings" in text
    assert "workshop-settings.html" in text
    assert 'html[data-workshop-engine="copilot"]' in text
    assert 'html[data-workshop-engine="brainstem"]' in text
    assert 'data-easy-lane="copilot"' in text
    assert 'data-easy-lane="brainstem"' in text
    assert "Default to the Brainstem" not in text


def test_hard_mode_embeds_the_complete_manual_tutorial():
    quest = QUEST.read_text(encoding="utf-8")
    manual = MANUAL.read_text(encoding="utf-8")
    assert (
        'src="manual-tutorial.html?embedded=1"'
        in quest
    )
    assert 'id="hard-mode-tutorial"' in quest
    assert "aibast-hard-mode-height" in quest
    assert "aibast-hard-mode-height" in manual
    assert 'data-embedded", "true"' in manual
    assert 'html[data-embedded="true"] .topbar' in manual
    assert ">Open the manual tutorial<" not in quest


def test_new_html_scripts_parse(tmp_path):
    for path in (SETTINGS, QUEST, MANUAL):
        text = path.read_text(encoding="utf-8")
        scripts = re.findall(r"<script>(.*?)</script>", text, re.DOTALL)
        assert scripts
        for index, script in enumerate(scripts):
            script_path = tmp_path / f"{path.stem}-{index}.js"
            script_path.write_text(script, encoding="utf-8")
            result = subprocess.run(
                ["node", "--check", str(script_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0, result.stderr
