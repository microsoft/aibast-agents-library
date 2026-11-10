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
    ("J17", "phone_copy_first_screen + end_card_one_primary", "all true"),
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
    ("J37", "watch_mode_plays", "A first; skip <= 25s; full <= 150s"),
    ("J38", "try_mode_completes", "12 highlighted steps"),
    ("J39", "practice_page_unchanged", "8 original steps"),
    ("J40", "stage_phone_readable", ">= 11px"),
    ("J41", "reduced_motion_stage", "waits 6s"),
    ("J42", "aideate_page", "all true"),
    ("J43", "aideate_reachable", "all true"),
    ("J44", "polish_r5", "all true"),
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
        const firstDetails = document.querySelector('details');
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
        return {exists:true, first_step:steps[0]?.innerText || '',
            what_you_need:document.querySelectorAll('[data-what-you-need]').length,
            commands:unique.length, text:text(false,true,unique.length === 1 ? unique[0] : null)};
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
    values = {"phone_copy_first_screen": bool(copy_inside), "end_card_one_primary": len(primary) == 1}
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
    names["h1"] = page.locator("h1").inner_text() == "Get an agent running"
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


# Visible coach text recorded from fork/staging:docs/practice/windows.html.
PRACTICE_TEXTS = (
    "Press Start: the four blue squares in the middle of the bar at the bottom of the screen.",
    "Type PowerShell. When Windows PowerShell shows up as the best match, press Enter.",
    "Copy the one line, then right-click inside the blue PowerShell window to paste it. Press Enter.",
    "It is installing. When the sign-in page opens, type the code shown in PowerShell (the line that says Your code), press Continue, then Authorize.",
    "Your Brainstem opened in Edge at localhost:7071. Say hello to it: type anything in the box at the bottom and press Send.",
    "Look around the library. In Edge, click the address bar, type microsoft.github.io/aibast-agents-library and press Enter. Browse the solutions, then come back here.",
    "Now the editor. Press Start, type Visual Studio Code, press Enter.",
    "In the Chat panel on the right, paste this line and press Enter. Then watch: Copilot finds your Brainstem, adds its folder on the left and opens it in the middle.",
)


def practice_clickthrough(page, shots=None):
    """Exercise the original eight steps with browser input, not engine calls."""
    texts = []
    for step in range(8):
        page.wait_for_function("(n) => window.practicePC?.step() === n", arg=step)
        texts.append(page.locator("#c-say").inner_text())
        if step == 3:
            page.locator("#ghcode").wait_for()
        if step == 4:
            page.locator(".edge .bs input").wait_for()
        if shots:
            page.wait_for_timeout(200)
            page.screenshot(path=str(shots / f"practice-{step + 1}.png"),
                            animations="disabled", mask=[page.locator("#tray .clock")])
        page.get_by_role("button", name="Show me where", exact=True).click()
        if step == 0:
            page.locator("#tb-start").click()
        elif step == 1:
            page.locator("#ssearch").fill("PowerShell")
            page.locator("#ssearch").press("Enter")
        elif step == 2:
            page.get_by_role("button", name="Copy the line", exact=True).click()
            page.locator(".ps .body").click()
            page.keyboard.insert_text(
                "irm https://microsoft.github.io/aibast-agents-library/install.ps1 | iex"
            )
            if shots:
                page.screenshot(path=str(shots / "practice-terminal-pasted.png"),
                                animations="disabled", mask=[page.locator("#tray .clock")])
            page.keyboard.press("Enter")
        elif step == 3:
            page.locator("#ghcode").fill("A1B2-C3D4")
            page.locator("#ghgo").click()
            page.locator("#ghauth").click()
        elif step == 4:
            page.locator(".edge .bs input").fill("Hello")
            page.locator(".edge .bs input").press("Enter")
        elif step == 5:
            page.locator("#eurl").fill("microsoft.github.io/aibast-agents-library")
            page.locator("#eurl").press("Enter")
        elif step == 6:
            page.locator("#tb-start").click()
            page.locator("#ssearch").fill("Visual Studio Code")
            page.locator("#ssearch").press("Enter")
        else:
            page.get_by_role("button", name="Copy the line", exact=True).click()
            page.locator(".vsc textarea").fill(
                "Go and read https://microsoft.github.io/aibast-agents-library/docs/start/skill.md and set up my Brainstem for me."
            )
            page.locator(".vsc textarea").press("Enter")
    page.wait_for_function("() => window.practicePC.step() === 8")
    return texts


def highlighted_clickthrough(page):
    """Use only the coach's current highlighted target for every desktop action."""
    visited = set()
    for _ in range(300):
        if page.locator("#c-n").inner_text() == "Done":
            return sorted(visited)
        page.get_by_role("button", name="Show me where", exact=True).click()
        hint = page.locator("#hint")
        selector = hint.get_attribute("data-target")
        if not selector:
            page.wait_for_timeout(250)
            continue
        target = page.locator(selector)
        if not target.count() or not target.first.is_visible():
            page.wait_for_timeout(250)
            continue
        target = target.first
        assert hint.is_visible(), f"Target {selector} has no visible highlight"
        assert boxes_intersect(hint.bounding_box(), target.bounding_box())
        visited.add(int(re.search(r"Step (\d+)", page.locator("#c-n").inner_text())[1]))
        if selector == "#ssearch":
            target.fill("PowerShell" if 2 in visited and 7 not in visited else "Visual Studio Code")
        elif selector == ".ps .in":
            if not target.inner_text():
                target.fill(page.locator("#c-acts [data-line]").get_attribute("data-line"))
            else:
                target.press("Enter")
        elif selector == "#ghcode":
            target.fill(re.search(r"Your code: ([A-Z0-9-]+)", page.locator(".ps .out").inner_text())[1])
        elif selector == ".edge .bs input":
            target.fill("Hello")
        elif selector == "#eurl":
            target.fill("microsoft.github.io/aibast-agents-library")
            target.press("Enter")
        elif selector == ".vsc textarea":
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
                 "start_visible": page.locator("#tb-start").is_visible(),
                 "taskbar_visible": page.locator("#taskbar").is_visible()}
        practice.close()
        return value, width >= 1440 * .55 and len(engines) == 1 and all(
            value[k] for k in ("start_visible", "taskbar_visible"))
    check("J36", desktop)

    def watch():
        load(page, base + "start.html")
        first = page.locator("#c-n").inner_text() == "Step 1 of 12"
        page.get_by_role("button", name="Skip to my agent", exact=True).click()
        page.wait_for_function("() => document.querySelector('#studio-question')?.textContent"
                              " === document.querySelector('#sample-question')?.textContent", timeout=25000)
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
        return {"starts_at_A1": first, "skip_reaches_studio": skipped, "full_run": full}, first and skipped and full
    check("J37", watch)

    def trying():
        load(page, base + "start.html")
        page.get_by_role("button", name="Try it yourself", exact=True).click()
        visited = highlighted_clickthrough(page)
        exact = (page.locator("#agent-pasted-line").inner_text() == page.locator("#setup-line").inner_text()
                 and page.locator("#studio-question").inner_text() == page.locator("#sample-question").inner_text())
        return {"visited": visited, "exact_agent_setup": exact}, visited == list(range(1, 13)) and exact
    check("J38", trying)

    def original():
        load(page, base + "docs/practice/windows.html")
        texts = practice_clickthrough(page, shots / "after" if (shots / "after").is_dir() else None)
        shared = page.locator('script[src$="/practice/desktop.js"]').count() == 1
        value = {"steps": len(texts), "original_texts": texts == list(PRACTICE_TEXTS),
                 "uses_extracted_engine": shared}
        return value, all((len(texts) == 8, value["original_texts"], shared))
    check("J39", original)

    def phone():
        first = {}
        for width, height in ((390, 844), (360, 640)):
            page.set_viewport_size({"width": width, "height": height})
            load(page, base + "start.html")
            if not page.locator("#pc").count():
                return None, False
            page.evaluate("window.scrollTo(0, 0)")
            first[str(width)] = page.locator("#copy").evaluate("e => {" + DOM + "return inside(e);}")
            page.screenshot(path=str(shots / f"start-{width}x{height}-first.png"))
        page.set_viewport_size({"width": 390, "height": 844})
        page.emulate_media(reduced_motion="reduce")
        load(page, base + "start.html")
        page.get_by_role("button", name="Skip to my agent", exact=True).click()
        sizes = []
        for number in range(9, 13):
            page.locator("#pc").scroll_into_view_if_needed()
            sizes.extend(stage_font_sizes(page))
            if number == 10:
                page.screenshot(path=str(shots / "start-390x844-stage-code.png"))
            page.get_by_role("button", name="Next step", exact=True).click()
            page.wait_for_function("(n) => window.practicePC.step() === n", arg=number)
        page.locator("#pc").scroll_into_view_if_needed()
        sizes.extend(stage_font_sizes(page))
        page.screenshot(path=str(shots / "start-390x844-stage.png"))
        return {"minimum_px": min(sizes) if sizes else None, "copy_first": first}, bool(
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
        page.get_by_role("button", name="Next step", exact=True).click()
        page.wait_for_function("() => document.querySelector('#c-n').textContent !== 'Step 1 of 12'")
        return {"waits": waits, "click_advances": True}, waits
    check("J41", reduced)
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
