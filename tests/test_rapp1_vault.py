"""The RAPP/1 reference vault stays valid, pinned, and wired into the guide.

The vault at docs/vault/ expands docs/rapp-guide.html. These tests hold four
properties:

1. Every derived file (manifest, bundle, index, llms files, zip) matches the
   notes on disk, so the viewer, the Obsidian download and AI readers all see
   the same bytes.
2. Every note passes the build checks: frontmatter, wikilinks, the upstream
   pin, the documentation tone bar, and no personal-fork addresses.
3. The Obsidian download is reproducible and opens as a vault.
4. The guide links into the vault, and every link it makes resolves.
"""

from __future__ import annotations

import io
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import build_rapp1_vault as vault  # noqa: E402

VAULT = ROOT / "docs" / "vault"
GUIDE = ROOT / "docs" / "rapp-guide.html"


def test_derived_files_match_the_notes():
    assert vault.main(["--check"]) == 0


def test_rendering_is_deterministic():
    assert vault.render_all() == vault.render_all()


def test_every_guide_step_has_a_vault_note():
    manifest = json.loads((VAULT / "manifest.json").read_text(encoding="utf-8"))
    paths = {note["path"] for note in manifest["notes"]}
    steps = [p for p in paths if p.startswith("Production Guide/Step ")]
    assert len(steps) == 14, sorted(steps)


def test_protocol_notes_are_pinned_to_the_upstream_commit():
    pinned = 0
    for section in vault.PINNED_SECTIONS:
        for path in (VAULT / section).glob("*.md"):
            meta, _ = vault.parse_frontmatter(path.read_text(encoding="utf-8"))
            assert meta.get("upstream_commit") == vault.UPSTREAM_COMMIT, path.name
            pinned += 1
    assert pinned >= 10


def test_validation_rejects_a_broken_note():
    good = {"path": "Protocol/The Frame.md", "raw": "", "body": "# The Frame\n", "meta": {
        "title": "The Frame", "section": "Protocol", "status": "published", "hook": "h", "source": "s",
        "upstream_commit": vault.UPSTREAM_COMMIT,
    }}
    vault.validate([good])
    cases = {
        "wikilink": {**good, "body": "# The Frame\n[[No Such Note]]\n"},
        "pin": {**good, "meta": {**good["meta"], "upstream_commit": "0" * 40}},
        "tone": {**good, "body": "# The Frame\nA magic trick.\n"},
        "identity": {**good, "raw": "see https://github.com/kody-w/rapp-1"},
        "title": {**good, "meta": {**good["meta"], "title": "Frame"}},
    }
    for name, note in cases.items():
        try:
            vault.validate([note])
        except vault.VaultError:
            continue
        raise AssertionError(f"{name} violation was accepted")


def test_obsidian_download_is_a_vault():
    archive = zipfile.ZipFile(io.BytesIO((VAULT / "rapp1-vault.zip").read_bytes()))
    names = archive.namelist()
    assert vault.ZIP_ROOT + ".obsidian/app.json" in names
    assert vault.ZIP_ROOT + "README.md" in names
    manifest = json.loads((VAULT / "manifest.json").read_text(encoding="utf-8"))
    for note in manifest["notes"]:
        assert vault.ZIP_ROOT + note["path"] in names, note["path"]


def test_viewer_loads_only_local_files():
    html = (VAULT / "index.html").read_text(encoding="utf-8")
    sources = re.findall(r'<script[^>]+src="([^"]+)"', html)
    assert sources == ["./marked.min.js", "./vault.js"]
    for asset in ("vault.js", "vault.css", "marked.min.js", "vendor/marked-LICENSE.txt", "NOTICE.md"):
        assert (VAULT / asset).is_file(), asset


def test_guide_links_into_the_vault_resolve():
    html = GUIDE.read_text(encoding="utf-8")
    manifest = json.loads((VAULT / "manifest.json").read_text(encoding="utf-8"))
    paths = {note["path"] for note in manifest["notes"]}
    links = re.findall(r'href="vault/([^"]+)"', html)
    assert len(links) >= 20
    for link in links:
        page, _, note = link.partition("#")
        assert (VAULT / page).is_file(), link
        if note:
            assert unquote(note) in paths, link
    assert html.count('class="vault-deeper"') == 14
    assert 'id="reference"' in html
