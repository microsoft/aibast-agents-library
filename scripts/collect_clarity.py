#!/usr/bin/env python3
"""Append yesterday's Microsoft Clarity site traffic to state/clarity_history.json.

Clarity's Data Export API only returns the last 1 to 3 days (about 10 calls a
day), so history has to be collected daily. Each run stores one entry per UTC
date: the aggregate metrics Clarity reports per page URL. Query strings and
fragments are stripped from URLs before anything is written.

Needs CLARITY_API_TOKEN (Clarity -> Settings -> Data Export). Without it the
script prints a notice and exits 0, so the metrics job keeps running.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "state" / "clarity_history.json"
SCHEMA = "aibast-clarity/1.0"
ENDPOINT = (
    "https://www.clarity.ms/export-data/api/v1/project-live-insights"
    "?numOfDays=1&dimension1=URL"
)


def strip_url(value: str) -> str:
    return value.split("#", 1)[0].split("?", 1)[0]


def sanitize(metrics: list) -> list:
    """Keep Clarity's aggregate rows; drop query strings from page URLs."""
    clean = []
    for metric in metrics if isinstance(metrics, list) else []:
        if not isinstance(metric, dict):
            continue
        rows = []
        for row in metric.get("information") or []:
            if not isinstance(row, dict):
                continue
            rows.append({
                key: strip_url(value) if key.lower() == "url" and isinstance(value, str) else value
                for key, value in row.items()
            })
        clean.append({"metricName": metric.get("metricName"), "information": rows})
    return clean


def merge(history: dict, day: str, metrics: list, collected_at: str) -> dict:
    days = dict(history.get("days") or {})
    days[day] = {"collected_at": collected_at, "metrics": sanitize(metrics)}
    return {"schema": SCHEMA, "days": dict(sorted(days.items()))}


def fetch(token: str) -> list:
    request = urllib.request.Request(
        ENDPOINT,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def main() -> int:
    token = os.environ.get("CLARITY_API_TOKEN", "").strip()
    if not token:
        print("CLARITY_API_TOKEN is not set; skipping Clarity export.")
        return 0
    try:
        metrics = fetch(token)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"::warning title=Clarity export failed::{error}")
        return 0
    now = datetime.now(timezone.utc)
    history = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else {}
    updated = merge(history, now.strftime("%Y-%m-%d"), metrics, now.isoformat(timespec="seconds"))
    HISTORY.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    print(f"Clarity: stored {len(updated['days'])} day(s) in {HISTORY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
