#!/usr/bin/env python3
"""Build the allowlisted GitHub Pages artifact for the AI Academy."""

from __future__ import annotations

import argparse
import bisect
import html
import json
import os
import posixpath
import re
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from urllib.request import Request, urlopen


MANIFEST_SCHEMA = "aibast-pages-artifact/1.0"
MANIFEST_NAME = "pages-manifest.json"
ARTIFACT_BYTE_LIMIT = 900_000_000
FILE_BYTE_LIMIT = 100 * 1024 * 1024
EXPECTED_ACADEMY_COURSES = 51

INCLUDE = "include"
EXCLUDED_SOLUTION_BLOB = "excluded-solution-blob"
OMIT = "omit"

SOLUTION_BLOB_EXCLUSIONS = frozenset({".gif", ".zip"})
FORBIDDEN_PAGES_SUFFIXES = frozenset({".gif", ".zip"})

ROOT_PUBLIC_SUFFIXES = frozenset(
    {".cmd", ".command", ".html", ".json", ".ps1", ".sh"}
)
ROOT_PUBLIC_FILES = frozenset(
    {
        ".nojekyll",
        "CONSTITUTION.md",
        "CONTRIBUTING.md",
        "LICENSE",
        "README.md",
        "SECURITY.md",
        "skill.md",
    }
)
PUBLIC_DIRECTORY_ROOTS = frozenset(
    {"academy", "docs", "reports", "skills", "solutions", "state"}
)
BETA_PUBLIC_FILES = frozenset(
    {
        "beta/LICENSE",
        "beta/README.md",
        "beta/THIRD-PARTY-NOTICES.md",
        "beta/VERSION",
        "beta/build/icon.svg",
        "beta/frontier.ps1",
        "beta/frontier.sh",
        "beta/index.html",
        "beta/install.cmd",
        "beta/install.sh",
        "beta/show-mode.html",
        "beta/ui/index.html",
        "beta/ui/renderer.js",
        "beta/ui/show-mode-tour.js",
    }
)
# The installers are vendored with the production identity baked in. When the
# artifact is built for any other ring (a staging fork, or a non-main branch),
# their defaults are rendered to that ring so the served one-liner installs the
# ring's own kernel. The repository files themselves are never modified.
CANONICAL_OWNER = "microsoft"
CANONICAL_REPO = "aibast-agents-library"
CANONICAL_BRANCH = "main"
INSTALLER_PATHS = frozenset(
    {
        "install.sh",
        "install.ps1",
        "install.cmd",
        "docs/install.sh",
        "docs/install.ps1",
        "docs/install.cmd",
    }
)

# The workshop lane skills name the repository and branch they pull workshops
# from. Like the installers, they are rendered to the ring that serves them.
RING_SKILL_PATHS = frozenset(
    {
        "skills/aibast-easy-mode-brainstem/SKILL.md",
        "skills/aibast-easy-mode-copilot/SKILL.md",
    }
)

RAPP_BRAINSTEM_PUBLIC_FILES = frozenset(
    {"rapp_brainstem/README.md", "rapp_brainstem/VERSION"}
)

NEVER_COPY_TOP_LEVEL = frozenset(
    {".git", ".github", "agents", "browser-audit", "tests", "tools"}
)
NEVER_COPY_COMPONENTS = frozenset(
    {
        ".cache",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "agents",
        "dist",
        "node_modules",
        "release",
        "releases",
        "tests",
        "tools",
    }
)
SOURCE_SCAN_ROOTS = (
    "academy",
    "docs",
    "reports",
    "skills",
    "solutions",
    "state",
    "beta",
    "rapp_brainstem",
    "agents",
    "tools",
)
GIT_RECURSIVE_ROOTS = SOURCE_SCAN_ROOTS

ACADEMY_PAGE_FIELDS = {
    "quest_url": "quest.html",
    "field_guide_url": "field-guide.html",
    "manual_url": "manual-tutorial.html",
    "evidence_url": "evidence-report.html",
}

OWNER_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
REF_RE = re.compile(r"^[^\x00-\x20~^:?*\\\[\]]+$")
TAG_RE = re.compile(r"""<(?:"[^"]*"|'[^']*'|[^'">])*>""", re.DOTALL)
ATTRIBUTE_RE = re.compile(
    r"""(?<![\w.:-])(?P<attr>href|src)(?P<equals>\s*=\s*)"""
    r"""(?:(?P<quote>["'])(?P<quoted_url>.*?)(?P=quote)|"""
    r"""(?P<bare_url>[^\s"'=<>`]+))""",
    re.IGNORECASE | re.DOTALL,
)
DYNAMIC_URL_MARKERS = ("${", "{{", "{%", "<%")
LIBRARY_DYNAMIC_ZIP_HREF = 'href="${esc(solutionDownloads.zip)}"'
LIBRARY_DYNAMIC_ZIP_SOURCE = (
    "zip: `${base}-copilot-studio-solution.zip`"
)


class BuildError(RuntimeError):
    """Raised when the Pages artifact cannot be built safely."""


@dataclass(frozen=True)
class SourceEntry:
    path: PurePosixPath
    size: int | None
    mode: str
    object_id: str | None
    tracked: bool
    present: bool

    @property
    def is_symlink(self) -> bool:
        return self.mode == "120000"

    @property
    def is_regular(self) -> bool:
        return self.mode.startswith("100")


@dataclass(frozen=True)
class AcademyRequirements:
    page_paths: frozenset[PurePosixPath]
    skill_paths: frozenset[PurePosixPath]


def _pure_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise BuildError(f"Unsafe repository path: {value}")
    return path


def _git_root(root: Path) -> Path | None:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
    )
    if result.returncode:
        return None
    candidate = Path(result.stdout.strip()).resolve()
    return candidate if candidate == root else None


def _parse_ls_tree(data: bytes) -> dict[PurePosixPath, SourceEntry]:
    entries: dict[PurePosixPath, SourceEntry] = {}
    for record in data.split(b"\0"):
        if not record:
            continue
        try:
            header, raw_path = record.split(b"\t", 1)
            mode, object_type, object_id = header.split()
            path = _pure_path(raw_path.decode("utf-8", "surrogateescape"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise BuildError("Could not parse git tree inventory") from exc
        if object_type != b"blob":
            continue
        entries[path] = SourceEntry(
            path=path,
            size=None,
            mode=mode.decode("ascii"),
            object_id=object_id.decode("ascii"),
            tracked=True,
            present=False,
        )
    return entries


def collect_git_entries(root: Path) -> dict[PurePosixPath, SourceEntry]:
    if _git_root(root) is None:
        return {}

    environment = os.environ.copy()
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    commands = [
        ["git", "-C", str(root), "ls-tree", "-z", "HEAD"],
        [
            "git",
            "-C",
            str(root),
            "ls-tree",
            "-rz",
            "HEAD",
            "--",
            *GIT_RECURSIVE_ROOTS,
        ],
    ]
    entries: dict[PurePosixPath, SourceEntry] = {}
    for command in commands:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
        )
        if result.returncode:
            message = result.stderr.decode("utf-8", "replace").strip()
            raise BuildError(f"Git inventory failed: {message}")
        entries.update(_parse_ls_tree(result.stdout))
    return entries


def _filesystem_entry(root: Path, path: Path) -> SourceEntry:
    relative = _pure_path(path.relative_to(root).as_posix())
    file_stat = path.lstat()
    if stat.S_ISLNK(file_stat.st_mode):
        mode = "120000"
    elif stat.S_ISREG(file_stat.st_mode):
        mode = "100755" if file_stat.st_mode & stat.S_IXUSR else "100644"
    else:
        mode = "special"
    return SourceEntry(
        path=relative,
        size=file_stat.st_size,
        mode=mode,
        object_id=None,
        tracked=False,
        present=True,
    )


def collect_filesystem_entries(root: Path) -> dict[PurePosixPath, SourceEntry]:
    entries: dict[PurePosixPath, SourceEntry] = {}
    for path in root.iterdir():
        if path.is_file() or path.is_symlink():
            entry = _filesystem_entry(root, path)
            entries[entry.path] = entry

    for relative_root in SOURCE_SCAN_ROOTS:
        scan_root = root / relative_root
        if not scan_root.exists() and not scan_root.is_symlink():
            continue
        if scan_root.is_symlink():
            entry = _filesystem_entry(root, scan_root)
            entries[entry.path] = entry
            continue
        for current_root, directory_names, file_names in os.walk(
            scan_root, followlinks=False
        ):
            current = Path(current_root)
            for directory_name in list(directory_names):
                directory = current / directory_name
                if directory.is_symlink():
                    entry = _filesystem_entry(root, directory)
                    entries[entry.path] = entry
                    directory_names.remove(directory_name)
            for file_name in file_names:
                file_path = current / file_name
                entry = _filesystem_entry(root, file_path)
                entries[entry.path] = entry
    return entries


def collect_source_entries(root: Path) -> dict[PurePosixPath, SourceEntry]:
    entries = collect_git_entries(root)
    for path, filesystem_entry in collect_filesystem_entries(root).items():
        tracked = entries.get(path)
        entries[path] = SourceEntry(
            path=path,
            size=filesystem_entry.size,
            mode=filesystem_entry.mode,
            object_id=tracked.object_id if tracked is not None else None,
            tracked=tracked is not None,
            present=True,
        )
    return entries


def repository_uses_promisor_remote(root: Path) -> bool:
    if _git_root(root) is None:
        return False
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "config",
            "--get-regexp",
            r"^remote\..*\.promisor$",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
    )
    if result.returncode not in {0, 1}:
        raise BuildError("Could not inspect partial-clone configuration")
    return any(
        line.rsplit(maxsplit=1)[-1].lower() == "true"
        for line in result.stdout.splitlines()
        if line.strip()
    )


def _local_blob_sizes(
    root: Path, entries: dict[PurePosixPath, SourceEntry]
) -> dict[PurePosixPath, tuple[str, int]]:
    object_ids = sorted(
        {entry.object_id for entry in entries.values() if entry.object_id}
    )
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "cat-file",
            "--batch-check=%(objectname) %(objecttype) %(objectsize)",
        ],
        input="".join(f"{object_id}\n" for object_id in object_ids),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if result.returncode:
        message = result.stderr.strip()
        raise BuildError(f"Could not read local blob sizes: {message}")
    sizes_by_id: dict[str, int] = {}
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) != 3 or fields[1] != "blob":
            raise BuildError(f"Unexpected local git object metadata: {line}")
        sizes_by_id[fields[0]] = int(fields[2])

    hydrated: dict[PurePosixPath, tuple[str, int]] = {}
    for path, entry in entries.items():
        if entry.object_id in sizes_by_id:
            hydrated[path] = (entry.object_id, sizes_by_id[entry.object_id])
    return hydrated


def fetch_github_tree_metadata(
    owner: str, repo: str, ref: str
) -> dict[PurePosixPath, tuple[str, int]]:
    endpoint = (
        f"https://api.github.com/repos/{quote(owner, safe='')}/"
        f"{quote(repo, safe='')}/git/trees/{quote(ref, safe='')}?recursive=1"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "aibast-pages-builder",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(endpoint, headers=headers)
    try:
        with urlopen(request, timeout=60) as response:
            payload_bytes = response.read(25_000_001)
    except HTTPError as exc:
        raise BuildError(
            f"GitHub tree metadata request failed with HTTP {exc.code}"
        ) from exc
    except URLError as exc:
        raise BuildError(f"GitHub tree metadata request failed: {exc.reason}") from exc
    if len(payload_bytes) > 25_000_000:
        raise BuildError("GitHub tree metadata response exceeded 25 MB")
    try:
        payload = json.loads(payload_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BuildError("GitHub tree metadata response was not valid JSON") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("tree"), list):
        raise BuildError("GitHub tree metadata response did not contain a tree")
    if payload.get("truncated"):
        raise BuildError("GitHub tree metadata response was truncated")

    metadata: dict[PurePosixPath, tuple[str, int]] = {}
    for item in payload["tree"]:
        if not isinstance(item, dict) or item.get("type") != "blob":
            continue
        path_value = item.get("path")
        object_id = item.get("sha")
        size = item.get("size")
        if (
            not isinstance(path_value, str)
            or not isinstance(object_id, str)
            or not isinstance(size, int)
        ):
            raise BuildError("GitHub tree metadata contained an invalid blob entry")
        metadata[_pure_path(path_value)] = (object_id, size)
    return metadata


def hydrate_excluded_sizes(
    root: Path,
    entries: dict[PurePosixPath, SourceEntry],
    owner: str,
    repo: str,
    ref: str,
) -> dict[PurePosixPath, SourceEntry]:
    missing = {
        path: entry
        for path, entry in entries.items()
        if classify_source_path(path) == EXCLUDED_SOLUTION_BLOB
        and entry.size is None
    }
    if not missing:
        return entries

    if repository_uses_promisor_remote(root):
        metadata = fetch_github_tree_metadata(owner, repo, ref)
    else:
        metadata = _local_blob_sizes(root, missing)

    hydrated = dict(entries)
    for path, entry in missing.items():
        remote = metadata.get(path)
        if remote is None:
            raise BuildError(f"No size metadata is available for excluded asset: {path}")
        object_id, size = remote
        if entry.object_id and entry.object_id != object_id:
            raise BuildError(
                f"Excluded asset metadata does not match the checkout: {path}"
            )
        hydrated[path] = replace(entry, size=size)
    return hydrated


def _is_blocked_component(path: PurePosixPath) -> bool:
    if not path.parts:
        return True
    if path.parts[0] in NEVER_COPY_TOP_LEVEL:
        return True
    if any(part in NEVER_COPY_COMPONENTS for part in path.parts):
        return True
    if "build" in path.parts and path.as_posix() != "beta/build/icon.svg":
        return True
    return False


def classify_source_path(path: PurePosixPath) -> str:
    if not path.parts or path.name == MANIFEST_NAME:
        return OMIT

    path_text = path.as_posix()
    if (
        path.parts[0] == "solutions"
        and path.suffix.lower() in SOLUTION_BLOB_EXCLUSIONS
    ):
        return EXCLUDED_SOLUTION_BLOB
    if _is_blocked_component(path):
        return OMIT
    if len(path.parts) == 1:
        if path.name in ROOT_PUBLIC_FILES or path.suffix.lower() in ROOT_PUBLIC_SUFFIXES:
            return INCLUDE
        return OMIT

    top_level = path.parts[0]
    if top_level == "solutions":
        return INCLUDE
    if top_level in PUBLIC_DIRECTORY_ROOTS:
        return INCLUDE
    if top_level == "beta":
        return INCLUDE if path_text in BETA_PUBLIC_FILES else OMIT
    if top_level == "rapp_brainstem":
        return INCLUDE if path_text in RAPP_BRAINSTEM_PUBLIC_FILES else OMIT
    return OMIT


def _assert_regular_source(root: Path, entry: SourceEntry) -> Path:
    source = root.joinpath(*entry.path.parts)
    if entry.is_symlink:
        raise BuildError(f"Refusing symlink source: {entry.path}")
    if not entry.is_regular:
        raise BuildError(f"Refusing non-regular source: {entry.path}")
    if not entry.present or not source.is_file():
        raise BuildError(
            f"Required sparse-checkout input is missing from disk: {entry.path}"
        )
    if source.is_symlink():
        raise BuildError(f"Refusing symlink source: {entry.path}")
    try:
        source.resolve().relative_to(root)
    except ValueError as exc:
        raise BuildError(f"Source escapes repository root: {entry.path}") from exc
    return source


def plan_artifact(
    root: Path, entries: dict[PurePosixPath, SourceEntry]
) -> tuple[frozenset[PurePosixPath], dict[str, dict[str, int]]]:
    included: set[PurePosixPath] = set()
    excluded = {
        ".gif": {"count": 0, "bytes": 0},
        ".zip": {"count": 0, "bytes": 0},
    }

    for path in sorted(entries, key=lambda item: item.as_posix()):
        entry = entries[path]
        classification = classify_source_path(path)
        if classification == INCLUDE:
            source = _assert_regular_source(root, entry)
            size = source.stat().st_size
            if size > FILE_BYTE_LIMIT:
                raise BuildError(
                    f"Included file exceeds {FILE_BYTE_LIMIT} bytes: {path} ({size})"
                )
            included.add(path)
        elif classification == EXCLUDED_SOLUTION_BLOB:
            if entry.is_symlink or not entry.is_regular:
                raise BuildError(f"Refusing non-regular excluded asset: {path}")
            if entry.size is None:
                raise BuildError(f"Excluded asset has no size metadata: {path}")
            extension = path.suffix.lower()
            excluded[extension]["count"] += 1
            excluded[extension]["bytes"] += entry.size
    return frozenset(included), excluded


def _catalog_path(value: object, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise BuildError(f"{label} must be a non-empty repository-relative path")
    parsed = urlsplit(value)
    if (
        parsed.scheme
        or parsed.netloc
        or parsed.query
        or parsed.fragment
        or parsed.path.startswith("/")
    ):
        raise BuildError(f"{label} is not repository-relative: {value}")
    decoded = unquote(parsed.path)
    if "\\" in decoded or "\0" in decoded:
        raise BuildError(f"{label} contains an unsafe path: {value}")
    normalized = posixpath.normpath(decoded)
    if normalized in {"", ".", ".."} or normalized.startswith("../"):
        raise BuildError(f"{label} escapes the repository: {value}")
    return _pure_path(normalized)


def validate_academy_source(
    root: Path, included: frozenset[PurePosixPath]
) -> AcademyRequirements:
    always_required = {
        PurePosixPath(".nojekyll"),
        PurePosixPath("academy.html"),
        PurePosixPath("academy.json"),
        PurePosixPath("beta/index.html"),
        PurePosixPath("index.html"),
    }
    missing_basics = sorted(
        path.as_posix() for path in always_required if path not in included
    )
    if missing_basics:
        raise BuildError(
            "Required Pages entry points are missing: " + ", ".join(missing_basics)
        )

    academy_path = root / "academy.json"
    try:
        academy = json.loads(academy_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"Could not read academy.json: {exc}") from exc
    if not isinstance(academy, dict) or not isinstance(academy.get("courses"), list):
        raise BuildError("academy.json must contain a courses array")

    courses = academy["courses"]
    if len(courses) != EXPECTED_ACADEMY_COURSES:
        raise BuildError(
            f"academy.json must contain {EXPECTED_ACADEMY_COURSES} courses; "
            f"found {len(courses)}"
        )

    page_paths: dict[str, set[PurePosixPath]] = {
        field: set() for field in ACADEMY_PAGE_FIELDS
    }
    skill_paths: set[PurePosixPath] = set()
    skill_count = 0
    for index, course in enumerate(courses):
        if not isinstance(course, dict):
            raise BuildError(f"academy.json course {index} is not an object")
        slug = course.get("slug")
        label = f"academy.json course {slug or index}"
        for field, expected_name in ACADEMY_PAGE_FIELDS.items():
            path = _catalog_path(course.get(field), f"{label}.{field}")
            if path.name != expected_name:
                raise BuildError(
                    f"{label}.{field} must end in {expected_name}: {path}"
                )
            if path not in included:
                raise BuildError(f"Required Academy page is missing: {path}")
            page_paths[field].add(path)

        skills = course.get("skills")
        if not isinstance(skills, list):
            raise BuildError(f"{label}.skills must be an array")
        skill_count += len(skills)
        for skill_index, skill in enumerate(skills):
            if not isinstance(skill, dict):
                raise BuildError(f"{label}.skills[{skill_index}] is not an object")
            path = _catalog_path(
                skill.get("path"), f"{label}.skills[{skill_index}].path"
            )
            if path.name != "SKILL.md" or path.parts[0] != "solutions":
                raise BuildError(f"Academy skill path is not a solution SKILL.md: {path}")
            if path not in included:
                raise BuildError(f"Required Academy skill is missing: {path}")
            skill_paths.add(path)

    for field, paths in page_paths.items():
        if len(paths) != EXPECTED_ACADEMY_COURSES:
            raise BuildError(
                f"Academy {field} paths must contain "
                f"{EXPECTED_ACADEMY_COURSES} unique files; found {len(paths)}"
            )

    summary = academy.get("summary")
    if not isinstance(summary, dict):
        raise BuildError("academy.json must contain a summary object")
    if summary.get("courses") != len(courses):
        raise BuildError("academy.json summary.courses does not match courses")
    if summary.get("skills") != skill_count:
        raise BuildError("academy.json summary.skills does not match linked skills")
    if len(skill_paths) != skill_count:
        raise BuildError("academy.json contains duplicate skill paths")

    return AcademyRequirements(
        page_paths=frozenset().union(*page_paths.values()),
        skill_paths=frozenset(skill_paths),
    )


def _is_dynamic_url(value: str) -> bool:
    return any(marker in value for marker in DYNAMIC_URL_MARKERS)


def _relative_link_target(page: PurePosixPath, value: str) -> PurePosixPath | None:
    decoded_value = html.unescape(value.strip())
    if not decoded_value or _is_dynamic_url(decoded_value):
        return None
    if decoded_value.startswith("#") or decoded_value.startswith("//"):
        return None
    parsed = urlsplit(decoded_value)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    decoded_path = unquote(parsed.path)
    if "\\" in decoded_path or "\0" in decoded_path:
        raise BuildError(f"Unsafe relative link in {page}: {value}")
    if decoded_path.startswith("/"):
        normalized = posixpath.normpath(decoded_path.lstrip("/"))
    else:
        normalized = posixpath.normpath(
            posixpath.join(page.parent.as_posix(), decoded_path)
        )
    if normalized == ".":
        return PurePosixPath(".")
    if normalized == ".." or normalized.startswith("../"):
        raise BuildError(f"Relative link escapes the artifact in {page}: {value}")
    return _pure_path(normalized)


def _artifact_has_target(
    target: PurePosixPath, included: frozenset[PurePosixPath]
) -> bool:
    if target in included:
        return True
    index_path = (
        PurePosixPath("index.html")
        if target == PurePosixPath(".")
        else target / "index.html"
    )
    return index_path in included


def _repository_only_target(path: PurePosixPath) -> bool:
    if not path.parts:
        return False
    if path.parts[0] in {"agents", "tools"}:
        return True
    return len(path.parts) > 1 and path.parts[:2] == (
        "rapp_brainstem",
        "agents",
    )


def _can_rewrite(
    target: PurePosixPath,
    entry: SourceEntry | None,
) -> bool:
    if entry is None or entry.is_symlink or not entry.is_regular:
        return False
    if (
        target.parts
        and target.parts[0] == "solutions"
        and target.suffix.lower() in SOLUTION_BLOB_EXCLUSIONS
    ):
        return True
    return _repository_only_target(target)


def _raw_github_url(
    owner: str,
    repo: str,
    ref: str,
    target: PurePosixPath,
    original_value: str,
) -> str:
    parsed = urlsplit(html.unescape(original_value.strip()))
    raw_base = _raw_github_base(owner, repo, ref)
    return urlunsplit(
        (
            "https",
            "raw.githubusercontent.com",
            f"{urlsplit(raw_base).path}/{quote(target.as_posix(), safe='/@-._~')}",
            parsed.query,
            parsed.fragment,
        )
    )


def _raw_github_base(owner: str, repo: str, ref: str) -> str:
    raw_path = "/".join(
        (
            quote(owner, safe="-._~"),
            quote(repo, safe="-._~"),
            quote(ref, safe="/-._~"),
        )
    )
    return f"https://raw.githubusercontent.com/{raw_path}"


def _line_number(newlines: list[int], offset: int) -> int:
    return bisect.bisect_right(newlines, offset) + 1


def _attribute_url(match: re.Match[str]) -> str:
    return match.group("quoted_url") or match.group("bare_url")


def _render_attribute(match: re.Match[str], value: str) -> str:
    quote_character = match.group("quote") or ""
    return (
        f"{match.group('attr')}{match.group('equals')}"
        f"{quote_character}{value}{quote_character}"
    )


def rewrite_html(
    page: PurePosixPath,
    text: str,
    included: frozenset[PurePosixPath],
    entries: dict[PurePosixPath, SourceEntry],
    owner: str,
    repo: str,
    ref: str,
) -> tuple[str, int, list[str]]:
    rewritten_count = 0
    broken: list[str] = []
    newlines = [index for index, character in enumerate(text) if character == "\n"]

    def replace_tag(tag_match: re.Match[str]) -> str:
        def replace_attribute(match: re.Match[str]) -> str:
            nonlocal rewritten_count
            value = _attribute_url(match)
            absolute_offset = tag_match.start() + match.start()
            try:
                target = _relative_link_target(page, value)
            except BuildError as exc:
                broken.append(
                    f"{page}:{_line_number(newlines, absolute_offset)}: {exc}"
                )
                return match.group(0)
            if target is None or _artifact_has_target(target, included):
                return match.group(0)

            entry = entries.get(target)
            if _can_rewrite(target, entry):
                rewritten_count += 1
                raw_url = _raw_github_url(owner, repo, ref, target, value)
                return _render_attribute(
                    match, html.escape(raw_url, quote=False)
                )

            classification = classify_source_path(target)
            if entry is None:
                reason = "source target is not tracked or present"
            else:
                reason = f"target is not in the Pages allowlist ({classification})"
            broken.append(
                f"{page}:{_line_number(newlines, absolute_offset)}: "
                f"{match.group('attr')}={value!r} -> {target} ({reason})"
            )
            return match.group(0)

        return ATTRIBUTE_RE.sub(replace_attribute, tag_match.group(0))

    rewritten = TAG_RE.sub(replace_tag, text)
    if page == PurePosixPath("index.html") and LIBRARY_DYNAMIC_ZIP_HREF in text:
        occurrences = rewritten.count(LIBRARY_DYNAMIC_ZIP_SOURCE)
        if occurrences != 1:
            broken.append(
                "index.html: dynamic Copilot Studio ZIP link has no "
                "classifiable source expression"
            )
        else:
            replacement = (
                f"zip: `{_raw_github_base(owner, repo, ref)}/"
                "${base}-copilot-studio-solution.zip`"
            )
            rewritten = rewritten.replace(
                LIBRARY_DYNAMIC_ZIP_SOURCE, replacement, 1
            )
            rewritten_count += 1
    return rewritten, rewritten_count, broken


def prepare_html(
    root: Path,
    included: frozenset[PurePosixPath],
    entries: dict[PurePosixPath, SourceEntry],
    owner: str,
    repo: str,
    ref: str,
) -> tuple[dict[PurePosixPath, bytes], int]:
    prepared: dict[PurePosixPath, bytes] = {}
    rewritten_count = 0
    broken: list[str] = []
    for path in sorted(included, key=lambda item: item.as_posix()):
        if path.suffix.lower() != ".html":
            continue
        source = _assert_regular_source(root, entries[path])
        try:
            text = source.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise BuildError(f"Could not read HTML file {path}: {exc}") from exc
        rewritten, count, page_broken = rewrite_html(
            path, text, included, entries, owner, repo, ref
        )
        prepared[path] = rewritten.encode("utf-8")
        rewritten_count += count
        broken.extend(page_broken)
    if broken:
        raise BuildError("Broken or unclassified Pages links:\n" + "\n".join(broken))
    return prepared, rewritten_count


def _installer_substitutions(
    suffix: str, owner: str, repo: str, branch: str
) -> list[tuple[str, str, bool]]:
    """(canonical text, ring text, required) for one installer flavour."""
    canonical = f"{CANONICAL_OWNER}/{CANONICAL_REPO}"
    ring = f"{owner}/{repo}"
    subs: list[tuple[str, str, bool]] = [
        (f"https://github.com/{canonical}.git", f"https://github.com/{ring}.git", suffix != ".cmd"),
        (
            f"https://raw.githubusercontent.com/{canonical}/{CANONICAL_BRANCH}/",
            f"https://raw.githubusercontent.com/{ring}/{branch}/",
            True,
        ),
        (
            f"https://{CANONICAL_OWNER}.github.io/{CANONICAL_REPO}/",
            f"https://{owner}.github.io/{repo}/",
            False,
        ),
    ]
    if suffix == ".sh":
        subs.append(
            (
                'REPO_REF="${BRAINSTEM_REPO_REF:-' + CANONICAL_BRANCH + '}"',
                'REPO_REF="${BRAINSTEM_REPO_REF:-' + branch + '}"',
                True,
            )
        )
    elif suffix == ".ps1":
        subs.append(
            (
                '$REPO_REF = if ($env:BRAINSTEM_REPO_REF) { $env:BRAINSTEM_REPO_REF } else { "'
                + CANONICAL_BRANCH
                + '" }',
                '$REPO_REF = if ($env:BRAINSTEM_REPO_REF) { $env:BRAINSTEM_REPO_REF } else { "'
                + branch
                + '" }',
                True,
            )
        )
    return subs


def _skill_substitutions(
    owner: str, repo: str, branch: str
) -> list[tuple[str, str, bool]]:
    """(canonical text, ring text, required) for a workshop lane skill."""
    return [
        (
            f"- Repository: `{CANONICAL_OWNER}/{CANONICAL_REPO}`",
            f"- Repository: `{owner}/{repo}`",
            True,
        ),
        (
            f"- Workshop branch: `{CANONICAL_BRANCH}`",
            f"- Workshop branch: `{branch}`",
            True,
        ),
    ]


def render_installer(
    path: PurePosixPath, text: str, owner: str, repo: str, branch: str
) -> str:
    """Point an installer's (or lane skill's) defaults at the ring being published."""
    if path.as_posix() in RING_SKILL_PATHS:
        substitutions = _skill_substitutions(owner, repo, branch)
    else:
        substitutions = _installer_substitutions(path.suffix.lower(), owner, repo, branch)
    for canonical, ring, required in substitutions:
        if canonical not in text:
            if required:
                raise BuildError(
                    f"Installer {path} no longer contains {canonical!r}; "
                    "update the ring identity render before publishing"
                )
            continue
        text = text.replace(canonical, ring)
    return text


def prepare_installers(
    root: Path,
    included: frozenset[PurePosixPath],
    entries: dict[PurePosixPath, SourceEntry],
    owner: str,
    repo: str,
    branch: str,
) -> dict[PurePosixPath, bytes]:
    if (owner, repo, branch) == (CANONICAL_OWNER, CANONICAL_REPO, CANONICAL_BRANCH):
        return {}
    prepared: dict[PurePosixPath, bytes] = {}
    for path in sorted(included, key=lambda item: item.as_posix()):
        if path.as_posix() not in INSTALLER_PATHS and path.as_posix() not in RING_SKILL_PATHS:
            continue
        source = _assert_regular_source(root, entries[path])
        try:
            text = source.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise BuildError(f"Could not read installer {path}: {exc}") from exc
        prepared[path] = render_installer(path, text, owner, repo, branch).encode("utf-8")
    return prepared


def _assert_no_symlink_components(root: Path, candidate: Path) -> None:
    relative = candidate.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise BuildError(f"Output path contains a symlink: {current}")


def resolve_output_path(root: Path, output: str | os.PathLike[str]) -> Path:
    output_path = Path(output).expanduser()
    if not output_path.is_absolute():
        output_path = root / output_path
    lexical = Path(os.path.abspath(output_path))
    try:
        relative = lexical.relative_to(root)
    except ValueError as exc:
        raise BuildError(f"Output path must stay inside repository root: {lexical}") from exc
    if not relative.parts:
        raise BuildError("Output path cannot be the repository root")
    if relative.parts[0] in {
        ".git",
        ".github",
        "academy",
        "agents",
        "beta",
        "browser-audit",
        "docs",
        "rapp_brainstem",
        "reports",
        "scripts",
        "skills",
        "solutions",
        "state",
        "tests",
        "tools",
    }:
        raise BuildError(f"Output path overlaps protected source content: {lexical}")
    _assert_no_symlink_components(root, lexical)
    resolved = lexical.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise BuildError(f"Resolved output escapes repository root: {resolved}") from exc
    return resolved


def _clean_output(output: Path) -> None:
    if not output.exists():
        return
    if output.is_symlink() or not output.is_dir():
        raise BuildError(f"Refusing to clean non-directory output: {output}")
    shutil.rmtree(output)


def _copy_artifact(
    root: Path,
    output: Path,
    included: frozenset[PurePosixPath],
    prepared: dict[PurePosixPath, bytes],
) -> None:
    output.mkdir(parents=True, exist_ok=False)
    for path in sorted(included, key=lambda item: item.as_posix()):
        source = root.joinpath(*path.parts)
        destination = output.joinpath(*path.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink() or not source.is_file():
            raise BuildError(f"Source changed during build: {path}")
        if path in prepared:
            destination.write_bytes(prepared[path])
        else:
            shutil.copyfile(source, destination)
        destination.chmod(0o644)


def _serialized_manifest(manifest: dict[str, object]) -> bytes:
    return (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_manifest(
    output: Path,
    owner: str,
    repo: str,
    ref: str,
    rewritten_count: int,
    excluded: dict[str, dict[str, int]],
    ring_branch: str = CANONICAL_BRANCH,
    rendered_installers: Iterable[str] = (),
) -> dict[str, object]:
    artifact_files = sorted(path for path in output.rglob("*") if path.is_file())
    copied_bytes = sum(path.stat().st_size for path in artifact_files)
    manifest: dict[str, object] = {
        "schema": MANIFEST_SCHEMA,
        "source": {"owner": owner, "repo": repo, "ref": ref},
        "ring": {
            "branch": ring_branch,
            "rendered_installers": sorted(rendered_installers),
        },
        "file_count": len(artifact_files) + 1,
        "total_bytes": 0,
        "rewritten_link_count": rewritten_count,
        "excluded": {
            extension: {
                "count": excluded[extension]["count"],
                "bytes": excluded[extension]["bytes"],
            }
            for extension in sorted(excluded)
        },
    }
    for _ in range(20):
        serialized = _serialized_manifest(manifest)
        total_bytes = copied_bytes + len(serialized)
        if manifest["total_bytes"] == total_bytes:
            break
        manifest["total_bytes"] = total_bytes
    else:
        raise BuildError("Manifest byte count did not stabilize")

    manifest_path = output / MANIFEST_NAME
    manifest_path.write_bytes(_serialized_manifest(manifest))
    manifest_path.chmod(0o644)
    return manifest


def _artifact_files(output: Path) -> list[Path]:
    files: list[Path] = []
    for path in output.rglob("*"):
        if path.is_symlink():
            raise BuildError(f"Artifact contains a symlink: {path.relative_to(output)}")
        if path.is_file():
            files.append(path)
    return sorted(files)


def _artifact_path_forbidden(relative: PurePosixPath) -> bool:
    if not relative.parts:
        return True
    if relative.parts[0] in NEVER_COPY_TOP_LEVEL:
        return True
    if any(part in NEVER_COPY_COMPONENTS for part in relative.parts):
        return True
    if "build" in relative.parts and relative.as_posix() != "beta/build/icon.svg":
        return True
    return False


def validate_html_links(output: Path) -> list[str]:
    files = _artifact_files(output)
    included = frozenset(
        PurePosixPath(path.relative_to(output).as_posix()) for path in files
    )
    broken: list[str] = []
    for html_path in (path for path in files if path.suffix.lower() == ".html"):
        relative = PurePosixPath(html_path.relative_to(output).as_posix())
        try:
            text = html_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            broken.append(f"{relative}: could not read HTML: {exc}")
            continue
        if (
            relative == PurePosixPath("index.html")
            and LIBRARY_DYNAMIC_ZIP_HREF in text
            and LIBRARY_DYNAMIC_ZIP_SOURCE in text
        ):
            broken.append(
                "index.html: dynamic Copilot Studio ZIP link remains relative"
            )
        newlines = [index for index, character in enumerate(text) if character == "\n"]
        for tag_match in TAG_RE.finditer(text):
            for match in ATTRIBUTE_RE.finditer(tag_match.group(0)):
                value = _attribute_url(match)
                absolute_offset = tag_match.start() + match.start()
                try:
                    target = _relative_link_target(relative, value)
                except BuildError as exc:
                    broken.append(
                        f"{relative}:{_line_number(newlines, absolute_offset)}: {exc}"
                    )
                    continue
                if target is not None and not _artifact_has_target(target, included):
                    broken.append(
                        f"{relative}:{_line_number(newlines, absolute_offset)}: "
                        f"{match.group('attr')}={value!r} -> {target}"
                    )
    return broken


def validate_academy_artifact(output: Path) -> AcademyRequirements:
    files = frozenset(
        PurePosixPath(path.relative_to(output).as_posix())
        for path in _artifact_files(output)
    )
    return validate_academy_source(output, files)


def validate_artifact(output: Path, check_links: bool = True) -> dict[str, object]:
    files = _artifact_files(output)
    total_bytes = 0
    for path in files:
        relative = PurePosixPath(path.relative_to(output).as_posix())
        size = path.stat().st_size
        total_bytes += size
        if _artifact_path_forbidden(relative):
            raise BuildError(f"Forbidden path included in artifact: {relative}")
        if (
            relative.parts
            and relative.parts[0] == "solutions"
            and relative.suffix.lower() in FORBIDDEN_PAGES_SUFFIXES
        ):
            raise BuildError(f"Excluded solution blob included in artifact: {relative}")
        if size > FILE_BYTE_LIMIT:
            raise BuildError(
                f"Artifact file exceeds {FILE_BYTE_LIMIT} bytes: {relative} ({size})"
            )
    if total_bytes >= ARTIFACT_BYTE_LIMIT:
        raise BuildError(
            f"Artifact is {total_bytes} bytes; limit is below {ARTIFACT_BYTE_LIMIT}"
        )

    manifest_path = output / MANIFEST_NAME
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"Could not read {MANIFEST_NAME}: {exc}") from exc
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise BuildError(f"{MANIFEST_NAME} has an unexpected schema")
    if manifest.get("file_count") != len(files):
        raise BuildError(
            f"{MANIFEST_NAME} file_count is {manifest.get('file_count')}; "
            f"actual count is {len(files)}"
        )
    if manifest.get("total_bytes") != total_bytes:
        raise BuildError(
            f"{MANIFEST_NAME} total_bytes is {manifest.get('total_bytes')}; "
            f"actual bytes are {total_bytes}"
        )

    validate_academy_artifact(output)
    if check_links:
        broken = validate_html_links(output)
        if broken:
            raise BuildError("Broken artifact links:\n" + "\n".join(broken))
    return manifest


def _validate_ref(ref: str, label: str = "ref") -> None:
    if (
        not ref
        or not REF_RE.fullmatch(ref)
        or ref.startswith("/")
        or ref.endswith("/")
        or ".." in ref.split("/")
    ):
        raise BuildError(f"Invalid GitHub {label}: {ref!r}")


def _validate_source_identity(
    owner: str, repo: str, ref: str, ring_branch: str = CANONICAL_BRANCH
) -> None:
    if not OWNER_REPO_RE.fullmatch(owner):
        raise BuildError(f"Invalid GitHub owner: {owner!r}")
    if not OWNER_REPO_RE.fullmatch(repo):
        raise BuildError(f"Invalid GitHub repository: {repo!r}")
    _validate_ref(ref)
    _validate_ref(ring_branch, "branch")


def build_site(
    root_value: str | os.PathLike[str],
    output_value: str | os.PathLike[str],
    owner: str,
    repo: str,
    ref: str,
    check_links: bool = True,
    ring_branch: str = CANONICAL_BRANCH,
) -> dict[str, object]:
    root_input = Path(root_value).expanduser()
    if root_input.is_symlink():
        raise BuildError(f"Repository root cannot be a symlink: {root_input}")
    try:
        root = root_input.resolve(strict=True)
    except OSError as exc:
        raise BuildError(f"Repository root does not exist: {root_input}") from exc
    if not root.is_dir():
        raise BuildError(f"Repository root is not a directory: {root}")

    _validate_source_identity(owner, repo, ref, ring_branch)
    output = resolve_output_path(root, output_value)
    entries = collect_source_entries(root)
    entries = hydrate_excluded_sizes(root, entries, owner, repo, ref)
    included, excluded = plan_artifact(root, entries)
    validate_academy_source(root, included)
    prepared_html, rewritten_count = prepare_html(
        root, included, entries, owner, repo, ref
    )
    prepared_installers = prepare_installers(
        root, included, entries, owner, repo, ring_branch
    )

    _clean_output(output)
    try:
        _copy_artifact(
            root, output, included, {**prepared_html, **prepared_installers}
        )
        _write_manifest(
            output,
            owner,
            repo,
            ref,
            rewritten_count,
            excluded,
            ring_branch=ring_branch,
            rendered_installers=[p.as_posix() for p in prepared_installers],
        )
        return validate_artifact(output, check_links=check_links)
    except Exception:
        if output.exists() and output.is_dir() and not output.is_symlink():
            shutil.rmtree(output)
        raise


def parse_args(arguments: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root (default: .)")
    parser.add_argument("--out", default="_site", help="Artifact output under root")
    parser.add_argument("--owner", required=True, help="GitHub repository owner")
    parser.add_argument("--repo", required=True, help="GitHub repository name")
    parser.add_argument("--ref", required=True, help="Immutable source ref or SHA")
    parser.add_argument(
        "--ring-branch",
        default=CANONICAL_BRANCH,
        help=(
            "Branch the published installers should install from (default: main). "
            "Any ring other than microsoft/aibast-agents-library@main gets its "
            "installers rendered to that identity."
        ),
    )
    parser.add_argument(
        "--check-links",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Validate all built HTML href/src targets (default: enabled)",
    )
    return parser.parse_args(arguments)


def main(arguments: Iterable[str] | None = None) -> int:
    args = parse_args(arguments)
    try:
        manifest = build_site(
            args.root,
            args.out,
            args.owner,
            args.repo,
            args.ref,
            check_links=args.check_links,
            ring_branch=args.ring_branch,
        )
    except (BuildError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    excluded = manifest["excluded"]
    rendered = manifest["ring"]["rendered_installers"]
    if rendered:
        print(
            f"Rendered {len(rendered)} installer(s) for "
            f"{args.owner}/{args.repo}@{args.ring_branch}: {', '.join(rendered)}"
        )
    print(
        f"Built {args.out}: {manifest['file_count']} files, "
        f"{manifest['total_bytes']} bytes, "
        f"{manifest['rewritten_link_count']} rewritten links; "
        f"excluded .zip={excluded['.zip']['count']}/"
        f"{excluded['.zip']['bytes']} bytes, "
        f".gif={excluded['.gif']['count']}/"
        f"{excluded['.gif']['bytes']} bytes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
