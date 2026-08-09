#!/usr/bin/env python3
"""
build_metrics.py — collect public AIBAST Agents Library metrics into state/metrics.json.

Sources (all public; only the GitHub traffic endpoints need a token):
  - registry.json                       agents, stacks, verticals, sizes, dates
  - api.github.com/repos/...            repository stars, forks, watchers, issues, releases
  - api.github.com/repos/.../issues     structured per-agent upvote events
  - api.github.com/.../traffic/*        clones, views, popular paths/referrers
  - data.jsdelivr.com                   CDN download hits, per-file + per-day

GitHub's traffic API only returns a 14-day rolling window, so daily rows are
merged into state/metrics_history.json keyed by date. That turns a rolling
window into an accumulating all-time total.

Counts vs uniques: clones, views, and CDN hits are plain event counts and
accumulate exactly. Uniques do NOT — GitHub reports uniques per window, so
summing daily uniques over-counts any machine active on more than one day.
The snapshot therefore publishes both: *_uniques_14d (GitHub's own figure,
authoritative) and *_uniques_daily_sum (an explicit upper bound).

This library ships installers, not just agent files, so the snapshot also
separates installer fetches (install.sh / install.ps1 / install.cmd) from
agent-template fetches — the two answer different questions: how many people
stood up a Brainstem, versus which industry templates they pulled.

Usage:
    python scripts/build_metrics.py                 # snapshot everything
    python scripts/build_metrics.py --offline       # local files only, no network
    GITHUB_TOKEN=xxx python scripts/build_metrics.py

Exit code is 0 even when network sources fail — partial metrics are still written.
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry.json"
SOLUTIONS_CATALOG = ROOT / "solutions" / "catalog.json"
OUT = ROOT / "state" / "metrics.json"
HISTORY = ROOT / "state" / "metrics_history.json"

OWNER = os.environ.get("METRICS_OWNER", "microsoft")
REPO = os.environ.get("METRICS_REPO", "aibast-agents-library")
GH_API = "https://api.github.com"
JSDELIVR = "https://data.jsdelivr.com/v1"
USER_AGENT = "aibast-metrics-builder"
TIMEOUT = 30
WORKSHOP_FEEDBACK_MARKER = "<!-- aibast-workshop-feedback:v1 -->"
WORKSHOP_FEEDBACK_SCHEMA = "aibast-workshop-feedback/1.0"
WORKSHOP_FEEDBACK_LABEL = "workshop-feedback"
AGENT_UPVOTE_MARKER = "<!-- aibast-agent-upvote:v1 -->"
AGENT_UPVOTE_SCHEMA = "aibast-agent-upvote/1.0"

# One-liner installers. A hit here is someone standing up a tier, not pulling
# an agent template, so it is counted and displayed separately.
INSTALLER_FILES = {
    "/install.sh", "/install.ps1", "/install.cmd", "/install.command",
    "/docs/install.sh", "/docs/install.ps1", "/docs/install.cmd", "/docs/install.command",
    "/community_rapp/install.sh", "/community_rapp/install.ps1",
}
# Catalog and deployment infrastructure — not an installable agent.
CATALOG_FILES = {"/registry.json", "/skill.md", "/azuredeploy.json", "/deploy.sh", "/deploy.ps1"}
FILE_KINDS = (
    "agent",
    "skill",
    "workshop",
    "source_bundle",
    "installer",
    "documentation",
    "catalog",
    "code",
    "asset",
)
FALLBACK_EXCLUDED_DIRS = {
    ".git",
    "work",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
}


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    print(msg, file=sys.stderr)


def request_json(url, token=None):
    """GET JSON. Returns (data, error) — error is None on success.

    Metrics are best-effort, but a caller that needs to explain a gap to a
    reader (the traffic endpoints) needs the reason, not just the absence.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = (json.loads(e.read().decode("utf-8")) or {}).get("message", "")
        except Exception:
            pass
        log(f"  ! {e.code} {url}{' — ' + detail if detail else ''}")
        return None, {"status": e.code, "message": detail or e.reason}
    except Exception as e:
        log(f"  ! {type(e).__name__} {url}: {e}")
        return None, {"status": None, "message": f"{type(e).__name__}: {e}"}


def fetch_json(url, token=None):
    """GET JSON, or None on any failure."""
    return request_json(url, token)[0]


def fetch_public(url, token=None):
    """Public GitHub endpoint, token first.

    A token that has not been SSO-authorized for the owning org gets 403 on this
    repository even though the data is public and an anonymous request succeeds.
    Falling back to anonymous keeps stars, forks and releases flowing instead of
    silently zeroing them out.
    """
    if token:
        d = fetch_json(url, token)
        if d is not None:
            return d
        log("  · token rejected — retrying anonymously")
    return fetch_json(url)


def load_json(path, default):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


# ---------------------------------------------------------------- local data

def build_agent_index(registry):
    """agent name -> record, plus file path -> name lookup."""
    agents = {}
    by_file = {}
    for a in registry.get("agents", []):
        name = a.get("name")
        rec = {
            "name": name,
            "display_name": a.get("display_name") or name,
            "publisher": (name or "@unknown/x").split("/")[0],
            "description": a.get("description", ""),
            "category": a.get("category", "general"),
            "tier": a.get("quality_tier", "community"),
            "version": a.get("version", ""),
            "author": a.get("author", ""),
            "tags": a.get("tags", [])[:6],
            "file": a.get("_file", ""),
            "stack": a.get("_stack"),
            "vertical": a.get("_stack_vertical"),
            "size_kb": a.get("_size_kb", 0),
            "lines": a.get("_lines", 0),
            "added_at": a.get("_added_at", ""),
            "downloads": 0,
        }
        agents[name] = rec
        if rec["file"]:
            by_file["/" + rec["file"].lstrip("/")] = name
    return agents, by_file


def build_workshop_catalog(registry, solution_catalog=None):
    """Resolve the canonical solution catalog through exact registry primaries."""
    catalog_doc = solution_catalog or load_json(SOLUTIONS_CATALOG, {})
    canonical = catalog_doc.get("solutions", catalog_doc)
    if not isinstance(canonical, dict):
        raise ValueError("solutions/catalog.json must contain a solutions object")
    agents = {agent.get("name"): agent for agent in registry.get("agents", [])}
    stacks = {
        stack.get("stack"): stack
        for stack in registry.get("stacks", [])
        if stack.get("stack")
    }
    workshops = []
    seen_slugs = set()
    for catalog_key, catalog_entry in canonical.items():
        primary = agents.get(catalog_key)
        if not primary:
            raise ValueError(f"canonical workshop primary missing from registry: {catalog_key}")
        solution = primary.get("_solution") or {}
        package = solution.get("package") or {}
        slug = package.get("slug")
        quest_url = package.get("quest_url")
        if not slug or not quest_url:
            raise ValueError(f"canonical workshop package incomplete: {catalog_key}")
        if slug in seen_slugs:
            raise ValueError(f"canonical workshop slug is not unique: {slug}")
        seen_slugs.add(slug)

        rules = [{"kind": "prefix", "path": f"solutions/{slug}/"}]
        primary_file = str(primary.get("_file") or "").lstrip("/")
        if primary_file:
            rules.append({"kind": "exact", "path": primary_file})
        stack = stacks.get(primary.get("_stack"))
        stack_path = str((stack or {}).get("path") or "").strip("/")
        if stack_path:
            rules.append({"kind": "prefix", "path": stack_path + "/"})
        workshops.append({
            "catalog_key": catalog_key,
            "slug": slug,
            "display_name": (
                (catalog_entry or {}).get("display_name")
                or solution.get("advertised_name")
                or primary.get("display_name")
                or catalog_key
            ),
            "quest_url": quest_url,
            "path_rules": rules,
        })
    return sorted(
        workshops,
        key=lambda row: (row["display_name"].casefold(), row["slug"]),
    )


def _excluded_repository_path(path):
    parts = Path(path).parts
    return (
        any(part in FALLBACK_EXCLUDED_DIRS for part in parts)
        or path.endswith((".tmp", ".temp", "~"))
    )


def tracked_repository_files(root=ROOT):
    """Return the deterministic tracked-file scope, preferring git."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=str(root),
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            paths = [
                path.decode("utf-8")
                for path in result.stdout.split(b"\0")
                if path
            ]
            return sorted(
                path for path in paths
                if not _excluded_repository_path(path)
            )
    except (OSError, UnicodeDecodeError):
        pass

    paths = []
    for candidate in root.rglob("*"):
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(root).as_posix()
        if not _excluded_repository_path(relative):
            paths.append(relative)
    return sorted(paths)


def classify_repository_file(path, agent_name=None):
    normalized = "/" + path.lstrip("/")
    name = Path(path).name.casefold()
    suffix = Path(path).suffix.casefold()
    if agent_name:
        return "agent"
    if name == "skill.md":
        return "skill"
    if re.match(r"^exports/[^/]+-source\.zip$", path):
        return "source_bundle"
    if normalized in INSTALLER_FILES:
        return "installer"
    if path.startswith("solutions/"):
        return "workshop"
    if (
        normalized in CATALOG_FILES
        or path in {"registry.json", "solutions/catalog.json"}
        or name in {"catalog.json", "registry.json"}
    ):
        return "catalog"
    if suffix in {".md", ".html", ".htm", ".txt", ".pdf", ".rst"}:
        return "documentation"
    if suffix in {
        ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".sh",
        ".ps1", ".cmd", ".bat", ".go", ".rs", ".java", ".cs", ".rb",
        ".php", ".sql", ".yml", ".yaml", ".toml",
    }:
        return "code"
    return "asset"


def build_file_scope(registry, workshop_catalog, paths=None):
    """Map every tracked file to a kind and explicit agent/workshop owner."""
    tracked = paths if paths is not None else tracked_repository_files()
    agent_by_file = {
        str(agent.get("_file") or "").lstrip("/"): agent.get("name")
        for agent in registry.get("agents", [])
        if agent.get("_file") and agent.get("name")
    }
    canonical_slugs = {row["slug"] for row in workshop_catalog}
    rows = []
    for path in sorted(set(tracked)):
        agent_name = agent_by_file.get(path)
        workshop_slug = None
        matches = _workshop_path_matches(path, workshop_catalog)
        if len(matches) == 1:
            workshop_slug = next(iter(matches))
        else:
            solution = re.match(r"^solutions/([^/]+)/", path)
            bundle = re.match(r"^exports/([^/]+)-source\.zip$", path)
            candidate = (
                solution.group(1) if solution
                else bundle.group(1) if bundle
                else None
            )
            if candidate in canonical_slugs:
                workshop_slug = candidate
        row = {
            "path": path,
            "kind": classify_repository_file(path, agent_name),
            "agent_name": agent_name,
            "workshop_slug": workshop_slug,
        }
        rows.append(row)
    return rows


def _file_metric_totals(rows):
    by_kind = {}
    for kind in FILE_KINDS:
        kind_rows = [row for row in rows if row["kind"] == kind]
        known = [row["downloads"] for row in kind_rows if row["downloads"] is not None]
        by_kind[kind] = {
            "files": len(kind_rows),
            "observed_files": len(known),
            "downloads": sum(known) if known else None,
        }
    known_downloads = [
        row["downloads"] for row in rows if row["downloads"] is not None
    ]
    totals = {
        "files": len(rows),
        "observed_files": len(known_downloads),
        "downloads": sum(known_downloads) if known_downloads else None,
        "by_kind": by_kind,
    }
    kind_total = _sum_available(
        values["downloads"] for values in by_kind.values()
    )
    if totals["downloads"] != kind_total:
        raise ValueError("file download totals do not reconcile by kind")
    return totals


def build_file_metrics(
    scope,
    observed_files=None,
    *,
    available=False,
    complete=False,
    as_of=None,
    diagnostics=None,
):
    """Join public jsDelivr observations to the complete tracked-file scope."""
    observed = {}
    for item in observed_files or []:
        path = normalize_repo_path(
            item.get("name"), allow_any_relative=True
        )
        hits = _nonnegative_int((item.get("hits") or {}).get("total"))
        if path is not None and hits is not None:
            observed[path] = hits
    scoped_paths = {row["path"] for row in scope}
    rows = []
    for base in scope:
        path = base["path"]
        if path in observed:
            downloads = observed[path]
            status = "observed" if downloads else "observed_zero"
        elif available and complete:
            downloads = 0
            status = "observed_zero"
        else:
            downloads = None
            status = "not_observed"
        rows.append({**base, "downloads": downloads, "status": status})
    result = {
        "schema": "aibast-file-metrics/1.0",
        "source_status": (
            "complete" if available and complete
            else "censored" if available
            else "unavailable"
        ),
        "as_of": as_of if available else None,
        "carried_forward": False,
        "totals": _file_metric_totals(rows),
        "rows": rows,
        "diagnostics": {
            **(diagnostics or {}),
            "unscoped_observed_files": len(set(observed) - scoped_paths),
        },
        "caveat": (
            "Only jsDelivr per-file observations are measurable. "
            "raw.githubusercontent.com, GitHub Pages, and direct GitHub downloads "
            "do not expose public per-file counters here."
        ),
    }
    return result


def carry_forward_file_metrics(scope, prior):
    previous = prior.get("file_metrics") or {}
    previous_rows = {
        row.get("path"): row
        for row in previous.get("rows", [])
        if row.get("path")
    }
    if not previous_rows:
        return build_file_metrics(scope)
    rows = []
    for base in scope:
        old = previous_rows.get(base["path"], {})
        downloads = old.get("downloads")
        if _nonnegative_int(downloads) is None:
            downloads = None
        rows.append({
            **base,
            "downloads": downloads,
            "status": old.get("status", "not_observed") if downloads is not None else "not_observed",
        })
    return {
        "schema": "aibast-file-metrics/1.0",
        "source_status": previous.get("source_status", "unavailable"),
        "as_of": previous.get("as_of") or prior.get("generated_at"),
        "carried_forward": True,
        "totals": _file_metric_totals(rows),
        "rows": rows,
        "diagnostics": previous.get("diagnostics", {}),
        "caveat": previous.get(
            "caveat",
            "Carried public jsDelivr per-file observations; direct download paths remain unobservable.",
        ),
    }


def apply_file_downloads_to_agents(agents, file_metrics):
    by_agent = {
        row["agent_name"]: row["downloads"]
        for row in file_metrics.get("rows", [])
        if row.get("agent_name")
    }
    for name, agent in agents.items():
        agent["downloads"] = by_agent.get(name)


def workshop_downloads_from_file_metrics(file_metrics, workshop_slugs):
    complete = file_metrics.get("source_status") == "complete"
    default = 0 if complete else None
    grouped = {
        slug: {"file_downloads": default, "bundle_downloads": default}
        for slug in workshop_slugs
    }
    for row in file_metrics.get("rows", []):
        slug = row.get("workshop_slug")
        downloads = row.get("downloads")
        if slug not in grouped or downloads is None:
            continue
        field = (
            "bundle_downloads"
            if row.get("kind") == "source_bundle"
            else "file_downloads"
        )
        if grouped[slug][field] is None:
            grouped[slug][field] = 0
        grouped[slug][field] += downloads
    return grouped


def file_download_summary(file_metrics, limit=40):
    rows = [
        row for row in file_metrics.get("rows", [])
        if isinstance(row.get("downloads"), int) and row["downloads"] > 0
    ]
    rows.sort(key=lambda row: (-row["downloads"], row["path"]))
    return [
        {
            "file": "/" + row["path"],
            "hits": row["downloads"],
            "agent": row.get("agent_name"),
            "workshop": row.get("workshop_slug"),
            "kind": row["kind"],
        }
        for row in rows[:limit]
    ]


def _nonnegative_int(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(value) or value < 0 or int(value) != value:
        return None
    return int(value)


def normalize_repo_path(value, allow_any_relative=False):
    """Normalize an exact path in this repository, rejecting lookalikes."""
    raw = str(value or "")
    parsed = urlsplit(raw)
    host = (parsed.hostname or "").casefold()
    path = parsed.path
    if parsed.scheme or parsed.netloc:
        if parsed.scheme not in {"http", "https"}:
            return None
        if host == "github.com":
            prefix = f"/{OWNER}/{REPO}/"
        elif host == f"{OWNER}.github.io":
            prefix = f"/{REPO}/"
        elif host == "raw.githubusercontent.com":
            prefix = f"/{OWNER}/{REPO}/main/"
        else:
            return None
        if not path.startswith(prefix):
            return None
        path = path[len(prefix):]
    else:
        if path.startswith(f"/{OWNER}/{REPO}/"):
            path = path[len(f"/{OWNER}/{REPO}/"):]
        elif path.startswith(f"/{REPO}/"):
            path = path[len(f"/{REPO}/"):]
        elif path.startswith(("/solutions/", "/agents/", "/exports/")):
            path = path[1:]
        elif allow_any_relative and path.startswith("/"):
            path = path[1:]
        elif not path.startswith(("solutions/", "agents/", "exports/")) and not allow_any_relative:
            return None

    decoded = unquote(path)
    if unquote(decoded) != decoded or "\\" in decoded:
        return None
    if decoded.startswith(("blob/main/", "tree/main/")):
        decoded = decoded.split("/", 2)[2]
    else:
        ref = re.match(r"^(?:blob|tree)/([0-9a-fA-F]{40})/(.+)$", decoded)
        if ref:
            decoded = ref.group(2)
    parts = decoded.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    return "/".join(parts)


def _workshop_path_matches(path, catalog):
    matches = set()
    for workshop in catalog:
        for rule in workshop.get("path_rules", []):
            rule_path = rule["path"]
            if (
                rule["kind"] == "exact" and path == rule_path
            ) or (
                rule["kind"] == "prefix"
                and (path == rule_path.rstrip("/") or path.startswith(rule_path))
            ):
                matches.add(workshop["slug"])
    return matches


def group_workshop_paths(paths, catalog, return_diagnostics=False):
    """Group strict, deduplicated GitHub popular-path observations."""
    if catalog and not isinstance(next(iter(catalog)), dict):
        catalog = [
            {
                "slug": slug,
                "path_rules": [{"kind": "prefix", "path": f"solutions/{slug}/"}],
            }
            for slug in catalog
        ]
    slugs = {row["slug"] for row in catalog}
    grouped = {
        slug: {
            "views_14d": None,
            "view_uniques_14d": None,
            "view_observed": False,
        }
        for slug in slugs
    }
    normalized_rows = {}
    diagnostics = {
        "duplicate_rows": 0,
        "conflicting_duplicates": [],
        "invalid_rows": 0,
        "rejected_rows": 0,
        "ambiguous_rows": 0,
        "observed_paths": 0,
    }
    for row in paths or []:
        path = normalize_repo_path(row.get("path"))
        count = _nonnegative_int(row.get("count"))
        uniques = _nonnegative_int(row.get("uniques"))
        if path is None:
            diagnostics["rejected_rows"] += 1
            continue
        if count is None or uniques is None:
            diagnostics["invalid_rows"] += 1
            continue
        previous = normalized_rows.get(path)
        if previous:
            if previous == (count, uniques):
                diagnostics["duplicate_rows"] += 1
            else:
                if path not in diagnostics["conflicting_duplicates"]:
                    diagnostics["conflicting_duplicates"].append(path)
                normalized_rows[path] = (
                    max(previous[0], count),
                    max(previous[1], uniques),
                )
            continue
        normalized_rows[path] = (count, uniques)

    for path, (count, uniques) in normalized_rows.items():
        matches = _workshop_path_matches(path, catalog)
        if not matches:
            continue
        if len(matches) != 1:
            diagnostics["ambiguous_rows"] += 1
            continue
        slug = next(iter(matches))
        bucket = grouped[slug]
        if not bucket["view_observed"]:
            bucket["views_14d"] = 0
            bucket["view_uniques_14d"] = 0
            bucket["view_observed"] = True
        bucket["views_14d"] += count
        bucket["view_uniques_14d"] += uniques
        diagnostics["observed_paths"] += 1
    result = {"counts": grouped, "diagnostics": diagnostics}
    return result if return_diagnostics else grouped


def group_workshop_downloads(
    files,
    workshop_slugs,
    return_diagnostics=False,
    complete=True,
):
    """Validate, deduplicate, and partition jsDelivr workshop file hits."""
    slugs = set(workshop_slugs)
    default = 0 if complete else None
    grouped = {
        slug: {"file_downloads": default, "bundle_downloads": default}
        for slug in slugs
    }
    normalized_rows = {}
    diagnostics = {
        "duplicate_rows": 0,
        "conflicting_duplicates": [],
        "invalid_rows": 0,
        "unmapped_rows": 0,
    }
    for row in files or []:
        name = normalize_repo_path(row.get("name"), allow_any_relative=True)
        hits = _nonnegative_int((row.get("hits") or {}).get("total"))
        if name is None or hits is None:
            diagnostics["invalid_rows"] += 1
            continue
        previous = normalized_rows.get(name)
        if previous is not None:
            if previous == hits:
                diagnostics["duplicate_rows"] += 1
            else:
                if name not in diagnostics["conflicting_duplicates"]:
                    diagnostics["conflicting_duplicates"].append(name)
                normalized_rows[name] = max(previous, hits)
            continue
        normalized_rows[name] = hits

    for name, hits in normalized_rows.items():
        solution = re.match(r"^solutions/([^/]+)/.+$", name)
        bundle = re.match(r"^exports/([^/]+)-source\.zip$", name)
        slug = None
        field = None
        if solution and solution.group(1) in slugs:
            slug = solution.group(1)
            field = "file_downloads"
        elif bundle and bundle.group(1) in slugs:
            slug = bundle.group(1)
            field = "bundle_downloads"
        if not slug:
            diagnostics["unmapped_rows"] += 1
            continue
        if grouped[slug][field] is None:
            grouped[slug][field] = 0
        grouped[slug][field] += hits
    result = {
        "counts": grouped,
        "diagnostics": diagnostics,
        "files": [
            {"name": "/" + name, "hits": {"total": hits}}
            for name, hits in sorted(normalized_rows.items())
        ],
    }
    return result if return_diagnostics else grouped


def parse_feedback_solution(body, workshop_slugs):
    """Return a canonical slug only for the exact workshop feedback schema."""
    text = body or ""
    if not text.startswith(WORKSHOP_FEEDBACK_MARKER):
        return None
    schema_lines = re.findall(
        rf"(?m)^- Schema: `{re.escape(WORKSHOP_FEEDBACK_SCHEMA)}`$",
        text,
    )
    solution_lines = re.findall(
        r"(?m)^- Solution: `@aibast-agents-library/([a-z0-9-]+)`$",
        text,
    )
    if (
        len(schema_lines) == 1
        and len(solution_lines) == 1
        and solution_lines[0] in set(workshop_slugs)
    ):
        return solution_lines[0]
    return None


def group_workshop_feedback(
    issues,
    workshop_slugs,
    return_diagnostics=False,
    complete=True,
):
    """Count strict, deduplicated feedback issue aggregates only."""
    slugs = set(workshop_slugs)
    default = 0 if complete else None
    grouped = {
        slug: {
            "feedback_reports": default,
            "feedback_open": default,
            "feedback_closed": default,
        }
        for slug in slugs
    }
    seen = set()
    diagnostics = {
        "duplicate_issues": 0,
        "invalid_issues": 0,
        "pull_requests": 0,
    }
    for issue in issues or []:
        if issue.get("pull_request"):
            diagnostics["pull_requests"] += 1
            continue
        identity = (
            ("number", issue.get("number"))
            if issue.get("number") is not None
            else ("id", issue.get("id"))
        )
        if identity[1] is None:
            diagnostics["invalid_issues"] += 1
            continue
        if identity in seen:
            diagnostics["duplicate_issues"] += 1
            continue
        seen.add(identity)
        slug = parse_feedback_solution(issue.get("body", ""), slugs)
        state = issue.get("state")
        if not slug or state not in {"open", "closed"}:
            diagnostics["invalid_issues"] += 1
            continue
        for field in ("feedback_reports", "feedback_open", "feedback_closed"):
            if grouped[slug][field] is None:
                grouped[slug][field] = 0
        grouped[slug]["feedback_reports"] += 1
        grouped[slug][f"feedback_{state}"] += 1
    result = {"counts": grouped, "diagnostics": diagnostics}
    return result if return_diagnostics else grouped


def fetch_issue_pages(token, label=None, page_size=100, max_pages=100):
    """Fetch all public issue pages available through numbered pagination."""
    issues = []
    pages = 0
    available = False
    for page in range(1, max_pages + 1):
        label_query = f"&labels={label}" if label else ""
        url = (
            f"{GH_API}/repos/{OWNER}/{REPO}/issues"
            f"?state=all&per_page={page_size}&page={page}{label_query}"
        )
        rows = fetch_public(url, token)
        if rows is None or not isinstance(rows, list):
            return {
                "issues": issues,
                "available": available,
                "complete": False,
                "pages": pages,
            }
        available = True
        pages += 1
        issues.extend(rows)
        if len(rows) < page_size:
            return {
                "issues": issues,
                "available": True,
                "complete": True,
                "pages": pages,
            }
    return {
        "issues": issues,
        "available": available,
        "complete": False,
        "pages": pages,
    }


def fetch_workshop_feedback(token, workshop_slugs):
    """Union labelled feedback with every valid marker-based feedback issue."""
    labelled = fetch_issue_pages(token, label=WORKSHOP_FEEDBACK_LABEL)
    unfiltered = fetch_issue_pages(token)
    if not labelled["available"] and not unfiltered["available"]:
        return {
            "status": "unavailable",
            "mode": "unavailable",
            "issues_scanned": 0,
            "pages": 0,
            "counts": {
                slug: {
                    "feedback_reports": None,
                    "feedback_open": None,
                    "feedback_closed": None,
                }
                for slug in workshop_slugs
            },
            "diagnostics": {},
        }

    candidates = list(labelled["issues"])
    candidates.extend(
        issue
        for issue in unfiltered["issues"]
        if (issue.get("body") or "").startswith(WORKSHOP_FEEDBACK_MARKER)
    )
    issues_by_id = {}
    for issue in candidates:
        identity = issue.get("id") or issue.get("number")
        if identity is not None:
            issues_by_id[identity] = issue
    issues = list(issues_by_id.values())
    complete = unfiltered["complete"]
    grouped = group_workshop_feedback(
        issues,
        workshop_slugs,
        return_diagnostics=True,
        complete=complete,
    )
    return {
        "status": "available" if complete else "partial",
        "mode": "workshop-feedback label + body marker union",
        "issues_scanned": len(issues),
        "pages": labelled["pages"] + unfiltered["pages"],
        "counts": grouped["counts"],
        "diagnostics": grouped["diagnostics"],
    }


def parse_agent_upvote(body, agent_names):
    """Return a canonical agent only for the exact upvote issue schema."""
    text = body or ""
    if not text.startswith(AGENT_UPVOTE_MARKER):
        return None
    schema_lines = re.findall(
        rf"(?m)^- Schema: (?:`{re.escape(AGENT_UPVOTE_SCHEMA)}`|"
        rf"{re.escape(AGENT_UPVOTE_SCHEMA)})$",
        text,
    )
    agent_matches = re.findall(
        r"(?m)^- Agent: (?:`(@aibast-agents-library/[a-z0-9-]+)`|"
        r"(@aibast-agents-library/[a-z0-9-]+))$",
        text,
    )
    agent_lines = [quoted or plain for quoted, plain in agent_matches]
    if (
        len(schema_lines) == 1
        and len(agent_lines) == 1
        and agent_lines[0] in set(agent_names)
    ):
        return agent_lines[0]
    return None


def group_agent_upvotes(issues, agent_names, complete=True):
    """Aggregate one vote per GitHub account and canonical agent."""
    names = set(agent_names)
    default = 0 if complete else None
    counts = {name: default for name in names}
    seen_votes = set()
    diagnostics = {
        "duplicate_votes": 0,
        "invalid_issues": 0,
        "pull_requests": 0,
        "open_votes": 0,
        "closed_votes": 0,
    }
    for issue in issues or []:
        if issue.get("pull_request"):
            diagnostics["pull_requests"] += 1
            continue
        agent = parse_agent_upvote(issue.get("body", ""), names)
        login = ((issue.get("user") or {}).get("login") or "").strip().casefold()
        state = issue.get("state")
        if not agent or not login or state not in {"open", "closed"}:
            diagnostics["invalid_issues"] += 1
            continue
        vote_key = (login, agent)
        if vote_key in seen_votes:
            diagnostics["duplicate_votes"] += 1
            continue
        seen_votes.add(vote_key)
        if counts[agent] is None:
            counts[agent] = 0
        counts[agent] += 1
        diagnostics[f"{state}_votes"] += 1
    return {
        "counts": counts,
        "total": _sum_available(counts.values()),
        "diagnostics": diagnostics,
    }


def fetch_agent_upvotes(token, agent_names):
    """Fetch all public issue pages; marker/body is the vote authority."""
    page_result = fetch_issue_pages(token)
    if not page_result["available"]:
        return {
            "status": "unavailable",
            "pages": 0,
            "issues_scanned": 0,
            "counts": {name: None for name in agent_names},
            "total": None,
            "diagnostics": {},
        }
    candidates = [
        issue for issue in page_result["issues"]
        if (issue.get("body") or "").startswith(AGENT_UPVOTE_MARKER)
    ]
    grouped = group_agent_upvotes(
        candidates,
        agent_names,
        complete=page_result["complete"],
    )
    return {
        "status": "available" if page_result["complete"] else "partial",
        "pages": page_result["pages"],
        "issues_scanned": len(candidates),
        **grouped,
    }


def _sum_available(values):
    available = [value for value in values if value is not None]
    return sum(available) if available else None


def build_workshop_metrics(
    catalog,
    path_rows=None,
    path_metrics=None,
    download_counts=None,
    feedback_counts=None,
    agent_upvotes=None,
    coverage=None,
):
    """Build sorted workshop rows and reconciled event-count totals."""
    path_result = path_metrics or group_workshop_paths(
        path_rows or [],
        catalog,
        return_diagnostics=True,
    )
    views = path_result["counts"]
    downloads = download_counts or {}
    feedback = feedback_counts or {}
    upvotes = agent_upvotes or {}
    rows = []
    for workshop in catalog:
        slug = workshop["slug"]
        view = views.get(slug, {})
        download = downloads.get(slug, {})
        feedback_row = feedback.get(slug, {})
        row = {
            "catalog_key": workshop.get("catalog_key"),
            "agent_name": workshop.get("catalog_key"),
            "slug": slug,
            "display_name": workshop["display_name"],
            "quest_url": workshop["quest_url"],
            "views_14d": view.get("views_14d"),
            "view_uniques_14d": view.get("view_uniques_14d"),
            "view_observed": bool(view.get("view_observed")),
            "file_downloads": download.get("file_downloads"),
            "bundle_downloads": download.get("bundle_downloads"),
            "feedback_reports": feedback_row.get("feedback_reports"),
            "feedback_open": feedback_row.get("feedback_open"),
            "feedback_closed": feedback_row.get("feedback_closed"),
            "agent_upvotes": upvotes.get(workshop.get("catalog_key")),
        }
        row["usage_events"] = _sum_available(
            row[field]
            for field in (
                "views_14d",
                "file_downloads",
                "bundle_downloads",
                "feedback_reports",
            )
        )
        if (
            row["feedback_reports"] is not None
            and row["feedback_reports"]
            != _sum_available((row["feedback_open"], row["feedback_closed"]))
        ):
            raise ValueError(f"feedback dimensions do not reconcile for {slug}")
        rows.append(row)
    rows.sort(
        key=lambda row: (
            -(row["usage_events"] if row["usage_events"] is not None else -1),
            -(row["views_14d"] if row["views_14d"] is not None else -1),
            row["display_name"].casefold(),
            row["slug"],
        )
    )
    totals = {
        "workshops": len(rows),
        "usage_events": _sum_available(row["usage_events"] for row in rows),
        "views_14d": _sum_available(row["views_14d"] for row in rows),
        "view_uniques_14d": _sum_available(
            row["view_uniques_14d"] for row in rows
        ),
        "file_downloads": _sum_available(row["file_downloads"] for row in rows),
        "bundle_downloads": _sum_available(
            row["bundle_downloads"] for row in rows
        ),
        "feedback_reports": _sum_available(
            row["feedback_reports"] for row in rows
        ),
        "feedback_open": _sum_available(row["feedback_open"] for row in rows),
        "feedback_closed": _sum_available(row["feedback_closed"] for row in rows),
        "agent_upvotes": _sum_available(row["agent_upvotes"] for row in rows),
    }
    source_totals = {
        field: totals[field]
        for field in (
            "views_14d",
            "file_downloads",
            "bundle_downloads",
            "feedback_reports",
        )
    }
    expected_usage = _sum_available(source_totals.values())
    row_usage = _sum_available(row["usage_events"] for row in rows)
    if totals["usage_events"] != expected_usage or totals["usage_events"] != row_usage:
        raise ValueError("workshop usage totals do not reconcile")
    return {
        "totals": totals,
        "source_totals": source_totals,
        "rows": rows,
        "usage_definition": (
            "usage_events is the sum of counted GitHub popular-path page views, "
            "jsDelivr workshop file downloads, jsDelivr source-bundle downloads, "
            "and public workshop feedback reports. It is an event floor, not users "
            "or unique usage. The sources use mixed measurement windows, and one "
            "person or action can create multiple events."
        ),
        "coverage": coverage or {
            "status": "unavailable",
            "views": {"status": "unavailable"},
            "downloads": {"status": "unavailable"},
            "feedback": {"status": "unavailable"},
        },
        "sources": [
            {
                "name": "GitHub Popular Paths API",
                "metric": "14-day workshop path views and path-level uniques; not complete GitHub Pages analytics",
                "url": f"{GH_API}/repos/{OWNER}/{REPO}/traffic/popular/paths",
            },
            {
                "name": "jsDelivr File Stats",
                "metric": "paginated workshop files under /solutions/<slug>/ and bundles at /exports/<slug>-source.zip",
                "url": f"{JSDELIVR}/stats/packages/gh/{OWNER}/{REPO}@main/files?period=year&limit=100&page=1",
            },
            {
                "name": "GitHub Issues API",
                "metric": "public workshop feedback issues identified by label or feedback marker",
                "url": f"{GH_API}/repos/{OWNER}/{REPO}/issues?state=all",
            },
            {
                "name": "GitHub Agent Upvote Issues",
                "metric": "validated per-agent preference events mapped to canonical workshop primaries; excluded from usage_events",
                "url": f"{GH_API}/repos/{OWNER}/{REPO}/issues?state=all",
            },
            {
                "name": "registry.json",
                "metric": "advertised workshop slugs, display names, and quest URLs",
                "url": f"https://{OWNER}.github.io/{REPO}/registry.json",
            },
        ],
    }


# --------------------------------------------------------------- remote data

def fetch_repo(token):
    d = fetch_public(f"{GH_API}/repos/{OWNER}/{REPO}", token)
    if not d:
        return {}
    stars = d.get("stargazers_count", 0)
    return {
        "stars": stars,
        "forks": d.get("forks_count", 0),
        "watchers": d.get("subscribers_count", 0),
        "open_issues": d.get("open_issues_count", 0),
        "size_kb": d.get("size", 0),
        "created_at": d.get("created_at"),
        "pushed_at": d.get("pushed_at"),
        "description": d.get("description"),
        "homepage": d.get("homepage"),
    }


def fetch_releases(token):
    rels = fetch_public(f"{GH_API}/repos/{OWNER}/{REPO}/releases?per_page=100", token) or []
    out, total = [], 0
    for r in rels:
        dl = sum(a.get("download_count", 0) for a in r.get("assets", []))
        total += dl
        out.append({
            "tag": r.get("tag_name"),
            "name": r.get("name"),
            "published_at": r.get("published_at"),
            "downloads": dl,
            "assets": [{"name": a["name"], "downloads": a.get("download_count", 0), "size": a.get("size", 0)}
                       for a in r.get("assets", [])],
        })
    return {"total_downloads": total, "count": len(out), "releases": out[:10]}


def traffic_gap(err):
    """Turn a traffic 403/404 into a sentence a reader can act on.

    The three failures look identical in the data (no numbers) and have
    completely different fixes, so the snapshot records which one happened.
    """
    if not err:
        return None
    msg = (err.get("message") or "").lower()
    if err.get("status") == 403 and "push access" in msg:
        return ("The token is valid for this repository but has read-only access. "
                "GitHub requires push access to read traffic; grant the account write "
                "on the repository, or set METRICS_TOKEN to a token from an account that has it.")
    if err.get("status") == 403 and "saml" in msg:
        return ("The token is not SSO-authorized for the owning organization. "
                "Authorize it for the org, or set METRICS_TOKEN to one that is.")
    if err.get("status") == 401:
        return "The token was rejected as invalid or expired."
    return f"GitHub returned {err.get('status') or 'an error'}: {err.get('message')}"


def fetch_traffic(token):
    """Clones + views + popular paths/referrers. Requires a push-scoped token.

    Returns the traffic dict; on failure it carries an `_error` key describing
    why, so the dashboard can say what is missing instead of showing a zero.
    """
    if not token:
        log("  · no token — skipping GitHub traffic")
        return {"_error": "No token was supplied, so the GitHub traffic endpoints were not called. "
                          "Set METRICS_TOKEN (needs push access to this repository) to start the series."}
    out = {}
    clones, err = request_json(f"{GH_API}/repos/{OWNER}/{REPO}/traffic/clones", token)
    if err:
        out["_error"] = traffic_gap(err)
    if clones:
        out["clones"] = {
            "count_14d": clones.get("count", 0),
            "uniques_14d": clones.get("uniques", 0),
            "daily": [{"date": c["timestamp"][:10], "count": c["count"], "uniques": c["uniques"]}
                      for c in clones.get("clones", [])],
        }
    views = fetch_json(f"{GH_API}/repos/{OWNER}/{REPO}/traffic/views", token)
    if views:
        out["views"] = {
            "count_14d": views.get("count", 0),
            "uniques_14d": views.get("uniques", 0),
            "daily": [{"date": v["timestamp"][:10], "count": v["count"], "uniques": v["uniques"]}
                      for v in views.get("views", [])],
        }
    paths = fetch_json(f"{GH_API}/repos/{OWNER}/{REPO}/traffic/popular/paths", token)
    if paths is not None:
        out["_paths_available"] = True
        out["paths"] = [{"path": p["path"], "title": p.get("title", ""), "count": p["count"], "uniques": p["uniques"]}
                        for p in paths[:20]]
    refs = fetch_json(f"{GH_API}/repos/{OWNER}/{REPO}/traffic/popular/referrers", token)
    if refs:
        out["referrers"] = [{"referrer": r["referrer"], "count": r["count"], "uniques": r["uniques"]} for r in refs[:12]]
    return out


def classify(name, is_agent):
    if is_agent:
        return "agent"
    if name in INSTALLER_FILES:
        return "installer"
    if name in CATALOG_FILES:
        return "catalog"
    return "asset"


def fetch_jsdelivr_file_pages(page_size=100, max_pages=100):
    """Fetch numbered jsDelivr file pages and detect ignored pagination."""
    rows = []
    pages = 0
    available = False
    previous_signature = None
    for page in range(1, max_pages + 1):
        url = (
            f"{JSDELIVR}/stats/packages/gh/{OWNER}/{REPO}@main/files"
            f"?period=year&limit={page_size}&page={page}"
        )
        batch = fetch_json(url)
        if batch is None or not isinstance(batch, list):
            return {
                "files": rows,
                "available": available,
                "complete": False,
                "pages": pages,
                "pagination": "request failed",
            }
        available = True
        signature = json.dumps(batch, sort_keys=True, separators=(",", ":"))
        if page > 1 and signature == previous_signature:
            return {
                "files": rows,
                "available": True,
                "complete": False,
                "pages": pages,
                "pagination": "page parameter unsupported",
            }
        previous_signature = signature
        pages += 1
        rows.extend(batch)
        if len(batch) < page_size:
            return {
                "files": rows,
                "available": True,
                "complete": True,
                "pages": pages,
                "pagination": "complete",
            }
    return {
        "files": rows,
        "available": available,
        "complete": False,
        "pages": pages,
        "pagination": "page limit reached",
    }


def fetch_jsdelivr(by_file, agents, workshop_slugs=()):
    """CDN hits: totals, daily series, and per-file download counts."""
    out = {
        "total_hits": 0,
        "bandwidth": 0,
        "daily": [],
        "files": [],
        "period": "year",
        "files_available": False,
        "files_complete": False,
        "file_pages": 0,
        "workshop_downloads": group_workshop_downloads(
            [], workshop_slugs, complete=False
        ),
        "workshop_download_diagnostics": {},
    }
    pkg = fetch_json(f"{JSDELIVR}/stats/packages/gh/{OWNER}/{REPO}?period=year")
    if pkg:
        out["total_hits"] = pkg.get("hits", {}).get("total", 0)
        out["bandwidth"] = pkg.get("bandwidth", {}).get("total", 0)
        out["rank"] = pkg.get("hits", {}).get("rank")
        dates = pkg.get("hits", {}).get("dates", {}) or {}
        out["daily"] = [{"date": d, "count": c} for d, c in sorted(dates.items()) if c]

    fetched = fetch_jsdelivr_file_pages()
    grouped = group_workshop_downloads(
        fetched["files"],
        workshop_slugs,
        return_diagnostics=True,
        complete=fetched["complete"],
    )
    files = grouped["files"]
    out["files_available"] = fetched["available"]
    out["files_complete"] = fetched["complete"]
    out["file_pages"] = fetched["pages"]
    out["file_pagination"] = fetched["pagination"]
    out["workshop_downloads"] = grouped["counts"]
    out["workshop_download_diagnostics"] = grouped["diagnostics"]
    out["observed_files"] = files
    rows = []
    for f in files:
        name = f.get("name", "")
        hits = f.get("hits", {}).get("total")
        if not hits:
            continue
        key = by_file.get(name)
        if key and key in agents:
            agents[key]["downloads"] += hits
        rows.append({
            "file": name,
            "hits": hits,
            "agent": agents[key]["name"] if key else None,
            "kind": classify(name, bool(key)),
        })
    rows.sort(key=lambda r: -r["hits"])
    out["files"] = rows[:40]
    out["agent_hits"] = sum(r["hits"] for r in rows if r["kind"] == "agent")
    out["installer_hits"] = sum(r["hits"] for r in rows if r["kind"] == "installer")
    return out


# ------------------------------------------------------------------ history

def merge_history(traffic, jsd, history=HISTORY):
    """Accumulate rolling-window daily rows so totals survive the 14-day cutoff.

    Also remembers the last successful traffic read. The Actions GITHUB_TOKEN is
    403 on the traffic endpoints, so an unauthenticated or CI run must not blank
    out figures a previous authorized run already established.
    """
    hist = load_json(history, {"clones": {}, "views": {}, "cdn": {}, "snapshots": []})
    for bucket, rows in (("clones", traffic.get("clones", {}).get("daily", [])),
                         ("views", traffic.get("views", {}).get("daily", []))):
        store = hist.setdefault(bucket, {})
        for row in rows:
            prev = store.get(row["date"], {"count": 0, "uniques": 0})
            store[row["date"]] = {
                "count": max(prev.get("count", 0), row["count"]),
                "uniques": max(prev.get("uniques", 0), row["uniques"]),
            }
    cdn = hist.setdefault("cdn", {})
    for row in jsd.get("daily", []):
        cdn[row["date"]] = max(cdn.get(row["date"], 0), row["count"])

    last = hist.setdefault("last_known", {})
    if traffic.get("clones"):
        last["clone_uniques_14d"] = traffic["clones"].get("uniques_14d", 0)
        last["clones_14d"] = traffic["clones"].get("count_14d", 0)
        last["at"] = now_iso()
    if traffic.get("views"):
        last["view_uniques_14d"] = traffic["views"].get("uniques_14d", 0)
        last["views_14d"] = traffic["views"].get("count_14d", 0)
    if traffic.get("_paths_available"):
        last["paths"] = traffic.get("paths", [])
        last["paths_at"] = now_iso()
    if traffic.get("referrers"):
        last["referrers"] = traffic["referrers"]

    totals = {
        "clones_all_time": sum(v["count"] for v in hist["clones"].values()),
        "clone_uniques_all_time": sum(v["uniques"] for v in hist["clones"].values()),
        "views_all_time": sum(v["count"] for v in hist["views"].values()),
        "view_uniques_all_time": sum(v["uniques"] for v in hist["views"].values()),
        "cdn_all_time": sum(hist["cdn"].values()),
        "days_tracked": len(hist["clones"]),
        "first_day": min(hist["clones"]) if hist["clones"] else None,
    }
    snap = {"at": now_iso(), **totals}
    hist.setdefault("snapshots", []).append(snap)
    hist["snapshots"] = hist["snapshots"][-365:]

    daily = []
    for day in sorted(set(hist["clones"]) | set(hist["views"]) | set(hist["cdn"]))[-90:]:
        daily.append({
            "date": day,
            "clones": hist["clones"].get(day, {}).get("count", 0),
            "clone_uniques": hist["clones"].get(day, {}).get("uniques", 0),
            "views": hist["views"].get(day, {}).get("count", 0),
            "cdn": hist["cdn"].get(day, 0),
        })

    history.parent.mkdir(parents=True, exist_ok=True)
    history.write_text(json.dumps(hist, indent=1, sort_keys=True) + "\n")
    return totals, daily, last


# ------------------------------------------------------------- leaderboards

def top(rows, key, n=15, require=True):
    out = sorted(rows, key=lambda r: (-(r.get(key) or 0), r["name"]))
    if require:
        out = [r for r in out if r.get(key)]
    return out[:n]


def slim(rec):
    fields = ("name", "display_name", "publisher", "category", "tier", "downloads", "upvotes",
              "lines", "size_kb", "added_at", "file", "description", "stack", "vertical")
    return {k: rec[k] for k in fields if k in rec}


def build_agent_metrics(agents):
    """Stable per-agent rows for library and metrics consumers."""
    return [
        {
            "name": rec["name"],
            "display_name": rec["display_name"],
            "downloads": rec.get("downloads"),
            "upvotes": rec.get("upvotes"),
            "file": rec.get("file"),
            "category": rec.get("category"),
            "stack": rec.get("stack"),
        }
        for rec in sorted(agents.values(), key=lambda row: row["name"])
    ]


def build_leaderboards(agents, registry):
    rows = list(agents.values())
    categories = defaultdict(lambda: {"agents": 0, "downloads": 0, "lines": 0})
    verticals = defaultdict(lambda: {"agents": 0, "downloads": 0, "stacks": set()})
    tiers = defaultdict(int)

    for r in rows:
        c = categories[r["category"]]
        c["agents"] += 1
        c["downloads"] += r["downloads"] or 0
        c["lines"] += r["lines"]
        if r["vertical"]:
            v = verticals[r["vertical"]]
            v["agents"] += 1
            v["downloads"] += r["downloads"] or 0
            if r["stack"]:
                v["stacks"].add(r["stack"])
        tiers[r["tier"]] += 1

    cat_rows = [{"name": k, **v} for k, v in categories.items()]
    cat_rows.sort(key=lambda r: -r["agents"])

    vert_rows = [{"name": k, "agents": v["agents"], "downloads": v["downloads"], "stacks": len(v["stacks"])}
                 for k, v in verticals.items()]
    vert_rows.sort(key=lambda r: -r["agents"])

    # Stacks are the unit customers actually deploy, so they get their own board.
    stack_rows = []
    for s in registry.get("stacks", []):
        members = [agents[n] for n in s.get("agents", []) if n in agents]
        member_downloads = [member["downloads"] for member in members]
        stack_rows.append({
            "name": s["stack"],
            "display_name": s.get("display_name", s["stack"]),
            "vertical": s.get("vertical", ""),
            "path": s.get("path", ""),
            "agents": len(members),
            "lines": sum(m["lines"] for m in members),
            "downloads": _sum_available(member_downloads),
        })
    stack_rows.sort(
        key=lambda row: (
            -(row["downloads"] if row["downloads"] is not None else -1),
            -row["agents"],
            row["name"],
        )
    )

    newest = [r for r in rows if r["added_at"]]
    newest.sort(key=lambda r: r["added_at"], reverse=True)
    most_upvoted = [
        slim(row)
        for row in sorted(
            (
                row for row in rows
                if isinstance(row.get("upvotes"), int) and row["upvotes"] > 0
            ),
            key=lambda row: (
                -row["upvotes"],
                -(row["downloads"] or 0),
                row["name"],
            ),
        )[:15]
    ]

    return {
        "most_downloaded": [slim(r) for r in top(rows, "downloads")],
        "most_upvoted": most_upvoted,
        "largest": [slim(r) for r in top(rows, "lines", n=15)],
        "newest": [slim(r) for r in newest[:15]],
        "stacks": stack_rows[:20],
        "categories": cat_rows,
        "verticals": vert_rows,
        "tiers": dict(sorted(tiers.items(), key=lambda kv: -kv[1])),
    }


# ----------------------------------------------------------------- assembly

REMOTE_TOTAL_FIELDS = (
    "downloads",
    "clones",
    "cdn_hits",
    "release_downloads",
    "agent_file_downloads",
    "installer_downloads",
    "skill_downloads",
    "agent_upvotes",
    "clones_excluding_ci_estimate",
    "ci_clone_estimate",
    "page_views",
    "clone_uniques_14d",
    "view_uniques_14d",
    "clone_uniques_daily_sum",
    "view_uniques_daily_sum",
    "days_tracked",
    "tracking_since",
)


def prior_agent_metric_map(prior, field):
    metrics = prior.get("agent_metrics")
    if isinstance(metrics, list):
        return {
            row.get("name"): row.get(field)
            for row in metrics
            if row.get("name")
        }
    if isinstance(metrics, dict):
        legacy_field = "d" if field == "downloads" else field
        return {
            name: (row or {}).get(legacy_field)
            for name, row in metrics.items()
        }
    return {}


def carried_block(prior, key):
    block = prior.get(key)
    if not isinstance(block, dict) or not block:
        return None
    carried = json.loads(json.dumps(block))
    carried["carried_forward"] = True
    carried.setdefault("as_of", prior.get("generated_at"))
    return carried


def unavailable_workshop_metrics(catalog, agent_upvotes=None):
    metrics = build_workshop_metrics(
        catalog,
        path_metrics={
            "counts": {
                row["slug"]: {
                    "views_14d": None,
                    "view_uniques_14d": None,
                    "view_observed": False,
                }
                for row in catalog
            },
            "diagnostics": {},
        },
        download_counts={
            row["slug"]: {
                "file_downloads": None,
                "bundle_downloads": None,
            }
            for row in catalog
        },
        feedback_counts={
            row["slug"]: {
                "feedback_reports": None,
                "feedback_open": None,
                "feedback_closed": None,
            }
            for row in catalog
        },
        agent_upvotes=agent_upvotes or {
            row["catalog_key"]: None for row in catalog
        },
        coverage={
            "status": "unavailable",
            "views": {"status": "unavailable"},
            "downloads": {"status": "unavailable"},
            "feedback": {"status": "unavailable"},
            "mixed_windows": True,
        },
    )
    metrics["as_of"] = None
    metrics["carried_forward"] = False
    return metrics


def carry_forward_workshops(
    catalog,
    prior,
    agent_upvotes=None,
    download_counts_override=None,
):
    previous = prior.get("workshops") or {}
    previous_rows = {
        row.get("slug"): row
        for row in previous.get("rows", [])
        if row.get("slug")
    }
    coverage = json.loads(json.dumps(previous.get("coverage") or {}))
    if not previous_rows or not coverage:
        return unavailable_workshop_metrics(catalog, agent_upvotes)

    def source_available(source):
        status = (coverage.get(source) or {}).get("status")
        return bool(status and status != "unavailable")

    views_available = source_available("views")
    downloads_available = source_available("downloads")
    feedback_available = source_available("feedback")
    path_counts = {}
    prior_download_counts = {}
    feedback_counts = {}
    for workshop in catalog:
        slug = workshop["slug"]
        old = previous_rows.get(slug, {})
        path_counts[slug] = {
            "views_14d": old.get("views_14d") if views_available else None,
            "view_uniques_14d": (
                old.get("view_uniques_14d") if views_available else None
            ),
            "view_observed": bool(old.get("view_observed")) if views_available else False,
        }
        prior_download_counts[slug] = {
            "file_downloads": old.get("file_downloads") if downloads_available else None,
            "bundle_downloads": (
                old.get("bundle_downloads") if downloads_available else None
            ),
        }
        feedback_counts[slug] = {
            "feedback_reports": (
                old.get("feedback_reports") if feedback_available else None
            ),
            "feedback_open": old.get("feedback_open") if feedback_available else None,
            "feedback_closed": (
                old.get("feedback_closed") if feedback_available else None
            ),
        }
    coverage["carried_forward"] = True
    metrics = build_workshop_metrics(
        catalog,
        path_metrics={"counts": path_counts, "diagnostics": {}},
        download_counts=download_counts_override or prior_download_counts,
        feedback_counts=feedback_counts,
        agent_upvotes=agent_upvotes or {
            row["catalog_key"]: None for row in catalog
        },
        coverage=coverage,
    )
    metrics["as_of"] = previous.get("as_of") or prior.get("generated_at")
    metrics["carried_forward"] = True
    return metrics

def main():
    ap = argparse.ArgumentParser(description="Build the public metrics snapshot for the AIBAST Agents Library.")
    ap.add_argument("--offline", action="store_true", help="skip all network calls")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    out_path = Path(args.out)
    prior = load_json(out_path, {})
    generated_at = now_iso()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    registry = load_json(REGISTRY, {})
    if not registry:
        log("✗ registry.json missing or unreadable — run build_registry.py first")
        return 1

    log("· indexing registry")
    agents, by_file = build_agent_index(registry)
    workshop_catalog = build_workshop_catalog(registry)
    workshop_slugs = [row["slug"] for row in workshop_catalog]
    agent_names = set(agents)
    file_scope = build_file_scope(registry, workshop_catalog)
    stats = registry.get("stats", {})

    if args.offline:
        repo = carried_block(prior, "repo") or {
            "stars": None,
            "forks": None,
            "watchers": None,
            "open_issues": None,
            "size_kb": None,
            "created_at": None,
            "pushed_at": None,
            "description": None,
            "homepage": None,
            "as_of": None,
            "carried_forward": False,
        }
        repo["stars"] = repo.get("stars")
        repo.pop("upvotes", None)
        prior_upvotes = prior_agent_metric_map(prior, "upvotes")
        for name, agent in agents.items():
            agent["upvotes"] = prior_upvotes.get(name)
        file_metrics = carry_forward_file_metrics(file_scope, prior)
        apply_file_downloads_to_agents(agents, file_metrics)
        agent_upvote_coverage = carried_block(
            prior, "agent_upvote_coverage"
        ) or {
            "status": (
                "carried_forward"
                if any(value is not None for value in prior_upvotes.values())
                else "unavailable"
            ),
            "as_of": (
                prior.get("generated_at")
                if any(value is not None for value in prior_upvotes.values())
                else None
            ),
            "carried_forward": any(
                value is not None for value in prior_upvotes.values()
            ),
        }
        releases = carried_block(prior, "releases") or {
            "total_downloads": None,
            "count": None,
            "releases": [],
            "as_of": None,
            "carried_forward": False,
        }
        cdn = carried_block(prior, "cdn") or {
            "total_hits": None,
            "bandwidth": None,
            "rank": None,
            "agent_hits": None,
            "installer_hits": None,
            "files": [],
            "as_of": None,
            "carried_forward": False,
        }
        traffic = carried_block(prior, "traffic") or {
            "paths": [],
            "referrers": [],
            "clones_14d": None,
            "views_14d": None,
            "live": False,
            "as_of": None,
            "unavailable_reason": (
                "Offline mode made zero network calls and no prior traffic "
                "snapshot was available."
            ),
            "carried_forward": False,
        }
        if traffic.get("carried_forward"):
            traffic["live"] = False
            traffic["unavailable_reason"] = (
                "Offline mode made zero network calls; traffic figures are "
                "carried forward from the original as_of timestamp."
            )
        workshops = carry_forward_workshops(
            workshop_catalog,
            prior,
            {name: agent.get("upvotes") for name, agent in agents.items()},
            workshop_downloads_from_file_metrics(
                file_metrics, workshop_slugs
            ),
        )
        workshops["coverage"]["agent_upvotes"] = {
            "status": agent_upvote_coverage["status"],
            "as_of": agent_upvote_coverage.get("as_of"),
            "carried_forward": agent_upvote_coverage.get(
                "carried_forward", False
            ),
            "scope": (
                "Canonical primary-agent upvotes carried separately from "
                "workshop usage events."
            ),
        }
        daily = prior.get("daily", []) if prior else []
        prior_totals = prior.get("totals") or {}
        remote_totals = {
            field: prior_totals.get(field) if prior else None
            for field in REMOTE_TOTAL_FIELDS
        }
        if remote_totals["agent_upvotes"] is None:
            remote_totals["agent_upvotes"] = _sum_available(
                prior_upvotes.values()
            )
        file_kind_totals = file_metrics["totals"]["by_kind"]
        remote_totals["agent_file_downloads"] = file_kind_totals["agent"]["downloads"]
        remote_totals["installer_downloads"] = file_kind_totals["installer"]["downloads"]
        remote_totals["skill_downloads"] = file_kind_totals["skill"]["downloads"]
        cdn["agent_hits"] = remote_totals["agent_file_downloads"]
        cdn["installer_hits"] = remote_totals["installer_downloads"]
        cdn["files"] = file_download_summary(file_metrics)
    else:
        repo = {}
        log("· github repo")
        repo = fetch_repo(token)
        log("· releases")
        releases = fetch_releases(token)
        log("· traffic")
        traffic_raw = fetch_traffic(token)
        log("· jsdelivr cdn")
        jsd = fetch_jsdelivr(by_file, agents, workshop_slugs)
        file_metrics = build_file_metrics(
            file_scope,
            jsd.get("observed_files", []),
            available=jsd.get("files_available", False),
            complete=jsd.get("files_complete", False),
            as_of=generated_at,
            diagnostics=jsd.get("workshop_download_diagnostics", {}),
        )
        apply_file_downloads_to_agents(agents, file_metrics)
        log("· workshop feedback")
        workshop_feedback = fetch_workshop_feedback(token, workshop_slugs)
        log("· agent upvotes")
        agent_upvotes = fetch_agent_upvotes(token, agent_names)
        for name, agent in agents.items():
            agent["upvotes"] = agent_upvotes["counts"].get(name)
        agent_upvote_coverage = {
            "status": agent_upvotes["status"],
            "as_of": (
                generated_at
                if agent_upvotes["status"] != "unavailable"
                else None
            ),
            "pages": agent_upvotes["pages"],
            "issues_scanned": agent_upvotes["issues_scanned"],
            "diagnostics": agent_upvotes["diagnostics"],
            "carried_forward": False,
            "scope": (
                "Public state=all GitHub issues whose body begins with the "
                "aibast-agent-upvote marker and exact schema. One GitHub account "
                "counts once per canonical agent; open and closed issues count."
            ),
        }

        stars = repo.get("stars") if repo else None
        repo["stars"] = stars
        repo["as_of"] = generated_at if repo else None
        repo["carried_forward"] = False
        releases["as_of"] = generated_at
        releases["carried_forward"] = False

        history = out_path.parent / HISTORY.name
        hist_totals, daily, last_known = merge_history(traffic_raw, jsd, history)
        traffic_live = bool(traffic_raw.get("clones"))
        traffic_error = traffic_raw.get("_error")
        traffic_paths = (
            traffic_raw.get("paths", [])
            if traffic_raw.get("_paths_available")
            else last_known.get("paths", [])
        )
        traffic = {
            "paths": traffic_paths,
            "referrers": (
                traffic_raw.get("referrers")
                or last_known.get("referrers", [])
            ),
            "clones_14d": (
                traffic_raw.get("clones", {}).get("count_14d")
                if traffic_raw.get("clones")
                else last_known.get("clones_14d", 0)
            ),
            "views_14d": (
                traffic_raw.get("views", {}).get("count_14d")
                if traffic_raw.get("views")
                else last_known.get("views_14d", 0)
            ),
            "live": traffic_live,
            "as_of": generated_at if traffic_live else last_known.get("at"),
            "unavailable_reason": None if traffic_live else traffic_error,
            "carried_forward": False,
        }

        if traffic_raw.get("_paths_available"):
            workshop_paths = traffic_raw.get("paths", [])
            workshop_view_status = "live popular-path response"
            workshop_view_as_of = generated_at
        elif "paths" in last_known:
            workshop_paths = last_known.get("paths", [])
            workshop_view_status = "last authorized popular-path response"
            workshop_view_as_of = last_known.get("paths_at") or last_known.get("at")
        else:
            workshop_paths = []
            workshop_view_status = "unavailable"
            workshop_view_as_of = None
        path_metrics = group_workshop_paths(
            workshop_paths,
            workshop_catalog,
            return_diagnostics=True,
        )
        workshop_download_status = (
            "complete paginated jsDelivr file response"
            if jsd.get("files_complete")
            else (
                "partial jsDelivr file response"
                if jsd.get("files_available")
                else "unavailable"
            )
        )
        workshop_feedback_status = (
            workshop_feedback.get("mode", "available")
            if workshop_feedback.get("status") in {"available", "partial"}
            else "unavailable"
        )
        workshop_statuses = (
            workshop_view_status,
            workshop_download_status,
            workshop_feedback_status,
        )
        workshop_coverage = {
            "status": (
                "unavailable"
                if all(status == "unavailable" for status in workshop_statuses)
                else "partial"
            ),
            "mixed_windows": True,
            "views": {
                "status": workshop_view_status,
                "as_of": workshop_view_as_of,
                "censored": True,
                "diagnostics": path_metrics["diagnostics"],
                "scope": (
                    "Observed GitHub popular-path rows only, limited to GitHub's "
                    "14-day top-path window; absent workshops are censored, not "
                    "verified zero. Path-level uniques can repeat across paths."
                ),
            },
            "downloads": {
                "status": workshop_download_status,
                "as_of": generated_at if jsd.get("files_available") else None,
                "pages": jsd.get("file_pages", 0),
                "pagination": jsd.get("file_pagination"),
                "diagnostics": jsd.get("workshop_download_diagnostics", {}),
                "scope": (
                    "Validated jsDelivr observations from the canonical tracked-file "
                    "ledger. Every file mapped to a workshop contributes once; "
                    "source bundles are partitioned from non-bundle files. Package "
                    "totals are not added. Raw GitHub, direct GitHub Pages, and "
                    "unattributed releases are uncounted."
                ),
            },
            "feedback": {
                "status": workshop_feedback_status,
                "as_of": generated_at if workshop_feedback.get("status") != "unavailable" else None,
                "issues_scanned": workshop_feedback.get("issues_scanned", 0),
                "pages": workshop_feedback.get("pages", 0),
                "diagnostics": workshop_feedback.get("diagnostics", {}),
                "scope": (
                    "Paginated public issues, deduplicated by number/id, excluding "
                    "pull requests, and requiring the marker at body start, exact "
                    "schema, and one canonical Solution field."
                ),
            },
            "agent_upvotes": {
                "status": agent_upvote_coverage["status"],
                "as_of": agent_upvote_coverage["as_of"],
                "scope": (
                    "Validated public agent-upvote issues mapped through each "
                    "workshop's canonical primary agent. This preference signal "
                    "is separate from usage_events."
                ),
            },
        }
        workshops = build_workshop_metrics(
            workshop_catalog,
            path_metrics=path_metrics,
            download_counts=workshop_downloads_from_file_metrics(
                file_metrics, workshop_slugs
            ),
            feedback_counts=workshop_feedback.get("counts", {}),
            agent_upvotes=agent_upvotes["counts"],
            coverage=workshop_coverage,
        )
        workshops["as_of"] = generated_at
        workshops["carried_forward"] = False

        release_dl = releases.get("total_downloads", 0)
        file_kind_totals = file_metrics["totals"]["by_kind"]
        agent_hits = file_kind_totals["agent"]["downloads"]
        installer_hits = file_kind_totals["installer"]["downloads"]
        skill_hits = file_kind_totals["skill"]["downloads"]
        daily_clones = sorted(
            value["count"]
            for value in load_json(history, {}).get("clones", {}).values()
        )
        ci_floor = daily_clones[0] if daily_clones else 0
        ci_estimate = ci_floor * len(daily_clones)
        clones_excl_ci = max(
            0,
            hist_totals["clones_all_time"] - ci_estimate,
        )
        remote_totals = {
            "downloads": (
                hist_totals["clones_all_time"]
                + hist_totals["cdn_all_time"]
                + release_dl
            ),
            "clones": hist_totals["clones_all_time"],
            "cdn_hits": hist_totals["cdn_all_time"],
            "release_downloads": release_dl,
            "agent_file_downloads": agent_hits,
            "installer_downloads": installer_hits,
            "skill_downloads": skill_hits,
            "agent_upvotes": agent_upvotes["total"],
            "clones_excluding_ci_estimate": clones_excl_ci,
            "ci_clone_estimate": ci_estimate,
            "page_views": hist_totals["views_all_time"],
            "clone_uniques_14d": (
                traffic_raw.get("clones", {}).get("uniques_14d")
                if traffic_raw.get("clones")
                else last_known.get("clone_uniques_14d", 0)
            ),
            "view_uniques_14d": (
                traffic_raw.get("views", {}).get("uniques_14d")
                if traffic_raw.get("views")
                else last_known.get("view_uniques_14d", 0)
            ),
            "clone_uniques_daily_sum": hist_totals["clone_uniques_all_time"],
            "view_uniques_daily_sum": hist_totals["view_uniques_all_time"],
            "days_tracked": hist_totals["days_tracked"],
            "tracking_since": hist_totals["first_day"],
        }
        cdn = {
            "total_hits": jsd["total_hits"],
            "bandwidth": jsd["bandwidth"],
            "rank": jsd.get("rank"),
            "agent_hits": agent_hits,
            "installer_hits": installer_hits,
            "files": file_download_summary(file_metrics),
            "as_of": generated_at if jsd.get("files_available") else None,
            "carried_forward": False,
        }

    doc = {
        "schema": "aibast-metrics/1.0",
        "generated_at": generated_at,
        "repo": {"owner": OWNER, "name": REPO,
                 "url": f"https://github.com/{OWNER}/{REPO}",
                 "site": f"https://{OWNER}.github.io/{REPO}/", **repo},
        "totals": {
            **remote_totals,
            "agents": stats.get("total_agents", len(agents)),
            "stacks": stats.get("total_stacks", 0),
            "verticals": stats.get("total_verticals", 0),
            "publishers": stats.get("publishers", 0),
            "categories": stats.get("categories", 0),
            "total_lines": sum(a["lines"] for a in agents.values()),
            "total_kb": round(sum(a["size_kb"] for a in agents.values()), 1),
        },
        "daily": daily,
        "traffic": traffic,
        "cdn": cdn,
        "releases": releases,
        "leaderboards": build_leaderboards(agents, registry),
        "agent_metrics": build_agent_metrics(agents),
        "agent_upvote_coverage": agent_upvote_coverage,
        "file_metrics": file_metrics,
        "workshops": workshops,
        "sources": [
            {"name": "GitHub Traffic API", "metric": "clones, views, popular paths (clones include this repo's own CI checkouts)", "url": f"{GH_API}/repos/{OWNER}/{REPO}/traffic/clones"},
            {"name": "jsDelivr CDN", "metric": "per-file download observations across every tracked repository file, including agents, skills, workshops, installers, documentation, code, and assets", "url": f"{JSDELIVR}/stats/packages/gh/{OWNER}/{REPO}"},
            {"name": "GitHub Releases", "metric": "release asset downloads", "url": f"{GH_API}/repos/{OWNER}/{REPO}/releases"},
            {"name": "GitHub Issues", "metric": "structured public agent upvotes and workshop feedback reports validated from issue bodies", "url": f"{GH_API}/repos/{OWNER}/{REPO}/issues?state=all"},
            {"name": "registry.json", "metric": "agents, stacks, verticals, categories", "url": f"https://{OWNER}.github.io/{REPO}/registry.json"},
        ],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(doc, indent=1) + "\n")
    t = doc["totals"]
    log(f"✓ {out_path}")
    log(f"  downloads={t['downloads']} (clones {t['clones']} + cdn {t['cdn_hits']} + releases {t['release_downloads']})")
    if traffic.get("unavailable_reason"):
        log(f"  · traffic unavailable: {traffic['unavailable_reason']}")
    log(f"  agents={t['agents']} stacks={t['stacks']} agent_files={t['agent_file_downloads']} "
        f"installers={t['installer_downloads']} agent_upvotes={t['agent_upvotes']}")
    log(f"  workshops={workshops['totals']['workshops']} "
        f"workshop_usage_events={workshops['totals']['usage_events']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
