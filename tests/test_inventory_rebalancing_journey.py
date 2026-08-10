import html
import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "solutions" / "inventory-rebalancing"
CASE_FILE = ROOT / "tests" / "demo_cases" / "inventory-rebalancing.json"

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


def extract_content_block(path):
    text = path.read_text(encoding="utf-8")
    block = text.split("content: |\n", 1)[1]
    return "\n".join(
        line[2:] if line.startswith("  ") else line
        for line in block.splitlines()
    ) + "\n"


def test_manifest_exposes_required_ready_course_resource_contract():
    manifest = read_json(PACKAGE / "export-manifest.json")
    resources = {item["id"]: item for item in manifest["files"]}
    assert REQUIRED_RESOURCE_IDS <= resources.keys()
    assert any(resource_id.startswith("knowledge-") for resource_id in resources)
    assert any(resource_id.startswith("skill-") for resource_id in resources)
    assert manifest["bundle"]["path"] == (
        "solutions/inventory-rebalancing/exports/"
        "inventory-rebalancing-source.zip"
    )
    for item in resources.values():
        assert item["status"] == "ready"
        assert item["raw_url"].startswith(manifest["raw_base"])
        assert item["raw_url"].endswith(item["path"])
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
        assert item["path"] in names
    assert not any("/." in name or "__pycache__" in name for name in names)
    assert {
        "solutions/inventory-rebalancing/quest.html",
        "solutions/inventory-rebalancing/manual-tutorial.html",
        "solutions/inventory-rebalancing/field-guide.html",
        "solutions/inventory-rebalancing/evidence-report.html",
        "solutions/inventory-rebalancing/evals/visual-checkpoints.json",
        "solutions/inventory-rebalancing/export-manifest.json",
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
    assert "Report an issue" in tutorial
    assert "Beta workshop" not in tutorial
    assert "Watch assisted film" not in tutorial
    for token in ("data-embedded", "aibast-hard-mode-height", "postMessage"):
        assert token not in tutorial
    assert "manual-progress" in tutorial
    assert 'badgeIds.push("hard-mode-complete")' in tutorial

    assert browserfilm["schema"] == "rapp-browserfilm/1.0"
    assert browserfilm["capture_status"] == "captured"
    frames = browserfilm["frames"]
    assert len(steps) == len(frames)
    assert "No PAC CLI, YAML import, or plugin architect" in tutorial
    assert "<strong>Action</strong>" in tutorial
    assert "<strong>Expected result</strong>" in tutorial
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
            assert "Withheld checkpoint" in step["text"]
            assert "not approved for learner display" in step["text"]
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
    manual_frames = read_json(
        PACKAGE / "screenshots" / "manual" / "browserfilm.json"
    )["frames"]

    assert re.sub(r"\s+", " ", THEME_SCRIPT) in compact_quest
    assert re.sub(r"\s+", " ", THEME_VARIABLES) in compact_quest
    assert "AIBAST guided workshop" in quest
    assert "Clawpilot" not in quest
    assert "Report an issue" in quest
    assert "Beta workshop" not in quest
    assert "workshop-settings.html" in quest
    assert "field-guide.html" in quest
    assert "evidence-report.html" in quest
    assert "<iframe" not in quest
    assert 'class="path" data-path="hard"' in quest
    assert "Open standalone Hard-mode guide" in quest
    assert 'data-easy-lane="copilot"' in quest
    assert 'data-easy-lane="brainstem"' in quest
    assert 'localStorage.getItem("aibast:workshop-engine") === "brainstem"' in quest
    assert re.search(r'\?\s*"brainstem"\s*:\s*"copilot"', quest)
    assert "GitHub Copilot only" in quest
    assert "GitHub Copilot + Brainstem" in quest
    assert len(re.findall(r"<[^>]+\bdata-report-location=", quest)) == (
        7 + len(cases) + len(manual_frames)
    )
    assert "aibast-workshop-feedback/1.0" in quest
    assert "Watch assisted film" not in quest
    assert "data-workshop-engine-choice" not in quest
    assert 'href="FIELD-GUIDE.md"' not in quest
    assert "VISUAL-EVIDENCE-AUDIT.md" not in quest
    assert "Draft" in quest
    assert re.search(r"published.{0,80}false", quest, re.IGNORECASE | re.DOTALL)
    assert "customer KPI" in quest
    assert "@aibast-agents-library/inventory-rebalancing" in quest
    assert "production-line-optimization" not in quest


def test_manual_and_assisted_evidence_is_real_and_consistent():
    manual = read_json(PACKAGE / "evals" / "manual-build-evidence.json")
    assisted = read_json(PACKAGE / "screenshots" / "assisted" / "browserfilm.json")
    cases = read_json(CASE_FILE)["cases"]
    assert manual["manual_agent"]["bot_id"] == "05b62fa7-0327-4626-b9db-8c9de02de91a"
    assert manual["manual_components"]["knowledge_files"]["parity_fix_confirmed"]
    assert manual["source_parity"] == {
        "knowledge_files_byte_identical_to_easy_source": True,
        "skill_files_exact_easy_content_blocks": True,
        "skill_frontmatter_included": True,
    }
    assert [item["case_id"] for item in manual["canonical_preview"]] == [
        case["id"] for case in cases
    ]
    for case, item in zip(cases, manual["canonical_preview"]):
        assert item["must_include"] == case["must_include"]
        assert item["passed"] is True
    assert manual["canonical_preview"][3]["source_capture"] == 142
    assert manual["publication_gate"]["published"] is False
    assert assisted["capture_status"] == "captured"
    assert len(assisted["frames"]) == 6
    for frame in assisted["frames"]:
        assert (PACKAGE / "screenshots" / "assisted" / frame["file"]).exists()


def test_manual_downloads_exactly_match_reviewed_easy_source():
    easy_knowledge = PACKAGE / "copilot-studio" / "capabilities" / "knowledge" / "files"
    manual_knowledge = PACKAGE / "manual" / "knowledge"
    knowledge_pairs = {
        "aibast-inventory-rebalancing-facility-sku-snapshot.md":
            "aibast_inventory-rebalancing-synthetic-records.md",
        "aibast-inventory-rebalancing-cost-and-review-rules.md":
            "aibast_inventory-rebalancing-review-rules.md",
    }
    for source, manual in knowledge_pairs.items():
        assert (easy_knowledge / source).read_bytes() == (
            manual_knowledge / manual
        ).read_bytes()

    behaviors = PACKAGE / "copilot-studio" / "behaviors"
    skills = PACKAGE / "manual" / "skills"
    skill_pairs = {
        "aibast-inventory-snapshot_pv7k2q.mcs.yml":
            "aibast_inventory_snapshot/SKILL.md",
        "aibast-rebalance-recommendation_pv7k2q.mcs.yml":
            "aibast_rebalance_recommendation/SKILL.md",
        "aibast-transfer-plan_pv7k2q.mcs.yml":
            "aibast_transfer_plan/SKILL.md",
        "aibast-cost-analysis_pv7k2q.mcs.yml":
            "aibast_cost_analysis/SKILL.md",
    }
    for source, manual in skill_pairs.items():
        content = extract_content_block(behaviors / source)
        assert content.startswith("---\n")
        assert "\n---\n" in content[4:]
        assert (skills / manual).read_text(encoding="utf-8") == content


def test_guides_state_identity_proof_boundaries_and_production_seams():
    readme = (PACKAGE / "README.md").read_text(encoding="utf-8")
    guide = (PACKAGE / "FIELD-GUIDE.md").read_text(encoding="utf-8")
    for identifier in [
        "aibast_InventoryRebalancingPilot",
        "236a0c04-ea66-46e8-b461-1e2b68291c92",
        "05b62fa7-0327-4626-b9db-8c9de02de91a",
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


def test_deployment_recipe_records_both_validated_draft_identities():
    recipe = read_json(PACKAGE / "deployment.json")
    studio = recipe["copilot_studio"]
    assert studio["validated_pilot"] == {
        "display_name": "Inventory Rebalancing Pilot",
        "schema_name": "aibast_InventoryRebalancingPilot",
        "bot_id": "236a0c04-ea66-46e8-b461-1e2b68291c92",
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
    assert studio["validated_manual"] == {
        "display_name": "Inventory Manual Build",
        "bot_id": "05b62fa7-0327-4626-b9db-8c9de02de91a",
        "environment_name": "kodyv8",
        "environment_id": "ee67a404-325c-e726-a18a-886fe708ca0b",
        "model": "Sonnet46",
        "skills": 4,
        "knowledge_files": 2,
        "web_search_removed": True,
        "status": "Draft",
        "published": False,
        "preview_cases_passed": 4,
        "preview_cases_total": 4,
    }
