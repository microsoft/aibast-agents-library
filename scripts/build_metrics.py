#!/usr/bin/env python3
"""
build_metrics.py — collect public AIBAST Agents Library metrics into state/metrics.json.

Sources (all public; only the GitHub traffic endpoints need a token):
  - registry.json                       agents, stacks, verticals, sizes, dates
  - api.github.com/repos/...            repository stars, forks, watchers, issues, releases
  - api.github.com/repos/.../issues     structured upvote, feedback, and AGI events
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
RAR_OWNER = os.environ.get("RAR_METRICS_OWNER", "kody-w")
RAR_REPO = os.environ.get("RAR_METRICS_REPO", "RAR")
GH_API = "https://api.github.com"
JSDELIVR = "https://data.jsdelivr.com/v1"
USER_AGENT = "aibast-metrics-builder"
TIMEOUT = 30
WORKSHOP_FEEDBACK_MARKER = "<!-- aibast-workshop-feedback:v1 -->"
WORKSHOP_FEEDBACK_SCHEMA = "aibast-workshop-feedback/1.0"
WORKSHOP_FEEDBACK_LABEL = "workshop-feedback"
AGENT_UPVOTE_MARKER = "<!-- aibast-agent-upvote:v1 -->"
AGENT_UPVOTE_SCHEMA = "aibast-agent-upvote/1.0"
AGI_PROGRESS_MARKER = "<!-- aibast-agi-progress:v1 -->"
AGI_PROGRESS_SCHEMA = "aibast-agi-progress/1.0"
AGI_PROGRESS_LABEL = "agi-progress"
AGI_ACHIEVEMENT_ORDER = (
    "started",
    "local-proof",
    "draft-builder",
    "preview-proven",
    "workshop-completed",
    "hard-mode-completed",
)
AGI_POINTS = {
    "started": 5,
    "local-proof": 15,
    "draft-builder": 20,
    "preview-proven": 25,
    "workshop-completed": 35,
    "hard-mode-completed": 50,
}
AGI_LABELS = {
    "started": "Started",
    "local-proof": "Local proof",
    "draft-builder": "Draft builder",
    "preview-proven": "Preview proven",
    "workshop-completed": "Workshop completed",
    "hard-mode-completed": "Hard mode completed",
}
AGI_CAVEAT = (
    "Agent Growth & Impact (AGI) Points are server-scored from opt-in public "
    "GitHub progress claims. Each explicitly claimed achievement has a fixed "
    "value: started 5, local-proof 15, draft-builder 20, preview-proven 25, "
    "workshop-completed 35, and hard-mode-completed 50, for at most 150 points "
    "per workshop. Re-syncing unions achievement IDs without duplicating "
    "points. Profiles are public by explicit submission consent. GitHub "
    "verification confirms authenticated issue authorship and canonical claim "
    "format only; achievement completion remains self-reported and is not "
    "independently proven. Verified public AGI remains separate from local "
    "self-paced state, repository stars, agent upvotes, downloads, and "
    "workshop usage events."
)

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
RAR_REGISTRY_SCHEMA = "rapp-registry/1.1"
RAR_METRICS_SCHEMA = "rar-metrics/1.0"
RAR_DISCUSSION_SCHEMA = "rar-discussion-ratings/1.0"
RAR_SIGNAL_IDS = (
    "worked",
    "did_not_work",
    "stuck",
    "regular_use",
    "shipped",
    "want_to_try",
    "saved_time",
)


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


def logical_agent_key(name):
    """Normalize a cross-registry logical identity without merging publishers."""
    value = str(name or "").strip().casefold()
    if "/" not in value:
        return None
    publisher, slug = value.split("/", 1)
    slug = re.sub(r"[_\s]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    if slug.endswith("-agent"):
        slug = slug[:-6].rstrip("-")
    return f"{publisher}/{slug}" if publisher and slug else None


def _sum_known(values):
    known = [value for value in values if _nonnegative_int(value) is not None]
    return sum(known) if known else None


def build_rar_source(
    registry,
    metrics,
    discussion_ratings,
    releases,
    *,
    generated_at,
):
    """Build a privacy-safe public RAR distribution and usage snapshot."""
    registry_valid = (
        isinstance(registry, dict)
        and registry.get("schema") == RAR_REGISTRY_SCHEMA
        and isinstance(registry.get("agents"), list)
    )
    if not registry_valid:
        return {
            "schema": "aibast-rar-federation/1.0",
            "status": "unavailable",
            "as_of": None,
            "carried_forward": False,
            "repo": f"{RAR_OWNER}/{RAR_REPO}",
            "coverage": {
                "registry": "unavailable",
                "cdn": "unavailable",
                "release_assets": "unavailable",
                "discussions": "unavailable",
                "traffic": "admin-token-required",
            },
            "totals": {
                "agents": None,
                "aibast_origin_agents": None,
                "agent_cdn_fetches": None,
                "agent_release_fetches": None,
                "agent_acquisitions": None,
                "positive_reactions": None,
                "comments": None,
                "usage_signals": {
                    signal: None for signal in RAR_SIGNAL_IDS
                },
                "repository_downloads": None,
                "repository_clones": None,
                "repository_page_views": None,
            },
            "aibast_origin": {},
            "agents": [],
        }

    agents = [
        agent
        for agent in registry["agents"]
        if isinstance(agent, dict)
        and isinstance(agent.get("name"), str)
        and agent["name"].startswith("@")
    ]
    registry_by_name = {agent["name"]: agent for agent in agents}
    metrics_valid = (
        isinstance(metrics, dict)
        and metrics.get("schema") == RAR_METRICS_SCHEMA
    )
    ratings_valid = (
        isinstance(discussion_ratings, dict)
        and discussion_ratings.get("schema") == RAR_DISCUSSION_SCHEMA
        and isinstance(discussion_ratings.get("agents"), dict)
    )
    releases_valid = isinstance(releases, list)

    cdn_by_agent = defaultdict(int)
    cdn_observed = set()
    if metrics_valid:
        for item in (metrics.get("cdn") or {}).get("files", []):
            if not isinstance(item, dict):
                continue
            name = item.get("agent")
            hits = _nonnegative_int(item.get("hits"))
            if name in registry_by_name and hits is not None:
                cdn_by_agent[name] += hits
                cdn_observed.add(name)

    install_names = {
        agent.get("_install_filename"): name
        for name, agent in registry_by_name.items()
        if agent.get("_install_filename")
    }
    release_by_agent = {
        name: 0 for name in registry_by_name
    } if releases_valid else {}
    unmapped_release_fetches = 0
    if releases_valid:
        for release in releases:
            if not isinstance(release, dict):
                continue
            for asset in release.get("assets", []):
                if not isinstance(asset, dict):
                    continue
                downloads = _nonnegative_int(asset.get("download_count"))
                if downloads is None:
                    continue
                agent_name = install_names.get(asset.get("name"))
                if agent_name:
                    release_by_agent[agent_name] += downloads
                else:
                    unmapped_release_fetches += downloads

    rating_rows = (
        discussion_ratings.get("agents", {})
        if ratings_valid
        else {}
    )
    rows = []
    usage_totals = {signal: 0 for signal in RAR_SIGNAL_IDS}
    acquisitions = 0
    positive_reactions = 0
    comments = 0
    for name, agent in sorted(registry_by_name.items()):
        rating = rating_rows.get(name) if ratings_valid else None
        signals = {}
        for signal in RAR_SIGNAL_IDS:
            value = (
                _nonnegative_int((rating.get("signals") or {}).get(signal))
                if isinstance(rating, dict)
                else None
            )
            signals[signal] = value
            if value is not None:
                usage_totals[signal] += value
        acquisition = (
            _nonnegative_int(rating.get("downloads"))
            if isinstance(rating, dict)
            else None
        )
        upvotes = (
            _nonnegative_int(rating.get("upvotes"))
            if isinstance(rating, dict)
            else None
        )
        comment_count = (
            _nonnegative_int(rating.get("comments"))
            if isinstance(rating, dict)
            else None
        )
        if acquisition is not None:
            acquisitions += acquisition
        if upvotes is not None:
            positive_reactions += upvotes
        if comment_count is not None:
            comments += comment_count
        publisher = name.split("/", 1)[0]
        rows.append({
            "rar_name": name,
            "display_name": agent.get("display_name") or name,
            "publisher": publisher,
            "file": agent.get("_file"),
            "install_filename": agent.get("_install_filename"),
            "sha256": agent.get("_sha256"),
            "logical_key": logical_agent_key(name),
            "aibast_origin": publisher == "@aibast-agents-library",
            "rar_cdn_fetches": (
                cdn_by_agent[name] if name in cdn_observed else None
            ),
            "rar_release_fetches": (
                release_by_agent.get(name) if releases_valid else None
            ),
            "rar_acquisitions": acquisition,
            "rar_positive_reactions": upvotes,
            "rar_comments": comment_count,
            "signals": signals,
            "discussion_url": (
                rating.get("url") if isinstance(rating, dict) else None
            ),
        })

    metric_totals = metrics.get("totals", {}) if metrics_valid else {}
    cdn_total = (
        _nonnegative_int(metric_totals.get("agent_file_downloads"))
        if metrics_valid
        else None
    )
    release_total = (
        sum(release_by_agent.values()) if releases_valid else None
    )
    aibast_rows = [row for row in rows if row["aibast_origin"]]
    coverage = {
        "registry": "available",
        "cdn": "censored" if metrics_valid else "unavailable",
        "release_assets": "available" if releases_valid else "unavailable",
        "discussions": "available" if ratings_valid else "unavailable",
        "traffic": (
            "available"
            if metrics_valid and (metrics.get("traffic") or {}).get("as_of")
            else "admin-token-required"
        ),
    }
    status = (
        "partial"
        if any(value != "available" for value in coverage.values())
        else "available"
    )
    return {
        "schema": "aibast-rar-federation/1.0",
        "status": status,
        "as_of": (
            metrics.get("generated_at")
            if metrics_valid
            else generated_at
        ),
        "carried_forward": False,
        "repo": f"{RAR_OWNER}/{RAR_REPO}",
        "site": f"https://{RAR_OWNER}.github.io/{RAR_REPO}/",
        "coverage": coverage,
        "totals": {
            "agents": len(rows),
            "aibast_origin_agents": len(aibast_rows),
            "agent_cdn_fetches": cdn_total,
            "agent_cdn_attributed_fetches": sum(cdn_by_agent.values()),
            "agent_release_fetches": release_total,
            "unmapped_release_fetches": (
                unmapped_release_fetches if releases_valid else None
            ),
            "agent_acquisitions": acquisitions if ratings_valid else None,
            "positive_reactions": (
                positive_reactions if ratings_valid else None
            ),
            "comments": comments if ratings_valid else None,
            "usage_signals": {
                signal: usage_totals[signal] if ratings_valid else None
                for signal in RAR_SIGNAL_IDS
            },
            "repository_downloads": (
                _nonnegative_int(metric_totals.get("downloads"))
                if metrics_valid
                else None
            ),
            "repository_clones": (
                _nonnegative_int(metric_totals.get("clones"))
                if metrics_valid
                else None
            ),
            "repository_page_views": (
                _nonnegative_int(metric_totals.get("page_views"))
                if metrics_valid
                else None
            ),
        },
        "aibast_origin": {
            "agents": len(aibast_rows),
            "cdn_fetches": _sum_known(
                row["rar_cdn_fetches"] for row in aibast_rows
            ),
            "release_fetches": _sum_known(
                row["rar_release_fetches"] for row in aibast_rows
            ),
            "acquisitions": _sum_known(
                row["rar_acquisitions"] for row in aibast_rows
            ),
            "usage_signals": {
                signal: _sum_known(
                    row["signals"][signal] for row in aibast_rows
                )
                for signal in RAR_SIGNAL_IDS
            },
        },
        "agents": rows,
        "caveat": (
            "RAR CDN and release fetches are distribution events, Discussion "
            "downloads are signed-in acquisition signals, and usage reactions "
            "are independent self-reports. They are never added together as users. "
            "Raw GitHub and Pages downloads remain unobservable."
        ),
    }


def fetch_public_releases(owner, repo, token=None, max_pages=20):
    releases = []
    for page in range(1, max_pages + 1):
        rows = fetch_public(
            f"{GH_API}/repos/{owner}/{repo}/releases"
            f"?per_page=100&page={page}",
            token,
        )
        if not isinstance(rows, list):
            return None
        releases.extend(rows)
        if len(rows) < 100:
            return releases
    return releases


def fetch_rar_source(token, generated_at):
    raw_base = (
        f"https://raw.githubusercontent.com/{RAR_OWNER}/{RAR_REPO}/main/"
    )
    registry = fetch_json(raw_base + "registry.json")
    metrics = fetch_json(raw_base + "state/metrics.json")
    discussion_ratings = fetch_json(
        raw_base + "state/discussion_ratings.json"
    )
    releases = fetch_public_releases(
        RAR_OWNER,
        RAR_REPO,
        token,
    )
    return build_rar_source(
        registry,
        metrics,
        discussion_ratings,
        releases,
        generated_at=generated_at,
    )


def carry_forward_rar_source(prior):
    previous = (
        (prior.get("ecosystem") or {}).get("sources") or {}
    ).get("rar")
    if not isinstance(previous, dict) or not previous.get("agents"):
        return build_rar_source(
            None,
            None,
            None,
            None,
            generated_at=now_iso(),
        )
    carried = json.loads(json.dumps(previous))
    carried["status"] = "partial"
    carried["carried_forward"] = True
    return carried


def build_ecosystem_metrics(
    agents,
    aibast_agent_fetches,
    rar_source,
    *,
    generated_at,
):
    local_keys = defaultdict(list)
    local_files = defaultdict(list)
    for name in agents:
        key = logical_agent_key(name)
        if key:
            local_keys[key].append(name)
        file_path = str(agents[name].get("file") or "").lstrip("/")
        if file_path:
            local_files[file_path].append(name)

    rar_rows = []
    matched_local = set()
    for row in rar_source.get("agents", []):
        item = dict(row)
        file_matches = local_files.get(
            str(item.get("file") or "").lstrip("/"),
            [],
        )
        matches = (
            file_matches
            if len(file_matches) == 1
            else local_keys.get(item.get("logical_key"), [])
        )
        canonical = matches[0] if len(matches) == 1 else None
        item["canonical_aibast_name"] = canonical
        if canonical:
            matched_local.add(canonical)
        rar_rows.append(item)
    rar_by_canonical = {
        row["canonical_aibast_name"]: row
        for row in rar_rows
        if row.get("canonical_aibast_name")
    }

    combined_rows = []
    for name, agent in sorted(agents.items()):
        rar = rar_by_canonical.get(name, {})
        direct = _nonnegative_int(agent.get("downloads"))
        rar_cdn = _nonnegative_int(rar.get("rar_cdn_fetches"))
        rar_release = _nonnegative_int(rar.get("rar_release_fetches"))
        combined_rows.append({
            "logical_name": name,
            "display_name": agent.get("display_name") or name,
            "publisher": name.split("/", 1)[0],
            "channels": ["aibast"] + (["rar"] if rar else []),
            "aibast_direct_agent_fetches": direct,
            "rar_name": rar.get("rar_name"),
            "rar_cdn_fetches": rar_cdn,
            "rar_release_fetches": rar_release,
            "combined_distribution_fetch_events": _sum_known(
                (direct, rar_cdn, rar_release)
            ),
            "rar_acquisitions": rar.get("rar_acquisitions"),
            "rar_positive_reactions": rar.get("rar_positive_reactions"),
            "rar_discussion_url": rar.get("discussion_url"),
            "rar_usage_signals": rar.get("signals") or {
                signal: None for signal in RAR_SIGNAL_IDS
            },
        })
    for rar in rar_rows:
        if rar.get("canonical_aibast_name"):
            continue
        rar_cdn = _nonnegative_int(rar.get("rar_cdn_fetches"))
        rar_release = _nonnegative_int(rar.get("rar_release_fetches"))
        combined_rows.append({
            "logical_name": rar["rar_name"],
            "display_name": rar.get("display_name") or rar["rar_name"],
            "publisher": rar.get("publisher"),
            "channels": ["rar"],
            "aibast_direct_agent_fetches": None,
            "rar_name": rar["rar_name"],
            "rar_cdn_fetches": rar_cdn,
            "rar_release_fetches": rar_release,
            "combined_distribution_fetch_events": _sum_known(
                (rar_cdn, rar_release)
            ),
            "rar_acquisitions": rar.get("rar_acquisitions"),
            "rar_positive_reactions": rar.get("rar_positive_reactions"),
            "rar_discussion_url": rar.get("discussion_url"),
            "rar_usage_signals": rar.get("signals") or {
                signal: None for signal in RAR_SIGNAL_IDS
            },
        })
    combined_rows.sort(
        key=lambda row: (
            -(row.get("combined_distribution_fetch_events") or 0),
            -(row.get("rar_acquisitions") or 0),
            row["logical_name"],
        )
    )

    rar_totals = rar_source.get("totals") or {}
    rar_cdn = _nonnegative_int(rar_totals.get("agent_cdn_fetches"))
    rar_release = _nonnegative_int(
        rar_totals.get("agent_release_fetches")
    )
    aibast_fetches = _nonnegative_int(aibast_agent_fetches)
    logical_keys = {
        key for key in local_keys if key
    } | {
        row["logical_key"]
        for row in rar_rows
        if row.get("logical_key")
    }
    rar_status = rar_source.get("status", "unavailable")
    status = (
        "available"
        if rar_status == "available" and aibast_fetches is not None
        else "partial"
        if rar_status in {"available", "partial"} or aibast_fetches is not None
        else "unavailable"
    )
    return {
        "schema": "aibast-ecosystem-metrics/1.0",
        "status": status,
        "as_of": generated_at,
        "totals": {
            "distribution_entries": len(agents)
            + (rar_totals.get("agents") or 0),
            "logical_agents": len(logical_keys),
            "overlap_agents": len(matched_local),
            "aibast_direct_agent_fetches": aibast_fetches,
            "rar_agent_cdn_fetches": rar_cdn,
            "rar_agent_release_fetches": rar_release,
            "combined_agent_distribution_fetch_events": _sum_known(
                (aibast_fetches, rar_cdn, rar_release)
            ),
            "rar_agent_acquisitions": rar_totals.get(
                "agent_acquisitions"
            ),
            "rar_positive_reactions": rar_totals.get(
                "positive_reactions"
            ),
            "rar_usage_signals": rar_totals.get("usage_signals") or {
                signal: None for signal in RAR_SIGNAL_IDS
            },
        },
        "sources": {
            "aibast": {
                "repo": f"{OWNER}/{REPO}",
                "agent_fetches": aibast_fetches,
                "agents": len(agents),
            },
            "rar": rar_source,
        },
        "agents": combined_rows,
        "caveat": (
            "Global distribution fetch events sum distinct observable AIBAST "
            "and RAR delivery channels. They do not identify people. RAR "
            "acquisitions and usage reactions remain separate because one person "
            "can create several signals and can remove a reaction later."
        ),
    }


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


def _agi_catalog_map(catalog):
    return {
        row.get("slug"): row
        for row in catalog
        if row.get("slug") and row.get("catalog_key")
    }


def _agi_field_value(raw):
    if raw != raw.strip() or not raw:
        return None
    if raw.startswith("`") or raw.endswith("`"):
        if not (raw.startswith("`") and raw.endswith("`")):
            return None
        value = raw[1:-1]
        if not value or "`" in value:
            return None
        return value
    if (
        len(raw) >= 2
        and raw[0] in {'"', "'"}
        and raw[-1] == raw[0]
    ):
        return None
    return raw


def parse_agi_claim(body, catalog):
    """Parse one strict opt-in AGI progress claim."""
    text = body or ""
    if not text.startswith(AGI_PROGRESS_MARKER):
        return None
    field_names = (
        "Schema",
        "Workshop",
        "Agent",
        "Achievements",
        "Source",
        "Source quest URL",
    )
    field_pattern = re.compile(
        rf"^(?:- )?({'|'.join(field_names)}): (.+)$"
    )
    quoted_pattern = re.compile(
        rf"^\s*>+\s*(?:- )?({'|'.join(field_names)}):"
    )
    field_like_pattern = re.compile(
        rf"^\s*(?:>+\s*)?(?:-\s*)?({'|'.join(field_names)})\s*:"
    )
    forbidden_field_pattern = re.compile(
        r"^\s*(?:>+\s*)?(?:-\s*)?"
        r"(?:Event|Achievement|Points|Point|Score)\s*:",
        re.IGNORECASE,
    )
    fields = defaultdict(list)
    for line in text.splitlines()[1:]:
        if quoted_pattern.match(line) or forbidden_field_pattern.match(line):
            return None
        match = field_pattern.match(line)
        if match:
            fields[match.group(1)].append(match.group(2))
        elif field_like_pattern.match(line):
            return None

    required_fields = (
        "Schema",
        "Workshop",
        "Agent",
        "Achievements",
    )
    source_values = fields["Source"] + fields["Source quest URL"]
    if (
        any(len(fields[name]) != 1 for name in required_fields)
        or len(source_values) != 1
    ):
        return None
    values = {
        name: _agi_field_value(fields[name][0])
        for name in required_fields
    }
    values["Source"] = _agi_field_value(source_values[0])
    if any(value is None for value in values.values()):
        return None

    workshop_map = _agi_catalog_map(catalog)
    workshop = values["Workshop"]
    expected = workshop_map.get(workshop)
    achievement_ids = [
        value.strip()
        for value in values["Achievements"].split(",")
    ]
    if (
        not achievement_ids
        or any(not value for value in achievement_ids)
        or len(set(achievement_ids)) != len(achievement_ids)
        or any(value not in AGI_POINTS for value in achievement_ids)
        or achievement_ids != sorted(
            achievement_ids,
            key=AGI_ACHIEVEMENT_ORDER.index,
        )
    ):
        return None
    claimed = set(achievement_ids)
    if any(value != "started" for value in claimed) and "started" not in claimed:
        return None
    if "workshop-completed" in claimed and not {
        "started",
        "local-proof",
        "draft-builder",
        "preview-proven",
    }.issubset(claimed):
        return None
    if "hard-mode-completed" in claimed and "started" not in claimed:
        return None
    if (
        values["Schema"] != AGI_PROGRESS_SCHEMA
        or expected is None
        or values["Agent"] != expected["catalog_key"]
    ):
        return None
    return {
        "workshop": workshop,
        "agent": values["Agent"],
        "achievements": achievement_ids,
        "source": values["Source"],
    }


def _github_login(login):
    value = (login or "").strip()
    if not re.fullmatch(
        r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?",
        value,
    ):
        return None
    return value


def _completion_rate(completions, starts):
    return round((completions / starts) * 100, 1) if starts else 0.0


def _achievement_completion_rate(achievements, starts):
    possible = starts * len(AGI_ACHIEVEMENT_ORDER)
    return round((achievements / possible) * 100, 1) if possible else 0.0


def group_agi_progress(issues, catalog, complete=True, as_of=None):
    """Union verified progress into public profiles without source issue content."""
    workshop_map = _agi_catalog_map(catalog)
    achievements_by_profile = defaultdict(lambda: defaultdict(set))
    display_logins = {}
    seen_achievements = set()
    diagnostics = {
        "accepted_issues": 0,
        "accepted_achievements": 0,
        "duplicate_achievements": 0,
        "invalid_issues": 0,
        "invalid_users": 0,
        "pull_requests": 0,
    }
    for issue in issues or []:
        if issue.get("pull_request"):
            diagnostics["pull_requests"] += 1
            continue
        claim = parse_agi_claim(issue.get("body", ""), catalog)
        login = _github_login((issue.get("user") or {}).get("login"))
        if not login:
            diagnostics["invalid_users"] += 1
            continue
        if not claim:
            diagnostics["invalid_issues"] += 1
            continue
        login_key = login.casefold()
        diagnostics["accepted_issues"] += 1
        prior_display = display_logins.get(login_key)
        display_logins[login_key] = min(
            (value for value in (prior_display, login) if value is not None),
            key=lambda value: (value.casefold(), value),
        )
        for achievement_id in claim["achievements"]:
            claim_key = (login_key, claim["workshop"], achievement_id)
            if claim_key in seen_achievements:
                diagnostics["duplicate_achievements"] += 1
                continue
            seen_achievements.add(claim_key)
            diagnostics["accepted_achievements"] += 1
            achievements_by_profile[login_key][claim["workshop"]].add(
                achievement_id
            )

    profiles = []
    workshop_counts = {
        slug: {
            "participants": 0,
            "points": 0,
            "achievements": 0,
            "starts": 0,
            "workshop_completions": 0,
            "hard_completions": 0,
            "achievement_counts": {
                achievement_id: 0
                for achievement_id in AGI_ACHIEVEMENT_ORDER
            },
        }
        for slug in workshop_map
    }
    achievement_claims = {
        achievement_id: set()
        for achievement_id in AGI_ACHIEVEMENT_ORDER
    }
    for login_key, workshops in achievements_by_profile.items():
        completed_workshops = sorted(
            slug for slug, achievement_ids in workshops.items()
            if "workshop-completed" in achievement_ids
        )
        badges = []
        points = 0
        achievement_count = 0
        starts = 0
        workshop_completions = 0
        hard_completions = 0
        for slug in sorted(workshops):
            achievement_ids = workshops[slug]
            workshop_points = sum(
                AGI_POINTS[achievement_id]
                for achievement_id in achievement_ids
            )
            points += workshop_points
            achievement_count += len(achievement_ids)
            starts += int("started" in achievement_ids)
            workshop_completions += int(
                "workshop-completed" in achievement_ids
            )
            hard_completions += int(
                "hard-mode-completed" in achievement_ids
            )
            workshop_counts[slug]["participants"] += 1
            workshop_counts[slug]["points"] += workshop_points
            workshop_counts[slug]["achievements"] += len(achievement_ids)
            workshop_counts[slug]["starts"] += int(
                "started" in achievement_ids
            )
            workshop_counts[slug]["workshop_completions"] += int(
                "workshop-completed" in achievement_ids
            )
            workshop_counts[slug]["hard_completions"] += int(
                "hard-mode-completed" in achievement_ids
            )
            for achievement_id in AGI_ACHIEVEMENT_ORDER:
                if achievement_id not in achievement_ids:
                    continue
                workshop_counts[slug]["achievement_counts"][
                    achievement_id
                ] += 1
                achievement_claims[achievement_id].add((login_key, slug))
                badges.append({
                    "workshop": slug,
                    "achievement": achievement_id,
                    "points": AGI_POINTS[achievement_id],
                })
        profiles.append({
            "login": display_logins[login_key],
            "points": points,
            "achievement_count": achievement_count,
            "starts": starts,
            "workshop_completions": workshop_completions,
            "hard_completions": hard_completions,
            "badges": badges,
            "achievement_ids": [
                f"{badge['workshop']}:{badge['achievement']}"
                for badge in badges
            ],
            "completed_workshops": completed_workshops,
        })
    profiles.sort(
        key=lambda row: (
            -row["points"],
            -row["achievement_count"],
            -row["workshop_completions"],
            -row["hard_completions"],
            row["login"].casefold(),
            row["login"],
        )
    )

    rows = []
    for slug, workshop in workshop_map.items():
        counts = workshop_counts[slug]
        rows.append({
            "slug": slug,
            "display_name": workshop["display_name"],
            "agent_name": workshop["catalog_key"],
            **counts,
            "completion_rate": _completion_rate(
                counts["workshop_completions"],
                counts["starts"],
            ),
            "hard_completion_rate": _completion_rate(
                counts["hard_completions"],
                counts["starts"],
            ),
            "achievement_completion_rate": _achievement_completion_rate(
                counts["achievements"],
                counts["starts"],
            ),
        })
    rows.sort(
        key=lambda row: (
            -row["points"],
            -row["achievements"],
            -row["workshop_completions"],
            -row["hard_completions"],
            -row["starts"],
            row["display_name"].casefold(),
            row["slug"],
        )
    )
    starts = sum(row["starts"] for row in profiles)
    workshop_completions = sum(
        row["workshop_completions"] for row in profiles
    )
    hard_completions = sum(row["hard_completions"] for row in profiles)
    points = sum(row["points"] for row in profiles)
    achievement_count = sum(row["achievement_count"] for row in profiles)
    achievement_rows = []
    for achievement_id in AGI_ACHIEVEMENT_ORDER:
        claims = achievement_claims[achievement_id]
        achievement_rows.append({
            "id": achievement_id,
            "label": AGI_LABELS[achievement_id],
            "points": AGI_POINTS[achievement_id],
            "claims": len(claims),
            "participants": len({login for login, _slug in claims}),
            "workshops": len({_slug for _login, _slug in claims}),
            "attainment_rate": _completion_rate(len(claims), starts),
        })
    return {
        "schema": "aibast-agi/2.0",
        "status": "available" if complete else "partial",
        "as_of": as_of,
        "carried_forward": False,
        "caveat": AGI_CAVEAT,
        "totals": {
            "participants": len(profiles),
            "points": points,
            "achievements": achievement_count,
            "starts": starts,
            "workshop_completions": workshop_completions,
            "hard_completions": hard_completions,
            "completion_rate": _completion_rate(
                workshop_completions,
                starts,
            ),
            "hard_completion_rate": _completion_rate(
                hard_completions,
                starts,
            ),
            "achievement_completion_rate": _achievement_completion_rate(
                achievement_count,
                starts,
            ),
        },
        "profiles": profiles,
        "workshops": rows,
        "achievements": achievement_rows,
        "coverage": {
            "status": "available" if complete else "partial",
            "scope": (
                "Public state=all GitHub issues whose body begins with the "
                "AGI progress marker and passes the exact schema, canonical "
                "workshop-primary-agent, ordered achievement subset, dependency, "
                "source, and public-login checks. Open, closed, and edited "
                "claims union by case-insensitive login/workshop/achievement."
            ),
            "diagnostics": diagnostics,
        },
    }


def unavailable_agi_metrics(catalog):
    rows = []
    for workshop in _agi_catalog_map(catalog).values():
        rows.append({
            "slug": workshop["slug"],
            "display_name": workshop["display_name"],
            "agent_name": workshop["catalog_key"],
            "participants": None,
            "points": None,
            "achievements": None,
            "starts": None,
            "workshop_completions": None,
            "hard_completions": None,
            "completion_rate": None,
            "hard_completion_rate": None,
            "achievement_completion_rate": None,
            "achievement_counts": {
                achievement_id: None
                for achievement_id in AGI_ACHIEVEMENT_ORDER
            },
        })
    rows.sort(key=lambda row: (row["display_name"].casefold(), row["slug"]))
    return {
        "schema": "aibast-agi/2.0",
        "status": "unavailable",
        "as_of": None,
        "carried_forward": False,
        "caveat": AGI_CAVEAT,
        "totals": {
            "participants": None,
            "points": None,
            "achievements": None,
            "starts": None,
            "workshop_completions": None,
            "hard_completions": None,
            "completion_rate": None,
            "hard_completion_rate": None,
            "achievement_completion_rate": None,
        },
        "profiles": [],
        "workshops": rows,
        "achievements": [
            {
                "id": achievement_id,
                "label": AGI_LABELS[achievement_id],
                "points": AGI_POINTS[achievement_id],
                "claims": None,
                "participants": None,
                "workshops": None,
                "attainment_rate": None,
            }
            for achievement_id in AGI_ACHIEVEMENT_ORDER
        ],
        "coverage": {
            "status": "unavailable",
            "scope": (
                "AGI claims were not read. Null means unavailable, not zero."
            ),
            "diagnostics": {},
        },
    }


def carry_forward_agi(prior, catalog):
    previous = prior.get("agi")
    canonical_slugs = set(_agi_catalog_map(catalog))
    if (
        not isinstance(previous, dict)
        or previous.get("schema") != "aibast-agi/2.0"
        or previous.get("status") == "unavailable"
        or {
            row.get("slug")
            for row in previous.get("workshops", [])
            if row.get("slug")
        } != canonical_slugs
    ):
        return unavailable_agi_metrics(catalog)
    carried = json.loads(json.dumps(previous))
    carried["carried_forward"] = True
    carried.setdefault("as_of", prior.get("generated_at"))
    carried["caveat"] = AGI_CAVEAT
    coverage = carried.setdefault("coverage", {})
    coverage["carried_forward"] = True
    return carried


def fetch_agi_progress(token, catalog, as_of=None):
    """Fetch marker-authoritative AGI progress from all public issue states."""
    page_result = fetch_issue_pages(token)
    if not page_result["available"]:
        return unavailable_agi_metrics(catalog)
    candidates = [
        issue
        for issue in page_result["issues"]
        if (issue.get("body") or "").startswith(AGI_PROGRESS_MARKER)
    ]
    result = group_agi_progress(
        candidates,
        catalog,
        complete=page_result["complete"],
        as_of=as_of,
    )
    result["coverage"].update({
        "pages": page_result["pages"],
        "issues_scanned": len(candidates),
    })
    return result


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
        "package_available": False,
        "files_available": False,
        "files_complete": False,
        "file_pages": 0,
        "workshop_downloads": group_workshop_downloads(
            [], workshop_slugs, complete=False
        ),
        "workshop_download_diagnostics": {},
    }
    pkg = fetch_json(f"{JSDELIVR}/stats/packages/gh/{OWNER}/{REPO}?period=year")
    if isinstance(pkg, dict):
        out["package_available"] = True
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

def merge_history(traffic, jsd, history=HISTORY, run_at=None):
    """Accumulate rolling-window daily rows so totals survive the 14-day cutoff.

    Also remembers the last successful traffic read. The Actions GITHUB_TOKEN is
    403 on the traffic endpoints, so an unauthenticated or CI run must not blank
    out figures a previous authorized run already established.
    """
    hist = load_json(
        history,
        {
            "clones": {},
            "views": {},
            "cdn": {},
            "tracking": {},
            "snapshots": [],
        },
    )
    run_at = run_at or now_iso()
    run_day = run_at[:10]
    tracking = hist.setdefault("tracking", {})
    for bucket, rows in (("clones", traffic.get("clones", {}).get("daily", [])),
                         ("views", traffic.get("views", {}).get("daily", []))):
        store = hist.setdefault(bucket, {})
        for row in rows:
            prev = store.get(row["date"], {"count": 0, "uniques": 0})
            store[row["date"]] = {
                "count": max(prev.get("count", 0), row["count"]),
                "uniques": max(prev.get("uniques", 0), row["uniques"]),
            }
        if traffic.get(bucket):
            tracking.setdefault(
                f"{bucket}_since",
                min(store) if store else run_day,
            )
            tracking[f"{bucket}_last"] = run_day
    cdn = hist.setdefault("cdn", {})
    for row in jsd.get("daily", []):
        cdn[row["date"]] = max(cdn.get(row["date"], 0), row["count"])
    if jsd.get("package_available"):
        tracking.setdefault("cdn_since", min(cdn) if cdn else run_day)
        tracking["cdn_last"] = run_day

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
    snap = {"at": run_at, **totals}
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
    rar_token = (
        os.environ.get("RAR_METRICS_TOKEN")
        or os.environ.get("RAR_GITHUB_TOKEN")
    )
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
        rar_source = carry_forward_rar_source(prior)
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
        agi = carry_forward_agi(prior, workshop_catalog)
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
        log("· public RAR federation")
        rar_source = fetch_rar_source(rar_token, generated_at)
        if rar_source["status"] == "unavailable":
            rar_source = carry_forward_rar_source(prior)
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
        log("· agi progress")
        agi = fetch_agi_progress(
            token,
            workshop_catalog,
            as_of=generated_at,
        )
        if agi["status"] == "unavailable":
            agi = carry_forward_agi(prior, workshop_catalog)
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
        hist_totals, daily, last_known = merge_history(
            traffic_raw,
            jsd,
            history,
            run_at=generated_at,
        )
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

    ecosystem = build_ecosystem_metrics(
        agents,
        remote_totals.get("agent_file_downloads"),
        rar_source,
        generated_at=generated_at,
    )

    doc = {
        "schema": "aibast-metrics/1.0",
        "generated_at": generated_at,
        "repo": {"owner": OWNER, "name": REPO,
                 "url": f"https://github.com/{OWNER}/{REPO}",
                 "site": f"https://{OWNER}.github.io/{REPO}/", **repo},
        "totals": {
            **remote_totals,
            "global_agent_distribution_fetch_events": ecosystem[
                "totals"
            ]["combined_agent_distribution_fetch_events"],
            "rar_agent_acquisitions": ecosystem["totals"][
                "rar_agent_acquisitions"
            ],
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
        "agi": agi,
        "ecosystem": ecosystem,
        "sources": [
            {"name": "GitHub Traffic API", "metric": "clones, views, popular paths (clones include this repo's own CI checkouts)", "url": f"{GH_API}/repos/{OWNER}/{REPO}/traffic/clones"},
            {"name": "jsDelivr CDN", "metric": "per-file download observations across every tracked repository file, including agents, skills, workshops, installers, documentation, code, and assets", "url": f"{JSDELIVR}/stats/packages/gh/{OWNER}/{REPO}"},
            {"name": "GitHub Releases", "metric": "release asset downloads", "url": f"{GH_API}/repos/{OWNER}/{REPO}/releases"},
            {"name": "GitHub Issues", "metric": "structured public agent upvotes, workshop feedback, and opt-in verified AGI progress syncs validated from issue bodies", "url": f"{GH_API}/repos/{OWNER}/{REPO}/issues?state=all"},
            {"name": "registry.json", "metric": "agents, stacks, verticals, categories", "url": f"https://{OWNER}.github.io/{REPO}/registry.json"},
            {"name": "Public RAR federation", "metric": "community agent CDN/release fetches, signed-in acquisitions, and separate usage reactions", "url": f"https://{RAR_OWNER}.github.io/{RAR_REPO}/stats.html"},
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
    log(
        f"  agi_status={agi['status']} "
        f"agi_participants={agi['totals']['participants']} "
        f"agi_points={agi['totals']['points']}"
    )
    log(
        f"  ecosystem_status={ecosystem['status']} "
        f"global_agent_fetches="
        f"{ecosystem['totals']['combined_agent_distribution_fetch_events']} "
        f"rar_acquisitions={ecosystem['totals']['rar_agent_acquisitions']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
