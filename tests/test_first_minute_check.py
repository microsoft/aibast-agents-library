"""First-minute judge helpers and the copyable-command DOM boundary."""

import importlib.util
import builtins
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

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
    assert judge.jargon_in("It will open at rapp.microsoft.com.") == []
    assert judge.jargon_in("RAPP at rapp.microsoft.com") == ["RAPP"]


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


def test_start_jargon_scan_excludes_only_the_single_copyable_command():
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        try:
            page = browser.new_page()
            markup = """
              <h1>Get an agent running</h1>
              <section data-what-you-need>Copilot Studio and GitHub Copilot</section>
              <ol><li data-step="1">Open GitHub Copilot chat.</li></ol>
              <pre data-copyable>Get https://example.test/solutions/ask-hr/SKILL.md and do it.</pre>
              <details><summary>More help</summary><p>Brainstem and RAPP</p></details>
            """
            page.set_content(markup)
            snapshot = judge.start_snapshot(page)
            assert snapshot["commands"] == 1
            assert "SKILL.md" not in snapshot["text"]
            assert all(judge.start_requirements(snapshot).values())

            page.set_content(markup + "<p>Install Brainstem</p>")
            assert not judge.start_requirements(judge.start_snapshot(page))[
                "no_jargon_outside_details"
            ]

            page.set_content(markup.replace(
                "<details>", "<pre data-copyable>Another SKILL.md command</pre><details>"
            ))
            snapshot = judge.start_snapshot(page)
            assert snapshot["commands"] == 2
            assert "SKILL.md" in snapshot["text"]
            assert not judge.start_requirements(snapshot)["no_jargon_outside_details"]

            quiet = ('<p class="journey-link">Want an AI assistant running on your own '
                     'computer instead? <a href="docs/practice/windows.html">'
                     'Practice the Brainstem setup.</a></p>')
            page.set_content(markup + quiet)
            assert judge.start_requirements(judge.start_snapshot(page))["no_jargon_outside_details"]
            page.set_content(markup + quiet.replace("docs/practice/windows.html", "other.html"))
            assert not judge.start_requirements(judge.start_snapshot(page))["no_jargon_outside_details"]
            page.set_content(markup + quiet + "<p>Install Brainstem</p>")
            assert not judge.start_requirements(judge.start_snapshot(page))["no_jargon_outside_details"]
        finally:
            browser.close()


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


def test_unmeasured_and_measured_failure_have_distinct_verdicts(capsys):
    checks = [
        judge.result("J44", {"cards_release_hover": False}, False),
        judge.measurement_failure("J58", judge.MeasurementError("Wait timed out: offline panel")),
        judge.measurement_failure("J57", AssertionError("different file object")),
    ]
    assert [c["status"] for c in checks] == ["failed", "could not measure", "failed"]
    assert all(judge.exit_code([c], True) == 1 for c in checks)
    judge.print_report({"checks": checks}, 1, 1)
    output = capsys.readouterr().out
    assert "COULD NOT MEASURE" in output and "Wait timed out: offline panel" in output
    assert "1 PASS" not in output


@pytest.mark.parametrize("argv", [
    ["--only", "J44,browser_routes"], ["--only", "polish_r5,J58"],
])
def test_only_selects_ids_and_names(monkeypatch, capsys, argv):
    selections = []

    def run(selection):
        selections.append(selection)
        return {"checks": [judge.result("J44", True, True), judge.result("J58", True, True)]}

    monkeypatch.setattr(judge, "run_once", run)
    assert judge.main([*argv, "--gate"]) == 0
    assert selections == [frozenset(("J44", "J58"))]
    assert "2 PASS" in capsys.readouterr().out


@pytest.mark.parametrize("argv", [["--only", "missing"], ["--only", ""], ["--repeat", "0"]])
def test_invalid_selection_or_repeat_fails_before_running(monkeypatch, argv):
    run = Mock()
    monkeypatch.setattr(judge, "run_once", run)
    with pytest.raises(SystemExit) as exc:
        judge.main(argv)
    assert exc.value.code == 2
    run.assert_not_called()


@pytest.mark.parametrize("gate,passes,expected,diff", [
    (False, [True, True, True], 0, False),
    (False, [False, False, False], 0, False),
    (True, [False, False, False], 1, False),
    (False, [True, False, True], 1, True),
    (True, [True, True, None], 1, True),
])
def test_repeat_runs_all_selections_and_diffs_verdicts(
    monkeypatch, capsys, gate, passes, expected, diff
):
    results = iter(passes)
    run = Mock(side_effect=lambda selection: {
        "checks": [judge.result("J44", value := next(results), value is True)]
    })
    monkeypatch.setattr(judge, "run_once", run)
    assert judge.main(["--only", "J44", "--repeat", "3", *(["--gate"] if gate else [])]) == expected
    assert run.call_count == 3
    output = capsys.readouterr().out
    assert ("Repeat verdicts differ:" in output) is diff
    if diff:
        assert "--- run 1" in output and "+++ run " in output


def test_condition_timeout_names_the_wait_and_fails_gate(stage_page):
    page, _ = stage_page
    with pytest.raises(judge.MeasurementError, match="Wait timed out: named readiness"):
        judge.wait_for_condition(page, "() => false", label="named readiness", timeout=50)


def test_layout_wait_works_with_page_javascript_disabled(stage_page):
    page, base = stage_page
    nojs = page.context.browser.new_page(java_script_enabled=False)
    try:
        judge.load(nojs, base + "index.html", java_script_enabled=False)
        assert nojs.locator("noscript").count() > 0
    finally:
        nojs.close()


def test_layout_wait_includes_pending_navigation(stage_page):
    page, base = stage_page
    judge.load(page, base + "index.html")
    page.get_by_role("link", name="Workshops", exact=True).click()
    judge.wait_for_layout(page)
    assert "at your own pace" in judge.plain_text(page)


@pytest.mark.parametrize("motion", ["layout", "document-scroll", "nested-scroll"])
def test_geometry_wait_observes_two_stable_frames_after_motion(stage_page, motion):
    page, _ = stage_page
    page.set_content("""
        <div id="scroller" style="height:100px;overflow:auto">
          <div id="target" style="height:2000px">Moving layout</div>
        </div><div style="height:2000px"></div>
    """)
    page.evaluate("""motion => {
        window.motionTick = 0;
        const animate = () => {
            window.motionTick++;
            if (window.motionTick <= 18) {
                if (motion === 'layout')
                    document.querySelector('#target').style.marginTop = motionTick + 'px';
                else if (motion === 'document-scroll') scrollTo(0, motionTick * 10);
                else document.querySelector('#scroller').scrollTop = motionTick * 10;
                window.lastMotionTick = motionTick;
            }
            requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }""", motion)
    judge.wait_for_geometry(page)
    assert page.evaluate("motionTick >= 20 && lastMotionTick === 18")


@pytest.mark.parametrize("heading,dialog", [
    ("Claims", ""), ("Other", ""), ("Claims", '<div role="dialog">Unexpected dialog</div>'),
])
def test_search_listing_waits_past_initial_rest_for_cards_without_relaxing_checks(
    stage_page, heading, dialog
):
    page, _ = stage_page
    page.set_content(f"""
        <div style="height:2000px"></div>
        <div id="grid"><article class="agent-card"><h2>{heading}</h2></article></div>
        {dialog}
    """)
    page.evaluate("""() => {
        window.searchTick = 0;
        const animate = () => {
            window.searchTick++;
            if (searchTick === 12)
                document.querySelector('#grid').scrollIntoView({behavior:'smooth'});
            if (searchTick < 120) requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }""")
    listing = judge.search_listing(page)
    assert listing == {
        "cards_in_view": True, "first_is_claims": heading == "Claims", "no_dialog": not dialog,
    }
    assert page.evaluate("searchTick >= 12")
    position = page.evaluate("scrollY")
    page.evaluate("""() => new Promise(resolve =>
        requestAnimationFrame(() => requestAnimationFrame(resolve)))""")
    assert page.evaluate("scrollY") == position


def test_geometry_wait_times_out_if_condition_never_becomes_true(stage_page):
    page, _ = stage_page
    page.set_content("<p>Stable, but not ready</p>")
    with pytest.raises(judge.MeasurementError, match="missing cards"):
        judge.wait_for_geometry(page, "() => false", label="missing cards", timeout=100)


def test_search_listing_preserves_partial_vertical_intersection_and_visibility(stage_page):
    page, _ = stage_page
    page.set_content("""
        <div id="grid">
          <article class="agent-card" hidden><h2>Other</h2></article>
          <article class="agent-card"
                   style="position:fixed;left:2000px;top:-10px;width:100px;height:20px">
            <h2>Claims</h2>
          </article>
        </div>
    """)
    assert all(judge.search_listing(page).values())


def test_browser_routes_waits_for_delayed_navigation_and_runs_alone(monkeypatch, tmp_path):
    playwright = pytest.importorskip("playwright.sync_api")
    root = judge.ROOT
    monkeypatch.setattr(judge, "ROOT", tmp_path)
    with judge.local_site(root) as base, playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()

        def delayed_context(**kwargs):
            context = browser.new_context(**kwargs)
            context.add_init_script("""(() => {
                const original = window.fetch;
                window.fetch = async (...args) => {
                    if (args[1]?.method === 'HEAD')
                        await new Promise(resolve => setTimeout(resolve, 350));
                    return original(...args);
                };
            })()""")
            return context

        token = judge.SELECTION.set(frozenset(("J58",)))
        try:
            checks = judge.measure_practice_snapshots(
                SimpleNamespace(new_context=delayed_context), base)
            assert [c["id"] for c in checks] == ["J58"]
            assert checks[0]["pass"], json.dumps(checks, indent=2)
        finally:
            judge.SELECTION.reset(token)
            browser.close()


@pytest.mark.parametrize("url,external", [
    ("https://aka.ms/deploytoazurebutton", True),
    ("https://raw.githubusercontent.com/owner/repo/audio.wav", True),
    ("http://example.com/image.png", False),
    (BASE + "missing.js", False),
    ("http://localhost:7071/health/public", False),
    ("https://localhost:7071/health/public", False),
    ("https://127.0.0.1:7777/probe", False),
    ("https://[::1]:7777/probe", False),
    ("https://localhost.example.com/image.png", True),
])
def test_external_https_classification_preserves_visitor_machine_probes(url, external):
    assert judge.blocked_external_https(url, BASE) is external


def test_error_filter_requires_exact_policy_block_attribution():
    url = "https://aka.ms/image"
    blocked = {url, "http://localhost:7071/health/public"}
    for kind, message in (
        ("requestfailed", "net::ERR_BLOCKED_BY_CLIENT"),
        ("console", "Failed to load resource: net::ERR_BLOCKED_BY_CLIENT.Inspector"),
    ):
        error = {"kind": kind, "message": message, "url": url}
        assert judge.policy_blocked_error(error, blocked, BASE)
        assert not judge.policy_blocked_error(error, set(), BASE)
        assert not judge.policy_blocked_error({**error, "url": ""}, blocked, BASE)
        assert not judge.policy_blocked_error(
            {**error, "url": "http://localhost:7071/health/public"}, blocked, BASE
        )
    for kind, message in (
        ("console", "TypeError: Cannot read properties of undefined"),
        ("console", "Failed to load resource: net::ERR_CONNECTION_REFUSED"),
        ("console", "Application failed: net::ERR_BLOCKED_BY_CLIENT"),
        ("pageerror", "Failed to load resource: net::ERR_BLOCKED_BY_CLIENT"),
        ("requestfailed", "net::ERR_CONNECTION_RESET"),
    ):
        assert not judge.policy_blocked_error(
            {"kind": kind, "message": message, "url": url}, blocked, BASE
        )


def test_demo_url_uses_discovered_scenario_and_discards_playback_parameters():
    url = BASE + judge.DEMO + "?autoplay=1&scenario=catalog-case&speed=50#player"
    assert judge.scenario_demo_url(url) == BASE + judge.DEMO + "?scenario=catalog-case"
    for query in ("", "?autoplay=1", "?scenario="):
        with pytest.raises(ValueError, match="discover"):
            judge.scenario_demo_url(BASE + judge.DEMO + query)


@pytest.mark.parametrize("normal_advances,reduced_advances,present,passed,waits", [
    (True, False, True, True, True),
    (False, False, True, False, True),
    (True, True, True, False, False),
    (False, False, False, False, None),
])
def test_autoplay_requires_normal_advancement_and_reduced_motion_wait(
    normal_advances, reduced_advances, present, passed, waits
):
    value, actual = judge.autoplay_result(
        {"advances": normal_advances, "chat_present": present},
        {"advances": reduced_advances, "chat_present": present},
    )
    assert actual is passed
    assert value["advances"] is normal_advances
    assert value["reduced_motion_advances"] is reduced_advances
    assert value["reduced_motion_waits"] is waits


@pytest.mark.parametrize("href", [
    "docs/aibast-rapp-pattern.html", "why.html",
    "https://microsoft.github.io/aibast-agents-library/docs/aibast-rapp-pattern.html",
])
def test_pattern_capability_accepts_inline_footer_and_disclosure_link_snapshots(href):
    assert judge.capabilities([{"href": href, "label": "shell template"}], BASE)[
        "why_or_pattern"
    ]
    assert not judge.capabilities([], BASE)["why_or_pattern"]


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
    assert len(report["checks"]) == len(judge.SPECS)
    assert {check["id"] for check in report["checks"]} == {spec[0] for spec in judge.SPECS}
    assert all(check["value"] is None and not check["pass"] for check in report["checks"])
    assert "Playwright unavailable" in report["flags"][0]


def test_judge_check_ids_are_unique():
    ids = [spec[0] for spec in judge.SPECS]
    assert len(ids) == len(set(ids))


def test_studio_and_icons_failures_are_distinguished():
    studio = judge.result("J63", None, False, name="studio_answer_readable")
    icons = judge.result("J76", None, False, name="icons_3d")
    assert studio["target"] != icons["target"]
    assert judge.exit_code([studio, {**icons, "pass": True}], True) == 1
    assert judge.exit_code([{**studio, "pass": True}, icons], True) == 1


def test_card_icons_preserve_accessibility_and_context_loss_restores_glyphs(stage_page):
    from tools.check_card_icons import PROBE, SNAPSHOT, drawn, ready

    page, base = stage_page
    page.add_init_script(PROBE)
    ready(page, base)
    assert drawn(page.evaluate(SNAPSHOT))
    enhanced = page.locator(".agent-card").first.aria_snapshot()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: errors.append(message.text)
            if message.type == "error" else None)
    page.evaluate("""() => {
        const [context] = window.iconContexts;
        context.getExtension('WEBGL_lose_context').loseContext();
    }""")
    page.wait_for_function("document.documentElement.dataset.cardIcons === 'fallback'")
    page.wait_for_function("""() =>
        parseFloat(getComputedStyle(document.querySelector('.agent-icon')).fontSize) > 0""")
    assert page.evaluate(SNAPSHOT)["glyphs"]
    assert page.locator(".agent-card").first.aria_snapshot() == enhanced
    assert not errors


def test_card_icons_redraw_with_the_new_theme_ink(stage_page):
    from tools.check_card_icons import ready

    page, base = stage_page
    ready(page, base)
    canvas = page.locator(".agent-icon canvas").first
    light = canvas.evaluate("c => c.toDataURL()")
    page.evaluate("document.documentElement.dataset.theme = 'dark'")
    page.wait_for_function("""before => {
        const c = document.querySelector('.agent-icon canvas');
        return c && c.toDataURL() !== before;
    }""", arg=light)
    page.evaluate("document.documentElement.dataset.theme = 'light'")
    page.wait_for_function("""before =>
        document.querySelector('.agent-icon canvas').toDataURL() === before""", arg=light)


def test_card_icons_do_no_idle_draws_and_reduced_motion_stops_active_rendering(stage_page):
    from tools.check_card_icons import ready

    page, base = stage_page
    page.emulate_media(reduced_motion="no-preference")
    ready(page, base)
    page.evaluate("""() => {
        window.iconDraws = 0;
        const draw = CanvasRenderingContext2D.prototype.drawImage;
        CanvasRenderingContext2D.prototype.drawImage = function(...args) {
            if (this.canvas.closest('.agent-icon')) window.iconDraws++;
            return draw.apply(this, args);
        };
    }""")
    page.wait_for_timeout(250)
    assert page.evaluate("window.iconDraws") == 0
    page.locator(".agent-card").first.hover()
    page.wait_for_timeout(250)
    assert page.evaluate("window.iconDraws") > 0
    page.emulate_media(reduced_motion="reduce")
    page.wait_for_timeout(100)
    draws = page.evaluate("window.iconDraws")
    page.wait_for_timeout(250)
    assert page.evaluate("window.iconDraws") == draws


def test_polish_measurements_detect_translucent_headers_and_broken_words(monkeypatch, tmp_path):
    playwright = pytest.importorskip("playwright.sync_api")
    root = judge.ROOT
    monkeypatch.setattr(judge, "ROOT", tmp_path)
    with judge.local_site(root) as base, playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        try:
            assert judge.measure_polish(browser, base, set())[0]["pass"]

            def regressed_context(**kwargs):
                context = browser.new_context(**kwargs)
                context.add_init_script("""document.addEventListener('DOMContentLoaded', () => {
                    const style = document.createElement('style');
                    style.textContent = `
                        .topbar { background:rgba(255,255,255,.5) !important; }
                        #setup-line { word-break:break-all !important; }
                        #setup-line span { white-space:normal !important; }
                    `;
                    document.head.append(style);
                });""")
                return context

            regressed = SimpleNamespace(new_context=regressed_context)
            check = judge.measure_polish(regressed, base, set())[0]
            assert not check["pass"]
            assert not check["value"]["opaque_headers"]
            assert not check["value"]["setup_wraps_at_spaces"]
            assert check["value"]["card_articles"]
            assert check["value"]["workshop_count"]
        finally:
            browser.close()


def test_polish_waits_for_slow_hover_release(monkeypatch, tmp_path):
    playwright = pytest.importorskip("playwright.sync_api")
    root = judge.ROOT
    monkeypatch.setattr(judge, "ROOT", tmp_path)
    with judge.local_site(root) as base, playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()

        def slow_context(**kwargs):
            context = browser.new_context(**kwargs)
            context.add_init_script("""document.addEventListener('DOMContentLoaded', () => {
                const style = document.createElement('style');
                style.textContent = `.agent-card {
                    transition:transform 650ms linear, border-color 650ms linear !important;
                } .agent-card:hover { transition:none !important; }`;
                document.head.append(style);
            });""")
            return context

        try:
            checks = judge.measure_polish(SimpleNamespace(new_context=slow_context), base, set())
            assert checks[0]["pass"], checks
            assert checks[0]["value"]["cards_release_hover"]
        finally:
            browser.close()


def test_every_solution_requires_exact_slug_visible_line_and_deployment_contract():
    solution = {"slug": "product-line-optimization",
                "get": {"prompt": "Get {pages}solutions/product-line-optimization/SKILL.md and do it."}}
    snapshot = {"slug": solution["slug"], "line": solution["get"]["prompt"].replace("{pages}", BASE),
                "line_visible": True}
    assert judge.resolved_solution(snapshot, solution, BASE)
    for key, value in (("slug", "building-permit-processing"), ("line", "Different setup"),
                       ("line_visible", False)):
        assert not judge.resolved_solution({**snapshot, key: value}, solution, BASE)


def test_unknown_solution_requires_named_visible_problem_without_substitute_line():
    snapshot = {"notice": 'Solution "does-not-exist" was not found.', "line_visible": False}
    assert judge.unknown_solution_loud(snapshot)
    assert not judge.unknown_solution_loud({**snapshot, "line_visible": True})
    assert not judge.unknown_solution_loud({**snapshot, "notice": "Not found"})
    assert not judge.unknown_solution_loud({**snapshot, "notice": ""})


def test_watch_inventory_uses_recorded_scenarios_not_marketing_video_counts():
    solutions = [
        {"id": "production-line-optimization", "try": {"scenarios": [
            {"recorded": True}, {"recorded": True}, {"recorded": False},
        ]}},
        {"id": "unrecorded", "try": {"scenarios": [{"recorded": False}]}},
    ]
    cards = [{"id": "production-line-optimization", "watch": True}, {"id": "unrecorded", "watch": False}]
    evidence, passed = judge.watch_inventory(solutions, cards, 2)
    assert passed and not evidence["missing"] and evidence["recorded_demos"] == 2
    assert not judge.watch_inventory(solutions, cards, 1)[1]
    assert not judge.watch_inventory(solutions, cards, 64)[1]
    assert not judge.watch_inventory(solutions, [], 0)[1]
    assert not judge.watch_inventory(solutions, [*cards, {"id": "other", "watch": True}], 2)[1]


def test_unbacked_claims_are_case_insensitive_but_not_approximate():
    assert judge.unbacked_claims("ABOUT 15 MINUTES, with one line.") == [
        "About 15 minutes", "with one line",
    ]
    assert judge.unbacked_claims("Three steps, sample data only.") == []


def test_picker_labels_must_be_nonempty_and_alphabetical():
    assert judge.alphabetical_labels(["Account", "claims", "Workforce"])
    assert not judge.alphabetical_labels(["Claims", "Account"])
    assert not judge.alphabetical_labels([])


def test_office_hours_requires_the_actual_destination_not_just_a_fragment():
    booking = "https://forms.cloud.microsoft/book"
    assert judge.office_hours_destination("start.html#office-hours", BASE + "index.html", booking)
    assert judge.office_hours_destination("#office-hours", BASE + "start.html", booking)
    assert judge.office_hours_destination(booking, BASE, booking)
    for href in ("docs/installer.html#office-hours", "start.html#other",
                 "https://example.com/start.html#office-hours", "https://forms.cloud.microsoft/other"):
        assert not judge.office_hours_destination(href, BASE, booking)


def test_legacy_samples_use_recorded_scenarios_and_preserve_canonical_ids():
    solutions = [
        {"slug": f"case-{i}", "try": {"scenarios": [
            {"id": f"case-{i}-unrecorded", "recorded": False},
            {"id": f"case-{i}-question", "recorded": True},
        ]}} for i in range(10)
    ]
    solutions.insert(0, {"slug": "missing", "try": {"scenarios": []}})
    samples = judge.legacy_demo_samples(solutions)
    assert len(samples) == 5
    assert [s["slug"] for s, _ in samples] == ["case-0", "case-2", "case-4", "case-6", "case-8"]
    assert all(scenario["id"] == s["slug"] + "-question" for s, scenario in samples)


def test_chat_observer_uses_attached_frames_after_same_tab_navigation(stage_page):
    page, base = stage_page
    page.emulate_media(reduced_motion="no-preference")
    judge.load(page, base + "index.html")
    page.locator('[data-first-minute="watch"]').click()
    assert judge.observe_chat(page) == {"advances": True, "chat_present": True}


def test_same_tab_back_resumes_preview_and_player_pause_and_tabs_stop():
    playwright = pytest.importorskip("playwright.sync_api")
    with judge.local_site(judge.ROOT) as base, playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.route("**/*", lambda route: route.continue_()
                       if route.request.url.startswith(base) else route.abort("blockedbyclient"))
            judge.load(page, base + "index.html")
            page.locator('[data-first-minute="watch"]').click()
            # every surface draws the same player bar inside the demo frame
            bar = lambda: page.frame_locator("iframe").first.get_by_role("toolbar", name="Demo player")
            bar().get_by_role("button", name="Pause", exact=True).wait_for()
            bar().get_by_role("button", name="Pause", exact=True).click()
            page.wait_for_timeout(300)
            assert page.locator("body").get_attribute("data-phase") == "paused"
            bar().get_by_role("button", name="Play", exact=True).click()
            page.get_by_role("tab", name="Copilot Studio", exact=True).click()
            page.wait_for_timeout(300)
            assert page.locator("body").get_attribute("data-phase") == "paused"
            bar().get_by_role("button", name="Play", exact=True).wait_for()
            page.go_back(wait_until="networkidle")
            assert page.url == base + "index.html"
            assert judge.observe_chat(page)["advances"]
            page.locator("#featured-demo").focus()
            assert page.locator(".preview-box").evaluate(
                "e => getComputedStyle(e).outlineStyle !== 'none'"
            )
        finally:
            browser.close()


def test_phone_copy_remains_reachable_on_pages_style_subpath():
    playwright = pytest.importorskip("playwright.sync_api")
    with judge.local_site(judge.ROOT) as base, playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 360, "height": 640})

            def route(request_route):
                url = request_route.request.url
                if url.startswith(base):
                    response = request_route.fetch(url=url.replace("/aibast-agents-library/", "/"))
                    request_route.fulfill(response=response)
                else:
                    request_route.abort("blockedbyclient")

            page.route("**/*", route)
            judge.load(page, base + "aibast-agents-library/start.html")
            copy = page.get_by_role("button", name="Copy", exact=True)
            assert copy.is_enabled()
            copy.scroll_into_view_if_needed()
            assert copy.evaluate("e => {" + judge.DOM + "return inside(e);}")
            assert "/aibast-agents-library/solutions/" in page.locator("[data-copyable]").inner_text()
            hint = page.locator('[data-step="1"] p')
            assert hint.is_visible() and "Visual Studio Code" in hint.inner_text()
        finally:
            browser.close()


@pytest.mark.parametrize("width,height", [(1440, 900), (390, 844)])
@pytest.mark.parametrize("motion", ["reduce", "no-preference"])
def test_office_hours_lands_after_delayed_setup_render(width, height, motion):
    playwright = pytest.importorskip("playwright.sync_api")
    with judge.local_site(judge.ROOT) as base, playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": width, "height": height},
                                    reduced_motion=motion)
            pending = []

            def route(request_route):
                url = request_route.request.url
                if "/api/v1/solutions/" in url:
                    pending.append(request_route)
                elif url.startswith(base):
                    request_route.continue_()
                else:
                    request_route.abort("blockedbyclient")

            page.route("**/*", route)
            page.goto(base + "start.html#office-hours", wait_until="domcontentloaded")
            page.wait_for_timeout(300)
            assert pending
            for request_route in pending:
                request_route.continue_()
            page.locator("#instructions").wait_for(state="visible")
            assert judge.top_in_view(page.locator("#office-hours").bounding_box(), height)
        finally:
            browser.close()


def test_banner_intersection_requires_positive_area_and_counts_partial_overlap():
    box = {"x": 0, "y": 10, "width": 100, "height": 20}
    assert judge.boxes_intersect(box, {**box, "y": 29})
    for other in (None, {**box, "y": 30}, {**box, "x": 100}, {**box, "height": 0}):
        assert not judge.boxes_intersect(box, other)


def test_plain_text_keeps_open_disclosures_and_only_excludes_footer_when_requested():
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        try:
            page = browser.new_page()
            page.set_content("""
                <p>Visible copy</p>
                <details><summary>Build it yourself</summary><p>Brainstem</p></details>
                <details open><summary>More help</summary><p>agent.py</p></details>
                <footer>registry.json</footer>
            """)
            text = judge.plain_text(page)
            assert "Visible copy" in text and "Build it yourself" in text
            assert "Brainstem" not in text and "agent.py" in text and "registry.json" in text
            assert "registry.json" not in judge.plain_text(page, exclude_footer=True)
            page.locator("details").first.evaluate("e => e.open = true")
            assert "Brainstem" in judge.plain_text(page)
        finally:
            browser.close()


@pytest.mark.parametrize("y,expected", [(-1, False), (0, True), (843, True), (844, False)])
def test_anchor_top_must_land_inside_viewport(y, expected):
    assert judge.top_in_view({"x": 0, "y": y, "width": 100, "height": 50}, 844) is expected
    assert not judge.top_in_view(None, 844)
    assert not judge.top_in_view({"x": 0, "y": y, "width": 0, "height": 50}, 844)


def test_practice_computer_is_one_click_from_setup_and_installer():
    playwright = pytest.importorskip("playwright.sync_api")
    with judge.local_site(judge.ROOT) as base, playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        try:
            page = browser.new_page(reduced_motion="reduce")
            page.route("**/*", lambda route: route.continue_()
                       if route.request.url.startswith(base) else route.abort("blockedbyclient"))
            judge.load(page, base + "start.html")
            page.get_by_role("button", name="Step by step", exact=True).click()
            assert page.locator("#practice-computer").get_attribute("data-mode") == "try"
            assert page.locator("#pc").is_visible()
            assert page.locator("#pc").evaluate("e => !e.inert")
            assert page.locator("#c-n").inner_text() == "Step 1 of 4"
            page.locator('a[href="docs/practice/windows.html"]').click()
            assert page.url == base + "docs/practice/windows.html"
            assert page.locator("#c-n").inner_text() == "Step 1 of 17"
            judge.load(page, base + "docs/installer.html")
            page.locator('a[href="practice/windows.html"]').click()
            assert page.url == base + "docs/practice/windows.html"
            page.locator("#pc").wait_for(state="visible")
            assert page.locator("#pc").is_visible()
            assert page.locator("#c-n").inner_text() == "Step 1 of 17"
        finally:
            browser.close()


@pytest.fixture
def stage_page():
    playwright = pytest.importorskip("playwright.sync_api")
    with judge.local_site(judge.ROOT) as base, playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 900},
                                    reduced_motion="reduce")
            page.route("**/*", lambda route: route.continue_()
                       if route.request.url.startswith(base) else route.abort("blockedbyclient"))
            yield page, base
        finally:
            browser.close()


def test_practice_audio_checks_local_bytes_then_uses_registry_raw(stage_page):
    page, base = stage_page
    requested = []
    page.route("**/api/registry.json", lambda route: route.fulfill(
        json={"raw":base + "raw/"}))

    def media(route):
        requested.append(route.request.url)
        name = route.request.url.rsplit("/", 1)[-1]
        data = (judge.ROOT / "solutions/_shared/narration/media" / name).read_bytes()
        route.fulfill(content_type="audio/wav",
                      body=data if "/raw/" in route.request.url else b"wrong hash")

    page.route("**/*.wav", media)
    judge.load(page, base + "docs/practice/windows.html?watch=0&step=3")
    page.get_by_role("button", name="Unmute", exact=True).click()
    page.wait_for_function("() => window.__narration.at(-1)?.source === 'raw'")
    assert len(requested) == 2
    assert requested[0].startswith(base + "solutions/")
    assert requested[1].startswith(base + "raw/solutions/")
    assert page.evaluate("document.querySelector('#practice-voice').src.startsWith('blob:')")
    assert page.locator("#practice-caption").text_content() == ""
    assert page.locator("#c-say").inner_text().startswith("Copy the one line, then press")
    assert "Paste this in your real PowerShell now, then come back." in page.locator("#c-context").inner_text()


def test_leaving_step_cancels_audio_that_is_still_being_fetched(stage_page):
    page, base = stage_page
    held = []
    data = json.loads((judge.ROOT / "api/v1/practice/narration.json").read_text())
    segment = next(s for s in data["brainstem"]["segments"] if s["id"] == "practice-paste")
    page.route("**/" + segment["media"]["contentHash"] + ".wav", lambda route: held.append(route))
    judge.load(page, base + "docs/practice/windows.html?watch=0&step=3")
    page.get_by_role("button", name="Unmute", exact=True).click()
    page.wait_for_timeout(150)
    assert len(held) == 1
    page.get_by_role("button", name="Back", exact=True).click()
    page.wait_for_function("() => window.__narration.at(-1)?.source === 'local'")
    held[0].fulfill(content_type="audio/wav",
                    body=(judge.ROOT / segment["media"]["url"]).read_bytes())
    page.wait_for_timeout(150)
    logs = page.evaluate("window.__narration")
    assert logs[-1]["id"] == "practice-find" and not logs[-1].get("end")
    assert all(s.get("stopped") and not s.get("source")
               for s in logs if s["id"] == "practice-paste")
    assert page.evaluate("document.querySelectorAll('audio').length") == 1


def test_practice_keeps_install_then_matches_real_interview(stage_page):
    # Windows 11 instructions; the interview below is compared to the real chat.
    expected = [
        "Press Start: the four blue squares in the middle of the bar at the bottom of the screen.",
        "In Search, type PowerShell. When Windows PowerShell shows up as the best match, press Enter.",
        "Copy the one line, then press Ctrl+V or right-click inside the blue Windows PowerShell window to paste it. Press Enter.",
        "It is installing. When the sign-in page opens, type the code shown on the sign-in page (the line that says Your code), press Continue, then Authorize.",
    ]
    page, base = stage_page
    judge.load(page, base + "docs/practice/windows.html")
    assert page.locator("#c-prog section > div").count() == 17
    assert page.locator("#c-prog h3").all_text_contents() == ["Install", "Interview it"]
    interview = judge.real_interview()
    interview[2]["hint"] = "Click <strong>Clear</strong> in the toolbar above the message box."
    assert page.evaluate("window.practicePC.STEPS.slice(4).map(s => ({id:s.id, heading:s.heading, hint:s.tourHint, skippable:!!s.skippable}))") == interview
    assert judge.practice_clickthrough(page) == expected
    assert list(judge.PRACTICE_TEXTS) == expected
    assert page.locator("#c-n").inner_text() == "Done"
    for host in ("start.html", "docs/practice/windows.html"):
        source = (judge.ROOT / host).read_text()
        assert source.count('/practice/desktop.js"') == 1
        assert "function makeWin" not in source
        assert 'id="taskbar"' not in source


def test_try_stage_completes_express_using_only_highlights(stage_page):
    page, base = stage_page
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    judge.load(page, base + "start.html")
    assert page.locator("#c-n").inner_text() == "Step 1 of 4"
    assert page.locator("#c-prog h3").all_text_contents() == [
        "Get your agent",
    ]
    page.get_by_role("button", name="Step by step", exact=True).click()
    assert judge.highlighted_clickthrough(page) == list(range(1, 5))
    assert page.locator("#agent-pasted-line").inner_text() == page.locator("#setup-line").inner_text()
    assert page.locator("#studio-question").inner_text() == page.locator("#sample-question").inner_text()
    assert page.locator("#studio-agent").inner_text() == page.locator("#solution option:checked").inner_text()
    assert page.locator("#studio-answer").inner_text().endswith("Sample data.")
    assert "placeholder" not in page.locator("#studio-answer").inner_text()
    assert not errors


def test_studio_judge_checks_filed_samples_and_responsive_frame(stage_page):
    page, base = stage_page
    checks = judge.measure_studio(page.context.browser, base)
    assert [check["id"] for check in checks] == ["J60", "J61", "J62", "J63"]
    assert all(check["pass"] for check in checks), checks


def test_studio_preview_judge_checks_layout_pointer_and_keyboard(stage_page, tmp_path):
    from tools.studio_preview_check import measure
    page, base = stage_page
    checks = measure(page.context.browser, base, tmp_path)
    assert all(check["pass"] for check in checks), checks


def test_studio_preview_rejects_missing_greeting_and_wrong_tab(stage_page):
    from tools.studio_preview_check import preview_layout
    page, base = stage_page
    judge.studio_ready(page, base)
    assert all(preview_layout(page).values())
    page.locator(".studio-description").evaluate("e => e.textContent = ''")
    page.locator('[data-studio-tab="preview"]').evaluate(
        "e => e.setAttribute('aria-pressed', 'false')")
    value = preview_layout(page)
    assert not value["greeting"]
    assert not value["preview_selected"]


def test_studio_preview_uses_each_own_sample_and_resets_chat(stage_page):
    page, base = stage_page
    judge.studio_ready(page, base)
    samples = json.loads((judge.ROOT / "solutions/account-intelligence/evals/transcripts.json").read_text())["transcripts"]
    assert page.locator(".studio-prompts button").all_text_contents() == [
        sample["prompt"] for sample in samples[:6]
    ]
    page.locator(".studio-prompts button").nth(1).click()
    assert page.locator("#studio-question").inner_text() == samples[1]["prompt"]
    assert judge.studio_answer_words(page.locator("#studio-answer").inner_text()) == (
        judge.studio_answer_words(samples[1]["assistant_response"] + "\n\nSample data."))
    assert not page.locator(".studio-prompts").is_visible()
    page.locator("#studio-new-chat").click()
    assert page.locator(".studio-greeting").is_visible()
    assert page.locator(".studio-prompts").is_visible()
    assert not page.locator("#studio-answer").count()
    assert page.locator("#studio-input").input_value() == samples[0]["prompt"]
    page.locator("#studio-input").fill("An unrecorded question")
    page.keyboard.press("Enter")
    assert not page.locator("#studio-answer").count()
    assert "Try the first sample question" in page.locator("#toast").inner_text()


def test_studio_judge_rejects_an_invented_answer(stage_page, monkeypatch):
    page, base = stage_page
    original_load = judge.load

    def mutated_load(target, url):
        original_load(target, url)
        target.evaluate("""() => {
            const mount = window.AibastDesktop.mount;
            window.AibastDesktop.mount = (host, options) => {
                options.story.answer = 'An invented sample answer.';
                return mount(host, options);
            };
        }""")

    monkeypatch.setattr(judge, "load", mutated_load)
    checks = judge.measure_studio(page.context.browser, base)
    assert not next(check for check in checks if check["id"] == "J61")["pass"]


def test_studio_without_recorded_answer_links_to_its_demo(stage_page):
    page, base = stage_page
    page.route("**/solutions/personalized-shopping-assistant/evals/transcripts.json",
               lambda route: route.fulfill(json={"transcripts": []}))
    judge.studio_ready(page, base, "personalized-shopping-assistant")
    page.locator("#studio-send").click()
    answer = page.locator("#studio-answer")
    assert answer.locator("a").inner_text() == "Open the demo to see this agent's sample answer"
    assert "personalized-shopping-assistant" in answer.locator("a").get_attribute("href")
    assert answer.inner_text().endswith("Sample data.")


@pytest.mark.parametrize("slug", ["personalized-shopping-assistant", "store-associate-copilot"])
def test_studio_uses_first_filed_sample_even_when_catalog_first_is_unrecorded(stage_page, slug):
    page, base = stage_page
    judge.studio_ready(page, base, slug)
    sample = json.loads((judge.ROOT / f"solutions/{slug}/evals/transcripts.json").read_text())["transcripts"][0]
    assert page.locator("#studio-input").input_value() == sample["prompt"]
    page.locator("#studio-input").press("Enter")
    assert page.locator("#studio-question").inner_text() == sample["prompt"]
    assert judge.studio_answer_words(page.locator("#studio-answer").inner_text()) == judge.studio_answer_words(sample["assistant_response"] + "\n\nSample data.")


def test_studio_omits_recorded_emoji_without_rewriting_sample_words(stage_page):
    page, base = stage_page
    judge.studio_ready(page, base, "inventory-rebalancing")
    page.locator("#studio-send").click()
    sample = json.loads((judge.ROOT / "solutions/inventory-rebalancing/evals/transcripts.json").read_text())["transcripts"][0]
    assert "\U0001f534" in sample["assistant_response"]
    assert judge.studio_answer_words(page.locator("#studio-answer").inner_text()) == judge.studio_answer_words(sample["assistant_response"].replace("\U0001f534", "") + "\n\nSample data.")


def test_studio_renders_only_supported_markdown_as_safe_dom(stage_page):
    page, base = stage_page
    text = (
        '# Overview\n## Evidence\n**Important** sample.\n\n'
        '- First **item**\n* Second item\n\n'
        '| Name | Value |\n|---|---|\n| Revenue | **$2.8B** |\n\n'
        '<img src=x onerror="window.unsafe = true"> [Link](https://example.com)\n'
        '1. Keep ordered prefixes and `code` literal.'
    )
    page.route("**/solutions/account-intelligence/evals/transcripts.json",
               lambda route: route.fulfill(json={"transcripts": [{
                   "prompt": "Show the sample.", "assistant_response": text,
               }]}))
    judge.studio_ready(page, base)
    page.locator("#studio-send").click()
    answer = page.locator("#studio-answer")
    assert answer.locator("h3").inner_text() == "Overview"
    assert answer.locator("h4").inner_text() == "Evidence"
    assert answer.locator("ul li").all_text_contents() == ["First item", "Second item"]
    assert answer.locator("thead th").all_text_contents() == ["Name", "Value"]
    assert answer.locator("tbody td").all_text_contents() == ["Revenue", "$2.8B"]
    assert answer.locator("strong").all_text_contents() == ["Important", "item", "$2.8B"]
    assert answer.locator("img, script, a, code, ol").count() == 0
    assert '<img src=x onerror="window.unsafe = true">' in answer.inner_text()
    assert judge.studio_answer_words(answer.inner_text()) == judge.studio_answer_words(text + "\n\nSample data.")


def test_studio_word_comparison_preserves_content_and_unsupported_marks():
    assert judge.studio_answer_words("4.7\u2605 (847 reviews)") == "4.7 (847 reviews)"
    assert judge.studio_answer_words("# Title\n**Revenue**\n- $2.8B") == "Title Revenue $2.8B"
    assert judge.studio_answer_words("| Name | Value |\n|---|---|\n| Acme | $2.8B |") == "Name Value Acme $2.8B"
    for changed in ("Revenue $2.8", "revenue $2.8B", "Revenue $2.8B.", "1. Revenue $2.8B",
                    "Revenue $2.8B |", "### Revenue $2.8B", "`Revenue` $2.8B"):
        assert judge.studio_answer_words(changed) != judge.studio_answer_words("**Revenue** $2.8B")


@pytest.mark.parametrize("width,height", [(1366,625), (1280,585), (1366,583)])
def test_studio_readability_rejects_missing_fade_and_hint(stage_page, width, height):
    page, base = stage_page
    page.set_viewport_size({"width":width, "height":height})
    judge.studio_ready(page, base)
    page.locator("#studio-send").click()
    assert page.locator(".studio-thread").evaluate("e => e.scrollHeight > e.clientHeight")
    page.add_style_tag(content='.studio-thread::after { background:none !important; } .studio-scroll-hint { display:none !important; }')
    measured = judge.studio_answer_readability(page)
    assert not measured["fade"]
    assert not measured["hint_when_more"]


def test_pause_holds_pending_install_work_and_mode_change_cancels_pointer_action(stage_page):
    page, base = stage_page
    page.emulate_media(reduced_motion="no-preference")
    judge.load(page, base + "docs/practice/windows.html")
    page.get_by_role("button", name="Step by step", exact=True).click()
    page.locator("#tb-start").click()
    page.locator("#ssearch").fill("PowerShell")
    page.locator(".res.best").click()
    page.locator(".ps .in").fill(
        "irm https://microsoft.github.io/aibast-agents-library/install.ps1 | iex"
    )
    page.locator(".ps .in").press("Enter")
    page.get_by_role("button", name="Watch", exact=True).click()
    page.get_by_role("button", name="Pause", exact=True).click()
    before = page.locator(".ps .out").inner_text()
    page.wait_for_timeout(1500)
    assert page.locator(".ps .out").inner_text() == before
    assert page.locator("#c-n").inner_text() == "Step 4 of 17"
    page.get_by_role("button", name="Play again", exact=True).click()
    page.wait_for_timeout(1150)
    page.get_by_role("button", name="Step by step", exact=True).click()
    page.wait_for_timeout(1200)
    assert page.locator("#c-n").inner_text() == "Step 1 of 17"
    assert not page.locator("#start").evaluate("e => e.classList.contains('open')")


def test_picker_replaces_replayed_run_and_rejects_an_inexact_setup_line(stage_page):
    page, base = stage_page
    judge.load(page, base + "start.html")
    page.get_by_role("button", name="Watch", exact=True).click()
    page.get_by_role("button", name="Play again", exact=True).click()
    options = page.locator("#solution option").evaluate_all("es => es.map(e => e.value)")
    page.locator("#solution").select_option(options[1])
    page.wait_for_function("(slug) => document.querySelector('#setup-line').textContent.includes(slug) && !document.querySelector('#instructions').hidden", arg=options[1])
    assert options[1] in page.locator("#setup-line").inner_text()
    page.get_by_role("button", name="Step by step", exact=True).click()
    page.locator("#agent-chat").click()
    page.locator(".vsc textarea").fill("A different setup line")
    page.locator(".vsc .send").click()
    assert page.locator("#c-n").inner_text() == "Step 2 of 4"
    assert "paste it exactly" in page.locator("#toast").inner_text()
    assert not page.locator("#agent-pasted-line").count()
    page.locator(".vsc textarea").fill(page.locator("#setup-line").inner_text())
    page.locator(".vsc .send").click()
    page.locator("#ms-signin").wait_for()
    page.locator("#solution").select_option(options[2])
    page.wait_for_function("(slug) => document.querySelector('#setup-line').textContent.includes(slug) && !document.querySelector('#instructions').hidden", arg=options[2])
    page.wait_for_timeout(1200)
    assert page.locator("#c-n").inner_text() == "Step 1 of 4"
    assert page.locator(".win").count() == 1
    assert not page.locator("#ms-signin").count()
    assert options[2] in page.locator("#setup-line").inner_text()


@pytest.mark.parametrize("number", range(10, 17))
def test_skip_leaves_the_next_step_completable_by_real_input(stage_page, number):
    page, base = stage_page
    judge.load(page, base + f"docs/practice/windows.html?watch=0&step={number}")
    page.get_by_role("button", name="Skip this step", exact=True).click()
    page.wait_for_function("(n) => window.practicePC.step() === n", arg=number)
    judge.journey_clickthrough(page, first=number+1, last=number+1)
    assert page.evaluate("window.practicePC.step()") == number+1


@pytest.mark.parametrize("number,selector", [
    (2, "#ssearch"), (3, ".ps .in"), (4, "#ghcode"), (6, ".bs form input"),
    (12, ".bs form input"), (14, ".bs form input"), (16, ".bs form input"),
])
def test_typed_step_opens_with_a_real_caret_without_page_scroll(stage_page, number, selector):
    page, base = stage_page
    page.set_viewport_size({"width":1280, "height":585})
    judge.load(page, base + f"docs/practice/windows.html?watch=0&step={number}")
    assert page.locator(selector).evaluate("e => e === document.activeElement")
    assert page.evaluate("scrollY") == 0


def test_search_enter_does_not_insert_a_newline_into_the_newly_focused_prompt(stage_page):
    page, base = stage_page
    judge.load(page, base + "docs/practice/windows.html?watch=0&step=2")
    page.locator("#ssearch").fill("PowerShell")
    page.keyboard.press("Enter")
    assert page.locator(".ps .in").evaluate("e => e === document.activeElement")
    assert page.locator(".ps .in").inner_text() == ""


@pytest.mark.parametrize("width,height", [(1920,1080), (1280,585), (1366,583)])
def test_last_step_keeps_both_group_headings_and_current_step_visible(stage_page, width, height):
    page, base = stage_page
    page.set_viewport_size({"width":width, "height":height})
    judge.load(page, base + "docs/practice/windows.html?watch=0&step=17")
    if not page.locator(".all-steps").evaluate("e => e.open"):
        page.locator(".all-steps summary").click()
    assert page.locator("#c-prog").evaluate("""e => {
        const box = getComputedStyle(e).position === 'absolute' ? e : e.parentElement;
        const bounds = box.getBoundingClientRect();
        return [...e.querySelectorAll('h3, [aria-current="step"]')].every(el => {
            const r = el.getBoundingClientRect();
            return r.top >= bounds.top && r.bottom <= bounds.bottom;
        });
    }""")


def test_powershell_native_paste_and_right_click_with_read_permission_denied(stage_page):
    page, base = stage_page
    page.context.grant_permissions(["clipboard-read", "clipboard-write"])
    judge.load(page, base + "docs/practice/windows.html?watch=0&step=3")
    page.evaluate("navigator.clipboard.writeText('native clipboard text')")
    cdp = page.context.new_cdp_session(page)
    context_id = cdp.send("Target.getTargetInfo")["targetInfo"]["browserContextId"]
    cdp.send("Browser.setPermission", {
        "permission":{"name":"clipboard-read"}, "setting":"denied",
        "origin":base.rstrip("/"), "browserContextId":context_id,
    })
    assert page.evaluate("() => navigator.permissions.query({name:'clipboard-read'}).then(p => p.state)") == "denied"
    page.evaluate("""() => {
        navigator.clipboard.readText = () => { throw Error('Must not read the clipboard'); };
    }""")
    prompt = page.locator(".ps .in")
    prompt.fill("replace this")
    prompt.select_text()
    page.keyboard.press("Meta+v" if page.evaluate(
        "navigator.platform.startsWith('Mac')") else "Control+v")
    assert prompt.inner_text() == "native clipboard text"
    prompt.fill("")
    prompt.click(button="right")
    assert prompt.inner_text() == page.locator("#c-acts [data-line]").get_attribute("data-line")
    assert page.evaluate("scrollY") == 0


def test_practice_defaults_and_cleanup_keep_one_control_per_action(stage_page):
    page, base = stage_page
    page.emulate_media(reduced_motion="no-preference")
    for path in ("start.html", "docs/practice/windows.html"):
        judge.load(page, base + path)
        assert page.locator("#practice-computer").get_attribute("data-mode") == "try"
        assert page.get_by_role("button", name="Watch", exact=True).is_visible()
    judge.load(page, base + "docs/practice/windows.html?step=17")
    page.get_by_role("button", name="What should I do next?", exact=True).click()
    assert page.get_by_role("link", name="Use the short guide.", exact=True).count() == 1
    judge.load(page, base + "index.html")
    page.locator("#search").fill("meeting")
    assert page.get_by_role("button", name="Clear search", exact=True).is_visible()
    assert page.get_by_role("searchbox").get_attribute("type") == "text"
    page.get_by_role("button", name="Clear search", exact=True).click()
    assert page.locator("#search").input_value() == ""


def test_real_laptop_acceptance(stage_page, tmp_path):
    from tools.practice_laptop_check import measure
    page, base = stage_page
    checks = measure(page.context.browser, base, tmp_path)
    assert all(check["pass"] for check in checks), json.dumps(checks, indent=2)


def test_preview_home_end_never_scroll_the_page_when_the_answer_fits(stage_page):
    page, base = stage_page
    page.set_viewport_size({"width":1920, "height":1080})
    judge.studio_ready(page, base)
    page.locator("#studio-send").click()
    page.locator(".studio-thread").focus()
    for key in ("End", "Home"):
        page.keyboard.press(key)
        assert page.evaluate("scrollY") == 0
    question = page.locator("#studio-question").bounding_box()
    thread = page.locator(".studio-thread").bounding_box()
    assert question["y"] >= thread["y"]
    assert question["y"] + question["height"] <= thread["y"] + thread["height"]


def test_watch_accepts_the_highlighted_action_without_switching_modes(stage_page):
    page, base = stage_page
    page.emulate_media(reduced_motion="no-preference")
    judge.load(page, base + "start.html")
    page.get_by_role("button", name="Watch", exact=True).click()
    page.locator("#agent-chat").click()
    assert page.locator("#practice-computer").get_attribute("data-mode") == "watch"
    assert page.locator("#c-n").inner_text() == "Step 2 of 4"
    assert not page.locator("#watch-pause-notice").is_visible()


def test_watch_accepts_space_on_the_highlighted_button_without_a_pause(stage_page):
    page, base = stage_page
    page.emulate_media(reduced_motion="no-preference")
    judge.load(page, base + "docs/practice/windows.html?step=5")
    page.locator("#watch-mode").click()
    page.locator(".bs .starter-btn").first.focus()
    page.keyboard.down("Space")
    page.wait_for_timeout(200)
    assert not page.locator("#watch-pause-notice").is_visible()
    page.keyboard.up("Space")
    page.wait_for_function("() => window.practicePC.step() === 5")
    assert page.locator("#practice-computer").get_attribute("data-mode") == "watch"
    assert not page.locator("#watch-pause-notice").is_visible()


def test_watch_stray_keyboard_input_and_explicit_takeover(stage_page):
    page, base = stage_page
    page.emulate_media(reduced_motion="no-preference")
    judge.load(page, base + "docs/practice/windows.html?step=4")
    page.locator("#watch-mode").click()
    page.locator("#ghcode").press("x")
    page.locator("#watch-pause-notice").wait_for(state="visible")
    page.locator("#ghcode").fill("A1B2-C3D4")
    assert page.locator("#practice-computer").get_attribute("data-mode") == "watch"
    assert page.locator("#watch-pause-notice p").inner_text() == (
        "Paused because you clicked. Press Resume to keep watching, or carry on yourself."
    )
    page.locator("#watch-take-over").click()
    assert page.locator("#practice-computer").get_attribute("data-mode") == "try"
    assert not page.locator("#watch-pause-notice").is_visible()


def test_watch_stray_controls_cannot_close_the_current_scene(stage_page):
    page, base = stage_page
    page.emulate_media(reduced_motion="no-preference")
    judge.load(page, base + "docs/practice/windows.html?step=4")
    page.locator("#watch-mode").click()
    before = page.evaluate("window.practicePC.capture()")
    page.locator(".edge .ctl i").last.click()
    page.locator("#watch-pause-notice").wait_for(state="visible")
    assert page.evaluate("window.practicePC.capture()") == before
    page.locator("#watch-resume").click()
    page.mouse.move(100, 100)
    page.mouse.wheel(0, 100)
    page.wait_for_timeout(200)
    assert page.locator("#stage-pause").inner_text() == "Pause"
    assert not page.locator("#watch-pause-notice").is_visible()


@pytest.mark.parametrize("path,selector,next_step", [
    ("docs/practice/windows.html?step=2", "#ssearch", 2),
    ("docs/practice/windows.html?step=3", ".ps .in", 3),
    ("start.html", ".vsc textarea", 2),
])
def test_watch_recovers_from_an_unexpected_draft(stage_page, path, selector, next_step):
    page, base = stage_page
    page.emulate_media(reduced_motion="no-preference")
    judge.load(page, base + path)
    if path == "start.html":
        page.get_by_role("button", name="Watch", exact=True).click()
        page.locator("#agent-chat").click()
    else:
        page.locator("#watch-mode").click()
    page.locator(selector).press("x")
    page.locator("#watch-pause-notice").wait_for(state="visible")
    page.locator("#watch-resume").click()
    page.wait_for_function("n => window.practicePC.step() === n", arg=next_step,
                           timeout=30000)
    assert page.locator("#practice-computer").get_attribute("data-mode") == "watch"
    assert not page.locator("#watch-pause-notice").is_visible()


def test_watch_pause_and_visibility_acceptance(stage_page):
    page, base = stage_page
    checks = judge.measure_watch_playback(page.context.browser, base)
    assert all(check["pass"] for check in checks), json.dumps(checks, indent=2)


def test_phone_typing_helpers_fill_without_submitting_and_start_over_stays_manual(stage_page):
    page, base = stage_page
    page.set_viewport_size({"width": 360, "height": 640})
    judge.load(page, base + "docs/practice/windows.html?watch=0")
    assert not page.locator(".all-steps").evaluate("e => e.open")
    page.locator("#tb-start").click()
    page.get_by_role("button", name="Type it for me", exact=True).click()
    assert page.locator("#ssearch").input_value() == "PowerShell"
    assert page.locator("#c-n").inner_text() == "Step 2 of 17"
    page.locator(".res.best").click()
    page.get_by_role("button", name="Type it for me", exact=True).click()
    assert page.locator("#c-n").inner_text() == "Step 3 of 17"
    assert not page.locator("#ghcode").count()
    page.get_by_role("button", name="Start over", exact=True).click()
    assert page.locator("#c-n").inner_text() == "Step 1 of 17"
    assert page.locator("#practice-computer").get_attribute("data-mode") == "try"
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")


def test_session_practice_acceptance(stage_page):
    page, base = stage_page
    checks = judge.measure_session(page.context.browser, base)
    assert all(check["pass"] for check in checks), json.dumps(checks, indent=2)


def test_practice_bar_and_finish_acceptance(stage_page):
    page, base = stage_page
    checks = judge.measure_practice_bar(page.context.browser, base)
    assert all(check["pass"] for check in checks), json.dumps(checks, indent=2)


def test_finish_counts_find_duplicates_outside_the_coach(stage_page):
    page, base = stage_page
    judge.load(page, base + "docs/practice/windows.html?watch=0&step=8")
    page.get_by_role("button", name="What do you remember?", exact=True).click()
    assert judge.finish_counts(page) == {"buttons":1, "sentences":1}
    page.locator("#pc").evaluate("""e => {
        const duplicate = document.createElement('section');
        duplicate.innerHTML = '<p>You have met it. It still knows you.</p><button>Keep going</button>';
        e.prepend(duplicate);
    }""")
    assert judge.finish_counts(page) == {"buttons":2, "sentences":2}


def test_real_browser_walk_acceptance(stage_page, tmp_path):
    from tools.practice_walk_check import measure

    page, base = stage_page
    checks = measure(page.context.browser, base, tmp_path)
    assert [check["id"] for check in checks] == [f"J{n}" for n in range(88, 98)]
    assert all(check["pass"] for check in checks), json.dumps(checks, indent=2)


def test_repeated_caption_has_no_space_or_duplicate_announcement(stage_page):
    page, base = stage_page
    judge.load(page, base + "docs/practice/windows.html?watch=0&step=3")
    page.wait_for_function("() => window.__narration?.at(-1)?.id === 'practice-paste'")
    caption = page.locator("#practice-caption")
    assert caption.get_attribute("aria-live") == "off"
    assert caption.evaluate("e => getComputedStyle(e).clipPath === 'inset(50%)'")
    height = page.locator("#coach").bounding_box()["height"]
    caption.evaluate("e => e.remove()")
    assert page.locator("#coach").bounding_box()["height"] == height
    assert not judge.bar_repeated_sentences(page)
    page.locator("#c-say").evaluate("e => e.append(document.createTextNode(' ' + e.textContent))")
    assert judge.bar_repeated_sentences(page)


def test_different_future_clip_keeps_visible_live_caption(stage_page):
    page, base = stage_page
    data = json.loads((judge.ROOT / "api/v1/practice/narration.json").read_text())
    segment = next(s for s in data["brainstem"]["segments"] if s["screenId"] == "start")
    different = "This clip has different words from the instruction."
    for cue in segment["captions"]["segments"]:
        cue["text"] = different
    page.route("**/api/v1/practice/narration.json", lambda route: route.fulfill(json=data))
    judge.load(page, base + "docs/practice/windows.html?watch=0&step=1")
    page.wait_for_function("(text) => document.querySelector('#practice-caption').textContent === text",
                           arg=different)
    caption = page.locator("#practice-caption")
    assert caption.get_attribute("aria-live") == "polite"
    assert caption.evaluate("e => getComputedStyle(e).clipPath === 'none'")
    assert caption.bounding_box()["height"] > 1


def test_practice_snapshot_files_routing_and_offline_acceptance(stage_page):
    page, base = stage_page
    checks = judge.measure_practice_snapshots(page.context.browser, base)
    assert [check["id"] for check in checks] == ["J56", "J57", "J58", "J59"]
    assert all(check["pass"] for check in checks), json.dumps(checks, indent=2)


def test_snapshot_preserves_personal_chat_drafts_and_window_state(stage_page):
    page, base = stage_page
    judge.load(page, base + "docs/practice/windows.html?watch=0&step=6")
    introduction = "Remember, my name is Morgan and I review customer invoices."
    page.locator(".bs form input").fill(introduction)
    page.locator(".bs form input").press("Enter")
    page.evaluate("window.practicePC.launch('files')")
    page.locator('[data-key="files"]').get_by_role("button", name="Documents", exact=True).click()
    page.locator('[data-key="files"] .mn').click()
    page.locator('.tb-app[data-win="ps"]').click()
    page.locator('[data-key="ps"] .mn').click()
    page.locator('[data-key="edge"] .mx').click()
    page.locator(".bs form input").fill("An unfinished question")
    saved = page.evaluate("window.practicePC.capture()")
    page.get_by_role("button", name="Start over", exact=True).click()
    page.evaluate("(s) => window.practicePC.restore(s)", saved)
    assert page.evaluate("window.practicePC.capture()") == saved
    assert page.locator(".bs form input").evaluate("e => e === document.activeElement")
    page.reload()
    page.locator(".bs form input").wait_for()
    assert page.evaluate("window.practicePC.capture()") == saved
    assert page.evaluate("window.practicePC.state.memory") == introduction
    assert introduction in page.locator(".bs .log").inner_text()


def test_snapshot_restores_signin_phase_without_navigating_a_draft_address(stage_page):
    page, base = stage_page
    judge.load(page, base + "docs/practice/windows.html?watch=0&step=4")
    page.locator("#ghcode").fill("WRONG")
    page.locator("#ghgo").click()
    page.locator("#eurl").fill("https://an-unfinished-address")
    saved = page.evaluate("window.practicePC.capture()")
    page.get_by_role("button", name="Start over", exact=True).click()
    page.evaluate("(s) => window.practicePC.restore(s)", saved)
    assert page.locator("#eurl").input_value() == "https://an-unfinished-address"
    assert page.locator("#ghwarn").is_visible()
    assert page.locator("#ghcode").input_value() == "WRONG"
    page.locator("#ghcode").fill("A1B2-C3D4")
    page.locator("#ghgo").click()
    authorize = page.evaluate("window.practicePC.capture()")
    page.get_by_role("button", name="Start over", exact=True).click()
    page.evaluate("(s) => window.practicePC.restore(s)", authorize)
    page.locator("#ghauth").click()
    assert page.locator("#c-n").inner_text() == "Step 5 of 17"
    assert page.locator(".bs .starter-btn").count() == 3


@pytest.mark.parametrize("text", [
    "Seller starts here", "Close the deal", "Only we have this",
    "Built for Contoso", "Globex Corporation", "$1,000", "EUR 250",
    "500 dollars", "A company named Example",
])
def test_aideate_copy_rejects_claims_customers_and_currency(text):
    assert judge.aideate_copy_violations(text)


def test_aideate_copy_allows_microsoft_products_steps_and_plain_preview_address():
    assert not judge.aideate_copy_violations(
        "Microsoft Copilot. 01 Clarify. Private preview at rapp.microsoft.com."
    )


def test_aideate_links_require_served_targets_and_real_fragments(stage_page):
    page, base = stage_page
    assert judge.aideate_link_failures(page, ["#request", "start.html"], base) == []
    assert judge.aideate_link_failures(page, ["#missing-anchor"], base)
    assert judge.aideate_link_failures(page, ["not-a-real-page.html"], base)
