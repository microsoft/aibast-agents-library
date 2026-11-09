"""Content-only ports of the maintained source pages; no second page shell."""

from __future__ import annotations

import html
import posixpath
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import quote, unquote, urlsplit, urlunsplit

ROUTES = {
    "index.html": "", "library.html": "",
    "academy.html": "learn/academy/", "docs/tutorial.html": "learn/tutorial/",
    "docs/rapp-guide.html": "learn/guide/", "docs/vault/index.html": "learn/vault/",
    "docs/installer.html": "install/", "why.html": "why/",
    "partner-standards.html": "partners/", "metrics.html": "metrics/",
    "blog.html": "blog/", "release-notes.html": "release-notes/",
    "request-info.html": "request/", "pitch-playbook.html": "pitch/",
    "achievements.html": "achievements/", "community-agents.html": "community/",
    "community-tools.html": "community/", "front-page.html": "about/",
}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def business_text(value):
    return (str(value).replace("like the Blade Runner test", "as a daily diagnostic")
            .replace("Acme Insurance", "Sample insurer").replace("Acme", "Sample account"))


@dataclass
class Element:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def find(self, *, tag=None, id=None, cls=None):
        for node in self.walk():
            if ((tag is None or node.tag == tag)
                    and (id is None or node.attrs.get("id") == id)
                    and (cls is None or cls in node.attrs.get("class", "").split())):
                return node
        raise ValueError(f"Missing source element: {tag=}, {id=}, {cls=}")

    def walk(self):
        yield self
        for node in self.children:
            if isinstance(node, Element):
                yield from node.walk()

    def text(self):
        return "".join(n.text() if isinstance(n, Element) else n for n in self.children)


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Element("document")
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Element(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def document(site, source):
    return Document((site.root / source).read_text(encoding="utf-8")).root


def href(value, source, depth):
    """Resolve at the old page, then address the new route from the shell root."""
    parts = urlsplit(value)
    if parts.scheme or parts.netloc or not parts.path:
        return value
    path = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parts.path)))
    fragment = parts.fragment
    if path == "docs/vault/index.html" and unquote(fragment).endswith(".md"):
        path = "learn/vault/" + unquote(fragment)[:-3] + ".html"
        fragment = ""
    else:
        path = ROUTES.get(path, path + "/" if parts.path.endswith("/") and path != "." else path)
    safe = "/@-._~ " if path.startswith("learn/vault/") else "/@-._~"
    return urlunsplit(("", "", "../" * depth + quote(path, safe=safe), parts.query, fragment))


def render(node, source, depth, *, omit=()):
    if isinstance(node, str):
        return html.escape(business_text(node), quote=False)
    if node.tag in {"script", "style"} or node.attrs.get("id") in omit:
        return ""
    classes = node.attrs.get("class", "").split()
    if "topbar" in classes or "skip-link" in classes:
        return ""
    attrs = dict(node.attrs)
    # The installer illustration is a picture, not an alternative site palette.
    preserve_style = source == "docs/installer.html" and (
        attrs.get("id") == "vscode-demo" or any(c.startswith("vsd-") for c in classes)
    )
    if not preserve_style:
        attrs.pop("style", None)
        if re.search(r"display\s*:\s*none", node.attrs.get("style", "")):
            attrs["style"] = "display:none"
    for key in list(attrs):
        if key.startswith("on"):
            attrs["data-port-" + key[2:]] = attrs.pop(key)
        elif source is not None and key in {"href", "src", "poster", "action"}:
            attrs[key] = href(attrs[key], source, depth)
    if attrs.get("id") == "main":
        attrs["id"] = "section-main"
    if node.tag == "main":
        attrs["data-source-main"] = ""
    if "viewbox" in attrs:
        attrs["viewBox"] = attrs.pop("viewbox")
    tag = "div" if node.tag in {"body", "main", "document"} else node.tag
    attributes = "".join(
        f' {key}' if value is None else f' {key}="{html.escape(value, quote=True)}"'
        for key, value in attrs.items()
    )
    start = f"<{tag}{attributes}>"
    if tag in VOID:
        return start
    return start + "".join(render(n, source, depth, omit=omit) for n in node.children) + f"</{tag}>"


def source_body(site, source, depth, *, omit=()):
    return render(document(site, source).find(tag="body"), source, depth, omit=omit)


def section_page(site, page, route, title, description, body, *, active="About"):
    depth = route.count("/")
    return page(site, title=title, description=description,
                body=f'<div class="wrap section-content">{body}</div>',
                depth=depth, active=active, path=route, page_type=route.strip("/").replace("/", "-"))


def link(label, target, *, source="index.html", depth=1):
    return f'<a href="{html.escape(href(target, source, depth), quote=True)}">{html.escape(label)}</a>'


def text(value):
    return html.escape(business_text(value), quote=True)


def items(values):
    return "<ul>" + "".join(f"<li>{text(v)}</li>" for v in values) + "</ul>"
