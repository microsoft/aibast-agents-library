import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "aibast-meeting-prep" / "SKILL.md"
LIBRARY = "https://microsoft.github.io/aibast-agents-library/"

PACK_HEADINGS = (
    "MEETING PACK",
    "Closest example:",
    "Why it fits:",
    "Where it does not fit:",
    "Show this first (demo link):",
    "Three questions to type in the demo:",
    "Ask the customer:",
    "Suggested first version:",
    "Rules to respect:",
    "Leave-behind links:",
    "Also close:",
)


def _text():
    return SKILL.read_text(encoding="utf-8")


def test_skill_has_the_expected_name():
    assert _text().startswith("---\nname: aibast-meeting-prep\n")


def test_pack_keeps_its_headings_in_order():
    pack = _text().split("## The meeting pack")[1].split("```")[1]
    position = -1
    for heading in PACK_HEADINGS:
        found = pack.find(heading)
        assert found > position, heading
        position = found


def test_skill_only_opens_the_public_library():
    text = _text()
    addresses = set(re.findall(r"https://[^\s`)\"]+", text))
    assert addresses == {
        LIBRARY,
        LIBRARY + "api/v1/search.json",
        LIBRARY + "prepare.html",
    }
    for forbidden in ("http://", "curl ", "python", "localhost", "raw.githubusercontent"):
        assert forbidden not in text, forbidden
    assert "Never put any part of the customer's brief into a web address" in text


def test_every_record_field_the_skill_names_exists_in_the_library():
    text = _text()
    listing = json.loads((ROOT / "api" / "v1" / "search.json").read_text(encoding="utf-8"))["solutions"]
    assert listing and all("doc" in row and "name" in row for row in listing)
    named = set(re.findall(r"`((?:try|learn|notice)\.[a-z_]+)`", text))
    assert named == {"try.page", "try.scenarios", "learn.field_guide", "learn.workshop", "notice.text"}
    for row in listing:
        record = json.loads((ROOT / row["doc"]).read_text(encoding="utf-8"))
        for field in ("name", "summary", "capabilities"):
            assert field in record, (row["slug"], field)
        for path in named:
            outer, inner = path.split(".")
            assert inner in record[outer], (row["slug"], path)


def test_skill_points_people_without_a_brief_at_the_customer_page():
    assert (ROOT / "prepare.html").exists()
    assert LIBRARY + "prepare.html" in _text()


def test_skill_keeps_to_sample_data_and_makes_no_promises():
    text = _text()
    for marker in (
        "Nothing is built, installed or sent by you.",
        "Never invent a capability, a number, a customer or a date.",
        "Do not suggest connecting the example to the customer's real data.",
        "Do not promise what will be built, what it will cost or when.",
        "Do not force a match.",
    ):
        assert marker in text, marker


def test_skill_stays_short_enough_to_paste():
    assert len(_text().splitlines()) <= 140
