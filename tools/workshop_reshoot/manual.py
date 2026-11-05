"""Hard-mode workshop capture: build the solution's manual agent by hand in the real Copilot Studio UI, exactly as the
workshop teaches, one frame per step, then every locked case in Preview (full-conversation frames), then the Draft
check. Never publishes.

    python manual.py <repo> <slug>

Frames -> solutions/<slug>/screenshots/manual/ (old frames removed); run record -> ~/.cache/aibast-reshoot/out/<slug>/manual.json
"""
import asyncio, json, re, sys
from datetime import datetime, timezone

import markdown
from playwright.async_api import async_playwright

import reshoot_lib as L

P = L.Package(sys.argv[1], sys.argv[2])
FRAMES = P.pkg / "screenshots" / "manual"


async def main():
    L.retire({P.manual_name, f"{P.deployment['display_name']} Manual"[:30]})
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*.jpg"):
        old.unlink()
    async with async_playwright() as p:
        page = await L.open_page(p)
        s = L.Shooter(page, FRAMES)
        try:
            for attempt in range(1, 5):
                try:
                    await page.goto(L.STUDIO + "/home", wait_until="domcontentloaded")
                    await page.wait_for_timeout(15000)
                    await s.dismiss()
                    await page.locator("button", has_text="Create an agent to take actions").click()
                    await page.get_by_role("textbox", name="Name your agent").wait_for(timeout=60000)
                    break
                except Exception:
                    if attempt == 4:
                        raise
                    print(f"[retry] Studio could not start a new agent (attempt {attempt})", flush=True)
                    await page.wait_for_timeout(15000 * attempt)
            await page.wait_for_timeout(4000)
            await s.frame("create-blank-agent", "Create a blank Copilot Studio agent", ["Untitled Agent", "Instructions"])

            name = page.get_by_role("textbox", name="Name your agent")
            await name.click(); await page.keyboard.press("Meta+A"); await page.keyboard.type(P.manual_name, delay=25)
            await page.keyboard.press("Enter"); await page.wait_for_timeout(1500)
            await s.frame("name-agent", f"Name {P.manual_name}", [P.manual_name])

            text = (P.pkg / "manual" / "GLOBAL-INSTRUCTIONS.md").read_text()
            ed = page.locator("[contenteditable=true]").first
            await ed.click()
            await page.evaluate("""([t,h]) => { const dt = new DataTransfer(); dt.setData("text/plain", t);
                dt.setData("text/html", h); document.activeElement.dispatchEvent(new ClipboardEvent("paste",
                {clipboardData: dt, bubbles: true, cancelable: true})); }""", [text, markdown.markdown(text)])
            await page.wait_for_timeout(2000)
            await page.mouse.move(400, 520)
            for _ in range(12):
                await page.mouse.wheel(0, -4000); await page.wait_for_timeout(120)
            await ed.evaluate("e => { let n = e; while (n) { if (n.scrollHeight > n.clientHeight + 4) n.scrollTop = 0; n = n.parentElement; } }")
            await page.wait_for_timeout(800)
            await s.frame("enter-instructions", "Enter the reviewed global instructions", [text.splitlines()[0].lstrip("# ").strip()])

            await page.get_by_role("button", name="Save", exact=True).click()
            await page.get_by_text("Your agent has been saved").wait_for(timeout=60000)
            await s.frame("save-instructions", "Save the instruction policy", ["Your agent has been saved", "Draft"], keep_toast=True)

            await s.dismiss()
            web = page.get_by_role("button", name="Remove Search all websites")
            if await web.count():
                await web.hover(); await web.click(); await page.wait_for_timeout(2000)
            web_removed = not await page.get_by_role("button", name="Remove Search all websites").count()
            await s.frame("remove-web-search", "Remove default web search", ["Provide trusted context to guide decisions"])

            for kf in P.knowledge:
                await s.dismiss()
                await page.get_by_role("button", name="Add knowledge").click(); await page.wait_for_timeout(2500)
                await page.get_by_label("File upload").set_input_files(str(kf))
                await page.get_by_role("button", name="Add to agent").wait_for(timeout=60000)
                await page.wait_for_timeout(3000)
                await page.get_by_role("button", name="Add to agent").click()
                await page.get_by_role("button", name=f"Remove {kf.name}").wait_for(timeout=120000)
                await s.frame(f"add-{kf.stem.replace('_', '-')}", f"Add knowledge: {kf.name}", [kf.name])

            for sk in P.skills:
                await s.dismiss()
                skill = P.skill_name(sk)
                await page.get_by_role("button", name="Add skill").click(); await page.wait_for_timeout(2000)
                await page.get_by_label("Skill file picker. Accepted: .md, .zip").set_input_files(str(sk))
                try:
                    await page.get_by_role("button", name=f"Remove skill {skill}").wait_for(timeout=60000)
                except Exception:
                    await page.screenshot(path=str(P.out / f"skill-fail-{skill}.png"))
                    raise RuntimeError(f"skill {sk.parent.name} was not added (see skill-fail-{skill}.png)")
                await s.frame(f"add-{sk.parent.name.replace('_', '-')}", f"Add skill: {sk.parent.name}", [skill])

            save = page.get_by_role("button", name="Save", exact=True)
            if await save.count() and await save.is_enabled():
                await save.click(); await page.wait_for_timeout(5000)
            await s.dismiss()
            model = (await page.evaluate("() => { const e = document.querySelector('[aria-label*=\"model\" i]'); return e ? e.innerText : '' }")).strip() or "Default model"
            more = page.locator("button", has_text=re.compile(r"^\+\d+$"))
            hidden = int((await more.first.inner_text()).strip("+")) if await more.count() else 0
            skills_on = await page.locator("button[aria-label^='Remove skill ']").count() + hidden
            knowledge_on = sum([await page.get_by_role("button", name=f"Remove {k.name}").count() for k in P.knowledge])
            names = P.skill_names()
            await s.frame("review-inventory", "Review model, skills, knowledge, and safety boundaries",
                          [model] + [k.name for k in P.knowledge] + names)
            if hidden:
                await more.first.click(); await page.wait_for_timeout(1500)
                await s.frame("review-skills", f"Review the skill list ({len(names)} skills)", names)
                if len(names) > 4:
                    await page.mouse.move(1210, 420)
                    for _ in range(6):
                        await page.mouse.wheel(0, 600); await page.wait_for_timeout(150)
                    await page.wait_for_timeout(800)
                    await s.frame("review-skills-more", "Review the rest of the skill list", names)
                back = page.get_by_text("Back", exact=True)
                if await back.count():
                    await back.first.click(); await page.wait_for_timeout(800)
            for _ in range(2):
                await page.keyboard.press("Escape"); await page.wait_for_timeout(300)

            await page.locator("button", has_text="Preview").first.click(); await page.wait_for_timeout(8000)
            nc = page.get_by_role("button", name="New chat")
            if await nc.count():
                await nc.click(); await page.wait_for_timeout(3000)
            await s.frame("open-preview", "Open a fresh Preview conversation", ["New chat", P.manual_name])

            results = [await L.run_case(page, s, c) for c in P.cases]
            bot_id = re.search(r"/agents/([0-9a-f-]{36})", page.url)
            await L.confirm_draft(page, s, P.manual_name)
        except Exception:
            await page.screenshot(path=str(P.out / "manual-error.png"), scale="css")
            raise
        finally:
            await page.close()
    rec = {"slug": P.slug, "display_name": P.manual_name, "bot_id": bot_id.group(1) if bot_id else None, "model": model,
           "captured_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "web_search_removed": web_removed,
           "knowledge_confirmed": knowledge_on, "knowledge_expected": len(P.knowledge),
           "skills_confirmed": skills_on, "skills_expected": len(P.skills), "frames": s.frames, "cases": results}
    (P.out / "manual.json").write_text(json.dumps(rec, indent=1))
    print(f"[done] {P.manual_name}: {sum(r['passed'] for r in results)}/{len(results)} cases, {len(s.frames)} frames, "
          f"skills {skills_on}/{len(P.skills)}, knowledge {knowledge_on}/{len(P.knowledge)}", flush=True)


if __name__ == "__main__":
    if not L.claim(P.out / "m"):
        sys.exit(3)
    try:
        asyncio.run(main())
    finally:
        L.release(P.out / "m")
