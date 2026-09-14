import hashlib
import html
import importlib.util
import json
import re
import textwrap
import zipfile
from pathlib import Path

import pytest

from tools import build_solution_export, normalize_manual_instructions
from tools import scaffold_solution_journey as scaffold
from tools.run_demo_cases import run_case


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "solutions" / "care-gap-closure"
CASE_FILE = ROOT / "tests" / "demo_cases" / "care-gap-closure.json"
EXPECTED = ["SYN-COL — 182 records", "Records requiring evidence review"]
REPAIRED_CAPTURES = {
    "easy-cg-01",
    "hard-step-03",
    "hard-step-04",
    "hard-cg-01",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def cg01(rows):
    return next(row for row in rows if row.get("case_id", row.get("id")) == "CG-01")


def context():
    return scaffold.load_context(
        ROOT, "care-gap-closure", allow_pending=True, raw_base=scaffold.DEFAULT_RAW_BASE
    )


@pytest.fixture(scope="module")
def agent_module():
    source = ROOT / read_json(PACKAGE / "deployment.json")["source_path"]
    spec = importlib.util.spec_from_file_location("care_gap_contract", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cg01_compares_all_measures_using_source_arithmetic(agent_module):
    queues = {
        key: row["source_population"] - row["source_closed"]
        for key, row in agent_module.MEASURES.items()
    }
    assert queues == {"SYN-BCS": 108, "SYN-COL": 182, "SYN-CDC": 53}
    assert max(queues, key=queues.get) == "SYN-COL"
    output = agent_module.CareGapClosureAgent().perform(operation="gap_analysis")
    assert f"**Largest evidence-review queue:** {EXPECTED[0]}." in output
    for key, count in queues.items():
        section = output.split(f"({key})", 1)[1].split("## ", 1)[0]
        assert f"Records requiring evidence review: {count}" in section

    records = (
        PACKAGE / "manual/knowledge/aibast_care-gap-closure-synthetic-records.md"
    ).read_text()
    for line in records.splitlines():
        if not line.startswith("| SYN-"):
            continue
        key, _, population, closed, count, rate, date, limitation = [
            cell.strip() for cell in line.strip("|").split("|")
        ]
        source = agent_module.MEASURES[key]
        assert int(population) == source["source_population"]
        assert int(closed) == source["source_closed"]
        assert int(count) == queues[key]
        assert rate == f"{round(int(closed) / int(population) * 100, 1)}%"
        assert date == source["evidence_as_of"]
        assert limitation == source["limitations"]


def test_cg01_rejects_a_wrong_leader_even_when_all_measure_rows_are_present(agent_module):
    case = cg01(read_json(CASE_FILE)["cases"])
    assert case["must_include"] == EXPECTED
    output = agent_module.CareGapClosureAgent().perform(operation=case["operation"])
    answer = " ".join(["Synthetic evidence requires qualified human review."] * 6)
    logs = f"[CareGapClosureAgent] {output}"
    assert run_case(case, answer, logs) == (True, [])
    wrong_leader = logs.replace(EXPECTED[0], "SYN-BCS — 108 records")
    passed, failures = run_case(case, answer, wrong_leader)
    assert not passed
    assert any(EXPECTED[0] in failure for failure in failures)


@pytest.mark.parametrize(
    ("filename", "key"),
    [
        ("transcripts.json", "transcripts"),
        ("manual-build-evidence.json", "canonical_preview"),
        ("copilot-studio-preview-evidence.json", "cases"),
    ],
)
def test_evaluation_contracts_match_the_locked_case(filename, key):
    assert cg01(read_json(PACKAGE / "evals" / filename)[key])["must_include"] == EXPECTED
    smoke = read_json(PACKAGE / "deployment.json")["smoke_test"]
    assert smoke["arguments"] == {"operation": "gap_analysis"}
    assert smoke["must_include"] == EXPECTED


def test_manual_and_native_sources_share_the_same_contract():
    manual = PACKAGE / "manual"
    native = PACKAGE / "copilot-studio"
    instructions = (manual / "GLOBAL-INSTRUCTIONS.md").read_text()
    assert normalize_manual_instructions.render_section(
        read_json(CASE_FILE)["cases"]
    ) in instructions
    settings = (native / "settings.mcs.yml").read_text()
    native_instructions = settings.split("          value: |\n", 1)[1].split(
        "template:", 1
    )[0]
    assert textwrap.dedent(native_instructions) == instructions
    for source in (manual / "knowledge").glob("*.md"):
        assert source.read_bytes() == (
            native / "capabilities/knowledge/files" / source.name
        ).read_bytes()
    for source in (manual / "skills").glob("*/SKILL.md"):
        mirror = native / "behaviors" / f"aibast_care-gap-closure-{source.parent.name}.mcs.yml"
        assert textwrap.dedent(mirror.read_text().split("content: |\n", 1)[1]) == source.read_text()
    for source in [
        manual / "GLOBAL-INSTRUCTIONS.md",
        manual / "skills/gap-analysis/SKILL.md",
        *sorted((manual / "knowledge").glob("*.md")),
    ]:
        assert EXPECTED[0] in source.read_text()


def test_outreach_and_dashboard_keep_their_breast_screening_evidence(agent_module):
    cases = read_json(CASE_FILE)["cases"]
    assert cases[3]["must_include"] == ["SYN-BCS", "source-recorded closed"]
    agent = agent_module.CareGapClosureAgent()
    outreach = agent.perform(operation="outreach_draft", measure_id="SYN-BCS")
    assert "(SYN-BCS)" in outreach
    assert "No message is sent" in outreach
    assert "Do not state" in outreach
    dashboard = agent.perform(operation="quality_dashboard")
    for rate in ("73.0%", "65.0%", "82.9%"):
        assert rate in dashboard


def test_transcript_revalidation_is_offline_and_preserves_recorded_output():
    capture = read_json(PACKAGE / "evals/transcripts.json")
    immutable = {
        "captured_at": capture["captured_at"],
        "transcripts": [
            {
                key: row[key]
                for key in (
                    "case_id", "prompt", "assistant_response", "agent_logs",
                    "model", "requested_model",
                )
            }
            for row in capture["transcripts"]
        ],
    }
    assert hashlib.sha256(json.dumps(immutable, sort_keys=True).encode()).hexdigest() == (
        "9cc14154c4488aea953f6ad09d40d9241d3d2a3b15d19c6c3818179ccf11a58f"
    )
    assert capture["captured_case_file_sha256"] == (
        "1bdadb805383e84752aeef511969d709f10d2e794b512f58772a62c94919d75c"
    )
    assert capture["case_file_sha256"] == hashlib.sha256(CASE_FILE.read_bytes()).hexdigest()
    assert capture["contract_revalidation"]["live_capture"] is False
    assert capture["contract_revalidation"]["validator"] == "tools.run_demo_cases.run_case"
    for case, transcript in zip(read_json(CASE_FILE)["cases"], capture["transcripts"]):
        assert case["id"] == transcript["case_id"]
        assert transcript["must_include"] == case["must_include"]
        assert run_case(case, transcript["assistant_response"], transcript["agent_logs"]) == (True, [])


def test_live_source_revision_is_not_claimed_as_verified():
    manual = read_json(PACKAGE / "evals/manual-build-evidence.json")
    preview = read_json(PACKAGE / "evals/copilot-studio-preview-evidence.json")
    assert manual["status"] == "reshoot_required"
    assert manual["manual_components"]["global_instructions"]["confirmed"] is False
    assert preview["source_contract_status"] == "reshoot_required"
    assert cg01(scaffold.easy_case_records(context()))["passed"] is False
    for cases in (manual["canonical_preview"], preview["cases"]):
        case = cg01(cases)
        assert case["passed"] is None
        assert case["status"] == "reshoot_required"
        assert case["captured_passed"] is True
        assert case["captured_must_include"] == [
            "SYN-BCS", "Records requiring evidence review"
        ]
    studio = read_json(PACKAGE / "deployment.json")["copilot_studio"]
    for key in ("validated_manual", "validated_pilot"):
        assert studio[key]["source_contract_status"] == "reshoot_required"
        assert studio[key]["preview_cases_passed"] == 3
        assert studio[key]["preview_cases_pending"] == 1
        assert studio[key]["published"] is False
    manual["manual_components"]["global_instructions"]["confirmed"] = True
    for case in manual["canonical_preview"]:
        case["passed"] = True
    assert scaffold.manual_evidence_passed(manual) is False
    with pytest.raises(scaffold.ScaffoldError, match="does not record passed manual Preview"):
        scaffold.load_context(
            ROOT, "care-gap-closure", allow_pending=False,
            raw_base=scaffold.DEFAULT_RAW_BASE,
        )


def test_affected_checkpoints_keep_historical_anchors_without_relabeling():
    visual = read_json(PACKAGE / "evals/visual-checkpoints.json")
    captures = {capture["id"]: capture for capture in visual["captures"]}
    assert visual["summary"] == {
        "total_existing_captures": 23, "reusable": 18, "reshoot_required": 5
    }
    assert {
        key for key, capture in captures.items()
        if capture["status"] == "reshoot_required"
    } == REPAIRED_CAPTURES | {"easy-cg-04"}
    for key in REPAIRED_CAPTURES:
        capture = captures[key]
        assert (ROOT / capture["historical_annotation"]).is_file()
        assert capture["historical_visible_anchors"]
        assert capture["historical_boxes"]
        assert "annotated" not in capture
        assert "visible_anchors" not in capture
        assert EXPECTED[0] in capture["reason"]
    assert captures["easy-cg-01"]["historical_visible_anchors"][0] == "SYN-BCS"
    assert captures["hard-cg-01"]["historical_visible_anchors"][0] == "SYN-BCS"
    assert "CG-01 / gap_analysis: SYN-BCS" in (
        captures["hard-step-03"]["historical_visible_anchors"][1]
    )
    assert "release_review" not in visual
    assert visual["historical_release_review"]["status"] == "approved"


def test_historical_screenshots_and_films_are_byte_identical():
    paths = sorted(
        path for path in (PACKAGE / "screenshots").rglob("*")
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif"}
    )
    paths += sorted((ROOT / "browser-audit/screenshots").glob("care-gap-closure-*.png"))
    manifest = {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
    }
    assert len(manifest) == 51
    assert hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest() == (
        "379ca2a604590526a49646825fcf684d6ee5f91c88e60cc730d4de1b748625a3"
    )


def test_generated_pages_do_not_promote_stale_images_or_captured_contracts():
    ctx = context()
    _, outputs = scaffold.generated_outputs(ctx)
    for path, expected in outputs.items():
        assert path.read_text() == scaffold.normalize_generated_text(expected)
    tutorial = (PACKAGE / "manual-tutorial.html").read_text()
    quest = (PACKAGE / "quest.html").read_text()
    for page in (tutorial, quest):
        assert "Pending evidence:" in page
        assert EXPECTED[0] in html.unescape(page)
        for filename in ("03-enter-instructions", "04-save-instructions", "14-cg-01"):
            assert f'src="screenshots/manual/annotated/{filename}.png"' not in page
        assert "The captured Preview evidence records CG-01" not in page
    assert 'src="screenshots/assisted/annotated/02-cg-01.png"' not in quest
    assert "Historical response evidence" in quest
    assert "SYN-BCS" in quest
    report = (PACKAGE / "evidence-report.html").read_text()
    gaps = report.split("<h2>Reference-only visual gaps</h2>", 1)[1]
    for key in REPAIRED_CAPTURES:
        assert key in gaps
    step14 = re.search(r'id="step-14">(.*?)</article>', tutorial, re.DOTALL).group(1)
    assert "fresh Preview" in html.unescape(step14)


def test_historical_native_export_is_not_presented_as_the_repaired_source():
    metadata = read_json(PACKAGE / "exports/care-gap-closure-solution-export.json")
    assert metadata["source_contract_status"] == "stale_source"
    assert hashlib.sha256((ROOT / metadata["zip"]).read_bytes()).hexdigest() == (
        "dd5fdcdc5fb7c484ad923464709d62587a1eca23ca8d497b4ddc72a7142681a0"
    )
    rows = read_json(ROOT / "state/copilot_studio_solution_exports.json")["solutions"]
    assert next(row for row in rows if row["slug"] == "care-gap-closure") == metadata
    links = scaffold.copilot_solution_download_links(context())
    assert "Historical export" in links
    assert "Download Copilot Studio solution" not in links
    assert metadata["source_contract_note"] in html.unescape(links)
    assert "Historical export" in (PACKAGE / "exports/README.md").read_text()


def test_source_bundle_contains_repaired_sources_and_preserved_media():
    bundle = PACKAGE / "exports/care-gap-closure-source.zip"
    with zipfile.ZipFile(bundle) as archive:
        for relative in (
            "manual/GLOBAL-INSTRUCTIONS.md",
            "copilot-studio/settings.mcs.yml",
            "evals/transcripts.json",
            "evals/visual-checkpoints.json",
            "manual-tutorial.html",
            "quest.html",
            "evidence-report.html",
            "exports/care-gap-closure-solution-export.json",
        ):
            path = PACKAGE / relative
            assert archive.read(path.relative_to(ROOT).as_posix()) == (
                build_solution_export.bundle_bytes(path)
            )
        for path in (PACKAGE / "screenshots").rglob("*"):
            if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif"}:
                assert archive.read(path.relative_to(ROOT).as_posix()) == path.read_bytes()
