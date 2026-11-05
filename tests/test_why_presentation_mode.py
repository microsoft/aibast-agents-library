"""why.html presents from its own prose, and the prose stays the default.

The page is used two ways: read on the web, and flipped through in a meeting when
someone is sceptical. Both have to come from one source, or the talk track and
the page drift apart. These tests hold that line:

* the prose page is what a reader, a crawler and a browser without JavaScript get;
* the deck is built from the same sections at runtime, never duplicated markup;
* the keys a presenter reaches for are wired, and Escape gets out.
"""

from __future__ import annotations

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

PAGE = (ROOT / "why.html").read_text(encoding="utf-8")
BODY = strip_block(PAGE)
SCRIPT = re.search(
    r"/\* Presentation mode for why\.html\..*?\n\}\)\(\);", BODY, re.DOTALL
)
_style_start = BODY.index("/* ---- Presentation mode")
STYLE = BODY[_style_start : BODY.index("</style>", _style_start)]


def test_the_prose_page_is_the_default():
    # Nothing in the shipped markup turns the deck on: it is opt-in at runtime.
    # (data-present appears in the stylesheet as a selector; what must not exist
    # is the attribute on an element.)
    html_tag = re.search(r"<html[^>]*>", BODY).group(0)
    assert "data-present" not in html_tag, "the page must not ship with the deck on"
    body_tag = re.search(r"<body[^>]*>", BODY).group(0)
    assert "data-present" not in body_tag
    assert 'id="deck"' in BODY
    deck = re.search(r'<div class="deck" id="deck"[^>]*></div>', BODY)
    assert deck, "the deck container must ship empty, built only when opened"
    assert 'aria-hidden="true"' in deck.group(0), "an empty deck must be hidden from assistive tech"
    assert "<main>" in BODY and 'main aria-hidden' not in BODY


def test_there_are_two_ways_in_and_both_are_named():
    launch = re.search(r'<button class="present-launch"[^>]*>', BODY)
    assert launch, "no fixed Present control"
    assert 'aria-label="Open presentation mode"' in launch.group(0)
    assert 'id="present-action"' in BODY, "no Present control among the page's own actions"
    assert ">Present this</button>" in BODY


def test_slides_are_cloned_from_the_page_not_duplicated():
    assert SCRIPT, "presentation script missing"
    source = SCRIPT.group(0)
    assert "cloneNode(true)" in source, "slides must be cloned from <main>"
    assert 'querySelector("main")' in source
    # Every section heading appears exactly once in the file: in the prose.
    for heading in ("What it is not", "The graduation path", "Who it is for"):
        assert BODY.count(f"<h2>{heading}</h2>") == 1, f"{heading} is duplicated into the deck"


def test_the_presenter_keys_are_wired():
    source = SCRIPT.group(0)
    for key in ('"ArrowRight"', '"ArrowLeft"', '"Home"', '"End"', '"Escape"', '"PageDown"', '"PageUp"'):
        assert key in source, f"{key} is not handled"
    assert '"p" || event.key === "P"' in source, "P does not open the deck"
    assert "requestFullscreen" in source, "F does not go fullscreen"
    # Typing in a field must not flip slides.
    assert "INPUT|TEXTAREA|SELECT" in source
    assert "isContentEditable" in source


def test_a_slide_can_be_linked_straight_from_a_meeting_invite():
    source = SCRIPT.group(0)
    assert 'params.get("present") === "1"' in source
    assert 'params.get("slide")' in source
    assert 'url.searchParams.set("slide"' in source, "the current slide is not reflected in the URL"
    assert 'url.searchParams.delete("present")' in source, "leaving must clean the URL"


def test_the_deck_is_announced_and_focus_moves_with_it():
    source = SCRIPT.group(0)
    assert 'setAttribute("aria-roledescription", "slide")' in source
    assert 'aria-label' in source and '" of "' in source, "slides need a position in their name"
    assert 'aria-live="polite"' in source, "the counter must be announced"
    assert "focus({ preventScroll: true })" in source, "focus must follow the active slide"
    assert 'main.setAttribute("aria-hidden", "true")' in source, "the prose must leave the a11y tree"


def test_the_presentation_styles_use_tokens_only():
    assert STYLE, "presentation stylesheet missing"
    literals = re.findall(r"#[0-9a-fA-F]{3,8}\b|\brgba?\([^)]*\)", STYLE)
    assert not literals, f"presentation mode hardcodes colours: {literals}"
    assert "var(--cp-bg)" in STYLE
    # 100vh is the viewport unit that jumps on mobile Safari; the deck must not use it.
    assert "100vh" not in STYLE.replace("92vh", "")


def test_printing_the_deck_gives_one_slide_per_page():
    assert "@media print" in STYLE
    assert "page-break-after: always" in STYLE


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required to parse the script")
def test_the_presentation_script_is_valid_javascript(tmp_path):
    script = tmp_path / "present.js"
    script.write_text(SCRIPT.group(0), encoding="utf-8")
    result = subprocess.run(
        ["node", "--check", str(script)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
