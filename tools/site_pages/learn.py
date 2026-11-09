"""Learning routes and the Markdown reference vault."""

from __future__ import annotations

import posixpath
import re
from urllib.parse import quote, unquote, urlsplit

from tools.build_gallery_submissions import markdown_to_html, read_json
from tools.build_site import card, steps
from tools.site_pages._content import (
    Document, document, href, items, link, render, section_page, source_body, text,
)


def academy(site):
    data = read_json(site.root / "academy.json")
    root = document(site, "academy.html")
    hero = root.find(cls="hero")
    body = render(hero, "academy.html", 2, omit=("liveSummary",))
    body = body.replace('<span id="dataDisclaimer"></span>', text(data["disclaimer"]))
    body += '<dl class="section-stats">' + "".join(
        f"<div><dt>{text(k.replace('_', ' '))}</dt><dd>{text(v)}</dd></div>"
        for k, v in data["summary"].items()) + "</dl>"
    body += "<h2>Capability journey</h2>" + steps([
        f'<strong>{text(stage["title"])}</strong><p>{text(stage["description"])}</p>'
        for stage in data["ecosystem"]])
    body += '<h2>Choose a learning path</h2><div class="grid">'
    for path in data["paths"]:
        body += (f'<article class="card" id="path-{text(path["id"])}">'
                 f'<h3>{text(path["title"])}</h3><p>{text(path["description"])}</p>'
                 f'<p>{text(path["audience"])}</p><p>{text(path["level"])} · {path["course_count"]} courses</p>'
                 + items(path["categories"])
                 + "<ul>" + "".join(
                     f'<li><a href="#course-{text(slug)}">{text(site.docs[slug]["name"])}</a></li>'
                     for slug in path["course_slugs"]) + "</ul></article>")
    body += "</div><h2>Practice milestones</h2>" + steps([
        f'<strong>{text(m["title"])} · {m["points"]} points</strong><p>{text(m["description"])}</p>'
        for m in data["milestones"]])
    body += ('<h2 id="catalog">Build something real</h2>'
             '<label for="course-search">Search courses and skills</label>'
             '<input id="course-search" type="search" placeholder="Search outcomes, platforms, skills">'
             '<label for="course-path">Learning path</label><select id="course-path"><option value="">All paths</option>'
             + "".join(f'<option value="{text(p["id"])}">{text(p["title"])}</option>' for p in data["paths"])
             + f'</select><p id="course-count" role="status">{len(data["courses"])} courses</p><div class="grid" id="courses">')
    rows = {r["slug"]: r for r in site.solutions()}
    for course in data["courses"]:
        slug = course["slug"]
        primary = card(rows[slug], "../../")
        details = (f'<p>{text(course["description"])}</p>'
                   f'<p>{text(course["industry"])} · {text(course["journey_stage"])}</p>'
                   f'<p>{course["demo_cases"]} demo cases · {course["manual_steps"]} manual steps · '
                   f'{course["skill_count"]} skills · Added {text(course["added_at"])}</p>'
                   f'<p>Demo video: {"Available" if course["has_demo_video"] else "Not available"}. '
                   f'One-pager: {"Available" if course["has_onepager"] else "Not available"}.</p>'
                   "<h4>Who it helps</h4>" + items(course["personas"])
                   + "<h4>Platforms</h4>" + items(course["platforms"])
                   + "<h4>Outcomes</h4>" + items(course["outcomes"])
                   + "<h4>Skills</h4><ul>" + "".join(
                       f'<li>{link(s["title"], s["path"], depth=2)}<p>{text(s["description"])}</p></li>'
                       for s in course["skills"]) + "</ul>")
        resources = " · ".join(link(label, course[key], depth=2) for label, key in (
            ("Workshop quest", "quest_url"), ("Field guide", "field_guide_url"),
            ("Manual tutorial", "manual_url"), ("Evidence report", "evidence_url")))
        body += (f'<div class="course" id="course-{text(slug)}" data-course="{text(slug)}" '
                 f'data-paths="{text("|".join(course["path_ids"]))}" '
                 f'data-search="{text(str(course).lower())}">'
                 + primary + f'<p class="course-resources">{resources}</p>'
                 + '<details><summary>Course details</summary>' + details + "</details></div>")
    body += ("</div><p id=\"course-empty\" hidden>No courses match these filters.</p>"
             "<h2>Your learning</h2><p>Progress is private by default and never submitted by this page. "
             "Review or resume saved milestones in "
             + link("Achievements", "achievements.html", depth=2) + ".</p>"
             '<p id="academy-progress" role="status"></p>')
    body += render(root.find(cls="footer"), "academy.html", 2)
    return body


def vault(site, page):
    folder = site.root / "docs" / "vault"
    files = sorted(folder.rglob("*.md"))
    titles = {}
    for file in files:
        raw = file.read_text(encoding="utf-8")
        title = re.search(r"^title:\s*(.+)$", raw, re.M)
        titles[file.stem] = file.relative_to(folder).with_suffix(".html").as_posix()
        if title:
            titles[title[1].strip('"')] = titles[file.stem]
    out = {}
    index = "<h1>Reference vault</h1><p>Linked notes on the production guide, building agents, and the RAPP/1 protocol.</p>"
    groups = {}
    for file in files:
        relative = file.relative_to(folder)
        route = "learn/vault/" + relative.with_suffix(".html").as_posix()
        depth = route.count("/")
        raw = file.read_text(encoding="utf-8")
        front = re.match(r"\A---\n(.*?)\n---\n", raw, re.S)
        metadata = front[1] if front else ""
        markdown = raw[front.end():] if front else raw
        title_match = re.search(r"^title:\s*(.+)$", metadata, re.M)
        title = title_match[1].strip('"') if title_match else file.stem
        def wiki(match):
            target, _, label = match[1].replace(r"\|", "|").partition("|")
            name, marker, fragment = target.partition("#")
            destination = titles.get(name)
            if destination is None:
                raise ValueError(f"{relative}: unresolved vault link {target}")
            url = "../" * depth + "learn/vault/" + quote(destination)
            if marker:
                url += "#" + quote(fragment.lower().replace(" ", "-"))
            return f"[{label or name}]({url})"
        # Do not interpret example wiki syntax inside fenced code.
        chunks = re.split(r"(```[^\n]*\n.*?```)", markdown, flags=re.S)
        rendered = []
        for chunk in chunks:
            if chunk.startswith("```"):
                code = chunk.split("\n", 1)[1].rsplit("```", 1)[0]
                rendered.append(f"<pre><code>{text(code)}</code></pre>")
            else:
                inline = re.split(r"(`[^`]+`)", chunk)
                chunk = "".join(part if part.startswith("`") else re.sub(r"\[\[([^]]+)\]\]", wiki, part)
                                for part in inline)
                rendered.append(markdown_to_html(chunk))
        fragment = Document("\n".join(rendered)).root
        for node in fragment.walk():
            if node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                node.attrs["id"] = re.sub(r"[^\w -]", "", node.text().lower()).replace(" ", "-")
        for node in fragment.walk():
            if "href" not in node.attrs:
                continue
            value = node.attrs["href"]
            parts = urlsplit(value)
            if parts.scheme or not parts.path or value.startswith("../" * depth + "learn/vault/"):
                continue
            target = posixpath.normpath(posixpath.join(relative.parent.as_posix(), unquote(parts.path)))
            if target.endswith(".md") and (folder / target).is_file():
                node.attrs["href"] = "../" * depth + "learn/vault/" + quote(target[:-3] + ".html")
                if parts.fragment:
                    node.attrs["href"] += "#" + parts.fragment
            else:
                # The original viewer resolves ordinary Markdown URLs at its vault root.
                node.attrs["href"] = href(value, "docs/vault/index.html", depth)
        for node in fragment.walk():
            value = node.attrs.get("href")
            if value and not urlsplit(value).scheme and "learn/vault/" in value:
                node.attrs["href"] = unquote(value)
        # URLs have already been rebased; rendering must not rebase them again.
        content = render(fragment, None, 0)
        provenance = f"<details><summary>Source and provenance</summary><pre>{text(metadata)}</pre></details>" if metadata else ""
        body = f'<p><a href="{"../" * depth}learn/vault/">Reference vault</a></p>' + content + provenance
        out[route] = page(site, title=title, description="RAPP/1 reference: " + title,
                          body=f'<article class="wrap section-content">{body}</article>',
                          depth=depth, active="Learn", path=route, page_type="learn-vault-note")
        groups.setdefault(relative.parent.as_posix(), []).append(
            f'<li><a href="../../learn/vault/{text(relative.with_suffix(".html").as_posix())}">{text(title)}</a></li>')
    for group, links in groups.items():
        index += f'<h2>{text("Welcome" if group == "." else group)}</h2><ul>{"".join(links)}</ul>'
    out["learn/vault/index.html"] = section_page(site, page, "learn/vault/", "Reference vault",
                                               "RAPP/1 notes and production guide reference.", index, active="Learn")
    return out


def build(site, page):
    entries = [
        ("academy", "Academy", "Choose a course, follow a workshop, and record practice milestones."),
        ("tutorial", "Five-minute start", "Install the Brainstem and write your first agent."),
        ("guide", "Production guide", "Follow the 14-step RAPP process and its human quality gates."),
        ("practice", "Windows practice", "Practice using PowerShell on a pretend Windows 11 computer."),
        ("vault", "Reference vault", "Read the linked notes behind the guide and the RAPP/1 protocol."),
    ]
    hub = '<h1>Learn</h1><p>Build an agent, practise the setup, and understand the path to production.</p><div class="grid">'
    hub += "".join(f'<a class="card flat" href="../learn/{slug}/"><h2>{text(title)}</h2><p>{text(description)}</p></a>'
                   for slug, title, description in entries) + "</div>"
    out = {"learn/index.html": section_page(site, page, "learn/", "Learn", "Practical learning resources.", hub, active="Learn")}
    out["learn/academy/index.html"] = section_page(site, page, "learn/academy/", "Academy",
                                                  "Courses, learning paths, and practice milestones.", academy(site), active="Learn")
    for route, source, title in (
        ("tutorial", "docs/tutorial.html", "Five-minute Brainstem start"),
        ("guide", "docs/rapp-guide.html", "RAPP production guide"),
    ):
        body = source_body(site, source, 2)
        if route == "guide":
            root = document(site, source)
            body = (render(root.find(cls="topbar-nav"), source, 2)
                    + render(root.find(cls="topbar-actions"), source, 2) + body)
        out[f"learn/{route}/index.html"] = section_page(
            site, page, f"learn/{route}/", title, title, body, active="Learn")
    out["learn/practice/index.html"] = section_page(
        site, page, "learn/practice/", "Windows practice",
        "Practise on a pretend Windows 11 computer without changing your real PC.",
        '<h1>Windows practice</h1><p>Practice on a pretend Windows 11 computer first. Nothing there touches your real PC.</p>'
        '<p><a class="button" href="../../docs/practice/windows.html">Open the Windows 11 practice computer</a></p>', active="Learn")
    out["docs/practice/windows.html"] = (site.root / "docs/practice/windows.html").read_bytes().decode("utf-8")
    out.update(vault(site, page))
    return out
