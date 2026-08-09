import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "solutions" / "inventory-rebalancing"

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


def extract_content_block(path):
    text = path.read_text(encoding="utf-8")
    block = text.split("content: |\n", 1)[1]
    return "\n".join(
        line[2:] if line.startswith("  ") else line
        for line in block.splitlines()
    ) + "\n"


def test_manifest_exposes_complete_ready_resource_contract():
    manifest = read_json(PACKAGE / "export-manifest.json")
    resources = {item["id"]: item for item in manifest["files"]}
    assert set(resources) == {
        "portable-agent",
        "deployment-recipe",
        "field-guide",
        "settings",
        "global-instructions",
        "agent-sync",
        "knowledge-records",
        "knowledge-rules",
        "skill-inventory-snapshot",
        "skill-rebalance",
        "skill-transfer",
        "skill-cost",
        "onepager-map",
        "brainstem-transcripts",
        "studio-preview-evidence",
        "assisted-browserfilm-manifest",
        "assisted-browserfilm",
        "assisted-contact-sheet",
        "manual-evidence",
        "quest",
        "manual-tutorial",
        "manual-browserfilm-manifest",
        "manual-browserfilm",
        "manual-contact-sheet",
    }
    assert manifest["bundle"]["path"] == (
        "solutions/inventory-rebalancing/exports/"
        "inventory-rebalancing-source.zip"
    )
    for item in resources.values():
        assert item["status"] == "ready"
        assert item["raw_url"].endswith(item["path"])
        assert (ROOT / item["path"]).exists()


def test_current_bundle_contains_all_ready_resources():
    manifest = read_json(PACKAGE / "export-manifest.json")
    bundle = ROOT / manifest["bundle"]["path"]
    assert bundle.exists()
    with zipfile.ZipFile(bundle) as archive:
        names = set(archive.namelist())
    for item in manifest["files"]:
        assert item["path"] in names
    assert not any("/." in name or "__pycache__" in name for name in names)


def test_manual_tutorial_uses_exact_theme_and_all_real_frames():
    tutorial = (PACKAGE / "manual-tutorial.html").read_text(encoding="utf-8")
    browserfilm = read_json(PACKAGE / "screenshots" / "manual" / "browserfilm.json")
    assert THEME_SCRIPT in tutorial
    assert THEME_VARIABLES in tutorial
    assert browserfilm["capture_status"] == "captured"
    assert len(browserfilm["frames"]) == 22
    assert "No PAC CLI, YAML import, or plugin architect" in tutorial
    assert "all 22 browser actions and four Preview gates were captured" in tutorial
    assert "0 of 22 complete" in tutorial
    assert "<strong>Action</strong>" in tutorial
    assert "<strong>Expected result</strong>" in tutorial
    assert "Download:" in tutorial
    for frame in browserfilm["frames"]:
        assert tutorial.count(frame["file"]) == 1
        assert frame["duration_ms"] > 0
        assert (PACKAGE / "screenshots" / "manual" / frame["file"]).exists()


def test_manual_tutorial_covers_parity_fixes_cases_and_draft_gate():
    tutorial = (PACKAGE / "manual-tutorial.html").read_text(encoding="utf-8")
    for required in [
        "Remove web search",
        "Upload synthetic inventory records",
        "Upload review rules",
        "Verify two complete knowledge files",
        "Add inventory snapshot",
        "Add rebalance recommendation",
        "Add transfer planning",
        "Add cost analysis",
        "Select Claude Sonnet 4.6",
        "Audit the complete inventory",
        "Run IR-01",
        "Run IR-02",
        "Run IR-03",
        "Run IR-04",
        "Record the Draft gate",
        "Dallas Fulfillment Center",
        "SKU-4406",
        "SKU-4402",
        "SLOW-MOVING",
        "SKU-4401",
        "no inventory has been reserved",
        "total annual holding cost",
        "synthetic planning estimates",
        "knowledge-parity state",
    ]:
        assert required in tutorial
    assert re.search(r"Do not choose Publish", tutorial)


def test_quest_distinguishes_easy_from_literal_browser_hard_mode():
    quest = (PACKAGE / "quest.html").read_text(encoding="utf-8")
    compact_quest = re.sub(r"\s+", " ", quest)
    assert re.sub(r"\s+", " ", THEME_SCRIPT) in compact_quest
    assert re.sub(r"\s+", " ", THEME_VARIABLES) in compact_quest
    assert "Copilot-assisted Easy mode" in quest
    assert "literal browser construction" in quest
    assert "Do not use PAC CLI or YAML import in Hard mode" in quest
    assert 'page:"manual-tutorial.html"' in quest
    assert "screenshots/manual/manual-build-walkthrough.gif" in quest
    assert "Draft and is not published" in quest
    assert "customer KPI" in quest
    assert "@aibast-agents-library/inventory-rebalancing" in quest
    assert "production-line-optimization" not in quest


def test_manual_and_assisted_evidence_is_real_and_consistent():
    manual = read_json(PACKAGE / "evals" / "manual-build-evidence.json")
    assisted = read_json(PACKAGE / "screenshots" / "assisted" / "browserfilm.json")
    assert manual["manual_agent"]["bot_id"] == "05b62fa7-0327-4626-b9db-8c9de02de91a"
    assert manual["manual_components"]["knowledge_files"]["parity_fix_confirmed"]
    assert manual["source_parity"] == {
        "knowledge_files_byte_identical_to_easy_source": True,
        "skill_files_exact_easy_content_blocks": True,
        "skill_frontmatter_included": True,
    }
    assert [case["case_id"] for case in manual["canonical_preview"]] == [
        "IR-01",
        "IR-02",
        "IR-03",
        "IR-04",
    ]
    assert all(case["passed"] for case in manual["canonical_preview"])
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
        "Easy mode — Copilot-assisted",
        "Hard mode — literal browser construction",
        "Production replacement seams",
        "Failure recovery",
        "Evidence gates",
        "not a customer KPI",
        "Draft",
        "knowledge parity",
        "cost analysis",
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
