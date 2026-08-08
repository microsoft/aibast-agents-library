import importlib.util
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FRAGMENT = Path(
    "/Users/kodywildfeuer/.copilot/session-state/"
    "994e930b-0925-4d45-b127-e1be7576fff1/files/"
    "rollout-fragments/financial-services.json"
)

SOLUTIONS = {
    "fs-customer-onboarding": (
        "customer_onboarding_fs_stack/customer_onboarding_fs_agent.py",
        "FSCustomerOnboardingAgent",
    ),
    "portfolio-rebalancing": (
        "portfolio_rebalancing_stack/portfolio_rebalancing_agent.py",
        "PortfolioRebalancingAgent",
    ),
    "underwriting-support": (
        "underwriting_support_stack/underwriting_support_agent.py",
        "UnderwritingSupportAgent",
    ),
    "customer-sentiment-churn": (
        "customer_sentiment_churn_stack/customer_sentiment_churn_agent.py",
        "CustomerSentimentChurnAgent",
    ),
    "fraud-detection-alert": (
        "fraud_detection_alert_stack/fraud_detection_alert_agent.py",
        "FraudDetectionAlertAgent",
    ),
    "claims-processing": (
        "claims_processing_stack/claims_processing_agent.py",
        "ClaimsProcessingAgent",
    ),
    "loan-origination-assistant": (
        "loan_origination_assistant_stack/loan_origination_assistant_agent.py",
        "LoanOriginationAssistantAgent",
    ),
    "wealth-insights-generator": (
        "wealth_insights_generator_stack/wealth_insights_generator_agent.py",
        "WealthInsightsGeneratorAgent",
    ),
    "financial-advisor-copilot": (
        "financial_advisor_copilot_stack/financial_advisor_copilot_agent.py",
        "FinancialAdvisorCopilotAgent",
    ),
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_agent(slug):
    relative, class_name = SOLUTIONS[slug]
    source = (
        ROOT
        / "agents"
        / "@aibast-agents-library"
        / "financial_services_stacks"
        / relative
    )
    spec = importlib.util.spec_from_file_location(slug.replace("-", "_"), source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return source, getattr(module, class_name)()


def test_direct_perform_outputs_cover_every_locked_operation():
    for slug in SOLUTIONS:
        _, agent = load_agent(slug)
        cases = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")["cases"]
        operations = agent.metadata["parameters"]["properties"]["operation"]["enum"]
        assert [case["operation"] for case in cases] == operations
        for case in cases:
            output = agent.perform(
                operation=case["operation"], **case.get("arguments", {})
            )
            assert "SYNTHETIC DEMO DATA" in output
            assert len(output.split()) >= case["min_words"]
            for expected in case["must_include"]:
                assert expected.lower() in output.lower(), (slug, case["id"], expected)
            for forbidden in case["must_not_include"]:
                assert forbidden.lower() not in output.lower()


def test_routing_schema_and_unknown_record_safety():
    for slug in SOLUTIONS:
        _, agent = load_agent(slug)
        description = agent.metadata["description"].lower()
        assert "fictional" in description or "synthetic" in description
        assert "review" in description
        operation = agent.metadata["parameters"]["properties"]["operation"]
        assert operation["description"]
        id_fields = set(agent.metadata["parameters"]["properties"]) - {"operation"}
        if id_fields:
            identifier = next(iter(id_fields))
            output = agent.perform(**{
                "operation": operation["enum"][0],
                identifier: "NOT-A-SYNTHETIC-RECORD",
            })
            assert "no substitute record was used" in output


def test_claims_metadata_routes_named_file_readiness_requests():
    _, agent = load_agent("claims-processing")
    description = agent.metadata["description"]
    operation = agent.metadata["parameters"]["properties"]["operation"]["description"]
    claim_id = agent.metadata["parameters"]["properties"]["claim_id"]["description"]
    assert "what is missing from a named claimant's file before evaluation" in description
    assert "Choose adjudication_review" in operation
    assert "missing documents" in operation
    assert "whether any claim was approved" in operation
    assert "Always call this tool" in description
    assert "Jennifer Liu or the theft file is CLM-2025-7004" in claim_id


def test_locked_failure_phrases_are_explicit_in_routing_metadata():
    expected = {
        "customer-sentiment-churn": ("Marcus", "retention_actions"),
        "financial-advisor-copilot": ("who is waiting", "service_intake"),
        "fraud-detection-alert": ("Dubai alert", "transaction_analysis"),
        "fs-customer-onboarding": ("Blackwood", "document_checklist"),
        "loan-origination-assistant": ("document review", "application_review"),
        "portfolio-rebalancing": ("drift guardrails", "portfolio_analysis"),
        "underwriting-support": (
            "most experienced underwriter",
            "risk_evaluation",
        ),
        "wealth-insights-generator": ("largest held-away", "client_insights"),
    }
    for slug, phrases in expected.items():
        _, agent = load_agent(slug)
        metadata = json.dumps(agent.metadata)
        assert "Always call this tool" in metadata
        assert all(phrase in metadata for phrase in phrases)


def test_claims_strict_capture_proves_named_file_routing():
    cases = read_json(ROOT / "tests" / "demo_cases" / "claims-processing.json")[
        "cases"
    ]
    artifact = read_json(
        ROOT / "solutions" / "claims-processing" / "evals" / "transcripts.json"
    )
    assert artifact["strict_isolation"] is True
    assert artifact["loaded_tools_after_capture"] == ["ClaimsProcessingAgent"]
    source, _ = load_agent("claims-processing")
    case_file = ROOT / "tests" / "demo_cases" / "claims-processing.json"
    assert artifact["agent_sources"][0]["sha256"] == hashlib.sha256(
        source.read_bytes()
    ).hexdigest()
    assert artifact["case_file_sha256"] == hashlib.sha256(
        case_file.read_bytes()
    ).hexdigest()
    captured = {item["case_id"]: item for item in artifact["transcripts"]}
    assert set(captured) == {case["id"] for case in cases}
    assert all(item["passed"] for item in captured.values())
    clp02 = captured["CLP-02"]
    assert "CLM-2025-7004" in clp02["agent_logs"]
    assert "Receipts or appraisals" in clp02["agent_logs"]
    assert clp02["expected_agent"] == "ClaimsProcessingAgent"


def test_all_financial_strict_captures_cover_locked_cases():
    for slug in SOLUTIONS:
        source, agent = load_agent(slug)
        case_file = ROOT / "tests" / "demo_cases" / f"{slug}.json"
        cases = read_json(case_file)["cases"]
        artifact = read_json(
            ROOT / "solutions" / slug / "evals" / "transcripts.json"
        )
        assert artifact["strict_isolation"] is True
        assert artifact["loaded_tools_after_capture"] == [agent.name]
        assert artifact["agent_sources"] == [
            {
                "path": source.relative_to(ROOT).as_posix(),
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        ]
        assert artifact["case_file_sha256"] == hashlib.sha256(
            case_file.read_bytes()
        ).hexdigest()
        captured = {item["case_id"]: item for item in artifact["transcripts"]}
        assert set(captured) == {case["id"] for case in cases}
        for case in cases:
            item = captured[case["id"]]
            assert item["prompt"] == case["prompt"]
            assert item["passed"] is True
            assert item["expected_agent"] == agent.name
            for expected in case["must_include"]:
                assert expected.lower() in item["agent_logs"].lower()


def test_packages_pin_onepagers_and_have_manual_assets():
    onepagers = read_json(ROOT / "state" / "onepager_content.json")["onepagers"]
    for slug in SOLUTIONS:
        package = ROOT / "solutions" / slug
        cases = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")["cases"]
        promise_map = read_json(package / "evals" / "onepager-map.json")
        deployment = read_json(package / "deployment.json")
        audit = read_json(package / "evals" / "source-audit.json")
        source, agent = load_agent(slug)
        assert promise_map["source_slide_sha256"] == onepagers[
            promise_map["onepager"]
        ]["source_sha256"]
        assert deployment["copilot_studio"]["manual_skill_count"] == len(cases)
        assert len(list((package / "manual" / "knowledge").glob("*.md"))) == 2
        skills = list((package / "manual" / "skills").glob("*/SKILL.md"))
        assert len(skills) == len(cases)
        assert all(path.read_text(encoding="utf-8").startswith("---\n") for path in skills)
        assert set(audit["operations"]) == {case["operation"] for case in cases}
        assert audit["source_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
        assert audit["unresolved_defects"] == []
        assert deployment["name"] == f"@aibast-agents-library/{slug}"
        assert deployment["expected_tool"] == agent.name
        assert deployment["target_filename"] == source.name


def test_demo_cases_are_persona_language_locked_and_safe():
    for slug in SOLUTIONS:
        cases = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")["cases"]
        assert len({case["operation"] for case in cases}) == len(cases)
        for case in cases:
            assert case["persona"]
            assert case["operation"] not in case["prompt"]
            assert case["must_include"]
            assert case["expects_agent"] == SOLUTIONS[slug][1]


def test_curated_fragment_has_pilot_quality_catalog_and_architecture_entries():
    fragment = read_json(FRAGMENT)
    assert fragment["schema"] == "aibast-solution-copy/1.0"
    expected = {f"@aibast-agents-library/{slug}" for slug in SOLUTIONS}
    assert set(fragment["solutions"]) == expected
    for entry in fragment["solutions"].values():
        assert all(
            entry[field]
            for field in (
                "sales_headline",
                "card_pitch",
                "why_try",
                "customer_challenge",
                "microsoft_ai_story",
                "business_value",
                "search_terms",
                "blueprint_role",
                "sample_prompts",
                "architecture",
            )
        )
        architecture = entry["architecture"]
        assert architecture["business_flow"]
        assert architecture["capabilities"]
        assert architecture["required_connections"]
        assert architecture["acceptance_checks"]
        assert architecture["hard_mode"]
        assert "stop before publish" in architecture["copilot_studio_prompt"].lower()


def test_copilot_studio_sources_are_promotion_ready():
    for slug in SOLUTIONS:
        package = ROOT / "solutions" / slug
        studio = package / "copilot-studio"
        assert (studio / "settings.mcs.yml").is_file()
        assert (studio / "agent.sync.yaml").is_file()
        deployment = read_json(package / "deployment.json")
        assert len(list((studio / "behaviors").glob("*.mcs.yml"))) == len(
            deployment["copilot_studio"]["operations"]
        )
        knowledge = studio / "capabilities" / "knowledge" / "files"
        assert len(list(knowledge.glob("*.md"))) == 2
