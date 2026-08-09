#!/usr/bin/env python3
"""Scaffold evidence-grounded customer journey surfaces for a solution package."""

from __future__ import annotations

import argparse
import html
import json
import os
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

THEME_PREFERENCE_SCRIPT = """(() => {
      const key = "aibast:theme";
      const param = new URLSearchParams(window.location.search).get("scoutTheme");
      const explicit = param === "dark" || param === "light" ? param : null;
      let stored = null;
      try {
        const candidate = localStorage.getItem(key);
        stored = candidate === "dark" || candidate === "light" ? candidate : null;
      } catch (_error) {
        stored = null;
      }
      const theme = explicit || stored || "light";
      document.documentElement.setAttribute("data-theme", theme);
      document.addEventListener("DOMContentLoaded", () => {
        const button = document.querySelector("[data-theme-toggle]");
        if (!button) return;
        const render = () => {
          const dark = document.documentElement.getAttribute("data-theme") === "dark";
          button.textContent = dark ? "Use light mode" : "Use dark mode";
          button.setAttribute("aria-pressed", String(dark));
        };
        button.addEventListener("click", () => {
          const next =
            document.documentElement.getAttribute("data-theme") === "dark"
              ? "light"
              : "dark";
          document.documentElement.setAttribute("data-theme", next);
          try {
            localStorage.setItem(key, next);
          } catch (_error) {
            /* The visible theme still changes when storage is unavailable. */
          }
          render();
        });
        render();
      });
    })();"""

WORKSHOP_ENGINE_SCRIPT = """(() => {
      const engine =
        localStorage.getItem("aibast:workshop-engine") === "brainstem"
          ? "brainstem"
          : "copilot";
      document.documentElement.setAttribute("data-workshop-engine", engine);
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

AGI_PROFILE_KEY = "aibast:agi-profile:v1"
AGI_POINTS = {
    "started": 5,
    "local-proof": 15,
    "draft-builder": 20,
    "preview-proven": 25,
    "workshop-complete": 35,
    "hard-mode-complete": 50,
}
AGI_LABELS = {
    "started": "Started",
    "local-proof": "Local proof",
    "draft-builder": "Draft builder",
    "preview-proven": "Preview proven",
    "workshop-complete": "Workshop complete",
    "hard-mode-complete": "Hard mode complete",
}
WORKSHOP_MISSION = (
    "Turn motivated, open-minded, non-technical sales professionals into AI "
    "superheroes who can match the practical output and problem-solving pace "
    "of technical peers who are not using AI, while staying evidence-grounded, "
    "governed, and honest about what the tools proved."
)

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
    .topbar-actions {{ display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; }}
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
      .topbar-actions {{ justify-content: flex-start; }}
      .page {{ width: min(100% - 24px, 1120px); padding-top: 24px; }}
      .hero {{ padding: 24px 20px; }}
    }}
"""


def render_agi_runtime(slug: str) -> str:
    badges = [
        {"id": badge_id, "label": AGI_LABELS[badge_id], "points": points}
        for badge_id, points in AGI_POINTS.items()
    ]
    return (
        """
      const AGI_PROFILE_KEY = __PROFILE_KEY__;
      const AGI_WORKSHOP_SLUG = __WORKSHOP_SLUG__;
      const AGI_BADGES = Object.freeze(__BADGES__);
      const AGI_BADGE_IDS = new Set(AGI_BADGES.map((badge) => badge.id));

      function emptyAgiProfile() {
        return { score: 0, workshops: {}, updatedAt: null };
      }

      function validAgiTimestamp(value) {
        return typeof value === "string" && !Number.isNaN(Date.parse(value))
          ? value
          : null;
      }

      function agiCount(value) {
        return Number.isInteger(value) && value >= 0 ? value : 0;
      }

      function sanitizeAgiProfile(value) {
        const clean = emptyAgiProfile();
        const source =
          value && typeof value === "object" && !Array.isArray(value) ? value : {};
        const workshops =
          source.workshops && typeof source.workshops === "object"
            ? source.workshops
            : {};
        Object.entries(workshops).forEach(([key, rawWorkshop]) => {
          if (!rawWorkshop || typeof rawWorkshop !== "object") return;
          const candidate =
            typeof rawWorkshop.slug === "string" ? rawWorkshop.slug : key;
          if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(candidate)) return;
          const rawProgress =
            rawWorkshop.progress && typeof rawWorkshop.progress === "object"
              ? rawWorkshop.progress
              : {};
          const progress = {
            easyChecked: agiCount(rawProgress.easyChecked),
            easyTotal: agiCount(rawProgress.easyTotal),
            hardChecked: agiCount(rawProgress.hardChecked),
            hardTotal: agiCount(rawProgress.hardTotal),
            easyComplete: rawProgress.easyComplete === true,
            hardComplete: rawProgress.hardComplete === true,
            updatedAt: validAgiTimestamp(rawProgress.updatedAt),
          };
          const achievements = {};
          const rawAchievements =
            rawWorkshop.achievements &&
            typeof rawWorkshop.achievements === "object"
              ? rawWorkshop.achievements
              : {};
          AGI_BADGES.forEach((badge) => {
            const raw = rawAchievements[badge.id];
            const earned =
              raw === true ||
              (raw && typeof raw === "object" && raw.earned === true);
            if (earned) {
              achievements[badge.id] = {
                earned: true,
                earnedAt: validAgiTimestamp(raw?.earnedAt),
              };
            }
          });
          clean.workshops[candidate] = {
            slug: candidate,
            mode: rawWorkshop.mode === "hard" ? "hard" : "easy",
            progress,
            achievements,
          };
        });
        clean.score = Object.values(clean.workshops).reduce(
          (total, workshop) =>
            total +
            AGI_BADGES.reduce(
              (subtotal, badge) =>
                subtotal +
                (workshop.achievements[badge.id]?.earned ? badge.points : 0),
              0,
            ),
          0,
        );
        clean.updatedAt = validAgiTimestamp(source.updatedAt);
        return clean;
      }

      function readAgiProfile() {
        try {
          return sanitizeAgiProfile(
            JSON.parse(localStorage.getItem(AGI_PROFILE_KEY) || "{}"),
          );
        } catch (_error) {
          return emptyAgiProfile();
        }
      }

      function writeAgiProfile(profile) {
        const clean = sanitizeAgiProfile(profile);
        clean.updatedAt = new Date().toISOString();
        localStorage.setItem(AGI_PROFILE_KEY, JSON.stringify(clean));
        return clean;
      }

      function ensureAgiWorkshop(profile, mode = "easy") {
        if (!profile.workshops[AGI_WORKSHOP_SLUG]) {
          profile.workshops[AGI_WORKSHOP_SLUG] = {
            slug: AGI_WORKSHOP_SLUG,
            mode: mode === "hard" ? "hard" : "easy",
            progress: {
              easyChecked: 0,
              easyTotal: 0,
              hardChecked: 0,
              hardTotal: 0,
              easyComplete: false,
              hardComplete: false,
              updatedAt: null,
            },
            achievements: {},
          };
        }
        const workshop = profile.workshops[AGI_WORKSHOP_SLUG];
        workshop.mode = mode === "hard" ? "hard" : "easy";
        return workshop;
      }

      function setAgiWorkshopProgress(profile, mode, patch) {
        const workshop = ensureAgiWorkshop(profile, mode);
        workshop.progress = {
          ...workshop.progress,
          ...patch,
          updatedAt: new Date().toISOString(),
        };
        return writeAgiProfile(profile);
      }

      function awardAgi(profile, badgeId, mode = "easy") {
        if (!AGI_BADGE_IDS.has(badgeId)) {
          return { profile: sanitizeAgiProfile(profile), awarded: null };
        }
        const workshop = ensureAgiWorkshop(profile, mode);
        if (workshop.achievements[badgeId]?.earned) {
          return { profile: sanitizeAgiProfile(profile), awarded: null };
        }
        workshop.achievements[badgeId] = {
          earned: true,
          earnedAt: new Date().toISOString(),
        };
        return {
          profile: writeAgiProfile(profile),
          awarded: AGI_BADGES.find((badge) => badge.id === badgeId),
        };
      }

      function aibastSignalIssueUrl() {
        const pagesOwner = String(globalThis.location?.hostname || "")
          .match(/^([a-z0-9-]+)\\.github\\.io$/i)?.[1];
        const owner = pagesOwner || "microsoft";
        return new URL(
          `https://github.com/${owner}/aibast-agents-library/issues/new`,
        );
      }
"""
        .replace("__PROFILE_KEY__", json.dumps(AGI_PROFILE_KEY))
        .replace("__WORKSHOP_SLUG__", json.dumps(slug))
        .replace("__BADGES__", json.dumps(badges, separators=(",", ":")))
    )


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


@dataclass
class ManualTutorialContent:
    steps_markup: str
    toc_markup: str
    frame_count: int
    pending_notice: str
    gif_button: str


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScaffoldError(f"Cannot read JSON evidence {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ScaffoldError(f"Expected a JSON object in {path}")
    return value


def visual_checkpoint_document(ctx: JourneyContext) -> dict[str, Any]:
    path = ctx.package / "evals" / "visual-checkpoints.json"
    return read_json(path) if path.exists() else {}


def visual_checkpoint(
    ctx: JourneyContext,
    *,
    mode: str,
    source: str | None = None,
    case_id: str | None = None,
    step: int | None = None,
) -> dict[str, Any] | None:
    for item in visual_checkpoint_document(ctx).get("captures", []):
        if not isinstance(item, dict) or item.get("mode") != mode:
            continue
        if case_id and item.get("case_id") == case_id:
            return item
        if step is not None and item.get("step") == step:
            return item
        if source and Path(str(item.get("source", ""))).name == source:
            return item
    return None


def checkpoint_asset(ctx: JourneyContext, checkpoint: dict[str, Any], key: str) -> Path:
    value = checkpoint.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ScaffoldError(f"Reusable visual checkpoint has no {key} path")
    return resolve_repo_path(ctx.root, ctx.package, value, ctx.package / value)


def draft_visual_checkpoint(
    ctx: JourneyContext,
    source: str | None,
) -> dict[str, Any] | None:
    if not source:
        return None
    matches = [
        item
        for item in visual_checkpoint_document(ctx).get("captures", [])
        if isinstance(item, dict)
        and item.get("mode") == "easy"
        and not (
            isinstance(item.get("case_id"), str)
            and item["case_id"].strip()
        )
        and Path(str(item.get("source", ""))).name == source
    ]
    if len(matches) > 1:
        raise ScaffoldError(
            f"Multiple Draft visual checkpoints use source {source}"
        )
    return matches[0] if matches else None


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def clean_frame_label(label: str, fallback: str) -> str:
    label = re.sub(r"^\s*\d+\s*[·.:\-]\s*", "", str(label)).strip()
    return label or fallback


def contains_word(value: str, word: str) -> bool:
    return re.search(rf"\b{re.escape(word)}\b", value) is not None


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


def manual_knowledge_files(package: Path) -> list[Path]:
    manual = sorted(
        path
        for path in (package / "manual" / "knowledge").glob("*.md")
        if path.is_file()
    )
    if manual:
        return manual
    return sorted(
        path
        for path in (
            package
            / "copilot-studio"
            / "capabilities"
            / "knowledge"
            / "files"
        ).glob("*.md")
        if path.is_file()
    )


def require_foundation(root: Path, package: Path, deployment: dict[str, Any], transcripts: dict[str, Any]) -> list[str]:
    required = [
        package / "README.md",
        package / "deployment.json",
        package / "evals" / "transcripts.json",
        package / "manual" / "GLOBAL-INSTRUCTIONS.md",
        package / "manual" / "skills",
        package / "copilot-studio",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    if not manual_knowledge_files(package):
        missing.append(
            f"solutions/{package.name}/manual/knowledge/<file> or "
            "copilot-studio/capabilities/knowledge/files/<file>"
        )
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
    if contains_word(lower, "create") and contains_word(lower, "agent"):
        return "A blank Copilot Studio agent is visible in the captured Draft workspace."
    if contains_word(lower, "name"):
        return f"The page header shows the recorded manual build name: {manual_display_name(ctx)}."
    if contains_word(lower, "instruction") or contains_word(lower, "instructions"):
        return "The reviewed manual/GLOBAL-INSTRUCTIONS.md policy is visible or saved without unrecorded edits."
    if "web search" in lower:
        return "The captured inventory no longer lists the default web-search capability."
    if any(
        contains_word(lower, word)
        for word in ("inventory", "review", "audit")
    ):
        return (
            f"The screenshot visibly confirms {model_name(ctx)}, "
            f"{component_count(ctx.manual_evidence, 'skills')} rendered skills, "
            "and no tools. Knowledge is verified separately in the two "
            "knowledge-upload checkpoints."
        )
    if any(
        contains_word(lower, word)
        for word in ("knowledge", "record", "records", "rule", "rules")
    ):
        return f"The captured Knowledge inventory reflects the reviewed files; the evidence records {component_count(ctx.manual_evidence, 'knowledge_files')} knowledge sources."
    if contains_word(lower, "skill") or contains_word(lower, "skills"):
        return f"The captured skill inventory reflects the reviewed uploads; the evidence records {component_count(ctx.manual_evidence, 'skills')} skills."
    if contains_word(lower, "model") or contains_word(lower, "sonnet"):
        return f"The model picker or inventory shows {model_name(ctx)}, matching the recorded evidence."
    if contains_word(lower, "preview"):
        return "A fresh Preview surface or its recorded qualitative result is visible; only the evidence file defines a pass."
    if contains_word(lower, "draft") or contains_word(lower, "publish"):
        return "The agent remains Draft and no Publish action is taken."
    return "The captured Copilot Studio screen shows completion of this named action; make no claim beyond the screenshot."


def choose_frame_resources(ctx: JourneyContext) -> list[Path]:
    knowledge = manual_knowledge_files(ctx.package)
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
            (contains_word(lower, "skill") or contains_word(lower, "skills"))
            and any(
                contains_word(lower, verb)
                for verb in ("add", "upload", "create", "install")
            )
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
    add_resource(resources, seen, ctx, "field-guide", "Customer field guide", ctx.package / "field-guide.html", "Styled facilitation, evidence boundaries, gates, and recovery", generated=True)
    add_resource(resources, seen, ctx, "field-guide-source", "Field guide source", ctx.package / "FIELD-GUIDE.md", "Markdown source retained for audit and export", generated=True)
    visual_audit = ctx.package / "VISUAL-EVIDENCE-AUDIT.md"
    if visual_audit.exists():
        add_resource(
            resources,
            seen,
            ctx,
            "visual-evidence-audit",
            "Visual evidence audit",
            visual_audit,
            "Browser-reviewed per-screenshot findings and remediation requirements",
        )
    add_resource(
        resources,
        seen,
        ctx,
        "easy-personless-guide",
        "Personless Easy-mode guide",
        ctx.package / "EASY-MODE-PERSONLESS.md",
        "Brainstem lane skill attachment, two-message workshop, and engine loop",
        generated=True,
    )
    add_resource(
        resources,
        seen,
        ctx,
        "easy-copilot-chat-prompts",
        "Copilot-only Easy-mode comparison",
        ctx.package / "EASY-MODE-COPILOT-CHAT.md",
        "Copilot-only lane skill attachment and the same two workshop messages",
        generated=True,
    )
    for mode, label, use in (
        (
            "brainstem",
            "Brainstem Easy Mode skill",
            "Download-and-drag harness that defaults workshop execution to Brainstem",
        ),
        (
            "copilot",
            "Copilot-only Easy Mode skill",
            "Download-and-drag harness that runs the workshop directly in GitHub Copilot",
        ),
    ):
        easy_skill = easy_mode_skill_path(ctx, mode)
        if not easy_skill:
            continue
        add_resource(
            resources,
            seen,
            ctx,
            f"easy-mode-{mode}-skill",
            label,
            easy_skill,
            use,
        )
    workshop_agent = workshop_agent_path(ctx)
    if workshop_agent:
        add_resource(
            resources,
            seen,
            ctx,
            "generic-workshop-agent",
            "Generic AIBAST Workshop agent",
            workshop_agent,
            "Registry-driven Brainstem engine shared by every packaged solution",
        )
    add_resource(resources, seen, ctx, "manual-instructions", "Manual global instructions", ctx.package / "manual" / "GLOBAL-INSTRUCTIONS.md", "Reviewed instructions for literal browser construction")

    settings = ctx.package / "copilot-studio" / "settings.mcs.yml"
    sync = ctx.package / "copilot-studio" / "agent.sync.yaml"
    if settings.exists():
        add_resource(resources, seen, ctx, "settings", "Copilot Studio settings", settings, "Easy-mode agent settings and instruction copy")
    if sync.exists():
        add_resource(resources, seen, ctx, "agent-sync", "Copilot Studio component manifest", sync, "Easy-mode component synchronization")

    for path in manual_knowledge_files(ctx.package):
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
    visual_document = visual_checkpoint_document(ctx)
    for item in visual_document.get("captures", []):
        if not isinstance(item, dict):
            continue
        annotated = item.get("annotated")
        if item.get("status") != "reusable" or not isinstance(annotated, str):
            continue
        annotated_path = ctx.root / annotated
        add_resource(
            resources,
            seen,
            ctx,
            resource_id("annotated-evidence", annotated_path),
            f"Annotated visual checkpoint: {item.get('id', annotated_path.stem)}",
            annotated_path,
            "Positive deterministic evidence highlighted for learner verification",
        )
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
        ("workshop-settings", "Global workshop settings", ctx.root / "solutions" / "_shared" / "workshop-settings.html", "Site-wide persisted Easy-mode harness preference"),
        ("evidence-report", "Styled evidence report", ctx.package / "evidence-report.html", "Learner-safe HTML summary of deterministic and visual evidence"),
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
                                "persona": str(
                                    case.get("persona")
                                    or transcript.get("persona")
                                    or "Workshop learner"
                                ),
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
                "persona": str(
                    transcript.get("persona") or "Workshop learner"
                ),
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
    return personless_prompts(ctx)


def workshop_agent_path(ctx: JourneyContext) -> Path | None:
    path = (
        ctx.root
        / "agents"
        / "@aibast-agents-library"
        / "templates"
        / "workshop_agent.py"
    )
    return path if path.exists() else None


def easy_mode_skill_path(
    ctx: JourneyContext,
    mode: str,
) -> Path | None:
    folder = {
        "brainstem": "aibast-easy-mode-brainstem",
        "copilot": "aibast-easy-mode-copilot",
    }.get(mode)
    if not folder:
        raise ValueError(f"Unknown Easy Mode skill: {mode}")
    path = (
        ctx.root
        / "skills"
        / folder
        / "SKILL.md"
    )
    return path if path.exists() else None


def easy_mode_solution_name(ctx: JourneyContext) -> str:
    return re.sub(r"\s+Agent$", "", ctx.title).strip()


def personless_prompts(ctx: JourneyContext) -> list[tuple[str, str]]:
    solution = easy_mode_solution_name(ctx)
    return [
        (
            "2. Build and test the solution",
            (
                f"Give me {solution} using Easy Mode and test it for me."
            ),
        ),
        (
            "3. Deploy the validated Draft",
            "Deploy it into Copilot Studio for me.",
        ),
    ]


def render_personless_easy_markdown(ctx: JourneyContext) -> str:
    skill = easy_mode_skill_path(ctx, "brainstem")
    workshop_agent = workshop_agent_path(ctx)
    skill_link = (
        ctx.raw(ctx.rel(skill)) if skill else "AIBAST Easy Mode skill pending"
    )
    workshop_agent_link = (
        ctx.raw(ctx.rel(workshop_agent))
        if workshop_agent
        else "Generic workshop agent pending"
    )
    prompts = "\n\n".join(
        f"## {title}\n\n```text\n{prompt}\n```"
        for title, prompt in personless_prompts(ctx)
    )
    return f"""# {ctx.title} — personless Easy mode

## 1. Attach the Brainstem skill

Download [{skill.name if skill else "SKILL.md"}]({skill_link}), open GitHub
Copilot Chat in VS Code, select **Agent mode**, and drag `SKILL.md` into the
chat. This skill fixes the lane to Brainstem and owns startup, agent
acquisition, testing, deployment, browser validation, and the final verdict.

Brainstem is the learner's personal, on-device training AI. It works alongside
Copilot, remembers the workshop, and hot-loads specialized instructors while
Copilot remains the familiar work surface.

Then send these two short messages:

{prompts}

## What pulls the harness

1. The attached skill starts the installed Brainstem, finds
   `@aibast-agents-library/workshop` in the AIBAST registry, and imports it
   through `/agents/import`.
2. `AIBASTWorkshopAgent` resolves the named solution from `registry.json`,
   retrieves its standard package, and hot-loads and tests the business agent.
3. The same generic engine remembers the active solution, so “Deploy it” runs
   the validated Draft flow without the attendee repeating URLs or context.
4. Copilot executes any real front-door handoff returned by Brainstem, sends
   the captured Preview evidence back, and continues until Brainstem returns
   `status: complete`.
5. The final gate requires **Draft** and `published: false`.

Generic workshop engine: {workshop_agent_link}

The person sets the destination and reads the
verdict; Brainstem + Copilot pull the harness.
"""


def render_easy_copilot_chat_markdown(ctx: JourneyContext) -> str:
    skill = easy_mode_skill_path(ctx, "copilot")
    skill_link = (
        ctx.raw(ctx.rel(skill)) if skill else "AIBAST Easy Mode skill pending"
    )
    sections = "\n\n".join(
        f"## {title}\n\n```text\n{prompt}\n```"
        for title, prompt in easy_copilot_chat_prompts(ctx)
    )
    return f"""# {ctx.title} — GitHub Copilot Easy mode

## 1. Attach the Copilot-only skill

Download [{skill.name if skill else "SKILL.md"}]({skill_link}), open GitHub
Copilot Chat in VS Code, select **Agent mode**, and drag `SKILL.md` into the
chat.

The attached skill carries the discovery, testing, deployment, and validation
harness directly in GitHub Copilot, so the attendee still uses the same short
messages instead of supplying URLs or mechanics. Before deployment it installs
and verifies the official `microsoft/copilot-studio-plugin`, its
`mcs-assistant@copilot-studio-plugin` capabilities, and a supported PAC CLI.

Then send these two short messages:

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

## Workshop mission

{WORKSHOP_MISSION}

## Evidence boundary

- All packaged records and outcomes are synthetic.
- Recorded cases provide qualitative workflow evidence only.
- They are not customer KPIs, measured production results, forecasts,
  commitments, or proof of a live system connection.
- A screenshot proves only the visible state in that frame.
- No image, GIF, transcript, connector result, or publication state is implied
  unless the corresponding file is present in `export-manifest.json`.

## Easy mode — GitHub Copilot (default)

1. Open GitHub Copilot Chat in VS Code and select **Agent mode**.
2. Download `skills/aibast-easy-mode-copilot/SKILL.md` and drag it into the
   chat.
3. Open `EASY-MODE-COPILOT-CHAT.md`.
4. Send its two short messages in order: build and test the named solution,
   then deploy the validated Draft.
5. The skill installs and verifies the official Microsoft Copilot Studio
   plugin and supported PAC CLI, then performs discovery, testing, deployment,
   and Preview validation directly through GitHub Copilot.
6. Stop at **Draft**. Publishing remains a separate human approval gate.

## Easy mode — GitHub Copilot + Brainstem (optional)

Brainstem is the learner's personal, on-device training AI working alongside
GitHub Copilot. Copilot stays the familiar work surface; Brainstem remembers
the workshop and hot-loads the specialized instructors.

Download `skills/aibast-easy-mode-brainstem/SKILL.md`, drag it into Copilot
Chat, open `EASY-MODE-PERSONLESS.md`, and send the same two short messages.
The skill starts Brainstem, installs the generic AIBAST Workshop agent, and
continues its front-door handoffs until functional validation returns
`status: complete`.

Both lanes use the same immutable assets, locked cases, real Preview gate, and
`published: false` boundary.

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


def render_field_guide_html(ctx: JourneyContext) -> str:
    rows = "\n".join(
        f"""<tr>
          <td><code>{html.escape(str(case["case_id"]))}</code></td>
          <td>{html.escape(str(case.get("persona", "Workshop learner")))}</td>
          <td>{html.escape(str(case["prompt"]))}</td>
        </tr>"""
        for case in easy_case_records(ctx)
    )
    seams = "\n".join(
        f"<li>{html.escape(value)}</li>"
        for value in production_seams(ctx)
    )
    build_prompt, deploy_prompt = [
        prompt for _title, prompt in personless_prompts(ctx)
    ]
    brainstem_skill = easy_mode_skill_path(ctx, "brainstem")
    copilot_skill = easy_mode_skill_path(ctx, "copilot")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(ctx.title)} field guide</title>
  <script>
    {THEME_SCRIPT}
    {THEME_PREFERENCE_SCRIPT}
    {WORKSHOP_ENGINE_SCRIPT}
  </script>
  <style>
{COMMON_CSS}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    .engine-panel {{ display: none; }}
    html[data-workshop-engine="copilot"] .engine-panel.copilot {{ display: block; }}
    html[data-workshop-engine="brainstem"] .engine-panel.brainstem {{ display: block; }}
    .prompt {{ padding: 14px; border: 1px solid var(--cp-border); border-radius: 10px; background: var(--cp-surface-soft); white-space: pre-wrap; font-family: Consolas, "Courier New", Courier, monospace; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 11px; border: 1px solid var(--cp-border); text-align: left; vertical-align: top; }}
    th {{ background: var(--cp-surface-soft); }}
    .gate-list li, .seam-list li {{ margin-bottom: 8px; }}
    @media (max-width: 760px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand"><span class="brand-mark">A</span><span>AIBAST field guide</span></div>
    <div class="topbar-actions"><button class="button" type="button" data-theme-toggle aria-pressed="false">Use dark mode</button><a class="button" href="../_shared/workshop-settings.html?return=../{html.escape(ctx.slug)}/field-guide.html">Workshop settings</a><a class="button primary" href="quest.html">Back to workshop</a></div>
  </header>
  <main class="page">
    <section class="hero">
      <p class="eyebrow">Facilitator and learner guide</p>
      <h1>{html.escape(ctx.title)}</h1>
      <p class="lede">Use this guide to understand the workshop boundary, expected proof, production seams, and recovery paths before or during the hands-on module.</p>
      <div class="notice"><strong>Workshop mission:</strong> {html.escape(WORKSHOP_MISSION)}</div>
      <div class="notice"><strong>Evidence boundary:</strong> all packaged records and outcomes are synthetic qualitative evidence—not customer KPIs, measured production results, live connections, or publication approval.</div>
    </section>

    <h2>Use your configured Easy-mode harness</h2>
    <section class="engine-panel copilot card">
      <h3>GitHub Copilot only</h3>
      <p>Attach the Copilot-only skill. It carries discovery, local testing, Draft deployment, and Preview validation directly in the active Copilot session.</p>
      <p><a class="button primary" href="../../{html.escape(ctx.rel(copilot_skill))}" download="SKILL.md">Download Copilot-only SKILL.md</a></p>
      <div class="prompt">{html.escape(build_prompt)}</div>
      <div class="prompt">{html.escape(deploy_prompt)}</div>
    </section>
    <section class="engine-panel brainstem card">
      <h3>GitHub Copilot + Brainstem</h3>
      <p>Attach the Brainstem skill. Copilot remains the work surface while the personal, on-device training AI persists the workshop and executes the generic engine handoffs.</p>
      <p><a class="button primary" href="../../{html.escape(ctx.rel(brainstem_skill))}" download="SKILL.md">Download Brainstem SKILL.md</a></p>
      <div class="prompt">{html.escape(build_prompt)}</div>
      <div class="prompt">{html.escape(deploy_prompt)}</div>
    </section>

    <h2>Locked Preview corpus</h2>
    <section class="card">
      <p>Run every case in a fresh Copilot Studio Preview conversation. The deterministic validator—not phrasing similarity—defines the complete pass.</p>
      <table>
        <thead><tr><th>Case</th><th>Persona</th><th>Prompt</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>

    <div class="grid">
      <section class="card">
        <h2>Production replacement seams</h2>
        <ul class="seam-list">{seams}</ul>
        <p>The pilot must never claim a live lookup or external write unless an approved production tool returns evidence that it succeeded.</p>
      </section>
      <section class="card">
        <h2>Evidence gates</h2>
        <ul class="gate-list">
          <li><strong>Source:</strong> deployment source and isolated transcripts exist.</li>
          <li><strong>Local:</strong> every locked business-agent case passes.</li>
          <li><strong>Preview:</strong> every front-door case passes in a fresh chat.</li>
          <li><strong>Visual:</strong> only approved annotated checkpoints count as proof; review-required captures may appear only as clearly labeled orientation references.</li>
          <li><strong>Draft:</strong> the package records <code>published: false</code>.</li>
          <li><strong>Customer:</strong> governance, telemetry, support, and success measures are agreed before production.</li>
        </ul>
      </section>
    </div>

    <h2>Failure recovery</h2>
    <section class="card">
      <table>
        <thead><tr><th>Symptom</th><th>Recovery</th></tr></thead>
        <tbody>
          <tr><td>A required source is missing</td><td>Stop. Restore the reviewed file; never substitute invented content.</td></tr>
          <tr><td>Knowledge is still processing</td><td>Wait for ingestion before Preview. A partial answer is not evidence.</td></tr>
          <tr><td>A case misses a marker</td><td>Keep the case failed and inspect the package. Never retry until it happens to pass.</td></tr>
          <tr><td>The existing Draft is found</td><td>The harness should clone and reconnect automatically.</td></tr>
          <tr><td>The agent appears Published</td><td>Stop immediately. This workshop ends at Draft.</td></tr>
        </tbody>
      </table>
    </section>

    <p><a class="button primary" href="quest.html">Start the workshop</a> <a class="button" href="manual-tutorial.html">Open Hard mode directly</a></p>
  </main>
</body>
</html>
"""


def render_evidence_report_html(ctx: JourneyContext) -> str:
    document = visual_checkpoint_document(ctx)
    summary = document.get("summary", {})
    captures = [
        item
        for item in document.get("captures", [])
        if isinstance(item, dict)
    ]
    reusable_rows = "\n".join(
        f"""<tr>
          <td><code>{html.escape(str(item.get("id", "")))}</code></td>
          <td>{html.escape(str(item.get("mode", "")))}</td>
          <td>{html.escape("; ".join(str(value) for value in item.get("visible_anchors", [])))}</td>
          <td>{html.escape(str(item.get("annotated", "")))}</td>
        </tr>"""
        for item in captures
        if item.get("status") == "reusable"
    )
    gap_rows = "\n".join(
        f"""<tr>
          <td><code>{html.escape(str(item.get("id", "")))}</code></td>
          <td>{html.escape(str(item.get("mode", "")))}</td>
          <td>{html.escape(str(item.get("source", "")))}</td>
          <td>{html.escape(str(item.get("reason", "")))}</td>
        </tr>"""
        for item in captures
        if item.get("status") == "reshoot_required"
    )
    case_rows = "\n".join(
        f"""<tr>
          <td><code>{html.escape(str(case["case_id"]))}</code></td>
          <td>{marker_chips(case.get("must_include", []), "Reviewed evidence")}</td>
          <td>{marker_chips(case.get("must_not_include", []), "No unsupported side effect")}</td>
        </tr>"""
        for case in easy_case_records(ctx)
    )
    visual_audit = ctx.package / "VISUAL-EVIDENCE-AUDIT.md"
    audit_download = (
        f'<a class="button" href="{html.escape(visual_audit.name)}" download>Download detailed audit source</a>'
        if visual_audit.exists()
        else ""
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(ctx.title)} evidence report</title>
  <script>
    {THEME_SCRIPT}
    {THEME_PREFERENCE_SCRIPT}
  </script>
  <style>
{COMMON_CSS}
    .summary-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin: 20px 0; }}
    .summary-grid article {{ padding: 18px; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); }}
    .summary-grid strong, .summary-grid span {{ display: block; }}
    .summary-grid strong {{ font-size: 28px; color: var(--cp-accent); }}
    .summary-grid span {{ color: var(--cp-text-muted); }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 11px; border: 1px solid var(--cp-border); text-align: left; vertical-align: top; }}
    th {{ background: var(--cp-surface-soft); }}
    .marker-chip {{ display: inline-flex; margin: 0 6px 6px 0; padding: 5px 8px; border: 1px solid var(--cp-border); border-radius: 999px; background: var(--cp-surface-soft); color: var(--cp-text-muted); font-size: 12px; }}
    .downloads {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    @media (max-width: 760px) {{ .summary-grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand"><span class="brand-mark">A</span><span>AIBAST evidence report</span></div>
    <div class="topbar-actions"><button class="button" type="button" data-theme-toggle aria-pressed="false">Use dark mode</button><a class="button primary" href="quest.html">Back to workshop</a></div>
  </header>
  <main class="page">
    <section class="hero">
      <p class="eyebrow">Workshop evidence</p>
      <h1>{html.escape(ctx.title)}</h1>
      <p class="lede">This report separates the deterministic machine gate from learner-facing visual checkpoints. A screenshot can support a positive observation; it never replaces the full locked-case validation.</p>
    </section>

    <div class="summary-grid">
      <article><strong>{html.escape(str(summary.get("reusable", 0)))}</strong><span>Reusable positive checkpoints</span></article>
      <article><strong>{html.escape(str(summary.get("reshoot_required", 0)))}</strong><span>Reference-only captures excluded from learner proof</span></article>
      <article><strong>{html.escape(str(summary.get("new_learn_step_captures_recommended", 0)))}</strong><span>Optional future Learn-step captures</span></article>
    </div>

    <h2>Deterministic case contract</h2>
    <section class="card" id="locked-cases">
      <table>
        <thead><tr><th>Case</th><th>Must include</th><th>Must not claim</th></tr></thead>
        <tbody>{case_rows}</tbody>
      </table>
    </section>

    <h2>Displayed visual checkpoints</h2>
    <section class="card">
      <p>Only approved positive checkpoints count as learner proof. Annotated paths are included for facilitator traceability.</p>
      <table>
        <thead><tr><th>Checkpoint</th><th>Mode</th><th>Visible evidence</th><th>Annotated asset</th></tr></thead>
        <tbody>{reusable_rows}</tbody>
      </table>
    </section>

    <h2>Reference-only visual gaps</h2>
    <section class="card">
      <p>These real source captures are inventoried for facilitators but withheld from learner pages until their review or reshoot requirement is resolved.</p>
      <table>
        <thead><tr><th>Checkpoint</th><th>Mode</th><th>Source asset</th><th>Reason</th></tr></thead>
        <tbody>{gap_rows}</tbody>
      </table>
    </section>

    <h2>Downloads for audit</h2>
    <section class="card downloads">
      <a class="button" href="evals/transcripts.json" download>Download locked transcripts</a>
      <a class="button" href="evals/visual-checkpoints.json" download>Download visual checkpoint contract</a>
      <a class="button" href="export-manifest.json" download>Download export manifest</a>
      <a class="button" href="exports/{html.escape(ctx.slug)}-source.zip" download>Download portable bundle</a>
      {audit_download}
    </section>
  </main>
</body>
</html>
"""


def raw_link(ctx: JourneyContext, path: Path) -> str:
    return ctx.raw(ctx.rel(path))


def page_relative_path(ctx: JourneyContext, path: Path) -> str:
    return Path(
        os.path.relpath(path.resolve(), start=ctx.package.resolve())
    ).as_posix()


def manual_copy_payload(
    ctx: JourneyContext,
    action: str,
    filename: str,
) -> tuple[str, str] | None:
    case = case_for_frame(ctx, filename)
    if case:
        prompt = case.get("prompt")
        if not isinstance(prompt, str):
            case_id = case.get("case_id")
            prompt = next(
                (
                    item.get("prompt")
                    for item in ctx.transcripts.get("transcripts", [])
                    if isinstance(item, dict)
                    and item.get("case_id") == case_id
                    and isinstance(item.get("prompt"), str)
                ),
                None,
            )
        if isinstance(prompt, str):
            return "Copy Preview prompt", prompt
    lower = action.lower()
    if "name" in lower and "agent" not in lower:
        return "Copy agent name", manual_display_name(ctx)
    if "name " in lower or lower.startswith("name"):
        return "Copy agent name", manual_display_name(ctx)
    if "enter" in lower and "instruction" in lower:
        instructions = (
            ctx.package / "manual" / "GLOBAL-INSTRUCTIONS.md"
        ).read_text(encoding="utf-8")
        return "Copy instructions", instructions
    return None


def render_manual_tutorial(
    ctx: JourneyContext,
    *,
    content_only: bool = False,
) -> str | ManualTutorialContent:
    resources = choose_frame_resources(ctx)
    step_cards = []
    toc_links = []
    for index, frame in enumerate(ctx.manual_frames, 1):
        filename = str(frame.get("file", ""))
        action = clean_frame_label(str(frame.get("label", "")), f"Review frame {index}")
        expected = expected_result(ctx, action, filename)
        copy_payload = manual_copy_payload(
            ctx,
            action,
            filename,
        )
        copy_id = f"hard-copy-{index}"
        copy_markup = (
            f'<button class="button copy-button" type="button" data-copy-target="{copy_id}">{html.escape(copy_payload[0])}</button>'
            f'<pre class="copy-source" id="{copy_id}" hidden>{html.escape(copy_payload[1])}</pre>'
            if copy_payload
            else ""
        )
        case = case_for_frame(ctx, filename)
        preview_reset = (
            '<div class="look-for"><strong>Before this case</strong>'
            f'<p>Open Preview in a fresh conversation before running '
            f'{html.escape(str(case.get("case_id", "this locked case")))}. '
            "A previous response must not influence the evidence.</p></div>"
            if case
            else ""
        )
        screenshot = ctx.manual_browserfilm_path.parent / filename
        capture_width = (ctx.manual_browserfilm or {}).get("width", "unknown")
        capture_height = (ctx.manual_browserfilm or {}).get("height", "unknown")
        checkpoint = visual_checkpoint(
            ctx,
            mode="hard",
            source=filename,
            case_id=(
                str(case_for_frame(ctx, filename).get("case_id"))
                if case_for_frame(ctx, filename)
                else None
            ),
            step=index,
        )
        if (
            checkpoint
            and checkpoint.get("status") == "reshoot_required"
            and screenshot.exists()
        ):
            reason = str(
                checkpoint.get("reason")
                or "This capture has not been approved as visual proof."
            )
            screenshot_html = (
                '<div class="look-for withheld-checkpoint">'
                "<strong>Withheld checkpoint — reshoot required</strong>"
                "<p>The recorded screenshot is not approved for learner display "
                f"and has been withheld. Review note: {html.escape(reason)}</p>"
                f"<p><strong>Expected state:</strong> {html.escape(expected)}</p>"
                "<p>Continue only when the visible product state and the "
                "deterministic gate agree.</p></div>"
            )
        elif checkpoint and checkpoint.get("status") == "reshoot_required":
            screenshot_html = (
                '<div class="look-for withheld-checkpoint">'
                "<strong>Withheld checkpoint — reshoot required</strong>"
                "<p>The recorded screenshot is not approved for learner display "
                "and is unavailable in this package.</p>"
                f"<p><strong>Expected state:</strong> {html.escape(expected)}</p>"
                "<p>Continue only when the visible product state and the "
                "deterministic gate agree.</p></div>"
            )
        elif checkpoint and checkpoint.get("status") == "reusable":
            annotated = checkpoint_asset(ctx, checkpoint, "annotated")
            annotated_url = page_relative_path(ctx, annotated)
            original = checkpoint_asset(ctx, checkpoint, "source")
            original_url = page_relative_path(ctx, original)
            anchors = "; ".join(
                str(value) for value in checkpoint.get("visible_anchors", [])
            )
            screenshot_html = (
                f'<a class="shot-link" href="{html.escape(annotated_url)}" download="{html.escape(annotated.name)}">'
                f'<img class="shot" data-evidence-status="reusable" src="{html.escape(annotated_url)}" '
                f'alt="{html.escape(action)} annotated evidence" loading="lazy"></a>'
                f'<p class="capture-meta">Positive visual checkpoint: {html.escape(anchors)}. '
                f"Source capture: {html.escape(str(capture_width))}×{html.escape(str(capture_height))} JPEG. "
                "The full pass remains the deterministic machine gate. "
                f'<a href="{html.escape(original_url)}" download="{html.escape(original.name)}">Download original</a>.</p>'
            )
        elif screenshot.exists():
            screenshot_html = (
                f'<a class="shot-link" href="screenshots/manual/{html.escape(filename)}" download="{html.escape(filename)}">'
                f'<img class="shot" src="screenshots/manual/{html.escape(filename)}" '
                f'alt="{html.escape(action)} evidence" loading="lazy"></a>'
                f'<p class="capture-meta">Source capture: {html.escape(str(capture_width))}×{html.escape(str(capture_height))} JPEG. Shown without browser upscaling. Download the original to inspect at 100%.</p>'
            )
        else:
            screenshot_html = (
                '<div class="missing">Evidence pending. No screenshot is shown and '
                "this action must not be claimed as captured.</div>"
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
        <header><span>{index}</span><div><h3>{html.escape(action)}</h3><p>Step {index} of {len(ctx.manual_frames)}</p></div>{report_button(ctx, location=f"Hard mode — step {index}: {action}", expected=expected, evidence=ctx.rel(screenshot))}</header>
        <div class="step-body">
          <div class="instruction-grid">
            <div class="instruction"><div class="instruction-heading"><strong>Action</strong>{copy_markup}</div><span>{html.escape(action)}</span></div>
            <div class="instruction expected"><strong>Expected result</strong>{html.escape(expected)}</div>
          </div>
          {preview_reset}
          {screenshot_html}
          <footer>
            <a href="{html.escape(page_relative_path(ctx, source))}" download>Download source: {html.escape(source_label)}</a>
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
    hard_checkpoints = [
        item
        for item in visual_checkpoint_document(ctx).get("captures", [])
        if isinstance(item, dict) and item.get("mode") == "hard"
    ]
    manual_film_approved = (
        manual_gif.exists()
        and bool(hard_checkpoints)
        and all(item.get("status") == "reusable" for item in hard_checkpoints)
    )
    gif_button = (
        '<a class="button" href="screenshots/manual/manual-build-walkthrough.gif">Watch the manual film</a>'
        if manual_film_approved
        else ""
    )
    content = ManualTutorialContent(
        steps_markup=steps_markup,
        toc_markup=toc_markup,
        frame_count=frame_count,
        pending_notice=pending_notice,
        gif_button=gif_button,
    )
    if content_only:
        return content
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Build {html.escape(ctx.title)} manually</title>
  <script>
    {THEME_SCRIPT}
    {THEME_PREFERENCE_SCRIPT}
  </script>
  <style>
{COMMON_CSS}
    .layout {{ display: grid; grid-template-columns: 270px minmax(0, 840px); gap: 32px; max-width: 1180px; margin: 0 auto; padding: 32px 24px 80px; }}
    .sidebar {{ position: sticky; top: 82px; align-self: start; max-height: calc(100vh - 104px); overflow: auto; }}
    .toc {{ display: grid; gap: 4px; margin-top: 14px; }}
    .toc a {{ padding: 7px 9px; border-left: 3px solid var(--cp-border); color: var(--cp-text-muted); text-decoration: none; font-size: 13px; }}
    .toc a:hover {{ border-left-color: var(--cp-accent); color: var(--cp-text); }}
    .step {{ scroll-margin-top: 90px; margin: 0 0 28px; overflow: hidden; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); }}
    .step header {{ display: grid; grid-template-columns: 36px 1fr auto; gap: 14px; align-items: center; padding: 20px 22px; border-bottom: 1px solid var(--cp-border); }}
    .step header > span {{ display: grid; width: 36px; height: 36px; place-items: center; border-radius: 10px; background: var(--cp-accent-soft); color: var(--cp-accent); font-weight: 800; }}
    .step h3, .step header p {{ margin: 0; }}
    .step header p {{ color: var(--cp-text-muted); font-size: 13px; }}
    .step-body {{ padding: 22px; }}
    .instruction-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 18px; }}
    .instruction {{ padding: 14px; border-radius: 10px; background: var(--cp-surface-soft); }}
    .instruction strong {{ display: block; margin-bottom: 6px; }}
    .instruction-heading {{ display: flex; align-items: start; justify-content: space-between; gap: 10px; margin-bottom: 6px; }}
    .instruction-heading strong {{ margin: 0; }}
    .copy-button {{ min-height: 34px; padding: 6px 10px; font-size: 13px; }}
    .copy-source {{ display: none; }}
    .instruction.expected {{ border-left: 4px solid var(--cp-success); }}
    .shot-link {{ display: block; text-align: center; }}
    .shot {{ display: block; width: auto; max-width: 100%; height: auto; margin: 0 auto; border: 1px solid var(--cp-border); border-radius: 10px; image-rendering: auto; }}
    .capture-meta {{ margin: 8px 0 0; color: var(--cp-text-muted); font-size: 12px; text-align: center; }}
    .reference-shot-wrap {{ margin: 16px 0; }}
    .quality-warning {{ margin: 10px 0 0; padding: 14px; border-left: 4px solid var(--cp-warning); background: var(--cp-surface-soft); color: var(--cp-text-muted); text-align: left; }}
    .quality-warning strong {{ color: var(--cp-text); }}
    .missing {{ padding: 32px; border: 2px dashed var(--cp-warning); border-radius: 10px; color: var(--cp-text-muted); }}
    .look-for {{ padding: 20px; border-left: 4px solid var(--cp-accent); border-radius: 10px; background: var(--cp-surface-soft); color: var(--cp-text-muted); }}
    .look-for strong {{ color: var(--cp-text); }}
    .look-for p {{ margin: 8px 0 0; }}
    .report-button {{ border-color: var(--cp-accent); color: var(--cp-accent); }}
    .feedback-notice {{ margin-top: 14px; padding: 14px; border-left: 4px solid var(--cp-accent); border-radius: 10px; background: var(--cp-surface-soft); color: var(--cp-text-muted); }}
    .step footer {{ display: flex; justify-content: space-between; gap: 12px; margin-top: 16px; flex-wrap: wrap; }}
    .agi-manual-note {{ margin-top: 10px; color: var(--cp-text-muted); font-size: 13px; }}
    .troubleshooting details {{ padding: 14px 0; border-bottom: 1px solid var(--cp-border); }}
    summary {{ cursor: pointer; font-weight: 700; }}
    @media (max-width: 900px) {{ .layout {{ grid-template-columns: 1fr; }} .sidebar {{ position: static; max-height: none; }} }}
    @media (max-width: 620px) {{ .instruction-grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand"><span class="brand-mark">A</span><span>AIBAST manual workshop</span></div>
    <div class="topbar-actions"><button class="button" type="button" data-theme-toggle aria-pressed="false">Use dark mode</button>{gif_button} <a class="button primary" href="exports/{html.escape(ctx.slug)}-source.zip">Download source bundle</a></div>
  </header>
  <div class="layout">
    <aside class="sidebar">
      <strong id="progress-label">0 of {frame_count} complete</strong>
      <div class="progress"><span id="progress-bar"></span></div>
      <p class="agi-manual-note">Hard-mode progress earns self-paced local Agent Growth &amp; Impact points on this device.</p>
      <p class="agi-manual-note" id="agi-manual-toast" role="status" aria-live="polite" aria-atomic="true"></p>
      <nav class="toc" aria-label="Tutorial actions">{toc_markup}</nav>
    </aside>
    <main>
      <section class="hero">
        <p class="eyebrow">Hard mode · literal browser construction</p>
        <h1>Build {html.escape(ctx.title)} manually.</h1>
        <p class="lede">No PAC CLI, YAML import, or plugin architect. Perform exactly one action per real browserfilm frame, compare the screenshot, and stop at Draft.</p>
        <div class="notice"><strong>Synthetic disclosure:</strong> this is qualitative workflow evidence using packaged synthetic inputs. It is not a customer KPI or a live-system result.</div>
        <div class="feedback-notice"><strong>Found something inaccurate?</strong> Use <em>Report an issue</em> on that step. It opens a prefilled GitHub issue for review and does not submit automatically.</div>
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
{render_agi_runtime(ctx.slug)}
      const key = "aibast:{html.escape(ctx.slug)}:manual-progress";
      const boxes = Array.from(document.querySelectorAll(".complete"));
      const label = document.getElementById("progress-label");
      const bar = document.getElementById("progress-bar");
      const agiToast = document.getElementById("agi-manual-toast");
      let saved = [];
      try {{
        const parsed = JSON.parse(localStorage.getItem(key) || "[]");
        saved = Array.isArray(parsed)
          ? parsed.filter((step) => typeof step === "string")
          : [];
      }} catch (_error) {{
        saved = [];
      }}
      boxes.forEach((box) => {{
        box.checked = saved.includes(box.dataset.step);
        box.addEventListener("change", update);
      }});
      function update() {{
        const done = boxes.filter((box) => box.checked).map((box) => box.dataset.step);
        const complete = boxes.length > 0 && done.length === boxes.length;
        localStorage.setItem(key, JSON.stringify(done));
        label.textContent = `${{done.length}} of ${{boxes.length}} complete`;
        bar.style.width = boxes.length ? `${{(done.length / boxes.length) * 100}}%` : "0%";
        let profile = readAgiProfile();
        if (done.length > 0 || profile.workshops[AGI_WORKSHOP_SLUG]) {{
          profile = setAgiWorkshopProgress(profile, "hard", {{
            hardChecked: done.length,
            hardTotal: boxes.length,
            hardComplete: complete,
          }});
          const badgeIds = [];
          if (done.length > 0) badgeIds.push("started");
          if (complete) badgeIds.push("hard-mode-complete");
          badgeIds.forEach((badgeId) => {{
            const result = awardAgi(profile, badgeId, "hard");
            profile = result.profile;
            if (result.awarded && agiToast) {{
              agiToast.textContent =
                `${{result.awarded.label}} earned: +${{result.awarded.points}} local achievement points.`;
            }}
          }});
        }}
      }}
      document.querySelectorAll("[data-copy-target]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const target = document.getElementById(button.dataset.copyTarget);
          if (!target) {{
            button.textContent = "Text unavailable";
            return;
          }}
          const original = button.textContent;
          navigator.clipboard.writeText(target.textContent).then(() => {{
            button.textContent = "Copied";
            window.setTimeout(() => {{
              button.textContent = original;
            }}, 1400);
          }}).catch(() => {{
            button.textContent = "Copy failed";
          }});
        }});
      }});
      document.querySelectorAll("[data-report-location]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const locationLabel = button.dataset.reportLocation || "Hard-mode step";
          const expected = button.dataset.reportExpected || "Describe the expected result.";
          const evidence = button.dataset.reportEvidence || "No evidence path supplied.";
          const title = `[Workshop feedback] {ctx.title}: ${{locationLabel}}`;
          const body = `<!-- aibast-workshop-feedback:v1 -->
## Workshop signal

- Schema: \\`aibast-workshop-feedback/1.0\\`
- Solution: \\`{ctx.deployment.get("name") or f"@aibast-agents-library/{ctx.slug}"}\\`
- Page: ${{location.href}}
- Mode: \\`hard\\`
- Location: ${{locationLabel}}
- Evidence: \\`${{evidence}}\\`

## Expected

${{expected}}

## What happened instead

Describe what was inaccurate or missing.

## Reproduction

1. Open the Hard-mode tutorial.
2. Follow the step shown above.
3. Record the visible Copilot Studio state.

> Workshop feedback report. Do not include credentials, tokens, customer data, or other sensitive information.`;
          const url = aibastSignalIssueUrl();
          url.searchParams.set("title", title);
          url.searchParams.set("body", body);
          window.open(url.toString(), "_blank", "noopener");
        }});
      }});
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
        "generic-workshop-agent",
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


def validated_pilot(ctx: JourneyContext) -> dict[str, Any]:
    studio = ctx.deployment.get("copilot_studio", {})
    if not isinstance(studio, dict):
        return {}
    pilot = studio.get("validated_pilot", {})
    return pilot if isinstance(pilot, dict) else {}


def copilot_studio_url(ctx: JourneyContext) -> str | None:
    pilot = validated_pilot(ctx)
    environment = pilot.get("environment_id")
    bot_id = pilot.get("bot_id")
    if not isinstance(environment, str) or not isinstance(bot_id, str):
        return None
    return (
        "https://copilotstudio.preview.microsoft.com/environments/"
        f"{environment}/agents/{bot_id}"
    )


def assisted_frame_for_case(
    ctx: JourneyContext,
    case_id: str,
    index: int,
) -> str | None:
    frames = [
        frame
        for frame in (ctx.assisted_browserfilm or {}).get("frames", [])
        if isinstance(frame, dict) and isinstance(frame.get("file"), str)
    ]
    expected = case_id.lower()
    for frame in frames:
        searchable = " ".join(
            [str(frame.get("file", "")), str(frame.get("label", ""))]
        ).lower()
        if expected in searchable:
            return str(frame["file"])
    case_frames = [
        frame
        for frame in frames
        if "confirm" not in str(frame.get("file", "")).lower()
        and "draft" not in str(frame.get("label", "")).lower()
    ]
    if index < len(case_frames):
        return str(case_frames[index]["file"])
    return None


def assisted_draft_frame(ctx: JourneyContext) -> str | None:
    for frame in (ctx.assisted_browserfilm or {}).get("frames", []):
        if not isinstance(frame, dict) or not isinstance(frame.get("file"), str):
            continue
        searchable = " ".join(
            [str(frame.get("file", "")), str(frame.get("label", ""))]
        ).lower()
        if "draft" in searchable or "confirm" in searchable:
            return str(frame["file"])
    return None


def marker_chips(values: Iterable[str], empty: str) -> str:
    rendered = [
        f'<span class="marker-chip">{html.escape(str(value))}</span>'
        for value in values
        if value
    ]
    return "".join(rendered) or f'<span class="marker-chip">{html.escape(empty)}</span>'


def report_button(
    ctx: JourneyContext,
    *,
    location: str,
    expected: str,
    evidence: str = "",
) -> str:
    return (
        '<button class="button report-button" type="button" '
        f'data-report-location="{html.escape(location, quote=True)}" '
        f'data-report-expected="{html.escape(expected, quote=True)}" '
        f'data-report-evidence="{html.escape(evidence, quote=True)}">'
        "Report an issue</button>"
    )


def render_lane_learning_steps(
    ctx: JourneyContext,
    lane: str,
    skill_download: str,
) -> str:
    is_brainstem = lane == "brainstem"
    prefix = "brainstem" if is_brainstem else "copilot"
    skill_title = (
        "Download and attach the Brainstem skill"
        if is_brainstem
        else "Download and attach the Copilot-only skill"
    )
    skill_explanation = (
        "This file fixes the workshop to Brainstem. Copilot remains the work "
        "surface while the learner's on-device training AI persists state, "
        "loads the generic workshop engine, and continues every handoff."
        if is_brainstem
        else "This file fixes the workshop to GitHub Copilot alone. The skill "
        "carries the same discovery, testing, deployment, and validation "
        "contract directly in the active Copilot session and bootstraps the "
        "official Microsoft Copilot Studio plugin."
    )
    local_expected = (
        "Brainstem reports the generic AIBAST Workshop Engine and "
        f"{ctx.deployment.get('expected_tool', 'the business agent')} loaded, "
        f"with {len(easy_case_records(ctx))}/{len(easy_case_records(ctx))} "
        "locked local cases passed."
        if is_brainstem
        else "Copilot reports the verified mcs-assistant plugin and PAC CLI, "
        "an isolated workspace, a verified source hash, "
        f"and {len(easy_case_records(ctx))}/{len(easy_case_records(ctx))} "
        "locked local cases passed."
    )
    build_prompt = personless_prompts(ctx)[0][1]
    deploy_prompt = personless_prompts(ctx)[1][1]
    pilot = validated_pilot(ctx)
    display_name = str(
        pilot.get("display_name")
        or ctx.deployment.get("display_name")
        or ctx.title
    )
    model = str(pilot.get("model") or model_name(ctx))
    knowledge_count = pilot.get(
        "knowledge_files",
        len(ctx.deployment.get("copilot_studio", {}).get("manual_knowledge_files", [])),
    )
    skill_count = pilot.get(
        "skills",
        ctx.deployment.get("copilot_studio", {}).get("manual_skill_count", "reviewed"),
    )
    return f"""
      <article class="learn-step" id="{prefix}-step-1">
        <header class="learn-step-header"><span>1</span><div><p>Prepare your Copilot</p><h3>{html.escape(skill_title)}</h3></div>{report_button(ctx, location=f"{lane} lane — step 1: attach skill", expected="The lane-specific SKILL.md is attached in a fresh GitHub Copilot Agent-mode chat.")}</header>
        <div class="learn-step-body">
          <p>{html.escape(skill_explanation)}</p>
          <div class="action-panel"><strong>Do this</strong><ol><li>Download the lane-specific <code>SKILL.md</code>.</li><li>Open GitHub Copilot Chat in VS Code.</li><li>Select <strong>Agent mode</strong>.</li><li>Drag the downloaded file into the chat.</li></ol>{skill_download}</div>
          <div class="expected-panel"><strong>Expected result</strong><p>The attachment appears in Copilot Chat. From this point forward, the selected skill—not extra wording in your prompts—determines which harness runs.</p></div>
          <label class="step-complete"><input type="checkbox" data-checkpoint="{prefix}-skill" data-agi-group="onboarding" data-agi-path="{prefix}"><span>I attached the correct lane skill.</span></label>
        </div>
      </article>

      <article class="learn-step" id="{prefix}-step-2">
        <header class="learn-step-header"><span>2</span><div><p>Prove the solution locally</p><h3>Ask Easy Mode to build and test {html.escape(easy_mode_solution_name(ctx))}</h3></div>{report_button(ctx, location=f"{lane} lane — step 2: local proof", expected=local_expected)}</header>
        <div class="learn-step-body">
          <p>This step proves the portable business logic before any Copilot Studio work begins. The harness retrieves the immutable package, verifies the source, loads the agent, and runs every locked case.</p>
          <div class="prompt-heading"><strong>Send this message</strong><button class="button primary" type="button" data-copy-target="{prefix}-build-prompt">Copy message</button></div>
          <pre class="prompt-block" id="{prefix}-build-prompt">{html.escape(build_prompt)}</pre>
          <div class="expected-panel"><strong>Expected result</strong><p>{html.escape(local_expected)}</p><p>Copilot should end by suggesting the next message: <code>Deploy it into Copilot Studio for me.</code></p></div>
          <label class="step-complete"><input type="checkbox" data-checkpoint="{prefix}-local" data-agi-group="local-proof" data-agi-path="{prefix}"><span>I saw every locked local case pass.</span></label>
        </div>
      </article>

      <article class="learn-step" id="{prefix}-step-3">
        <header class="learn-step-header"><span>3</span><div><p>Create the reviewed Draft</p><h3>Deploy the already-tested solution to Copilot Studio</h3></div>{report_button(ctx, location=f"{lane} lane — step 3: Draft deployment", expected=f"Draft {display_name}; model {model}; {knowledge_count} knowledge files; {skill_count} skills; published false.")}</header>
        <div class="learn-step-body">
          <p>The harness now uses the verified Microsoft Copilot Studio plugin to reuse or create the source-controlled Draft, synchronize the reviewed instructions and assets, validate the PAC project, and leave publication off.</p>
          <div class="prompt-heading"><strong>Send this message</strong><button class="button primary" type="button" data-copy-target="{prefix}-deploy-prompt">Copy message</button></div>
          <pre class="prompt-block" id="{prefix}-deploy-prompt">{html.escape(deploy_prompt)}</pre>
          <div class="expected-panel"><strong>Expected result</strong><ul><li>Draft: <code>{html.escape(display_name)}</code></li><li>Model: <code>{html.escape(model)}</code></li><li>Knowledge files: <code>{html.escape(str(knowledge_count))}</code></li><li>Skills: <code>{html.escape(str(skill_count))}</code></li><li>Status: <strong>Draft</strong>; published: <code>false</code></li></ul><p>The harness then validates the real Preview front door before returning its final verdict.</p></div>
          <label class="step-complete"><input type="checkbox" data-checkpoint="{prefix}-draft" data-agi-group="draft-builder" data-agi-path="{prefix}"><span>I saw the Draft identity and unpublished state.</span></label>
        </div>
      </article>"""


def render_preview_case_cards(ctx: JourneyContext) -> str:
    cards = []
    for index, case in enumerate(easy_case_records(ctx)):
        case_id = str(case["case_id"])
        target = f"preview-prompt-{slugify(case_id)}"
        screenshot = assisted_frame_for_case(ctx, case_id, index)
        checkpoint = visual_checkpoint(
            ctx,
            mode="easy",
            case_id=case_id,
        )
        capture_width = (ctx.assisted_browserfilm or {}).get("width", "unknown")
        capture_height = (ctx.assisted_browserfilm or {}).get("height", "unknown")
        if (
            checkpoint
            and checkpoint.get("status") == "reshoot_required"
            and screenshot
            and (ctx.package / "screenshots" / "assisted" / screenshot).is_file()
        ):
            reason = str(
                checkpoint.get("reason")
                or "This capture has not been approved as visual proof."
            )
            screenshot_html = (
                '<div class="missing withheld-checkpoint">'
                "<strong>Withheld checkpoint — reshoot required.</strong> "
                "The recorded screenshot is not approved for learner display. "
                f"Review note: {html.escape(reason)} "
                f"Expected state: the {html.escape(case_id)} response visibly "
                "matches every reviewed marker above.</div>"
            )
        elif checkpoint and checkpoint.get("status") == "reshoot_required":
            screenshot_html = (
                '<div class="missing withheld-checkpoint">'
                "<strong>Withheld checkpoint — reshoot required.</strong> "
                "The recorded screenshot is not approved for learner display. "
                f"Expected state: the {html.escape(case_id)} response visibly "
                "matches every reviewed marker above.</div>"
            )
        elif checkpoint and checkpoint.get("status") == "reusable":
            annotated = checkpoint_asset(ctx, checkpoint, "annotated")
            annotated_url = page_relative_path(ctx, annotated)
            original = checkpoint_asset(ctx, checkpoint, "source")
            original_url = page_relative_path(ctx, original)
            anchors = "; ".join(
                str(value) for value in checkpoint.get("visible_anchors", [])
            )
            screenshot_html = (
                '<div class="preview-shot-wrap">'
                f'<a href="{html.escape(annotated_url)}" download="{html.escape(annotated.name)}">'
                f'<img class="preview-shot" data-evidence-status="reusable" src="{html.escape(annotated_url)}" alt="{html.escape(case_id)} positive visual checkpoint" loading="lazy"></a>'
                f'<p class="capture-meta">Visible positive anchors: {html.escape(anchors)}. '
                "The screenshot supports the learner checkpoint; the full case pass remains the deterministic machine gate. "
                f'Source: {html.escape(str(capture_width))}×{html.escape(str(capture_height))} JPEG. '
                f'<a href="{html.escape(original_url)}" download="{html.escape(original.name)}">Download original</a>.</p></div>'
            )
        elif screenshot:
            screenshot_html = (
                f'<div class="preview-shot-wrap"><img class="preview-shot" src="screenshots/assisted/{html.escape(screenshot)}" alt="{html.escape(case_id)} passed in Copilot Studio Preview" loading="lazy">'
                f'<p class="capture-meta">Source capture: {html.escape(str(capture_width))}×{html.escape(str(capture_height))} JPEG. Shown at or below natural size. <a href="screenshots/assisted/{html.escape(screenshot)}" download="{html.escape(screenshot)}">Download original</a>.</p></div>'
            )
        else:
            screenshot_html = '<div class="missing">No assisted Preview screenshot is packaged for this case.</div>'
        card_classes = "preview-case preview-case-wide" if "<img " in screenshot_html else "preview-case"
        cards.append(
            f"""
        <article class="{card_classes}">
          <header><div><p class="prompt-kicker">{html.escape(case_id)} · {html.escape(str(case.get("persona", "Workshop learner")))}</p><h4>Confirm the expected evidence</h4></div><div class="report-actions"><button class="button" type="button" data-copy-target="{target}">Copy Preview prompt</button>{report_button(ctx, location=f"Easy Preview — {case_id}", expected=f"Must include: {', '.join(case.get('must_include', []))}; must not include: {', '.join(case.get('must_not_include', []))}", evidence=str((checkpoint or {}).get("annotated") or (checkpoint or {}).get("source") or screenshot or ""))}</div></header>
          <pre class="prompt-block" id="{target}">{html.escape(str(case["prompt"]))}</pre>
          <div class="marker-group"><strong>Must include</strong><div>{marker_chips(case.get("must_include", []), "Reviewed evidence")}</div></div>
          <div class="marker-group"><strong>Must not claim</strong><div>{marker_chips(case.get("must_not_include", []), "No unsupported side effect")}</div></div>
          {screenshot_html}
          <label class="step-complete"><input type="checkbox" data-checkpoint="preview-{html.escape(slugify(case_id))}" data-agi-group="preview-proven" data-agi-path="shared"><span>The Preview response matched this contract.</span></label>
        </article>"""
        )
    return "\n".join(cards)


def render_completion_state(ctx: JourneyContext) -> str:
    pilot = validated_pilot(ctx)
    case_total = len(easy_case_records(ctx))
    draft_frame = assisted_draft_frame(ctx)
    checkpoint = draft_visual_checkpoint(ctx, draft_frame) or visual_checkpoint(
        ctx, mode="easy", source=draft_frame
    )
    capture_width = (ctx.assisted_browserfilm or {}).get("width", "unknown")
    capture_height = (ctx.assisted_browserfilm or {}).get("height", "unknown")
    if (
        checkpoint
        and checkpoint.get("status") == "reshoot_required"
        and draft_frame
        and (ctx.package / "screenshots" / "assisted" / draft_frame).is_file()
    ):
        reason = str(
            checkpoint.get("reason")
            or "This capture has not been approved as visual proof."
        )
        screenshot = (
            '<div class="missing withheld-checkpoint">'
            "<strong>Withheld checkpoint — reshoot required.</strong> "
            "The recorded screenshot is not approved for learner display. "
            f"Review note: {html.escape(reason)} "
            "<strong>Expected state:</strong> the target agent is visibly Draft "
            "and publication remains off.</div>"
        )
    elif checkpoint and checkpoint.get("status") == "reshoot_required":
        screenshot = (
            '<div class="missing withheld-checkpoint">'
            "<strong>Withheld checkpoint — reshoot required.</strong> "
            "The recorded screenshot is not approved for learner display. "
            "<strong>Expected state:</strong> the target agent is visibly Draft "
            "and publication remains off.</div>"
        )
    elif checkpoint and checkpoint.get("status") == "reusable":
        annotated = checkpoint_asset(ctx, checkpoint, "annotated")
        annotated_url = page_relative_path(ctx, annotated)
        original = checkpoint_asset(ctx, checkpoint, "source")
        original_url = page_relative_path(ctx, original)
        screenshot = (
            '<div class="preview-shot-wrap">'
            f'<a href="{html.escape(annotated_url)}" download="{html.escape(annotated.name)}">'
            f'<img class="preview-shot" data-evidence-status="reusable" src="{html.escape(annotated_url)}" alt="Validated agent remains Draft" loading="lazy"></a>'
            f'<p class="capture-meta">Positive visual checkpoint. Source: {html.escape(str(capture_width))}×{html.escape(str(capture_height))} JPEG. '
            f'<a href="{html.escape(original_url)}" download="{html.escape(original.name)}">Download original</a>.</p></div>'
        )
    elif draft_frame:
        screenshot = (
            f'<div class="preview-shot-wrap"><img class="preview-shot" src="screenshots/assisted/{html.escape(draft_frame)}" alt="Validated agent remains Draft" loading="lazy">'
            f'<p class="capture-meta">Source capture: {html.escape(str(capture_width))}×{html.escape(str(capture_height))} JPEG. Shown at or below natural size. <a href="screenshots/assisted/{html.escape(draft_frame)}" download="{html.escape(draft_frame)}">Download original</a>.</p></div>'
        )
    else:
        screenshot = ""
    return f"""
      <section class="learn-step" id="easy-step-5">
        <header class="learn-step-header"><span>5</span><div><p>Recognize completion</p><h3>Know what “done” looks like</h3></div>{report_button(ctx, location="Easy mode — final completion verdict", expected=f"Local {case_total}/{case_total}; Preview {case_total}/{case_total}; Draft {pilot.get('display_name') or ctx.title}; published false.", evidence=str((checkpoint or {}).get("annotated") or (checkpoint or {}).get("source") or draft_frame or ""))}</header>
        <div class="learn-step-body">
          <p>The workshop is complete only when both the portable agent and the Copilot Studio front door prove the same behavior.</p>
          <div class="done-grid">
            <article><strong>Local proof</strong><span>{case_total}/{case_total} locked cases passed</span></article>
            <article><strong>Preview proof</strong><span>{case_total}/{case_total} locked cases passed</span></article>
            <article><strong>Draft identity</strong><span>{html.escape(str(pilot.get("display_name") or ctx.title))}</span></article>
            <article><strong>Model</strong><span>{html.escape(str(pilot.get("model") or model_name(ctx)))}</span></article>
            <article><strong>Inventory</strong><span>{html.escape(str(pilot.get("knowledge_files", "reviewed")))} knowledge · {html.escape(str(pilot.get("skills", "reviewed")))} skills</span></article>
            <article><strong>Publication gate</strong><span>Draft · published false</span></article>
          </div>
          {screenshot}
          <div class="expected-panel"><strong>Final expected verdict</strong><p>The harness reports <code>status: complete</code>, exact case totals, the Draft identity, and <code>published: false</code>. The module ends here; it does not offer publication.</p></div>
          <label class="step-complete"><input type="checkbox" data-checkpoint="easy-complete" data-agi-group="final-verdict" data-agi-path="shared"><span>I confirmed the final Draft verdict.</span></label>
        </div>
      </section>"""


def render_quest(ctx: JourneyContext, resources: list[Resource]) -> str:
    manual_content = render_manual_tutorial(ctx, content_only=True)
    if not isinstance(manual_content, ManualTutorialContent):
        raise ScaffoldError("Hard-mode tutorial content could not be generated")
    workshop_agent = workshop_agent_path(ctx)
    workshop_agent_link = (
        f'<a class="button" href="../../{html.escape(ctx.rel(workshop_agent))}" download>Download generic workshop agent</a>'
        if workshop_agent
        else '<span class="button" aria-disabled="true">Workshop agent pending</span>'
    )
    brainstem_skill = easy_mode_skill_path(ctx, "brainstem")
    copilot_skill = easy_mode_skill_path(ctx, "copilot")
    brainstem_skill_download = (
        f'<a class="button primary" href="../../{html.escape(ctx.rel(brainstem_skill))}" download="SKILL.md">Download Brainstem SKILL.md</a>'
        if brainstem_skill
        else '<span class="button" aria-disabled="true">Brainstem SKILL.md pending</span>'
    )
    copilot_skill_download = (
        f'<a class="button primary" href="../../{html.escape(ctx.rel(copilot_skill))}" download="SKILL.md">Download Copilot-only SKILL.md</a>'
        if copilot_skill
        else '<span class="button" aria-disabled="true">Copilot-only SKILL.md pending</span>'
    )
    studio_url = copilot_studio_url(ctx)
    studio_button = (
        f'<a class="button primary" href="{html.escape(studio_url)}" target="_blank" rel="noopener">Open the Copilot Studio Draft ↗</a>'
        if studio_url
        else '<span class="button" aria-disabled="true">Copilot Studio link unavailable</span>'
    )
    visual_audit_link = (
        '<a class="button" href="evidence-report.html">Evidence report</a>'
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(ctx.title)} workshop</title>
  <script>
    {THEME_SCRIPT}
    {THEME_PREFERENCE_SCRIPT}
    {WORKSHOP_ENGINE_SCRIPT}
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
    .easy-lane {{ display: none; }}
    html[data-workshop-engine="brainstem"] .easy-lane[data-easy-lane="brainstem"] {{ display: block; }}
    html[data-workshop-engine="copilot"] .easy-lane[data-easy-lane="copilot"] {{ display: block; }}
    .engine-label {{ display: none; color: var(--cp-accent); }}
    html[data-workshop-engine="brainstem"] .engine-label.brainstem {{ display: inline; }}
    html[data-workshop-engine="copilot"] .engine-label.copilot {{ display: inline; }}
    .engine-flow {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 18px 0; }}
    .engine-node {{ padding: 14px; border: 1px solid var(--cp-border); border-radius: 10px; background: var(--cp-surface); text-align: center; font-weight: 750; }}
    .comparison-note {{ margin: 14px 0; padding: 14px; border-left: 4px solid var(--cp-warning); background: var(--cp-surface-soft); color: var(--cp-text-muted); }}
    .skill-onboarding {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 18px; align-items: center; margin: 16px 0 8px; padding: 20px; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); }}
    .skill-onboarding h3 {{ margin: 0 0 6px; }}
    .skill-onboarding p {{ margin: 0; color: var(--cp-text-muted); }}
    .drag-target {{ margin-top: 10px; padding: 12px; border: 1px dashed var(--cp-border-strong); border-radius: 10px; background: var(--cp-surface-soft); color: var(--cp-text); font-weight: 700; }}
    .outcome-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }}
    .outcome-card {{ padding: 18px; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); }}
    .outcome-card strong {{ display: block; margin-bottom: 6px; }}
    .outcome-card p {{ margin: 0; color: var(--cp-text-muted); }}
    .facilitator-details {{ margin-top: 18px; padding: 14px; border: 1px solid var(--cp-border); border-radius: 10px; background: var(--cp-surface-soft); }}
    .facilitator-details summary {{ cursor: pointer; font-weight: 750; }}
    .facilitator-actions {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }}
    .comparison-table {{ width: 100%; margin-top: 14px; border-collapse: collapse; }}
    .comparison-table th, .comparison-table td {{ padding: 12px; border: 1px solid var(--cp-border); text-align: left; vertical-align: top; }}
    .comparison-table th {{ background: var(--cp-surface-soft); }}
    .module-summary {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 20px 0; }}
    .module-summary article {{ padding: 18px; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); }}
    .module-summary h3 {{ margin-top: 0; }}
    .module-summary ul {{ margin-bottom: 0; padding-left: 20px; }}
    .learn-step {{ margin: 22px 0; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); overflow: hidden; }}
    .learn-step-header {{ display: grid; grid-template-columns: 44px 1fr auto; gap: 14px; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--cp-border); background: var(--cp-surface-soft); }}
    .learn-step-header > span {{ display: grid; width: 40px; height: 40px; place-items: center; border-radius: 10px; background: var(--cp-accent); color: var(--cp-accent-fg); font-weight: 800; }}
    .learn-step-header p {{ margin: 0; color: var(--cp-accent); font-size: 12px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; }}
    .learn-step-header h3 {{ margin: 2px 0 0; }}
    .learn-step-body {{ padding: 20px; }}
    .action-panel, .expected-panel {{ margin: 16px 0; padding: 16px; border-radius: 10px; }}
    .action-panel {{ border: 1px solid var(--cp-border); background: var(--cp-surface-soft); }}
    .action-panel > strong, .expected-panel > strong {{ display: block; margin-bottom: 8px; }}
    .action-panel ol, .expected-panel ul {{ margin: 8px 0 12px; padding-left: 22px; }}
    .expected-panel {{ border-left: 4px solid var(--cp-success); background: var(--cp-surface-soft); }}
    .step-complete {{ display: flex; gap: 10px; align-items: center; margin-top: 14px; padding: 12px; border: 1px solid var(--cp-border); border-radius: 10px; background: var(--cp-bg-elevated); font-weight: 700; }}
    .step-complete input {{ width: 20px; height: 20px; accent-color: var(--cp-accent); }}
    .preview-intro {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; justify-content: space-between; margin-bottom: 16px; }}
    .preview-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    .preview-case {{ padding: 16px; border: 1px solid var(--cp-border); border-radius: 14px; background: var(--cp-bg-elevated); }}
    .preview-case-wide {{ grid-column: 1 / -1; }}
    .preview-case header {{ display: flex; justify-content: space-between; gap: 12px; align-items: start; }}
    .preview-case h4 {{ margin: 0; }}
    .report-actions {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }}
    .report-button {{ border-color: var(--cp-accent); color: var(--cp-accent); }}
    .feedback-notice {{ margin-top: 14px; padding: 14px; border-left: 4px solid var(--cp-accent); border-radius: 10px; background: var(--cp-surface-soft); color: var(--cp-text-muted); }}
    .agi-panel {{ display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(260px, .8fr); gap: 18px; margin: 20px 0; padding: 18px; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); }}
    .agi-panel h2, .agi-panel h3, .agi-panel p {{ margin-top: 0; }}
    .agi-panel h2 {{ margin-bottom: 4px; font-size: 20px; }}
    .agi-score-line {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px 18px; }}
    .agi-score {{ color: var(--cp-accent); font-size: 30px; font-weight: 800; }}
    .agi-badges {{ display: flex; flex-wrap: wrap; gap: 7px; margin: 12px 0; padding: 0; list-style: none; }}
    .agi-badge {{ padding: 5px 8px; border: 1px solid var(--cp-border); border-radius: 999px; background: var(--cp-surface-soft); font-size: 12px; }}
    .agi-claims {{ padding-left: 18px; border-left: 1px solid var(--cp-border); }}
    .agi-claim-actions {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .agi-claim-actions [hidden] {{ display: none; }}
    .agi-fine-print {{ margin: 10px 0 0; color: var(--cp-text-muted); font-size: 13px; }}
    .agi-toast {{ position: fixed; right: 18px; bottom: 18px; z-index: 50; max-width: 360px; padding: 12px 14px; border: 1px solid var(--cp-accent); border-radius: 10px; background: var(--cp-panel-strong); box-shadow: var(--cp-shadow); }}
    .agi-toast:empty {{ display: none; }}
    .marker-group {{ margin: 12px 0; }}
    .marker-group > strong {{ display: block; margin-bottom: 6px; }}
    .marker-chip {{ display: inline-flex; margin: 0 6px 6px 0; padding: 5px 8px; border: 1px solid var(--cp-border); border-radius: 999px; background: var(--cp-surface); color: var(--cp-text-muted); font-size: 12px; }}
    .preview-shot-wrap {{ margin-top: 14px; text-align: center; }}
    .reference-shot-wrap {{ margin-top: 14px; }}
    .preview-shot {{ display: block; width: 100%; max-width: 100%; height: auto; margin: 0 auto; border: 1px solid var(--cp-border); border-radius: 10px; image-rendering: auto; }}
    .capture-meta {{ margin: 8px 0 0; color: var(--cp-text-muted); font-size: 12px; text-align: center; }}
    .quality-warning {{ margin: 16px 0; padding: 14px; border-left: 4px solid var(--cp-warning); background: var(--cp-surface-soft); color: var(--cp-text-muted); }}
    .quality-warning strong {{ color: var(--cp-text); }}
    .done-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 16px 0; }}
    .done-grid article {{ padding: 14px; border: 1px solid var(--cp-border); border-radius: 10px; background: var(--cp-surface-soft); }}
    .done-grid strong, .done-grid span {{ display: block; }}
    .done-grid span {{ margin-top: 5px; color: var(--cp-text-muted); }}
    .troubleshooting-table {{ width: 100%; border-collapse: collapse; }}
    .troubleshooting-table th, .troubleshooting-table td {{ padding: 12px; border: 1px solid var(--cp-border); text-align: left; vertical-align: top; }}
    .troubleshooting-table th {{ background: var(--cp-surface-soft); }}
    .hard-overview {{ margin-top: 20px; }}
    .hard-overview h2 {{ margin-top: 0; }}
    .hard-actions {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }}
    .hard-progress-card {{ margin: 20px 0; padding: 18px; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); }}
    .hard-progress-heading {{ display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px 18px; align-items: baseline; margin-bottom: 10px; }}
    .hard-progress-heading p {{ margin: 0; color: var(--cp-text-muted); }}
    .hard-toc {{ display: flex; gap: 8px; margin-top: 14px; padding-bottom: 4px; overflow-x: auto; }}
    .hard-toc a {{ flex: 0 0 auto; padding: 7px 10px; border: 1px solid var(--cp-border); border-radius: 10px; background: var(--cp-surface-soft); color: var(--cp-text); text-decoration: none; font-size: 13px; }}
    .step {{ scroll-margin-top: 90px; margin: 0 0 28px; overflow: hidden; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); }}
    .step header {{ display: grid; grid-template-columns: 36px 1fr auto; gap: 14px; align-items: center; padding: 20px 22px; border-bottom: 1px solid var(--cp-border); }}
    .step header > span {{ display: grid; width: 36px; height: 36px; place-items: center; border-radius: 10px; background: var(--cp-accent-soft); color: var(--cp-accent); font-weight: 800; }}
    .step h3, .step header p {{ margin: 0; }}
    .step header p {{ color: var(--cp-text-muted); font-size: 13px; }}
    .step-body {{ padding: 22px; }}
    .instruction-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 18px; }}
    .instruction {{ padding: 14px; border-radius: 10px; background: var(--cp-surface-soft); }}
    .instruction strong {{ display: block; margin-bottom: 6px; }}
    .instruction-heading {{ display: flex; align-items: start; justify-content: space-between; gap: 10px; margin-bottom: 6px; }}
    .instruction-heading strong {{ margin: 0; }}
    .copy-button {{ min-height: 34px; padding: 6px 10px; font-size: 13px; }}
    .copy-source {{ display: none; }}
    .instruction.expected {{ border-left: 4px solid var(--cp-success); }}
    .shot-link {{ display: block; text-align: center; }}
    .shot {{ display: block; width: 100%; max-width: 100%; height: auto; margin: 0 auto; border: 1px solid var(--cp-border); border-radius: 10px; image-rendering: auto; }}
    .missing {{ padding: 32px; border: 2px dashed var(--cp-warning); border-radius: 10px; color: var(--cp-text-muted); }}
    .look-for {{ margin: 16px 0; padding: 20px; border-left: 4px solid var(--cp-accent); border-radius: 10px; background: var(--cp-surface-soft); color: var(--cp-text-muted); }}
    .look-for strong {{ color: var(--cp-text); }}
    .look-for p {{ margin: 8px 0 0; }}
    .step footer {{ display: flex; justify-content: space-between; gap: 12px; margin-top: 16px; flex-wrap: wrap; }}
    .complete {{ width: 20px; height: 20px; accent-color: var(--cp-accent); }}
    .hard-troubleshooting details {{ padding: 14px 0; border-bottom: 1px solid var(--cp-border); }}
    .prompt-card {{ margin: 16px 0; padding: 18px; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); }}
    .prompt-heading {{ display: flex; align-items: start; justify-content: space-between; gap: 16px; }}
    .prompt-heading h3 {{ margin: 0; }}
    .prompt-kicker {{ margin: 0 0 4px; color: var(--cp-accent); font-size: 12px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; }}
    .prompt-block {{ overflow-x: auto; margin: 14px 0 0; padding: 16px; border: 1px solid var(--cp-border); border-radius: 10px; background: var(--cp-surface-soft); color: var(--cp-text); white-space: pre-wrap; word-break: break-word; font-family: Consolas, "Courier New", Courier, monospace; font-size: 13px; line-height: 1.55; }}
    .resource-list {{ columns: 2; padding-left: 22px; }}
    .resource-list li {{ break-inside: avoid; margin-bottom: 10px; }}
    @media (max-width: 760px) {{ .engine-flow, .outcome-grid, .skill-onboarding, .module-summary, .preview-grid, .done-grid, .agi-panel {{ grid-template-columns: 1fr; }} .agi-claims {{ padding: 16px 0 0; border-top: 1px solid var(--cp-border); border-left: 0; }} }}
    @media (max-width: 620px) {{ .resource-list {{ columns: 1; }} .prompt-heading {{ display: block; }} .prompt-heading .button {{ margin-top: 12px; }} .instruction-grid {{ grid-template-columns: 1fr; }} .step header {{ grid-template-columns: 36px 1fr; }} .step header .report-button {{ grid-column: 1 / -1; }} }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand"><span class="brand-mark">A</span><span>AIBAST guided workshop</span></div>
    <div class="topbar-actions"><button class="button" type="button" data-theme-toggle aria-pressed="false">Use dark mode</button><a class="button" href="../_shared/workshop-settings.html?return=../{html.escape(ctx.slug)}/quest.html">Workshop settings</a><a class="button primary" href="field-guide.html">Open field guide</a></div>
  </header>
  <main class="page">
    <section class="hero">
      <p class="eyebrow">Evidence-grounded customer journey</p>
      <h1>{html.escape(ctx.title)}</h1>
      <p class="lede">Use your globally configured Easy-mode harness, or reproduce every action directly in Hard mode.</p>
      <div class="notice"><strong>Workshop mission:</strong> {html.escape(WORKSHOP_MISSION)}</div>
      <div class="notice"><strong>Boundary:</strong> synthetic qualitative evidence only—not a customer KPI, measured production result, live connection, or publication approval.</div>
      <div class="feedback-notice"><strong>Found something inaccurate?</strong> Use <em>Report an issue</em> at that point. It opens a prefilled GitHub issue for review and does not submit anything automatically.</div>
      <div class="mode-switch" role="tablist">
        <button class="mode active" data-mode="easy" role="tab">Easy</button>
        <button class="mode" data-mode="hard" role="tab">Hard</button>
      </div>
    </section>

    <section class="agi-panel" aria-labelledby="agi-panel-title">
      <div>
        <p class="eyebrow">Self-paced local achievements</p>
        <h2 id="agi-panel-title">Workshop achievements</h2>
        <div class="agi-score-line">
          <span><strong class="agi-score" id="agi-total-score">0</strong> total points</span>
          <span><strong id="agi-workshop-score">0</strong> in this workshop</span>
        </div>
        <p id="agi-progress-label">0 of 0 Easy checkpoints complete</p>
        <div class="progress" aria-hidden="true"><span id="agi-progress-bar"></span></div>
        <ul class="agi-badges" id="agi-badge-list" aria-label="Badges earned in this workshop"><li class="agi-badge">No badges yet</li></ul>
        <a href="../../achievements.html">View achievements and local profile</a>
      </div>
      <div class="agi-claims">
        <h3>Optional public verification</h3>
        <p class="agi-fine-print">These points and badges are local, self-reported workshop progress—not externally verified proof or a capability claim.</p>
        <div class="agi-claim-actions">
          <button class="button primary" type="button" data-agi-sync hidden>Sync achievements to GitHub</button>
        </div>
        <p class="agi-fine-print">This opens one prefilled progress issue containing every badge currently earned here. Nothing syncs until you submit it. Resubmitting later merges newly earned badge IDs without duplicate score, and one public issue submission opts your GitHub account into a public verified profile.</p>
      </div>
    </section>
    <div class="agi-toast" id="agi-badge-toast" role="status" aria-live="polite" aria-atomic="true"></div>

    <section class="path" data-path="easy">
      <div class="module-summary">
        <article>
          <h3>What you will learn</h3>
          <ul>
            <li>Use your globally configured Easy-mode harness.</li>
            <li>Use the lane skill to build and prove the portable agent.</li>
            <li>Deploy the reviewed solution as an unpublished Draft.</li>
            <li>Confirm the behavior yourself in Copilot Studio Preview.</li>
            <li>Recognize the evidence that means the module is complete.</li>
          </ul>
        </article>
        <article>
          <h3>Before you begin</h3>
          <ul>
            <li>Use VS Code with GitHub Copilot Chat in Agent mode.</li>
            <li>Sign in to GitHub with Copilot access.</li>
            <li>Have access to a Copilot Studio environment.</li>
            <li>Your workshop preference is saved globally; use <strong>Workshop settings</strong> to change it.</li>
            <li>Do not publish. This module ends with a validated Draft.</li>
          </ul>
        </article>
      </div>

      <h2>Easy mode <span class="engine-label copilot">— GitHub Copilot only</span><span class="engine-label brainstem">— GitHub Copilot + Brainstem</span></h2>

      <div class="easy-lane" data-easy-lane="brainstem">
        <div class="notice"><strong>Brainstem lane:</strong> Brainstem is the learner’s personal, on-device training AI working alongside Copilot. It persists the workshop, loads the generic engine, and continues every handoff.</div>
        {render_lane_learning_steps(ctx, "brainstem", brainstem_skill_download)}
      </div>

      <div class="easy-lane" data-easy-lane="copilot">
        <div class="comparison-note"><strong>Skeptic comparison — Copilot-only lane:</strong> GitHub Copilot carries the same harness directly in the active session. The skill still discovers every asset and runs every gate; there is no persistent Brainstem engine between turns.</div>
        {render_lane_learning_steps(ctx, "copilot", copilot_skill_download)}
      </div>

      <section class="learn-step" id="easy-step-4">
        <header class="learn-step-header"><span>4</span><div><p>Verify the real experience</p><h3>Confirm the Draft in Copilot Studio Preview</h3></div></header>
        <div class="learn-step-body">
          <p>The harness already runs these checks automatically. Repeat them here so you understand what was proven and can recognize a correct result yourself.</p>
          <div class="preview-intro"><ol><li>Open the validated Draft.</li><li>Select <strong>Preview</strong>.</li><li>Choose <strong>New chat</strong> before each case.</li><li>Paste the exact prompt.</li><li>Compare the answer with the required and forbidden markers.</li></ol><div>{studio_button}</div></div>
          <div class="expected-panel"><strong>Expected result</strong><p>Every case passes in a fresh Preview conversation, and the agent still appears as <strong>Draft</strong>.</p></div>
          <div class="preview-grid">
            {render_preview_case_cards(ctx)}
          </div>
        </div>
      </section>

      {render_completion_state(ctx)}

      <section class="card">
        <h3>Troubleshooting</h3>
        <table class="troubleshooting-table">
          <thead><tr><th>What you see</th><th>What it means</th><th>What to do</th></tr></thead>
          <tbody>
            <tr><td>Copilot ignores the lane</td><td>The wrong skill is attached, or the chat began before attachment.</td><td>Start a new Agent-mode chat and attach the correct lane-specific <code>SKILL.md</code> first.</td></tr>
            <tr><td>Local validation is not {len(easy_case_records(ctx))}/{len(easy_case_records(ctx))}</td><td>The portable source, package, or locked behavior does not match.</td><td>Stop. Do not deploy. Let the harness report the exact failed case and marker.</td></tr>
            <tr><td>No active Copilot Studio environment</td><td>PAC has no selected environment.</td><td>Sign in or select the intended environment, then resend the deploy message.</td></tr>
            <tr><td>The Draft already exists</td><td>The recorded schema is already in the environment.</td><td>The harness should clone and reconnect automatically. Treat an attendee choice prompt as a harness defect.</td></tr>
            <tr><td>A Preview case misses a marker</td><td>The real front door does not match the reviewed contract.</td><td>Keep the case failed. Inspect instructions and assets; do not retry until it happens to pass.</td></tr>
            <tr><td>The agent is Published</td><td>The workshop crossed its safety boundary.</td><td>Stop immediately. The module must end at Draft with <code>published: false</code>.</td></tr>
          </tbody>
        </table>
      </section>

      <details class="facilitator-details">
        <summary>Facilitator evidence and portable download</summary>
        <p>These links support audit, troubleshooting, and offline delivery. They are not learner steps.</p>
        <div class="facilitator-actions">
          <a class="button" href="field-guide.html">Field guide</a>
          <a class="button" href="evidence-report.html#locked-cases">Locked evidence</a>
          {visual_audit_link}
          <a class="button" href="export-manifest.json" download>Download audit manifest</a>
          <a class="button" href="exports/{html.escape(ctx.slug)}-source.zip" download>Download portable bundle</a>
          {workshop_agent_link}
          <a class="button" href="https://kodyw.com/the-personless-harness/" target="_blank" rel="noopener">Personless harness article ↗</a>
        </div>
      </details>
    </section>

    <section class="path" data-path="hard" hidden>
      <section class="card hard-overview">
        <p class="eyebrow">Hard mode · literal browser construction</p>
        <h2>Build {html.escape(ctx.title)} manually on this page.</h2>
        <p class="lede">No PAC CLI, YAML import, plugin architect, or nested tutorial frame. Perform one action per real browserfilm frame, compare the screenshot, and stop at Draft.</p>
        <div class="notice"><strong>Synthetic disclosure:</strong> this is qualitative workflow evidence using packaged synthetic inputs. It is not a customer KPI or a live-system result.</div>
        <div class="feedback-notice"><strong>Found something inaccurate?</strong> Use <em>Report an issue</em> on that step. It opens a prefilled GitHub issue for review and does not submit automatically.</div>
        {manual_content.pending_notice}
        <div class="hard-actions">
          <a class="button" href="manual-tutorial.html" target="_blank" rel="noopener">Open standalone Hard-mode guide ↗</a>
          <a class="button primary" href="exports/{html.escape(ctx.slug)}-source.zip">Download source bundle</a>
        </div>
      </section>

      <section class="hard-progress-card" aria-labelledby="hard-progress-label">
        <div class="hard-progress-heading">
          <strong id="hard-progress-label">0 of {manual_content.frame_count} complete</strong>
          <p>Hard-mode progress is saved on this device and contributes to the same achievement profile.</p>
        </div>
        <div class="progress" aria-hidden="true"><span id="hard-progress-bar"></span></div>
        <p class="muted" id="hard-progress-toast" role="status" aria-live="polite" aria-atomic="true"></p>
        <nav class="hard-toc" aria-label="Hard-mode tutorial actions">{manual_content.toc_markup}</nav>
      </section>

      <h2>Build and verify</h2>
      {manual_content.steps_markup}

      <h2 id="hard-troubleshooting">Hard-mode troubleshooting</h2>
      <section class="card hard-troubleshooting">
        <details open><summary>A screenshot or browserfilm frame is missing</summary><p>Stop. Do not invent, recreate, or substitute an image. Capture the real frame, update the browserfilm manifest, and regenerate without <code>--allow-pending</code>.</p></details>
        <details><summary>A knowledge file is still processing</summary><p>Wait for ingestion to finish before Preview. A partial answer is not evidence.</p></details>
        <details><summary>A skill upload fails</summary><p>Use the linked raw <code>SKILL.md</code>. Fix the reviewed source deliberately; do not silently skip the action.</p></details>
        <details><summary>The model differs from Easy mode</summary><p>Record the substitution and stop the parity claim until Easy and Hard use the same reviewed model.</p></details>
        <details><summary>The Preview answer misses an identifier</summary><p>Mark the recorded case failed, inspect instructions and inventory, then replay the exact prompt in a fresh conversation.</p></details>
        <details><summary>Should I publish?</summary><p>No. Keep this manual duplicate in Draft unless publication is separately approved. Do not choose Publish as part of this tutorial.</p></details>
      </section>
    </section>

  </main>
  <script>
    (() => {{
{render_agi_runtime(ctx.slug)}
      const AGI_CANONICAL_AGENT = {json.dumps(str(ctx.deployment.get("name") or f"@aibast-agents-library/{ctx.slug}"))};
      const AGI_SYNC_ORDER = Object.freeze([
        {{ localId: "started", claimId: "started" }},
        {{ localId: "local-proof", claimId: "local-proof" }},
        {{ localId: "draft-builder", claimId: "draft-builder" }},
        {{ localId: "preview-proven", claimId: "preview-proven" }},
        {{ localId: "workshop-complete", claimId: "workshop-completed" }},
        {{ localId: "hard-mode-complete", claimId: "hard-mode-completed" }},
      ]);
      const modeKey = "aibast:{html.escape(ctx.slug)}:quest-mode";
      const globalEngineKey = "aibast:workshop-engine";
      const progressKey = "aibast:{html.escape(ctx.slug)}:quest-progress";
      const hardProgressKey = "aibast:{html.escape(ctx.slug)}:manual-progress";
      const buttons = Array.from(document.querySelectorAll("[data-mode]"));
      const paths = Array.from(document.querySelectorAll("[data-path]"));
      const boxes = Array.from(document.querySelectorAll("[data-checkpoint]"));
      const hardBoxes = Array.from(document.querySelectorAll(".complete[data-step]"));
      const agiTotalScore = document.getElementById("agi-total-score");
      const agiWorkshopScore = document.getElementById("agi-workshop-score");
      const agiProgressLabel = document.getElementById("agi-progress-label");
      const agiProgressBar = document.getElementById("agi-progress-bar");
      const agiBadgeList = document.getElementById("agi-badge-list");
      const agiToast = document.getElementById("agi-badge-toast");
      const hardProgressLabel = document.getElementById("hard-progress-label");
      const hardProgressBar = document.getElementById("hard-progress-bar");
      const hardProgressToast = document.getElementById("hard-progress-toast");
      let saved = {{}};
      try {{
        const parsed = JSON.parse(localStorage.getItem(progressKey) || "{{}}");
        saved =
          parsed && typeof parsed === "object" && !Array.isArray(parsed)
            ? parsed
            : {{}};
      }} catch (_error) {{
        saved = {{}};
      }}
      boxes.forEach((box) => {{
        box.checked = saved[box.dataset.checkpoint] === true;
        box.addEventListener("change", () => {{
          saved[box.dataset.checkpoint] = box.checked;
          localStorage.setItem(progressKey, JSON.stringify(saved));
          evaluateAgi(true);
        }});
      }});
      let hardSaved = [];
      try {{
        const parsed = JSON.parse(localStorage.getItem(hardProgressKey) || "[]");
        hardSaved = Array.isArray(parsed)
          ? parsed.filter((step) => typeof step === "string")
          : [];
      }} catch (_error) {{
        hardSaved = [];
      }}
      hardBoxes.forEach((box) => {{
        box.checked = hardSaved.includes(box.dataset.step);
        box.addEventListener("change", () => updateHardProgress(true));
      }});

      function currentEasyPath() {{
        return localStorage.getItem(globalEngineKey) === "brainstem"
          ? "brainstem"
          : "copilot";
      }}

      function requiredEasyBoxes() {{
        const path = currentEasyPath();
        return boxes.filter(
          (box) => box.dataset.agiPath === path || box.dataset.agiPath === "shared",
        );
      }}

      function agiGroupComplete(group) {{
        const path = currentEasyPath();
        const members = boxes.filter(
          (box) =>
            box.dataset.agiGroup === group &&
            (box.dataset.agiPath === path || box.dataset.agiPath === "shared"),
        );
        return members.length > 0 && members.every((box) => box.checked);
      }}

      function announceAgiBadge(badge) {{
        if (!badge || !agiToast) return;
        agiToast.textContent =
          `${{badge.label}} earned: +${{badge.points}} local achievement points.`;
        window.setTimeout(() => {{
          if (agiToast.textContent.includes(badge.label)) agiToast.textContent = "";
        }}, 5000);
      }}

      function updateHardProgress(announce = false) {{
        const done = hardBoxes
          .filter((box) => box.checked)
          .map((box) => box.dataset.step);
        const complete =
          hardBoxes.length > 0 && done.length === hardBoxes.length;
        localStorage.setItem(hardProgressKey, JSON.stringify(done));
        if (hardProgressLabel) {{
          hardProgressLabel.textContent =
            `${{done.length}} of ${{hardBoxes.length}} complete`;
        }}
        if (hardProgressBar) {{
          hardProgressBar.style.width = hardBoxes.length
            ? `${{(done.length / hardBoxes.length) * 100}}%`
            : "0%";
        }}
        const activeMode =
          localStorage.getItem(modeKey) === "hard" ? "hard" : "easy";
        let profile = readAgiProfile();
        if (done.length === 0 && !profile.workshops[AGI_WORKSHOP_SLUG]) {{
          renderAgiPanel(profile, activeMode);
          return;
        }}
        profile = setAgiWorkshopProgress(profile, activeMode, {{
          hardChecked: done.length,
          hardTotal: hardBoxes.length,
          hardComplete: complete,
        }});
        if (done.length > 0) {{
          const result = awardAgi(profile, "started", activeMode);
          profile = result.profile;
          if (announce) announceAgiBadge(result.awarded);
        }}
        if (complete) {{
          const result = awardAgi(
            profile,
            "hard-mode-complete",
            activeMode,
          );
          profile = result.profile;
          if (announce) announceAgiBadge(result.awarded);
        }}
        if (hardProgressToast) {{
          hardProgressToast.textContent = complete
            ? "Hard mode complete. The achievement is saved in this device's achievement profile."
            : "";
        }}
        renderAgiPanel(profile, activeMode);
      }}

      function earnedAgiSyncIds(achievements) {{
        return AGI_SYNC_ORDER.filter(
          (entry) => achievements[entry.localId]?.earned,
        ).map((entry) => entry.claimId);
      }}

      function renderAgiPanel(profile, mode) {{
        const workshop = profile.workshops[AGI_WORKSHOP_SLUG];
        const achievements = workshop?.achievements || {{}};
        const workshopPoints = AGI_BADGES.reduce(
          (total, badge) =>
            total + (achievements[badge.id]?.earned ? badge.points : 0),
          0,
        );
        agiTotalScore.textContent = String(profile.score);
        agiWorkshopScore.textContent = String(workshopPoints);
        const easyRequired = requiredEasyBoxes();
        const easyChecked = easyRequired.filter((box) => box.checked).length;
        const hardChecked = workshop?.progress?.hardChecked || 0;
        const hardTotal = workshop?.progress?.hardTotal || 0;
        const checked = mode === "hard" ? hardChecked : easyChecked;
        const total = mode === "hard" ? hardTotal : easyRequired.length;
        agiProgressLabel.textContent =
          `${{checked}} of ${{total}} ${{mode === "hard" ? "Hard steps" : "Easy checkpoints"}} complete`;
        agiProgressBar.style.width = total ? `${{(checked / total) * 100}}%` : "0%";
        agiBadgeList.replaceChildren();
        const earned = AGI_BADGES.filter(
          (badge) => achievements[badge.id]?.earned,
        );
        if (!earned.length) {{
          const item = document.createElement("li");
          item.className = "agi-badge";
          item.textContent = "No badges yet";
          agiBadgeList.append(item);
        }} else {{
          earned.forEach((badge) => {{
            const item = document.createElement("li");
            item.className = "agi-badge";
            item.textContent = `${{badge.label}} · +${{badge.points}}`;
            agiBadgeList.append(item);
          }});
        }}
        document.querySelector("[data-agi-sync]").hidden =
          earnedAgiSyncIds(achievements).length === 0;
      }}

      function evaluateAgi(announce = false) {{
        const mode = localStorage.getItem(modeKey) === "hard" ? "hard" : "easy";
        const easyRequired = requiredEasyBoxes();
        const easyChecked = easyRequired.filter((box) => box.checked).length;
        const hasCheckpoint = boxes.some((box) => box.checked);
        let profile = readAgiProfile();
        const existing = profile.workshops[AGI_WORKSHOP_SLUG];
        if (hasCheckpoint || existing) {{
          profile = setAgiWorkshopProgress(profile, mode, {{
            easyChecked,
            easyTotal: easyRequired.length,
            easyComplete:
              easyRequired.length > 0 && easyChecked === easyRequired.length,
          }});
          const earnedByCondition = [
            ["started", hasCheckpoint],
            ["local-proof", agiGroupComplete("local-proof")],
            ["draft-builder", agiGroupComplete("draft-builder")],
            ["preview-proven", agiGroupComplete("preview-proven")],
            [
              "workshop-complete",
              easyRequired.length > 0 && easyChecked === easyRequired.length,
            ],
          ];
          earnedByCondition.forEach(([badgeId, condition]) => {{
            if (!condition) return;
            const result = awardAgi(profile, badgeId, mode);
            profile = result.profile;
            if (announce) announceAgiBadge(result.awarded);
          }});
        }}
        renderAgiPanel(profile, mode);
      }}

      function selectMode(mode) {{
        buttons.forEach((button) => button.classList.toggle("active", button.dataset.mode === mode));
        paths.forEach((path) => {{ path.hidden = path.dataset.path !== mode; }});
        localStorage.setItem(modeKey, mode);
        evaluateAgi(false);
      }}
      buttons.forEach((button) => button.addEventListener("click", () => selectMode(button.dataset.mode)));
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
      document.querySelectorAll("[data-report-location]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const locationLabel = button.dataset.reportLocation || "Workshop";
          const expected = button.dataset.reportExpected || "Describe the expected result.";
          const evidence = button.dataset.reportEvidence || "No evidence path supplied.";
          const reportMode = button.closest('[data-path="hard"]')
            ? "hard"
            : localStorage.getItem(globalEngineKey) === "brainstem"
              ? "brainstem"
              : "copilot";
          const title = `[Workshop feedback] {ctx.title}: ${{locationLabel}}`;
          const body = `<!-- aibast-workshop-feedback:v1 -->
## Workshop signal

- Schema: \\`aibast-workshop-feedback/1.0\\`
- Solution: \\`{ctx.deployment.get("name") or f"@aibast-agents-library/{ctx.slug}"}\\`
- Page: ${{location.href}}
- Mode: \\`${{reportMode}}\\`
- Location: ${{locationLabel}}
- Evidence: \\`${{evidence}}\\`

## Workshop context

This issue was opened from a contextual workshop <em>Report an issue</em> button.

## Expected

${{expected}}

## What happened instead

Describe what was inaccurate or missing.

## Reproduction

1. Open the workshop page.
2. Select the mode shown above.
3. Follow the step or Preview case.
4. Record the visible result and any Copilot response.

> Workshop feedback report. Do not include credentials, tokens, customer data, or other sensitive information.`;
          const url = aibastSignalIssueUrl();
          url.searchParams.set("title", title);
          url.searchParams.set("body", body);
          window.open(url.toString(), "_blank", "noopener");
        }});
      }});
      function openAgiSync() {{
        const profile = readAgiProfile();
        const achievements =
          profile.workshops[AGI_WORKSHOP_SLUG]?.achievements || {{}};
        const earnedIds = earnedAgiSyncIds(achievements);
        if (!earnedIds.length) return;
        const source = new URL(window.location.href);
        source.search = "";
        source.hash = "";
        const body = `<!-- aibast-agi-progress:v1 -->
## Workshop achievement progress

- Schema: \\`aibast-agi-progress/1.0\\`
- Workshop: \\`${{AGI_WORKSHOP_SLUG}}\\`
- Agent: \\`${{AGI_CANONICAL_AGENT}}\\`
- Achievements: ${{earnedIds.join(", ")}}
- Source: ${{source.toString()}}

Opening this form does not sync anything. Submit the issue to sync these earned IDs. Resubmitting later merges newly earned IDs without duplicate score; the server computes the verified score. One public GitHub issue submission opts this account into a public verified profile.

> Do not add credentials, tokens, customer data, or other sensitive information.`;
        const url = aibastSignalIssueUrl();
        url.searchParams.set("title", `[Achievement progress] {ctx.title}`);
        url.searchParams.set("body", body);
        window.open(url.toString(), "_blank", "noopener");
      }}
      document.querySelector("[data-agi-sync]").addEventListener("click", () => {{
        openAgiSync();
      }});
      selectMode(localStorage.getItem(modeKey) === "hard" ? "hard" : "easy");
      updateHardProgress(false);
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
        ("Customer field guide", f"`solutions/{ctx.slug}/field-guide.html`"),
        ("Evidence report", f"`solutions/{ctx.slug}/evidence-report.html`"),
        (
            "Brainstem Easy Mode skill",
            "`skills/aibast-easy-mode-brainstem/SKILL.md`",
        ),
        (
            "Copilot-only Easy Mode skill",
            "`skills/aibast-easy-mode-copilot/SKILL.md`",
        ),
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
    if (ctx.package / "VISUAL-EVIDENCE-AUDIT.md").exists():
        rows.insert(
            1,
            (
                "Visual evidence audit",
                f"`solutions/{ctx.slug}/VISUAL-EVIDENCE-AUDIT.md`",
            ),
        )
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


def normalize_generated_text(content: str) -> str:
    return "\n".join(line.rstrip() for line in content.strip().splitlines()) + "\n"


def write_outputs(ctx: JourneyContext) -> list[Resource]:
    resources = collect_resources(ctx)
    outputs = {
        ctx.package / "FIELD-GUIDE.md": render_field_guide(ctx),
        ctx.package / "field-guide.html": render_field_guide_html(ctx),
        ctx.package / "evidence-report.html": render_evidence_report_html(ctx),
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
        path.write_text(normalize_generated_text(content), encoding="utf-8")
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
