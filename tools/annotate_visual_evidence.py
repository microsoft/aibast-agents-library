#!/usr/bin/env python3
"""Draw deterministic evidence boxes on existing screenshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent


FONT_CANDIDATES = {
    False: [
        "C:/Windows/Fonts/segoeui.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    True: [
        "C:/Windows/Fonts/segoeuib.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
}

# Microsoft Fluent palette: brand blue callouts on a softly dimmed screen.
ACCENT = (15, 108, 189)          # #0F6CBD
ACCENT_DARK = (17, 94, 163)      # #115EA3
INK = (36, 36, 36)               # #242424
SCALE = 2                        # supersampling factor for smooth edges


def font(size: int, bold: bool = False):
    for name in FONT_CANDIDATES[bold]:
        path = Path(name)
        if not path.exists():
            continue
        try:
            loaded = ImageFont.truetype(str(path), size)
            if bold and path.name == "SFNS.ttf":
                try:
                    loaded.set_variation_by_name("Semibold")
                except (OSError, ValueError, AttributeError):
                    pass
            return loaded
        except OSError:
            continue
    return ImageFont.load_default()


def _scaled(box: dict) -> tuple[int, int, int, int]:
    x, y = int(box["x"]) * SCALE, int(box["y"]) * SCALE
    return x, y, x + int(box["width"]) * SCALE, y + int(box["height"]) * SCALE


def _pill(draw, xy, text, text_font, fill, color):
    x, y = xy
    bounds = draw.textbbox((0, 0), text, font=text_font)
    w = bounds[2] - bounds[0] + 22 * SCALE
    h = bounds[3] - bounds[1] + 12 * SCALE
    draw.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=fill)
    draw.text((x + 11 * SCALE - bounds[0], y + 6 * SCALE - bounds[1]), text, fill=color, font=text_font)
    return w, h


def annotate(item: dict, root: Path = ROOT) -> None:
    """Spotlight the evidence: dim the frame, keep each box bright, outline it in brand blue with a
    numbered badge and a label pill, and add an optional caption bar (item["caption"]). Output keeps
    the source dimensions; rendering is supersampled for smooth edges and is deterministic."""
    source = root / item["source"]
    target = root / item["annotated"]
    base = Image.open(source).convert("RGB")
    width, height = base.size
    big = base.resize((width * SCALE, height * SCALE), Image.LANCZOS).convert("RGBA")
    boxes = item.get("boxes", [])

    # 1. Spotlight: dim everything, then cut the evidence areas back out.
    shade = Image.new("RGBA", big.size, (20, 24, 32, 64))
    holes = Image.new("L", big.size, 0)
    hole_draw = ImageDraw.Draw(holes)
    for box in boxes:
        x0, y0, x1, y1 = _scaled(box)
        hole_draw.rounded_rectangle((x0, y0, x1, y1), radius=10 * SCALE, fill=255)
    shade.putalpha(Image.eval(holes, lambda v: 0 if v else 64))
    canvas = Image.alpha_composite(big, shade)

    # 2. Soft shadow under each outline.
    glow = Image.new("RGBA", big.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for box in boxes:
        x0, y0, x1, y1 = _scaled(box)
        glow_draw.rounded_rectangle((x0 - 2 * SCALE, y0 - 2 * SCALE, x1 + 2 * SCALE, y1 + 2 * SCALE),
                                    radius=12 * SCALE, outline=(15, 108, 189, 70), width=6 * SCALE)
    canvas = Image.alpha_composite(canvas, glow)
    draw = ImageDraw.Draw(canvas, "RGBA")

    badge_font = font(12 * SCALE, bold=True)
    for index, box in enumerate(boxes, start=1):
        x0, y0, x1, y1 = _scaled(box)
        draw.rounded_rectangle((x0, y0, x1, y1), radius=10 * SCALE, outline=ACCENT + (255,), width=3 * SCALE)
        # numbered badge on the top-left corner
        r = 11 * SCALE
        cx, cy = x0, y0
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ACCENT_DARK + (255,), outline=(255, 255, 255, 255), width=2 * SCALE)
        num = str(index)
        nb = draw.textbbox((0, 0), num, font=badge_font)
        draw.text((cx - (nb[2] - nb[0]) / 2 - nb[0], cy - (nb[3] - nb[1]) / 2 - nb[1]), num, fill=(255, 255, 255, 255), font=badge_font)

    # Bottom bar: the step caption, then a numbered legend matching the badges (labels never cover the UI).
    caption = item.get("caption")
    labels = [str(box.get("label") or f"Visible anchor {i}") for i, box in enumerate(boxes, start=1)]
    if caption or labels:
        cap_font = font(15 * SCALE, bold=True)
        leg_font = font(13 * SCALE)
        line = 26 * SCALE
        entries, row, used = [], [], 20 * SCALE
        for i, text in enumerate(labels, start=1):
            w = draw.textbbox((0, 0), text, font=leg_font)[2] + 48 * SCALE
            if row and used + w > (width - 20) * SCALE:
                entries.append(row)
                row, used = [], 20 * SCALE
            row.append((i, text))
            used += w
        if row:
            entries.append(row)
        bar_h = ((1 if caption else 0) + len(entries)) * line + 18 * SCALE
        top = height * SCALE - bar_h
        draw.rectangle((0, top, width * SCALE, height * SCALE), fill=(27, 27, 31, 236))
        draw.rectangle((0, top, 6 * SCALE, height * SCALE), fill=ACCENT + (255,))
        y = top + 9 * SCALE
        if caption:
            cb = draw.textbbox((0, 0), caption, font=cap_font)
            draw.text((20 * SCALE, y + (line - (cb[3] - cb[1])) / 2 - cb[1]), caption, fill=(255, 255, 255, 255), font=cap_font)
            y += line
        for row in entries:
            x = 20 * SCALE
            for i, text in row:
                r = 9 * SCALE
                cy = y + line / 2
                draw.ellipse((x, cy - r, x + 2 * r, cy + r), fill=ACCENT + (255,))
                nb = draw.textbbox((0, 0), str(i), font=badge_font)
                draw.text((x + r - (nb[2] - nb[0]) / 2 - nb[0], cy - (nb[3] - nb[1]) / 2 - nb[1]), str(i),
                          fill=(255, 255, 255, 255), font=badge_font)
                tb = draw.textbbox((0, 0), text, font=leg_font)
                draw.text((x + 2 * r + 8 * SCALE, cy - (tb[3] - tb[1]) / 2 - tb[1]), text, fill=(232, 232, 236, 255), font=leg_font)
                x += 2 * r + 8 * SCALE + (tb[2] - tb[0]) + 22 * SCALE
            y += line

    out = canvas.convert("RGB").resize((width, height), Image.LANCZOS)
    target.parent.mkdir(parents=True, exist_ok=True)
    # 256-colour octree palette: keeps the brand blue exact at about a fifth of the RGB size (the Pages artifact is
    # capped at 900 MB, and full-conversation frames are tall)
    out.convert("RGB").quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(
        target, format="PNG", optimize=True)


def build(spec_path: Path, root: Path = ROOT) -> tuple[int, int]:
    document = json.loads(spec_path.read_text(encoding="utf-8"))
    reusable = 0
    reshoot = 0
    for item in document["captures"]:
        if item["status"] == "reusable":
            annotate(item, root=root)
            reusable += 1
        elif item["status"] == "reshoot_required":
            reshoot += 1
    return reusable, reshoot


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()
    reusable, reshoot = build(args.spec.resolve())
    print(
        f"[OK] Annotated {reusable} reusable captures; "
        f"{reshoot} require reshoot"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
