#!/usr/bin/env python3
"""Fail-closed first-release gate for the 51 advertised workshops."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import audit_workshop_course_rollout as course  # noqa: E402


SCHEMA = "aibast-workshop-first-release-audit/1.0"
EXPECTED_WORKSHOPS = 51
GENERIC_REASON = "captures were not independently revalidated"
GENERIC_REASON_SINGULAR = "capture was not independently revalidated"
DRAFT_PATTERN = re.compile(
    r"\bdraft\b|confirm[-_ ]?(?:state|draft)", re.IGNORECASE
)
CSS_URL_PATTERN = re.compile(r"url\(\s*([^)]+?)\s*\)", re.IGNORECASE)


def _strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from _strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _strings(nested)


def _case_ids(data: Any) -> list[str]:
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        return []
    result: list[str] = []
    for case in data["cases"]:
        if not isinstance(case, dict):
            continue
        case_id = case.get("case_id", case.get("id"))
        if isinstance(case_id, str) and case_id.strip():
            result.append(case_id.strip())
    return result


def _draft_agent_identities(package: Path) -> set[str]:
    path = package / "deployment.json"
    try:
        deployment = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    if not isinstance(deployment, dict):
        return set()
    copilot = deployment.get("copilot_studio", {})
    if not isinstance(copilot, dict):
        return set()
    export_agent = copilot.get("export_agent")
    if isinstance(export_agent, dict):
        display_name = export_agent.get("display_name")
        return {
            display_name.strip()
            for display_name in [display_name]
            if isinstance(display_name, str) and display_name.strip()
        }
    identities = set()
    for key in ("validated_manual", "validated_pilot"):
        agent = copilot.get(key)
        display_name = (
            agent.get("display_name") if isinstance(agent, dict) else None
        )
        if isinstance(display_name, str) and display_name.strip():
            identities.add(display_name.strip())
    return identities


def _machine_draft_proven(package: Path) -> bool:
    deployment_path = package / "deployment.json"
    evidence_path = package / "evals" / "dataverse-draft-evidence.json"
    try:
        deployment = json.loads(deployment_path.read_text(encoding="utf-8"))
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if (
        not isinstance(deployment, dict)
        or not isinstance(evidence, dict)
        or evidence.get("schema") != "aibast-dataverse-draft-evidence/1.0"
    ):
        return False
    copilot = deployment.get("copilot_studio", {})
    export_agent = (
        copilot.get("export_agent")
        or copilot.get("validated_pilot")
        or {}
    ) if isinstance(copilot, dict) else {}
    if not isinstance(export_agent, dict):
        return False
    identity = evidence.get("identity")
    source = evidence.get("source")
    record = evidence.get("record")
    assertions = evidence.get("assertions")
    if not all(
        isinstance(value, dict)
        for value in (identity, source, record, assertions)
    ):
        return False
    expected_identity = {
        "slug": package.name,
        "solution": deployment.get("name"),
        "display_name": export_agent.get("display_name"),
        "schema_name": export_agent.get("schema_name"),
        "bot_id": export_agent.get("bot_id"),
    }
    if identity != expected_identity:
        return False
    if (
        source.get("kind") != "Dataverse Web API"
        or source.get("environment_name") != export_agent.get("environment_name")
        or source.get("environment_id") != export_agent.get("environment_id")
        or source.get("environment_url")
        != "https://org7dfbd855.crm.dynamics.com"
        or source.get("api_version") != "v9.2"
    ):
        return False
    if (
        record.get("botid") != export_agent.get("bot_id")
        or record.get("name") != export_agent.get("display_name")
        or record.get("publishedon") is not None
        or record.get("componentstate") != 0
        or record.get("statecode") != 0
        or record.get("statuscode") != 1
        or not isinstance(record.get("modifiedon"), str)
        or not isinstance(record.get("versionnumber"), int)
        or record["versionnumber"] <= 0
        or not re.fullmatch(r'W/"\d+"', str(record.get("odata_etag") or ""))
    ):
        return False
    synchronization = record.get("synchronizationstatus")
    if (
        not isinstance(synchronization, dict)
        or synchronization.get("lastFinishedPublishOperation") is not None
    ):
        return False
    canonical_record = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    if hashlib.sha256(canonical_record).hexdigest() != evidence.get(
        "record_sha256"
    ):
        return False
    return assertions == {
        "bot_id_matches": True,
        "display_name_matches": True,
        "publishedon_is_null": True,
        "last_finished_publish_operation_is_null": True,
    }


def _machine_case_ids(root: Path, package: Path) -> set[str]:
    evidence_path = package / "evals" / "copilot-studio-preview-evidence.json"
    transcript_path = package / "evals" / "transcripts.json"
    deployment_path = package / "deployment.json"
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        transcripts = json.loads(transcript_path.read_text(encoding="utf-8"))
        deployment = json.loads(deployment_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    copilot = deployment.get("copilot_studio", {}) if isinstance(
        deployment, dict
    ) else {}
    export_agent = (
        copilot.get("export_agent")
        or copilot.get("validated_pilot")
        or {}
    ) if isinstance(copilot, dict) else {}
    if (
        not isinstance(evidence, dict)
        or evidence.get("schema")
        != "aibast-copilot-studio-preview-evidence/1.0"
        or evidence.get("status") != "Draft"
        or evidence.get("published") is not False
        or evidence.get("display_name") != export_agent.get("display_name")
        or evidence.get("schema_name") != export_agent.get("schema_name")
        or evidence.get("bot_id") != export_agent.get("bot_id")
        or evidence.get("environment_name")
        != export_agent.get("environment_name")
        or evidence.get("environment_id")
        != export_agent.get("environment_id")
        or not _machine_draft_proven(package)
        or not isinstance(transcripts, dict)
        or transcripts.get("schema") != "aibast-canonical-transcripts/1.0"
        or transcripts.get("strict_isolation") is not True
    ):
        return set()
    preview = evidence.get("cases")
    transcript_rows = transcripts.get("transcripts")
    case_file = transcripts.get("case_file")
    case_file_sha256 = transcripts.get("case_file_sha256")
    agent_sources = transcripts.get("agent_sources")
    if (
        not isinstance(preview, list)
        or not isinstance(transcript_rows, list)
        or not isinstance(case_file, str)
        or not isinstance(case_file_sha256, str)
        or not isinstance(agent_sources, list)
        or not agent_sources
    ):
        return set()

    case_path = (root / case_file).resolve()
    if not case_path.is_relative_to(root.resolve()) or not case_path.is_file():
        return set()
    try:
        case_source = case_path.read_bytes()
        case_data = json.loads(case_source.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return set()
    if hashlib.sha256(case_source).hexdigest() != case_file_sha256:
        return set()

    for source in agent_sources:
        if not isinstance(source, dict):
            return set()
        raw_path = source.get("path")
        expected_sha256 = source.get("sha256")
        if not isinstance(raw_path, str) or not isinstance(expected_sha256, str):
            return set()
        agent_path = (root / raw_path).resolve()
        if (
            not agent_path.is_relative_to(root.resolve())
            or not agent_path.is_file()
        ):
            return set()
        try:
            actual_sha256 = hashlib.sha256(agent_path.read_bytes()).hexdigest()
        except OSError:
            return set()
        if actual_sha256 != expected_sha256:
            return set()

    locked_cases = {}
    for case in case_data.get("cases", []) if isinstance(case_data, dict) else []:
        if not isinstance(case, dict):
            continue
        case_id = case.get("case_id", case.get("id"))
        if isinstance(case_id, str) and case_id.strip():
            locked_cases[case_id.strip()] = case
    captured = {
        row.get("case_id"): row
        for row in transcript_rows
        if isinstance(row, dict) and isinstance(row.get("case_id"), str)
    }
    loaded_tools = transcripts.get("loaded_tools_after_capture")
    if not isinstance(loaded_tools, list):
        return set()

    verified: set[str] = set()
    for preview_case in preview:
        if (
            not isinstance(preview_case, dict)
            or preview_case.get("passed") is not True
            or not isinstance(preview_case.get("case_id"), str)
        ):
            continue
        case_id = preview_case["case_id"].strip()
        locked = locked_cases.get(case_id)
        transcript = captured.get(case_id)
        if not case_id or not isinstance(locked, dict) or not isinstance(
            transcript, dict
        ):
            continue
        prompt = locked.get("prompt")
        must_include = locked.get("must_include")
        must_not_include = locked.get("must_not_include")
        expected_agent = locked.get("expects_agent")
        if (
            not isinstance(prompt, str)
            or not isinstance(must_include, list)
            or not must_include
            or not all(isinstance(value, str) and value for value in must_include)
            or not isinstance(must_not_include, list)
            or not all(isinstance(value, str) for value in must_not_include)
            or not isinstance(expected_agent, str)
            or not expected_agent
        ):
            continue
        if (
            preview_case.get("prompt") != prompt
            and preview_case.get("prompt") is not None
        ):
            continue
        if (
            preview_case.get("must_include") != must_include
            or preview_case.get("must_not_include") != must_not_include
            or transcript.get("prompt") != prompt
            or transcript.get("must_include") != must_include
            or transcript.get("expected_agent") != expected_agent
            or transcript.get("passed") is not True
            or expected_agent not in loaded_tools
        ):
            continue
        output = "\n".join(
            str(transcript.get(key) or "")
            for key in ("assistant_response", "agent_logs")
        ).casefold()
        if not output.strip():
            continue
        if any(value.casefold() not in output for value in must_include):
            continue
        if any(value and value.casefold() in output for value in must_not_include):
            continue
        verified.add(case_id)
    return verified


def _capture_paths(
    root: Path,
    package: Path,
    captures: Iterable[dict[str, Any]],
) -> set[Path]:
    paths: set[Path] = set()
    for capture in captures:
        for key in ("source", "annotated"):
            raw = capture.get(key)
            if isinstance(raw, str):
                path = course.relative_path(root, package, raw)
                if path is not None:
                    paths.add(path.resolve())
    return paths


def _browserfilm_sources(
    root: Path,
    package: Path,
    mode: str,
    failures: list[str],
) -> dict[Path, set[tuple[str, str, str | int]]]:
    film_path = package / "screenshots" / (
        "manual" if mode == "hard" else "assisted"
    ) / "browserfilm.json"
    film_failures = course.Failures()
    frames, _references, _sources = course.load_browserfilm(
        root, film_path, mode, film_failures
    )
    failures.extend(
        f"browserfilm: {failure}" for failure in film_failures.items
    )
    classified: dict[Path, set[tuple[str, str, str | int]]] = {}
    for index, frame in enumerate(frames, start=1):
        if not isinstance(frame, dict) or not isinstance(frame.get("file"), str):
            continue
        source = course.relative_path(root, film_path.parent, frame["file"])
        reference = course.browserfilm_frame_reference(mode, index, frame)
        if source is not None and reference is not None:
            classified.setdefault(source.resolve(), set()).add(reference)
    return classified


def _duplicate_capture_paths(
    root: Path,
    package: Path,
    captures: Iterable[dict[str, Any]],
    key: str,
) -> list[str]:
    seen: set[Path] = set()
    duplicates: set[str] = set()
    for capture in captures:
        raw = capture.get(key)
        if not isinstance(raw, str):
            continue
        path = course.relative_path(root, package, raw)
        if path is None:
            continue
        resolved = path.resolve()
        if resolved in seen:
            duplicates.add(course.repo_name(root, resolved))
        seen.add(resolved)
    return sorted(duplicates)


def _image_fingerprint(
    root: Path,
    path: Path | None,
    label: str,
    failures: list[str],
) -> tuple[int, int, str] | None:
    if path is None:
        failures.append(f"{label} has no safe image path")
        return None
    try:
        with Image.open(path) as image:
            image.load()
            pixels = image.convert("RGBA")
            width, height = pixels.size
            digest = hashlib.sha256(pixels.tobytes()).hexdigest()
    except Exception as exc:
        failures.append(
            f"{label} cannot be decoded as an image "
            f"({course.repo_name(root, path)}: {exc})"
        )
        return None
    return width, height, digest


def _case_id(capture: dict[str, Any]) -> str | None:
    value = capture.get("case_id")
    return value.strip() if isinstance(value, str) and value.strip() else None


def _capture_claim(
    capture: dict[str, Any],
    actual: set[tuple[str, str, str | int]],
) -> tuple[str, str, str | int] | None:
    mode = capture.get("mode")
    case_id = _case_id(capture)
    hard_case = (
        ("hard", "case", case_id)
        if mode == "hard" and case_id is not None
        else None
    )
    if hard_case is not None and actual == {hard_case}:
        return hard_case
    if mode == "hard" and isinstance(capture.get("step"), int):
        return "hard", "step", capture["step"]
    if mode == "easy" and case_id is not None:
        return "easy", "case", case_id
    draft = ("easy", "draft", "draft")
    if mode == "easy" and (
        actual == {draft} or DRAFT_PATTERN.search(" ".join(_strings(capture)))
    ):
        return draft
    return None


def _audit_reusable_image_content(
    root: Path,
    package: Path,
    reusable: Iterable[dict[str, Any]],
    claims: dict[int, tuple[str, str, str | int] | None],
    failures: list[str],
) -> None:
    sources: dict[
        tuple[int, int, str],
        list[tuple[object, str, Path]],
    ] = {}
    annotations: dict[
        tuple[int, int, str],
        list[tuple[str, Path]],
    ] = {}
    for capture in reusable:
        capture_id = str(capture.get("id") or "unnamed")
        fingerprints: dict[str, tuple[int, int, str] | None] = {}
        paths: dict[str, Path | None] = {}
        for key in ("source", "annotated"):
            raw = capture.get(key)
            path = (
                course.relative_path(root, package, raw)
                if isinstance(raw, str)
                else None
            )
            paths[key] = path.resolve() if path is not None else None
            fingerprints[key] = _image_fingerprint(
                root,
                paths[key],
                f"reusable capture {capture_id} {key}",
                failures,
            )
        source_fingerprint = fingerprints["source"]
        annotated_fingerprint = fingerprints["annotated"]
        source_path = paths["source"]
        annotated_path = paths["annotated"]
        if source_fingerprint is not None and source_path is not None:
            claim: object = claims.get(id(capture))
            if claim is None:
                claim = ("capture", capture_id)
            sources.setdefault(source_fingerprint, []).append(
                (claim, capture_id, source_path)
            )
        if annotated_fingerprint is not None and annotated_path is not None:
            annotations.setdefault(annotated_fingerprint, []).append(
                (capture_id, annotated_path)
            )
        if (
            source_fingerprint is not None
            and annotated_fingerprint == source_fingerprint
        ):
            failures.append(
                f"reusable capture {capture_id} annotation is pixel-identical "
                "to its source"
            )

    for records in sources.values():
        if len({record[0] for record in records}) <= 1:
            continue
        rendered = ", ".join(
            f"{capture_id} ({course.repo_name(root, path)})"
            for _claim, capture_id, path in records
        )
        failures.append(
            "reusable source image content is duplicated across distinct "
            f"claims: {rendered}"
        )
    for records in annotations.values():
        if len(records) <= 1:
            continue
        rendered = ", ".join(
            f"{capture_id} ({course.repo_name(root, path)})"
            for capture_id, path in records
        )
        failures.append(
            f"reusable annotated image content is duplicated: {rendered}"
        )


def _srcset_urls(value: str) -> Iterable[str]:
    for candidate in value.split(","):
        parts = candidate.strip().split()
        if parts:
            yield parts[0]


def _css_urls(value: str) -> Iterable[str]:
    for match in CSS_URL_PATTERN.finditer(value):
        raw = match.group(1).strip()
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {"'", '"'}:
            raw = raw[1:-1].strip()
        if raw:
            yield raw


def _learner_asset_path(root: Path, package: Path, raw: str) -> Path | None:
    value = raw.strip()
    return (
        course.root_path(root, value)
        if value.startswith("/")
        else course.relative_path(root, package, value)
    )


def _learner_screenshot_assets(
    root: Path,
    package: Path,
    failures: list[str],
) -> tuple[list[Path], int, int, int]:
    assets: list[Path] = []
    reference_only = 0
    image_count = 0
    link_count = 0
    screenshot_root = (package / "screenshots").resolve()
    for name in ("quest.html", "manual-tutorial.html"):
        parse_failures = course.Failures()
        parsed = course.parse_html(package / name, name, parse_failures)
        failures.extend(parse_failures.items)
        if parsed is None:
            continue
        parser = parsed[1]
        for tag in parser.tags:
            if (
                tag.name == "img"
                and tag.attrs.get("data-evidence-status") == "reference-only"
            ):
                reference_only += 1
            references: list[tuple[str, str]] = []
            for attribute in ("src", "href", "xlink:href", "poster"):
                raw = tag.attrs.get(attribute)
                if raw:
                    references.append((attribute, raw))
            if tag.name == "object" and tag.attrs.get("data"):
                references.append(("data", str(tag.attrs["data"])))
            srcset = tag.attrs.get("srcset")
            if srcset:
                references.extend(
                    ("srcset", raw) for raw in _srcset_urls(srcset)
                )
            inline_style = tag.attrs.get("style")
            if inline_style:
                references.extend(
                    ("style", raw) for raw in _css_urls(inline_style)
                )
            if tag.name == "style":
                references.extend(
                    ("style-block", raw) for raw in _css_urls(tag.text)
                )
            for mechanism, raw in references:
                path = _learner_asset_path(root, package, raw)
                if (
                    path is None
                    or not course._is_within(path.resolve(), screenshot_root)
                ):
                    continue
                assets.append(path.resolve())
                if tag.name == "img" and mechanism == "src":
                    image_count += 1
                if tag.name == "a" and mechanism == "href":
                    link_count += 1
    return assets, reference_only, image_count, link_count


def audit_workshop(
    root: Path,
    slug: str,
    base_result: dict[str, Any],
) -> dict[str, Any]:
    root = root.resolve()
    package = root / "solutions" / slug
    failures: list[str] = []

    if not base_result.get("passed"):
        failures.append("base course audit did not pass")
        failures.extend(
            f"base: {failure}" for failure in base_result.get("failures", [])
        )

    visual_failures = course.Failures()
    visual = course.read_json(
        package / "evals" / "visual-checkpoints.json",
        "evals/visual-checkpoints.json",
        visual_failures,
    )
    failures.extend(visual_failures.items)
    captures = (
        visual.get("captures")
        if isinstance(visual, dict) and isinstance(visual.get("captures"), list)
        else []
    )
    captures = [item for item in captures if isinstance(item, dict)]
    reusable = [item for item in captures if item.get("status") == "reusable"]
    hard_reusable = [
        item for item in reusable if item.get("mode") == "hard"
    ]
    for key in ("source", "annotated"):
        duplicates = _duplicate_capture_paths(
            root, package, reusable, key
        )
        if duplicates:
            failures.append(
                f"reusable {key} paths must be unique: "
                + ", ".join(duplicates)
            )

    browserfilm_sources = {
        "easy": _browserfilm_sources(root, package, "easy", failures),
        "hard": _browserfilm_sources(root, package, "hard", failures),
    }
    reusable_claims: dict[
        int, tuple[str, str, str | int] | None
    ] = {}
    draft_agent_identities = _draft_agent_identities(package)
    draft_reusable: list[dict[str, Any]] = []
    for capture in reusable:
        mode = capture.get("mode")
        capture_id = str(capture.get("id") or "unnamed")
        source_raw = capture.get("source")
        source = (
            course.relative_path(root, package, source_raw)
            if isinstance(source_raw, str)
            else None
        )
        actual = (
            browserfilm_sources.get(str(mode), {}).get(source.resolve(), set())
            if source is not None
            else set()
        )
        expected = _capture_claim(capture, actual)
        reusable_claims[id(capture)] = expected
        if expected is None:
            failures.append(
                f"reusable capture {capture_id} has no bindable case, Draft, "
                "or hard-step claim"
            )
            continue
        if actual != {expected}:
            rendered = ", ".join(str(item) for item in sorted(actual, key=str))
            failures.append(
                f"reusable capture {capture_id} source does not match claimed "
                f"{expected[0]} {expected[1]} {expected[2]}"
                + (f" (source classifies as {rendered})" if rendered else "")
            )
            continue
        visible_anchors = " ".join(
            str(value)
            for value in capture.get("visible_anchors", [])
            if isinstance(value, str)
        )
        if (
            draft_agent_identities
            and "draft" in visible_anchors.casefold()
            and any(
                identity.casefold() in visible_anchors.casefold()
                for identity in draft_agent_identities
            )
        ):
            draft_reusable.append(capture)
    _audit_reusable_image_content(
        root,
        package,
        reusable,
        reusable_claims,
        failures,
    )

    if not isinstance(visual, dict) or visual.get("schema") != course.VISUAL_SCHEMA:
        failures.append(
            f"visual checkpoint schema must be {course.VISUAL_SCHEMA}"
        )

    review = visual.get("release_review") if isinstance(visual, dict) else None
    if not isinstance(review, dict):
        failures.append("release_review must be a top-level object")
    else:
        if review.get("status") != "approved":
            failures.append("release_review.status must be approved")
        if review.get("reviewer") != f"workshop-builder:{slug}":
            failures.append(
                f"release_review.reviewer must be workshop-builder:{slug}"
            )
        for field in ("reviewed_at", "method", "notes"):
            value = review.get(field)
            if not isinstance(value, str) or not value.strip():
                failures.append(f"release_review.{field} must be nonempty")

    reason_text = " ".join(_strings(visual)).lower() if visual is not None else ""
    if GENERIC_REASON in reason_text or GENERIC_REASON_SINGULAR in reason_text:
        failures.append(
            "generic conservative rollout reason says captures were not "
            "independently revalidated"
        )

    case_failures = course.Failures()
    cases = course.read_json(
        root / "tests" / "demo_cases" / f"{slug}.json",
        f"tests/demo_cases/{slug}.json",
        case_failures,
    )
    failures.extend(case_failures.items)
    locked_case_ids = _case_ids(cases)
    reusable_case_ids = {
        item["case_id"]
        for item in reusable
        if isinstance(item.get("case_id"), str) and item["case_id"].strip()
    }
    machine_case_ids = _machine_case_ids(root, package)
    covered_case_ids = reusable_case_ids | machine_case_ids
    missing_cases = [
        case_id for case_id in locked_case_ids if case_id not in covered_case_ids
    ]
    if missing_cases:
        failures.append(
            "locked cases lack reusable captures: " + ", ".join(missing_cases)
        )

    draft_machine_proven = _machine_draft_proven(package)
    if not draft_reusable and not draft_machine_proven:
        failures.append(
            "Draft state lacks identity-bound visual or Dataverse proof"
        )
    if len(hard_reusable) < 5:
        failures.append(
            f"reusable manual-mode captures {len(hard_reusable)} < 5"
        )

    required_reusable = max(10, math.ceil(len(captures) * 0.35))
    if len(reusable) < required_reusable:
        failures.append(
            f"reusable captures {len(reusable)} < required {required_reusable}"
        )

    (
        learner_assets,
        reference_only,
        learner_images,
        learner_links,
    ) = _learner_screenshot_assets(root, package, failures)
    if reference_only:
        failures.append(
            f"learner HTML contains {reference_only} reference-only image(s)"
        )
    reusable_paths = _capture_paths(root, package, reusable)
    reshoot_paths = _capture_paths(
        root,
        package,
        [item for item in captures if item.get("status") == "reshoot_required"],
    )
    allowed_derived_assets: set[Path] = set()
    manual_sources = set(browserfilm_sources["hard"])
    manual_walkthrough = (
        package / "screenshots" / "manual" / "manual-build-walkthrough.gif"
    ).resolve()
    if (
        manual_sources
        and manual_sources.issubset(reusable_paths)
        and manual_walkthrough.is_file()
    ):
        allowed_derived_assets.add(manual_walkthrough)
    reachable_reshoots = sorted(
        {
            course.repo_name(root, path)
            for path in learner_assets
            if path in reshoot_paths and path not in allowed_derived_assets
        }
    )
    if reachable_reshoots:
        failures.append(
            "learner pages link or display reshoot-required screenshots: "
            + ", ".join(reachable_reshoots)
        )
    unapproved = sorted(
        {
            course.repo_name(root, path)
            for path in learner_assets
            if (
                path not in reusable_paths
                and path not in allowed_derived_assets
            )
        }
    )
    if unapproved:
        failures.append(
            "learner-linked or displayed screenshots are not approved reusable "
            "captures: "
            + ", ".join(unapproved)
        )

    metrics = {
        "base_passed": bool(base_result.get("passed")),
        "locked_cases": len(locked_case_ids),
        "locked_cases_covered": len(locked_case_ids) - len(missing_cases),
        "locked_cases_visually_covered": len(
            set(locked_case_ids) & reusable_case_ids
        ),
        "locked_cases_machine_covered": len(
            set(locked_case_ids) & machine_case_ids
        ),
        "captures": len(captures),
        "reusable": len(reusable),
        "required_reusable": required_reusable,
        "reusable_ratio": (
            round(len(reusable) / len(captures), 4) if captures else 0.0
        ),
        "hard_reusable": len(hard_reusable),
        "draft_reusable": len(draft_reusable),
        "draft_machine_proven": draft_machine_proven,
        "learner_images": learner_images,
        "learner_screenshot_links": learner_links,
        "learner_screenshot_assets": len(learner_assets),
        "reference_only_images": reference_only,
        "allowed_derived_assets": len(allowed_derived_assets),
    }
    return {
        "slug": slug,
        "passed": not failures,
        "failures": list(dict.fromkeys(failures)),
        "metrics": metrics,
    }


def audit_repository(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    scope_failures = course.Failures()
    slugs, exclusions = course.course_scope(root, scope_failures)
    global_failures = list(scope_failures.items)
    if len(slugs) != EXPECTED_WORKSHOPS:
        global_failures.append(
            f"advertised workshop count {len(slugs)} != {EXPECTED_WORKSHOPS}"
        )

    base_report = course.audit_repository(root)
    raw_base_solutions = base_report.get("solutions")
    base_solutions = raw_base_solutions if isinstance(raw_base_solutions, list) else []
    if (
        base_report.get("total") != EXPECTED_WORKSHOPS
        or not isinstance(raw_base_solutions, list)
        or len(base_solutions) != EXPECTED_WORKSHOPS
    ):
        global_failures.append(
            "base course audit did not resolve exactly 51 workshops"
        )
    base_by_slug = {
        item.get("slug"): item
        for item in base_solutions
        if isinstance(item, dict) and isinstance(item.get("slug"), str)
    }
    if set(base_by_slug) != set(slugs):
        global_failures.append(
            "base course audit did not resolve exactly the advertised slugs"
        )

    workshops = [
        audit_workshop(
            root,
            slug,
            base_by_slug.get(
                slug,
                {
                    "slug": slug,
                    "passed": False,
                    "failures": ["missing from base course audit"],
                },
            ),
        )
        for slug in slugs
    ]
    if global_failures:
        for workshop in workshops:
            workshop["passed"] = False
            workshop["failures"] = list(
                dict.fromkeys(
                    [f"global: {failure}" for failure in global_failures]
                    + workshop["failures"]
                )
            )

    totals = {
        "workshops": len(workshops),
        "passed": sum(item["passed"] for item in workshops),
        "failed": sum(not item["passed"] for item in workshops),
        "locked_cases": sum(
            item["metrics"]["locked_cases"] for item in workshops
        ),
        "locked_cases_covered": sum(
            item["metrics"]["locked_cases_covered"] for item in workshops
        ),
        "captures": sum(item["metrics"]["captures"] for item in workshops),
        "reusable": sum(item["metrics"]["reusable"] for item in workshops),
        "hard_reusable": sum(
            item["metrics"]["hard_reusable"] for item in workshops
        ),
        "learner_images": sum(
            item["metrics"]["learner_images"] for item in workshops
        ),
        "reference_only_images": sum(
            item["metrics"]["reference_only_images"] for item in workshops
        ),
    }
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "expected_workshops": EXPECTED_WORKSHOPS,
        "global_failures": global_failures,
        "excluded_non_advertised": exclusions,
        "totals": totals,
        "workshops": workshops,
    }


def print_human(report: dict[str, Any]) -> None:
    totals = report["totals"]
    print(
        "AIBAST workshop first release: "
        f"{totals['passed']}/{totals['workshops']} passed; "
        f"{totals['failed']} failed; "
        f"{totals['reusable']}/{totals['captures']} reusable"
    )
    for failure in report["global_failures"]:
        print(f"  - global: {failure}")
    for workshop in report["workshops"]:
        metrics = workshop["metrics"]
        state = "PASS" if workshop["passed"] else "FAIL"
        print(
            f"{state:4} {workshop['slug']} "
            f"cases={metrics['locked_cases_covered']}/{metrics['locked_cases']} "
            f"reusable={metrics['reusable']}/{metrics['captures']} "
            f"hard={metrics['hard_reusable']} draft={metrics['draft_reusable']}"
        )
        for failure in workshop["failures"]:
            print(f"  - {failure}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the machine-readable first-release report",
    )
    args = parser.parse_args(argv)
    report = audit_repository(ROOT)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human(report)
    totals = report["totals"]
    return 0 if (
        totals["workshops"] == EXPECTED_WORKSHOPS
        and totals["failed"] == 0
        and not report["global_failures"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
