import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "aibast-business-case" / "SKILL.md"

HEADINGS = (
    "BUSINESS CASE:",
    "The problem:",
    "Who it affects:",
    "What it costs today:",
    "What a good result looks like:",
    "The first version we propose:",
    "What we need from you:",
    "What this is not:",
    "How we will know it worked:",
    "Open questions:",
)


def _text():
    return SKILL.read_text(encoding="utf-8")


def test_skill_has_the_expected_name():
    assert _text().startswith("---\nname: aibast-business-case\n")


def test_page_keeps_its_headings_in_order():
    page = _text().split("## Write the page")[1].split("```")[1]
    position = -1
    for heading in HEADINGS:
        found = page.find(heading)
        assert found > position, heading
        position = found


def test_skill_opens_no_address_at_all():
    text = _text()
    assert not re.search(r"https?://", text)
    assert "You open no web addresses and you\nsend nothing anywhere." in text


def test_skill_uses_only_the_persons_numbers():
    text = _text()
    for marker in (
        "Never fill in a number for them.",
        "Do not turn hours into money unless the person gives the hourly figure.",
        "Do not invent a saving, a percentage, a return or a payback period.",
        "Do not give a price, a licence cost or a date.",
        "Every number above came from you. Check them before you send this.",
        "It is not connected to our systems and changes no records.",
    ):
        assert marker in text, marker


def test_skill_stays_short_enough_to_paste():
    assert len(_text().splitlines()) <= 110
