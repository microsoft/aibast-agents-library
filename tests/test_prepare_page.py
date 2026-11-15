import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "prepare.html"
SKILL = ROOT / "skills" / "aibast-intake" / "SKILL.md"


def _page():
    return PAGE.read_text(encoding="utf-8")


def _flat(text):
    return re.sub(r"\s+", " ", text)


def test_page_writes_the_same_brief_as_the_skill():
    brief = SKILL.read_text(encoding="utf-8").split("## The brief")[1].split("```")[1]
    headings = [line.strip() for line in brief.splitlines() if line.strip()]
    page = _page()
    position = -1
    for heading in headings:
        label = heading.rstrip(":") if not heading[0].isdigit() else heading
        found = page.find('"' + label)
        assert found > position, heading
        position = found


def test_page_asks_the_skills_five_questions():
    page = _flat(_page())
    assert page.count("<section data-step=") == 6  # five questions and the brief
    for wording in (
        "the one task or problem you would most like help with",
        "What happens today, and what improvement would make this worth doing?",
        "Which systems or files hold the information this work depends on?",
        "If an AI helper for this task existed tomorrow, what are three things someone on your team would type into it?",
        "What is the smallest first version that would still help?",
    ):
        assert wording in page, wording
        assert wording in _flat(SKILL.read_text(encoding="utf-8")), wording


def test_page_keeps_what_people_type_on_the_page():
    page = _page()
    for forbidden in (
        "fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "sessionStorage",
        "document.cookie", "clarity", "<iframe", "mailto:", 'action="',
    ):
        assert forbidden not in page, forbidden
    assert "Nothing you type is stored or sent" in page
    assert "no real names, records, passwords or confidential numbers" in page


def test_page_points_at_the_skill_on_its_own_ring():
    page = _page()
    assert 'new URL("skills/aibast-intake/SKILL.md", location.href)' in page
    assert "raw.githubusercontent.com" not in page


def test_blank_answers_become_not_sure_yet():
    assert 'var NOT_SURE = "Not sure yet";' in _page()
