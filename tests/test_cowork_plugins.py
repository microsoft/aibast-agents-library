"""Every solution ships one Cowork plugin: one skill, its data beside it."""
import importlib.util
import json
import re
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_cowork_plugins", ROOT / "tools" / "build_cowork_plugins.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

SOLUTIONS = builder.solutions()


def test_there_is_a_plugin_for_every_solution_with_skills():
    assert len(SOLUTIONS) >= 72


@pytest.mark.parametrize("solution", SOLUTIONS, ids=lambda p: p.name)
def test_committed_plugin_matches_the_builder(solution):
    out = builder.target(solution)
    assert out.is_file(), f"run tools/build_cowork_plugins.py ({out.name} is missing)"
    assert out.read_bytes() == builder.build_zip(solution), f"{out.name} is stale"


@pytest.mark.parametrize("solution", SOLUTIONS, ids=lambda p: p.name)
def test_plugin_is_one_skill_with_a_strict_header(solution):
    slug = solution.name
    with zipfile.ZipFile(builder.target(solution)) as archive:
        names = archive.namelist()
        skills = [n for n in names if n.endswith("/SKILL.md")]
        assert skills == [f"skills/{slug}/SKILL.md"], "one plugin carries exactly one skill"
        manifest = json.loads(archive.read(".claude-plugin/plugin.json"))
        assert manifest["name"] == slug
        text = archive.read(skills[0]).decode("utf-8")
    front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert front, "the skill starts with a front-matter header"
    lines = front.group(1).splitlines()
    assert lines[0] == f"name: {slug}"
    # Cowork rejected an unquoted description that contained ": " (2026-11-12);
    # the description must be one double-quoted scalar.
    assert len(lines) == 2 and lines[1].startswith('description: "')
    assert len(json.loads(lines[1][len("description: "):])) < 1024


def test_library_page_offers_the_download():
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "-cowork-plugin.zip" in page and "Download Cowork plugin" in page
