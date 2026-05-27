#!/usr/bin/env python3
"""Kernel-currency tests — the local brainstem IS the rapp-installer grail kernel.

`brainstem.py` (the kernel) and `index.html` (the chat UI) are FROZEN: they must match the canonical
grail in rapp-installer (`rapp_brainstem/`) byte-for-byte and are never hand-edited (RAPP canon). These
tests assert this repo's local-install tier is on grail **v0.6.0**. When the grail is intentionally
bumped, update GRAIL_VERSION + GRAIL_SHA256 + GRAIL_INDEX_SHA256 here in the same change that re-vendors
brainstem.py + index.html.

Grail source: https://raw.githubusercontent.com/kody-w/rapp-installer/main/rapp_brainstem/
"""
import os
import sys
import hashlib
import unittest

BRAINSTEM_DIR = os.path.dirname(os.path.abspath(__file__))
if BRAINSTEM_DIR not in sys.path:
    sys.path.insert(0, BRAINSTEM_DIR)

GRAIL_VERSION = "0.6.0"
GRAIL_SHA256 = "f7fb359bbe8b6ba3db3665d81cb8e573a266c716278d8d21d8962ea40821e5aa"
GRAIL_INDEX_SHA256 = "82445dad957c7dae8a280c9b851fb80eeef1b55c1a2945b636a4556f6d6dd0b0"  # rapp_brainstem/index.html (chat UI)


class TestKernelCurrency(unittest.TestCase):
    def test_version_pinned_to_grail(self):
        v = open(os.path.join(BRAINSTEM_DIR, "VERSION")).read().strip()
        self.assertEqual(v, GRAIL_VERSION, f"brainstem VERSION {v!r} != grail {GRAIL_VERSION!r}")

    def test_brainstem_matches_grail_sha(self):
        data = open(os.path.join(BRAINSTEM_DIR, "brainstem.py"), "rb").read()
        got = hashlib.sha256(data).hexdigest()
        self.assertEqual(got, GRAIL_SHA256,
                         "brainstem.py has drifted from the rapp-installer grail kernel — it is a "
                         "frozen kernel (never hand-edit; re-vendor from the grail instead).")

    def test_chat_ui_matches_grail(self):
        data = open(os.path.join(BRAINSTEM_DIR, "index.html"), "rb").read()
        got = hashlib.sha256(data).hexdigest()
        self.assertEqual(got, GRAIL_INDEX_SHA256,
                         "index.html (the chat UI) has drifted from the grail — it ships with the "
                         "kernel; re-vendor it too.")

    def test_kernel_exposes_contract_routes(self):
        import brainstem  # imports the Flask app; decorators register the routes
        rules = {r.rule for r in brainstem.app.url_map.iter_rules()}
        for route in ("/chat", "/health", "/version"):
            self.assertIn(route, rules, f"grail kernel is missing the {route} route")

    def test_kernel_reports_its_version(self):
        import brainstem
        self.assertEqual(getattr(brainstem, "VERSION", None), GRAIL_VERSION)


if __name__ == "__main__":
    unittest.main()
