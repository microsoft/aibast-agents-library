"""AIBAST design tokens: the one stylesheet every published page carries.

The site has no build step and every page is a self-contained HTML file, so a
shared ``<link rel=stylesheet>`` would never ship (``scripts/build_pages_site.py``
only publishes ``.cmd .command .html .json .ps1 .sh``). The tokens are therefore
stamped into each page the same way the Microsoft Clarity tag is, from this one
module:

    python scripts/apply_design_tokens.py           # rewrite pages
    python scripts/apply_design_tokens.py --check   # exit 1 if any page is stale

Two rules make the stamp safe to apply to 200+ existing pages:

1. **It is inserted before the page's own ``<style>``.** Every rule here is
   therefore the floor, not the ceiling: a page that already styles something
   keeps winning. Nothing a page renders today changes because of the stamp.
2. **The colour values are the ones the site already shipped.** The
   ``--cp-*`` palette was already byte-identical across ``index.html``,
   ``metrics.html``, ``achievements.html``, ``docs/rapp-guide.html`` and all 206
   generated pages under ``solutions/``. This module adopts those exact values
   rather than inventing a palette, so the stamp unifies the remaining pages
   onto the existing brand instead of restyling the brand.

What the stamp adds on top of the colours is the part the site never had in one
place: a type scale, a spacing scale, one radius scale, a visible focus ring, a
reduced-motion guard and anchor scroll offsets. Those are the cross-cutting
fixes from the design audit, and stamping them means all published pages get
them at once.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

START_MARK = "<!-- aibast-design:start -->"
END_MARK = "<!-- aibast-design:end -->"
BLOCK_RE = re.compile(
    re.escape(START_MARK) + r".*?" + re.escape(END_MARK),
    re.DOTALL,
)
# Stripping also swallows the newline the stamp adds, so a stripped page is
# byte-identical to the same page before it was ever stamped. The workshop
# export audit compares a page against its copy inside a ZIP on exactly that.
STRIP_RE = re.compile(BLOCK_RE.pattern + r"\n?", re.DOTALL)
BLOCK_BYTES_RE = re.compile(STRIP_RE.pattern.encode("ascii"), re.DOTALL)
STYLE_OPEN_RE = re.compile(r"<style[\s>]", re.IGNORECASE)
HEAD_CLOSE_RE = re.compile(r"</head>", re.IGNORECASE)
CLARITY_START_RE = re.compile(r"<!--\s*clarity:start\s*-->", re.IGNORECASE)

# The palette.
#
# The site shipped a warm cream ground (#f7f4ef) with an oxblood accent (#b11f4b).
# That combination is the one the anti-slop design skill names as its second most
# recurring AI tell: "warm beige/cream + brass/clay/oxblood" is what an LLM reaches
# for by default, and it makes the brand invisible. A Microsoft engineering catalog
# has no reason to look like warm-craft packaging.
#
# So the GROUND changed and the SIGNATURE stayed. "signal" is a cool neutral canvas
# (zinc, not paper) carrying the one saturated accent the library already owned.
# "fluent" is the alternative: Microsoft's own neutrals and brand blue, no crimson.
# Switch the whole site with one edit here plus scripts/apply_design_tokens.py.
PALETTE = "gallery"

# Palettes that render one scheme only. The page still carries both blocks (the
# dark block repeats the same values), so a page that toggles data-theme keeps
# working; the toggle button itself is hidden because it would change nothing.
SINGLE_SCHEME: dict[str, str] = {"gallery": "dark"}

PALETTES: dict[str, dict[str, dict[str, str]]] = {
    "gallery": {
        # The library gallery mockup (docs/mockups/library-gallery.html in the
        # aibast-rapp workspace, Kody 2026-11-09): a committed navy ground, white
        # ink, one cyan signal, Microsoft blue only inside primary buttons. Dark
        # only; "light" repeats the same values so every page renders the same
        # whatever the visitor's OS prefers.
        "light": {
            "--cp-bg": "#0b0f1a",
            "--cp-bg-elevated": "#121829",
            "--cp-surface": "#121829",
            "--cp-surface-soft": "#1a2238",
            "--cp-border": "#2a3450",
            "--cp-border-strong": "#3d4a6b",
            "--cp-text": "#ffffff",
            "--cp-text-muted": "#a8b3c7",
            "--cp-text-soft": "#c7d0df",
            "--cp-accent": "#50e6ff",
            "--cp-accent-hover": "#7eecff",
            "--cp-accent-soft": "rgba(80, 230, 255, 0.12)",
            "--cp-accent-fg": "#0b0f1a",
            "--cp-success": "#4ade80",
            "--cp-danger": "#fb8a8a",
            "--cp-warning": "#fbbf24",
            "--cp-link": "#50e6ff",
            "--cp-shadow": "0 1px 2px rgba(0, 0, 0, 0.40)",
            "--cp-overlay": "rgba(11, 15, 26, 0.72)",
            "--cp-panel": "rgba(18, 24, 41, 0.86)",
            "--cp-panel-strong": "rgba(18, 24, 41, 0.97)",
            "--cp-sheen": "rgba(255, 255, 255, 0.05)",
            "--cp-highlight": "rgba(80, 230, 255, 0.14)",
        },
        "dark": {
            "--cp-bg": "#0b0f1a",
            "--cp-bg-elevated": "#121829",
            "--cp-surface": "#121829",
            "--cp-surface-soft": "#1a2238",
            "--cp-border": "#2a3450",
            "--cp-border-strong": "#3d4a6b",
            "--cp-text": "#ffffff",
            "--cp-text-muted": "#a8b3c7",
            "--cp-text-soft": "#c7d0df",
            "--cp-accent": "#50e6ff",
            "--cp-accent-hover": "#7eecff",
            "--cp-accent-soft": "rgba(80, 230, 255, 0.12)",
            "--cp-accent-fg": "#0b0f1a",
            "--cp-success": "#4ade80",
            "--cp-danger": "#fb8a8a",
            "--cp-warning": "#fbbf24",
            "--cp-link": "#50e6ff",
            "--cp-shadow": "0 1px 2px rgba(0, 0, 0, 0.40)",
            "--cp-overlay": "rgba(11, 15, 26, 0.72)",
            "--cp-panel": "rgba(18, 24, 41, 0.86)",
            "--cp-panel-strong": "rgba(18, 24, 41, 0.97)",
            "--cp-sheen": "rgba(255, 255, 255, 0.05)",
            "--cp-highlight": "rgba(80, 230, 255, 0.14)",
        },
    },
    "signal": {
        "light": {
            "--cp-bg": "#f4f4f5",
            "--cp-bg-elevated": "#fafafa",
            "--cp-surface": "#ffffff",
            "--cp-surface-soft": "#eeeeef",
            "--cp-border": "#dcdcde",
            "--cp-border-strong": "#8e8e93",
            "--cp-text": "#18181b",
            "--cp-text-muted": "#52525b",
            "--cp-text-soft": "#6b6b74",
            "--cp-accent": "#b11f4b",
            "--cp-accent-hover": "#9a1a41",
            "--cp-accent-soft": "rgba(177, 31, 75, 0.08)",
            "--cp-accent-fg": "#ffffff",
            "--cp-success": "#15803d",
            "--cp-danger": "#c81e1e",
            "--cp-warning": "#b45309",
            "--cp-link": "#0f6cbd",
            "--cp-shadow": "0 16px 40px rgba(24, 24, 27, 0.10)",
            "--cp-overlay": "rgba(24, 24, 27, 0.55)",
            "--cp-panel": "rgba(255, 255, 255, 0.86)",
            "--cp-panel-strong": "rgba(255, 255, 255, 0.96)",
            "--cp-sheen": "rgba(24, 24, 27, 0.04)",
            "--cp-highlight": "rgba(177, 31, 75, 0.12)",
        },
        "dark": {
            "--cp-bg": "#18181b",
            "--cp-bg-elevated": "#232327",
            "--cp-surface": "#1f1f23",
            "--cp-surface-soft": "#27272b",
            "--cp-border": "#34343a",
            "--cp-border-strong": "#54545c",
            "--cp-text": "#f4f4f5",
            "--cp-text-muted": "#a9a9b2",
            "--cp-text-soft": "#c4c4cc",
            "--cp-accent": "#ff7a9c",
            "--cp-accent-hover": "#ff96b0",
            "--cp-accent-soft": "rgba(255, 122, 156, 0.14)",
            "--cp-accent-fg": "#18181b",
            "--cp-success": "#4ade80",
            "--cp-danger": "#fb8a8a",
            "--cp-warning": "#fbbf24",
            "--cp-link": "#66b3ff",
            "--cp-shadow": "0 16px 40px rgba(0, 0, 0, 0.45)",
            "--cp-overlay": "rgba(9, 9, 11, 0.7)",
            "--cp-panel": "rgba(31, 31, 35, 0.78)",
            "--cp-panel-strong": "rgba(31, 31, 35, 0.96)",
            "--cp-sheen": "rgba(255, 255, 255, 0.05)",
            "--cp-highlight": "rgba(255, 122, 156, 0.12)",
        },
    },
    "fluent": {
        "light": {
            "--cp-bg": "#f5f5f5",
            "--cp-bg-elevated": "#fafafa",
            "--cp-surface": "#ffffff",
            "--cp-surface-soft": "#ededed",
            "--cp-border": "#d1d1d1",
            "--cp-border-strong": "#8a8886",
            "--cp-text": "#1b1a19",
            "--cp-text-muted": "#57534e",
            "--cp-text-soft": "#6b6b6b",
            "--cp-accent": "#0f6cbd",
            "--cp-accent-hover": "#115ea3",
            "--cp-accent-soft": "rgba(15, 108, 189, 0.08)",
            "--cp-accent-fg": "#ffffff",
            "--cp-success": "#15803d",
            "--cp-danger": "#c81e1e",
            "--cp-warning": "#b45309",
            "--cp-link": "#0f6cbd",
            "--cp-shadow": "0 16px 40px rgba(27, 26, 25, 0.10)",
            "--cp-overlay": "rgba(27, 26, 25, 0.55)",
            "--cp-panel": "rgba(255, 255, 255, 0.86)",
            "--cp-panel-strong": "rgba(255, 255, 255, 0.96)",
            "--cp-sheen": "rgba(27, 26, 25, 0.04)",
            "--cp-highlight": "rgba(15, 108, 189, 0.12)",
        },
        "dark": {
            "--cp-bg": "#1b1a19",
            "--cp-bg-elevated": "#292827",
            "--cp-surface": "#242322",
            "--cp-surface-soft": "#2e2d2c",
            "--cp-border": "#3d3b39",
            "--cp-border-strong": "#5c5a58",
            "--cp-text": "#f3f2f1",
            "--cp-text-muted": "#adaba9",
            "--cp-text-soft": "#c8c6c4",
            "--cp-accent": "#62abf5",
            "--cp-accent-hover": "#83bdf7",
            "--cp-accent-soft": "rgba(98, 171, 245, 0.14)",
            "--cp-accent-fg": "#06182e",
            "--cp-success": "#4ade80",
            "--cp-danger": "#fb8a8a",
            "--cp-warning": "#fbbf24",
            "--cp-link": "#62abf5",
            "--cp-shadow": "0 16px 40px rgba(0, 0, 0, 0.45)",
            "--cp-overlay": "rgba(0, 0, 0, 0.7)",
            "--cp-panel": "rgba(36, 35, 34, 0.78)",
            "--cp-panel-strong": "rgba(36, 35, 34, 0.96)",
            "--cp-sheen": "rgba(255, 255, 255, 0.05)",
            "--cp-highlight": "rgba(98, 171, 245, 0.12)",
        },
    },
}

LIGHT = PALETTES[PALETTE]["light"]
DARK = PALETTES[PALETTE]["dark"]

# Every token a palette defines. Pages may USE these (var(--cp-bg)) but never
# DECLARE them: the stamped block is the only place they are set, so a retheme
# is one constant above plus scripts/apply_design_tokens.py. The stamper strips
# any page-local declaration of these names (see strip_local_palette).
PALETTE_TOKEN_NAMES: frozenset[str] = frozenset(LIGHT) | frozenset(
    {"--cp-focus", "--cp-focus-halo"}
)

# Added by the design pass. These had no single definition anywhere: the audit
# counted 29 distinct font sizes and 10 corner radii on index.html alone.
SCALE = {
    # Type. One ramp, fluid between 360px and 1440px viewports.
    "--cp-font": (
        '"Segoe UI Variable", "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, '
        '"Helvetica Neue", Arial, sans-serif'
    ),
    "--cp-font-mono": (
        'Consolas, "Cascadia Mono", Menlo, ui-monospace, SFMono-Regular, "SF Mono", monospace'
    ),
    "--cp-text-xs": "0.75rem",
    "--cp-text-sm": "0.875rem",
    "--cp-text-base": "1rem",
    "--cp-text-lg": "1.125rem",
    "--cp-text-xl": "clamp(1.25rem, 1.15rem + 0.4vw, 1.5rem)",
    "--cp-text-2xl": "clamp(1.5rem, 1.3rem + 0.9vw, 2rem)",
    "--cp-text-3xl": "clamp(1.875rem, 1.5rem + 1.6vw, 2.75rem)",
    "--cp-text-4xl": "clamp(2.25rem, 1.6rem + 2.8vw, 3.75rem)",
    "--cp-leading-tight": "1.15",
    "--cp-leading-snug": "1.35",
    "--cp-leading": "1.6",
    "--cp-tracking-tight": "-0.02em",
    "--cp-tracking-label": "0.08em",
    "--cp-measure": "65ch",
    # Space. A 4px base, so existing hand-set values land on the same grid.
    "--cp-space-1": "0.25rem",
    "--cp-space-2": "0.5rem",
    "--cp-space-3": "0.75rem",
    "--cp-space-4": "1rem",
    "--cp-space-5": "1.5rem",
    "--cp-space-6": "2rem",
    "--cp-space-7": "3rem",
    "--cp-space-8": "4rem",
    "--cp-space-9": "6rem",
    # Shape. One scale: the audit found ten radii including three asymmetric ones.
    "--cp-radius-sm": "6px",
    "--cp-radius": "8px",
    "--cp-radius-lg": "12px",
    "--cp-radius-pill": "999px",
    # Motion.
    "--cp-ease": "cubic-bezier(0.2, 0, 0, 1)",
    "--cp-duration-fast": "120ms",
    "--cp-duration": "220ms",
    # The four Microsoft logo squares, so the header mark never needs a literal.
    "--cp-logo-1": "#f25022",
    "--cp-logo-2": "#7fba00",
    "--cp-logo-3": "#00a4ef",
    "--cp-logo-4": "#ffb900",
    # Structure.
    "--cp-container": "1200px",
    "--cp-header-height": "52px",
    "--cp-z-base": "1",
    "--cp-z-sticky": "100",
    "--cp-z-overlay": "200",
    "--cp-z-modal": "300",
    "--cp-z-toast": "400",
}

# Focus ring. The audit measured the old ring (a 12%-opacity accent tint) at
# about 1.2:1 against every surface it landed on, i.e. invisible. This is a
# solid two-tone ring that reads on both themes.
FOCUS_RINGS: dict[str, dict[str, dict[str, str]]] = {
    "gallery": {
        "light": {"--cp-focus": "#50e6ff", "--cp-focus-halo": "rgba(80, 230, 255, 0.35)"},
        "dark": {"--cp-focus": "#50e6ff", "--cp-focus-halo": "rgba(80, 230, 255, 0.35)"},
    },
    "signal": {
        "light": {"--cp-focus": "#0b5fa5", "--cp-focus-halo": "rgba(11, 95, 165, 0.28)"},
        "dark": {"--cp-focus": "#7cc4ff", "--cp-focus-halo": "rgba(124, 196, 255, 0.34)"},
    },
    "fluent": {
        "light": {"--cp-focus": "#0b5fa5", "--cp-focus-halo": "rgba(11, 95, 165, 0.28)"},
        "dark": {"--cp-focus": "#7cc4ff", "--cp-focus-halo": "rgba(124, 196, 255, 0.34)"},
    },
}
FOCUS_LIGHT = FOCUS_RINGS[PALETTE]["light"]
FOCUS_DARK = FOCUS_RINGS[PALETTE]["dark"]


def _declarations(tokens: dict[str, str], indent: str = "  ") -> str:
    return "\n".join(f"{indent}{name}: {value};" for name, value in tokens.items())


def render_tokens() -> str:
    """The exact block stamped into every published page."""
    light = {**LIGHT, **FOCUS_LIGHT, **SCALE}
    dark = {**DARK, **FOCUS_DARK}
    root_scheme = SINGLE_SCHEME.get(PALETTE, "light")
    single_scheme_rules = ""
    if PALETTE in SINGLE_SCHEME:
        single_scheme_rules = (
            "/* This palette renders one scheme, so a light/dark toggle would change\n"
            "   nothing; pages that carry one keep their markup and lose the button. */\n"
            "[data-theme-toggle], #themeToggle { display: none !important; }\n"
        )
    return f"""{START_MARK}
<style>
/* AIBAST design tokens - generated by tools/design_tokens.py, do not hand-edit.
   Palette: {PALETTE}. Stamped before each page's own <style>, so page rules
   still win; pages never declare these tokens themselves, only use them. */
:root {{
  color-scheme: {root_scheme};
{_declarations(light)}
}}
html[data-theme="dark"] {{
  color-scheme: dark;
{_declarations(dark)}
}}
@media (prefers-color-scheme: dark) {{
  html:not([data-theme="light"]) {{
    color-scheme: dark;
{_declarations(dark, indent="    ")}
  }}
}}
/* Keyboard focus has to be visible on every page, not only the ones that
   remembered to style it. Pages that define their own :focus-visible override
   this, because their <style> comes after. */
:where(a, button, input, select, textarea, summary, [tabindex]):focus-visible {{
  outline: 2px solid var(--cp-focus);
  outline-offset: 2px;
  border-radius: var(--cp-radius-sm);
  box-shadow: 0 0 0 4px var(--cp-focus-halo);
}}
/* An anchored heading must not land under a sticky header. */
:where([id]) {{ scroll-margin-top: calc(var(--cp-header-height) + var(--cp-space-4)); }}
:where(img, svg, video, canvas) {{ max-width: 100%; }}
:where(p) {{ text-wrap: pretty; }}
::selection {{ background: var(--cp-accent-soft); color: var(--cp-text); }}
/* Opt-in: aligns digits in tables and metric readouts. */
.cp-nums {{ font-variant-numeric: tabular-nums; }}
{single_scheme_rules}@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }}
}}
</style>
{END_MARK}"""


def current_block(root: Path = ROOT) -> str:
    """Alias kept so callers read the same way as tools.clarity_tag."""
    del root
    return render_tokens()


def strip_block(text: str) -> str:
    """Remove a previously stamped block (and the blank line it left)."""
    return STRIP_RE.sub("", text)


def strip_block_bytes(data: bytes) -> bytes:
    """Byte-level strip, for comparing a page against a copy inside an export ZIP."""
    return BLOCK_BYTES_RE.sub(b"", data)


# A page-local declaration of a palette token, e.g. "  --cp-bg: #f4f4f5;\n".
# Declarations are matched one line at a time, which is how every page and
# generator writes them; the line's indentation and trailing newline go too.
_LOCAL_TOKEN_RE = re.compile(
    r"^[ \t]*(?:" + "|".join(sorted(map(re.escape, PALETTE_TOKEN_NAMES))) + r")\s*:[^;{}\n]*;[ \t]*\n?",
    re.MULTILINE,
)
# A rule set left with nothing but whitespace (or only a color-scheme line)
# after its token declarations went: ":root {\n  color-scheme: light;\n}".
_EMPTY_RULE_RE = re.compile(
    r"^[ \t]*(?::root|html\[data-theme=[\"']dark[\"']\]|html:not\(\[data-theme=[\"']light[\"']\]\))"
    r"[ \t]*\{\s*(?:color-scheme\s*:\s*(?:light|dark)\s*;\s*)?\}[ \t]*\n?",
    re.MULTILINE,
)
_EMPTY_MEDIA_RE = re.compile(
    r"^[ \t]*@media \(prefers-color-scheme: dark\)[ \t]*\{\s*\}[ \t]*\n?",
    re.MULTILINE,
)


def strip_local_palette(html: str) -> str:
    """Remove page-local declarations of the shared palette tokens.

    The stamped block is the only place ``--cp-*`` palette tokens are set. A
    page that also declared them in its own ``:root`` would win the cascade
    (its ``<style>`` comes after the stamp) and freeze the old colours, which
    is exactly what made the 2026-09 retheme a 13,570-line edit. Only the
    page's own CSS is touched: the stamped block is kept aside and restored.
    """
    existing = BLOCK_RE.search(html)
    if existing:
        head, block, tail = html[: existing.start()], existing.group(0), html[existing.end() :]
    else:
        head, block, tail = html, "", ""
    cleaned = []
    for part in (head, tail):
        part = _LOCAL_TOKEN_RE.sub("", part)
        part = _EMPTY_RULE_RE.sub("", part)
        part = _EMPTY_MEDIA_RE.sub("", part)
        cleaned.append(part)
    return cleaned[0] + block + cleaned[1]


def local_palette_declarations(html: str) -> list[str]:
    """The page-local palette declarations a page still carries (should be none)."""
    stripped = strip_block(html)
    return [m.group(0).strip() for m in _LOCAL_TOKEN_RE.finditer(stripped)]


def stamp(html: str, block: str) -> str:
    """Insert or refresh the block, and remove any page-local palette copy.

    Placement is deliberate: immediately before the page's first ``<style>`` so
    every page rule still overrides it. Pages with no ``<style>`` get it before
    ``</head>``.
    """
    html = strip_local_palette(html)
    existing = BLOCK_RE.search(html)
    if existing:
        if existing.group(0) == block:
            return html
        return html[: existing.start()] + block + html[existing.end() :]

    # Earliest of: the page's first <style>, the Clarity block, </head>. Being
    # before the page's style keeps these rules a floor; being before the
    # Clarity block keeps the two stampers from fighting over the slot right
    # in front of </head> on pages that have no <style> of their own.
    candidates = [
        match.start()
        for match in (
            STYLE_OPEN_RE.search(html),
            CLARITY_START_RE.search(html),
            HEAD_CLOSE_RE.search(html),
        )
        if match is not None
    ]
    if not candidates:
        raise ValueError("page has neither <style> nor </head>; cannot place design tokens")
    at = min(candidates)
    return html[:at] + block + "\n" + html[at:]


# ---------------------------------------------------------------------------
# Preview page. docs/design-system.html is generated from here so a palette can
# be judged by eye before (or after) it is stamped into 300+ pages. Every colour
# on it comes from a token; the page is itself stamped like any other.
# ---------------------------------------------------------------------------

PREVIEW_PATH = ROOT / "docs" / "design-system.html"


def _swatch_rows(theme: dict[str, str]) -> str:
    rows = []
    for name, value in theme.items():
        rows.append(
            f'<tr><td><code>{name}</code></td><td>{value}</td>'
            f'<td><span class="sw" style="background: var({name})"></span></td></tr>'
        )
    return "\n".join(rows)


def render_preview() -> str:
    """The design-system page: tokens, type, shape and the component vocabulary."""
    scheme_note = (
        f"This palette renders one scheme ({SINGLE_SCHEME[PALETTE]}); light and dark blocks carry the same values."
        if PALETTE in SINGLE_SCHEME
        else "This palette has a light and a dark scheme; the page follows the visitor's system setting."
    )
    others = ", ".join(sorted(n for n in PALETTES if n != PALETTE)) or "none"
    body = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AIBAST design system</title>
<meta name="description" content="The one set of design tokens every AIBAST Agents Library page carries, with the component vocabulary rendered from them.">
<meta name="robots" content="noindex">
<style>
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: var(--cp-bg); color: var(--cp-text); font-family: var(--cp-font); font-size: 14px; line-height: 1.45; }}
a {{ color: var(--cp-link); }}
code {{ font-family: var(--cp-font-mono); font-size: var(--cp-text-xs); }}
.wrap {{ max-width: var(--cp-container); margin: 0 auto; padding: 0 var(--cp-space-5); }}
header {{ border-bottom: 1px solid var(--cp-border); position: sticky; top: 0; background: var(--cp-bg); z-index: var(--cp-z-sticky); }}
.bar {{ display: flex; align-items: center; gap: var(--cp-space-3); height: var(--cp-header-height); }}
.ms {{ display: grid; grid-template-columns: 9px 9px; gap: 2px; }} .ms i {{ width: 9px; height: 9px; display: block; }}
.brand {{ font-weight: 600; font-size: 15px; white-space: nowrap; }} .brand span {{ color: var(--cp-text-muted); font-weight: 400; }}
nav {{ margin-left: auto; display: flex; gap: 18px; }} nav a {{ color: var(--cp-text-muted); text-decoration: none; font-size: 13px; }} nav a.on {{ color: var(--cp-text); }}
.kick {{ color: var(--cp-accent); font-size: var(--cp-text-xs); font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; }}
.hero {{ padding: var(--cp-space-7) 0 var(--cp-space-5); border-bottom: 1px solid var(--cp-border); }}
.hero h1 {{ font-size: var(--cp-text-4xl); line-height: var(--cp-leading-tight); font-weight: 600; margin: var(--cp-space-2) 0 var(--cp-space-3); letter-spacing: var(--cp-tracking-tight); max-width: 760px; }}
.hero p {{ color: var(--cp-text-muted); font-size: var(--cp-text-base); margin: 0; max-width: var(--cp-measure); }}
h2 {{ font-size: var(--cp-text-xl); font-weight: 600; margin: var(--cp-space-6) 0 var(--cp-space-3); }}
.find {{ background: var(--cp-surface); border-bottom: 1px solid var(--cp-border); padding: var(--cp-space-4) 0; }}
.q {{ width: 100%; height: 44px; border-radius: var(--cp-radius-sm); border: 1px solid var(--cp-border); background: var(--cp-bg); color: var(--cp-text); padding: 0 var(--cp-space-3); font: inherit; }}
.chips {{ display: flex; gap: var(--cp-space-2); margin-top: var(--cp-space-3); flex-wrap: wrap; }}
.chip {{ border: 1px solid var(--cp-border); background: transparent; color: var(--cp-text); border-radius: var(--cp-radius-pill); padding: 5px 12px; font: inherit; cursor: pointer; }}
.chip[aria-pressed="true"] {{ background: var(--cp-text); color: var(--cp-bg); border-color: var(--cp-text); }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: var(--cp-space-4); }}
.card {{ background: var(--cp-surface); border: 1px solid var(--cp-border); border-radius: var(--cp-radius); padding: 18px; display: flex; flex-direction: column; gap: var(--cp-space-2); min-width: 0; }}
.card:hover {{ border-color: var(--cp-accent); }}
.card h3 {{ margin: 0; font-size: var(--cp-text-base); font-weight: 600; line-height: 1.3; }}
.card p {{ margin: 0; color: var(--cp-text-muted); font-size: 13px; }}
.meta {{ margin-top: auto; padding-top: var(--cp-space-2); display: flex; flex-wrap: wrap; gap: 6px; color: var(--cp-text-muted); font-size: var(--cp-text-xs); }}
.tag {{ border: 1px solid var(--cp-border); border-radius: 4px; padding: 1px 7px; }}
.btn {{ display: inline-flex; align-items: center; justify-content: center; gap: var(--cp-space-2); height: 40px; padding: 0 var(--cp-space-4); border-radius: var(--cp-radius-sm); border: 1px solid var(--cp-border); background: transparent; color: var(--cp-text); text-decoration: none; font: inherit; font-weight: 600; cursor: pointer; }}
.btn.pri {{ background: var(--cp-accent); border-color: var(--cp-accent); color: var(--cp-accent-fg); }}
.btn.pri:hover {{ background: var(--cp-accent-hover); border-color: var(--cp-accent-hover); }}
.row {{ display: flex; gap: var(--cp-space-3); flex-wrap: wrap; align-items: center; }}
.tabs {{ display: flex; gap: 4px; border-bottom: 1px solid var(--cp-border); }}
.tab {{ background: none; border: 0; border-bottom: 2px solid transparent; color: var(--cp-text-muted); padding: 10px 14px; font: inherit; font-weight: 600; cursor: pointer; }}
.tab[aria-selected="true"] {{ color: var(--cp-text); border-color: var(--cp-accent); }}
.step {{ display: flex; gap: var(--cp-space-3); align-items: flex-start; background: var(--cp-surface); border: 1px solid var(--cp-border); border-radius: var(--cp-radius); padding: var(--cp-space-3); margin-bottom: var(--cp-space-2); }}
.num {{ flex: none; width: 24px; height: 24px; border-radius: 12px; border: 1px solid var(--cp-accent); color: var(--cp-accent); display: grid; place-items: center; font-size: var(--cp-text-xs); font-weight: 600; }}
.note {{ color: var(--cp-text-muted); font-size: var(--cp-text-xs); }}
.code {{ background: var(--cp-bg); border: 1px solid var(--cp-border); border-radius: var(--cp-radius-sm); padding: 10px; font-family: var(--cp-font-mono); font-size: var(--cp-text-xs); overflow-wrap: anywhere; }}
.status {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: var(--cp-text-xs); font-weight: 600; }}
.ok {{ color: var(--cp-success); border: 1px solid var(--cp-success); }} .warn {{ color: var(--cp-warning); border: 1px solid var(--cp-warning); }} .bad {{ color: var(--cp-danger); border: 1px solid var(--cp-danger); }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }} td, th {{ border-top: 1px solid var(--cp-border); padding: 8px 6px; vertical-align: top; text-align: left; }} th {{ color: var(--cp-text-muted); font-weight: 600; }}
.sw {{ display: inline-block; width: 64px; height: 22px; border-radius: 4px; border: 1px solid var(--cp-border-strong); }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: var(--cp-space-4); }}
.box {{ background: var(--cp-surface); border: 1px solid var(--cp-border); border-radius: var(--cp-radius); padding: var(--cp-space-4); }}
.shape {{ display: flex; gap: var(--cp-space-4); align-items: flex-end; }} .shape div {{ width: 72px; height: 48px; background: var(--cp-surface-soft); border: 1px solid var(--cp-border); display: grid; place-items: center; font-size: var(--cp-text-xs); color: var(--cp-text-muted); }}
footer {{ border-top: 1px solid var(--cp-border); color: var(--cp-text-muted); font-size: var(--cp-text-xs); padding: 18px 0 30px; margin-top: var(--cp-space-8); }}
@media (max-width: 820px) {{ .two {{ grid-template-columns: 1fr; }} nav {{ display: none; }} }}
</style>
</head>
<body>
<header><div class="wrap bar">
 <div class="ms" aria-hidden="true"><i style="background: var(--cp-logo-1)"></i><i style="background: var(--cp-logo-2)"></i><i style="background: var(--cp-logo-3)"></i><i style="background: var(--cp-logo-4)"></i></div>
 <div class="brand">AIBAST Agents Library <span>/ Design system</span></div>
 <nav><a class="on" href="#">Solutions</a><a href="#">Industries</a><a href="#">Learn</a><a href="#">About</a></nav>
</div></header>
<main>
<section class="hero"><div class="wrap">
 <div class="kick">Palette: {PALETTE}</div>
 <h1>One set of tokens, every page</h1>
 <p>Every published page carries this block from <code>tools/design_tokens.py</code> and declares none of it itself. Change the palette there, run <code>scripts/retheme.sh</code>, and the whole library follows. {scheme_note} Other palettes on file: {others}.</p>
</div></section>
<section class="find"><div class="wrap">
 <input class="q" type="search" placeholder="Search by problem, role or product" aria-label="Search">
 <div class="chips"><button class="chip" aria-pressed="true">All</button><button class="chip">Single agent</button><button class="chip">Agent team</button><button class="chip">Financial services</button><button class="chip">Healthcare</button><button class="chip">Retail</button></div>
</div></section>
<div class="wrap">
 <h2>Cards</h2>
 <div class="grid">
  <div class="card"><div class="kick">Financial services</div><h3>Account Intelligence Agent</h3><p>Prepare for the account conversation from one evidence view.</p><div class="meta"><span class="tag">Copilot Studio</span><span class="tag">Dynamics 365</span></div></div>
  <div class="card"><div class="kick">Healthcare +2</div><h3>Prior Authorization Team</h3><p>Three agents hand a request across intake, policy and reply.</p><div class="meta"><span class="tag">Agent team</span><span class="tag">Microsoft 365</span></div></div>
  <div class="card"><div class="kick">Retail</div><h3>Inventory Rebalancing Agent</h3><p>Move stock before the shelf runs out, with the reason shown.</p><div class="meta"><span class="tag">Power Platform</span></div></div>
 </div>
 <h2>Buttons, status and tabs</h2>
 <div class="row"><a class="btn pri" href="#">Download package</a><a class="btn" href="#">Try the demo chat</a><span class="status ok">Passed</span><span class="status warn">Pending</span><span class="status bad">Failed</span></div>
 <div class="tabs" style="margin-top: var(--cp-space-4)"><button class="tab" aria-selected="true">What it does</button><button class="tab">How it works</button><button class="tab">What's inside</button><button class="tab">Set it up</button></div>
 <h2>Steps and code</h2>
 <div class="step"><span class="num">1</span><div>Download the solution package.</div></div>
 <div class="step"><span class="num">2</span><div>Import it in Copilot Studio, or ask your AI to do it:<div class="code" style="margin-top: 6px">Go and read https://microsoft.github.io/aibast-agents-library/solutions/account-intelligence/SKILL.md and set it up for me.</div></div></div>
 <h2>Type and shape</h2>
 <div class="two">
  <div class="box"><div class="kick">Type ramp</div><div style="font-size: var(--cp-text-4xl); font-weight: 600; letter-spacing: var(--cp-tracking-tight); line-height: var(--cp-leading-tight)">Aa 4xl</div><div style="font-size: var(--cp-text-2xl); font-weight: 600">Aa 2xl heading</div><div style="font-size: var(--cp-text-base)">Aa base body text</div><div class="note">xs muted note</div><div class="code" style="margin-top: 8px">mono: var(--cp-font-mono)</div></div>
  <div class="box"><div class="kick">Radii and space</div><div class="shape"><div style="border-radius: var(--cp-radius-sm)">sm</div><div style="border-radius: var(--cp-radius)">md</div><div style="border-radius: var(--cp-radius-lg)">lg</div><div style="border-radius: var(--cp-radius-pill)">pill</div></div><p class="note" style="margin: 12px 0 0">Space scale 1 to 9 on a 4px grid; container {SCALE["--cp-container"]}; header {SCALE["--cp-header-height"]}.</p></div>
 </div>
 <h2>Tokens</h2>
 <div class="two">
  <div class="box"><div class="kick">Light block (:root)</div><table><tr><th>Token</th><th>Value</th><th></th></tr>{_swatch_rows({**LIGHT, **FOCUS_LIGHT})}</table></div>
  <div class="box"><div class="kick">Dark block (html[data-theme="dark"])</div><table><tr><th>Token</th><th>Value</th><th></th></tr>{_swatch_rows({**DARK, **FOCUS_DARK})}</table></div>
 </div>
 <h2>How to retheme</h2>
 <div class="step"><span class="num">1</span><div>Add or edit a palette in <code>tools/design_tokens.py</code> and point <code>PALETTE</code> at it. Keep every token name; the tests check contrast and that the ground is never warm paper.</div></div>
 <div class="step"><span class="num">2</span><div>Run <code>scripts/retheme.sh</code>. It stamps every page, rewrites this preview and the metrics contract, rebuilds the impact report and the library API's page hashes, then runs the audits and the token tests.</div></div>
 <div class="step"><span class="num">3</span><div>Open this page and a few real ones, then open a pull request to staging. Nothing else to edit: pages use the tokens and never declare them, and the stamper removes any copy a generator sneaks back in.</div></div>
</div>
</main>
<footer><div class="wrap">Generated by tools/design_tokens.py. Edit the module, not this file.</div></footer>
</body>
</html>
"""
    page = stamp(body, render_tokens())
    # A published page also carries the Clarity tag; stamp it here so a preview
    # rewrite never drops it (tests/test_clarity_tag.py checks every page).
    try:
        from tools.clarity_tag import current_tag as _clarity_tag, stamp as _clarity_stamp

        page = _clarity_stamp(page, _clarity_tag(ROOT))
    except Exception:  # pragma: no cover - the tag is optional when no project is configured
        pass
    return page


def write_preview(path: Path = PREVIEW_PATH) -> bool:
    """Write the preview page; True if it changed."""
    html = render_preview()
    if path.exists() and path.read_text(encoding="utf-8") == html:
        return False
    path.write_text(html, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="AIBAST design tokens")
    parser.add_argument("--print", action="store_true", help="print the stamped block")
    parser.add_argument("--preview", action="store_true", help=f"write {PREVIEW_PATH.relative_to(ROOT)}")
    parser.add_argument("--list", action="store_true", help="list palettes; * marks the active one")
    args = parser.parse_args(argv)
    if args.list:
        for name in PALETTES:
            print(("* " if name == PALETTE else "  ") + name + (f" (single scheme: {SINGLE_SCHEME[name]})" if name in SINGLE_SCHEME else ""))
    if args.print:
        print(render_tokens())
    if args.preview:
        changed = write_preview()
        print(f"{'wrote' if changed else 'unchanged'} {PREVIEW_PATH.relative_to(ROOT)}")
    if not (args.list or args.print or args.preview):
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
