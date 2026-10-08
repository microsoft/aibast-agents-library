import importlib.util
import hashlib
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent

AGENTS = [
    {
        "id": "patient_intake",
        "slug": "patient-intake",
        "path": "agents/@aibast-agents-library/healthcare_stacks/patient_intake_stack/patient_intake_agent.py",
        "class": "PatientIntakeAgent",
        "operations": [
            "intake_readiness",
            "coverage_evidence",
            "appointment_availability",
            "pre_visit_summary",
            "new_patient_intake",
            "appointment_hold_draft",
            "intake_packet",
            "reminder_plan",
        ],
        "filter": {"patient_id": "SYN-PT-001"},
        "case_filters": {
            "new_patient_intake": {"patient_id": "SYN-PT-003"},
            "appointment_hold_draft": {"patient_id": "SYN-PT-003"},
            "intake_packet": {"patient_id": "SYN-PT-003"},
            "reminder_plan": {"patient_id": "SYN-PT-003"},
        },
        "legacy": [
            ("insurance_verification", "Synthetic"),
            ("appointment_scheduling", "nothing has been reserved or booked"),
        ],
        "source_constants": ["PATIENTS", "AVAILABILITY", "PROVIDERS", "INTAKE_PACKETS", "REMINDER_PROTOCOL"],
        "headings": [
            "Intake Readiness Draft",
            "Coverage Evidence Review",
            "Appointment Availability Review",
            "Pre-Visit Readiness Summary",
            "New Patient Registration Draft",
            "Appointment Request Draft",
            "Digital Intake Packet Draft",
            "No-Show Prevention Reminder Plan",
        ],
    },
    {
        "id": "care_gap_closure",
        "slug": "care-gap-closure",
        "path": "agents/@aibast-agents-library/healthcare_stacks/care_gap_closure_stack/care_gap_closure_agent.py",
        "class": "CareGapClosureAgent",
        "operations": [
            "gap_analysis",
            "cohort_review",
            "outreach_draft",
            "quality_dashboard",
            "hedis_status",
            "top_gaps",
            "risk_stratification",
            "outreach_strategy",
            "campaign_projection",
            "monitoring_plan",
        ],
        "filter": {"measure_id": "SYN-BCS"},
        "case_filters": {
            "gap_analysis": {}, "quality_dashboard": {}, "hedis_status": {}, "top_gaps": {},
            "risk_stratification": {}, "outreach_strategy": {}, "campaign_projection": {},
            "monitoring_plan": {},
        },
        "legacy": [
            ("outreach_campaign", "No message is sent"),
            ("hedis_dashboard", "Synthetic"),
        ],
        "source_constants": ["MEASURES", "COHORTS", "PANEL", "HEDIS_MEASURES", "A1C_TIERS", "A1C_BARRIERS",
                             "INTERVENTIONS", "CHANNEL_PLAN", "MONITORING"],
        "headings": [
            "Source-Evidence Gap Analysis",
            "Aggregate Cohort Review",
            "Outreach Draft",
            "Qualitative Quality Dashboard",
            "HEDIS Performance Summary",
            "Top 5 Care Gap Measures",
            "Diabetes Cohort Risk Stratification",
            "Outreach Strategy Draft",
            "Campaign Deployment Plan and Projected Impact",
            "Monitoring and Alert Configuration",
        ],
    },
    {
        "id": "prior_authorization",
        "slug": "prior-authorization",
        "path": "agents/@aibast-agents-library/healthcare_stacks/prior_authorization_stack/prior_authorization_agent.py",
        "class": "PriorAuthorizationAgent",
        "operations": [
            "request_evidence",
            "criteria_evidence",
            "status_summary",
            "appeal_evidence_packet",
            "patient_auth_request",
            "payer_requirements_check",
            "submission_packet",
            "approval_outlook",
            "tracking_plan",
            "portfolio_status",
            "denial_review",
        ],
        "filter": {"auth_id": "SYN-AUTH-001"},
        "legacy": [
            ("status_tracking", "not an agent determination"),
            ("appeal_preparation", "reviewer must confirm"),
        ],
        "source_constants": ["REQUESTS", "POLICIES", "PATIENT_REQUESTS", "PORTFOLIO_METRICS", "CHEN_REQUEST",
                             "PAYER_REQUIREMENTS_72148", "JOHNSON_DENIAL"],
        "headings": [
            "Prior-Authorization Evidence Inventory",
            "Criteria-to-Evidence Crosswalk",
            "Source-Recorded Status Summary",
            "Reconsideration Evidence Draft",
            "Prior Authorization Request",
            "Insurance Requirements",
            "Submission Packet",
            "Approval Outlook and Appeal Strategy",
            "Tracking and Notification Plan",
            "Active Prior Authorizations",
            "Denial Details",
        ],
    },
    {
        "id": "clinical_notes_summarizer",
        "slug": "clinical-notes-summarizer",
        "path": "agents/@aibast-agents-library/healthcare_stacks/clinical_notes_summarizer_stack/clinical_notes_summarizer_agent.py",
        "class": "ClinicalNotesSummarizerAgent",
        "operations": [
            "encounter_summary",
            "medication_inventory",
            "problem_list_extract",
            "referral_context",
            "preop_snapshot",
            "cardiopulmonary_review",
            "perioperative_medication_review",
            "anesthesia_considerations",
            "risk_factor_summary",
            "reevaluation_criteria",
            "clearance_note_draft",
        ],
        "filter": {"encounter_id": "SYN-ENC-001"},
        "legacy": [
            ("medication_review", "Source-recorded"),
            ("referral_summary", "No referral was placed"),
        ],
        "source_constants": ["ENCOUNTERS", "PREOP_PATIENT", "CARDIAC_FINDINGS", "RESPIRATORY_FINDINGS",
                             "PERIOP_MEDICATIONS", "OTHER_MEDICATIONS", "ASA_FACTORS", "REEVALUATION_CRITERIA"],
        "headings": [
            "Source-Grounded Encounter Summary",
            "Medication Source Inventory",
            "Problem-List Source Extract",
            "Referral Context Extract",
            "Pre-Op Clearance Summary",
            "Cardiopulmonary Assessment",
            "Medications - 12 Active",
            "Anesthesia and Monitoring Considerations",
            "ASA Class III Justification",
            "Clearance Re-evaluation Criteria",
            "Pre-Operative Clearance Note - Draft",
        ],
    },
]


def _load_agent(config):
    module = _load_module(config)
    return getattr(module, config["class"])()


def _load_module(config):
    path = REPO_ROOT / config["path"]
    spec = importlib.util.spec_from_file_location(f"healthcare_{config['id']}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _primitive_values(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _primitive_values(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _primitive_values(item)
    elif value is not None:
        yield str(value)


@pytest.mark.parametrize("config", AGENTS, ids=lambda config: config["id"])
def test_healthcare_schema_and_routes_are_safe(config):
    agent = _load_agent(config)
    schema = agent.metadata["parameters"]
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["operation"]
    assert schema["properties"]["operation"]["enum"] == config["operations"]
    for operation in config["operations"]:
        output = agent.perform(operation=operation).lower()
        assert "synthetic" in output
        assert "review" in output


@pytest.mark.parametrize("config", AGENTS, ids=lambda config: config["id"])
def test_healthcare_filters_and_unknown_routes(config):
    agent = _load_agent(config)
    output = agent.perform(operation=config["operations"][0], **config["filter"])
    assert next(iter(config["filter"].values())) in output
    assert "Unknown operation" in agent.perform(operation="mutate_record")


@pytest.mark.parametrize("config", AGENTS, ids=lambda config: config["id"])
def test_healthcare_legacy_routes_preserve_boundaries(config):
    agent = _load_agent(config)
    for operation, expected in config["legacy"]:
        assert expected in agent.perform(operation=operation)


def test_care_gap_persona_contract_is_explicit():
    config = next(item for item in AGENTS if item["id"] == "care_gap_closure")
    agent = _load_agent(config)
    operation_help = agent.metadata["parameters"]["properties"]["operation"]["description"]
    assert "largest evidence-review queue" in operation_help
    output = agent.perform(operation="gap_analysis")
    assert "**Largest evidence-review queue:** SYN-COL — 182 records." in output
    assert "Records requiring evidence review" in output


def test_clinical_problem_list_persona_contract_is_explicit():
    config = next(item for item in AGENTS if item["id"] == "clinical_notes_summarizer")
    agent = _load_agent(config)
    operation_help = agent.metadata["parameters"]["properties"]["operation"]["description"]
    assert "source-coded problems without confirming a diagnosis" in operation_help
    output = agent.perform(operation="problem_list_extract", encounter_id="SYN-ENC-001")
    assert "source-coded type 2 diabetes" in output
    assert "No diagnosis was added" in output


@pytest.mark.parametrize(
    ("slug", "expected_agent"),
    [
        ("patient-intake", "PatientIntakeAgent"),
        ("care-gap-closure", "CareGapClosureAgent"),
        ("prior-authorization", "PriorAuthorizationAgent"),
        ("clinical-notes-summarizer", "ClinicalNotesSummarizerAgent"),
    ],
)
def test_refined_healthcare_captures_pass_in_strict_isolation(slug, expected_agent):
    cases_path = REPO_ROOT / "tests" / "demo_cases" / f"{slug}.json"
    capture_path = REPO_ROOT / "solutions" / slug / "evals" / "transcripts.json"
    cases = json.loads(cases_path.read_text())["cases"]
    capture = json.loads(capture_path.read_text())
    assert capture["strict_isolation"] is True
    assert capture["loaded_tools_after_capture"] == [expected_agent]
    assert {item["case_id"] for item in capture["transcripts"]} == {
        case["id"] for case in cases
    }
    assert all(item["passed"] for item in capture["transcripts"])
    source = REPO_ROOT / capture["agent_sources"][0]["path"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == capture["agent_sources"][0]["sha256"]


@pytest.mark.parametrize("config", AGENTS, ids=lambda config: config["id"])
def test_healthcare_manual_knowledge_contains_complete_source_evidence(config):
    module = _load_module(config)
    knowledge_dir = REPO_ROOT / "solutions" / config["slug"] / "manual" / "knowledge"
    knowledge_files = sorted(knowledge_dir.glob("*.md"))
    assert len(knowledge_files) == 2
    records = next(path for path in knowledge_files if "synthetic-records" in path.name).read_text()
    rules = next(path for path in knowledge_files if "review-rules" in path.name).read_text()
    assert len(records) > 1800
    assert len(rules) > 2500
    for constant_name in config["source_constants"]:
        for value in _primitive_values(getattr(module, constant_name)):
            assert value in records, f"{config['slug']} knowledge missing {constant_name} value {value!r}"
    assert module.SAFETY in rules
    for operation, heading in zip(config["operations"], config["headings"]):
        assert f"`{operation}`" in rules
        assert heading in rules


@pytest.mark.parametrize("config", AGENTS, ids=lambda config: config["id"])
def test_locked_case_evidence_exists_in_source_and_manual_package(config):
    agent = _load_agent(config)
    solution = REPO_ROOT / "solutions" / config["slug"]
    manual_text = "\n".join(
        path.read_text()
        for path in sorted((solution / "manual").rglob("*.md"))
    )
    case_doc = json.loads(
        (REPO_ROOT / "tests" / "demo_cases" / f"{config['slug']}.json").read_text()
    )
    for case in case_doc["cases"]:
        case_filter = config.get("case_filters", {}).get(
            case["operation"], config["filter"]
        )
        source_output = agent.perform(operation=case["operation"], **case_filter)
        for evidence in case["must_include"]:
            assert evidence in source_output
            assert evidence in manual_text
