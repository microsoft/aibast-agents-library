"""The generated site's 404 page, workshop pages and recorded-conversation links (tools/build_site.py)."""
from __future__ import annotations

import io
import os
import re
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import build_site, design_tokens  # noqa: E402
from tools.build_gallery_submissions import read_json  # noqa: E402

ADDED = ROOT / "federation" / "copilot-studio-gallery" / "field-service-dispatch"


class SiteWorkshops(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = build_site.Site(ROOT)
        cls.out = build_site.build(cls.site)
        cls.rows = {r["slug"]: r for r in cls.site.solutions()}

    def layered_row(self):
        agent = sorted(ADDED.glob("*_agent.py"))[0]
        slug = "building-permit-processing"
        self.site.layered[slug] = {"agent": agent, "answers": read_json(ADDED / "reference-answers.json")}
        self.addCleanup(self.site.layered.pop, slug)
        return self.rows[slug]

    def test_404_resolves_from_the_site_root_at_any_depth(self):
        html = self.out["404.html"].decode("utf-8")
        head = html.split("</head>")[0]
        base = head.index('b.setAttribute("href","/aibast-agents-library/")')
        self.assertLess(base, head.index("assets/site.css"))  # before every link it must govern
        with mock.patch.dict(os.environ, {"AIBAST_SITE_URL": "https://example.github.io/fork-name"}):
            self.assertIn('"/fork-name/"', build_site.not_found(self.site))

    def test_every_recorded_scenario_gets_a_watch_link(self):
        html = self.out["solutions/building-permit-processing/index.html"].decode("utf-8")
        panel = html.split('id="panel-how"')[1].split("</section>")[0]
        watched = re.findall(r"scenario=([a-z0-9-]+)", panel)
        recorded = [s.partition("scenario=")[2] for s in self.site.docs["building-permit-processing"]["try"]["scenarios"]]
        self.assertGreater(len(recorded), len(self.site.library["building-permit-processing"]["sample_prompts"]))
        self.assertEqual(sorted(set(watched)), sorted(recorded))
        self.assertIn("Review routing and due date", panel)  # the title from the scenario record

    def test_workshop_link_only_when_the_workshop_is_built(self):
        for slug in self.rows:
            html = self.out[f"solutions/{slug}/index.html"].decode("utf-8")
            if "Start the workshop" in html:
                self.assertIn(f"workshops/{slug}/index.html", self.out, slug)

    def test_skill_and_page_name_the_same_host(self):
        row = self.layered_row()
        with mock.patch.dict(os.environ, {"AIBAST_SITE_URL": "https://example.github.io/aibast-agents-library/"}):
            skill = build_site.workshop_skill(self.site, row)
            page = build_site.workshop(self.site, row)
        for text in (skill, page):
            self.assertNotIn("microsoft.github.io/aibast-agents-library/install", text)
            self.assertIn("https://example.github.io/aibast-agents-library/install.sh", text)
            self.assertIn("https://example.github.io/aibast-agents-library/workshops/building-permit-processing/", text)

    def test_fingerprint_step_starts_in_the_agents_folder(self):
        page = build_site.workshop(self.site, self.layered_row())
        self.assertIn("cd ~/.brainstem/src/rapp_brainstem/agents", page)
        self.assertIn("cd $env:USERPROFILE\\.brainstem\\src\\rapp_brainstem\\agents", page)

    def test_every_workshop_class_has_a_rule(self):
        page = build_site.workshop(self.site, self.layered_row())
        main = page.split('<main id="main">')[1].split("</main>")[0]
        used = {c for attr in re.findall(r'class="([^"]+)"', main) for c in attr.split()}
        css = (ROOT / "tools" / "site" / "site.css").read_text(encoding="utf-8") + design_tokens.render_tokens()
        defined = set(re.findall(r"\.([A-Za-z][\w-]*)", css))
        self.assertEqual(used - defined, set())

    def test_check_explains_a_build_without_federation(self):
        err = io.StringIO()
        with redirect_stderr(err):
            code = build_site.main(["--check", "--out", str(ROOT / "no-such-dist")])
        self.assertEqual(code, 1)
        self.assertIn("differences", err.getvalue())
        self.assertIn("without --federation", err.getvalue())


if __name__ == "__main__":
    unittest.main()
