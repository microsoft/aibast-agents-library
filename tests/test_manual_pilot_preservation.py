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
        # copilot-studio/ is now the native source pulled back from the
        # re-shot agent. Copilot Studio pads blank YAML block lines with
        # indentation, so parity is content parity with trailing whitespace
        # normalized on both sides; any real text drift still fails.
        settings_path = package / "copilot-studio/settings.mcs.yml"
        settings = settings_path.read_text()
        expected = render_settings(
            parse_yaml_scalar(settings, "displayName"),
            parse_yaml_scalar(settings, "schemaName"),
            (package / "manual/GLOBAL-INSTRUCTIONS.md").read_text(),
        )
        assert normalized(settings) == normalized(expected)
        skills = list((package / "manual/skills").glob("*/SKILL.md"))
        assert skills
        for path in skills:
            rendered, fields = render_skill(path)
            native = package / "copilot-studio/behaviors" / f"aibast_{fields['name']}.mcs.yml"
            assert normalized(native.read_text()) == normalized(rendered)


def test_dated_review_stays_history_and_current_acceptance_comes_from_the_live_reshoot():
    for slug in SLUGS:
        package = ROOT / "solutions" / slug
        review = read(package / "evals/manual-pilot-review.json")
        evidence = read(package / "evals/manual-build-evidence.json")
        visual = read(package / "evals/visual-checkpoints.json")
        cases = read(ROOT / "tests/demo_cases" / f"{slug}.json")["cases"]
        # The 2026-09-12 review is a dated, uncertified historical record.
        assert review["reviewed_on"].startswith("2026-09-12")
        assert review["status"] == "blocked"
        assert review["certified"] is False
        # Current acceptance is the live re-shoot, never the old review.
        assert "review_snapshot" not in evidence
        assert manual_evidence_passed(evidence)
        assert [case["case_id"] for case in evidence["canonical_preview"]] == [case["id"] for case in cases]
        assert [case["prompt"] for case in evidence["canonical_preview"]] == [case["prompt"] for case in cases]
        assert all(case["passed"] is True for case in evidence["canonical_preview"])
        assert evidence["publication_gate"]["published"] is False
        assert visual["summary"]["reshoot_required"] == 0
        assert visual["summary"]["reusable"] == len(visual["captures"])
        assert all(capture["status"] == "reusable" for capture in visual["captures"])
        tutorial = (package / "manual-tutorial.html").read_text()
        assert re.search(r"<img\b", tutorial)
        assert "Preservation review, not certification" not in tutorial
        assert "manual-pilot-review.json" not in tutorial


def test_manual_bundles_are_complete_public_safe_sources_with_unpublished_native_imports():
    forbidden = re.compile(
        r"/Users/|[A-Z]:\\\\Users\\\\|login\.microsoftonline\.com|github_pat_|gh[opsu]_[A-Za-z0-9]{20,}",
        re.IGNORECASE,
    )
    for slug in SLUGS:
        package = ROOT / "solutions" / slug
        manifest = read(package / "export-manifest.json")
        assert manifest["raw_base"] == "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/"
        assert "/microsoft/aibast-agents-library/tree/main/" in manifest["github_folder"]
        assert "include_paths" not in manifest["bundle"]
        assert manifest["copilot_studio_solution"]["status"] == "exported"
        native = read(package / "exports" / f"{slug}-solution-export.json")
        assert native["status"] == "exported"
        assert native["published"] is False
        assert native["managed"] is False
        with zipfile.ZipFile(ROOT / manifest["bundle"]["path"]) as archive:
            names = set(archive.namelist())
            assert native["zip"] in names
            for name in names:
                if name.endswith((".md", ".json", ".yml", ".yaml", ".html", ".py", ".txt")):
                    text = archive.read(name).decode("utf-8")
                    assert not forbidden.search(text), name
        with zipfile.ZipFile(ROOT / native["zip"]) as archive:
            names = archive.namelist()
            config_path = next(name for name in names if name.endswith("/configuration.json"))
            config = json.loads(archive.read(config_path))
            assert "instructions" in config["agentSettings"]


def test_manual_upload_links_bind_the_named_files_not_sorted_positions():
    for slug in SLUGS:
        package = ROOT / "solutions" / slug
        tutorial = (package / "manual-tutorial.html").read_text()
        bound = 0
        for number, block in re.findall(
            r'<article class="step" id="step-(\d+)">(.*?)</article>', tutorial, re.DOTALL
        ):
            title = re.search(r"<h3>(.*?)</h3>", block)[1]
            match = re.fullmatch(r"Add (knowledge|skill): (\S+)", title)
            if not match:
                continue
            kind, name = match.groups()
            path = (
                f"manual/knowledge/{name}" if kind == "knowledge"
                else f"manual/skills/{name}/SKILL.md"
            )
            assert (package / path).is_file(), (slug, number, path)
            assert re.findall(r'href="(manual/[^"]+)" download', block) == [path], (slug, number)
            bound += 1
        assert bound == len(list((package / "manual/knowledge").glob("*.md"))) + len(
            list((package / "manual/skills").glob("*/SKILL.md"))
        )
