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
INPUTS = {
    "manual/GLOBAL-INSTRUCTIONS.md": (6104, "263396c47f80e3d8572cf7264d9f717b13f0e3f05803d26cf0fd4f2b51650931"),
    "manual/skills/aibast_execution-plan_06/SKILL.md": (2881, "5ce85e4f7aa132efa23e37e20e0aa0a7ae708d32a891d459e6d305470ca67181"),
    "manual/skills/aibast_portfolio-analysis_01/SKILL.md": (1044, "9c0f20bb40cc1c961e73a19ff0774fd40137fba5e665b539fb0cb5c5150f189f"),
    "manual/skills/aibast_rebalance-recommendation_02/SKILL.md": (2482, "787d18b44961a31b89badbbcd84e9887d53891a893c8ed6cd968e5af3ae40fc9"),
    "manual/skills/aibast_retirement-scenario_05/SKILL.md": (2575, "5c3634e6bbb4dbd7fe87822590661f7da9829134f98b49627154f4b32bb0e306"),
    "manual/skills/aibast_tax-impact_03/SKILL.md": (3520, "e09490b57a6dd09037e9e86629cbbf1443ec2ad308b37447ef1250faa6078707"),
    "manual/skills/aibast_tax-loss-harvest_04/SKILL.md": (2314, "d9b15ac995eb7fbba484e7fd720bdde85bef60a94133c7219377fe5fdedf302a"),
    "manual/knowledge/aibast_portfolio-rebalancing-controls-and-review.md": (36654, "69ed1039c93384d5a4da89c59704f2827e15e57460b7b36d66879f208028ef63"),
    "manual/knowledge/aibast_portfolio-rebalancing-synthetic-records.md": (12712, "3714d3ff9b5a5527d70220bf88a3e84037b788d55001220a416c1cd8548b1f9e"),
}
CAPTURE_HASHES = [
    "7f718e37f761a58b03c23222755d9c3e0d3f1c40e53074468f60d23b19c8da3a",
    "fa28ee55938050c641813881eeabf886cf9a505fd40de6f5692ee7b494332995",
    "cfc093d636d68d4c66cd0af80d302562114e6aab4df7c75b45d6ae9aa507672e",
    "dd1caef97e08f9aa595ef162787d81398623a9631eabf91364cadea86935d2ef",
    "f07db96831e52a61bdf1a47744aeb1c97b1432be981b47fe6b129f513bfe6482",
    "0c11cb204c187727b4906c9f7b40593dda9e1b458f4f6a3107fb4b7b55f10c8a",
]
SUBMISSIONS = [
    "2026-09-13T04:14:50.946Z", "2026-09-13T04:22:00.310Z",
    "2026-09-13T04:25:27.921Z", "2026-09-13T04:31:12.868Z",
    "2026-09-13T04:37:17.330Z", "2026-09-13T04:43:59.275Z",
]
IMAGES = {
    "PRB-01-response-board.png": (869, 1504, "994064b171f9f166713596efa683f81a747a1eedcb5943bed1729e9a80555118"),
    "PRB-02-response-board.png": (869, 883, "d060a644aa1f55bbe1d334f360c15b63063e38385700e4316cf0ded2f9419f39"),
    "PRB-03-response-board.png": (869, 1450, "b3e8aa317c59b1df7bc34d948d003eb4faac4c8d58d1604a559b137eb7796bb3"),
    "PRB-04-response-board.png": (869, 897, "e4ab501a0000cb6063c2832b0fe2bf175baaa6a685a7ad0e2475e223a78ad346"),
    "PRB-05-response-board.png": (869, 1241, "a959a70964f06ccd10ec9681ba6c56659fdd5283ed8e5977fba532825a5c7d31"),
    "PRB-06-response-board.png": (869, 1637, "d7e0f5ca692f895d2c3c84d445997187930defec79c2a14dfe70d227b648c369"),
    "UI-saved-configuration-board.png": (940, 818, "1fc9fe955feb5302a83c441f030ded2b548fb5440d8bb4753e7bf444898bf90e"),
    "UI-fresh-preview.png": (916, 736, "418be17620065ce8caea209a6113b45c486dbb3f169b0c27a4d9e7bcc43387e7"),
    "UI-final-draft.png": (779, 259, "75ce48e283dc90e3e8347b689c49af436c36e7383f769fde4a3780db5fefae13"),
    "UI-name-readback.png": (512, 105, "e08172a5cd6db2bfbab41d3aae00cf8c607dc8a2b79efc0011fb98a088775873"),
    "UI-persisted-policy-board.png": (972, 1476, "2644d2e9b6f1c4d51f54644fb0ae87645e4de626568118cbbc2ae9a4a51749c0"),
    "UI-empty-tools.png": (366, 108, "533d1e42e3d8708bb67c2349f863a4899c05c6559d977e9f8b7e0466529800d0"),
    "UI-controls-upload-ready-board.png": (796, 1012, "55439e544814f3d9d743c6d88cea538a35a270a060a76000bdc777adb8aa1b45"),
}
REVIEWED_STEPS = [2, 3, 4, 5, 6, *range(14, 23)]
OPEN_STEPS = [1, *range(7, 14)]
PRIVATE = re.compile(
    r"/Users/|copilotstudio\.preview\.microsoft\.com/environments/"
    r"|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    r"|repaired-r5-build/|browser-output\.txt|original\.jpg",
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


def test_nine_frozen_r5_manual_inputs_are_exact_bytes_not_normalized_copies():
    inventory = read("evals/manual-inputs-r5.json")
    assert inventory["build_revision"] == "repaired-r5"
    assert {
        item["path"]: (item["bytes"], item["sha256"])
        for item in inventory["inputs"]
    } == {PREFIX + path: value for path, value in INPUTS.items()}
    for relative, (size, expected) in INPUTS.items():
        data = (PACKAGE / relative).read_bytes()
        assert len(data) == size
        assert digest(data) == expected
    controls = (PACKAGE / "manual/knowledge/aibast_portfolio-rebalancing-controls-and-review.md").read_text()
    for path in (PACKAGE / "manual/skills").glob("*/SKILL.md"):
        assert path.read_text().rstrip() in controls


def test_current_native_matrix_is_dated_single_build_acceptance_not_certification():
    evidence = read("evals/manual-build-evidence.json")
    review = read("evals/manual-pilot-review.json")
    locked = json.loads((ROOT / "tests/demo_cases/portfolio-rebalancing.json").read_text())
    cases = evidence["canonical_preview"]
    assert evidence["status"] == "reshoot_required"
    assert evidence["certified"] is review["certified"] is False
    assert not scaffold.manual_evidence_passed(evidence)
    assert [case["case_id"] for case in cases] == [case["id"] for case in locked["cases"]]
    assert [case["prompt"] for case in cases] == [case["prompt"] for case in locked["cases"]]
    assert [case["output_sha256"] for case in cases] == CAPTURE_HASHES
    assert [case["submitted_at"] for case in cases] == SUBMISSIONS
    for case in cases:
        assert case["passed"] is True and case["status"] == "passed"
        assert case["build_revision"] == "repaired-r5"
        assert case["submission_count"] == 1
        assert case["fresh_native_conversation"] is True
        assert all(case["checks"].values())
    regression = evidence["native_regression"]
    assert regression["status"] == "passed"
    assert regression["passed"] == regression["total"] == 6
    assert regression["older_passes_carried_forward"] is False
    assert regression["unchanged_frozen_build"] is True
    assert digest((ROOT / "tests/demo_cases/portfolio-rebalancing.json").read_bytes()) == regression["locked_cases_sha256"]
    assert "including ungraded debug/UI text" in evidence["output_hash_scope"]
    assert evidence["persistence"]["verified_at"] == "2026-09-13T03:59:19.049Z"
    assert evidence["persistence"]["all_six_complete_skill_bodies_names_descriptions_match"]
    assert evidence["publication_gate"]["same_agent_reopened_at"] == "2026-09-13T04:56:08.534Z"
    assert evidence["publication_gate"]["matching_results"] == 1
    assert evidence["publication_gate"]["published"] is False
    assert review["accepted_student_steps"] == REVIEWED_STEPS
    assert review["open_student_steps"] == OPEN_STEPS
    assert evidence["browserfilm"]["reviewed_assets"] == 13
    assert evidence["browserfilm"]["reviewed_steps"] == REVIEWED_STEPS
    assert evidence["browserfilm"]["open_steps"] == OPEN_STEPS
    assert context().missing_evidence == [
        PREFIX + "evals/manual-build-evidence.json does not record passed manual Preview evidence"
    ]


def test_current_case_summaries_preserve_the_reviewed_numeric_and_semantic_edges():
    cases = read("evals/manual-build-evidence.json")["canonical_preview"]
    for index, terms in enumerate((
        ("$12,450,000", "3-point inclusive", "+5pp", "-3pp", "$8,200,000", "VYMI", "equals", "'breaching'"),
        ("$622,500", "$372,500", "$373,750", "$746,250", "not recomputed", "no funding conclusion"),
        ("$4,357,500", "$3,800,000", "$622,500", "1/7", "$79,642.857", "$79,643", "23.8%", "$18,955"),
        ("VEA $106,250", "VWO $57,500", "BND $87,500", "not allocation drift", "savings or deductions"),
        ("by ID, not its display name", "$12,450,000", "25 years", "$498,000/year", "Seven categories", "not all absent"),
        ("Quarterly", "VMFXX $746,250", "no proceeds-only", "plain lists", "zero checkboxes", "30/10/15"),
    )):
        for term in terms:
            assert term in cases[index]["observed_result"]
    assert len(cases[2]["fixed_review_statements"]) == 4
    assert len(cases[3]["fixed_review_statements"]) == 5
    assert cases[5]["native_checkbox_count"] == 0
    assert cases[5]["cash_review_statement"] == "Confirm available cash and settlement timing in the approved trading system."
    assert cases[5]["no_order_statement"] == "No order has been created, routed, or executed."
    assert cases[4]["no_success_probability_statement"] == (
        "No success probability is provided or asserted. Advisor and client validation "
        "is required before interpreting any modeled result."
    )


def test_only_reviewed_pngs_are_current_and_creation_upload_steps_stay_open():
    visual = read("evals/visual-checkpoints.json")
    captures = visual["captures"]
    current = [item for item in captures if item["status"] == "reusable"]
    assert len(current) == visual["summary"]["reusable"] == 14
    assert visual["summary"]["reviewed_manual_images"] == len(IMAGES) == 13
    assert visual["summary"]["manual_build_steps_open"] == len(OPEN_STEPS) == 8
    assert {Path(item["annotated"]).name for item in current} == set(IMAGES)
    directory = PACKAGE / "screenshots/manual/repaired-r5"
    assert {path.name for path in directory.iterdir()} == set(IMAGES) | {"browserfilm.json"}
    for item in current:
        data = (ROOT / item["annotated"]).read_bytes()
        width, height, expected = IMAGES[Path(item["annotated"]).name]
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert struct.unpack(">II", data[16:24]) == (width, height)
        assert digest(data) == item["media"]["sha256"] == expected
        assert (item["media"]["width"], item["media"]["height"]) == (width, height)
        assert len(data) == item["media"]["bytes"]
        assert item["media"]["format"] == "PNG"
        assert item["media"]["private_originals"] is True
        assert item["source"] == item["annotated"]
    open_manual = [item for item in captures if item["mode"] == "hard" and item["status"] == "reshoot_required"]
    assert [item["step"] for item in open_manual] == OPEN_STEPS
    assert all("annotated" not in item and "source" not in item for item in open_manual)
    assert all(item["status"] == "reshoot_required" for item in captures if item["mode"] == "easy")
    manifest = read("screenshots/manual/repaired-r5/browserfilm.json")
    assert manifest["kind"] == "reviewed-reference-set"
    assert "gif" not in manifest and "contact_sheet" not in manifest
    assert len(manifest["frames"]) == 22
    assert sum(frame["captured"] for frame in manifest["frames"]) == 14
    for item in current:
        if item["step"] in (2, 3, 4, 5):
            assert item["evidence_stage"] == "post_regression_readback"
            assert "not an upload-action recording" in item["review_provenance"]
    controls = next(item for item in current if item["step"] == 6)
    assert controls["evidence_stage"] == "r5_upload_and_later_ready"
    assert "Ready" in controls["visible_anchors"]
    assert controls["media"]["view_count"] == controls["media"]["capture_count"] == 2
    assert "did not re-upload or change the file" in controls["media"]["scope"]
    assert visual["strict_coverage"]["reviewed_student_steps"] == REVIEWED_STEPS
    assert visual["strict_coverage"]["open_student_steps"] == OPEN_STEPS


def test_standalone_and_embedded_manual_guides_keep_all_steps_and_real_media_boundaries():
    tutorial = (PACKAGE / "manual-tutorial.html").read_text()
    quest = (PACKAGE / "quest.html").read_text()
    standalone = step_blocks(tutorial)
    embedded = step_blocks(quest)
    assert standalone == embedded
    assert set(standalone) == {str(step) for step in range(1, 23)}
    assert set(re.findall(r'href="(manual/[^"]+)" download', tutorial)) == set(INPUTS)
    for step, block in standalone.items():
        if int(step) in OPEN_STEPS:
            assert "<img " not in block
            assert "Live verification checkpoint" in block
        else:
            filename = {
                "2": "UI-name-readback.png",
                "3": "UI-persisted-policy-board.png",
                "4": "UI-persisted-policy-board.png",
                "5": "UI-empty-tools.png",
                "6": "UI-controls-upload-ready-board.png",
                "14": "UI-saved-configuration-board.png",
                "15": "UI-fresh-preview.png",
                "22": "UI-final-draft.png",
            }.get(step, f"PRB-{int(step) - 15:02}-response-board.png")
            assert f'src="screenshots/manual/repaired-r5/{filename}"' in block
            assert block.count("<img ") == 1
            assert " PNG." in block
            assert "Private full-window originals are not distributed" in block
            assert " JPEG" not in block and "Download original" not in block
    assert "3 cropped views from 2 actual native UI captures" in standalone["14"]
    assert "4 cropped views from 4 actual native UI captures" in standalone["3"]
    assert "not a new paste action" in standalone["4"]
    assert "no GUID is claimed visible" in standalone["22"]
    assert "knowledge file linked for this step" in standalone["6"]
    assert "frontmatter name and description" in standalone["12"]
    policy = re.search(
        r'<pre class="copy-source" id="hard-copy-3" hidden>(.*?)</pre>',
        standalone["3"], re.DOTALL,
    )[1]
    assert html.unescape(policy) == (PACKAGE / "manual/GLOBAL-INSTRUCTIONS.md").read_text()
    for generated in (tutorial, quest):
        assert "Native r5 regression accepted; workshop still partial" in generated
        assert "still needs fresh live regression" not in generated
        assert "Do not create a duplicate" in generated
        assert "zero configured Tools" in generated
        assert "No PAC CLI, YAML import, or plugin architect" in generated
    assert "Historical Easy completion record" in quest
    assert "Required Easy Preview proof" in quest
    for name in ("EASY-MODE-PERSONLESS.md", "EASY-MODE-COPILOT-CHAT.md"):
        assert "Evidence lane boundary" in (PACKAGE / name).read_text()
        assert "not a newly accepted run" in (PACKAGE / name).read_text()
    assert all(case["passed"] is False for case in scaffold.easy_case_records(context()))
    sources = scaffold.choose_frame_resources(context())
    assert {source.relative_to(PACKAGE).as_posix() for source in sources if "/manual/" in str(source)} == set(INPUTS)


@pytest.mark.parametrize("value", [None, 0, -1, "869", True])
def test_reviewed_board_metadata_rejects_unknown_or_invalid_dimensions(value):
    item = next(item for item in read("evals/visual-checkpoints.json")["captures"] if item["status"] == "reusable")
    item["media"]["width"] = value
    with pytest.raises(scaffold.ScaffoldError, match="positive integer width"):
        scaffold.reviewed_media_caption(context(), item)


def test_reference_readmes_derive_step_coverage_and_deduplicate_shared_images():
    ctx = context()
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
        assert "three\nlabeled views from two" not in rendered


def test_manual_bundle_is_narrow_exact_and_deterministic_without_an_import_claim():
    manifest = read("export-manifest.json")
    bundle = manifest["bundle"]
    assert manifest["raw_base"] == scaffold.DEFAULT_RAW_BASE
    assert "/microsoft/aibast-agents-library/tree/main/" in manifest["github_folder"]
    assert bundle["kind"] == "manual-inputs"
    assert bundle["native_importable"] is bundle["standalone_guide"] is False
    expected = {PREFIX + path for path in INPUTS} | {
        PREFIX + "evals/manual-inputs-r5.json", PREFIX + "exports/README.md",
    }
    assert set(bundle["include_paths"]) == expected
    with zipfile.ZipFile(ROOT / bundle["path"]) as archive:
        assert set(archive.namelist()) == expected
        assert len(archive.namelist()) == 11
        assert archive.testzip() is None
        for name in archive.namelist():
            assert archive.read(name) == (ROOT / name).read_bytes()
            assert not PRIVATE.search(archive.read(name).decode()), name
    included = {item["path"] for item in manifest["files"] if item["included_in_bundle"]}
    assert included == expected
    assert not any(name.endswith((".html", ".png", ".jpg", ".gif", ".zip", ".py", ".yml")) for name in expected)
    assert "not a standalone workshop" in bundle["description"]
    # HTML hosting normalization remains intentional; Markdown is never normalized.
    assert build_solution_export.bundle_bytes(PACKAGE / "manual/GLOBAL-INSTRUCTIONS.md") == (PACKAGE / "manual/GLOBAL-INSTRUCTIONS.md").read_bytes()


def test_historical_metadata_failures_and_native_archive_stay_separate_and_intact():
    index = read("evals/history/2026-08/index.json")
    assert len(index["files"]) == 5
    for item in index["files"]:
        assert digest((ROOT / item["archived_path"]).read_bytes()) == item["sha256"]
    historical = read("evals/history/2026-08/manual-build-evidence.json")
    assert historical["status"] == "passed"
    assert historical["captured_at"].startswith("2026-08-")
    review = read("evals/manual-pilot-review.json")
    failures = review["historical_failures"]
    assert [item["revision"] for item in failures] == ["r1", "r2", "r3", "r4"]
    assert [(len(item["passed"]), len(item["failed"])) for item in failures] == [(2, 4), (2, 4), (3, 3), (5, 1)]
    assert failures[-1]["failed"] == ["PRB-03"]
    assert len(review["r5_changes_from_r4"]) == 4
    metadata = read("exports/portfolio-rebalancing-solution-export.json")
    assert metadata["source_contract_status"] == "stale_source"
    assert metadata["manual_content_inventory"] == {"archive_entries": 5, "skills": 0, "knowledge_files": 0}
    assert metadata["sha256"] == "a8563232136a44717647e858fcee2b5d2cba9d78100201278ea5beac592b69a8"
    assert digest((ROOT / metadata["zip"]).read_bytes()) == metadata["sha256"]
    with zipfile.ZipFile(ROOT / metadata["zip"]) as archive:
        assert archive.namelist() == review["historical_native_export"]["entries"]
    inventory = json.loads((ROOT / "state/copilot_studio_solution_exports.json").read_text())
    assert next(item for item in inventory["solutions"] if item["slug"] == "portfolio-rebalancing") == metadata
    for page in ("quest.html", "field-guide.html", "manual-tutorial.html", "evidence-report.html"):
        assert not re.search(r'href="[^"]*portfolio-rebalancing-copilot-studio-solution\.zip"', (PACKAGE / page).read_text())


def test_current_public_metadata_and_guides_do_not_publish_private_browser_provenance():
    for relative in (
        "evals/manual-build-evidence.json", "evals/manual-pilot-review.json",
        "evals/manual-inputs-r5.json", "evals/visual-checkpoints.json",
        "screenshots/manual/repaired-r5/browserfilm.json", "deployment.json",
        "README.md", "manual-tutorial.html", "quest.html", "field-guide.html",
        "evidence-report.html", "EASY-MODE-PERSONLESS.md", "EASY-MODE-COPILOT-CHAT.md",
    ):
        assert not PRIVATE.search((PACKAGE / relative).read_text()), relative
    deployment = read("deployment.json")["copilot_studio"]
    assert deployment["required_connections"] == []
    assert len(deployment["production_replacement_connections"]) == 5
    assert deployment["validated_manual"]["preview_cases_passed"] == 6
    assert deployment["validated_pilot"]["preview_cases_passed"] is None
