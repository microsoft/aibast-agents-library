"""The site generator (tools/build_site.py) honours docs/SITE-REWRITE.md:
one input tree, every route present, one palette, every internal link resolving, idempotent."""

from __future__ import annotations

import json
import posixpath
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import build_site, design_tokens  # noqa: E402

HREF_RE = re.compile(r'(?:href|src)="([^"#?]*)')


class SiteBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = build_site.Site(ROOT)
        cls.out = build_site.build(cls.site)
        cls.rows = cls.site.solutions()
        cls.pages = {k: v.decode("utf-8") for k, v in cls.out.items() if k.endswith(".html")}

    def test_every_listed_solution_has_a_page(self):
        listed = set(self.site.config["submissions"])
        built = {k.split("/")[1] for k in self.out if k.startswith("solutions/") and k.endswith("/index.html")}
        self.assertEqual(listed, built)

    def test_routes_from_the_design(self):
        for path in ("index.html", "built-by-aibast/index.html", "categories/index.html", "contributors/index.html",
                     "contributors/aibast/index.html", "404.html", "solutions.json", "assets/site.css", "assets/site.js"):
            self.assertIn(path, self.out, path)
        self.assertTrue(any(k.startswith("tags/") for k in self.out))
        self.assertTrue(any(k.startswith("categories/") and k != "categories/index.html" for k in self.out))

    def test_pages_use_the_one_palette_and_declare_none(self):
        block = design_tokens.render_tokens()
        for path, html in self.pages.items():
            self.assertIn(block, html, f"{path} is missing the design-token block")
            self.assertEqual(design_tokens.local_palette_declarations(html), [], f"{path} declares a palette token")
        css = self.out["assets/site.css"].decode("utf-8")
        self.assertEqual(design_tokens.local_palette_declarations("<style>" + css + "</style>"), [], "site.css declares a palette token")
        self.assertNotRegex(css, r"#[0-9a-fA-F]{3,8}\b", "site.css carries a colour literal")

    def test_internal_links_resolve(self):
        known = set(self.out)
        tree_files = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts}
        missing = []
        for path, html in self.pages.items():
            depth = path.count("/")
            for href in HREF_RE.findall(html):
                if not href or href.startswith(("http", "mailto:", "data:", "javascript:")):
                    continue
                target = posixpath.normpath(posixpath.join(posixpath.dirname(path), href)) if not href.startswith("/") else href.lstrip("/")
                if target in (".", "") or href.endswith("/"):
                    target = "" if target in (".", "") else target + "/"
                    target += "index.html"
                if target.startswith("../"):
                    missing.append(f"{path} -> {href} (escapes the site)")
                    continue
                if target in known or target in tree_files or target + "/index.html" in known:
                    continue
                missing.append(f"{path} -> {href}")
        self.assertEqual(missing[:20], [], f"{len(missing)} dangling links")

    def test_catalog_json_matches_the_pages(self):
        payload = json.loads(self.out["solutions.json"])
        self.assertEqual(len(payload), len(self.rows))
        for row in payload:
            self.assertIn(f"solutions/{row['slug']}/index.html", self.out)
            for key in ("name", "description", "tags", "category", "download", "skillCount"):
                self.assertIn(key, row)

    def test_cards_show_only_recorded_facts(self):
        home = self.pages["index.html"]
        self.assertEqual(home.count('class="card"'), len(self.rows) + min(3, sum(1 for r in self.rows if r["featured"])))
        for r in self.rows:
            if not r["lib"].get("assets", {}).get("demo_video"):
                page = self.pages[f"solutions/{r['slug']}/index.html"]
                self.assertIn("No demo video yet", page)

    def test_demo_before_download(self):
        for r in self.rows[:5]:
            page = self.pages[f"solutions/{r['slug']}/index.html"]
            self.assertLess(page.index("Try it without deploying"), page.index("Get this solution"))

    def test_build_is_deterministic(self):
        again = build_site.build(build_site.Site(ROOT))
        self.assertEqual(again, self.out)


if __name__ == "__main__":
    unittest.main()
