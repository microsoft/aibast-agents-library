import hashlib
import html
import json
import re
import zipfile
from pathlib import Path

from tools.build_solution_export import bundle_bytes
from tools.scaffold_solution_journey import manual_evidence_passed


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "solutions/prior-authorization"
# The shared-grounding-r4 native pilot (and its incomplete historical import)
# was superseded by the full re-shoot in the real Copilot Studio UI. Its
# records stay under evals/history/; these tests protect the current package.
SKILLS = (
    "appeal-evidence-packet", "approval-outlook", "criteria-evidence", "denial-review",
    "patient-auth-request", "payer-requirements-check", "portfolio-status",
    "request-evidence", "status-summary", "submission-packet", "tracking-plan",
)
FOOTER = (
    "Synthetic healthcare evidence only; no diagnosis, treatment, eligibility, "
    "authorization, scheduling, outreach, submission, or record change. Human review required."
)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def test_prior_current_manual_evidence_passes_every_locked_case_and_stays_draft():
    evidence = read_json(PACKAGE / "evals/manual-build-evidence.json")
    assert evidence["status"] == "passed"
    assert manual_evidence_passed(evidence)
    assert evidence["target_model"] == "Claude Opus 5"
    assert evidence["model_confirmed"] is True
    for legacy in ("build_revision", "lane_scope", "native_regression", "review_snapshot"):
        assert legacy not in evidence
    components = evidence["manual_components"]
    assert components["skills"] == {"expected": len(SKILLS), "confirmed": len(SKILLS)}
    assert components["knowledge_files"] == {"expected": 2, "confirmed": 2}
    assert components["tools"] == {"expected": 0, "confirmed": 0}
    assert evidence["publication_gate"]["required_state"] == "Draft"
    assert evidence["publication_gate"]["published"] is False
    cases = read_json(ROOT / "tests/demo_cases/prior-authorization.json")["cases"]
    assert len(cases) == 11
    actual = {case["case_id"]: case for case in evidence["canonical_preview"]}
    assert set(actual) == {case["id"] for case in cases}
    for case in cases:
        result = actual[case["id"]]
        assert result["prompt"] == case["prompt"]
        assert result["must_include"] == case["must_include"]
        assert result["must_not_include"] == case["must_not_include"]
        assert result["passed"] is True
        assert (PACKAGE / "screenshots/manual" / result["expected_screenshot"]).is_file()


def test_prior_reference_set_covers_all_steps_with_current_sources():
    evidence = read_json(PACKAGE / "evals/manual-build-evidence.json")
    film = read_json(ROOT / evidence["browserfilm"]["manifest"])
    visual = read_json(PACKAGE / "evals/visual-checkpoints.json")
    frames = film["frames"]
    assert len(frames) == 34
    assert all(frame["captured"] is True for frame in frames)
    steps = {item["step"]: item for item in visual["captures"] if item["mode"] == "hard"}
    assert set(steps) == set(range(1, len(frames) + 1))
    assert visual["summary"]["reshoot_required"] == 0
    for number, frame in enumerate(frames, start=1):
        checkpoint = steps[number]
        assert checkpoint["status"] == "reusable"
        assert checkpoint["source"].endswith(frame["file"])
        image = (ROOT / checkpoint["annotated"]).read_bytes()
        assert image.startswith(b"\x89PNG\r\n\x1a\n")
    tutorial = (PACKAGE / "manual-tutorial.html").read_text(encoding="utf-8")
    expected_sources = {
        6: "manual/knowledge/aibast_prior-authorization-review-rules.md",
        7: "manual/knowledge/aibast_prior-authorization-synthetic-records.md",
        **{8 + index: f"manual/skills/{name}/SKILL.md" for index, name in enumerate(SKILLS)},
    }
    for number, source in expected_sources.items():
        assert (PACKAGE / source).is_file()
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
    for number, case in enumerate(cases, start=23):
        assert payloads[number] == case["prompt"]
    assert "Confirm Draft and stop before publish" in tutorial


def test_prior_bundle_and_download_manifest_ship_the_current_sources():
    manifest = read_json(PACKAGE / "export-manifest.json")
    assert manifest["raw_base"] == "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/"
    assert manifest["bundle"]["path"] == "solutions/prior-authorization/exports/prior-authorization-source.zip"
    assert "include_paths" not in manifest["bundle"]
    assert "native_importable" not in manifest["bundle"]
    assert "source_bundle" not in read_json(PACKAGE / "deployment.json")
    for item in manifest["files"]:
        assert item["raw_url"] == manifest["raw_base"] + item["path"]
    inputs = [
        "manual/GLOBAL-INSTRUCTIONS.md",
        "manual/knowledge/aibast_prior-authorization-review-rules.md",
        "manual/knowledge/aibast_prior-authorization-synthetic-records.md",
        *(f"manual/skills/{name}/SKILL.md" for name in SKILLS),
    ]
    with zipfile.ZipFile(ROOT / manifest["bundle"]["path"]) as archive:
        names = set(archive.namelist())
        for name in names:
            assert archive.read(name) == bundle_bytes(ROOT / name)
        for relative in inputs:
            assert f"solutions/prior-authorization/{relative}" in names
    # A shipped input inventory must hash the bytes it ships. The superseded
    # r4 inventory pins old policy/knowledge/case bytes.
    stale = "solutions/prior-authorization/evals/manual-inputs-r4.json"
    if (ROOT / stale).exists():
        inventory = read_json(ROOT / stale)
        current = all(
            sha256((ROOT / item["path"]).read_bytes()) == item["sha256"]
            for item in [*inventory["inputs"], inventory["locked_cases"]]
        )
        manifest_paths = {item["path"] for item in manifest["files"]}
        assert current or (stale not in names and stale not in manifest_paths), (
            "superseded manual-inputs-r4.json still ships with hashes that no longer match"
        )


def test_prior_current_native_export_is_unpublished_and_offered_consistently():
    metadata = read_json(PACKAGE / "exports/prior-authorization-solution-export.json")
    inventory = read_json(ROOT / "state/copilot_studio_solution_exports.json")
    row = next(item for item in inventory["solutions"] if item["slug"] == "prior-authorization")
    assert row == metadata
    assert row["status"] == "exported"
    assert row["published"] is False
    assert row["managed"] is False
    assert "source_contract_status" not in row
    assert sha256((ROOT / row["zip"]).read_bytes()) == row["sha256"]
    assert row["sha256"] != read_json(PACKAGE / "evals/history/2026-08/prior-authorization-solution-export.json")["sha256"]
    for name in ("quest.html", "evidence-report.html"):
        page = (PACKAGE / name).read_text(encoding="utf-8")
        assert "Download Copilot Studio solution" in page
    preview = read_json(PACKAGE / "evals/copilot-studio-preview-evidence.json")
    assert "evidence_status" not in preview
    assert preview["status"] == "Draft"
    assert preview["published"] is False


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
    readme = (PACKAGE / "README.md").read_text(encoding="utf-8")
    assert "No global Brainstem capture, Copilot Studio project" not in readme
    for page in ("quest.html", "manual-tutorial.html", "evidence-report.html"):
        text = (PACKAGE / page).read_text(encoding="utf-8")
        assert "historical import withheld" not in text
        assert "manual-pilot-review.json" not in text
    assert FOOTER in (PACKAGE / "manual/GLOBAL-INSTRUCTIONS.md").read_text(encoding="utf-8")
