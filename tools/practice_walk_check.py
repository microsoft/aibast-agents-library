"""Regressions from the real-browser ORDER Y walk, measured with browser input."""

from tools.practice_laptop_check import RECTS


SPECS = (
    ("J88", "walk_typing_focus", "real caret + spaced keyboard input on every typed step"),
    ("J89", "walk_finish_once", "one Keep going + one finish sentence, whole page"),
    ("J90", "express_paste_parity", "Ctrl+V + right click + visible paste; gesture-only reads"),
    ("J91", "walk_cookie_clearance", "both pages; 1366x625, 1280x585, 1366x583, 390x844; full bar hit tests"),
    ("J92", "walk_pause_clearance", "all 17 + 4 steps; notice never covers current target"),
    ("J93", "walk_signin_help", "Stuck points to visible Your code on sign-in card"),
    ("J94", "walk_news_guidance", "exact words + one-click fill in Show me where and Stuck"),
    ("J95", "walk_background_resume", "hidden/visible mid-action; advances or visible Resume"),
    ("J96", "express_send_clearance", "Send >= one space token from window edge at all sizes"),
    ("J97", "express_direct_steps", "?step=1-4; real reachable state; invalid values start at 1"),
)


def finish_counts(page):
    return page.evaluate("""() => {
        const visible = e => {
            if (!e.checkVisibility()) return false;
            const r = e.getBoundingClientRect();
            if (r.bottom <= 0 || r.top >= innerHeight) return false;
            for (let p = e; p; p = p.parentElement)
                if (getComputedStyle(p).clipPath !== 'none') return false;
            return true;
        };
        const sentence = 'You have met it. It still knows you.';
        return {
            buttons:[...document.querySelectorAll('button')].filter(e =>
                visible(e) && e.textContent.trim() === 'Keep going').length,
            sentences:[...document.querySelectorAll('body *')].filter(e =>
                visible(e) && e.textContent.trim() === sentence &&
                ![...e.children].some(child => child.textContent.trim() === sentence)).length
        };
    }""")


def measure(browser, base, shots):
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from tools.first_minute_check import (
        LAPTOP_VIEWPORTS, SETTLE_TIMEOUT, load, measurement_failure, result, selected, wait_for_layout,
    )

    shots.mkdir(parents=True, exist_ok=True)
    checks = []
    for check_id, _, _ in SPECS:
        if not selected(check_id):
            continue
        context = browser.new_context(viewport={"width":1366, "height":768},
                                      reduced_motion="reduce",
                                      permissions=["clipboard-read", "clipboard-write"])
        context.route("**/*", lambda route: route.continue_()
                      if route.request.url.startswith(base) else route.abort("blockedbyclient"))
        page = context.new_page()
        page.set_default_timeout(SETTLE_TIMEOUT)
        errors = []
        page.on("pageerror", lambda error: errors.append(error.stack))

        def practice(number):
            load(page, base + f"docs/practice/windows.html?watch=0&step={number}")
            page.wait_for_function(
                "n => window.practicePC?.step() === n - 1", arg=number)

        def express(number=1):
            load(page, base + "start.html?watch=0")
            page.wait_for_function("() => !!window.practicePC")
            if number > 1:
                page.locator("#agent-chat").click()
            if number > 2:
                page.locator(".vsc textarea").fill(page.locator("#setup-line").inner_text())
                page.keyboard.press("Enter")
                page.locator("#ms-signin").wait_for()
            if number > 3:
                page.locator("#ms-signin").click()
                page.locator("#agent-yes").click()

        def picture(name):
            page.screenshot(path=str(shots / f"{name}.png"))

        def clear_controls(selectors):
            values = page.evaluate(RECTS, selectors)
            assert all(values.values()), values
            return values

        def caret(selector, text):
            assert page.locator(selector).evaluate("e => e === document.activeElement"), selector
            page.keyboard.type(text)
            assert page.locator(selector).evaluate(
                "(e, text) => (e.isContentEditable ? e.textContent : e.value) === text", text
            ), selector
            assert page.evaluate("scrollX === 0 && scrollY === 0")

        try:
            values = {}
            if check_id == "J88":
                typed = {2:("#ssearch", "PowerShell"), 3:(".ps .in", "a line with spaces"),
                         4:("#ghcode", "A1B2-C3D4"), 6:(".bs form input", "Remember my name"),
                         12:(".bs form input", "get my latest hacker news"),
                         14:(".bs form input", "get my latest hacker news"),
                         16:(".bs form input", "Learn a new agent")}
                for number, (selector, text) in typed.items():
                    practice(number)
                    caret(selector, text)
                    values[str(number)] = True
                practice(15)
                page.locator("#bs-book").click()
                picture("item-1-library-open")
                caret("#bs-library-search", "meeting prep")
                assert page.locator("#bs-add-meeting").is_visible()
                picture("item-1-library-typed")
                values["library"] = True
                express(2)
                caret(".vsc textarea", "a setup line with spaces")
                express(4)
                page.locator("#agent-open").click()
                assert page.locator("#studio-input").evaluate("e => e === document.activeElement")
                page.keyboard.press("ControlOrMeta+A")
                page.keyboard.type("a sample question")
                assert page.locator("#studio-input").input_value() == "a sample question"
                values["express_inputs"] = True
            elif check_id == "J89":
                practice(8)
                page.get_by_role("button", name="What do you remember?", exact=True).click()
                picture("item-2-finish")
                values = finish_counts(page)
                assert values == {"buttons":1, "sentences":1}, values
                page.get_by_role("button", name="Keep going", exact=True).click()
                assert page.evaluate("window.practicePC.step() === 8")
            elif check_id == "J90":
                page.add_init_script("""window.__clipboardReads = [];
                    Object.defineProperty(navigator.clipboard, 'readText', {value:() => {
                        window.__clipboardReads.push(navigator.userActivation.isActive);
                        return Promise.reject(new DOMException('Denied', 'NotAllowedError'));
                    }});""")
                for local in (True, False):
                    for method in ("Control+v", "right-click", "visible"):
                        practice(3) if local else express(2)
                        selector = ".ps .in" if local else ".vsc textarea"
                        expected = (page.locator("#c-acts [data-line]").get_attribute("data-line")
                                    if local else page.locator("#setup-line").inner_text())
                        assert page.evaluate("window.__clipboardReads.length === 0")
                        if method == "Control+v":
                            page.keyboard.press("Control+v")
                        elif method == "right-click":
                            page.locator(selector).click(button="right")
                        else:
                            helper = page.get_by_role("button", name="Type it for me", exact=True)
                            assert helper.is_visible(), "visible paste affordance"
                            helper.click()
                        page.wait_for_function("""({selector, expected}) => {
                            const e = document.querySelector(selector);
                            return (e.isContentEditable ? e.textContent : e.value) === expected;
                        }""", arg={"selector":selector, "expected":expected}, timeout=1500)
                        assert page.evaluate("window.__clipboardReads.every(Boolean)")
                        values[f"{local}-{method}"] = True
            elif check_id == "J91":
                site = "https://microsoft.github.io/aibast-agents-library/"

                def local_pages(route):
                    if route.request.url.startswith(site):
                        response = route.fetch(url=base + route.request.url[len(site):])
                        route.fulfill(response=response)
                    else:
                        route.abort("blockedbyclient")

                context.unroute("**/*")
                context.route("**/*", local_pages)
                for width, height in ((1366, 625), (1280, 585), (1366, 583), (390, 844)):
                    page.set_viewport_size({"width":width, "height":height})
                    for path in ("start.html", "docs/practice/windows.html"):
                        page.goto(site + path + "?watch=0&step=2")
                        page.wait_for_function("() => !!window.practicePC")
                        page.locator("#aibast-clarity-consent").wait_for(state="visible")
                        if path == "start.html" and page.evaluate("window.practicePC.step()") == 0:
                            page.locator("#agent-chat").click()
                        page.wait_for_function("document.querySelector('#c-n').textContent.startsWith('Step 2')")
                        page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
                        label = "start" if path == "start.html" else "practice"
                        picture(f"item-4-{label}-{width}x{height}")
                        values[f"{label}-{width}x{height}-layout"] = page.evaluate("""() =>
                            Object.fromEntries(['#pc','#coach','#aibast-clarity-consent',
                                '#practice-computer'].map(s => {
                                const e = document.querySelector(s), r = e.getBoundingClientRect();
                                return [s, {top:r.top, bottom:r.bottom, height:r.height,
                                    cssHeight:getComputedStyle(e).height,
                                    consent:e.getAttribute('data-consent-space'),
                                    reserve:e.style.getPropertyValue('--practice-desktop-height')}];
                            }))""")
                        assert page.locator("#pc").evaluate("e => e.getBoundingClientRect().height >= 200")
                        selectors = ["#c-say", "#c-n", "#watch-mode", "#try-mode", "#practice-mute"]
                        selectors += page.locator("#c-acts button").evaluate_all(
                            "es => es.flatMap((e,i) => e.checkVisibility() ? "
                            "['#c-acts button:nth-of-type('+(i+1)+')'] : [])")
                        values[f"{label}-{width}x{height}"] = clear_controls(selectors)
                        page.get_by_role("button", name="Show me where", exact=True).click()
                        assert page.locator("#aibast-clarity-consent").is_visible()
            elif check_id == "J92":
                for local, count in ((True, 17), (False, 4)):
                    for number in range(1, count + 1):
                        practice(number) if local else express(number)
                        page.get_by_role("button", name="Watch", exact=True).click()
                        page.locator("#pc").click(position={"x":120, "y":8})
                        page.locator("#watch-pause-notice").wait_for(state="visible")
                        overlap = page.evaluate("""() => {
                            const selector = document.querySelector('#hint').dataset.target;
                            const target = document.querySelector(selector);
                            if (!target) return true;
                            const a = document.querySelector('#watch-pause-notice').getBoundingClientRect();
                            const b = target.getBoundingClientRect();
                            return a.left < b.right && a.right > b.left &&
                                a.top < b.bottom && a.bottom > b.top;
                        }""")
                        assert not overlap, (local, number, "notice covers target on appearance")
                        wait_for_layout(page)
                        if local and number == 4:
                            page.locator("#ghcode").fill("A1B2-C3D4")
                            clear_controls(["#ghgo", "#watch-resume"])
                        if number == 4:
                            picture(f"item-5-{'practice' if local else 'start'}-step-4")
                        selector = page.locator("#hint").get_attribute("data-target")
                        assert selector
                        clear_controls([selector, "#watch-resume"])
                        values[f"{local}-{number}"] = True
            elif check_id == "J93":
                practice(4)
                page.locator("#step-help summary").click()
                help_text = page.locator("#step-help").inner_text()
                assert "Your code" in help_text and "sign-in card" in help_text, help_text
                clear_controls(["#ghcard .device-code", "#ghcode"])
                values["visible_code_and_help"] = True
            elif check_id == "J94":
                for help_control in ("Show me where", "Stuck?"):
                    practice(14)
                    if help_control == "Stuck?":
                        page.locator("#step-help summary").click()
                        area = page.locator("#step-help")
                    else:
                        page.get_by_role("button", name=help_control, exact=True).click()
                        area = page.locator("#coach")
                    assert "get my latest hacker news" in area.inner_text()
                    area.get_by_role("button", name="Type it for me", exact=True).click()
                    assert page.locator(".bs form input").input_value() == "get my latest hacker news"
                    assert page.locator(".bs form input").evaluate("e => e === document.activeElement")
                    page.keyboard.press("Enter")
                    assert page.evaluate("window.practicePC.step() === 14")
                    values[help_control] = True
            elif check_id == "J95":
                page.emulate_media(reduced_motion="no-preference")
                for local in (True, False):
                    practice(2) if local else express(2)
                    page.get_by_role("button", name="Watch", exact=True).click()
                    page.wait_for_function("""() =>
                        document.querySelector('#watch-pointer').classList.contains('click')""",
                                           timeout=30000)
                    before = page.evaluate("window.practicePC.capture()")
                    page.evaluate("""() => {
                        Object.defineProperty(document, 'hidden', {configurable:true, value:true});
                        document.dispatchEvent(new Event('visibilitychange'));
                    }""")
                    # Measure that Watch keeps exactly the same scene while hidden.
                    page.wait_for_timeout(1400)
                    assert page.evaluate("window.practicePC.capture()") == before
                    page.evaluate("""() => {
                        delete document.hidden;
                        document.dispatchEvent(new Event('visibilitychange'));
                    }""")
                    try:
                        page.wait_for_function("""before =>
                            JSON.stringify(window.practicePC.capture()) !== JSON.stringify(before)""",
                                               arg=before, timeout=12000)
                        values[str(local)] = "continued"
                    except PlaywrightTimeoutError:
                        assert page.locator("#stage-pause").inner_text() == "Resume"
                        assert page.locator("#watch-pause-notice").is_visible()
                        page.locator("#watch-resume").click()
                        page.wait_for_function("""before =>
                            JSON.stringify(window.practicePC.capture()) !== JSON.stringify(before)""",
                                               arg=before, timeout=15000)
                        values[str(local)] = "resumed"
                    picture(f"item-8-{'practice' if local else 'start'}-returned")
                    page.locator("#stage-pause").click()
                    assert page.locator("#stage-pause").inner_text() == "Resume"
                    paused = page.evaluate("window.practicePC.capture()")
                    page.evaluate("""() => {
                        Object.defineProperty(document, 'hidden', {configurable:true, value:true});
                        document.dispatchEvent(new Event('visibilitychange'));
                        delete document.hidden;
                        document.dispatchEvent(new Event('visibilitychange'));
                    }""")
                    assert page.evaluate("window.practicePC.capture()") == paused
                    assert page.locator("#stage-pause").inner_text() == "Resume"
                    values[f"{local}-deliberate-pause-kept"] = True
            elif check_id == "J96":
                for width, height in (*LAPTOP_VIEWPORTS, (390, 844)):
                    page.set_viewport_size({"width":width, "height":height})
                    express(2)
                    for screen, selector in (("copilot", ".vsc .send"), ("studio", "#studio-send")):
                        if screen == "studio":
                            express(4)
                            page.locator("#agent-open").click()
                        clear_controls([selector])
                        gap = page.locator(selector).evaluate("""e => {
                            const token = parseFloat(getComputedStyle(document.documentElement)
                                .getPropertyValue('--cp-space-3'));
                            return {actual:e.closest('.win').getBoundingClientRect().bottom -
                                e.getBoundingClientRect().bottom,
                                required:token * parseFloat(getComputedStyle(document.documentElement).fontSize)};
                        }""")
                        assert gap["actual"] >= gap["required"], (screen, width, height, gap)
                        values[f"{screen}-{width}x{height}"] = gap
            elif check_id == "J97":
                for requested in ("4", "3", "2", "1", "0", "5", "bad", "1.5"):
                    load(page, base + f"start.html?watch=0&step={requested}")
                    page.wait_for_function("() => !!window.practicePC")
                    expected = int(requested) if requested in ("1", "2", "3", "4") else 1
                    assert page.evaluate("window.practicePC.step()") == expected - 1, requested
                    if expected == 2:
                        caret(".vsc textarea", "linked setup")
                    if expected == 3:
                        page.locator("#ms-signin").click()
                        page.locator("#agent-yes").click()
                        page.locator("#agent-open").wait_for()
                    if expected == 4:
                        page.locator("#agent-open").click()
                        page.locator("#studio-send").click()
                        assert page.locator("#studio-answer").is_visible()
                    values[requested] = True
            assert not errors, errors
            checks.append(result(check_id, values, True))
        except Exception as exc:
            checks.append(measurement_failure(check_id, exc, observations=values))
        finally:
            context.close()
    return checks
