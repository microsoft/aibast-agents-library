"""Browser evidence for the library's decorative card icons (J76-J78)."""

import json
from pathlib import Path
import re
from statistics import median


ROOT = Path(__file__).resolve().parents[1]
SPECS = (
    ("J76", "icons_3d", "drawn; one context; fallback; rerenders; clean console"),
    ("J77", "icons_calm", "still idle; one hover/focus; reduced motion still"),
    ("J78", "icons_cost", "median <= baseline + 100ms; bounded canvases"),
)
PROBE = r"""
(() => {
    const original = HTMLCanvasElement.prototype.getContext;
    window.iconContexts = new Set();
    HTMLCanvasElement.prototype.getContext = function(kind, ...args) {
        const context = original.call(this, kind, ...args);
        if (context && /^(webgl2?|experimental-webgl)$/.test(kind)) window.iconContexts.add(context);
        return context;
    };
    requestAnimationFrame(function firstCard() {
        const card = document.querySelector('.agent-card');
        const rect = card?.getBoundingClientRect();
        if (rect && rect.width && rect.bottom > 0 && rect.top < innerHeight) {
            window.firstCardVisible = performance.now();
        } else requestAnimationFrame(firstCard);
    });
})();
"""
SNAPSHOT = r"""() => {
    const icons = [...document.querySelectorAll('.agent-icon')].filter(e => {
        const r = e.getBoundingClientRect();
        return e.checkVisibility() && r.bottom > 0 && r.top < innerHeight
            && r.right > 0 && r.left < innerWidth;
    });
    const pixels = e => {
        const c = e.querySelector('canvas');
        if (!c) return null;
        const bytes = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
        let hash = 2166136261, filled = 0;
        for (let i = 0; i < bytes.length; i++) {
            hash = Math.imul(hash ^ bytes[i], 16777619);
            if (i % 4 === 3 && bytes[i]) filled++;
        }
        return {hash, filled, decorative: c.getAttribute('aria-hidden') === 'true'};
    };
    return {
        icons: icons.map(pixels),
        glyphs: icons.every(e => e.textContent.trim()
            && parseFloat(getComputedStyle(e).fontSize) > 0
            && !e.querySelector('canvas')),
        contexts: window.iconContexts.size,
        canvases: document.querySelectorAll('.agent-icon canvas').length,
        visible: icons.length
    };
}"""


def drawn(snapshot):
    return bool(snapshot["icons"]) and all(
        icon and icon["filled"] > 20 and icon["decorative"]
        for icon in snapshot["icons"]
    )


def hashes(page):
    return [icon and icon["hash"] for icon in page.evaluate(SNAPSHOT)["icons"]]


def symbol_sheet(page, shots):
    page.mouse.move(0, 0)
    page.evaluate("""() => {
        const sheet = document.createElement('section');
        sheet.id = 'icon-evidence';
        sheet.setAttribute('aria-label', 'All fourteen symbols at card size');
        Object.assign(sheet.style, {
            position: 'fixed', inset: '0', zIndex: '100', padding: '48px',
            background: 'var(--cp-bg)', display: 'grid',
            gridTemplateColumns: 'repeat(7, 1fr)', alignContent: 'center', gap: '24px'
        });
        for (const kind of Object.keys(CATEGORY_ICONS)) {
            const cell = document.createElement('div');
            cell.className = 'agent-card';
            Object.assign(cell.style, {
                padding: '24px 12px', display: 'grid', justifyItems: 'center',
                gap: '20px', textAlign: 'center'
            });
            const icon = document.createElement('span');
            icon.className = 'agent-icon';
            icon.dataset.iconKind = kind;
            icon.textContent = CATEGORY_ICONS[kind];
            const label = document.createElement('span');
            label.textContent = CATEGORY_NAMES[kind] || 'Customer Service';
            cell.append(icon, label);
            sheet.append(cell);
        }
        document.body.append(sheet);
    }""")
    page.wait_for_timeout(350)
    pixels = page.locator("#icon-evidence .agent-icon").evaluate_all(
        """es => es.map(e => {
            const c = e.querySelector('canvas');
            if (!c) return false;
            const data = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
            const points = [];
            for (let i = 3; i < data.length; i += 4) {
                if (data[i] > 128) points.push((i - 3) / 4);
            }
            if (!points.length) return false;
            const xs = points.map(i => i % c.width), ys = points.map(i => Math.floor(i / c.width));
            const fill = Math.max(Math.max(...xs) - Math.min(...xs),
                Math.max(...ys) - Math.min(...ys)) / c.width;
            return fill >= 0.58 && fill <= 0.75;
        })""")
    if shots:
        page.screenshot(path=str(shots / "all-14-symbols.png"))
    page.locator("#icon-evidence").evaluate("e => e.remove()")
    return len(pixels) == 14 and all(pixels)


def ready(page, base, query=""):
    page.goto(base + "index.html" + query, wait_until="networkidle")
    page.locator(".agent-icon").first.scroll_into_view_if_needed()
    page.wait_for_timeout(350)


def measure(browser, base, shots=None):
    """Measure actual pixels, context creation, fallback, interactions and cost."""
    checks = []
    errors = []
    shots = Path(shots) if shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)

    def context(*, owner=browser, **options):
        ctx = owner.new_context(viewport={"width": 1440, "height": 900}, **options)
        ctx.add_init_script(PROBE)
        ctx.route("**/*", lambda route: route.continue_()
                  if route.request.url.startswith(base) else route.abort("blockedbyclient"))
        return ctx

    def record(check_id, values, passed):
        _, name, target = next(spec for spec in SPECS if spec[0] == check_id)
        checks.append({
            "id": check_id, "name": name, "target": target,
            "value": values, "pass": bool(passed),
        })

    ctx = context()
    page = ctx.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: errors.append(message.text)
            if message.type == "error" and "ERR_BLOCKED_BY_CLIENT" not in message.text else None)
    try:
        ready(page, base)
        initial = page.evaluate(SNAPSHOT)
        if shots:
            page.screenshot(path=str(shots / "cards-1440.png"))
        idle = hashes(page)
        page.wait_for_timeout(2000)
        calm = {"idle_2s": hashes(page) == idle}
        page.locator(".agent-card").first.hover()
        page.wait_for_timeout(400)
        hover_start = hashes(page)
        page.wait_for_timeout(500)
        hover_end = hashes(page)
        calm["only_hovered_changes"] = bool(hover_start) and hover_start[0] != hover_end[0] \
            and hover_start[1:] == hover_end[1:]
        if shots:
            page.screenshot(path=str(shots / "card-hovered.png"))
        page.mouse.move(0, 0)
        page.wait_for_timeout(200)
        page.locator(".agent-card").first.focus()
        page.wait_for_timeout(400)
        focused = hashes(page)
        page.wait_for_timeout(500)
        focus_end = hashes(page)
        calm["only_focused_changes"] = bool(focused) and focused[0] != focus_end[0] \
            and focused[1:] == focus_end[1:]
        page.locator("#search").focus()

        variants = {}
        for query in ("?q=account", "?industry=healthcare", "?view=partners",
                      "?view=first-party"):
            ready(page, base, query)
            variants[query] = drawn(page.evaluate(SNAPSHOT))
        for view in ("stacks", "templates"):
            page.evaluate("view => { state.view = view; render(); }", view)
            page.locator(".agent-icon").first.scroll_into_view_if_needed()
            page.wait_for_timeout(350)
            variants[view] = drawn(page.evaluate(SNAPSHOT))
        ready(page, base)
        page.locator("#search").fill("account")
        page.wait_for_timeout(500)
        variants["live_search"] = drawn(page.evaluate(SNAPSHOT))
        page.locator("#search").fill("")
        page.locator(".more-filters summary").click()
        page.locator("#industry").select_option("healthcare")
        page.wait_for_timeout(500)
        variants["live_filter"] = drawn(page.evaluate(SNAPSHOT))
        page.evaluate("""() => {
            const card = document.querySelector('.agent-card').cloneNode(true);
            card.querySelectorAll('canvas').forEach(e => e.remove());
            card.querySelectorAll('[data-icon-drawn]').forEach(e => delete e.dataset.iconDrawn);
            document.querySelector('#grid').prepend(card);
        }""")
        page.wait_for_timeout(350)
        variants["added_later"] = drawn(page.evaluate(SNAPSHOT))
        variants["all_14_card_size"] = symbol_sheet(page, shots)

        bounds = []
        ready(page, base)
        height = page.evaluate("document.documentElement.scrollHeight")
        for top in range(0, height, 650):
            page.evaluate("top => scrollTo(0, top)", top)
            page.wait_for_timeout(75)
            state = page.evaluate(SNAPSHOT)
            bounds.append(state["contexts"] == 1
                          and state["canvases"] <= state["visible"] + 3)
        cost = {"one_context_bounded_canvases": all(bounds)}
        page.set_viewport_size({"width": 390, "height": 844})
        ready(page, base)
        variants["phone"] = drawn(page.evaluate(SNAPSHOT))
        if shots:
            page.screenshot(path=str(shots / "cards-390.png"))
        page.emulate_media(reduced_motion="reduce")
        page.mouse.move(0, 0)
        ready(page, base)
        reduced = hashes(page)
        page.locator(".agent-card").first.hover()
        page.wait_for_timeout(2000)
        calm["reduced_hover_2s"] = hashes(page) == reduced
        page.locator(".agent-card").first.focus()
        page.wait_for_timeout(500)
        calm["reduced_focus"] = hashes(page) == reduced
    except Exception as exc:
        record("J76", {"error": f"{type(exc).__name__}: {exc}"}, False)
        calm = {"incomplete": False}
        cost = {"incomplete": False}
    finally:
        ctx.close()

    fallbacks = {}
    for mode in ("webgl_off", "module_failure"):
        disabled = browser.browser_type.launch(args=["--disable-webgl"]) \
            if mode == "webgl_off" else None
        ctx = context(owner=disabled or browser)
        if mode == "module_failure":
            ctx.route("**/docs/card-icons.js", lambda route: route.fulfill(
                content_type="text/javascript", body="throw new Error('module unavailable');"))
        page = ctx.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda message: errors.append(message.text)
                if message.type == "error" and "ERR_BLOCKED_BY_CLIENT" not in message.text else None)
        try:
            ready(page, base)
            snapshot = page.evaluate(SNAPSHOT)
            fallbacks[mode] = snapshot["glyphs"] and snapshot["contexts"] == 0
            if shots and mode == "webgl_off":
                page.screenshot(path=str(shots / "webgl-off.png"))
        finally:
            ctx.close()
            if disabled:
                disabled.close()
    if not any(check["id"] == "J76" for check in checks):
        values = {"initial_drawn": drawn(initial), "one_context": initial["contexts"] == 1,
                  **variants, **fallbacks, "console_errors": errors}
        record("J76", values, drawn(initial) and initial["contexts"] == 1
               and all(variants.values()) and all(fallbacks.values()) and not errors)
    record("J77", calm, all(calm.values()))

    timings = {"before": [], "after": []}
    for _ in range(5):
        for mode in timings:
            ctx = context()
            def serve_index(route):
                response = route.fetch()
                body = response.text()
                if mode == "before":
                    body = re.sub(r"// card-icons:start.*?// card-icons:end",
                                  "", body, flags=re.S)
                route.fulfill(response=response, body=body)
            ctx.route("**/index.html", serve_index)
            page = ctx.new_page()
            try:
                page.goto(base + "index.html#grid", wait_until="domcontentloaded")
                page.wait_for_function("window.firstCardVisible > 0")
                timings[mode].append(round(page.evaluate("window.firstCardVisible"), 2))
            finally:
                ctx.close()
    timing = {mode: median(samples) for mode, samples in timings.items()}
    cost.update(samples_ms=timings, median_ms=timing,
                delta_ms=round(timing["after"] - timing["before"], 2))
    record("J78", cost, cost.get("one_context_bounded_canvases", False)
           and cost["delta_ms"] <= 100)
    return checks


if __name__ == "__main__":
    from first_minute_check import local_site
    from playwright.sync_api import sync_playwright

    with local_site(ROOT) as base, sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        try:
            checks = measure(browser, base, ROOT / "_shots/q")
            print(json.dumps(checks, indent=2))
            (ROOT / "_shots/q/latest.json").write_text(json.dumps(checks, indent=2) + "\n")
        finally:
            browser.close()
    raise SystemExit(int(any(not check["pass"] for check in checks)))
