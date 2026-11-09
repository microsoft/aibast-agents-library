"""Inbound aggregation (tools/aggregate_gallery.py): carried gallery entries stay byte-identical to the
pinned gallery commit and get a provenance sidecar; our own slugs can never be replaced."""
from __future__ import annotations

import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import aggregate_gallery as ag  # noqa: E402


class AggregateGallery(unittest.TestCase):
    def test_allowlist_is_well_formed_and_never_names_our_slugs(self):
        inbound = json.loads(ag.INBOUND.read_text())
        ours = set(json.loads(ag.OURS.read_text())["submissions"])
        self.assertEqual(inbound["schema"], "aibast-gallery-inbound/1.0")
        self.assertEqual(set(inbound["slugs"]) & ours, set())

    def test_our_slug_is_refused(self):
        ours = sorted(json.loads(ag.OURS.read_text())["submissions"])[0]
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ag.main(["--only", ours])
        self.assertEqual(rc, 1)
        self.assertIn("refused", buf.getvalue())

    def test_sidecar_carries_provenance(self):
        contract = json.loads(ag.CONTRACT.read_text())
        side = ag.sidecar("some-entry", {"name": "x"}, contract)
        self.assertEqual(side["origin"]["name"], "Copilot Studio Gallery")
        self.assertEqual(side["origin"]["commit"], contract["commit"])
        self.assertTrue(side["origin"]["url"].endswith("/submissions/some-entry/"))

    @unittest.skipUnless(os.environ.get("GALLERY_CHECKER_DIR"), "needs a gallery checkout (GALLERY_CHECKER_DIR)")
    def test_carried_folders_match_the_pinned_commit(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ag.main(["--check"])
        self.assertEqual(rc, 0, buf.getvalue())


if __name__ == "__main__":
    unittest.main()
