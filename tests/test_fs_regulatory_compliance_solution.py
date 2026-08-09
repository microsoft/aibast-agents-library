import hashlib
import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "agents"
    / "@aibast-agents-library"
    / "financial_services_stacks"
    / "regulatory_compliance_fs_stack"
    / "regulatory_compliance_fs_agent.py"
)
PACKAGE = ROOT / "solutions" / "fs-regulatory-compliance"
CASE_FILE = ROOT / "tests" / "demo_cases" / "fs-regulatory-compliance.json"
NAME = "@aibast-agents-library/fs-regulatory-compliance"
SCENARIO_CASES = {
    "regulatory-audit-readiness": "RC-01",
    "regulatory-certification-readiness": "RC-02",
    "regulatory-trade-surveillance": "RC-03",
    "regulatory-algorithm-go-live": "RC-04",
    "regulatory-board-evidence": "RC-05",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_agent_module():
    spec = importlib.util.spec_from_file_location("fs_regulatory_compliance", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_source_operations_cover_the_locked_cases():
    module = load_agent_module()
    agent = module.FSRegulatoryComplianceAgent()
    expected = {
        "compliance_dashboard": ["T-2041", "T-2233", "TRD-88133"],
        "trade_surveillance": ["TRD-88133", "field"],
        "documentation_review": ["ALGO-POV-NL"],
        "remediation_submission": [
            "TRD-88133",
            "T-2041",
            "T-2107",
            "549300XKQZ2P4NLK7T18",
            "XPAR",
            "XLON",
        ],
        "certification_tracker": ["T-2041", "T-2233"],
    }
    assert agent.metadata["parameters"]["properties"]["operation"]["enum"] == list(
        expected
    )
    for operation, values in expected.items():
        output = agent.perform(operation=operation)
        for value in values:
            assert value in output


def test_remediation_is_source_backed_and_approval_gated():
    module = load_agent_module()
    agent = module.FSRegulatoryComplianceAgent()
    operation_copy = agent.metadata["parameters"]["properties"]["operation"][
        "description"
    ]
    output = agent.perform(operation="remediation_submission")
    assert "authorized compliance review" in operation_copy
    assert "never file, transmit, or change an external ARM record" in operation_copy
    assert "file them to the ARM portal" not in operation_copy
    assert "Synthetic dry run" in output
    assert "correction report" in output
    assert "new submission" in output
    assert "authorized compliance reviewer" in output
    assert "correct venue to the admitted MIC (" not in output
    assert "Field corrections applied" not in output
    assert "no filing is transmitted" in output


def test_dashboard_sets_audit_outcome_and_advice_boundaries():
    module = load_agent_module()
    agent = module.FSRegulatoryComplianceAgent()
    output = agent.perform(operation="compliance_dashboard")
    description = agent.metadata["description"]
    assert "at-risk areas and control gaps only" in description
    assert "never state that an audit will pass or fail" in description
    assert "never present the result as legal or regulatory advice" in description
    assert "Audit-readiness assessment: AT RISK" in output
    assert "cannot determine whether an audit will pass or fail" in output
    assert "does not provide legal or regulatory advice" in output


def test_package_maps_the_approved_onepager_and_manual_assets():
    onepagers = read_json(ROOT / "state" / "onepager_content.json")["onepagers"]
    promise_map = read_json(PACKAGE / "evals" / "onepager-map.json")
    source = onepagers[promise_map["onepager"]]
    assert promise_map["solution"] == NAME
    assert promise_map["source_slide_sha256"] == source["source_sha256"]
    assert len(promise_map["promises"]) == 4
    assert len(list((PACKAGE / "manual" / "knowledge").glob("*.md"))) == 2
    skills = list((PACKAGE / "manual" / "skills").glob("*/SKILL.md"))
    assert len(skills) == 5
    assert all(path.read_text(encoding="utf-8").startswith("---\n") for path in skills)


def test_canonical_transcripts_cover_all_cases_in_isolation():
    cases = read_json(CASE_FILE)["cases"]
    artifact = read_json(PACKAGE / "evals" / "transcripts.json")
    assert artifact["solution"] == NAME
    assert artifact["strict_isolation"] is True
    assert artifact["loaded_tools_after_capture"] == ["FSRegulatoryCompliance"]
    captured = {item["case_id"]: item for item in artifact["transcripts"]}
    assert set(captured) == {case["id"] for case in cases}
    for case in cases:
        item = captured[case["id"]]
        assert item["prompt"] == case["prompt"]
        assert item["passed"] is True
        for value in case["must_include"]:
            assert value.lower() in item["agent_logs"].lower()
    rc01 = captured["RC-01"]["assistant_response"].lower()
    assert "at risk" in rc01 or "control gap" in rc01
    assert not re.search(r"\b(?:will|would|going to)\s+fail\b", rc01)
    assert "yes, you will fail" not in rc01


def test_catalog_prompts_and_deployment_match_canonical_cases():
    catalog = read_json(ROOT / "solutions" / "catalog.json")["solutions"][NAME]
    transcript = read_json(PACKAGE / "evals" / "transcripts.json")
    captured = {item["case_id"]: item for item in transcript["transcripts"]}
    prompts = catalog["sample_prompts"]
    assert len(prompts) == 5
    for prompt in prompts:
        match = re.search(r"[?&]scenario=([a-z0-9-]+)", prompt["demo_url"])
        assert match
        case_id = SCENARIO_CASES[match.group(1)]
        assert prompt["prompt"] == captured[case_id]["prompt"]

    recipe = read_json(PACKAGE / "deployment.json")
    cases = read_json(CASE_FILE)["cases"]
    smoke = next(
        case for case in cases if case["prompt"] == recipe["smoke_test"]["prompt"]
    )
    assert recipe["name"] == NAME
    assert recipe["expected_tool"] == "FSRegulatoryCompliance"
    assert recipe["smoke_test"]["must_call"] == smoke["expects_agent"]
    assert recipe["smoke_test"]["must_include"] == smoke["must_include"][:2]
    assert recipe["copilot_studio"]["manual_skill_count"] == 5
    assert recipe["demo_scenarios"] == list(SCENARIO_CASES)


def test_shared_demo_loads_exact_regulatory_transcripts():
    demo = (
        ROOT / "solutions" / "_shared" / "m365-copilot-demo.html"
    ).read_text(encoding="utf-8")
    for scenario, case_id in SCENARIO_CASES.items():
        assert f'"{scenario}": {{' in demo
        assert f'caseId: "{case_id}"' in demo
    assert 'solution: "fs-regulatory-compliance"' in demo
    assert "Exact Brainstem transcript" in demo


def test_registry_and_transcript_pin_the_final_source():
    registry = read_json(ROOT / "registry.json")["agents"]
    entry = next(item for item in registry if item["name"] == NAME)
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    transcript = read_json(PACKAGE / "evals" / "transcripts.json")
    assert entry["version"] == "2.0.2"
    assert entry["_sha256"] == digest
    assert transcript["agent_sources"] == [
        {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "sha256": digest,
        }
    ]


def test_catalog_value_claims_are_qualitative():
    catalog = read_json(ROOT / "solutions" / "catalog.json")["solutions"][NAME]
    public_copy = json.dumps(
        {
            "sales_headline": catalog["sales_headline"],
            "card_pitch": catalog["card_pitch"],
            "why_try": catalog["why_try"],
            "customer_challenge": catalog["customer_challenge"],
            "business_value": catalog["business_value"],
        }
    )
    assert "%" not in public_copy
    assert not re.search(r"\b\d+(?:\.\d+)?\b", public_copy)
