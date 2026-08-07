#!/usr/bin/env python3
"""
build_metrics.py — collect public AIBAST Agents Library metrics into state/metrics.json.

Sources (all public; only the GitHub traffic endpoints need a token):
  - registry.json                       agents, stacks, verticals, sizes, dates
  - api.github.com/repos/...            stars, forks, watchers, issues, releases
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
import os
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry.json"
OUT = ROOT / "state" / "metrics.json"
HISTORY = ROOT / "state" / "metrics_history.json"

OWNER = "microsoft"
REPO = "aibast-agents-library"
GH_API = "https://api.github.com"
JSDELIVR = "https://data.jsdelivr.com/v1"
USER_AGENT = "aibast-metrics-builder"
TIMEOUT = 30

# One-liner installers. A hit here is someone standing up a tier, not pulling
# an agent template, so it is counted and displayed separately.
INSTALLER_FILES = {
    "/install.sh", "/install.ps1", "/install.cmd", "/install.command",
    "/docs/install.sh", "/docs/install.ps1", "/docs/install.cmd", "/docs/install.command",
    "/community_rapp/install.sh", "/community_rapp/install.ps1",
}
# Catalog and deployment infrastructure — not an installable agent.
CATALOG_FILES = {"/registry.json", "/skill.md", "/azuredeploy.json", "/deploy.sh", "/deploy.ps1"}


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


# --------------------------------------------------------------- remote data

def fetch_repo(token):
    d = fetch_public(f"{GH_API}/repos/{OWNER}/{REPO}", token)
    if not d:
        return {}
    return {
        "stars": d.get("stargazers_count", 0),
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
    if paths:
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


def fetch_jsdelivr(by_file, agents):
    """CDN hits: totals, daily series, and per-file download counts."""
    out = {"total_hits": 0, "bandwidth": 0, "daily": [], "files": [], "period": "year"}
    pkg = fetch_json(f"{JSDELIVR}/stats/packages/gh/{OWNER}/{REPO}?period=year")
    if pkg:
        out["total_hits"] = pkg.get("hits", {}).get("total", 0)
        out["bandwidth"] = pkg.get("bandwidth", {}).get("total", 0)
        out["rank"] = pkg.get("hits", {}).get("rank")
        dates = pkg.get("hits", {}).get("dates", {}) or {}
        out["daily"] = [{"date": d, "count": c} for d, c in sorted(dates.items()) if c]

    files = fetch_json(f"{JSDELIVR}/stats/packages/gh/{OWNER}/{REPO}@main/files?period=year&limit=100") or []
    rows = []
    for f in files:
        name = f.get("name", "")
        hits = f.get("hits", {}).get("total", 0)
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
    if traffic.get("paths"):
        last["paths"] = traffic["paths"]
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
    out = sorted(rows, key=lambda r: (-r[key], r["name"]))
    if require:
        out = [r for r in out if r[key]]
    return out[:n]


def slim(rec):
    fields = ("name", "display_name", "publisher", "category", "tier", "downloads",
              "lines", "size_kb", "added_at", "file", "description", "stack", "vertical")
    return {k: rec[k] for k in fields if k in rec}


def build_agent_metrics(agents):
    """Compact per-agent map for the library UI. Only agents with a signal."""
    return {rec["name"]: {"d": rec["downloads"]}
            for rec in agents.values() if rec["downloads"]}


def build_leaderboards(agents, registry):
    rows = list(agents.values())
    categories = defaultdict(lambda: {"agents": 0, "downloads": 0, "lines": 0})
    verticals = defaultdict(lambda: {"agents": 0, "downloads": 0, "stacks": set()})
    tiers = defaultdict(int)

    for r in rows:
        c = categories[r["category"]]
        c["agents"] += 1
        c["downloads"] += r["downloads"]
        c["lines"] += r["lines"]
        if r["vertical"]:
            v = verticals[r["vertical"]]
            v["agents"] += 1
            v["downloads"] += r["downloads"]
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
        stack_rows.append({
            "name": s["stack"],
            "display_name": s.get("display_name", s["stack"]),
            "vertical": s.get("vertical", ""),
            "path": s.get("path", ""),
            "agents": len(members),
            "lines": sum(m["lines"] for m in members),
            "downloads": sum(m["downloads"] for m in members),
        })
    stack_rows.sort(key=lambda r: (-r["downloads"], -r["agents"], r["name"]))

    newest = [r for r in rows if r["added_at"]]
    newest.sort(key=lambda r: r["added_at"], reverse=True)

    return {
        "most_downloaded": [slim(r) for r in top(rows, "downloads")],
        "largest": [slim(r) for r in top(rows, "lines", n=15)],
        "newest": [slim(r) for r in newest[:15]],
        "stacks": stack_rows[:20],
        "categories": cat_rows,
        "verticals": vert_rows,
        "tiers": dict(sorted(tiers.items(), key=lambda kv: -kv[1])),
    }


# ----------------------------------------------------------------- assembly

def main():
    ap = argparse.ArgumentParser(description="Build the public metrics snapshot for the AIBAST Agents Library.")
    ap.add_argument("--offline", action="store_true", help="skip all network calls")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    registry = load_json(REGISTRY, {})
    if not registry:
        log("✗ registry.json missing or unreadable — run build_registry.py first")
        return 1

    log("· indexing registry")
    agents, by_file = build_agent_index(registry)

    repo = releases = traffic = {}
    jsd = {"total_hits": 0, "bandwidth": 0, "daily": [], "files": [], "agent_hits": 0, "installer_hits": 0}
    if not args.offline:
        log("· github repo")
        repo = fetch_repo(token)
        log("· releases")
        releases = fetch_releases(token)
        log("· traffic")
        traffic = fetch_traffic(token)
        log("· jsdelivr cdn")
        jsd = fetch_jsdelivr(by_file, agents)

    out_path = Path(args.out)
    history = out_path.parent / HISTORY.name
    hist_totals, daily, last_known = merge_history(traffic, jsd, history)
    traffic_live = bool(traffic.get("clones"))
    traffic_error = traffic.get("_error")

    release_dl = releases.get("total_downloads", 0) if releases else 0
    agent_hits = jsd.get("agent_hits", 0)
    installer_hits = jsd.get("installer_hits", 0)

    # GitHub counts every actions/checkout as a clone, and this repo runs
    # registry and preflight workflows on every push. The lowest daily clone
    # count over the tracked window is a floor on that self-generated baseline;
    # subtracting it gives a defensible estimate of non-CI clones.
    daily_clones = sorted(v["count"] for v in load_json(history, {}).get("clones", {}).values())
    ci_floor = daily_clones[0] if daily_clones else 0
    ci_estimate = ci_floor * len(daily_clones)
    clones_excl_ci = max(0, hist_totals["clones_all_time"] - ci_estimate)

    total_downloads = hist_totals["clones_all_time"] + hist_totals["cdn_all_time"] + release_dl
    stats = registry.get("stats", {})

    doc = {
        "schema": "aibast-metrics/1.0",
        "generated_at": now_iso(),
        "repo": {"owner": OWNER, "name": REPO,
                 "url": f"https://github.com/{OWNER}/{REPO}",
                 "site": f"https://{OWNER}.github.io/{REPO}/", **repo},
        "totals": {
            "downloads": total_downloads,
            "clones": hist_totals["clones_all_time"],
            "cdn_hits": hist_totals["cdn_all_time"],
            "release_downloads": release_dl,
            "agent_file_downloads": agent_hits,
            "installer_downloads": installer_hits,
            "clones_excluding_ci_estimate": clones_excl_ci,
            "ci_clone_estimate": ci_estimate,
            "page_views": hist_totals["views_all_time"],
            # `is None` semantics, not `or` — a genuine 0 from a live read must
            # not be overwritten by a stale non-zero figure.
            "clone_uniques_14d": (traffic.get("clones", {}).get("uniques_14d")
                                  if traffic.get("clones") else last_known.get("clone_uniques_14d", 0)),
            "view_uniques_14d": (traffic.get("views", {}).get("uniques_14d")
                                 if traffic.get("views") else last_known.get("view_uniques_14d", 0)),
            "clone_uniques_daily_sum": hist_totals["clone_uniques_all_time"],
            "view_uniques_daily_sum": hist_totals["view_uniques_all_time"],
            "days_tracked": hist_totals["days_tracked"],
            "tracking_since": hist_totals["first_day"],
            "agents": stats.get("total_agents", len(agents)),
            "stacks": stats.get("total_stacks", 0),
            "verticals": stats.get("total_verticals", 0),
            "publishers": stats.get("publishers", 0),
            "categories": stats.get("categories", 0),
            "total_lines": sum(a["lines"] for a in agents.values()),
            "total_kb": round(sum(a["size_kb"] for a in agents.values()), 1),
        },
        "daily": daily,
        "traffic": {
            "paths": traffic.get("paths") or last_known.get("paths", []),
            "referrers": traffic.get("referrers") or last_known.get("referrers", []),
            "clones_14d": (traffic.get("clones", {}).get("count_14d")
                           if traffic.get("clones") else last_known.get("clones_14d", 0)),
            "views_14d": (traffic.get("views", {}).get("count_14d")
                          if traffic.get("views") else last_known.get("views_14d", 0)),
            "live": traffic_live,
            "as_of": now_iso() if traffic_live else last_known.get("at"),
            "unavailable_reason": None if traffic_live else traffic_error,
        },
        "cdn": {"total_hits": jsd["total_hits"], "bandwidth": jsd["bandwidth"],
                "rank": jsd.get("rank"), "agent_hits": agent_hits,
                "installer_hits": installer_hits, "files": jsd["files"]},
        "releases": releases or {"total_downloads": 0, "count": 0, "releases": []},
        "leaderboards": build_leaderboards(agents, registry),
        "agent_metrics": build_agent_metrics(agents),
        "sources": [
            {"name": "GitHub Traffic API", "metric": "clones, views, popular paths (clones include this repo's own CI checkouts)", "url": f"{GH_API}/repos/{OWNER}/{REPO}/traffic/clones"},
            {"name": "jsDelivr CDN", "metric": "per-file download hits — agent templates and installers", "url": f"{JSDELIVR}/stats/packages/gh/{OWNER}/{REPO}"},
            {"name": "GitHub Releases", "metric": "release asset downloads", "url": f"{GH_API}/repos/{OWNER}/{REPO}/releases"},
            {"name": "registry.json", "metric": "agents, stacks, verticals, categories", "url": f"https://{OWNER}.github.io/{REPO}/registry.json"},
        ],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(doc, indent=1) + "\n")
    t = doc["totals"]
    log(f"✓ {out_path}")
    log(f"  downloads={t['downloads']} (clones {t['clones']} + cdn {t['cdn_hits']} + releases {t['release_downloads']})")
    if traffic_error:
        log(f"  · traffic unavailable: {traffic_error}")
    log(f"  agents={t['agents']} stacks={t['stacks']} agent_files={t['agent_file_downloads']} "
        f"installers={t['installer_downloads']} stars={doc['repo'].get('stars', 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
