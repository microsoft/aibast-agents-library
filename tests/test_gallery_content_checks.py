"""The Copilot Studio Gallery's five publication checks, read mechanically over our submissions/.
Every folder we author must pass (tools/check_gallery_content.py); inbound folders are only noted."""
from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import check_gallery_content as cgc  # noqa: E402


class ContentChecks(unittest.TestCase):
    def test_every_authored_folder_passes(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cgc.main([str(ROOT)])
        self.assertEqual(rc, 0, buf.getvalue())

    def test_checker_catches_each_kind(self):
        fixture = ROOT / "tests" / "fixtures" / "gallery_shape" / "flows-only-sample"
        findings = cgc.check_folder(fixture)
        self.assertTrue(any("check 1" in f for f in findings), findings)   # fixture README lacks review wording
        self.assertTrue(any("flow" in f for f in findings), findings)      # declared flow not named in README

    def test_connector_label(self):
        self.assertEqual(cgc.connector_label("/providers/Microsoft.PowerApps/apis/shared_workiqmcp"), "Work IQ MCP (`shared_workiqmcp`)")
        self.assertEqual(cgc.declared_connections_xml(
            "<connectionreferences><connectionreference><connectorid>/providers/x/apis/shared_foo</connectorid></connectionreference></connectionreferences>"), ["shared_foo"])

    def test_honest_negation_is_not_an_overclaim(self):
        self.assertFalse(cgc.OVERCLAIM.search("This is a sample.") )
        import re
        text = "This sample is not production-ready."
        m = cgc.OVERCLAIM.search(text)
        self.assertTrue(m)
        self.assertTrue(re.search(r"\b(not|never|no|isn't|is not|without)\b[^.]{0,30}$", text[:m.start()], re.I))


if __name__ == "__main__":
    unittest.main()
