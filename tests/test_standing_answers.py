"""Standing answers: asked once per period, caught up once, nothing lost half way."""
import datetime as dt
import importlib.util
import pathlib

import pytest

FILE = pathlib.Path(__file__).resolve().parents[1] / "agents/@aibast-agents-library/templates/standing_answers_agent.py"


@pytest.fixture()
def sa(tmp_path, monkeypatch):
    monkeypatch.setenv("AIBAST_STANDING_DIR", str(tmp_path))
    spec = importlib.util.spec_from_file_location("standing_answers_agent", FILE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MON = dt.datetime(2026, 11, 16, 9, 0)  # a Monday


def test_asked_once_per_period(sa):
    assert sa.add("Which deals are stalled?", "weekly", "stalled")["ok"]
    calls = []
    ask = lambda base, q: calls.append(q) or "Three deals."
    assert sa.run(now=MON, ask=ask)["asked"] == ["stalled"]
    assert sa.run(now=MON + dt.timedelta(days=2), ask=ask)["asked"] == []
    assert sa.run(now=MON + dt.timedelta(days=7), ask=ask)["asked"] == ["stalled"]
    assert len(calls) == 2


def test_missed_periods_are_caught_up_once(sa):
    sa.add("Q?", "daily", "q")
    calls = []
    sa.run(now=MON + dt.timedelta(days=9), ask=lambda b, q: calls.append(q) or "A")
    assert len(calls) == 1


def test_weekdays_skip_the_weekend(sa):
    sa.add("Q?", "weekdays", "q")
    sat = MON + dt.timedelta(days=5)
    assert sa.run(now=sat, ask=lambda b, q: "A")["asked"] == []


def test_a_failure_is_reported_and_retried_next_time(sa):
    sa.add("Q?", "daily", "q")
    def down(b, q):
        raise OSError("refused")
    out = sa.run(now=MON, ask=down)
    assert not out["ok"] and out["failed"][0]["label"] == "q"
    assert sa.run(now=MON, ask=lambda b, q: "A")["asked"] == ["q"]


def test_empty_answer_is_not_saved(sa):
    sa.add("Q?", "daily", "q")
    assert not sa.run(now=MON, ask=lambda b, q: "")["ok"]
    assert sa.latest()["answers"] == []


def test_latest_carries_the_note_and_remove_needs_a_yes(sa):
    sa.add("Q?", "daily", "q")
    sa.run(now=MON, ask=lambda b, q: "A")
    got = sa.latest()
    assert got["answers"][0]["answer"] == "A" and "Experimental" in got["note"]
    assert sa.remove("q")["needs_confirmation"] and sa.list_items()["count"] == 1
    assert sa.remove("q", True)["ok"] and sa.list_items()["count"] == 0


def test_same_name_twice_is_refused_and_bad_input_is_plain(sa):
    assert sa.add("Q?", "daily", "q")["ok"]
    assert not sa.add("Other?", "daily", "q")["ok"]
    assert not sa.add("", "daily")["ok"] and not sa.add("Q2?", "hourly")["ok"]
