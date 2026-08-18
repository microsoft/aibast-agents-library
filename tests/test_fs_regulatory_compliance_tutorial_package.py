import html
import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "solutions" / "fs-regulatory-compliance"
CASE_FILE = ROOT / "tests" / "demo_cases" / "fs-regulatory-compliance.json"

REQUIRED_RESOURCE_IDS = {
    "portable-agent",
    "deployment-recipe",
    "field-guide",
    "field-guide-source",
    "settings",
    "agent-sync",
    "manual-instructions",
    "easy-mode-brainstem-skill",
    "easy-mode-copilot-skill",
    "generic-workshop-agent",
    "brainstem-transcripts",
    "manual-evidence",
    "assisted-browserfilm-manifest",
    "assisted-browserfilm",
    "assisted-contact-sheet",
    "manual-browserfilm-manifest",
    "manual-browserfilm",
    "manual-contact-sheet",
    "easy-evidence-visual-checkpoints",
    "workshop-settings",
    "evidence-report",
    "quest",
    "manual-tutorial",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def plain_text(value):
    return " ".join(
        html.unescape(re.sub(r"<[^>]+>", " ", value)).split()
    )


def tutorial_steps(tutorial):
    matches = re.findall(
        r'<article class="step" id="step-(\d+)">(.*?)</article>',
        tutorial,
        re.DOTALL,
    )
    steps = []
    for number, block in matches:
        heading = re.search(r"<h3>(.*?)</h3>", block, re.DOTALL)
        assert heading
        downloads = []
        for attrs, label in re.findall(
            r"<a\b([^>]*)>(.*?)</a>", block, re.DOTALL | re.IGNORECASE
        ):
            if plain_text(label).startswith("Download source:"):
                href = re.search(r'href="([^"]+)"', attrs)
                assert href
                assert re.search(r"\bdownload(?:\s|=|$)", attrs)
                downloads.append(href.group(1))
        steps.append(
            {
                "number": int(number),
                "title": plain_text(heading.group(1)),
                "text": plain_text(block),
                "images": re.findall(
                    r'<img\b[^>]*\bsrc="([^"]+)"',
                    block,
                    re.IGNORECASE,
                ),
                "reports": len(
                    re.findall(r"<[^>]+\bdata-report-location=", block)
                ),
                "downloads": downloads,
                "report_evidence": re.findall(
                    r'data-report-evidence="([^"]*)"', block
                ),
            }
        )
    return steps


def test_export_manifest_contains_required_course_resources_and_zip_contract():
    manifest = read_json(PACKAGE / "export-manifest.json")
    assert manifest["solution"] == "@aibast-agents-library/fs-regulatory-compliance"
    resources = {item["id"]: item for item in manifest["files"]}
    assert REQUIRED_RESOURCE_IDS <= resources.keys()
    assert any(resource_id.startswith("knowledge-") for resource_id in resources)
    assert any(resource_id.startswith("skill-") for resource_id in resources)

    for item in resources.values():
        path = ROOT / item["path"]
        assert item["status"] == "ready"
        assert path.is_file(), item["path"]
        assert item["raw_url"].startswith(manifest["raw_base"])
        assert item["raw_url"].endswith(item["path"])

    for filename, brand in (
        ("field-guide.html", "AIBAST field guide"),
        ("evidence-report.html", "AIBAST evidence report"),
    ):
        page = (PACKAGE / filename).read_text(encoding="utf-8")
        assert "<style>" in page
        assert brand in page
        assert "Clawpilot" not in page

    visual = read_json(PACKAGE / "evals" / "visual-checkpoints.json")
    assert visual["schema"] == "aibast-visual-checkpoints/1.0"
    assert visual["summary"]["total_existing_captures"] == len(visual["captures"])
    assert visual["summary"]["reusable"] == sum(
        capture["status"] == "reusable" for capture in visual["captures"]
    )
    assert visual["summary"]["reshoot_required"] == sum(
        capture["status"] == "reshoot_required"
        for capture in visual["captures"]
    )

    bundle = ROOT / manifest["bundle"]["path"]
    assert bundle.is_file()
    assert manifest["bundle"]["raw_url"].startswith(manifest["raw_base"])
    with zipfile.ZipFile(bundle) as archive:
        names = set(archive.namelist())
    assert not any("/." in name or "__pycache__" in name for name in names)
    assert {item["path"] for item in manifest["files"]} <= names
    assert {
        "solutions/fs-regulatory-compliance/quest.html",
        "solutions/fs-regulatory-compliance/manual-tutorial.html",
        "solutions/fs-regulatory-compliance/field-guide.html",
        "solutions/fs-regulatory-compliance/evidence-report.html",
        "solutions/fs-regulatory-compliance/evals/visual-checkpoints.json",
        "solutions/fs-regulatory-compliance/export-manifest.json",
        "skills/aibast-easy-mode-brainstem/SKILL.md",
        "skills/aibast-easy-mode-copilot/SKILL.md",
    } <= names


def test_manual_tutorial_is_aibast_themed_and_matches_browserfilm_actions():
    tutorial = (PACKAGE / "manual-tutorial.html").read_text(encoding="utf-8")
    steps = tutorial_steps(tutorial)
    browserfilm = read_json(PACKAGE / "screenshots" / "manual" / "browserfilm.json")
    visual = read_json(PACKAGE / "evals" / "visual-checkpoints.json")

    assert "AIBAST" in tutorial
    assert "Clawpilot" not in tutorial
    assert "Report an issue" in tutorial
    assert "Beta workshop" not in tutorial
    assert "Watch assisted film" not in tutorial
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
    for token in ("data-embedded", "aibast-hard-mode-height", "postMessage"):
        assert token not in tutorial
    assert "manual-progress" in tutorial
    assert 'badgeIds.push("hard-mode-complete")' in tutorial

    assert browserfilm["schema"] == "rapp-browserfilm/1.0"
    assert browserfilm["status"] == "captured"
    frames = browserfilm["frames"]
    assert len(steps) == len(frames)
    hard_visuals = {
        capture["step"]: capture
        for capture in visual["captures"]
        if capture.get("mode") == "hard"
    }
    assert set(hard_visuals) == set(range(1, len(frames) + 1))

    for index, (step, frame) in enumerate(zip(steps, frames), start=1):
        action = re.sub(r"^\d+\s*·\s*", "", frame["label"])
        assert step["number"] == index
        assert step["title"] == action
        assert step["reports"] == 1
        assert len(step["downloads"]) == 1
        assert (PACKAGE / step["downloads"][0]).is_file()
        assert len(step["report_evidence"]) == 1
        assert step["report_evidence"][0].endswith(frame["file"])
        assert frame["duration_ms"] > 0
        assert frame["captured"] is True
        assert (PACKAGE / "screenshots" / "manual" / frame["file"]).is_file()

        checkpoint = hard_visuals[index]
        assert checkpoint["source"].endswith(frame["file"])
        if checkpoint["status"] == "reshoot_required":
            assert not step["images"]
            assert "Live verification checkpoint" in step["text"]
            assert "Withheld checkpoint" not in step["text"]
            assert "not approved for learner display" not in step["text"]
            assert checkpoint["reason"]
        else:
            assert checkpoint["status"] == "reusable"
            assert step["images"]


def test_manual_tutorial_covers_locked_cases_and_draft_gate_from_evidence():
    tutorial = (PACKAGE / "manual-tutorial.html").read_text(encoding="utf-8")
    cases = read_json(CASE_FILE)["cases"]
    evidence = read_json(PACKAGE / "evals" / "manual-build-evidence.json")
    preview = evidence["canonical_preview"]
    frame_files = {
        frame["file"]
        for frame in read_json(
            PACKAGE / "screenshots" / "manual" / "browserfilm.json"
        )["frames"]
    }

    assert [item["case_id"] for item in preview] == [
        case["id"] for case in cases
    ]
    for case, item in zip(cases, preview):
        assert item["must_include"] == case["must_include"]
        assert item["passed"] is True
        assert item["expected_screenshot"] in frame_files
        assert case["id"] in tutorial
        for marker in case["must_include"]:
            assert marker in tutorial

    gate = evidence["publication_gate"]
    assert gate["required_state"] == "Draft"
    assert gate["published"] is False
    assert gate["confirmation_screenshot"] in frame_files
    assert "Draft" in tutorial
    assert re.search(r"do not publish|stop before publish", tutorial, re.IGNORECASE)


def test_browserfilm_and_manual_evidence_are_captured():
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
    assert all(case["passed"] is True for case in evidence["canonical_preview"])
    assert evidence["publication_gate"]["published"] is False
    assert evidence["manual_agent"]["bot_id"] == "ad9993c3-ea7a-4ecf-a86b-40a9d39a4fa3"


def test_quest_exposes_beta_course_shell_and_global_easy_lanes():
    quest = (PACKAGE / "quest.html").read_text(encoding="utf-8")
    cases = read_json(CASE_FILE)["cases"]
    manual_frames = read_json(
        PACKAGE / "screenshots" / "manual" / "browserfilm.json"
    )["frames"]

    assert "AIBAST guided workshop" in quest
    assert "Clawpilot" not in quest
    assert "Report an issue" in quest
    assert "Beta workshop" not in quest
    assert "workshop-settings.html" in quest
    assert "field-guide.html" in quest
    assert "evidence-report.html" in quest
    assert "<iframe" not in quest
    assert 'class="path" data-path="hard"' in quest
    assert "Open standalone Manual-mode guide" in quest
    assert 'data-easy-lane="copilot"' in quest
    assert 'data-easy-lane="brainstem"' in quest
    assert 'localStorage.getItem("aibast:workshop-engine") === "copilot"' in quest
    assert re.search(
        r'\?\s*"brainstem"\s*:\s*"copilot"', quest
    )
    assert "GitHub Copilot only" in quest
    assert "GitHub Copilot + Brainstem" in quest
    assert len(re.findall(r"<[^>]+\bdata-report-location=", quest)) == (
        8 + len(cases) + len(manual_frames)  # 1 workshop-setup + 3+3 lane steps + 1 easy verdict
    )
    assert "aibast-workshop-feedback/1.0" in quest
    assert "Watch assisted film" not in quest
    assert "data-workshop-engine-choice" not in quest
    assert 'href="FIELD-GUIDE.md"' not in quest
    assert "VISUAL-EVIDENCE-AUDIT.md" not in quest
    assert "Draft" in quest
    assert re.search(r"published.{0,80}false", quest, re.IGNORECASE | re.DOTALL)
