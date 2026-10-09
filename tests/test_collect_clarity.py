from scripts import collect_clarity


def test_sanitize_strips_query_strings_from_urls():
    metrics = [{
        "metricName": "Traffic",
        "information": [{
            "totalSessionCount": "4",
            "URL": "https://microsoft.github.io/aibast-agents-library/?utm=x#agent/a",
        }],
    }]
    clean = collect_clarity.sanitize(metrics)
    assert clean[0]["information"][0]["URL"] == "https://microsoft.github.io/aibast-agents-library/"
    assert clean[0]["information"][0]["totalSessionCount"] == "4"


def test_merge_keeps_one_entry_per_day_in_date_order():
    history = collect_clarity.merge({}, "2026-10-09", [], "2026-10-09T06:00:00+00:00")
    history = collect_clarity.merge(history, "2026-10-08", [], "2026-10-08T06:00:00+00:00")
    history = collect_clarity.merge(history, "2026-10-09", [{"metricName": "Traffic"}], "later")
    assert history["schema"] == collect_clarity.SCHEMA
    assert list(history["days"]) == ["2026-10-08", "2026-10-09"]
    assert history["days"]["2026-10-09"]["collected_at"] == "later"


def test_missing_token_skips_without_failing(monkeypatch, capsys):
    monkeypatch.delenv("CLARITY_API_TOKEN", raising=False)
    assert collect_clarity.main() == 0
    assert "skipping" in capsys.readouterr().out
