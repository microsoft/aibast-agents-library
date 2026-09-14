import copy
import hashlib
import html
import json
import re
import zipfile
from pathlib import Path

from bs4 import BeautifulSoup

from tools import scaffold_solution_journey as scaffold
from tools.build_solution_export import bundle_bytes


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "solutions/procurement-agent"
SOURCE_COMMIT = "38a1c30d3cccfa1cab379f6a0bb94879cf4de496"
REVISION = "grounding-r3"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def context():
    return scaffold.load_context(
        ROOT, "procurement-agent", allow_pending=True,
        raw_base="https://raw.githubusercontent.com/kody-w/aibast-agents-library/staging/",
    )


def test_procurement_candidate_does_not_inherit_native_acceptance():
    evidence = read_json(PACKAGE / "evals/manual-build-evidence.json")
    assert evidence["build_revision"] == REVISION
    assert evidence["source_commit"] == SOURCE_COMMIT
    assert evidence["status"] == "reshoot_required"
    assert scaffold.manual_evidence_passed(evidence) is False
    regression = evidence["native_regression"]
    assert regression["status"] == "blocked"
    assert regression["accepted_components"] == 0
    assert regression["cases_run"] == regression["passed"] == 0
    assert regression["total"] == 4
    assert regression["older_passes_carried_forward"] is False
    assert not any(evidence["persistence"].values())
    assert evidence["publication_gate"]["published"] is False
    assert evidence["publication_gate"]["current_revision_confirmed"] is False
    expected = {
        case["id"]: case
        for case in read_json(ROOT / "tests/demo_cases/procurement-agent.json")["cases"]
    }
    assert {row["case_id"] for row in evidence["canonical_preview"]} == set(expected)
    for row in evidence["canonical_preview"]:
        assert row["passed"] is None
        assert row["status"] == "reshoot_required"
        assert row["current_revision_run"] is False
        assert row["prompt"] == expected[row["case_id"]]["prompt"]
        assert row["must_include"] == expected[row["case_id"]]["must_include"]
    misleading = copy.deepcopy(evidence)
    for row in misleading["canonical_preview"]:
        row["passed"] = True
    for component in misleading["manual_components"].values():
        component["confirmed"] = component["expected"]
    assert scaffold.manual_evidence_passed(misleading) is False
    assert all(case["passed"] is False for case in scaffold.easy_case_records(context()))


def test_procurement_seven_inputs_and_locked_cases_are_pinned_to_exact_bytes():
    inventory = read_json(PACKAGE / "evals/manual-inputs-r3.json")
    assert inventory["build_revision"] == REVISION
    assert inventory["source_commit"] == SOURCE_COMMIT
    assert len(inventory["inputs"]) == 7
    for item in inventory["inputs"]:
        data = (ROOT / item["path"]).read_bytes()
        assert len(data) == item["bytes"]
        assert sha256(data) == item["sha256"]
        assert item["public_url"] == (
            "https://raw.githubusercontent.com/kody-w/aibast-agents-library/"
            f"{SOURCE_COMMIT}/{item['path']}"
        )
    locked = inventory["locked_cases"]
    assert locked["path"] == "tests/demo_cases/procurement-agent.json"
    data = (ROOT / locked["path"]).read_bytes()
    assert len(data) == locked["bytes"]
    assert sha256(data) == locked["sha256"]


def test_procurement_generated_guides_deliver_current_policy_without_stale_proof():
    _, outputs = scaffold.generated_outputs(context())
    for path, expected in outputs.items():
        assert path.read_text(encoding="utf-8") == scaffold.normalize_generated_text(expected)
    instructions = (PACKAGE / "manual/GLOBAL-INSTRUCTIONS.md").read_text(encoding="utf-8")
    for name in ("manual-tutorial.html", "quest.html"):
        text = (PACKAGE / name).read_text(encoding="utf-8")
        payloads = {
            int(number): html.unescape(content)
            for number, content in re.findall(
                r'<pre class="copy-source" id="hard-copy-(\d+)" hidden>(.*?)</pre>',
                text, re.DOTALL,
            )
        }
        assert payloads[3] == instructions
        assert "Pending evidence:" in text
        assert "Watch the manual film" not in text
        assert "Download Copilot Studio solution" not in text
        page = BeautifulSoup(text, "html.parser")
        assert page.select('a[href="exports/procurement-agent-source.zip"]')
        assert not page.select('img[data-evidence-status="reusable"]')
    report = (PACKAGE / "evidence-report.html").read_text(encoding="utf-8")
    assert "Reference-only visual gaps" in report
    assert "Download Copilot Studio solution" not in report


def test_procurement_input_bundle_is_complete_and_not_a_native_import():
    manifest = read_json(PACKAGE / "export-manifest.json")
    inventory = read_json(PACKAGE / "evals/manual-inputs-r3.json")
    bundle = manifest["bundle"]
    assert bundle["native_importable"] is False
    assert bundle["standalone_guide"] is False
    expected = {
        *(item["path"] for item in inventory["inputs"]),
        inventory["locked_cases"]["path"],
        "solutions/procurement-agent/evals/manual-inputs-r3.json",
        "solutions/procurement-agent/exports/README.md",
    }
    assert set(bundle["include_paths"]) == expected
    with zipfile.ZipFile(ROOT / bundle["path"]) as archive:
        assert set(archive.namelist()) == expected
        for name in archive.namelist():
            assert archive.read(name) == bundle_bytes(ROOT / name)
        assert all("/copilot-studio/" not in name for name in archive.namelist())
        assert all("/history/" not in name for name in archive.namelist())
        assert all(not name.endswith((".html", ".png", ".jpg", ".gif", ".zip")) for name in archive.namelist())


def test_procurement_historical_metadata_and_media_remain_byte_identical():
    history = read_json(PACKAGE / "evals/history/2026-08/index.json")
    assert history["status"] == "historical_only"
    assert len(history["files"]) == 8
    for item in history["files"]:
        data = (ROOT / item["archived_path"]).read_bytes()
        assert len(data) == item["bytes"]
        assert sha256(data) == item["sha256"]
    assert history["media_sha256"]
    for name, digest in history["media_sha256"].items():
        assert sha256((ROOT / name).read_bytes()) == digest
    visual = read_json(PACKAGE / "evals/visual-checkpoints.json")
    assert visual["summary"]["reusable"] == 0
    assert visual["summary"]["reshoot_required"] == len(visual["captures"])
    for row in visual["captures"]:
        assert row["status"] == "reshoot_required"
        assert row["historical"] is True
        assert "annotated" not in row
        assert "visible_anchors" not in row
    for mode in ("manual", "assisted"):
        film = read_json(PACKAGE / f"screenshots/{mode}/browserfilm.json")
        assert all(frame["captured"] is False for frame in film["frames"])


def test_procurement_historical_export_is_withheld_in_every_current_surface():
    metadata = read_json(PACKAGE / "exports/procurement-agent-solution-export.json")
    original = read_json(PACKAGE / "evals/history/2026-08/solution-export.json")
    assert metadata["source_contract_status"] == "stale_source"
    assert metadata["manual_content_inventory"] == {
        "archive_entries": 5, "skills": 0, "knowledge_files": 0,
    }
    assert metadata["sha256"] == original["sha256"]
    assert sha256((ROOT / metadata["zip"]).read_bytes()) == original["sha256"]
    records = read_json(ROOT / "state/copilot_studio_solution_exports.json")["solutions"]
    assert next(row for row in records if row["slug"] == "procurement-agent") == metadata
    assert "Download Copilot Studio solution" not in scaffold.copilot_solution_download_links(context())
    studio = read_json(PACKAGE / "deployment.json")["copilot_studio"]
    for key in ("validated_manual", "validated_pilot"):
        assert studio[key]["source_contract_status"] == "reshoot_required"
        assert studio[key]["preview_cases_passed"] == 0
        assert studio[key]["preview_cases_pending"] == 4
        assert studio[key]["current_revision_confirmed"] is False
