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
    assert len(report["checks"]) == 44
    assert all(check["value"] is None and not check["pass"] for check in report["checks"])
    assert "Playwright unavailable" in report["flags"][0]


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


def test_chat_observer_uses_attached_frames_after_same_tab_navigation(monkeypatch):
    demo = Mock(parent_frame=None, child_frames=[object()])
    surface = Mock(parent_frame=demo)
    surface.frame_element.return_value.is_visible.return_value = True
    snapshots = iter(["Question", "Question and answer"])
    monkeypatch.setattr(judge, "demo_frame", lambda page: demo)
    monkeypatch.setattr(judge, "chat_snapshot",
                        lambda frame: "" if frame is demo else next(snapshots))
    page = SimpleNamespace(frames=[demo, surface], wait_for_timeout=lambda ms: None)
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
            page.get_by_role("button", name="Pause", exact=True).wait_for()
            page.get_by_role("button", name="Pause", exact=True).click()
            assert page.locator("body").get_attribute("data-phase") == "paused"
            page.get_by_role("button", name="Play", exact=True).click()
            page.get_by_role("tab", name="Copilot Studio", exact=True).click()
            page.wait_for_timeout(300)
            assert page.locator("body").get_attribute("data-phase") == "paused"
            assert page.get_by_role("button", name="Play", exact=True).is_visible()
            page.go_back(wait_until="networkidle")
            assert page.url == base + "index.html"
            assert judge.observe_chat(page)["advances"]
            page.locator("#featured-demo").focus()
            assert page.locator(".preview-box").evaluate(
                "e => getComputedStyle(e).outlineStyle !== 'none'"
            )
        finally:
            browser.close()


def test_phone_copy_remains_in_first_screen_on_pages_style_subpath():
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
            page.get_by_role("button", name="Try it yourself", exact=True).click()
            assert page.locator("#practice-computer").get_attribute("data-mode") == "try"
            assert page.locator("#pc").is_visible()
            assert page.locator("#pc").evaluate("e => !e.inert")
            assert page.locator("#c-n").inner_text() == "Step 1 of 12"
            judge.load(page, base + "docs/installer.html")
            page.locator('a[href="practice/windows.html"]').click()
            assert page.url == base + "docs/practice/windows.html"
            assert page.locator("#pc").is_visible()
            assert page.locator("#c-n").inner_text() == "Step 1 of 8"
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


def test_original_practice_steps_match_recorded_fork_staging_text(stage_page):
    # Recorded from fork/staging, not derived from the extracted engine.
    expected = [
        "Press Start: the four blue squares in the middle of the bar at the bottom of the screen.",
        "Type PowerShell. When Windows PowerShell shows up as the best match, press Enter.",
        "Copy the one line, then right-click inside the blue PowerShell window to paste it. Press Enter.",
        "It is installing. When the sign-in page opens, type the code shown in PowerShell (the line that says Your code), press Continue, then Authorize.",
        "Your Brainstem opened in Edge at localhost:7071. Say hello to it: type anything in the box at the bottom and press Send.",
        "Look around the library. In Edge, click the address bar, type microsoft.github.io/aibast-agents-library and press Enter. Browse the solutions, then come back here.",
        "Now the editor. Press Start, type Visual Studio Code, press Enter.",
        "In the Chat panel on the right, paste this line and press Enter. Then watch: Copilot finds your Brainstem, adds its folder on the left and opens it in the middle.",
    ]
    page, base = stage_page
    judge.load(page, base + "docs/practice/windows.html")
    assert judge.practice_clickthrough(page) == expected
    assert list(judge.PRACTICE_TEXTS) == expected
    assert page.locator("#c-n").inner_text() == "Done"
    for host in ("start.html", "docs/practice/windows.html"):
        source = (judge.ROOT / host).read_text()
        assert source.count('/practice/desktop.js"') == 1
        assert "function makeWin" not in source
        assert 'id="taskbar"' not in source


def test_try_stage_completes_both_chapters_using_only_highlights(stage_page):
    page, base = stage_page
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    judge.load(page, base + "start.html")
    assert page.locator("#c-n").inner_text() == "Step 1 of 12"
    assert page.locator("#c-prog h3").all_text_contents() == [
        "Chapter A: Set up your computer", "Chapter B: Get your agent",
    ]
    page.get_by_role("button", name="Try it yourself", exact=True).click()
    assert judge.highlighted_clickthrough(page) == list(range(1, 13))
    assert page.locator("#agent-pasted-line").inner_text() == page.locator("#setup-line").inner_text()
    assert page.locator("#studio-question").inner_text() == page.locator("#sample-question").inner_text()
    assert page.locator("#studio-agent").inner_text() == page.locator("#solution option:checked").inner_text()
    assert "Sample data: answer placeholder." in page.locator("#studio-answer").inner_text()
    assert not errors


def test_pause_holds_pending_install_work_and_mode_change_cancels_pointer_action(stage_page):
    page, base = stage_page
    page.emulate_media(reduced_motion="no-preference")
    judge.load(page, base + "start.html")
    page.get_by_role("button", name="Try it yourself", exact=True).click()
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
    assert page.locator("#c-n").inner_text() == "Step 4 of 12"
    page.get_by_role("button", name="Play again", exact=True).click()
    page.wait_for_timeout(1150)
    page.get_by_role("button", name="Try it yourself", exact=True).click()
    page.wait_for_timeout(1200)
    assert page.locator("#c-n").inner_text() == "Step 1 of 12"
    assert not page.locator("#start").evaluate("e => e.classList.contains('open')")


def test_picker_replaces_replayed_run_and_rejects_an_inexact_setup_line(stage_page):
    page, base = stage_page
    judge.load(page, base + "start.html")
    page.get_by_role("button", name="Play again", exact=True).click()
    options = page.locator("#solution option").evaluate_all("es => es.map(e => e.value)")
    page.locator("#solution").select_option(options[1])
    page.wait_for_function("() => document.querySelector('#c-n').textContent === 'Step 9 of 12'")
    assert options[1] in page.locator("#setup-line").inner_text()
    page.get_by_role("button", name="Try it yourself", exact=True).click()
    page.locator("#agent-chat").click()
    page.locator(".vsc textarea").fill("A different setup line")
    page.locator(".vsc .send").click()
    assert page.locator("#c-n").inner_text() == "Step 10 of 12"
    assert "paste it exactly" in page.locator("#toast").inner_text()
    assert not page.locator("#agent-pasted-line").count()
    page.locator(".vsc textarea").fill(page.locator("#setup-line").inner_text())
    page.locator(".vsc .send").click()
    page.locator("#ms-signin").wait_for()
    page.locator("#solution").select_option(options[2])
    page.wait_for_function("() => document.querySelector('#c-n').textContent === 'Step 9 of 12'")
    page.wait_for_timeout(1200)
    assert page.locator("#c-n").inner_text() == "Step 9 of 12"
    assert page.locator(".win").count() == 1
    assert not page.locator("#ms-signin").count()
    assert options[2] in page.locator("#setup-line").inner_text()


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
