import json
import re
from pathlib import Path

from scripts import build_metrics


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
WORKFLOW = ROOT / ".github/workflows/agent-download-assets.yml"


def test_every_agent_has_unique_immutable_release_asset_name():
    filenames = []
    for agent in REGISTRY["agents"]:
        prefix = agent["_install_prefix"]
        filename = agent["_install_filename"]
        assert re.fullmatch(r"[a-z0-9_]+__", prefix)
        assert filename.startswith(prefix)
        assert filename.endswith("_agent.py")
        assert agent["_sha256"][:12] in filename
        filenames.append(filename)
    assert len(filenames) == len(set(filenames))


def test_release_asset_downloads_aggregate_across_agent_versions():
    agents = {
        "@aibast-agents-library/example": {
            "name": "@aibast-agents-library/example",
            "install_prefix": "example__",
            "downloads": 2,
        },
        "@aibast-agents-library/other": {
            "name": "@aibast-agents-library/other",
            "install_prefix": "other__",
            "downloads": None,
        },
    }
    releases = {
        "available": True,
        "releases": [
            {
                "tag": "agent-downloads",
                "assets": [
                    {"name": "example__aaaaaaaaaaaa_agent.py", "downloads": 3},
                    {"name": "example__bbbbbbbbbbbb_agent.py", "downloads": 4},
                    {"name": "other__cccccccccccc_agent.py", "downloads": 5},
                    {"name": "unrelated.zip", "downloads": 99},
                ]
            },
            {
                "tag": "agent-downloads-staging",
                "assets": [
                    {"name": "example__dddddddddddd_agent.py", "downloads": 50},
                ],
            }
        ],
    }
    assert build_metrics.apply_release_downloads_to_agents(
        agents,
        releases,
    )
    assert agents["@aibast-agents-library/example"]["downloads"] == 9
    assert agents["@aibast-agents-library/other"]["downloads"] == 5


def test_staging_agent_downloads_use_only_the_staging_release():
    agents = {
        "@aibast-agents-library/example": {
            "name": "@aibast-agents-library/example",
            "install_prefix": "example__",
            "downloads": 0,
        },
    }
    releases = {
        "available": True,
        "releases": [
            {
                "tag": "agent-downloads",
                "assets": [
                    {"name": "example__aaaaaaaaaaaa_agent.py", "downloads": 3},
                ],
            },
            {
                "tag": "agent-downloads-staging",
                "assets": [
                    {"name": "example__bbbbbbbbbbbb_agent.py", "downloads": 7},
                ],
            },
        ],
    }

    build_metrics.apply_release_downloads_to_agents(
        agents,
        releases,
        release_tag="agent-downloads-staging",
    )

    assert agents["@aibast-agents-library/example"]["downloads"] == 7


def test_release_api_failure_carries_the_previous_snapshot():
    prior = {
        "generated_at": "2026-08-01T12:00:00Z",
        "releases": {
            "available": True,
            "total_downloads": 9,
            "count": 1,
            "releases": [{"tag": "agent-downloads", "assets": []}],
        },
    }

    releases = build_metrics.resolve_release_metrics(
        {
            "available": False,
            "total_downloads": None,
            "count": None,
            "releases": [],
        },
        prior,
    )

    assert releases["available"] is True
    assert releases["total_downloads"] == 9
    assert releases["carried_forward"] is True


def test_asset_workflow_publishes_and_refreshes_static_metrics():
    text = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "agent-downloads-staging",
        "agent-downloads",
        "gh release upload",
        "_install_filename",
        "workflow_id: \"metrics.yml\"",
        "easy-mode-copilot-chat-pilot",
        "git add registry.json",
        "Auto-build registry.json [skip ci]",
        'git push',
        'git rev-parse HEAD',
        'fetch-depth: 0',
        'registry_path.write_bytes(previous_path.read_bytes())',
        'git rebase "origin/$GITHUB_REF_NAME"',
    ):
        assert token in text
