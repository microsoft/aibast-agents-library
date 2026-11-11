"""ORDER AA regressions, exercised with real Chromium input."""

from tools.practice_laptop_check import RECTS


SPECS = (
    ("J98", "pause_preserves_desktop", "every step and judged size; unchanged desktop + clickable target"),
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
            assert not errors, errors
            checks.append(result(check_id, values, True))
        except Exception as exc:
            checks.append(measurement_failure(check_id, exc, observations=values))
        finally:
            context.close()
    return checks
