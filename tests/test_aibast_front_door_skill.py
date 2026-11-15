import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "aibast" / "SKILL.md"
LIBRARY = "https://microsoft.github.io/aibast-agents-library/"
NINE = {
    "aibast-intake", "aibast-meeting-prep", "aibast-cost-estimate",
    "aibast-business-case", "aibast-industry-shortlist", "aibast-meeting-follow-up",
    "aibast-pilot-scorecard", "aibast-demo-rehearsal", "aibast-it-answer-pack",
}


def _text():
    return SKILL.read_text(encoding="utf-8")


def test_skill_has_the_expected_name():
    assert _text().startswith("---\nname: aibast\n")


def test_every_named_skill_exists_and_the_menus_cover_all_nine():
    text = _text()
    named = set(re.findall(r"\baibast-[a-z-]+[a-z]", text)) - {"aibast-agents-library"}
    for name in named:
        assert (ROOT / "skills" / name / "SKILL.md").exists(), name
    menus = text.split("## Menus")[1].split("## Run the skill")[0]
    assert set(re.findall(r"→ (aibast-[a-z-]+)", menus)) == NINE


def test_skill_only_opens_library_addresses():
    for url in re.findall(r"https://[^\s`)\"]+", _text()):
        assert url.startswith(LIBRARY), url
    for forbidden in ("http://", "raw.githubusercontent", "kody-w", "localhost"):
        assert forbidden not in _text(), forbidden


def test_skill_offers_one_next_step_and_keeps_the_rules():
    text = _text()
    for marker in (
        "or stop here",
        "Offer only one next step at a time",
        "Never put anything the person typed into",
        "sample data only",
        "Do not promise what will be built",
        "Do not name competitors",
        "Nothing is sent anywhere by you.",
        "Do not invent a skill.",
    ):
        assert marker in text, marker


def test_skill_stays_short():
    assert len(_text().splitlines()) <= 90
