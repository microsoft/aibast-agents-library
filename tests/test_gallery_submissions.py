"""The submissions/ tree is the gallery-ready layout of AIBAST industry solutions.

It mirrors the microsoft/copilot-studio-gallery submission contract exactly:
submissions/<slug>/{metadata.json, README.md, solution/}. The tree is built by
tools/build_gallery_submissions.py from the exported Copilot Studio solutions, so
these tests hold the build idempotent and the sidecars within the gallery's schema.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "build_gallery_submissions.py"
INPUT = ROOT / "tools" / "gallery_submissions.json"
OUT = ROOT / "submissions"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
GALLERY_CATEGORIES = {
    "Customer service", "Sales & marketing", "IT & security", "Operations",
    "Project & communications management", "HR", "Finance", "Legal & compliance",
    "Productivity & knowledge", "Agent Building", "Governance", "Other",
}


def listed_slugs():
    return sorted(json.loads(INPUT.read_text(encoding="utf-8"))["submissions"])


def test_tree_matches_the_build():
    result = subprocess.run(
        [sys.executable, str(TOOL), "--check"], cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("slug", listed_slugs())
def test_submission_meets_gallery_contract(slug):
    assert SLUG_RE.match(slug)
    folder = OUT / slug
    metadata = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["name"].strip()
    assert 0 < len(metadata["description"]) <= 320
    assert metadata["tags"] and all(0 < len(tag) <= 40 for tag in metadata["tags"])
    assert metadata["category"] in GALLERY_CATEGORIES
    assert metadata["author"].strip()
    assert "previewWorkflow" not in metadata, "agent-only solutions must omit previewWorkflow"

    readme = (folder / "README.md").read_text(encoding="utf-8")
    assert readme.startswith(f"# {metadata['name']}\n")
    assert "## Prerequisites and import" in readme

    solution = folder / "solution"
    for required in ("solution.xml", "customizations.xml", "[Content_Types].xml"):
        assert (solution / required).is_file(), required
    bots = list(solution.glob("bots/*/bot.xml"))
    assert len(bots) == 1
    bot_xml = bots[0].read_text(encoding="utf-8")
    from xml.sax.saxutils import escape as xml_escape
    assert f"<name>{xml_escape(metadata['name'])}</name>" in bot_xml
    assert "cliagent-" in bot_xml
    config = json.loads((bots[0].parent / "configuration.json").read_text(encoding="utf-8"))
    assert config["agentSettings"]["model"]["series"] == "Auto"
    assert config["agentSettings"]["greetingText"].strip()
    assert "<Managed>0</Managed>" in (solution / "solution.xml").read_text(encoding="utf-8")

    for path in folder.rglob("*"):
        assert not path.is_symlink(), path
        if path.is_file():
            assert path.stat().st_size <= 2 * 1024 * 1024, path
