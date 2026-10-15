#!/usr/bin/env python3
"""Build the library's public, static API for people, search engines and AI agents.

Runs in the Pages workflow before build_pages_site.py and writes into the overlay directory (nothing is
committed). Every file is plain static content served from the Pages CDN, so any number of visitors and
agents can read it with no rate limit, and the same files work unchanged behind any other CDN.

  api/v1/index.json            what this API serves (schema, counts, endpoints)
  api/v1/agents.json           every solution agent, one line each
  api/v1/agents/<slug>.json    one agent: the business case, prompts with their recorded answers, links
  openapi.json                 OpenAPI 3.1 description of the endpoints above
  llms.txt / llms-full.txt     plain-text entry point for AI agents (llmstxt.org)
  sitemap.xml / robots.txt     for search engines
  feed.xml                     Atom feed of agents, newest first

Usage: python scripts/build_public_api.py --out DIR --site https://owner.github.io/repo/ --repository owner/repo
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "aibast-public-api/1.0"
AGENT_SCHEMA = "aibast-public-agent/1.0"
SCENARIO = re.compile(r"[?&]scenario=([a-z0-9-]+)")
SITEMAP_PAGES = ("index.html", "metrics.html", "why.html", "docs/index.html", "docs/installer.html", "docs/tutorial.html")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def request_form(root):
    """The asset request form and its solution field, as the library page defines them."""
    page = (root / "index.html").read_text(encoding="utf-8")
    form = re.search(r'const REQUEST_FORM = "([^"]+)";', page)
    field = re.search(r'const REQUEST_FORM_SOLUTION_FIELD = "([^"]+)";', page)
    names = re.search(r"const REQUEST_FORM_SOLUTION_NAMES = (\{.*?\});", page, re.S)
    overrides = dict(re.findall(r'"([^"]+)":\s*"([^"]+)"', names.group(1))) if names else {}
    return (form.group(1), field.group(1), overrides) if form and field else (None, None, {})


def build(root, site, repository):
    site = site.rstrip("/") + "/"
    registry = {agent["name"]: agent for agent in read_json(root / "registry.json")["agents"]}
    catalog = read_json(root / "solutions" / "catalog.json")["solutions"]
    scenarios = read_json(root / "solutions" / "_shared" / "demo-scenarios.json")
    form, form_field, form_names = request_form(root)
    transcripts = {}
    files = {}
    rows = []
    for agent_id in sorted(catalog):
        entry = catalog[agent_id]
        agent = registry.get(agent_id, {})
        solution = agent.get("_solution") or {}
        slug = agent_id.split("/")[-1]
        prompts = []
        for prompt in entry.get("sample_prompts", []):
            match = SCENARIO.search(prompt.get("demo_url", ""))
            scenario = scenarios["scenarios"].get(match.group(1)) if match else None
            answer = None
            if scenario and scenario["recorded"]:
                folder = scenario["folder"]
                if folder not in transcripts:
                    path = root / "solutions" / folder / "evals" / "transcripts.json"
                    transcripts[folder] = {t["case_id"]: t for t in read_json(path)["transcripts"]}
                recorded = transcripts[folder].get(scenario["case_id"])
                if recorded:
                    answer = {
                        "persona": recorded.get("persona"),
                        "prompt": recorded["prompt"],
                        "answer": recorded["assistant_response"],
                        "model": recorded.get("model"),
                    }
            prompts.append({
                "label": prompt["label"],
                "prompt": prompt["prompt"],
                "demo_url": site + prompt["demo_url"],
                "recorded": answer is not None,
                "recorded_answer": answer,
            })
        package = solution.get("package") or {}
        links = {
            "page": f"{site}index.html#agent/{quote(agent_id, safe='')}",
            "workshop": site + package["quest_url"] if package.get("quest_url") else None,
            "source": f"https://github.com/{repository}/blob/main/{agent['_file']}" if agent.get("_file") else None,
            "request_onepager_and_video": (
                f"{form}&{form_field}={quote(json.dumps(form_names.get(agent_id, entry['display_name'])), safe='')}"
                if form and (solution.get("has_onepager") or solution.get("has_demo_video")) else None
            ),
        }
        document = {
            "schema": AGENT_SCHEMA,
            "id": agent_id,
            "slug": slug,
            "name": entry["display_name"],
            "headline": entry.get("sales_headline"),
            "pitch": entry.get("card_pitch"),
            "category": agent.get("category"),
            "industries": solution.get("industries") or [],
            "personas": solution.get("personas") or [],
            "microsoft_products": solution.get("featured_tools") or [],
            "journey_stage": entry.get("journey_stage"),
            "why_try": entry.get("why_try"),
            "customer_challenge": entry.get("customer_challenge"),
            "microsoft_ai_story": entry.get("microsoft_ai_story"),
            "business_value": entry.get("business_value") or [],
            "business_flow": (entry.get("architecture") or {}).get("business_flow") or [],
            "capabilities": (entry.get("architecture") or {}).get("capabilities") or [],
            "has_onepager": bool(solution.get("has_onepager")),
            "has_demo_video": bool(solution.get("has_demo_video")),
            "synthetic_data": bool(agent.get("_synthetic_data", True)),
            "added_at": agent.get("_added_at"),
            "prompts": prompts,
            "links": links,
        }
        files[f"api/v1/agents/{slug}.json"] = document
        rows.append({
            "id": agent_id,
            "slug": slug,
            "name": document["name"],
            "pitch": document["pitch"],
            "category": document["category"],
            "industries": document["industries"],
            "journey_stage": document["journey_stage"],
            "recorded_prompts": sum(p["recorded"] for p in prompts),
            "added_at": document["added_at"],
            "url": f"{site}api/v1/agents/{slug}.json",
            "page": links["page"],
        })
    source_hash = hashlib.sha256(
        b"".join((root / name).read_bytes() for name in ("registry.json", "solutions/catalog.json"))
    ).hexdigest()
    files["api/v1/agents.json"] = {"schema": "aibast-public-agents/1.0", "count": len(rows), "agents": rows}
    files["api/v1/index.json"] = {
        "schema": SCHEMA,
        "site": site,
        "source_sha256": source_hash,
        "agents": len(rows),
        "recorded_prompts": sum(r["recorded_prompts"] for r in rows),
        "endpoints": {
            "agents": f"{site}api/v1/agents.json",
            "agent": f"{site}api/v1/agents/{{slug}}.json",
            "demo_scenarios": f"{site}solutions/_shared/demo-scenarios.json",
            "github_snapshot": f"{site}api/v1/github/index.json",
            "openapi": f"{site}openapi.json",
            "llms": f"{site}llms.txt",
            "feed": f"{site}feed.xml",
        },
        "note": "Static files, refreshed on every deploy. All demo data is synthetic.",
    }
    files["openapi.json"] = openapi(site)
    texts = {
        "llms.txt": llms(site, rows, full=False, documents=files),
        "llms-full.txt": llms(site, rows, full=True, documents=files),
        "robots.txt": f"User-agent: *\nAllow: /\nSitemap: {site}sitemap.xml\n",
        "sitemap.xml": sitemap(root, site, files),
        "feed.xml": feed(site, rows),
    }
    return files, texts


def openapi(site):
    agent = {"$ref": "#/components/schemas/Agent"}
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "AI BAST Agents Library",
            "version": "1.0.0",
            "description": "Static, read-only API over the AI BAST Agents Library: Microsoft agent solutions with "
                           "their business case, example prompts and recorded answers on synthetic data.",
        },
        "servers": [{"url": site.rstrip("/")}],
        "paths": {
            "/api/v1/agents.json": {"get": {
                "operationId": "listAgents",
                "summary": "List every agent solution in the library",
                "responses": {"200": {"description": "All agents", "content": {"application/json": {}}}},
            }},
            "/api/v1/agents/{slug}.json": {"get": {
                "operationId": "getAgent",
                "summary": "One agent: business case, industries, prompts with recorded answers, and links",
                "parameters": [{"name": "slug", "in": "path", "required": True, "schema": {"type": "string"},
                                "description": "The agent's slug from listAgents, e.g. account-intelligence"}],
                "responses": {"200": {"description": "The agent", "content": {"application/json": {"schema": agent}}}},
            }},
        },
        "components": {"schemas": {"Agent": {"type": "object", "properties": {
            "id": {"type": "string"}, "name": {"type": "string"}, "pitch": {"type": "string"},
            "industries": {"type": "array", "items": {"type": "string"}},
            "personas": {"type": "array", "items": {"type": "string"}},
            "prompts": {"type": "array", "items": {"type": "object"}},
            "links": {"type": "object"},
        }}}},
    }


def llms(site, rows, full, documents):
    lines = [
        "# AI BAST Agents Library",
        "",
        "> Microsoft agent solutions for pre-sales: each one has a business case, example prompts with recorded "
        "answers on synthetic data, a hands-on workshop, and a one-pager and demo video on request.",
        "",
        f"- API index: {site}api/v1/index.json",
        f"- All agents (JSON): {site}api/v1/agents.json",
        f"- OpenAPI: {site}openapi.json",
        f"- Library: {site}index.html",
        "",
        "## Agents",
        "",
    ]
    for row in rows:
        lines.append(f"- [{row['name']}]({row['url']}): {row['pitch'] or ''}")
        if full:
            document = documents[f"api/v1/agents/{row['slug']}.json"]
            if document["industries"]:
                lines.append(f"  - Industries: {', '.join(document['industries'])}")
            if document["personas"]:
                lines.append(f"  - Built for: {', '.join(document['personas'])}")
            for prompt in document["prompts"]:
                state = "recorded demo" if prompt["recorded"] else "not recorded yet"
                lines.append(f"  - Prompt ({state}): {prompt['prompt']} {prompt['demo_url']}")
    return "\n".join(lines) + "\n"


def sitemap(root, site, files):
    pages = [page for page in SITEMAP_PAGES if (root / page).exists()]
    pages += sorted(p.relative_to(root).as_posix() for p in (root / "solutions").glob("*/quest.html"))
    pages += sorted(name for name in files if name.startswith("api/v1/agents/"))
    body = "".join(f"  <url><loc>{escape(site + page)}</loc></url>\n" for page in pages)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n'


def feed(site, rows):
    dated = sorted((r for r in rows if r["added_at"]), key=lambda r: (r["added_at"], r["slug"]), reverse=True)
    updated = dated[0]["added_at"] if dated else "1970-01-01T00:00:00Z"
    entries = "".join(
        "  <entry>\n"
        f"    <id>{escape(r['url'])}</id>\n"
        f"    <title>{escape(r['name'])}</title>\n"
        f"    <updated>{escape(r['added_at'])}</updated>\n"
        f"    <link href=\"{escape(r['page'])}\"/>\n"
        f"    <summary>{escape(r['pitch'] or '')}</summary>\n"
        "  </entry>\n"
        for r in dated
    )
    return ('<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom">\n'
            f"  <id>{escape(site)}feed.xml</id>\n  <title>AI BAST Agents Library: agents</title>\n"
            f"  <updated>{escape(updated)}</updated>\n  <link href=\"{escape(site)}\"/>\n{entries}</feed>\n")


def write(out, files, texts):
    out = Path(out)
    for name, value in files.items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, value in texts.items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True)
    parser.add_argument("--site", required=True)
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()
    files, texts = build(ROOT, args.site, args.repository)
    write(args.out, files, texts)
    print(f"wrote the public API: {files['api/v1/index.json']['agents']} agents, "
          f"{files['api/v1/index.json']['recorded_prompts']} recorded prompts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
