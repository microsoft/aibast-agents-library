"""The speed-barrier log stays honest and stays in step with the guide.

``state/speed_barriers.json`` is the record of what the platform used to cost and
what it costs now. It exists so the gain is measurable instead of remembered, and
so the original 2025 figures are never quietly overwritten. The guide renders the
same log in its Speed Barriers Broken section.

These tests hold three things:

* every barrier carries a then, a now and the evidence that it fell;
* the guide states every barrier the log claims, so the two cannot drift;
* the honest half survives — barriers that have not fallen stay listed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.design_tokens import strip_block  # noqa: E402

LOG = json.loads((ROOT / "state" / "speed_barriers.json").read_text(encoding="utf-8"))
GUIDE = strip_block((ROOT / "docs" / "rapp-guide.html").read_text(encoding="utf-8"))
SECTION = GUIDE[GUIDE.index('id="roadmap"') : GUIDE.index('id="tools"')]


def visible(html: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)


SECTION_TEXT = visible(SECTION)


def test_the_log_has_the_shape_the_guide_renders():
    assert LOG["schema"] == "aibast-speed-barriers/1.0"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", LOG["updated"])
    assert LOG["baseline"]["document"] == "docs/rapp-guide.html"
    assert LOG["barriers"], "an empty log is not a log"


def test_every_barrier_carries_then_now_and_evidence():
    seen: set[str] = set()
    for entry in LOG["barriers"]:
        where = entry.get("id", "?")
        assert re.fullmatch(r"[a-z0-9-]+", where), where
        assert where not in seen, f"duplicate barrier id {where}"
        seen.add(where)
        for field in ("barrier", "then", "now", "evidence", "broken"):
            assert entry.get(field, "").strip(), f"{where} is missing {field}"
        # A log entry records something that happened, not something planned.
        assert re.fullmatch(r"\d{4}", entry["broken"]), where
        forecast = re.search(r"\b(will|plan to|going to|roadmap|soon)\b", entry["now"], re.I)
        assert not forecast, f"{where}: 'now' reads as a forecast, not a measurement"


def test_the_guide_states_every_barrier_in_the_log():
    missing = [e["barrier"] for e in LOG["barriers"] if e["barrier"].lower() not in SECTION_TEXT.lower()]
    assert not missing, f"the guide's Speed Barriers section does not mention: {missing}"


def test_the_guide_keeps_the_original_figures_rather_than_overwriting_them():
    # The whole point is that the old numbers survive as the baseline.
    for phrase in ("2-3 weeks", "3-5 days", "3-5 weeks"):
        assert phrase in SECTION_TEXT, f"the {phrase} baseline is no longer recorded in the guide"
    assert "Speed Barriers Broken" in visible(GUIDE)


def test_what_has_not_improved_is_still_listed():
    assert LOG["still_standing"], "a log that only records wins is marketing"
    for entry in LOG["still_standing"]:
        for field in ("barrier", "cost", "note"):
            assert entry.get(field, "").strip(), entry
    # Security and compliance is the longest pole in the guide and has not moved.
    assert any("security" in e["barrier"].lower() for e in LOG["still_standing"])


def test_the_log_carries_no_customer_or_internal_identifiers():
    blob = json.dumps(LOG).lower()
    for banned in ("spur", "juke", "acv", "@microsoft.com", "headcount"):
        assert banned not in blob, f"{banned!r} does not belong in a public log"


def test_the_guide_section_is_free_of_the_internal_content_it_replaced():
    lowered = SECTION_TEXT.lower()
    for banned in ("spur", "juke room", "2tb", "external drive", "procurement"):
        assert banned not in lowered, f"{banned!r} survived in the published roadmap section"
