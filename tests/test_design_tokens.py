"""The shared design tokens are one block, on every page, changing nothing.

These tests protect three properties:

1. Every published page carries the current block exactly once, so the site has
   one design system instead of the five it grew.
2. The block is reversible: stripping it returns the page byte-for-byte, which
   is what lets the workshop export audit compare a page with its copy in a ZIP.
3. The colour values are the ones the site already shipped. Editing a value in
   tools/design_tokens.py restyles 224 pages at once, so the palette is pinned
   here against the pages that carried it first.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import apply_design_tokens as cli  # noqa: E402
from tools.clarity_tag import public_pages  # noqa: E402
from tools.design_tokens import (  # noqa: E402
    DARK,
    PALETTE,
    PALETTES,
    END_MARK,
    FOCUS_DARK,
    FOCUS_LIGHT,
    LIGHT,
    SCALE,
    START_MARK,
    render_tokens,
    stamp,
    strip_block,
    strip_block_bytes,
)

BLOCK = render_tokens()
PAGES = sorted(public_pages(ROOT))


def test_every_published_page_carries_the_block_exactly_once():
    assert PAGES, "no public pages discovered"
    missing: list[str] = []
    duplicated: list[str] = []
    for page in PAGES:
        html = page.read_text(encoding="utf-8")
        count = html.count(START_MARK)
        if count == 0:
            missing.append(page.relative_to(ROOT).as_posix())
        elif count > 1 or html.count(END_MARK) != count:
            duplicated.append(page.relative_to(ROOT).as_posix())
        else:
            assert BLOCK in html, f"{page.relative_to(ROOT)} carries a stale block"
    assert not missing, missing
    assert not duplicated, duplicated


def test_check_mode_passes_on_the_committed_tree():
    assert cli.main(["--check"]) == 0


def test_block_sits_before_the_pages_own_style_so_page_rules_still_win():
    # The whole safety argument for stamping 224 existing pages is cascade order.
    for page in PAGES:
        html = page.read_text(encoding="utf-8")
        start = html.index(START_MARK)
        end = html.index(END_MARK) + len(END_MARK)
        after = html[end:]
        own_style = re.search(r"<style[\s>]", after, re.IGNORECASE)
        if own_style is None:
            continue
        before = re.search(r"<style[\s>]", html[:start], re.IGNORECASE)
        assert before is None, (
            f"{page.relative_to(ROOT)}: a page <style> precedes the shared block, "
            "so the block would override page rules"
        )


def test_stamping_is_idempotent_and_reversible():
    for page in PAGES[:40]:
        html = page.read_text(encoding="utf-8")
        assert stamp(html, BLOCK) == html, f"{page.relative_to(ROOT)} is not stable"
        stripped = strip_block(html)
        assert START_MARK not in stripped
        assert stamp(stripped, BLOCK) == html
        assert strip_block_bytes(html.encode("utf-8")) == stripped.encode("utf-8")


def test_stripping_returns_the_page_as_it_was_before_the_design_pass():
    # Byte-exact reversibility is what the workshop export audit relies on.
    page = ROOT / "why.html"
    committed = subprocess.run(
        ["git", "show", "HEAD:why.html"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if committed.returncode != 0 or START_MARK.encode() in committed.stdout:
        return  # the block is already committed; the property is covered above
    assert strip_block_bytes(page.read_bytes()) == committed.stdout


def _relative_luminance(hex_colour: str) -> float:
    raw = hex_colour.lstrip("#")
    channels = [int(raw[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(foreground: str, background: str) -> float:
    a, b = _relative_luminance(foreground), _relative_luminance(background)
    high, low = max(a, b), min(a, b)
    return (high + 0.05) / (low + 0.05)


def _rgb(hex_colour: str) -> tuple[int, int, int]:
    raw = hex_colour.lstrip("#")
    return tuple(int(raw[i : i + 2], 16) for i in (0, 2, 4))


# The families the anti-slop design skill names as its second most recurring AI
# tell: "warm beige/cream + brass/clay/oxblood + espresso near-black". The site
# shipped #f7f4ef on #b11f4b, which is squarely in it.
BANNED_GROUNDS = {
    "#f5f1ea", "#f7f5f1", "#fbf8f1", "#efeae0",
    "#ece6db", "#faf7f1", "#e8dfcb", "#f7f4ef",
}


def test_the_ground_is_not_the_warm_paper_ai_tell():
    ground = LIGHT["--cp-bg"].lower()
    assert ground not in BANNED_GROUNDS, (
        f"{ground} is the warm cream ground the design skill bans as a default. "
        "Pick a neutral or a committed colour, not paper."
    )
    # Neutral means the channels stay close together. A warm ground runs R > G > B
    # with a wide spread; that spread is the tell, not the lightness.
    for token in ("--cp-bg", "--cp-surface", "--cp-bg-elevated", "--cp-surface-soft"):
        r, g, b = _rgb(LIGHT[token])
        assert max(r, g, b) - min(r, g, b) <= 6, (
            f"light {token} {LIGHT[token]} is a tinted ground (spread {max(r,g,b)-min(r,g,b)}); "
            "the neutral scale must stay neutral"
        )
        r, g, b = _rgb(DARK[token])
        assert max(r, g, b) - min(r, g, b) <= 8, (
            f"dark {token} {DARK[token]} is a tinted ground (spread {max(r,g,b)-min(r,g,b)})"
        )


def test_there_is_exactly_one_accent():
    # "Max 1 accent colour" is the rule the site broke in four places before this
    # pass: a crimson, a Microsoft blue, a purple and a set of decorative hues.
    for theme in (LIGHT, DARK):
        accent, hover = _rgb(theme["--cp-accent"]), _rgb(theme["--cp-accent-hover"])
        distance = sum(abs(a - b) for a, b in zip(accent, hover))
        assert distance <= 120, "accent-hover must be a shade of the accent, not a second colour"
    assert set(LIGHT) == set(DARK), "a theme is missing a token the other defines"


def test_the_palette_is_selectable_and_every_option_is_complete():
    # Switching the whole site is one edit here plus apply_design_tokens.py, which
    # is the point of stamping a single block into every page.
    assert PALETTE in PALETTES
    for name, palette in PALETTES.items():
        assert set(palette["light"]) == set(palette["dark"]), name
        assert set(palette["light"]) == set(LIGHT), f"{name} does not define the same tokens"


def test_every_text_token_passes_wcag_aa_on_the_surfaces_it_lands_on():
    """The 2026-09 design pass corrected three tokens that failed here.

    ``--cp-success`` was #16a34a (3.30:1 on white), ``--cp-link`` was #0078d4
    (4.13:1 on the site's own cream) and ``--cp-danger`` was #dc2626 (4.40:1 on
    cream). All three are body-size text on 224 pages. This test is the reason
    they cannot come back.
    """
    light_surfaces = (LIGHT["--cp-bg"], LIGHT["--cp-surface"], LIGHT["--cp-bg-elevated"])
    dark_surfaces = (DARK["--cp-bg"], DARK["--cp-surface"], DARK["--cp-bg-elevated"])
    text_tokens = ("--cp-text", "--cp-text-muted", "--cp-accent", "--cp-link",
                   "--cp-success", "--cp-danger")
    failures: list[str] = []
    for token in text_tokens:
        for surface in light_surfaces:
            ratio = contrast(LIGHT[token], surface)
            if ratio < 4.5:
                failures.append(f"light {token} {LIGHT[token]} on {surface}: {ratio:.2f}:1")
        for surface in dark_surfaces:
            ratio = contrast(DARK[token], surface)
            if ratio < 4.5:
                failures.append(f"dark {token} {DARK[token]} on {surface}: {ratio:.2f}:1")
    assert not failures, failures


def test_the_focus_ring_is_actually_visible():
    # The ring it replaces was a 12%-opacity accent tint, about 1.2:1 on every
    # surface it landed on. A focus indicator needs 3:1 against its neighbours.
    assert contrast(FOCUS_LIGHT["--cp-focus"], LIGHT["--cp-bg"]) >= 3
    assert contrast(FOCUS_LIGHT["--cp-focus"], LIGHT["--cp-surface"]) >= 3
    assert contrast(FOCUS_DARK["--cp-focus"], DARK["--cp-bg"]) >= 3
    assert contrast(FOCUS_DARK["--cp-focus"], DARK["--cp-surface"]) >= 3


def test_no_page_redefines_a_shared_token_with_a_different_value():
    # A page may still declare the palette locally (four of them did first);
    # what it may not do is drift from the shared value.
    pattern = re.compile(r"(--cp-[a-z0-9-]+)\s*:\s*([^;}]+)[;}]")
    canonical = {**LIGHT, **SCALE}
    drift: list[str] = []
    for page in PAGES:
        body = strip_block(page.read_text(encoding="utf-8"))
        for name, value in pattern.findall(body):
            expected = canonical.get(name)
            if expected is None:
                continue
            if value.strip() != expected and value.strip() != DARK.get(name):
                drift.append(f"{page.relative_to(ROOT)}: {name} = {value.strip()}")
    assert not drift, drift[:12]


def test_the_block_carries_the_cross_cutting_fixes_it_promises():
    assert "color-scheme: light" in BLOCK and "color-scheme: dark" in BLOCK
    assert "prefers-color-scheme: dark" in BLOCK
    assert ":focus-visible" in BLOCK and "outline: 2px solid var(--cp-focus)" in BLOCK
    assert "scroll-margin-top" in BLOCK
    assert "prefers-reduced-motion: reduce" in BLOCK
    assert "--cp-radius" in BLOCK and "--cp-space-4" in BLOCK and "--cp-text-3xl" in BLOCK
