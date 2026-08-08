import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "solutions" / "fs-regulatory-compliance"
RAW_BASE = "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/"

EXPECTED_RESOURCE_IDS = {
    "export-manifest",
    "portable-agent",
    "deployment-recipe",
    "field-guide",
    "global-instructions",
    "knowledge-records",
    "knowledge-rules",
    "skill-compliance-dashboard",
    "skill-trade-surveillance",
    "skill-documentation-review",
    "skill-remediation-submission",
    "skill-certification-tracker",
    "onepager-map",
    "brainstem-transcripts",
    "source-audit",
    "studio-preview-evidence",
    "assisted-browserfilm-manifest",
    "assisted-browserfilm",
    "assisted-contact-sheet",
    "manual-tutorial",
    "manual-evidence",
    "manual-browserfilm-manifest",
    "manual-browserfilm",
    "manual-contact-sheet",
    "quest",
    "exports-readme",
}

EXPECTED_SCREENSHOTS = [
    "01-create-blank-agent.jpg",
    "02-name-manual-agent.jpg",
    "03-enter-global-instructions.jpg",
    "04-save-global-instructions.jpg",
    "05-open-web-search-settings.jpg",
    "06-remove-web-search.jpg",
    "07-open-knowledge-upload.jpg",
    "08-upload-synthetic-records.jpg",
    "09-upload-rules-controls.jpg",
    "10-verify-two-knowledge-files.jpg",
    "11-open-skill-upload.jpg",
    "12-upload-dashboard-skill.jpg",
    "13-upload-surveillance-skill.jpg",
    "14-upload-documentation-skill.jpg",
    "15-upload-remediation-skill.jpg",
    "16-upload-certification-skill.jpg",
    "17-open-model-picker.jpg",
    "18-select-sonnet46.jpg",
    "19-review-complete-inventory.jpg",
    "20-open-preview.jpg",
    "21-preview-rc01-audit-readiness.jpg",
    "22-preview-rc02-certifications.jpg",
    "23-preview-rc03-trade-surveillance.jpg",
    "24-preview-rc04-algorithm-go-live.jpg",
    "25-preview-rc05-board-evidence.jpg",
    "26-confirm-draft-no-publish.jpg",
]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def tutorial_steps():
    tutorial = (PACKAGE / "manual-tutorial.html").read_text(encoding="utf-8")
    match = re.search(
        r'<script type="application/json" id="step-data">\s*(\[.*?\])\s*</script>',
        tutorial,
        re.DOTALL,
    )
    assert match
    return tutorial, json.loads(match.group(1))


def test_export_manifest_contains_every_tutorial_resource():
    manifest = read_json(PACKAGE / "export-manifest.json")
    assert manifest["solution"] == "@aibast-agents-library/fs-regulatory-compliance"
    assert manifest["bundle"]["status"] == "complete"
    resources = {item["id"]: item for item in manifest["files"]}
    assert set(resources) == EXPECTED_RESOURCE_IDS
    for item in resources.values():
        path = ROOT / item["path"]
        assert path.exists(), item["path"]
        assert item["raw_url"] == RAW_BASE + item["path"]
    assert resources["manual-evidence"]["evidence_status"] == "captured"
    assert resources["manual-browserfilm"]["evidence_status"] == "captured"
    assert resources["manual-contact-sheet"]["evidence_status"] == "captured"


def test_manual_tutorial_is_clawpilot_themed_and_action_complete():
    tutorial, steps = tutorial_steps()
    assert "scoutTheme" in tutorial
    assert 'document.documentElement.setAttribute("data-theme", theme);' in tutorial
    for token in (
        "--cp-bg:",
        "--cp-surface:",
        "--cp-border:",
        "--cp-text:",
        "--cp-accent:",
        "--cp-success:",
        "--cp-warning:",
        "--cp-link:",
        "--cp-shadow:",
    ):
        assert token in tutorial
    assert (
        '"Segoe UI", Aptos, Calibri, -apple-system, BlinkMacSystemFont, sans-serif'
        in tutorial
    )

    assert len(steps) == 26
    assert [step["screenshot"] for step in steps] == EXPECTED_SCREENSHOTS
    assert all(step["action"] for step in steps)
    assert all(step["expected"] for step in steps)
    assert all(step["resourceId"] for step in steps)
    assert all(step["troubleshooting"] for step in steps)
    assert "Screenshot unavailable" in tutorial
    assert "Raw download:" in tutorial


def test_manual_sequence_covers_every_required_browser_action():
    tutorial, steps = tutorial_steps()
    combined = " ".join(
        f"{step['title']} {step['action']} {step['expected']}" for step in steps
    )
    for phrase in (
        "Create a blank agent",
        "Remove web search",
        "Exactly two custom Markdown knowledge files",
        "fifth and final skill",
        "Claude Sonnet 4.6",
        "Review complete inventory",
        "Run RC-01",
        "Run RC-02",
        "Run RC-03",
        "Run RC-04",
        "Run RC-05",
        "Confirm Draft and stop",
    ):
        assert phrase in combined
    assert "one browser action · one expected screenshot" in tutorial.lower()


def test_browserfilm_and_manual_evidence_are_captured():
    browserfilm = read_json(PACKAGE / "screenshots" / "manual" / "browserfilm.json")
    assert browserfilm["status"] == "captured"
    assert [frame["file"] for frame in browserfilm["frames"]] == EXPECTED_SCREENSHOTS
    assert all(frame["captured"] is True for frame in browserfilm["frames"])
    assert all(frame["duration_ms"] > 0 for frame in browserfilm["frames"])

    evidence = read_json(PACKAGE / "evals" / "manual-build-evidence.json")
    assert evidence["status"] == "passed"
    assert evidence["model_confirmed"] is True
    assert evidence["manual_components"]["knowledge_files"] == {
        "expected": 2,
        "confirmed": 2,
    }
    assert evidence["manual_components"]["skills"] == {
        "expected": 5,
        "confirmed": 5,
    }
    assert len(evidence["canonical_preview"]) == 5
    assert all(case["passed"] is True for case in evidence["canonical_preview"])
    assert evidence["publication_gate"]["published"] is False
    assert evidence["publication_gate"]["required_state"] == "Draft"
    assert evidence["manual_agent"]["bot_id"] == "ad9993c3-ea7a-4ecf-a86b-40a9d39a4fa3"


def test_quest_exposes_easy_and_true_manual_paths():
    quest = (PACKAGE / "quest.html").read_text(encoding="utf-8")
    assert "Easy mode" in quest
    assert "Manual Hard mode" in quest
    assert "Upload five SKILL.md files" in quest
    assert "Remove web search and add knowledge" in quest
    assert "Select Sonnet46 and review inventory" in quest
    assert "Run the five-case Preview" in quest
    assert "Enforce the no-publish gate" in quest
    assert "manual screenshots" in quest
