#!/usr/bin/env python3
"""Build a complete downloadable solution bundle from its export manifest."""

import argparse
import json
import re
import stat
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

# The Microsoft Clarity block is a hosting artifact stamped on the published
# site (see tools/clarity_tag.py); bundled pages ship without it so analytics
# changes never rebuild a bundle. Kept inline so this file runs standalone.
CLARITY_BLOCK_RE = re.compile(
    rb"<!-- clarity:start -->.*?<!-- clarity:end -->\n?", re.DOTALL
)

# Every archive member gets the same timestamp and a normalized file mode so
# that the bundle bytes depend only on the repository content, never on when
# or where the checkout was made. Release publishing compares these bytes.
FIXED_DATE_TIME = (1980, 1, 1, 0, 0, 0)


def member_info(path, name):
    info = zipfile.ZipInfo(name, date_time=FIXED_DATE_TIME)
    executable = path.stat().st_mode & stat.S_IXUSR
    info.external_attr = ((0o100755 if executable else 0o100644) & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def bundle_bytes(path):
    data = path.read_bytes()
    if path.suffix.lower() == ".html":
        return CLARITY_BLOCK_RE.sub(b"", data)
    return data


def explicit_bundle_files(paths, bundle, declared=None):
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
        if path.resolve() in {bundle.resolve(), (declared or bundle).resolve()}:
            raise ValueError("A source bundle cannot include itself")
        if not path.is_file():
            raise FileNotFoundError(path)
        files.add(path)
    return files


def build(manifest_path, output=None):
    """Write the bundle declared by ``manifest_path``.

    ``output`` overrides the destination (for example a release staging
    directory); the declared ``bundle.path`` is still never packaged.
    """
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    declared = ROOT / manifest["bundle"]["path"]
    bundle = Path(output) if output is not None else declared
    package_dir = manifest_path.parent

    include_paths = manifest["bundle"].get("include_paths")
    if include_paths is not None:
        files = explicit_bundle_files(include_paths, bundle, declared)
    else:
        files = {
            path for path in package_dir.rglob("*")
            if path.is_file()
            and path != bundle
            and path != declared
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

    bundle.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            name = path.relative_to(ROOT).as_posix()
            if include_paths is not None:
                info = zipfile.ZipInfo(name)
                info.compress_type = zipfile.ZIP_DEFLATED
            else:
                info = member_info(path, name)
            archive.writestr(info, bundle_bytes(path))
    return bundle, len(files)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the bundle here instead of the manifest's bundle.path.",
    )
    args = parser.parse_args()
    output = args.output.resolve() if args.output else None
    bundle, count = build(args.manifest.resolve(), output)
    shown = bundle.relative_to(ROOT) if bundle.is_relative_to(ROOT) else bundle
    print(f"[OK] Wrote {shown} with {count} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
