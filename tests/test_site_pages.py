"""Section ports retain source facts and the shared shell, including offline content."""

import html
import posixpath
import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from tools import build_site, design_tokens
from tools.site_pages import about, install, learn
from tools.site_pages._content import Document, business_text, document, href

ROOT = Path(__file__).resolve().parents[1]


class SectionPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = build_site.Site(ROOT)
        cls.sections = {}
        for module in (about, install, learn):
            cls.sections.update(module.build(cls.site, build_site.page))
        cls.out = build_site.build(cls.site)

    def test_every_requested_route_is_built(self):
        routes = (
            "learn", "learn/academy", "learn/tutorial", "learn/guide", "learn/practice", "learn/vault",
            "install", "why", "partners", "metrics", "blog", "release-notes", "request", "pitch",
            "achievements", "community", "about",
        )
        for route in routes:
            with self.subTest(route=route):
                self.assertIn(route + "/index.html", self.out)
        for source in (ROOT / "docs/vault").rglob("*.md"):
            path = "learn/vault/" + source.relative_to(ROOT / "docs/vault").with_suffix(".html").as_posix()
            self.assertIn(path, self.out)
        self.assertIn("docs/practice/windows.html", self.out)

    def test_section_pages_use_only_the_shared_palette(self):
        tokens = design_tokens.render_tokens()
        for path, content in self.sections.items():
            if not path.endswith(".html"):
                continue
            with self.subTest(path=path):
                self.assertIn(tokens, content)
                self.assertEqual(design_tokens.local_palette_declarations(content), [])
                if path != "docs/practice/windows.html":
                    root = Document(content).root
                    self.assertEqual(len([n for n in root.walk() if n.tag == "main"]), 1)
                    self.assertFalse(any(k.startswith("on") for n in root.walk() for k in n.attrs))

    def test_academy_has_all_72_courses_and_their_resources(self):
        source = build_site.read_json(ROOT / "academy.json")
        page = self.sections["learn/academy/index.html"]
        root = Document(page).root
        courses = [n for n in root.walk() if "data-course" in n.attrs]
        self.assertEqual(len(courses), 72)
        self.assertEqual({n.attrs["data-course"] for n in courses}, {c["slug"] for c in source["courses"]})
        for course in source["courses"]:
            node = root.find(id="course-" + course["slug"])
            links = {n.attrs["href"] for n in node.walk() if "href" in n.attrs}
            self.assertIn("../../solutions/" + course["slug"] + "/", links)
            for key in ("quest_url", "field_guide_url", "manual_url", "evidence_url"):
                self.assertIn("../../" + course[key], links)
        self.assertIn(source["disclaimer"], html.unescape(page))
        for path in source["paths"]:
            self.assertIn(path["title"], html.unescape(page))
        for milestone in source["milestones"]:
            self.assertIn(milestone["description"], html.unescape(page))

    def test_installer_commands_are_verbatim(self):
        source = document(self.site, "docs/installer.html")
        port = Document(self.sections["install/index.html"]).root
        for id in ("brainstem-cmd", "brainstem-win-cmd"):
            command = source.find(id=id).text()
            self.assertEqual(port.find(id=id).text(), command)
            self.assertIn(command, html.unescape(self.sections["install/index.html"]))
        for id in ("brainstem", "hippocampus", "nervous-system", "vscode-demo"):
            self.assertEqual(source.find(id=id).text(), port.find(id=id).text())
        self.assertEqual(port.find(id="download-link").attrs["href"], "../install.command")
        for name in ("install.sh", "install.ps1", "install.cmd", "install.command", "docs/install.sh"):
            self.assertNotIn(name, self.sections)

    def test_practice_computer_and_metrics_snapshot_are_unchanged(self):
        self.assertEqual(self.out["docs/practice/windows.html"], (ROOT / "docs/practice/windows.html").read_bytes())
        self.assertEqual(self.out["state/metrics.json"], (ROOT / "state/metrics.json").read_bytes())

    def test_real_section_html_links_resolve(self):
        missing = []
        for path, content in self.sections.items():
            if not path.endswith(".html"):
                continue
            for node in Document(content).root.walk():
                for attr in ("href", "src"):
                    value = node.attrs.get(attr)
                    if not value:
                        continue
                    parts = urlsplit(value)
                    if parts.scheme or parts.netloc or not parts.path:
                        continue
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(path), unquote(parts.path)))
                    if parts.path.endswith("/") or target == ".":
                        target = ("" if target == "." else target + "/") + "index.html"
                    if target not in self.out and not (ROOT / target).is_file():
                        missing.append(f"{path} -> {value}")
        self.assertEqual(missing, [])

    def test_guide_preserves_all_sections_code_and_quiz_facts(self):
        source = document(self.site, "docs/rapp-guide.html")
        port = Document(self.sections["learn/guide/index.html"]).root
        for node in source.walk():
            if node.attrs.get("class") == "content-section" or "content-section" in node.attrs.get("class", "").split():
                self.assertEqual(business_text(node.text()), port.find(id=node.attrs["id"]).text())
        for step in range(1, 15):
            self.assertIsNotNone(port.find(id=f"step{step}"))
        self.assertEqual(source.find(id="quiz-principles").text(), port.find(id="quiz-principles").text())
        self.assertNotIn("Blade Runner", port.text())
        self.assertNotIn("Acme", port.text())

    def test_vault_wiki_links_fences_and_relative_urls(self):
        for path, page in self.sections.items():
            if not path.startswith("learn/vault/") or not path.endswith(".html"):
                continue
            root = Document(page).root
            def prose(node):
                if isinstance(node, str):
                    return node
                if node.tag in {"code", "pre", "script", "style"}:
                    return ""
                return "".join(prose(child) for child in node.children)
            self.assertNotRegex(prose(root), r"\[\[[^\]]+\]\]")
            for node in root.walk():
                target = node.attrs.get("href", "").split("#")[0]
                if target and not urlsplit(target).scheme and "learn/vault/" in target:
                    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(path), unquote(target)))
                    if resolved.endswith("learn/vault"):
                        resolved += "/index.html"
                    self.assertIn(resolved, self.sections.keys(), f"{path} -> {target}")
        wire = self.sections["learn/vault/Protocol/The Wire.html"]
        self.assertIn("<pre><code>POST /chat", wire)
        self.assertIn('href="../../../learn/vault/Protocol/The Frame.html"', wire)
        self.assertEqual(href("vault/index.html#Protocol%2FThe%20Wire.md", "docs/rapp-guide.html", 2),
                         "../../learn/vault/Protocol/The Wire.html")

    def test_json_backed_pages_render_without_loading_placeholders(self):
        for path in ("blog/index.html", "community/index.html", "about/index.html"):
            page = self.sections[path]
            self.assertNotRegex(page, r"Loading (?:the index|demos|related resources)")
        notes = build_site.read_json(ROOT / "field-notes.json")
        blog = html.unescape(self.sections["blog/index.html"])
        for topic in notes["topics"]:
            for note in topic["notes"]:
                self.assertIn(note["question"], blog)
                self.assertIn(note["answer"], blog)
        self.assertIn("November 6, 2026", blog)
        partners = html.unescape(self.sections["partners/index.html"])
        for agent in self.site.partners["agents"]:
            self.assertIn(agent["source_url"], partners)
            if agent.get("partner_reported_outcome"):
                self.assertIn(agent["partner_reported_outcome"], partners)


if __name__ == "__main__":
    unittest.main()
