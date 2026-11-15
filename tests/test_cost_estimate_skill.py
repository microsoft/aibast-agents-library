import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "aibast-cost-estimate" / "SKILL.md"
RATES = ROOT / "api" / "v1" / "public" / "copilot-credit-rates.json"
RATES_URL = "https://microsoft.github.io/aibast-agents-library/api/v1/public/copilot-credit-rates.json"


def _text():
    return SKILL.read_text(encoding="utf-8")


def test_skill_has_the_expected_name():
    assert _text().startswith("---\nname: aibast-cost-estimate\n")


def test_skill_opens_only_the_public_rates():
    text = _text()
    assert set(re.findall(r"https://[^\s`)\"]+", text)) == {RATES_URL}
    assert "Never put anything the person tells you into a web address" in text


def test_every_rate_field_the_skill_names_exists():
    rates = json.loads(RATES.read_text(encoding="utf-8"))
    named = set(re.findall(r"`((?:data|units|provenance)\.[A-Za-z_]+)`", _text()))
    assert named == {
        "data.otherKnowledge",
        "data.toolInvocation",
        "data.tenantGraphGrounding",
        "units.credit_usd",
        "provenance.page",
    }
    for path in named:
        outer, inner = path.split(".")
        assert rates[outer][inner], path
    assert "Not a price quote" in rates["disclaimer"]


def test_skill_carries_no_rate_of_its_own():
    body = _text().split("## Work it out")[0]
    assert not re.search(r"\b\d+(\.\d+)?\s*credits?\b", body)
    assert "$0" not in _text() and "0.01" not in _text()


def test_skill_is_an_estimate_and_never_a_quote():
    text = _text()
    for marker in (
        "PLANNING ESTIMATE (not a price quote)",
        "Never use a rate from\nmemory, and never invent one.",
        "Never\nguess a number for them.",
        "Do not give one single number. Always show the three rows.",
        "Do not advise on licences, discounts or agreements.",
        "Do not compare with other vendors.",
        "Your Microsoft contact\n  confirms the real figure.",
    ):
        assert marker in text, marker


def test_skill_stays_short_enough_to_paste():
    assert len(_text().splitlines()) <= 110
