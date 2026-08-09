#!/usr/bin/env python3
"""Draw deterministic evidence boxes on existing screenshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent


def font(size: int, bold: bool = False):
    names = [
        (
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Arial.ttf"
        ),
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for name in names:
        path = Path(name)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default()


def annotate(item: dict) -> None:
    source = ROOT / item["source"]
    target = ROOT / item["annotated"]
    image = Image.open(source).convert("RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    for index, box in enumerate(item.get("boxes", []), start=1):
        x = int(box["x"])
        y = int(box["y"])
        width = int(box["width"])
        height = int(box["height"])
        color = (22, 163, 74, 255)
        fill = (22, 163, 74, 28)
        draw.rounded_rectangle(
            (x, y, x + width, y + height),
            radius=8,
            outline=color,
            width=5,
            fill=fill,
        )
        label = str(box.get("label") or f"Visible anchor {index}")
        text_font = font(16, bold=True)
        bounds = draw.textbbox((0, 0), label, font=text_font)
        label_width = bounds[2] - bounds[0] + 18
        label_height = bounds[3] - bounds[1] + 12
        label_y = max(2, y - label_height - 3)
        draw.rounded_rectangle(
            (x, label_y, x + label_width, label_y + label_height),
            radius=6,
            fill=(22, 163, 74, 236),
        )
        draw.text(
            (x + 9, label_y + 5),
            label,
            fill=(255, 255, 255, 255),
            font=text_font,
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, format="PNG", optimize=True)


def build(spec_path: Path) -> tuple[int, int]:
    document = json.loads(spec_path.read_text(encoding="utf-8"))
    reusable = 0
    reshoot = 0
    for item in document["captures"]:
        if item["status"] == "reusable":
            annotate(item)
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
