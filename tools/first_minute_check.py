#!/usr/bin/env python3
"""Measure the first-minute journey without modifying pages or using the network."""

import argparse
from contextlib import contextmanager
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from threading import Thread
import time
from urllib.parse import parse_qsl, unquote, urlencode, urljoin, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
DEMO = "solutions/_shared/m365-copilot-demo.html"
JARGON = (
    "Brainstem", "RAPP", "Hippocampus", "agent.py", "slide-sourced",
    "1P", "harness", "SKILL.md",
)
SPECS = (
    ("J1", "clicks_to_playing_demo", "<= 1"),
    ("J2", "above_fold_actions", "<= 12"),
    ("J3", "primary_actions_above_fold", "== 1"),
    ("J4", "jargon_first_screen", "none"),
    ("J5", "start_page", "all true"),
    ("J6", "console_errors", "0"),
    ("J7", "internal_links", "0 missing"),
    ("J8", "phone", "all true"),
    ("J9", "capabilities_kept", "all true"),
    ("J10", "demo_autostarts", "advances <= 6s; reduced motion waits"),
    ("J11", "every_solution_resolves", "all"),
    ("J12", "unknown_solution_is_loud", "true"),
    ("J13", "every_recorded_solution_has_watch", "true"),
    ("J14", "preview_never_blank", "true"),
    ("J15", "noscript_path", "true"),
    ("J16", "phone_preview_readable", ">= 11px"),
    ("J17", "phone_copy_reachable + end_card_one_primary", "all true"),
    ("J18", "watch_opens_same_tab", "all true"),
    ("J19", "phone_preview_shows_chat", "2s, 4s, 8s"),
    ("J20", "search_enter_lists", "all true"),
    ("J21", "details_focus", "all true"),
    ("J22", "old_demo_links", "5 of 5"),
    ("J23", "noscript_demo", "all true"),
    ("J24", "one_name", "all true"),
    ("J25", "no_unbacked_claims", "none"),
    ("J26", "start_page_plain", "all true"),
    ("J27", "links_match_labels", "all true"),
    ("J28", "office_hours_lands", "all true"),
    ("J29", "demo_can_skip", "all true"),
    ("J30", "banner_never_covers_captions", "all true"),
    ("J31", "no_results_plain", "all true"),
    ("J32", "preview_readable_desktop", "full window, caption >= 10px"),
    ("J33", "start_phone_keeps_hint", "all true"),
    ("J34", "honest_hero", "all true"),
    ("J35", "no_jargon_below_results", "all true"),
    ("J36", "stage_is_desktop", ">= 55%; one shared engine"),
    ("J37", "watch_mode_plays", "4 express steps <= 35s"),
    ("J38", "try_mode_completes", "4 highlighted express steps"),
    ("J39", "practice_install_preserved", "4 original install steps"),
    ("J40", "stage_phone_readable", ">= 11px"),
    ("J41", "reduced_motion_stage", "waits 6s"),
    ("J42", "aideate_page", "all true"),
    ("J43", "aideate_reachable", "all true"),
    ("J44", "polish_r5", "all true"),
    ("J45", "stage_fills_screen", ">= 92%; desktop + bar in viewport"),
    ("J46", "stage_two_modes", "Watch + 4 real-input steps"),
    ("J47", "stage_keeps_everything", "all true"),
    ("J48", "two_journeys", "4 express; 17 local; reciprocal links"),
    ("J49", "interview_matches_real_chat", "13 headings + hints + 3 pills"),
    ("J50", "practice_runs_end_to_end", "17 done/skipped/watch; visible hints; mobile"),
    ("J51", "session_follow_along", "exact Windows line; pretend install < 10s"),
    ("J52", "session_finish_line", "exact text; one primary; continues to 9"),
    ("J53", "session_self_serve", "17 steps; reload; links; storage optional"),
    ("J54", "windows_first", "3 sizes; no clipping; keyboard-only"),
    ("J55", "host_sheet", "loads; clean console; one print page; linked"),
)


def jargon_in(text):
    # A web address is a place to go, not a term to learn: "rapp.microsoft.com" is not the word RAPP.
    text = re.sub(r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|ms|net|org|io)\b", " ", text, flags=re.I)
    return [
        term for term in JARGON
        if re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, re.I)
    ]


def internal_target(href, page_url, root):
    """Return a confined file path, or None for a non-site URL."""
    url = urlsplit(urljoin(page_url, href))
    origin = urlsplit(page_url)
    path = unquote(url.path)
    if url.scheme not in ("http", "https"):
        return None
    if (url.scheme, url.netloc) != (origin.scheme, origin.netloc):
        if url.netloc.lower() != "microsoft.github.io":
            return None
        prefix = "/aibast-agents-library/"
        if path == prefix.rstrip("/"):
            path = "/"
        elif path.startswith(prefix):
            path = "/" + path[len(prefix):]
        else:
            return None
    root = Path(root).resolve()
    target = (root / path.lstrip("/")).resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"Link escapes repository: {href}")
    if path.endswith("/") or target.is_dir():
        target /= "index.html"
    return target


def missing_links(links, page_url, root):
    missing = []
    for href in sorted(set(links)):
        try:
            target = internal_target(href, page_url, root)
            if target is not None and not target.is_file():
                missing.append({"page": urlsplit(page_url).path, "href": href})
        except ValueError as exc:
            missing.append({
                "page": urlsplit(page_url).path, "href": href, "error": str(exc),
            })
    return missing


def blocked_external_https(url, base):
    parsed = urlsplit(url)
    return (
        parsed.scheme == "https"
        and parsed.hostname not in ("localhost", "127.0.0.1", "::1")
        and parsed.netloc != urlsplit(base).netloc
    )


def policy_blocked_error(error, blocked, base):
    """Suppress only browser resource errors attributable to our HTTPS block."""
    url = error.get("url", "")
    if url not in blocked or not blocked_external_https(url, base):
        return False
    if error["kind"] == "requestfailed":
        return bool(re.fullmatch(
            r"net::ERR_BLOCKED_BY_CLIENT(?:\.Inspector)?", error.get("message", "")
        ))
    if error["kind"] == "console":
        return bool(re.fullmatch(
            r"Failed to load resource: net::ERR_BLOCKED_BY_CLIENT(?:\.Inspector)?",
            error.get("message", ""),
        ))
    return False


def scenario_demo_url(url):
    """Retain the catalog scenario but never carry playback controls into J10."""
    parsed = urlsplit(url)
    scenario = next(
        (value for key, value in parse_qsl(parsed.query) if key == "scenario" and value),
        None,
    )
    if not scenario:
        raise ValueError("Catalog journey did not discover a demo scenario")
    return urlunsplit((
        parsed.scheme, parsed.netloc, parsed.path,
        urlencode({"scenario": scenario}), "",
    ))


def autoplay_result(normal, reduced):
    waits = not reduced["advances"] if reduced["chat_present"] else None
    value = {
        "advances": normal["advances"],
        "reduced_motion_advances": reduced["advances"],
        "reduced_motion_waits": waits,
        "normal_chat_present": normal["chat_present"],
        "reduced_motion_chat_present": reduced["chat_present"],
    }
    return value, normal["advances"] and waits is True


def capabilities(controls, page_url):
    paths = []
    origin = urlsplit(page_url)
    for control in controls:
        if not control.get("href"):
            continue
        url = urlsplit(urljoin(page_url, control["href"]))
        if url.scheme not in ("http", "https"):
            continue
        if (url.scheme, url.netloc) != (origin.scheme, origin.netloc) and not (
            url.netloc == "microsoft.github.io"
            and url.path.startswith("/aibast-agents-library/")
        ):
            continue
        paths.append((url.path, url.fragment))
    return {
        "request_info": any(p.endswith("/request-info.html") for p, _ in paths),
        "office_hours": any(
            p.endswith("/docs/installer.html") and h == "office-hours"
            for p, h in paths
        ),
        "academy": any(p.endswith("/academy.html") for p, _ in paths),
        "workshops": any(
            h == "workshops" or re.search(r"/workshops?(?:[/.]|$)", p)
            or p.endswith("/quest.html") for p, h in paths
        ),
        "installer": any(p.endswith("/docs/installer.html") for p, _ in paths),
        "why_or_pattern": any(
            p.endswith(("/why.html", "/docs/aibast-rapp-pattern.html"))
            for p, _ in paths
        ),
    }


def start_requirements(snapshot):
    step = snapshot.get("first_step", "")
    return {
        "exists": snapshot.get("exists", False),
        "first_step_is_non_technical": bool(step) and not re.search(
            r"VS\s+Code|Agent\s+mode", step, re.I
        ),
        "one_what_you_need": snapshot.get("what_you_need", 0) == 1,
        "one_copyable_command_before_details": snapshot.get("commands", 0) == 1,
        "no_jargon_outside_details": snapshot.get("exists", False)
        and not jargon_in(snapshot.get("text", "")),
    }


def result(check_id, value, passed, **details):
    _, name, target = next(spec for spec in SPECS if spec[0] == check_id)
    return {
        "id": check_id, "name": name, "value": value,
        "target": target, "pass": bool(passed), **details,
    }


def exit_code(checks, gate):
    return int(gate and any(not check["pass"] for check in checks))


@contextmanager
def local_site(root):
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(QuietHandler, directory=str(root))
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


# Shared DOM definitions keep the desktop, phone, and text measurements consistent.
DOM = r"""
const visible = e => {
    if (!e.checkVisibility({checkOpacity: true, checkVisibilityCSS: true})) return false;
    const r = e.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
};
const inside = e => {
    const r = e.getBoundingClientRect();
    return visible(e) && r.left >= 0 && r.top >= 0
        && r.right <= innerWidth && r.bottom <= innerHeight;
};
const cookie = e => !!e.closest(
    '#aibast-clarity-consent, [id*="cookie" i], [aria-label*="cookie" i], [data-cookie-banner]'
);
const labelled = e => (e.getAttribute('aria-label') || e.innerText
    || e.getAttribute('title') || e.getAttribute('placeholder') || '').trim();
const controls = () => [...document.querySelectorAll('a,button,input,select,summary')]
    .filter(e => visible(e) && !e.matches(':disabled,[aria-disabled="true"]'));
const text = (fold, outsideDetails = false, excluded = null) => {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const parts = [];
    while (walker.nextNode()) {
        const n = walker.currentNode, e = n.parentElement;
        if (!n.textContent.trim() || !e || !visible(e)
            || e.closest('script,style,noscript,template')
            || (outsideDetails && e.closest('details'))
            || (excluded && excluded.contains(e))) continue;
        const range = document.createRange(); range.selectNodeContents(n);
        if (!fold || [...range.getClientRects()].some(r =>
            r.width && r.height && r.bottom > 0 && r.top < innerHeight
            && r.right > 0 && r.left < innerWidth)) parts.push(n.textContent);
    }
    return parts.join(' ');
};
"""


def evaluate(page, expression):
    return page.evaluate("() => {" + DOM + "\n" + expression + "\n}")


def load(page, url):
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(250)


def first_cta(page):
    marked = page.locator('[data-first-minute="watch"]').filter(visible=True)
    if marked.count():
        return marked.first
    return page.locator(
        ".card-actions .primary, .agent-card .primary, .card .primary"
    ).filter(visible=True).first


def click_control(page, control):
    if not control.is_visible() or not control.is_enabled():
        raise ValueError("Journey control is hidden or disabled")
    label = control.evaluate(
        "(e) => (e.getAttribute('aria-label') || e.innerText || e.title || '').trim()"
    )
    if not label:
        raise ValueError("Journey control has no visible/accessibility label")
    before = set(page.context.pages)
    control.click()
    page.wait_for_timeout(300)
    opened = [p for p in page.context.pages if p not in before]
    destination = opened[-1] if opened else page
    destination.wait_for_load_state("networkidle")
    return destination, label


def demo_frame(page):
    return next(
        (frame for frame in page.frames if urlsplit(frame.url).path.endswith("/" + DEMO)),
        None,
    )


def chat_snapshot(frame):
    return frame.evaluate(r"""() => {
        const nodes = [...document.querySelectorAll(
            '[data-aibast~="placeholder"],[data-aibast~="question"],'
            + '[data-aibast~="answer"],[role="log"],[data-chat-text],.chat-message'
        )];
        return nodes.filter(e => e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})
            && e.getClientRects().length).map(e => e.innerText.trim()).filter(Boolean).join('\n');
    }""")


def observe_chat(page, seconds=6):
    """Observe changing rendered chat, not a Play label, caption, or JS counter."""
    previous = {}
    ready = False
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        demo = demo_frame(page)
        if demo:
            frames = [demo, *(frame for frame in page.frames if frame.parent_frame == demo)]
            for frame in frames:
                # Do not count text in an iframe whose player is hidden.
                if frame.parent_frame and not frame.frame_element().is_visible():
                    continue
                current = chat_snapshot(frame)
                if current:
                    ready = True
                    old = previous.get(frame)
                    if old is not None and current != old:
                        return {"advances": True, "chat_present": True}
                    previous[frame] = current
        page.wait_for_timeout(100)
    return {"advances": False, "chat_present": ready}


def journey(page, base, flags):
    load(page, base + "index.html")
    path = []
    demo_url = None
    page, label = click_control(page, first_cta(page))
    path.append(label)
    # Prefer an already visible direct demo. For collapsed demos, open the
    # smallest number of enclosing details; scrolling itself is not a click.
    for _ in range(6):
        frame = demo_frame(page)
        if frame:
            demo_url = frame.url
            break
        candidates = page.locator("a[href]").evaluate_all(r"""es => es
            .filter(e => /interactive demo/i.test(e.innerText)
                || /m365-copilot-demo\.html/.test(e.getAttribute('href')))
            .map(e => {
                const closed = []; let p = e.parentElement;
                while (p) {
                    if (p.matches('details:not([open])')) closed.unshift(p);
                    p = p.parentElement;
                }
                return {index:es.indexOf(e), closed:closed.length,
                    visible:e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})
                        && e.getClientRects().length > 0};
            }).filter(e => e.visible || e.closed > 0)
            .sort((a,b) => a.closed - b.closed)""")
        if not candidates:
            flags.append("J1: no visible interactive-demo path after the primary control.")
            return result("J1", None, False, clicks=path), demo_url
        link = page.locator("a[href]").nth(candidates[0]["index"])
        ancestors = link.locator("xpath=ancestor::details[not(@open)]")
        while ancestors.count():
            outermost = link.locator("xpath=ancestor::details[not(@open)][last()]")
            page, label = click_control(page, outermost.locator(":scope > summary"))
            path.append(label)
        page, label = click_control(page, link)
        path.append(label)
    if not demo_frame(page):
        flags.append("J1: bounded journey did not reach the demo player.")
        return result("J1", None, False, clicks=path), demo_url
    observed = observe_chat(page)
    auto = observed["advances"]
    if not auto:
        player = demo_frame(page)
        play = player.get_by_role("button", name="Play", exact=True)
        if play.count() and play.is_visible():
            page, label = click_control(page, play)
            path.append(label)
            observed = observe_chat(page)
    measured = len(path) if observed["advances"] else None
    if measured is None:
        flags.append("J1: no advancing chat observed, even after Play.")
    return result(
        "J1", measured, measured is not None and measured <= 1,
        clicks=path, without_play=auto, observation_seconds=6,
    ), demo_url


def start_snapshot(page):
    return evaluate(page, r"""
        const steps = [...document.querySelectorAll(
            '[data-step="1"], ol > li, h2, h3'
        )].filter(e => visible(e) && !e.closest('details')
            && (e.matches('[data-step="1"],ol > li') || /^(step\s*)?1[.):\s]/i.test(e.innerText)));
        const firstDetails = document.querySelector('details:not(.all-steps)');
        const blocks = [...document.querySelectorAll(
            'pre, [data-copyable], [data-command], .command-block, .code-block'
        )].filter(e => visible(e) && !e.closest('details')
            && (!firstDetails || !!(e.compareDocumentPosition(firstDetails)
                & Node.DOCUMENT_POSITION_FOLLOWING)));
        const copyable = blocks.filter(e => e.matches('[data-copyable]')
            || [...e.parentElement.querySelectorAll('button,[role="button"]')]
                .some(b => visible(b) && /copy/i.test(labelled(b))));
        const unique = copyable.filter(e => !copyable.some(
            other => other !== e && e.contains(other)
        ));
        const quiet = document.querySelector('.journey-link');
        const approvedQuiet = quiet?.textContent.trim() ===
            'Want an AI assistant running on your own computer instead? Practice the Brainstem setup.'
            && quiet.querySelector('a')?.getAttribute('href') === 'docs/practice/windows.html' ? quiet : null;
        return {exists:true, first_step:steps[0]?.innerText || '',
            what_you_need:document.querySelectorAll('[data-what-you-need]').length,
            commands:unique.length, text:text(false,true,{contains:e =>
                (unique.length === 1 && unique[0].contains(e)) || approvedQuiet?.contains(e)})};
    """)


def phone_snapshot(page):
    return evaluate(page, """
        return {scroll_width:document.documentElement.scrollWidth,
            no_horizontal_overflow:document.documentElement.scrollWidth <= 390};
    """)


def visible_navigation(page):
    page.locator("details").evaluate_all("es => es.forEach(e => e.open = true)")
    return evaluate(page, """
        return controls().filter(e => e.matches('a[href]') || labelled(e)).map(e => ({
            href:e.getAttribute('href') || e.dataset.href || '',
            label:labelled(e)
        }));
    """)


def measure(browser, base, flags, blocked):
    context = browser.new_context(
        viewport={"width": 1440, "height": 900}, reduced_motion="no-preference",
        service_workers="block",
    )

    def route(request_route):
        url = request_route.request.url
        if url.startswith(base):
            request_route.continue_()
        else:
            blocked.add(url)
            request_route.abort("blockedbyclient")

    context.route("**/*", route)
    errors = []
    auditing = set()

    def listen(page):
        def record(kind, **detail):
            if page in auditing:
                errors.append({"page": page.url, "kind": kind, **detail})
        page.on("console", lambda msg: record(
            "console", message=msg.text, url=msg.location.get("url", "")
        )
                if msg.type == "error" else None)
        page.on("pageerror", lambda exc: record("pageerror", message=str(exc)))
        page.on("requestfailed", lambda req: record(
            "requestfailed", url=req.url, message=req.failure
        ))
        page.on("response", lambda response: record(
            "http", url=response.url, status=response.status
        ) if response.status >= 400 else None)

    context.on("page", listen)
    checks = []
    page = context.new_page()
    load(page, base + "index.html")
    desktop = evaluate(page, """
        const actions = controls().filter(inside);
        return {actions:actions.filter(e => !cookie(e)).length,
            cookie_actions:actions.filter(cookie).length,
            primary:[...document.querySelectorAll('[class*="primary"]')].filter(inside).length,
            text:text(true)};
    """)
    checks.extend((
        result("J2", desktop["actions"], desktop["actions"] <= 12,
               cookie_actions=desktop["cookie_actions"]),
        result("J3", desktop["primary"], desktop["primary"] == 1),
        result("J4", jargon_in(desktop["text"]), not jargon_in(desktop["text"])),
    ))
    # Disclosures are opened only after the above-fold measurements.
    links = visible_navigation(page)
    kept = capabilities(links, page.url)
    checks.append(result("J9", kept, all(kept.values())))
    if not kept["why_or_pattern"]:
        flags.append(
            "J9: no visible why/pattern link survives catalog JS rendering, including "
            "opened details and footer. The source intro link is removed by the page's "
            "assignment to document.querySelector('.intro p').textContent."
        )
    journey_page = context.new_page()
    j1, demo_url = journey(journey_page, base, flags)
    checks.append(j1)
    demo_url = scenario_demo_url(demo_url or base + DEMO)
    start_exists = (ROOT / "start.html").is_file()
    start = context.new_page()
    snapshot = {"exists": False}
    if start_exists:
        load(start, base + "start.html")
        snapshot = start_snapshot(start)
    requirements = start_requirements(snapshot)
    checks.append(result("J5", requirements, all(requirements.values()), evidence=snapshot))

    missing = []
    urls = [base + "index.html", base + "docs/installer.html", demo_url]
    if start_exists:
        urls.insert(1, base + "start.html")
    for url in urls:
        audit_page = context.new_page()
        auditing.add(audit_page)
        load(audit_page, url)
        audit_page.wait_for_timeout(750)
        if url != demo_url:
            hrefs = audit_page.locator("[href]").evaluate_all(
                "es => es.map(e => e.getAttribute('href'))"
            )
            missing.extend(missing_links(hrefs, audit_page.url, ROOT))
        auditing.remove(audit_page)
        audit_page.close()
    ignored = [error for error in errors if policy_blocked_error(error, blocked, base)]
    errors = [error for error in errors if not policy_blocked_error(error, blocked, base)]
    checks.append(result(
        "J6", len(errors), not errors, errors=errors, pages=urls,
        blocked_external_info=ignored,
    ))
    checks.append(result("J7", len(missing), not missing, missing=missing))

    phone = context.new_page()
    phone.set_viewport_size({"width": 390, "height": 844})
    load(phone, base + "index.html")
    mobile = {"index": phone_snapshot(phone)}
    cta = phone.locator('[data-first-minute="watch"]').filter(visible=True)
    if not cta.count():
        cta = phone.locator("a.primary,button.primary").filter(visible=True)
    mobile["index"]["primary_cta_in_viewport"] = bool(
        cta.count() and cta.first.evaluate("e => {" + DOM + "return inside(e);}")
    )
    for name, url in (("start", base + "start.html"), ("demo", demo_url)):
        if name == "start" and not start_exists:
            mobile[name] = {"exists": False, "no_horizontal_overflow": None}
            continue
        load(phone, url)
        mobile[name] = phone_snapshot(phone)
    mobile_pass = all(
        value["no_horizontal_overflow"] is True for value in mobile.values()
    ) and mobile["index"]["primary_cta_in_viewport"]
    checks.append(result("J8", mobile, mobile_pass))

    auto_page = context.new_page()
    opened = time.monotonic()
    auto_page.goto(demo_url, wait_until="domcontentloaded")
    normal = observe_chat(auto_page, max(0, 6 - (time.monotonic() - opened)))
    reduced_page = context.new_page()
    reduced_page.emulate_media(reduced_motion="reduce")
    opened = time.monotonic()
    reduced_page.goto(demo_url, wait_until="domcontentloaded")
    reduced = observe_chat(reduced_page, max(0, 6 - (time.monotonic() - opened)))
    autoplay, autoplay_pass = autoplay_result(normal, reduced)
    checks.append(result("J10", autoplay, autoplay_pass,
                         url=demo_url, observation_seconds=6))
    if not normal["chat_present"] or not reduced["chat_present"]:
        flags.append(
            "J10: catalog scenario did not render chat in both motion modes; "
            "absence of chat is not evidence that reduced motion waits."
        )
    flags.append(
        "J2/J3 use fully contained boxes; J4 includes text intersecting the viewport. "
        "J8 uses the landing page's marked watch CTA, otherwise its first primary action."
    )
    if blocked:
        flags.append(
            "All requests outside the isolated localhost server were blocked, including "
            "other localhost ports. J6 excludes only attributable external HTTPS block "
            "errors (reported as info); visitor-machine probes and real errors count. "
            "Narration may use caption fallback."
        )
    context.close()
    return sorted(checks, key=lambda check: int(check["id"][1:]))


def resolved_solution(snapshot, solution, base):
    return (
        snapshot["slug"] == solution["slug"]
        and snapshot["line"] == solution["get"]["prompt"].replace("{pages}", base)
        and snapshot["line_visible"]
    )


def unknown_solution_loud(snapshot):
    return (
        bool(re.search(r"not found|unknown|does not exist|unavailable", snapshot["notice"], re.I))
        and "does-not-exist" in snapshot["notice"]
        and not snapshot["line_visible"]
    )


def watch_inventory(solutions, cards, demo_count):
    expected = {solution["id"] for solution in solutions
                if any(scenario["recorded"] for scenario in solution["try"]["scenarios"])}
    watched = {card["id"] for card in cards if card["watch"]}
    recorded = sum(
        scenario["recorded"] for solution in solutions for scenario in solution["try"]["scenarios"]
    )
    return {
        "expected": len(expected), "watch_buttons": len(watched),
        "hero_demos": demo_count, "recorded_demos": recorded, "missing": sorted(expected - watched),
        "unexpected": sorted(watched - expected),
    }, watched == expected and demo_count == recorded


def setup_selection(page):
    return evaluate(page, """
        const command = document.querySelector('[data-copyable]');
        const notice = document.querySelector('[role="status"],[role="alert"]');
        return {slug:document.querySelector('select')?.value || '',
            line:command?.textContent || '', line_visible:!!command && visible(command),
            notice:notice && visible(notice) ? notice.innerText : ''};
    """)


def preview_snapshot(page):
    return evaluate(page, """
        const frame = document.querySelector('.intro-preview iframe');
        if (!frame) return {width:0,height:0,poster:false};
        const box = frame.getBoundingClientRect();
        const overlaps = r => r.width && r.height && r.right > box.left && r.left < box.right
            && r.bottom > box.top && r.top < box.bottom;
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let poster = false;
        while (walker.nextNode()) {
            const n = walker.currentNode, e = n.parentElement;
            if (!n.textContent.trim() || !visible(e) || e.closest('script,style,noscript')) continue;
            const range = document.createRange(); range.selectNodeContents(n);
            if ([...range.getClientRects()].some(overlaps)) poster = true;
        }
        poster ||= [...document.querySelectorAll('img')].some(e =>
            visible(e) && e.complete && e.naturalWidth > 0 && overlaps(e.getBoundingClientRect()));
        return {width:box.width,height:box.height,poster};
    """)


CHAT_FONT_JS = r"""() => {
    const sizes = [];
    for (const root of document.querySelectorAll(
        '[data-aibast~="placeholder"],[data-aibast~="question"],[data-aibast~="answer"],[data-chat-text]'
    )) {
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
            const n = walker.currentNode, e = n.parentElement;
            if (!n.textContent.trim() || !e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})) continue;
            const range = document.createRange(); range.selectNodeContents(n);
            const r = range.getBoundingClientRect();
            let left = 0, top = 0, right = innerWidth, bottom = innerHeight, scale = 1;
            for (let p = e; p; p = p.parentElement) {
                const css = getComputedStyle(p), rect = p.getBoundingClientRect();
                if (css.transform !== 'none') scale *= Math.abs(new DOMMatrix(css.transform).d);
                if (/(hidden|clip|auto|scroll)/.test(css.overflowX)) {
                    left = Math.max(left, rect.left); right = Math.min(right, rect.right);
                }
                if (/(hidden|clip|auto|scroll)/.test(css.overflowY)) {
                    top = Math.max(top, rect.top); bottom = Math.min(bottom, rect.bottom);
                }
            }
            if (r.width && r.height && r.right > left && r.left < right && r.bottom > top && r.top < bottom)
                sizes.push(parseFloat(getComputedStyle(e).fontSize) * scale);
        }
    }
    return sizes;
}"""


def measure_attack(browser, base, blocked):
    context = browser.new_context(viewport={"width": 1440, "height": 900},
                                  reduced_motion="no-preference", service_workers="block")

    def route(request_route):
        if request_route.request.url.startswith(base):
            request_route.continue_()
        else:
            blocked.add(request_route.request.url)
            request_route.abort("blockedbyclient")

    context.route("**/*", route)
    checks = []
    search = json.loads((ROOT / "api/v1/search.json").read_text())["solutions"]
    solutions = [json.loads((ROOT / item["doc"]).read_text()) for item in search]
    page = context.new_page()
    failures = []
    for solution in solutions:
        load(page, base + "start.html?solution=" + solution["slug"])
        snapshot = setup_selection(page)
        if not resolved_solution(snapshot, solution, base):
            failures.append({"slug": solution["slug"], "actual": snapshot})
    checks.append(result("J11", f"{len(solutions) - len(failures)} of {len(solutions)}",
                         not failures, failures=failures))
    load(page, base + "start.html?solution=does-not-exist")
    unknown = setup_selection(page)
    checks.append(result("J12", unknown_solution_loud(unknown), unknown_solution_loud(unknown),
                         evidence=unknown))

    load(page, base + "index.html")
    cards = page.locator('.agent-card[data-name]').evaluate_all("""es => es.map(e => ({
        id:decodeURIComponent(e.dataset.name),
        watch:[...e.querySelectorAll('a,button')].some(b => b.innerText.trim() === 'Watch demo'
            && b.checkVisibility({checkOpacity:true,checkVisibilityCSS:true}))
    }))""")
    counts = page.locator("#stats").inner_text()
    match = re.search(r"([\d,]+)\s+(?:recorded\s+)?demos", counts)
    inventory, passed = watch_inventory(
        solutions, cards, int(match.group(1).replace(",", "")) if match else None
    )
    checks.append(result("J13", passed, passed, evidence=inventory))

    delayed = context.new_page()
    pending = []
    delayed.route("**/solutions/_shared/m365-copilot-demo.html?*",
                  lambda request_route: pending.append((request_route, time.monotonic())))
    delayed.goto(base + "index.html", wait_until="domcontentloaded")
    delayed.wait_for_timeout(1000)
    before = preview_snapshot(delayed)
    for request_route, requested_at in pending:
        delayed.wait_for_timeout(max(0, 5000 - (time.monotonic() - requested_at) * 1000))
        request_route.continue_()
    delayed.wait_for_load_state("networkidle")
    delayed.wait_for_timeout(500)
    after = preview_snapshot(delayed)
    stable = before["width"] > 0 and all(abs(before[k] - after[k]) < .5 for k in ("width", "height"))
    checks.append(result("J14", before["poster"] and stable, before["poster"] and stable,
                         at_one_second=before, after_load=after, stable_size=stable))
    delayed.close()

    nojs = browser.new_context(java_script_enabled=False, viewport={"width": 1440, "height": 900})
    nojs.route("**/*", route)
    noscript = {}
    for name in ("index", "start"):
        fallback = nojs.new_page()
        load(fallback, base + name + ".html")
        snapshot = evaluate(fallback, """
            const nodes = [...document.querySelectorAll('noscript')].filter(visible);
            return {text:nodes.map(e => e.innerText).join(' '),
                links:nodes.flatMap(e => [...e.querySelectorAll('a[href]')])
                    .filter(visible).map(e => e.getAttribute('href')),
                dead_controls:controls().filter(e => e.matches('button,select,input')
                    || e.matches('[data-first-minute],.intro-preview a')).map(labelled),
                preview:[...document.querySelectorAll('.intro-preview')].some(visible)};
        """)
        kept = capabilities([{"href": href} for href in snapshot["links"]], fallback.url)
        snapshot["pass"] = (
            bool(re.search(r"JavaScript", snapshot["text"], re.I))
            and kept["request_info"] and kept["office_hours"]
            and not missing_links(snapshot["links"], fallback.url, ROOT)
            and not snapshot["dead_controls"] and not snapshot["preview"]
            and (name != "start" or all(
                phrase in snapshot["text"] for phrase in
                ("Open GitHub Copilot chat", "Paste", "Ask", "JavaScript")
            ))
        )
        noscript[name] = snapshot
        fallback.close()
    nojs.close()
    checks.append(result("J15", all(s["pass"] for s in noscript.values()),
                         all(s["pass"] for s in noscript.values()), evidence=noscript))

    phone = context.new_page()
    phone.set_viewport_size({"width": 390, "height": 844})
    load(phone, base + "index.html")
    phone.wait_for_timeout(1500)
    sizes = []
    demo = demo_frame(phone)
    if demo:
        for frame in [demo, *demo.child_frames]:
            scale = 1
            ancestor = frame
            while ancestor.parent_frame:
                element = ancestor.frame_element()
                if not element.is_visible():
                    scale = 0
                    break
                scale *= element.evaluate("e => e.getBoundingClientRect().width / e.offsetWidth")
                ancestor = ancestor.parent_frame
            if scale:
                sizes.extend(size * scale for size in frame.evaluate(CHAT_FONT_JS))
    minimum = min(sizes) if sizes else None
    checks.append(result("J16", round(minimum, 2) if minimum is not None else None,
                         minimum is not None and minimum >= 11, visible_text_nodes=len(sizes)))
    load(phone, base + "start.html")
    copy = phone.get_by_role("button", name="Copy", exact=True)
    copy.scroll_into_view_if_needed()
    copy_inside = copy.count() == 1 and copy.evaluate("e => {" + DOM + "return inside(e);}")

    end = context.new_page()
    demo_url = next(solution["try"]["page"] for solution in solutions if solution["try"]["page"])
    load(end, base + demo_url + "&speed=50")
    end.locator("#end").wait_for(state="visible", timeout=60000)
    primary = evaluate(end, """
        const reference = document.querySelector('#show-how');
        const style = reference ? getComputedStyle(reference) : null;
        return controls().filter(e => visible(e) && (
            e.matches('[class*="primary"]') || (style
                && getComputedStyle(e).backgroundColor === style.backgroundColor
                && getComputedStyle(e).color === style.color)
        )).map(labelled);
    """)
    values = {"phone_copy_reachable": bool(copy_inside), "end_card_one_primary": len(primary) == 1}
    checks.append(result("J17", values, all(values.values()), end_primary_controls=primary))
    context.close()
    return checks


UNBACKED_CLAIMS = (
    "under a minute", "About 15 minutes", "with one line", "built into your coding tools",
)


def unbacked_claims(text):
    return [phrase for phrase in UNBACKED_CLAIMS if phrase.casefold() in text.casefold()]


def alphabetical_labels(labels):
    return bool(labels) and labels == sorted(labels, key=str.casefold)


def office_hours_destination(href, page_url, booking):
    destination = urlsplit(urljoin(page_url, href))
    origin = urlsplit(page_url)
    return urljoin(page_url, href) == booking or (
        (destination.scheme, destination.netloc) == (origin.scheme, origin.netloc)
        and destination.path == "/start.html" and destination.fragment == "office-hours"
    )


def legacy_demo_samples(solutions, count=5):
    recorded = [s for s in solutions if any(x["recorded"] for x in s["try"]["scenarios"])]
    selected = recorded[::max(1, len(recorded) // count)][:count]
    return [
        (solution, next(s for s in solution["try"]["scenarios"] if s["recorded"]))
        for solution in selected
    ]


# Measure text within the conversation scroller, after all ancestor clipping.
# Composer placeholders, headers and the player's captions cannot satisfy J19.
MESSAGE_AREA_JS = r"""() => {
    const root = document.querySelector('[data-aibast~="scroll"]');
    if (!root) return '';
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT), parts = [];
    while (walker.nextNode()) {
        const n = walker.currentNode, e = n.parentElement;
        if (!n.textContent.trim() || !e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})) continue;
        let left = 0, top = 0, right = innerWidth, bottom = innerHeight;
        for (let p = e; p; p = p.parentElement) {
            const css = getComputedStyle(p), r = p.getBoundingClientRect();
            if (/(hidden|clip|auto|scroll)/.test(css.overflowX)) {
                left = Math.max(left,r.left); right = Math.min(right,r.right);
            }
            if (/(hidden|clip|auto|scroll)/.test(css.overflowY)) {
                top = Math.max(top,r.top); bottom = Math.min(bottom,r.bottom);
            }
        }
        const range = document.createRange(); range.selectNodeContents(n);
        if ([...range.getClientRects()].some(r => r.width && r.height
            && r.left < right && r.right > left && r.top >= top && r.bottom <= bottom))
            parts.push(n.textContent.trim());
    }
    return parts.join(' ');
}"""


def measure_attack2(browser, base, blocked):
    context = browser.new_context(viewport={"width": 1440, "height": 900},
                                  reduced_motion="no-preference", service_workers="block")

    def route(request_route):
        if request_route.request.url.startswith(base):
            request_route.continue_()
        else:
            blocked.add(request_route.request.url)
            request_route.abort("blockedbyclient")

    context.route("**/*", route)
    checks = []
    search = json.loads((ROOT / "api/v1/search.json").read_text())["solutions"]
    solutions = [json.loads((ROOT / item["doc"]).read_text()) for item in search]
    page = context.new_page()
    load(page, base + "index.html")
    targets = page.locator('[data-first-minute="watch"],.card-actions a').evaluate_all(
        """es => es.filter(e => e.matches('[data-first-minute]') || e.innerText.trim() === 'Watch demo')
        .map(e => ({label:e.innerText,target:e.getAttribute('target')}))"""
    )
    destination, _ = click_control(page, first_cta(page))
    same_tab = {"no_blank_targets": bool(targets) and all(t["target"] != "_blank" for t in targets),
                "one_page": len(context.pages) == 1,
                "hero_navigates_to_player": destination is page and urlsplit(page.url).path.endswith(DEMO)}
    checks.append(result("J18", same_tab, all(same_tab.values()), targets=targets))
    for popup in list(context.pages):
        if popup is not page:
            popup.close()

    phone = context.new_page()
    phone.set_viewport_size({"width": 390, "height": 844})
    opened = time.monotonic()
    phone.goto(base + "index.html", wait_until="domcontentloaded")
    samples = {}
    shots = ROOT / "_shots/r3"
    shots.mkdir(parents=True, exist_ok=True)
    for second in (2, 4, 8):
        phone.wait_for_timeout(max(0, second * 1000 - (time.monotonic() - opened) * 1000))
        demo = demo_frame(phone)
        samples[str(second)] = [
            frame.evaluate(MESSAGE_AREA_JS) for frame in demo.child_frames
            if frame.frame_element().is_visible()
        ] if demo else []
        if second == 4:
            phone.screenshot(path=str(shots / "index-390x844-4s.png"))
    checks.append(result("J19", {s: any(texts) for s, texts in samples.items()},
                         all(any(texts) for texts in samples.values()), evidence=samples))

    load(page, base + "index.html")
    page.locator("#search").fill("insurance claims")
    page.locator("#search").press("Enter")
    page.wait_for_timeout(500)
    listing = evaluate(page, """
        const cards = [...document.querySelectorAll('#grid .agent-card')].filter(visible);
        return {no_dialog:!document.querySelector('[role="dialog"]'),
            cards_in_view:cards.some(e => {const r=e.getBoundingClientRect();
                return r.top < innerHeight && r.bottom > 0;}),
            first_is_claims:/Claims/.test(cards[0]?.querySelector('h2')?.innerText || '')};
    """)
    checks.append(result("J20", listing, all(listing.values())))

    load(page, base + "index.html")
    details = page.locator('.card-actions button').filter(has_text="Details").first
    details.click()
    focus = {"opens_inside": page.evaluate(
        "() => !!document.activeElement.closest('[role=dialog]')")}
    page.screenshot(path=str(shots / "details-open.png"))
    contained = []
    for _ in range(12):
        page.keyboard.press("Tab")
        contained.append(page.evaluate("() => !!document.activeElement.closest('[role=dialog]')"))
    focus["tabs_stay_inside"] = all(contained)
    page.keyboard.press("Escape")
    focus["escape_closes_and_returns"] = (
        page.locator('[role="dialog"]').count() == 0 and details.evaluate("e => e === document.activeElement")
    )
    details.click()
    page.locator("#modal-root").click(position={"x": 2, "y": 2})
    focus["outside_closes_and_returns"] = (
        page.locator('[role="dialog"]').count() == 0 and details.evaluate("e => e === document.activeElement")
    )
    checks.append(result("J21", focus, all(focus.values())))

    legacy = []
    for solution, scenario in legacy_demo_samples(solutions):
        snapshots = []
        for scenario_id in (scenario["id"], solution["slug"] + "-" + scenario["id"]):
            load(page, base + DEMO + "?" + urlencode({
                "scenario": scenario_id, "autoplay": "0", "speed": "50", "only": "1",
            }))
            available = page.locator("#stage").is_visible()
            if available:
                page.get_by_role("button", name="Play", exact=True).click()
                page.wait_for_timeout(500)
            question = page.frame_locator("#surface").locator('[data-aibast~="question"]')
            snapshots.append({
                "name": page.locator("#name").inner_text(),
                "line": page.locator("#get").inner_text(),
                "question": question.inner_text() if available and question.count() else "",
                "problem": page.locator("#msg").inner_text(),
            })
        legacy.append({"slug": solution["slug"], "pass": snapshots[0] == snapshots[1]
                       and snapshots[0]["question"] == scenario["prompt"]
                       and not snapshots[1]["problem"], "snapshots": snapshots})
    checks.append(result("J22", f"{sum(x['pass'] for x in legacy)} of 5",
                         len(legacy) == 5 and all(x["pass"] for x in legacy), evidence=legacy))

    nojs = browser.new_context(java_script_enabled=False)
    nojs.route("**/*", route)
    fallback = nojs.new_page()
    load(fallback, base + DEMO)
    noscript = evaluate(fallback, """
        const nodes=[...document.querySelectorAll('noscript')].filter(visible);
        return {text:nodes.map(e=>e.innerText).join(' '),
            links:nodes.flatMap(e=>[...e.querySelectorAll('a[href]')]).filter(visible)
                .map(e=>e.getAttribute('href')),
            dead:controls().filter(e=>e.matches('button')).map(labelled)};
    """)
    nojs.close()
    fallback_values = {
        "explains_javascript": bool(re.search(r"(needs?|requires?|turn on|enable).*JavaScript|JavaScript.*(needed|required)",
                                             noscript["text"], re.I)),
        "start_link": any(urlsplit(urljoin(base + DEMO, h)).path == "/start.html" for h in noscript["links"]),
        "catalog_link": any(urlsplit(urljoin(base + DEMO, h)).path == "/index.html" for h in noscript["links"]),
        "working_links": bool(noscript["links"]) and not missing_links(noscript["links"], base + DEMO, ROOT),
        "no_dead_controls": not noscript["dead"],
    }
    checks.append(result("J23", fallback_values, all(fallback_values.values()), evidence=noscript))

    load(page, base + "index.html")
    names = {
        "nav": page.locator('nav a[href="start.html"]').inner_text() == "Get an agent running",
        "quiet": page.locator('.intro-links a[href="start.html"]').inner_text() == "Get an agent running",
        "request_label": "Request one-pagers &" not in evaluate(page, "return text(false);"),
    }
    first_screen = evaluate(page, "return text(true);")
    load(page, base + "start.html")
    names["h1"] = page.locator("h1").inner_text() == "Get an agent into Copilot Studio"
    checks.append(result("J24", names, all(names.values())))
    page.screenshot(path=str(shots / "start-1440x900.png"))
    claims = {"index_first_screen": unbacked_claims(first_screen),
              "start": unbacked_claims(evaluate(page, "return text(false);"))}

    plain = evaluate(page, """
        const need = document.querySelector('[data-what-you-need]');
        const command = document.querySelector('[data-copyable]');
        const explanation = command?.closest('.copy-block')?.nextElementSibling || command?.nextElementSibling;
        const office = document.querySelector('#office-hours');
        return {needs:need?.innerText || '', explanation:explanation && visible(explanation)
                ? explanation.innerText : '',
            office_visible:!!office && visible(office) && !office.closest('details'),
            booking:office?.querySelector('a[href]')?.href || '',
            labels:[...document.querySelectorAll('select option')].map(e=>e.textContent)};
    """)
    installer = (ROOT / "docs/installer.html").read_text()
    booking = re.search(r'<a[^>]+href="([^"]+)"[^>]*>Sign up</a>', installer).group(1)
    start_values = {
        "names_tools": all(t in plain["needs"] for t in ("Visual Studio Code", "GitHub Copilot")),
        "explains_paste": all(t in plain["explanation"] for t in ("builds", "Copilot Studio", "sample data")),
        "office_hours": plain["office_visible"] and plain["booking"] == booking,
        "alphabetical": alphabetical_labels(plain["labels"]),
    }
    checks.append(result("J26", start_values, all(start_values.values()), evidence=plain))
    phone.set_viewport_size({"width": 360, "height": 640})
    load(phone, base + "start.html")
    phone.screenshot(path=str(shots / "start-360x640.png"))

    office_links = []
    for name in ("index", "start"):
        load(page, base + name + ".html")
        links = evaluate(page, """
            return controls().filter(e=>e.matches('a[href]') && /office hours/i.test(labelled(e))
                && (location.pathname.endsWith('/start.html') || inside(e)))
                .map(e=>({label:labelled(e),href:e.getAttribute('href')}));
        """)
        office_links.extend({**link, "page": name, "pass": office_hours_destination(
            link["href"], page.url, booking)} for link in links)
    load(page, base + "index.html")
    page.locator('nav a').filter(has_text="Workshops").click()
    page.wait_for_timeout(500)
    workshops = evaluate(page, """
        const headings=[...document.querySelectorAll('h1,h2,h3')].filter(e=>{
            const r=e.getBoundingClientRect();return visible(e) && r.top>=0 && r.top<innerHeight;
        });
        return {heading:headings[0]?.innerText || '',
            sentence:text(true).includes('Build an agent yourself, step by step.'),
            ids:[...document.querySelectorAll('#grid .agent-card[data-name]')].map(e=>decodeURIComponent(e.dataset.name))};
    """)
    page.screenshot(path=str(shots / "workshops.png"))
    expected_workshops = {s["id"] for s in solutions if s["learn"]["workshop"]}
    label_values = {
        "office_destinations": bool(office_links) and all(x["pass"] for x in office_links),
        "workshops_heading": "Workshop" in workshops["heading"],
        "workshops_sentence": workshops["sentence"],
        "workshops_list": bool(workshops["ids"]) and set(workshops["ids"]) == expected_workshops,
    }
    checks.append(result("J27", label_values, all(label_values.values()),
                         office_links=office_links, workshops=workshops))

    demo_url = next(s["try"]["page"] for s in solutions if s["try"]["page"])
    load(page, base + demo_url + "&speed=50&only=1")
    page.locator("#end").wait_for(state="visible", timeout=60000)
    claims["demo_end"] = unbacked_claims(evaluate(page, "return text(false);"))
    checks.append(result("J25", claims, not any(claims.values())))
    context.close()
    return sorted(checks, key=lambda check: int(check["id"][1:]))


def boxes_intersect(a, b):
    return bool(a and b and a["width"] > 0 and a["height"] > 0
                and b["width"] > 0 and b["height"] > 0
                and a["x"] < b["x"] + b["width"] and b["x"] < a["x"] + a["width"]
                and a["y"] < b["y"] + b["height"] and b["y"] < a["y"] + a["height"])


def top_in_view(box, height):
    return bool(box and box["width"] > 0 and box["height"] > 0 and 0 <= box["y"] < height)


def preview_font_sizes(page):
    sizes = []
    demo = demo_frame(page)
    if demo:
        for frame in [demo, *demo.child_frames]:
            scale, ancestor = 1, frame
            while ancestor.parent_frame:
                element = ancestor.frame_element()
                if not element.is_visible():
                    scale = 0
                    break
                scale *= element.evaluate("e => e.getBoundingClientRect().width / e.offsetWidth")
                ancestor = ancestor.parent_frame
            if scale:
                sizes.extend(size * scale for size in frame.evaluate(CHAT_FONT_JS))
    return sizes


PLAIN_TEXT_JS = r"""
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), parts = [];
    while (walker.nextNode()) {
        const n = walker.currentNode, e = n.parentElement;
        if (!n.textContent.trim() || !visible(e)
            || e.closest('script,style,noscript,template')
            || (excludeFooter && e.closest('footer'))
            || (e.closest('details:not([open])')
                && !e.closest('details:not([open])').querySelector(':scope > summary')?.contains(e))) continue;
        parts.push(n.textContent.trim());
    }
    return parts.join(' ');
"""


def plain_text(page, exclude_footer=False):
    return evaluate(page, f"const excludeFooter = {json.dumps(exclude_footer)};\n" + PLAIN_TEXT_JS)


def measure_attack3(browser, base, blocked):
    # Serve local bytes under a Pages hostname so the real consent banner runs.
    site = "http://first-minute.github.io/"
    context = browser.new_context(viewport={"width": 1440, "height": 900},
                                  reduced_motion="no-preference", service_workers="block")

    def route(request_route):
        url = request_route.request.url
        if url.startswith(site):
            response = request_route.fetch(url=base + url[len(site):])
            request_route.fulfill(response=response)
        else:
            blocked.add(url)
            request_route.abort("blockedbyclient")

    context.route("**/*", route)
    page = context.new_page()
    shots = ROOT / "_shots/r4"
    shots.mkdir(parents=True, exist_ok=True)
    search = json.loads((ROOT / "api/v1/search.json").read_text())["solutions"]
    solution = next(json.loads((ROOT / item["doc"]).read_text()) for item in search
                    if json.loads((ROOT / item["doc"]).read_text())["try"]["page"])
    setup = site + "start.html?solution=" + solution["slug"]
    demo = site + solution["try"]["page"]
    checks, arrivals = [], {}
    for width, height in ((1440, 900), (390, 844)):
        page.set_viewport_size({"width": width, "height": height})
        load(page, site + "index.html")
        page.locator(".intro-links a").filter(has_text="Office hours").click()
        page.wait_for_timeout(3000)
        arrivals[f"{width}_hero"] = top_in_view(page.locator("#office-hours").bounding_box(), height)
        if width == 1440:
            page.screenshot(path=str(shots / "office-hours-1440x900.png"))
        load(page, setup + "#office-hours")
        page.wait_for_timeout(3000)
        arrivals[f"{width}_direct"] = top_in_view(page.locator("#office-hours").bounding_box(), height)
    checks.append(result("J28", arrivals, all(arrivals.values())))

    load(page, demo)
    skip = page.get_by_role("link", name="Skip to setup", exact=True)
    skipping = {"during_playback": page.locator("body").get_attribute("data-phase") in ("playing", "answering")
                and skip.count() == 1 and skip.is_visible()}
    if skipping["during_playback"]:
        skip.click()
        skipping["correct_destination"] = page.url == setup
    else:
        skipping["correct_destination"] = False
    load(page, demo + "&autoplay=0")
    total = int(page.locator("#step").inner_text().split(" of ")[-1])
    for _ in range(total - 1):
        page.get_by_role("button", name="Next step", exact=True).click()
    page.get_by_role("button", name="Next step", exact=True).click()
    page.wait_for_timeout(900)
    skipping["next_ends_within_1s"] = page.locator("#end").is_visible()
    skipping["end_focus"] = page.evaluate("() => !!document.activeElement.closest('#end[role=dialog]')")
    if skipping["next_ends_within_1s"]:
        page.get_by_role("link", name="Watch again", exact=True).click()
        skipping["replay_returns_focus"] = page.locator("#play").evaluate("e => e === document.activeElement")
    else:
        skipping["replay_returns_focus"] = False
    load(page, demo + "&embed=1")
    skipping["embed_hides_skip"] = not page.get_by_role("link", name="Skip to setup", exact=True).is_visible()
    checks.append(result("J29", skipping, all(skipping.values())))

    clearance = {}
    for width, height in ((1440, 900), (390, 844)):
        page.set_viewport_size({"width": width, "height": height})
        load(page, demo)
        banner = page.locator("#aibast-clarity-consent")
        caption = page.locator("#caption")
        clearance[f"{width}_caption"] = banner.is_visible() and caption.evaluate(
            "e => {" + DOM + "return inside(e);}") and not boxes_intersect(
            banner.bounding_box(), caption.bounding_box())
        if width == 390:
            page.screenshot(path=str(shots / "demo-mid-play-banner-390x844.png"))
    load(page, site + "index.html")
    page.locator(".card-actions button").filter(has_text="Details").first.click()
    panel = page.locator('[role="dialog"]')
    page.locator("#modal-root").evaluate("e => {e.scrollTop = e.scrollHeight;}")
    action = panel.locator("a,button").filter(visible=True).last
    box, banner_box = action.bounding_box(), page.locator("#aibast-clarity-consent").bounding_box()
    clearance["details_last_action"] = bool(box and banner_box and box["y"] >= 0
        and box["y"] + box["height"] <= banner_box["y"])
    checks.append(result("J30", clearance, all(clearance.values())))

    load(page, site + "index.html")
    page.locator("#search").fill("zzzz")
    page.locator("#search").press("Enter")
    page.wait_for_timeout(400)
    empty = evaluate(page, """
        const root = document.querySelector('#grid');
        const primary = [...root.querySelectorAll('.primary')].filter(visible).map(labelled);
        const details = [...root.querySelectorAll('details')].find(e =>
            e.querySelector('summary')?.innerText.trim() === 'Build it yourself');
        return {primary, office:[...root.querySelectorAll('a')].some(e =>
                visible(e) && /office hours/i.test(e.innerText)),
            developer:!!details && !details.open
                && ['Open Brainstem with this request','Download Learn New agent.py','Brain Surgeon']
                    .every(s => details.textContent.includes(s))};
    """)
    plain = plain_text(page)
    no_results = {"one_clear_primary": empty["primary"] == ["Clear search and filters"],
                  "office_hours": empty["office"], "developer_path_kept": empty["developer"],
                  "plain_text": not any(s.lower() in plain.lower() for s in
                                       ("Brainstem", "agent.py", "localhost", "Brain Surgeon"))}
    checks.append(result("J31", no_results, all(no_results.values()), evidence=empty))
    page.screenshot(path=str(shots / "no-results.png"))

    desktop_sizes = {}
    for width, height in ((1024, 768), (1440, 900)):
        page.set_viewport_size({"width": width, "height": height})
        load(page, site + "index.html")
        page.wait_for_timeout(1500)
        # Owner pick 2026-11-10: the desktop preview shows the full Copilot window, not the plain
        # chat. What must stay readable is the caption line that says what is happening.
        demo = next((f for f in page.frames if "m365-copilot-demo.html" in f.url), None)
        inner = [f.url for f in page.frames if f.parent_frame is demo] if demo else []
        caption = demo.evaluate("parseFloat(getComputedStyle(document.querySelector('#caption')).fontSize)") if demo else None
        desktop_sizes[str(width)] = {"caption_px": caption,
                                     "full_window": bool(inner) and not any("compact=1" in u for u in inner)}
        if width == 1024:
            page.screenshot(path=str(shots / "index-1024x768.png"))
    checks.append(result("J32", desktop_sizes, all(
        v["full_window"] and v["caption_px"] is not None and v["caption_px"] >= 10
        for v in desktop_sizes.values())))
    page.set_viewport_size({"width": 390, "height": 844})
    load(page, setup)
    hints = evaluate(page, """
        const hint = document.querySelector('[data-step="1"] p');
        const need = document.querySelector('[data-what-you-need]');
        return {hint:!!hint && visible(hint) && hint.innerText.includes('Visual Studio Code'),
            help:[...need.querySelectorAll('p')].some(e =>
                visible(e) && e.innerText.startsWith('Do not have these?')
                    && [...e.querySelectorAll('a')].some(a => /office hours/i.test(a.innerText)))};
    """)
    checks.append(result("J33", hints, all(hints.values())))
    page.screenshot(path=str(shots / "start-390x844.png"))
    load(page, site + "index.html")
    honest = {"hero": "a real question" not in evaluate(page, "return text(true);")}
    page.locator("nav a").filter(has_text="Workshops").click()
    page.wait_for_timeout(300)
    honest["workshops"] = "at your own pace" in evaluate(page, "return text(false);")
    checks.append(result("J34", honest, all(honest.values())))
    load(page, site + "index.html")
    plain = plain_text(page, exclude_footer=True)
    export = evaluate(page, """
        const details = [...document.querySelectorAll('details')].find(e =>
            e.querySelector('summary')?.innerText.trim() === 'For developers');
        return !!details && !details.open && details.textContent.includes('Export a RAPP catalog snapshot')
            && !!details.querySelector('[data-action="export-workspace"]');
    """)
    exports = {"plain": not any(s in plain for s in ("Export a RAPP catalog snapshot", "registry.json")),
               "export_kept": export}
    checks.append(result("J35", exports, all(exports.values())))
    context.close()
    return checks


# The four install steps stay in order; the sacred interview is checked live in J49.
PRACTICE_TEXTS = (
    "Press Start: the four blue squares in the middle of the bar at the bottom of the screen.",
    "In Search, type PowerShell. When Windows PowerShell shows up as the best match, press Enter.",
    "Copy the one line, then press Ctrl+V or right-click inside the blue Windows PowerShell window to paste it. Press Enter.",
    "It is installing. When the sign-in page opens, type the code shown in PowerShell (the line that says Your code), press Continue, then Authorize.",
)


def practice_clickthrough(page, shots=None):
    _, texts = journey_clickthrough(page, shots=shots)
    return texts[:4]


def highlighted_clickthrough(page, shots=None):
    """Use only the coach's current highlighted target for every desktop action."""
    visited = set()
    previous = 0
    for _ in range(300):
        if page.locator("#c-n").inner_text() == "Done":
            return sorted(visited)
        page.get_by_role("button", name="Show me where", exact=True).click()
        hint = page.locator("#hint")
        selector = hint.get_attribute("data-target")
        if not selector or selector in (".ps .body", ".vsc .thread"):
            page.wait_for_timeout(250)
            continue
        target = page.locator(selector)
        if not target.count() or not target.first.is_visible():
            page.wait_for_timeout(250)
            continue
        target = target.first
        assert hint.is_visible(), f"Target {selector} has no visible highlight"
        geometry = page.evaluate("""() => {
            const hint = document.querySelector('#hint');
            const selector = hint.dataset.target;
            const target = selector && document.querySelector(selector);
            return {selector, hint:hint.getBoundingClientRect().toJSON(),
                target:target?.getBoundingClientRect().toJSON()};
        }""")
        if geometry["selector"] != selector:
            continue
        assert boxes_intersect(geometry["hint"], geometry["target"]), geometry
        number = int(re.search(r"Step (\d+)", page.locator("#c-n").inner_text())[1])
        assert number in (previous, previous + 1), f"Skipped from step {previous} to {number}"
        previous = number
        if shots and ((number not in visited and number in (1, 2))
                      or (number == 4 and selector == "#studio-send")):
            page.screenshot(path=str(shots / f"start-1440x900-step-{number}.png"))
        visited.add(number)
        if selector == ".vsc textarea":
            target.fill(page.locator("#c-acts [data-line]").get_attribute("data-line"))
        else:
            target.click()
        page.wait_for_timeout(200)
    raise AssertionError("Highlighted click-through did not finish in 300 actions")


def stage_snapshot(page):
    return page.evaluate("""() => ({
        step:document.querySelector('#c-n')?.textContent,
        say:document.querySelector('#c-say')?.textContent,
        desktop:document.querySelector('#pc')?.innerText,
        pointer:document.querySelector('#watch-pointer')?.getAttribute('style')
    })""")


def stage_font_sizes(page):
    return page.evaluate(CHAT_FONT_JS.replace(
        "'[data-aibast~=\"placeholder\"],[data-aibast~=\"question\"],[data-aibast~=\"answer\"],[data-chat-text]'",
        "'#pc'"
    ))


def measure_stage(browser, base, blocked):
    context = browser.new_context(viewport={"width": 1440, "height": 900},
                                  reduced_motion="no-preference", service_workers="block")
    context.route("**/*", lambda route: route.continue_()
                  if route.request.url.startswith(base) else route.abort("blockedbyclient"))
    checks = []
    shots = ROOT / "_shots/stage"
    shots.mkdir(parents=True, exist_ok=True)

    def check(check_id, run):
        try:
            value, passed = run()
            checks.append(result(check_id, value, passed))
        except Exception as exc:
            checks.append(result(check_id, None, False, error=f"{type(exc).__name__}: {exc}"))

    page = context.new_page()
    page.set_default_timeout(30000)
    load(page, base + "start.html")

    def desktop():
        width = page.locator("#pc").bounding_box()["width"] if page.locator("#pc").count() else 0
        scripts = page.locator("script[src]").evaluate_all("es => es.map(e => new URL(e.src).pathname)")
        practice = context.new_page()
        load(practice, base + "docs/practice/windows.html")
        shared = practice.locator("script[src]").evaluate_all("es => es.map(e => new URL(e.src).pathname)")
        engines = [s for s in scripts if s in shared and s.endswith("/practice/desktop.js")]
        value = {"width_fraction": width / 1440, "shared_engines": len(engines),
                 "chat_visible": page.locator("#agent-chat").is_visible(),
                 "taskbar_visible": page.locator("#taskbar").is_visible()}
        practice.close()
        return value, width >= 1440 * .55 and len(engines) == 1 and all(
            value[k] for k in ("chat_visible", "taskbar_visible"))
    check("J36", desktop)

    def watch():
        load(page, base + "start.html")
        first = page.locator("#c-n").inner_text() == "Step 1 of 4"
        page.wait_for_function("() => document.querySelector('#studio-question')?.textContent"
                              " === document.querySelector('#sample-question')?.textContent", timeout=35000)
        name = page.locator("#solution option:checked").inner_text()
        skipped = (page.locator("#studio-agent").inner_text() == name
                   and page.locator("#agent-pasted-line").inner_text() == page.locator("#setup-line").inner_text()
                   and "Sample data" in page.locator("#studio-answer").inner_text())
        load(page, base + "start.html")
        page.wait_for_function("() => document.querySelector('#c-n')?.textContent === 'Done'", timeout=150000)
        full = (page.locator("#studio-question").is_visible()
                and page.locator("#studio-agent").inner_text() == name
                and page.locator("#studio-question").inner_text() == page.locator("#sample-question").inner_text()
                and page.locator("#agent-pasted-line").inner_text() == page.locator("#setup-line").inner_text())
        return {"starts_at_express_1": first, "reaches_studio_35s": skipped, "full_run": full}, first and skipped and full
    check("J37", watch)

    def trying():
        load(page, base + "start.html")
        page.get_by_role("button", name="Step by step", exact=True).click()
        visited = highlighted_clickthrough(page)
        exact = (page.locator("#agent-pasted-line").inner_text() == page.locator("#setup-line").inner_text()
                 and page.locator("#studio-question").inner_text() == page.locator("#sample-question").inner_text())
        return {"visited": visited, "exact_agent_setup": exact}, visited == list(range(1, 5)) and exact
    check("J38", trying)

    def original():
        load(page, base + "docs/practice/windows.html?watch=0&step=1")
        texts = practice_clickthrough(page, shots / "after" if (shots / "after").is_dir() else None)
        shared = page.locator('script[src$="/practice/desktop.js"]').count() == 1
        value = {"steps": len(texts), "original_texts": texts == list(PRACTICE_TEXTS),
                 "uses_extracted_engine": shared}
        return value, all((len(texts) == 4, value["original_texts"], shared))
    check("J39", original)

    def phone():
        first = {}
        for width, height in ((390, 844), (360, 640)):
            page.set_viewport_size({"width": width, "height": height})
            load(page, base + "start.html")
            if not page.locator("#pc").count():
                return None, False
            page.evaluate("window.scrollTo(0, 0)")
            page.locator("#copy").scroll_into_view_if_needed()
            first[str(width)] = (page.locator("#copy").is_visible()
                                and page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
            page.screenshot(path=str(shots / f"start-{width}x{height}-first.png"))
        page.set_viewport_size({"width": 390, "height": 844})
        page.emulate_media(reduced_motion="reduce")
        load(page, base + "start.html")
        sizes = []
        for number in range(1, 5):
            page.locator("#pc").scroll_into_view_if_needed()
            sizes.extend(stage_font_sizes(page))
            if number == 2:
                page.screenshot(path=str(shots / "start-390x844-stage-code.png"))
            if number == 1:
                page.locator("#agent-chat").click()
            elif number == 2:
                page.locator(".vsc textarea").fill(page.locator("#setup-line").inner_text())
                page.locator(".vsc .send").click()
                page.locator("#ms-signin").wait_for()
            elif number == 3:
                page.locator("#ms-signin").click()
                page.locator("#agent-yes").click()
            else:
                page.locator("#agent-open").click()
                page.locator("#studio-send").click()
            page.wait_for_function("(n) => window.practicePC.step() === n", arg=number)
        page.locator("#pc").scroll_into_view_if_needed()
        sizes.extend(stage_font_sizes(page))
        page.screenshot(path=str(shots / "start-390x844-stage.png"))
        return {"minimum_px": min(sizes) if sizes else None, "copy_reachable_no_overflow": first}, bool(
            sizes and min(sizes) >= 11 and all(first.values()))
    check("J40", phone)

    def reduced():
        page.emulate_media(reduced_motion="reduce")
        load(page, base + "start.html")
        if not page.locator("#pc").count():
            return None, False
        before = stage_snapshot(page)
        page.wait_for_timeout(6000)
        after = stage_snapshot(page)
        pointer = page.locator("#watch-pointer")
        waits = before == after and not pointer.is_visible()
        manual = page.locator("#practice-computer").get_attribute("data-mode") == "try"
        page.locator("#agent-chat").click()
        page.wait_for_function("() => document.querySelector('#c-n').textContent !== 'Step 1 of 4'")
        return {"waits": waits, "step_by_step": manual, "click_advances": True}, waits and manual
    check("J41", reduced)
    context.close()
    return checks


def touch_clickthrough(page, shots=None):
    """Complete the whole practice computer with taps, without a hardware keyboard."""
    visited = []
    for step in range(4):
        page.wait_for_function("(n) => window.practicePC.step() === n", arg=step)
        if step == 2:
            page.locator("#ms-signin").wait_for()
        if step == 3:
            page.locator("#agent-open").tap()
        page.get_by_role("button", name="Show me where", exact=True).tap()
        assert page.locator("#hint").is_visible()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        if shots and step in (0, 1):
            page.evaluate("scrollTo(0,0)")
            page.screenshot(path=str(shots / f"start-390x844-step-{step + 1}.png"))
        visited.append(step + 1)
        if step == 1:
            page.get_by_role("button", name="Type it for me", exact=True).tap()
            page.locator(".vsc .send").tap()
        elif step == 0:
            page.locator("#agent-chat").tap()
        elif step == 2:
            page.locator("#ms-signin").tap()
            page.locator("#agent-yes").tap()
        else:
            page.locator("#studio-send").tap()
        page.wait_for_function("(n) => window.practicePC.step() === n", arg=step + 1)
    return visited


def measure_fullscreen_stage(browser, base):
    context = browser.new_context(viewport={"width": 1440, "height": 900},
                                  reduced_motion="no-preference")
    context.route("**/*", lambda route: route.continue_()
                  if route.request.url.startswith(base) else route.abort("blockedbyclient"))
    page = context.new_page()
    page.set_default_timeout(10000)
    checks = []
    shots = ROOT / "_shots/h"
    shots.mkdir(parents=True, exist_ok=True)

    def check(check_id, run):
        try:
            value, passed = run()
            checks.append(result(check_id, value, passed))
        except Exception as exc:
            checks.append(result(check_id, None, False, error=f"{type(exc).__name__}: {exc}"))

    def layout():
        sizes = {}
        for path, width, height in (
            (path, width, height)
            for path in ("start.html", "docs/practice/windows.html")
            for width, height in ((1440, 900), (1280, 720))
        ):
            page.set_viewport_size({"width": width, "height": height})
            load(page, base + path + "?watch=0")
            page.locator("#pc").wait_for()
            name = "start" if path == "start.html" else "practice"
            page.screenshot(path=str(shots / f"{name}-{width}x{height}-step-1.png"))
            sizes[f"{name}-{width}x{height}"] = page.evaluate("""() => {
                const pc = document.querySelector('#pc').getBoundingClientRect();
                const bar = document.querySelector('#coach').getBoundingClientRect();
                const main = document.querySelector('main, .page').getBoundingClientRect();
                return {width_fraction:pc.width/main.width,
                    desktop_inside:pc.top >= 0 && pc.bottom <= innerHeight,
                    bar_inside:bar.top >= pc.bottom && bar.bottom <= innerHeight,
                    full_width_bar:Math.abs(pc.width-bar.width) < 2,
                    no_side_column:document.querySelector('.stage').children.length === 1};
            }""")
        return sizes, all(v["width_fraction"] >= .92 and all(
            v[k] for k in ("desktop_inside", "bar_inside", "full_width_bar", "no_side_column")
        ) for v in sizes.values())
    check("J45", layout)

    def modes():
        page.set_viewport_size({"width": 1440, "height": 900})
        load(page, base + "start.html")
        page.locator("#pc").wait_for()
        page.wait_for_function("() => window.practicePC.step() > 0", timeout=6000)
        auto = page.locator("#practice-computer").get_attribute("data-mode") == "watch"
        before = page.evaluate("window.practicePC.step()")
        page.locator("#pc").click(position={"x": 4, "y": 4})
        takeover = (page.locator("#practice-computer").get_attribute("data-mode") == "try"
                    and page.evaluate("window.practicePC.step()") == before)
        load(page, base + "start.html")
        page.get_by_role("button", name="Step by step", exact=True).click()
        before = stage_snapshot(page)
        page.wait_for_timeout(8000)
        waits = stage_snapshot(page) == before
        visited = highlighted_clickthrough(page, ROOT / "_shots/j")
        studio = page.locator("#studio-question").is_visible()
        load(page, base + "start.html?watch=0")
        page.locator("#pc").wait_for()
        opt_out = (page.locator("#practice-computer").get_attribute("data-mode") == "try"
                   and page.evaluate("window.practicePC.step()") == 0)
        touch = {}
        touch_context = browser.new_context(has_touch=True, reduced_motion="reduce")
        touch_context.route("**/*", lambda route: route.continue_()
                            if route.request.url.startswith(base) else route.abort("blockedbyclient"))
        try:
            mobile = touch_context.new_page()
            for width in (360, 390):
                mobile.set_viewport_size({"width": width, "height": 844})
                load(mobile, base + "start.html?watch=0")
                mobile.locator("#pc").wait_for()
                assert not mobile.locator(".all-steps").evaluate("e => e.open")
                mobile.locator(".all-steps summary").tap()
                assert mobile.locator("#c-prog .now").is_visible()
                mobile.locator(".all-steps summary").tap()
                touch[str(width)] = touch_clickthrough(mobile, shots if width == 390 else None)
        finally:
            touch_context.close()
        value = {"autoplays": auto, "takeover_keeps_step": takeover,
                 "manual_waits_8s": waits, "visited": visited,
                 "ends_in_studio": studio, "watch_0_is_manual": opt_out, "touch_steps": touch}
        return value, all((auto, takeover, waits, visited == list(range(1, 5)), studio, opt_out,
                          all(v == list(range(1, 5)) for v in touch.values())))
    check("J46", modes)

    def kept():
        load(page, base + "start.html?watch=0")
        page.locator("#pc").wait_for()
        value = page.evaluate("""() => ({
            picker:!!document.querySelector('#solution:not(:disabled)'),
            setup_section:[...document.querySelectorAll('h2')].some(e => e.textContent === 'The setup line'),
            copy:!!document.querySelector('#copy:not(:disabled)'),
            question:!!document.querySelector('#sample-question')?.textContent,
            needs:!!document.querySelector('[data-what-you-need]'),
            preview:document.body.textContent.includes('Private preview'),
            details:['Where is GitHub Copilot chat?', 'Prefer to build it by hand?',
                'Run it on your own computer instead'].every(s =>
                [...document.querySelectorAll('details summary')].some(e => e.textContent === s)),
            office_hours:!!document.querySelector('#office-hours a'),
            one_copyable:document.querySelectorAll('[data-copyable]').length === 1
        })""")
        for selector in ("#solution", "#copy", "#sample-question", "[data-what-you-need]",
                         ".ai-soon", "#office-hours a"):
            page.locator(selector).scroll_into_view_if_needed()
            value[f"reachable_{selector}"] = page.locator(selector).is_visible()
        value["matches_getLine"] = page.evaluate("""async () => {
            const slug = document.querySelector('#solution').value;
            const solution = await (await fetch(`api/v1/solutions/${slug}.json`)).json();
            return document.querySelector('#setup-line').textContent ===
                window.AibastJourney.getLine(solution, new URL('./', location.href).href);
        }""")
        page.locator("#agent-chat").click()
        value["bar_setup"] = page.locator("#stage-setup-line").inner_text() == page.locator("#setup-line").inner_text()
        page.locator("#solution").select_option(index=1)
        page.locator("#agent-chat").wait_for()
        page.locator("#agent-chat").click()
        value["picker_updates_line"] = page.locator("#stage-setup-line").inner_text() == page.locator("#setup-line").inner_text()
        page.locator(".vsc textarea").fill(page.locator("#setup-line").inner_text())
        page.locator(".vsc .send").click()
        page.locator("#ms-signin").click()
        page.locator("#agent-yes").click()
        value["bar_question"] = page.locator("#stage-question").inner_text() == page.locator("#sample-question").inner_text()
        load(page, base + "docs/practice/windows.html")
        page.locator("#tb-start").click()
        page.screenshot(path=str(shots / "practice-1440x900-step-2.png"))
        return value, all(value.values())
    check("J47", kept)
    context.close()
    return checks


def aideate_copy_violations(text):
    patterns = (
        r"\bseller starts\b", r"\bClose the deal\b", r"\bOnly we have\b",
        r"\b(?:Contoso|Fabrikam|Northwind|Adventure Works|Acme|"
        r"OpenAI|Google|Amazon|AWS|Anthropic|Salesforce|Apple|Meta|"
        r"Nvidia|IBM|Oracle|SAP|Deloitte|Accenture|Walmart|Wells Fargo)\b",
        r"\b(?!Microsoft\b)[A-Z][\w'-]*(?:\s+[\w&'-]+){0,3}\s+"
        r"(?:Corporation|Corp|Inc|Ltd|LLC|PLC|GmbH)\b",
        r"[$\u00a3\u20ac\u00a5\u20b9]\s*\d[\d,.]*",
        r"\b(?:USD|GBP|EUR|JPY|CAD|AUD|INR)\s*\d[\d,.]*",
        r"\b\d[\d,.]*\s*(?:USD|GBP|EUR|JPY|CAD|AUD|INR|dollars?|pounds?|euros?|yen)\b",
        r"\b(?:customer|company|client)\s+(?:named|called)\s+\S+",
    )
    return [match.group(0) for pattern in patterns
            for match in re.finditer(pattern, text, re.I)]


class LinkAnchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors = set()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == "id" or (tag == "a" and name == "name"):
                self.anchors.add(value)


def aideate_link_failures(page, links, base):
    page_url = base + "aideate.html"
    missing = missing_links(links, page_url, ROOT)
    if missing:
        return missing
    responses = {}
    for href in sorted(set(links)):
        target = internal_target(href, page_url, ROOT)
        if target is None:
            continue
        url = urljoin(base, target.relative_to(ROOT).as_posix())
        if url not in responses:
            response = page.request.get(url)
            parser = LinkAnchors()
            parser.feed(response.text())
            responses[url] = response.status, parser.anchors
        status, anchors = responses[url]
        fragment = unquote(urlsplit(urljoin(page_url, href)).fragment)
        if status != 200 or (fragment and fragment not in anchors):
            missing.append({"href": href, "status": status, "fragment": fragment})
    return missing


def measure_aideate(browser, base, blocked):
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    errors = []

    def route(request_route):
        if request_route.request.url.startswith(base):
            request_route.continue_()
        else:
            blocked.add(request_route.request.url)
            request_route.abort("blockedbyclient")

    context.route("**/*", route)
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append({
        "kind": "pageerror", "message": str(error),
    }))
    page.on("console", lambda message: errors.append({
        "kind": "console", "message": message.text,
        "url": message.location.get("url", ""),
    }) if message.type == "error" else None)
    page.on("response", lambda response: errors.append({
        "kind": "http", "url": response.url, "status": response.status,
    }) if response.status >= 400 else None)
    page.on("requestfailed", lambda request: errors.append({
        "kind": "requestfailed", "url": request.url, "message": request.failure,
    }))
    try:
        load(page, base + "aideate.html")
        snapshot = evaluate(page, """
            const accent = getComputedStyle(document.documentElement)
                .getPropertyValue('--cp-accent').trim();
            const sample = document.createElement('span');
            sample.style.backgroundColor = accent; document.body.append(sample);
            const primaryColor = getComputedStyle(sample).backgroundColor; sample.remove();
            const primary = controls().filter(inside).filter(e =>
                getComputedStyle(e).backgroundColor === primaryColor).map(labelled);
            const address = 'rapp.microsoft.com';
            return {primary, text:text(false),
                address_is_text:text(false).includes(address),
                address_not_linked:![...document.querySelectorAll('a')].some(e =>
                    e.textContent.includes(address) || (e.getAttribute('href') || '').includes(address)),
                links:[...document.querySelectorAll('a[href]')].map(e => e.getAttribute('href'))};
        """)
        violations = aideate_copy_violations(snapshot["text"])
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(250)
        overflow = phone_snapshot(page)
        relevant_errors = [
            error for error in errors
            if not policy_blocked_error(error, blocked, base)
            and urlsplit(error.get("url", "")).hostname != "forms.cloud.microsoft"
        ]
        values = {
            "zero_console_errors": not relevant_errors,
            "one_request_primary": snapshot["primary"] == ["Request a session"],
            "no_phone_overflow": overflow["no_horizontal_overflow"],
            "approved_copy": not violations,
            "preview_address_is_text": snapshot["address_is_text"],
            "preview_address_not_linked": snapshot["address_not_linked"],
        }
        checks = [result("J42", values, all(values.values()),
                         errors=relevant_errors, primary=snapshot["primary"],
                         copy_violations=violations)]
        missing = aideate_link_failures(page, snapshot["links"], base)
        reachable = {}
        for source in ("index.html", "start.html"):
            load(page, base + source)
            reachable[source] = page.locator("a[href]").evaluate_all("""es => es.some(e =>
                new URL(e.href).origin === location.origin
                && new URL(e.href).pathname === new URL('aideate.html', location.href).pathname)""")
        reachable["all_same_site_links_resolve"] = not missing
        checks.append(result("J43", reachable, all(reachable.values()), missing=missing))
        return checks
    finally:
        context.close()


def measure_polish(browser, base, blocked):
    shots = ROOT / "_shots" / "g"
    shots.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(viewport={"width": 1440, "height": 900},
                                  reduced_motion="reduce")

    def route(request_route):
        if request_route.request.url.startswith(base):
            request_route.continue_()
        else:
            blocked.add(request_route.request.url)
            request_route.abort("blockedbyclient")

    context.route("**/*", route)
    page = context.new_page()
    details = {}
    values = {}
    try:
        load(page, base + "index.html")
        page.wait_for_selector(".agent-card")
        page.mouse.move(0, 0)
        details["employee_errors"] = page.locator(".agent-card").evaluate_all(
            r"es => es.filter(e => /\ba employee\b/i.test(e.innerText)).map(e => e.innerText)"
        )
        values["card_articles"] = not details["employee_errors"]
        details["hero"] = page.evaluate("""() => {
            const box = s => document.querySelector(s).getBoundingClientRect();
            const preview = box('.preview-box'), search = box('.search-wrap');
            const intro = box('.intro'), figure = box('.intro-preview');
            const style = getComputedStyle(document.querySelector('.intro'));
            const top = intro.top + parseFloat(style.paddingTop);
            const bottom = intro.bottom - parseFloat(style.paddingBottom);
            return {gap:search.top - preview.bottom, search_bottom:search.bottom,
                preview_ratio:preview.width / preview.height,
                center_offset:Math.abs((figure.top + figure.bottom - top - bottom) / 2)};
        }""")
        hero = details["hero"]
        values["hero_space"] = (
            0 <= hero["gap"] <= 96 and hero["search_bottom"] <= 900
            and hero["center_offset"] <= 2
            and abs(hero["preview_ratio"] - 1.6) < .01
        )
        page.screenshot(path=str(shots / "index-1440-first-screen.png"))
        alphas = {}
        for source in ("index.html", "start.html", "aideate.html"):
            load(page, base + source)
            page.evaluate("window.scrollTo(0, 400)")
            page.wait_for_timeout(200)
            alphas[source] = page.locator(".topbar").evaluate(r"""e => {
                const color = getComputedStyle(e).backgroundColor;
                const numbers = color.match(/[\d.]+/g).map(Number);
                return numbers.length === 4 ? numbers[3] : 1;
            }""")
            if source == "index.html":
                page.screenshot(path=str(shots / "index-scrolled-header.png"))
        details["header_alpha"] = alphas
        values["opaque_headers"] = all(alpha == 1 for alpha in alphas.values())

        load(page, base + "index.html")
        cards = page.locator(".agent-card")
        cards.nth(2).scroll_into_view_if_needed()
        page.mouse.move(0, 0)
        page.wait_for_timeout(200)
        resting = cards.evaluate_all("""es => es.map(e => {
            const s = getComputedStyle(e);
            return {transform:s.transform, border:s.borderColor,
                shadow:s.boxShadow, hovered:e.matches(':hover')};
        })""")
        cards.nth(2).hover()
        page.wait_for_timeout(200)
        page.mouse.move(0, 0)
        page.wait_for_timeout(200)
        released = cards.evaluate_all("""es => es.map(e => {
            const s = getComputedStyle(e);
            return {transform:s.transform, border:s.borderColor,
                shadow:s.boxShadow, hovered:e.matches(':hover')};
        })""")
        details["hover_like_cards"] = [
            i for i, card in enumerate(released)
            if card["hovered"] or card["transform"] != "none"
            or card["border"] != resting[0]["border"]
            or card["shadow"] != resting[0]["shadow"]
        ]
        values["cards_release_hover"] = not details["hover_like_cards"] and released == resting
        page.screenshot(path=str(shots / "third-column-cards.png"))
        touch = browser.new_context(viewport={"width": 1440, "height": 900}, has_touch=True,
                                    reduced_motion="reduce")
        touch.route("**/*", route)
        try:
            touch_page = touch.new_page()
            load(touch_page, base + "index.html")
            third = touch_page.locator(".agent-card").nth(2)
            third.scroll_into_view_if_needed()
            third.locator("h2").tap()
            touch_page.keyboard.press("Escape")
            touch_page.wait_for_timeout(200)
            details["touch_card"] = third.evaluate("""e => {
                const s = getComputedStyle(e);
                return {transform:s.transform, border:s.borderColor,
                    hover_capable:matchMedia('(hover:hover) and (pointer:fine)').matches};
            }""")
            values["cards_release_hover"] = values["cards_release_hover"] and (
                not details["touch_card"]["hover_capable"]
                and details["touch_card"]["transform"] == "none"
                and details["touch_card"]["border"] == resting[0]["border"]
            )
        finally:
            touch.close()

        load(page, base + "index.html?view=solutions#workshops")
        details["workshops"] = {
            "cards": page.locator(".agent-card").count(),
            "label": page.locator("#result-count").inner_text(),
        }
        workshops = details["workshops"]
        values["workshop_count"] = workshops["label"] == (
            f'{workshops["cards"]} workshop' + ("" if workshops["cards"] == 1 else "s")
        ) and workshops["cards"] > 0
        page.locator("#result-count").scroll_into_view_if_needed()
        page.screenshot(path=str(shots / "workshops-view-count.png"))

        phone = {}
        for width in (360, 390):
            page.set_viewport_size({"width": width, "height": 844})
            load(page, base + "start.html")
            page.wait_for_function("() => document.querySelector('#setup-line').textContent.length > 0")
            phone[str(width)] = page.locator("#setup-line").evaluate(r"""e => {
                const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
                const chars = [];
                while (walker.nextNode()) {
                    const n = walker.currentNode;
                    for (let i = 0; i < n.length; i++) {
                        const range = document.createRange();
                        range.setStart(n, i); range.setEnd(n, i + 1);
                        const r = range.getBoundingClientRect();
                        chars.push({char:n.textContent[i], top:r.top, left:r.left, right:r.right});
                    }
                }
                const breaks = chars.flatMap((c, i) => {
                    const previous = chars[i - 1];
                    return previous && Math.abs(c.top - previous.top) > 2
                        && !/\s/.test(c.char + previous.char) && previous.char !== '/'
                        ? [i] : [];
                });
                const r = e.getBoundingClientRect();
                return {mid_word_breaks:breaks, chars:chars.length,
                    text_fits:chars.every(c => c.left >= r.left && c.right <= r.right),
                    no_page_overflow:document.documentElement.scrollWidth <= innerWidth};
            }""")
            page.locator("#setup-line").scroll_into_view_if_needed()
            page.screenshot(path=str(shots / f"start-{width}-setup-line.png"))
        details["setup"] = phone
        values["setup_wraps_at_spaces"] = all(
            item["chars"] > 0 and not item["mid_word_breaks"]
            and item["text_fits"] and item["no_page_overflow"]
            for item in phone.values()
        )
        page.set_viewport_size({"width": 1440, "height": 900})
        load(page, base + "aideate.html")
        claim = page.locator(".ai-claim").inner_text()
        values["aideate_claim"] = (
            claim == "Working in your own environment, in one session."
            and "Proven in minutes, on your own stack." not in page.locator("body").inner_text()
        )
        page.locator(".ai-claim").scroll_into_view_if_needed()
        page.screenshot(path=str(shots / "aideate-claim.png"))
        return [result("J44", values, all(values.values()), measurements=details)]
    finally:
        context.close()


def real_interview():
    """Read the real tour at check time, including its dynamic export/delete copy."""
    source = (ROOT / "rapp_brainstem/index.html").read_text()
    tour = source.split("function defineSteps()", 1)[1].split(
        "async function pickSurgeryFile()", 1
    )[0]
    matches = list(re.finditer(r"id: '([^']+)'", tour))
    steps = []
    for index, match in enumerate(matches):
        if match[1] == "intro":
            continue
        block = tour[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(tour)]
        heading = re.search(r"<h3>(.*?)</h3>", block, re.S)
        hint = re.search(r"(?:hint:|this\.hint =)\s*`(.*?)`", block, re.S)
        assert heading and hint, f"Real tour step {match[1]} has no heading/hint"
        steps.append({
            "id": match[1], "heading": heading[1],
            "hint": re.sub(r"\$\{esc\(surgeryFile \|\| ''\)\}", "hacker_news_agent.py", hint[1]),
            "skippable": "skippable: true" in block,
        })
    return steps


def journey_clickthrough(page, *, skip=False, shots=None, restore_helper=False):
    """Drive visible controls with real browser pointer/keyboard input."""
    local = "/docs/practice/" in page.url
    count = 17 if local else 4
    assert page.evaluate("window.practicePC.STEPS.length") == count
    visited = []
    texts = []
    for number in range(1, count + 1):
        page.wait_for_function("(n) => window.practicePC.step() === n", arg=number - 1)
        if local and number == 4:
            page.locator("#ghcode").wait_for()
        if local and number == 5:
            page.locator(".bs .starter-btn").first.wait_for()
        if not local and number == 3:
            page.locator("#ms-signin").wait_for()
        page.get_by_role("button", name="Show me where", exact=True).click()
        selector = page.locator("#hint").get_attribute("data-target")
        assert selector and page.locator(selector).first.is_visible(), (number, selector)
        assert page.locator("#hint").is_visible()
        assert page.evaluate("""() => {
            const h = document.querySelector('#hint');
            const t = document.querySelector(h.dataset.target);
            const a = h.getBoundingClientRect(), b = t.getBoundingClientRect();
            return a.left <= b.right && a.right >= b.left && a.top <= b.bottom &&
                a.bottom >= b.top && b.width > 0 && b.height > 0;
        }""")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        visited.append(number)
        texts.append(page.locator("#c-say").inner_text())
        if shots and ((local and number in (3, 5, 6, 9, 11, 13, 15, 16, 17))
                      or (not local and number in (1, 2, 4))):
            page.evaluate("scrollTo(0,0)")
            page.screenshot(path=str(shots / (
                f"{'practice' if local else 'start'}-{page.viewport_size['width']}x"
                f"{page.viewport_size['height']}-step-{number}.png"
            )))
        if skip and page.get_by_role("button", name="Skip this step", exact=True).count():
            page.get_by_role("button", name="Skip this step", exact=True).click()
            continue
        if not local:
            if number == 1:
                page.locator("#agent-chat").click()
            elif number == 2:
                page.locator(".vsc textarea").fill(page.locator("#setup-line").inner_text())
                page.locator(".vsc textarea").press("Enter")
            elif number == 3:
                page.locator("#ms-signin").click()
                page.locator("#agent-yes").click()
            else:
                page.locator("#agent-open").click()
                page.locator("#studio-send").click()
            continue
        if number == 1:
            page.locator("#tb-start").click()
        elif number == 2:
            page.locator("#ssearch").fill("PowerShell")
            page.locator("#ssearch").press("Enter")
        elif number == 3:
            page.locator(".ps .in").fill(
                page.locator("#c-acts [data-line]").get_attribute("data-line")
            )
            page.locator(".ps .in").press("Enter")
        elif number == 4:
            page.locator("#ghcode").fill("A1B2-C3D4")
            page.locator("#ghgo").click()
            page.locator("#ghauth").click()
        elif number in (5, 8, 17):
            pill = {5: "What can you do?", 8: "What do you remember?",
                    17: "What should I do next?"}[number]
            page.get_by_role("button", name=pill, exact=True).click()
            if number == 8:
                assert "Alex" in page.locator(".bs .log").inner_text()
                assert "agent called ContextMemory" in page.locator(".bs .log").inner_text()
                page.get_by_role("button", name="Keep going", exact=True).click()
        elif number in (6, 12, 14, 16):
            prompt = {
                6: "Remember, my name is Alex and I prepare customer meetings.",
                12: "get my latest hacker news", 14: "get my latest hacker news",
                16: "Learn a new agent called QuoteOfTheDay that gives me an inspiring quote when I ask for motivation.",
            }[number]
            page.locator(".bs form input").fill(prompt)
            page.locator(".bs form input").press("Enter")
            chat = page.locator(".bs .log").inner_text()
            if number == 6:
                assert "agent called ManageMemory" in chat
            elif number == 12:
                assert "I cannot get Hacker News" in chat
            elif number == 14:
                assert "Hacker News is available again" in chat
        elif number == 7:
            page.locator("#bs-clear").click()
            assert page.locator(".bs .log").inner_text().find("Alex") == -1
        elif number == 9:
            page.locator("#bs-agents").click()
        elif number == 10:
            page.locator("#bs-export-agent").click()
        elif number == 11:
            page.locator("#bs-delete-agent").click()
            page.locator("#bs-confirm-delete").click()
        elif number == 13:
            if restore_helper:
                helper = page.get_by_role("button", name="Do it for me", exact=True)
                assert helper.is_visible()
                helper.click()
            else:
                page.locator("#download-agent").drag_to(page.locator("#bs-drop"))
        elif number == 15:
            page.locator("#bs-book").click()
            page.locator("#bs-library-search").fill("meeting prep")
            page.locator("#bs-add-meeting").click()
    page.wait_for_function("(n) => window.practicePC.step() === n", arg=count)
    if local and not skip:
        assert "Sample reply" in page.locator(".bs .log").inner_text()
        assert page.evaluate("window.practicePC.state.memory").startswith("Remember, my name is Alex")
        assert page.evaluate("window.practicePC.state.news") is True
        assert page.evaluate("window.practicePC.state.meeting") is True
        assert page.evaluate("window.practicePC.state.created") is True
    return visited, texts


def measure_two_journeys(browser, base):
    context = browser.new_context(viewport={"width": 1440, "height": 900},
                                  reduced_motion="reduce")
    context.route("**/*", lambda route: route.continue_()
                  if route.request.url.startswith(base) else route.abort("blockedbyclient"))
    page = context.new_page()
    page.set_default_timeout(12000)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
    checks = []
    shots = ROOT / "_shots/j"
    shots.mkdir(parents=True, exist_ok=True)

    def check(check_id, run):
        try:
            value = run()
            checks.append(result(check_id, value, all(value.values())))
        except Exception as exc:
            checks.append(result(check_id, None, False, error=f"{type(exc).__name__}: {exc}"))

    def separated():
        load(page, base + "start.html?watch=0")
        page.locator("#pc").wait_for()
        express = page.evaluate("window.practicePC.STEPS.map(s => s.id)")
        text = page.locator("body").inner_text()
        forward = page.locator('a[href="docs/practice/windows.html"]').count() == 1
        load(page, base + "docs/practice/windows.html?watch=0&step=1")
        page.locator("#pc").wait_for()
        practice = page.evaluate("window.practicePC.STEPS.map(s => s.id)")
        return {
            "express_four": express == ["agent-chat", "agent-line", "agent-setup", "agent-test"],
            "no_install_in_express": not re.search(r"PowerShell|Brainstem install|code chat", text, re.I),
            "practice_install_then_interview": practice == [
                "start", "find", "paste", "signin", *[s["id"] for s in real_interview()]
            ],
            "links_both_ways": forward and page.locator('a[href="../../start.html"]').count() >= 1,
        }
    check("J48", separated)

    def matches():
        load(page, base + "docs/practice/windows.html?watch=0&step=1")
        page.locator("#pc").wait_for()
        actual = page.evaluate("""() => window.practicePC.STEPS.slice(4).map(s => {
            const rendered = document.createElement('div');
            rendered.innerHTML = s.say;
            return {id:s.id, heading:rendered.querySelector('strong')?.textContent,
                hint:s.tourHint, skippable:!!s.skippable};
        })""")
        expected = real_interview()
        assert len(expected) == 13
        # Finish install using visible input before inspecting the pretend chat.
        page.locator("#tb-start").click()
        page.locator("#ssearch").fill("PowerShell")
        page.locator("#ssearch").press("Enter")
        page.locator(".ps .in").fill("irm https://microsoft.github.io/aibast-agents-library/install.ps1 | iex")
        page.locator(".ps .in").press("Enter")
        page.locator("#ghcode").fill("A1B2-C3D4")
        page.locator("#ghgo").click()
        page.locator("#ghauth").click()
        page.locator(".bs .starter-btn").first.wait_for()
        return {"headings_hints_skips_match": actual == expected,
                "starter_labels": page.locator(".bs .starter-btn").all_text_contents() == [
                    "What can you do?", "What do you remember?", "What should I do next?"
                ]}
    check("J49", matches)

    def end_to_end():
        load(page, base + "docs/practice/windows.html?watch=0&step=1")
        page.locator("#pc").wait_for()
        done, _ = journey_clickthrough(page, shots=shots)
        load(page, base + "docs/practice/windows.html?watch=0&step=1")
        page.locator("#pc").wait_for()
        skipped, _ = journey_clickthrough(page, skip=True)
        for width in (360, 390):
            page.set_viewport_size({"width": width, "height": 844})
            load(page, base + "docs/practice/windows.html?watch=0&step=1")
            page.locator("#pc").wait_for()
            journey_clickthrough(page, shots=shots if width == 390 else None, restore_helper=True)
        page.set_viewport_size({"width": 1440, "height": 900})
        page.emulate_media(reduced_motion="no-preference")
        page.evaluate("localStorage.removeItem('aibast-practice-session')")
        load(page, base + "docs/practice/windows.html")
        page.wait_for_function("() => window.practicePC?.step() === 17", timeout=180000)
        watch = page.evaluate("window.practicePC.state.completed")
        return {"done": done == list(range(1, 18)), "skipped": skipped == list(range(1, 18)),
                "watch_all_17": watch == list(range(1, 18)), "mobile_no_overflow": True,
                "console_clean": not errors}
    check("J50", end_to_end)
    context.close()
    return checks


def measure_session(browser, base):
    shots = ROOT / "_shots/k"
    shots.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(viewport={"width":1366, "height":768},
                                  reduced_motion="no-preference",
                                  permissions=["clipboard-read", "clipboard-write"])
    context.route("**/*", lambda route: route.continue_()
                  if route.request.url.startswith(base) else route.abort("blockedbyclient"))
    page = context.new_page()
    page.set_default_timeout(12000)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: errors.append(message.text)
            if message.type == "error" else None)
    checks = []
    practice = base + "docs/practice/windows.html"

    def check(check_id, run):
        try:
            value = run()
            checks.append(result(check_id, value, all(value.values())))
        except Exception as exc:
            checks.append(result(check_id, None, False,
                                 error=f"{type(exc).__name__}: {exc}"))

    def open_step(number):
        load(page, practice + f"?watch=0&step={number}")
        page.wait_for_function("(n) => window.practicePC?.step() === n - 1", arg=number)

    def follow():
        load(page, base + "docs/installer.html")
        line = page.locator("#brainstem-win-cmd").inner_text()
        open_step(2)
        page.screenshot(path=str(shots / "practice-1366x768-step-2.png"))
        page.locator("#ssearch").fill("PowerShell")
        page.locator("#ssearch").press("Enter")
        copy = page.get_by_role("button", name="Copy the real line", exact=True)
        copy.click()
        copied = page.evaluate("navigator.clipboard.readText()")
        page.screenshot(path=str(shots / "practice-1366x768-step-3.png"))
        assert "Paste this in your real PowerShell now, then come back. It installs while you practise." in page.locator("#c-context").inner_text()
        page.locator(".ps .in").focus()
        page.keyboard.insert_text(copied)
        assert page.locator(".ps .in").text_content().strip() == line
        start = time.monotonic()
        page.locator(".ps .in").press("Enter")
        page.locator("#ghcode").wait_for()
        page.locator("#ghcode").fill("A1B2-C3D4")
        page.locator("#ghgo").click()
        page.locator("#ghauth").click()
        page.locator(".bs .starter-btn").first.wait_for()
        duration = time.monotonic() - start
        page.screenshot(path=str(shots / "practice-1366x768-step-5.png"))
        return {"copied_bytes_match":copied.encode() == line.encode(),
                "pretend_under_10_seconds":duration < 10,
                "labelled_pretend":"pretend" in page.locator(".lede").inner_text().lower()}
    check("J51", follow)

    def finish_line():
        open_step(8)
        page.get_by_role("button", name="What do you remember?", exact=True).click()
        exact = page.locator("#c-say").inner_text() == "You have met it. It still knows you."
        address = page.locator("#c-context").inner_text() == "Your real one should be ready: open http://localhost:7071 and do the same four steps."
        primary = page.locator("#c-acts .pri").count() == 1
        page.screenshot(path=str(shots / "practice-1366x768-step-8-finish.png"))
        page.reload()
        page.get_by_role("button", name="Keep going", exact=True).wait_for()
        page.get_by_role("button", name="Keep going", exact=True).click()
        page.wait_for_function("() => window.practicePC.step() === 8")
        page.screenshot(path=str(shots / "practice-1366x768-step-9.png"))
        return {"finish_text":exact, "localhost_plain_text":address and
                page.locator('a[href="http://localhost:7071"]').count() == 0,
                "one_primary":primary, "continues_to_9":True, "finish_resumes":True}
    check("J52", finish_line)

    def self_serve():
        links = True
        for number in range(1, 18):
            open_step(number)
            assert page.locator("#c-say").inner_text()
            assert page.get_by_role("button", name="Show me where", exact=True).is_visible()
            page.locator("#step-help summary").click()
            assert page.locator("#step-fixes li").count() in (2, 3)
            href = page.locator("#step-help-link").get_attribute("href")
            links &= f"step={number}&" in href and page.evaluate("window.practicePC.STEPS[window.practicePC.step()].id") in unquote(href)
            if number == 3:
                page.screenshot(path=str(shots / "practice-stuck-open.png"))
            page.reload()
            page.wait_for_function("(n) => window.practicePC?.step() === n - 1", arg=number)
        open_step(5)
        page.get_by_role("button", name="What can you do?", exact=True).click()
        # Remove the explicit step without navigating, so reload tests browser persistence.
        page.evaluate("history.replaceState(null, '', location.pathname + '?watch=0')")
        page.reload()
        page.wait_for_function("() => window.practicePC?.step() === 5")
        page.add_init_script("""Object.defineProperty(window, 'localStorage', {
            get() { throw new DOMException('Storage blocked', 'SecurityError'); }
        });""")
        for number in range(1, 18):
            open_step(number)
        page.set_viewport_size({"width":390, "height":844})
        open_step(3)
        page.screenshot(path=str(shots / "practice-390-step-3.png"), full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        return {"all_17_instructions_hints_fixes":True, "help_names_step":links,
                "reload_resumes":True, "links_1_to_17":True,
                "storage_blocked":True, "phone_no_horizontal_scroll":True}
    check("J53", self_serve)

    def keyboard_focus(selector):
        target = page.locator(selector).first
        for _ in range(120):
            if target.evaluate("e => e === document.activeElement"):
                break
            page.keyboard.press("Tab")
        assert target.evaluate("e => e === document.activeElement"), (
            "Tab cannot reach", selector, page.evaluate("document.activeElement.outerHTML"))
        assert target.evaluate("e => getComputedStyle(e).outlineStyle !== 'none'"), (
            "Focus is not visible", selector)

    def keyboard_activate(selector):
        keyboard_focus(selector)
        page.keyboard.press("Enter")

    def windows():
        for width, height in ((1366,768), (1536,864), (1920,1080)):
            page.set_viewport_size({"width":width, "height":height})
            for number in range(1,18):
                open_step(number)
                assert not re.search(r"\b(?:Mac|macOS|Command|Cmd)\b",
                                     page.locator("#practice-computer").inner_text(), re.I)
                assert page.evaluate("""() => {
                    if (document.documentElement.scrollWidth > innerWidth ||
                        document.documentElement.scrollHeight > innerHeight) return false;
                    const pc = document.querySelector('#pc').getBoundingClientRect();
                    return [...document.querySelectorAll('#coach button, #coach a, #coach summary, #pc button, #pc input, #pc [role="button"]')]
                      .filter(e => e.checkVisibility()).every(e => {
                        const r = e.getBoundingClientRect();
                        const container = e.closest('#pc') ? pc : {left:0,top:0,right:innerWidth,bottom:innerHeight};
                        return r.left >= container.left && r.top >= container.top &&
                            r.right <= container.right && r.bottom <= container.bottom;
                      });
                }"""), (width, height, number)
        page.set_viewport_size({"width":1366,"height":768})
        page.emulate_media(reduced_motion="reduce")
        open_step(1)
        keyboard_activate("#tb-start")
        keyboard_focus("#ssearch")
        page.keyboard.type("PowerShell"); page.keyboard.press("Enter")
        keyboard_activate("#c-acts [data-line]")
        keyboard_focus(".ps .in")
        page.keyboard.insert_text(page.evaluate("navigator.clipboard.readText()"))
        page.keyboard.press("Enter")
        page.locator("#ghcode").wait_for()
        keyboard_focus("#ghcode"); page.keyboard.type("A1B2-C3D4")
        keyboard_activate("#ghgo"); keyboard_activate("#ghauth")
        page.locator(".bs .starter-btn").first.wait_for()
        keyboard_activate(".bs .starter-btn:nth-child(1)")
        keyboard_focus(".bs form input")
        page.keyboard.type("Remember, my name is Alex and I prepare customer meetings.")
        page.keyboard.press("Enter")
        keyboard_activate("#bs-clear")
        keyboard_activate(".bs .starter-btn:nth-child(2)")
        keyboard_activate("#c-acts .pri")
        keyboard_activate("#bs-agents")
        keyboard_activate("#bs-export-agent")
        keyboard_activate("#bs-delete-agent")
        keyboard_activate("#bs-confirm-delete")
        keyboard_focus(".bs form input")
        page.keyboard.type("get my latest hacker news"); page.keyboard.press("Enter")
        keyboard_activate(".restore-helper")
        keyboard_focus(".bs form input")
        page.keyboard.type("get my latest hacker news"); page.keyboard.press("Enter")
        keyboard_activate("#bs-book")
        keyboard_focus("#bs-library-search"); page.keyboard.type("meeting prep")
        keyboard_activate("#bs-add-meeting")
        keyboard_focus(".bs form input")
        page.keyboard.type("Learn a new agent called QuoteOfTheDay that gives me an inspiring quote when I ask for motivation.")
        page.keyboard.press("Enter")
        keyboard_activate(".bs .starter-btn:nth-child(3)")
        assert page.evaluate("window.practicePC.step()") == 17, (
            "Keyboard journey stopped at", page.evaluate("window.practicePC.step()"))
        return {"windows_words":True, "three_sizes_all_17_fit":True,
                "keyboard_all_17":True, "visible_focus":True}
    check("J54", windows)

    def host_sheet():
        errors.clear()
        open_step(1)
        page.get_by_text("Hosting a session?", exact=True).click()
        page.get_by_role("link", name="Open the printable 20-minute host sheet.").click()
        page.wait_for_url("**/docs/practice/session.html")
        page.screenshot(path=str(shots / "session-screen.png"), full_page=True)
        assert not missing_links(page.locator("a[href]").evaluate_all(
            "es => es.map(e => e.href)"), page.url, ROOT)
        page.emulate_media(media="print")
        page.screenshot(path=str(shots / "session-print.png"), full_page=True)
        pdf = page.pdf(path=str(shots / "session-print.pdf"), prefer_css_page_size=True)
        pages = len(re.findall(rb"/Type\s*/Page\b", pdf))
        return {"linked_and_loads":True, "console_clean":not errors,
                "one_print_page":pages == 1,
                "timeline_and_next_steps":all(text in page.locator("body").inner_text()
                    for text in ("0-2", "2-4", "4-16", "16-20", "9-17", "AIdeate"))}
    check("J55", host_sheet)
    context.close()
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", action="store_true", help="Exit 1 for any failed check")
    args = parser.parse_args(argv)
    flags = []
    blocked = set()
    checks = []
    try:
        from playwright.sync_api import sync_playwright

        with local_site(ROOT) as base, sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                checks = measure(browser, base, flags, blocked)
                checks.extend(measure_attack(browser, base, blocked))
                checks.extend(measure_attack2(browser, base, blocked))
                checks.extend(measure_attack3(browser, base, blocked))
                checks.extend(measure_stage(browser, base, blocked))
                checks.extend(measure_aideate(browser, base, blocked))
                checks.extend(measure_polish(browser, base, blocked))
                checks.extend(measure_fullscreen_stage(browser, base))
                checks.extend(measure_two_journeys(browser, base))
                checks.extend(measure_session(browser, base))
            finally:
                browser.close()
    except Exception as exc:
        # A failed measurement must remain an explicit failure, never a green default.
        flags.append(f"Measurement error: {type(exc).__name__}: {exc}")
        measured = {check["id"] for check in checks}
        checks.extend(
            result(check_id, None, False, error="measurement incomplete")
            for check_id, _, _ in SPECS if check_id not in measured
        )
    report = {
        "checks": checks, "flags": flags, "blocked_external_requests": sorted(blocked),
        "blocked_external_info": sorted(
            url for url in blocked if blocked_external_https(url, base)
        ) if blocked else [],
        "viewport": {"desktop": [1440, 900], "phone": [390, 844]},
    }
    print(json.dumps(report, sort_keys=True))
    print("\nID   Check                           Value             Target      Pass")
    for check in checks:
        value = check["value"]
        display = json.dumps(value, separators=(",", ":"))
        if check["id"] == "J10" and isinstance(value, dict):
            display = (
                f'normal:{value["advances"]} reduced:{value["reduced_motion_advances"]}'
            )
        elif isinstance(value, dict) and all(
            isinstance(v, bool) or v is None for v in value.values()
        ):
            display = f"{sum(v is True for v in value.values())}/{len(value)} true"
        elif isinstance(value, dict):
            display = "see JSON"
        if len(display) > 18 and check["id"] != "J10":
            display = display[:15] + "..."
        print(
            f'{check["id"]:<4} {check["name"]:<31} {display:<18} '
            f'{check["target"]:<11} {"PASS" if check["pass"] else "FAIL"}'
        )
    return exit_code(checks, args.gate)


if __name__ == "__main__":
    raise SystemExit(main())
