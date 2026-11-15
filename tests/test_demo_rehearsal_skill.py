import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "aibast-demo-rehearsal" / "SKILL.md"


def _text():
    return SKILL.read_text(encoding="utf-8")


def test_skill_has_the_expected_name():
    assert _text().startswith("---\nname: aibast-demo-rehearsal\n")


def test_skill_opens_only_the_named_addresses():
    found = set(re.findall(r"https://[^\s`)\"]+", _text()))
    assert found == {'https://microsoft.github.io/aibast-agents-library/api/v1/search.json', 'https://microsoft.github.io/aibast-agents-library/'}


def test_every_record_field_the_skill_names_exists():
    named = set(re.findall(r"`((?:try|learn)\.[a-z_]+)`", _text()))
    assert named == {'try.page', 'try.scenarios'}
    for row in json.loads((ROOT / "api/v1/search.json").read_text(encoding="utf-8"))["solutions"]:
        record = json.loads((ROOT / row["doc"]).read_text(encoding="utf-8"))
        for path in named:
            outer, inner = path.split(".")
            assert inner in record[outer], (row["slug"], path)


def test_markers_and_length():
    text = _text()
    for marker in ['REHEARSAL NOTES', 'where `recorded` is true', 'Do not invent capabilities', 'Do not name competitors', 'sample data']:
        assert marker in text, marker
    assert len(text.splitlines()) <= 75
