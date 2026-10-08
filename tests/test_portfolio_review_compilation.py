import hashlib
import html
import json
import re
import struct
import zipfile
from pathlib import Path

import pytest

from tools import build_solution_export
from tools import scaffold_solution_journey as scaffold


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "solutions/portfolio-rebalancing"
PREFIX = "solutions/portfolio-rebalancing/"
# The frozen "repaired-r5" review compilation (nine inputs, six reviewed
# response boards, open creation/upload steps 1 and 7-13) was superseded when
# the workshop was re-shot end to end in the real Copilot Studio UI. These
# tests now protect the re-shot package: every locked case and every student
# step is backed by current evidence, the Draft is never published, and the
# superseded r5 artifacts stay history rather than current proof.
INPUTS = {
    "manual/GLOBAL-INSTRUCTIONS.md",
    *(
        f"manual/skills/{name}/SKILL.md"
        for name in (
            "aibast_portfolio-analysis_01", "aibast_rebalance-recommendation_02",
            "aibast_tax-impact_03", "aibast_tax-loss-harvest_04",
            "aibast_retirement-scenario_05", "aibast_execution-plan_06",
            "aibast_risk-comparison_07", "aibast_client-summary_08",
        )
    ),
    "manual/knowledge/aibast_portfolio-rebalancing-controls-and-review.md",
    "manual/knowledge/aibast_portfolio-rebalancing-synthetic-records.md",
}
PRIVATE = re.compile(
    r"/Users/|repaired-r5-build/|browser-output\.txt|original\.jpg",
    re.IGNORECASE,
)


def read(relative):
    return json.loads((PACKAGE / relative).read_text(encoding="utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def context():
    return scaffold.load_context(
        ROOT, "portfolio-rebalancing", allow_pending=True,
        raw_base=scaffold.DEFAULT_RAW_BASE,
    )


def step_blocks(text):
    return dict(re.findall(
        r'<article class="step" id="step-(\d+)">(.*?)</article>', text, re.DOTALL,
    ))


def locked_cases():
    return json.loads((ROOT / "tests/demo_cases/portfolio-rebalancing.json").read_text())["cases"]


def manual_frames():
    return read("screenshots/manual/browserfilm.json")["frames"]


def test_current_manual_inputs_are_the_packaged_tutorial_downloads():
    assert {
        path.relative_to(PACKAGE).as_posix()
        for path in (PACKAGE / "manual").rglob("*.md")
    } == INPUTS
    tutorial = (PACKAGE / "manual-tutorial.html").read_text()
    assert set(re.findall(r'href="(manual/[^"]+)" download', tutorial)) == INPUTS
    sources = scaffold.choose_frame_resources(context())
    assert {
        source.relative_to(PACKAGE).as_posix()
        for source in sources if "/manual/" in str(source)
    } == INPUTS


def test_superseded_r5_inventory_is_not_presented_as_the_current_build():
    # manual-inputs-r5.json pins the nine pre-reshoot input hashes. Those bytes
    # no longer match the packaged inputs, so the file may survive only as
    # history; it must not be offered as the reviewed build's exact inventory.
    inventory = PACKAGE / "evals/manual-inputs-r5.json"
    if inventory.exists():
        records = read("evals/manual-inputs-r5.json")["inputs"]
        assert any(
            digest((ROOT / item["path"]).read_bytes()) != item["sha256"]
            for item in records
        )
        manifest_paths = {item["path"] for item in read("export-manifest.json")["files"]}
        assert PREFIX + "evals/manual-inputs-r5.json" not in manifest_paths
        assert "manual-inputs-r5.json" not in (PACKAGE / "README.md").read_text()


def test_current_native_matrix_passes_every_locked_case_on_one_unpublished_draft():
    evidence = read("evals/manual-build-evidence.json")
    cases = evidence["canonical_preview"]
    locked = locked_cases()
    assert evidence["status"] == "passed"
    assert scaffold.manual_evidence_passed(evidence)
    assert [case["case_id"] for case in cases] == [case["id"] for case in locked]
    assert [case["prompt"] for case in cases] == [case["prompt"] for case in locked]
    for case, contract in zip(cases, locked):
        assert case["passed"] is True
        assert case["must_include"] == contract["must_include"]
        assert case["must_not_include"] == contract["must_not_include"]
        assert (PACKAGE / "screenshots/manual" / case["expected_screenshot"]).is_file()
    components = evidence["manual_components"]
    assert all(item["confirmed"] == item["expected"] for item in components.values())
    assert components["skills"]["confirmed"] == 8
    assert components["knowledge_files"]["confirmed"] == 2
    assert components["tools"]["confirmed"] == 0
    assert components["web_search_removed"]["confirmed"] is True
    gate = evidence["publication_gate"]
    assert gate["required_state"] == "Draft"
    assert gate["published"] is False
    assert (PACKAGE / "screenshots/manual" / gate["confirmation_screenshot"]).is_file()
    assert context().missing_evidence == []


def test_locked_case_contracts_are_grounded_in_the_packaged_sources():
    sources = "".join((PACKAGE / path).read_text() for path in sorted(INPUTS))
    for case in locked_cases():
        for term in case["must_include"]:
            assert term in sources, (case["id"], term)
        assert case["must_not_include"]
    for statement in (
        "No order has been created, routed, or executed.",
        "Confirm available cash and settlement timing in the approved trading system.",
        "No success probability",
    ):
        assert statement in sources


def test_every_capture_is_reviewed_current_media_and_every_step_is_covered():
    visual = read("evals/visual-checkpoints.json")
    captures = visual["captures"]
    assert visual["summary"] == {
        "total_existing_captures": len(captures),
        "reusable": len(captures),
        "reshoot_required": 0,
    }
    assert visual["reshoot_plan"] == {"replacement_captures": [], "new_learn_step_captures": []}
    assert visual["release_review"]["status"] == "approved"
    assert "nothing published" in visual["release_review"]["notes"]
    hard = {item["step"]: item for item in captures if item["mode"] == "hard"}
    assert set(hard) == set(range(1, len(manual_frames()) + 1))
    for item in captures:
        assert item["status"] == "reusable"
        assert "repaired-r5" not in item["source"]
        for field in ("source", "annotated"):
            assert (ROOT / item[field]).is_file(), item[field]
        assert item["visible_anchors"]
    easy_cases = {item["case_id"] for item in captures if item["mode"] == "easy" and "case_id" in item}
    assert easy_cases == {case["id"] for case in locked_cases()}


def test_standalone_and_embedded_manual_guides_keep_all_steps_and_real_media():
    tutorial = (PACKAGE / "manual-tutorial.html").read_text()
    quest = (PACKAGE / "quest.html").read_text()
    standalone = step_blocks(tutorial)
    embedded = step_blocks(quest)
    assert standalone == embedded
    assert set(standalone) == {str(step) for step in range(1, len(manual_frames()) + 1)}
    for block in standalone.values():
        assert block.count("<img ") == 1
        assert re.search(r'src="screenshots/manual/annotated/[^"]+\.png"', block)
        assert "repaired-r5" not in block
    policy = re.search(
        r'<pre class="copy-source" id="hard-copy-3" hidden>(.*?)</pre>',
        standalone["3"], re.DOTALL,
    )[1]
    assert html.unescape(policy) == (PACKAGE / "manual/GLOBAL-INSTRUCTIONS.md").read_text()
    for generated in (tutorial, quest):
        assert "workshop still partial" not in generated
        assert "manual-pilot-review.json" not in generated
        assert "Do not choose Publish" in generated
        for case in locked_cases():
            assert case["prompt"] in html.unescape(generated)
    assert all(case["passed"] is True for case in scaffold.easy_case_records(context()))


@pytest.mark.parametrize("value", [None, 0, -1, "869", True])
def test_reviewed_board_metadata_rejects_unknown_or_invalid_dimensions(value):
    # Generator contract for reviewed board/crop media; the re-shot package no
    # longer ships boards, so a synthetic checkpoint exercises the validator.
    base = next(item for item in read("evals/visual-checkpoints.json")["captures"] if item["status"] == "reusable")
    media = {
        "kind": "labeled_board", "width": 869, "height": 1504,
        "view_count": 2, "capture_count": 2, "format": "PNG",
        "scope": "Synthetic scope.", "private_originals": True,
    }
    caption = scaffold.reviewed_media_caption(context(), {**base, "media": dict(media)})
    assert "869×1504 PNG" in caption
    assert "Private full-window originals are not distributed" in caption
    item = {**base, "media": {**media, "width": value}}
    with pytest.raises(scaffold.ScaffoldError, match="positive integer width"):
        scaffold.reviewed_media_caption(context(), item)


def test_reference_readmes_derive_step_coverage_and_deduplicate_shared_images():
    ctx = context()
    ctx.manual_browserfilm = {**(ctx.manual_browserfilm or {}), "kind": "reviewed-reference-set"}
    ctx.manual_frames = [
        {"step": 2, "captured": True, "file": "shared.png"},
        {"step": 3, "captured": True, "file": "shared.png"},
        {"step": 4, "captured": False},
    ]
    for rendered in (
        scaffold.render_screenshot_readme(ctx),
        scaffold.render_film_readme(ctx, "manual"),
    ):
        assert "Reviewed student steps: 2, 3." in rendered
        assert "Distinct reviewed PNG assets: 1." in rendered
        assert "Open student steps: 4." in rendered
        assert "Steps 1-13" not in rendered
        assert "Nine parent-reviewed" not in rendered


def test_source_bundle_is_complete_exact_and_free_of_private_provenance():
    manifest = read("export-manifest.json")
    bundle = manifest["bundle"]
    assert manifest["raw_base"] == scaffold.DEFAULT_RAW_BASE
    assert "/microsoft/aibast-agents-library/tree/main/" in manifest["github_folder"]
    assert bundle["path"] == PREFIX + "exports/portfolio-rebalancing-source.zip"
    with zipfile.ZipFile(ROOT / bundle["path"]) as archive:
        names = set(archive.namelist())
        assert archive.testzip() is None
        assert {PREFIX + path for path in INPUTS} <= names
        assert PREFIX + "copilot-studio/settings.mcs.yml" in names
        assert PREFIX + "evals/manual-build-evidence.json" in names
        for name in names:
            data = archive.read(name)
            assert data == build_solution_export.bundle_bytes(ROOT / name), name
            if name.endswith((".md", ".json", ".html", ".yml")):
                assert not PRIVATE.search(data.decode()), name
    # HTML hosting normalization remains intentional; Markdown is never normalized.
    assert build_solution_export.bundle_bytes(PACKAGE / "manual/GLOBAL-INSTRUCTIONS.md") == (PACKAGE / "manual/GLOBAL-INSTRUCTIONS.md").read_bytes()


def test_historical_archive_stays_intact_and_current_native_export_is_offered_unpublished():
    index = read("evals/history/2026-08/index.json")
    assert len(index["files"]) == 5
    for item in index["files"]:
        assert digest((ROOT / item["archived_path"]).read_bytes()) == item["sha256"]
    historical = read("evals/history/2026-08/manual-build-evidence.json")
    assert historical["status"] == "passed"
    assert historical["captured_at"].startswith("2026-08-")
    metadata = read("exports/portfolio-rebalancing-solution-export.json")
    assert metadata["status"] == "exported"
    assert metadata["published"] is False
    assert metadata["managed"] is False
    assert "source_contract_status" not in metadata
    assert digest((ROOT / metadata["zip"]).read_bytes()) == metadata["sha256"]
    assert any("remains unpublished" in caveat for caveat in metadata["import_caveats"])
    inventory = json.loads((ROOT / "state/copilot_studio_solution_exports.json").read_text())
    assert next(item for item in inventory["solutions"] if item["slug"] == "portfolio-rebalancing") == metadata
    assert re.search(
        r'href="[^"]*portfolio-rebalancing-copilot-studio-solution\.zip"',
        (PACKAGE / "quest.html").read_text(),
    )


def test_current_public_metadata_and_guides_do_not_publish_private_browser_provenance():
    for relative in (
        "evals/manual-build-evidence.json", "evals/visual-checkpoints.json",
        "screenshots/manual/browserfilm.json", "deployment.json",
        "README.md", "manual-tutorial.html", "quest.html", "field-guide.html",
        "evidence-report.html", "EASY-MODE-PERSONLESS.md", "EASY-MODE-COPILOT-CHAT.md",
    ):
        assert not PRIVATE.search((PACKAGE / relative).read_text()), relative
    deployment = read("deployment.json")["copilot_studio"]
    assert deployment["required_connections"] == []
    assert len(deployment["production_replacement_connections"]) == 5
    assert deployment["validated_manual"]["published"] is False
    # deployment.json must agree with the current manual evidence, not the
    # superseded six-case r5 matrix.
    assert deployment["validated_manual"]["preview_cases_passed"] == len(locked_cases())
    assert deployment["validated_manual"]["preview_cases_total"] == len(locked_cases())
    assert deployment["validated_manual"]["skills"] == 8
