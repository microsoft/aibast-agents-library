#!/usr/bin/env python3
"""Build the AIBAST Agents Library static API (rapp-static-api/1.1).

One hand-authored input, api/manifest.json, plus the library's own generated files
(registry.json, solutions/catalog.json, solutions/_shared/demo-scenarios.json and each
solution's evals and exports) produce:

  llms.txt                          plain-words front door for AI agents
  api/registry.json                 schema-tagged index of every endpoint with its hash
  api/v1/index.json                 where to start, counts, endpoint list
  api/v1/search.json                one line per solution, for finding the right one
  api/v1/solutions/<slug>.json      one document per solution: what, try, get, learn, proof
  api/v1/scenarios/<id>.json        one demo question with its recorded answer
  api/v1/catalog/<name>.json         one document per agent.py, with its SHA-256
  api/v1/stacks.json                every stack and the agents in it
  api/v1/surfaces/<surface>.json    the demo surfaces the player can draw
  api/v1/status.json, badge.json    health and counts
  api/versions/<name>/<sha8>.json   content-addressed copies; never deleted or changed

Every link inside a document is a path relative to the site root, so the same files work on
any ring's Pages site. Only registry.json and llms.txt name the canonical Pages and raw bases;
the Pages build renders those two for the ring that serves them.

Usage: python tools/build_library_api.py [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "api"
MANIFEST = API / "manifest.json"
V1 = API / "v1"
VERSIONS = API / "versions"
LLMS = ROOT / "llms.txt"

SCHEMA_REGISTRY = "aibast-library-api/1.0"
SCHEMA_INDEX = "aibast-library-index/1.0"
SCHEMA_SEARCH = "aibast-library-search/1.0"
SCHEMA_SOLUTION = "aibast-library-solution/1.0"
SCHEMA_SCENARIO = "aibast-library-scenario/1.0"
SCHEMA_AGENT = "aibast-library-agent/1.0"
SCHEMA_STACKS = "aibast-library-stacks/1.0"
SCHEMA_SURFACE = "aibast-library-surface/1.0"
SCHEMA_STATUS = "aibast-library-api-status/1.0"
SCHEMA_ANSWER = "rapp-preview-answer/1"  # the answer shape aibast-rapp's preview already returns

SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class BuildError(Exception):
    pass


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def dump(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False) + "\n").encode("utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def agent_file_slug(name: str) -> str:
    return name.split("/", 1)[-1] if name.startswith("@") else name


def solution_docs(manifest, catalog, registry, scenarios, raw_base):
    """One npm-style document per solution."""
    by_name = {agent["name"]: agent for agent in registry["agents"]}
    stacks = {stack["stack"]: stack for stack in registry["stacks"]}
    deploy_agent = ROOT / manifest["deploy_agent"]
    deploy = {"path": manifest["deploy_agent"], "url": raw_base + manifest["deploy_agent"],
              "sha256": sha256_file(deploy_agent)}
    narration = manifest.get("narration", {})
    docs = {}
    for agent_id, entry in sorted(catalog.items()):
        agent = by_name.get(agent_id, {})
        sol = agent.get("_solution") or {}
        package = entry.get("package") or sol.get("package") or {}
        slug = package.get("slug")
        if not slug or not SLUG.match(slug):
            continue
        folder = ROOT / "solutions" / slug
        scenario_ids = scenarios["agents"].get(agent_id, {}).get("scenarios", [])
        tries = []
        for sid in scenario_ids:
            item = scenarios["scenarios"][sid]
            tries.append({"id": sid, "title": item["title"], "prompt": item["prompt"],
                          "recorded": item["recorded"],
                          "doc": f"api/v1/scenarios/{sid}.json" if item["recorded"] else None})
        first = next((t["id"] for t in tries if t["recorded"]), None)
        get = {"instructions": None, "prompt": None, "package": None, "settings": None,
               "deploy_agent": deploy, "undo": "Ask the AI that deployed it to remove it."}
        skill = folder / "SKILL.md"
        if skill.exists():
            get["instructions"] = {"path": rel(skill), "sha256": sha256_file(skill)}
            get["prompt"] = "Get {pages}" + rel(skill) + " and do it."
        export_meta = folder / "exports" / f"{slug}-solution-export.json"
        if export_meta.exists():
            meta = load(export_meta)
            zip_path = ROOT / meta["zip"]
            settings_path = ROOT / meta["deployment_settings"]
            if zip_path.exists():
                get["package"] = {"kind": "copilot-studio-solution", "path": meta["zip"],
                                  "url": raw_base + meta["zip"], "sha256": sha256_file(zip_path),
                                  "bytes": zip_path.stat().st_size,
                                  "unique_name": meta.get("solution_unique_name"),
                                  "managed": bool(meta.get("managed")), "published": False}
            if settings_path.exists():
                get["settings"] = {"path": meta["deployment_settings"],
                                   "url": raw_base + meta["deployment_settings"],
                                   "sha256": sha256_file(settings_path)}
        learn = {}
        for key, name in (("field_guide", "field-guide.html"), ("manual_tutorial", "manual-tutorial.html"),
                          ("workshop", "quest.html"), ("readme", "README.md"),
                          ("evidence_report", "evidence-report.html")):
            if (folder / name).exists():
                learn[key] = f"solutions/{slug}/{name}"
        transcripts = folder / "evals" / "transcripts.json"
        proof = {"readiness": agent.get("_readiness", []),
                 "transcripts": None, "evidence_report": learn.get("evidence_report")}
        if transcripts.exists():
            cases = load(transcripts).get("transcripts", [])
            proof["transcripts"] = {"path": rel(transcripts), "sha256": sha256_file(transcripts),
                                    "cases": len(cases), "passed": sum(1 for c in cases if c.get("passed"))}
        blocks = []
        stack_name = agent.get("_stack")
        stack = stacks.get(stack_name) if stack_name else None
        for member in (stack or {}).get("agents", [agent_id]):
            info = by_name.get(member)
            if info:
                blocks.append({"name": member, "file": info.get("_file"), "sha256": info.get("_sha256"),
                               "doc": f"api/v1/catalog/{agent_file_slug(member)}.json"})
        docs[slug] = {
            "schema": SCHEMA_SOLUTION,
            "slug": slug,
            "id": agent_id,
            "name": entry.get("display_name") or sol.get("advertised_name") or slug,
            "headline": entry.get("sales_headline") or sol.get("sales_headline"),
            "summary": entry.get("card_pitch") or sol.get("card_pitch"),
            "industries": sol.get("industries", []),
            "personas": sol.get("personas", []),
            "products": sol.get("featured_tools", []),
            "capabilities": sol.get("capabilities", []),
            "value": entry.get("business_value", []),
            "notice": {"synthetic_data": True, "text": manifest["notice"]},
            "try": {"page": f"{manifest['demo_page']}?scenario={first}" if first else None,
                    "surfaces": sorted(manifest["surfaces"]), "scenarios": tries,
                    "narration": narration_block(manifest, slug, [
                        ("intro", narration.get(slug, {}).get("intro"), "landing"),
                        ("outro", narration.get(slug, {}).get("outro"), "end")])},
            "get": get,
            "learn": learn,
            "proof": proof,
            "building_blocks": {"stack": stack_name, "agents": blocks},
        }
    return docs


def scenario_docs(manifest, scenarios, solutions_by_agent):
    docs = {}
    narration = manifest.get("narration", {})
    transcripts_cache = {}
    for sid, item in sorted(scenarios["scenarios"].items()):
        if not item["recorded"]:
            continue
        folder = item["folder"]
        if folder not in transcripts_cache:
            path = ROOT / "solutions" / folder / "evals" / "transcripts.json"
            transcripts_cache[folder] = {c["case_id"]: c for c in load(path).get("transcripts", [])} if path.exists() else {}
        case = transcripts_cache[folder].get(item["case_id"])
        if not case:
            raise BuildError(f"{sid}: case {item['case_id']} is missing from {folder}/evals/transcripts.json")
        slug = solutions_by_agent.get(item["agent_id"])
        name = scenarios["agents"].get(item["agent_id"], {}).get("name", "")
        lines = narration.get(slug or "", {}).get("steps", {}).get(sid, {})
        docs[sid] = {
            "schema": SCHEMA_SCENARIO,
            "id": sid,
            "solution": slug,
            "title": item["title"],
            "persona": case.get("persona"),
            "notice": manifest["notice"],
            "question": case["prompt"],
            "answer": {
                "schema": SCHEMA_ANSWER,
                "id": f"recorded-{sid}",
                "agent": {"id": item["agent_id"], "name": name},
                "question": case["prompt"],
                "lookups": [],
                "answer": case["assistant_response"],
                "shown": case["assistant_response"],
                "kind": "recorded",
                "citations": [],
                "basis": "recorded-sample",
            },
            "narration": narration_block(manifest, slug or "", [
                (f"{sid}.before", lines.get("before"), "ask"), (f"{sid}.after", lines.get("after"), "answer")]),
        }
    return docs


def agent_docs(registry):
    docs = {}
    for agent in sorted(registry["agents"], key=lambda a: a["name"]):
        slug = agent_file_slug(agent["name"])
        if not SLUG.match(slug.replace("_", "-")):
            continue
        docs[slug] = {
            "schema": SCHEMA_AGENT,
            "name": agent["name"],
            "display_name": agent.get("display_name"),
            "description": agent.get("description"),
            "version": agent.get("version"),
            "kind": agent.get("_catalog_kind"),
            "category": agent.get("category"),
            "tags": agent.get("tags", []),
            "dependencies": agent.get("dependencies", []),
            "stack": agent.get("_stack"),
            "synthetic_data": bool(agent.get("_synthetic_data")),
            "file": agent.get("_file"),
            "sha256": agent.get("_sha256"),
            "install_filename": agent.get("_install_filename"),
        }
    return docs


def stacks_doc(registry):
    return {"schema": SCHEMA_STACKS,
            "stacks": [{"stack": s["stack"], "vertical": s.get("vertical"), "display_name": s.get("display_name"),
                        "path": s.get("path"), "agents": s.get("agents", [])}
                       for s in sorted(registry["stacks"], key=lambda s: s["stack"])]}


NARRATION_MEDIA = "solutions/_shared/narration/media"


def narration_segment(manifest, slug, key, text, screen):
    """One clip in the Cowork demo narration shape: content-addressed wav plus timed captions."""
    block = manifest.get("narration", {}).get(slug, {})
    media = block.get("media", {}).get(key)
    if not text:
        return None
    seg = {"id": key, "screenId": screen, "startMs": 0, "media": None,
           "captions": {"unit": "milliseconds", "alignment": "provider-segments",
                        "segments": [{"text": text, "startMs": 0, "endMs": media["durationMs"] if media else None}]}}
    if media:
        seg["media"] = {"url": f"{NARRATION_MEDIA}/{media['sha256']}.wav", "contentHash": media["sha256"],
                        "mimeType": "audio/wav", "sizeBytes": media["bytes"], "durationMs": media["durationMs"]}
    return seg


def narration_block(manifest, slug, parts):
    block = manifest.get("narration", {}).get(slug)
    if not block:
        return None
    segments = [s for s in (narration_segment(manifest, slug, k, t, sc) for k, t, sc in parts) if s]
    return {"mode": "synthesized", "captions": True, "status": block.get("status", "draft"),
            "voice": manifest.get("voice"), "segments": segments}


def surface_docs(manifest):
    docs = {}
    for key, value in sorted(manifest["surfaces"].items()):
        docs[key] = {"schema": SCHEMA_SURFACE, "id": key, "name": value["name"], "template": value["template"],
                     "status": value["status"], "note": value.get("note"),
                     "default": key == manifest.get("default_surface")}
    return docs


def build(manifest):
    pages, raw = manifest["canonical"]["pages"], manifest["canonical"]["raw"]
    registry = load(ROOT / "registry.json")
    catalog = load(ROOT / "solutions" / "catalog.json")["solutions"]
    scenarios = load(ROOT / "solutions" / "_shared" / "demo-scenarios.json")
    solutions = solution_docs(manifest, catalog, registry, scenarios, raw)
    by_agent = {doc["id"]: slug for slug, doc in solutions.items()}
    scen = scenario_docs(manifest, scenarios, by_agent)
    agents = agent_docs(registry)
    files: dict[str, object] = {}
    for slug, doc in solutions.items():
        files[f"api/v1/solutions/{slug}.json"] = doc
    for sid, doc in scen.items():
        files[f"api/v1/scenarios/{sid}.json"] = doc
    for slug, doc in agents.items():
        files[f"api/v1/catalog/{slug}.json"] = doc
    for key, doc in surface_docs(manifest).items():
        files[f"api/v1/surfaces/{key}.json"] = doc
    files["api/v1/stacks.json"] = stacks_doc(registry)
    files["api/v1/search.json"] = {
        "schema": SCHEMA_SEARCH,
        "solutions": [{"slug": slug, "name": d["name"], "headline": d["headline"], "industries": d["industries"],
                       "personas": d["personas"], "doc": f"api/v1/solutions/{slug}.json",
                       "demo": d["try"]["page"]} for slug, d in solutions.items()],
    }
    recorded = len(scen)
    summary = {"solutions": len(solutions), "agents": len(agents), "stacks": len(registry["stacks"]),
               "scenarios": scenarios["summary"]["scenarios"], "recorded": recorded,
               "surfaces": len(manifest["surfaces"]),
               "with_package": sum(1 for d in solutions.values() if d["get"]["package"]),
               "with_instructions": sum(1 for d in solutions.values() if d["get"]["instructions"])}
    files["api/v1/index.json"] = {
        "schema": SCHEMA_INDEX,
        "title": manifest["title"],
        "description": manifest["description"],
        "notice": manifest["notice"],
        "summary": summary,
        "surfaces": [{"id": k, "name": v["name"], "doc": f"api/v1/surfaces/{k}.json"}
                     for k, v in sorted(manifest["surfaces"].items())],
        "start": [
            "Find a solution in api/v1/search.json.",
            "Read its api/v1/solutions/<slug>.json.",
            "To show it, open try.page or read each try.scenarios[].doc.",
            "To deploy it, follow get.prompt with {pages} set to this site's address.",
        ],
        "endpoints": {"search": "api/v1/search.json", "solution": "api/v1/solutions/{slug}.json",
                      "scenario": "api/v1/scenarios/{id}.json", "agent": "api/v1/catalog/{name}.json",
                      "stacks": "api/v1/stacks.json", "surface": "api/v1/surfaces/{id}.json",
                      "status": "api/v1/status.json", "badge": "api/v1/badge.json", "registry": "api/registry.json"},
    }
    files["api/v1/status.json"] = {"schema": SCHEMA_STATUS, "ok": True, "summary": summary}
    files["api/v1/badge.json"] = {"schemaVersion": 1, "label": "library api",
                                  "message": f"{summary['solutions']} solutions, {recorded} demos",
                                  "color": "blue"}
    return files, summary, pages, raw


def stable_generated(path: Path, body: dict) -> str:
    """Keep the old timestamp when nothing but the timestamp would change."""
    if path.exists():
        try:
            old = load(path)
        except ValueError:
            old = None
        if isinstance(old, dict):
            stamp = old.pop("generated", None)
            if stamp and old == body:
                return stamp
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def render(manifest):
    files, summary, pages, raw = build(manifest)
    out: dict[str, bytes] = {}
    entries = []
    for name, doc in sorted(files.items()):
        data = dump(doc)
        out[name] = data
        digest = sha256_bytes(data)
        key = name[len("api/v1/"):-len(".json")]
        version = f"api/versions/{key}/{digest[:12]}.json"
        out[version] = data
        entries.append({"name": key, "path": name, "sha256": digest, "sha8": digest[:12], "version": version})
    body = {"schema": SCHEMA_REGISTRY, "spec": "rapp-static-api/1.1", "name": manifest["name"],
            "pages": pages, "raw": raw, "summary": summary, "entries": entries}
    path = ROOT / "api" / "registry.json"
    registry = {"schema": body["schema"], "generated": stable_generated(path, body), **{k: v for k, v in body.items() if k != "schema"}}
    out["api/registry.json"] = dump(registry)
    out["llms.txt"] = llms_text(manifest, summary, pages, raw).encode("utf-8")
    return out


def llms_text(manifest, summary, pages, raw):
    return f"""# {manifest['title']}

> {manifest['description']}

{manifest['notice']}

Site: {pages}
Raw fallback: {raw}

## Start here
- {pages}api/v1/index.json: where to start, counts and every endpoint.
- {pages}api/v1/search.json: one line per solution ({summary['solutions']}). Find the right one here.
- {pages}api/v1/solutions/<slug>.json: everything about one solution: what it is, try it, get it, learn it, proof.
- {pages}api/v1/scenarios/<id>.json: one demo question with its recorded answer ({summary['recorded']} recorded).
- {pages}api/registry.json: every endpoint with its SHA-256 and a permanent copy under api/versions/.

## To show a solution
Open the solution's try.page. It plays the recorded demo in Microsoft 365 Copilot, Cowork or Copilot Studio.
Every answer is a recorded sample answer. Questions outside the recorded ones are not answered.

## To deploy a solution
Read get.prompt in the solution document, replace {{pages}} with {pages}, and follow it.
It asks the user once before changing anything. Check every download against its sha256.

## Rules
- Sample data only. Never connect a library solution to an organization's own data.
- Same-site reads use relative paths. Do not bypass the cache.
"""


def write(out: dict[str, bytes], check: bool) -> list[str]:
    changed = []
    for name, data in sorted(out.items()):
        path = ROOT / name
        if name.startswith("api/versions/") and path.exists():
            if path.read_bytes() != data:
                raise BuildError(f"{name} already exists with different bytes; versions are append-only")
            continue
        if path.exists() and path.read_bytes() == data:
            continue
        changed.append(name)
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    # endpoints that are no longer produced are removed; versions never are
    current = {name for name in out if name.startswith("api/v1/")}
    for path in sorted(V1.rglob("*.json")) if V1.exists() else []:
        name = rel(path)
        if name not in current:
            changed.append(name + " (removed)")
            if not check:
                path.unlink()
    return changed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if the committed files are out of date")
    args = parser.parse_args(argv)
    try:
        out = render(load(MANIFEST))
        changed = write(out, args.check)
    except BuildError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if args.check and changed:
        print("library API is out of date; run python tools/build_library_api.py", file=sys.stderr)
        for name in changed[:20]:
            print("  " + name, file=sys.stderr)
        return 1
    print(f"library API: {len(out)} files, {len(changed)} changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
