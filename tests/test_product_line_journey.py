import html
import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "solutions" / "product-line-optimization"
CASE_FILE = ROOT / "tests" / "demo_cases" / "product-line-optimization.json"

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

THEME_SCRIPT = """(() => {
      const param = new URLSearchParams(window.location.search).get("scoutTheme");
      const theme =
        param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      document.documentElement.setAttribute("data-theme", theme);
    })();"""

THEME_VARIABLES = """--cp-bg: #f7f4ef;
      --cp-bg-elevated: #fcfbf8;
      --cp-surface: #ffffff;
      --cp-surface-soft: #f5f5f5;
      --cp-border: #dedede;
      --cp-border-strong: #919191;
      --cp-text: #242424;
      --cp-text-muted: #5c5c5c;
      --cp-text-soft: #6f6f6f;
      --cp-accent: #b11f4b;
      --cp-accent-hover: #9a1a41;
      --cp-accent-soft: rgba(177, 31, 75, 0.08);
      --cp-accent-fg: #ffffff;
      --cp-success: #16a34a;
      --cp-danger: #dc2626;
      --cp-warning: #f59e0b;
      --cp-link: #0078d4;
      --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.12);
      --cp-overlay: rgba(255, 255, 255, 0.8);
      --cp-panel: rgba(255, 255, 255, 0.86);
      --cp-panel-strong: rgba(255, 255, 255, 0.96);
      --cp-sheen: rgba(255, 255, 255, 0.55);
      --cp-highlight: rgba(177, 31, 75, 0.12);"""


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


def test_manifest_exposes_required_ready_course_resource_contract():
    manifest = read_json(PACKAGE / "export-manifest.json")
    resources = {item["id"]: item for item in manifest["files"]}
    assert REQUIRED_RESOURCE_IDS <= resources.keys()
    assert any(resource_id.startswith("knowledge-") for resource_id in resources)
    assert any(resource_id.startswith("skill-") for resource_id in resources)
    assert manifest["bundle"]["path"] == (
        "solutions/product-line-optimization/exports/"
        "product-line-optimization-source.zip"
    )
    for item in resources.values():
        assert item["raw_url"].startswith(manifest["raw_base"])
        assert item["raw_url"].endswith(item["path"])
        assert item["status"] == "ready"
        assert (ROOT / item["path"]).is_file()

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


def test_current_bundle_contains_all_ready_resources():
    manifest = read_json(PACKAGE / "export-manifest.json")
    bundle = ROOT / manifest["bundle"]["path"]
    assert bundle.exists()
    with zipfile.ZipFile(bundle) as archive:
        names = set(archive.namelist())
    for item in manifest["files"]:
        if item["status"] == "ready":
            assert item["path"] in names
    assert not any("/." in name or "__pycache__" in name for name in names)
    assert {
        "solutions/product-line-optimization/quest.html",
        "solutions/product-line-optimization/manual-tutorial.html",
        "solutions/product-line-optimization/field-guide.html",
        "solutions/product-line-optimization/evidence-report.html",
        "solutions/product-line-optimization/evals/visual-checkpoints.json",
        "solutions/product-line-optimization/export-manifest.json",
        "skills/aibast-easy-mode-brainstem/SKILL.md",
        "skills/aibast-easy-mode-copilot/SKILL.md",
    } <= names


def test_manual_tutorial_uses_exact_theme_and_matches_browserfilm_actions():
    tutorial = (PACKAGE / "manual-tutorial.html").read_text(encoding="utf-8")
    steps = tutorial_steps(tutorial)
    browserfilm = read_json(PACKAGE / "screenshots" / "manual" / "browserfilm.json")
    visual = read_json(PACKAGE / "evals" / "visual-checkpoints.json")

    assert THEME_SCRIPT in tutorial
    assert THEME_VARIABLES in tutorial
    assert "AIBAST" in tutorial
    assert "Clawpilot" not in tutorial
    assert "Beta workshop" in tutorial
    assert "Watch assisted film" not in tutorial
    for token in (
        'get("embedded")',
        '=== "1"',
        "data-embedded",
        "aibast-hard-mode-height",
        "postMessage",
        "ResizeObserver",
    ):
        assert token in tutorial

    assert browserfilm["schema"] == "rapp-browserfilm/1.0"
    assert browserfilm["capture_status"] == "captured"
    frames = browserfilm["frames"]
    assert len(steps) == len(frames)
    assert "No PAC CLI, YAML import, or plugin architect" in tutorial
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
        assert (PACKAGE / "screenshots" / "manual" / frame["file"]).is_file()

        checkpoint = hard_visuals[index]
        assert checkpoint["source"].endswith(frame["file"])
        if checkpoint["status"] == "reshoot_required":
            assert not step["images"]
            assert "What to look for" in step["text"]
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


def test_quest_exposes_beta_course_shell_and_global_easy_lanes():
    quest = (PACKAGE / "quest.html").read_text(encoding="utf-8")
    compact_quest = re.sub(r"\s+", " ", quest)
    cases = read_json(CASE_FILE)["cases"]

    assert re.sub(r"\s+", " ", THEME_SCRIPT) in compact_quest
    assert re.sub(r"\s+", " ", THEME_VARIABLES) in compact_quest
    assert "AIBAST guided workshop" in quest
    assert "Clawpilot" not in quest
    assert "Beta workshop" in quest
    assert "workshop-settings.html" in quest
    assert "field-guide.html" in quest
    assert "evidence-report.html" in quest
    assert 'src="manual-tutorial.html?embedded=1"' in quest
    assert 'data-easy-lane="copilot"' in quest
    assert 'data-easy-lane="brainstem"' in quest
    assert 'localStorage.getItem("aibast:workshop-engine") === "brainstem"' in quest
    assert re.search(r'\?\s*"brainstem"\s*:\s*"copilot"', quest)
    assert "GitHub Copilot only" in quest
    assert "GitHub Copilot + Brainstem" in quest
    assert len(re.findall(r"<[^>]+\bdata-report-location=", quest)) == (
        7 + len(cases)
    )
    assert "aibast-workshop-feedback/1.0" in quest
    assert "Watch assisted film" not in quest
    assert "data-workshop-engine-choice" not in quest
    assert 'href="FIELD-GUIDE.md"' not in quest
    assert "VISUAL-EVIDENCE-AUDIT.md" not in quest
    assert "Draft" in quest
    assert re.search(r"published.{0,80}false", quest, re.IGNORECASE | re.DOTALL)
    assert "customer KPI" in quest


def test_guides_state_proof_boundaries_and_production_seams():
    readme = (PACKAGE / "README.md").read_text(encoding="utf-8")
    guide = (PACKAGE / "FIELD-GUIDE.md").read_text(encoding="utf-8")
    for identifier in [
        "aibast_ProductLineOptimizationPilot",
        "643beb44-c693-44b6-b58d-7631cd1f190c",
        "ee67a404-325c-e726-a18a-886fe708ca0b",
        "Sonnet46",
    ]:
        assert identifier in readme
    for required in [
        "Production replacement seams",
        "Failure recovery",
        "Evidence gates",
        "customer KPIs",
        "Draft",
        "one action to each frame",
        "model parity",
        "published: false",
    ]:
        assert required in guide


def test_deployment_recipe_records_validated_draft_identity():
    recipe = read_json(PACKAGE / "deployment.json")
    pilot = recipe["copilot_studio"]["validated_pilot"]
    assert pilot == {
        "display_name": "Product Line Optimization Pilot",
        "schema_name": "aibast_ProductLineOptimizationPilot",
        "bot_id": "643beb44-c693-44b6-b58d-7631cd1f190c",
        "environment_name": "kodyv8",
        "environment_id": "ee67a404-325c-e726-a18a-886fe708ca0b",
        "model": "Sonnet46",
        "skills": 4,
        "knowledge_files": 2,
        "changes_pushed": 7,
        "status": "Draft",
        "published": False,
        "preview_cases_passed": 4,
        "preview_cases_total": 4,
    }
