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
GUIDE = ROOT / "solutions/time-entry-billing/field-guide.html"
QUEST = ROOT / "solutions/time-entry-billing/quest.html"


def test_prominent_field_guide_navigation_uses_styled_html():
    quest = QUEST.read_text(encoding="utf-8")
    guide = GUIDE.read_text(encoding="utf-8")
    assert 'href="field-guide.html"' in quest
    assert 'href="FIELD-GUIDE.md"' not in quest
    assert THEME_SCRIPT in guide
    assert WORKSHOP_ENGINE_SCRIPT in guide
    assert THEME_VARIABLES in guide
    assert DARK_THEME_VARIABLES in guide
    assert "Facilitator and learner guide" in guide
    assert "Locked Preview corpus" in guide
    assert "Production replacement seams" in guide
    assert "Evidence gates" in guide
    assert "Failure recovery" in guide
    assert "Back to workshop" in guide


def test_field_guide_scripts_parse(tmp_path):
    text = GUIDE.read_text(encoding="utf-8")
    scripts = re.findall(r"<script>(.*?)</script>", text, re.DOTALL)
    assert scripts
    for index, script in enumerate(scripts):
        path = tmp_path / f"field-guide-{index}.js"
        path.write_text(script, encoding="utf-8")
        result = subprocess.run(
            ["node", "--check", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
