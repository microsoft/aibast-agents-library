"""Generated cover art for solutions, workshops and field notes.

These deterministic, decorative SVGs use repository design tokens and the
catalog's industry glyphs. They do not depict recorded runs or provide evidence.
They avoid an external stock-art dependency and remain subject to the
repository's licence.

Import ``cover_svg`` for inline rendering, or run
``python tools/solution_covers.py`` to explicitly refresh the featured cover in
``field-notes.json``. Importing this module does not modify site content.
"""

from __future__ import annotations

import hashlib
import math

WIDTH, HEIGHT = 960, 300

# The catalog's own per-vertical marks, so a cover and its card agree.
VERTICAL_GLYPH = {
    "b2b_sales": "↗",
    "b2c_sales": "◎",
    "energy": "↯",
    "financial_services": "◆",
    "general": "✦",
    "healthcare": "✚",
    "human_resources": "◇",
    "manufacturing": "⚙",
    "professional_services": "§",
    "retail_cpg": "▦",
    "slg_government": "⌂",
    "software_digital_products": "⌘",
    "customer_service": "☎",
}

SOFT = "var(--cp-text-soft)"
ACCENT = "var(--cp-accent)"
TEXT = "var(--cp-text)"
SURFACE = "var(--cp-surface)"
GROUND = "var(--cp-surface-soft)"


class _Rng:
    """A deterministic byte stream from a seed. Same slug, same art, forever."""

    def __init__(self, seed: str) -> None:
        self._block = hashlib.sha256(seed.encode("utf-8")).digest()
        self._i = 0

    def byte(self) -> int:
        value = self._block[self._i % len(self._block)]
        self._i += 1
        if self._i % len(self._block) == 0:
            self._block = hashlib.sha256(self._block).digest()
        return value

    def unit(self) -> float:
        return self.byte() / 255.0

    def between(self, low: float, high: float) -> float:
        return low + (high - low) * self.unit()


def _glyph(mark: str) -> str:
    return (
        f'<text x="{WIDTH - 34}" y="{HEIGHT - 26}" text-anchor="end" font-size="40" '
        f'font-weight="700" font-family="system-ui,sans-serif" fill="{ACCENT}" '
        f'opacity=".26">{mark}</text>'
    )


def _signal(rng: _Rng, mark: str) -> str:
    """Decorative signal bars with one highlighted cluster."""
    count = 46 + rng.byte() % 22
    pad, base, span = 56, HEIGHT - 58, HEIGHT - 150
    phase = rng.between(0, 6.283)
    slow, fast = rng.between(1.2, 2.6), rng.between(3.1, 6.4)
    hot = int(count * rng.between(0.28, 0.72))
    parts = []
    for i in range(count):
        t = i / (count - 1)
        x = pad + (WIDTH - pad * 2) * t
        envelope = math.sin(math.pi * t) ** 0.7
        height = span * envelope * (
            0.42
            + 0.34 * math.sin(phase + t * slow * math.pi)
            + 0.18 * math.sin(phase * 2 + t * fast * math.pi)
        )
        height = max(6.0, height)
        lit = abs(i - hot) <= 1
        parts.append(
            f'<path d="M{x:.1f} {base:.1f}v-{height:.1f}" '
            f'stroke="{ACCENT if lit else SOFT}" stroke-width="{5 if lit else 3.4}" '
            f'stroke-linecap="round" opacity="{0.95 if lit else 0.34}"/>'
        )
    parts.append(
        f'<path d="M{pad} {base + 12}H{WIDTH - pad}" stroke="var(--cp-border)" stroke-width="1.5"/>'
    )
    return "".join(parts) + _glyph(mark)


def _routing(rng: _Rng, mark: str) -> str:
    """Work arrives, is classified, and leaves resolved. One lane is the answer."""
    lanes = 4 + rng.byte() % 3
    pad_x = 78
    pad_y = 40 + rng.byte() % 22
    inner = HEIGHT - pad_y * 2
    # Vary where the fan opens and how far it travels before it commits.
    entry_y = HEIGHT / 2 + rng.between(-34, 34)
    exit_y = HEIGHT / 2 + rng.between(-24, 24)
    spread = rng.between(0.55, 1.0)
    hot = rng.byte() % lanes
    parts = []
    for i in range(lanes):
        centred = (i + 1) / (lanes + 1) - 0.5
        y = HEIGHT / 2 + centred * inner * spread
        bend = pad_x + (WIDTH - pad_x * 2) * rng.between(0.22, 0.5)
        lit = i == hot
        colour, width = (ACCENT, 3.0) if lit else (SOFT, 1.4)
        parts.append(
            f'<path d="M{pad_x} {entry_y:.1f} C{bend:.1f} {entry_y:.1f}, {bend:.1f} {y:.1f}, '
            f'{bend + 46:.1f} {y:.1f} H{WIDTH - pad_x - 66} '
            f'C{WIDTH - pad_x - 22} {y:.1f}, {WIDTH - pad_x - 22} {exit_y:.1f}, '
            f'{WIDTH - pad_x} {exit_y:.1f}" stroke="{colour}" stroke-width="{width}" '
            f'fill="none" stroke-linecap="round" opacity="{0.95 if lit else 0.4}"/>'
        )
        parts.append(
            f'<circle cx="{bend + 46:.1f}" cy="{y:.1f}" r="{5 if lit else 3.5}" '
            f'fill="{colour}" opacity="{1 if lit else 0.55}"/>'
        )
    for cx, cy in ((pad_x, entry_y), (WIDTH - pad_x, exit_y)):
        parts.append(
            f'<circle cx="{cx}" cy="{cy:.1f}" r="10" fill="{SURFACE}" '
            f'stroke="{TEXT}" stroke-width="2.5"/>'
        )
    return "".join(parts) + _glyph(mark)


def _mesh(rng: _Rng, mark: str) -> str:
    """Several agents, one answer: a small network with a single lit path."""
    cols = 5 + rng.byte() % 2
    rows = 3
    pad_x, pad_y = 110, 66
    step_x = (WIDTH - pad_x * 2) / (cols - 1)
    step_y = (HEIGHT - pad_y * 2) / (rows - 1)
    points = [
        [
            (pad_x + step_x * c + rng.between(-11, 11), pad_y + step_y * r + rng.between(-13, 13))
            for r in range(rows)
        ]
        for c in range(cols)
    ]
    lit = [rng.byte() % rows for _ in range(cols)]
    parts = []
    for c in range(cols - 1):
        for a in range(rows):
            for b in range(rows):
                on = a == lit[c] and b == lit[c + 1]
                if not on and rng.unit() > 0.42:
                    continue
                x1, y1 = points[c][a]
                x2, y2 = points[c + 1][b]
                parts.append(
                    f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" '
                    f'stroke="{ACCENT if on else SOFT}" stroke-width="{2.6 if on else 1}" '
                    f'opacity="{0.95 if on else 0.22}"/>'
                )
    for c in range(cols):
        for r in range(rows):
            x, y = points[c][r]
            on = r == lit[c]
            parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{6 if on else 3.4}" '
                f'fill="{ACCENT if on else SOFT}" opacity="{1 if on else 0.4}"/>'
            )
    return "".join(parts) + _glyph(mark)


COMPOSITIONS = (_signal, _routing, _mesh)


def cover_svg(slug: str, vertical: str = "general") -> str:
    """Return the inline SVG cover for one slug. Decorative, so aria-hidden."""
    if not slug:
        raise ValueError("a cover needs a slug to derive itself from")
    rng = _Rng(slug)
    mark = VERTICAL_GLYPH.get(vertical, VERTICAL_GLYPH["general"])
    draw = COMPOSITIONS[hashlib.sha256(slug.encode("utf-8")).digest()[0] % len(COMPOSITIONS)]
    return (
        f'<svg class="cover" xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" aria-hidden="true" focusable="false">'
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{GROUND}"/>'
        f"{draw(rng, mark)}"
        f"</svg>"
    )


def composition_of(slug: str) -> str:
    """Which composition a slug draws. Exposed so tests can assert the spread."""
    return COMPOSITIONS[
        hashlib.sha256(slug.encode("utf-8")).digest()[0] % len(COMPOSITIONS)
    ].__name__.lstrip("_")


VERTICAL_OF_SLUG_SOURCE = "registry.json"


def vertical_for(slug: str, registry: dict) -> str:
    """The catalog's vertical for a solution slug, or the cross-industry mark."""
    for stack in registry.get("stacks", []):
        if stack.get("stack", "").replace("_", "-") == slug:
            return stack.get("vertical", "general")
    return "general"


def _refresh_field_notes() -> int:
    """Write the featured workshop's cover into field-notes.json.

    Run explicitly when a consumer uses the generated cover. Only the featured
    cover and its catalog-derived vertical are updated.
    """
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    notes_path = root / "field-notes.json"
    notes = json.loads(notes_path.read_text(encoding="utf-8"))
    registry = json.loads((root / VERTICAL_OF_SLUG_SOURCE).read_text(encoding="utf-8"))

    featured = notes["featured_workshop"]
    vertical = vertical_for(featured["slug"], registry)
    featured["vertical"] = vertical
    featured["cover"] = cover_svg(featured["slug"], vertical)
    notes_path.write_text(json.dumps(notes, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"field-notes.json: cover for {featured['slug']} ({vertical}), "
        f"{len(featured['cover'].encode('utf-8'))} bytes, {composition_of(featured['slug'])}"
    )
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Refresh the featured workshop's decorative SVG in field-notes.json."
    )
    parser.parse_args()
    raise SystemExit(_refresh_field_notes())
