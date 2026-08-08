import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = (
    ROOT
    / "agents"
    / "@aibast-agents-library"
    / "financial_services_stacks"
)

PACKAGES = {
    "fs-customer-onboarding": {
        "source": "customer_onboarding_fs_stack/customer_onboarding_fs_agent.py",
        "class": "FSCustomerOnboardingAgent",
        "constants": [
            "CUSTOMER_APPLICATIONS",
            "KYC_DOCUMENTS",
            "VERIFICATION_STATUS",
            "ACCOUNT_TYPES",
        ],
    },
    "portfolio-rebalancing": {
        "source": "portfolio_rebalancing_stack/portfolio_rebalancing_agent.py",
        "class": "PortfolioRebalancingAgent",
        "constants": ["PORTFOLIOS", "TAX_RATES"],
    },
    "underwriting-support": {
        "source": "underwriting_support_stack/underwriting_support_agent.py",
        "class": "UnderwritingSupportAgent",
        "constants": [
            "APPLICATIONS",
            "UNDERWRITING_GUIDELINES",
            "PRICING_MODELS",
        ],
    },
    "customer-sentiment-churn": {
        "source": "customer_sentiment_churn_stack/customer_sentiment_churn_agent.py",
        "class": "CustomerSentimentChurnAgent",
        "constants": [
            "CUSTOMER_INTERACTIONS",
            "CHURN_INDICATORS",
            "RETENTION_ACTIONS",
            "SEGMENT_BENCHMARKS",
        ],
    },
    "fraud-detection-alert": {
        "source": "fraud_detection_alert_stack/fraud_detection_alert_agent.py",
        "class": "FraudDetectionAlertAgent",
        "constants": [
            "TRANSACTIONS",
            "ALERT_RULES",
            "FRAUD_PATTERNS",
            "INVESTIGATION_CASES",
        ],
    },
    "claims-processing": {
        "source": "claims_processing_stack/claims_processing_agent.py",
        "class": "ClaimsProcessingAgent",
        "constants": [
            "CLAIMS",
            "POLICY_DETAILS",
            "FRAUD_INDICATORS",
            "ADJUSTER_NOTES",
        ],
    },
    "loan-origination-assistant": {
        "source": "loan_origination_assistant_stack/loan_origination_assistant_agent.py",
        "class": "LoanOriginationAssistantAgent",
        "constants": [
            "LOAN_APPLICATIONS",
            "APPROVAL_CRITERIA",
            "DOCUMENT_REQUIREMENTS",
            "RATE_SHEET",
            "CONDITIONS",
        ],
    },
    "wealth-insights-generator": {
        "source": "wealth_insights_generator_stack/wealth_insights_generator_agent.py",
        "class": "WealthInsightsGeneratorAgent",
        "constants": [
            "MARKET_DATA",
            "CLIENT_PORTFOLIOS",
            "PERFORMANCE_BENCHMARKS",
            "OPPORTUNITY_SIGNALS",
        ],
    },
    "financial-advisor-copilot": {
        "source": "financial_advisor_copilot_stack/financial_advisor_copilot_agent.py",
        "class": "FinancialAdvisorCopilotAgent",
        "constants": [
            "CLIENT_PORTFOLIOS",
            "INVESTMENT_RECOMMENDATIONS",
            "COMPLIANCE_RULES",
            "SERVICE_REQUESTS",
        ],
    },
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_package(slug):
    config = PACKAGES[slug]
    source = SOURCE_ROOT / config["source"]
    spec = importlib.util.spec_from_file_location(
        f"knowledge_fidelity_{slug.replace('-', '_')}", source
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return source, module, getattr(module, config["class"])()


def knowledge_paths(slug):
    knowledge = ROOT / "solutions" / slug / "manual" / "knowledge"
    records = next(knowledge.glob("*synthetic-records.md"))
    controls = next(knowledge.glob("*controls-and-review.md"))
    return records, controls


def test_knowledge_files_are_complete_not_placeholder_summaries():
    forbidden = ("todo", "placeholder", "schema-only", "add records here")
    for slug in PACKAGES:
        records_path, controls_path = knowledge_paths(slug)
        records = records_path.read_text(encoding="utf-8")
        controls = controls_path.read_text(encoding="utf-8")
        assert len(records) > 9_000, slug
        assert len(controls) > 20_000, slug
        assert "Complete deterministic source records" in records
        assert "Locked-case deterministic outputs" in records
        assert "Exact tool-routing contract" in controls
        assert "Canonical strict-isolation tool evidence" in controls
        assert "Evidence-first response contract" in controls
        combined = (records + controls).lower()
        for marker in forbidden:
            assert marker not in combined, (slug, marker)


def test_every_deterministic_source_record_is_packaged_exactly():
    for slug, config in PACKAGES.items():
        source, module, agent = load_package(slug)
        records_path, controls_path = knowledge_paths(slug)
        records = records_path.read_text(encoding="utf-8")
        controls = controls_path.read_text(encoding="utf-8")
        assert hashlib.sha256(source.read_bytes()).hexdigest() in records
        for name in config["constants"]:
            exact = json.dumps(
                getattr(module, name),
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            assert f"### `{name}`" in records
            assert exact in records
        exact_metadata = json.dumps(
            agent.metadata,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        assert exact_metadata in controls


def test_every_locked_case_has_exact_source_and_transcript_evidence():
    for slug in PACKAGES:
        _, _, agent = load_package(slug)
        records_path, controls_path = knowledge_paths(slug)
        records = records_path.read_text(encoding="utf-8")
        controls = controls_path.read_text(encoding="utf-8")
        cases = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")[
            "cases"
        ]
        artifact = read_json(
            ROOT / "solutions" / slug / "evals" / "transcripts.json"
        )
        captured = {item["case_id"]: item for item in artifact["transcripts"]}
        assert set(captured) == {case["id"] for case in cases}
        for case in cases:
            args = case.get("arguments") or {}
            direct_output = agent.perform(operation=case["operation"], **args)
            item = captured[case["id"]]
            assert direct_output in records
            assert case["persona"] in controls
            assert case["prompt"] in controls
            assert item["agent_logs"] in controls
            for expected in case["must_include"]:
                assert expected.lower() in (records + controls).lower()


def test_controls_embed_every_reviewed_skill_and_regulated_boundary():
    required_terms = (
        "never browse",
        "never",
        "invent",
        "required reviewers",
        "no external side effect",
        "not advice",
    )
    for slug in PACKAGES:
        _, controls_path = knowledge_paths(slug)
        controls = controls_path.read_text(encoding="utf-8")
        lower = controls.lower()
        for term in required_terms:
            assert term in lower, (slug, term)
        skills = sorted(
            (ROOT / "solutions" / slug / "manual" / "skills").glob(
                "*/SKILL.md"
            )
        )
        assert skills
        for skill in skills:
            assert skill.read_text(encoding="utf-8").rstrip() in controls
