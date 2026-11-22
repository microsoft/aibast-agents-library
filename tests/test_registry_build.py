"""
Test that build_registry.py runs successfully.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_registry_build_exits_zero():
    registry_path = REPO_ROOT / "registry.json"
    original = registry_path.read_bytes()
    generated = None
    try:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "build_registry.py")],
            capture_output=True, text=True, timeout=60,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            generated = json.loads(registry_path.read_text(encoding="utf-8"))
    finally:
        registry_path.write_bytes(original)
    assert result.returncode == 0, (
        f"build_registry.py failed (exit {result.returncode})\n"
        f"stdout: {result.stdout[:500]}\n"
        f"stderr: {result.stderr[:500]}"
    )
    original_agents = {
        agent["name"]: agent
        for agent in json.loads(original.decode("utf-8"))["agents"]
    }
    generated_agents = {agent["name"]: agent for agent in generated["agents"]}
    for name in (
        "@aibast-agents-library/procurement-agent",
        "@aibast-agents-library/procurement-support",
    ):
        assert (
            generated_agents[name]["_solution"]
            == original_agents[name]["_solution"]
        )
