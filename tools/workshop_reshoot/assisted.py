"""Easy-mode workshop capture: push the reviewed package as a Copilot Studio Draft with the library's own
tools/promote_solution_draft.py (pac, Copilot-assisted path) onto the solution's Pilot agent (updated in place when it
exists), then capture the real Studio UI: the build, every locked case in Preview, and the Draft check. Never publishes.

    python assisted.py <repo> <slug>

Frames -> solutions/<slug>/screenshots/assisted/; run record -> ~/.cache/aibast-reshoot/out/<slug>/assisted.json
"""
import asyncio, json, re, subprocess, sys, time
from datetime import datetime, timezone

from playwright.async_api import async_playwright

import reshoot_lib as L

P = L.Package(sys.argv[1], sys.argv[2])
FRAMES = P.pkg / "screenshots" / "assisted"
ORG = L.ORG + "/"


def _clone(bot_id, project):
    last = ""
    for _ in range(3):
        subprocess.run(["rm", "-rf", str(P.out / "clone")], check=False)
        c = subprocess.run(["pac", "copilot", "clone", "--bot", bot_id, "--environment", ORG, "--output-dir", str(P.out / "clone")],
                           capture_output=True, text=True, timeout=900)
        cloned = [x.parent for x in (P.out / "clone").rglob("settings.mcs.yml")] if (P.out / "clone").exists() else []
        if not c.returncode and cloned:
            subprocess.run(["mv", str(cloned[0]), str(project)], check=True)
            subprocess.run(["rm", "-rf", str(P.out / "clone")], check=True)
            return
        last = (c.stdout + c.stderr)[-1500:]
    raise RuntimeError(f"pac copilot clone failed:\n{last}")


def promote():
    project = P.out / "assisted-project"
    bot_id = P.pilot.get("bot_id")
    for attempt in range(4):
        if attempt:
            time.sleep(30 * attempt)       # pac crashes and sync conflicts are transient under load
        settings = project / "settings.mcs.yml"
        if not bot_id and settings.exists():
            # a previous attempt created the agent (init) but the push failed: re-attach to it by schema name
            sm = re.search(r"^schemaName:\s*(\S+)", settings.read_text(), re.M)
            if sm:
                hit = L.dv("GET", "bots?$select=botid&$filter=" + urllib_quote(f"schemaname eq '{sm.group(1)}'")).get("value", [])
                bot_id = hit[0]["botid"] if hit else None
        subprocess.run(["rm", "-rf", str(project)], check=False)
        update = []
        if bot_id:
            _clone(bot_id, project)
            update = ["--update-existing", "--rename-existing"]
        cmd = ["python3", "tools/promote_solution_draft.py", P.slug, "--project-dir", str(project),
               "--environment", ORG, "--push"] + update
        if P.pilot.get("display_name"):
            cmd += ["--display-name", P.pilot["display_name"]]
        r = subprocess.run(cmd, cwd=P.repo, capture_output=True, text=True, timeout=1200)
        (P.out / "promote.log").write_text(r.stdout + r.stderr)
        if not r.returncode:
            return json.loads(r.stdout[r.stdout.index("{"):])
        m = re.search(r"already exists \(ID: ([0-9a-f-]{36})\)", r.stdout + r.stderr)
        if m and not bot_id:
            bot_id = m.group(1)
        print(f"[retry] promote attempt {attempt + 1} failed: {(r.stdout + r.stderr).strip().splitlines()[-1][:160]}", flush=True)
        last = (r.stdout + r.stderr)[-2000:]
    raise RuntimeError(f"promote failed after retries:\n{last}")


async def main():
    res = promote()
    name = res["display_name"]
    q = urllib_quote(f"schemaname eq '{res['schema_name']}'")
    bot = L.dv("GET", f"bots?$select=botid,name,schemaname&$filter={q}")["value"][0]
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*.jpg"):
        old.unlink()
    async with async_playwright() as p:
        page = await L.open_page(p)
        s = L.Shooter(page, FRAMES)
        try:
            await page.goto(f"{L.STUDIO}/agents/{bot['botid']}", wait_until="domcontentloaded")
            await page.wait_for_timeout(15000)
            await s.dismiss()
            await s.frame("review-build", "Review the Copilot-assisted Draft configuration",
                          [name, "Draft"] + [k.name for k in P.knowledge] + P.skill_names())
            await page.locator("button", has_text="Preview").first.click(); await page.wait_for_timeout(8000)
            results = [await L.run_case(page, s, c) for c in P.cases]
            await L.confirm_draft(page, s, name)
        except Exception:
            await page.screenshot(path=str(P.out / "assisted-error.png"), scale="css")
            raise
        finally:
            await page.close()
    rec = {"slug": P.slug, "display_name": name, "schema_name": res["schema_name"], "bot_id": bot["botid"],
           "push_output": res.get("push_output"), "captured_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
           "frames": s.frames, "cases": results}
    (P.out / "assisted.json").write_text(json.dumps(rec, indent=1))
    print(f"[done] {name}: {sum(r['passed'] for r in results)}/{len(results)} cases, {len(s.frames)} frames", flush=True)


def urllib_quote(t):
    import urllib.parse
    return urllib.parse.quote(t)


if __name__ == "__main__":
    if not L.claim(P.out / "a"):
        sys.exit(3)
    try:
        asyncio.run(main())
    finally:
        L.release(P.out / "a")
