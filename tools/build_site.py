#!/usr/bin/env python3
"""Build the AIBAST Agents Library site from its inputs, the way the Copilot Studio Gallery
builds its site from submissions/ (docs/SITE-REWRITE.md is the contract).

One input tree -> one build -> dist/. Nothing in dist/ is committed.

    submissions/<slug>/            metadata.json, README.md, library.json, solution/   (the solutions)
    tools/gallery_submissions.json which slugs, their category and featured flag
    partners.json, community_tools.json                                      (the other contributors)
    tools/design_tokens.py                                                   (the one palette)
    tools/site/site.css, tools/site/site.js                                   (one stylesheet, one script)

Routes written (see docs/SITE-REWRITE.md section 3):
    /                      gallery: search, industry chips, Filters, cards
    /built-by-aibast/      the featured solutions
    /solutions/<slug>/     one solution: Overview, How it works, What's inside, Set it up; demo-first rail
    /tags/<tag>/  /categories/<category>/  /contributors/  /contributors/<key>/
    /solutions.json        the catalog, same fields as the gallery's endpoint
    /404.html

Usage:
    python tools/build_site.py                 # write dist/
    python tools/build_site.py --out <dir>
    python tools/build_site.py --check         # build in memory, report what would change
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import clarity_tag, design_tokens  # noqa: E402
from tools.build_gallery_submissions import gallery_docs, markdown_to_html, read_json  # noqa: E402

SITE_NAME = "AIBAST Agents Library"
SITE_TAGLINE = "Ready-made agents for the customer conversation"
SITE_LEDE = ("Find a solution for the industry in front of you, watch it work with sample data, "
             "and set it up in Copilot Studio in minutes.")
CANONICAL = "https://microsoft.github.io/aibast-agents-library/"
RAW_BASE = "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/"
REPO = "https://github.com/microsoft/aibast-agents-library"
ASSET_DIR = ROOT / "tools" / "site"
DIST = ROOT / "dist"
FIRST_PARTY_KEY = "aibast"
DEFAULT_SCOPE = "all"
INDUSTRY_CHIPS = 8

NAV = [
    ("Solutions", ""),
    ("Industries", "categories/"),
    ("Contributors", "contributors/"),
    ("Learn", "learn/"),
    ("Install", "install/"),
    ("About", "about/"),
]


# --------------------------------------------------------------------------- helpers

def esc(value) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def slugify(value: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def rel(depth: int) -> str:
    """Relative base for a page this many folders deep. "./" at the root so no href is ever empty."""
    return "../" * depth if depth else "./"


def plural(count: int, word: str, plural_word: str | None = None) -> str:
    return f"{count} {word if count == 1 else (plural_word or word + 's')}"


def kb(size: int | None) -> str:
    return f"{round(size / 1024)} KB" if size else ""


# --------------------------------------------------------------------------- data

class Site:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.config = read_json(root / "tools" / "gallery_submissions.json")
        docs, index = gallery_docs(root, RAW_BASE)
        self.docs = docs
        self.index = index
        self.library = {}
        for slug in docs:
            sidecar = root / "submissions" / slug / "library.json"
            self.library[slug] = read_json(sidecar) if sidecar.exists() else {}
        self.partners = read_json(root / "partners.json") if (root / "partners.json").exists() else {"partners": [], "agents": []}
        self.community = read_json(root / "community_tools.json") if (root / "community_tools.json").exists() else {"tools": []}
        self.tokens = design_tokens.render_tokens()
        self.clarity = clarity_tag.current_tag(root)

    # ---- derived facts
    def solutions(self) -> list[dict]:
        rows = []
        for slug, doc in self.docs.items():
            lib = self.library.get(slug, {})
            spec = self.config["submissions"].get(slug, {})
            rows.append({
                "slug": slug,
                "doc": doc,
                "lib": lib,
                "featured": bool(spec.get("featured", False)),
                "industries": lib.get("industries") or [],
                "contains": [k for k, n in (("skill", doc["counts"]["skills"]), ("knowledge", doc["counts"]["knowledge"]), ("tool", doc["counts"]["tools"])) if n],
            })
        rows.sort(key=lambda r: (not r["featured"], r["doc"]["name"].lower()))
        return rows

    def industries(self, rows) -> list[tuple[str, int]]:
        counts: dict[str, int] = {}
        for r in rows:
            for i in r["industries"]:
                counts[i] = counts.get(i, 0) + 1
        return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    def tags(self, rows) -> list[tuple[str, int]]:
        counts: dict[str, int] = {}
        for r in rows:
            for t in r["doc"]["tags"]:
                counts[t] = counts.get(t, 0) + 1
        return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    def categories(self, rows) -> list[tuple[str, int]]:
        counts: dict[str, int] = {}
        for r in rows:
            c = r["doc"]["category"] or "Other"
            counts[c] = counts.get(c, 0) + 1
        return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    def contributors(self, rows) -> list[dict]:
        """AIBAST (first party, every submission), then partners and community authors.
        Partner and community entries link to their own source; they are not submissions."""
        out = [{
            "key": FIRST_PARTY_KEY,
            "name": self.config["author"]["name"],
            "url": self.config["author"]["url"],
            "kind": "First party",
            "items": [{"name": r["doc"]["name"], "href": f"solutions/{r['slug']}/", "external": False} for r in rows],
        }]
        for p in self.partners.get("partners", []):
            agents = [a for a in self.partners.get("agents", []) if a.get("partner_id") == p["id"]]
            out.append({
                "key": slugify(p["name"]), "name": p["name"], "url": p.get("url"), "kind": "Partner",
                "description": p.get("description"),
                "items": [{"name": a["name"], "href": a.get("source_url") or p.get("url"), "external": True, "note": a.get("description")} for a in agents],
            })
        by_author: dict[str, dict] = {}
        for t in self.community.get("tools", []):
            key = slugify(t.get("author") or t["name"])
            entry = by_author.setdefault(key, {"key": key, "name": t.get("author") or t["name"], "url": None, "kind": "Community", "items": []})
            entry["items"].append({"name": t["name"], "href": t.get("url"), "external": True, "note": t.get("description")})
        out.extend(sorted(by_author.values(), key=lambda c: c["name"].lower()))
        return out


# --------------------------------------------------------------------------- shell

LOGO = ('<span class="ms" aria-hidden="true"><i style="background:var(--cp-logo-1)"></i><i style="background:var(--cp-logo-2)"></i>'
        '<i style="background:var(--cp-logo-3)"></i><i style="background:var(--cp-logo-4)"></i></span>')

ICONS = {
    "search": '<svg width="18" height="18" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M8.5 3a5.5 5.5 0 0 1 4.23 9.02l4.12 4.13a.5.5 0 0 1-.63.76l-.07-.06-4.13-4.12A5.5 5.5 0 1 1 8.5 3Zm0 1a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9Z"/></svg>',
    "play": '<svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M17.22 8.69a1.5 1.5 0 0 1 0 2.62l-10 5.5A1.5 1.5 0 0 1 5 15.5v-11a1.5 1.5 0 0 1 2.22-1.31l10 5.5Z"/></svg>',
    "doc": '<svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M6 2a2 2 0 0 0-2 2v12c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V7.41a1.5 1.5 0 0 0-.44-1.06l-3.91-3.91A1.5 1.5 0 0 0 10.59 2H6Zm4 1.5V6a1 1 0 0 0 1 1h2.5L10 3.5Z"/></svg>',
    "dl": '<svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M15.5 17a.5.5 0 0 1 0 1h-11a.5.5 0 0 1 0-1h11ZM10 2a.5.5 0 0 1 .5.41v11.38l3.65-3.64a.5.5 0 0 1 .7.7l-4.5 4.5a.5.5 0 0 1-.7 0l-4.5-4.5a.5.5 0 0 1 .7-.7l3.65 3.64V2.5A.5.5 0 0 1 10 2Z"/></svg>',
    "chat": '<svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M10 2a8 8 0 1 1-3.61 15.14l-3.77.95a.5.5 0 0 1-.61-.61l.95-3.77A8 8 0 0 1 10 2Zm0 1a7 7 0 0 0-6.02 10.57l.1.17-.78 3.1 3.1-.78.17.1A7 7 0 1 0 10 3Z"/></svg>',
    "skill": '<svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M10 2.5 12.1 7l4.9.6-3.6 3.4.9 4.9L10 13.5 5.7 15.9l.9-4.9L3 7.6 7.9 7 10 2.5Z"/></svg>',
}


def shell_header(base: str, active: str = "") -> str:
    nav = []
    for label, href in NAV:
        is_ext = href.startswith("http")
        target = href if is_ext else base + href
        cls = ' class="on"' if (not is_ext and active == label) else ""
        extra = ' target="_blank" rel="noopener"' if is_ext else ""
        nav.append(f'<a href="{esc(target)}"{cls}{extra}>{esc(label)}</a>')
    return (f'<header class="site-top"><div class="wrap bar">\n <a class="brand" href="{base}">{LOGO}<span class="brand-name">{esc(SITE_NAME)}</span></a>\n'
            f' <nav aria-label="Site">{"".join(nav)}</nav>\n</div></header>')


def shell_footer(base: str) -> str:
    return (f'<footer class="site-foot"><div class="wrap">\n <p>Every demo uses sample data only and is not connected to any organization&#39;s data. '
            'Solutions are provided as-is and are not covered by Microsoft Support; the underlying Copilot Studio and Power Platform products keep their standard support.</p>\n'
            f'             <p class="foot-links"><a href="{base}solutions.json">Catalog (JSON)</a> · <a href="{base}llms.txt">llms.txt</a> · <a href="{esc(REPO)}" target="_blank" rel="noopener">View on GitHub</a> · <a href="{base}install/">Install the Brainstem</a></p>\n</div></footer>')


SUPPORTING_PAGES = ("quest.html", "field-guide.html", "manual-tutorial.html", "evidence-report.html")
TOPBAR_RE = re.compile(r'<header class="topbar">.*?</header>', re.S)


def wrap_supporting_page(site: Site, r: dict, name: str, html_text: str) -> str:
    """The four workshop pages per solution are rendered by tools/scaffold_solution_journey.py and
    keep their own stylesheet and scripts. The site puts them inside its shell: header above their
    topbar, footer below, breadcrumb pointing at the solution page. Nothing else in them changes."""
    base = rel(2)
    doc = r["doc"]
    def topbar(match):
        old = match.group(0)
        old = re.sub(r'<a class="academy-breadcrumb" href="[^"]*">[^<]*</a>',
                     f'<a class="academy-breadcrumb" href="./">Solutions / {esc(doc["name"])}</a>', old)
        return shell_header(base, "Solutions") + "\n" + old
    html_text = TOPBAR_RE.sub(topbar, html_text, count=1)
    html_text = html_text.replace("</head>", f'<link rel="stylesheet" href="{base}assets/shell.css">\n</head>', 1)
    html_text = html_text.replace("</body>", shell_footer(base) + "\n</body>", 1)
    return html_text


def page(site: Site, *, title: str, description: str, body: str, depth: int, active: str = "", path: str = "",
         extra_head: str = "", body_class: str = "", page_type: str = "page") -> str:
    base = rel(depth)
    full_title = SITE_NAME if title == SITE_NAME else f"{title} · {SITE_NAME}"
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(CANONICAL + path)}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(SITE_NAME)}">
<link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{base}assets/shell.css">
<link rel="stylesheet" href="{base}assets/site.css">
{extra_head}
<style>
/* page-local layout only; every colour comes from the design tokens */
</style>
</head>
<body data-page="{esc(page_type)}" data-base="{base}"{f' class="{esc(body_class)}"' if body_class else ''}>
<a class="skip" href="#main">Skip to content</a>
{shell_header(base, active)}
<main id="main">
{body}
</main>
{shell_footer(base)}
<script src="{base}assets/site.js" defer></script>
</body>
</html>
"""
    doc = design_tokens.stamp(doc, site.tokens)
    return clarity_tag.stamp(doc, site.clarity)


# --------------------------------------------------------------------------- components

def card(r: dict, base: str) -> str:
    doc, lib = r["doc"], r["lib"]
    industries = r["industries"]
    kicker = esc(industries[0]) + (f' <span class="more">+{len(industries) - 1}</span>' if len(industries) > 1 else "") if industries else esc(doc["category"] or "")
    headline = lib.get("headline") or doc["description"]
    facts = []
    if lib.get("assets", {}).get("demo_video"):
        facts.append(f'<span class="has">{ICONS["play"]}Demo video</span>')
    if lib.get("assets", {}).get("onepager"):
        facts.append(f'<span class="has">{ICONS["doc"]}One-pager</span>')
    prompts = lib.get("sample_prompts") or []
    if prompts:
        facts.append(f'<span class="has">{ICONS["chat"]}{plural(len(prompts), "sample chat")}</span>')
    facts.append(f'<span class="has">{ICONS["skill"]}{plural(doc["counts"]["skills"], "skill")}</span>')
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in doc["tags"][:3])
    search_blob = " ".join([doc["name"], headline, doc["description"], *doc["tags"], *industries, *(lib.get("personas") or []), *(lib.get("products") or [])]).lower()
    featured = '<span class="badge" title="Built by AIBAST">Built by AIBAST</span>' if r["featured"] else ""
    return (f'<article class="card" data-search="{esc(search_blob)}" data-industries="{esc("|".join(industries))}" '
            f'data-category="{esc(doc["category"] or "Other")}" data-tags="{esc("|".join(doc["tags"]))}" '
            f'data-contains="{esc("|".join(r["contains"]))}" data-author="{FIRST_PARTY_KEY}" data-featured="{int(r["featured"])}">'
            f'<a class="card-link" href="{base}solutions/{r["slug"]}/" aria-label="View {esc(doc["name"])}"></a>'
            f'<div class="card-top"><span class="kick">{kicker}</span>{featured}</div>'
            f'<h3>{esc(doc["name"])}</h3><p>{esc(headline)}</p>'
            f'<div class="meta">{tags}</div><div class="meta facts">{"".join(facts)}</div></article>')


def gallery_section(site: Site, rows: list[dict], base: str, *, heading: str, scope: str) -> str:
    industries = site.industries(rows)
    top = industries[:INDUSTRY_CHIPS]
    rest = industries[INDUSTRY_CHIPS:]
    tags = site.tags(rows)
    categories = site.categories(rows)
    contains_labels = (("skill", "Skills"), ("knowledge", "Knowledge files"), ("tool", "Tools"))
    chips = "".join(f'<button type="button" class="chip" data-industry="{esc(name)}" aria-pressed="false">{esc(name)} <span class="n">{count}</span></button>' for name, count in top)
    more = ""
    if rest:
        more = ('<select id="more-industries" aria-label="More industries"><option value="">More industries</option>'
                + "".join(f'<option value="{esc(name)}">{esc(name)} ({count})</option>' for name, count in rest) + "</select>")
    facet = lambda name, items: "".join(  # noqa: E731
        f'<label class="opt"><input type="checkbox" name="{name}" value="{esc(v)}"><span>{esc(label)} <em class="n">{count}</em></span></label>'
        for v, label, count in items)
    contains_counts = {k: sum(1 for r in rows if k in r["contains"]) for k, _ in contains_labels}
    dialog = f"""
<dialog id="filters" class="filters" aria-labelledby="filters-title">
 <form method="dialog" class="filters-form">
  <header><h2 id="filters-title">Filters</h2><button type="button" class="x" data-close aria-label="Close">×</button></header>
  <p class="sub">Match any selected industry or category; require every selected tag and component type.</p>
  <fieldset><legend>Contains</legend><div class="opts">{facet("contains", [(k, label, contains_counts[k]) for k, label in contains_labels if contains_counts[k]])}</div></fieldset>
  <fieldset><legend>Categories</legend><div class="opts">{facet("category", [(c, c, n) for c, n in categories])}</div></fieldset>
  <fieldset><legend>Industries</legend><div class="opts">{facet("industry", [(i, i, n) for i, n in industries])}</div></fieldset>
  <fieldset><legend>Tags</legend><input type="search" class="picker" placeholder="Search tags" data-picker="tag" aria-label="Search tags"><div class="opts tall">{facet("tag", [(t, t, n) for t, n in tags])}</div></fieldset>
  <footer><button type="button" class="btn" data-clear>Clear all</button><button type="submit" class="btn pri" data-apply>Apply</button></footer>
 </form>
</dialog>"""
    cards = "".join(card(r, base) for r in rows)
    return f"""
<section class="find" aria-label="Find solutions"><div class="wrap">
 <div class="sbox">{ICONS["search"]}<input id="q" type="search" placeholder="Search by problem, role or product" autocomplete="off" aria-label="Search solutions"></div>
 <div class="chips" role="group" aria-label="Filter by industry">
  <button type="button" class="chip" id="open-filters" aria-haspopup="dialog" aria-controls="filters">Filters <span class="n" id="filter-count" hidden></span></button>
  <span class="sep"></span>{chips}{more}
 </div>
 <div id="applied" class="applied" hidden></div>
</div></section>
{dialog}
<section class="wrap" data-gallery data-scope="{esc(scope)}">
 <div class="cathead"><h2>{esc(heading)}</h2><span class="count" id="count">{len(rows)} of {len(rows)}</span></div>
 <div class="grid" id="grid">{cards}</div>
 <p class="empty" id="empty" hidden>No solutions match. Clear a filter or try another word.</p>
</section>"""


# --------------------------------------------------------------------------- pages

def home(site: Site, rows: list[dict]) -> str:
    base = rel(0)
    featured = [r for r in rows if r["featured"]]
    hero = f"""
<section class="hero"><div class="wrap">
 <div class="kick">{esc(SITE_NAME)}</div>
 <h1>{esc(SITE_TAGLINE)}</h1>
 <p>{esc(SITE_LEDE)}</p>
 <p class="hero-facts">{plural(len(rows), "solution")} · {plural(len(site.industries(rows)), "industry", "industries")} · sample data only</p>
</div></section>"""
    sections = ""
    if featured:
        sections += f"""
<section class="wrap featured-row"><div class="cathead"><h2>Built by AIBAST</h2><a class="more-link" href="{base}built-by-aibast/">See all {len(featured)}</a></div>
 <div class="grid">{''.join(card(r, base) for r in featured[:3])}</div></section>"""
    body = hero + sections + gallery_section(site, rows, base, heading="All solutions", scope="all")
    return page(site, title=SITE_NAME, description=SITE_LEDE, body=body, depth=0, active="Solutions", path="", page_type="gallery")


def built_by(site: Site, rows: list[dict]) -> str:
    base = rel(1)
    featured = [r for r in rows if r["featured"]]
    head = f"""
<section class="hero small"><div class="wrap">
 <a class="crumb" href="{base}">← All solutions</a>
 <h1>Built by AIBAST</h1>
 <p>Solutions the AIBAST team built, recorded and tested with sample data. Review each one before importing it into your environment.</p>
</div></section>"""
    if not featured:
        body = head + '<section class="wrap"><p class="empty">No solution carries the Built by AIBAST mark yet. Mark one with <code>"featured": true</code> in tools/gallery_submissions.json.</p></section>'
    else:
        body = head + gallery_section(site, featured, base, heading="Built by AIBAST", scope="featured")
    return page(site, title="Built by AIBAST", description="Solutions built by the AIBAST team.", body=body, depth=1, active="Solutions", path="built-by-aibast/", page_type="gallery")


def steps(items: list[str]) -> str:
    return '<ol class="flow">' + "".join(f'<li><span class="num">{i + 1}</span><div>{item}</div></li>' for i, item in enumerate(items)) + "</ol>"


def solution(site: Site, r: dict, all_rows: list[dict]) -> str:
    base = rel(2)
    doc, lib = r["doc"], r["lib"]
    slug = r["slug"]
    agent = doc["agents"][0] if doc["agents"] else {}
    industries = r["industries"]
    prompts = lib.get("sample_prompts") or []
    learn = lib.get("learn") or {}
    assets = lib.get("assets") or {}
    tests = lib.get("tests") or {}
    download = doc["download"]
    try_page = doc["try"]["page"]
    demo_href = (base + try_page) if try_page else None

    # tabs
    overview = []
    if lib.get("capabilities"):
        overview.append("<h2>What it does</h2><ul>" + "".join(f"<li>{esc(c)}</li>" for c in lib["capabilities"]) + "</ul>")
    if lib.get("outcomes"):
        overview.append("<h2>Why it matters</h2><ul>" + "".join(f"<li>{esc(o)}</li>" for o in lib["outcomes"]) + "</ul>")
    if lib.get("personas"):
        overview.append(f"<h2>Who it helps</h2><p class=\"sub\">{esc(', '.join(lib['personas']))}</p>")
    overview.append('<details class="readme"><summary>Read the full overview</summary>' + doc["readme_html"] + "</details>")

    how = []
    if prompts:
        how.append("<h2>A conversation, step by step</h2>")
        how.append(steps([f'<strong>{esc(p.get("label") or "")}</strong><div class="note">“{esc(p.get("prompt") or "")}”</div>'
                          + (f'<a class="mini" href="{base}{esc(p["demo"])}">{ICONS["play"]} Watch this turn</a>' if p.get("demo") else "")
                          for p in prompts]))
    if lib.get("business_flow"):
        how.append("<h2>Where it runs</h2>" + steps([esc(x) for x in lib["business_flow"]]))
    if lib.get("why_try"):
        how.append(f'<h2>Why try the demo</h2><p class="sub">{esc(lib["why_try"])}</p>')

    inside = [f'<h2>Agents in this solution</h2>']
    inside.append('<table class="facts-table"><thead><tr><th>Agent</th><th>Skills</th><th>Knowledge</th><th>Tools</th></tr></thead><tbody>'
                  f'<tr><td><strong>{esc(agent.get("name", doc["name"]))}</strong><div class="note">{esc(agent.get("schema_name", ""))} · model {esc(agent.get("model") or "Auto")}</div></td>'
                  f'<td>{doc["counts"]["skills"]}</td><td>{doc["counts"]["knowledge"]}</td><td>{doc["counts"]["tools"]}</td></tr></tbody></table>')
    if agent.get("skills"):
        inside.append("<h2>Skills</h2><div class=\"two\">" + "".join(
            f'<div class="box"><h3>{esc(s.get("name"))}</h3><p class="note">{esc(s.get("description") or "")}</p></div>' for s in agent["skills"]) + "</div>")
    if agent.get("knowledge"):
        inside.append("<h2>Knowledge files</h2><ul>" + "".join(f"<li><code>{esc(k)}</code></li>" for k in agent["knowledge"]) + "</ul>")
    inside.append(f'<h2>Files in the package</h2><p class="note">The download rebuilds these {len(doc["files"])} files at the ZIP root. Solution <code>{esc(doc["unique_name"])}</code>, version {esc(doc["version"])}.</p>'
                  '<div class="scroll"><table class="files"><thead><tr><th>Path</th></tr></thead><tbody>' + "".join(f"<tr><td><code>{esc(f)}</code></td></tr>" for f in doc["files"]) + "</tbody></table></div>")

    install = lib.get("install") or {}
    size_note = f" ({kb(download.get('bytes'))})" if download.get("bytes") else ""
    setup = ["<h2>Before you start</h2><ul><li>A Copilot Studio environment you can make agents in.</li><li>Sample data only. Do not connect it to an organization's data.</li>"
             + "".join(f"<li>{esc(x)}</li>" for x in (lib.get("requirements") or []) if x != "Microsoft Copilot Studio") + "</ul>",
             "<h2>Set it up</h2>",
             steps([
                 f'Download the solution package{size_note} and import it in Copilot Studio through Power Platform Solutions.',
                 'Or ask your AI to do it for you:' + (f'<div class="code"><code>{esc(install.get("ai_prompt"))}</code><button type="button" class="copy" data-copy>Copy</button></div>' if install.get("ai_prompt") else ""),
                 f'Open the agent and try the first sample chat: <em>“{esc(prompts[0]["prompt"])}”</em>' if prompts else "Open the agent and start with its greeting.",
             ])]
    learn_links = [(learn.get("field_guide"), "Field guide"), (learn.get("manual_tutorial"), "Build it by hand"), (learn.get("quest"), "Workshop"), (learn.get("evidence"), "Evidence report")]
    learn_links = [(h, l) for h, l in learn_links if h]
    if learn_links:
        setup.append("<h2>Learn more</h2><p class=\"sub\">" + " · ".join(f'<a href="{base}{esc(h)}">{esc(l)}</a>' for h, l in learn_links) + "</p>")

    tabs = [("overview", "What it does", "".join(overview)), ("how", "How it works", "".join(how) or '<p class="sub">No recorded conversation yet.</p>'),
            ("inside", "What's inside", "".join(inside)), ("setup", "Set it up", "".join(setup))]
    tab_buttons = "".join(f'<button class="tab" role="tab" id="tab-{k}" aria-controls="panel-{k}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">{esc(label)}</button>' for i, (k, label, _) in enumerate(tabs))
    panels = "".join(f'<section class="panel" id="panel-{k}" role="tabpanel" aria-labelledby="tab-{k}"{"" if i == 0 else " hidden"}>{body}</section>' for i, (k, _, body) in enumerate(tabs))

    # rail
    rail = []
    rail.append('<div class="box"><h3>Try it without deploying</h3><p class="note">A recorded conversation with sample data, in the Microsoft 365 Copilot look. Nothing to install.</p>'
                + (f'<a class="btn pri" href="{demo_href}">{ICONS["play"]}Try the demo chat</a>' if demo_href else '<p class="note">No recorded demo yet.</p>') + "</div>")
    size_tail = f", {kb(download.get('bytes'))}" if download.get("bytes") else ""
    dl_note = f'Unmanaged Copilot Studio solution{size_tail}. Review the source before importing.'
    sha = f'<p class="note mono">sha256 {esc(download["sha256"][:16])}…</p>' if download.get("sha256") else ""
    rail.append(f'<div class="box"><h3>Get this solution</h3><p class="note">{dl_note}</p>'
                f'<label class="ack"><input type="checkbox" data-ack> I will review this sample and import it only into an environment I control.</label>'
                f'<a class="btn" href="{esc(download["url"])}" data-download aria-disabled="true">{ICONS["dl"]}Download package</a>{sha}</div>')
    show = []
    show.append(f'<div class="has">{ICONS["play"]}<span>Demo video</span></div><p class="note">{"Available in the AIBAST SharePoint library." if assets.get("demo_video") else "No demo video yet."}</p>')
    show.append(f'<div class="has">{ICONS["doc"]}<span>One-pager</span></div><p class="note">{"Available in the AIBAST SharePoint library." if assets.get("onepager") else "No one-pager yet."}</p>')
    rail.append('<div class="box"><h3>Show it to a customer</h3>' + "".join(show) + f'<a class="mini" href="{base}request/">Request the files</a></div>')
    facts = [("Built for", ", ".join(lib.get("personas") or []) or "—"), ("Uses", ", ".join(lib.get("products") or []) or "—"),
             ("Agents", str(doc["counts"]["agents"])), ("Skills", str(doc["counts"]["skills"])),
             ("Tested", f'{tests.get("passed")} of {tests.get("cases")} sample chats' if tests.get("cases") else "—"),
             ("Updated", doc.get("updated") or "—"), ("Version", doc.get("version") or "—")]
    rail.append('<div class="box"><dl class="kv">' + "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in facts) + "</dl></div>")

    chips = "".join(f'<a class="tag link" href="{base}categories/{slugify(doc["category"] or "Other")}/">{esc(doc["category"] or "Other")}</a>') + "".join(
        f'<a class="tag" href="{base}tags/{esc(t)}/">{esc(t)}</a>' for t in doc["tags"])
    headline = lib.get("headline") or doc["description"]
    body = f"""
<div class="wrap">
 <div class="crumb"><a href="{base}">Solutions</a> / {esc(doc["name"])}</div>
 <div class="dtop">
  <div class="dmain">
   <div class="kick">{esc(" · ".join(industries) or (doc["category"] or ""))}</div>
   <h1>{esc(doc["name"])}</h1>
   <p class="lede">{esc(headline)}</p>
   {f'<p class="sub">{esc(doc["description"])}</p>' if headline != doc["description"] else ""}
   <p class="byline">by <a href="{base}contributors/{FIRST_PARTY_KEY}/">{esc(doc["author"]["name"])}</a> · Version {esc(doc["version"])}{f' · Updated {esc(doc["updated"])}' if doc.get("updated") else ""}</p>
   <div class="meta">{chips}</div>
   <div class="mobile-actions">{f'<a class="btn pri" href="{demo_href}">{ICONS["play"]}Try the demo chat</a>' if demo_href else ''}</div>
   <div class="tabs" role="tablist" aria-label="Solution sections">{tab_buttons}</div>
   {panels}
  </div>
  <aside class="side">{''.join(rail)}</aside>
 </div>
</div>"""
    return page(site, title=doc["name"], description=doc["description"], body=body, depth=2, active="Solutions", path=f"solutions/{slug}/", page_type="solution")


def listing(site: Site, rows: list[dict], *, title: str, kicker: str, lede: str, depth: int, path: str, back: str = "") -> str:
    base = rel(depth)
    cards = "".join(card(r, base) for r in rows)
    body = f"""
<section class="hero small"><div class="wrap">
 <a class="crumb" href="{base}">← All solutions</a>
 <div class="kick">{esc(kicker)}</div><h1>{title}</h1><p>{esc(lede)}</p>
</div></section>
<section class="wrap"><div class="grid pad">{cards}</div></section>"""
    plain = re.sub(r"<[^>]+>", "", title)
    return page(site, title=plain, description=lede, body=body, depth=depth, active="Solutions" if "tag" in kicker.lower() else "Industries", path=path, page_type="listing")


def categories_index(site: Site, rows: list[dict]) -> str:
    base = rel(1)
    cats = site.categories(rows)
    inds = site.industries(rows)
    items = "".join(f'<a class="card flat" href="{base}categories/{slugify(c)}/"><h3>{esc(c)}</h3><p>{plural(n, "solution")}</p></a>' for c, n in cats)
    ind_items = "".join(f'<a class="chip static" href="{base}?industry={esc(i)}">{esc(i)} <span class="n">{n}</span></a>' for i, n in inds)
    body = f"""
<section class="hero small"><div class="wrap"><div class="kick">Browse</div><h1>Industries and categories</h1>
 <p>Every solution carries one category (the Copilot Studio Gallery vocabulary) and the industries it was written for.</p></div></section>
<section class="wrap"><div class="cathead"><h2>Categories</h2></div><div class="grid">{items}</div>
 <div class="cathead"><h2>Industries</h2></div><div class="chips wrap-chips">{ind_items}</div></section>"""
    return page(site, title="Industries and categories", description="Browse the library by category and industry.", body=body, depth=1, active="Industries", path="categories/", page_type="listing")


def contributors_page(site: Site, contributors: list[dict]) -> str:
    base = rel(1)
    cards = []
    for c in contributors:
        shown = c["items"][:8]
        extra = len(c["items"]) - len(shown)
        links = "".join(
            '<li><a href="' + esc(it["href"] if it["external"] else base + it["href"]) + '"'
            + (' target="_blank" rel="noopener"' if it["external"] else "") + '>' + esc(it["name"]) + "</a></li>"
            for it in shown if it.get("href"))
        cards.append(f"""<li class="card contributor" data-search="{esc((c["name"] + " " + " ".join(i["name"] for i in c["items"])).lower())}">
 <div class="card-top"><span class="kick">{esc(c["kind"])}</span><span class="count">{plural(len(c["items"]), "entry", "entries")}</span></div>
 <h3><a href="{base}contributors/{esc(c["key"])}/">{esc(c["name"])}</a></h3>
 {f'<p>{esc(c.get("description"))}</p>' if c.get("description") else ''}
 <ul class="mini-list">{links}{f'<li class="note">+{extra} more</li>' if extra > 0 else ''}</ul></li>""")
    body = f"""
<section class="hero small"><div class="wrap"><div class="kick">Community</div><h1>Contributors</h1>
 <p>The AIBAST team, partners, and community authors behind the library. Partner and community entries link to their own source and are not submissions.</p>
 <div class="sbox narrow">{ICONS["search"]}<input id="dir-q" type="search" placeholder="Search contributors or solutions" aria-label="Search contributors"></div></div></section>
<section class="wrap"><ul class="grid plain" id="directory">{''.join(cards)}</ul></section>"""
    return page(site, title="Contributors", description="People and teams behind the AIBAST Agents Library.", body=body, depth=1, active="Contributors", path="contributors/", page_type="contributors")


def contributor_page(site: Site, c: dict, rows_by_slug: dict) -> str:
    base = rel(2)
    if c["key"] == FIRST_PARTY_KEY:
        cards = "".join(card(r, base) for r in rows_by_slug.values())
        body_list = f'<div class="grid pad">{cards}</div>'
    else:
        items = "".join(
            f'<li class="card flat"><h3><a href="{esc(it["href"])}" target="_blank" rel="noopener">{esc(it["name"])}</a></h3>'
            + (f'<p>{esc(it.get("note"))}</p>' if it.get("note") else "") + "</li>"
            for it in c["items"] if it.get("href"))
        body_list = f'<ul class="grid plain pad">{items}</ul>'
    body = f"""
<section class="hero small"><div class="wrap"><a class="crumb" href="{base}contributors/">← Contributors</a>
 <div class="kick">{esc(c["kind"])}</div><h1>{esc(c["name"])}</h1>
 <p>{esc(c.get("description") or plural(len(c["items"]), "entry", "entries"))}{f' · <a href="{esc(c["url"])}" target="_blank" rel="noopener">Website</a>' if c.get("url") else ''}</p></div></section>
<section class="wrap">{body_list}</section>"""
    return page(site, title=c["name"], description=f'{c["name"]} in the {SITE_NAME}.', body=body, depth=2, active="Contributors", path=f"contributors/{c['key']}/", page_type="contributor")


def not_found(site: Site) -> str:
    body = f"""
<section class="hero"><div class="wrap"><div class="kick">404</div><h1>That page moved or never existed</h1>
 <p>Search the solutions, or start from the front door.</p><p><a class="btn pri" href="{rel(0)}">All solutions</a></p></div></section>"""
    return page(site, title="Page not found", description="Page not found.", body=body, depth=0, path="404.html", page_type="404")


def catalog_json(rows: list[dict]) -> str:
    payload = []
    for r in rows:
        doc, lib = r["doc"], r["lib"]
        payload.append({
            "slug": r["slug"], "name": doc["name"], "description": doc["description"], "category": doc["category"],
            "tags": doc["tags"], "industries": r["industries"], "author": doc["author"]["name"], "authors": [doc["author"]],
            "version": doc["version"], "download": doc["download"], "submissionType": "solution", "makeup": "Agents",
            "agentCount": doc["counts"]["agents"], "skillCount": doc["counts"]["skills"], "knowledgeCount": doc["counts"]["knowledge"],
            "toolCount": doc["counts"]["tools"], "componentCount": doc["counts"]["skills"] + doc["counts"]["knowledge"] + doc["counts"]["tools"],
            "featured": r["featured"], "builtByAibast": r["featured"], "try": doc["try"]["page"], "page": f"solutions/{r['slug']}/",
            "api": f"api/v1/gallery/{r['slug']}.json",
        })
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------- aliases

# Old address -> new route (docs/SITE-REWRITE.md section 4, "delete by aliasing"). A stub is written
# at the old address only when the new route exists in this build, so no stub ever points at nothing;
# until then the committed page keeps serving. `{slug}` targets read the slug from the old page's
# query string (solution.html?slug=x) or hash (academy.html#course/x) in the browser.
REDIRECTS = {
    "library.html": "./",
    "solution.html": "solutions/{slug}/",
    "academy.html": "learn/academy/",
    "achievements.html": "achievements/",
    "blog.html": "blog/",
    "community-agents.html": "community/",
    "community-tools.html": "community/",
    "front-page.html": "about/",
    "metrics.html": "metrics/",
    "partner-standards.html": "partners/",
    "pitch-playbook.html": "pitch/",
    "release-notes.html": "release-notes/",
    "request-info.html": "request/",
    "why.html": "why/",
    "docs/index.html": "learn/tutorial/",
    "docs/installer.html": "install/",
    "docs/tutorial.html": "learn/tutorial/",
    "docs/rapp-guide.html": "learn/guide/",
    "submissions/index.html": "./",
}


def redirect_stub(site: Site, old: str, target: str) -> str:
    depth = old.count("/")
    base = rel(depth)
    dynamic = "{slug}" in target
    plain_target = target.replace("{slug}/", "")
    href = base + plain_target if (plain_target != "./" and not dynamic) else base
    script = ""
    if dynamic:
        script = f"""<script>
(function () {{
  var slug = new URLSearchParams(location.search).get("slug") || (location.hash.match(/^#[/]?course[/]([a-z0-9-]+)/) || [])[1];
  var target = "{base}" + "{target.split("{slug}")[0]}" + (slug ? slug + "/" : "");
  location.replace(target);
}})();
</script>"""
    else:
        script = f'<meta http-equiv="refresh" content="0; url={esc(href)}">'
    body = f"""
<section class="hero"><div class="wrap"><div class="kick">This page moved</div>
 <h1>It now lives in the new library</h1>
 <p>You are being taken to <a href="{esc(href)}">{esc(href)}</a>. Update your bookmark when you get there.</p></div></section>"""
    return page(site, title="This page moved", description="This page moved to the new library.", body=body, depth=depth, path=old,
                extra_head=script + f'<link rel="canonical" href="{esc(CANONICAL + plain_target.lstrip("./"))}">', page_type="redirect")


def alias_pages(site: Site, out: dict[str, bytes]) -> dict[str, str]:
    stubs = {}
    for old, target in REDIRECTS.items():
        if old in out:
            continue
        route = target.replace("{slug}/", "")
        route_file = ("index.html" if route == "./" else route + "index.html")
        if route_file not in out and not ("{slug}" in target and any(k.startswith("solutions/") for k in out)):
            continue
        stubs[old] = redirect_stub(site, old, target)
    return stubs


# --------------------------------------------------------------------------- build

def section_modules():
    """tools/site_pages/<section>.py: each exposes build(site, page) -> {path: html} for one
    section of the site (learn, install, about...). Loaded in name order; a module may only
    write paths no other part of the build produces."""
    import importlib
    folder = ROOT / "tools" / "site_pages"
    if not folder.exists():
        return []
    modules = []
    for file in sorted(folder.glob("*.py")):
        if file.name.startswith("_"):
            continue
        modules.append(importlib.import_module(f"tools.site_pages.{file.stem}"))
    return modules


def build(site: Site) -> dict[str, bytes]:
    rows = site.solutions()
    by_slug = {r["slug"]: r for r in rows}
    out: dict[str, bytes] = {}

    def put(path: str, text: str):
        out[path] = text.encode("utf-8")

    put("index.html", home(site, rows))
    put("built-by-aibast/index.html", built_by(site, rows))
    for r in rows:
        put(f"solutions/{r['slug']}/index.html", solution(site, r, rows))
        for name in SUPPORTING_PAGES:
            source = site.root / "solutions" / r["slug"] / name
            if source.exists():
                put(f"solutions/{r['slug']}/{name}", wrap_supporting_page(site, r, name, source.read_text(encoding="utf-8")))
    for tag, _ in site.tags(rows):
        tagged = [r for r in rows if tag in r["doc"]["tags"]]
        put(f"tags/{tag}/index.html", listing(site, tagged, title=f'<span class="accent">#</span>{esc(tag)}', kicker="Tag collection",
                                             lede=f'{plural(len(tagged), "solution")} tagged “{tag}”.', depth=2, path=f"tags/{tag}/"))
    put("categories/index.html", categories_index(site, rows))
    for cat, _ in site.categories(rows):
        inside = [r for r in rows if (r["doc"]["category"] or "Other") == cat]
        put(f"categories/{slugify(cat)}/index.html", listing(site, inside, title=esc(cat), kicker="Category",
                                                             lede=f'{plural(len(inside), "solution")} in {cat}.', depth=2, path=f"categories/{slugify(cat)}/"))
    contributors = site.contributors(rows)
    put("contributors/index.html", contributors_page(site, contributors))
    for c in contributors:
        put(f"contributors/{c['key']}/index.html", contributor_page(site, c, by_slug))
    put("404.html", not_found(site))
    put("solutions.json", catalog_json(rows))
    for module in section_modules():
        for path, text in module.build(site, page).items():
            if path in out:
                raise ValueError(f"{module.__name__} wrote {path}, which another part of the build already owns")
            put(path, text)
    for old, text in alias_pages(site, out).items():
        put(old, text)
    for asset in sorted(ASSET_DIR.iterdir()):
        if asset.is_file():
            out[f"assets/{asset.name}"] = asset.read_bytes()
    return out


def write(out: dict[str, bytes], dist: Path) -> None:
    for path, data in out.items():
        target = dist / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_bytes() != data:
            target.write_bytes(data)
    # remove files this build no longer produces (dist/ is ours; everything in it comes from here)
    for existing in dist.rglob("*"):
        if existing.is_file() and existing.relative_to(dist).as_posix() not in out:
            existing.unlink()
    for folder in sorted((p for p in dist.rglob("*") if p.is_dir()), key=lambda p: -len(p.parts)):
        if not any(folder.iterdir()):
            folder.rmdir()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DIST)
    parser.add_argument("--check", action="store_true", help="build in memory and report differences against --out")
    args = parser.parse_args(argv)
    site = Site()
    out = build(site)
    if args.check:
        drift = []
        for path, data in out.items():
            target = args.out / path
            if not target.exists():
                drift.append(f"missing {path}")
            elif target.read_bytes() != data:
                drift.append(f"differs {path}")
        if drift:
            print("DRIFT:\n  " + "\n  ".join(drift[:40]), file=sys.stderr)
            return 1
        print(f"ok    {len(out)} files match {args.out}")
        return 0
    write(out, args.out)
    pages = sum(1 for p in out if p.endswith(".html"))
    digest = hashlib.sha256(b"".join(out[k] for k in sorted(out))).hexdigest()[:12]
    print(f"built {pages} pages, {len(out)} files -> {args.out} ({digest})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
