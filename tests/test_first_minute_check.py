"""Pure first-minute judge helpers: no Playwright or browser required."""

import importlib.util
import builtins
import json
from pathlib import Path

import pytest


SPEC = importlib.util.spec_from_file_location(
    "first_minute_check", Path(__file__).resolve().parents[1] / "tools/first_minute_check.py"
)
judge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(judge)
BASE = "http://127.0.0.1:1234/"


def test_jargon_matches_literal_terms_without_matching_substrings():
    assert judge.jargon_in("Rapp uses AGENT.PY and skill.md, not wrapping.") == [
        "RAPP", "agent.py", "SKILL.md",
    ]
    assert judge.jargon_in("wrapping skull.md agentXpy 1Person") == []


@pytest.mark.parametrize("href", [
    "../index.html?view=solutions#workshops",
    "/index.html",
    "https://microsoft.github.io/aibast-agents-library/index.html#top",
])
def test_internal_targets_strip_queries_and_fragments(tmp_path, href):
    assert judge.internal_target(href, BASE + "docs/installer.html", tmp_path) == (
        tmp_path / "index.html"
    )


def test_links_resolve_directories_and_ignore_non_site_urls(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/index.html").touch()
    for href in ("docs/", "docs"):
        assert judge.internal_target(href, BASE, tmp_path).is_file()
    for href in (
        "mailto:hello@example.com", "javascript:void(0)", "https://example.com/",
        "https://microsoft.github.io/another-repo/",
    ):
        assert judge.internal_target(href, BASE, tmp_path) is None


def test_missing_links_include_hidden_or_download_hrefs_and_deduplicate(tmp_path):
    (tmp_path / "index.html").touch()
    assert judge.missing_links(
        ["#top", "missing.zip?download=1", "missing.zip?download=1", "https://example.com"],
        BASE + "index.html", tmp_path,
    ) == [{"page": "/index.html", "href": "missing.zip?download=1"}]


def test_encoded_traversal_and_symlinks_cannot_escape_repository(tmp_path):
    with pytest.raises(ValueError, match="escapes"):
        judge.internal_target("/%2e%2e/secret", BASE, tmp_path)
    (tmp_path / "escape").symlink_to(tmp_path.parent, target_is_directory=True)
    with pytest.raises(ValueError, match="escapes"):
        judge.internal_target("/escape/secret", BASE, tmp_path)


def test_start_page_requires_real_step_marker_and_single_copyable_command():
    snapshot = {
        "exists": True, "first_step": "1. Open GitHub Copilot",
        "what_you_need": 1, "commands": 1, "text": "Build an assistant",
    }
    assert all(judge.start_requirements(snapshot).values())
    assert not all(judge.start_requirements({}).values())
    for key, value, failed in (
        ("first_step", "", "first_step_is_non_technical"),
        ("first_step", "1. Open VS Code", "first_step_is_non_technical"),
        ("first_step", "1. Select Agent mode", "first_step_is_non_technical"),
        ("commands", 2, "one_copyable_command_before_details"),
        ("what_you_need", 0, "one_what_you_need"),
        ("text", "Install Brainstem", "no_jargon_outside_details"),
    ):
        assert not judge.start_requirements({**snapshot, key: value})[failed]


def test_capabilities_require_destinations_not_marketing_text():
    controls = [
        {"href": "request-info.html"}, {"href": "docs/installer.html#office-hours"},
        {"href": "academy.html"}, {"href": "?view=solutions#workshops"},
        {"href": "why.html"},
    ]
    assert all(judge.capabilities(controls, BASE + "index.html").values())
    assert not any(judge.capabilities(
        [{"href": "", "label": "workshops academy office hours"}], BASE
    ).values())
    assert not any(judge.capabilities(
        [{"href": "https://example.com/academy.html"}], BASE
    ).values())
    assert not judge.capabilities(
        [{"href": "docs/installer.html#other"}], BASE
    )["office_hours"]
    assert judge.capabilities(
        [{"href": "solutions/account/quest.html"}], BASE
    )["workshops"]
    assert judge.capabilities(
        [{"href": "docs/aibast-rapp-pattern.html"}], BASE
    )["why_or_pattern"]


def test_gate_is_opt_in_and_unmeasured_results_fail():
    checks = [judge.result("J1", None, False)]
    assert checks[0]["target"] == "<= 1"
    assert judge.exit_code(checks, False) == 0
    assert judge.exit_code(checks, True) == 1
    assert judge.exit_code([judge.result("J2", 5, True)], True) == 0


@pytest.mark.parametrize("argv,expected", [([], 0), (["--gate"], 1)])
def test_missing_playwright_is_reported_without_hiding_failure(
    monkeypatch, capsys, argv, expected
):
    real_import = builtins.__import__

    def without_playwright(name, *args, **kwargs):
        if name == "playwright.sync_api":
            raise ModuleNotFoundError("Playwright unavailable in this test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_playwright)
    assert judge.main(argv) == expected
    report = json.loads(capsys.readouterr().out.splitlines()[0])
    assert len(report["checks"]) == 10
    assert all(check["value"] is None and not check["pass"] for check in report["checks"])
    assert "Playwright unavailable" in report["flags"][0]
