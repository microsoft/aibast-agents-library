"""Browser acceptance for the URL-only path chooser."""

import json
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlsplit


def measure(browser, base, *, measurement_failure, result, selected):
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "api/v1/paths.json").read_text())
    shots = root / "_shots/ac"
    shots.mkdir(parents=True, exist_ok=True)
    checks = []
    for number in range(110, 116):
        check_id = f"J{number}"
        if not selected(check_id):
            continue
        context = browser.new_context(viewport={"width": 1366, "height": 625},
                                      java_script_enabled=number != 112)
        context.route("https://**/*", lambda route: route.abort())
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        observations = {}

        def load(query=""):
            response = page.goto(base + "paths.html" + ("?" + query if query else ""))
            assert response.status == 200
            page.locator("#chooser").wait_for(state="visible")

        def preview(goal, have="vscode,studio", area="account-intelligence"):
            return urlencode({"goal": goal, "have": have, "area": area})

        def change_query(query):
            page.evaluate("""query => {
                history.replaceState(null, '', '?' + query);
                dispatchEvent(new PopStateEvent('popstate'));
            }""", query)

        try:
            if number == 110:
                load()
                count = 0
                destinations = set()
                for route in data["routes"]:
                    for area in route["solutions"] or [""]:
                        for have in (["none", "vscode", "studio", "vscode,studio"] if route["needs"] else ["none"]):
                            query = urlencode({"goal": route["id"], "have": have, "area": area})
                            change_query(query)
                            assert page.locator("#screen h1").inner_text() == "Here is your path"
                            got = page.locator(".route-list li").evaluate_all(
                                "nodes => nodes.map(n => n.dataset.destination)")
                            missing = [item for item in data["prerequisites"]
                                       if item["id"] in route["needs"] and item["id"] not in have.split(",")]
                            assert 2 <= len(got) <= 4
                            expected = [step.get("url") or data["solutions"][area][step["destination"]]
                                        for step in route["steps"]]
                            if missing:
                                assert got[0] == missing[0]["url"]
                                assert "Missing:" in page.locator("#screen").inner_text()
                                expected.insert(0, missing[0]["url"])
                            assert got == expected, (query, got, expected)
                            if route["id"] != "local":
                                assert "brainstem" not in page.locator("#screen").inner_text().lower()
                            first = page.locator("#screen a.primary").get_attribute("href")
                            assert urlsplit(first).path.endswith(urlsplit(got[0]).path)
                            destinations.update(got)
                            count += 1
                for destination in destinations:
                    response = context.request.get(urljoin(base, destination))
                    assert response.status == 200, destination
                observations = {"combinations": count, "real_destinations": len(destinations)}
            elif number == 111:
                visited = set()
                count = 0
                for route in data["routes"]:
                    for area in route["solutions"] or [""]:
                        for have in (["none", "vscode,studio"] if route["needs"] else ["none"]):
                            query = urlencode({"goal": route["id"], "have": have, "area": area})
                            steps = [step.get("url") or data["solutions"][area][step["destination"]]
                                     for step in route["steps"]]
                            missing = [item for item in data["prerequisites"]
                                       if item["id"] in route["needs"] and item["id"] not in have.split(",")]
                            if missing:
                                steps.insert(0, missing[0]["url"])
                            for index, destination in enumerate(steps, 1):
                                # Each concrete destination is rendered, not just HEAD-checked.
                                # Other combinations are exhaustively checked in J110.
                                if destination in visited:
                                    continue
                                visited.add(destination)
                                target = urljoin(base, destination)
                                parsed = urlsplit(target)
                                separator = "&" if parsed.query else "?"
                                target = target.split("#")[0] + separator + urlencode({"path": query, "pathStep": index})
                                if parsed.fragment:
                                    target += "#" + parsed.fragment
                                errors.clear()
                                response = page.goto(target, wait_until="networkidle")
                                assert response.status == 200, target
                                strip = page.locator("#your-path")
                                strip.get_by_text(f"Your path: step {index} of {len(steps)}", exact=True).wait_for()
                                assert strip.get_by_role("link", name="Back to my path", exact=True).count() == 1
                                change = strip.get_by_role("link", name="Not what you wanted? Change my answers", exact=True)
                                assert "screen=goal" in change.get_attribute("href")
                                assert not errors, (destination, errors)
                                count += 1
                observations = {"pages_rendered_with_strip": count, "page_errors": 0}
            elif number == 112:
                response = page.goto(base + "paths.html")
                assert response.status == 200
                links = page.locator("#fallback li a")
                got = set(links.evaluate_all("nodes => nodes.map(n => n.getAttribute('href'))"))
                from tools.library_api_paths import destination_urls
                assert got == set(destination_urls(data))
                assert links.first.is_visible() and links.last.is_visible()
                observations = {"all_destinations": len(got)}
            elif number == 113:
                load()
                page.get_by_role("button", name="I already build agents in VS Code but they come out messy", exact=True).click()
                page.locator('input[value="vscode"]').check()
                page.locator('input[value="studio"]').check()
                page.get_by_role("button", name="Continue", exact=True).click()
                page.locator('input[type="search"]').fill("Account Intelligence")
                page.locator(".results button").first.click()
                result_url = page.url
                assert "Here is your path" == page.locator("#screen h1").inner_text()
                page.get_by_role("link", name="Other paths", exact=True).click()
                page.locator("#chooser").wait_for(state="visible")
                page.get_by_role("button", name="Back", exact=True).click()
                assert page.locator("#screen h1").inner_text() == "Here is your path"
                assert "area=account-intelligence" in page.url
                page.get_by_role("button", name="Back", exact=True).click()
                assert "Account Intelligence" in page.locator("#screen").inner_text()
                page.get_by_role("button", name="Back", exact=True).click()
                assert page.locator('input[value="vscode"]').is_checked()
                assert page.locator('input[value="studio"]').is_checked()
                page.go_back()
                page.go_back()
                assert page.locator("#screen h1").inner_text() == "Here is your path"
                page.goto(result_url)
                page.locator("#screen a.primary").wait_for()
                page.get_by_role("link", name="Start step 1", exact=True).click()
                page.locator("#your-path").get_by_role("link", name="Not what you wanted? Change my answers", exact=True).click()
                page.locator("#chooser").wait_for(state="visible")
                assert "goal=build" in page.url and "area=account-intelligence" in page.url
                page.get_by_role("button", name="I already build agents in VS Code but they come out messy", exact=True).click()
                assert page.locator("#screen h1").inner_text() == "Here is your path"
                assert "have=vscode%2Cstudio" in page.url
                observations = {"Back": True, "browser_back": True, "shared_result": True, "change_restores": True}
            elif number == 114:
                load()
                states = {
                    "question-1": "",
                    "question-2": "goal=build",
                    "question-3": "goal=build&have=vscode,studio",
                    "customer-demo": preview("demo"),
                    "build-my-own": preview("build"),
                    "brainstem": preview("local"),
                    "missing-tools": preview("build", "none"),
                    "host-missing-tools": preview("host", "none"),
                    "tell-us": preview("build") + "&screen=request&from=area",
                }
                for width, height in ((1366, 625), (1366, 583), (1536, 703), (1920, 919), (390, 844)):
                    page.set_viewport_size({"width": width, "height": height})
                    for name, query in states.items():
                        change_query(query)
                        page.evaluate("document.activeElement?.blur()")
                        dimensions = page.evaluate("""() => {
                            const nodes = [...document.querySelectorAll('#chooser button, #chooser a, #chooser input')];
                            const bounds = nodes.filter(n => n.getClientRects().length)
                                .map(n => n.getBoundingClientRect());
                            return {width: document.documentElement.scrollWidth,
                                fits: bounds.every(r => r.left >= 0 && r.right <= innerWidth &&
                                    r.top >= 0 && r.bottom <= innerHeight)};
                        }""")
                        assert dimensions["width"] <= width and dimensions["fits"], (width, height, name, dimensions)
                        assert page.locator("#screen .primary").count() <= 1
                        if (width, height) == (1366, 625):
                            page.screenshot(path=str(shots / f"{name}.png"))
                for width, height in ((1366, 625), (1366, 583), (1536, 703), (1920, 919)):
                    page.set_viewport_size({"width": width, "height": height})
                    page.goto(base + "docs/practice/windows.html?" + urlencode({
                        "path": "goal=local", "pathStep": 1, "watch": 0}))
                    page.locator("#your-path").get_by_text("Your path: step 1 of 2", exact=True).wait_for()
                    page.locator(".coach").wait_for()
                    bounds = page.locator(".coach").bounding_box()
                    assert bounds["y"] + bounds["height"] <= height, (width, height, bounds)
                observations = {"viewports": 5, "states_per_viewport": len(states)}
            elif number == 115:
                load(preview("build", "none"))
                page.get_by_role("link", name="Book office hours", exact=True).click()
                page.locator("#your-path").get_by_text("Your path: step 1 of 3", exact=True).wait_for()
                page.locator("#your-path").get_by_role("link", name="Return to getting ready", exact=True).click()
                page.locator("#your-path").get_by_text("Your path: step 1 of 3", exact=True).wait_for()
                assert page.url.startswith(base + "docs/path-requirements.html?")
                for query in ("", "goal=build", "goal=build&have=none"):
                    load(query)
                    page.get_by_role("button", name="Something else", exact=True).click()
                    assert page.locator('input[name="text"]').get_attribute("maxlength") == "200"
                    assert "leave out names and company details" in page.locator("#screen").inner_text()
                    page.get_by_role("button", name="Back", exact=True).click()
                    assert page.locator('input[name="text"]').count() == 0
                    assert "Tell us what you were looking for" not in page.locator("#screen").inner_text()
                load("goal=demo")
                page.locator('input[type="search"]').fill("no matching synthetic area xyz")
                page.get_by_role("button", name="We don't have that yet. Tell us", exact=True).click()
                text = "<b>Need a sample checklist</b>"
                page.locator('input[name="text"]').fill(text)
                page.get_by_role("button", name="Continue to request form", exact=True).click()
                page.locator("#path-request-summary").wait_for()
                assert page.url.startswith(base + "request-info.html?")
                assert page.locator("#path-request-summary").locator("b").count() == 0
                assert "You were looking for: " + text in page.locator("#path-request-summary").inner_text()
                page.get_by_role("link", name="Meanwhile, the closest we have is Learn the basics first", exact=True).click()
                page.locator("#screen a.primary").wait_for()
                assert page.locator("#screen h1").inner_text() == "Here is your path"
                assert "goal=basics" in page.url
                observations = {"every_question": True, "no_match": True, "safe_text": True,
                                "nearest_path": True, "help_keeps_path": True}
            assert not errors, errors
            checks.append(result(check_id, observations, True))
        except Exception as exc:
            checks.append(measurement_failure(check_id, exc, observations=observations))
        finally:
            context.close()
    return checks
