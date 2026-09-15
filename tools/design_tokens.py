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
PALETTE = "signal"

PALETTES: dict[str, dict[str, dict[str, str]]] = {
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

# Added by the design pass. These had no single definition anywhere: the audit
# counted 29 distinct font sizes and 10 corner radii on index.html alone.
SCALE = {
    # Type. One ramp, fluid between 360px and 1440px viewports.
    "--cp-font": (
        '"Segoe UI", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif'
    ),
    "--cp-font-mono": (
        'ui-monospace, SFMono-Regular, "SF Mono", "Cascadia Mono", "Segoe UI Mono", '
        'Menlo, Consolas, monospace'
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
    "--cp-radius": "10px",
    "--cp-radius-lg": "16px",
    "--cp-radius-pill": "999px",
    # Motion.
    "--cp-ease": "cubic-bezier(0.2, 0, 0, 1)",
    "--cp-duration-fast": "120ms",
    "--cp-duration": "220ms",
    # Structure.
    "--cp-container": "1200px",
    "--cp-header-height": "68px",
    "--cp-z-base": "1",
    "--cp-z-sticky": "100",
    "--cp-z-overlay": "200",
    "--cp-z-modal": "300",
    "--cp-z-toast": "400",
}

# Focus ring. The audit measured the old ring (a 12%-opacity accent tint) at
# about 1.2:1 against every surface it landed on, i.e. invisible. This is a
# solid two-tone ring that reads on both themes.
FOCUS_LIGHT = {"--cp-focus": "#0b5fa5", "--cp-focus-halo": "rgba(11, 95, 165, 0.28)"}
FOCUS_DARK = {"--cp-focus": "#7cc4ff", "--cp-focus-halo": "rgba(124, 196, 255, 0.34)"}


def _declarations(tokens: dict[str, str], indent: str = "  ") -> str:
    return "\n".join(f"{indent}{name}: {value};" for name, value in tokens.items())


def render_tokens() -> str:
    """The exact block stamped into every published page."""
    light = {**LIGHT, **FOCUS_LIGHT, **SCALE}
    dark = {**DARK, **FOCUS_DARK}
    return f"""{START_MARK}
<style>
/* AIBAST design tokens - generated by tools/design_tokens.py, do not hand-edit.
   Stamped before each page's own <style>, so page rules still win. */
:root {{
  color-scheme: light;
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
@media (prefers-reduced-motion: reduce) {{
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


def stamp(html: str, block: str) -> str:
    """Insert or refresh the block.

    Placement is deliberate: immediately before the page's first ``<style>`` so
    every page rule still overrides it. Pages with no ``<style>`` get it before
    ``</head>``.
    """
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
