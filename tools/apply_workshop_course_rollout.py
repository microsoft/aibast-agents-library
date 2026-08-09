#!/usr/bin/env python3
"""Apply the conservative visual contract and scaffold advertised workshops."""

from __future__ import annotations

import argparse
import contextlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import scaffold_solution_journey as journey  # noqa: E402


EXPECTED_ADVERTISED_COUNT = 51
REFERENCE_SLUG = "time-entry-billing"
CONTRACT_SCHEMA = "aibast-visual-checkpoints/1.0"
SUMMARY_SCHEMA = "aibast-workshop-course-rollout/1.0"
RESHOOT_REASON = (
    "This existing capture was not independently revalidated for a positive "
    "deterministic learner anchor and is hidden from learner pages until "
    "independently approved."
)
POLICY = {
    "machine_gate": (
        "The full locked case passes only when the deterministic validator "
        "confirms every must_include and must_not_include marker against the "
        "final response."
    ),
    "visual_gate": (
        "A reusable screenshot must show at least one positive deterministic "
        "anchor from the expected state and must not show a blocker or refusal."
    ),
    "partial_rule": (
        "An annotated screenshot is a learner-facing visual checkpoint, not a "
        "substitute for the full machine gate."
    ),
    "reshoot_rule": (
        "Reshoot when the target state is absent, the response is blocked or "
        "refusing, or no positive deterministic anchor is visible."
    ),
}
SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
DRAFT_RE = re.compile(r"\b(?:draft|confirm)\b", re.IGNORECASE)


class RolloutError(RuntimeError):
    """Raised when rollout inputs are incomplete or inconsistent."""


@dataclass(frozen=True)
class AdvertisedSolution:
    name: str
    slug: str


@dataclass(frozen=True)
class RolloutInputs:
    case_ids: tuple[str, ...]
    assisted_frames: tuple[dict[str, Any], ...]
    manual_frames: tuple[dict[str, Any], ...]


def read_json_object(path: Path, description: str) -> dict[str, Any]:
    if not path.is_file():
        raise RolloutError(f"Required {description} is missing: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RolloutError(f"Cannot read {description} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RolloutError(f"Expected a JSON object in {description}: {path}")
    return value


def resolve_advertised_solutions(
    root: Path = ROOT,
    *,
    expected_count: int | None = EXPECTED_ADVERTISED_COUNT,
) -> dict[str, AdvertisedSolution]:
    """Resolve catalog-advertised names to registry package slugs."""

    catalog = read_json_object(root / "solutions" / "catalog.json", "solution catalog")
    registry = read_json_object(root / "registry.json", "registry")
    catalog_entries = catalog.get("solutions")
    registry_agents = registry.get("agents")
    if not isinstance(catalog_entries, dict):
        raise RolloutError("solutions/catalog.json must contain a solutions object")
    if not isinstance(registry_agents, list):
        raise RolloutError("registry.json must contain an agents array")

    agents_by_name: dict[str, dict[str, Any]] = {}
    for item in registry_agents:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            continue
        name = item["name"]
        if name in agents_by_name:
            raise RolloutError(f"Registry contains duplicate agent name: {name}")
        agents_by_name[name] = item

    resolved: dict[str, AdvertisedSolution] = {}
    for name in catalog_entries:
        if not isinstance(name, str):
            raise RolloutError("Solution catalog keys must be strings")
        agent = agents_by_name.get(name)
        if agent is None:
            raise RolloutError(f"Advertised catalog solution is absent from registry: {name}")
        solution = agent.get("_solution")
        package = solution.get("package") if isinstance(solution, dict) else None
        slug = package.get("slug") if isinstance(package, dict) else None
        if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
            raise RolloutError(f"Registry package slug is missing or invalid for {name}")
        demo = agent.get("_demo")
        demo_slug = demo.get("slug") if isinstance(demo, dict) else None
        if demo_slug is not None and demo_slug != slug:
            raise RolloutError(
                f"Registry package/demo slug mismatch for {name}: {slug} != {demo_slug}"
            )
        if slug in resolved:
            raise RolloutError(
                f"Advertised catalog solutions resolve to duplicate package slug: {slug}"
            )
        resolved[slug] = AdvertisedSolution(name=name, slug=slug)

    if expected_count is not None and len(resolved) != expected_count:
        raise RolloutError(
            f"Expected exactly {expected_count} advertised solution slugs; "
            f"resolved {len(resolved)}"
        )
    if "grid-outage-response" in resolved:
        raise RolloutError(
            "Registry-only grid-outage-response must not enter advertised rollout scope"
        )
    return dict(sorted(resolved.items()))


def select_targets(
    advertised: dict[str, AdvertisedSolution],
    *,
    slug: str | None,
    all_packages: bool,
) -> tuple[list[AdvertisedSolution], list[dict[str, str]]]:
    if all_packages:
        skipped: list[dict[str, str]] = []
        targets: list[AdvertisedSolution] = []
        for item in advertised.values():
            if item.slug == REFERENCE_SLUG:
                skipped.append(
                    {
                        "slug": item.slug,
                        "reason": (
                            "Preserved as the individually reviewed visual-contract "
                            "reference package."
                        ),
                    }
                )
            else:
                targets.append(item)
        return targets, skipped

    if slug not in advertised:
        raise RolloutError(f"Slug is not an advertised solution package: {slug}")
    return [advertised[slug]], []


def _case_ids(document: dict[str, Any], path: Path) -> tuple[str, ...]:
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise RolloutError(f"Locked demo case list is missing or empty: {path}")
    result: list[str] = []
    for index, case in enumerate(cases, 1):
        case_id = case.get("id") if isinstance(case, dict) else None
        if not isinstance(case_id, str) or not case_id.strip():
            raise RolloutError(f"Locked demo case {index} has no string id: {path}")
        case_id = case_id.strip()
        if case_id in result:
            raise RolloutError(f"Locked demo case id is duplicated in {path}: {case_id}")
        result.append(case_id)
    return tuple(result)


def _frames(
    document: dict[str, Any],
    path: Path,
    *,
    required: bool,
) -> tuple[dict[str, Any], ...]:
    frames = document.get("frames")
    if not isinstance(frames, list) or (required and not frames):
        qualifier = "missing or empty" if required else "invalid"
        raise RolloutError(f"Browserfilm frames are {qualifier}: {path}")
    result: list[dict[str, Any]] = []
    for index, frame in enumerate(frames, 1):
        if not isinstance(frame, dict):
            raise RolloutError(f"Browserfilm frame {index} is not an object: {path}")
        filename = frame.get("file")
        if not isinstance(filename, str) or not filename.strip():
            raise RolloutError(f"Browserfilm frame {index} has no file: {path}")
        result.append(frame)
    return tuple(result)


def load_rollout_inputs(root: Path, slug: str) -> RolloutInputs:
    package = root / "solutions" / slug
    if not package.is_dir():
        raise RolloutError(f"Required solution package is missing: {package}")

    cases_path = root / "tests" / "demo_cases" / f"{slug}.json"
    manual_path = package / "screenshots" / "manual" / "browserfilm.json"
    assisted_path = package / "screenshots" / "assisted" / "browserfilm.json"

    case_ids = _case_ids(read_json_object(cases_path, "locked demo cases"), cases_path)
    manual_frames = _frames(
        read_json_object(manual_path, "manual browserfilm"),
        manual_path,
        required=True,
    )
    assisted_frames: tuple[dict[str, Any], ...] = ()
    if assisted_path.exists():
        assisted_frames = _frames(
            read_json_object(assisted_path, "assisted browserfilm"),
            assisted_path,
            required=False,
        )
    return RolloutInputs(case_ids, assisted_frames, manual_frames)


def _safe_filename(frame: dict[str, Any]) -> str:
    filename = str(frame["file"]).strip()
    path = PurePosixPath(filename)
    if "\\" in filename or path.is_absolute() or ".." in path.parts:
        raise RolloutError(f"Browserfilm frame uses an unsafe source path: {filename}")
    return path.as_posix()


def _label(frame: dict[str, Any]) -> str:
    value = frame.get("label", "")
    return value.strip() if isinstance(value, str) else str(value).strip()


def _explicit_case_id(label: str, case_ids: tuple[str, ...]) -> str | None:
    matches = [
        case_id
        for case_id in case_ids
        if re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(case_id)}(?![A-Za-z0-9_])",
            label,
            re.IGNORECASE,
        )
    ]
    if len(matches) > 1:
        raise RolloutError(
            f"Browserfilm label references multiple locked cases: {label}"
        )
    return matches[0] if matches else None


def _is_draft_or_confirm(frame: dict[str, Any]) -> bool:
    return bool(DRAFT_RE.search(_label(frame)))


def _unique_capture_id(base: str, used: dict[str, int]) -> str:
    used[base] = used.get(base, 0) + 1
    return base if used[base] == 1 else f"{base}-{used[base]:02d}"


def _assisted_captures(
    slug: str,
    case_ids: tuple[str, ...],
    frames: tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    classifications: list[tuple[str | None, bool]] = []
    explicitly_used: set[str] = set()
    for frame in frames:
        is_draft = _is_draft_or_confirm(frame)
        explicit = None if is_draft else _explicit_case_id(_label(frame), case_ids)
        if explicit:
            explicitly_used.add(explicit)
        classifications.append((explicit, is_draft))

    remaining = [case_id for case_id in case_ids if case_id not in explicitly_used]
    remaining_index = 0
    assigned: list[tuple[str | None, bool]] = []
    for explicit, is_draft in classifications:
        case_id = explicit
        if case_id is None and not is_draft and remaining_index < len(remaining):
            case_id = remaining[remaining_index]
            remaining_index += 1
        assigned.append((case_id, is_draft))

    captures: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    used_ids: dict[str, int] = {}
    for index, (frame, (case_id, is_draft)) in enumerate(
        zip(frames, assigned), 1
    ):
        filename = _safe_filename(frame)
        source = f"solutions/{slug}/screenshots/assisted/{filename}"
        if case_id:
            reference = f"case:{case_id}"
            base_id = f"easy-{case_id.lower()}"
        elif is_draft:
            reference = f"draft:{_label(frame)}"
            base_id = "easy-draft"
        else:
            reference = f"frame:{_label(frame)}"
            base_id = f"easy-frame-{index:02d}"
        key = ("easy", reference, source)
        if key in seen:
            continue
        seen.add(key)
        capture: dict[str, Any] = {
            "id": _unique_capture_id(base_id, used_ids),
            "mode": "easy",
            "source": source,
            "status": "reshoot_required",
            "reason": RESHOOT_REASON,
        }
        if case_id:
            capture["case_id"] = case_id
        captures.append(capture)
    return captures


def _manual_captures(
    slug: str,
    case_ids: tuple[str, ...],
    frames: tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    captures: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()
    for step, frame in enumerate(frames, 1):
        filename = _safe_filename(frame)
        source = f"solutions/{slug}/screenshots/manual/{filename}"
        key = ("hard", step, source)
        if key in seen:
            continue
        seen.add(key)
        capture: dict[str, Any] = {
            "id": f"hard-step-{step:02d}",
            "mode": "hard",
            "step": step,
            "source": source,
            "status": "reshoot_required",
            "reason": RESHOOT_REASON,
        }
        if not _is_draft_or_confirm(frame):
            case_id = _explicit_case_id(_label(frame), case_ids)
            if case_id:
                capture["case_id"] = case_id
        captures.append(capture)
    return captures


def build_visual_contract(
    solution: AdvertisedSolution,
    inputs: RolloutInputs,
) -> dict[str, Any]:
    captures = _assisted_captures(
        solution.slug,
        inputs.case_ids,
        inputs.assisted_frames,
    )
    captures.extend(
        _manual_captures(
            solution.slug,
            inputs.case_ids,
            inputs.manual_frames,
        )
    )
    total = len(captures)
    return {
        "schema": CONTRACT_SCHEMA,
        "solution": solution.name,
        "policy": dict(POLICY),
        "summary": {
            "total_existing_captures": total,
            "reusable": 0,
            "reshoot_required": total,
            "new_learn_step_captures_recommended": 0,
        },
        "captures": captures,
    }


def write_visual_contract(
    root: Path,
    solution: AdvertisedSolution,
    inputs: RolloutInputs,
    *,
    force: bool,
) -> tuple[str, dict[str, Any] | None]:
    path = root / "solutions" / solution.slug / "evals" / "visual-checkpoints.json"
    existed = path.exists()
    if existed and not force:
        return "preserved", None
    document = build_visual_contract(solution, inputs)
    try:
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise RolloutError(f"Cannot write visual checkpoint contract {path}: {exc}") from exc
    return ("replaced" if existed else "created"), document


def apply_package(
    root: Path,
    solution: AdvertisedSolution,
    *,
    raw_base: str,
    build_export: bool,
    force_visual_contract: bool,
    preflight_func: Callable[..., Any] | None = None,
    scaffold_func: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    inputs = load_rollout_inputs(root, solution.slug)
    preflight = preflight_func or journey.load_context
    scaffold = scaffold_func or journey.scaffold
    preflight(
        root,
        solution.slug,
        allow_pending=False,
        raw_base=raw_base,
    )
    contract_state, document = write_visual_contract(
        root,
        solution,
        inputs,
        force=force_visual_contract,
    )
    scaffold(
        solution.slug,
        root=root,
        allow_pending=False,
        raw_base=raw_base,
        build_bundle=build_export,
    )
    return {
        "slug": solution.slug,
        "visual_contract": contract_state,
        "capture_count": (
            document["summary"]["total_existing_captures"]
            if document is not None
            else None
        ),
        "export_built": build_export,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Apply conservative visual-checkpoint contracts and scaffold "
            "advertised workshop course packages."
        )
    )
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--slug", help="Apply one advertised solution package slug.")
    scope.add_argument(
        "--all",
        action="store_true",
        help="Apply all advertised packages except the reviewed Billing reference.",
    )
    parser.add_argument(
        "--raw-base",
        default=journey.DEFAULT_RAW_BASE,
        help="Raw repository base URL passed to the journey scaffolder.",
    )
    parser.add_argument(
        "--build-export",
        action="store_true",
        help="Build each source ZIP after successful generation.",
    )
    parser.add_argument(
        "--force-visual-contract",
        action="store_true",
        help="Replace an existing visual-checkpoints.json instead of preserving it.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Write the final machine-readable summary to stdout.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help=argparse.SUPPRESS,
    )
    return parser.parse_args(argv)


def _progress(message: str, *, json_mode: bool) -> None:
    print(message, file=sys.stderr if json_mode else sys.stdout)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.repo_root.resolve()
    summary: dict[str, Any] = {
        "schema": SUMMARY_SCHEMA,
        "completed": [],
        "failed": [],
        "skipped": [],
    }
    try:
        advertised = resolve_advertised_solutions(root)
        targets, skipped = select_targets(
            advertised,
            slug=args.slug,
            all_packages=args.all,
        )
        summary["advertised_count"] = len(advertised)
        summary["requested_count"] = len(targets)
        summary["skipped"] = skipped
    except Exception as exc:
        error = str(exc)
        summary["failed"].append({"slug": args.slug, "error": error})
        _progress(f"[ERROR] {error}", json_mode=args.json)
        if args.json:
            print(json.dumps(summary, indent=2))
        return 2

    _progress(
        f"[SCOPE] Resolved {len(advertised)} advertised packages; "
        f"processing {len(targets)} sequentially.",
        json_mode=args.json,
    )
    for item in targets:
        _progress(f"[START] {item.slug}", json_mode=args.json)
        try:
            output = (
                contextlib.redirect_stdout(sys.stderr)
                if args.json
                else contextlib.nullcontext()
            )
            with output:
                result = apply_package(
                    root,
                    item,
                    raw_base=args.raw_base,
                    build_export=args.build_export,
                    force_visual_contract=args.force_visual_contract,
                )
        except Exception as exc:
            error = str(exc)
            summary["failed"].append({"slug": item.slug, "error": error})
            _progress(f"[ERROR] {item.slug}: {error}", json_mode=args.json)
            continue
        summary["completed"].append(result)
        _progress(
            f"[OK] {item.slug}: visual contract {result['visual_contract']}",
            json_mode=args.json,
        )

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(
            f"[DONE] {len(summary['completed'])} completed, "
            f"{len(summary['failed'])} failed, "
            f"{len(summary['skipped'])} skipped."
        )
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
