import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INTAKE_SKILL = ROOT / "skills" / "aibast-intake" / "SKILL.md"

BRIEF_HEADINGS = (
    "AIBAST USE CASE BRIEF",
    "Industry:",
    "The problem:",
    "Who has it (roles, rough headcount):",
    "What happens today:",
    "What a good result looks like:",
    "Systems and files involved (names only):",
    "Three things people would ask:",
    "Smallest useful first version:",
    "Rules and limits to respect:",
    "Other ideas:",
)


def _text():
    return INTAKE_SKILL.read_text(encoding="utf-8")


def test_skill_has_the_expected_name():
    assert _text().startswith("---\nname: aibast-intake\n")


def test_interview_is_exactly_five_questions():
    section = _text().split("## The five questions")[1].split("\n## ")[0]
    numbered = re.findall(r"^\d+\. \*\*", section, flags=re.MULTILINE)
    assert len(numbered) == 5


def test_brief_keeps_its_headings_in_order():
    brief = _text().split("## The brief")[1].split("```")[1]
    position = -1
    for heading in BRIEF_HEADINGS:
        found = brief.find(heading)
        assert found > position, heading
        position = found


def test_skill_keeps_private_information_out():
    text = _text()
    for marker in (
        "no\n   real names, records, passwords or confidential numbers",
        "Never ask for sign-in details, sample records or file uploads.",
        "do not repeat it",
    ):
        assert marker in text


def test_skill_only_interviews():
    text = _text()
    for marker in (
        "Nothing is built, installed, downloaded or sent by you.",
        "Do not promise what will be built or when.",
        "Do not send the brief anywhere yourself",
        "The interview ends with the brief.",
    ):
        assert marker in text


def test_skill_needs_no_tooling_or_network():
    text = _text()
    for forbidden in ("http://", "https://", "curl ", "python", "localhost"):
        assert forbidden not in text, forbidden


def test_skill_stays_short_enough_to_paste():
    assert len(_text().splitlines()) <= 110
