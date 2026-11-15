import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "aibast-industry-shortlist" / "SKILL.md"
LIBRARY = "https://microsoft.github.io/aibast-agents-library/"


def _text():
    return SKILL.read_text(encoding="utf-8")


def test_skill_has_the_expected_name():
    assert _text().startswith("---\nname: aibast-industry-shortlist\n")


def test_skill_opens_only_the_public_library():
    assert set(re.findall(r"https://[^\s`)\"]+", _text())) == {LIBRARY, LIBRARY + "api/v1/search.json"}
    assert "Never put anything the person tells you into a web address" in _text()


def test_every_field_the_skill_names_exists():
    rows = json.loads((ROOT / "api/v1/search.json").read_text(encoding="utf-8"))["solutions"]
    for row in rows:
        for field in ("name", "headline", "demo"):
            assert row.get(field), (row["slug"], field)
        assert isinstance(row["industries"], list) and isinstance(row["personas"], list)
    assert sum("Cross-Industry" in r["industries"] for r in rows) >= 3


def test_markers_and_length():
    text = _text()
    for marker in ("SHORTLIST:", "word for word", "sample data only", "Do not name competitors"):
        assert marker in text, marker
    assert len(text.splitlines()) <= 90
