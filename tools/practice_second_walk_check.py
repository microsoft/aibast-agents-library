"""ORDER AA regressions, exercised with real Chromium input."""

from tools.practice_laptop_check import RECTS


SPECS = (
    ("J98", "pause_preserves_desktop", "every step and judged size; unchanged desktop + clickable target"),
    ("J99", "resume_is_explicit", "quiet remembered-step notice; first visit quiet; start + Watch replay reset"),
    ("J100", "shareable_current_step", "all direct steps + progress + restart + resume; replaceState only"),
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
        context = browser.new_context(reduced_motion="reduce",
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
            assert not errors, errors
            checks.append(result(check_id, values, True))
        except Exception as exc:
            checks.append(measurement_failure(check_id, exc, observations=values))
        finally:
            context.close()
    return checks
