"""Every solution count a reader sees agrees with the data behind it.

The catalog page renders one card per name in ``solutions/catalog.json`` and
shows ``registry.json`` ``stats.advertised_solutions`` as its headline. When the
two rules differ, the header says one number and the grid shows another. Pages
that state a count by hand (the README, the field notes, the RAPP guide) drift
the same way each time a solution ships. These tests fail on either drift.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


REGISTRY = _load("registry.json")
STATS = REGISTRY["stats"]
CATALOG = _load("solutions/catalog.json")["solutions"]
LISTINGS = _load("solutions.json")["solutions"]
ACADEMY = _load("academy.json")
AGENTS = {agent["name"]: agent for agent in REGISTRY["agents"]}
SOLUTIONS = len(CATALOG)


def test_header_count_equals_the_cards_the_page_renders():
    # index.html renders a card per catalog name and puts
    # stats.advertised_solutions in the header.
    assert STATS["advertised_solutions"] == SOLUTIONS


def test_every_count_source_names_the_same_solutions():
    slotted = [
        row["repo_agent"]
        for row in LISTINGS
        if row.get("is_primary") and row.get("slot") is not None
    ]
    assert sorted(slotted) == sorted(CATALOG)
    assert sorted(course["agent"] for course in ACADEMY["courses"]) == sorted(CATALOG)
    assert ACADEMY["summary"]["courses"] == SOLUTIONS


def test_a_listing_outside_the_catalog_is_not_counted():
    # A solutions.json listing with no slot and no catalog entry stays on the
    # agent but must not move the headline.
    unlisted = [
        name
        for name, agent in AGENTS.items()
        if agent.get("_solution") and name not in CATALOG
    ]
    counted = sum(1 for agent in AGENTS.values() if agent.get("_solution"))
    assert STATS["advertised_solutions"] == counted - len(unlisted)


def test_industry_tiles_add_up_to_the_header_and_match_the_academy():
    tiles = Counter(AGENTS[name]["category"] for name in CATALOG)
    assert sum(tiles.values()) == STATS["advertised_solutions"]
    courses = Counter(
        AGENTS[course["agent"]]["category"] for course in ACADEMY["courses"]
    )
    assert tiles == courses


def test_slide_one_pager_and_demo_stats_count_only_advertised_solutions():
    advertised = [AGENTS[name]["_solution"] for name in CATALOG]
    assert STATS["source_verified_solutions"] == sum(
        bool(s.get("source_verified")) for s in advertised
    )
    assert STATS["solution_onepagers"] == sum(
        bool(s.get("has_onepager")) for s in advertised
    )
    assert STATS["solution_demo_videos"] == sum(
        bool(s.get("has_demo_video")) for s in advertised
    )


def _numbers(pattern: str, text: str) -> list[int]:
    found = [int(value) for value in re.findall(pattern, text)]
    assert found, f"stated count not found: {pattern}"
    return found


def test_readme_states_the_real_workshop_count():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert _numbers(r"\*\*(\d+) certified workshops\*\*", text) == [SOLUTIONS]


def test_field_notes_state_the_real_counts():
    notes = {
        note["id"]: note
        for topic in _load("field-notes.json")["topics"]
        for note in topic["notes"]
    }
    workshop = notes["what-is-a-workshop"]["answer"]
    assert _numbers(r"There are (\d+) of them", workshop) == [SOLUTIONS]
    size = notes["how-big-is-this"]["answer"]
    assert _numbers(r"(\d+) agents", size) == [STATS["total_agents"]]
    assert _numbers(r"(\d+) published solutions", size) == [SOLUTIONS]
    assert _numbers(r"(\d+) industries", size) == [STATS["total_verticals"]]
    # Hand-written line counts go stale on every release; the metrics page
    # carries that number.
    assert not re.search(r"\d[\d,]* lines", size)


def test_every_field_note_states_the_real_agent_and_industry_counts():
    """No note may state a stale count, not only the two checked above."""
    notes = [note for topic in _load("field-notes.json")["topics"] for note in topic["notes"]]
    agent_note = next(n for n in notes if n["id"] == "what-is-an-agent")["answer"]
    assert _numbers(r"publishes (\d+) of them", agent_note) == [STATS["total_agents"]]
    for note in notes:
        text = note.get("question", "") + " " + note["answer"]
        for value in re.findall(r"(\d+) industries", text):
            assert int(value) == STATS["total_verticals"], (note["id"], value)
        for value in re.findall(r"(\d+) agents\b", text):
            assert int(value) == STATS["total_agents"], (note["id"], value)


def _guide_text_before_tools() -> str:
    text = (ROOT / "docs" / "rapp-guide.html").read_text(encoding="utf-8")
    end = text.index('id="tools"')
    return text[:end]


def test_rapp_guide_states_the_real_solution_counts():
    guide = _guide_text_before_tools()
    single_file = sum(
        1
        for name in CATALOG
        for stack in REGISTRY["stacks"]
        if stack["stack"] == AGENTS[name]["_stack"]
        and stack["vertical"] == AGENTS[name]["_stack_vertical"]
        and stack["agent_count"] == 1
    )
    shape = re.findall(r"the shape (\d+) of the (\d+) published solutions use", guide)
    assert shape == [(str(single_file), str(SOLUTIONS))]
    assert _numbers(r"library of (\d+) published patterns", guide) == [SOLUTIONS]
    assert _numbers(r"<td>(\d+) published solutions", guide) == [SOLUTIONS]
    # The Speed Barriers row states the same split, not "each a single-file agent".
    assert "each a single-file agent" not in guide
    row = re.findall(
        r"<td>(\d+) published solutions, (\d+) of them single-file agents", guide
    )
    assert row == [(str(SOLUTIONS), str(single_file))]
    assert _numbers(r"every published workshop, (\d+) of them today", guide) == [SOLUTIONS]
    shipped = re.findall(
        r"(\d+) solutions, (\d+) published one-pagers, (\d+) filmed demos", guide
    )
    assert shipped == [
        (
            str(SOLUTIONS),
            str(STATS["solution_onepagers"]),
            str(STATS["solution_demo_videos"]),
        )
    ]
    academy = re.findall(
        r"(\d+) complete workshops and a (\d+)-course Academy with (\d+) uploadable skills",
        guide,
    )
    assert academy == [
        (
            str(SOLUTIONS),
            str(ACADEMY["summary"]["courses"]),
            str(ACADEMY["summary"]["skills"]),
        )
    ]


# --- The metrics page and every other page that states a solution count -----

import shutil
import subprocess
import sys

import pytest

METRICS = _load("state/metrics.json")

# Pages a reader opens that may state a solution count by hand. The RAPP guide
# is checked above, phrase by phrase, and is excluded here.
COUNTED_PAGES = sorted(
    {
        ROOT / "index.html",
        ROOT / "metrics.html",
        ROOT / "README.md",
        ROOT / "why.html",
        *(ROOT / "docs").glob("*.html"),
    }
    - {ROOT / "docs" / "rapp-guide.html"}
)

# A number followed by a noun that means "solution in the library".
SOLUTION_COUNT = re.compile(
    r"(?<![\w#&.-])(\d{2,3})\+?\s+"
    r"(?:(?:published|certified|complete|catalog-advertised|advertised|ready-to-deploy|deployable)\s+)*"
    r"(?:solutions?|workshops?|workshop quests|use cases)\b",
    re.IGNORECASE,
)


def test_metrics_snapshot_states_the_catalog_solution_count():
    # The metrics page links "N solutions in the library" to the catalog, so it
    # needs the catalog's own number, not the stack total (which also counts a
    # stack the catalog does not render).
    assert METRICS["totals"]["solutions"] == SOLUTIONS


def test_metrics_builder_counts_the_catalog_solutions(tmp_path):
    out = tmp_path / "metrics.json"
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_metrics.py"), "--offline", "--out", str(out)],
        capture_output=True, text=True, timeout=180, cwd=str(ROOT),
    )
    assert result.returncode == 0, result.stderr[:800]
    totals = json.loads(out.read_text(encoding="utf-8"))["totals"]
    assert totals["solutions"] == SOLUTIONS == STATS["advertised_solutions"]


def _render_stack_hint(snapshot: dict) -> str:
    """Run the page's own renderStacks() against a snapshot and return the hint."""
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed")
    html = (ROOT / "metrics.html").read_text(encoding="utf-8")
    start = html.index("function renderStacks()")
    end = html.index("\nfunction ", start + 1)
    script = """
const M = %s;
const els = {};
const $ = id => (els[id] = els[id] || { innerHTML: '', textContent: '' });
const num = v => (v === null || v === undefined) ? '-' : Number(v).toLocaleString('en-US');
const esc = s => String(s);
const pretty = s => String(s);
const OWNER = 'o', REPO = 'r';
%s
renderStacks();
process.stdout.write(els['stack-hint'].innerHTML || els['stack-hint'].textContent);
""" % (json.dumps(snapshot), html[start:end])
    result = subprocess.run(
        [node, "-"], input=script, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr[:800]
    return result.stdout


def test_metrics_library_link_states_the_number_the_catalog_shows():
    hint = _render_stack_hint(METRICS)
    link = re.search(r'<a href="library.html">([^<]*)</a>', hint)
    assert link, hint
    assert [int(n.replace(",", "")) for n in re.findall(r"[\d,]+", link.group(1))] == [SOLUTIONS], hint


def test_metrics_library_link_follows_the_data_not_a_literal():
    # Change the data; the page must follow it.
    snapshot = json.loads(json.dumps(METRICS))
    snapshot["totals"]["solutions"] = 41
    snapshot["totals"]["stacks"] = 45
    hint = _render_stack_hint(snapshot)
    link = re.search(r'<a href="library.html">([^<]*)</a>', hint)
    assert link and re.findall(r"\d+", link.group(1)) == ["41"], hint


@pytest.mark.parametrize("page", COUNTED_PAGES, ids=lambda p: str(p.relative_to(ROOT)))
def test_no_page_states_a_solution_count_the_data_disagrees_with(page):
    text = page.read_text(encoding="utf-8")
    stale = [
        (m.group(0), text.count("\n", 0, m.start()) + 1)
        for m in SOLUTION_COUNT.finditer(text)
        if int(m.group(1)) != SOLUTIONS
    ]
    assert not stale, f"{page.name} states a count that is not {SOLUTIONS}: {stale}"
