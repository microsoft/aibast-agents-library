import json
import re
import zipfile
from pathlib import Path

from tools.build_solution_export import bundle_bytes
from tools import scaffold_solution_journey as scaffold


ROOT = Path(__file__).resolve().parents[1]


def advertised_slugs():
    catalog = json.loads(
        (ROOT / "solutions" / "catalog.json").read_text(encoding="utf-8")
    )["solutions"]
    registry = json.loads(
        (ROOT / "registry.json").read_text(encoding="utf-8")
    )["agents"]
    registry_by_name = {
        row["name"]: row
        for row in registry
        if row.get("_solution")
    }
    return sorted({
        registry_by_name[name]["_solution"]["package"]["slug"]
        for name in catalog
    })


def test_all_advertised_workshops_match_the_authoritative_scaffold():
    for slug in advertised_slugs():
        evidence_path = ROOT / "solutions" / slug / "evals/manual-build-evidence.json"
        documented_reshoot = (
            json.loads(evidence_path.read_text(encoding="utf-8")).get("status")
            == "reshoot_required"
        )
        context = scaffold.load_context(
            ROOT,
            slug,
            allow_pending=documented_reshoot,
            raw_base=scaffold.DEFAULT_RAW_BASE,
        )
        if documented_reshoot:
            assert context.missing_evidence == [
                f"solutions/{slug}/evals/manual-build-evidence.json "
                "does not record passed manual Preview evidence"
            ]
        resources, outputs = scaffold.generated_outputs(context)

        for path, expected in outputs.items():
            assert path.read_text(encoding="utf-8") == (
                scaffold.normalize_generated_text(expected)
            ), f"{slug}: stale generated file {path.relative_to(ROOT)}"

        readme = (context.package / "README.md").read_text(encoding="utf-8")
        match = re.search(
            re.escape(scaffold.README_START)
            + r".*?"
            + re.escape(scaffold.README_END),
            readme,
            re.DOTALL,
        )
        assert match, f"{slug}: generated README block is missing"
        assert match.group(0) == scaffold.readme_block(context, resources)


def test_all_advertised_source_bundles_match_current_files_with_hosting_normalization():
    for slug in advertised_slugs():
        manifest = json.loads(
            (ROOT / "solutions" / slug / "export-manifest.json").read_text(encoding="utf-8")
        )
        with zipfile.ZipFile(ROOT / manifest["bundle"]["path"]) as archive:
            for name in archive.namelist():
                source = ROOT / name
                assert source.is_file(), f"{slug}: missing bundle source {name}"
                assert archive.read(name) == bundle_bytes(source), f"{slug}: stale bundle member {name}"
