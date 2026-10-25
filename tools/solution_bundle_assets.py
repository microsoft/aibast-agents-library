#!/usr/bin/env python3
"""Build and compare the solution source bundles published as release assets.

Every ``solutions/<slug>/export-manifest.json`` declares one source bundle
(``bundle.path``, named ``<slug>-source.zip``). The bundles are generated from
files already in the repository, so they are published as assets on the
rolling ``solution-bundles`` release instead of being committed. This module is
the single entry point the publishing workflow uses:

    python tools/solution_bundle_assets.py build --out dist/solution-bundles
    python tools/solution_bundle_assets.py same PUBLISHED.zip BUILT.zip

``build`` writes every bundle with the deterministic bundler in
``tools/build_solution_export.py`` plus a ``SHA256SUMS`` file. ``same`` exits 0
when a published asset matches a fresh build: byte-identical, or (if a
different zlib produced different compressed bytes) identical member names,
member contents and member modes.
"""

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import build_solution_export  # noqa: E402


RELEASE_TAG = "solution-bundles"
SUMS_NAME = "SHA256SUMS"


def bundle_manifests(root=None):
    """Return ``(asset_name, manifest_path)`` for every declared source bundle."""
    root = Path(root or build_solution_export.ROOT)
    rows = []
    for manifest_path in sorted((root / "solutions").glob("*/export-manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        bundle_path = (manifest.get("bundle") or {}).get("path")
        if not bundle_path:
            continue
        name = Path(bundle_path).name
        slug = manifest_path.parent.name
        if name != f"{slug}-source.zip":
            raise ValueError(
                f"{manifest_path}: bundle.path must end in {slug}-source.zip, got {bundle_path}"
            )
        rows.append((name, manifest_path))
    names = [name for name, _ in rows]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate solution bundle asset names")
    return rows


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_all(out, root=None):
    """Build every bundle into ``out`` and write ``SHA256SUMS``."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    sums = []
    for name, manifest_path in bundle_manifests(root):
        target = out / name
        _bundle, count = build_solution_export.build(manifest_path, target)
        sums.append((sha256_file(target), name))
        print(f"built {name} ({count} files)")
    (out / SUMS_NAME).write_text(
        "".join(f"{digest}  {name}\n" for digest, name in sums), encoding="utf-8"
    )
    return sums


def _members(path):
    with zipfile.ZipFile(path) as archive:
        return [
            (info.filename, info.external_attr >> 16, archive.read(info))
            for info in archive.infolist()
        ]


def compare(published, built):
    """Return "identical", "content-identical" or "different"."""
    if sha256_file(published) == sha256_file(built):
        return "identical"
    try:
        return "content-identical" if _members(published) == _members(built) else "different"
    except zipfile.BadZipFile:
        return "different"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build", help="Build every source bundle")
    build_parser.add_argument("--out", type=Path, required=True)
    same_parser = commands.add_parser("same", help="Compare a published asset to a build")
    same_parser.add_argument("published", type=Path)
    same_parser.add_argument("built", type=Path)
    commands.add_parser("list", help="Print every source bundle asset name")
    args = parser.parse_args(argv)

    if args.command == "build":
        sums = build_all(args.out.resolve())
        print(f"Built {len(sums)} solution source bundles in {args.out}")
        return 0
    if args.command == "list":
        for name, _manifest in bundle_manifests():
            print(name)
        return 0
    result = compare(args.published, args.built)
    print(result)
    return 0 if result != "different" else 1


if __name__ == "__main__":
    raise SystemExit(main())
