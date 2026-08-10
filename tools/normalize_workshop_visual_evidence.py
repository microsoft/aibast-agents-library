#!/usr/bin/env python3
"""Deterministically normalize workshop visual evidence without creating proof."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import annotate_visual_evidence as annotate_tool  # noqa: E402
from tools import audit_workshop_course_rollout as course  # noqa: E402
from tools import audit_workshop_first_release as release  # noqa: E402


CASE_PATTERN = re.compile(
    r"(?<![A-Z0-9_])([A-Z][A-Z0-9_]*-\d+)(?![A-Z0-9_])"
)
REUSABLE_INPUT_STATUSES = {"reusable", "approved"}


@dataclass(frozen=True)
class Binding:
    mode: str
    step: int | None = None
    case_id: str | None = None
    draft: bool = False


@dataclass(frozen=True)
class ImageInfo:
    width: int
    height: int
    digest: str
    format: str | None


@dataclass
class Candidate:
    index: int
    capture: dict[str, Any]
    binding: Binding
    source: Path
    annotated: Path
    source_info: ImageInfo
    annotated_info: ImageInfo


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _image_info(path: Path) -> tuple[ImageInfo | None, str | None]:
    try:
        with Image.open(path) as image:
            image.load()
            pixels = image.convert("RGBA")
            width, height = pixels.size
            digest = hashlib.sha256(pixels.tobytes()).hexdigest()
            return ImageInfo(width, height, digest, image.format), None
    except Exception as exc:
        return None, str(exc)


def _frame_binding(mode: str, index: int, frame: dict[str, Any]) -> Binding | None:
    label = str(frame.get("label", ""))
    case_match = CASE_PATTERN.search(label)
    case_id = case_match.group(1) if case_match else None
    if mode == "hard":
        return Binding(mode="hard", step=index, case_id=case_id)
    if case_id:
        return Binding(mode="easy", case_id=case_id)
    if "draft" in label.lower() or "confirm" in label.lower():
        return Binding(mode="easy", draft=True)
    return None


def _browserfilm_bindings(
    root: Path, package: Path
) -> tuple[dict[Path, set[Binding]], list[str]]:
    bindings: dict[Path, set[Binding]] = {}
    problems: list[str] = []
    for mode, directory in (("easy", "assisted"), ("hard", "manual")):
        film_path = package / "screenshots" / directory / "browserfilm.json"
        try:
            document = _read_json(film_path)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            problems.append(f"{directory} browserfilm is unreadable: {exc}")
            continue
        frames = document.get("frames") if isinstance(document, dict) else None
        if not isinstance(frames, list):
            problems.append(f"{directory} browserfilm frames are not a list")
            continue
        for index, frame in enumerate(frames, start=1):
            if not isinstance(frame, dict) or not isinstance(frame.get("file"), str):
                problems.append(
                    f"{directory} browserfilm frame {index} has no source file"
                )
                continue
            source = course.relative_path(root, film_path.parent, frame["file"])
            binding = _frame_binding(mode, index, frame)
            if source is None or binding is None:
                continue
            bindings.setdefault(source.resolve(), set()).add(binding)
    return bindings, problems


def _locked_case_ids(root: Path, slug: str) -> set[str]:
    path = root / "tests" / "demo_cases" / f"{slug}.json"
    try:
        document = _read_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return set()
    return set(release._case_ids(document))


def _apply_binding(capture: dict[str, Any], binding: Binding) -> None:
    capture["mode"] = binding.mode
    if binding.draft:
        capture["draft"] = True
    else:
        capture.pop("draft", None)
    if binding.step is None:
        capture.pop("step", None)
    else:
        capture["step"] = binding.step
    if binding.case_id is None:
        capture.pop("case_id", None)
    else:
        capture["case_id"] = binding.case_id


def _demote(capture: dict[str, Any], reason: str) -> None:
    capture["status"] = "reshoot_required"
    capture["reason"] = reason
    capture.pop("annotated", None)
    capture.pop("visible_anchors", None)
    capture.pop("boxes", None)


def _valid_anchors(capture: dict[str, Any]) -> bool:
    anchors = capture.get("visible_anchors")
    return (
        isinstance(anchors, list)
        and bool(anchors)
        and all(isinstance(anchor, str) and anchor.strip() for anchor in anchors)
    )


def _box_problem(
    capture: dict[str, Any], width: int, height: int
) -> str | None:
    boxes = capture.get("boxes")
    if not isinstance(boxes, list) or not boxes:
        return "Reusable evidence has no annotation boxes."
    for index, box in enumerate(boxes, start=1):
        if not isinstance(box, dict):
            return f"Annotation box {index} is not an object."
        values = tuple(
            course.numeric(box.get(key)) for key in ("x", "y", "width", "height")
        )
        if any(value is None for value in values):
            return f"Annotation box {index} has nonnumeric coordinates."
        x, y, box_width, box_height = values
        assert x is not None and y is not None
        assert box_width is not None and box_height is not None
        if (
            x < 0
            or y < 0
            or box_width <= 0
            or box_height <= 0
            or x + box_width > width
            or y + box_height > height
        ):
            return (
                f"Annotation box {index} is outside the "
                f"{width}x{height} source bounds."
            )
    return None


def _candidate(
    root: Path,
    package: Path,
    index: int,
    capture: dict[str, Any],
    binding: Binding,
) -> tuple[Candidate | None, str | None]:
    source_raw = capture.get("source")
    source = (
        course.relative_path(root, package, source_raw)
        if isinstance(source_raw, str)
        else None
    )
    if source is None or not source.is_file():
        return None, "Reusable evidence source image is missing or unsafe."
    annotated_raw = capture.get("annotated")
    annotated = (
        course.relative_path(root, package, annotated_raw)
        if isinstance(annotated_raw, str)
        else None
    )
    if (
        annotated is None
        or Path(str(annotated_raw)).suffix.lower() != ".png"
        or not annotated.is_file()
    ):
        return None, "Reusable evidence annotation is missing or is not a PNG path."
    source_info, source_error = _image_info(source)
    if source_info is None:
        return None, f"Reusable evidence source image cannot be decoded: {source_error}."
    annotated_info, annotated_error = _image_info(annotated)
    if annotated_info is None:
        return None, (
            "Reusable evidence annotation cannot be decoded: "
            f"{annotated_error}."
        )
    if annotated_info.format != "PNG":
        return None, "Reusable evidence annotation content is not PNG."
    if not _valid_anchors(capture):
        return None, "Reusable evidence has no nonempty visible anchors."
    box_problem = _box_problem(capture, source_info.width, source_info.height)
    if box_problem:
        return None, box_problem
    if (
        source_info.width,
        source_info.height,
    ) != (
        annotated_info.width,
        annotated_info.height,
    ):
        return None, "Reusable evidence annotation dimensions differ from its source."
    if source_info.digest == annotated_info.digest:
        return None, "Reusable evidence annotation is pixel-identical to its source."
    return (
        Candidate(
            index=index,
            capture=capture,
            binding=binding,
            source=source.resolve(),
            annotated=annotated.resolve(),
            source_info=source_info,
            annotated_info=annotated_info,
        ),
        None,
    )


def _rank(candidate: Candidate, locked_cases: set[str]) -> tuple[Any, ...]:
    binding = candidate.binding
    if binding.mode == "easy" and binding.case_id in locked_cases:
        category = 0
    elif binding.mode == "easy" and binding.draft:
        category = 1
    elif binding.mode == "hard" and binding.case_id in locked_cases:
        category = 2
    else:
        category = 3
    step = binding.step if binding.step is not None else sys.maxsize
    capture_id = str(candidate.capture.get("id", ""))
    return category, step, capture_id, candidate.index


def _duplicate_components(candidates: list[Candidate]) -> list[list[Candidate]]:
    parent = list(range(len(candidates)))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    groups: dict[tuple[str, object], int] = {}
    for index, candidate in enumerate(candidates):
        keys = (
            ("source-path", candidate.source),
            ("annotation-path", candidate.annotated),
            (
                "source-content",
                (
                    candidate.source_info.width,
                    candidate.source_info.height,
                    candidate.source_info.digest,
                ),
            ),
            (
                "annotation-content",
                (
                    candidate.annotated_info.width,
                    candidate.annotated_info.height,
                    candidate.annotated_info.digest,
                ),
            ),
        )
        for key in keys:
            if key in groups:
                union(index, groups[key])
            else:
                groups[key] = index
    components: dict[int, list[Candidate]] = {}
    for index, candidate in enumerate(candidates):
        components.setdefault(find(index), []).append(candidate)
    return [items for items in components.values() if len(items) > 1]


def _review_is_structurally_valid(review: Any, slug: str) -> bool:
    return (
        isinstance(review, dict)
        and review.get("status") == "approved"
        and review.get("reviewer") == f"workshop-builder:{slug}"
        and all(
            isinstance(review.get(field), str) and review[field].strip()
            for field in ("reviewed_at", "method", "notes")
        )
    )


def _may_preserve_release_review(
    root: Path,
    package: Path,
    document: dict[str, Any],
    slug: str,
    locked_cases: set[str],
    bindings_by_index: dict[int, Binding],
) -> bool:
    captures = [
        capture
        for capture in document.get("captures", [])
        if isinstance(capture, dict)
    ]
    reusable = [
        capture for capture in captures if capture.get("status") == "reusable"
    ]
    visually_covered = {
        capture.get("case_id")
        for capture in reusable
        if isinstance(capture.get("case_id"), str)
    }
    covered = visually_covered | release._machine_case_ids(root, package)
    draft_identities = release._draft_agent_identities(package)
    drafts = [
        capture
        for index, capture in enumerate(captures)
        if capture.get("status") == "reusable"
        and bindings_by_index.get(index) is not None
        and "draft" in " ".join(
            str(value)
            for value in capture.get("visible_anchors", [])
            if isinstance(value, str)
        ).casefold()
        and any(
            identity.casefold() in " ".join(
                str(value)
                for value in capture.get("visible_anchors", [])
                if isinstance(value, str)
            ).casefold()
            for identity in draft_identities
        )
    ]
    draft_proven = bool(drafts) or release._machine_draft_proven(package)
    hard_count = sum(capture.get("mode") == "hard" for capture in reusable)
    required = max(10, math.ceil(len(captures) * 0.35))
    reason_text = " ".join(release._strings(document)).lower()
    no_generic_reasons = (
        release.GENERIC_REASON not in reason_text
        and release.GENERIC_REASON_SINGULAR not in reason_text
    )
    return (
        _review_is_structurally_valid(document.get("release_review"), slug)
        and locked_cases.issubset(covered)
        and draft_proven
        and hard_count >= 5
        and len(reusable) >= required
        and no_generic_reasons
    )


def normalize_workshop(
    slug: str,
    *,
    root: Path = ROOT,
    dry_run: bool = False,
) -> dict[str, Any]:
    root = root.resolve()
    package = root / "solutions" / slug
    spec_path = package / "evals" / "visual-checkpoints.json"
    result: dict[str, Any] = {
        "slug": slug,
        "changed": False,
        "captures": 0,
        "reusable_before": 0,
        "reusable_after": 0,
        "demoted": 0,
        "binding_corrections": 0,
        "release_review_removed": False,
        "annotations_regenerated": 0,
        "problems": [],
    }
    try:
        original_text = spec_path.read_text(encoding="utf-8")
        document = json.loads(original_text)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        result["problems"].append(f"visual checkpoint document is unreadable: {exc}")
        return result
    if not isinstance(document, dict):
        result["problems"].append("visual checkpoint document is not an object")
        return result
    captures = document.get("captures")
    if not isinstance(captures, list):
        result["problems"].append("captures is not a list")
        return result

    bindings, film_problems = _browserfilm_bindings(root, package)
    result["problems"].extend(film_problems)
    locked_cases = _locked_case_ids(root, slug)
    result["captures"] = len(captures)
    result["reusable_before"] = sum(
        isinstance(capture, dict)
        and capture.get("status") in REUSABLE_INPUT_STATUSES
        for capture in captures
    )
    candidates: list[Candidate] = []
    bindings_by_index: dict[int, Binding] = {}

    for index, capture in enumerate(captures):
        if not isinstance(capture, dict):
            result["problems"].append(f"capture {index + 1} is not an object")
            continue
        source_raw = capture.get("source")
        source = (
            course.relative_path(root, package, source_raw)
            if isinstance(source_raw, str)
            else None
        )
        actual = bindings.get(source.resolve(), set()) if source is not None else set()
        capture_id = str(capture.get("id") or f"#{index + 1}")
        if len(actual) != 1:
            reason = (
                "Source is not classifiable through exactly one assisted or "
                "manual browserfilm frame."
            )
            if capture.get("status") != "reshoot_required" or any(
                key in capture for key in ("annotated", "visible_anchors", "boxes")
            ):
                result["demoted"] += 1
            _demote(capture, reason)
            continue
        binding = next(iter(actual))
        bindings_by_index[index] = binding
        before = (
            capture.get("mode"),
            capture.get("step"),
            capture.get("case_id"),
        )
        _apply_binding(capture, binding)
        after = (
            capture.get("mode"),
            capture.get("step"),
            capture.get("case_id"),
        )
        if before != after:
            result["binding_corrections"] += 1

        if capture.get("status") not in REUSABLE_INPUT_STATUSES:
            if capture.get("status") != "reshoot_required":
                _demote(
                    capture,
                    f"Unsupported visual evidence status {capture.get('status')!r}.",
                )
                result["demoted"] += 1
            else:
                capture.pop("annotated", None)
                capture.pop("visible_anchors", None)
                capture.pop("boxes", None)
                reason = capture.get("reason")
                if not isinstance(reason, str) or not reason.strip():
                    capture["reason"] = (
                        "Evidence remains reshoot-required because no reusable "
                        "visual proof was established."
                    )
            continue

        candidate, problem = _candidate(
            root, package, index, capture, binding
        )
        if problem is not None:
            _demote(capture, problem)
            result["demoted"] += 1
            continue
        assert candidate is not None
        capture["status"] = "reusable"
        capture.pop("reason", None)
        candidates.append(candidate)

    duplicate_losers: set[int] = set()
    for component in _duplicate_components(candidates):
        retained = min(component, key=lambda item: _rank(item, locked_cases))
        retained_id = str(retained.capture.get("id") or f"#{retained.index + 1}")
        for candidate in component:
            if candidate.index == retained.index:
                continue
            duplicate_losers.add(candidate.index)
            _demote(
                candidate.capture,
                f"Duplicate visual evidence; retained capture {retained_id}.",
            )
    result["demoted"] += len(duplicate_losers)

    document["summary"] = {
        "total_existing_captures": len(captures),
        "reusable": sum(
            isinstance(capture, dict) and capture.get("status") == "reusable"
            for capture in captures
        ),
        "reshoot_required": sum(
            isinstance(capture, dict)
            and capture.get("status") == "reshoot_required"
            for capture in captures
        ),
    }
    if "release_review" in document and not _may_preserve_release_review(
        root,
        package,
        document,
        slug,
        locked_cases,
        bindings_by_index,
    ):
        document.pop("release_review", None)
        result["release_review_removed"] = True

    result["reusable_after"] = document["summary"]["reusable"]
    normalized_text = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
    result["changed"] = normalized_text != original_text
    if not dry_run:
        if result["changed"]:
            spec_path.write_text(normalized_text, encoding="utf-8")
        reusable_to_annotate = [
            capture
            for capture in captures
            if isinstance(capture, dict) and capture.get("status") == "reusable"
        ]
        for capture in reusable_to_annotate:
            annotate_tool.annotate(capture, root=root)
        result["annotations_regenerated"] = len(reusable_to_annotate)
    return result


def normalize_repository(
    *,
    root: Path = ROOT,
    only_slug: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    failures = course.Failures()
    slugs, _exclusions = course.course_scope(root.resolve(), failures)
    if only_slug is not None:
        slugs = [only_slug]
    workshops = [
        normalize_workshop(slug, root=root, dry_run=dry_run) for slug in slugs
    ]
    return {
        "dry_run": dry_run,
        "workshops": workshops,
        "totals": {
            "workshops": len(workshops),
            "changed": sum(item["changed"] for item in workshops),
            "captures": sum(item["captures"] for item in workshops),
            "reusable_before": sum(
                item["reusable_before"] for item in workshops
            ),
            "reusable_after": sum(item["reusable_after"] for item in workshops),
            "demoted": sum(item["demoted"] for item in workshops),
            "binding_corrections": sum(
                item["binding_corrections"] for item in workshops
            ),
            "release_reviews_removed": sum(
                item["release_review_removed"] for item in workshops
            ),
            "annotations_regenerated": sum(
                item["annotations_regenerated"] for item in workshops
            ),
            "problems": len(failures.items)
            + sum(len(item["problems"]) for item in workshops),
        },
        "scope_problems": failures.items,
    }


def _print_human(report: dict[str, Any]) -> None:
    totals = report["totals"]
    action = "Would normalize" if report["dry_run"] else "Normalized"
    print(
        f"{action} {totals['workshops']} workshop(s): "
        f"{totals['reusable_before']} -> {totals['reusable_after']} reusable; "
        f"{totals['demoted']} demoted; "
        f"{totals['binding_corrections']} binding corrections"
    )
    for item in report["workshops"]:
        print(
            f"{item['slug']}: reusable "
            f"{item['reusable_before']} -> {item['reusable_after']}, "
            f"demoted={item['demoted']}, changed={str(item['changed']).lower()}"
        )
        for problem in item["problems"]:
            print(f"  - {problem}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--slug", help="normalize one workshop package")
    scope.add_argument("--all", action="store_true", help="normalize all workshops")
    parser.add_argument(
        "--dry-run", action="store_true", help="report changes without writing"
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable results"
    )
    args = parser.parse_args(argv)
    report = normalize_repository(
        root=ROOT,
        only_slug=args.slug,
        dry_run=args.dry_run,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_human(report)
    return 1 if report["totals"]["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
