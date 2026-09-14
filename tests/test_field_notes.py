"""Frontier Field Notes stays useful to someone who knows nothing yet.

``field-notes.json`` is the teaching content and ``blog.html`` renders it. The
page exists because the catalog is legible only to people who already know what
an agent is. These tests hold the things that would quietly undo that:

* every link a reader is invited to follow actually resolves;
* the featured workshop is a real, complete workshop, not a nice idea;
* each note answers a question rather than announcing a topic;
* the three engineering posts that were already written survive untouched.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.design_tokens import strip_block  # noqa: E402

NOTES = json.loads((ROOT / "field-notes.json").read_text(encoding="utf-8"))
PAGE = (ROOT / "blog.html").read_text(encoding="utf-8")
BODY = strip_block(PAGE)
SCRIPT = re.search(r"<script>\n\(\(\) => \{.*?\}\)\(\);\n</script>", BODY, re.DOTALL)
ROLLOUT = json.loads((ROOT / "state" / "solution_rollout.json").read_text(encoding="utf-8"))


def every_link():
    featured = NOTES["featured_workshop"]
    yield featured["href"]
    for item in featured["evidence"]:
        yield item["href"]
    for topic in NOTES["topics"]:
        for note in topic["notes"]:
            if note.get("link"):
                yield note["link"]["href"]


def test_the_notes_have_the_shape_the_page_renders():
    assert NOTES["schema"] == "aibast-field-notes/1.0"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", NOTES["updated"])
    assert NOTES["title"] == "Frontier Field Notes"
    assert NOTES["topics"], "a page of notes needs notes"
    # Workshops come first: that is the entry point for a general reader.
    assert NOTES["topics"][0]["id"] == "workshops"


def test_every_link_a_reader_is_invited_to_follow_resolves():
    missing = []
    for href in every_link():
        if href.startswith("http"):
            continue
        target = ROOT / href.split("?")[0].split("#")[0]
        if not target.exists():
            missing.append(href)
    assert not missing, f"dead links in field-notes.json: {missing}"


def test_the_featured_workshop_is_a_real_complete_workshop():
    featured = NOTES["featured_workshop"]
    slug = featured["slug"]
    record = next((s for s in ROLLOUT["solutions"] if s["slug"] == slug), None)
    assert record, f"{slug} is not a published solution"
    assert record["complete"], f"{slug} is not complete; do not feature it"
    assert featured["href"] == f"solutions/{slug}/quest.html"
    assert re.fullmatch(r"[A-Z][a-z]+ \d{4}", featured["month"]), featured["month"]


def test_the_featured_workshop_answers_all_four_questions():
    featured = NOTES["featured_workshop"]
    for field in ("who", "what", "where", "why", "summary"):
        value = featured.get(field, "")
        assert len(value.split()) >= 20, f"featured.{field} is too thin to teach anything"


def test_each_note_asks_a_question_and_answers_it():
    seen: set[str] = set()
    for topic in NOTES["topics"]:
        assert re.fullmatch(r"[a-z0-9-]+", topic["id"]), topic["id"]
        assert topic["notes"], f"{topic['id']} has no notes"
        for note in topic["notes"]:
            where = note.get("id", "?")
            assert where not in seen, f"duplicate note id {where}"
            seen.add(where)
            assert note["question"].endswith("?"), f"{where}: the heading is not a question"
            assert len(note["answer"].split()) >= 25, f"{where}: the answer is too short to teach"
            assert note.get("takeaway", "").strip(), f"{where} has no takeaway"


def test_the_notes_avoid_unexplained_jargon():
    # A reader who has never built an agent has to survive the first screen.
    blob = " ".join(
        note["answer"] + " " + note["question"]
        for topic in NOTES["topics"]
        for note in topic["notes"]
    ).lower()
    for term in ("rapp/1", "hippocampus", "dataverse", "connection reference", "orchestrator"):
        assert term not in blob, f"{term!r} needs defining before it can be used here"


def test_the_engineering_posts_that_were_already_written_survive():
    kept = subprocess.run(
        ["git", "show", "HEAD:blog.html"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    for title in (
        "How a Background Thread Silently Ate Your Login",
        "Why We Killed Remote Agents (For Now)",
        "Version Tracking with a Plain Text File",
    ):
        assert f"<h2>{title}</h2>" in kept, f"{title} is not in the committed baseline"
        assert f"<h2>{title}</h2>" in BODY, f"{title} was dropped from the page"
    assert BODY.count('<div class="post">') == 3


def test_the_page_renders_the_notes_rather_than_duplicating_them():
    assert SCRIPT, "render script missing"
    source = SCRIPT.group(0)
    assert 'fetch("field-notes.json"' in source
    # None of the note prose may be hardcoded into the page.
    for topic in NOTES["topics"]:
        for note in topic["notes"]:
            assert note["answer"][:40] not in BODY, f"{note['id']} is duplicated into the markup"
    assert 'id="under-the-hood"' in BODY
    assert NOTES["deep_dives"]["id"] == "under-the-hood"


def test_the_page_escapes_what_it_renders():
    source = SCRIPT.group(0)
    assert "const esc = (value)" in source
    assert "innerHTML" in source
    # Only markup-building lines matter. Anything assigned through textContent
    # or handed to Error() is inert text by construction.
    markup = "\n".join(
        line for line in source.splitlines()
        if "textContent" not in line and "new Error(" not in line
    )
    leaked = re.findall(r"\$\{(?!esc\()([a-z]\w*(?:\.\w+)*)\}", markup)
    assert not leaked, f"unescaped interpolation into markup: {leaked}"


def test_the_page_uses_tokens_rather_than_hardcoded_colour():
    style = BODY[BODY.rindex("<style>") : BODY.index("</style>", BODY.rindex("<style>"))]
    literals = re.findall(r"#[0-9a-fA-F]{3,8}\b|\brgba?\([^)]*\)", style)
    assert not literals, f"blog.html hardcodes colours: {literals}"


def test_no_emoji_reaches_the_reader():
    for blob, where in ((json.dumps(NOTES, ensure_ascii=False), "field-notes.json"), (BODY, "blog.html")):
        stray = [c for c in blob if 0x1F300 <= ord(c) <= 0x1FAFF]
        assert not stray, f"{where} carries emoji: {stray}"


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required to parse the script")
def test_the_render_script_is_valid_javascript(tmp_path):
    script = tmp_path / "notes.js"
    script.write_text(SCRIPT.group(0)[len("<script>") : -len("</script>")], encoding="utf-8")
    result = subprocess.run(["node", "--check", str(script)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
