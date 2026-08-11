import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "state" / "architecture_level2.json"
LIBRARY = ROOT / "library.html"


def expected_agents():
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
    return {
        agent["name"]
        for agent in registry["agents"]
        if (agent.get("_solution") or {}).get("architecture")
    }


def test_level2_catalog_covers_every_existing_level1_architecture():
    document = json.loads(CATALOG.read_text(encoding="utf-8"))
    assert document["schema"] == "aibast-architecture-l2-catalog/1.0"
    assert document["count"] == 51
    assert set(document["solutions"]) == expected_agents()

    domain_limits = {
        "knowledge": (2, 5),
        "intelligence_processing": (3, 6),
        "clients_user_interface": (2, 5),
        "management_reporting": (2, 5),
    }
    fingerprints = set()
    for agent, architecture in document["solutions"].items():
        assert architecture["agent"] == agent
        assert set(architecture["domains"]) == set(domain_limits)
        for domain, (minimum, maximum) in domain_limits.items():
            items = architecture["domains"][domain]
            assert minimum <= len(items) <= maximum
        assert 3 <= len(architecture["tools"]) <= 8
        assert 4 <= len(architecture["supporting_features"]) <= 7
        all_items = [
            item
            for items in architecture["domains"].values()
            for item in items
        ] + architecture["tools"] + architecture["supporting_features"]
        assert all(
            0 < len(item["name"]) <= 60
            and 0 < len(item["detail"]) <= 140
            for item in all_items
        )
        fingerprint = tuple(
            item["name"]
            for items in architecture["domains"].values()
            for item in items
        )
        assert fingerprint not in fingerprints
        fingerprints.add(fingerprint)


def test_level2_builder_reproduces_committed_catalog(tmp_path):
    output = tmp_path / "architecture_level2.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_architecture_level2.py"),
            "--input",
            str(ROOT / "state" / "architecture_level2_sources"),
            "--out",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    expected = json.loads(CATALOG.read_text(encoding="utf-8"))
    actual = json.loads(output.read_text(encoding="utf-8"))
    actual["generated_at"] = expected["generated_at"]
    assert actual == expected


def test_library_renders_level1_then_level2_architecture():
    text = LIBRARY.read_text(encoding="utf-8")
    assert "state/architecture_level2.json${stamp}" in text
    assert "function architectureLevel2HTML(agentName)" in text
    assert "<span>L1</span>" in text
    assert "<span>L2</span>" in text
    assert "Knowledge" in text
    assert "Intelligence layer / processing" in text
    assert "Clients / user interface" in text
    assert "Management / reporting" in text
    assert "Supporting features &amp; foundation models" in text
