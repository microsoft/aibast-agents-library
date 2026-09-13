import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from tests.test_library_agent_upvotes import run_library_node


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "state" / "copilot_studio_solution_exports.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def advertised_slugs():
    catalog = read_json(ROOT / "solutions" / "catalog.json")["solutions"]
    registry = read_json(ROOT / "registry.json")["agents"]
    registry_by_name = {
        row["name"]: row
        for row in registry
        if row.get("_solution")
    }
    return {
        registry_by_name[name]["_solution"]["package"]["slug"]
        for name in catalog
    }


def test_historical_native_archives_and_declared_source_bundles_are_intact():
    inventory = read_json(STATE_PATH)
    rows = inventory["solutions"]
    assert inventory["summary"] == {
        "total": 51,
        "exported": 51,
        "missing": 0,
        "with_deployment_settings": 51,
        "unpublished": 51,
    }
    assert {row["slug"] for row in rows} == advertised_slugs()

    for row in rows:
        slug = row["slug"]
        assert row["status"] == "exported"
        assert row["managed"] is False
        assert row["published"] is False
        assert row["error"] is None
        assert row["settings_error"] is None

        solution_zip = ROOT / row["zip"]
        settings = ROOT / row["deployment_settings"]
        metadata = ROOT / row["metadata"]
        source_zip = (
            ROOT
            / "solutions"
            / slug
            / "exports"
            / f"{slug}-source.zip"
        )
        draft_evidence = (
            ROOT
            / "solutions"
            / slug
            / "evals"
            / "dataverse-draft-evidence.json"
        )
        for artifact in (
            solution_zip,
            settings,
            metadata,
            source_zip,
            draft_evidence,
        ):
            assert artifact.is_file(), artifact

        solution_bytes = solution_zip.read_bytes()
        assert len(solution_bytes) == row["bytes"]
        assert hashlib.sha256(solution_bytes).hexdigest() == row["sha256"]
        assert read_json(metadata) == row
        read_json(settings)
        draft = read_json(draft_evidence)
        assert draft["schema"] == "aibast-dataverse-draft-evidence/1.0"
        assert draft["identity"]["display_name"] == row["agent_display_name"]
        assert draft["identity"]["schema_name"] == row["bot_schema_name"]
        assert draft["record"]["botid"] == draft["identity"]["bot_id"]
        assert draft["record"]["publishedon"] is None
        assert all(draft["assertions"].values())
        canonical_record = json.dumps(
            draft["record"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        assert hashlib.sha256(canonical_record).hexdigest() == (
            draft["record_sha256"]
        )

        schema_name = row["bot_schema_name"]
        with zipfile.ZipFile(solution_zip) as archive:
            names = set(archive.namelist())
            assert archive.testzip() is None
            assert {
                "solution.xml",
                "customizations.xml",
                "[Content_Types].xml",
                f"bots/{schema_name}/configuration.json",
                f"bots/{schema_name}/bot.xml",
            } <= names

        with zipfile.ZipFile(source_zip) as archive:
            names = set(archive.namelist())
            manifest = read_json(ROOT / "solutions" / slug / "export-manifest.json")
            if manifest["bundle"].get("include_paths") is not None:
                assert names == set(manifest["bundle"]["include_paths"])
                assert manifest["bundle"]["native_importable"] is False
                assert row["source_contract_status"] == "stale_source"
                assert row["manual_content_inventory"] == {
                    "archive_entries": 5, "skills": 0, "knowledge_files": 0
                }
                assert row["zip"] not in names
                assert row["deployment_settings"] not in names
                assert row["metadata"] not in names
                assert f"solutions/{slug}/evals/dataverse-draft-evidence.json" not in names
            else:
                assert row["zip"] in names
                assert row["deployment_settings"] in names
                assert row["metadata"] in names
                assert (
                    f"solutions/{slug}/evals/dataverse-draft-evidence.json"
                    in names
                )


def test_library_builds_direct_solution_downloads():
    library = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "function copilotSolutionDownloads(agent)" in library
    assert 'zip: `${base}-copilot-studio-solution.zip`' in library
    assert 'settings: `${base}-deployment-settings.json`' in library
    assert "Download Copilot Studio solution" in library


def library_export_consumer(inventory):
    agents = [
        agent for agent in read_json(ROOT / "registry.json")["agents"]
        if agent["name"] in {
            "@aibast-agents-library/care-gap-closure",
            "@aibast-agents-library/account-intelligence",
            "@aibast-agents-library/fs-customer-onboarding",
            "@aibast-agents-library/fs-regulatory-compliance",
            "@aibast-agents-library/portfolio-rebalancing",
        }
    ]
    fixtures = {
        "registry.json": {"agents": agents},
        "solutions/catalog.json": {
            "solutions": {agent["name"]: {} for agent in agents}
        },
        "state/copilot_studio_solution_exports.json": inventory,
    }
    return run_library_node(
        f"const fixtures = {json.dumps(fixtures)};\n"
        """
getJSON = async ([path]) => fixtures[path.split("?")[0]] ?? null;
restoreState = renderStats = buildFilters = renderIndustryMenu = bindInputs = render = () => {};
(async () => {
  await init();
  const downloads = {};
  const dialogs = {};
  for (const agent of state.agents) {
    const slug = agent._solution.package.slug;
    downloads[slug] = copilotSolutionDownloads(agent);
    openModal = markup => { dialogs[slug] = markup; };
    openAgent(agent.name);
  }
  console.log(JSON.stringify({
    selected: [...state.exportedSolutionSlugs],
    downloads,
    dialogs
  }));
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
"""
    )


def test_library_consumer_withholds_shipped_stale_export_and_keeps_current_exports():
    result = library_export_consumer(read_json(STATE_PATH))

    assert "care-gap-closure" not in result["selected"]
    assert result["downloads"]["care-gap-closure"] is None
    stale_dialog = result["dialogs"]["care-gap-closure"]
    assert "Download agent.py" in stale_dialog
    assert "current native Copilot Studio export is unavailable" in stale_dialog
    for unsupported in (
        "Download Copilot Studio solution",
        "care-gap-closure-copilot-studio-solution.zip",
        "care-gap-closure-deployment-settings.json",
        "import the unmanaged Copilot Studio solution manually",
    ):
        assert unsupported not in stale_dialog

    assert result["downloads"]["account-intelligence"] == {
        "zip": (
            "solutions/account-intelligence/exports/"
            "account-intelligence-copilot-studio-solution.zip"
        ),
        "settings": (
            "solutions/account-intelligence/exports/"
            "account-intelligence-deployment-settings.json"
        ),
    }
    current_dialog = result["dialogs"]["account-intelligence"]
    assert "Download Copilot Studio solution" in current_dialog
    assert "import the unmanaged Copilot Studio solution manually" in current_dialog
    assert "current native Copilot Studio export is unavailable" not in current_dialog
    for slug in ("fs-customer-onboarding", "fs-regulatory-compliance", "portfolio-rebalancing"):
        assert slug not in result["selected"]
        assert result["downloads"][slug] is None
        assert "current native Copilot Studio export is unavailable" in result["dialogs"][slug]
        assert f"{slug}-copilot-studio-solution.zip" not in result["dialogs"][slug]


@pytest.mark.parametrize(
    ("inventory", "importable"),
    [
        (None, False),
        ({}, False),
        ({"solutions": [None]}, False),
        ({"solutions": [{
            "slug": "care-gap-closure", "status": "exported", "settings_error": None,
        }]}, True),
        ({"solutions": [{
            "slug": "care-gap-closure", "status": "exported", "settings_error": None,
            "source_contract_status": "stale_source",
        }]}, False),
        ({"solutions": [{
            "slug": "care-gap-closure", "status": "exported", "settings_error": "failed",
        }]}, False),
        ({"solutions": [{
            "slug": "care-gap-closure", "status": "missing", "settings_error": None,
        }]}, False),
    ],
    ids=["missing-inventory", "empty-inventory", "null-row", "current", "stale-source", "settings-error", "not-exported"],
)
def test_library_export_selector_and_ui_fail_closed(inventory, importable):
    result = library_export_consumer(inventory)
    assert ("care-gap-closure" in result["selected"]) is importable
    assert (result["downloads"]["care-gap-closure"] is not None) is importable
    dialog = result["dialogs"]["care-gap-closure"]
    assert "Download agent.py" in dialog
    assert ("Download Copilot Studio solution" in dialog) is importable
    assert ("import the unmanaged Copilot Studio solution manually" in dialog) is importable
