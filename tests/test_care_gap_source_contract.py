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
    cases = read_json(CASE_FILE)["cases"]
    routes = normalize_manual_instructions.skill_routes(
        cases, manual / "skills", instructions
    )
    assert normalize_manual_instructions.render_section(cases, routes) in instructions
    assert "SYN-COL has 182 records, SYN-BCS has 108, and SYN-CDC has 53" in instructions
    assert "## Locked Preview evidence anchors" not in instructions
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
        # behaviors are named after the skill's front-matter name, not its folder
        skill_name = re.search(r"^name:\s*(\S+)", source.read_text(), re.M).group(1)
        mirror = native / "behaviors" / f"aibast_{skill_name}.mcs.yml"
        assert textwrap.dedent(mirror.read_text().split("content: |\n", 1)[1]) == source.read_text()
    for source in [
        *sorted((manual / "skills").glob("aibast_gap-analysis_*/SKILL.md")),
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
    # 2026-10-06 video alignment: CG-05..CG-10 were added and every case was recaptured live in strict
    # isolation, replacing the 2026-09-11 offline revalidation of the four original cases.
    assert hashlib.sha256(json.dumps(immutable, sort_keys=True).encode()).hexdigest() == (
        "f8bef795ee4ebc0eef757b57d66966e7d7df6a212bf19041cb01a0b8482e1663"
    )
    assert capture["case_file_sha256"] == hashlib.sha256(CASE_FILE.read_bytes()).hexdigest()
    assert capture["strict_isolation"] is True
    for case, transcript in zip(read_json(CASE_FILE)["cases"], capture["transcripts"]):
        assert case["id"] == transcript["case_id"]
        assert transcript["must_include"] == case["must_include"]
        assert run_case(case, transcript["assistant_response"], transcript["agent_logs"]) == (True, [])


def test_live_source_revision_is_verified_by_the_reshoot_and_stays_fail_closed():
    # The repaired CG-01 contract (SYN-COL leader) was re-shot live in Copilot
    # Studio for both lanes. Acceptance must come from the current evidence,
    # every locked case must pass, and both agents must remain unpublished Drafts.
    cases = read_json(CASE_FILE)["cases"]
    manual = read_json(PACKAGE / "evals/manual-build-evidence.json")
    preview = read_json(PACKAGE / "evals/copilot-studio-preview-evidence.json")
    assert manual["status"] == "passed"
    assert manual["manual_components"]["global_instructions"]["confirmed"] is True
    assert manual["publication_gate"]["published"] is False
    assert preview["status"] == "Draft"
    assert preview["published"] is False
    for rows in (manual["canonical_preview"], preview["cases"]):
        assert [row["case_id"] for row in rows] == [case["id"] for case in cases]
        assert all(row["passed"] is True for row in rows)
        assert cg01(rows)["must_include"] == EXPECTED
        assert "captured_must_include" not in cg01(rows)
    assert cg01(scaffold.easy_case_records(context()))["passed"] is True
    studio = read_json(PACKAGE / "deployment.json")["copilot_studio"]
    for key in ("validated_manual", "validated_pilot"):
        assert studio[key]["published"] is False
        assert "source_contract_status" not in studio[key], (
            f"{key} still carries the superseded reshoot_required contract"
        )
        assert studio[key]["preview_cases_total"] == len(cases)
        assert studio[key]["preview_cases_passed"] == len(cases)
    # The gate still fails closed if CG-01 loses its pass.
    broken = json.loads(json.dumps(manual))
    cg01(broken["canonical_preview"])["passed"] = None
    assert scaffold.manual_evidence_passed(broken) is False


def test_repaired_checkpoints_show_the_current_contract():
    visual = read_json(PACKAGE / "evals/visual-checkpoints.json")
    captures = {capture["id"]: capture for capture in visual["captures"]}
    assert visual["summary"] == {
        "total_existing_captures": len(captures),
        "reusable": len(captures),
        "reshoot_required": 0,
    }
    assert {capture["status"] for capture in captures.values()} == {"reusable"}
    for key in ("easy-cg-01", "hard-cg-01"):
        capture = captures[key]
        assert (ROOT / capture["annotated"]).is_file()
        assert capture["visible_anchors"] == EXPECTED
        assert not any(name.startswith("historical") for name in capture)
    assert "historical_release_review" not in visual


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
    # Re-shot 2026-10 frame set: 32 manual + 12 assisted captures, their
    # annotated copies, two films, two contact sheets and two audit shots.
    assert len(manifest) == 94
    assert hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest() == (
        "11ddd09c33c42ec7ea5f7790342c22dfd10c4e68af96f2421c1756211cb19ecf"
    )


def test_generated_pages_promote_only_the_current_contract():
    ctx = context()
    _, outputs = scaffold.generated_outputs(ctx)
    for path, expected in outputs.items():
        assert path.read_text() == scaffold.normalize_generated_text(expected)
    tutorial = (PACKAGE / "manual-tutorial.html").read_text()
    quest = (PACKAGE / "quest.html").read_text()
    for page in (tutorial, quest):
        assert "Pending evidence:" not in page
        assert EXPECTED[0] in html.unescape(page)
        assert 'src="screenshots/manual/annotated/22-cg-01.png"' in page
        unescaped = html.unescape(page)
        assert "records CG-01 with the recorded identifiers SYN-BCS" not in unescaped
        if "The captured Preview evidence records CG-01" in unescaped:
            assert f"records CG-01 with the recorded identifiers {EXPECTED[0]}" in unescaped
        assert "Historical response evidence" not in page
    assert "Confirm Draft and stop before publish" in tutorial
    assert "Do not choose Publish" in tutorial
    assert 'src="screenshots/assisted/annotated/02-cg-01.png"' in quest
    report = (PACKAGE / "evidence-report.html").read_text()
    gaps = report.split("<h2>Reference-only visual gaps</h2>", 1)[1].split("</section>", 1)[0]
    assert "<tbody></tbody>" in gaps
    step = re.search(r'id="step-21">(.*?)</article>', tutorial, re.DOTALL).group(1)
    assert "fresh Preview" in html.unescape(step)


def test_native_export_is_the_current_unpublished_source():
    metadata = read_json(PACKAGE / "exports/care-gap-closure-solution-export.json")
    assert metadata["status"] == "exported"
    assert metadata["published"] is False
    assert metadata["managed"] is False
    assert "source_contract_status" not in metadata
    assert hashlib.sha256((ROOT / metadata["zip"]).read_bytes()).hexdigest() == metadata["sha256"]
    rows = read_json(ROOT / "state/copilot_studio_solution_exports.json")["solutions"]
    assert next(row for row in rows if row["slug"] == "care-gap-closure") == metadata
    links = scaffold.copilot_solution_download_links(context())
    assert "Historical export" not in links
    assert "Download Copilot Studio solution" in links
    assert "Historical export" not in (PACKAGE / "exports/README.md").read_text()


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
