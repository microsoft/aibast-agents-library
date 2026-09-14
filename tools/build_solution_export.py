#!/usr/bin/env python3
"""Build a complete downloadable solution bundle from its export manifest."""

import argparse
import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

# The Microsoft Clarity block is a hosting artifact stamped on the published
# site (see tools/clarity_tag.py); bundled pages ship without it so analytics
# changes never rebuild a bundle. Kept inline so this file runs standalone.
CLARITY_BLOCK_RE = re.compile(
    rb"<!-- clarity:start -->.*?<!-- clarity:end -->\n?", re.DOTALL
)


def bundle_bytes(path):
    data = path.read_bytes()
    if path.suffix.lower() == ".html":
        return CLARITY_BLOCK_RE.sub(b"", data)
    return data


def explicit_bundle_files(paths, bundle):
    if not isinstance(paths, list) or not paths:
        raise ValueError("bundle.include_paths must be a non-empty list")
    files = set()
    for value in paths:
        if not isinstance(value, str):
            raise ValueError("bundle.include_paths entries must be repository-relative paths")
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts or any(
            part.startswith(".") or part == "__pycache__" for part in relative.parts
        ):
            raise ValueError(f"Unsafe bundle path: {value}")
        path = ROOT / relative
        if not path.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError(f"Bundle path escapes the repository: {value}")
        if path.resolve() == bundle.resolve():
            raise ValueError("A source bundle cannot include itself")
        if not path.is_file():
            raise FileNotFoundError(path)
        files.add(path)
    return files


def build(manifest_path):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bundle = ROOT / manifest["bundle"]["path"]
    package_dir = manifest_path.parent
    bundle.parent.mkdir(parents=True, exist_ok=True)

    include_paths = manifest["bundle"].get("include_paths")
    if include_paths is not None:
        files = explicit_bundle_files(include_paths, bundle)
    else:
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
            name = path.relative_to(ROOT).as_posix()
            info = (
                zipfile.ZipInfo(name)
                if include_paths is not None
                else zipfile.ZipInfo.from_file(path, name)
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, bundle_bytes(path))
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
