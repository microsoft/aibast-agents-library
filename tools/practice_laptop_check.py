"""Real laptop practice-computer acceptance, using browser input and geometry."""

import json


RECTS = """selectors => {
    const viewport = {left:0, top:0, right:innerWidth, bottom:innerHeight};
    const inside = (a,b) => a.width > 0 && a.height > 0 &&
        a.left >= b.left - .5 && a.right <= b.right + .5 &&
        a.top >= b.top - .5 && a.bottom <= b.bottom + .5;
    return Object.fromEntries(selectors.map(selector => {
        const el = document.querySelector(selector);
        if (!el || !el.checkVisibility()) return [selector, false];
        const r = el.getBoundingClientRect();
        let visible = inside(r, viewport);
        for (let p = el.parentElement; p; p = p.parentElement) {
            const s = getComputedStyle(p);
            if (/(auto|scroll|hidden|clip)/.test(s.overflowX + s.overflowY))
                visible &&= inside(r, p.getBoundingClientRect());
        }
        const win = el.closest('.win');
        if (win) visible &&= inside(r, win.getBoundingClientRect());
        const points = [[r.x+r.width/2,r.y+r.height/2],
            [r.left+4,r.top+4], [r.right-4,r.top+4],
            [r.left+4,r.bottom-4], [r.right-4,r.bottom-4]];
        return [selector, visible && points.every(([x,y]) =>
            el.contains(document.elementFromPoint(x,y)))];
    }));
}"""

MESSAGES = """() => {
    const log = document.querySelector('.bs .log');
    const r = log.getBoundingClientRect(), style = getComputedStyle(log);
    const latest = [...log.querySelectorAll('.m')].slice(-2);
    return {
        six_lines:log.clientHeight >= 6 * parseFloat(style.lineHeight),
        latest_question_and_reply:latest.every(el => {
            const b = el.getBoundingClientRect();
            return b.top >= r.top && b.bottom <= r.bottom;
        })
    };
}"""


def measure(browser, base, shots):
    from tools.first_minute_check import (
        LAPTOP_VIEWPORTS, journey_clickthrough, load, result,
        studio_answer_readability,
    )
    shots.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(reduced_motion="reduce")
    context.route("**/*", lambda route: route.continue_()
                  if route.request.url.startswith(base) else route.abort("blockedbyclient"))
    page = context.new_page()
    page.set_default_timeout(4000)
    page.add_init_script("""Object.defineProperty(navigator.clipboard, 'readText', {
        value:() => {
            window.clipboardReads = (window.clipboardReads || 0) + 1;
            return Promise.reject(new DOMException('Denied', 'NotAllowedError'));
        }
    }); window.clipboardReads = 0;""")
    fit, focus, lists, skips, paste = {}, {}, {}, {}, {}

    def rects(key, selectors):
        fit[key] = page.evaluate(RECTS, selectors)

    def open_step(number):
        load(page, base + f"docs/practice/windows.html?watch=0&step={number}")
        page.wait_for_function("(n) => window.practicePC?.step() === n-1", arg=number)
        if number == 4:
            page.locator("#ghcode").wait_for()

    def inspect(number, local, size):
        key = f"{size}-{'windows' if local else 'start'}-{number}"
        typed = ({2:"#ssearch", 3:".ps .in", 4:"#ghcode", 6:".bs form input",
                  12:".bs form input", 14:".bs form input", 16:".bs form input"}
                 if local else {2:".vsc textarea"})
        if number in typed:
            focus[key] = page.locator(typed[number]).evaluate(
                "e => e === document.activeElement && scrollX === 0 && scrollY === 0")
        page.get_by_role("button", name="Show me where", exact=True).click()
        selector = page.locator("#hint").get_attribute("data-target")
        rects(key + "-target", [selector] if selector else ["#missing-target"])
        fit[key + "-desktop"] = page.evaluate("""() => {
            const pc = document.querySelector('#pc').getBoundingClientRect();
            const bar = document.querySelector('#coach').getBoundingClientRect();
            return {no_page_scroll:scrollY === 0 && scrollX === 0,
                desktop_and_bar:pc.top >= 0 && bar.bottom <= innerHeight,
                sixty_percent:pc.height >= innerHeight * .6};
        }""")
        rects(key + "-taskbar", ["#tb-start", "#taskbar .clock"])
        lists[key] = page.evaluate("""() => {
            const list = document.querySelector('.all-steps');
            const current = list.querySelector('[aria-current="step"]');
            const bounds = list.getBoundingClientRect();
            const visible = el => {
                const r = el.getBoundingClientRect();
                return el.checkVisibility() && r.top >= bounds.top &&
                    r.bottom <= bounds.bottom && r.bottom <= innerHeight;
            };
            const compact = getComputedStyle(list.querySelector('summary')).display !== 'none';
            return compact && !list.open
                ? /Step \\d+ of (17|4)/.test(document.querySelector('#c-n').textContent) &&
                    /Steps/i.test(list.querySelector('summary').textContent)
                : !!current && visible(current) && visible(current.parentElement.querySelector('h3')) &&
                    [...list.querySelectorAll('h3')].every(visible);
        }""")
        if local and number >= 6 and number not in (7, 8, 10, 11, 13):
            fit[key + "-messages"] = page.evaluate(MESSAGES)
        if local and number == 4:
            rects(key + "-code", ["#ghcode", "#ghgo"])
            fit[key + "-your-code"] = page.evaluate("""() => {
                const field = document.querySelector('#ghcode').getBoundingClientRect();
                return [...document.querySelectorAll('#ghcard p, .ps .out span')]
                    .filter(e => /Your code.*A1B2-C3D4/.test(e.textContent))
                    .some(code => {
                        const r = code.getBoundingClientRect();
                        const at = document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
                        return code.contains(at) && r.top >= 0 && r.bottom <= innerHeight &&
                            field.bottom <= innerHeight;
                    });
            }""")
            page.locator("#ghcode").fill("A1B2-C3D4")
            page.locator("#ghgo").click()
            rects(key + "-authorize", ["#ghauth"])
        if local and number == 11:
            page.locator("#bs-delete-agent").click()
            rects(key + "-confirm-delete", ["#bs-confirm-delete"])
        if not local and number == 4:
            rects(key + "-open-studio", ["#agent-open"])
            fit[key + "-hint-on-open-studio"] = selector == "#agent-open"
        if size in ("1366x625", "1280x585") and (
                local and number in (3, 4, 6, 8, 11, 12) or not local and number == 2):
            page.screenshot(path=str(shots / f"{'windows' if local else 'start'}-{size}-step-{number}.png"))

    try:
        for width, height in LAPTOP_VIEWPORTS:
            page.set_viewport_size({"width":width, "height":height})
            size = f"{width}x{height}"
            for number in range(1, 18):
                try:
                    open_step(number)
                    inspect(number, True, size)
                    if number == 8:
                        page.get_by_role("button", name="What do you remember?", exact=True).click()
                        fit[f"{size}-windows-8-finish-messages"] = page.evaluate(MESSAGES)
                        rects(f"{size}-windows-8-keep-going", ["#stage-keep-going"])
                except Exception as exc:
                    fit[f"{size}-windows-{number}-error"] = {"error":str(exc), "pass":False}
            try:
                load(page, base + "start.html?watch=0")
                journey_clickthrough(page, on_step=lambda n: inspect(n, False, size))
                readable = studio_answer_readability(page)
                fit[f"{size}-studio-five-lines"] = readable["full_lines"] >= 5
                # Check the initial question, not the end-scrolled answer.
                page.locator(".studio-thread").press("Home")
                page.wait_for_function("document.querySelector('.studio-thread').scrollTop === 0")
                rects(f"{size}-studio-question", ["#studio-question"])
                if size in ("1366x625", "1280x585"):
                    page.screenshot(path=str(shots / f"start-{size}-step-4-after-send.png"))
            except Exception as exc:
                fit[f"{size}-start-error"] = {"error":str(exc), "pass":False}

        page.set_viewport_size({"width":1280, "height":585})
        for number in range(1, 17):
            open_step(number)
            if not page.get_by_role("button", name="Skip this step", exact=True).count():
                continue
            try:
                page.get_by_role("button", name="Skip this step", exact=True).click()
                page.wait_for_function("(n) => window.practicePC.step() === n", arg=number)
                journey_clickthrough(page, first=number+1, last=number+1)
                if number == 7:
                    page.get_by_role("button", name="Keep going", exact=True).first.click()
                skips[str(number)] = page.evaluate("window.practicePC.step()") == number+1
            except Exception as exc:
                skips[str(number)] = {"error":str(exc), "pass":False}

        for denied in (False, True):
            try:
                context.grant_permissions(["clipboard-read", "clipboard-write"], origin=base.rstrip("/"))
                open_step(3)
                line = page.locator("#c-acts [data-line]").get_attribute("data-line")
                page.evaluate("line => navigator.clipboard.writeText(line)", line)
                if denied:
                    cdp = context.new_cdp_session(page)
                    context_id = cdp.send("Target.getTargetInfo")["targetInfo"]["browserContextId"]
                    cdp.send("Browser.setPermission", {
                        "permission":{"name":"clipboard-read"}, "setting":"denied",
                        "origin":base.rstrip("/"), "browserContextId":context_id,
                    })
                    paste["read-permission-denied"] = page.evaluate(
                        "() => navigator.permissions.query({name:'clipboard-read'}).then(p => p.state === 'denied')")
                page.locator(".ps .in").click()
                page.keyboard.press("Control+v")
                paste[f"ctrl-v-denied-{denied}"] = page.locator(".ps .in").inner_text() == line
                page.locator(".ps .in").fill("")
                page.keyboard.press("Meta+v" if page.evaluate(
                    "navigator.platform.startsWith('Mac')") else "Control+v")
                paste[f"native-paste-denied-{denied}"] = page.locator(".ps .in").inner_text() == line
                paste[f"native-no-read-denied-{denied}"] = page.evaluate("window.clipboardReads === 0")
                open_step(3)
                page.get_by_role("button", name="Copy the real line", exact=True).click()
                page.locator(".ps .in").click(button="right")
                paste[f"right-click-denied-{denied}"] = page.locator(".ps .in").inner_text() == line
                paste[f"no-read-denied-{denied}"] = page.evaluate("window.clipboardReads === 0")
            except Exception as exc:
                paste[f"denied-{denied}"] = {"error":str(exc), "pass":False}
    finally:
        context.close()

    def passed(value):
        if isinstance(value, dict):
            return bool(value) and all(passed(flag) for flag in value.values())
        return value is True

    return [result(check, values, passed(values)) for check, values in (
        ("J80", fit), ("J81", skips), ("J82", paste), ("J83", focus), ("J84", lists))]


if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    from tools.first_minute_check import ROOT, local_site
    with local_site(ROOT) as base, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            checks = measure(browser, base, ROOT / "_shots/v")
            print(json.dumps(checks))
        finally:
            browser.close()
    raise SystemExit(0 if all(check["pass"] for check in checks) else 1)
