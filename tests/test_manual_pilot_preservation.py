import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

from tools.promote_solution_draft import parse_yaml_scalar, render_settings, render_skill
from tools.scaffold_solution_journey import manual_evidence_passed


ROOT = Path(__file__).resolve().parents[1]
SLUGS = ("fs-customer-onboarding", "fs-regulatory-compliance")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalized(text):
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def test_dated_status_snapshot_counts_its_roster_without_certifying_reports():
    snapshot = read(ROOT / "state/manual_workshop_pilot_2026-09-12.json")
    assert snapshot["as_of"].startswith("2026-09-12T")
    assert snapshot["captured_revision"] == 88
    assert snapshot["status"] == "incomplete"
    assert snapshot["certification_claim"] is False
    assert snapshot["counts"] == dict(Counter(snapshot["workshops"].values()))
    assert sum(snapshot["counts"].values()) == snapshot["target_total"] == 51
    assert set(snapshot["status_definitions"]) == {
        "complete", "reported_complete", "blocked", "in_progress", "pending"
    }
    assert snapshot["workshops"]["portfolio-rebalancing"] == "in_progress"
    for slug, path in snapshot["preservation_reviews"].items():
        assert slug in SLUGS
        assert snapshot["workshops"][slug] == "blocked"
        assert read(ROOT / path)["certified"] is False


def test_promoted_manual_files_match_reviewed_payload_fingerprints_and_native_source():
    for slug in SLUGS:
        package = ROOT / "solutions" / slug
        review = read(package / "evals/manual-pilot-review.json")
        for source in review["promoted_manual_sources"]:
            assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["packaged_sha256"]
            assert source["comparison"] == "exact content; terminal newline normalized"
        for source in review["knowledge_sources"]:
            digest = hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest()
            assert digest == source["packaged_sha256"]
            assert source["changed_since_live_capture"] == (
                source["tested_sha256"] != source["packaged_sha256"]
            )
        settings_path = package / "copilot-studio/settings.mcs.yml"
        settings = settings_path.read_text()
        expected = render_settings(
            parse_yaml_scalar(settings, "displayName"),
            parse_yaml_scalar(settings, "schemaName"),
            (package / "manual/GLOBAL-INSTRUCTIONS.md").read_text(),
        )
        assert settings == normalized(expected)
        for path in (package / "manual/skills").glob("*/SKILL.md"):
            rendered, fields = render_skill(path)
            native = package / "copilot-studio/behaviors" / f"aibast_{fields['name']}.mcs.yml"
            assert native.read_text() == normalized(rendered)


def test_reviewed_findings_do_not_replace_live_regression_or_visual_acceptance():
    for slug, count in zip(SLUGS, (4, 5)):
        package = ROOT / "solutions" / slug
        review = read(package / "evals/manual-pilot-review.json")
        evidence = read(package / "evals/manual-build-evidence.json")
        visual = read(package / "evals/visual-checkpoints.json")
        cases = read(ROOT / "tests/demo_cases" / f"{slug}.json")["cases"]
        assert review["status"] == "blocked"
        assert review["certified"] is False
        assert review["reported_passing_responses"] == count
        assert review["historical_failures"]
        assert review["open_gates"]
        assert not manual_evidence_passed(evidence)
        assert [case["case_id"] for case in evidence["canonical_preview"]] == [case["id"] for case in cases]
        assert [case["prompt"] for case in evidence["canonical_preview"]] == [case["prompt"] for case in cases]
        assert all(case["passed"] is None for case in evidence["canonical_preview"])
        assert all(case["status"] == "reshoot_required" for case in evidence["canonical_preview"])
        assert all(case["review_criteria"] for case in evidence["canonical_preview"])
        assert visual["summary"]["reusable"] == 0
        assert visual["summary"]["reshoot_required"] == len(visual["captures"])
        assert all(capture["status"] == "reshoot_required" for capture in visual["captures"])
        tutorial = (package / "manual-tutorial.html").read_text()
        assert not re.search(r"<img\b", tutorial)
        assert "Source tests are not live validation" in tutorial
        assert "Preservation review, not certification" in tutorial

    regulatory = read(ROOT / "solutions/fs-regulatory-compliance/evals/manual-pilot-review.json")
    assert regulatory["final_revision_timing"]["full_final_revision_regression_proven"] is False
    assert regulatory["final_revision_timing"]["selected_cases_before_replacement"] == ["RC-02", "RC-03", "RC-04"]
    discrepancies = {case["case_id"]: case["discrepancy"]
                     for case in regulatory["case_checks"] if "discrepancy" in case}
    assert set(discrepancies) == {"RC-03", "RC-05"}


def test_manual_bundles_are_explicit_public_safe_sources_not_native_imports():
    forbidden = re.compile(
        r"/Users/|[A-Z]:\\\\Users\\\\|copilotstudio\.preview\.microsoft\.com/environments/"
        r"|login\.microsoftonline\.com|github_pat_|gh[opsu]_[A-Za-z0-9]{20,}"
        r"|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        re.IGNORECASE,
    )
    for slug in SLUGS:
        package = ROOT / "solutions" / slug
        manifest = read(package / "export-manifest.json")
        assert manifest["raw_base"] == "https://raw.githubusercontent.com/kody-w/aibast-agents-library/staging/"
        assert "/kody-w/aibast-agents-library/tree/staging/" in manifest["github_folder"]
        assert manifest["bundle"]["native_importable"] is False
        assert manifest["copilot_studio_solution"]["status"] == "stale_source"
        assert "solution_unique_name" not in manifest["copilot_studio_solution"]
        with zipfile.ZipFile(ROOT / manifest["bundle"]["path"]) as archive:
            assert set(archive.namelist()) == set(manifest["bundle"]["include_paths"])
            assert not any(name.endswith((".zip", ".jpg", ".png", ".gif")) for name in archive.namelist())
            for name in archive.namelist():
                text = archive.read(name).decode("utf-8")
                assert not forbidden.search(text), name
                assert not name.endswith("dataverse-draft-evidence.json")
        native = read(package / "exports" / f"{slug}-solution-export.json")
        assert native["manual_content_inventory"] == {
            "archive_entries": 5, "skills": 0, "knowledge_files": 0
        }
        with zipfile.ZipFile(ROOT / native["zip"]) as archive:
            assert len(archive.namelist()) == 5
            config_path = next(name for name in archive.namelist() if name.endswith("/configuration.json"))
            config = json.loads(archive.read(config_path))
            assert set(config["agentSettings"]) == {"$kind", "model", "instructions"}
            assert not any(name.endswith((".md", ".yml", ".yaml")) for name in archive.namelist())


def test_regulatory_upload_links_bind_the_named_files_not_sorted_positions():
    package = ROOT / "solutions/fs-regulatory-compliance"
    tutorial = (package / "manual-tutorial.html").read_text()
    expected = {
        8: "manual/knowledge/aibast_fs-regulatory-compliance-synthetic-records.md",
        9: "manual/knowledge/aibast_fs-regulatory-compliance-rules-and-controls.md",
        12: "manual/skills/aibast_compliance-dashboard_rc01/SKILL.md",
        13: "manual/skills/aibast_trade-surveillance_rc02/SKILL.md",
        16: "manual/skills/aibast_certification-tracker_rc05/SKILL.md",
    }
    for step, path in expected.items():
        block = re.search(rf'<article class="step" id="step-{step}">(.*?)</article>', tutorial, re.DOTALL)[1]
        assert f'href="{path}" download' in block
