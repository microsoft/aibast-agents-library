import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "solutions" / "product-line-optimization"

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


def test_manifest_exposes_complete_ready_and_pending_resource_contract():
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
        "skill-line-health",
        "skill-bottleneck",
        "skill-throughput",
        "skill-shift-plan",
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
        "solutions/product-line-optimization/exports/"
        "product-line-optimization-source.zip"
    )
    for item in resources.values():
        assert item["raw_url"].endswith(item["path"])
        assert item["status"] == "ready"
        assert (ROOT / item["path"]).exists()


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


def test_manual_tutorial_uses_exact_theme_and_planned_capture_sequence():
    tutorial = (PACKAGE / "manual-tutorial.html").read_text(encoding="utf-8")
    browserfilm = read_json(PACKAGE / "screenshots" / "manual" / "browserfilm.json")
    assert THEME_SCRIPT in tutorial
    assert THEME_VARIABLES in tutorial
    assert browserfilm["capture_status"] == "captured"
    assert len(browserfilm["frames"]) == 23
    assert "No PAC CLI, YAML import, or plugin architect" in tutorial
    assert "all 23 browser actions and four Preview gates were captured" in tutorial
    assert "0 of 23 complete" in tutorial
    for frame in browserfilm["frames"]:
        assert tutorial.count(frame["file"]) == 1
        assert frame["duration_ms"] > 0


def test_manual_tutorial_covers_inventory_cases_and_draft_gate():
    tutorial = (PACKAGE / "manual-tutorial.html").read_text(encoding="utf-8")
    for required in [
        "Remove web search",
        "Upload synthetic production records",
        "Upload optimization rules",
        "Add plant-wide line health",
        "Add bottleneck identification",
        "Add improvement options",
        "Add shift planning",
        "Select Claude Sonnet 4.6",
        "Audit the complete inventory",
        "Run PLO-01",
        "Run PLO-02",
        "Run PLO-03",
        "Run PLO-04",
        "Record the Draft gate",
        "Polymer Molding Line C",
        "Electronics Assembly Line A",
        "Functional Test",
        "Robotic Welding",
        "Injection Molding",
        "Option 1",
        "Option 2",
        "Quality improvement",
        "Day, Swing, and Night",
    ]:
        assert required in tutorial
    assert re.search(r"Do not choose Publish", tutorial)


def test_quest_distinguishes_copilot_easy_from_literal_browser_hard_mode():
    quest = (PACKAGE / "quest.html").read_text(encoding="utf-8")
    assert "Copilot-assisted Easy mode" in quest
    assert "literal browser construction" in quest
    assert "Do not use PAC CLI or YAML import in Hard mode" in quest
    assert 'page:"manual-tutorial.html"' in quest
    assert "screenshots/manual/manual-build-walkthrough.gif" in quest
    assert "Draft and is not published" in quest
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
        "Easy mode — Copilot-assisted",
        "Hard mode — literal browser construction",
        "Production replacement seams",
        "Failure recovery",
        "Evidence gates",
        "not a customer KPI",
        "Draft",
        "ee4836e5-16a4-4d23-8bd6-342155d3a2af",
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
