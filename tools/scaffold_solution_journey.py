#!/usr/bin/env python3
"""Scaffold evidence-grounded customer journey surfaces for a solution package."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RAW_BASE = (
    "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/"
)
README_START = "<!-- scaffold-solution-journey:start -->"
README_END = "<!-- scaffold-solution-journey:end -->"

THEME_SCRIPT = """(() => {
      const param = new URLSearchParams(window.location.search).get("scoutTheme");
      const theme =
        param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      document.documentElement.setAttribute("data-theme", theme);
    })();"""

THEME_VARIABLES = """--cp-bg: #f7f4ef;
      --cp-bg-elevated: #fcfbf8;
      --cp-surface: #ffffff;
      --cp-surface-soft: #f5f5f5;
      --cp-border: #dedede;
      --cp-border-strong: #919191;
      --cp-text: #242424;
      --cp-text-muted: #5c5c5c;
      --cp-text-soft: #6f6f6f;
      --cp-accent: #b11f4b;
      --cp-accent-hover: #9a1a41;
      --cp-accent-soft: rgba(177, 31, 75, 0.08);
      --cp-accent-fg: #ffffff;
      --cp-success: #16a34a;
      --cp-danger: #dc2626;
      --cp-warning: #f59e0b;
      --cp-link: #0078d4;
      --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.12);
      --cp-overlay: rgba(255, 255, 255, 0.8);
      --cp-panel: rgba(255, 255, 255, 0.86);
      --cp-panel-strong: rgba(255, 255, 255, 0.96);
      --cp-sheen: rgba(255, 255, 255, 0.55);
      --cp-highlight: rgba(177, 31, 75, 0.12);"""

DARK_THEME_VARIABLES = """--cp-bg: #3d3b3a;
      --cp-bg-elevated: #343231;
      --cp-surface: #292929;
      --cp-surface-soft: #2e2e2e;
      --cp-border: #474747;
      --cp-border-strong: #5f5f5f;
      --cp-text: #dedede;
      --cp-text-muted: #919191;
      --cp-text-soft: #b0b0b0;
      --cp-accent: #fd8ea1;
      --cp-accent-hover: #fb7b91;
      --cp-accent-soft: rgba(253, 142, 161, 0.14);
      --cp-accent-fg: #1a1a1a;
      --cp-success: #4ade80;
      --cp-danger: #f87171;
      --cp-warning: #fbbf24;
      --cp-link: #4da6ff;
      --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
      --cp-overlay: rgba(41, 41, 41, 0.88);
      --cp-panel: rgba(41, 41, 41, 0.72);
      --cp-panel-strong: rgba(41, 41, 41, 0.96);
      --cp-sheen: rgba(255, 255, 255, 0.04);
      --cp-highlight: rgba(253, 142, 161, 0.12);"""

COMMON_CSS = f"""
    :root {{
      color-scheme: light;
      {THEME_VARIABLES}
    }}
    html[data-theme="dark"] {{
      color-scheme: dark;
      {DARK_THEME_VARIABLES}
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background: var(--cp-bg);
      color: var(--cp-text);
      font-family: "Segoe UI", Aptos, Calibri, -apple-system, BlinkMacSystemFont, sans-serif;
      line-height: 1.55;
    }}
    a {{ color: var(--cp-link); }}
    button, .button {{ font: inherit; }}
    .topbar {{
      position: sticky;
      top: 0;
      z-index: 20;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 12px 24px;
      border-bottom: 1px solid var(--cp-border);
      background: var(--cp-panel-strong);
    }}
    .brand {{ display: flex; align-items: center; gap: 10px; font-weight: 750; }}
    .brand-mark {{
      display: grid;
      width: 32px;
      height: 32px;
      place-items: center;
      border-radius: 10px;
      background: var(--cp-accent);
      color: var(--cp-accent-fg);
    }}
    .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 38px;
      padding: 8px 14px;
      border: 1px solid var(--cp-border-strong);
      border-radius: 10px;
      background: var(--cp-surface);
      color: var(--cp-text);
      text-decoration: none;
      cursor: pointer;
    }}
    .button.primary {{
      border-color: var(--cp-accent);
      background: var(--cp-accent);
      color: var(--cp-accent-fg);
    }}
    .page {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 40px 0 80px; }}
    .hero {{
      padding: 32px;
      border: 1px solid var(--cp-border);
      border-radius: 18px;
      background: var(--cp-surface);
      box-shadow: var(--cp-shadow);
    }}
    .eyebrow {{
      margin: 0 0 8px;
      color: var(--cp-accent);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .09em;
      text-transform: uppercase;
    }}
    h1 {{ margin: 0; font-size: clamp(34px, 7vw, 64px); line-height: 1; letter-spacing: -.045em; }}
    h2 {{ margin-top: 42px; }}
    .lede {{ max-width: 760px; color: var(--cp-text-muted); font-size: 18px; }}
    .notice {{
      margin-top: 18px;
      padding: 15px;
      border-left: 4px solid var(--cp-warning);
      background: var(--cp-surface-soft);
    }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    .card {{
      border: 1px solid var(--cp-border);
      border-radius: 14px;
      background: var(--cp-surface);
      padding: 20px;
    }}
    .card h3 {{ margin-top: 0; }}
    .muted {{ color: var(--cp-text-muted); }}
    .status {{ color: var(--cp-accent); font-weight: 750; }}
    .progress {{ height: 8px; overflow: hidden; border-radius: 999px; background: var(--cp-border); }}
    .progress span {{ display: block; width: 0; height: 100%; background: var(--cp-accent); }}
    @media (max-width: 760px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .topbar {{ align-items: flex-start; padding: 12px 16px; }}
      .page {{ width: min(100% - 24px, 1120px); padding-top: 24px; }}
      .hero {{ padding: 24px 20px; }}
    }}
"""


class ScaffoldError(RuntimeError):
    """Raised when evidence is insufficient to scaffold without fabrication."""


@dataclass
class Resource:
    id: str
    label: str
    path: str
    use: str
    status: str = "ready"


@dataclass
class JourneyContext:
    root: Path
    slug: str
    package: Path
    title: str
    deployment: dict[str, Any]
    transcripts: dict[str, Any]
    manual_evidence: dict[str, Any] | None
    manual_evidence_path: Path
    manual_browserfilm: dict[str, Any] | None
    manual_browserfilm_path: Path
    assisted_browserfilm: dict[str, Any] | None
    assisted_browserfilm_path: Path
    manual_frames: list[dict[str, Any]]
    missing_evidence: list[str]
    raw_base: str
    allow_pending: bool

    def rel(self, path: Path) -> str:
        return path.resolve().relative_to(self.root).as_posix()

    def raw(self, path: str) -> str:
        return f"{self.raw_base}{path}"


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScaffoldError(f"Cannot read JSON evidence {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ScaffoldError(f"Expected a JSON object in {path}")
    return value


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def clean_frame_label(label: str, fallback: str) -> str:
    label = re.sub(r"^\s*\d+\s*[·.:\-]\s*", "", str(label)).strip()
    return label or fallback


def resolve_repo_path(root: Path, package: Path, value: str | None, fallback: Path) -> Path:
    if not value:
        return fallback
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    if candidate.parts and candidate.parts[0] == "solutions":
        return root / candidate
    return package / candidate


def canonical_cases(evidence: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not evidence:
        return []
    cases = evidence.get("canonical_preview")
    if isinstance(cases, dict):
        return [cases]
    if isinstance(cases, list):
        return [case for case in cases if isinstance(case, dict)]
    return []


def manual_evidence_passed(evidence: dict[str, Any] | None) -> bool:
    if not evidence:
        return False
    if str(evidence.get("status", "")).lower() in {"failed", "error", "pending"}:
        return False
    cases = canonical_cases(evidence)
    if not cases or not all(case.get("passed") is True for case in cases):
        return False
    components = evidence.get("manual_components", {})
    if isinstance(components, dict):
        for value in components.values():
            if isinstance(value, dict) and value.get("expected") is not None:
                if value.get("confirmed") != value.get("expected"):
                    return False
    publication = evidence.get("publication_gate") or evidence.get("publication") or {}
    if isinstance(publication, dict) and publication.get("published") is True:
        return False
    return True


def source_agent_path(root: Path, deployment: dict[str, Any], transcripts: dict[str, Any]) -> Path | None:
    explicit = deployment.get("source_path")
    if isinstance(explicit, str):
        return root / explicit
    source_url = deployment.get("source_url")
    if isinstance(source_url, str) and "/main/" in source_url:
        return root / source_url.split("/main/", 1)[1]
    sources = transcripts.get("agent_sources", [])
    if isinstance(sources, list) and sources and isinstance(sources[0], dict):
        path = sources[0].get("path")
        if isinstance(path, str):
            return root / path
    return None


def require_foundation(root: Path, package: Path, deployment: dict[str, Any], transcripts: dict[str, Any]) -> list[str]:
    required = [
        package / "README.md",
        package / "deployment.json",
        package / "evals" / "transcripts.json",
        package / "manual" / "GLOBAL-INSTRUCTIONS.md",
        package / "manual" / "knowledge",
        package / "manual" / "skills",
        package / "copilot-studio",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    if (package / "manual" / "knowledge").exists() and not any(
        path.is_file() for path in (package / "manual" / "knowledge").rglob("*")
    ):
        missing.append(f"solutions/{package.name}/manual/knowledge/<file>")
    if (package / "manual" / "skills").exists() and not list(
        (package / "manual" / "skills").rglob("SKILL.md")
    ):
        missing.append(f"solutions/{package.name}/manual/skills/**/SKILL.md")
    source = source_agent_path(root, deployment, transcripts)
    if source is None or not source.exists():
        missing.append("portable source agent referenced by deployment/transcripts")
    return missing


def collect_referenced_screenshots(
    ctx: JourneyContext,
) -> list[tuple[Path, str]]:
    referenced: list[tuple[Path, str]] = []
    for frame in ctx.manual_frames:
        filename = frame.get("file")
        if isinstance(filename, str) and filename:
            referenced.append(
                (
                    ctx.manual_browserfilm_path.parent / filename,
                    f"manual browserfilm frame {filename}",
                )
            )
    for case in canonical_cases(ctx.manual_evidence):
        filename = case.get("expected_screenshot")
        if isinstance(filename, str) and filename:
            referenced.append(
                (
                    ctx.package / "screenshots" / "manual" / filename,
                    f"manual evidence screenshot {filename}",
                )
            )
    publication = (
        (ctx.manual_evidence or {}).get("publication_gate")
        or (ctx.manual_evidence or {}).get("publication")
        or {}
    )
    if isinstance(publication, dict):
        filename = publication.get("confirmation_screenshot")
        if isinstance(filename, str) and filename:
            referenced.append(
                (
                    ctx.package / "screenshots" / "manual" / filename,
                    f"Draft-gate screenshot {filename}",
                )
            )
    referenced.extend(
        [
            (
                referenced_media_path(
                    ctx,
                    "gif",
                    ctx.package
                    / "screenshots"
                    / "manual"
                    / "manual-build-walkthrough.gif",
                ),
                "manual browserfilm GIF",
            ),
            (
                referenced_media_path(
                    ctx,
                    "contact_sheet",
                    ctx.package
                    / "screenshots"
                    / "manual"
                    / "manual-build-contact-sheet.jpg",
                ),
                "manual browserfilm contact sheet",
            ),
        ]
    )
    if ctx.assisted_browserfilm:
        for frame in ctx.assisted_browserfilm.get("frames", []):
            if isinstance(frame, dict) and isinstance(frame.get("file"), str):
                referenced.append(
                    (
                        ctx.assisted_browserfilm_path.parent / frame["file"],
                        f"assisted browserfilm frame {frame['file']}",
                    )
                )
        referenced.extend(
            [
                (
                    ctx.package
                    / "screenshots"
                    / "assisted"
                    / "copilot-assisted-walkthrough.gif",
                    "assisted browserfilm GIF",
                ),
                (
                    ctx.package
                    / "screenshots"
                    / "assisted"
                    / "copilot-assisted-contact-sheet.jpg",
                    "assisted browserfilm contact sheet",
                ),
            ]
        )
    return referenced


def load_context(
    root: Path,
    slug: str,
    *,
    allow_pending: bool,
    raw_base: str,
) -> JourneyContext:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ScaffoldError("Solution slug must contain lowercase letters, numbers, and hyphens only")
    root = root.resolve()
    package = root / "solutions" / slug
    if not package.is_dir():
        raise ScaffoldError(f"Solution package does not exist: {package}")

    deployment_path = package / "deployment.json"
    transcripts_path = package / "evals" / "transcripts.json"
    if not deployment_path.exists() or not transcripts_path.exists():
        raise ScaffoldError("The standard deployment.json and evals/transcripts.json foundation is required")
    deployment = read_json(deployment_path)
    transcripts = read_json(transcripts_path)
    missing = require_foundation(root, package, deployment, transcripts)
    if missing:
        raise ScaffoldError("Standard solution foundation is incomplete:\n- " + "\n- ".join(missing))

    manual_evidence_path = package / "evals" / "manual-build-evidence.json"
    manual_evidence = read_json(manual_evidence_path) if manual_evidence_path.exists() else None
    evidence_browserfilm = (
        manual_evidence.get("browserfilm", {}).get("manifest")
        if manual_evidence and isinstance(manual_evidence.get("browserfilm"), dict)
        else None
    )
    manual_browserfilm_path = resolve_repo_path(
        root,
        package,
        evidence_browserfilm if isinstance(evidence_browserfilm, str) else None,
        package / "screenshots" / "manual" / "browserfilm.json",
    )
    manual_browserfilm = (
        read_json(manual_browserfilm_path) if manual_browserfilm_path.exists() else None
    )
    manual_frames = (
        [
            frame
            for frame in manual_browserfilm.get("frames", [])
            if isinstance(frame, dict)
        ]
        if manual_browserfilm
        else []
    )

    assisted_browserfilm_path = package / "screenshots" / "assisted" / "browserfilm.json"
    assisted_browserfilm = (
        read_json(assisted_browserfilm_path) if assisted_browserfilm_path.exists() else None
    )

    ctx = JourneyContext(
        root=root,
        slug=slug,
        package=package,
        title=str(deployment.get("display_name") or title_from_slug(slug)),
        deployment=deployment,
        transcripts=transcripts,
        manual_evidence=manual_evidence,
        manual_evidence_path=manual_evidence_path,
        manual_browserfilm=manual_browserfilm,
        manual_browserfilm_path=manual_browserfilm_path,
        assisted_browserfilm=assisted_browserfilm,
        assisted_browserfilm_path=assisted_browserfilm_path,
        manual_frames=manual_frames,
        missing_evidence=[],
        raw_base=raw_base.rstrip("/") + "/",
        allow_pending=allow_pending,
    )

    if not manual_evidence:
        ctx.missing_evidence.append(ctx.rel(manual_evidence_path))
    elif not manual_evidence_passed(manual_evidence):
        ctx.missing_evidence.append(
            f"{ctx.rel(manual_evidence_path)} does not record passed manual Preview evidence"
        )
    if not manual_browserfilm:
        ctx.missing_evidence.append(ctx.rel(manual_browserfilm_path))
    elif not manual_frames:
        ctx.missing_evidence.append(f"{ctx.rel(manual_browserfilm_path)} has no frames")

    for path, description in collect_referenced_screenshots(ctx):
        if not path.exists():
            ctx.missing_evidence.append(f"{description}: {ctx.rel(path)}")

    if ctx.missing_evidence and not allow_pending:
        raise ScaffoldError(
            "Manual evidence is incomplete; refusing to fabricate journey proof. "
            "Capture/fix the evidence or rerun with --allow-pending:\n- "
            + "\n- ".join(ctx.missing_evidence)
        )
    return ctx


def component_count(evidence: dict[str, Any] | None, key: str) -> str:
    value = (evidence or {}).get("manual_components", {}).get(key)
    if isinstance(value, dict):
        value = value.get("confirmed", value.get("expected"))
    return str(value) if value is not None else "recorded inventory"


def model_name(ctx: JourneyContext) -> str:
    if ctx.manual_evidence:
        for key in ("target_model", "model"):
            value = ctx.manual_evidence.get(key)
            if isinstance(value, str) and value:
                return value
    pilot = ctx.deployment.get("copilot_studio", {}).get("validated_pilot", {})
    value = pilot.get("model") if isinstance(pilot, dict) else None
    return str(value or "the reviewed Easy-mode model")


def manual_display_name(ctx: JourneyContext) -> str:
    evidence = ctx.manual_evidence or {}
    manual_agent = evidence.get("manual_agent", {})
    if isinstance(manual_agent, dict):
        value = manual_agent.get("display_name") or manual_agent.get("expected_display_name")
        if value:
            return str(value)
    return str(evidence.get("display_name") or f"{ctx.title} Manual Build")


def case_for_frame(ctx: JourneyContext, filename: str) -> dict[str, Any] | None:
    for case in canonical_cases(ctx.manual_evidence):
        if case.get("expected_screenshot") == filename:
            return case
    return None


def expected_result(ctx: JourneyContext, action: str, filename: str) -> str:
    lower = action.lower()
    case = case_for_frame(ctx, filename)
    if case:
        case_id = case.get("case_id", "recorded Preview case")
        identifiers = ", ".join(str(value) for value in case.get("must_include", []))
        suffix = f" with the recorded identifiers {identifiers}" if identifiers else ""
        return f"The captured Preview evidence records {case_id}{suffix}; do not infer results beyond it."
    if "create" in lower and "agent" in lower:
        return "A blank Copilot Studio agent is visible in the captured Draft workspace."
    if "name" in lower:
        return f"The page header shows the recorded manual build name: {manual_display_name(ctx)}."
    if "instruction" in lower:
        return "The reviewed manual/GLOBAL-INSTRUCTIONS.md policy is visible or saved without unrecorded edits."
    if "web search" in lower:
        return "The captured inventory no longer lists the default web-search capability."
    if "knowledge" in lower or "record" in lower or "rules" in lower:
        return f"The captured Knowledge inventory reflects the reviewed files; the evidence records {component_count(ctx.manual_evidence, 'knowledge_files')} knowledge sources."
    if "skill" in lower:
        return f"The captured skill inventory reflects the reviewed uploads; the evidence records {component_count(ctx.manual_evidence, 'skills')} skills."
    if "model" in lower or "sonnet" in lower:
        return f"The model picker or inventory shows {model_name(ctx)}, matching the recorded evidence."
    if "preview" in lower:
        return "A fresh Preview surface or its recorded qualitative result is visible; only the evidence file defines a pass."
    if "draft" in lower or "publish" in lower:
        return "The agent remains Draft and no Publish action is taken."
    if "inventory" in lower or "review" in lower or "audit" in lower:
        return "The captured inventory can be compared with the manual evidence counts without adding unrecorded components."
    return "The captured Copilot Studio screen shows completion of this named action; make no claim beyond the screenshot."


def choose_frame_resources(ctx: JourneyContext) -> list[Path]:
    knowledge = sorted(path for path in (ctx.package / "manual" / "knowledge").rglob("*") if path.is_file())
    skills = sorted((ctx.package / "manual" / "skills").rglob("SKILL.md"))
    knowledge_index = 0
    skill_index = 0
    selected: list[Path] = []
    for index, frame in enumerate(ctx.manual_frames, 1):
        filename = str(frame.get("file", ""))
        action = clean_frame_label(str(frame.get("label", "")), f"Review frame {index}")
        lower = action.lower()
        case = case_for_frame(ctx, filename)
        if case:
            selected.append(ctx.manual_evidence_path)
        elif "instruction" in lower:
            selected.append(ctx.package / "manual" / "GLOBAL-INSTRUCTIONS.md")
        elif (
            "skill" in lower
            and not any(word in lower for word in ("open", "review", "audit", "inventory", "diagnose"))
            and skills
        ):
            selected.append(skills[min(skill_index, len(skills) - 1)])
            skill_index += 1
        elif (
            any(word in lower for word in ("upload", "add", "select"))
            and any(word in lower for word in ("knowledge", "record", "rule", "policy", "file"))
            and not any(word in lower for word in ("open", "verify", "wait"))
            and knowledge
        ):
            selected.append(knowledge[min(knowledge_index, len(knowledge) - 1)])
            knowledge_index += 1
        elif any(word in lower for word in ("model", "draft", "publish", "create", "name")):
            selected.append(ctx.package / "deployment.json")
        else:
            selected.append(ctx.package / "export-manifest.json")
    return selected


def generic_label(path: Path) -> str:
    if path.name == "SKILL.md":
        return f"Manual skill: {path.parent.name.replace('_', ' ').replace('-', ' ')}"
    return path.stem.replace("_", " ").replace("-", " ").title()


def resource_id(prefix: str, path: Path) -> str:
    name = path.parent.name if path.name == "SKILL.md" else path.stem
    return slugify(f"{prefix}-{name}")


def add_resource(
    resources: list[Resource],
    seen: set[str],
    ctx: JourneyContext,
    resource_id_value: str,
    label: str,
    path: Path,
    use: str,
    *,
    generated: bool = False,
) -> None:
    rel = ctx.rel(path)
    if rel in seen:
        return
    seen.add(rel)
    status = "ready" if generated or path.exists() else "pending_capture"
    resources.append(Resource(resource_id_value, label, rel, use, status))


def referenced_media_path(
    ctx: JourneyContext,
    evidence_key: str,
    fallback: Path,
) -> Path:
    browserfilm = (ctx.manual_evidence or {}).get("browserfilm", {})
    value = browserfilm.get(evidence_key) if isinstance(browserfilm, dict) else None
    return resolve_repo_path(
        ctx.root,
        ctx.package,
        value if isinstance(value, str) else None,
        fallback,
    )


def collect_resources(ctx: JourneyContext) -> list[Resource]:
    resources: list[Resource] = []
    seen: set[str] = set()
    source = source_agent_path(ctx.root, ctx.deployment, ctx.transcripts)
    if source:
        add_resource(
            resources,
            seen,
            ctx,
            "portable-agent",
            "Portable source agent",
            source,
            "Local Brainstem runtime and production-logic reference",
        )
    add_resource(resources, seen, ctx, "deployment-recipe", "Deployment recipe", ctx.package / "deployment.json", "Easy-mode deployment contract")
    add_resource(resources, seen, ctx, "field-guide", "Customer field guide", ctx.package / "FIELD-GUIDE.md", "Facilitation, evidence boundaries, gates, and recovery", generated=True)
    add_resource(
        resources,
        seen,
        ctx,
        "easy-personless-guide",
        "Personless Easy-mode guide",
        ctx.package / "EASY-MODE-PERSONLESS.md",
        "One-sentence Brainstem + Copilot workshop trigger and engine loop",
        generated=True,
    )
    add_resource(
        resources,
        seen,
        ctx,
        "easy-copilot-chat-prompts",
        "Copilot-only Easy-mode comparison",
        ctx.package / "EASY-MODE-COPILOT-CHAT.md",
        "Detailed GitHub Copilot-only prompts retained for the skeptic comparison",
        generated=True,
    )
    workshop_agent = personless_agent_path(ctx)
    if workshop_agent:
        add_resource(
            resources,
            seen,
            ctx,
            "easy-personless-agent",
            "Personless workshop Brainstem agent",
            workshop_agent,
            "Hot-loaded workshop engine for asset retrieval, local proof, Draft setup, and verdict",
        )
    add_resource(resources, seen, ctx, "manual-instructions", "Manual global instructions", ctx.package / "manual" / "GLOBAL-INSTRUCTIONS.md", "Reviewed instructions for literal browser construction")

    settings = ctx.package / "copilot-studio" / "settings.mcs.yml"
    sync = ctx.package / "copilot-studio" / "agent.sync.yaml"
    if settings.exists():
        add_resource(resources, seen, ctx, "settings", "Copilot Studio settings", settings, "Easy-mode agent settings and instruction copy")
    if sync.exists():
        add_resource(resources, seen, ctx, "agent-sync", "Copilot Studio component manifest", sync, "Easy-mode component synchronization")

    for path in sorted(path for path in (ctx.package / "manual" / "knowledge").rglob("*") if path.is_file()):
        add_resource(resources, seen, ctx, resource_id("knowledge", path), generic_label(path), path, "Manual knowledge upload")
    for path in sorted((ctx.package / "manual" / "skills").rglob("SKILL.md")):
        add_resource(resources, seen, ctx, resource_id("skill", path), generic_label(path), path, "Manual skill upload")
    for path in sorted(path for path in (ctx.package / "copilot-studio" / "capabilities" / "knowledge").rglob("*") if path.is_file()):
        add_resource(resources, seen, ctx, resource_id("easy-knowledge", path), generic_label(path), path, "Copilot Studio knowledge source or synchronization metadata")
    for path in sorted(path for path in (ctx.package / "copilot-studio" / "behaviors").rglob("*") if path.is_file()):
        add_resource(resources, seen, ctx, resource_id("easy-skill", path), generic_label(path), path, "Copilot Studio behavior source")

    for path in sorted((ctx.package / "evals").glob("*.json")):
        stem = path.stem
        if stem == "transcripts":
            identifier, label, use = "brainstem-transcripts", "Isolated Brainstem transcripts", "Canonical source-agent acceptance evidence"
        elif stem == "manual-build-evidence":
            identifier, label, use = "manual-evidence", "Manual build evidence", "Manual identity, inventory, Preview, and Draft-gate evidence"
        elif "onepager" in stem or "map" in stem:
            identifier, label, use = "onepager-map", generic_label(path), "Advertised-promise mapping evidence"
        else:
            identifier, label, use = resource_id("easy-evidence", path), generic_label(path), "Easy-mode deployment or Preview evidence"
        add_resource(resources, seen, ctx, identifier, label, path, use)
    if not ctx.manual_evidence_path.exists():
        add_resource(resources, seen, ctx, "manual-evidence", "Manual build evidence", ctx.manual_evidence_path, "Required manual identity, Preview, and Draft-gate evidence")

    add_resource(resources, seen, ctx, "manual-browserfilm-manifest", "Manual browserfilm manifest", ctx.manual_browserfilm_path, "Ordered literal-browser evidence frames")
    for index, frame in enumerate(ctx.manual_frames, 1):
        filename = frame.get("file")
        if isinstance(filename, str) and filename:
            add_resource(
                resources,
                seen,
                ctx,
                f"manual-frame-{index:02d}",
                clean_frame_label(str(frame.get("label", "")), f"Manual frame {index}"),
                ctx.manual_browserfilm_path.parent / filename,
                "Real manual browser evidence frame",
            )
    manual_gif = referenced_media_path(
        ctx,
        "gif",
        ctx.package / "screenshots" / "manual" / "manual-build-walkthrough.gif",
    )
    manual_contact = referenced_media_path(
        ctx,
        "contact_sheet",
        ctx.package / "screenshots" / "manual" / "manual-build-contact-sheet.jpg",
    )
    add_resource(resources, seen, ctx, "manual-browserfilm", "Manual browserfilm", manual_gif, "Animated manual walkthrough")
    add_resource(resources, seen, ctx, "manual-contact-sheet", "Manual contact sheet", manual_contact, "Static manual evidence overview")

    assisted_gif = (
        ctx.package
        / "screenshots"
        / "assisted"
        / "copilot-assisted-walkthrough.gif"
    )
    assisted_contact = (
        ctx.package
        / "screenshots"
        / "assisted"
        / "copilot-assisted-contact-sheet.jpg"
    )
    if ctx.assisted_browserfilm or assisted_gif.exists() or assisted_contact.exists():
        if ctx.assisted_browserfilm:
            add_resource(resources, seen, ctx, "assisted-browserfilm-manifest", "Copilot-assisted browserfilm manifest", ctx.assisted_browserfilm_path, "Ordered Easy-mode evidence frames")
        if ctx.assisted_browserfilm or assisted_gif.exists():
            add_resource(resources, seen, ctx, "assisted-browserfilm", "Copilot-assisted browserfilm", assisted_gif, "Animated Easy-mode walkthrough")
        if ctx.assisted_browserfilm or assisted_contact.exists():
            add_resource(resources, seen, ctx, "assisted-contact-sheet", "Copilot-assisted contact sheet", assisted_contact, "Static Easy-mode evidence overview")
        if ctx.assisted_browserfilm:
            for index, frame in enumerate(ctx.assisted_browserfilm.get("frames", []), 1):
                if isinstance(frame, dict) and isinstance(frame.get("file"), str):
                    add_resource(
                        resources,
                        seen,
                        ctx,
                        f"assisted-frame-{index:02d}",
                        clean_frame_label(str(frame.get("label", "")), f"Assisted frame {index}"),
                        ctx.assisted_browserfilm_path.parent / frame["file"],
                        "Real Copilot-assisted browser evidence frame",
                    )

    generated = [
        ("quest", "Guided field quest", ctx.package / "quest.html", "Resumable Easy/Hard customer journey"),
        ("manual-tutorial", "Manual browser tutorial", ctx.package / "manual-tutorial.html", "One action per real manual evidence frame"),
        ("screenshots-readme", "Screenshot evidence README", ctx.package / "screenshots" / "README.md", "Evidence boundary and capture inventory"),
        ("manual-screenshots-readme", "Manual screenshot README", ctx.package / "screenshots" / "manual" / "README.md", "Manual frame and film inventory"),
        ("exports-readme", "Export README", ctx.package / "exports" / "README.md", "Bundle build instructions"),
    ]
    if (ctx.package / "screenshots" / "assisted").exists():
        generated.append(
            (
                "assisted-screenshots-readme",
                "Assisted screenshot README",
                ctx.package / "screenshots" / "assisted" / "README.md",
                "Copilot-assisted evidence inventory",
            )
        )
    for identifier, label, path, use in generated:
        add_resource(resources, seen, ctx, identifier, label, path, use, generated=True)
    return resources


def render_manifest(ctx: JourneyContext, resources: list[Resource]) -> str:
    solution = ctx.deployment.get("name") or f"@aibast-agents-library/{ctx.slug}"
    bundle_path = f"solutions/{ctx.slug}/exports/{ctx.slug}-source.zip"
    manifest = {
        "schema": "aibast-solution-export/1.0",
        "solution": solution,
        "raw_base": ctx.raw_base,
        "github_folder": (
            "https://github.com/microsoft/aibast-agents-library/tree/main/"
            f"solutions/{ctx.slug}"
        ),
        "evidence_boundary": (
            "Synthetic solution evidence only. Qualitative workflow proof is not a "
            "customer KPI, measured production result, or publication approval."
        ),
        "bundle": {
            "label": f"Complete {ctx.title} source bundle",
            "path": bundle_path,
            "raw_url": ctx.raw(bundle_path),
        },
        "files": [
            {
                "id": resource.id,
                "label": resource.label,
                "path": resource.path,
                "raw_url": ctx.raw(resource.path),
                "use": resource.use,
                "status": resource.status,
            }
            for resource in resources
        ],
    }
    return json.dumps(manifest, indent=2) + "\n"


def markdown_list(values: Iterable[str], fallback: str) -> str:
    items = [f"- {value}" for value in values if value]
    return "\n".join(items) if items else f"- {fallback}"


def production_seams(ctx: JourneyContext) -> list[str]:
    copilot = ctx.deployment.get("copilot_studio", {})
    values = copilot.get("required_connections", []) if isinstance(copilot, dict) else []
    seams = [
        f"Replace packaged synthetic inputs with an approved {value} connection; preserve the reviewed input and output contract."
        for value in values
        if isinstance(value, str)
    ]
    if seams:
        return seams
    return [
        "Replace manual knowledge files with approved, governed customer sources while preserving grounding and citation boundaries.",
        "Replace recommendation-only skill seams with approved tools only after identity, authorization, confirmation, and success evidence are defined.",
        "Keep publication, sharing, telemetry, retention, and support ownership as explicit production decisions.",
    ]


def easy_case_records(ctx: JourneyContext) -> list[dict[str, Any]]:
    transcripts = {
        str(item.get("case_id", "case")): item
        for item in ctx.transcripts.get("transcripts", [])
        if isinstance(item, dict)
    }
    possible: list[dict[str, Any]] = []
    seen: set[str] = set()
    for name in ("copilot-studio-preview-evidence.json", "copilot-studio-transcripts.json"):
        path = ctx.package / "evals" / name
        if path.exists():
            evidence = read_json(path)
            cases = evidence.get("cases") or evidence.get("transcripts") or []
            if isinstance(cases, list):
                for case in cases:
                    if isinstance(case, dict):
                        case_id = str(case.get("case_id", "case"))
                        if case_id in seen:
                            continue
                        transcript = transcripts.get(case_id, {})
                        possible.append(
                            {
                                "case_id": case_id,
                                "prompt": str(
                                    case.get("prompt")
                                    or transcript.get("prompt")
                                    or "recorded prompt"
                                ),
                                "must_include": list(
                                    case.get("must_include")
                                    or transcript.get("must_include")
                                    or []
                                ),
                                "must_not_include": list(
                                    case.get("must_not_include") or []
                                ),
                            }
                        )
                        seen.add(case_id)
    for case_id, transcript in transcripts.items():
        if case_id in seen:
            continue
        possible.append(
            {
                "case_id": case_id,
                "prompt": str(transcript.get("prompt", "recorded prompt")),
                "must_include": list(transcript.get("must_include") or []),
                "must_not_include": [],
            }
        )
        seen.add(case_id)
    return possible


def easy_case_lines(ctx: JourneyContext) -> list[str]:
    return [
        f"`{case['case_id']}` — {case['prompt']}"
        for case in easy_case_records(ctx)
    ]


def easy_case_contract(ctx: JourneyContext) -> str:
    sections = []
    for case in easy_case_records(ctx):
        includes = ", ".join(case["must_include"]) or "the packaged expected evidence"
        excludes = ", ".join(case["must_not_include"]) or "any unsupported side effect"
        sections.append(
            "\n".join(
                [
                    f"{case['case_id']}",
                    f'Prompt: "{case["prompt"]}"',
                    f"Must include: {includes}",
                    f"Must not include: {excludes}",
                ]
            )
        )
    return "\n\n".join(sections) or (
        "No locked case is available. Stop and report the missing evidence."
    )


def copilot_chat_prompt(value: str) -> str:
    prefix = "You are GitHub Copilot Chat running in Agent mode in VS Code."
    cleaned = re.sub(
        r"^You are GitHub Copilot(?: Chat)? running in Agent mode(?: in VS Code)?\.\s*",
        "",
        value.strip(),
        flags=re.IGNORECASE,
    )
    return f"{prefix} {cleaned}".strip()


def easy_copilot_chat_prompts(ctx: JourneyContext) -> list[tuple[str, str]]:
    package = f"solutions/{ctx.slug}"
    deployment_url = ctx.raw(f"{package}/deployment.json")
    manifest_url = ctx.raw(f"{package}/export-manifest.json")
    source_url = str(ctx.deployment.get("source_url") or "the source in deployment.json")
    expected_tool = str(ctx.deployment.get("expected_tool") or "the expected tool")
    smoke = ctx.deployment.get("smoke_test", {})
    smoke_prompt = str(smoke.get("prompt") or "the smoke prompt in deployment.json")
    studio = ctx.deployment.get("copilot_studio", {})
    plugin = str(studio.get("plugin") or "the Microsoft Copilot Studio plugin")
    model = model_name(ctx)
    knowledge = [
        f"{package}/{value}"
        for value in studio.get("manual_knowledge_files", [])
        if isinstance(value, str)
    ]
    skills = [
        ctx.rel(path)
        for path in sorted((ctx.package / "manual" / "skills").rglob("SKILL.md"))
    ]
    connections = [
        value
        for value in studio.get("required_connections", [])
        if isinstance(value, str)
    ]
    knowledge_text = "\n".join(f"- {value}" for value in knowledge)
    skills_text = "\n".join(f"- {value}" for value in skills)
    connections_text = ", ".join(connections) or "the documented production connections"
    cases = easy_case_contract(ctx)

    fast_path = copilot_chat_prompt(
        f"""Complete the {ctx.title} Easy mode end to end and own every terminal, file, plugin, and validation step.

Read {deployment_url} and {manifest_url}. Work from the reviewed package in `{package}`. Verify that the portable source is `{source_url}` and the expected tool is `{expected_tool}`. Install or start the repository's local Brainstem using its existing supported scripts, load the exact agent, confirm it appears in `/health`, run the smoke prompt "{smoke_prompt}", and show the evidence. Do not ask me to open a terminal, run a command, clone a repository, or install dependencies myself.

Then use the Microsoft Copilot Studio plugin (`{plugin}`) to initialize or update the source-controlled Copilot Studio Draft from `{package}/copilot-studio`. Preserve the reviewed instructions, use model `{model}`, remove web search, upload the exact knowledge and skill files listed below, and leave production connections unbound unless an already-approved connection exists. Never invent a connection or substitute different content.

Knowledge:
{knowledge_text}

Skills:
{skills_text}

Start a fresh Preview conversation for each locked case below. Send each prompt exactly as written, compare the response with the required and forbidden markers, and report pass or fail without retrying until it happens to pass.

{cases}

Finish with the local health result, smoke-test result, Copilot Studio display name and bot identity, model, inventory counts, case-by-case results, Git diff, and unresolved blockers. Stop with the agent in Draft. Stop before publish. Do not publish, send messages, modify customer systems, post revenue, change time entries, create invoices, or contact clients."""
    )
    inspect = copilot_chat_prompt(
        f"""Take ownership of the {ctx.title} Easy mode. Read {deployment_url}, {manifest_url}, `{package}/deployment.json`, the portable source, global instructions, every knowledge file, every `SKILL.md`, Copilot Studio source, and locked evidence. Before modifying anything, tell me the exact source, expected tool, smoke prompt, model, knowledge files, skills, locked cases, safety boundaries, and Draft gate you will preserve. Identify any missing prerequisite as a blocker. Do not ask me to open a terminal or run commands myself."""
    )
    local = copilot_chat_prompt(
        f"""Run the local proof for {ctx.title}. Use only the repository's existing Brainstem install/start flow. Own all terminal commands yourself. Load `{source_url}` as `{expected_tool}`, confirm it in `http://localhost:7071/health`, send the exact smoke prompt "{smoke_prompt}" to the local chat endpoint, and compare the result with deployment.json. Report the commands you ran and the observed evidence. Do not change source behavior, connect customer systems, or ask me to perform setup."""
    )
    author = copilot_chat_prompt(
        f"""Create or update the {ctx.title} Copilot Studio Draft using the Microsoft Copilot Studio plugin (`{plugin}`) and the reviewed source under `{package}/copilot-studio`. Preserve the existing Draft identity when one is recorded. Use model `{model}`, exact global instructions, all {len(knowledge)} packaged knowledge files, and all {len(skills)} packaged skills. Remove web search and any unapproved tool. Keep {connections_text} as documented production seams; do not fabricate or bind a live connection. Synchronize changes and report the exact files changed and agent identity. Stop before publish."""
    )
    validate = copilot_chat_prompt(
        f"""Validate the {ctx.title} Draft in Copilot Studio Preview. Start a fresh conversation for every case. Paste each prompt exactly, check every required and forbidden marker, capture the observed result, and report pass or fail. Do not paraphrase acceptance text, silently edit the agent, or retry until a response happens to pass.

{cases}"""
    )
    audit = copilot_chat_prompt(
        f"""Perform the final Easy-mode audit for {ctx.title}. Confirm the local tool loaded and passed its smoke test; the source-controlled Copilot Studio project matches deployment.json; model `{model}`, exact instructions, {len(knowledge)} knowledge files, {len(skills)} skills, and all locked cases are present; web search and unapproved tools are absent; every case passed; no external side effect occurred; and the agent is Draft and unpublished. Show the Git diff, evidence paths, agent identity, environment, inventory counts, case totals, and blockers. Do not publish or commit unless I explicitly ask."""
    )
    return [
        ("Fast path — complete Easy mode in one message", fast_path),
        ("1. Inspect the package and state the plan", inspect),
        ("2. Install and prove the portable agent locally", local),
        ("3. Create or update the Copilot Studio Draft", author),
        ("4. Replay every locked validation prompt", validate),
        ("5. Audit the result and stop at Draft", audit),
    ]


def personless_agent_path(ctx: JourneyContext) -> Path | None:
    agents = sorted((ctx.package / "easy").glob("*_agent.py"))
    return agents[0] if agents else None


def personless_trigger_sentence(ctx: JourneyContext) -> str:
    agent = personless_agent_path(ctx)
    if not agent:
        return (
            f"Run the {ctx.title} workshop through my local RAPP Brainstem "
            "personlessly, keep executing every Brainstem handoff until it "
            "reports complete, and stop before publish."
        )
    return (
        "Use my local RAPP Brainstem at http://localhost:7071: hot-load "
        f"{ctx.raw(ctx.rel(agent))} through /agents/import, ask /chat to run "
        f"the {ctx.title} workshop, execute every handoff it returns until "
        "Brainstem reports complete, and stop before publish."
    )


def render_personless_easy_markdown(ctx: JourneyContext) -> str:
    agent = personless_agent_path(ctx)
    agent_link = ctx.raw(ctx.rel(agent)) if agent else "Agent cartridge pending"
    return f"""# {ctx.title} — personless Easy mode

Open GitHub Copilot Chat in VS Code, select **Agent mode**, and paste this one
sentence:

```text
{personless_trigger_sentence(ctx)}
```

## What pulls the harness

1. GitHub Copilot checks the local Brainstem and imports the raw workshop
   cartridge through `/agents/import`.
2. Brainstem invokes `TimeEntryBillingWorkshop`, which downloads the reviewed
   GitHub assets, verifies their pinned source hash, and hot-loads the business
   agent into its live agents directory.
3. The workshop cartridge runs every locked local case, prepares or pushes the
   Copilot Studio Draft through the active PAC environment, and returns the
   exact front-door actions still required.
4. Copilot performs those actions, sends the captured Preview evidence back to
   Brainstem, and continues until Brainstem returns `status: complete`.
5. The final gate requires **Draft** and `published: false`.

Workshop cartridge: {agent_link}

This is the default Easy path. The person sets the destination and reads the
verdict; Brainstem + Copilot pull the harness.
"""


def render_easy_copilot_chat_markdown(ctx: JourneyContext) -> str:
    sections = "\n\n".join(
        f"## {title}\n\n```text\n{prompt}\n```"
        for title, prompt in easy_copilot_chat_prompts(ctx)
    )
    return f"""# {ctx.title} — Copilot-only Easy mode comparison

Open this repository in VS Code, open **GitHub Copilot Chat**, select **Agent
mode**, and paste either the fast-path message or messages 1–5 in order.
These are natural-language commands for Copilot to perform the work; they are
not shell commands for the user to translate or run.

This comparison lane intentionally omits Brainstem so workshop participants can
answer “why not just use GitHub Copilot by itself?” It is retained behind the
default Brainstem + Copilot personless lane.

{sections}

## Completion boundary

Copilot may perform setup, local validation, source-controlled Copilot Studio
authoring, and evidence checks. It must stop at **Draft**. Publishing and every
production write remain separate human approval gates.
"""


def render_field_guide(ctx: JourneyContext) -> str:
    missing = (
        "\n## Pending evidence\n\n"
        + markdown_list(ctx.missing_evidence, "No pending evidence.")
        + "\n\nPending items are not proof and must not be described as captured.\n"
        if ctx.missing_evidence
        else ""
    )
    return f"""# {ctx.title} — customer field guide

Use this guide with the customer at the keyboard. The goal is to inspect the
portable source, reproduce the synthetic workflow, review the deployment
blueprint, and decide what production integration would require.

## Evidence boundary

- All packaged records and outcomes are synthetic.
- Recorded cases provide qualitative workflow evidence only.
- They are not customer KPIs, measured production results, forecasts,
  commitments, or proof of a live system connection.
- A screenshot proves only the visible state in that frame.
- No image, GIF, transcript, connector result, or publication state is implied
  unless the corresponding file is present in `export-manifest.json`.

## Easy mode — with Brainstem (default)

1. Open GitHub Copilot Chat in VS Code and select **Agent mode**.
2. Open `EASY-MODE-PERSONLESS.md`.
3. Paste its single sentence.
4. Copilot hot-loads the task-specific workshop agent into the local Brainstem.
5. Brainstem retrieves the reviewed GitHub assets, hot-loads the business
   agent, proves it locally, drives Draft setup, and returns front-door actions.
6. Copilot executes each handoff and sends evidence back until Brainstem
   returns `status: complete`.
7. Stop at **Draft**. Publishing remains a separate human approval gate.

## Easy mode — without Brainstem (comparison)

`EASY-MODE-COPILOT-CHAT.md` retains the detailed GitHub Copilot-only prompts
for participants who ask why Copilot cannot do the same work alone. That lane
keeps the person in the harness; it is deliberately secondary.

Both Easy lanes preserve every recorded case prompt:

{markdown_list(easy_case_lines(ctx), "No Easy-mode case evidence is recorded; treat this checkpoint as pending.")}

## Hard mode — literal browser construction

Hard mode is for reviewers who want to reproduce the build in the browser.
Do not use PAC CLI, YAML import, or a plugin architect in Hard mode.

1. Open `manual-tutorial.html`.
2. Perform exactly one browser action per captured frame.
3. Use the linked `manual/GLOBAL-INSTRUCTIONS.md`, knowledge files, and
   `SKILL.md` files; do not retype or silently revise them.
4. Compare each action with its real screenshot and expected-result boundary.
5. Replay only the Preview cases recorded in `evals/manual-build-evidence.json`.
6. Keep the manual duplicate in **Draft**. Do not choose Publish.

## Production replacement seams

{markdown_list(production_seams(ctx), "No production seam is declared.")}

The pilot must never claim a side effect, live lookup, or system update unless
an approved production tool returns evidence that it succeeded.

## Failure recovery

| Symptom | Recovery |
| --- | --- |
| A required evidence file is missing | Stop. Capture or restore the real file; never substitute a mockup. |
| A browser frame disagrees with the tutorial | Treat the frame and evidence JSON as authoritative, correct the package metadata, and regenerate. |
| Knowledge is still processing | Wait for ingestion to finish before Preview; do not interpret a partial answer as evidence. |
| A skill upload fails | Download the linked raw `SKILL.md`, correct the reviewed source if necessary, and retry visibly. |
| Easy and Hard inventories differ | Stop the comparison and restore exact instruction, knowledge, skill, and model parity. |
| A recorded identifier is absent | Mark the case failed and investigate; do not retry until it happens to pass. |
| Publish is offered | Stop at Draft unless a separate approver explicitly authorizes publication. |

## Evidence gates

- **Source gate:** deployment source and isolated transcripts exist.
- **Easy gate:** available Easy evidence identifies the agent, environment,
  model, inventory, cases, and Draft state.
- **Manual gate:** manual evidence passes, every browserfilm frame exists, and
  the tutorial maps one action to each frame.
- **Parity gate:** Easy and Hard use the reviewed instructions, knowledge,
  skills, model, and case identifiers.
- **Draft gate:** the package records `published: false`; publication is not
  part of scaffolding.
- **Customer gate:** replacement connections, governance, telemetry, support,
  and success measures are agreed before production.
{missing}"""


def raw_link(ctx: JourneyContext, path: Path) -> str:
    return ctx.raw(ctx.rel(path))


def render_manual_tutorial(ctx: JourneyContext) -> str:
    resources = choose_frame_resources(ctx)
    step_cards = []
    toc_links = []
    for index, frame in enumerate(ctx.manual_frames, 1):
        filename = str(frame.get("file", ""))
        action = clean_frame_label(str(frame.get("label", "")), f"Review frame {index}")
        expected = expected_result(ctx, action, filename)
        screenshot = ctx.manual_browserfilm_path.parent / filename
        screenshot_html = (
            f'<img class="shot" src="screenshots/manual/{html.escape(filename)}" '
            f'alt="{html.escape(action)} evidence">'
            if screenshot.exists()
            else (
                '<div class="missing">Evidence pending. No screenshot is shown and '
                "this action must not be claimed as captured.</div>"
            )
        )
        source = resources[index - 1]
        source_label = (
            "Export manifest"
            if source.name == "export-manifest.json"
            else generic_label(source)
        )
        toc_links.append(
            f'<a href="#step-{index}">{index}. {html.escape(action)}</a>'
        )
        step_cards.append(
            f"""
      <article class="step" id="step-{index}">
        <header><span>{index}</span><div><h3>{html.escape(action)}</h3><p>Frame {index} of {len(ctx.manual_frames)}</p></div></header>
        <div class="step-body">
          <div class="instruction-grid">
            <div class="instruction"><strong>Action</strong>{html.escape(action)}</div>
            <div class="instruction expected"><strong>Expected result</strong>{html.escape(expected)}</div>
          </div>
          {screenshot_html}
          <footer>
            <a href="{html.escape(raw_link(ctx, source))}">Raw download: {html.escape(source_label)}</a>
            <label><input class="complete" type="checkbox" data-step="{index}"> Mark complete</label>
          </footer>
        </div>
      </article>"""
        )

    pending_notice = (
        '<div class="notice"><strong>Pending evidence:</strong> this page was generated '
        "with <code>--allow-pending</code>. Missing evidence is labeled and is not proof.</div>"
        if ctx.missing_evidence
        else "<!-- No pending evidence. -->"
    )
    steps_markup = "\n".join(card.strip() for card in step_cards) or (
        '<div class="notice"><strong>No manual frames are available.</strong> '
        "Capture manual evidence before using this tutorial as proof.</div>"
    )
    toc_markup = "\n".join(toc_links)
    frame_count = len(ctx.manual_frames)
    manual_gif = referenced_media_path(
        ctx,
        "gif",
        ctx.package / "screenshots" / "manual" / "manual-build-walkthrough.gif",
    )
    gif_button = (
        '<a class="button" href="screenshots/manual/manual-build-walkthrough.gif">Watch the manual film</a>'
        if manual_gif.exists()
        else '<span class="button" aria-disabled="true">Manual film pending</span>'
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Build {html.escape(ctx.title)} manually</title>
  <script>
    {THEME_SCRIPT}
  </script>
  <style>
{COMMON_CSS}
    .layout {{ display: grid; grid-template-columns: 270px minmax(0, 840px); gap: 32px; max-width: 1180px; margin: 0 auto; padding: 32px 24px 80px; }}
    .sidebar {{ position: sticky; top: 82px; align-self: start; max-height: calc(100vh - 104px); overflow: auto; }}
    .toc {{ display: grid; gap: 4px; margin-top: 14px; }}
    .toc a {{ padding: 7px 9px; border-left: 3px solid var(--cp-border); color: var(--cp-text-muted); text-decoration: none; font-size: 13px; }}
    .toc a:hover {{ border-left-color: var(--cp-accent); color: var(--cp-text); }}
    .step {{ scroll-margin-top: 90px; margin: 0 0 28px; overflow: hidden; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); }}
    .step header {{ display: flex; gap: 14px; padding: 20px 22px; border-bottom: 1px solid var(--cp-border); }}
    .step header > span {{ display: grid; width: 36px; height: 36px; place-items: center; border-radius: 10px; background: var(--cp-accent-soft); color: var(--cp-accent); font-weight: 800; }}
    .step h3, .step header p {{ margin: 0; }}
    .step header p {{ color: var(--cp-text-muted); font-size: 13px; }}
    .step-body {{ padding: 22px; }}
    .instruction-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 18px; }}
    .instruction {{ padding: 14px; border-radius: 10px; background: var(--cp-surface-soft); }}
    .instruction strong {{ display: block; margin-bottom: 6px; }}
    .instruction.expected {{ border-left: 4px solid var(--cp-success); }}
    .shot {{ display: block; width: 100%; border: 1px solid var(--cp-border); border-radius: 10px; }}
    .missing {{ padding: 32px; border: 2px dashed var(--cp-warning); border-radius: 10px; color: var(--cp-text-muted); }}
    .step footer {{ display: flex; justify-content: space-between; gap: 12px; margin-top: 16px; flex-wrap: wrap; }}
    .troubleshooting details {{ padding: 14px 0; border-bottom: 1px solid var(--cp-border); }}
    summary {{ cursor: pointer; font-weight: 700; }}
    @media (max-width: 900px) {{ .layout {{ grid-template-columns: 1fr; }} .sidebar {{ position: static; max-height: none; }} }}
    @media (max-width: 620px) {{ .instruction-grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand"><span class="brand-mark">C</span><span>Clawpilot manual journey</span></div>
    <div>{gif_button} <a class="button primary" href="exports/{html.escape(ctx.slug)}-source.zip">Download source bundle</a></div>
  </header>
  <div class="layout">
    <aside class="sidebar">
      <strong id="progress-label">0 of {frame_count} complete</strong>
      <div class="progress"><span id="progress-bar"></span></div>
      <nav class="toc" aria-label="Tutorial actions">{toc_markup}</nav>
    </aside>
    <main>
      <section class="hero">
        <p class="eyebrow">Hard mode · literal browser construction</p>
        <h1>Build {html.escape(ctx.title)} manually.</h1>
        <p class="lede">No PAC CLI, YAML import, or plugin architect. Perform exactly one action per real browserfilm frame, compare the screenshot, and stop at Draft.</p>
        <div class="notice"><strong>Synthetic disclosure:</strong> this is qualitative workflow evidence using packaged synthetic inputs. It is not a customer KPI or a live-system result.</div>
        {pending_notice}
      </section>
      <h2>Build and verify</h2>
      {steps_markup}
      <h2 id="troubleshooting">Troubleshooting</h2>
      <section class="card troubleshooting">
        <details open><summary>A screenshot or browserfilm frame is missing</summary><p>Stop. Do not invent, recreate, or substitute an image. Capture the real frame, update the browserfilm manifest, and regenerate without <code>--allow-pending</code>.</p></details>
        <details><summary>A knowledge file is still processing</summary><p>Wait for ingestion to finish before Preview. A partial answer is not evidence.</p></details>
        <details><summary>A skill upload fails</summary><p>Use the linked raw <code>SKILL.md</code>. Fix the reviewed source deliberately; do not silently skip the action.</p></details>
        <details><summary>The model differs from Easy mode</summary><p>Record the substitution and stop the parity claim until Easy and Hard use the same reviewed model.</p></details>
        <details><summary>The Preview answer misses an identifier</summary><p>Mark the recorded case failed, inspect instructions and inventory, then replay the exact prompt in a fresh conversation.</p></details>
        <details><summary>Should I publish?</summary><p>No. Keep this manual duplicate in Draft unless publication is separately approved. Do not choose Publish as part of this tutorial.</p></details>
      </section>
    </main>
  </div>
  <script>
    (() => {{
      const key = "aibast:{html.escape(ctx.slug)}:manual-progress";
      const boxes = Array.from(document.querySelectorAll(".complete"));
      const label = document.getElementById("progress-label");
      const bar = document.getElementById("progress-bar");
      let saved = [];
      try {{ saved = JSON.parse(localStorage.getItem(key) || "[]"); }} catch (_error) {{ saved = []; }}
      boxes.forEach((box) => {{
        box.checked = saved.includes(box.dataset.step);
        box.addEventListener("change", update);
      }});
      function update() {{
        const done = boxes.filter((box) => box.checked).map((box) => box.dataset.step);
        localStorage.setItem(key, JSON.stringify(done));
        label.textContent = `${{done.length}} of ${{boxes.length}} complete`;
        bar.style.width = boxes.length ? `${{(done.length / boxes.length) * 100}}%` : "0%";
      }}
      update();
    }})();
  </script>
</body>
</html>
"""


def quest_resources(ctx: JourneyContext, resources: list[Resource]) -> str:
    preferred = {
        "deployment-recipe",
        "field-guide",
        "easy-personless-guide",
        "easy-personless-agent",
        "easy-copilot-chat-prompts",
        "manual-instructions",
        "brainstem-transcripts",
        "manual-evidence",
        "assisted-browserfilm",
        "manual-browserfilm",
        "manual-tutorial",
    }
    cards = []
    for resource in resources:
        if resource.id not in preferred:
            continue
        status = "Ready" if resource.status == "ready" else "Pending — not evidence"
        cards.append(
            f'<li><a href="{html.escape(resource.path.removeprefix(f"solutions/{ctx.slug}/"))}">'
            f"{html.escape(resource.label)}</a> <span class=\"status\">{status}</span></li>"
        )
    return "\n".join(cards)


def render_easy_prompt_cards(ctx: JourneyContext) -> str:
    cards = []
    for index, (title, prompt) in enumerate(
        easy_copilot_chat_prompts(ctx),
        start=1,
    ):
        target = f"easy-prompt-{index}"
        cards.append(
            f"""<article class="prompt-card">
        <div class="prompt-heading">
          <div><p class="prompt-kicker">GitHub Copilot Chat message {index}</p><h3>{html.escape(title)}</h3></div>
          <button class="button primary" type="button" data-copy-target="{target}">Copy prompt</button>
        </div>
        <pre class="prompt-block" id="{target}">{html.escape(prompt)}</pre>
      </article>"""
        )
    return "\n".join(cards)


def render_quest(ctx: JourneyContext, resources: list[Resource]) -> str:
    assisted_gif = ctx.package / "screenshots" / "assisted" / "copilot-assisted-walkthrough.gif"
    manual_gif = referenced_media_path(
        ctx,
        "gif",
        ctx.package / "screenshots" / "manual" / "manual-build-walkthrough.gif",
    )
    assisted_link = (
        '<a class="button" href="screenshots/assisted/copilot-assisted-walkthrough.gif">Watch assisted film</a>'
        if assisted_gif.exists()
        else '<span class="button" aria-disabled="true">Assisted film pending</span>'
    )
    manual_link = (
        '<a class="button" href="screenshots/manual/manual-build-walkthrough.gif">Watch manual film</a>'
        if manual_gif.exists()
        else '<span class="button" aria-disabled="true">Manual film pending</span>'
    )
    workshop_agent = personless_agent_path(ctx)
    workshop_agent_link = (
        f'<a class="button" href="{html.escape(workshop_agent.relative_to(ctx.package).as_posix())}">View workshop agent</a>'
        if workshop_agent
        else '<span class="button" aria-disabled="true">Workshop agent pending</span>'
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(ctx.title)} deployment quest</title>
  <script>
    {THEME_SCRIPT}
  </script>
  <style>
{COMMON_CSS}
    .mode-switch {{ display: inline-flex; gap: 6px; margin-top: 20px; padding: 5px; border: 1px solid var(--cp-border); border-radius: 999px; background: var(--cp-surface-soft); }}
    .mode {{ border: 0; border-radius: 999px; padding: 9px 14px; background: transparent; color: var(--cp-text-muted); cursor: pointer; font-weight: 750; }}
    .mode.active {{ background: var(--cp-accent); color: var(--cp-accent-fg); }}
    .checkpoint {{ display: grid; grid-template-columns: auto 1fr; gap: 12px; align-items: start; margin: 12px 0; padding: 16px; border: 1px solid var(--cp-border); border-radius: 12px; background: var(--cp-surface); }}
    .checkpoint input {{ width: 20px; height: 20px; margin-top: 3px; accent-color: var(--cp-accent); }}
    .checkpoint strong, .checkpoint span {{ display: block; }}
    .checkpoint span {{ color: var(--cp-text-muted); }}
    .path[hidden] {{ display: none; }}
    .easy-lane-switch {{ display: inline-flex; gap: 6px; margin: 16px 0; padding: 5px; border: 1px solid var(--cp-border); border-radius: 10px; background: var(--cp-surface-soft); }}
    .easy-lane-button {{ border: 0; border-radius: 8px; padding: 10px 14px; background: transparent; color: var(--cp-text-muted); cursor: pointer; font-weight: 750; }}
    .easy-lane-button.active {{ background: var(--cp-accent); color: var(--cp-accent-fg); }}
    .easy-lane[hidden] {{ display: none; }}
    .engine-flow {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 18px 0; }}
    .engine-node {{ padding: 14px; border: 1px solid var(--cp-border); border-radius: 10px; background: var(--cp-surface); text-align: center; font-weight: 750; }}
    .comparison-note {{ margin: 14px 0; padding: 14px; border-left: 4px solid var(--cp-warning); background: var(--cp-surface-soft); color: var(--cp-text-muted); }}
    .prompt-card {{ margin: 16px 0; padding: 18px; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); }}
    .prompt-heading {{ display: flex; align-items: start; justify-content: space-between; gap: 16px; }}
    .prompt-heading h3 {{ margin: 0; }}
    .prompt-kicker {{ margin: 0 0 4px; color: var(--cp-accent); font-size: 12px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; }}
    .prompt-block {{ overflow-x: auto; margin: 14px 0 0; padding: 16px; border: 1px solid var(--cp-border); border-radius: 10px; background: var(--cp-surface-soft); color: var(--cp-text); white-space: pre-wrap; word-break: break-word; font-family: Consolas, "Courier New", Courier, monospace; font-size: 13px; line-height: 1.55; }}
    .resource-list {{ columns: 2; padding-left: 22px; }}
    .resource-list li {{ break-inside: avoid; margin-bottom: 10px; }}
    @media (max-width: 760px) {{ .engine-flow {{ grid-template-columns: 1fr; }} }}
    @media (max-width: 620px) {{ .resource-list {{ columns: 1; }} .prompt-heading {{ display: block; }} .prompt-heading .button {{ margin-top: 12px; }} .easy-lane-switch {{ display: grid; }} }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand"><span class="brand-mark">C</span><span>Clawpilot deployment quest</span></div>
    <a class="button primary" href="FIELD-GUIDE.md">Open field guide</a>
  </header>
  <main class="page">
    <section class="hero">
      <p class="eyebrow">Evidence-grounded customer journey</p>
      <h1>{html.escape(ctx.title)}</h1>
      <p class="lede">Default to the Brainstem + Copilot personless harness, compare it with Copilot alone, or reproduce every click in Hard mode.</p>
      <div class="notice"><strong>Boundary:</strong> synthetic qualitative evidence only—not a customer KPI, measured production result, live connection, or publication approval.</div>
      <div class="mode-switch" role="tablist">
        <button class="mode active" data-mode="easy" role="tab">Easy</button>
        <button class="mode" data-mode="hard" role="tab">Hard</button>
      </div>
    </section>

    <section class="path" data-path="easy">
      <h2>Easy mode</h2>
      <div class="easy-lane-switch" role="tablist" aria-label="Easy mode harness">
        <button class="easy-lane-button active" type="button" data-easy-lane-button="brainstem">With Brainstem — default</button>
        <button class="easy-lane-button" type="button" data-easy-lane-button="copilot">GitHub Copilot only</button>
      </div>

      <div class="easy-lane" data-easy-lane="brainstem">
        <div class="notice"><strong>Personless harness:</strong> the attendee sets the destination with one sentence. Brainstem is the engine; Copilot pulls the front-door actions until Brainstem returns the verdict.</div>
        <article class="prompt-card">
          <div class="prompt-heading">
            <div><p class="prompt-kicker">One sentence · recommended</p><h3>Run the personless workshop</h3></div>
            <button class="button primary" type="button" data-copy-target="personless-prompt">Copy sentence</button>
          </div>
          <pre class="prompt-block" id="personless-prompt">{html.escape(personless_trigger_sentence(ctx))}</pre>
        </article>
        <div class="engine-flow" aria-label="Personless harness loop">
          <div class="engine-node">1. GitHub Copilot</div>
          <div class="engine-node">2. RAPP Brainstem</div>
          <div class="engine-node">3. Hot-loaded workshop agent</div>
          <div class="engine-node">4. Evidence verdict</div>
        </div>
        <label class="checkpoint"><input type="checkbox" data-checkpoint="brainstem-hotload"><span><strong>Brainstem hot-loaded the workshop cartridge</strong><span>The raw task-specific agent entered the live agents directory through the standard import boundary.</span></span></label>
        <label class="checkpoint"><input type="checkbox" data-checkpoint="brainstem-local"><span><strong>The engine proved the business agent locally</strong><span>Source integrity and every locked deterministic case passed without attendee action.</span></span></label>
        <label class="checkpoint"><input type="checkbox" data-checkpoint="brainstem-studio"><span><strong>Copilot executed Brainstem’s front-door handoffs</strong><span>The Draft was prepared, Preview evidence returned to Brainstem, and the loop continued without a person pulling each step.</span></span></label>
        <label class="checkpoint"><input type="checkbox" data-checkpoint="brainstem-verdict"><span><strong>Brainstem reported complete</strong><span>The final state proves Draft, published false, and every locked case passed.</span></span></label>
        <p><a class="button" href="EASY-MODE-PERSONLESS.md">Open personless guide</a> {workshop_agent_link} <a class="button" href="https://kodyw.com/the-personless-harness/" target="_blank" rel="noopener">Why personless? ↗</a></p>
      </div>

      <div class="easy-lane" data-easy-lane="copilot" hidden>
        <div class="comparison-note"><strong>Skeptic comparison:</strong> this lane proves GitHub Copilot can perform the work without Brainstem, but the attendee remains the horse—feeding the sequence, checking each stage, and deciding what happens next.</div>
        <p>Use the fast-path prompt or messages 1–5 in order. These detailed prompts remain intentionally behind the Brainstem-default lane.</p>
        {render_easy_prompt_cards(ctx)}
        <label class="checkpoint"><input type="checkbox" data-checkpoint="copilot-source"><span><strong>Copilot inspected the source package</strong><span>It reported the source, tool, model, knowledge, skills, locked cases, and safety boundary before editing.</span></span></label>
        <label class="checkpoint"><input type="checkbox" data-checkpoint="copilot-build"><span><strong>Copilot completed local and Copilot Studio setup</strong><span>GitHub Copilot owned terminal and plugin actions, but the user still supplied the detailed harness.</span></span></label>
        <label class="checkpoint"><input type="checkbox" data-checkpoint="copilot-cases"><span><strong>Copilot replayed every locked case</strong><span>It used exact prompts and identifiers and recorded pass/fail evidence without retrying until success.</span></span></label>
        <label class="checkpoint"><input type="checkbox" data-checkpoint="copilot-draft"><span><strong>Stop at the Draft gate</strong><span>The agent must remain Draft and is not published. Publishing needs separate human approval.</span></span></label>
        <p><a class="button" href="EASY-MODE-COPILOT-CHAT.md">Open Copilot-only prompts</a> {assisted_link}</p>
      </div>
    </section>

    <section class="path" data-path="hard" hidden>
      <h2>Hard mode — literal browser construction</h2>
      <p>Do not use PAC CLI or YAML import in Hard mode. Do not use a plugin architect.</p>
      <label class="checkpoint"><input type="checkbox" data-checkpoint="hard-tutorial"><span><strong>Open the manual tutorial</strong><span>Use <a href="manual-tutorial.html">manual-tutorial.html</a>; it maps one action to each real browserfilm frame.</span></span></label>
      <label class="checkpoint"><input type="checkbox" data-checkpoint="hard-parity"><span><strong>Match reviewed components</strong><span>Use the exact manual instructions, knowledge, skills, and reviewed model.</span></span></label>
      <label class="checkpoint"><input type="checkbox" data-checkpoint="hard-cases"><span><strong>Replay manual Preview evidence</strong><span>Compare only with recorded case identifiers and screenshots; do not invent missing proof.</span></span></label>
      <label class="checkpoint"><input type="checkbox" data-checkpoint="hard-draft"><span><strong>Record the explicit Draft gate</strong><span>Do not choose Publish. The manual duplicate remains Draft and is not published.</span></span></label>
      <p>{manual_link}</p>
    </section>

    <section class="card">
      <h2>Raw resources</h2>
      <ul class="resource-list">
        {quest_resources(ctx, resources)}
      </ul>
      <p><a href="export-manifest.json">Open the complete raw resource manifest</a> · <a href="exports/{html.escape(ctx.slug)}-source.zip">Download the source bundle</a></p>
    </section>
  </main>
  <script>
    (() => {{
      const modeKey = "aibast:{html.escape(ctx.slug)}:quest-mode";
      const easyLaneKey = "aibast:{html.escape(ctx.slug)}:easy-lane";
      const progressKey = "aibast:{html.escape(ctx.slug)}:quest-progress";
      const buttons = Array.from(document.querySelectorAll("[data-mode]"));
      const paths = Array.from(document.querySelectorAll("[data-path]"));
      const easyLaneButtons = Array.from(document.querySelectorAll("[data-easy-lane-button]"));
      const easyLanes = Array.from(document.querySelectorAll("[data-easy-lane]"));
      const boxes = Array.from(document.querySelectorAll("[data-checkpoint]"));
      let saved = {{}};
      try {{ saved = JSON.parse(localStorage.getItem(progressKey) || "{{}}"); }} catch (_error) {{ saved = {{}}; }}
      boxes.forEach((box) => {{
        box.checked = Boolean(saved[box.dataset.checkpoint]);
        box.addEventListener("change", () => {{
          saved[box.dataset.checkpoint] = box.checked;
          localStorage.setItem(progressKey, JSON.stringify(saved));
        }});
      }});
      function selectMode(mode) {{
        buttons.forEach((button) => button.classList.toggle("active", button.dataset.mode === mode));
        paths.forEach((path) => {{ path.hidden = path.dataset.path !== mode; }});
        localStorage.setItem(modeKey, mode);
      }}
      buttons.forEach((button) => button.addEventListener("click", () => selectMode(button.dataset.mode)));
      function selectEasyLane(lane) {{
        easyLaneButtons.forEach((button) => button.classList.toggle("active", button.dataset.easyLaneButton === lane));
        easyLanes.forEach((panel) => {{ panel.hidden = panel.dataset.easyLane !== lane; }});
        localStorage.setItem(easyLaneKey, lane);
      }}
      easyLaneButtons.forEach((button) => button.addEventListener("click", () => selectEasyLane(button.dataset.easyLaneButton)));
      document.querySelectorAll("[data-copy-target]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const target = document.getElementById(button.dataset.copyTarget);
          if (!target) {{
            button.textContent = "Prompt missing";
            return;
          }}
          const original = button.textContent;
          navigator.clipboard.writeText(target.textContent).then(() => {{
            button.textContent = "Copied";
            window.setTimeout(() => {{ button.textContent = original; }}, 1400);
          }}).catch(() => {{
            button.textContent = "Copy failed";
          }});
        }});
      }});
      selectEasyLane(localStorage.getItem(easyLaneKey) || "brainstem");
      selectMode(localStorage.getItem(modeKey) || "easy");
    }})();
  </script>
</body>
</html>
"""


def render_screenshot_readme(ctx: JourneyContext) -> str:
    assisted = len((ctx.assisted_browserfilm or {}).get("frames", []))
    manual = len(ctx.manual_frames)
    return f"""# Screenshot evidence

Only real browser captures belong in this tree. Do not add mockups, generated
screens, recreated UI, or claims that are not visible in the evidence.

- Copilot-assisted frames recorded: {assisted}
- Literal-browser manual frames recorded: {manual}
- Manual sequence: `manual/browserfilm.json`
- Assisted sequence: `assisted/browserfilm.json` when available

All inputs and demonstrated outcomes are synthetic. These captures provide
qualitative workflow evidence, not customer KPIs or proof of a live connection.
"""


def render_film_readme(ctx: JourneyContext, mode: str) -> str:
    browserfilm = ctx.manual_browserfilm if mode == "manual" else ctx.assisted_browserfilm
    count = len((browserfilm or {}).get("frames", []))
    film = "manual-build-walkthrough.gif" if mode == "manual" else "copilot-assisted-walkthrough.gif"
    contact = "manual-build-contact-sheet.jpg" if mode == "manual" else "copilot-assisted-contact-sheet.jpg"
    label = "literal browser Hard-mode" if mode == "manual" else "Copilot-assisted Easy-mode"
    return f"""# {label.capitalize()} evidence

`browserfilm.json` is the ordered authority for {count} real browser frames.
`{film}` and `{contact}` summarize those frames when the files are present.

Do not replace a missing capture with a generated image or describe a pending
asset as evidence. The package uses synthetic inputs and qualitative language;
no frame is a customer KPI, production result, or publication approval.
"""


def render_exports_readme(ctx: JourneyContext) -> str:
    return f"""# Export bundle

Build `{ctx.slug}-source.zip` from the generated manifest:

```text
python3 tools/build_solution_export.py \\
  solutions/{ctx.slug}/export-manifest.json
```

The existing builder includes the complete solution package plus every
non-pending resource declared by the manifest. Items marked `pending_capture`
are intentionally excluded until real evidence exists.
"""


def readme_block(ctx: JourneyContext, resources: list[Resource]) -> str:
    ready = sum(resource.status == "ready" for resource in resources)
    pending = sum(resource.status != "ready" for resource in resources)
    rows = [
        ("Customer field guide", f"`solutions/{ctx.slug}/FIELD-GUIDE.md`"),
        (
            "Personless Easy-mode guide",
            f"`solutions/{ctx.slug}/EASY-MODE-PERSONLESS.md`",
        ),
        (
            "Copilot-only Easy-mode comparison",
            f"`solutions/{ctx.slug}/EASY-MODE-COPILOT-CHAT.md`",
        ),
        ("Guided Easy/Hard quest", f"`solutions/{ctx.slug}/quest.html`"),
        ("Literal browser tutorial", f"`solutions/{ctx.slug}/manual-tutorial.html`"),
        ("Raw export manifest", f"`solutions/{ctx.slug}/export-manifest.json`"),
        ("Source bundle", f"`solutions/{ctx.slug}/exports/{ctx.slug}-source.zip`"),
        ("Manual evidence", f"`solutions/{ctx.slug}/evals/manual-build-evidence.json`"),
        ("Manual browserfilm", f"`solutions/{ctx.slug}/screenshots/manual/browserfilm.json`"),
    ]
    table = "\n".join(f"| {label} | {path} |" for label, path in rows)
    status = (
        f"**Scaffold status:** {ready} resources ready; {pending} pending. "
        + (
            "Pending assets are not evidence and must not be claimed as captured."
            if pending
            else "Manual evidence and referenced screenshots passed scaffold validation."
        )
    )
    return f"""{README_START}
## Customer journey package map

| Surface | Location |
| --- | --- |
{table}

{status}

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
{README_END}"""


def update_readme(ctx: JourneyContext, resources: list[Resource]) -> None:
    path = ctx.package / "README.md"
    original = path.read_text(encoding="utf-8")
    block = readme_block(ctx, resources)
    pattern = re.compile(
        re.escape(README_START) + r".*?" + re.escape(README_END),
        re.DOTALL,
    )
    if pattern.search(original):
        updated = pattern.sub(block, original)
    else:
        updated = original.rstrip() + "\n\n" + block + "\n"
    path.write_text(updated, encoding="utf-8")


def write_outputs(ctx: JourneyContext) -> list[Resource]:
    resources = collect_resources(ctx)
    outputs = {
        ctx.package / "FIELD-GUIDE.md": render_field_guide(ctx),
        ctx.package / "EASY-MODE-PERSONLESS.md": render_personless_easy_markdown(ctx),
        ctx.package / "EASY-MODE-COPILOT-CHAT.md": render_easy_copilot_chat_markdown(ctx),
        ctx.package / "quest.html": render_quest(ctx, resources),
        ctx.package / "manual-tutorial.html": render_manual_tutorial(ctx),
        ctx.package / "export-manifest.json": render_manifest(ctx, resources),
        ctx.package / "screenshots" / "README.md": render_screenshot_readme(ctx),
        ctx.package / "screenshots" / "manual" / "README.md": render_film_readme(ctx, "manual"),
        ctx.package / "exports" / "README.md": render_exports_readme(ctx),
    }
    if (ctx.package / "screenshots" / "assisted").exists():
        outputs[ctx.package / "screenshots" / "assisted" / "README.md"] = render_film_readme(
            ctx, "assisted"
        )
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
    update_readme(ctx, resources)
    return resources


def build_export(ctx: JourneyContext) -> None:
    builder = ctx.root / "tools" / "build_solution_export.py"
    if not builder.exists():
        raise ScaffoldError(f"Export builder is missing: {builder}")
    result = subprocess.run(
        [sys.executable, str(builder), str(ctx.package / "export-manifest.json")],
        cwd=ctx.root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ScaffoldError(f"Export build failed: {detail}")
    if result.stdout.strip():
        print(result.stdout.strip())


def scaffold(
    slug: str,
    *,
    root: Path = ROOT,
    allow_pending: bool = False,
    raw_base: str = DEFAULT_RAW_BASE,
    build_bundle: bool = False,
) -> JourneyContext:
    ctx = load_context(
        root,
        slug,
        allow_pending=allow_pending,
        raw_base=raw_base,
    )
    resources = write_outputs(ctx)
    if build_bundle:
        build_export(ctx)
    ready = sum(resource.status == "ready" for resource in resources)
    pending = sum(resource.status != "ready" for resource in resources)
    print(
        f"[OK] Scaffolded solutions/{slug}: {ready} resources ready, "
        f"{pending} pending"
    )
    return ctx


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate evidence-grounded field guide, quest, manual tutorial, "
            "export manifest, screenshot READMEs, and package-map updates."
        )
    )
    parser.add_argument("slug", help="Existing solution slug under solutions/")
    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help=(
            "Generate explicit pending placeholders instead of refusing when "
            "manual evidence or referenced screenshots are incomplete."
        ),
    )
    parser.add_argument(
        "--build-export",
        action="store_true",
        help="Run tools/build_solution_export.py after scaffolding.",
    )
    parser.add_argument(
        "--raw-base",
        default=DEFAULT_RAW_BASE,
        help="Raw repository base URL used in export links.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help=argparse.SUPPRESS,
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        scaffold(
            args.slug,
            root=args.repo_root,
            allow_pending=args.allow_pending,
            raw_base=args.raw_base,
            build_bundle=args.build_export,
        )
    except ScaffoldError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
