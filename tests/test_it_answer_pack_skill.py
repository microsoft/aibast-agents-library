import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "aibast-it-answer-pack" / "SKILL.md"


def _text():
    return SKILL.read_text(encoding="utf-8")


def test_skill_has_the_expected_name():
    assert _text().startswith("---\nname: aibast-it-answer-pack\n")


def test_skill_opens_only_the_named_addresses():
    found = set(re.findall(r"https://[^\s`)\"]+", _text()))
    assert found and all(u.startswith("https://learn.microsoft.com/en-us/") for u in found), found


def test_markers_and_length():
    text = _text()
    for marker in ['IT ANSWER PACK', 'Not covered by the public pages. Ask your Microsoft contact.', 'Never claim a certification', 'Never put customer text', 'Your Microsoft contact confirms anything for your agreement.']:
        assert marker in text, marker
    assert len(text.splitlines()) <= 100
