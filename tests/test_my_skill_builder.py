import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = "https://microsoft.github.io/aibast-agents-library/"
PATHS = json.loads((ROOT / "api" / "v1" / "paths.json").read_text(encoding="utf-8"))


def _route(route_id):
    return next(r for r in PATHS["routes"] if r["id"] == route_id)


def test_every_named_skill_exists():
    for route in PATHS["routes"]:
        for name in route.get("skills", []):
            assert (ROOT / "skills" / name / "SKILL.md").is_file(), (route["id"], name)


def _build(route_id, area_name):
    route = _route(route_id)
    skills = {n: (ROOT / "skills" / n / "SKILL.md").read_text(encoding="utf-8") for n in route["skills"]}
    harness = (ROOT / "solutions" / "_shared" / "my-skill.js").read_text(encoding="utf-8") + (
        "\nprocess.stdout.write(globalThis.AIBASTMySkill.assembleSkill("
        + json.dumps({"route": route, "areaName": area_name, "skills": skills}) + "));\n")
    result = subprocess.run(["node"], input=harness, capture_output=True, text=True, check=True)
    return route, result.stdout


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js required")
@pytest.mark.parametrize("route_id, area_name", [
    ("customer", ""),
    ("demo", "Account Intelligence Agent"),
    ("build", "First-Time Fix Agent"),
])
def test_generated_skill_carries_each_child_and_only_library_urls(route_id, area_name):
    route, text = _build(route_id, area_name)
    assert text.startswith("---\nname: aibast-my-" + route_id + "\n")
    assert LIBRARY + "skills/aibast/SKILL.md" in text
    for name in route["skills"]:
        assert "## Part: " + name in text
        child = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        first_rule = next(line for line in child.split("---", 2)[2].splitlines() if line.startswith("- "))
        assert first_rule in text, (name, first_rule)
    if area_name:
        assert "- Area they chose: " + area_name in text
    allowed = set()
    for name in route["skills"]:
        allowed |= set(re.findall(r"https?://[^\s`)\"]+", (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")))
    for url in re.findall(r"https?://[^\s`)\"]+", text):
        assert url.startswith(LIBRARY) or url in allowed, url
