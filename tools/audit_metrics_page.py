#!/usr/bin/env python3
"""Fail-closed preservation and workshop-theme audit for metrics.html."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PAGE = REPO_ROOT / "metrics.html"
DEFAULT_CONTRACT = REPO_ROOT / "state" / "metrics_page_contract.json"
TRUSTED_COMMIT = "9788f8faa24f7de33cc830da218f3aced6585584"
TRUSTED_PATH = "metrics.html"
TRUSTED_BLOB = "d78c8422eca6fdf22f73e8ecae4950ff5756a3f6"

SCOUT_THEME_SCRIPT = """(() => {
    const param = new URLSearchParams(window.location.search).get("scoutTheme");
    const theme =
      param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
  })();"""

LIGHT_THEME = {
    "--cp-bg": "#f7f4ef",
    "--cp-bg-elevated": "#fcfbf8",
    "--cp-surface": "#ffffff",
    "--cp-surface-soft": "#f5f5f5",
    "--cp-border": "#dedede",
    "--cp-border-strong": "#919191",
    "--cp-text": "#242424",
    "--cp-text-muted": "#5c5c5c",
    "--cp-text-soft": "#6f6f6f",
    "--cp-accent": "#b11f4b",
    "--cp-accent-hover": "#9a1a41",
    "--cp-accent-soft": "rgba(177, 31, 75, 0.08)",
    "--cp-accent-fg": "#ffffff",
    "--cp-success": "#16a34a",
    "--cp-danger": "#dc2626",
    "--cp-warning": "#f59e0b",
    "--cp-link": "#0078d4",
    "--cp-shadow": "0 18px 48px rgba(0, 0, 0, 0.12)",
    "--cp-overlay": "rgba(255, 255, 255, 0.8)",
    "--cp-panel": "rgba(255, 255, 255, 0.86)",
    "--cp-panel-strong": "rgba(255, 255, 255, 0.96)",
    "--cp-sheen": "rgba(255, 255, 255, 0.55)",
    "--cp-highlight": "rgba(177, 31, 75, 0.12)",
}

DARK_THEME = {
    "--cp-bg": "#3d3b3a",
    "--cp-bg-elevated": "#343231",
    "--cp-surface": "#292929",
    "--cp-surface-soft": "#2e2e2e",
    "--cp-border": "#474747",
    "--cp-border-strong": "#5f5f5f",
    "--cp-text": "#dedede",
    "--cp-text-muted": "#919191",
    "--cp-text-soft": "#b0b0b0",
    "--cp-accent": "#fd8ea1",
    "--cp-accent-hover": "#fb7b91",
    "--cp-accent-soft": "rgba(253, 142, 161, 0.14)",
    "--cp-accent-fg": "#1a1a1a",
    "--cp-success": "#4ade80",
    "--cp-danger": "#f87171",
    "--cp-warning": "#fbbf24",
    "--cp-link": "#4da6ff",
    "--cp-shadow": "0 18px 48px rgba(0, 0, 0, 0.32)",
    "--cp-overlay": "rgba(41, 41, 41, 0.88)",
    "--cp-panel": "rgba(41, 41, 41, 0.72)",
    "--cp-panel-strong": "rgba(41, 41, 41, 0.96)",
    "--cp-sheen": "rgba(255, 255, 255, 0.04)",
    "--cp-highlight": "rgba(253, 142, 161, 0.12)",
}

REQUIRED_FUNCTIONS = [
    "load",
    "getJSON",
    "liveTopUp",
    "render",
    "renderKPIs",
    "renderChart",
    "renderBoards",
    "renderStacks",
    "renderBars",
    "renderCDNFiles",
    "renderPaths",
    "renderReferrers",
    "renderReleases",
    "renderSources",
]

LEGACY_VARIABLES = {
    "--bg",
    "--surface",
    "--surface2",
    "--border",
    "--border-hover",
    "--text",
    "--text-dim",
    "--text-muted",
    "--accent",
    "--purple",
    "--green",
    "--orange",
    "--red",
}

SCHEMA_FIELDS = [
    "generated_at",
    "repo.stars",
    "repo.forks",
    "repo.open_issues",
    "totals.downloads",
    "totals.clones",
    "totals.cdn_hits",
    "totals.release_downloads",
    "totals.agent_file_downloads",
    "totals.installer_downloads",
    "totals.page_views",
    "totals.clone_uniques_14d",
    "totals.view_uniques_14d",
    "totals.clone_uniques_daily_sum",
    "totals.days_tracked",
    "totals.tracking_since",
    "totals.agents",
    "totals.stacks",
    "totals.verticals",
    "totals.total_lines",
    "totals.total_kb",
    "daily[].date",
    "daily[].clones",
    "daily[].views",
    "daily[].cdn",
    "traffic.live",
    "traffic.as_of",
    "traffic.unavailable_reason",
    "traffic.paths[].path",
    "traffic.paths[].count",
    "traffic.referrers[].referrer",
    "traffic.referrers[].count",
    "cdn.total_hits",
    "cdn.bandwidth",
    "cdn.rank",
    "cdn.files[].file",
    "cdn.files[].agent",
    "cdn.files[].kind",
    "cdn.files[].hits",
    "releases.releases[].tag",
    "releases.releases[].name",
    "releases.releases[].published_at",
    "releases.releases[].assets",
    "releases.releases[].downloads",
    "leaderboards.most_downloaded",
    "leaderboards.most_downloaded[].name",
    "leaderboards.most_downloaded[].display_name",
    "leaderboards.most_downloaded[].file",
    "leaderboards.most_downloaded[].tier",
    "leaderboards.most_downloaded[].category",
    "leaderboards.most_downloaded[].stack",
    "leaderboards.most_downloaded[].downloads",
    "leaderboards.newest",
    "leaderboards.newest[].name",
    "leaderboards.newest[].display_name",
    "leaderboards.newest[].file",
    "leaderboards.newest[].tier",
    "leaderboards.newest[].category",
    "leaderboards.newest[].stack",
    "leaderboards.newest[].added_at",
    "leaderboards.largest",
    "leaderboards.largest[].name",
    "leaderboards.largest[].display_name",
    "leaderboards.largest[].file",
    "leaderboards.largest[].tier",
    "leaderboards.largest[].category",
    "leaderboards.largest[].stack",
    "leaderboards.largest[].lines",
    "leaderboards.stacks",
    "leaderboards.stacks[].path",
    "leaderboards.stacks[].display_name",
    "leaderboards.stacks[].vertical",
    "leaderboards.stacks[].agents",
    "leaderboards.stacks[].lines",
    "leaderboards.stacks[].downloads",
    "leaderboards.verticals",
    "leaderboards.verticals[].name",
    "leaderboards.verticals[].agents",
    "leaderboards.verticals[].stacks",
    "leaderboards.categories",
    "leaderboards.categories[].name",
    "leaderboards.categories[].agents",
    "leaderboards.categories[].lines",
    "leaderboards.tiers",
    "sources[].name",
    "sources[].metric",
    "sources[].url",
]

SCHEMA_EVIDENCE = {
    "generated_at": ["M.generated_at"],
    "repo.stars": ["r.stars", "M.repo.stars"],
    "repo.forks": ["r.forks", "M.repo.forks"],
    "repo.open_issues": ["r.open_issues", "M.repo.open_issues"],
    "totals.downloads": ["t.downloads", "M.totals.downloads"],
    "totals.clones": ["t.clones"],
    "totals.cdn_hits": ["t.cdn_hits", "M.totals.cdn_hits"],
    "totals.release_downloads": ["t.release_downloads"],
    "totals.agent_file_downloads": ["t.agent_file_downloads"],
    "totals.installer_downloads": ["t.installer_downloads"],
    "totals.page_views": ["t.page_views"],
    "totals.clone_uniques_14d": ["t.clone_uniques_14d"],
    "totals.view_uniques_14d": ["t.view_uniques_14d"],
    "totals.clone_uniques_daily_sum": ["t.clone_uniques_daily_sum"],
    "totals.days_tracked": ["t.days_tracked"],
    "totals.tracking_since": ["t.tracking_since"],
    "totals.agents": ["t.agents"],
    "totals.stacks": ["t.stacks", "M.totals.stacks"],
    "totals.verticals": ["t.verticals"],
    "totals.total_lines": ["t.total_lines"],
    "totals.total_kb": ["t.total_kb"],
    "daily[].date": ["d.date"],
    "daily[].clones": ["d.clones"],
    "daily[].views": ["d.views"],
    "daily[].cdn": ["d.cdn"],
    "traffic.live": ["tr.live"],
    "traffic.as_of": ["tr.as_of"],
    "traffic.unavailable_reason": ["tr.unavailable_reason"],
    "traffic.paths[].path": ["p.path"],
    "traffic.paths[].count": ["p.count"],
    "traffic.referrers[].referrer": ["r.referrer"],
    "traffic.referrers[].count": ["r.count"],
    "cdn.total_hits": ["M.cdn.total_hits"],
    "cdn.bandwidth": ["M.cdn.bandwidth"],
    "cdn.rank": ["M.cdn.rank"],
    "cdn.files[].file": ["f.file"],
    "cdn.files[].agent": ["f.agent"],
    "cdn.files[].kind": ["f.kind"],
    "cdn.files[].hits": ["f.hits"],
    "releases.releases[].tag": ["r.tag"],
    "releases.releases[].name": ["r.name"],
    "releases.releases[].published_at": ["r.published_at"],
    "releases.releases[].assets": ["r.assets"],
    "releases.releases[].downloads": ["r.downloads"],
    "leaderboards.most_downloaded": ["most_downloaded"],
    "leaderboards.most_downloaded[].name": ["r.name"],
    "leaderboards.most_downloaded[].display_name": ["r.display_name"],
    "leaderboards.most_downloaded[].file": ["r.file"],
    "leaderboards.most_downloaded[].tier": ["r.tier"],
    "leaderboards.most_downloaded[].category": ["r.category"],
    "leaderboards.most_downloaded[].stack": ["r.stack"],
    "leaderboards.most_downloaded[].downloads": ["metric: 'downloads'"],
    "leaderboards.newest": ["newest"],
    "leaderboards.newest[].name": ["r.name"],
    "leaderboards.newest[].display_name": ["r.display_name"],
    "leaderboards.newest[].file": ["r.file"],
    "leaderboards.newest[].tier": ["r.tier"],
    "leaderboards.newest[].category": ["r.category"],
    "leaderboards.newest[].stack": ["r.stack"],
    "leaderboards.newest[].added_at": ["metric: 'added_at'"],
    "leaderboards.largest": ["largest"],
    "leaderboards.largest[].name": ["r.name"],
    "leaderboards.largest[].display_name": ["r.display_name"],
    "leaderboards.largest[].file": ["r.file"],
    "leaderboards.largest[].tier": ["r.tier"],
    "leaderboards.largest[].category": ["r.category"],
    "leaderboards.largest[].stack": ["r.stack"],
    "leaderboards.largest[].lines": ["metric: 'lines'"],
    "leaderboards.stacks": [".stacks"],
    "leaderboards.stacks[].path": ["s.path"],
    "leaderboards.stacks[].display_name": ["s.display_name"],
    "leaderboards.stacks[].vertical": ["s.vertical"],
    "leaderboards.stacks[].agents": ["s.agents"],
    "leaderboards.stacks[].lines": ["s.lines"],
    "leaderboards.stacks[].downloads": ["s.downloads"],
    "leaderboards.verticals": [".verticals"],
    "leaderboards.verticals[].name": ["v.name"],
    "leaderboards.verticals[].agents": ["v.agents"],
    "leaderboards.verticals[].stacks": ["v.stacks"],
    "leaderboards.categories": [".categories"],
    "leaderboards.categories[].name": ["c.name"],
    "leaderboards.categories[].agents": ["c.agents"],
    "leaderboards.categories[].lines": ["c.lines"],
    "leaderboards.tiers": [".tiers"],
    "sources[].name": ["s.name"],
    "sources[].metric": ["s.metric"],
    "sources[].url": ["s.url"],
}

FUNCTION_DATA = {
    "getJSON": [
        "paths",
        "fetch(",
        "cache: 'no-store'",
        ".ok",
        ".json()",
        "return null",
    ],
    "load": ["state/metrics.json", "M=", "render()", "liveTopUp()"],
    "liveTopUp": [
        "api.github.com/repos/",
        "data.jsdelivr.com/v1/stats/packages/gh/",
        "M.repo.stars",
        "M.repo.forks",
        "M.repo.open_issues",
        "M.totals.downloads",
        "M.totals.cdn_hits",
        "renderKPIs()",
    ],
    "render": [
        "M.generated_at",
        "M.traffic",
        "tr.live",
        "tr.as_of",
        "tr.unavailable_reason",
        "M.totals",
        "t.tracking_since",
        "t.days_tracked",
        "t.agents",
    ],
    "renderKPIs": [
        "M.totals",
        "M.repo",
        "t.downloads",
        "t.clones",
        "t.cdn_hits",
        "t.release_downloads",
        "t.agent_file_downloads",
        "t.installer_downloads",
        "t.agents",
        "t.stacks",
        "t.verticals",
        "t.total_lines",
        "t.total_kb",
        "t.clone_uniques_14d",
        "t.clone_uniques_daily_sum",
        "t.tracking_since",
        "t.page_views",
        "t.view_uniques_14d",
        "r.stars",
        "r.forks",
        "r.open_issues",
    ],
    "renderChart": ["M.daily", "d.date", "d.clones", "d.views", "d.cdn"],
    "renderBoards": [
        "M.leaderboards",
        "r[cfg.metric]",
        "r.file",
        "r.name",
        "r.display_name",
        "r.tier",
        "r.category",
        "r.stack",
    ],
    "renderStacks": [
        "M.leaderboards",
        ".stacks",
        "M.totals.stacks",
        "s.path",
        "s.display_name",
        "s.vertical",
        "s.agents",
        "s.lines",
        "s.downloads",
    ],
    "renderBars": ["r.label", "r.value"],
    "renderCDNFiles": [
        "M.cdn",
        "f.file",
        "f.agent",
        "f.kind",
        "f.hits",
        "M.cdn.total_hits",
        "M.cdn.bandwidth",
        "M.cdn.rank",
    ],
    "renderPaths": ["M.traffic", ".paths", "p.path", "p.count"],
    "renderReferrers": [
        "M.traffic",
        ".referrers",
        "r.referrer",
        "r.count",
    ],
    "renderReleases": [
        "M.releases",
        "rel.releases",
        "r.tag",
        "r.name",
        "r.published_at",
        "r.assets",
        "r.downloads",
    ],
    "renderSources": ["M.sources", "s.name", "s.metric", "s.url"],
}

POST_MIGRATION_REQUIREMENTS = {
    "headline": "Downloads, agent upvotes, and workshop usage",
    "heading": "Workshop adoption",
    "required_ids": [
        "workshop-summary",
        "workshop-hint",
        "workshop-coverage",
        "workshop-tabs",
        "workshop-table",
    ],
    "functions": ["renderWorkshops", "renderWorkshopControls"],
    "visible_phrases": [
        "Views cover only observed GitHub top popular-path rows in the 14-day API window",
        "Raw GitHub and direct GitHub Pages fetches are uncounted",
        "This is a floor and an event sum, not people, users, or unique usage",
        "These sources use mixed measurement windows",
        "one person or action can create multiple events",
        "Agent upvotes are preference signals shown separately and are never added to usage events",
    ],
    "agent_upvote_phrases": [
        "structured public GitHub issue submissions",
        "One GitHub account counts once per agent",
        "Opening the form is not a vote",
        "issue must be submitted",
    ],
    "forbidden_upvote_phrases": [
        "Community upvotes",
        "Upvote on GitHub",
    ],
    "kpi_fields": ["usage_events", "workshops"],
    "row_fields": [
        "slug",
        "display_name",
        "views_14d",
        "view_uniques_14d",
        "file_downloads",
        "bundle_downloads",
        "feedback_reports",
        "usage_events",
        "agent_upvotes",
        "agent_name",
    ],
    "quest_template": "solutions/${encodeURIComponent(row.slug)}/quest.html",
    "sorts": [
        {"id": "usage_events", "label": "Usage"},
        {"id": "views_14d", "label": "Views"},
        {"id": "file_downloads", "label": "File downloads"},
        {"id": "bundle_downloads", "label": "Bundle downloads"},
        {"id": "feedback_reports", "label": "Feedback"},
    ],
    "agent_upvote_sort": {"id": "agent_upvotes", "label": "Agent upvotes"},
    "agent_upvote_board": {
        "id": "most_upvoted",
        "label": "Most upvoted",
        "metric": "upvotes",
        "unit": "agent upvotes",
    },
    "agent_metrics_fields": [
        "name",
        "display_name",
        "file",
        "tier",
        "category",
        "stack",
        "upvotes",
    ],
    "admin_setup_href": "docs/metrics-admin-setup.html",
    "admin_guidance": ["METRICS_TOKEN", "Administration: read", "SSO"],
    "file_ledger": {
        "heading": "File downloads",
        "required_ids": [
            "file-download-ledger",
            "file-ledger-search",
            "file-ledger-kind",
            "file-ledger-sort",
            "file-ledger-summary",
            "file-ledger-table",
            "file-ledger-prev",
            "file-ledger-next",
            "file-ledger-page",
        ],
        "functions": [
            "fileKindLabel",
            "renderFileLedgerControls",
            "renderFileLedger",
        ],
        "visible_phrases": [
            "Every tracked repository file is represented",
            "raw.githubusercontent.com",
            "GitHub Pages",
            "direct GitHub downloads",
            "remain unobservable",
            "Complete coverage can report zero",
            "censored coverage keeps downloads unavailable",
            "null",
            "Workshop file and source-bundle totals reconcile from this ledger",
        ],
        "row_fields": [
            "path",
            "kind",
            "agent_name",
            "workshop_slug",
            "downloads",
            "status",
        ],
        "skill_kind": "Skill (SKILL.md)",
    },
}


def normalized_text(value: str) -> str:
    value = unescape(re.sub(r"<[^>]+>", " ", value))
    return " ".join(value.split()).casefold()


def normalized_visible_text(value: str) -> str:
    value = re.sub(r"<(?:script|style)\b.*?</(?:script|style)>", " ", value, flags=re.I | re.S)
    return normalized_text(value)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def compact_js(value: str) -> str:
    return re.sub(r"\s+", "", value)


def unexpected_color_literals(
    styles: str, theme_blocks: list[tuple[re.Match[str] | None, dict[str, str]]]
) -> list[str]:
    color_literal = re.compile(
        r"#[0-9a-fA-F]{3,8}\b|(?:rgb|rgba|hsl|hsla)\s*\([^)]*\)"
    )
    allowed: set[tuple[int, int]] = set()
    for block_match, variables in theme_blocks:
        if not block_match:
            continue
        block = block_match.group(1)
        offset = block_match.start(1)
        for name, value in variables.items():
            declaration = re.search(
                rf"{re.escape(name)}\s*:\s*({re.escape(value)})\s*;",
                block,
                re.I,
            )
            if not declaration:
                continue
            value_start = offset + declaration.start(1)
            for match in color_literal.finditer(declaration.group(1)):
                allowed.add(
                    (value_start + match.start(), value_start + match.end())
                )
    return [
        match.group()
        for match in color_literal.finditer(styles)
        if match.span() not in allowed
    ]


def attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    return {key: value or "" for key, value in attrs}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[dict[str, str]] = []
        self.tags: list[tuple[str, dict[str, str]]] = []
        self.headings: list[tuple[str, str]] = []
        self.scripts: list[tuple[dict[str, str], str]] = []
        self.styles: list[str] = []
        self._capture_tag: str | None = None
        self._capture_attrs: dict[str, str] = {}
        self._capture_parts: list[str] = []
        self._heading_tag: str | None = None
        self._heading_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = attrs_dict(attrs)
        self.tags.append((tag, data))
        if data.get("id"):
            self.ids.add(data["id"])
        if tag == "a":
            self.links.append(data)
        if tag in {"h1", "h2"}:
            self._heading_tag = tag
            self._heading_parts = []
        if tag in {"script", "style"}:
            self._capture_tag = tag
            self._capture_attrs = data
            self._capture_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == self._heading_tag:
            self.headings.append((tag, " ".join("".join(self._heading_parts).split())))
            self._heading_tag = None
        if tag == self._capture_tag:
            content = "".join(self._capture_parts)
            if tag == "script":
                self.scripts.append((self._capture_attrs, content))
            else:
                self.styles.append(content)
            self._capture_tag = None
            self._capture_attrs = {}
            self._capture_parts = []

    def handle_data(self, data: str) -> None:
        if self._heading_tag:
            self._heading_parts.append(data)
        if self._capture_tag:
            self._capture_parts.append(data)


def parse_page(html: str) -> PageParser:
    parser = PageParser()
    parser.feed(html)
    parser.close()
    return parser


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def trusted_source() -> str:
    resolved = git_output("rev-parse", f"{TRUSTED_COMMIT}:{TRUSTED_PATH}").strip()
    if resolved != TRUSTED_BLOB:
        raise RuntimeError(
            f"trusted provenance mismatch: {TRUSTED_COMMIT}:{TRUSTED_PATH} "
            f"resolved to {resolved}, expected {TRUSTED_BLOB}"
        )
    kind = git_output("cat-file", "-t", TRUSTED_BLOB).strip()
    if kind != "blob":
        raise RuntimeError(f"trusted object is {kind}, not blob")
    return git_output("cat-file", "blob", TRUSTED_BLOB)


def function_bodies(script: str) -> dict[str, str]:
    found: dict[str, str] = {}
    pattern = re.compile(r"(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{")
    for match in pattern.finditer(script):
        depth = 1
        quote: str | None = None
        escaped = False
        i = match.end()
        while i < len(script) and depth:
            char = script[i]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
            elif char in {"'", '"', "`"}:
                quote = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            i += 1
        found[match.group(1)] = script[match.end() : i - 1]
    return found


def extract_explanations(source: str) -> list[dict[str, str]]:
    section = re.search(
        r"<h2>Where these numbers come from</h2>.*?(?=<footer>)", source, re.S
    )
    if not section:
        raise RuntimeError("trusted source explanation section not found")
    paragraphs = re.findall(r'<p class="note"[^>]*>(.*?)</p>', section.group(), re.S)
    result = []
    for paragraph in paragraphs:
        text = normalized_text(paragraph)
        result.append({"sha256": digest(text), "normalized_text": text})
    if len(result) != 5:
        raise RuntimeError(f"expected 5 trusted source caveats, found {len(result)}")
    return result


def build_contract() -> dict:
    source = trusted_source()
    parser = parse_page(source)
    script = "\n".join(content for attrs, content in parser.scripts if not attrs.get("src"))
    bodies = function_bodies(script)
    target_map = {
        name: sorted(set(re.findall(r"""\$\(\s*['"]([^'"]+)['"]\s*\)""", body)))
        for name, body in bodies.items()
        if name in REQUIRED_FUNCTIONS
    }
    static_hrefs = []
    href_templates = []
    for link in parser.links:
        href = link.get("href", "")
        if not href:
            continue
        if "${" in href:
            if href not in href_templates:
                href_templates.append(href)
        elif href not in static_hrefs:
            static_hrefs.append(href)
    for href in re.findall(r"""<a\b[^>]*\bhref=['"]([^'"]+)['"]""", source, re.I):
        if "${" in href and href not in href_templates:
            href_templates.append(href)
    boards_match = re.search(r"const\s+BOARDS\s*=\s*(\[.*?\]);", script, re.S)
    if not boards_match:
        raise RuntimeError("trusted BOARDS definition not found")
    boards = [
        dict(zip(("id", "label", "metric", "unit"), values))
        for values in re.findall(
            r"\{\s*id:\s*'([^']+)'\s*,\s*label:\s*'([^']+)'\s*,"
            r"\s*metric:\s*'([^']+)'\s*,\s*unit:\s*'([^']+)'\s*\}",
            boards_match.group(1),
        )
    ]
    return {
        "contract_schema": "aibast-metrics-page-contract/1.0",
        "provenance": {
            "commit": TRUSTED_COMMIT,
            "path": TRUSTED_PATH,
            "blob": TRUSTED_BLOB,
            "blob_sha256": digest(source),
            "extraction": "git cat-file blob",
        },
        "preservation": {
            "headings": [
                {"level": tag, "text": text} for tag, text in parser.headings
            ],
            "required_ids": sorted(parser.ids),
            "chart_ids": ["chart"],
            "table_ids": ["stack-table"],
            "static_hrefs": static_hrefs,
            "href_templates": href_templates,
            "public_data_sources": [
                "state/metrics.json",
                "https://microsoft.github.io/aibast-agents-library/state/metrics.json",
                "https://api.github.com/repos/${OWNER}/${REPO}",
                "https://data.jsdelivr.com/v1/stats/packages/gh/${OWNER}/${REPO}?period=year",
            ],
            "functions": REQUIRED_FUNCTIONS,
            "function_targets": target_map,
            "function_data": FUNCTION_DATA,
            "boards": boards,
            "active_board": "most_downloaded",
            "schema_fields_consumed": SCHEMA_FIELDS,
            "schema_evidence": SCHEMA_EVIDENCE,
            "source_explanations": extract_explanations(source),
            "download_formula": {
                "components": [
                    "totals.clones",
                    "totals.cdn_hits",
                    "totals.release_downloads",
                ],
                "live_top_up": "M.totals.downloads += (hits - M.totals.cdn_hits)",
            },
            "distinct_fetch_metrics": [
                "totals.agent_file_downloads",
                "totals.installer_downloads",
            ],
            "render_inventory": {
                "renderKPIs": ["kpis"],
                "renderChart": ["chart"],
                "renderBoards": ["tabs", "board"],
                "renderStacks": ["stack-table"],
                "renderBars": ["vert-bars", "cat-bars", "tier-bars"],
                "renderCDNFiles": ["cdn-files"],
                "renderPaths": ["paths"],
                "renderReferrers": ["referrers"],
                "renderReleases": ["releases"],
                "renderSources": ["sources"],
            },
        },
        "post_migration": POST_MIGRATION_REQUIREMENTS,
        "workshop_theme": {
            "first_script": SCOUT_THEME_SCRIPT,
            "light_variables": LIGHT_THEME,
            "dark_variables": DARK_THEME,
            "sans_fonts": ["Segoe UI", "Aptos"],
            "mono_font": "Consolas",
            "topbar_links": [
                {"label": "Library", "href": "library.html"},
                {"label": "Production Guide", "href": "docs/rapp-guide.html"},
                {
                    "label": "Workshop settings",
                    "href": "solutions/_shared/workshop-settings.html",
                },
                {"label": "Metrics", "href": "metrics.html", "current": True},
                {
                    "label": "Report an issue",
                    "href_prefix": "https://github.com/microsoft/aibast-agents-library/issues/new",
                },
            ],
            "feedback_marker": "aibast-workshop-feedback:v1",
            "feedback_schema": "aibast-workshop-feedback/1.0",
        },
    }


@dataclass
class AuditResult:
    failures: dict[str, list[str]] = field(default_factory=dict)
    passes: dict[str, list[str]] = field(default_factory=dict)

    def fail(self, category: str, message: str) -> None:
        self.failures.setdefault(category, []).append(message)

    def ok(self, category: str, message: str) -> None:
        self.passes.setdefault(category, []).append(message)

    @property
    def passed(self) -> bool:
        return not self.failures


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


def find_tag(
    parser: PageParser, tag: str, *, element_id: str | None = None
) -> list[dict[str, str]]:
    return [
        attrs
        for current, attrs in parser.tags
        if current == tag and (element_id is None or attrs.get("id") == element_id)
    ]


def has_link(parser: PageParser, label: str, href: str | None = None) -> bool:
    for attrs in parser.links:
        if href is not None and attrs.get("href") != href:
            continue
        # The parser intentionally stores attributes only; label matching is done
        # against page text after href identity narrows the link.
        if href is not None:
            return True
    return False


def validate_javascript(result: AuditResult, parser: PageParser) -> None:
    scripts = [
        content
        for attrs, content in parser.scripts
        if not attrs.get("src")
        and attrs.get("type", "").casefold() not in {"application/json", "application/ld+json"}
        and content.strip()
    ]
    node = shutil.which("node")
    if not node:
        result.fail("javascript", "node is required to fail-closed on JavaScript syntax")
        return
    for index, script in enumerate(scripts, 1):
        checked = subprocess.run(
            [node, "--check", "-"],
            input=script,
            text=True,
            capture_output=True,
            check=False,
        )
        if checked.returncode:
            detail = (checked.stderr or checked.stdout).strip().splitlines()
            result.fail(
                "javascript",
                f"inline script {index} is malformed: "
                + (detail[-1] if detail else "node --check failed"),
            )
    if "javascript" not in result.failures:
        result.ok("javascript", f"{len(scripts)} inline scripts parse")


def audit_html(html: str, contract: dict) -> AuditResult:
    result = AuditResult()
    parser = parse_page(html)
    scripts = [content for attrs, content in parser.scripts if not attrs.get("src")]
    script = "\n".join(scripts)
    script_compact = compact_js(script)
    page_text = normalized_text(html)
    visible_page_text = normalized_visible_text(html)
    styles = "\n".join(parser.styles)
    preservation = contract["preservation"]
    post_migration = contract.get("post_migration")
    theme = contract["workshop_theme"]

    if not isinstance(post_migration, dict):
        result.fail("contract", "post-migration workshop requirements are missing")
        validate_javascript(result, parser)
        return result

    expected_headings = [
        (item["level"], item["text"]) for item in preservation["headings"]
    ]
    actual_contract_headings = [
        heading for heading in parser.headings if heading in expected_headings
    ]
    require(
        result,
        actual_contract_headings == expected_headings,
        "preservation",
        "static dashboard heading order changed or a heading is missing",
        "static dashboard headings and order preserved",
    )
    missing_ids = sorted(set(preservation["required_ids"]) - parser.ids)
    require(
        result,
        not missing_ids,
        "preservation",
        f"required dashboard IDs missing: {', '.join(missing_ids)}",
        "required dashboard IDs preserved",
    )
    for item in preservation["source_explanations"]:
        valid_hash = digest(item["normalized_text"]) == item["sha256"]
        require(
            result,
            valid_hash and item["normalized_text"] in page_text,
            "sources",
            f"source caveat missing or altered (sha256 {item['sha256']})",
        )
    for href in preservation["static_hrefs"]:
        require(
            result,
            has_link(parser, "", href),
            "links",
            f"existing public link missing: {href}",
        )
    for href in preservation["href_templates"]:
        require(
            result,
            href in html,
            "links",
            f"generated public link template missing: {href}",
        )
    for source in preservation["public_data_sources"]:
        candidates = {
            source,
            source.replace(
                "https://microsoft.github.io/aibast-agents-library/state/metrics.json",
                "SITE + 'state/metrics.json'",
            ),
        }
        require(
            result,
            any(candidate in html for candidate in candidates),
            "sources",
            f"public data source missing: {source}",
        )

    bodies = function_bodies(script)
    for function in preservation["functions"]:
        require(
            result,
            function in bodies,
            "javascript",
            f"required function missing: {function}",
        )
    for function, targets in preservation["function_targets"].items():
        body = bodies.get(function, "")
        found = set(re.findall(r"""\$\(\s*['"]([^'"]+)['"]\s*\)""", body))
        missing = sorted(set(targets) - found)
        require(
            result,
            not missing,
            "mappings",
            f"{function} lost contracted targets: {', '.join(missing)}",
        )
    for function, tokens in preservation["function_data"].items():
        body = compact_js(bodies.get(function, ""))
        missing = [token for token in tokens if compact_js(token) not in body]
        require(
            result,
            not missing,
            "mappings",
            f"{function} lost contracted data mappings: {', '.join(missing)}",
        )
    for function, targets in preservation["render_inventory"].items():
        haystack = bodies.get(function, "")
        for target in targets:
            require(
                result,
                target in haystack or f"renderBars('{target}'" in script,
                "mappings",
                f"{function} no longer renders contracted target {target}",
            )
    for field_name in preservation["schema_fields_consumed"]:
        evidence = preservation["schema_evidence"].get(field_name, [])
        require(
            result,
            bool(evidence) and any(token in script for token in evidence),
            "schema",
            f"metrics schema field is no longer consumed: {field_name}",
        )

    missing_workshop_ids = sorted(
        set(post_migration["required_ids"]) - parser.ids
    )
    require(
        result,
        not missing_workshop_ids,
        "workshops",
        f"required workshop IDs missing: {', '.join(missing_workshop_ids)}",
        "required workshop IDs present",
    )
    require(
        result,
        ("h2", post_migration["heading"]) in parser.headings,
        "workshops",
        "visible Workshop adoption heading is missing",
    )
    for phrase in post_migration["visible_phrases"]:
        require(
            result,
            normalized_text(phrase) in page_text,
            "workshops",
            f"workshop explanation missing or altered: {phrase}",
        )
    for function in post_migration["functions"]:
        require(
            result,
            function in bodies,
            "javascript",
            f"required function missing: {function}",
        )

    render_body = bodies.get("render", "")
    workshops_body = bodies.get("renderWorkshops", "")
    controls_body = bodies.get("renderWorkshopControls", "")
    require(
        result,
        re.search(r"\brenderWorkshops\s*\(", render_body) is not None,
        "workshops",
        "render() must invoke renderWorkshops()",
    )
    require(
        result,
        re.search(r"\brenderWorkshopControls\s*\(", workshops_body) is not None,
        "workshops",
        "renderWorkshops() must invoke renderWorkshopControls()",
    )

    kpi_body = bodies.get("renderKPIs", "")
    guarded_kpi_totals = re.search(
        r"(?:const|let|var)\s+workshopTotals\s*=\s*"
        r"(?:\(\s*M\.workshops\s*(?:\|\||\?\?)\s*\{\s*\}\s*\)\.totals"
        r"|M\.workshops\?\.totals)\s*(?:\|\||\?\?)\s*\{\s*\}",
        kpi_body,
    )
    require(
        result,
        guarded_kpi_totals is not None,
        "workshops",
        "Workshop KPI must guard absent M.workshops/totals for old snapshots",
    )
    for field_name in post_migration["kpi_fields"]:
        require(
            result,
            f"workshopTotals.{field_name}" in kpi_body,
            "workshops",
            f"Workshop KPI is not bound to workshops.totals.{field_name}",
        )

    guarded_workshops = re.search(
        r"(?:const|let|var)\s+workshops\s*=\s*M\.workshops\s*"
        r"(?:\|\||\?\?)\s*\{\s*\}",
        workshops_body,
    )
    guarded_totals = re.search(
        r"(?:const|let|var)\s+totals\s*=\s*workshops\.totals\s*"
        r"(?:\|\||\?\?)\s*\{\s*\}",
        workshops_body,
    )
    guarded_rows = re.search(
        r"Array\.isArray\s*\(\s*workshops\.rows\s*\)\s*\?"
        r"\s*workshops\.rows\.slice\s*\(\s*\)\s*:\s*\[\s*\]",
        workshops_body,
    )
    require(
        result,
        all((guarded_workshops, guarded_totals, guarded_rows)),
        "workshops",
        "renderWorkshops() must tolerate snapshots without the workshops schema",
    )
    for field_name in post_migration["row_fields"]:
        require(
            result,
            f"row.{field_name}" in workshops_body,
            "workshops",
            f"Workshop table row is not bound to {field_name}",
        )
    require(
        result,
        post_migration["quest_template"] in workshops_body,
        "workshops",
        "Workshop rows must link to solutions/<slug>/quest.html",
    )
    require(
        result,
        "${num(row.usage_events)}" in workshops_body
        and "${num(row.agent_upvotes)}" in workshops_body
        and workshops_body.index("${num(row.usage_events)}")
        < workshops_body.index("${num(row.agent_upvotes)}"),
        "workshops",
        "Workshop usage events and agent upvotes need separate table bindings",
    )
    require(
        result,
        re.search(
            r"usage_events\s*(?:\+?=|:).*?agent_upvotes"
            r"|agent_upvotes\s*(?:\+?=|:).*?usage_events"
            r"|row\.usage_events\s*\+\s*row\.agent_upvotes"
            r"|row\.agent_upvotes\s*\+\s*row\.usage_events",
            workshops_body,
            re.S,
        )
        is None,
        "workshops",
        "agent upvotes must never be added into workshop usage_events",
    )

    sort_match = re.search(
        r"const\s+WORKSHOP_SORTS\s*=\s*(\[.*?\]);", script, re.S
    )
    require(
        result,
        bool(sort_match),
        "workshops",
        "WORKSHOP_SORTS definition is missing",
    )
    if sort_match:
        observed_sorts = re.findall(
            r"\{\s*id:\s*['\"]([^'\"]+)['\"]\s*,\s*"
            r"label:\s*['\"]([^'\"]+)['\"]\s*\}",
            sort_match.group(1),
        )
        expected_sorts = [
            (item["id"], item["label"]) for item in post_migration["sorts"]
        ]
        require(
            result,
            observed_sorts == expected_sorts,
            "workshops",
            "workshop sort controls, labels, or order changed",
        )
    agent_sort = post_migration["agent_upvote_sort"]
    require(
        result,
        re.search(
            r"const\s+WORKSHOP_UPVOTE_SORT\s*=\s*\{\s*"
            rf"id:\s*['\"]{re.escape(agent_sort['id'])}['\"]\s*,\s*"
            rf"label:\s*['\"]{re.escape(agent_sort['label'])}['\"]\s*\}}\s*;",
            script,
            re.S,
        )
        is not None
        and "ALL_WORKSHOP_SORTS" in controls_body
        and "ALL_WORKSHOP_SORTS" in workshops_body,
        "workshops",
        "Agent upvotes workshop sort is missing or not wired separately",
    )
    require(
        result,
        "$('workshop-tabs')" in controls_body
        and "aria-pressed" in controls_body
        and 'aria-controls="workshop-table"' in controls_body
        and "data-workshop-sort" in controls_body,
        "workshops",
        "workshop sort controls need pressed state and workshop-table controls",
    )
    workshop_tabs = find_tag(parser, "div", element_id="workshop-tabs")
    require(
        result,
        bool(workshop_tabs)
        and workshop_tabs[0].get("role") == "group"
        and bool(workshop_tabs[0].get("aria-label")),
        "accessibility",
        "workshop sort controls need an accessible labelled group",
    )
    require(
        result,
        re.search(
            r"\$\(\s*['\"]workshop-tabs['\"]\s*\)\.addEventListener"
            r"\s*\(\s*['\"]click['\"].*?"
            r"activeWorkshopSort\s*=\s*control\.dataset\.workshopSort\s*;"
            r".*?renderWorkshops\s*\(\s*\)",
            script,
            re.S,
        )
        is not None,
        "workshops",
        "workshop controls must update activeWorkshopSort then rerender",
    )

    live_top_up = bodies.get("liveTopUp", "")
    require(
        result,
        re.search(
            r"M\s*(?:\.\s*workshops|\[\s*['\"]workshops['\"]\s*\])"
            r"|workshops\s*\.\s*rows",
            live_top_up,
        )
        is None,
        "workshops",
        "liveTopUp must not mutate per-workshop rows from package-wide CDN totals",
    )

    admin_href = post_migration["admin_setup_href"]
    permanent_admin_links = [
        attrs for attrs in parser.links if attrs.get("href") == admin_href
    ]
    require(
        result,
        bool(permanent_admin_links)
        and "admin setup checklist" in page_text,
        "admin",
        "permanent Admin setup checklist link is missing",
    )
    admin_body = bodies.get("appendAdminSetupNotice", "")
    require(
        result,
        admin_href in admin_body
        and "Admin setup checklist" in admin_body
        and all(token in admin_body for token in post_migration["admin_guidance"]),
        "admin",
        "conditional Admin setup checklist link or token guidance is incomplete",
    )
    require(
        result,
        re.search(
            r"if\s*\(\s*trafficUnavailable\s*\).*?"
            r"appendAdminSetupNotice\s*\(",
            render_body,
            re.S,
        )
        is not None
        and re.search(
            r"if\s*\([^)]*(?:coverage\.status|workshopViewsUnavailable)"
            r"[^)]*\).*?appendAdminSetupNotice\s*\(",
            workshops_body,
            re.S,
        )
        is not None,
        "admin",
        "Admin setup checklist must appear conditionally for traffic/workshop gaps",
    )
    for token in post_migration["admin_guidance"]:
        require(
            result,
            token.casefold() in page_text,
            "admin",
            f"permanent admin guidance is missing: {token}",
        )

    file_ledger = post_migration["file_ledger"]
    missing_file_ids = sorted(set(file_ledger["required_ids"]) - parser.ids)
    require(
        result,
        not missing_file_ids,
        "file-ledger",
        f"required file ledger IDs missing: {', '.join(missing_file_ids)}",
        "required file ledger IDs present",
    )
    require(
        result,
        ("h2", file_ledger["heading"]) in parser.headings,
        "file-ledger",
        "visible File downloads heading is missing",
    )
    for phrase in file_ledger["visible_phrases"]:
        require(
            result,
            normalized_text(phrase) in visible_page_text,
            "file-ledger",
            f"file ledger disclosure missing or altered: {phrase}",
        )
    for function in file_ledger["functions"]:
        require(
            result,
            function in bodies,
            "javascript",
            f"required function missing: {function}",
        )

    file_controls_body = bodies.get("renderFileLedgerControls", "")
    file_ledger_body = bodies.get("renderFileLedger", "")
    file_kind_body = bodies.get("fileKindLabel", "")
    require(
        result,
        re.search(r"\brenderFileLedger\s*\(", render_body) is not None
        and re.search(
            r"\brenderFileLedgerControls\s*\(", file_ledger_body
        )
        is not None,
        "file-ledger",
        "render() must invoke the file ledger, which must invoke its controls",
    )
    require(
        result,
        "Skill downloads" in kpi_body and "t.skill_downloads" in kpi_body,
        "file-ledger",
        "Skill downloads KPI must bind totals.skill_downloads",
    )
    require(
        result,
        re.search(r"kind\s*===\s*['\"]skill['\"]", file_kind_body) is not None
        and file_ledger["skill_kind"] in file_kind_body
        and "fileKindLabel(kind)" in file_controls_body,
        "file-ledger",
        "file kind controls must expose the SKILL.md filter",
    )
    require(
        result,
        "M.file_metrics" in file_ledger_body
        and re.search(
            r"Array\.isArray\s*\(\s*metrics\.rows\s*\)",
            file_ledger_body,
        )
        is not None,
        "file-ledger",
        "file ledger must tolerate snapshots without file_metrics rows",
    )
    for field_name in file_ledger["row_fields"]:
        require(
            result,
            f"row.{field_name}" in file_ledger_body,
            "file-ledger",
            f"file ledger row is not bound to {field_name}",
        )
    require(
        result,
        "${num(row.downloads)}" in file_ledger_body
        and re.search(
            r"num\s*\(\s*row\.downloads\s*(?:\?\?|\|\|)\s*0\s*\)",
            file_ledger_body,
        )
        is None,
        "file-ledger",
        "censored file downloads must remain unavailable/null, never fabricated zero",
    )
    require(
        result,
        "by_kind" in file_ledger_body
        and "Object.entries" in file_ledger_body,
        "file-ledger",
        "file ledger summary must expose totals by kind",
    )
    require(
        result,
        all(
            token in file_ledger_body
            for token in (
                "file-ledger-search",
                "file-ledger-kind",
                "file-ledger-sort",
                "file-ledger-summary",
                "file-ledger-table",
                "file-ledger-prev",
                "file-ledger-next",
                "file-ledger-page",
                "metrics.source_status",
            )
        ),
        "file-ledger",
        "file ledger controls, coverage summary, table, or pagination mapping is incomplete",
    )
    page_size_match = re.search(
        r"const\s+FILE_LEDGER_PAGE_SIZE\s*=\s*(\d+)", script
    )
    require(
        result,
        bool(page_size_match)
        and 1 <= int(page_size_match.group(1)) <= 100
        and "Math.min(Math.max(1, fileLedgerPage), pageCount)"
        in file_ledger_body
        and ".slice(start, start + FILE_LEDGER_PAGE_SIZE)"
        in file_ledger_body,
        "file-ledger",
        "file ledger pagination must be bounded to a finite page size",
    )
    search = find_tag(parser, "input", element_id="file-ledger-search")
    kind_select = find_tag(parser, "select", element_id="file-ledger-kind")
    sort_select = find_tag(parser, "select", element_id="file-ledger-sort")
    prev_button = find_tag(parser, "button", element_id="file-ledger-prev")
    next_button = find_tag(parser, "button", element_id="file-ledger-next")
    file_table = find_tag(parser, "table", element_id="file-ledger-table")
    require(
        result,
        bool(search)
        and search[0].get("type") == "search"
        and search[0].get("aria-controls") == "file-ledger-table"
        and bool(kind_select)
        and kind_select[0].get("aria-controls") == "file-ledger-table"
        and bool(sort_select)
        and sort_select[0].get("aria-controls") == "file-ledger-table"
        and bool(file_table)
        and bool(prev_button)
        and prev_button[0].get("type") == "button"
        and prev_button[0].get("aria-controls") == "file-ledger-table"
        and bool(next_button)
        and next_button[0].get("type") == "button"
        and next_button[0].get("aria-controls") == "file-ledger-table",
        "accessibility",
        "file ledger search, filters, table, and pagination need accessible controls",
    )
    require(
        result,
        re.search(
            r"\$\(\s*['\"]file-ledger-search['\"]\s*\)"
            r"\.addEventListener\s*\(\s*['\"]input['\"].*?"
            r"renderFileLedger\s*\(\s*true\s*\)",
            script,
            re.S,
        )
        is not None
        and len(
            re.findall(
                r"\$\(\s*['\"]file-ledger-(?:kind|sort)['\"]\s*\)"
                r"\.addEventListener\s*\(\s*['\"]change['\"].*?"
                r"renderFileLedger\s*\(\s*true\s*\)",
                script,
                re.S,
            )
        )
        == 2
        and len(
            re.findall(
                r"\$\(\s*['\"]file-ledger-(?:prev|next)['\"]\s*\)"
                r"\.addEventListener\s*\(\s*['\"]click['\"].*?"
                r"renderFileLedger\s*\(\s*\)",
                script,
                re.S,
            )
        )
        == 2,
        "file-ledger",
        "file ledger input, filters, and pagination must rerender",
    )
    require(
        result,
        "M.file_metrics" not in live_top_up
        and "fileLedger" not in live_top_up
        and "file_metrics" not in live_top_up,
        "file-ledger",
        "liveTopUp must not mutate per-file rows from package-wide CDN totals",
    )

    board_match = re.search(r"const\s+BOARDS\s*=\s*(\[.*?\]);", script, re.S)
    require(result, bool(board_match), "boards", "BOARDS definition missing")
    if board_match:
        observed = re.findall(
            r"\{\s*id:\s*['\"]([^'\"]+)['\"]\s*,\s*label:\s*['\"]([^'\"]+)['\"]\s*,"
            r"\s*metric:\s*['\"]([^'\"]+)['\"]\s*,\s*unit:\s*['\"]([^'\"]+)['\"]\s*\}",
            board_match.group(1),
        )
        expected = [
            (b["id"], b["label"], b["metric"], b["unit"])
            for b in preservation["boards"]
        ]
        require(
            result,
            observed == expected,
            "boards",
            "leaderboard definitions, metrics, or order changed",
            "leaderboard definitions and order preserved",
        )
    agent_board = post_migration["agent_upvote_board"]
    require(
        result,
        re.search(
            r"const\s+AGENT_UPVOTE_BOARD\s*=\s*\{\s*"
            rf"id:\s*['\"]{re.escape(agent_board['id'])}['\"]\s*,\s*"
            rf"label:\s*['\"]{re.escape(agent_board['label'])}['\"]\s*,\s*"
            rf"metric:\s*['\"]{re.escape(agent_board['metric'])}['\"]\s*,\s*"
            rf"unit:\s*['\"]{re.escape(agent_board['unit'])}['\"]\s*\}}\s*;",
            script,
            re.S,
        )
        is not None,
        "upvotes",
        "Most upvoted agent board definition or upvote metric binding is missing",
    )
    render_boards_body = bodies.get("renderBoards", "")
    require(
        result,
        "ALL_BOARDS" in render_boards_body
        and "AGENT_UPVOTE_BOARD" in script
        and "most_upvoted" in render_boards_body,
        "upvotes",
        "Most upvoted agent board is not wired into renderBoards()",
    )
    require(
        result,
        "M.agent_metrics" in render_boards_body
        and re.search(
            r"Array\.isArray\s*\(\s*M\.agent_metrics\s*\)",
            render_boards_body,
        )
        is not None
        and re.search(
            r"activeBoard\s*===\s*['\"]most_upvoted['\"]",
            render_boards_body,
        )
        is not None
        and "r[cfg.metric]" in render_boards_body,
        "upvotes",
        "Most upvoted board must bind guarded agent_metrics upvote rows",
    )
    for field_name in post_migration["agent_metrics_fields"]:
        evidence = (
            f"r.{field_name}" in render_boards_body
            if field_name != "upvotes"
            else agent_board["metric"] == field_name
            and "r[cfg.metric]" in render_boards_body
        )
        require(
            result,
            evidence,
            "upvotes",
            f"Most upvoted board is not bound to agent_metrics.{field_name}",
        )
    require(
        result,
        re.search(
            rf"(?:let|const|var)\s+activeBoard\s*=\s*['\"]"
            rf"{re.escape(preservation['active_board'])}['\"]",
            script,
        )
        is not None,
        "boards",
        "default leaderboard changed",
    )
    require(
        result,
        "$('refresh').onclick=()=>load()" in script_compact
        or "addEventListener('click',load)" in script_compact
        or 'addEventListener("click",load)' in script_compact,
        "mappings",
        "Refresh control no longer reloads metrics through load()",
    )

    formula = compact_js(preservation["download_formula"]["live_top_up"])
    require(
        result,
        formula in script_compact,
        "downloads",
        "live download top-up formula changed; it must add only the new CDN-hit delta",
    )
    for expression in ("t.clones", "t.cdn_hits", "t.release_downloads"):
        require(
            result,
            expression in script,
            "downloads",
            f"download KPI lost component {expression}",
        )
    require(
        result,
        "downloads = git clones + jsdelivr cdn file hits + github release asset downloads"
        in page_text,
        "downloads",
        "download formula explanation is missing or changed",
    )
    require(
        result,
        "Agent file fetches" in html and "t.agent_file_downloads" in script,
        "downloads",
        "distinct Agent file fetches KPI is missing",
    )
    require(
        result,
        "Installer fetches" in html and "t.installer_downloads" in script,
        "downloads",
        "distinct Installer fetches KPI is missing",
    )
    for needle in (
        "No per-file CDN fetches recorded yet",
        "raw.githubusercontent.com",
        "only jsDelivr publishes per-file numbers",
    ):
        require(
            result,
            needle in html,
            "boards",
            f"leaderboard/source caveat missing: {needle}",
        )

    require(
        result,
        normalized_text(post_migration["headline"]) in visible_page_text,
        "upvotes",
        "headline must say Downloads, agent upvotes, and workshop usage",
    )
    kpi_body = bodies.get("renderKPIs", "")
    require(
        result,
        "Agent upvotes" in kpi_body and "t.agent_upvotes" in kpi_body,
        "upvotes",
        "Agent upvotes KPI must bind totals.agent_upvotes",
    )
    for phrase in post_migration["agent_upvote_phrases"]:
        require(
            result,
            normalized_text(phrase) in page_text,
            "upvotes",
            f"agent upvote explanation missing or altered: {phrase}",
        )
    for phrase in post_migration["forbidden_upvote_phrases"]:
        require(
            result,
            normalized_text(phrase) not in page_text,
            "upvotes",
            f"repository-star upvote language/action is forbidden: {phrase}",
        )
    require(
        result,
        "Repository stars" in kpi_body
        and re.search(r"label:\s*['\"]Repository stars['\"]", kpi_body) is not None
        and "r.stars" in kpi_body
        and re.search(
            r"label:\s*['\"](?:Community upvotes|Stars)['\"]",
            kpi_body,
            re.I,
        )
        is None,
        "upvotes",
        "repository stars may appear only as the Repository stars KPI",
    )
    visible_without_repository_stars = visible_page_text.replace(
        "repository stars", ""
    )
    require(
        result,
        re.search(r"\bstars\b", visible_without_repository_stars) is None
        and "github stars" not in page_text
        and "repository-level github stars" not in page_text,
        "upvotes",
        "repository-star presentation must use only the label Repository stars",
    )
    forbidden_repo_upvote_tokens = (
        "M.repo.upvotes",
        "r.upvotes",
        "communityUpvotes",
    )
    require(
        result,
        not any(token in script for token in forbidden_repo_upvote_tokens),
        "upvotes",
        "repository stars must not be aliased or consumed as upvotes",
    )
    repo_star_actions = [
        attrs
        for attrs in parser.links
        if attrs.get("href") == "https://github.com/microsoft/aibast-agents-library"
        and (
            attrs.get("id") == "upvote-github"
            or "upvote" in attrs.get("class", "").casefold()
        )
    ]
    require(
        result,
        not repo_star_actions,
        "upvotes",
        "repository link must not be presented as an upvote action",
    )
    repo_live = bodies.get("liveTopUp", "")
    require(
        result,
        "agent_upvotes" not in repo_live
        and "agent_metrics" not in repo_live
        and re.search(r"M\.repo\.stars\s*=\s*repo\.stargazers_count", repo_live)
        is not None,
        "upvotes",
        "liveTopUp may refresh Repository stars but not snapshot agent upvotes",
    )

    first_attrs, first_content = parser.scripts[0] if parser.scripts else ({}, "")
    require(
        result,
        not first_attrs.get("src")
        and first_content.strip() == theme["first_script"].strip(),
        "theme",
        "the mandatory scoutTheme bootstrap is not the exact first inline script",
    )
    root_block = re.search(r":root\s*\{(.*?)\}", styles, re.S)
    dark_block = re.search(
        r'html\s*\[\s*data-theme\s*=\s*["\']dark["\']\s*\]\s*\{(.*?)\}',
        styles,
        re.S,
    )
    require(result, bool(root_block), "theme", "light :root theme block missing")
    require(result, bool(dark_block), "theme", "dark theme block missing")
    for label, block, variables in (
        ("light", root_block.group(1) if root_block else "", theme["light_variables"]),
        ("dark", dark_block.group(1) if dark_block else "", theme["dark_variables"]),
    ):
        for name, value in variables.items():
            pattern = rf"{re.escape(name)}\s*:\s*{re.escape(value)}\s*;"
            require(
                result,
                re.search(pattern, block, re.I) is not None,
                "theme",
                f"{label} theme variable must be exact: {name}: {value}",
            )
    require(
        result,
        re.search(r"font-family\s*:[^;]*(?:Segoe UI)[^;]*(?:Aptos)", styles, re.I)
        is not None,
        "theme",
        "sans stack must include Segoe UI and Aptos",
    )
    require(
        result,
        re.search(r"font-family\s*:[^;]*Consolas", styles, re.I) is not None,
        "theme",
        "monospace stack must include Consolas",
    )
    for forbidden in ("fonts.googleapis.com", "fonts.gstatic.com", "Clawpilot"):
        require(
            result,
            forbidden.casefold() not in html.casefold(),
            "theme",
            f"forbidden presentation dependency/token found: {forbidden}",
        )
    for forbidden in ("Inter", "Beta"):
        require(
            result,
            re.search(rf"\b{forbidden}\b", html, re.I) is None,
            "theme",
            f"forbidden presentation token found: {forbidden}",
        )
    for variable in LEGACY_VARIABLES:
        require(
            result,
            re.search(rf"(?<![\w-]){re.escape(variable)}\s*:", styles) is None,
            "theme",
            f"legacy theme variable found: {variable}",
        )
    require(
        result,
        re.search(r"(?:linear|radial|conic)-gradient\s*\(", html, re.I) is None,
        "theme",
        "gradients are forbidden",
    )

    color_literal = re.compile(
        r"#[0-9a-fA-F]{3,8}\b|(?:rgb|rgba|hsl|hsla)\s*\([^)]*\)"
    )
    require(
        result,
        not unexpected_color_literals(
            styles,
            [
                (root_block, theme["light_variables"]),
                (dark_block, theme["dark_variables"]),
            ],
        ),
        "theme",
        "hardcoded presentation color exists outside the exact cp theme variables",
    )
    for _tag, attrs in parser.tags:
        for name, value in attrs.items():
            require(
                result,
                color_literal.search(value) is None,
                "theme",
                f"hardcoded color literal found in inline {name} attribute",
            )
    require(
        result,
        color_literal.search(script) is None,
        "theme",
        "JavaScript contains a hardcoded presentation color literal",
    )
    require(
        result,
        re.search(
            r"(?:fill|stroke|color|background(?:-color)?)\s*=\s*['\"]"
            r"(?:#[0-9a-fA-F]{3,8}|rgba?\()",
            script,
            re.I,
        )
        is None,
        "theme",
        "generated SVG/markup contains a hardcoded color literal",
    )

    header_match = re.search(r"<header\b.*?</header>", html, re.I | re.S)
    header_html = header_match.group() if header_match else ""
    require(
        result,
        bool(header_match) and re.search(r"<nav\b[^>]*aria-label=", header_html, re.I),
        "navigation",
        "cohesive topbar must contain a labelled navigation",
    )
    for link in theme["topbar_links"]:
        if "href" in link:
            matches = [
                attrs
                for attrs in parser.links
                if attrs.get("href") == link["href"]
            ]
            require(
                result,
                bool(matches),
                "navigation",
                f"topbar link missing: {link['label']} -> {link['href']}",
            )
            require(
                result,
                link["href"] in header_html
                and normalized_text(link["label"]) in normalized_text(header_html),
                "navigation",
                f"topbar does not visibly contain {link['label']}",
            )
            if link.get("current"):
                require(
                    result,
                    any(attrs.get("aria-current") == "page" for attrs in matches),
                    "navigation",
                    "Metrics/current topbar link needs aria-current=page",
                )
        else:
            require(
                result,
                any(
                    attrs.get("href", "").startswith(link["href_prefix"])
                    for attrs in parser.links
                ),
                "navigation",
                f"topbar link missing: {link['label']}",
            )
            require(
                result,
                link["href_prefix"] in header_html
                and normalized_text(link["label"]) in normalized_text(header_html),
                "navigation",
                f"topbar does not visibly contain {link['label']}",
            )
    theme_buttons = [
        attrs
        for tag, attrs in parser.tags
        if tag == "button"
        and (
            attrs.get("id") == "themeToggle"
            or "theme-toggle" in attrs
            or "data-theme-toggle" in attrs
        )
    ]
    require(
        result,
        any(
            attrs.get("aria-pressed") in {"true", "false"}
            and attrs.get("aria-label")
            for attrs in theme_buttons
        ),
        "navigation",
        "accessible theme toggle is missing",
    )
    interactive_script = "\n".join(scripts[1:])
    require(
        result,
        "themeToggle" in interactive_script
        and re.search(
            r"(?:addEventListener\s*\(\s*['\"]click['\"]|\.onclick\s*=|onclick=)",
            interactive_script,
        )
        is not None
        and (
            re.search(
                r"setAttribute\s*\(\s*['\"]data-theme['\"]",
                interactive_script,
            )
            is not None
            or re.search(r"\.dataset\.theme\s*=", interactive_script) is not None
        ),
        "navigation",
        "theme toggle is not wired to change data-theme",
    )

    require(
        result,
        theme["feedback_marker"] in html
        and theme["feedback_schema"] in html
        and "issues/new" in html
        and "searchParams.set" in script
        and "body" in script,
        "feedback",
        "shared feedback marker/schema/issues/new body wiring is incomplete",
    )
    semantic_tags = {tag for tag, _attrs in parser.tags}
    for tag in ("header", "nav", "main", "footer"):
        require(
            result,
            tag in semantic_tags,
            "accessibility",
            f"semantic <{tag}> landmark missing",
        )
    skip_links = [
        attrs
        for attrs in parser.links
        if "skip-link" in attrs.get("class", "").split()
        and attrs.get("href", "").startswith("#")
    ]
    require(result, bool(skip_links), "accessibility", "skip link missing")
    if skip_links:
        require(
            result,
            skip_links[0]["href"][1:] in parser.ids,
            "accessibility",
            "skip link target is missing",
        )
    require(
        result,
        ":focus-visible" in styles,
        "accessibility",
        "focus-visible styling missing",
    )
    require(
        result,
        "@media (prefers-reduced-motion: reduce)" in styles
        or "@media(prefers-reduced-motion:reduce)" in compact_js(styles),
        "accessibility",
        "prefers-reduced-motion handling missing",
    )
    require(
        result,
        "@media" in styles and ("grid-template-columns" in styles or "flex-wrap" in styles),
        "responsive",
        "responsive cards/layout rule missing",
    )
    require(
        result,
        "overflow-x: auto" in styles
        or "overflow-x:auto" in styles
        or "overflow-wrap: anywhere" in styles,
        "responsive",
        "horizontal overflow safety for tables/cards missing",
    )

    refresh = find_tag(parser, "button", element_id="refresh")
    require(
        result,
        bool(refresh)
        and refresh[0].get("type") == "button"
        and bool(refresh[0].get("aria-label") or refresh[0].get("aria-controls")),
        "accessibility",
        "Refresh must be an accessible type=button control",
    )
    statuses = [
        attrs
        for tag, attrs in parser.tags
        if attrs.get("role") == "status"
        and attrs.get("aria-live")
        and attrs.get("aria-atomic") == "true"
    ]
    require(
        result,
        bool(statuses),
        "accessibility",
        "accessible status live region missing",
    )
    tabs = find_tag(parser, "div", element_id="tabs")
    require(
        result,
        bool(tabs) and tabs[0].get("role") == "tablist",
        "accessibility",
        "tabs container needs role=tablist",
    )
    require(
        result,
        'role="tab"' in script
        and "aria-selected" in script
        and "aria-controls" in script
        and "keydown" in script
        and "ArrowLeft" in script
        and "ArrowRight" in script,
        "accessibility",
        "rendered tabs need ARIA state and keyboard arrow navigation",
    )
    charts = find_tag(parser, "svg", element_id="chart")
    require(
        result,
        bool(charts)
        and charts[0].get("role") == "img"
        and bool(charts[0].get("aria-labelledby") or charts[0].get("aria-label")),
        "accessibility",
        "chart needs an accessible image name/description",
    )
    tables = find_tag(parser, "table", element_id="stack-table")
    require(
        result,
        bool(tables)
        and (
            bool(tables[0].get("aria-label"))
            or bool(tables[0].get("aria-labelledby"))
            or "<caption" in html.casefold()
        ),
        "accessibility",
        "stack table needs a caption or accessible name",
    )
    require(
        result,
        re.search(r"<th\b[^>]*\bscope=['\"]col['\"]", html, re.I) is not None
        or 'scope="col"' in script
        or "scope='col'" in script,
        "accessibility",
        "rendered table headers need scope=col",
    )

    validate_javascript(result, parser)
    return result


def validate_contract(contract: dict) -> list[str]:
    errors = []
    provenance = contract.get("provenance", {})
    expected = {
        "commit": TRUSTED_COMMIT,
        "path": TRUSTED_PATH,
        "blob": TRUSTED_BLOB,
        "extraction": "git cat-file blob",
    }
    for key, value in expected.items():
        if provenance.get(key) != value:
            errors.append(f"contract provenance {key} mismatch")
    try:
        source = trusted_source()
    except RuntimeError as exc:
        return [str(exc)]
    if provenance.get("blob_sha256") != digest(source):
        errors.append("contract trusted blob SHA-256 mismatch")
    rebuilt = build_contract()
    if rebuilt != contract:
        errors.append("contract does not match deterministic trusted-blob extraction")
    return errors


def load_contract(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def print_result(result: AuditResult, page: Path) -> None:
    print(f"metrics page audit: {'PASS' if result.passed else 'FAIL'} ({page})")
    categories = sorted(set(result.passes) | set(result.failures))
    for category in categories:
        failures = result.failures.get(category, [])
        passes = result.passes.get(category, [])
        state = "FAIL" if failures else "PASS"
        print(f"[{state}] {category}: {len(passes)} checks passed, {len(failures)} failed")
        for message in failures:
            print(f"  - {message}")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", type=Path, default=DEFAULT_PAGE)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument(
        "--write-contract",
        action="store_true",
        help="rebuild the contract from the pinned git blob",
    )
    parser.add_argument(
        "--skip-contract-provenance",
        action="store_true",
        help="used only by isolated fixture tests",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.write_contract:
        contract = build_contract()
        args.contract.parent.mkdir(parents=True, exist_ok=True)
        args.contract.write_text(
            json.dumps(contract, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(
            f"wrote {args.contract} from "
            f"{TRUSTED_COMMIT}:{TRUSTED_PATH} ({TRUSTED_BLOB})"
        )
        return 0

    try:
        contract = load_contract(args.contract)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"metrics page audit: FAIL\n[FAIL] contract: {exc}", file=sys.stderr)
        return 2
    if not args.skip_contract_provenance:
        errors = validate_contract(contract)
        if errors:
            print("metrics page audit: FAIL")
            print(f"[FAIL] contract: 0 checks passed, {len(errors)} failed")
            for error in errors:
                print(f"  - {error}")
            return 2
    try:
        html = args.page.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"metrics page audit: FAIL\n[FAIL] page: {exc}", file=sys.stderr)
        return 2
    result = audit_html(html, contract)
    print_result(result, args.page)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
