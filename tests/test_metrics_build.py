"""
The library page and the metrics dashboard both read fields the registry
builder adds. These tests pin that contract so a builder change cannot quietly
empty either page.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "registry.json"


def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_registry_exposes_stacks():
    reg = load_registry()
    assert reg["stats"]["total_stacks"] > 0
    assert reg["stacks"], "registry.json must carry a stacks block for library.html"
    for stack in reg["stacks"]:
        for field in ("stack", "vertical", "display_name", "path", "agents", "agent_count"):
            assert field in stack, f"stack {stack.get('stack')} missing {field}"
        assert stack["agent_count"] == len(stack["agents"])


def test_every_agent_has_library_fields():
    reg = load_registry()
    names = {a["name"] for a in reg["agents"]}
    for a in reg["agents"]:
        assert a.get("_sha256"), f"{a['name']} missing _sha256"
        # templates/ holds connector templates and the agent generator - library
        # infrastructure, not industry solutions, so they sit outside a stack.
        if "/templates/" in a["_file"]:
            continue
        assert a.get("_stack"), f"{a['name']} is not inside a *_stack folder"
        assert a.get("_stack_vertical"), f"{a['name']} missing _stack_vertical"
    # Every stack member must resolve to a real agent, or the stack install
    # command on the library page emits a 404 curl.
    for stack in reg["stacks"]:
        for member in stack["agents"]:
            assert member in names, f"stack {stack['stack']} references unknown agent {member}"


def test_metrics_build_offline_exits_zero(tmp_path):
    out = tmp_path / "metrics.json"
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "build_metrics.py"),
         "--offline", "--out", str(out)],
        capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, result.stderr[:800]
    doc = json.loads(out.read_text())
    assert doc["totals"]["agents"] == len(load_registry()["agents"])
    assert doc["leaderboards"]["stacks"], "stack leaderboard must not be empty"
    assert doc["leaderboards"]["verticals"], "vertical breakdown must not be empty"
