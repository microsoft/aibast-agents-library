import hashlib
import html
import json
import re
import struct
import zipfile
from pathlib import Path

from tools.build_solution_export import bundle_bytes
from tools.scaffold_solution_journey import manual_evidence_passed


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "solutions/prior-authorization"
REVISION = "shared-grounding-r4"
FOOTER = (
    "Synthetic healthcare evidence only; no diagnosis, treatment, eligibility, "
    "authorization, scheduling, outreach, submission, or record change. Human review required."
)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def test_prior_current_manual_evidence_is_the_reviewed_native_regression():
    evidence = read_json(PACKAGE / "evals/manual-build-evidence.json")
    assert evidence["build_revision"] == REVISION
    assert evidence["status"] == "passed"
    assert manual_evidence_passed(evidence)
    assert evidence["target_model"] == "Claude Sonnet 4.6"
    assert evidence["lane_scope"] == "native_manual_only"
    assert evidence["native_regression"]["passed"] == 4
    assert evidence["native_regression"]["total"] == 4
    assert evidence["native_regression"]["older_passes_carried_forward"] is False
    assert evidence["persistence"]["saved_left_through_agents_reopened"] is True
    assert evidence["persistence"]["complete_global_policy_matches"] is True
    assert evidence["persistence"]["all_four_complete_skill_bodies_names_descriptions_match"] is True
    assert evidence["publication_gate"]["same_tested_identity_confirmed_by_navigation"] is True
    assert evidence["publication_gate"]["required_state"] == "Draft"
    assert evidence["publication_gate"]["published"] is False
    cases = read_json(ROOT / "tests/demo_cases/prior-authorization.json")["cases"]
    actual = {case["case_id"]: case for case in evidence["canonical_preview"]}
    assert set(actual) == {case["id"] for case in cases}
    for case in cases:
        result = actual[case["id"]]
        assert result["prompt"] == case["prompt"]
        assert result["status"] == "passed"
        assert result["submission_count"] == 1
        assert result["fresh_native_conversation"] is True
        answer = result["assistant_response"]
        assert sha256(answer.encode()) == result["final_answer_sha256"]
        assert len(answer.split()) >= case["min_words"]
        assert all(anchor in answer for anchor in case["must_include"])
        assert all(text.lower() not in answer.lower() for text in case["must_not_include"])
        assert answer.rstrip().endswith(FOOTER)
        assert result["native_activity"]["matching_skill_loaded"] is True
        assert result["native_activity"]["structured_knowledge_searches"] >= 1
        assert result["citation_sources"]
    assert "Criteria-to-Evidence Crosswalk" not in actual["PA-01"]["assistant_response"]
    appeal = actual["PA-04"]["assistant_response"]
    assert "The synthetic source does not state why this workflow state was recorded." in appeal
    assert "gap driving" not in appeal
    assert "gap to address" not in appeal


def test_prior_reference_set_covers_all_steps_without_relabeling_replacements():
    evidence = read_json(PACKAGE / "evals/manual-build-evidence.json")
    film = read_json(ROOT / evidence["browserfilm"]["manifest"])
    visual = read_json(PACKAGE / "evals/visual-checkpoints.json")
    assert film["kind"] == "reviewed-reference-set"
    assert len(film["frames"]) == 18
    assert all(frame["captured"] is True for frame in film["frames"])
    assert evidence["browserfilm"]["open_steps"] == []
    steps = {item["step"]: item for item in visual["captures"] if item["mode"] == "hard"}
    assert set(steps) == set(range(1, 19))
    assert visual["summary"]["manual_build_steps_open"] == 0
    for number, frame in enumerate(film["frames"], start=1):
        checkpoint = steps[number]
        assert checkpoint["status"] == "reusable"
        assert checkpoint["source"].endswith(frame["file"])
        image = (ROOT / checkpoint["annotated"]).read_bytes()
        media = checkpoint["media"]
        assert image.startswith(b"\x89PNG\r\n\x1a\n")
        assert sha256(image) == media["sha256"]
        assert struct.unpack(">II", image[16:24]) == (media["width"], media["height"])
        assert media["private_originals"] is True
        assert media["view_count"] > 0 and media["capture_count"] > 0
        assert checkpoint["reviewed_at"] and checkpoint["review_provenance"]
    for number in (3, 6, 7, 8, 9, 10):
        assert steps[number]["evidence_stage"] == "existing_draft_replacement"
        assert "not" in steps[number]["media"]["scope"]
    assert steps[11]["capture_revision"] == "initial-r1"
    assert steps[9]["capture_revision"] == "line-templates-r2"
    tutorial = (PACKAGE / "manual-tutorial.html").read_text(encoding="utf-8")
    assert "leave, reopen the same Draft, and compare the full persisted text" in tutorial
    assert "policy is visible or saved" not in tutorial
    expected_sources = {
        6: "manual/knowledge/aibast_prior-authorization-review-rules.md",
        7: "manual/knowledge/aibast_prior-authorization-synthetic-records.md",
        8: "manual/skills/appeal-evidence-packet/SKILL.md",
        9: "manual/skills/criteria-evidence/SKILL.md",
        10: "manual/skills/request-evidence/SKILL.md",
        11: "manual/skills/status-summary/SKILL.md",
    }
    for number, source in expected_sources.items():
        assert film["frames"][number - 1]["source_path"] == source
        section = tutorial.split(f'id="step-{number}"', 1)[1].split("</article>", 1)[0]
        assert f'href="{source}" download' in section
    payloads = {
        int(number): html.unescape(content)
        for number, content in re.findall(
            r'<pre class="copy-source" id="hard-copy-(\d+)" hidden>(.*?)</pre>',
            tutorial,
            re.DOTALL,
        )
    }
    assert payloads[3] == (PACKAGE / "manual/GLOBAL-INSTRUCTIONS.md").read_text(encoding="utf-8")
    cases = read_json(ROOT / "tests/demo_cases/prior-authorization.json")["cases"]
    for number, case in enumerate(cases, start=14):
        assert payloads[number] == case["prompt"]


def test_prior_bundle_and_download_manifest_match_the_frozen_inputs_and_cases():
    inventory = read_json(PACKAGE / "evals/manual-inputs-r4.json")
    manifest = read_json(PACKAGE / "export-manifest.json")
    assert inventory["source_commit"] == "434dc32418d13317c2891a58d7cb5aa381a8c515"
    assert len(inventory["inputs"]) == 7
    for item in inventory["inputs"]:
        payload = (ROOT / item["path"]).read_bytes()
        assert len(payload) == item["bytes"]
        assert sha256(payload) == item["sha256"]
    locked = inventory["locked_cases"]
    assert locked["path"] == "tests/demo_cases/prior-authorization.json"
    assert sha256((ROOT / locked["path"]).read_bytes()) == locked["sha256"]
    assert manifest["raw_base"] == "https://raw.githubusercontent.com/kody-w/aibast-agents-library/staging/"
    assert manifest["bundle"]["native_importable"] is False
    assert manifest["bundle"]["standalone_guide"] is False
    assert locked["path"] in manifest["bundle"]["include_paths"]
    resources = {item["path"]: item for item in manifest["files"]}
    assert resources[locked["path"]]["included_in_bundle"] is True
    for item in manifest["files"]:
        assert item["raw_url"] == manifest["raw_base"] + item["path"]
    with zipfile.ZipFile(ROOT / manifest["bundle"]["path"]) as archive:
        assert set(archive.namelist()) == set(manifest["bundle"]["include_paths"])
        for name in archive.namelist():
            assert archive.read(name) == bundle_bytes(ROOT / name)
        assert all("/copilot-studio/" not in name for name in archive.namelist())
        assert all("/history/" not in name for name in archive.namelist())


def test_prior_incomplete_historical_import_is_withheld_consistently():
    metadata = read_json(PACKAGE / "exports/prior-authorization-solution-export.json")
    inventory = read_json(ROOT / "state/copilot_studio_solution_exports.json")
    row = next(item for item in inventory["solutions"] if item["slug"] == "prior-authorization")
    assert row == metadata
    assert row["source_contract_status"] == "stale_source"
    assert row["manual_content_inventory"] == {"archive_entries": 5, "skills": 0, "knowledge_files": 0}
    assert sha256((ROOT / row["zip"]).read_bytes()) == row["sha256"]
    with zipfile.ZipFile(ROOT / row["zip"]) as archive:
        assert len(archive.namelist()) == 5
    for name in ("quest.html", "evidence-report.html", "manual-tutorial.html"):
        page = (PACKAGE / name).read_text(encoding="utf-8")
        assert "Download Copilot Studio solution" not in page
    evidence = read_json(PACKAGE / "evals/manual-build-evidence.json")
    assert "Historical" in evidence["lane_evidence_note"]
    assert read_json(PACKAGE / "evals/copilot-studio-preview-evidence.json")["evidence_status"] == "historical_not_revalidated"


def test_prior_history_and_promise_mapping_preserve_the_evidence_boundary():
    history = read_json(PACKAGE / "evals/history/2026-08/index.json")
    assert history["status"] == "historical_only"
    for item in history["files"]:
        assert sha256((ROOT / item["archived_path"]).read_bytes()) == item["sha256"]
    promises = read_json(PACKAGE / "evals/onepager-map.json")["promises"]
    by_case = {case: promise for promise in promises for case in promise["demo_cases"]}
    assert by_case["PA-01"]["operations"] == ["request_evidence"]
    assert by_case["PA-01"]["advertised_promise"].startswith("Compile")
    assert by_case["PA-02"]["operations"] == ["criteria_evidence"]
    assert by_case["PA-02"]["advertised_promise"].startswith("Pull")
    review = read_json(PACKAGE / "evals/manual-pilot-review.json")
    assert len(review["historical_failures"]) == 3
    assert review["accepted_student_steps"] == list(range(1, 19))
    assert review["open_student_steps"] == []
    readme = (PACKAGE / "README.md").read_text(encoding="utf-8")
    assert "No global Brainstem capture, Copilot Studio project" not in readme
