"""Shared pieces of the workshop re-shoot: the real Copilot Studio UI (kodyv8), driven over CDP from an authenticated
Chrome, captured frame by frame with evidence boxes measured from the page.

Environment: a Chrome with remote debugging on 127.0.0.1:9333 signed in to the target environment; `az` signed in
(AZURE_CONFIG_DIR) for Dataverse reads; `pac` for the Copilot-assisted path. Run records go to
~/.cache/aibast-reshoot/out/<slug>/ (never a temp folder).
"""
import json, os, re, subprocess, time, urllib.parse, urllib.request
from pathlib import Path

ENV_ID = os.environ.get("RESHOOT_ENV_ID", "ee67a404-325c-e726-a18a-886fe708ca0b")
ORG = os.environ.get("RESHOOT_ORG", "https://org7dfbd855.crm.dynamics.com")
CDP = os.environ.get("RESHOOT_CDP", "http://127.0.0.1:9333")
VIEW = {"width": 1424, "height": 863}
CACHE = Path(os.environ.get("RESHOOT_CACHE", Path.home() / ".cache" / "aibast-reshoot"))
AZ = dict(os.environ, AZURE_CONFIG_DIR=os.environ.get("AZURE_CONFIG_DIR", str(Path.home() / ".azure-mcap")))
STUDIO = "https://copilotstudio.microsoft.com/environments/" + ENV_ID


class Package:
    """One solution package in a library checkout."""

    def __init__(self, repo, slug):
        self.repo, self.slug = Path(repo).expanduser().resolve(), slug
        self.pkg = self.repo / "solutions" / slug
        self.out = CACHE / "out" / slug
        self.out.mkdir(parents=True, exist_ok=True)
        self.deployment = json.loads((self.pkg / "deployment.json").read_text())
        self.cases = json.loads((self.repo / "tests" / "demo_cases" / f"{slug}.json").read_text())["cases"]
        self.knowledge = sorted(list((self.pkg / "manual" / "knowledge").glob("*.md"))
                                or list((self.pkg / "copilot-studio" / "capabilities" / "knowledge" / "files").glob("*.md")),
                                key=lambda p: ("synthetic-records" in p.name, p.name))
        self.skills = sorted((self.pkg / "manual" / "skills").glob("*/SKILL.md"), key=lambda p: p.parent.name)
        cs = self.deployment.get("copilot_studio", {})
        self.manual_name = (cs.get("validated_manual") or {}).get("display_name") or fit_name(self.deployment["display_name"])
        if len(self.manual_name) > 30:
            self.manual_name = fit_name(self.manual_name.replace(" Manual", ""))
        self.pilot = cs.get("validated_pilot") or {}

    def skill_name(self, path):
        m = re.search(r"^name:\s*(.+)$", path.read_text(), re.M)
        return m.group(1).strip().strip('"') if m else path.parent.name

    def skill_names(self):
        return [self.skill_name(p) for p in self.skills]

    def case(self, case_id):
        return next((c for c in self.cases if c["id"] == case_id), None)


def fit_name(base):
    """Studio agent names are limited to 30 characters: '<solution> Manual', dropping 'Agent' and trailing words."""
    base = base[:-6] if base.endswith(" Agent") else base
    words = base.split()
    while words and len(" ".join(words)) + 7 > 30:
        words.pop()
    return f"{' '.join(words)} Manual"


def dv(method, path, body=None):
    tok = subprocess.run(["az", "account", "get-access-token", "--resource", ORG, "--query", "accessToken", "-o", "tsv"],
                         capture_output=True, text=True, env=AZ, check=True).stdout.strip()
    req = urllib.request.Request(f"{ORG}/api/data/v9.2/{path}", method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return json.loads(data) if data.strip() else {}


def retire(names):
    """Rename older agents with these exact display names so the new build is the only match in search."""
    q = urllib.parse.quote(" or ".join(f"name eq '{n.replace(chr(39), chr(39) * 2)}'" for n in names))
    for b in dv("GET", f"bots?$select=botid,name&$filter={q}").get("value", []):
        new = f"zz retired workshop build {b['botid'][:8]}"
        dv("PATCH", f"bots({b['botid']})", {"name": new})
        print(f"renamed older agent {b['botid']} to '{new}'", flush=True)


def claim(out, lane=None):
    """One process per solution and mode: the first to claim owns it; a dead owner is taken over."""
    lane = lane or str(os.getpid())
    out.mkdir(parents=True, exist_ok=True)
    p = out / ".claim"
    try:
        fd = os.open(str(p), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, lane.encode()); os.close(fd)
        return True
    except FileExistsError:
        owner = p.read_text().strip()
        if owner == lane:
            return True
        try:
            os.kill(int(owner), 0)
            return False
        except (ProcessLookupError, ValueError):
            p.write_text(lane)
            return True


def release(out):
    try:
        (out / ".claim").unlink()
    except FileNotFoundError:
        pass


def judge(answer, case):
    """Machine gate on the rendered answer: every must_include present (markdown symbols ignored); no must_not_include
    present unless negated ('No message was sent' does not trip a ban on 'message was sent')."""
    def plain(t):
        return re.sub(r"\s+", " ", re.sub(r"[*_`]", "", t)).lower()
    low = plain(answer)
    missing = [v for v in case["must_include"] if plain(v) not in low]
    hits = []
    for v in case.get("must_not_include", []):
        for m in re.finditer(re.escape(plain(v)), low):
            if not re.search(r"\b(no|not|never)\s+$", low[max(0, m.start() - 6):m.start()]):
                hits.append(v)
                break
    return (not missing and not hits), missing, hits


class Shooter:
    """Takes numbered frames; records anchors and DOM-measured boxes (evidence.py re-places boxes from the image)."""

    def __init__(self, page, frames_dir, start=0):
        self.page, self.frames, self.n, self.frames_dir = page, [], start, frames_dir

    async def dismiss(self):
        for label in ("Dismiss save notification", "Dismiss announcement", "Got it"):
            b = self.page.get_by_role("button", name=label, exact=True)
            try:
                if await b.count() and await b.first.is_visible():
                    await b.first.click(timeout=2000)
                    await self.page.wait_for_timeout(400)
            except Exception:
                pass
        await self.page.mouse.move(2, 400)    # no hover tooltips in frames

    async def frame(self, fid, label, anchors=(), keep_toast=False):
        if not keep_toast:
            await self.dismiss()
        await self.page.wait_for_timeout(700)
        self.n += 1
        name = f"{self.n:02d}-{fid}.jpg"
        await self.page.screenshot(path=str(self.frames_dir / name), type="jpeg", quality=75, scale="css", timeout=90000)
        self.frames.append({"file": name, "label": label, "anchors": list(anchors)})
        print(f"[frame] {name}: {label}", flush=True)
        return name


async def wait_answer(page, before, prompt, timeout=300):
    t0, last, stable = time.time(), "", 0
    while time.time() - t0 < timeout:
        await page.wait_for_timeout(2500)
        done = await page.get_by_role("button", name="Copy message").count() > before
        busy = await page.locator("[aria-label*='Stop'], [aria-busy='true']").count()
        txt = (await page.locator("main").first.inner_text()).split(prompt)[-1]
        thinking = bool(re.search(r"\bThinking\s*$", txt.split("Ask a question")[0].strip()))
        if done and not busy and not thinking and txt == last and len(txt) > 200:
            stable += 1
            if stable >= 2:
                return txt
        else:
            stable = 0
        last = txt
    return last


async def run_case(page, s, case, tries=2):
    """Fresh Preview chat; type the locked prompt; wait; collapse the reasoning trace; grow the viewport to the whole
    conversation and frame it. Retried in a fresh chat when the machine gate fails."""
    for attempt in range(1, tries + 1):
        nc = page.get_by_role("button", name="New chat")
        if await nc.count():
            await nc.click(); await page.wait_for_timeout(3000)
        before, steady = -1, 0
        for _ in range(20):
            n = await page.get_by_role("button", name="Copy message").count()
            steady = steady + 1 if n == before else 0
            before = n
            if steady >= 2:
                break
            await page.wait_for_timeout(1000)
        await page.get_by_label("Chat message input").first.click()
        await page.keyboard.type(case["prompt"], delay=12)
        await page.keyboard.press("Enter")
        answer = await wait_answer(page, before, case["prompt"])
        ok, missing, banned = judge(answer, case)
        if not ok and attempt < tries:
            print(f"[case] {case['id']} retry (missing {missing} banned {banned})", flush=True)
            continue
        trace = page.get_by_text(re.compile(r"^(Thought for \d+ seconds?|Reasoned through)"), exact=False)
        try:
            if await trace.count():
                await trace.last.click(); await page.wait_for_timeout(1200)
        except Exception:
            pass
        extra = await page.evaluate("""() => { let best = null;
            for (const e of document.querySelectorAll('*')) {
              if (e.scrollHeight > e.clientHeight + 40 && e.clientHeight > 300 && /auto|scroll/.test(getComputedStyle(e).overflowY))
                if (!best || e.scrollHeight > best.scrollHeight) best = e; }
            return best ? best.scrollHeight - best.clientHeight : 0 }""")
        if extra > 0:
            await page.set_viewport_size({"width": VIEW["width"], "height": min(VIEW["height"] + extra + 40, 6000)})
            await page.wait_for_timeout(1500)
        await s.frame(case["id"].lower(), f"{'Pass' if ok else 'Check'} {case['id']}: {case.get('persona', '')}".rstrip(": "),
                      case["must_include"])
        await page.set_viewport_size(VIEW)
        await page.wait_for_timeout(800)
        print(f"[case] {case['id']} {'PASS' if ok else 'FAIL missing ' + str(missing) + ' banned ' + str(banned)}", flush=True)
        return {"case_id": case["id"], "persona": case.get("persona"), "prompt": case["prompt"],
                "must_include": case["must_include"], "must_not_include": case.get("must_not_include", []),
                "passed": ok, "missing": missing, "banned": banned, "attempts": attempt,
                "expected_screenshot": s.frames[-1]["file"], "answer": answer.strip()[:8000]}


async def confirm_draft(page, s, name):
    """Agents list filtered to the agent: its row shows Draft (nothing published). A crashed tab is replaced once."""
    try:
        await _confirm(page, s, name)
    except Exception as e:
        if "closed" not in str(e).lower():
            raise
        fresh = await page.context.new_page()
        await fresh.set_viewport_size(VIEW)
        s.page = fresh
        s.n -= 0 if not s.frames or "confirm-draft" not in s.frames[-1]["file"] else 1
        await _confirm(fresh, s, name)
        await fresh.close()


async def _confirm(page, s, name):
    await page.goto(STUDIO + "/agents", wait_until="domcontentloaded")
    await page.wait_for_timeout(12000)
    await s.dismiss()
    search = page.get_by_placeholder("Search by name")
    if await search.count():
        await search.fill(name); await page.wait_for_timeout(5000)
    await s.frame("confirm-draft", "Confirm Draft and stop before publish", [name, "Draft"])


async def open_page(p):
    b = await p.chromium.connect_over_cdp(CDP)
    page = await b.contexts[0].new_page()
    await page.set_viewport_size(VIEW)
    return page
