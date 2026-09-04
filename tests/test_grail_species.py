"""Grail species regression: the vendored Brainstem kernel stays kernel-compatible.

Offline (always): diff ``rapp_brainstem/`` + ``install.sh`` against the pinned
Grail shape in ``rapp/GRAIL-SPECIES.json``.  Any missing route, BasicAgent
method, shim, discovery rule, port, response field, or install-layout constant
is a species break and fails the suite.  Additions are allowed.

Live (opt-in, ``GRAIL_SPECIES_LIVE=1``): fetch ``kody-w/rapp-installer@main``
and diff against it.  Items the Grail has that we lack are reported as
"pending kernel sync" and do not fail; the run fails only when the vendored
kernel drops compatibility with the pinned contract.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import grail_species  # noqa: E402

PIN = REPO_ROOT / "rapp" / "GRAIL-SPECIES.json"
KERNEL = REPO_ROOT / "rapp_brainstem"
INSTALLER = REPO_ROOT / "install.sh"


def _vendored_shape() -> dict:
    return grail_species.compute_shape(KERNEL, INSTALLER)


class PinnedShapeIsWellFormed(unittest.TestCase):
    def test_pin_exists_and_parses(self):
        self.assertTrue(PIN.exists(), f"missing {PIN}")
        data = json.loads(PIN.read_text(encoding="utf-8"))
        for key in (
            "shape_version",
            "kernel_version",
            "routes",
            "basic_agent",
            "discovery",
            "env_keys",
            "default_port",
            "chat_response_field",
            "shims",
            "inventory",
            "install_layout",
            "source",
        ):
            self.assertIn(key, data, f"pin lacks {key}")
        self.assertEqual(data["shape_version"], grail_species.SHAPE_VERSION)
        self.assertTrue(data["routes"], "pin has no routes")
        self.assertEqual(data["chat_response_field"], "response")
        self.assertEqual(data["default_port"], 7071)

    def test_pin_source_is_traceable(self):
        source = json.loads(PIN.read_text(encoding="utf-8"))["source"]
        self.assertEqual(source["repo"], grail_species.GRAIL_REPO)
        self.assertRegex(source["commit"], r"^[0-9a-f]{40}$")
        self.assertIn("fetched_at", source)


class VendoredKernelIsSameSpecies(unittest.TestCase):
    def test_vendored_matches_pinned_grail_shape(self):
        grail = json.loads(PIN.read_text(encoding="utf-8"))
        result = grail_species.diff_shapes(grail, _vendored_shape())
        self.assertFalse(
            result["breaks"],
            "Vendored rapp_brainstem/ broke the Grail species contract:\n"
            + grail_species.render_table(result),
        )

    def test_vendored_shape_reads_the_kernel(self):
        shape = _vendored_shape()
        self.assertRegex(shape["kernel_version"] or "", r"^\d+\.\d+\.\d+$")
        self.assertIn("POST /chat", shape["routes"])
        self.assertIn("GET /health", shape["routes"])
        self.assertEqual(shape["discovery"]["glob"], "*_agent.py")
        self.assertTrue(shape["discovery"]["flat"])
        self.assertEqual(shape["basic_agent"]["class"], "BasicAgent")
        self.assertIn("perform", shape["basic_agent"]["methods"])
        self.assertEqual(shape["install_layout"]["BRAINSTEM_HOME"], "$HOME/.brainstem")
        self.assertEqual(shape["install_layout"]["VENV_DIR"], "$BRAINSTEM_HOME/venv")
        self.assertEqual(
            shape["install_layout"]["SRC_DIR"], "$BRAINSTEM_HOME/src/rapp_brainstem"
        )


@unittest.skipUnless(os.environ.get("GRAIL_SPECIES_LIVE") == "1", "set GRAIL_SPECIES_LIVE=1")
class LiveGrailComparison(unittest.TestCase):
    def test_live_grail_main(self):
        with tempfile.TemporaryDirectory() as tmp:
            outdir = Path(tmp)
            source = grail_species.fetch_grail(outdir, ref="main")
            live = grail_species.compute_shape(
                outdir / grail_species.KERNEL_DIR, outdir / grail_species.INSTALLER
            )
        live["source"] = source
        vendored = _vendored_shape()
        result = grail_species.diff_shapes(live, vendored)
        table = grail_species.render_table(result)
        print(f"\nLive Grail {source['repo']}@{source['commit'][:12]}\n{table}")

        # Anything the live Grail has that we lack is a pending kernel sync,
        # not a regression of this repository.
        pending = [b for b in result["breaks"] if ": missing " in b]
        hard = [b for b in result["breaks"] if ": missing " not in b]
        if pending:
            print("pending kernel sync:")
            for item in pending:
                print(f"  - {item}")
        if live.get("kernel_version") != vendored.get("kernel_version"):
            print(
                f"pending kernel sync: kernel_version grail={live.get('kernel_version')} "
                f"vendored={vendored.get('kernel_version')}"
            )

        # Compatibility is judged against the pinned contract; a live break that
        # is not simply "the Grail moved ahead" means we changed a shared item.
        pinned = json.loads(PIN.read_text(encoding="utf-8"))
        pinned_result = grail_species.diff_shapes(pinned, vendored)
        self.assertFalse(
            hard + pinned_result["breaks"],
            "Vendored kernel is no longer compatible with the Grail:\n" + table,
        )


if __name__ == "__main__":
    unittest.main()
