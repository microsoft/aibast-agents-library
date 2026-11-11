"""ORDER AA regressions, exercised with real Chromium input."""

from tools.practice_laptop_check import RECTS


SPECS = (
    ("J98", "pause_preserves_desktop", "every step and judged size; unchanged desktop + clickable target"),
    ("J99", "resume_is_explicit", "quiet remembered-step notice; first visit quiet; start + Watch replay reset"),
    ("J100", "shareable_current_step", "all direct steps + progress + restart + resume; replaceState only"),
    ("J101", "direct_step_starting_scenes", "all 4 + 17 direct links show their own ready-to-use starting scene"),
    ("J102", "restore_real_pointer_drag", "real mouse + touch down/move/up; cancellation + helper retained"),
    ("J103", "finish_sentence_once_in_dom", "one page-text copy + one accessible status; no clipped caption duplicate"),
)


def measure(browser, base, shots):
    from tools.first_minute_check import (
        LAPTOP_VIEWPORTS, load, measurement_failure, result, selected, wait_for_layout,
    )

    shots.mkdir(parents=True, exist_ok=True)
    checks = []
    for check_id, _, _ in SPECS:
        if not selected(check_id):
            continue
        context = browser.new_context(reduced_motion="reduce", has_touch=True,
                                      viewport={"width":1366, "height":583})
        context.route("**/*", lambda route: route.continue_()
                      if route.request.url.startswith(base) else route.abort("blockedbyclient"))
        page = context.new_page()
        page.set_default_timeout(4000)
        errors, values = [], {}
        page.on("pageerror", lambda error: errors.append(error.stack))

        def open_step(path, number):
            load(page, base + f"{path}?watch=0&step={number}")
            page.wait_for_function("n => window.practicePC?.step() === n - 1", arg=number)

        def clear(selectors):
            flags = page.evaluate(RECTS, selectors)
            assert all(flags.values()), flags

        def picture(name):
            page.screenshot(path=str(shots / f"{name}.png"))

        try:
            if check_id == "J98":
                for width, height in (*LAPTOP_VIEWPORTS, (390, 844)):
                    page.set_viewport_size({"width":width, "height":height})
                    for path, count in (("docs/practice/windows.html", 17), ("start.html", 4)):
                        for number in range(1, count + 1):
                            key = f"{path}-{number}-{width}x{height}"
                            open_step(path, number)
                            page.locator("#watch-mode").click()
                            wait_for_layout(page)
                            before = page.locator("#pc").bounding_box()
                            page.locator("#pc").click(position={"x":120, "y":1})
                            page.locator("#watch-pause-notice").wait_for(state="visible")
                            wait_for_layout(page)
                            after = page.locator("#pc").bounding_box()
                            assert before == after, (key, before, after)
                            selector = page.locator("#hint").get_attribute("data-target")
                            assert selector, key
                            clear([selector, "#watch-resume"])
                            if path.startswith("docs/") and number == 4:
                                page.locator("#ghcode").fill("A1B2-C3D4")
                                clear(["#ghgo"])
                                if (width, height) == (1366, 583):
                                    picture("item-1-step-4-paused-1366x583")
                            values[key] = True
            elif check_id == "J99":
                path = "docs/practice/windows.html"
                load(page, base + path + "?watch=0")
                assert page.evaluate("window.practicePC.step()") == 0
                assert page.get_by_text("Picking up at step", exact=False).count() == 0
                values["first_visit"] = True
                for number in (4, 8, 13, 17):
                    open_step(path, number)
                    load(page, base + path + "?watch=0")
                    assert page.evaluate("window.practicePC.step()") == number - 1
                    assert page.locator("#resume-notice").count() == 1, "missing resume notice"
                    assert page.locator("#resume-notice").inner_text().startswith(
                        f"Picking up at step {number}.")
                    clear(["#start-from-one"])
                    if number == 8:
                        picture("item-2-resumed-step-8")
                    page.locator("#start-from-one").click()
                    assert page.evaluate("window.practicePC.step()") == 0
                    assert page.locator("#resume-notice").is_hidden()
                    values[f"restart-{number}"] = True
                    open_step(path, number)
                    load(page, base + path + "?watch=0")
                    page.locator("#watch-mode").click()
                    clear(["#start-from-one", "#stage-again"])
                    page.locator("#stage-again").click()
                    assert page.evaluate("window.practicePC.step()") == 0
                    assert page.locator("#resume-notice").is_hidden()
                    page.locator("#try-mode").click()
                    values[f"replay-{number}"] = True
                open_step(path, 4)
                assert page.get_by_text("Picking up at step", exact=False).count() == 0
                values["direct_link_not_resume"] = True
            elif check_id == "J100":
                from urllib.parse import parse_qs, urlsplit

                def address(number):
                    query = parse_qs(urlsplit(page.url).query)
                    assert query.get("step") == [str(number)], page.url
                    assert query.get("watch") == ["0"], page.url
                    assert urlsplit(page.url).fragment == "practice", page.url

                for path, count in (("start.html", 4), ("docs/practice/windows.html", 17)):
                    for number in range(1, count + 1):
                        load(page, base + f"{path}?watch=0&step={number}#practice")
                        address(number)
                        values[f"{path}-{number}"] = True
                    load(page, base + f"{path}?watch=0&step=1#practice")
                    history = page.evaluate("history.length")
                    page.evaluate("window.__sameDocument = true")
                    page.locator("#agent-chat" if path == "start.html" else "#tb-start").click()
                    page.wait_for_function("window.practicePC.step() === 1")
                    address(2)
                    assert page.evaluate("history.length") == history
                    assert page.evaluate("window.__sameDocument === true")
                    page.get_by_role("button", name="Start over", exact=True).click()
                    address(1)
                    assert page.evaluate("history.length") == history
                    values[f"{path}-progress-and-restart"] = True
                open_step("docs/practice/windows.html", 13)
                load(page, base + "docs/practice/windows.html?watch=0#practice")
                address(13)
                values["resume"] = True
            elif check_id == "J101":
                scenes = {
                    "start.html": {
                        4:"#studio-send", 1:"#agent-chat", 2:".vsc textarea", 3:"#ms-signin",
                    },
                    "docs/practice/windows.html": {
                        1:"#tb-start", 2:"#ssearch", 3:".ps .in", 4:"#ghcode",
                        5:".bs .starter-btn:nth-child(1)", 6:".bs form input",
                        7:"#bs-clear", 8:".bs .starter-btn:nth-child(2)", 9:"#bs-agents",
                        10:"#bs-export-agent", 11:"#bs-delete-agent", 12:".bs form input",
                        13:"#download-agent", 14:".bs form input", 15:"#bs-book",
                        16:".bs form input", 17:".bs .starter-btn:nth-child(3)",
                    },
                }
                for path, steps in scenes.items():
                    for number, selector in steps.items():
                        open_step(path, number)
                        assert page.locator(selector).count() == 1, (path, number, selector)
                        clear([selector])
                        assert page.locator("#c-n").inner_text().startswith(f"Step {number} of ")
                        if path == "start.html" and number == 4:
                            assert page.locator(".sample-studio").is_visible()
                            assert page.locator("#studio-input").input_value() == page.locator(
                                "#stage-question").inner_text()
                            assert page.locator("#studio-input").evaluate("e => e === document.activeElement")
                            picture("item-4-start-step-4-preview")
                            page.locator("#studio-send").click()
                            assert page.locator("#studio-answer").is_visible()
                        if path.startswith("docs/") and number == 8:
                            assert page.locator(".bs .log").inner_text() == ""
                        if path.startswith("docs/") and number in (12, 13):
                            assert page.evaluate("window.practicePC.state.news === false")
                        values[f"{path}-{number}"] = True
            elif check_id == "J102":
                def points():
                    source = page.locator("#download-agent").bounding_box()
                    destination = page.locator(".bs .log").bounding_box()
                    return ((source["x"] + source["width"] / 2,
                             source["y"] + source["height"] / 2),
                            (destination["x"] + destination["width"] - 30,
                             destination["y"] + destination["height"] - 20))

                def drag(kind, end=True, outside=False):
                    start, stop = points()
                    if outside:
                        stop = (20, 20)
                    if kind == "mouse":
                        page.mouse.move(*start)
                        page.mouse.down()
                        page.mouse.move(*stop, steps=20)
                        page.mouse.up()
                    else:
                        cdp = context.new_cdp_session(page)
                        def touch(event, x=0, y=0):
                            cdp.send("Input.dispatchTouchEvent", {
                                "type":event, "touchPoints":[] if event in ("touchEnd", "touchCancel")
                                else [{"x":x, "y":y, "id":0}],
                            })
                        touch("touchStart", *start)
                        for i in range(1, 21):
                            touch("touchMove", *(a + (b-a)*i/20 for a, b in zip(start, stop)))
                        touch("touchEnd" if end else "touchCancel")
                        cdp.detach()

                for kind in ("mouse", "touch"):
                    open_step("docs/practice/windows.html", 13)
                    page.evaluate("""() => {
                        window.__dragInput = [];
                        for (const type of ['pointerdown', 'pointermove', 'pointerup'])
                            document.addEventListener(type, e => {
                                if (e.isTrusted) window.__dragInput.push([type, e.pointerType]);
                            }, {capture:true});
                    }""")
                    picture(f"item-5-{kind}-before")
                    drag(kind)
                    assert page.evaluate("window.practicePC.step()") == 13, f"{kind} drag did not restore"
                    assert page.evaluate("window.practicePC.state.news") is True
                    assert page.locator("#download-agent").count() == 0
                    assert page.locator(".file-drag-preview").count() == 0
                    for event in ("pointerdown", "pointermove", "pointerup"):
                        assert page.evaluate(
                            "entry => window.__dragInput.some(e => JSON.stringify(e) === JSON.stringify(entry))",
                            [event, kind])
                    picture(f"item-5-{kind}-restored")
                    values[kind] = True
                for kind, outside in (("mouse", True), ("touch", False)):
                    open_step("docs/practice/windows.html", 13)
                    drag(kind, end=False, outside=outside)
                    assert page.evaluate("window.practicePC.step()") == 12
                    assert page.evaluate("window.practicePC.state.news") is False
                    assert page.locator(".file-drag-preview").count() == 0
                    values[f"{kind}-cancelled"] = True
                page.get_by_role("button", name="Do it for me", exact=True).click()
                assert page.evaluate("window.practicePC.step()") == 13
                values["helper"] = True
            elif check_id == "J103":
                open_step("docs/practice/windows.html", 8)
                page.get_by_role("button", name="What do you remember?", exact=True).click()
                sentence = "You have met it. It still knows you."
                count = page.locator("body").text_content().count(sentence)
                assert count == 1, f"finish sentence occurs {count} times in page text"
                assert page.locator("#practice-caption").text_content().count(sentence) == 0
                assert page.locator(".bs-finish [role=status]").inner_text() == sentence
                assert page.locator("body").aria_snapshot().count(sentence) == 1
                clear(["#stage-keep-going"])
                values["dom_and_accessibility_once"] = True
                page.get_by_role("button", name="Keep going", exact=True).click()
                assert page.evaluate("window.practicePC.step()") == 8
                values["continue"] = True
            assert not errors, errors
            checks.append(result(check_id, values, True))
        except Exception as exc:
            checks.append(measurement_failure(check_id, exc, observations=values))
        finally:
            context.close()
    return checks
