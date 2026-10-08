"""Rebuild a solution's run records (~/.cache/aibast-reshoot/out/<slug>/{manual,assisted}.json) from the re-shoot
evidence already written into the package (browserfilm manifests, manual/preview evidence, case files), so boxes can be
re-placed and flagged frames retaken without a full rebuild. Only modes whose every frame exists on disk are recovered.

    python recover.py <repo> <slug>
"""
import json, re, sys

import reshoot_lib as L

P = L.Package(sys.argv[1], sys.argv[2])


def load(p):
    return json.loads(p.read_text()) if p.exists() else {}


def step_anchors(fid, name, model):
    know = [k.name for k in P.knowledge]
    skills = P.skill_names()
    stems = {f"add-{k.stem.replace('_', '-')}": k.name for k in P.knowledge}
    dirs = {f"add-{s.parent.name.replace('_', '-')}": P.skill_name(s) for s in P.skills}
    if fid == "create-blank-agent":
        return ["Untitled Agent", "Instructions"]
    if fid == "name-agent":
        return [name]
    if fid == "enter-instructions":
        return [(P.pkg / "manual" / "GLOBAL-INSTRUCTIONS.md").read_text().splitlines()[0].lstrip("# ").strip()]
    if fid == "save-instructions":
        return ["Your agent has been saved", "Draft"]
    if fid == "remove-web-search":
        return ["Provide trusted context to guide decisions"]
    if fid in stems:
        return [stems[fid]]
    if fid in dirs:
        return [dirs[fid]]
    if fid == "review-inventory":
        return [model] + know + skills
    if fid.startswith("review-skills"):
        return skills
    if fid == "open-preview":
        return ["New chat", name]
    if fid == "review-build":
        return [name, "Draft"] + know + skills
    if fid == "confirm-draft":
        return [name, "Draft"]
    return []


def frames_from(sub):
    film = load(P.pkg / "screenshots" / sub / "browserfilm.json")
    frames = []
    for f in film.get("frames", []):
        if not (P.pkg / "screenshots" / sub / f["file"]).exists():
            return None
        frames.append({"file": f["file"], "label": re.sub(r"^\d+ · ", "", f["label"])})
    return frames or None


def recover_manual():
    ev = load(P.pkg / "evals" / "manual-build-evidence.json")
    frames = frames_from("manual")
    if not frames or not ev.get("canonical_preview"):
        return False
    name, model = ev["manual_agent"]["display_name"], ev.get("target_model") or "Claude Opus 5"
    by_shot = {c["expected_screenshot"]: c for c in ev["canonical_preview"]}
    for f in frames:
        c = by_shot.get(f["file"])
        f["anchors"] = (P.case(c["case_id"]) or c)["must_include"] if c else step_anchors(f["file"][3:-4], name, model)
    mc = ev.get("manual_components", {})
    rec = {"slug": P.slug, "display_name": name, "bot_id": ev["manual_agent"].get("bot_id"), "model": model,
           "captured_at": ev.get("captured_at"), "web_search_removed": (mc.get("web_search_removed") or {}).get("confirmed", True),
           "knowledge_confirmed": (mc.get("knowledge_files") or {}).get("confirmed", len(P.knowledge)),
           "knowledge_expected": len(P.knowledge),
           "skills_confirmed": (mc.get("skills") or {}).get("confirmed", len(P.skills)), "skills_expected": len(P.skills),
           "frames": frames,
           "cases": [dict(c, persona=(P.case(c["case_id"]) or {}).get("persona")) for c in ev["canonical_preview"]]}
    (P.out / "manual.json").write_text(json.dumps(rec, indent=1))
    return True


def recover_assisted():
    ev = load(P.pkg / "evals" / "copilot-studio-preview-evidence.json")
    frames = frames_from("assisted")
    if not frames or not ev.get("cases") or not ev.get("bot_id"):
        return False
    name = ev["display_name"]
    files = {f["file"][3:-4]: f["file"] for f in frames}
    cases = []
    for c in ev["cases"]:
        shot = files.get(c["case_id"].lower())
        if not shot:
            return False
        lc = P.case(c["case_id"]) or {}
        cases.append(dict(c, persona=lc.get("persona"), prompt=lc.get("prompt", ""), expected_screenshot=shot))
    by_shot = {c["expected_screenshot"]: c for c in cases}
    for f in frames:
        c = by_shot.get(f["file"])
        f["anchors"] = c["must_include"] if c else step_anchors(f["file"][3:-4], name, ev.get("model") or "")
    rec = {"slug": P.slug, "display_name": name, "schema_name": ev.get("schema_name"), "bot_id": ev["bot_id"],
           "push_output": ev.get("push_result"), "captured_at": ev.get("captured_at"), "frames": frames, "cases": cases}
    (P.out / "assisted.json").write_text(json.dumps(rec, indent=1))
    return True


if __name__ == "__main__":
    m, a = recover_manual(), recover_assisted()
    print(f"{P.slug}: manual {'recovered' if m else 'needs capture'}, assisted {'recovered' if a else 'needs capture'}")
