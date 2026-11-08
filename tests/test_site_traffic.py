from datetime import date

from scripts import build_site_traffic as st
from tools.design_tokens import strip_block


def _day(public_visits, staging_visits=0, dead_pct=0):
    pub = "https://microsoft.github.io/aibast-agents-library/index.html"
    stg = "https://kody-w.github.io/aibast-agents-library/index.html"
    return {"metrics": [
        {"metricName": "Traffic", "information": [
            {"totalSessionCount": str(public_visits), "Url": pub},
            {"totalSessionCount": str(staging_visits), "Url": stg},
        ]},
        {"metricName": "EngagementTime", "information": [{"activeTime": str(10 * public_visits), "Url": pub}]},
        {"metricName": "DeadClickCount", "information": [
            {"sessionsCount": str(public_visits), "sessionsWithMetricPercentage": str(dead_pct), "Url": pub},
        ]},
    ]}


def test_public_and_staging_are_counted_separately():
    history = {"days": {"2026-10-09": _day(10, staging_visits=4, dead_pct=50)}}
    week = st.build(history, date(2026, 10, 9))["this_week"]
    assert week["page_visits"] == 10
    assert week["staging_visits"] == 4
    assert week["top_pages"] == [{"page": "Library home", "visits": 10}]
    assert week["active_seconds_per_visit"] == 10
    assert week["friction"]["DeadClickCount"] == 50


def test_week_over_week_needs_a_full_prior_week():
    days = {f"2026-10-{d:02d}": _day(1) for d in range(1, 15)}
    report = st.build({"days": days}, date(2026, 10, 14))
    assert report["this_week"]["page_visits"] == 7
    assert report["last_week"]["days"] == 7
    assert "+0%" in st.change(7, 7, 7)
    assert st.change(7, 0, 3) == "Last week not collected yet"


def test_raw_csv_has_one_row_per_value():
    csv_text = st.raw_csv({"days": {"2026-10-09": _day(2)}})
    lines = csv_text.strip().splitlines()
    assert lines[0] == "date,metric,url,site,field,value"
    assert any(",Traffic," in line and ",public,totalSessionCount,2" in line for line in lines)


def test_report_rebuild_preserves_the_shared_theme_and_navigation():
    report = st.build({}, date(2026, 10, 9))
    rendered = st.render(report)
    assert 'class="logo">AI</div>' in rendered
    assert "font-family: var(--cp-font);" in rendered
    assert "background: var(--cp-accent); color: var(--cp-accent-fg);" in rendered
    assert '<a class="hero-action primary" href="../metrics.html">All library metrics</a>' in rendered
    committed = strip_block(st.OUT_HTML.read_text(encoding="utf-8"))
    own_style = lambda page: page.split("<style>", 1)[1].split("</style>", 1)[0]
    assert own_style(committed) == own_style(rendered)
