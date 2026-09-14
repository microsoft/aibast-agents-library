#!/usr/bin/env python3
"""Fail-closed acceptance gate for the Microsoft AI Academy."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator, Mapping
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
AUDIT_SCHEMA = "aibast-academy-audit/1.0"
ACADEMY_SCHEMA = "aibast-academy/1.0"
EXPECTED_COURSES = 51
EXPECTED_SKILLS = 229
EXPECTED_PATHS = 6
EXPECTED_INDUSTRIES = 12
EXPECTED_MILESTONES = 6
EXPECTED_POINTS = 150
START_PATH_ID = "start-here"

REQUIRED_INTEGRATION_PAGES = (
    "index.html",
    "library.html",
    "achievements.html",
    "metrics.html",
    "docs/rapp-guide.html",
    "README.md",
)
REQUIRED_ACADEMY_LINKS = {
    "index.html",
    "achievements.html",
    "metrics.html",
    "docs/rapp-guide.html",
}
REQUIRED_MEASUREMENTS = (
    "catalog_courses",
    "academy_courses",
    "discovered_skills",
    "academy_skills",
    "paths",
    "industries",
    "milestones",
    "milestone_points",
    "certified_courses",
    "inline_scripts",
    "integration_links",
)
RESOURCE_FILENAMES = {
    "quest": "quest.html",
    "manual_tutorial": "manual-tutorial.html",
    "field_guide": "field-guide.html",
    "evidence_report": "evidence-report.html",
}
RESOURCE_ALIASES = {
    "quest": {"quest", "quest_url"},
    "manual_tutorial": {
        "manual",
        "manual_url",
        "manual_tutorial",
        "manual_tutorial_url",
        "tutorial",
        "tutorial_url",
    },
    "field_guide": {
        "field_guide",
        "field_guide_url",
        "guide",
        "guide_url",
    },
    "evidence_report": {
        "evidence",
        "evidence_url",
        "evidence_report",
        "evidence_report_url",
        "report",
        "report_url",
    },
}
SUMMARY_FIELDS = {
    "courses",
    "skills",
    "paths",
    "industries",
    "points_per_course",
}
VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONT_MATTER_KEY_RE = re.compile(
    r"^([A-Za-z][A-Za-z0-9_-]*)\s*:\s*(.*)$"
)
MUTATING_METHOD_RE = re.compile(
    r"\bmethod\s*:\s*['\"](?:POST|PUT|PATCH|DELETE)['\"]", re.I
)
try:
    from tools.clarity_tag import strip_tag as strip_clarity_tag
except ModuleNotFoundError:
    from clarity_tag import strip_tag as strip_clarity_tag

ANALYTICS_RE = re.compile(
    r"google-analytics|googletagmanager|analytics\.js|gtag\s*\(|"
    r"\bfbq\s*\(|mixpanel|hotjar|segment\.com|plausible(?:\.io)?|"
    r"clarity\s*\(",
    re.I,
)
AUTO_SUBMISSION_RE = re.compile(
    r"\bsendBeacon\s*\(|\bXMLHttpRequest\b|"
    r"\.requestSubmit\s*\(|\.submit\s*\(",
    re.I,
)


def normalize_source(source: str) -> str:
    """Normalize source before any line- or delimiter-based slicing."""

    return source.replace("\r\n", "\n").replace("\r", "\n")


@dataclass
class AuditResult:
    failures: dict[str, list[str]] = field(default_factory=dict)
    passes: dict[str, list[str]] = field(default_factory=dict)
    measurements: dict[str, int] = field(default_factory=dict)

    def fail(self, category: str, message: str) -> None:
        bucket = self.failures.setdefault(category, [])
        if message not in bucket:
            bucket.append(message)

    def ok(self, category: str, message: str) -> None:
        bucket = self.passes.setdefault(category, [])
        if message not in bucket:
            bucket.append(message)

    def measure(self, name: str, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            self.fail("measurement", f"{name} is not a measured integer")
            return
        self.measurements[name] = value

    @property
    def passed(self) -> bool:
        return not self.failures

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": AUDIT_SCHEMA,
            "status": "pass" if self.passed else "fail",
            "measurements": dict(sorted(self.measurements.items())),
            "passes": self.passes,
            "failures": self.failures,
        }


def require(
    result: AuditResult,
    condition: bool,
    category: str,
    failure: str,
    success: str | None = None,
) -> None:
    if condition:
        result.ok(category, success or "check passed")
    else:
        result.fail(category, failure)


def read_text(path: Path, result: AuditResult, category: str) -> str:
    try:
        return normalize_source(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        result.fail(category, f"{path}: unreadable ({exc})")
        return ""


def read_json(path: Path, result: AuditResult, category: str) -> Any:
    source = read_text(path, result, category)
    if not source:
        return {}
    try:
        return json.loads(source)
    except json.JSONDecodeError as exc:
        result.fail(
            category,
            f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}",
        )
        return {}


def _nonnegative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _positive_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def parse_front_matter(source: str) -> dict[str, str]:
    """Parse the small front-matter subset needed by the Academy gate."""

    source = normalize_source(source)
    if source.startswith("\ufeff"):
        source = source[1:]
    lines = source.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(
            index for index, line in enumerate(lines[1:], 1) if line.strip() == "---"
        )
    except StopIteration:
        return {}

    values: dict[str, str] = {}
    index = 1
    while index < end:
        match = FRONT_MATTER_KEY_RE.match(lines[index])
        if not match:
            index += 1
            continue
        key, raw_value = match.groups()
        value = raw_value.strip()
        if value in {"|", ">", "|-", ">-", "|+", ">+"}:
            block: list[str] = []
            index += 1
            while index < end and (
                lines[index].startswith((" ", "\t")) or not lines[index].strip()
            ):
                block.append(lines[index].strip())
                index += 1
            value = " ".join(part for part in block if part)
        else:
            index += 1
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1].strip()
        values[key.casefold()] = value
    return values


def _decoded_path(value: str) -> str:
    decoded = value
    for _ in range(3):
        next_value = unquote(decoded)
        if next_value == decoded:
            break
        decoded = next_value
    return decoded


def is_safe_repository_url(value: Any) -> bool:
    """Return whether a value is a non-escaping repository-relative URL."""

    if not isinstance(value, str) or not value or value != value.strip():
        return False
    if any(ord(char) < 32 for char in value) or "\\" in value:
        return False
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or value.startswith(("/", "//")):
        return False
    decoded = _decoded_path(parsed.path)
    if "\\" in decoded or decoded.startswith(("/", "//")):
        return False
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", decoded):
        return False
    if decoded:
        parts = PurePosixPath(decoded).parts
        if any(part in {"", ".", ".."} for part in parts):
            return False
        if posixpath.normpath(decoded).startswith("../"):
            return False
    elif not parsed.fragment:
        return False
    return True


def _url_key(key: str) -> bool:
    key = key.casefold()
    if key in {"url", "href", "path", "file"}:
        return True
    if key.endswith(("_url", "_href", "_file")):
        return True
    return key.endswith("_path") and not key.endswith(
        ("path_id", "path_ids", "primary_path")
    )


def iter_repository_urls(value: Any, key: str = "") -> Iterator[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child in value.items():
            child_name = str(child_key)
            if _url_key(child_name):
                if isinstance(child, list):
                    for item in child:
                        yield child_name, item
                else:
                    yield child_name, child
            yield from iter_repository_urls(child, child_name)
    elif isinstance(value, list):
        for child in value:
            yield from iter_repository_urls(child, key)


def audit_repository_urls(data: Any, result: AuditResult) -> None:
    for key, value in iter_repository_urls(data):
        if not isinstance(value, str):
            result.fail("urls", f"{key} must be a repository-relative string")
        elif not is_safe_repository_url(value):
            result.fail("urls", f"unsafe repository URL in {key}: {value!r}")

    serialized = json.dumps(data, ensure_ascii=False)
    for forbidden in ("http://", "https://", "javascript:", "data:", "file://"):
        if forbidden.casefold() in serialized.casefold():
            result.fail(
                "urls",
                f"academy.json contains a non-repository URL scheme ({forbidden})",
            )


def _identifier(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        for key in ("id", "slug", "name", "value"):
            candidate = value.get(key)
            if isinstance(candidate, str):
                return candidate
    return ""


def _identifiers(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [_identifier(value) for value in values]


def _summary_value(
    summary: Mapping[str, Any],
    field_name: str,
    result: AuditResult,
) -> int | None:
    if field_name not in summary:
        result.fail("summary", f"summary is missing its {field_name} measurement")
        return None
    value = summary[field_name]
    if not _nonnegative_integer(value):
        result.fail("summary", f"summary {field_name} must be an integer")
        return None
    return value


def _catalog_solutions(
    root: Path,
    result: AuditResult,
) -> tuple[dict[str, Any], dict[str, str]]:
    catalog = read_json(root / "solutions" / "catalog.json", result, "catalog")
    solutions = catalog.get("solutions") if isinstance(catalog, Mapping) else None
    if not isinstance(solutions, dict):
        result.fail("catalog", "solutions/catalog.json must contain a solutions object")
        return {}, {}

    result.measure("catalog_courses", len(solutions))
    require(
        result,
        len(solutions) == EXPECTED_COURSES,
        "catalog",
        f"solutions/catalog.json must contain exactly {EXPECTED_COURSES} courses",
        f"catalog contains {EXPECTED_COURSES} courses",
    )
    if any(key.rsplit("/", 1)[-1] == "grid-outage-response" for key in solutions):
        result.fail("catalog", "grid-outage-response must not be in the Academy catalog")

    registry_slugs: dict[str, str] = {}
    registry_path = root / "registry.json"
    if registry_path.is_file():
        registry = read_json(registry_path, result, "catalog")
        rows = registry.get("agents") if isinstance(registry, Mapping) else None
        if not isinstance(rows, list):
            result.fail("catalog", "registry.json agents cannot be measured")
        else:
            for row in rows:
                if not isinstance(row, Mapping):
                    continue
                name = row.get("name")
                solution = row.get("_solution")
                package = (
                    solution.get("package")
                    if isinstance(solution, Mapping)
                    else None
                )
                demo = row.get("_demo")
                slug = (
                    package.get("slug")
                    if isinstance(package, Mapping)
                    else None
                )
                if not isinstance(slug, str) and isinstance(demo, Mapping):
                    slug = demo.get("slug")
                if isinstance(name, str) and isinstance(slug, str):
                    registry_slugs[name] = slug

    slug_map: dict[str, str] = {}
    for catalog_key, catalog_row in solutions.items():
        if not isinstance(catalog_key, str):
            result.fail("catalog", "solutions/catalog.json contains a non-string key")
            continue
        explicit = (
            catalog_row.get("slug")
            if isinstance(catalog_row, Mapping)
            else None
        )
        slug = (
            explicit
            if isinstance(explicit, str)
            else registry_slugs.get(catalog_key, catalog_key.rsplit("/", 1)[-1])
        )
        slug_map[catalog_key] = slug
    return solutions, slug_map


def _discover_skills(
    root: Path,
    course_slugs: Iterable[str],
    result: AuditResult,
) -> dict[str, list[str]]:
    discovered: dict[str, list[str]] = {}
    for slug in sorted(set(course_slugs)):
        skill_root = root / "solutions" / slug / "manual" / "skills"
        paths = (
            sorted(path for path in skill_root.rglob("SKILL.md") if path.is_file())
            if skill_root.is_dir()
            else []
        )
        discovered[slug] = [
            path.relative_to(root).as_posix() for path in paths
        ]

    all_paths = [path for paths in discovered.values() for path in paths]
    result.measure("discovered_skills", len(all_paths))
    require(
        result,
        len(all_paths) == EXPECTED_SKILLS,
        "skills",
        f"expected {EXPECTED_SKILLS} discovered manual skills, found {len(all_paths)}",
        f"discovered {EXPECTED_SKILLS} manual skills",
    )
    for relative in all_paths:
        source = read_text(root / relative, result, "skills")
        front_matter = parse_front_matter(source)
        for field_name in ("name", "description"):
            value = front_matter.get(field_name, "").strip()
            if not value or value.casefold() in {"null", "none", "~"}:
                result.fail(
                    "skills",
                    f"{relative}: front matter is missing {field_name}",
                )
    return discovered


def _course_resource_candidates(
    course: Mapping[str, Any],
    resource_name: str,
) -> set[str]:
    aliases = RESOURCE_ALIASES[resource_name]
    candidates: set[str] = set()

    def add(value: Any) -> None:
        if isinstance(value, str):
            candidates.add(value)
        elif isinstance(value, Mapping):
            for key in ("url", "href", "path", "file"):
                nested = value.get(key)
                if isinstance(nested, str):
                    candidates.add(nested)

    for key, value in course.items():
        if str(key).casefold() in aliases:
            add(value)
    for container_name in ("resources", "links", "artifacts"):
        container = course.get(container_name)
        if isinstance(container, Mapping):
            for key, value in container.items():
                if str(key).casefold() in aliases:
                    add(value)
        elif isinstance(container, list):
            for item in container:
                if not isinstance(item, Mapping):
                    continue
                item_name = _identifier(
                    item.get("type")
                    or item.get("kind")
                    or item.get("id")
                    or item.get("name")
                )
                if item_name.casefold() in aliases:
                    add(item)
    return candidates


def _course_skill_paths(
    course: Mapping[str, Any],
    result: AuditResult,
    slug: str,
) -> list[str]:
    container: Any = None
    for key in ("skills", "manual_skills", "skill_paths"):
        if key in course:
            container = course[key]
            break
    if not isinstance(container, list):
        result.fail("skills", f"{slug}: skills must be a list")
        return []

    paths: list[str] = []
    for index, item in enumerate(container):
        path: Any = item
        if isinstance(item, Mapping):
            path = next(
                (
                    item[key]
                    for key in ("path", "file", "url", "href", "skill_path")
                    if key in item
                ),
                None,
            )
        if not isinstance(path, str) or not path:
            result.fail("skills", f"{slug}: skill {index + 1} has no path")
            continue
        paths.append(path)
    if not paths:
        result.fail("skills", f"{slug}: at least one manual skill is required")
    return paths


def _declared_path_courses(path: Mapping[str, Any]) -> list[str] | None:
    for key in ("course_slugs", "courses", "course_ids"):
        if key not in path:
            continue
        value = path[key]
        if not isinstance(value, list):
            return []
        return [
            item.get("slug", "")
            if isinstance(item, Mapping)
            else item
            for item in value
            if isinstance(item, (str, Mapping))
        ]
    return None


def _primary_path_ids(course: Mapping[str, Any]) -> set[str]:
    primary: set[str] = set()
    for key in ("primary_path_id", "primary_path"):
        value = course.get(key)
        if isinstance(value, str) and value:
            primary.add(value)
        elif isinstance(value, Mapping):
            identifier = _identifier(value)
            if identifier:
                primary.add(identifier)
    entries = course.get("paths")
    if isinstance(entries, list):
        for entry in entries:
            if not isinstance(entry, Mapping):
                continue
            if entry.get("primary") is True or entry.get("is_primary") is True:
                identifier = _identifier(entry)
                if identifier:
                    primary.add(identifier)
    return primary


def _audit_paths(
    raw_paths: Any,
    courses: list[Mapping[str, Any]],
    result: AuditResult,
) -> tuple[list[str], list[str]]:
    if not isinstance(raw_paths, list):
        result.fail("paths", "academy paths must be a list")
        return [], []
    result.measure("paths", len(raw_paths))
    require(
        result,
        len(raw_paths) == EXPECTED_PATHS,
        "paths",
        f"expected exactly {EXPECTED_PATHS} paths, found {len(raw_paths)}",
        f"found {EXPECTED_PATHS} paths",
    )

    path_ids = [_identifier(path) for path in raw_paths]
    if any(not path_id or not SLUG_RE.fullmatch(path_id) for path_id in path_ids):
        result.fail("paths", "every path must have a slug-safe id")
    if len(path_ids) != len(set(path_ids)):
        result.fail("paths", "path IDs must be unique")
    if START_PATH_ID not in path_ids:
        result.fail("paths", f"the {START_PATH_ID!r} path is required")

    known = set(path_ids)
    category_owners: dict[str, str] = {}
    for raw_path in raw_paths:
        if not isinstance(raw_path, Mapping):
            continue
        path_id = _identifier(raw_path)
        categories = raw_path.get("categories")
        if not isinstance(categories, list) or any(
            not isinstance(category, str) or not category
            for category in categories
        ):
            result.fail(
                "industries",
                f"{path_id or '<unknown path>'}: categories must be a string list",
            )
            continue
        if len(categories) != len(set(categories)):
            result.fail("industries", f"{path_id}: path categories contain duplicates")
        if path_id == START_PATH_ID:
            if categories:
                result.fail("industries", "start-here must not own categories")
            continue
        if not categories:
            result.fail("industries", f"{path_id}: non-start path must own categories")
        for category in categories:
            previous = category_owners.get(category)
            if previous is not None:
                result.fail(
                    "industries",
                    f"category {category!r} belongs to multiple paths: {previous}, {path_id}",
                )
                continue
            category_owners[category] = path_id

    course_categories: list[str] = []
    for course in courses:
        category = course.get("category")
        slug = course.get("slug", "<unknown course>")
        if not isinstance(category, str) or not category:
            result.fail("industries", f"{slug}: category is missing")
            continue
        course_categories.append(category)
    unique_categories = sorted(set(course_categories))
    result.measure("industries", len(unique_categories))
    require(
        result,
        len(unique_categories) == EXPECTED_INDUSTRIES,
        "industries",
        f"expected exactly {EXPECTED_INDUSTRIES} course categories, "
        f"found {len(unique_categories)}",
        f"derived {EXPECTED_INDUSTRIES} course categories",
    )
    missing_owners = sorted(set(unique_categories) - set(category_owners))
    unused_owners = sorted(set(category_owners) - set(unique_categories))
    if missing_owners or unused_owners:
        result.fail(
            "industries",
            "path category coverage is not exact "
            f"(missing={missing_owners}, unused={unused_owners})",
        )

    derived_members: dict[str, set[str]] = {path_id: set() for path_id in known}
    for course in courses:
        slug = course.get("slug")
        label = slug if isinstance(slug, str) else "<unknown course>"
        category = course.get("category")
        course_path_ids = course.get("path_ids")
        if not isinstance(course_path_ids, list) or not course_path_ids:
            result.fail("paths", f"{label}: path_ids must be a non-empty list")
            continue
        if any(not isinstance(path_id, str) for path_id in course_path_ids):
            result.fail("paths", f"{label}: path_ids must contain only strings")
            continue
        if len(course_path_ids) != len(set(course_path_ids)):
            result.fail("paths", f"{label}: path_ids contain duplicates")
        unknown = sorted(set(course_path_ids) - known)
        if unknown:
            result.fail("paths", f"{label}: unknown path_ids {unknown}")
        for path_id in set(course_path_ids) & known:
            if isinstance(slug, str):
                derived_members[path_id].add(slug)

        primary = _primary_path_ids(course)
        if len(primary) != 1:
            result.fail(
                "paths",
                f"{label}: exactly one explicit primary path is required",
            )
        else:
            primary_id = next(iter(primary))
            if primary_id == START_PATH_ID:
                result.fail("paths", f"{label}: start-here cannot be the primary path")
            if primary_id not in course_path_ids:
                result.fail(
                    "paths",
                    f"{label}: primary path {primary_id!r} is absent from path_ids",
                )
            if primary_id not in known:
                result.fail(
                    "paths",
                    f"{label}: primary path {primary_id!r} is not declared",
                )
            expected_primary = (
                category_owners.get(category)
                if isinstance(category, str)
                else None
            )
            if expected_primary is not None and primary_id != expected_primary:
                result.fail(
                    "paths",
                    f"{label}: primary path {primary_id!r} does not own category {category!r}",
                )

        if isinstance(category, str) and category in category_owners:
            expected_non_start = {category_owners[category]}
            actual_non_start = set(course_path_ids) - {START_PATH_ID}
            if actual_non_start != expected_non_start:
                result.fail(
                    "paths",
                    f"{label}: non-start path_ids {sorted(actual_non_start)} "
                    f"do not match category owner {sorted(expected_non_start)}",
                )

    for raw_path in raw_paths:
        if not isinstance(raw_path, Mapping):
            result.fail("paths", "every path entry must be an object")
            continue
        path_id = _identifier(raw_path)
        declared = _declared_path_courses(raw_path)
        if declared is None or path_id not in derived_members:
            continue
        if any(not isinstance(slug, str) or not slug for slug in declared):
            result.fail("paths", f"{path_id}: declared course membership is invalid")
            continue
        if len(declared) != len(set(declared)):
            result.fail("paths", f"{path_id}: declared courses contain duplicates")
        if set(declared) != derived_members[path_id]:
            result.fail(
                "paths",
                f"{path_id}: declared courses do not match course path_ids",
            )
        course_count = raw_path.get("course_count")
        if course_count is not None and course_count != len(derived_members[path_id]):
            result.fail(
                "paths",
                f"{path_id}: course_count={course_count!r}, "
                f"measured {len(derived_members[path_id])}",
            )

    unreferenced = sorted(
        path_id for path_id, members in derived_members.items() if not members
    )
    if unreferenced:
        result.fail("paths", f"unreferenced paths: {unreferenced}")
    return path_ids, unique_categories


def _audit_milestones(
    raw: Any,
    result: AuditResult,
) -> tuple[list[str], int | None]:
    if not isinstance(raw, list):
        result.fail("milestones", "academy milestones must be a list")
        return [], None
    result.measure("milestones", len(raw))
    require(
        result,
        len(raw) == EXPECTED_MILESTONES,
        "milestones",
        f"expected exactly {EXPECTED_MILESTONES} milestones, found {len(raw)}",
        f"found {EXPECTED_MILESTONES} milestones",
    )
    milestone_ids = _identifiers(raw)
    if any(not milestone_id for milestone_id in milestone_ids):
        result.fail("milestones", "every milestone must have an id")
    if len(milestone_ids) != len(set(milestone_ids)):
        result.fail("milestones", "milestone IDs must be unique")

    points: list[int] = []
    for milestone in raw:
        if not isinstance(milestone, Mapping):
            result.fail("milestones", "every milestone must be an object")
            continue
        value = milestone.get("points")
        if value is None:
            value = milestone.get("point_value")
        if not _positive_integer(value):
            result.fail(
                "milestones",
                f"{_identifier(milestone) or '<unknown>'}: points must be positive",
            )
            continue
        points.append(value)
    if len(points) != len(raw):
        return milestone_ids, None
    total = sum(points)
    result.measure("milestone_points", total)
    require(
        result,
        total == EXPECTED_POINTS,
        "milestones",
        f"milestone points must total {EXPECTED_POINTS}, found {total}",
        f"milestones total {EXPECTED_POINTS} points",
    )
    return milestone_ids, total


def _audit_certification(
    root: Path,
    course_slugs: set[str],
    result: AuditResult,
) -> None:
    rollout = read_json(
        root / "state" / "workshop_course_rollout.json",
        result,
        "certification",
    )
    if (
        not isinstance(rollout, Mapping)
        or rollout.get("schema") != "aibast-workshop-course-rollout-audit/1.0"
    ):
        result.fail("certification", "workshop rollout schema is missing or stale")
    rows = rollout.get("solutions") if isinstance(rollout, Mapping) else None
    if not isinstance(rows, list):
        result.fail(
            "certification",
            "state/workshop_course_rollout.json must contain a solutions list",
        )
        return
    rollout_slugs = [
        row.get("slug")
        for row in rows
        if isinstance(row, Mapping) and isinstance(row.get("slug"), str)
    ]
    if len(rollout_slugs) != len(rows):
        result.fail("certification", "every rollout row must have a slug")
    if len(rollout_slugs) != len(set(rollout_slugs)):
        result.fail("certification", "rollout course slugs must be unique")
    if set(rollout_slugs) != course_slugs:
        result.fail(
            "certification",
            "rollout course scope does not match Academy courses",
        )

    passed = 0
    for row in rows:
        if not isinstance(row, Mapping):
            result.fail("certification", "rollout rows must be objects")
            continue
        slug = row.get("slug", "<unknown>")
        failures = row.get("failures")
        if row.get("passed") is not True or failures != []:
            result.fail("certification", f"{slug}: rollout certification failed")
        else:
            passed += 1
    result.measure("certified_courses", passed)

    expected_totals = {
        "total": len(rows),
        "passed": passed,
        "failed": len(rows) - passed,
    }
    for key, expected in expected_totals.items():
        actual = rollout.get(key) if isinstance(rollout, Mapping) else None
        if actual != expected:
            result.fail(
                "certification",
                f"rollout {key}={actual!r}, expected {expected}",
            )


def audit_academy_data(
    root: Path,
    data: Any,
    result: AuditResult,
) -> None:
    if not isinstance(data, Mapping):
        result.fail("schema", "academy.json must contain an object")
        return
    require(
        result,
        data.get("schema") == ACADEMY_SCHEMA,
        "schema",
        f"academy.json schema must be {ACADEMY_SCHEMA}",
        f"schema is {ACADEMY_SCHEMA}",
    )
    audit_repository_urls(data, result)

    summary = data.get("summary")
    if not isinstance(summary, Mapping):
        result.fail("summary", "academy.json must contain a summary object")
        summary = {}
    elif set(summary) != SUMMARY_FIELDS:
        result.fail(
            "summary",
            "summary keys must be exactly "
            + ", ".join(sorted(SUMMARY_FIELDS))
            + f" (found {sorted(summary)})",
        )
    summary_values = {
        name: _summary_value(summary, name, result)
        for name in SUMMARY_FIELDS
    }

    raw_courses = data.get("courses")
    if not isinstance(raw_courses, list):
        result.fail("catalog", "academy courses must be a list")
        return
    result.measure("academy_courses", len(raw_courses))
    courses: list[Mapping[str, Any]] = []
    for index, course in enumerate(raw_courses):
        if not isinstance(course, Mapping):
            result.fail("catalog", f"course {index + 1} must be an object")
        else:
            courses.append(course)

    catalog, expected_slug_map = _catalog_solutions(root, result)
    course_agents = [
        course.get("agent")
        for course in courses
        if isinstance(course.get("agent"), str)
    ]
    course_slugs = [
        course.get("slug")
        for course in courses
        if isinstance(course.get("slug"), str)
    ]
    if len(course_agents) != len(courses):
        result.fail("catalog", "every course must have an agent catalog key")
    if len(course_slugs) != len(courses):
        result.fail("catalog", "every course must have a slug")
    if len(course_agents) != len(set(course_agents)):
        result.fail("catalog", "course agent keys must be unique")
    if len(course_slugs) != len(set(course_slugs)):
        result.fail("catalog", "course slugs must be unique")
    if any(not SLUG_RE.fullmatch(slug) for slug in course_slugs):
        result.fail("catalog", "course slugs must use lowercase kebab-case")
    if "grid-outage-response" in course_slugs:
        result.fail("catalog", "grid-outage-response must remain excluded")
    if set(course_agents) != set(catalog):
        missing = sorted(set(catalog) - set(course_agents))
        extra = sorted(set(course_agents) - set(catalog))
        result.fail(
            "catalog",
            f"Academy agent keys differ (missing={missing}, extra={extra})",
        )
    if set(course_slugs) != set(expected_slug_map.values()):
        missing = sorted(set(expected_slug_map.values()) - set(course_slugs))
        extra = sorted(set(course_slugs) - set(expected_slug_map.values()))
        result.fail(
            "catalog",
            f"Academy course slugs differ (missing={missing}, extra={extra})",
        )
    for course in courses:
        key = course.get("agent")
        slug = course.get("slug")
        if (
            isinstance(key, str)
            and isinstance(slug, str)
            and expected_slug_map.get(key) != slug
        ):
            result.fail(
                "catalog",
                f"{key}: slug {slug!r} does not match {expected_slug_map.get(key)!r}",
            )

    path_ids, industry_ids = _audit_paths(
        data.get("paths", data.get("learning_paths")),
        courses,
        result,
    )
    _, milestone_points = _audit_milestones(data.get("milestones"), result)

    discovered = _discover_skills(root, course_slugs, result)
    discovered_paths = {
        path for paths in discovered.values() for path in paths
    }
    academy_skill_paths: list[str] = []
    for course in courses:
        slug = course.get("slug")
        if not isinstance(slug, str):
            continue
        for resource_name, filename in RESOURCE_FILENAMES.items():
            candidates = _course_resource_candidates(course, resource_name)
            expected = f"solutions/{slug}/{filename}"
            if candidates != {expected}:
                result.fail(
                    "artifacts",
                    f"{slug}: {resource_name} must resolve exactly to {expected}",
                )
            if not (root / expected).is_file():
                result.fail("artifacts", f"{expected}: required artifact is missing")

        paths = _course_skill_paths(course, result, slug)
        if course.get("skill_count") != len(paths):
            result.fail(
                "skills",
                f"{slug}: skill_count={course.get('skill_count')!r}, "
                f"measured {len(paths)}",
            )
        academy_skill_paths.extend(paths)
        prefix = f"solutions/{slug}/manual/skills/"
        for path in paths:
            if not path.startswith(prefix) or not path.endswith("/SKILL.md"):
                result.fail(
                    "skills",
                    f"{slug}: skill path is outside its manual package ({path})",
                )
            if path not in discovered_paths:
                result.fail("skills", f"{slug}: skill path does not exist ({path})")

    result.measure("academy_skills", len(academy_skill_paths))
    if len(academy_skill_paths) != len(set(academy_skill_paths)):
        result.fail("skills", "Academy skill paths must be unique")
    if set(academy_skill_paths) != discovered_paths:
        missing = sorted(discovered_paths - set(academy_skill_paths))
        extra = sorted(set(academy_skill_paths) - discovered_paths)
        result.fail(
            "skills",
            f"Academy skill inventory differs (missing={missing}, extra={extra})",
        )

    expected_summary = {
        "courses": len(courses),
        "skills": len(discovered_paths),
        "paths": len(path_ids),
        "industries": len(industry_ids),
        "points_per_course": milestone_points,
    }
    for name, expected in expected_summary.items():
        actual = summary_values.get(name)
        if expected is not None and actual != expected:
            result.fail(
                "summary",
                f"summary {name}={actual!r}, measured {expected}",
            )

    _audit_certification(root, set(course_slugs), result)


@dataclass
class ParsedElement:
    tag: str
    attrs: dict[str, str]
    text_parts: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join("".join(self.text_parts).split())


class AcademyHTMLParser(HTMLParser):
    """Strict-enough parser that records unmatched and unclosed structure."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[ParsedElement] = []
        self.open_elements: list[ParsedElement] = []
        self.errors: list[str] = []
        self.ids: list[str] = []
        self.scripts: list[ParsedElement] = []
        self.styles: list[ParsedElement] = []

    def _element(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> ParsedElement:
        data = {name.casefold(): value or "" for name, value in attrs}
        element = ParsedElement(tag.casefold(), data)
        self.elements.append(element)
        if data.get("id"):
            self.ids.append(data["id"])
        if element.tag == "script":
            self.scripts.append(element)
        elif element.tag == "style":
            self.styles.append(element)
        return element

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        element = self._element(tag, attrs)
        if element.tag not in VOID_ELEMENTS:
            self.open_elements.append(element)

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        self._element(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag in VOID_ELEMENTS:
            self.errors.append(f"void element </{tag}> must not have an end tag")
            return
        if not self.open_elements:
            self.errors.append(f"unexpected closing tag </{tag}>")
            return
        if self.open_elements[-1].tag == tag:
            self.open_elements.pop()
            return
        expected = self.open_elements[-1].tag
        self.errors.append(
            f"mismatched closing tag </{tag}>; expected </{expected}>"
        )
        matching = next(
            (
                index
                for index in range(len(self.open_elements) - 1, -1, -1)
                if self.open_elements[index].tag == tag
            ),
            None,
        )
        if matching is not None:
            del self.open_elements[matching:]

    def handle_data(self, data: str) -> None:
        for element in self.open_elements:
            element.text_parts.append(data)

    def finish(self) -> None:
        self.close()
        if self.open_elements:
            tags = ", ".join(f"<{element.tag}>" for element in self.open_elements)
            self.errors.append(f"unclosed elements: {tags}")


def parse_html(source: str) -> AcademyHTMLParser:
    parser = AcademyHTMLParser()
    try:
        parser.feed(normalize_source(source))
        parser.finish()
    except Exception as exc:
        parser.errors.append(f"HTML parser failed: {exc}")
    return parser


def _has_accessible_name(
    element: ParsedElement,
    labelled_control_ids: set[str],
    available_ids: set[str],
) -> bool:
    attrs = element.attrs
    if attrs.get("aria-label", "").strip() or attrs.get("title", "").strip():
        return True
    labelledby = attrs.get("aria-labelledby", "")
    if labelledby and all(part in available_ids for part in labelledby.split()):
        return True
    if element.tag == "button" and element.text:
        return True
    element_id = attrs.get("id")
    return bool(element_id and element_id in labelled_control_ids)


def _normalized_href(page_path: str, href: str) -> str | None:
    if not isinstance(href, str) or not href:
        return None
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or href.startswith(("/", "//")):
        return None
    decoded = _decoded_path(parsed.path)
    if not decoded or "\\" in decoded:
        return None
    base = PurePosixPath(page_path).parent.as_posix()
    normalized = posixpath.normpath(posixpath.join(base, decoded))
    if normalized == ".." or normalized.startswith("../"):
        return None
    return normalized.removeprefix("./")


def _links_to(
    parser: AcademyHTMLParser,
    page_path: str,
    target: str,
) -> bool:
    return any(
        _normalized_href(page_path, element.attrs.get("href", "")) == target
        for element in parser.elements
        if element.tag == "a"
    )


def _validate_javascript(
    parser: AcademyHTMLParser,
    result: AuditResult,
    node_executable: str | None = None,
) -> str:
    executable = [
        script
        for script in parser.scripts
        if not script.attrs.get("src")
        and script.attrs.get("type", "").casefold()
        not in {"application/json", "application/ld+json"}
        and "".join(script.text_parts).strip()
    ]
    result.measure("inline_scripts", len(executable))
    if not executable:
        result.fail("javascript", "academy.html has no executable inline JavaScript")
        return ""

    node = node_executable if node_executable is not None else shutil.which("node")
    if not node:
        result.fail(
            "javascript",
            "node is required; JavaScript syntax checks never skip",
        )
        return "\n".join("".join(script.text_parts) for script in executable)

    for index, script in enumerate(executable, 1):
        source = normalize_source("".join(script.text_parts))
        try:
            checked = subprocess.run(
                [node, "--check", "-"],
                input=source,
                text=True,
                capture_output=True,
                check=False,
                timeout=15,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            result.fail("javascript", f"inline script {index} could not be checked: {exc}")
            continue
        if checked.returncode:
            detail = (checked.stderr or checked.stdout).strip().splitlines()
            result.fail(
                "javascript",
                f"inline script {index} is malformed: "
                + (detail[-1] if detail else "node --check failed"),
            )
    if "javascript" not in result.failures:
        result.ok("javascript", f"{len(executable)} inline scripts parse with node")
    return "\n".join("".join(script.text_parts) for script in executable)


def javascript_function_body(source: str, name: str) -> str | None:
    source = normalize_source(source)
    match = re.search(
        rf"\bfunction\s+{re.escape(name)}\s*\([^)]*\)\s*\{{",
        source,
    )
    if not match:
        return None
    start = match.end()
    depth = 1
    quote: str | None = None
    escaped = False
    line_comment = False
    block_comment = False
    index = start
    while index < len(source):
        char = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
        elif block_comment:
            if char == "*" and following == "/":
                block_comment = False
                index += 1
        elif quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in {"'", '"', "`"}:
            quote = char
        elif char == "/" and following == "/":
            line_comment = True
            index += 1
        elif char == "/" and following == "*":
            block_comment = True
            index += 1
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:index]
        index += 1
    return None


def _visible_static_loading(parser: AcademyHTMLParser) -> bool:
    excluded = {"html", "head", "body", "main", "script", "style"}
    for element in parser.elements:
        if element.tag in excluded:
            continue
        attrs = element.attrs
        if "hidden" in attrs or attrs.get("aria-hidden") == "true":
            continue
        marker = " ".join(
            (
                attrs.get("id", ""),
                attrs.get("class", ""),
                attrs.get("data-state", ""),
                element.text,
            )
        ).casefold()
        if "loading" in marker:
            return True
    return False


def audit_academy_html(
    source: str,
    result: AuditResult,
    *,
    node_executable: str | None = None,
) -> None:
    source = normalize_source(source)
    parser = parse_html(source)
    if parser.errors:
        for error in parser.errors:
            result.fail("html", error)
    else:
        result.ok("html", "HTML structure is balanced and parseable")
    for required_tag in ("html", "head", "body"):
        count = sum(
            element.tag == required_tag for element in parser.elements
        )
        if count != 1:
            result.fail(
                "html",
                f"academy.html must contain exactly one <{required_tag}> element",
            )
    duplicate_ids = sorted(
        identifier
        for identifier in set(parser.ids)
        if parser.ids.count(identifier) > 1
    )
    if duplicate_ids:
        result.fail("html", f"duplicate element IDs: {duplicate_ids}")

    external_scripts = [
        script.attrs.get("src", "")
        for script in parser.scripts
        if script.attrs.get("src")
    ]
    if external_scripts:
        result.fail(
            "security",
            f"external script sources are forbidden: {external_scripts}",
        )

    script = _validate_javascript(
        parser,
        result,
        node_executable=node_executable,
    )
    styles = "\n".join("".join(style.text_parts) for style in parser.styles)

    mains = [element for element in parser.elements if element.tag == "main"]
    require(
        result,
        len(mains) == 1,
        "accessibility",
        "academy.html must contain exactly one main landmark",
        "one main landmark is present",
    )
    skip_links = [
        element
        for element in parser.elements
        if element.tag == "a"
        and element.attrs.get("href", "").startswith("#")
        and "skip" in element.text.casefold()
    ]
    valid_skip = any(
        link.attrs["href"][1:] in set(parser.ids) for link in skip_links
    )
    require(
        result,
        valid_skip,
        "accessibility",
        "a working skip link to an in-page target is required",
        "skip link target exists",
    )

    labelled_control_ids = {
        element.attrs.get("for", "")
        for element in parser.elements
        if element.tag == "label" and element.attrs.get("for")
    }
    available_ids = set(parser.ids)
    controls = [
        element
        for element in parser.elements
        if element.tag in {"button", "input", "select", "textarea"}
        and element.attrs.get("type", "").casefold() != "hidden"
    ]
    unnamed = [
        element.attrs.get("id") or f"<{element.tag}>"
        for element in controls
        if not _has_accessible_name(
            element,
            labelled_control_ids,
            available_ids,
        )
    ]
    if not controls:
        result.fail("accessibility", "interactive controls cannot be measured")
    elif unnamed:
        result.fail("accessibility", f"controls lack accessible names: {unnamed}")
    if not any(
        element.attrs.get("aria-label")
        or element.attrs.get("aria-labelledby")
        or element.tag == "label"
        for element in parser.elements
    ):
        result.fail("accessibility", "accessible labels are missing")
    if not any(
        element.attrs.get("role") == "status"
        or element.attrs.get("aria-live") in {"polite", "assertive"}
        for element in parser.elements
    ):
        result.fail("accessibility", "status changes need an accessible live region")

    if not re.search(
        r"@media[^{]*prefers-reduced-motion\s*:\s*reduce",
        styles,
        re.I,
    ):
        result.fail("accessibility", "reduced-motion CSS is missing")
    if not re.search(r"@media[^{]*max-width\s*:", styles, re.I):
        result.fail("accessibility", "a mobile max-width breakpoint is missing")
    if ":focus-visible" not in styles.casefold():
        result.fail("accessibility", "focus-visible styling is missing")

    lower_script = script.casefold()
    direct_academy_fetch = re.search(
        r"\bfetch\s*\(\s*['\"][^'\"]*academy\.json(?:[?#][^'\"]*)?['\"]",
        script,
        re.I,
    )
    academy_url_variables = re.findall(
        r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*"
        r"['\"][^'\"]*academy\.json(?:[?#][^'\"]*)?['\"]",
        script,
        re.I,
    )
    variable_academy_fetch = any(
        re.search(rf"\bfetch\s*\(\s*{re.escape(name)}\b", script)
        for name in academy_url_variables
    )
    if not direct_academy_fetch and not variable_academy_fetch:
        result.fail("data-loading", "academy.html must fetch academy.json")

    storage_requirements = {
        "aibast:achievement-profile:v1": "achievement profile storage key is missing",
        "localstorage": "local storage integration is missing",
        "json.parse": "stored JSON is not parsed",
        "sanitize": "stored achievement data is not sanitized",
        "typeof": "stored values are not type-checked",
        "array.isarray": "stored arrays are not validated",
        "try": "storage access is not guarded",
        "catch": "malformed or denied storage has no fallback",
    }
    for token, failure in storage_requirements.items():
        if token not in lower_script:
            result.fail("storage", failure)
    if not re.search(
        r"try\s*\{[\s\S]*?localStorage[\s\S]*?\}\s*catch",
        script,
        re.I,
    ):
        result.fail(
            "storage",
            "localStorage reads must be enclosed by a try/catch fallback",
        )
    declared_names = set(
        re.findall(
            r"(?:function\s+|(?:const|let|var)\s+)([A-Za-z_$][\w$]*)",
            script,
        )
    )
    sanitizer_names = {
        name
        for name in declared_names
        if re.search(r"sanitize|normaliz|validat", name, re.I)
    }
    if not sanitizer_names or not any(
        len(re.findall(rf"\b{re.escape(name)}\s*\(", script)) >= 2
        for name in sanitizer_names
    ):
        result.fail("storage", "parsed storage data is not passed through a sanitizer")

    if "urlsearchparams" not in lower_script:
        result.fail("url-state", "URLSearchParams state handling is missing")
    for key in ("q", "path", "industry", "progress", "sort"):
        if not re.search(
            rf"\.(?:get|set)\s*\(\s*['\"]{re.escape(key)}['\"]",
            script,
        ):
            result.fail("url-state", f"URL state key {key!r} is not exposed")
    if not re.search(r"history\.(?:replaceState|pushState)\s*\(", script):
        result.fail("url-state", "URL state is never written to browser history")
    if "#course/" not in script or "location.hash" not in script:
        result.fail("deep-links", "#course/ deep-link support is missing")
    if "hashchange" not in lower_script:
        result.fail("deep-links", "course deep links do not react to hash changes")

    if "escape" not in lower_script:
        result.fail("dialog", "Escape-to-close handling is missing")
    close_body = javascript_function_body(script, "closeCourse")
    if close_body is None:
        result.fail("dialog", "function closeCourse is missing or unparseable")
    else:
        native_close = re.search(r"\.close\s*\(", close_body)
        hidden_close = re.search(
            r"\b(?:elements\.)?[A-Za-z_$][\w$]*modal[\w$]*"
            r"\.hidden\s*=\s*true",
            close_body,
            re.I,
        )
        if not native_close and not hidden_close:
            result.fail(
                "dialog",
                "closeCourse neither closes a dialog nor hides the custom modal",
            )
        if not re.search(
            r"(?:state\.)?returnFocus|previousFocus|lastFocused|focusReturn|opener|trigger",
            close_body,
            re.I,
        ) or not re.search(r"\.focus\s*\(", close_body):
            result.fail(
                "dialog",
                "closeCourse does not restore focus to its retained trigger",
            )

    if not _visible_static_loading(parser):
        result.fail("states", "a visible static loading state is missing")

    create_state_body = javascript_function_body(script, "createStateCard")
    if (
        create_state_body is None
        or "document.createElement" not in create_state_body
        or "title" not in create_state_body
        or "message" not in create_state_body
    ):
        result.fail(
            "states",
            "createStateCard must construct user-facing dynamic state output",
        )

    render_catalog_body = javascript_function_body(script, "renderCatalog")
    if render_catalog_body is None:
        result.fail("states", "function renderCatalog is missing or unparseable")
    else:
        if not re.search(
            r"No courses (?:match|are available)",
            render_catalog_body,
            re.I,
        ):
            result.fail(
                "states",
                "renderCatalog lacks user-facing empty-result text",
            )
        if not re.search(
            r"(?:replaceChildren|append)\s*\(",
            render_catalog_body,
        ):
            result.fail(
                "states",
                "renderCatalog does not place its empty state in the page",
            )

    load_error_body = javascript_function_body(script, "renderLoadError")
    if load_error_body is None:
        result.fail("states", "function renderLoadError is missing or unparseable")
    else:
        if "createStateCard" not in load_error_body or not re.search(
            r"(?:replaceChildren|append)\s*\(",
            load_error_body,
        ):
            result.fail(
                "states",
                "renderLoadError does not render a dynamic error card",
            )
        if not re.search(
            r"did not load|could not be loaded|unavailable|failed to load",
            load_error_body,
            re.I,
        ):
            result.fail(
                "states",
                "renderLoadError lacks user-facing failure text",
            )

    viewport = next(
        (
            element.attrs.get("content", "")
            for element in parser.elements
            if element.tag == "meta"
            and element.attrs.get("name", "").casefold() == "viewport"
        ),
        "",
    )
    if re.search(r"user-scalable\s*=\s*no", viewport, re.I):
        result.fail("accessibility", "user-scalable=no is forbidden")
    if "offsetparent" in lower_script:
        result.fail("accessibility", "offsetParent visibility logic is forbidden")
    # The site-wide Microsoft Clarity block (tools/clarity_tag.py) is the one
    # sanctioned analytics surface: consent-gated, github.io-only, GPC/DNT-aware.
    # Everything else that looks like tracking stays forbidden.
    if ANALYTICS_RE.search(strip_clarity_tag(source)):
        result.fail("security", "analytics or tracking code is forbidden")
    if AUTO_SUBMISSION_RE.search(script) or MUTATING_METHOD_RE.search(script):
        result.fail("security", "automatic public submission primitives are forbidden")
    for form in (
        element for element in parser.elements if element.tag == "form"
    ):
        if form.attrs.get("method", "get").casefold() != "get":
            result.fail("security", "mutating form submissions are forbidden")
    for image in (
        element for element in parser.elements if element.tag == "img"
    ):
        src = image.attrs.get("src", "")
        dimensions = {
            image.attrs.get("width", ""),
            image.attrs.get("height", ""),
        }
        style = image.attrs.get("style", "").replace(" ", "").casefold()
        if (
            urlsplit(src).scheme
            and (
                "1" in dimensions
                or "width:1px" in style
                or "height:1px" in style
            )
        ):
            result.fail("security", "tracking-pixel-like external image is forbidden")

    for target in sorted(REQUIRED_ACADEMY_LINKS):
        if not _links_to(parser, "academy.html", target):
            result.fail("navigation", f"academy.html does not link to {target}")


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag.casefold() != "a":
            return
        data = {name.casefold(): value or "" for name, value in attrs}
        if data.get("href"):
            self.hrefs.append(data["href"])


def _integration_links_to_academy(page_path: str, source: str) -> bool:
    source = normalize_source(source)
    if page_path.casefold().endswith(".md"):
        hrefs = re.findall(r"\[[^\]]+\]\(\s*([^) \t]+)", source)
        hrefs.extend(
            re.findall(r"<a\b[^>]*\bhref=['\"]([^'\"]+)['\"]", source, re.I)
        )
    else:
        parser = LinkParser()
        parser.feed(source)
        parser.close()
        hrefs = parser.hrefs
    return any(
        _normalized_href(page_path, href) == "academy.html" for href in hrefs
    )


def audit_integration_sources(
    sources: Mapping[str, str],
    result: AuditResult,
) -> None:
    linked = 0
    for page_path in REQUIRED_INTEGRATION_PAGES:
        source = sources.get(page_path)
        if not isinstance(source, str):
            result.fail("navigation", f"{page_path}: source cannot be measured")
            continue
        if _integration_links_to_academy(page_path, source):
            linked += 1
        else:
            result.fail("navigation", f"{page_path}: Academy link is missing")
    result.measure("integration_links", linked)


def load_integration_sources(
    root: Path,
    result: AuditResult,
) -> dict[str, str]:
    return {
        page_path: read_text(root / page_path, result, "navigation")
        for page_path in REQUIRED_INTEGRATION_PAGES
    }


def finalize_measurements(result: AuditResult) -> None:
    for name in REQUIRED_MEASUREMENTS:
        if name not in result.measurements:
            result.fail("measurement", f"required measurement {name!r} is unavailable")


def audit(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    result = AuditResult()
    data = read_json(root / "academy.json", result, "schema")
    audit_academy_data(root, data, result)
    academy_html = read_text(root / "academy.html", result, "html")
    audit_academy_html(academy_html, result)
    audit_integration_sources(load_integration_sources(root, result), result)
    finalize_measurements(result)
    return result.as_dict()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root to audit (default: script parent)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the complete machine-readable report",
    )
    return parser.parse_args(argv)


def _human_report(report: Mapping[str, Any]) -> str:
    status = str(report.get("status", "fail")).upper()
    lines = [f"[{status}] Microsoft AI Academy acceptance gate"]
    measurements = report.get("measurements", {})
    if isinstance(measurements, Mapping) and measurements:
        rendered = ", ".join(
            f"{name}={value}" for name, value in sorted(measurements.items())
        )
        lines.append(f"Measurements: {rendered}")
    failures = report.get("failures", {})
    if isinstance(failures, Mapping):
        for category, messages in failures.items():
            if not isinstance(messages, list):
                continue
            for message in messages:
                lines.append(f"- {category}: {message}")
    if status == "PASS":
        lines.append("All Academy data, UI, safety, and integration checks passed.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = audit(args.root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        stream = sys.stdout if report["status"] == "pass" else sys.stderr
        print(_human_report(report), file=stream)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
