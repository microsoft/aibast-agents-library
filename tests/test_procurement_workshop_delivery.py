import copy
import hashlib
import html
import json
import re
import zipfile
from pathlib import Path

from bs4 import BeautifulSoup

from tools import scaffold_solution_journey as scaffold
from tools.build_solution_export import bundle_bytes


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "solutions/procurement-agent"
# The grounding-r3 candidate (source commit 38a1c30d) was superseded by the
# full re-shoot in the real Copilot Studio UI. Its records stay under
# evals/history/; these tests protect the current, fully captured package.
MANUAL_INPUTS = (
    "manual/GLOBAL-INSTRUCTIONS.md",
    "manual/knowledge/aibast_procurement-agent-rules-and-guardrails.md",
    "manual/knowledge/aibast_procurement-agent-synthetic-records.md",
    "manual/skills/aibast_purchase-request_01/SKILL.md",
    "manual/skills/aibast_vendor-comparison_02/SKILL.md",
    "manual/skills/aibast_approval-routing_03/SKILL.md",
    "manual/skills/aibast_spend-analysis_04/SKILL.md",
    "manual/skills/aibast_draft-purchase-order_05/SKILL.md",
    "manual/skills/aibast_expedite-approval_06/SKILL.md",
    "manual/skills/aibast_budget-impact_07/SKILL.md",
    "manual/skills/aibast_draft-rfq_08/SKILL.md",
)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def context():
    return scaffold.load_context(
        ROOT, "procurement-agent", allow_pending=True,
        raw_base="https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/",
    )


def test_procurement_current_evidence_passes_every_locked_case_and_stays_draft():
    evidence = read_json(PACKAGE / "evals/manual-build-evidence.json")
    assert evidence["status"] == "passed"
    assert scaffold.manual_evidence_passed(evidence) is True
    for legacy in ("build_revision", "source_commit", "native_regression", "source_contract_status"):
        assert legacy not in evidence
    components = evidence["manual_components"]
    assert components["skills"] == {"expected": 8, "confirmed": 8}
    assert components["knowledge_files"] == {"expected": 2, "confirmed": 2}
    assert components["tools"] == {"expected": 0, "confirmed": 0}
    assert components["web_search_removed"]["confirmed"] is True
    assert evidence["publication_gate"]["published"] is False
    assert evidence["publication_gate"]["required_state"] == "Draft"
    expected = {
        case["id"]: case
        for case in read_json(ROOT / "tests/demo_cases/procurement-agent.json")["cases"]
    }
    assert len(expected) == 8
    assert {row["case_id"] for row in evidence["canonical_preview"]} == set(expected)
    for row in evidence["canonical_preview"]:
        assert row["passed"] is True
        assert row["prompt"] == expected[row["case_id"]]["prompt"]
        assert row["must_include"] == expected[row["case_id"]]["must_include"]
        assert row["must_not_include"] == expected[row["case_id"]]["must_not_include"]
    # Fail closed: one unproven case or one unconfirmed component blocks acceptance.
    unproven = copy.deepcopy(evidence)
    unproven["canonical_preview"][-1]["passed"] = None
    assert scaffold.manual_evidence_passed(unproven) is False
    partial = copy.deepcopy(evidence)
    partial["manual_components"]["skills"]["confirmed"] = 7
    assert scaffold.manual_evidence_passed(partial) is False
    published = copy.deepcopy(evidence)
    published["publication_gate"]["published"] = True
    assert scaffold.manual_evidence_passed(published) is False
    assert all(case["passed"] is True for case in scaffold.easy_case_records(context()))


def test_procurement_manual_inputs_and_locked_cases_are_the_downloadable_sources():
    found = {
        path.relative_to(PACKAGE).as_posix() for path in (PACKAGE / "manual").rglob("*.md")
    }
    assert found == set(MANUAL_INPUTS)
    bundle = PACKAGE / "exports/procurement-agent-source.zip"
    with zipfile.ZipFile(bundle) as archive:
        names = set(archive.namelist())
        for relative in MANUAL_INPUTS:
            name = f"solutions/procurement-agent/{relative}"
            assert archive.read(name) == bundle_bytes(ROOT / name)
    # A shipped input inventory must hash the bytes it ships. The superseded
    # grounding-r3 inventory pins old records/rules/cases bytes and must not be
    # presented as a current download.
    stale = "solutions/procurement-agent/evals/manual-inputs-r3.json"
    if (ROOT / stale).exists():
        inventory = read_json(ROOT / stale)
        current = all(
            sha256((ROOT / item["path"]).read_bytes()) == item["sha256"]
            for item in [*inventory["inputs"], inventory["locked_cases"]]
        )
        manifest_paths = {item["path"] for item in read_json(PACKAGE / "export-manifest.json")["files"]}
        assert current or (stale not in names and stale not in manifest_paths), (
            "superseded manual-inputs-r3.json still ships with hashes that no longer match"
        )


def test_procurement_generated_guides_deliver_current_policy_and_real_evidence():
    _, outputs = scaffold.generated_outputs(context())
    for path, expected in outputs.items():
        assert path.read_text(encoding="utf-8") == scaffold.normalize_generated_text(expected)
    instructions = (PACKAGE / "manual/GLOBAL-INSTRUCTIONS.md").read_text(encoding="utf-8")
    for name in ("manual-tutorial.html", "quest.html"):
        text = (PACKAGE / name).read_text(encoding="utf-8")
        payloads = {
            int(number): html.unescape(content)
            for number, content in re.findall(
                r'<pre class="copy-source" id="hard-copy-(\d+)" hidden>(.*?)</pre>',
                text, re.DOTALL,
            )
        }
        assert payloads[3] == instructions
        assert "Pending evidence:" not in text
        assert "grounding-r3" not in text
        if name == "quest.html":
            assert "Download Copilot Studio solution" in text
        page = BeautifulSoup(text, "html.parser")
        assert page.select('a[href="exports/procurement-agent-source.zip"]')
        assert page.select('img[data-evidence-status="reusable"]')
        if name == "quest.html":
            assert "Do not publish. This module ends with a validated Draft." in text
        else:
            assert "Confirm Draft and stop before publish" in text
    report = (PACKAGE / "evidence-report.html").read_text(encoding="utf-8")
    gaps = report.split("<h2>Reference-only visual gaps</h2>", 1)[1].split("Downloads for audit", 1)[0]
    assert not BeautifulSoup(gaps, "html.parser").select("tbody tr")
    assert "Download Copilot Studio solution" in report


def test_procurement_source_bundle_is_the_standard_complete_bundle():
    manifest = read_json(PACKAGE / "export-manifest.json")
    bundle = manifest["bundle"]
    assert bundle["path"] == "solutions/procurement-agent/exports/procurement-agent-source.zip"
    assert "include_paths" not in bundle
    assert "native_importable" not in bundle
    assert "source_bundle" not in read_json(PACKAGE / "deployment.json")
    with zipfile.ZipFile(ROOT / bundle["path"]) as archive:
        names = archive.namelist()
        for name in names:
            assert archive.read(name) == bundle_bytes(ROOT / name)
        for required in (
            "solutions/procurement-agent/manual-tutorial.html",
            "solutions/procurement-agent/quest.html",
            "solutions/procurement-agent/evals/manual-build-evidence.json",
            "solutions/procurement-agent/screenshots/manual/browserfilm.json",
        ):
            assert required in names


def test_procurement_history_stays_intact_and_current_captures_are_reusable():
    history = read_json(PACKAGE / "evals/history/2026-08/index.json")
    assert history["status"] == "historical_only"
    assert len(history["files"]) == 8
    for item in history["files"]:
        data = (ROOT / item["archived_path"]).read_bytes()
        assert len(data) == item["bytes"]
        assert sha256(data) == item["sha256"]
    visual = read_json(PACKAGE / "evals/visual-checkpoints.json")
    assert visual["summary"]["reshoot_required"] == 0
    assert visual["summary"]["reusable"] == len(visual["captures"])
    for row in visual["captures"]:
        assert row["status"] == "reusable"
        assert (ROOT / row["source"]).is_file()
        assert (ROOT / row["annotated"]).is_file()
    for mode, count in (("manual", 28), ("assisted", 10)):
        film = read_json(PACKAGE / f"screenshots/{mode}/browserfilm.json")
        assert len(film["frames"]) == count
        assert all(frame["captured"] is True for frame in film["frames"])


def test_procurement_current_native_export_is_unpublished_in_every_surface():
    metadata = read_json(PACKAGE / "exports/procurement-agent-solution-export.json")
    assert metadata["status"] == "exported"
    assert metadata["published"] is False
    assert metadata["managed"] is False
    assert "source_contract_status" not in metadata
    assert sha256((ROOT / metadata["zip"]).read_bytes()) == metadata["sha256"]
    assert metadata["sha256"] != read_json(PACKAGE / "evals/history/2026-08/solution-export.json")["sha256"]
    records = read_json(ROOT / "state/copilot_studio_solution_exports.json")["solutions"]
    assert next(row for row in records if row["slug"] == "procurement-agent") == metadata
    assert "Download Copilot Studio solution" in scaffold.copilot_solution_download_links(context())


def test_procurement_deployment_recipe_reflects_the_current_validated_drafts():
    studio = read_json(PACKAGE / "deployment.json")["copilot_studio"]
    evidence = read_json(PACKAGE / "evals/manual-build-evidence.json")
    cases = len(evidence["canonical_preview"])
    for key in ("validated_manual", "validated_pilot"):
        assert studio[key]["published"] is False
        # deployment.json must not keep claiming the superseded candidate state.
        assert "source_contract_status" not in studio[key], key
        assert studio[key].get("preview_cases_total") in (None, cases), key
        assert studio[key].get("preview_cases_passed") in (None, cases), key
    assert "source_contract_status" not in studio
