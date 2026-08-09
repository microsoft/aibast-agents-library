#!/usr/bin/env python3
"""Normalize solution deployment recipes to the no-terminal contract."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REGISTRY_URL = (
    "https://raw.githubusercontent.com/microsoft/"
    "aibast-agents-library/main/registry.json"
)
RAW_BASE = (
    "https://raw.githubusercontent.com/microsoft/"
    "aibast-agents-library/main/"
)
INSTALLERS = {
    "macos_linux": "https://microsoft.github.io/aibast-agents-library/install.sh",
    "windows_powershell": (
        "https://microsoft.github.io/aibast-agents-library/install.ps1"
    ),
    "windows_cmd": "https://microsoft.github.io/aibast-agents-library/install.cmd",
}


def normalize(recipe, agent):
    normalized = dict(recipe)
    normalized.setdefault("schema", "aibast-deployment-recipe/1.0")
    normalized["name"] = agent["name"]
    normalized.setdefault("display_name", agent["display_name"])
    normalized["registry_url"] = REGISTRY_URL
    normalized["source_url"] = RAW_BASE + agent["_file"]
    normalized["target_filename"] = Path(agent["_file"]).name
    normalized.setdefault("expected_tool", recipe.get("smoke_test", {}).get("must_call"))
    normalized["brainstem"] = {
        "health_url": "http://localhost:7071/health",
        "chat_url": "http://localhost:7071/chat",
        "ui_url": "http://localhost:7071",
        "installers": INSTALLERS,
        "default_source_dir": "~/.brainstem/src/rapp_brainstem",
        "default_agents_dir": "~/.brainstem/src/rapp_brainstem/agents",
        "policy_clean_launcher_dir": "~/.copilot/bin",
    }
    smoke = normalized.setdefault("smoke_test", {})
    smoke["must_call"] = normalized["expected_tool"]
    studio = normalized.setdefault("copilot_studio", {})
    studio.setdefault("plugin", "mcs-assistant@copilot-studio-plugin")
    studio["minimum_pac_version"] = "2.9.3"
    studio.setdefault("authoring_mode", "cli-copilot")
    studio["publish_requires_confirmation"] = True
    return normalized


def main():
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
    agents = {agent["name"]: agent for agent in registry["agents"]}
    changed = 0
    for path in sorted((ROOT / "solutions").glob("*/deployment.json")):
        recipe = json.loads(path.read_text(encoding="utf-8"))
        name = recipe.get("name")
        if name not in agents:
            raise KeyError(f"{path}: unknown registry agent {name}")
        normalized = normalize(recipe, agents[name])
        path.write_text(
            json.dumps(normalized, indent=2) + "\n",
            encoding="utf-8",
        )
        changed += 1
    print(f"[OK] Normalized {changed} deployment recipes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
