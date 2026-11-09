import re
import subprocess
import json
from pathlib import Path

from tools.scaffold_solution_journey import (
    THEME_PREFERENCE_SCRIPT,
    THEME_SCRIPT,
    WORKSHOP_ENGINE_SCRIPT,
)
from tools.design_tokens import local_palette_declarations, render_tokens


ROOT = Path(__file__).resolve().parent.parent
SETTINGS = ROOT / "solutions/_shared/workshop-settings.html"
QUEST = ROOT / "solutions/time-entry-billing/quest.html"
MANUAL = ROOT / "solutions/time-entry-billing/manual-tutorial.html"


def test_global_workshop_settings_explain_one_mode_without_controls():
    text = SETTINGS.read_text(encoding="utf-8")
    assert THEME_SCRIPT in text
    assert THEME_PREFERENCE_SCRIPT in text
    # The palette arrives through the stamped block only (tools/design_tokens.py).
    assert render_tokens() in text
    assert not local_palette_declarations(text)
    assert 'const key = "aibast:workshop-engine"' in text
    assert "There is one mode now and nothing to choose." in text
    assert 'type="radio"' not in text
    assert 'name="engine"' not in text
    assert "localStorage.getItem(key)" in text
    settings_script = re.findall(r"<script>(.*?)</script>", text, re.DOTALL)[-1]
    assert "localStorage.setItem" not in settings_script
    assert 'const theme = explicit || stored || "light"' in text
    assert "data-theme-toggle" in text


def run_settings_script(tmp_path, return_value, saved_value="copilot", denied=False):
    text = SETTINGS.read_text(encoding="utf-8")
    script = re.findall(r"<script>(.*?)</script>", text, re.DOTALL)[-1]
    location = (
        "https://example.test/solutions/_shared/workshop-settings.html"
        f"?return={return_value}"
    )
    harness = f"""
const assigned = [];
global.window = {{
  location: {{
    href: {json.dumps(location)},
    origin: "https://example.test",
    search: new URL({json.dumps(location)}).search,
    assign: (value) => assigned.push(value),
  }},
}};
const listeners = {{}};
const form = {{
  elements: {{ engine: {{ value: "" }} }},
  addEventListener: (name, callback) => listeners[name] = callback,
}};
const back = {{ href: "" }};
global.document = {{
  getElementById: (id) => id === "settings-form" ? form : back,
}};
const stored = {{ "aibast:workshop-engine": {json.dumps(saved_value)} }};
global.localStorage = {{
  getItem: (key) => {{
    if ({json.dumps(denied)}) throw new Error("storage denied");
    return stored[key] || null;
  }},
  setItem: (key, value) => stored[key] = value,
}};
{script}
console.log(JSON.stringify({{
  href: back.href,
  stored: stored["aibast:workshop-engine"],
  listenerCount: Object.keys(listeners).length,
}}));
"""
    script_path = tmp_path / "workshop-settings-harness.js"
    script_path.write_text(harness, encoding="utf-8")
    result = subprocess.run(
        ["node", str(script_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_workshop_settings_accept_valid_relative_return_and_ignore_old_preferences(tmp_path):
    result = run_settings_script(tmp_path, "..%2Ftime-entry-billing%2Fquest.html")
    expected = "https://example.test/solutions/time-entry-billing/quest.html"
    assert result == {
        "href": expected,
        "stored": "copilot",
        "listenerCount": 0,
    }


def test_workshop_settings_reject_hostile_returns(tmp_path):
    fallback = "https://example.test/library.html"
    for value in (
        "javascript%3Aalert(1)",
        "data%3Atext%2Fhtml%2Cbad",
        "%2F%2Fevil.example%2Fpath",
        "https%3A%2F%2Fevil.example%2Fpath",
        "http%3A%2F%2F%5Binvalid",
    ):
        result = run_settings_script(tmp_path, value)
        assert result["href"] == fallback
        assert result["stored"] == "copilot"
        assert result["listenerCount"] == 0


def test_workshop_settings_tolerate_all_saved_values_and_denied_storage(tmp_path):
    for saved in (None, "copilot", "brainstem", "invalid"):
        for denied in (False, True):
            result = run_settings_script(tmp_path, "", saved, denied)
            assert result["href"] == "https://example.test/library.html"
            assert result["stored"] == saved
            assert result["listenerCount"] == 0


def test_quest_renders_only_the_global_engine_and_links_settings():
    text = QUEST.read_text(encoding="utf-8")
    assert WORKSHOP_ENGINE_SCRIPT in text
    assert "aibast:workshop-engine" in text
    assert "data-easy-lane-button" not in text
    assert "Choose your Easy-mode lane" not in text
    assert "Compare and contrast while you build" not in text
    assert "Workshop settings" in text
    assert "workshop-settings.html" in text
    assert "data-workshop-engine=" not in text
    assert "data-easy-lane" not in text
    assert "engine-label" not in text
    assert text.count('download="SKILL.md"') == 1
    assert "Default to the Brainstem" not in text


def test_hard_mode_renders_the_complete_manual_tutorial_natively():
    quest = QUEST.read_text(encoding="utf-8")
    manual = MANUAL.read_text(encoding="utf-8")
    assert "<iframe" not in quest
    assert 'class="path" data-path="hard"' in quest
    assert "Build and verify" in quest
    assert quest.count('<article class="step"') == manual.count(
        '<article class="step"'
    )
    assert "manual-progress" in quest
    assert "manual-progress" in manual
    assert "updateHardProgress" in quest
    for token in ("aibast-hard-mode-height", "data-embedded", "postMessage"):
        assert token not in quest
        assert token not in manual
    assert "Open standalone Manual-mode guide" in quest


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
