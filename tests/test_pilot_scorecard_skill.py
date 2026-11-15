import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "aibast-pilot-scorecard" / "SKILL.md"


def _text():
    return SKILL.read_text(encoding="utf-8")


def test_skill_has_the_expected_name():
    assert _text().startswith("---\nname: aibast-pilot-scorecard\n")


def test_skill_opens_only_the_named_addresses():
    found = set(re.findall(r"https://[^\s`)\"]+", _text()))
    assert found == set()


def test_markers_and_length():
    text = _text()
    for marker in ['PILOT SCORECARD:', 'Never invent, estimate or average a number', 'Wait for the answers', 'Do not name competitors', 'Do not suggest connecting to real data']:
        assert marker in text, marker
    assert len(text.splitlines()) <= 75
