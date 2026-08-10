#!/usr/bin/env python3
"""Build weekly/monthly AIBAST impact reports from the metrics snapshot."""

from __future__ import annotations

import argparse
import html
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_METRICS = ROOT / "state" / "metrics.json"
DEFAULT_HISTORY = ROOT / "state" / "impact_history.json"
DEFAULT_METRICS_HISTORY = ROOT / "state" / "metrics_history.json"
DEFAULT_OUT_DIR = ROOT / "reports"
REPORT_SCHEMA = "aibast-impact-report/1.0"
HISTORY_SCHEMA = "aibast-impact-history/1.0"
MAX_HISTORY_ROWS = 400

THEME_SCRIPT = """(() => {
    const param = new URLSearchParams(window.location.search).get("scoutTheme");
    const theme =
      param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
  })();"""

THEME_CSS = """:root {
  color-scheme: light;
  --cp-bg: #f7f4ef;
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
  --cp-highlight: rgba(177, 31, 75, 0.12);
}
html[data-theme="dark"] {
  color-scheme: dark;
  --cp-bg: #3d3b3a;
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
  --cp-highlight: rgba(253, 142, 161, 0.12);
}"""


METRICS = (
    {
        "id": "total_downloads",
        "label": "AIBAST observed repository downloads",
        "section": "Reach and consumption",
        "path": ("totals", "downloads"),
        "source": "downloads",
        "kind": "cumulative",
        "unit": "count",
        "daily_fields": ("clones", "cdn"),
    },
    {
        "id": "git_clones",
        "label": "Git clones",
        "section": "Reach and consumption",
        "path": ("totals", "clones"),
        "source": "traffic",
        "kind": "cumulative",
        "unit": "count",
        "daily_fields": ("clones",),
    },
    {
        "id": "clones_excluding_ci",
        "label": "Clones excluding CI estimate",
        "section": "Reach and consumption",
        "path": ("totals", "clones_excluding_ci_estimate"),
        "source": "traffic",
        "kind": "cumulative",
        "unit": "count",
    },
    {
        "id": "page_views",
        "label": "AIBAST repository and Pages views",
        "section": "Reach and consumption",
        "path": ("totals", "page_views"),
        "source": "traffic",
        "kind": "cumulative",
        "unit": "count",
        "daily_fields": ("views",),
    },
    {
        "id": "cdn_hits",
        "label": "jsDelivr file hits",
        "section": "Reach and consumption",
        "path": ("totals", "cdn_hits"),
        "source": "cdn",
        "kind": "cumulative",
        "unit": "count",
        "daily_fields": ("cdn",),
    },
    {
        "id": "release_downloads",
        "label": "Release asset downloads",
        "section": "Reach and consumption",
        "path": ("totals", "release_downloads"),
        "source": "releases",
        "kind": "cumulative",
        "unit": "count",
    },
    {
        "id": "agent_file_downloads",
        "label": "AIBAST direct agent file downloads",
        "section": "Reach and consumption",
        "path": ("totals", "agent_file_downloads"),
        "source": "file_metrics",
        "kind": "cumulative",
        "unit": "count",
    },
    {
        "id": "skill_downloads",
        "label": "AIBAST skill file downloads",
        "section": "Reach and consumption",
        "path": ("totals", "skill_downloads"),
        "source": "file_metrics",
        "kind": "cumulative",
        "unit": "count",
    },
    {
        "id": "installer_downloads",
        "label": "AIBAST installer file downloads",
        "section": "Reach and consumption",
        "path": ("totals", "installer_downloads"),
        "source": "file_metrics",
        "kind": "cumulative",
        "unit": "count",
    },
    {
        "id": "clone_uniques_14d",
        "label": "Unique cloners (14-day window)",
        "section": "Reach and consumption",
        "path": ("totals", "clone_uniques_14d"),
        "source": "traffic",
        "kind": "rolling",
        "unit": "count",
    },
    {
        "id": "view_uniques_14d",
        "label": "Unique visitors (14-day window)",
        "section": "Reach and consumption",
        "path": ("totals", "view_uniques_14d"),
        "source": "traffic",
        "kind": "rolling",
        "unit": "count",
    },
    {
        "id": "stars",
        "label": "GitHub stars",
        "section": "Community engagement",
        "path": ("repo", "stars"),
        "source": "repo",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "forks",
        "label": "GitHub forks",
        "section": "Community engagement",
        "path": ("repo", "forks"),
        "source": "repo",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "watchers",
        "label": "GitHub watchers",
        "section": "Community engagement",
        "path": ("repo", "watchers"),
        "source": "repo",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "open_issues",
        "label": "Open GitHub issues",
        "section": "Community engagement",
        "path": ("repo", "open_issues"),
        "source": "repo",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "agent_upvotes",
        "label": "Agent upvotes",
        "section": "Community engagement",
        "path": ("totals", "agent_upvotes"),
        "source": "agent_upvotes",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "agent_acquisitions",
        "label": "Signed-in agent acquisitions",
        "section": "Community engagement",
        "path": ("totals", "agent_acquisitions"),
        "source": "agent_acquisitions",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "workshop_usage_events",
        "label": "Workshop usage events",
        "section": "Community engagement",
        "path": ("workshops", "totals", "usage_events"),
        "source": "workshops",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "workshop_views_14d",
        "label": "Workshop views (14-day top paths)",
        "section": "Community engagement",
        "path": ("workshops", "totals", "views_14d"),
        "source": "workshop_views",
        "kind": "rolling",
        "unit": "count",
    },
    {
        "id": "workshop_file_downloads",
        "label": "Workshop file downloads",
        "section": "Community engagement",
        "path": ("workshops", "totals", "file_downloads"),
        "source": "workshop_downloads",
        "kind": "cumulative",
        "unit": "count",
    },
    {
        "id": "workshop_bundle_downloads",
        "label": "Workshop bundle downloads",
        "section": "Community engagement",
        "path": ("workshops", "totals", "bundle_downloads"),
        "source": "workshop_downloads",
        "kind": "cumulative",
        "unit": "count",
    },
    {
        "id": "workshop_feedback",
        "label": "Workshop feedback reports",
        "section": "Community engagement",
        "path": ("workshops", "totals", "feedback_reports"),
        "source": "workshop_feedback",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "achievement_participants",
        "label": "Verified achievement participants",
        "section": "Learning impact",
        "path": ("achievements", "totals", "participants"),
        "source": "achievements",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "achievement_points",
        "label": "Verified achievement points",
        "section": "Learning impact",
        "path": ("achievements", "totals", "points"),
        "source": "achievements",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "verified_achievements",
        "label": "Verified achievements",
        "section": "Learning impact",
        "path": ("achievements", "totals", "achievements"),
        "source": "achievements",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "achievement_starts",
        "label": "Workshop starts",
        "section": "Learning impact",
        "path": ("achievements", "totals", "starts"),
        "source": "achievements",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "achievement_completions",
        "label": "Workshop completions",
        "section": "Learning impact",
        "path": ("achievements", "totals", "workshop_completions"),
        "source": "achievements",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "achievement_hard_completions",
        "label": "Hard-mode completions",
        "section": "Learning impact",
        "path": ("achievements", "totals", "hard_completions"),
        "source": "achievements",
        "kind": "gauge",
        "unit": "count",
    },
    {
        "id": "achievement_completion_rate",
        "label": "Workshop completion rate",
        "section": "Learning impact",
        "path": ("achievements", "totals", "completion_rate"),
        "source": "achievements",
        "kind": "rate",
        "unit": "percent",
    },
    {
        "id": "achievement_hard_completion_rate",
        "label": "Hard-mode completion rate",
        "section": "Learning impact",
        "path": ("achievements", "totals", "hard_completion_rate"),
        "source": "achievements",
        "kind": "rate",
        "unit": "percent",
    },
    {
        "id": "achievement_achievement_rate",
        "label": "Achievement completion rate",
        "section": "Learning impact",
        "path": ("achievements", "totals", "achievement_completion_rate"),
        "source": "achievements",
        "kind": "rate",
        "unit": "percent",
    },
    {
        "id": "tracked_files",
        "label": "Tracked repository files",
        "section": "Library footprint",
        "path": ("file_metrics", "totals", "files"),
        "source": "catalog",
        "kind": "catalog",
        "unit": "count",
    },
    {
        "id": "observed_files",
        "label": "Files covered by download observations",
        "section": "Library footprint",
        "path": ("file_metrics", "totals", "observed_files"),
        "source": "file_metrics",
        "kind": "catalog",
        "unit": "count",
    },
    {
        "id": "agents",
        "label": "Catalog agents",
        "section": "Library footprint",
        "path": ("totals", "agents"),
        "source": "catalog",
        "kind": "catalog",
        "unit": "count",
    },
    {
        "id": "skills",
        "label": "Tracked SKILL.md files",
        "section": "Library footprint",
        "path": ("file_metrics", "totals", "by_kind", "skill", "files"),
        "source": "catalog",
        "kind": "catalog",
        "unit": "count",
    },
    {
        "id": "workshops",
        "label": "Canonical workshops",
        "section": "Library footprint",
        "path": ("workshops", "totals", "workshops"),
        "source": "catalog",
        "kind": "catalog",
        "unit": "count",
    },
    {
        "id": "stacks",
        "label": "Deployable stacks",
        "section": "Library footprint",
        "path": ("totals", "stacks"),
        "source": "catalog",
        "kind": "catalog",
        "unit": "count",
    },
    {
        "id": "verticals",
        "label": "Industry verticals",
        "section": "Library footprint",
        "path": ("totals", "verticals"),
        "source": "catalog",
        "kind": "catalog",
        "unit": "count",
    },
)

DAILY_FIELD_SOURCES = {
    "clones": "traffic",
    "views": "traffic",
    "cdn": "cdn",
}


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return default


def numeric(value: Any) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(value):
        return None
    return value


def get_path(document: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = document
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
            timezone.utc
        )
    except ValueError:
        return None


def source_status(document: dict[str, Any], source: str) -> str:
    traffic = document.get("traffic") or {}
    cdn = document.get("cdn") or {}
    releases = document.get("releases") or {}
    file_metrics = document.get("file_metrics") or {}
    upvotes = document.get("agent_upvote_coverage") or {}
    acquisitions = document.get("agent_acquisition_coverage") or {}
    workshops = document.get("workshops") or {}
    workshop_coverage = workshops.get("coverage") or {}
    achievements = document.get("achievements") or {}
    if source == "catalog":
        return "available"
    if source == "repo":
        repo = document.get("repo") or {}
        if not repo.get("as_of"):
            return "unavailable"
        return "partial" if repo.get("carried_forward") else "available"
    if source == "traffic":
        if traffic.get("live"):
            return "available"
        return "partial" if traffic.get("as_of") else "unavailable"
    if source == "cdn":
        if not cdn.get("as_of"):
            return "unavailable"
        return "partial" if cdn.get("carried_forward") else "available"
    if source == "releases":
        if not releases.get("as_of"):
            return "unavailable"
        return "partial" if releases.get("carried_forward") else "available"
    if source == "file_metrics":
        status = file_metrics.get("source_status")
        if status == "complete" and not file_metrics.get("carried_forward"):
            return "available"
        return "partial" if status in {"complete", "censored"} else "unavailable"
    if source == "agent_upvotes":
        status = upvotes.get("status")
        if status == "available" and not upvotes.get("carried_forward"):
            return "available"
        return (
            "partial"
            if status in {"available", "partial", "carried_forward"}
            else "unavailable"
        )
    if source == "agent_acquisitions":
        status = acquisitions.get("status")
        if status == "available" and not acquisitions.get(
            "carried_forward"
        ):
            return "available"
        return (
            "partial"
            if status in {"available", "partial", "carried_forward"}
            else "unavailable"
        )
    if source == "workshops":
        return (
            "partial"
            if workshop_coverage.get("status") == "partial"
            else "available"
            if workshop_coverage.get("status") == "available"
            else "unavailable"
        )
    if source == "workshop_views":
        status = (workshop_coverage.get("views") or {}).get("status")
        return normalized_source_status(status)
    if source == "workshop_downloads":
        status = (workshop_coverage.get("downloads") or {}).get("status")
        return normalized_source_status(status)
    if source == "workshop_feedback":
        status = (workshop_coverage.get("feedback") or {}).get("status")
        return normalized_source_status(status)
    if source == "achievements":
        status = achievements.get("status")
        if status == "available" and not achievements.get("carried_forward"):
            return "available"
        return (
            "partial"
            if status in {"available", "partial", "carried_forward"}
            else "unavailable"
        )
    if source == "downloads":
        statuses = {
            source_status(document, "traffic"),
            source_status(document, "cdn"),
            source_status(document, "releases"),
        }
        if statuses == {"unavailable"}:
            return "unavailable"
        return "available" if statuses == {"available"} else "partial"
    return "unavailable"


def normalized_source_status(value: Any) -> str:
    status = str(value or "").casefold()
    if (
        not status
        or "unavailable" in status
        or "required" in status
        or "not-instrumented" in status
    ):
        return "unavailable"
    if any(
        marker in status
        for marker in ("partial", "censored", "carried", "last authorized")
    ):
        return "partial"
    return "available"


def extract_metric_rows(document: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for definition in METRICS:
        status = source_status(document, definition["source"])
        value = numeric(get_path(document, definition["path"]))
        if status == "unavailable":
            value = None
        rows.append(
            {
                **definition,
                "value": value,
                "status": status if value is not None else "unavailable",
            }
        )
    return rows


def compact_workshops(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    achievement_rows = {
        row.get("slug"): row
        for row in (document.get("achievements") or {}).get("workshops", [])
        if isinstance(row, dict) and row.get("slug")
    }
    result = {}
    for row in (document.get("workshops") or {}).get("rows", []):
        if not isinstance(row, dict) or not row.get("slug"):
            continue
        slug = row["slug"]
        achievements = achievement_rows.get(slug, {})
        result[slug] = {
            "display_name": row.get("display_name") or slug,
            "usage_events": numeric(row.get("usage_events")),
            "views_14d": numeric(row.get("views_14d")),
            "file_downloads": numeric(row.get("file_downloads")),
            "bundle_downloads": numeric(row.get("bundle_downloads")),
            "feedback_reports": numeric(row.get("feedback_reports")),
            "agent_upvotes": numeric(row.get("agent_upvotes")),
            "achievement_points": numeric(achievements.get("points")),
            "achievement_starts": numeric(achievements.get("starts")),
            "achievement_completions": numeric(achievements.get("workshop_completions")),
            "achievement_hard_completions": numeric(achievements.get("hard_completions")),
        }
    return result


def compact_agents(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row["name"]: {
            "display_name": row.get("display_name") or row["name"],
            "downloads": numeric(row.get("downloads")),
            "upvotes": numeric(row.get("upvotes")),
            "acquisitions": numeric(row.get("acquisitions")),
        }
        for row in document.get("agent_metrics", [])
        if isinstance(row, dict) and row.get("name")
    }


def compact_snapshot(document: dict[str, Any]) -> dict[str, Any]:
    generated_at = document.get("generated_at")
    if parse_time(generated_at) is None:
        raise ValueError("metrics snapshot has no valid generated_at timestamp")
    repo = document.get("repo") or {}
    return {
        "at": generated_at,
        "repo": {
            "owner": repo.get("owner"),
            "name": repo.get("name"),
        },
        "metrics": {
            row["id"]: {"value": row["value"], "status": row["status"]}
            for row in extract_metric_rows(document)
        },
        "workshops": compact_workshops(document),
        "agents": compact_agents(document),
    }


def load_history(path: Path) -> dict[str, Any]:
    document = load_json(path, {})
    if not isinstance(document, dict) or document.get("schema") != HISTORY_SCHEMA:
        return {"schema": HISTORY_SCHEMA, "snapshots": []}
    snapshots = document.get("snapshots")
    if not isinstance(snapshots, list):
        snapshots = []
    return {"schema": HISTORY_SCHEMA, "snapshots": snapshots}


def record_snapshot(
    history: dict[str, Any],
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    timestamp = parse_time(snapshot["at"])
    if timestamp is None:
        raise ValueError("impact snapshot has no valid timestamp")
    identity = (
        timestamp.date().isoformat(),
        snapshot["repo"].get("owner"),
        snapshot["repo"].get("name"),
    )
    rows = [
        row
        for row in history.get("snapshots", [])
        if (
            (
                parse_time(row.get("at")).date().isoformat()
                if parse_time(row.get("at"))
                else None
            ),
            (row.get("repo") or {}).get("owner"),
            (row.get("repo") or {}).get("name"),
        )
        != identity
    ]
    rows.append(snapshot)
    rows.sort(key=lambda row: row.get("at") or "")
    return {"schema": HISTORY_SCHEMA, "snapshots": rows[-MAX_HISTORY_ROWS:]}


def matching_snapshots(
    history: dict[str, Any],
    current: dict[str, Any],
) -> list[dict[str, Any]]:
    repo = current["repo"]
    return [
        row
        for row in history.get("snapshots", [])
        if (row.get("repo") or {}).get("owner") == repo.get("owner")
        and (row.get("repo") or {}).get("name") == repo.get("name")
        and parse_time(row.get("at")) is not None
    ]


def baseline_for(
    history: dict[str, Any],
    current: dict[str, Any],
    days: int,
) -> dict[str, Any] | None:
    current_at = parse_time(current["at"])
    assert current_at is not None
    target = current_at - timedelta(days=days)
    eligible = [
        row
        for row in matching_snapshots(history, current)
        if parse_time(row.get("at")) <= target
    ]
    return max(eligible, key=lambda row: row["at"]) if eligible else None


def daily_activity(
    document: dict[str, Any],
    definition: dict[str, Any],
    days: int,
    metrics_history: dict[str, Any] | None = None,
) -> tuple[int | float | None, str]:
    fields = definition.get("daily_fields")
    if not fields:
        return None, "not_applicable"
    current_at = parse_time(document.get("generated_at"))
    if current_at is None:
        return None, "unavailable"
    cutoff = (current_at - timedelta(days=days - 1)).date()
    history = metrics_history or {}
    tracking = history.get("tracking") or {}
    total = 0
    complete_fields = 0
    incomplete_fields = 0
    for field in fields:
        source = DAILY_FIELD_SOURCES[field]
        if source_status(document, source) != "available":
            incomplete_fields += 1
            continue
        bucket_name = "cdn" if field == "cdn" else field
        bucket = history.get(bucket_name)
        if not isinstance(bucket, dict):
            incomplete_fields += 1
            continue
        since_raw = tracking.get(f"{bucket_name}_since")
        last_raw = tracking.get(f"{bucket_name}_last")
        if not since_raw and bucket:
            since_raw = min(bucket)
        since = parse_time(f"{since_raw}T00:00:00Z") if since_raw else None
        last = parse_time(f"{last_raw}T00:00:00Z") if last_raw else None
        if (
            since is None
            or since.date() > cutoff
            or last is None
            or last.date() < current_at.date() - timedelta(days=1)
        ):
            incomplete_fields += 1
            continue
        for day_raw, value in bucket.items():
            try:
                day = datetime.strptime(day_raw, "%Y-%m-%d").date()
            except (TypeError, ValueError):
                continue
            if day < cutoff:
                continue
            if field == "cdn":
                count = numeric(value)
            else:
                count = numeric((value or {}).get("count"))
            if count is not None:
                total += count
        complete_fields += 1
    if complete_fields == 0:
        return None, "baseline_pending"
    return total, "partial" if incomplete_fields else "complete"


def period_metric(
    definition: dict[str, Any],
    current_row: dict[str, Any],
    baseline: dict[str, Any] | None,
    document: dict[str, Any],
    days: int,
    metrics_history: dict[str, Any] | None = None,
) -> dict[str, Any]:
    activity, activity_status = daily_activity(
        document,
        definition,
        days,
        metrics_history,
    )
    if definition.get("daily_fields"):
        if current_row["status"] == "unavailable":
            return {
                "status": "unavailable",
                "calculation": "period_activity",
                "value": None,
                "baseline": None,
                "change": None,
                "change_percent": None,
            }
        if activity_status in {"complete", "partial"}:
            status = current_row["status"]
            if definition["id"] == "total_downloads" or activity_status == "partial":
                status = "partial"
            return {
                "status": status,
                "calculation": "period_activity",
                "value": activity,
                "baseline": None,
                "change": activity,
                "change_percent": None,
            }
    if current_row["value"] is None:
        return {
            "status": "current_unavailable",
            "calculation": "snapshot_change",
            "value": None,
            "baseline": None,
            "change": None,
            "change_percent": None,
        }
    if baseline is None:
        return {
            "status": "baseline_pending",
            "calculation": "snapshot_change",
            "value": current_row["value"],
            "baseline": None,
            "change": None,
            "change_percent": None,
        }
    prior = (baseline.get("metrics") or {}).get(definition["id"]) or {}
    prior_value = numeric(prior.get("value"))
    if prior_value is None:
        return {
            "status": "baseline_unavailable",
            "calculation": "snapshot_change",
            "value": current_row["value"],
            "baseline": None,
            "change": None,
            "change_percent": None,
        }
    change = current_row["value"] - prior_value
    percent = (
        round((change / prior_value) * 100, 1)
        if prior_value != 0
        else 0.0
        if change == 0
        else None
    )
    return {
        "status": (
            "partial"
            if "partial" in {current_row["status"], prior.get("status")}
            else "available"
        ),
        "calculation": "snapshot_change",
        "value": current_row["value"],
        "baseline": prior_value,
        "change": round(change, 1) if isinstance(change, float) else change,
        "change_percent": percent,
    }


def top_movers(
    current: dict[str, dict[str, Any]],
    prior: dict[str, dict[str, Any]],
    field: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    rows = []
    for key, current_row in current.items():
        prior_row = prior.get(key) or {}
        value = numeric(current_row.get(field))
        baseline = numeric(prior_row.get(field))
        if value is None or baseline is None:
            continue
        change = value - baseline
        if change == 0:
            continue
        rows.append(
            {
                "id": key,
                "label": current_row.get("display_name") or key,
                "current": value,
                "change": change,
            }
        )
    rows.sort(key=lambda row: (-row["change"], row["label"].casefold()))
    return rows[:limit]


def build_period(
    name: str,
    days: int,
    document: dict[str, Any],
    current: dict[str, Any],
    current_rows: list[dict[str, Any]],
    history: dict[str, Any],
    metrics_history: dict[str, Any] | None = None,
) -> dict[str, Any]:
    baseline = baseline_for(history, current, days)
    current_at = parse_time(current["at"])
    baseline_at = parse_time(baseline.get("at")) if baseline else None
    observed_days = (
        round((current_at - baseline_at).total_seconds() / 86400, 1)
        if current_at and baseline_at
        else None
    )
    prior_workshops = (baseline or {}).get("workshops") or {}
    prior_agents = (baseline or {}).get("agents") or {}
    return {
        "name": name,
        "days": days,
        "status": "complete" if baseline else "baseline_pending",
        "baseline_at": baseline.get("at") if baseline else None,
        "observed_days": observed_days,
        "metrics": {
            row["id"]: period_metric(
                row,
                row,
                baseline,
                document,
                days,
                metrics_history,
            )
            for row in current_rows
        },
        "movers": {
            "workshop_usage": top_movers(
                current.get("workshops") or {},
                prior_workshops,
                "usage_events",
            ),
            "workshop_achievement_points": top_movers(
                current.get("workshops") or {},
                prior_workshops,
                "achievement_points",
            ),
            "agent_downloads": top_movers(
                current.get("agents") or {},
                prior_agents,
                "downloads",
            ),
            "agent_upvotes": top_movers(
                current.get("agents") or {},
                prior_agents,
                "upvotes",
            ),
            "agent_acquisitions": top_movers(
                current.get("agents") or {},
                prior_agents,
                "acquisitions",
            ),
        },
    }


def coverage_summary(document: dict[str, Any]) -> dict[str, Any]:
    traffic = document.get("traffic") or {}
    file_metrics = document.get("file_metrics") or {}
    workshops = document.get("workshops") or {}
    achievements = document.get("achievements") or {}
    upvotes = document.get("agent_upvote_coverage") or {}
    acquisitions = document.get("agent_acquisition_coverage") or {}
    return {
        "traffic": {
            "status": "live" if traffic.get("live") else "unavailable"
            if not traffic.get("as_of")
            else "carried_forward",
            "as_of": traffic.get("as_of"),
            "reason": traffic.get("unavailable_reason"),
        },
        "file_downloads": {
            "status": file_metrics.get("source_status") or "unavailable",
            "as_of": file_metrics.get("as_of"),
        },
        "agent_upvotes": {
            "status": upvotes.get("status") or "unavailable",
            "as_of": upvotes.get("as_of"),
        },
        "agent_acquisitions": {
            "status": acquisitions.get("status") or "unavailable",
            "as_of": acquisitions.get("as_of"),
        },
        "workshops": {
            "status": (workshops.get("coverage") or {}).get("status")
            or "unavailable",
            "as_of": workshops.get("as_of"),
        },
        "achievements": {
            "status": achievements.get("status") or "unavailable",
            "as_of": achievements.get("as_of"),
        },
    }


def report_links(document: dict[str, Any]) -> dict[str, str]:
    site = str((document.get("repo") or {}).get("site") or "").rstrip("/") + "/"
    return {
        "site": site,
        "metrics": site + "metrics.html",
        "html": site + "reports/impact-report.html",
        "pdf": site + "reports/impact-report.pdf",
        "email": site + "reports/impact-report-email.txt",
        "json": site + "reports/impact-report.json",
    }


def build_report(
    document: dict[str, Any],
    history: dict[str, Any],
    metrics_history: dict[str, Any] | None = None,
) -> dict[str, Any]:
    current = compact_snapshot(document)
    rows = extract_metric_rows(document)
    generated = parse_time(document.get("generated_at"))
    assert generated is not None
    links = report_links(document)
    caveats = [
        (
            "This report uses AIBAST-only public GitHub, Discussion, jsDelivr, "
            "release, and opt-in issue signals. RAR is excluded from every count. "
            "It contains no private analytics or tracking pixel."
        ),
        (
            "Raw GitHub, raw.githubusercontent.com, and direct GitHub Pages file "
            "downloads expose no public per-file counter, so download figures are "
            "a measurable floor rather than total use."
        ),
        (
            "GitHub traffic and popular paths require repository Administration: "
            "read. Unavailable traffic remains unavailable instead of becoming a "
            "fabricated zero."
        ),
        (
            "Workshop usage combines mixed-window public events and is not a user "
            "count. Agent rating upvotes, signed-in acquisitions, and achievement "
            "points remain separate signals."
        ),
        (
            "Verified achievements confirm authenticated GitHub issue authorship "
            "and schema only; the underlying self-reported completion is not "
            "independently proven."
        ),
        (
            "A native upvote on an agent rating Discussion records preference. "
            "A native upvote on its acquisition Discussion records one signed-in "
            "account's declared download, copy, or install. Neither replaces "
            "observable CDN or release file-transfer counts."
        ),
    ]
    subject = (
        "AIBAST weekly and monthly impact report - "
        f"{generated.strftime('%B')} {generated.day}, {generated.year}"
    )
    return {
        "schema": REPORT_SCHEMA,
        "generated_at": document["generated_at"],
        "subject": subject,
        "repo": document.get("repo") or {},
        "links": links,
        "coverage": coverage_summary(document),
        "current": {
            "metrics": rows,
            "workshops": current["workshops"],
            "agents": current["agents"],
        },
        "periods": {
            "week": build_period(
                "Weekly",
                7,
                document,
                current,
                rows,
                history,
                metrics_history,
            ),
            "month": build_period(
                "Monthly",
                30,
                document,
                current,
                rows,
                history,
                metrics_history,
            ),
        },
        "caveats": caveats,
    }


def format_number(value: int | float | None, unit: str = "count") -> str:
    if value is None:
        return "Unavailable"
    if unit == "percent":
        return f"{value:,.1f}%"
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.1f}"
    return f"{int(value):,}"


def signed_number(value: int | float, unit: str = "count") -> str:
    if unit == "percent":
        return f"{value:+,.1f} pp"
    if isinstance(value, float) and not value.is_integer():
        return f"{value:+,.1f}"
    return f"{int(value):+,}"


def format_period_metric(
    definition: dict[str, Any],
    period_row: dict[str, Any],
) -> str:
    status = period_row.get("status")
    if status == "baseline_pending":
        return "Baseline pending"
    if status == "baseline_unavailable":
        return "Baseline unavailable"
    if status in {"current_unavailable", "unavailable"}:
        return "Unavailable"
    change = numeric(period_row.get("change"))
    if change is None:
        return "Unavailable"
    rendered = signed_number(change, definition["unit"])
    percent = numeric(period_row.get("change_percent"))
    if period_row.get("calculation") == "period_activity":
        suffix = " observed"
    elif definition["kind"] == "rolling":
        suffix = " snapshot change"
    else:
        suffix = ""
    if percent is not None and definition["unit"] != "percent":
        rendered += f" ({percent:+.1f}%)"
    if status == "partial":
        suffix += " - partial"
    return rendered + suffix


def grouped_metrics(report: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in report["current"]["metrics"]:
        groups[row["section"]].append(row)
    return dict(groups)


MOVER_GROUPS = (
    ("workshop_usage", "Workshop usage"),
    ("workshop_achievement_points", "Workshop achievement points"),
    ("agent_downloads", "Agent downloads"),
    ("agent_upvotes", "Agent upvotes"),
    ("agent_acquisitions", "Signed-in agent acquisitions"),
)


def mover_groups(period: dict[str, Any]) -> list[tuple[str, list[dict[str, Any]]]]:
    movers = period.get("movers") or {}
    return [
        (label, movers.get(key) or [])
        for key, label in MOVER_GROUPS
        if movers.get(key)
    ]


def format_mover(row: dict[str, Any]) -> str:
    return (
        f"{row.get('label') or row.get('id')}: "
        f"{signed_number(row.get('change') or 0)} "
        f"(current {format_number(row.get('current'))})"
    )


def render_email_text(report: dict[str, Any]) -> str:
    week = report["periods"]["week"]
    month = report["periods"]["month"]
    lines = [
        f"Subject: {report['subject']}",
        "",
        "AIBAST - WEEKLY & MONTHLY IMPACT",
        f"Snapshot: {report['generated_at']}",
        f"Site: {report['links']['site']}",
        "",
        "Weekly compares the current snapshot with a snapshot at least 7 days old.",
        "Monthly compares with a snapshot at least 30 days old.",
        "Exact daily clone/view/CDN activity is summed directly where available.",
        "",
    ]
    for section, rows in grouped_metrics(report).items():
        lines.extend([section.upper(), "-" * len(section)])
        lines.append(
            f"{'Metric':48} {'Current':>14} {'7-day':>32} {'30-day':>32}"
        )
        for row in rows:
            current = format_number(row["value"], row["unit"])
            weekly = format_period_metric(row, week["metrics"][row["id"]])
            monthly = format_period_metric(row, month["metrics"][row["id"]])
            lines.append(
                f"{row['label'][:48]:48} {current:>14} "
                f"{weekly[:32]:>32} {monthly[:32]:>32}"
            )
        lines.append("")
    for key, title in (("week", "TOP WEEKLY MOVERS"), ("month", "TOP MONTHLY MOVERS")):
        lines.extend([title, "-" * len(title)])
        groups = mover_groups(report["periods"][key])
        if not groups:
            lines.append("No complete dated baseline or non-zero movers yet.")
        else:
            for label, rows in groups:
                lines.append(f"{label}:")
                lines.extend(f"- {format_mover(row)}" for row in rows)
        lines.append("")
    lines.extend(
        [
            "MEASUREMENT STATUS",
            "------------------",
            *[
                f"- {name.replace('_', ' ').title()}: {details.get('status')}"
                + (
                    f" (as of {details.get('as_of')})"
                    if details.get("as_of")
                    else ""
                )
                for name, details in report["coverage"].items()
            ],
            "",
            "IMPORTANT NOTES",
            "---------------",
            *[f"- {note}" for note in report["caveats"]],
            "",
            f"Open the formatted report: {report['links']['html']}",
            f"Download the PDF: {report['links']['pdf']}",
            f"View live metrics: {report['links']['metrics']}",
        ]
    )
    return "\n".join(lines) + "\n"


def render_email_markdown(report: dict[str, Any]) -> str:
    week = report["periods"]["week"]
    month = report["periods"]["month"]
    lines = [
        f"**Subject:** {report['subject']}",
        "",
        "# AIBAST - Weekly & Monthly Impact",
        "",
        f"**Snapshot:** `{report['generated_at']}`",
        f"**Site:** {report['links']['site']}",
        "",
    ]
    for section, rows in grouped_metrics(report).items():
        lines.extend(
            [
                f"## {section}",
                "",
                "| Metric | Current | 7-day impact | 30-day impact |",
                "|---|---:|---:|---:|",
            ]
        )
        for row in rows:
            lines.append(
                f"| {row['label']} | "
                f"{format_number(row['value'], row['unit'])} | "
                f"{format_period_metric(row, week['metrics'][row['id']])} | "
                f"{format_period_metric(row, month['metrics'][row['id']])} |"
            )
        lines.append("")
    for key, title in (("week", "Top weekly movers"), ("month", "Top monthly movers")):
        lines.extend([f"## {title}", ""])
        groups = mover_groups(report["periods"][key])
        if not groups:
            lines.extend(
                ["No complete dated baseline or non-zero movers yet.", ""]
            )
            continue
        for label, rows in groups:
            lines.append(f"**{label}**")
            lines.extend(f"- {format_mover(row)}" for row in rows)
            lines.append("")
    lines.extend(
        [
            "## Measurement notes",
            "",
            *[f"- {note}" for note in report["caveats"]],
            "",
            f"[Open report]({report['links']['html']}) | "
            f"[Download PDF]({report['links']['pdf']}) | "
            f"[Live metrics]({report['links']['metrics']})",
            "",
        ]
    )
    return "\n".join(lines)


def render_html(report: dict[str, Any]) -> str:
    week = report["periods"]["week"]
    month = report["periods"]["month"]
    section_markup = []
    for section, rows in grouped_metrics(report).items():
        body = "\n".join(
            f"""<tr>
              <th scope="row">{html.escape(row["label"])}</th>
              <td>{html.escape(format_number(row["value"], row["unit"]))}<span class="source-status">{html.escape(row["status"])}</span></td>
              <td>{html.escape(format_period_metric(row, week["metrics"][row["id"]]))}</td>
              <td>{html.escape(format_period_metric(row, month["metrics"][row["id"]]))}</td>
            </tr>"""
            for row in rows
        )
        section_markup.append(
            f"""<section class="report-section">
        <h2>{html.escape(section)}</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Metric</th><th>Current</th><th>7-day impact</th><th>30-day impact</th></tr></thead>
            <tbody>{body}</tbody>
          </table>
        </div>
      </section>"""
        )
    coverage = "\n".join(
        f'<li><strong>{html.escape(name.replace("_", " ").title())}:</strong> '
        f'{html.escape(str(details.get("status") or "unavailable"))}'
        + (
            f' <span>as of {html.escape(str(details["as_of"]))}</span>'
            if details.get("as_of")
            else ""
        )
        + "</li>"
        for name, details in report["coverage"].items()
    )
    caveats = "\n".join(
        f"<li>{html.escape(note)}</li>" for note in report["caveats"]
    )
    mover_cards = []
    for key, title in (("week", "Top weekly movers"), ("month", "Top monthly movers")):
        groups = mover_groups(report["periods"][key])
        if groups:
            groups_markup = "".join(
                f"<h3>{html.escape(label)}</h3><ol>"
                + "".join(
                    f"<li>{html.escape(format_mover(row))}</li>"
                    for row in rows
                )
                + "</ol>"
                for label, rows in groups
            )
        else:
            groups_markup = (
                "<p>No complete dated baseline or non-zero movers yet.</p>"
            )
        mover_cards.append(
            f'<article class="mover-card"><h2>{html.escape(title)}</h2>'
            f"{groups_markup}</article>"
        )
    repo = report["repo"]
    return f"""<!doctype html>
<html lang="en">
<head>
  <script>
  {THEME_SCRIPT}
  </script>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(report["subject"])}</title>
  <meta name="description" content="Weekly and monthly public impact report for the AIBAST Agents Library.">
  <style>
{THEME_CSS}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--cp-bg); color: var(--cp-text); font-family: "Segoe UI", Aptos, Calibri, -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.5; }}
    a {{ color: var(--cp-link); }}
    .page {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 40px 0 72px; }}
    .hero, .report-section, .notes {{ margin-bottom: 20px; padding: 24px; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); box-shadow: 0 0 2px var(--cp-border), 0 1px 2px var(--cp-border); }}
    .eyebrow {{ margin: 0 0 8px; color: var(--cp-accent); font-size: 12px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }}
    h1 {{ margin: 0; font-size: clamp(32px, 6vw, 54px); line-height: 1; }}
    h2 {{ margin: 0 0 14px; }}
    .lede {{ max-width: 820px; color: var(--cp-text-muted); font-size: 17px; }}
    .meta, .actions {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }}
    .pill, .button {{ display: inline-flex; align-items: center; min-height: 38px; padding: 8px 12px; border: 1px solid var(--cp-border); border-radius: 10px; background: var(--cp-surface-soft); color: var(--cp-text); text-decoration: none; }}
    .button.primary {{ border-color: var(--cp-accent); background: var(--cp-accent); color: var(--cp-accent-fg); }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 11px 12px; border: 1px solid var(--cp-border); text-align: left; vertical-align: top; }}
    thead th {{ background: var(--cp-surface-soft); }}
    tbody th {{ width: 34%; }}
    .source-status {{ display: block; margin-top: 3px; color: var(--cp-text-muted); font-size: 11px; text-transform: uppercase; }}
    .movers {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 20px; }}
    .mover-card {{ padding: 20px; border: 1px solid var(--cp-border); border-radius: 16px; background: var(--cp-surface); }}
    .mover-card h2 {{ margin-top: 0; }}
    .mover-card h3 {{ margin-bottom: 6px; color: var(--cp-accent); font-size: 14px; }}
    .mover-card ol {{ margin-top: 0; padding-left: 22px; }}
    .notes-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    .notes ul {{ margin-bottom: 0; padding-left: 20px; }}
    .notes li {{ margin-bottom: 8px; }}
    footer {{ color: var(--cp-text-muted); font-size: 13px; text-align: center; }}
    @media (max-width: 760px) {{ .notes-grid, .movers {{ grid-template-columns: 1fr; }} .hero, .report-section, .notes {{ padding: 18px; }} }}
    @media print {{ body {{ background: var(--cp-surface); }} .page {{ width: 100%; padding: 0; }} .actions {{ display: none; }} .hero, .report-section, .notes {{ break-inside: avoid; box-shadow: none; }} }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <p class="eyebrow">AIBAST impact reporting</p>
      <h1>Weekly &amp; monthly impact</h1>
      <p class="lede">A shareable, automation-ready view of every measurable AIBAST library signal. The report preserves unavailable and partial coverage rather than manufacturing zeros.</p>
      <div class="meta">
        <span class="pill">Snapshot {html.escape(report["generated_at"])}</span>
        <span class="pill">{html.escape(str(repo.get("owner") or ""))}/{html.escape(str(repo.get("name") or ""))}</span>
        <span class="pill">7-day baseline: {html.escape(str(week.get("baseline_at") or "building history"))}</span>
        <span class="pill">30-day baseline: {html.escape(str(month.get("baseline_at") or "building history"))}</span>
      </div>
      <div class="actions">
        <a class="button primary" href="impact-report.pdf">Download PDF</a>
        <a class="button" href="impact-report-email.txt" download>Email-ready text</a>
        <a class="button" href="impact-report-email.md" download>Email-ready Markdown</a>
        <a class="button" href="impact-report.json">Machine-readable JSON</a>
        <a class="button" href="../metrics.html">Live metrics dashboard</a>
      </div>
    </section>
    {"".join(section_markup)}
    <section class="movers" aria-label="Top weekly and monthly movers">{"".join(mover_cards)}</section>
    <section class="notes">
      <div class="notes-grid">
        <div><h2>Measurement status</h2><ul>{coverage}</ul></div>
        <div><h2>Interpretation notes</h2><ul>{caveats}</ul></div>
      </div>
    </section>
    <footer>Generated by <code>scripts/build_impact_report.py</code> from the authoritative public metrics snapshot.</footer>
  </main>
</body>
</html>
"""


def write_pdf(report: dict[str, Any], path: Path) -> None:
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            PageBreak,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "ReportLab is required for PDF output. Install "
            "scripts/impact-report-requirements.txt."
        ) from exc

    accent = colors.HexColor("#b11f4b")
    text = colors.HexColor("#242424")
    muted = colors.HexColor("#5c5c5c")
    border = colors.HexColor("#dedede")
    soft = colors.HexColor("#f5f5f5")
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ImpactTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=accent,
            alignment=TA_CENTER,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ImpactSubtitle",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=muted,
            alignment=TA_CENTER,
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ImpactSection",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=text,
            spaceBefore=8,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ImpactSmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=muted,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ImpactCell",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=text,
        )
    )

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(border)
        canvas.line(18 * mm, 13 * mm, 192 * mm, 13 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(muted)
        canvas.drawString(18 * mm, 8 * mm, report["links"]["html"])
        canvas.drawRightString(
            192 * mm,
            8 * mm,
            f"Page {document.page}",
        )
        canvas.restoreState()

    document = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title=report["subject"],
        author="AIBAST Agents Library",
        subject="Weekly and monthly public impact",
    )
    story = [
        Paragraph("AIBAST Agents Library", styles["ImpactTitle"]),
        Paragraph("Weekly &amp; Monthly Impact Report", styles["ImpactTitle"]),
        Paragraph(
            f"Snapshot {html.escape(report['generated_at'])}<br/>"
            f"{html.escape(report['links']['site'])}",
            styles["ImpactSubtitle"],
        ),
    ]
    week = report["periods"]["week"]
    month = report["periods"]["month"]
    for section, rows in grouped_metrics(report).items():
        story.append(Paragraph(html.escape(section), styles["ImpactSection"]))
        data = [
            [
                Paragraph("<b>Metric</b>", styles["ImpactCell"]),
                Paragraph("<b>Current</b>", styles["ImpactCell"]),
                Paragraph("<b>7-day</b>", styles["ImpactCell"]),
                Paragraph("<b>30-day</b>", styles["ImpactCell"]),
            ]
        ]
        for row in rows:
            data.append(
                [
                    Paragraph(html.escape(row["label"]), styles["ImpactCell"]),
                    Paragraph(
                        html.escape(format_number(row["value"], row["unit"])),
                        styles["ImpactCell"],
                    ),
                    Paragraph(
                        html.escape(
                            format_period_metric(
                                row,
                                week["metrics"][row["id"]],
                            )
                        ),
                        styles["ImpactCell"],
                    ),
                    Paragraph(
                        html.escape(
                            format_period_metric(
                                row,
                                month["metrics"][row["id"]],
                            )
                        ),
                        styles["ImpactCell"],
                    ),
                ]
            )
        table = Table(
            data,
            colWidths=[67 * mm, 28 * mm, 39 * mm, 39 * mm],
            repeatRows=1,
            hAlign="LEFT",
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), soft),
                    ("TEXTCOLOR", (0, 0), (-1, 0), text),
                    ("GRID", (0, 0), (-1, -1), 0.35, border),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.extend([table, Spacer(1, 4 * mm)])
    for key, title in (("week", "Top weekly movers"), ("month", "Top monthly movers")):
        story.append(Paragraph(title, styles["ImpactSection"]))
        groups = mover_groups(report["periods"][key])
        if not groups:
            story.append(
                Paragraph(
                    "No complete dated baseline or non-zero movers yet.",
                    styles["ImpactSmall"],
                )
            )
        else:
            for label, rows in groups:
                story.append(
                    Paragraph(f"<b>{html.escape(label)}</b>", styles["ImpactSmall"])
                )
                for row in rows:
                    story.append(
                        Paragraph(
                            f"- {html.escape(format_mover(row))}",
                            styles["ImpactSmall"],
                        )
                    )
        story.append(Spacer(1, 3 * mm))
    story.extend(
        [
            PageBreak(),
            Paragraph("Measurement and interpretation", styles["ImpactSection"]),
        ]
    )
    for note in report["caveats"]:
        story.append(
            Paragraph(f"- {html.escape(note)}", styles["ImpactSmall"])
        )
        story.append(Spacer(1, 2 * mm))
    story.append(Spacer(1, 4 * mm))
    story.append(
        Paragraph(
            "Automation files: "
            f"{html.escape(report['links']['email'])} and "
            f"{html.escape(report['links']['json'])}",
            styles["ImpactSmall"],
        )
    )
    document.build(story, onFirstPage=footer, onLaterPages=footer)


def write_outputs(
    report: dict[str, Any],
    out_dir: Path,
    *,
    skip_pdf: bool = False,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        out_dir / "impact-report.json": json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        out_dir / "impact-report.html": render_html(report),
        out_dir / "impact-report-email.txt": render_email_text(report),
        out_dir / "impact-report-email.md": render_email_markdown(report),
    }
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
    written = list(outputs)
    if not skip_pdf:
        pdf = out_dir / "impact-report.pdf"
        write_pdf(report, pdf)
        written.append(pdf)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build weekly/monthly AIBAST impact report exports."
    )
    parser.add_argument("--metrics", default=str(DEFAULT_METRICS))
    parser.add_argument("--history", default=str(DEFAULT_HISTORY))
    parser.add_argument(
        "--metrics-history",
        default=str(DEFAULT_METRICS_HISTORY),
        help="source-specific daily traffic/CDN history",
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument(
        "--no-record",
        action="store_true",
        help="do not append the current snapshot to impact history",
    )
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="write JSON, HTML, and email text without PDF",
    )
    args = parser.parse_args()

    metrics_path = Path(args.metrics)
    history_path = Path(args.history)
    metrics_history_path = Path(args.metrics_history)
    out_dir = Path(args.out_dir)
    document = load_json(metrics_path, {})
    if not isinstance(document, dict) or document.get("schema") != "aibast-metrics/1.0":
        print(f"Invalid metrics snapshot: {metrics_path}", file=sys.stderr)
        return 1
    history = load_history(history_path)
    metrics_history = load_json(metrics_history_path, {})
    current = compact_snapshot(document)
    if not args.no_record:
        history = record_snapshot(history, current)
        history_path.parent.mkdir(parents=True, exist_ok=True)
        history_path.write_text(
            json.dumps(history, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    report = build_report(document, history, metrics_history)
    try:
        outputs = write_outputs(report, out_dir, skip_pdf=args.skip_pdf)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    for path in outputs:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
