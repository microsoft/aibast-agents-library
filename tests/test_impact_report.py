import json
import re
from copy import deepcopy
from pathlib import Path

import pytest

from scripts import build_impact_report


def metrics_fixture(
    generated_at="2026-08-09T12:00:00Z",
    *,
    stars=12,
    achievement_points=150,
    achievement_rate=50.0,
):
    return {
        "schema": "aibast-metrics/1.0",
        "generated_at": generated_at,
        "repo": {
            "owner": "example",
            "name": "aibast-agents-library",
            "site": "https://example.github.io/aibast-agents-library/",
            "stars": stars,
            "forks": 3,
            "watchers": 4,
            "open_issues": 2,
            "as_of": generated_at,
        },
        "totals": {
            "downloads": 180,
            "clones": 100,
            "cdn_hits": 70,
            "release_downloads": 10,
            "agent_file_downloads": 20,
            "installer_downloads": 5,
            "skill_downloads": 15,
            "agent_upvotes": 6,
            "agent_acquisitions": 4,
            "clones_excluding_ci_estimate": 80,
            "page_views": 400,
            "clone_uniques_14d": 18,
            "view_uniques_14d": 75,
            "agents": 72,
            "stacks": 52,
            "verticals": 12,
        },
        "daily": [
            {
                "date": "2026-08-03",
                "clones": 0,
                "clone_uniques": 0,
                "views": 0,
                "cdn": 0,
            },
            {
                "date": "2026-08-04",
                "clones": 4,
                "clone_uniques": 2,
                "views": 20,
                "cdn": 8,
            },
            {
                "date": "2026-08-08",
                "clones": 6,
                "clone_uniques": 3,
                "views": 30,
                "cdn": 12,
            },
        ],
        "traffic": {
            "live": True,
            "as_of": generated_at,
            "unavailable_reason": None,
        },
        "cdn": {"as_of": generated_at},
        "releases": {"as_of": generated_at},
        "agent_upvote_coverage": {
            "status": "available",
            "as_of": generated_at,
        },
        "agent_acquisition_coverage": {
            "status": "available",
            "as_of": generated_at,
        },
        "file_metrics": {
            "source_status": "complete",
            "as_of": generated_at,
            "totals": {
                "files": 3994,
                "observed_files": 3994,
                "by_kind": {"skill": {"files": 234}},
            },
        },
        "workshops": {
            "as_of": generated_at,
            "coverage": {
                "status": "partial",
                "views": {"status": "live popular-path response"},
                "downloads": {"status": "complete paginated response"},
                "feedback": {"status": "available"},
            },
            "totals": {
                "workshops": 51,
                "usage_events": 40,
                "views_14d": 15,
                "file_downloads": 20,
                "bundle_downloads": 3,
                "feedback_reports": 2,
            },
            "rows": [
                {
                    "slug": "account-intelligence",
                    "display_name": "Account Intelligence",
                    "usage_events": 40,
                    "views_14d": 15,
                    "file_downloads": 20,
                    "bundle_downloads": 3,
                    "feedback_reports": 2,
                    "agent_upvotes": 6,
                }
            ],
        },
        "achievements": {
            "status": "available",
            "as_of": generated_at,
            "totals": {
                "participants": 2,
                "points": achievement_points,
                "achievements": 8,
                "starts": 2,
                "workshop_completions": 1,
                "hard_completions": 1,
                "completion_rate": achievement_rate,
                "hard_completion_rate": 50.0,
                "achievement_completion_rate": 66.7,
            },
            "workshops": [
                {
                    "slug": "account-intelligence",
                    "points": achievement_points,
                    "starts": 2,
                    "workshop_completions": 1,
                    "hard_completions": 1,
                }
            ],
        },
        "agent_metrics": [
            {
                "name": "@aibast-agents-library/account-intelligence",
                "display_name": "Account Intelligence",
                "downloads": 20,
                "upvotes": 6,
                "acquisitions": 4,
            }
        ],
        "ecosystem": {
            "status": "partial",
            "as_of": generated_at,
            "totals": {
                "distribution_entries": 354,
                "logical_agents": 300,
                "overlap_agents": 54,
                "aibast_direct_agent_fetches": 20,
                "rar_agent_cdn_fetches": 5,
                "rar_agent_release_fetches": 0,
                "combined_agent_distribution_fetch_events": 25,
                "rar_agent_acquisitions": 3,
                "rar_positive_reactions": 4,
                "rar_usage_signals": {
                    "worked": 2,
                    "did_not_work": 1,
                    "stuck": 0,
                    "regular_use": 1,
                    "shipped": 1,
                    "want_to_try": 3,
                    "saved_time": 2,
                },
            },
            "sources": {
                "rar": {
                    "status": "partial",
                    "as_of": generated_at,
                    "coverage": {
                        "cdn": "censored",
                        "release_assets": "available",
                        "discussions": "available",
                        "traffic": "admin-token-required",
                    },
                }
            },
            "agents": [
                {
                    "logical_name": "@rapp/learn-new",
                    "display_name": "Learn New",
                    "channels": ["rar"],
                    "combined_distribution_fetch_events": 5,
                    "rar_acquisitions": 2,
                    "rar_usage_signals": {
                        "worked": 1,
                        "regular_use": 1,
                        "shipped": 0,
                    },
                },
                {
                    "logical_name": (
                        "@aibast-agents-library/account-intelligence"
                    ),
                    "display_name": "Account Intelligence",
                    "channels": ["aibast", "rar"],
                    "combined_distribution_fetch_events": 3,
                    "rar_acquisitions": 1,
                    "rar_usage_signals": {
                        "worked": 0,
                        "regular_use": 0,
                        "shipped": 1,
                    },
                },
            ],
        },
    }


def history_with_baselines():
    monthly = metrics_fixture(
        "2026-07-09T12:00:00Z",
        stars=5,
        achievement_points=0,
        achievement_rate=0.0,
    )
    weekly = metrics_fixture(
        "2026-08-01T12:00:00Z",
        stars=10,
        achievement_points=100,
        achievement_rate=40.0,
    )
    history = {"schema": build_impact_report.HISTORY_SCHEMA, "snapshots": []}
    for document in (monthly, weekly):
        history = build_impact_report.record_snapshot(
            history,
            build_impact_report.compact_snapshot(document),
        )
    return history


def source_metrics_history():
    return {
        "tracking": {
            "clones_since": "2026-08-03",
            "clones_last": "2026-08-09",
            "views_since": "2026-08-03",
            "views_last": "2026-08-09",
            "cdn_since": "2026-08-03",
            "cdn_last": "2026-08-09",
        },
        "clones": {
            "2026-08-04": {"count": 4, "uniques": 2},
            "2026-08-08": {"count": 6, "uniques": 3},
        },
        "views": {
            "2026-08-04": {"count": 20, "uniques": 10},
            "2026-08-08": {"count": 30, "uniques": 12},
        },
        "cdn": {
            "2026-08-04": 8,
            "2026-08-08": 12,
        },
    }


def test_report_calculates_weekly_monthly_and_daily_activity():
    document = metrics_fixture()
    report = build_impact_report.build_report(
        document,
        history_with_baselines(),
        source_metrics_history(),
    )

    week = report["periods"]["week"]
    month = report["periods"]["month"]
    assert week["baseline_at"] == "2026-08-01T12:00:00Z"
    assert month["baseline_at"] == "2026-07-09T12:00:00Z"
    assert week["metrics"]["git_clones"]["change"] == 10
    assert week["metrics"]["cdn_hits"]["change"] == 20
    assert week["metrics"]["page_views"]["change"] == 50
    assert week["metrics"]["total_downloads"]["change"] == 30
    assert week["metrics"]["total_downloads"]["status"] == "partial"
    assert week["metrics"]["stars"]["change"] == 2
    assert week["metrics"]["stars"]["change_percent"] == 20.0
    assert month["metrics"]["stars"]["change"] == 7
    assert week["metrics"]["achievement_points"]["change"] == 50
    assert month["metrics"]["achievement_points"]["change"] == 150
    assert month["metrics"]["achievement_points"]["change_percent"] is None
    assert week["metrics"]["achievement_completion_rate"]["change"] == 10.0
    assert build_impact_report.format_period_metric(
        next(row for row in report["current"]["metrics"] if row["id"] == "achievement_completion_rate"),
        week["metrics"]["achievement_completion_rate"],
    ) == "+10.0 pp"
    current = {row["id"]: row for row in report["current"]["metrics"]}
    assert current["agent_acquisitions"]["value"] == 4
    assert current["agent_acquisitions"]["status"] == "available"
    assert "ecosystem_leaderboards" not in report["current"]
    assert "RAR is excluded from every count" in report["caveats"][0]


def test_unavailable_traffic_is_not_reported_as_zero():
    document = metrics_fixture()
    document["traffic"] = {
        "live": False,
        "as_of": None,
        "unavailable_reason": "authorization required",
    }
    report = build_impact_report.build_report(document, history_with_baselines())
    metrics = {
        row["id"]: row for row in report["current"]["metrics"]
    }

    assert metrics["page_views"]["value"] is None
    assert metrics["git_clones"]["value"] is None
    assert metrics["cdn_hits"]["value"] == 70
    assert report["coverage"]["traffic"]["status"] == "unavailable"
    assert (
        report["periods"]["week"]["metrics"]["page_views"]["status"]
        == "unavailable"
    )


def test_history_deduplicates_and_keeps_repository_timelines_separate():
    document = metrics_fixture()
    current = build_impact_report.compact_snapshot(document)
    history = {"schema": build_impact_report.HISTORY_SCHEMA, "snapshots": []}
    history = build_impact_report.record_snapshot(history, current)
    history = build_impact_report.record_snapshot(history, current)
    later_same_day = deepcopy(current)
    later_same_day["at"] = "2026-08-09T23:00:00Z"
    history = build_impact_report.record_snapshot(history, later_same_day)
    other = deepcopy(current)
    other["repo"]["owner"] = "other"
    history = build_impact_report.record_snapshot(history, other)

    assert len(history["snapshots"]) == 2
    assert build_impact_report.matching_snapshots(history, current) == [
        later_same_day
    ]


def test_daily_metrics_wait_for_full_window_or_use_snapshot_baseline():
    document = metrics_fixture()
    document["daily"] = []
    no_history = {"schema": build_impact_report.HISTORY_SCHEMA, "snapshots": []}
    pending = build_impact_report.build_report(document, no_history)
    assert (
        pending["periods"]["week"]["metrics"]["git_clones"]["status"]
        == "baseline_pending"
    )
    assert (
        pending["periods"]["week"]["metrics"]["git_clones"]["change"]
        is None
    )

    with_history = build_impact_report.build_report(
        document,
        history_with_baselines(),
    )
    assert (
        with_history["periods"]["week"]["metrics"]["git_clones"][
            "calculation"
        ]
        == "snapshot_change"
    )


def test_stale_traffic_cannot_borrow_current_cdn_window():
    document = metrics_fixture()
    document["traffic"] = {
        "live": False,
        "as_of": "2026-08-01T12:00:00Z",
        "unavailable_reason": "authorization expired",
    }
    report = build_impact_report.build_report(
        document,
        history_with_baselines(),
        source_metrics_history(),
    )
    weekly = report["periods"]["week"]["metrics"]

    assert weekly["git_clones"]["calculation"] == "snapshot_change"
    assert weekly["git_clones"]["status"] == "partial"
    assert weekly["total_downloads"]["calculation"] == "period_activity"
    assert weekly["total_downloads"]["change"] == 20
    assert weekly["total_downloads"]["status"] == "partial"


def test_partial_and_censored_sources_stay_partial():
    document = metrics_fixture()
    document["file_metrics"]["source_status"] = "censored"
    document["agent_upvote_coverage"]["status"] = "partial"
    document["achievements"]["status"] = "partial"
    document["workshops"]["coverage"]["views"]["status"] = (
        "last authorized popular-path response"
    )
    rows = {
        row["id"]: row
        for row in build_impact_report.extract_metric_rows(document)
    }

    assert rows["agent_file_downloads"]["status"] == "partial"
    assert rows["agent_upvotes"]["status"] == "partial"
    assert rows["achievement_points"]["status"] == "partial"
    assert rows["workshop_views_14d"]["status"] == "partial"


def test_top_movers_are_ranked_and_rendered():
    history = history_with_baselines()
    for snapshot in history["snapshots"]:
        workshop = snapshot["workshops"]["account-intelligence"]
        workshop["usage_events"] = 10
        agent = snapshot["agents"][
            "@aibast-agents-library/account-intelligence"
        ]
        agent["downloads"] = 5
    report = build_impact_report.build_report(metrics_fixture(), history)
    weekly = report["periods"]["week"]["movers"]

    assert weekly["workshop_usage"][0]["change"] == 30
    assert weekly["agent_downloads"][0]["change"] == 15
    email = build_impact_report.render_email_text(report)
    html = build_impact_report.render_html(report)
    assert "TOP WEEKLY MOVERS" in email
    assert "Account Intelligence: +30" in email
    assert "Top weekly movers" in html


def test_writes_email_html_json_exports(tmp_path):
    report = build_impact_report.build_report(
        metrics_fixture(),
        history_with_baselines(),
    )
    written = build_impact_report.write_outputs(
        report,
        tmp_path,
        skip_pdf=True,
    )

    assert {path.name for path in written} == {
        "impact-report.json",
        "impact-report.html",
        "impact-report-email.txt",
        "impact-report-email.md",
    }
    html_text = (tmp_path / "impact-report.html").read_text()
    email_text = (tmp_path / "impact-report-email.txt").read_text()
    markdown = (tmp_path / "impact-report-email.md").read_text()
    payload = json.loads((tmp_path / "impact-report.json").read_text())
    assert build_impact_report.THEME_SCRIPT in html_text
    assert build_impact_report.THEME_CSS in html_text
    scripts = re.findall(r"<script>(.*?)</script>", html_text, re.DOTALL)
    assert scripts[0].strip() == build_impact_report.THEME_SCRIPT
    style = re.search(r"<style>(.*?)</style>", html_text, re.DOTALL).group(1)
    component_css = style.replace(build_impact_report.THEME_CSS, "", 1)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", component_css)
    assert not re.search(r"\b(?:rgb|rgba|hsl|hsla)\s*\(", component_css)
    assert (
        'font-family: "Segoe UI", Aptos, Calibri, -apple-system, '
        "BlinkMacSystemFont, sans-serif;"
    ) in html_text
    assert "7-day impact" in html_text
    assert "30-day impact" in html_text
    assert "Subject:" in email_text
    assert "MEASUREMENT STATUS" in email_text
    assert "GLOBAL AGENT LEADERS" not in email_text
    assert "AIBAST - WEEKLY & MONTHLY IMPACT" in email_text
    assert "| Metric | Current | 7-day impact | 30-day impact |" in markdown
    assert payload["schema"] == build_impact_report.REPORT_SCHEMA
    serialized = json.dumps(payload)
    for forbidden in ("issue_body", "access_token", "private@example.test"):
        assert forbidden not in serialized


def test_writes_valid_pdf_when_reportlab_is_available(tmp_path):
    pytest.importorskip("reportlab")
    report = build_impact_report.build_report(
        metrics_fixture(),
        history_with_baselines(),
    )
    path = tmp_path / "impact-report.pdf"

    build_impact_report.write_pdf(report, path)

    assert path.read_bytes().startswith(b"%PDF-")
    assert path.stat().st_size > 5_000


def test_cli_records_history_and_builds_non_pdf_exports(tmp_path, monkeypatch):
    metrics_path = tmp_path / "metrics.json"
    history_path = tmp_path / "impact-history.json"
    out_dir = tmp_path / "reports"
    metrics_path.write_text(json.dumps(metrics_fixture()), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "build_impact_report.py",
            "--metrics",
            str(metrics_path),
            "--history",
            str(history_path),
            "--out-dir",
            str(out_dir),
            "--skip-pdf",
        ],
    )

    assert build_impact_report.main() == 0
    history = json.loads(history_path.read_text())
    assert history["schema"] == build_impact_report.HISTORY_SCHEMA
    assert len(history["snapshots"]) == 1
    report = json.loads((out_dir / "impact-report.json").read_text())
    assert report["periods"]["week"]["status"] == "baseline_pending"
    assert report["periods"]["month"]["status"] == "baseline_pending"


def test_metrics_workflow_and_dashboard_publish_report_exports():
    root = Path(__file__).resolve().parent.parent
    workflow = (root / ".github/workflows/metrics.yml").read_text()
    dashboard = (root / "metrics.html").read_text()
    admin = (root / "docs/metrics-admin-setup.html").read_text()

    for token in (
        "python scripts/build_impact_report.py",
        "aibast-impact-report",
        "reports/impact-report.pdf",
        "reports/impact-report-email.txt",
        "state/impact_history.json",
    ):
        assert token in workflow
    for token in (
        "reports/impact-report.html",
        "reports/impact-report.pdf",
        "reports/impact-report-email.txt",
        "Signed-in acquisitions",
        "RAR is intentionally excluded from these counts",
    ):
        assert token in dashboard
    assert 'id="global-agent-ecosystem"' not in dashboard
    assert "function renderEcosystem()" not in dashboard
    assert "Baseline pending" in admin
    assert "Weekly/monthly impact exports" in admin
