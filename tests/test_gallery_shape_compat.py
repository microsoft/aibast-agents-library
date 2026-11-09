"""Two-way compatibility with the Copilot Studio Gallery folder shape.

Inbound: any submissions/<slug>/ folder that follows the gallery contract (metadata.json + README.md +
exploded solution/) renders in this site with no entry in tools/gallery_submissions.json, including
forms our own exports never use (an `authors` list, a flows-only package, several agents).
Outbound: every one of our submissions stays in that same shape, so it can move the other way unchanged.
"""
from __future__ import annotations

import json
import shutil
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import build_site  # noqa: E402
from tools.build_gallery_submissions import discover_submissions, gallery_docs, metadata_authors  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "gallery_shape"


class GalleryShapeInbound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The generator reads the whole repository root (docs/, why.html, state/ ...), so the
        # fixtures are placed in the real submissions/ tree for the build and removed afterwards.
        cls.root = ROOT
        cls.added = []
        for fixture in sorted(FIXTURES.iterdir()):
            target = ROOT / "submissions" / fixture.name
            if target.exists():
                raise RuntimeError(f"{target} already exists; the fixture slug must stay unused")
            shutil.copytree(fixture, target)
            cls.added.append(target)
        try:
            cls.ours = sorted(slug for slug in discover_submissions(ROOT) if slug not in {f.name for f in FIXTURES.iterdir()})[0]
            cls.site = build_site.Site(ROOT)
            cls.out = build_site.build(cls.site)
        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        for target in cls.added:
            shutil.rmtree(target, ignore_errors=True)

    def test_folders_are_discovered_without_a_config_entry(self):
        found = discover_submissions(self.root)
        self.assertIn("flows-only-sample", found)
        self.assertIn("two-agent-sample", found)
        self.assertNotIn("flows-only-sample", self.site.config["submissions"])

    def test_every_discovered_folder_gets_a_page_and_a_catalog_row(self):
        catalog = {row["slug"]: row for row in json.loads(self.out["solutions.json"])}
        for slug in ("flows-only-sample", "two-agent-sample", self.ours):
            self.assertIn(f"solutions/{slug}/index.html", self.out, slug)
            self.assertIn(slug, catalog)

    def test_authors_list_and_single_author_both_render(self):
        page = self.out["solutions/flows-only-sample/index.html"].decode()
        self.assertIn("Sample Author One", page)
        self.assertIn('href="https://example.com/two"', page)
        self.assertNotIn("contributors/aibast", page.split('class="byline"')[1].split("</p>")[0])
        page = self.out["solutions/two-agent-sample/index.html"].decode()
        self.assertIn("Sample Team", page)
        self.assertEqual(metadata_authors({"author": "A", "authorUrl": "u"}), [{"name": "A", "url": "u"}])
        self.assertEqual(metadata_authors({"authors": [{"name": "B"}]}), [{"name": "B", "url": None}])

    def test_flows_only_package_has_no_agent_and_a_built_download(self):
        docs, _ = gallery_docs(self.root, build_site.RAW_BASE)
        doc = docs["flows-only-sample"]
        self.assertEqual(doc["counts"]["agents"], 0)
        self.assertEqual(doc["version"], "1.0.0.0")
        self.assertIn("downloads/flows-only-sample.zip", self.out)
        names = zipfile.ZipFile(__import__("io").BytesIO(self.out["downloads/flows-only-sample.zip"])).namelist()
        self.assertIn("solution.xml", names)
        self.assertIn("Workflows/Sample-123.json", names)
        page = self.out["solutions/flows-only-sample/index.html"].decode()
        self.assertIn("flows and components rather than a conversational agent", page)
        self.assertIn("downloads/flows-only-sample.zip", page)
        catalog = {row["slug"]: row for row in json.loads(self.out["solutions.json"])}
        self.assertEqual(catalog["flows-only-sample"]["makeup"], "Flows")

    def test_two_agents_are_both_listed(self):
        docs, _ = gallery_docs(self.root, build_site.RAW_BASE)
        doc = docs["two-agent-sample"]
        self.assertEqual([a["name"] for a in doc["agents"]], ["Agent A", "Agent B"])
        self.assertEqual(doc["counts"]["skills"], 1)
        page = self.out["solutions/two-agent-sample/index.html"].decode()
        self.assertIn("Agent A", page)
        self.assertIn("Agent B", page)

    def test_our_own_solution_still_links_the_aibast_contributor(self):
        page = self.out[f"solutions/{self.ours}/index.html"].decode()
        self.assertIn("contributors/aibast/", page.split('class="byline"')[1].split("</p>")[0])

    def test_build_is_byte_stable(self):
        again = build_site.build(build_site.Site(self.root))
        self.assertEqual(self.out["downloads/flows-only-sample.zip"], again["downloads/flows-only-sample.zip"])


class GalleryShapeOutbound(unittest.TestCase):
    def test_every_submission_has_the_gallery_contract_files(self):
        slugs = discover_submissions(ROOT)
        self.assertGreaterEqual(len(slugs), 72)
        for slug in slugs:
            folder = ROOT / "submissions" / slug
            meta = json.loads((folder / "metadata.json").read_text())
            for key in ("name", "description", "tags"):
                self.assertIn(key, meta, f"{slug} metadata lacks {key}")
            self.assertTrue(metadata_authors(meta), f"{slug} has no author")
            self.assertTrue((folder / "README.md").exists(), slug)
            self.assertTrue((folder / "solution" / "solution.xml").exists(), slug)


if __name__ == "__main__":
    unittest.main()
