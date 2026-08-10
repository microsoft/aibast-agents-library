import hashlib
import json
import zipfile
from pathlib import Path


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


def test_all_advertised_solution_exports_are_importable_and_bound():
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
            assert row["zip"] in names
            assert row["deployment_settings"] in names
            assert row["metadata"] in names
            assert (
                f"solutions/{slug}/evals/dataverse-draft-evidence.json"
                in names
            )


def test_library_builds_direct_solution_downloads():
    library = (ROOT / "library.html").read_text(encoding="utf-8")
    assert "function copilotSolutionDownloads(agent)" in library
    assert 'zip: `${base}-copilot-studio-solution.zip`' in library
    assert 'settings: `${base}-deployment-settings.json`' in library
    assert "Download Copilot Studio solution" in library
