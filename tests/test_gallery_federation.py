"""Federation (tools/federate_gallery.py + tools/build_site.py --federation): another library in the
Copilot Studio Gallery folder shape is listed beside ours, read from its own tree unchanged, with
provenance, its own download, and no copy in this repository. A shared slug lists both versions, each linking the other."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import build_site, federate_gallery  # noqa: E402
from tools.build_gallery_submissions import discover_submissions  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "gallery_shape"


class Federation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="federation-"))
        source = federate_gallery.sources()[0]
        tree = cls.tmp / source["key"]
        shutil.copytree(FIXTURES, tree / "submissions")
        # a folder whose slug we already own: ours must win
        cls.ours = discover_submissions(ROOT)[0]
        shutil.copytree(FIXTURES / "two-agent-sample", tree / "submissions" / cls.ours)
        (tree / ".federation.json").write_text(json.dumps({
            "key": source["key"], "commit": "0" * 40, "fetched_at": "2026-11-09T00:00:00+00:00",
            "downloads": {"two-agent-sample": "https://example.com/their/two-agent-sample.zip"}}))
        cls.source = source
        cls.before = sorted(p.name for p in (ROOT / "submissions").iterdir())
        cls.site = build_site.Site(ROOT, federation_dir=cls.tmp)
        cls.out = build_site.build(cls.site)
        cls.catalog = {row["slug"]: row for row in json.loads(cls.out["solutions.json"])}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_source_list_is_well_formed(self):
        for key in ("key", "name", "repository", "branch", "raw_base", "tree_base", "page_base", "license"):
            self.assertIn(key, self.source)
        self.assertTrue(self.source["raw_base"].startswith("https://raw.githubusercontent.com/"))

    def test_their_solutions_are_listed_with_provenance(self):
        for slug in ("flows-only-sample", "two-agent-sample"):
            self.assertIn(f"solutions/{slug}/index.html", self.out)
            self.assertEqual(self.catalog[slug]["origin"], self.source["name"])
            self.assertEqual(self.catalog[slug]["originUrl"], self.source["page_base"] + slug + "/")
        page = self.out["solutions/two-agent-sample/index.html"].decode()
        self.assertIn(f'from <a href="{self.source["page_base"]}two-agent-sample/"', page)
        self.assertIn("listed here unchanged", page)
        self.assertNotIn("contributors/aibast", page.split('class="byline"')[1].split("</p>")[0])
        self.assertIn(f'>{self.source["name"]}</span>', self.out["index.html"].decode())

    def test_their_package_is_downloaded_from_them_never_rebuilt_here(self):
        page = self.out["solutions/two-agent-sample/index.html"].decode()
        self.assertIn('href="https://example.com/their/two-agent-sample.zip" data-download', page)
        self.assertNotIn("downloads/two-agent-sample.zip", self.out)
        self.assertNotIn("downloads/flows-only-sample.zip", self.out)   # no published download: link to their page
        self.assertIn("Get it there", self.out["solutions/flows-only-sample/index.html"].decode())

    def test_same_slug_lists_both_versions_and_each_links_the_other(self):
        suffix = self.source["variant_suffix"]
        theirs = f"{self.ours}-{suffix}"
        self.assertIsNone(self.catalog[self.ours]["origin"])                       # ours keeps the address
        self.assertEqual(self.catalog[theirs]["variantOf"], self.ours)
        self.assertEqual(self.catalog[theirs]["origin"], self.source["name"])
        ours_page = self.out[f"solutions/{self.ours}/index.html"].decode()
        their_page = self.out[f"solutions/{theirs}/index.html"].decode()
        self.assertIn("contributors/aibast/", ours_page.split('class="byline"')[1].split("</p>")[0])
        self.assertIn("Other versions of this solution", ours_page)
        self.assertIn(f'solutions/{theirs}/"', ours_page)
        self.assertIn("Other versions of this solution", their_page)
        self.assertIn(f'solutions/{self.ours}/"', their_page)
        # their own address for the variant is the original slug in their library
        self.assertEqual(self.catalog[theirs]["originUrl"], self.source["page_base"] + self.ours + "/")

    def test_no_two_output_paths_differ_only_by_case(self):
        lowered = [p.lower() for p in self.out]
        self.assertEqual(len(lowered), len(set(lowered)))

    def test_the_build_publishes_what_it_streamed_and_from_which_commit(self):
        status = json.loads(self.out["federation.json"])
        self.assertEqual(status["schema"], "aibast-gallery-federation-status/1.0")
        source = status["sources"][0]
        self.assertEqual(source["commit"], "0" * 40)
        self.assertEqual(source["count"], 3)   # two fixtures plus the shared-slug variant
        self.assertEqual(status["ours"], len(discover_submissions(ROOT)))

    def test_nothing_of_theirs_lands_in_this_repository(self):
        self.assertEqual(self.before, sorted(p.name for p in (ROOT / "submissions").iterdir()))

    def test_without_a_fetch_the_site_is_ours_alone(self):
        plain = build_site.Site(ROOT, federation_dir=self.tmp / "missing")
        self.assertEqual(sorted(plain.docs), discover_submissions(ROOT))


class AddedValue(unittest.TestCase):
    """What this library adds to another library's solution (sample data as a knowledge file, a
    recorded chat) is kept in our repository and published beside their unchanged package."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="federation-added-"))
        source = federate_gallery.sources()[0]
        tree = cls.tmp / "fed" / source["key"]
        shutil.copytree(FIXTURES, tree / "submissions")
        (tree / ".federation.json").write_text(json.dumps({"key": source["key"], "commit": "0" * 40, "fetched_at": "2026-11-09T00:00:00+00:00", "downloads": {}}))
        added = cls.tmp / "added" / source["key"] / "two-agent-sample"
        (added / "knowledge").mkdir(parents=True)
        (added / "knowledge" / "aibast_sample-synthetic-records.md").write_text("# Synthetic records\n\nInvented.\n")
        (added / "library.json").write_text(json.dumps({
            "schema": "aibast-library-solution/1.0", "slug": "two-agent-sample", "added_note": "Ours.", "industries": ["Healthcare"],
            "capabilities": ["Does a thing"], "sample_prompts": [{"label": "Ask", "prompt": "What is on file?"}]}))
        (added / "transcripts.json").write_text(json.dumps({"captured_at": "2026-11-09T00:00:00Z", "surface": "test", "environment": "test",
                                                             "turns": [{"id": "T-01", "title": "Ask", "prompt": "What is on file?", "response": "One record."}]}))
        cls.tree = tree
        cls.before = {p.relative_to(tree).as_posix(): p.read_bytes() for p in tree.rglob("*") if p.is_file()}
        cls.site = build_site.Site(ROOT, federation_dir=cls.tmp / "fed", added_dir=cls.tmp / "added")
        cls.out = build_site.build(cls.site)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_their_tree_is_untouched(self):
        after = {p.relative_to(self.tree).as_posix(): p.read_bytes() for p in self.tree.rglob("*") if p.is_file()}
        self.assertEqual(after, self.before)

    def test_sample_data_package_is_theirs_plus_one_knowledge_file(self):
        import io
        import zipfile
        names = set(zipfile.ZipFile(io.BytesIO(self.out["downloads/two-agent-sample-with-sample-data.zip"])).namelist())
        theirs = {p.relative_to(self.tree / "submissions/two-agent-sample/solution").as_posix()
                  for p in (self.tree / "submissions/two-agent-sample/solution").rglob("*") if p.is_file()}
        self.assertTrue(theirs <= names)
        extra = sorted(names - theirs)
        self.assertEqual(len(extra), 2)
        self.assertTrue(extra[0].endswith("/botcomponent.xml") and extra[1].endswith("/filedata/aibast_sample-synthetic-records.md"))
        self.assertLessEqual(len(extra[0].split("/")[1]), 100)

    def test_recorded_chat_is_playable(self):
        scenario = json.loads(self.out["api/v1/scenarios/two-agent-sample-t-01.json"])
        self.assertEqual(scenario["answer"]["answer"], "One record.")
        self.assertEqual(scenario["answer"]["kind"], "recorded")
        solution = json.loads(self.out["api/v1/solutions/two-agent-sample.json"])
        self.assertEqual(solution["try"]["scenarios"][0]["id"], scenario["id"])

    def test_page_says_what_is_ours_and_what_is_theirs(self):
        page = self.out["solutions/two-agent-sample/index.html"].decode()
        for text in ("Added by the", "From the authors", "Get it with sample data", "Get the original" if "Get the original" in page else "From the", "Try the demo chat"):
            self.assertIn(text, page)
        self.assertIn("with their package unchanged", page)

    def test_solutions_without_additions_are_unchanged(self):
        self.assertNotIn("downloads/flows-only-sample-with-sample-data.zip", self.out)
        self.assertNotIn("Added by the", self.out["solutions/flows-only-sample/index.html"].decode())


if __name__ == "__main__":
    unittest.main()
