"""Positioning, field notes, attribution, metrics, and community resources."""

from tools.build_gallery_submissions import read_json
from tools.site_pages._content import (
    Document, document, items, link, render, section_page, source_body, text,
)


def fill(root, id, markup):
    node = root.find(id=id)
    node.children = Document(markup).root.children
    node.attrs.pop("hidden", None)
    node.attrs.pop("aria-busy", None)


def blog(site):
    source = "blog.html"
    root = document(site, source)
    data = read_json(site.root / "field-notes.json")
    fill(root, "notes-title", text(data["title"]))
    fill(root, "notes-tagline", text(data["tagline"]))
    featured = data["featured_workshop"]
    feature = (f'<p class="kick">Workshop of the month · {text(featured["month"])}</p>'
               f'<h2><a href="{text(featured["href"])}">{text(featured["title"])}</a></h2>'
               f'<p>{text(featured["industry"])}</p><p>{text(featured["summary"])}</p><dl class="kv">'
               + "".join(f'<dt>{label}</dt><dd>{text(featured[key])}</dd>' for key, label in (
                   ("who", "Who it is for"), ("what", "What you build"),
                   ("where", "Where it runs"), ("why", "Why it matters"))) + "</dl>"
               + "".join(f'<p><a href="{text(e["href"])}">{text(e["label"])}</a> · {text(e["note"])}</p>'
                         for e in featured["evidence"]))
    fill(root, "featured", feature)
    topics = ""
    for topic in data["topics"]:
        topics += f'<section class="topic" id="{text(topic["id"])}"><h2>{text(topic["title"])}</h2><p>{text(topic["blurb"])}</p>'
        for note in topic["notes"]:
            topics += (f'<article class="box" id="{text(note["id"])}"><h3>{text(note["question"])}</h3>'
                       f'<p>{text(note["answer"])}</p><p>{text(note["takeaway"])}</p>'
                       f'<a href="{text(note["link"]["href"])}">{text(note["link"]["label"])}</a></article>')
        topics += "</section>"
    fill(root, "topics", topics)
    deep = data["deep_dives"]
    fill(root, "deep-title", text(deep["title"]))
    fill(root, "deep-blurb", text(deep["blurb"]))
    fill(root, "jump", " ".join(
        f'<a class="chip" href="#{text(t["id"])}">{text(t["title"])}</a>'
        for t in [*data["topics"], deep]))
    fill(root, "reviewed", "These notes were last reviewed " + text(data["updated"]) + ".")
    return render(root.find(tag="body"), source, 1)


def front_page(site):
    source = "front-page.html"
    root = document(site, source)
    data = read_json(site.root / "front-page.json")
    fill(root, "front-page-title", text(data["title"]))
    fill(root, "front-page-tagline", text(data["tagline"]))
    fill(root, "jump", " ".join(
        f'<a class="chip" href="#{text(s["id"])}">{text(s["title"])}</a>'
        for s in data["sections"]))
    sections = ""
    for section in data["sections"]:
        sections += (f'<section id="{text(section["id"])}"><h2>{text(section["title"])}</h2>'
                     f'<p>{text(section["blurb"])}</p><div class="grid">')
        for entry in section["links"]:
            sections += (f'<article class="card"><h3><a href="{text(entry["href"])}">{text(entry["label"])}</a></h3>'
                         f'<span class="tag">{text(entry["kind"])}</span><p>{text(entry["why"])}</p></article>')
        sections += "</div></section>"
    fill(root, "sections", sections)
    fill(root, "status", "Last reviewed " + text(data["updated"]) + ".")
    sections = render(root.find(tag="body"), source, 1)
    destinations = [("why", "Why the Brainstem"), ("partners", "Partners and listing standards"),
                    ("metrics", "Public metrics"), ("blog", "Field notes"), ("release-notes", "Release notes"),
                    ("request", "Request files"), ("pitch", "Pitch playbook"),
                    ("achievements", "Workshop achievements"), ("community", "Community agents")]
    return sections + '<h2>About the library</h2><div class="grid">' + "".join(
        f'<a class="card flat" href="../{route}/">{label}</a>' for route, label in destinations) + "</div>"


def partners(site):
    data = site.partners
    body = (source_body(site, "partner-standards.html", 1)
            + f'<h2>Partner catalog</h2><p>{text(data["note"])}</p><p>{text(data["guidance"])}</p>'
            + f'<p>Snapshot: {text(data["snapshot_date"])} · {data["count"]} entries</p>')
    for partner in data["partners"]:
        body += (f'<h2>{link(partner["name"], partner["url"])}</h2>'
                 f'<p>{text(partner["description"])}</p><div class="grid">')
        for agent in data["agents"]:
            if agent["partner_id"] != partner["id"]:
                continue
            body += (f'<article class="card"><h3>{link(agent["name"], agent["source_url"])}</h3>'
                     f'<p>{text(agent["category"])} · {text(agent["product"])}</p>'
                     f'<p>{text(agent["description"])}</p>'
                     "<h4>What it does</h4>" + items(agent["what_it_does"])
                     + "<h4>Problem it solves</h4>" + items(agent["problem_it_solves"])
                     + "<h4>Who it helps</h4>" + items(agent["who_it_helps"]))
            if agent.get("partner_reported_outcome"):
                body += (f'<p><strong>Partner-reported, not independently verified by AIBAST:</strong> '
                         f'{text(agent["partner_reported_outcome"])}</p>')
            body += "</article>"
        body += "</div>"
    return body


def community(site):
    source = "community-agents.html"
    root = document(site, source)
    demos, resources = [], []
    for entry in site.community["tools"]:
        content = (f'<article class="card" data-demo-id="{text(entry["id"])}">'
                   f'<h3><a href="{text(entry["url"])}">{text(entry["name"])}</a></h3>'
                   f'<p>{text(entry["author"])}</p><p>{text(entry["description"])}</p>')
        if entry.get("kind") == "demo":
            content += f'<p>{text(entry.get("industry", ""))}</p>' + items(entry.get("products", []))
            if entry.get("thumbnail"):
                content += f'<img src="{text(entry["thumbnail"])}" alt="" loading="lazy">'
            if entry.get("onepager"):
                content += f'<p><a href="{text(entry["onepager"])}">One-pager</a></p>'
            if entry.get("graduated_to"):
                content += f'<p><a href="solutions/{text(entry["graduated_to"])}/quest.html">Now in the library</a></p>'
            demos.append(content + "</article>")
        else:
            resources.append(content + "</article>")
    fill(root, "demo-grid", "".join(demos) or '<p>No demos yet. Be the first to submit one.</p>')
    fill(root, "community-grid", "".join(resources))
    body = render(root.find(tag="body"), source, 1)
    body += f'<p>Snapshot: {text(site.community["snapshot_date"])} · {site.community["count"]} entries</p>'
    return body


def build(site, page):
    out = {}
    for route, source, title in (
        ("why", "why.html", "Why the RAPP Brainstem?"),
        ("release-notes", "release-notes.html", "Release notes"),
        ("request", "request-info.html", "Request one-pagers and demo videos"),
        ("pitch", "pitch-playbook.html", "Pitch playbook"),
        ("achievements", "achievements.html", "Workshop achievements"),
        ("metrics", "metrics.html", "Public library metrics"),
    ):
        body = source_body(site, source, 1)
        if route == "metrics":
            root = document(site, source)
            body = ('<div class="section-actions">'
                    + render(root.find(id="reportIssue"), source, 1)
                    + render(root.find(id="refresh"), source, 1)
                    + '<button id="themeToggle" hidden type="button">Theme</button></div>' + body)
        if route == "achievements":
            body += '<button id="themeToggle" hidden type="button">Theme</button>'
        out[f"{route}/index.html"] = section_page(site, page, route + "/", title, title, body)
    for route, title, body in (
        ("about", "About the library", front_page(site)),
        ("partners", "Partners and listing standards", partners(site)),
        ("blog", "Frontier Field Notes", blog(site)),
        ("community", "Community agents", community(site)),
    ):
        out[f"{route}/index.html"] = section_page(site, page, route + "/", title, title, body)
    # The dashboard and local achievement page read the same unchanged public snapshot.
    out["state/metrics.json"] = (site.root / "state/metrics.json").read_text(encoding="utf-8")
    if (site.root / "api/v1/github/repo.json").exists():
        out["api/v1/github/repo.json"] = (site.root / "api/v1/github/repo.json").read_text(encoding="utf-8")
    return out
