"""AIdeate's progressive wheel enhancement must never hide its content."""

import pytest

from tools.first_minute_check import ROOT, load, local_site
from tools import first_minute_check as judge


@pytest.fixture(scope="module")
def aideate_browser():
    playwright = pytest.importorskip("playwright.sync_api")
    with local_site(ROOT) as base, playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        try:
            yield browser, base
        finally:
            browser.close()


def wheel_snapshot(page):
    return page.locator(".ai-ring").evaluate("""e => ({
        labels: [...e.querySelectorAll('.ai-node,.ai-mid')].map(n => ({
            text:n.innerText, style:n.getAttribute('style')
        })),
        canvas:e.querySelector('canvas')?.toDataURL(),
        highlighted:document.querySelectorAll('.ai-steps .is-on').length,
        frames:window.wheelFrames
    })""")


@pytest.mark.parametrize("webgl", [False, True])
@pytest.mark.parametrize("width", [360, 390, 768, 1440])
def test_wheel_content_and_canvas_stay_inside_viewport(aideate_browser, webgl, width):
    browser, base = aideate_browser
    context = browser.new_context(viewport={"width": width, "height": 900})
    context.route("https://**/*", lambda route: route.abort("blockedbyclient"))
    if not webgl:
        context.add_init_script("""
            const getContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(kind, ...args) {
                return /webgl/i.test(kind) ? null : getContext.call(this, kind, ...args);
            };
        """)
    try:
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda message: errors.append(message.text)
                if message.type == "error" and message.location.get("url", "").startswith(base)
                else None)
        load(page, base + "aideate.html")
        for label in ("Clarify", "Prove", "Reuse", "From idea to"):
            assert page.locator(".ai-ring").get_by_text(label, exact=False).is_visible()
        if not webgl:
            assert page.locator(".ai-ring svg").is_visible()
            assert page.locator(".ai-ring canvas").count() == 0
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert page.locator(".ai-ring canvas").evaluate_all(
            "es => es.every(e => {const r=e.getBoundingClientRect(); "
            "return r.left >= 0 && r.right <= innerWidth;})"
        )
        assert not errors
    finally:
        context.close()


def test_reduced_motion_wheel_never_schedules_animation_or_reacts_to_pointer(aideate_browser):
    browser, base = aideate_browser
    context = browser.new_context(reduced_motion="reduce")
    context.route("https://**/*", lambda route: route.abort("blockedbyclient"))
    context.add_init_script("""
        window.wheelFrames = 0;
        const raf = window.requestAnimationFrame;
        window.requestAnimationFrame = callback => {
            window.wheelFrames++;
            return raf(callback);
        };
    """)
    try:
        page = context.new_page()
        load(page, base + "aideate.html")
        page.locator(".ai-ring").scroll_into_view_if_needed()
        before = wheel_snapshot(page)
        page.locator(".ai-loop").hover(position={"x": 20, "y": 20})
        page.wait_for_timeout(500)
        assert wheel_snapshot(page) == before
        assert before["highlighted"] == 0
        assert before["frames"] == 0
        assert page.locator(".ai-ring").evaluate(
            "e => e.getAnimations({subtree:true}).every(a => a.playState !== 'running')"
        )
    finally:
        context.close()


@pytest.mark.parametrize("mutation,failed", [
    ("console.error('AIdeate test error')", "zero_console_errors"),
    ("document.querySelector('.ai-cta').textContent = 'Another action'", "one_request_primary"),
    ("document.querySelector('h1').textContent = 'Only we have this'", "approved_copy"),
    ("document.querySelector('main').style.minWidth = '1600px'", "no_phone_overflow"),
    ("document.querySelector('.ai-soon strong').outerHTML = "
     "'<a href=\"https://rapp.microsoft.com\">rapp.microsoft.com</a>'",
     "preview_address_not_linked"),
])
def test_aideate_judge_rejects_real_page_regressions(aideate_browser, monkeypatch, mutation, failed):
    browser, base = aideate_browser
    original_load = judge.load

    def mutated_load(page, url):
        original_load(page, url)
        if url.endswith("/aideate.html"):
            page.evaluate(mutation)

    monkeypatch.setattr(judge, "load", mutated_load)
    checks = judge.measure_aideate(browser, base, set())
    assert checks[0]["id"] == "J42"
    assert not checks[0]["pass"]
    assert not checks[0]["value"][failed]
    assert checks[1]["pass"]


def test_aideate_judge_passes_published_page_and_navigation(aideate_browser):
    browser, base = aideate_browser
    checks = judge.measure_aideate(browser, base, set())
    assert [check["id"] for check in checks] == ["J42", "J43"]
    assert all(check["pass"] for check in checks)


@pytest.mark.parametrize("source", ["index.html", "start.html", "aideate.html"])
def test_aideate_judge_rejects_unreachable_links(aideate_browser, monkeypatch, source):
    browser, base = aideate_browser
    original_load = judge.load

    def mutated_load(page, url):
        original_load(page, url)
        if url.endswith("/" + source):
            page.evaluate("""() => {
                if (location.pathname.endsWith('/aideate.html')) {
                    document.querySelector('.ai-quiet').href = '#missing-section';
                } else {
                    document.querySelectorAll('a[href="aideate.html"]').forEach(e => e.remove());
                }
            }""")

    monkeypatch.setattr(judge, "load", mutated_load)
    checks = judge.measure_aideate(browser, base, set())
    assert checks[0]["pass"]
    assert not checks[1]["pass"]
