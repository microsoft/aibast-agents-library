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


def test_every_plugin_shows_its_library_card_name_in_cowork():
    """Cowork title-cases the lowercase name ("Ask Hr"); displayName is the label.

    Proven in Cowork on 2026-11-13: displayName sets the list and step label;
    display_name and title are ignored; SKILL.md accepts no extra fields.
    """
    import json
    import re
    import zipfile
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    seen = set()
    packages = sorted(root.glob("solutions/*/exports/*-cowork-plugin.zip"))
    assert len(packages) >= 72
    for package in packages:
        slug = package.parent.parent.name
        with zipfile.ZipFile(package) as archive:
            manifest = json.loads(archive.read(".claude-plugin/plugin.json"))
            skill = archive.read(f"skills/{slug}/SKILL.md").decode("utf-8")
        card = json.loads((root / "api/v1/solutions" / f"{slug}.json").read_text(encoding="utf-8"))["name"]
        assert manifest["displayName"] == card, slug
        assert re.fullmatch(r"[a-z0-9.-]+", manifest["name"]), slug
        assert re.search(rf"^name: {re.escape(slug)}$", skill, re.M), slug
        assert f"# {card}\n" in skill, slug
        assert card not in seen, f"duplicate plugin label {card}"
        seen.add(card)
