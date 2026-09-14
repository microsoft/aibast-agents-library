import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from tools import solution_covers as covers


ROOT = Path(__file__).resolve().parents[1]


def test_published_solution_covers_are_deterministic_decorative_svg():
    registry = json.loads((ROOT / "registry.json").read_text())
    slugs = [
        agent["_solution"]["package"]["slug"]
        for agent in registry["agents"]
        if agent.get("_solution")
    ]
    compositions = set()
    for slug in slugs:
        vertical = covers.vertical_for(slug, registry)
        svg = covers.cover_svg(slug, vertical)
        assert svg == covers.cover_svg(slug, vertical)
        image = ET.fromstring(svg)
        assert image.tag == "{http://www.w3.org/2000/svg}svg"
        assert image.attrib["viewBox"] == "0 0 960 300"
        assert image.attrib["aria-hidden"] == "true"
        assert image.attrib["focusable"] == "false"
        assert covers.VERTICAL_GLYPH[vertical] in svg
        assert "var(--cp-" in svg
        assert not image.findall(".//{http://www.w3.org/2000/svg}script")
        compositions.add(covers.composition_of(slug))
    assert compositions == {"signal", "routing", "mesh"}


def test_empty_slug_is_rejected_and_unknown_vertical_has_a_documented_mark():
    with pytest.raises(ValueError, match="needs a slug"):
        covers.cover_svg("")
    assert covers.cover_svg("example", "unknown") == covers.cover_svg("example")


def test_refresh_is_explicit_idempotent_and_preserves_other_notes(tmp_path, monkeypatch):
    tool = tmp_path / "tools/solution_covers.py"
    tool.parent.mkdir()
    monkeypatch.setattr(covers, "__file__", str(tool))
    notes = {"title": "Keep this title", "featured_workshop": {
        "slug": "account-intelligence", "summary": "Keep this summary",
    }}
    notes_path = tmp_path / "field-notes.json"
    notes_path.write_text(json.dumps(notes))
    (tmp_path / "registry.json").write_text(json.dumps({"stacks": [{
        "stack": "account_intelligence", "vertical": "b2b_sales",
    }]}))
    assert covers._refresh_field_notes() == 0
    actual = json.loads(notes_path.read_text())
    assert actual["title"] == notes["title"]
    assert actual["featured_workshop"] == {
        **notes["featured_workshop"],
        "vertical": "b2b_sales",
        "cover": covers.cover_svg("account-intelligence", "b2b_sales"),
    }
    first = notes_path.read_bytes()
    assert covers._refresh_field_notes() == 0
    assert notes_path.read_bytes() == first


@pytest.mark.parametrize("argument", ["--help", "--unknown"])
def test_cli_help_and_invalid_arguments_do_not_write_site_content(tmp_path, argument):
    tool = tmp_path / "tools/solution_covers.py"
    tool.parent.mkdir()
    shutil.copyfile(ROOT / "tools/solution_covers.py", tool)
    notes = tmp_path / "field-notes.json"
    notes.write_text('{"preserve": true}\n')
    result = subprocess.run(
        [sys.executable, str(tool), argument],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    assert result.returncode == (0 if argument == "--help" else 2)
    assert notes.read_text() == '{"preserve": true}\n'
