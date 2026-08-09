#!/usr/bin/env python3
"""Build labeled browser walkthrough GIFs and contact sheets from screenshots."""

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def font(size, bold=False):
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
             "/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
    ]
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default()


def fit(image, width, height):
    canvas = Image.new("RGB", (width, height), "#f7f4ef")
    copy = image.convert("RGB")
    copy.thumbnail((width, height), Image.Resampling.LANCZOS)
    x = (width - copy.width) // 2
    y = (height - copy.height) // 2
    canvas.paste(copy, (x, y))
    return canvas


def decorate(image, label, index, total, watermark):
    header = 54
    footer = 20
    frame = Image.new("RGB", (image.width, image.height + header + footer), "#242424")
    frame.paste(image, (0, header))
    draw = ImageDraw.Draw(frame)
    draw.text((18, 14), label, fill="#ffffff", font=font(21, bold=True))
    step = f"{index}/{total}"
    box = draw.textbbox((0, 0), step, font=font(16, bold=True))
    draw.text(
        (frame.width - (box[2] - box[0]) - 18, 17),
        step,
        fill="#fd8ea1",
        font=font(16, bold=True),
    )
    progress = int(frame.width * index / total)
    draw.rectangle((0, frame.height - footer, frame.width, frame.height), fill="#dedede")
    draw.rectangle((0, frame.height - footer, progress, frame.height), fill="#b11f4b")
    mark_box = draw.textbbox((0, 0), watermark, font=font(12))
    draw.text(
        (frame.width - (mark_box[2] - mark_box[0]) - 10, frame.height - 17),
        watermark,
        fill="#242424",
        font=font(12),
    )
    return frame


def build(manifest_path, output_path, contact_path=None):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    width = manifest.get("width", 1280)
    height = manifest.get("height", 780)
    watermark = manifest.get("watermark", "rapp-browserfilm")
    frames = []
    durations = []
    decorated = []
    for index, item in enumerate(manifest["frames"], start=1):
        source = (manifest_path.parent / item["file"]).resolve()
        frame = decorate(
            fit(Image.open(source), width, height),
            item["label"],
            index,
            len(manifest["frames"]),
            watermark,
        )
        decorated.append(frame)
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
        durations.append(item.get("duration_ms", 1500))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )

    if contact_path:
        columns = 2
        rows = math.ceil(len(decorated) / columns)
        thumb_width = width // 2
        thumb_height = (height + 74) // 2
        sheet = Image.new(
            "RGB",
            (thumb_width * columns, thumb_height * rows),
            "#f7f4ef",
        )
        for index, frame in enumerate(decorated):
            thumb = frame.copy()
            thumb.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
            x = (index % columns) * thumb_width
            y = (index // columns) * thumb_height
            sheet.paste(thumb, (x, y))
        contact_path.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(contact_path, quality=88, optimize=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--contact-sheet", type=Path)
    args = parser.parse_args()
    build(
        args.manifest.resolve(),
        args.output.resolve(),
        args.contact_sheet.resolve() if args.contact_sheet else None,
    )
    print(f"[OK] rapp-browserfilm wrote {args.output}")
    if args.contact_sheet:
        print(f"[OK] contact sheet wrote {args.contact_sheet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
