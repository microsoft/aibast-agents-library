import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CATALOG = json.loads(
    (ROOT / "solutions" / "catalog.json").read_text(encoding="utf-8")
)["solutions"]
ONEPAGERS = json.loads(
    (ROOT / "state" / "onepager_content.json").read_text(encoding="utf-8")
)["onepagers"]

PACKAGES = {
    "@aibast-agents-library/building-permit-processing": {
        "slug": "building-permit-processing",
        "case_file": ROOT / "tests" / "demo_cases" / "building-permit-processing.json",
        "scenario_cases": {
            "permit-backlog": "BPP-01",
            "permit-intake": "BPP-02",
            "permit-routing": "BPP-03",
            "permit-updates": "BPP-04",
            "permit-inspections": "BPP-05",
        },
    },
    "@aibast-agents-library/production-line-optimization": {
        "slug": "product-line-optimization",
        "case_file": ROOT / "tests" / "demo_cases" / "product-line-optimization.json",
        "scenario_cases": {
            "production-line-health": "PLO-01",
            "production-bottleneck": "PLO-02",
            "production-options": "PLO-03",
            "production-shift-plan": "PLO-04",
        },
    },
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_solution_assets_are_packaged_under_solutions():
    assert not (ROOT / "solution_copy.json").exists()
    assert not (ROOT / "onepager_content.json").exists()
    for package in PACKAGES.values():
        folder = ROOT / "solutions" / package["slug"]
        assert (folder / "README.md").exists()
        assert (folder / "deployment.json").exists()
        assert (folder / "evals" / "onepager-map.json").exists()
        assert (folder / "evals" / "transcripts.json").exists()
    assert (ROOT / "solutions" / "_shared" / "m365-copilot-demo.html").exists()
    permit = ROOT / "solutions" / "building-permit-processing"
    assert (permit / "FIELD-GUIDE.md").exists()
    assert (permit / "quest.html").exists()
    assert (permit / "copilot-studio" / "settings.mcs.yml").exists()
    assert not (permit / "copilot-studio" / ".mcs").exists()
    assert len(list((permit / "copilot-studio" / "behaviors").glob("*.mcs.yml"))) == 7
    assert (permit / "evals" / "deployment-evidence.json").exists()


def test_promise_maps_are_pinned_to_the_approved_powerpoints():
    for name, package in PACKAGES.items():
        folder = ROOT / "solutions" / package["slug"]
        promise_map = read_json(folder / "evals" / "onepager-map.json")
        assert promise_map["solution"] == name
        source = ONEPAGERS[promise_map["onepager"]]
        assert promise_map["source_slide_sha256"] == source["source_sha256"]
        assert promise_map["promises"]
        for promise in promise_map["promises"]:
            assert promise["advertised_promise"]
            assert promise["operations"]
            assert promise["demo_cases"]
            assert promise["synthetic_evidence"]


def test_transcripts_cover_every_locked_case_in_strict_isolation():
    for name, package in PACKAGES.items():
        folder = ROOT / "solutions" / package["slug"]
        cases = read_json(package["case_file"])["cases"]
        transcript = read_json(folder / "evals" / "transcripts.json")
        assert transcript["solution"] == name
        assert transcript["strict_isolation"] is True
        assert transcript["loaded_tools_after_capture"] == [
            cases[0]["expects_agent"]
        ]
        captured = {item["case_id"]: item for item in transcript["transcripts"]}
        assert set(captured) == {case["id"] for case in cases}
        for case in cases:
            item = captured[case["id"]]
            assert item["prompt"] == case["prompt"]
            assert item["passed"] is True
            assert item["expected_agent"] == case["expects_agent"]
            for value in case["must_include"]:
                assert value.lower() in item["agent_logs"].lower()


def test_catalog_demo_links_point_to_exact_canonical_prompts():
    for name, package in PACKAGES.items():
        folder = ROOT / "solutions" / package["slug"]
        transcript = read_json(folder / "evals" / "transcripts.json")
        captured = {item["case_id"]: item for item in transcript["transcripts"]}
        prompts = CATALOG[name]["sample_prompts"]
        assert len(prompts) == len(package["scenario_cases"])
        for prompt in prompts:
            match = re.search(r"[?&]scenario=([a-z0-9-]+)", prompt["demo_url"])
            assert match, prompt
            scenario = match.group(1)
            case_id = package["scenario_cases"][scenario]
            assert prompt["prompt"] == captured[case_id]["prompt"]


def test_deployment_recipe_matches_captured_source_and_smoke_case():
    for name, package in PACKAGES.items():
        folder = ROOT / "solutions" / package["slug"]
        recipe = read_json(folder / "deployment.json")
        transcript = read_json(folder / "evals" / "transcripts.json")
        cases = read_json(package["case_file"])["cases"]
        assert recipe["name"] == name
        assert recipe["source_url"].endswith(transcript["agent_sources"][0]["path"])
        smoke_case = next(
            case for case in cases if case["prompt"] == recipe["smoke_test"]["prompt"]
        )
        assert recipe["smoke_test"]["must_call"] == smoke_case["expects_agent"]
        assert recipe["smoke_test"]["must_include"] == smoke_case["must_include"][:2]


def test_published_copilot_studio_corpus_matches_every_permit_case():
    package = PACKAGES["@aibast-agents-library/building-permit-processing"]
    folder = ROOT / "solutions" / package["slug"]
    cases = read_json(package["case_file"])["cases"]
    artifact = read_json(folder / "evals" / "copilot-studio-transcripts.json")
    assert artifact["environment_id"] == "ee67a404-325c-e726-a18a-886fe708ca0b"
    assert artifact["agent_schema_name"] == "aibast_BuildingPermitPilot"
    assert artifact["strict_case_parity"] is True
    captured = {item["case_id"]: item for item in artifact["transcripts"]}
    assert set(captured) == {case["id"] for case in cases}
    for case in cases:
        item = captured[case["id"]]
        assert item["prompt"] == case["prompt"]
        assert item["passed"] is True
        for value in case["must_include"]:
            assert value.lower() in item["assistant_response"].lower()


def test_shared_demo_reads_canonical_transcript_artifacts():
    demo = (
        ROOT / "solutions" / "_shared" / "m365-copilot-demo.html"
    ).read_text(encoding="utf-8")
    assert 'fetch(`../${definition.solution}/evals/transcripts.json`' in demo
    assert "Exact Brainstem transcript" in demo
    for package in PACKAGES.values():
        for scenario in package["scenario_cases"]:
            assert f'"{scenario}": {{' in demo


def test_deployment_evidence_records_runtime_proof_and_remaining_gates():
    evidence = read_json(
        ROOT
        / "solutions"
        / "building-permit-processing"
        / "evals"
        / "deployment-evidence.json"
    )
    assert evidence["fresh_brainstem"]["smoke_test"] == "passed"
    assert evidence["fresh_brainstem"]["user_terminal_required"] is False
    assert evidence["copilot_studio"]["environment_name"] == "kodyv8"
    assert evidence["copilot_studio"]["runtime_cases_passed"] == 5
    assert evidence["copilot_studio"]["runtime_cases_total"] == 5
    assert evidence["browserfilm"]["frames"] == 8
    assert evidence["remaining_evidence"]


def test_rapp_browserfilm_assets_are_reproducible():
    folder = (
        ROOT
        / "solutions"
        / "building-permit-processing"
        / "screenshots"
    )
    manifest = read_json(folder / "browserfilm.json")
    assert manifest["schema"] == "rapp-browserfilm/1.0"
    assert manifest["raw_base_url"].startswith(
        "https://raw.githubusercontent.com/microsoft/aibast-agents-library/"
    )
    assert len(manifest["frames"]) == 8
    for frame in manifest["frames"]:
        assert (folder / frame["file"]).exists()
        assert frame["label"]
        assert frame["duration_ms"] > 0
    gif = folder / "copilot-assisted-walkthrough.gif"
    assert gif.read_bytes()[:6] in (b"GIF87a", b"GIF89a")
    assert gif.stat().st_size > 100_000
    assert (folder / "copilot-assisted-contact-sheet.jpg").stat().st_size > 10_000

    manual = folder / "manual"
    manual_manifest = read_json(manual / "browserfilm.json")
    assert len(manual_manifest["frames"]) == 24
    assert manual_manifest["raw_base_url"].endswith(
        "/solutions/building-permit-processing/screenshots/manual/"
    )
    for frame in manual_manifest["frames"]:
        assert (manual / frame["file"]).exists()
        assert frame["label"]
        assert frame["duration_ms"] > 0
    manual_gif = manual / "manual-build-walkthrough.gif"
    assert manual_gif.read_bytes()[:6] in (b"GIF87a", b"GIF89a")
    assert manual_gif.stat().st_size > 100_000
    assert (manual / "manual-build-contact-sheet.jpg").stat().st_size > 10_000

    quest = (
        ROOT
        / "solutions"
        / "building-permit-processing"
        / "quest.html"
    ).read_text(encoding="utf-8")
    assert "screenshots/copilot-assisted-walkthrough.gif" in quest
    assert "screenshots/manual/manual-build-walkthrough.gif" in quest
    assert "Download every source file" in quest
    assert "Upload the first four skills" in quest
    assert "Install and authenticate every prerequisite" not in quest


def test_manual_build_evidence_records_preview_parity():
    evidence = read_json(
        ROOT
        / "solutions"
        / "building-permit-processing"
        / "evals"
        / "manual-build-evidence.json"
    )
    assert evidence["status"] == "draft"
    assert evidence["manual_components"]["knowledge_files"] == 2
    assert evidence["manual_components"]["skills"] == 7
    assert evidence["canonical_preview"]["passed"] is True
    assert evidence["publication"]["published"] is False


def test_manual_tutorial_covers_every_browserfilm_step():
    package = ROOT / "solutions" / "building-permit-processing"
    tutorial = (package / "manual-tutorial.html").read_text(encoding="utf-8")
    manifest = read_json(package / "screenshots" / "manual" / "browserfilm.json")
    assert "Hard mode · AI skeptic edition" in tutorial
    assert "manual-build-walkthrough.gif" in tutorial
    assert "export-manifest.json" in tutorial
    for frame in manifest["frames"]:
        assert frame["file"] in tutorial


def test_export_manifest_and_bundle_are_complete():
    manifest_path = (
        ROOT
        / "solutions"
        / "building-permit-processing"
        / "export-manifest.json"
    )
    manifest = read_json(manifest_path)
    bundle = ROOT / manifest["bundle"]["path"]
    assert bundle.exists()
    assert manifest["bundle"]["raw_url"].endswith(manifest["bundle"]["path"])

    for item in manifest["files"]:
        path = ROOT / item["path"]
        assert path.exists(), item["path"]
        assert item["raw_url"].endswith(item["path"])

    with zipfile.ZipFile(bundle) as archive:
        names = set(archive.namelist())
    assert not any("/." in name or "__pycache__" in name for name in names)
    for item in manifest["files"]:
        assert item["path"] in names
    assert (
        "solutions/building-permit-processing/"
        "screenshots/manual/manual-build-walkthrough.gif"
    ) in names
