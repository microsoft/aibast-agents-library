#!/usr/bin/env python3
"""Build a complete downloadable solution bundle from its export manifest."""

import argparse
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def build(manifest_path):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bundle = ROOT / manifest["bundle"]["path"]
    package_dir = manifest_path.parent
    bundle.parent.mkdir(parents=True, exist_ok=True)

    files = {
        path for path in package_dir.rglob("*")
        if path.is_file()
        and path != bundle
        and not any(
            part.startswith(".") or part == "__pycache__"
            for part in path.relative_to(package_dir).parts
        )
    }
    for item in manifest["files"]:
        if item.get("status") == "pending_capture":
            continue
        path = ROOT / item["path"]
        if not path.exists():
            raise FileNotFoundError(path)
        files.add(path)

    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, path.relative_to(ROOT).as_posix())
    return bundle, len(files)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    bundle, count = build(args.manifest.resolve())
    print(f"[OK] Wrote {bundle.relative_to(ROOT)} with {count} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
