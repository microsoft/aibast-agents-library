import html
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

REQUIRED_COURSE_RESOURCE_IDS = {
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
    assert manual_manifest["schema"] == "rapp-browserfilm/1.0"
    assert manual_manifest["frames"]
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
    cases = read_json(
        ROOT / "tests" / "demo_cases" / "building-permit-processing.json"
    )["cases"]
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
    assert re.search(r'\?\s*"brainstem"\s*:\s*"copilot"', quest)
    assert "GitHub Copilot only" in quest
    assert "GitHub Copilot + Brainstem" in quest
    assert len(re.findall(r"<[^>]+\bdata-report-location=", quest)) == (
        8 + len(cases) + len(manual_manifest["frames"])
    )
    assert "aibast-workshop-feedback/1.0" in quest
    assert "Watch assisted film" not in quest
    assert "screenshots/copilot-assisted-walkthrough.gif" not in quest
    assert "data-workshop-engine-choice" not in quest
    assert 'href="FIELD-GUIDE.md"' not in quest
    assert "VISUAL-EVIDENCE-AUDIT.md" not in quest
    assert "Draft" in quest
    assert re.search(r"published.{0,80}false", quest, re.IGNORECASE | re.DOTALL)


def test_manual_build_evidence_records_preview_parity():
    package = ROOT / "solutions" / "building-permit-processing"
    evidence = read_json(
        package / "evals" / "manual-build-evidence.json"
    )
    cases = read_json(
        ROOT / "tests" / "demo_cases" / "building-permit-processing.json"
    )["cases"]
    assert evidence["status"] == "draft"
    assert evidence["manual_components"]["knowledge_files"] == 2
    assert evidence["manual_components"]["skills"] == 7
    assert evidence["canonical_preview"]["prompt"] == cases[0]["prompt"]
    assert evidence["canonical_preview"]["must_include"] == cases[0]["must_include"]
    assert evidence["canonical_preview"]["passed"] is True
    assert evidence["publication"]["published"] is False
    report = (package / "evidence-report.html").read_text(encoding="utf-8").lower()
    for case in cases:
        assert case["id"].lower() in report
        for marker in case["must_include"]:
            assert marker.lower() in report


def test_manual_tutorial_matches_browserfilm_and_visual_contract():
    package = ROOT / "solutions" / "building-permit-processing"
    tutorial = (package / "manual-tutorial.html").read_text(encoding="utf-8")
    steps = tutorial_steps(tutorial)
    browserfilm = read_json(package / "screenshots" / "manual" / "browserfilm.json")
    visual = read_json(package / "evals" / "visual-checkpoints.json")

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
        assert (package / step["downloads"][0]).is_file()
        assert len(step["report_evidence"]) == 1
        assert step["report_evidence"][0].endswith(frame["file"])
        assert frame["duration_ms"] > 0
        assert (package / "screenshots" / "manual" / frame["file"]).is_file()

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


def test_export_manifest_and_bundle_are_complete():
    manifest_path = (
        ROOT
        / "solutions"
        / "building-permit-processing"
        / "export-manifest.json"
    )
    manifest = read_json(manifest_path)
    resources = {item["id"]: item for item in manifest["files"]}
    assert REQUIRED_COURSE_RESOURCE_IDS <= resources.keys()
    assert any(resource_id.startswith("knowledge-") for resource_id in resources)
    assert any(resource_id.startswith("skill-") for resource_id in resources)
    bundle = ROOT / manifest["bundle"]["path"]
    assert bundle.exists()
    assert manifest["bundle"]["raw_url"].startswith(manifest["raw_base"])
    assert manifest["bundle"]["raw_url"].endswith(manifest["bundle"]["path"])

    for item in manifest["files"]:
        path = ROOT / item["path"]
        assert item["status"] == "ready"
        assert path.is_file(), item["path"]
        assert item["raw_url"].startswith(manifest["raw_base"])
        assert item["raw_url"].endswith(item["path"])

    package = ROOT / "solutions" / "building-permit-processing"
    for filename, brand in (
        ("field-guide.html", "AIBAST field guide"),
        ("evidence-report.html", "AIBAST evidence report"),
    ):
        page = (package / filename).read_text(encoding="utf-8")
        assert "<style>" in page
        assert brand in page
        assert "Clawpilot" not in page

    visual = read_json(package / "evals" / "visual-checkpoints.json")
    assert visual["schema"] == "aibast-visual-checkpoints/1.0"
    assert visual["summary"]["total_existing_captures"] == len(visual["captures"])
    assert visual["summary"]["reusable"] == sum(
        capture["status"] == "reusable" for capture in visual["captures"]
    )
    assert visual["summary"]["reshoot_required"] == sum(
        capture["status"] == "reshoot_required"
        for capture in visual["captures"]
    )

    with zipfile.ZipFile(bundle) as archive:
        names = set(archive.namelist())
    assert not any("/." in name or "__pycache__" in name for name in names)
    for item in manifest["files"]:
        assert item["path"] in names
    assert (
        "solutions/building-permit-processing/"
        "screenshots/manual/manual-build-walkthrough.gif"
    ) in names
    assert {
        "solutions/building-permit-processing/quest.html",
        "solutions/building-permit-processing/manual-tutorial.html",
        "solutions/building-permit-processing/field-guide.html",
        "solutions/building-permit-processing/evidence-report.html",
        "solutions/building-permit-processing/evals/visual-checkpoints.json",
        "solutions/building-permit-processing/export-manifest.json",
        "skills/aibast-easy-mode-brainstem/SKILL.md",
        "skills/aibast-easy-mode-copilot/SKILL.md",
    } <= names
