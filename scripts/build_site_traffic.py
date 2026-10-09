#!/usr/bin/env python3
"""Build reports/site-traffic.html from state/clarity_history.json.

A leadership-readable view of the public library site: page visits this week
against last week, the most visited pages, engagement and friction. Staging
(<owner>.github.io forks) is counted separately and never mixed into the
public numbers.

Clarity reports per page URL, so "page visits" counts sessions that viewed
each page; a session that viewed three pages counts three times.
"""
from __future__ import annotations

import csv
import html
import io
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.clarity_tag import current_tag as clarity_current_tag  # noqa: E402
from tools.design_tokens import current_block as design_block, stamp as design_stamp  # noqa: E402

HISTORY = ROOT / "state" / "clarity_history.json"
OUT_HTML = ROOT / "reports" / "site-traffic.html"
OUT_JSON = ROOT / "reports" / "site-traffic.json"
OUT_CSV = ROOT / "reports" / "site-traffic-raw.csv"
PUBLIC_PREFIX = "https://microsoft.github.io/aibast-agents-library"
WINDOW = 7
FRICTION = (
    ("DeadClickCount", "Dead clicks", "clicked something that did nothing"),
    ("QuickbackClick", "Quick backs", "left a page right after opening it"),
    ("RageClickCount", "Rage clicks", "clicked repeatedly in frustration"),
)


def num(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def site_of(url: str) -> str:
    if url.startswith(PUBLIC_PREFIX):
        return "public"
    if url.endswith(".github.io") or ".github.io/aibast-agents-library" in url:
        return "staging"
    return "other"


def page_name(url: str) -> str:
    path = url[len(PUBLIC_PREFIX):] or "/"
    return "Library home" if path in ("/", "/index.html") else path


def rows(day: dict, metric: str) -> list[dict]:
    for entry in day.get("metrics") or []:
        if entry.get("metricName") == metric:
            return entry.get("information") or []
    return []


def summarize(days: dict[str, dict]) -> dict:
    visits: dict[str, float] = {}
    staging = 0.0
    active = 0.0
    friction = {key: [0.0, 0.0] for key, _, _ in FRICTION}
    for day in days.values():
        for row in rows(day, "Traffic"):
            url = row.get("Url") or ""
            count = num(row.get("totalSessionCount"))
            if site_of(url) == "public":
                page = page_name(url)
                visits[page] = visits.get(page, 0) + count
            elif site_of(url) == "staging":
                staging += count
        for row in rows(day, "EngagementTime"):
            if site_of(row.get("Url") or "") == "public":
                active += num(row.get("activeTime"))
        for key, _, _ in FRICTION:
            for row in rows(day, key):
                if site_of(row.get("Url") or "") != "public":
                    continue
                sessions = num(row.get("sessionsCount"))
                friction[key][0] += sessions * num(row.get("sessionsWithMetricPercentage")) / 100
                friction[key][1] += sessions
    total = sum(visits.values())
    return {
        "days": len(days),
        "page_visits": int(total),
        "staging_visits": int(staging),
        "active_seconds_per_visit": round(active / total) if total else None,
        "top_pages": sorted(
            ({"page": page, "visits": int(count)} for page, count in visits.items()),
            key=lambda item: (-item["visits"], item["page"]),
        )[:10],
        "friction": {
            key: round(100 * hit / seen) if seen else None
            for key, (hit, seen) in friction.items()
        },
    }


def window(history: dict, end: date, length: int) -> dict[str, dict]:
    start = end - timedelta(days=length - 1)
    return {
        day: entry for day, entry in (history.get("days") or {}).items()
        if start.isoformat() <= day <= end.isoformat()
    }


def build(history: dict, today: date) -> dict:
    this_week = summarize(window(history, today, WINDOW))
    last_week = summarize(window(history, today - timedelta(days=WINDOW), WINDOW))
    return {
        "schema": "aibast-site-traffic/1.0",
        "as_of": today.isoformat(),
        "days_collected": len(history.get("days") or {}),
        "this_week": this_week,
        "last_week": last_week,
    }


def change(now: int, before: int, before_days: int) -> str:
    if before_days < WINDOW or not before:
        return "Last week not collected yet"
    delta = round(100 * (now - before) / before)
    return f"{'+' if delta >= 0 else ''}{delta}% vs last week ({before:,})"


def raw_csv(history: dict) -> str:
    """Every stored Clarity value as one row: day, metric, page URL, field, value."""
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["date", "metric", "url", "site", "field", "value"])
    for day, entry in sorted((history.get("days") or {}).items()):
        for metric in entry.get("metrics") or []:
            for row in metric.get("information") or []:
                url = row.get("Url") or ""
                for field, value in row.items():
                    if field != "Url":
                        writer.writerow([day, metric.get("metricName"), url, site_of(url), field, value])
    return out.getvalue()


def render(report: dict) -> str:
    week, last = report["this_week"], report["last_week"]
    esc = html.escape
    secs = week["active_seconds_per_visit"]
    building = (
        f'<p class="note">Collecting history: {week["days"]} of {WINDOW} days this week so far. '
        "Week-over-week comparisons start once two full weeks exist.</p>"
        if week["days"] < WINDOW else ""
    )
    pages = "".join(
        f'<tr><td>{esc(row["page"])}</td><td class="n">{row["visits"]:,}</td></tr>'
        for row in week["top_pages"]
    ) or '<tr><td colspan="2">No visits recorded yet.</td></tr>'
    friction = "".join(
        f'<div class="k"><b>{week["friction"][key] if week["friction"][key] is not None else "—"}%</b>'
        f"<span>{esc(label)}: share of page visits where someone {esc(meaning)}</span></div>"
        for key, label, meaning in FRICTION
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Library Site Traffic</title>
<meta name="description" content="Weekly public site traffic for the AIBAST Agents Library, from Microsoft Clarity.">
<style>
  body {{ margin: 0; background: var(--cp-bg); color: var(--cp-text); font: 15px/1.5 "Segoe UI", system-ui, sans-serif; }}
  main {{ max-width: 860px; margin: 32px auto; padding: 0 16px; }}
  h1 {{ font-size: 26px; margin: 0 0 4px; }}
  h2 {{ font-size: 17px; margin: 28px 0 10px; }}
  .sub, .note {{ color: var(--cp-text-muted); font-size: 13px; }}
  .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }}
  .k {{ background: var(--cp-surface); border: 1px solid var(--cp-border); border-radius: 12px; padding: 14px; }}
  .k b {{ display: block; font-size: 26px; }}
  .k span {{ color: var(--cp-text-muted); font-size: 13px; }}
  table {{ width: 100%; border-collapse: collapse; background: var(--cp-surface); border: 1px solid var(--cp-border); }}
  td, th {{ padding: 8px 12px; border-bottom: 1px solid var(--cp-border); text-align: left; }}
  td.n, th.n {{ text-align: right; font-variant-numeric: tabular-nums; }}
  a {{ color: var(--cp-link); }}
</style>
{clarity_current_tag(ROOT).rstrip()}
</head>
<body>
<main>
  <h1>Library site traffic</h1>
  <p class="sub">Public site only, last {WINDOW} days to {esc(report["as_of"])} · source: Microsoft Clarity, collected daily ·
  <a href="../metrics.html">All library metrics</a></p>
  {building}
  <div class="kpis">
    <div class="k"><b>{week["page_visits"]:,}</b><span>Page visits this week<br>{esc(change(week["page_visits"], last["page_visits"], last["days"]))}</span></div>
    <div class="k"><b>{f"{secs}s" if secs is not None else "—"}</b><span>Active time per page visit</span></div>
    <div class="k"><b>{week["staging_visits"]:,}</b><span>Staging visits (team review traffic, not counted above)</span></div>
  </div>
  <h2>Most visited pages</h2>
  <table><thead><tr><th>Page</th><th class="n">Visits</th></tr></thead><tbody>{pages}</tbody></table>
  <h2>Where people get stuck</h2>
  <div class="kpis">{friction}</div>
  <h2>Raw data</h2>
  <p>Everything above can be rebuilt from these files, which update daily:</p>
  <ul>
    <li><a href="site-traffic-raw.csv" download>site-traffic-raw.csv</a>: every Clarity value, one row per day, metric, page and field (opens in Excel)</li>
    <li><a href="../state/clarity_history.json" download>clarity_history.json</a>: the daily Clarity exports exactly as stored</li>
    <li><a href="site-traffic.json" download>site-traffic.json</a>: the numbers shown on this page</li>
  </ul>
  <p class="note">A page visit is a session that viewed that page, so one session that opens three pages counts three times.
  Clarity only counts visitors who accept the consent bar, so real reach is higher than shown.</p>
</main>
</body>
</html>
"""


def main() -> int:
    history = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else {}
    days = sorted((history.get("days") or {}).keys())
    today = date.fromisoformat(days[-1]) if days else date.today()
    report = build(history, today)
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_CSV.write_text(raw_csv(history), encoding="utf-8")
    OUT_HTML.write_text(design_stamp(render(report), design_block(ROOT)), encoding="utf-8")
    print(f"Site traffic: {report['this_week']['page_visits']} public page visits over {report['this_week']['days']} day(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
