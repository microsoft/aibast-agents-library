#!/usr/bin/env python3
"""Fail-closed acceptance gate for the AIBAST workshop-course rollout."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import struct
import subprocess
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import unquote, urlparse
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "aibast-workshop-course-rollout-audit/1.0"
VISUAL_SCHEMA = "aibast-visual-checkpoints/1.0"
BROWSERFILM_SCHEMA = "rapp-browserfilm/1.0"
RAW_SUFFIXES = {".md", ".json", ".py"}
HTML_FILES = (
    "quest.html",
    "manual-tutorial.html",
    "field-guide.html",
    "evidence-report.html",
)
VOID_TAGS = {
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


class Tag:
    def __init__(
        self,
        name: str,
        attrs: dict[str, str | None],
        parent: int | None,
    ) -> None:
        self.name = name
        self.attrs = attrs
        self.parent = parent
        self.children: list[int] = []
        self.text_parts: list[str] = []

    @property
    def text(self) -> str:
        return " ".join("".join(self.text_parts).split())

    @property
    def classes(self) -> set[str]:
        return set((self.attrs.get("class") or "").split())


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[Tag] = []
        self.stack: list[int] = []
        self.visible_parts: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        name = tag.lower()
        parent = self.stack[-1] if self.stack else None
        record = Tag(name, {key.lower(): value for key, value in attrs}, parent)
        index = len(self.tags)
        self.tags.append(record)
        if parent is not None:
            self.tags[parent].children.append(index)
        if name not in VOID_TAGS:
            self.stack.append(index)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if self.stack and self.tags[self.stack[-1]].name == tag.lower():
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        name = tag.lower()
        for position in range(len(self.stack) - 1, -1, -1):
            if self.tags[self.stack[position]].name == name:
                del self.stack[position:]
                return

    def handle_data(self, data: str) -> None:
        for index in self.stack:
            self.tags[index].text_parts.append(data)
        if not any(
            self.tags[index].name in {"script", "style"} for index in self.stack
        ):
            self.visible_parts.append(data)

    @property
    def visible_text(self) -> str:
        return " ".join("".join(self.visible_parts).split())

    def find(self, name: str | None = None, class_name: str | None = None) -> list[Tag]:
        return [
            tag
            for tag in self.tags
            if (name is None or tag.name == name)
            and (class_name is None or class_name in tag.classes)
        ]

    def descendants(self, tag: Tag) -> list[Tag]:
        start = self.tags.index(tag)
        pending = list(self.tags[start].children)
        result: list[Tag] = []
        while pending:
            index = pending.pop(0)
            result.append(self.tags[index])
            pending[0:0] = self.tags[index].children
        return result


class Failures:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, message: str) -> None:
        if message not in self.items:
            self.items.append(message)


class ScriptChecker:
    def __init__(self, node_path: str | None = None) -> None:
        self.node_path = node_path if node_path is not None else shutil.which("node")
        self.cache: dict[str, str | None] = {}
        self.checked = 0

    def check(self, script: str) -> str | None:
        if not self.node_path:
            return "node is unavailable; inline JavaScript cannot be measured"
        if script in self.cache:
            return self.cache[script]
        self.checked += 1
        try:
            result = subprocess.run(
                [self.node_path, "--check", "-"],
                input=script,
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            error = f"node --check could not run: {exc}"
        else:
            if result.returncode == 0:
                error = None
            else:
                detail = next(
                    (
                        line.strip()
                        for line in result.stderr.splitlines()
                        if line.strip()
                    ),
                    f"exit {result.returncode}",
                )
                error = f"malformed inline JavaScript ({detail})"
        self.cache[script] = error
        return error


def read_json(path: Path, label: str, failures: Failures) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        failures.add(f"{label}: missing")
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        failures.add(f"{label}: unreadable JSON ({exc})")
    return None


def parse_html(path: Path, label: str, failures: Failures) -> tuple[str, DocumentParser] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        failures.add(f"{label}: missing")
        return None
    except (OSError, UnicodeError) as exc:
        failures.add(f"{label}: unreadable ({exc})")
        return None
    parser = DocumentParser()
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:
        failures.add(f"{label}: HTML cannot be parsed ({exc})")
        return None
    return text, parser


def package_slug(agent: dict[str, Any]) -> str:
    demo = agent.get("_demo")
    if isinstance(demo, dict) and isinstance(demo.get("slug"), str):
        return demo["slug"]
    return str(agent.get("name", "")).rsplit("/", 1)[-1]


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def root_path(root: Path, raw_path: str) -> Path | None:
    parsed = urlparse(raw_path)
    if parsed.scheme or parsed.netloc:
        return None
    value = unquote(parsed.path).lstrip("/")
    pure = PurePosixPath(value)
    if not value or ".." in pure.parts:
        return None
    candidate = (root / Path(*pure.parts)).resolve()
    root_resolved = root.resolve()
    return candidate if _is_within(candidate, root_resolved) else None


def relative_path(root: Path, base: Path, raw_path: str) -> Path | None:
    parsed = urlparse(raw_path)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    value = unquote(parsed.path)
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        return None
    if pure.parts and pure.parts[0] in {"solutions", "skills", "agents", "tests"}:
        return root_path(root, value)
    candidate = (base / Path(*pure.parts)).resolve()
    return candidate if _is_within(candidate, root.resolve()) else None


def repo_name(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def image_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as stream:
            header = stream.read(32)
            if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
                width, height = struct.unpack(">II", header[16:24])
                return (width, height) if width > 0 and height > 0 else None
            if header[:6] in {b"GIF87a", b"GIF89a"} and len(header) >= 10:
                width, height = struct.unpack("<HH", header[6:10])
                return (width, height) if width > 0 and height > 0 else None
            if not header.startswith(b"\xff\xd8"):
                return None
            stream.seek(2)
            sof_markers = {
                0xC0,
                0xC1,
                0xC2,
                0xC3,
                0xC5,
                0xC6,
                0xC7,
                0xC9,
                0xCA,
                0xCB,
                0xCD,
                0xCE,
                0xCF,
            }
            while True:
                byte = stream.read(1)
                if not byte:
                    return None
                if byte != b"\xff":
                    continue
                while byte == b"\xff":
                    byte = stream.read(1)
                if not byte:
                    return None
                marker = byte[0]
                if marker in {0x01, *range(0xD0, 0xDA)}:
                    continue
                length_bytes = stream.read(2)
                if len(length_bytes) != 2:
                    return None
                length = struct.unpack(">H", length_bytes)[0]
                if length < 2:
                    return None
                if marker in sof_markers:
                    payload = stream.read(5)
                    if len(payload) != 5:
                        return None
                    height, width = struct.unpack(">HH", payload[1:5])
                    return (width, height) if width > 0 and height > 0 else None
                stream.seek(length - 2, 1)
    except OSError:
        return None


def raw_link_failures(label: str, parser: DocumentParser, failures: Failures) -> None:
    for anchor in parser.find("a"):
        href = anchor.attrs.get("href")
        if not href:
            continue
        suffix = Path(urlparse(href).path).suffix.lower()
        if suffix in RAW_SUFFIXES and "download" not in anchor.attrs:
            failures.add(
                f"{label}: raw {suffix} link lacks download attribute ({href})"
            )


def check_common_html(
    label: str,
    text: str,
    parser: DocumentParser,
    checker: ScriptChecker,
    failures: Failures,
    metrics: dict[str, Any],
) -> None:
    lowered = text.lower()
    if "aibast" not in parser.visible_text.lower():
        failures.add(f"{label}: missing visible AIBAST branding")
    if "clawpilot" in lowered:
        failures.add(f"{label}: contains stale Clawpilot branding")
    raw_link_failures(label, parser, failures)
    scripts = [
        tag.text
        for tag in parser.find("script")
        if not tag.attrs.get("src") and tag.text.strip()
    ]
    metrics.setdefault("inline_scripts", 0)
    metrics["inline_scripts"] += len(scripts)
    if not scripts:
        failures.add(f"{label}: no measurable inline script")
    for index, script in enumerate(scripts, start=1):
        error = checker.check(script)
        if error:
            failures.add(f"{label}: inline script {index}: {error}")


def has_href(parser: DocumentParser, needle: str) -> bool:
    return any(
        needle.lower() in (tag.attrs.get("href") or "").lower()
        for tag in parser.find("a")
    )


def has_per_page_lane_selector(parser: DocumentParser) -> bool:
    for tag in parser.tags:
        attrs = tag.attrs
        values = " ".join(
            str(value).lower() for value in attrs.values() if value is not None
        )
        if tag.name in {"button", "input", "select", "option"}:
            if any(
                key in attrs
                for key in (
                    "data-engine",
                    "data-engine-choice",
                    "data-workshop-engine",
                    "data-workshop-engine-choice",
                )
            ):
                return True
            if tag.name in {"input", "option"} and (
                attrs.get("value") or ""
            ).lower() in {"brainstem", "copilot"}:
                return True
            if "engine-switch" in values or "lane-selector" in values:
                return True
    return False


def check_quest(
    root: Path,
    package: Path,
    text: str,
    parser: DocumentParser,
    locked_cases: list[dict[str, Any]] | None,
    failures: Failures,
    metrics: dict[str, Any],
) -> None:
    label = "quest.html"
    lowered = text.lower()
    if "beta workshop" not in lowered:
        failures.add(f"{label}: missing Beta workshop label")
    if "aibast:workshop-engine" not in text:
        failures.add(f"{label}: missing global aibast:workshop-engine key")
    if not has_href(parser, "workshop-settings.html"):
        failures.add(f"{label}: missing workshop settings link")
    lane_values = {
        (tag.attrs.get("data-easy-lane") or "").lower()
        for tag in parser.tags
        if tag.attrs.get("data-easy-lane")
    }
    if not {"brainstem", "copilot"}.issubset(lane_values):
        failures.add(f"{label}: missing GitHub Copilot and Brainstem lane containers")
    visible = parser.visible_text.lower()
    if "github copilot" not in visible or "brainstem" not in visible:
        failures.add(f"{label}: missing visible GitHub Copilot or Brainstem lane")
    if has_per_page_lane_selector(parser):
        failures.add(f"{label}: contains a forbidden per-page lane selector")
    script_text = "\n".join(tag.text for tag in parser.find("script"))
    default_script = (
        re.search(
            r"localStorage\.getItem\(\s*['\"]aibast:workshop-engine['\"]\s*\)",
            script_text,
        )
        and re.search(r"===\s*['\"]brainstem['\"]", script_text)
        and re.search(r":\s*['\"]copilot['\"]", script_text)
        and "data-workshop-engine" in script_text
    )
    if not default_script:
        failures.add(f"{label}: Copilot-default global engine script is not measurable")
    iframe_sources = [
        tag.attrs.get("src") or ""
        for tag in parser.find("iframe")
    ]
    if "manual-tutorial.html?embedded=1" not in iframe_sources:
        failures.add(f"{label}: missing embedded manual-tutorial.html?embedded=1")
    if not has_href(parser, "field-guide.html"):
        failures.add(f"{label}: missing field-guide.html link")
    if not has_href(parser, "evidence-report.html"):
        failures.add(f"{label}: missing evidence-report.html link")
    for anchor in parser.find("a"):
        href = (anchor.attrs.get("href") or "").lower()
        if href.endswith("field-guide.md") or "visual-evidence-audit.md" in href:
            failures.add(f"{label}: contains forbidden raw guide/audit navigation ({href})")
    if "watch assisted film" in lowered:
        failures.add(f"{label}: contains forbidden Watch assisted film control")
    if "<!-- aibast-workshop-feedback:v1 -->" not in text:
        failures.add(f"{label}: missing contextual feedback marker")
    if "aibast-workshop-feedback/1.0" not in text:
        failures.add(f"{label}: missing contextual feedback schema")
    report_buttons = [
        tag for tag in parser.tags if "data-report-location" in tag.attrs
    ]
    preview_prompts = [
        tag
        for tag in parser.tags
        if (tag.attrs.get("id") or "").startswith("preview-prompt-")
    ]
    copy_targets = [
        tag.attrs.get("data-copy-target")
        for tag in parser.tags
        if (tag.attrs.get("data-copy-target") or "").startswith("preview-prompt-")
    ]
    metrics["quest_report_buttons"] = len(report_buttons)
    metrics["quest_preview_prompts"] = len(preview_prompts)
    if locked_cases is None:
        failures.add(f"{label}: report-button total cannot be measured without locked cases")
    else:
        expected_reports = 7 + len(locked_cases)
        if len(report_buttons) != expected_reports:
            failures.add(
                f"{label}: report buttons {len(report_buttons)} != "
                f"7 + {len(locked_cases)} locked cases ({expected_reports})"
            )
        if len(preview_prompts) != len(locked_cases):
            failures.add(
                f"{label}: Preview prompts {len(preview_prompts)} != "
                f"locked cases {len(locked_cases)}"
            )
    prompt_ids = {tag.attrs["id"] for tag in preview_prompts}
    missing_copy = sorted(prompt_ids - set(copy_targets))
    duplicate_copy = sorted(
        target for target in prompt_ids if copy_targets.count(target) != 1
    )
    if missing_copy:
        failures.add(
            f"{label}: Preview prompts lack copy actions ({', '.join(missing_copy)})"
        )
    if duplicate_copy:
        failures.add(
            f"{label}: Preview prompt copy actions are not one-to-one "
            f"({', '.join(duplicate_copy)})"
        )


def load_browserfilm(
    root: Path,
    path: Path,
    mode: str,
    failures: Failures,
) -> tuple[list[dict[str, Any]], set[tuple[str, str, str | int]], set[Path]]:
    label = repo_name(root, path)
    data = read_json(path, label, failures)
    if not isinstance(data, dict):
        return [], set(), set()
    if data.get("schema") != BROWSERFILM_SCHEMA:
        failures.add(f"{label}: schema is not {BROWSERFILM_SCHEMA}")
    frames = data.get("frames")
    if not isinstance(frames, list):
        failures.add(f"{label}: frames is not a list")
        return [], set(), set()
    expected_width = data.get("width")
    expected_height = data.get("height")
    expected_dimensions = (
        (expected_width, expected_height)
        if isinstance(expected_width, int)
        and not isinstance(expected_width, bool)
        and expected_width > 0
        and isinstance(expected_height, int)
        and not isinstance(expected_height, bool)
        and expected_height > 0
        else None
    )
    if expected_dimensions is None:
        failures.add(f"{label}: declared image dimensions are not measurable")
    references: set[tuple[str, str, str | int]] = set()
    sources: set[Path] = set()
    for index, frame in enumerate(frames, start=1):
        if not isinstance(frame, dict) or not isinstance(frame.get("file"), str):
            failures.add(f"{label}: frame {index} has no source file")
            continue
        source = relative_path(root, path.parent, frame["file"])
        if source is None:
            failures.add(f"{label}: frame {index} has unsafe source path")
            continue
        sources.add(source)
        dimensions = image_dimensions(source) if source.is_file() else None
        if not source.is_file():
            failures.add(f"{label}: frame {index} source is missing ({frame['file']})")
        elif dimensions is None:
            failures.add(
                f"{label}: frame {index} source dimensions cannot be measured "
                f"({frame['file']})"
            )
        label_text = str(frame.get("label", ""))
        case_match = re.search(
            r"(?<![A-Z0-9_])([A-Z][A-Z0-9_]*-\d+)(?![A-Z0-9_])",
            label_text,
        )
        if case_match:
            references.add((mode, "case", case_match.group(1)))
        elif mode == "hard":
            references.add((mode, "step", index))
        elif "draft" in label_text.lower():
            references.add((mode, "draft", "draft"))
        else:
            failures.add(f"{label}: frame {index} reference cannot be classified")
    return frames, references, sources


def check_manual(
    text: str,
    parser: DocumentParser,
    manual_frames: list[dict[str, Any]],
    failures: Failures,
    metrics: dict[str, Any],
) -> None:
    label = "manual-tutorial.html"
    lowered = text.lower()
    if "beta workshop" not in lowered:
        failures.add(f"{label}: missing Beta workshop label")
    required_protocol = (
        'get("embedded")',
        '=== "1"',
        "data-embedded",
        "aibast-hard-mode-height",
        "postMessage",
        "ResizeObserver",
    )
    for token in required_protocol:
        if token not in text:
            failures.add(f"{label}: embedded-height protocol lacks {token}")
    if "<!-- aibast-workshop-feedback:v1 -->" not in text:
        failures.add(f"{label}: missing contextual feedback marker")
    if "aibast-workshop-feedback/1.0" not in text:
        failures.add(f"{label}: missing contextual feedback schema")
    if "watch assisted film" in lowered:
        failures.add(f"{label}: contains forbidden assisted-film control")
    steps = parser.find("article", "step")
    metrics["manual_steps"] = len(steps)
    metrics["manual_frames"] = len(manual_frames)
    if len(steps) != len(manual_frames):
        failures.add(
            f"{label}: tutorial steps {len(steps)} != browserfilm frames "
            f"{len(manual_frames)}"
        )
    for index, step in enumerate(steps, start=1):
        descendants = parser.descendants(step)
        reports = [
            tag for tag in descendants if "data-report-location" in tag.attrs
        ]
        downloads = [
            tag
            for tag in descendants
            if tag.name == "a" and tag.text.startswith("Download source:")
        ]
        if len(reports) != 1:
            failures.add(
                f"{label}: step {index} has {len(reports)} report buttons; expected 1"
            )
        if len(downloads) != 1:
            failures.add(
                f"{label}: step {index} has {len(downloads)} explicit "
                "Download source: links; expected 1"
            )
    metrics["manual_report_buttons"] = len(
        [tag for tag in parser.tags if "data-report-location" in tag.attrs]
    )
    metrics["manual_source_downloads"] = len(
        [
            tag
            for tag in parser.find("a")
            if tag.text.startswith("Download source:")
        ]
    )


def check_field_guide(
    text: str,
    parser: DocumentParser,
    failures: Failures,
) -> None:
    label = "field-guide.html"
    if not parser.find("style") or not any(
        tag.text.strip() for tag in parser.find("style")
    ):
        failures.add(f"{label}: missing styled HTML")
    script_text = "\n".join(tag.text for tag in parser.find("script"))
    for token in ("data-theme", "aibast:workshop-engine", "data-workshop-engine"):
        if token not in script_text:
            failures.add(f"{label}: theme/global engine script lacks {token}")
    if "aibast field guide" not in parser.visible_text.lower():
        failures.add(f"{label}: missing AIBAST field-guide branding")
    if not has_href(parser, "workshop-settings.html"):
        failures.add(f"{label}: missing workshop settings link")
    if not has_href(parser, "quest.html"):
        failures.add(f"{label}: missing back-to-workshop link")
    for phrase in ("locked preview corpus", "production replacement seams", "evidence gates"):
        if phrase not in parser.visible_text.lower():
            failures.add(f"{label}: missing {phrase}")


def check_evidence_report(
    text: str,
    parser: DocumentParser,
    locked_cases: list[dict[str, Any]] | None,
    reusable: int | None,
    reshoot: int | None,
    failures: Failures,
) -> None:
    label = "evidence-report.html"
    visible = parser.visible_text.lower()
    if not parser.find("style") or not any(
        tag.text.strip() for tag in parser.find("style")
    ):
        failures.add(f"{label}: missing styled HTML")
    if "aibast evidence report" not in visible:
        failures.add(f"{label}: missing AIBAST evidence branding")
    for phrase in (
        "deterministic case contract",
        "displayed visual checkpoints",
        "hidden visual gaps",
        "downloads for audit",
    ):
        if phrase not in visible:
            failures.add(f"{label}: missing {phrase}")
    if locked_cases is None:
        failures.add(f"{label}: locked-case summary cannot be measured")
    else:
        for case in locked_cases:
            case_id = case.get("id")
            if not isinstance(case_id, str) or case_id.lower() not in visible:
                failures.add(f"{label}: locked-case summary lacks {case_id!r}")
    summary_text = " ".join(tag.text for tag in parser.find(class_name="summary-grid"))
    if reusable is None or reshoot is None:
        failures.add(f"{label}: visual summary cannot be reconciled")
    else:
        if str(reusable) not in summary_text:
            failures.add(
                f"{label}: visual summary lacks reusable count {reusable}"
            )
        if str(reshoot) not in summary_text:
            failures.add(
                f"{label}: visual summary lacks reshoot count {reshoot}"
            )
    audit_needles = (
        "evals/visual-checkpoints.json",
        "export-manifest.json",
        ".zip",
    )
    for needle in audit_needles:
        if not has_href(parser, needle):
            failures.add(f"{label}: audit downloads lack {needle}")


def capture_references(
    capture: dict[str, Any],
) -> set[tuple[str, str, str | int]]:
    mode = capture.get("mode")
    if mode not in {"easy", "hard"}:
        return set()
    references: set[tuple[str, str, str | int]] = set()
    step = capture.get("step")
    if (
        mode == "hard"
        and isinstance(step, int)
        and not isinstance(step, bool)
        and step > 0
    ):
        references.add((mode, "step", step))
    capture_id = str(capture.get("id", ""))
    if mode == "easy" and "draft" in capture_id.lower():
        references.add((mode, "draft", "draft"))
    case_id = capture.get("case_id")
    if isinstance(case_id, str) and case_id:
        references.add((mode, "case", case_id))
    if isinstance(step, int) and not isinstance(step, bool) and step > 0:
        references.add((mode, "step", step))
    return references


def numeric(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) else None


def displayed_screenshots(
    root: Path,
    package: Path,
    documents: Iterable[tuple[Path, DocumentParser]],
    failures: Failures,
) -> set[Path]:
    displayed: set[Path] = set()
    screenshot_root = (package / "screenshots").resolve()
    for page, parser in documents:
        for image in parser.find("img"):
            source_raw = image.attrs.get("src")
            if not source_raw:
                continue
            source = relative_path(root, page.parent, source_raw)
            if source is None or not _is_within(source, screenshot_root):
                continue
            displayed.add(source)
            if not source.is_file():
                failures.add(
                    f"{page.name}: learner-displayed screenshot is missing "
                    f"({source_raw})"
                )
    return displayed


def check_visual_contract(
    root: Path,
    package: Path,
    data: Any,
    browserfilm_references: set[tuple[str, str, str | int]],
    displayed: set[Path],
    failures: Failures,
    metrics: dict[str, Any],
) -> tuple[int | None, int | None]:
    label = "evals/visual-checkpoints.json"
    if not isinstance(data, dict):
        return None, None
    if data.get("schema") != VISUAL_SCHEMA:
        failures.add(f"{label}: schema is not {VISUAL_SCHEMA}")
    captures = data.get("captures")
    summary = data.get("summary")
    if not isinstance(captures, list):
        failures.add(f"{label}: captures is not a list")
        return None, None
    if not isinstance(summary, dict):
        failures.add(f"{label}: summary is not an object")
        summary = {}
    reusable_count = sum(
        isinstance(item, dict) and item.get("status") == "reusable"
        for item in captures
    )
    reshoot_count = sum(
        isinstance(item, dict) and item.get("status") == "reshoot_required"
        for item in captures
    )
    metrics["visual_captures"] = len(captures)
    metrics["visual_reusable"] = reusable_count
    metrics["visual_reshoot_required"] = reshoot_count
    expected_summary = {
        "total_existing_captures": len(captures),
        "reusable": reusable_count,
        "reshoot_required": reshoot_count,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            failures.add(
                f"{label}: summary {key}={summary.get(key)!r} != {expected}"
            )
    classified: dict[tuple[str, str, str | int], set[str]] = {}
    reusable_display_paths: set[Path] = set()
    reshoot_paths: set[Path] = set()
    seen_ids: set[str] = set()
    for index, capture in enumerate(captures, start=1):
        prefix = f"{label}: capture {index}"
        if not isinstance(capture, dict):
            failures.add(f"{prefix} is not an object")
            continue
        capture_id = capture.get("id")
        if not isinstance(capture_id, str) or not capture_id.strip():
            failures.add(f"{prefix} has no id")
            capture_id = f"#{index}"
        elif capture_id in seen_ids:
            failures.add(f"{label}: duplicate capture id {capture_id}")
        seen_ids.add(str(capture_id))
        prefix = f"{label}: {capture_id}"
        references = capture_references(capture)
        if not references:
            failures.add(f"{prefix} has no measurable frame/case/draft reference")
        status = capture.get("status")
        if status not in {"reusable", "reshoot_required"}:
            failures.add(f"{prefix} has invalid classification {status!r}")
        else:
            for reference in references:
                classified.setdefault(reference, set()).add(status)
        source_raw = capture.get("source")
        source = (
            relative_path(root, package, source_raw)
            if isinstance(source_raw, str)
            else None
        )
        if source is None:
            failures.add(f"{prefix} has no safe source image")
            source_dimensions = None
        elif not source.is_file():
            failures.add(f"{prefix} source image is missing ({source_raw})")
            source_dimensions = None
        else:
            source_dimensions = image_dimensions(source)
            if source_dimensions is None:
                failures.add(f"{prefix} source image dimensions cannot be measured")
        annotated_raw = capture.get("annotated")
        annotated = (
            relative_path(root, package, annotated_raw)
            if isinstance(annotated_raw, str)
            else None
        )
        if status == "reusable":
            if annotated is None or Path(str(annotated_raw)).suffix.lower() != ".png":
                failures.add(f"{prefix} reusable annotation is not a PNG path")
                annotated_dimensions = None
            elif not annotated.is_file():
                failures.add(f"{prefix} reusable annotation is missing ({annotated_raw})")
                annotated_dimensions = None
            else:
                annotated_dimensions = image_dimensions(annotated)
                if annotated_dimensions is None:
                    failures.add(
                        f"{prefix} reusable annotation dimensions cannot be measured"
                    )
            anchors = capture.get("visible_anchors")
            if not isinstance(anchors, list) or not anchors or not all(
                isinstance(anchor, str) and anchor.strip() for anchor in anchors
            ):
                failures.add(f"{prefix} reusable checkpoint lacks visible anchors")
            boxes = capture.get("boxes")
            if not isinstance(boxes, list) or not boxes:
                failures.add(f"{prefix} reusable annotation lacks boxes")
            elif source_dimensions is None:
                failures.add(f"{prefix} annotation boxes cannot be measured")
            else:
                width, height = source_dimensions
                valid_boxes = 0
                for box_index, box in enumerate(boxes, start=1):
                    if not isinstance(box, dict):
                        failures.add(f"{prefix} box {box_index} is not an object")
                        continue
                    x = numeric(box.get("x"))
                    y = numeric(box.get("y"))
                    box_width = numeric(box.get("width"))
                    box_height = numeric(box.get("height"))
                    if None in {x, y, box_width, box_height}:
                        failures.add(
                            f"{prefix} box {box_index} coordinates are not measurable"
                        )
                        continue
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
                        failures.add(
                            f"{prefix} box {box_index} is outside "
                            f"{width}x{height} source bounds"
                        )
                        continue
                    valid_boxes += 1
                if valid_boxes == 0:
                    failures.add(f"{prefix} has no valid in-bounds annotation box")
            if (
                source_dimensions is not None
                and annotated_dimensions is not None
                and source_dimensions != annotated_dimensions
            ):
                failures.add(
                    f"{prefix} annotated dimensions {annotated_dimensions} != "
                    f"source dimensions {source_dimensions}"
                )
            if source is not None:
                reusable_display_paths.add(source)
            if annotated is not None:
                reusable_display_paths.add(annotated)
        elif status == "reshoot_required":
            reason = capture.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                failures.add(f"{prefix} reshoot checkpoint lacks a reason")
            if source is not None:
                reshoot_paths.add(source)
            if annotated is not None:
                reshoot_paths.add(annotated)
    for reference in sorted(browserfilm_references, key=str):
        statuses = classified.get(reference)
        if not statuses:
            failures.add(
                f"{label}: missing visual classification for "
                f"{reference[0]} {reference[1]} {reference[2]}"
            )
        elif len(statuses) != 1:
            failures.add(
                f"{label}: conflicting visual classifications for "
                f"{reference[0]} {reference[1]} {reference[2]}"
            )
    for path in sorted(displayed):
        if path in reshoot_paths:
            failures.add(
                f"{label}: learner HTML displays reshoot-required image "
                f"({repo_name(root, path)})"
            )
        if path not in reusable_display_paths:
            failures.add(
                f"{label}: learner-displayed screenshot has no reusable checkpoint "
                f"({repo_name(root, path)})"
            )
    return reusable_count, reshoot_count


def check_manifest_and_zip(
    root: Path,
    slug: str,
    data: Any,
    failures: Failures,
    metrics: dict[str, Any],
) -> None:
    label = "export-manifest.json"
    if not isinstance(data, dict):
        return
    raw_base = data.get("raw_base")
    if not isinstance(raw_base, str) or not raw_base:
        failures.add(f"{label}: raw_base is missing")
        raw_base = ""
    files = data.get("files")
    if not isinstance(files, list):
        failures.add(f"{label}: files is not a list")
        files = []
    metrics["manifest_items"] = len(files)
    ready_files: dict[str, Path] = {}
    for index, item in enumerate(files, start=1):
        prefix = f"{label}: item {index}"
        if not isinstance(item, dict):
            failures.add(f"{prefix} is not an object")
            continue
        path_raw = item.get("path")
        path = root_path(root, path_raw) if isinstance(path_raw, str) else None
        if path is None:
            failures.add(f"{prefix} has no safe repository path")
        elif not path.is_file():
            failures.add(f"{prefix} path is missing ({path_raw})")
        raw_url = item.get("raw_url")
        if (
            not raw_base
            or not isinstance(raw_url, str)
            or not raw_url.startswith(raw_base)
        ):
            failures.add(f"{prefix} raw_url does not share manifest raw_base")
        if item.get("status") != "ready":
            failures.add(
                f"{prefix} has pending/non-ready status {item.get('status')!r}"
            )
        elif path is not None and path.is_file() and isinstance(path_raw, str):
            ready_files[PurePosixPath(path_raw).as_posix().lstrip("/")] = path
    bundle = data.get("bundle")
    if not isinstance(bundle, dict):
        failures.add(f"{label}: source ZIP bundle is missing")
        return
    bundle_path_raw = bundle.get("path")
    bundle_path = (
        root_path(root, bundle_path_raw)
        if isinstance(bundle_path_raw, str)
        else None
    )
    bundle_url = bundle.get("raw_url")
    if (
        not raw_base
        or not isinstance(bundle_url, str)
        or not bundle_url.startswith(raw_base)
    ):
        failures.add(f"{label}: source ZIP raw_url does not share manifest raw_base")
    if bundle_path is None:
        failures.add(f"{label}: source ZIP has no safe repository path")
        return
    if not bundle_path.is_file():
        failures.add(f"{label}: source ZIP is missing ({bundle_path_raw})")
        return
    required_zip_entries = {
        f"solutions/{slug}/quest.html",
        f"solutions/{slug}/manual-tutorial.html",
        f"solutions/{slug}/field-guide.html",
        f"solutions/{slug}/evidence-report.html",
        f"solutions/{slug}/evals/visual-checkpoints.json",
        f"solutions/{slug}/export-manifest.json",
        "skills/aibast-easy-mode-brainstem/SKILL.md",
        "skills/aibast-easy-mode-copilot/SKILL.md",
    }
    try:
        with ZipFile(bundle_path) as archive:
            entry_names = {
                PurePosixPath(name).as_posix().lstrip("/"): name
                for name in archive.namelist()
                if not name.endswith("/")
            }
            entries = set(entry_names)
            for entry, path in sorted(ready_files.items()):
                if entry not in entries:
                    failures.add(
                        f"{label}: source ZIP missing ready manifest file {entry}"
                    )
                    continue
                if archive.read(entry_names[entry]) != path.read_bytes():
                    failures.add(
                        f"{label}: source ZIP has stale bytes for ready manifest "
                        f"file {entry}"
                    )
    except (OSError, BadZipFile) as exc:
        failures.add(f"{label}: source ZIP cannot be inspected ({exc})")
        return
    metrics["zip_entries"] = len(entries)
    for missing in sorted(required_zip_entries - entries):
        failures.add(f"{label}: source ZIP missing required file {missing}")


def audit_solution(
    root: Path,
    slug: str,
    checker: ScriptChecker | None = None,
    global_failures: Iterable[str] = (),
) -> dict[str, Any]:
    root = root.resolve()
    package = root / "solutions" / slug
    failures = Failures()
    metrics: dict[str, Any] = {}
    checker = checker or ScriptChecker()
    for failure in global_failures:
        failures.add(f"global: {failure}")

    locked_data = read_json(
        root / "tests" / "demo_cases" / f"{slug}.json",
        f"tests/demo_cases/{slug}.json",
        failures,
    )
    locked_cases: list[dict[str, Any]] | None = None
    if isinstance(locked_data, dict) and isinstance(locked_data.get("cases"), list):
        if all(isinstance(case, dict) for case in locked_data["cases"]):
            locked_cases = locked_data["cases"]
        else:
            failures.add(f"tests/demo_cases/{slug}.json: cases contain non-objects")
    elif locked_data is not None:
        failures.add(f"tests/demo_cases/{slug}.json: cases is not a list")
    metrics["locked_cases"] = len(locked_cases) if locked_cases is not None else None

    documents: dict[str, tuple[str, DocumentParser]] = {}
    for name in HTML_FILES:
        parsed = parse_html(package / name, name, failures)
        if parsed:
            documents[name] = parsed
            check_common_html(name, parsed[0], parsed[1], checker, failures, metrics)

    assisted_frames, assisted_refs, _ = load_browserfilm(
        root,
        package / "screenshots" / "assisted" / "browserfilm.json",
        "easy",
        failures,
    )
    manual_frames, manual_refs, _ = load_browserfilm(
        root,
        package / "screenshots" / "manual" / "browserfilm.json",
        "hard",
        failures,
    )
    metrics["assisted_frames"] = len(assisted_frames)

    if "quest.html" in documents:
        check_quest(
            root,
            package,
            *documents["quest.html"],
            locked_cases,
            failures,
            metrics,
        )
    if "manual-tutorial.html" in documents:
        check_manual(
            *documents["manual-tutorial.html"],
            manual_frames,
            failures,
            metrics,
        )
    if "field-guide.html" in documents:
        check_field_guide(*documents["field-guide.html"], failures)

    visual_data = read_json(
        package / "evals" / "visual-checkpoints.json",
        "evals/visual-checkpoints.json",
        failures,
    )
    learner_documents = [
        (package / name, documents[name][1])
        for name in ("quest.html", "manual-tutorial.html")
        if name in documents
    ]
    displayed = displayed_screenshots(
        root, package, learner_documents, failures
    )
    reusable, reshoot = check_visual_contract(
        root,
        package,
        visual_data,
        assisted_refs | manual_refs,
        displayed,
        failures,
        metrics,
    )
    hard_reshoot_required = (
        isinstance(visual_data, dict)
        and any(
            isinstance(item, dict)
            and item.get("mode") == "hard"
            and item.get("status") == "reshoot_required"
            for item in visual_data.get("captures", [])
        )
    )
    if hard_reshoot_required and "manual-tutorial.html" in documents:
        manual_parser = documents["manual-tutorial.html"][1]
        if any(
            "manual-build-walkthrough.gif"
            in (anchor.attrs.get("href") or "")
            for anchor in manual_parser.find("a")
        ):
            failures.add(
                "manual-tutorial.html: exposes the manual film while one or "
                "more Hard captures require reshoot"
            )
    if "evidence-report.html" in documents:
        check_evidence_report(
            *documents["evidence-report.html"],
            locked_cases,
            reusable,
            reshoot,
            failures,
        )

    manifest_data = read_json(
        package / "export-manifest.json",
        "export-manifest.json",
        failures,
    )
    check_manifest_and_zip(root, slug, manifest_data, failures, metrics)
    return {
        "slug": slug,
        "passed": not failures.items,
        "failures": failures.items,
        "metrics": metrics,
    }


def audit_global(root: Path, checker: ScriptChecker) -> list[str]:
    failures: list[str] = []
    skill = root / "skills" / "aibast-easy-mode-copilot" / "SKILL.md"
    try:
        text = skill.read_text(encoding="utf-8")
    except FileNotFoundError:
        failures.append("GitHub Copilot lane skill is missing")
    except (OSError, UnicodeError) as exc:
        failures.append(f"GitHub Copilot lane skill is unreadable ({exc})")
    else:
        if "brainstem" in text.lower():
            failures.append(
                "GitHub Copilot lane skill contains forbidden case-insensitive brainstem"
            )
    if not checker.node_path:
        failures.append("node is unavailable; inline JavaScript cannot be checked")
    return failures


def course_scope(
    root: Path,
    failures: Failures,
) -> tuple[list[str], list[dict[str, str]]]:
    catalog = read_json(root / "solutions" / "catalog.json", "solutions/catalog.json", failures)
    registry = read_json(root / "registry.json", "registry.json", failures)
    catalog_solutions = catalog.get("solutions") if isinstance(catalog, dict) else None
    registry_agents = registry.get("agents") if isinstance(registry, dict) else None
    if not isinstance(catalog_solutions, dict):
        if catalog is not None:
            failures.add("solutions/catalog.json: solutions is not an object")
        catalog_solutions = {}
    if not isinstance(registry_agents, list):
        if registry is not None:
            failures.add("registry.json: agents is not a list")
        registry_agents = []

    advertised_names = {
        name for name in catalog_solutions if isinstance(name, str) and name
    }
    if len(advertised_names) != len(catalog_solutions):
        failures.add("solutions/catalog.json: contains an invalid advertised solution name")
    registry_by_name: dict[str, dict[str, Any]] = {}
    for index, agent in enumerate(registry_agents, start=1):
        if not isinstance(agent, dict) or not agent.get("_solution"):
            continue
        name = agent.get("name")
        if not isinstance(name, str) or not name:
            failures.add(f"registry.json: solution agent {index} has no name")
            continue
        if name in registry_by_name:
            failures.add(f"registry.json: duplicate solution name {name}")
            continue
        registry_by_name[name] = agent

    slugs: list[str] = []
    for name in sorted(advertised_names):
        agent = registry_by_name.get(name)
        if agent is None:
            failures.add(f"solutions/catalog.json: advertised solution missing from registry ({name})")
            slug = name.rsplit("/", 1)[-1]
        else:
            slug = package_slug(agent)
        if not slug:
            failures.add(f"solutions/catalog.json: advertised solution has no package slug ({name})")
            continue
        slugs.append(slug)

    exclusions: list[dict[str, str]] = []
    for name in sorted(set(registry_by_name) - advertised_names):
        agent = registry_by_name[name]
        slug = package_slug(agent)
        case_path = root / "tests" / "demo_cases" / f"{slug}.json"
        try:
            case_data = json.loads(case_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            status_text = ""
            failures.add(
                f"registry-only solution {slug} cannot prove non-advertised status ({exc})"
            )
        else:
            status = case_data.get("status") if isinstance(case_data, dict) else None
            status_text = status if isinstance(status, str) else ""
        if "not sharepoint-advertised" in status_text.lower() and re.search(
            r"must\b.*\bship", status_text, re.IGNORECASE
        ):
            exclusions.append(
                {
                    "slug": slug,
                    "status": "excluded_non_advertised",
                    "reason": status_text,
                }
            )
        else:
            failures.add(
                f"registry-only solution lacks excluded_non_advertised proof ({slug})"
            )

    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        failures.add(
            f"solutions/catalog.json: duplicate mapped package slugs "
            f"({', '.join(duplicates)})"
        )
    return sorted(set(slugs)), exclusions


def audit_repository(
    root: Path = ROOT,
    only_slug: str | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    checker = ScriptChecker()
    scope_failures = Failures()
    slugs, exclusions = course_scope(root, scope_failures)
    if "time-entry-billing" not in slugs:
        scope_failures.add("solutions/catalog.json: missing required reference time-entry-billing")
    if only_slug is not None:
        if only_slug not in slugs:
            scope_failures.add(
                f"requested solution is not advertised ({only_slug})"
            )
            slugs = [only_slug]
        else:
            slugs = [only_slug]
    global_failures = scope_failures.items + audit_global(root, checker)
    solutions = [
        audit_solution(root, slug, checker, global_failures) for slug in slugs
    ]
    passed = sum(solution["passed"] for solution in solutions)
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "total": len(solutions),
        "passed": passed,
        "failed": len(solutions) - passed,
        "reference_slug": "time-entry-billing",
        "builder_total": sum(slug != "time-entry-billing" for slug in slugs),
        "critic_total": len(slugs),
        "excluded_non_advertised": exclusions,
        "solutions": solutions,
    }


def print_human(report: dict[str, Any]) -> None:
    print(
        "AIBAST workshop-course rollout: "
        f"{report['passed']}/{report['total']} passed; "
        f"{report['failed']} failed"
    )
    print(
        f"Builders: {report['builder_total']} non-reference; "
        f"critics: {report['critic_total']} including "
        f"{report['reference_slug']}"
    )
    for excluded in report["excluded_non_advertised"]:
        print(
            "EXCLUDED_NON_ADVERTISED "
            f"{excluded['slug']}: {excluded['reason']}"
        )
    for solution in report["solutions"]:
        state = "PASS" if solution["passed"] else "FAIL"
        print(f"{state:4} {solution['slug']}")
        for failure in solution["failures"]:
            print(f"  - {failure}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the machine-readable acceptance report",
    )
    parser.add_argument(
        "--slug",
        help="audit one advertised solution instead of the full rollout",
    )
    args = parser.parse_args(argv)
    report = audit_repository(ROOT, only_slug=args.slug)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=False))
    else:
        print_human(report)
    expected_total = 1 if args.slug else 51
    return 0 if report["total"] == expected_total and report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
