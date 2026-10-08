"""Targeted retakes: recapture only the frames evidence.py marked reshoot_required, on the agent already built (manual or
Copilot-assisted), replacing the frame file and its record. Handles locked-case frames (fresh Preview chat, retried),
open-preview, confirm-draft and review frames; build-step frames are reported (they need a rebuild).

    python retake.py <repo> <slug> [--tries 3]      then: python evidence.py <repo> <slug>
"""
import asyncio, json, sys
from pathlib import Path

from playwright.async_api import async_playwright

import reshoot_lib as L

P = L.Package(sys.argv[1], sys.argv[2])
TRIES = int(sys.argv[sys.argv.index("--tries") + 1]) if "--tries" in sys.argv else 3


async def retake(page, run, sub, items):
    left = []
    by_file = {f["file"]: i for i, f in enumerate(run["frames"])}
    url = f"{L.STUDIO}/agents/{run['bot_id']}"
    for item in items:
        fname = Path(item["source"]).name
        idx = by_file.get(fname)
        if idx is None:
            left.append(fname); continue
        fid = fname[3:-4]
        s = L.Shooter(page, P.pkg / "screenshots" / sub, start=idx)
        case = P.case(item.get("case_id")) if item.get("case_id") else None
        if case:
            await page.goto(url + "/preview", wait_until="domcontentloaded"); await page.wait_for_timeout(12000)
            await s.dismiss()
            rec = await L.run_case(page, s, case, tries=TRIES)
            run["cases"] = [rec if c["case_id"] == rec["case_id"] else c for c in run["cases"]]
        elif fid == "open-preview":
            await page.goto(url + "/preview", wait_until="domcontentloaded"); await page.wait_for_timeout(12000)
            await s.dismiss()
            nc = page.get_by_role("button", name="New chat")
            if await nc.count():
                await nc.click(); await page.wait_for_timeout(3000)
            await s.frame("open-preview", "Open a fresh Preview conversation", ["New chat", run["display_name"]])
        elif fid == "confirm-draft":
            await L.confirm_draft(page, s, run["display_name"])
        elif fid in ("review-build", "review-inventory"):
            await page.goto(url, wait_until="domcontentloaded"); await page.wait_for_timeout(15000)
            await s.dismiss()
            await s.frame(fid, run["frames"][idx]["label"], run["frames"][idx].get("anchors", []))
        else:
            left.append(fname); continue
        new = s.frames[-1]
        if new["file"] != fname:
            (P.pkg / "screenshots" / sub / new["file"]).rename(P.pkg / "screenshots" / sub / fname)
            new["file"] = fname
            if case:
                run["cases"] = [dict(c, expected_screenshot=fname) if c["case_id"] == case["id"] else c for c in run["cases"]]
        run["frames"][idx] = new
        print(f"[retake] {sub} {fname}", flush=True)
    return left


async def main():
    cp = json.loads((P.pkg / "evals" / "visual-checkpoints.json").read_text())
    todo = [c for c in cp["captures"] if c["status"] == "reshoot_required"]
    if not todo:
        print(f"[ok] {P.slug}: nothing to retake"); return
    async with async_playwright() as p:
        page = await L.open_page(p)
        try:
            for mode, sub in (("hard", "manual"), ("easy", "assisted")):
                items = [c for c in todo if c["mode"] == mode]
                path = P.out / f"{sub}.json"
                if not items or not path.exists():
                    continue
                run = json.loads(path.read_text())
                left = await retake(page, run, sub, items)
                path.write_text(json.dumps(run, indent=1))
                if left:
                    print(f"[left] {P.slug} {sub}: needs a rebuild to retake: {left}", flush=True)
        finally:
            await page.close()


if __name__ == "__main__":
    asyncio.run(main())
