"""Pointer, keyboard, and layout acceptance for the shared Studio Preview scene."""

import json


SPECS = (
    ("J85", "studio_preview_layout", "Preview tabs; rail; greeting; prompts; composer"),
    ("J86", "studio_preview_fits", "5 sizes; five-point hit tests; no clipping"),
    ("J87", "studio_preview_flow", "pill + Send + keyboard; filed answer; done"),
)
VIEWPORTS = ((1366, 625), (1536, 703), (1920, 919), (1280, 585), (1366, 583), (390, 844))


def preview_layout(page):
    return page.evaluate("""() => {
        const scene = document.querySelector('.sample-studio');
        const tabs = [...scene.querySelectorAll('[data-studio-tab]')];
        const name = scene.querySelector('#studio-agent').textContent;
        const prompts = scene.querySelector('.studio-prompts');
        return {
            four_tabs:tabs.map(e => e.textContent).join('|') === 'Build|Preview|Evaluate|Monitor',
            preview_selected:tabs.filter(e => e.getAttribute('aria-pressed') === 'true')
                .map(e => e.textContent).join() === 'Preview',
            left_rail:!!scene.querySelector('.studio-nav'),
            header:['New chat','History','Debug mode','0 credits'].every(t =>
                scene.querySelector('.studio-test-header')?.textContent.includes(t)),
            debug_on:!!scene.querySelector('[role="switch"][aria-checked="true"]'),
            greeting:scene.querySelector('.studio-greeting h2')?.textContent === name
                && !!scene.querySelector('.studio-description')?.textContent.trim(),
            two_columns:!!prompts && getComputedStyle(prompts).gridTemplateColumns.split(' ').length === 2,
            own_prompts:!!prompts?.children.length && prompts.children.length <= 6
                && prompts.firstElementChild.textContent === scene.querySelector('#studio-input').value,
            composer:scene.querySelector('#studio-input').placeholder === 'Message ' + name,
            disclaimer:scene.textContent.includes('AI-generated content may be incorrect. Learn more'),
            truthful_state:scene.querySelector('.studio-draft')?.textContent.trim() === 'Draft',
            honest_footer:scene.textContent.includes('Practice view of Copilot Studio. Your screen may differ.')
        };
    }""")


def measure(browser, base, shots):
    from tools.first_minute_check import (
        ROOT, result, studio_answer_readability, studio_answer_words, studio_ready,
    )
    from tools.practice_laptop_check import RECTS

    shots.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(reduced_motion="reduce")
    context.route("**/*", lambda route: route.continue_()
                  if route.request.url.startswith(base) else route.abort("blockedbyclient"))
    page = context.new_page()
    page.set_default_timeout(5000)
    checks = []
    try:
        studio_ready(page, base)
        layout = preview_layout(page)
        solution = json.loads((ROOT / "api/v1/solutions/account-intelligence.json").read_text())
        layout["story_description"] = (
            page.locator(".studio-description").count() == 1
            and page.locator(".studio-description").inner_text() == solution["headline"]
        )
        checks.append(result("J85", layout, all(layout.values())))
        fits = {}
        for width, height in VIEWPORTS:
            page.set_viewport_size({"width":width, "height":height})
            studio_ready(page, base)
            for state in ("before", "after"):
                if state == "after":
                    page.locator("#studio-send").click()
                key = f"{width}x{height}-{state}"
                fits[key] = page.evaluate(RECTS, ["#studio-input", "#studio-send"]
                                         + (["#studio-question"] if state == "after" else []))
                fits[key]["no_horizontal_scroll"] = page.evaluate("""() => {
                    const scene = document.querySelector('.sample-studio');
                    return document.documentElement.scrollWidth <= innerWidth
                        && scene.scrollWidth <= scene.clientWidth
                        && [...scene.querySelectorAll('*')].every(e =>
                            !e.checkVisibility() || e.getBoundingClientRect().right <= scene.getBoundingClientRect().right + 1);
                }""")
                if state == "before":
                    fits[key]["greeting_unclipped"] = page.evaluate("""() => {
                        const greeting = document.querySelector('.studio-greeting')?.getBoundingClientRect();
                        const thread = document.querySelector('.studio-thread').getBoundingClientRect();
                        return !!greeting && greeting.top >= thread.top && greeting.bottom <= thread.bottom;
                    }""")
                if state == "after":
                    readable = studio_answer_readability(page)
                    fits[key]["readable"] = readable["full_lines"] >= (4 if width == 390 else 5)
                    fits[key]["scroll_hint"] = readable["hint_when_more"] and readable["hint_hidden_at_end"]
                    page.locator(".studio-thread").press("Home")
                    fits[key]["clear_answer_lines"] = page.evaluate("""minimum => {
                        const thread = document.querySelector('.studio-thread');
                        const answer = document.querySelector('#studio-answer');
                        const fade = thread.dataset.more === 'true'
                            ? parseFloat(getComputedStyle(thread, '::after').height) : 0;
                        return Math.floor((thread.getBoundingClientRect().bottom - fade
                            - answer.getBoundingClientRect().top)
                            / parseFloat(getComputedStyle(answer).lineHeight)) >= minimum;
                    }""", 4 if width == 390 else 5)
                page.screenshot(path=str(shots / f"practice-{key}.png"))
        page.set_viewport_size({"width":1366, "height":768})
        studio_ready(page, base)
        page.screenshot(path=str(shots / "start-1366x768-test-step.png"))
        checks.append(result("J86", fits, all(all(v.values()) for v in fits.values())))

        flow = {}
        sample = json.loads((ROOT / "solutions/account-intelligence/evals/transcripts.json").read_text())["transcripts"][0]
        for action in ("pill", "send", "keyboard"):
            studio_ready(page, base)
            if action == "pill":
                if not page.locator(".studio-prompts button").count():
                    flow[action] = {"first_pill":False}
                    continue
                page.locator(".studio-prompts button").first.click()
            elif action == "send":
                page.locator("#studio-send").click()
            else:
                # The actual keyboard path starts at the focused, prefilled composer.
                page.keyboard.press("Enter")
            if not page.locator("#studio-answer").count():
                flow[action] = {"answer":False, "done_event":False}
                continue
            value = studio_answer_readability(page)
            flow[action] = {
                "filed_question":page.locator("#studio-question").inner_text() == sample["prompt"],
                "filed_answer":studio_answer_words(page.locator("#studio-answer").inner_text())
                    == studio_answer_words(sample["assistant_response"] + "\n\nSample data."),
                "done_event":page.locator("#c-n").inner_text() == "Done",
                "readable":value["full_lines"] >= 5 and value["rendered_marks"],
                "pills_hidden":not page.locator(".studio-prompts").is_visible(),
            }
        checks.append(result("J87", flow, all(all(v.values()) for v in flow.values())))
    except Exception as exc:
        measured = {check["id"] for check in checks}
        checks.extend(result(check_id, None, False, error=f"{type(exc).__name__}: {exc}")
                      for check_id, _, _ in SPECS if check_id not in measured)
    finally:
        context.close()
    return checks
