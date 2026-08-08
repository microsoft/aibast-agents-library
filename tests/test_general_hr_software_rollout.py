import hashlib
import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FRAGMENT = Path(
    "/Users/kodywildfeuer/.copilot/session-state/"
    "994e930b-0925-4d45-b127-e1be7576fff1/files/"
    "rollout-fragments/general-hr-software.json"
)
SOLUTIONS = {
    "ai-customer-assistant": (
        "agents/@aibast-agents-library/general_stacks/"
        "ai_customer_assistant_stack/ai_customer_assistant_agent.py",
        "AICustomerAssistantAgent",
    ),
    "procurement-agent": (
        "agents/@aibast-agents-library/general_stacks/"
        "procurement_agent_stack/procurement_agent.py",
        "ProcurementAgent",
    ),
    "procurement-support": (
        "agents/@aibast-agents-library/general_stacks/"
        "procurement_support_stack/procurement_support_agent.py",
        "ProcurementSupportAgent",
    ),
    "product-feedback-synthesizer": (
        "agents/@aibast-agents-library/software_dp_stacks/"
        "product_feedback_synthesizer_stack/product_feedback_synthesizer_agent.py",
        "ProductFeedbackSynthesizerAgent",
    ),
    "ask-hr": (
        "agents/@aibast-agents-library/human_resources_stacks/"
        "ask_hr_stack/ask_hr_agent.py",
        "AskHRAgent",
    ),
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_agent(slug, source, class_name):
    spec = importlib.util.spec_from_file_location(slug, ROOT / source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, getattr(module, class_name)()


def test_every_operation_has_a_passing_persona_language_case():
    for slug, (source, class_name) in SOLUTIONS.items():
        _module, agent = load_agent(slug, source, class_name)
        capture = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")
        assert capture["agent_files"] == [Path(source).stem]
        cases = capture["cases"]
        operations = agent.metadata["parameters"]["properties"]["operation"]["enum"]
        assert [case["operation"] for case in cases] == operations
        for case in cases:
            assert case["persona"]
            assert case["operation"] not in case["prompt"]
            output = agent.perform(**case["arguments"])
            for value in case["must_include"]:
                assert value.lower() in output.lower(), (slug, case["id"], value)


def test_packages_pin_approved_slides_and_match_source_operations():
    onepagers = read_json(ROOT / "state" / "onepager_content.json")["onepagers"]
    for slug, (source, class_name) in SOLUTIONS.items():
        _module, agent = load_agent(slug, source, class_name)
        package = ROOT / "solutions" / slug
        assert package.is_dir()
        assert (package / "README.md").is_file()
        promise_map = read_json(package / "evals" / "onepager-map.json")
        source_audit = read_json(package / "evals" / "source-audit.json")
        deployment = read_json(package / "deployment.json")
        operations = agent.metadata["parameters"]["properties"]["operation"]["enum"]
        assert promise_map["source_slide_sha256"] == onepagers[
            promise_map["onepager"]
        ]["source_sha256"]
        assert promise_map["source_audit"]["implemented_operations"] == operations
        assert source_audit["status"] == "audited-and-fixed"
        assert source_audit["approved_slide"]["sha256"] == promise_map[
            "source_slide_sha256"
        ]
        assert source_audit["findings"]
        assert source_audit["fixes"]
        assert deployment["source_url"].endswith(source)
        assert deployment["expected_tool"] == class_name
        assert deployment["copilot_studio"]["operations"] == operations
        assert deployment["copilot_studio"]["manual_skill_count"] == len(operations)
        assert deployment["copilot_studio"]["publish_requires_confirmation"] is True
        assert len(list((package / "manual" / "knowledge").glob("*.md"))) == 2
        skills = list((package / "manual" / "skills").glob("*/SKILL.md"))
        assert len(skills) == len(operations)
        assert all(path.read_text(encoding="utf-8").startswith("---\n") for path in skills)


def test_manual_knowledge_is_complete_and_reproduces_locked_evidence():
    source_evidence = {
        "ai-customer-assistant": [
            "INQ-4001",
            "INQ-4002",
            "INQ-4003",
            "INQ-4004",
            "KB-101",
            "KB-102",
            "KB-103",
            "KB-104",
            "2025-11-14T09:23:00Z",
            "Tier 2 Engineering",
            "4.3/5.0",
        ],
        "procurement-agent": [
            "PR-5001",
            "PR-5002",
            "PR-5003",
            "PR-5004",
            "VND-001",
            "VND-006",
            "IT-INFRA-2025",
            "$4,350,000",
            "-$60,000",
            "CEO + Board",
        ],
        "procurement-support": [
            "DISC-101",
            "DISC-102",
            "DISC-103",
            "MedSupply Cooperative",
            "Northstar Imaging",
            "CareTech Devices",
            "$12,000",
            "2026-10-15",
            "Clinical consumables",
        ],
        "product-feedback-synthesizer": [
            "FB-5001",
            "FB-5006",
            "FR-001",
            "FR-006",
            "2025-Q4",
            "2026-Q1",
            "$1,278,000",
            "5.2/10",
            "380.0",
            "candidate_for_review",
        ],
        "ask-hr": [
            "emp-1001",
            "emp-1002",
            "emp-1003",
            "Jordan Chen",
            "Michael Torres",
            "Sarah Williams",
            "Memorial Day",
            "Sep 14, 2026",
            "2025-09-14",
            "10.5 days",
        ],
    }
    placeholder_phrases = (
        "placeholder",
        "schema-only",
        "schema only",
        "summary-only",
        "representative sample",
        "see the source agent",
    )

    for slug in SOLUTIONS:
        knowledge = ROOT / "solutions" / slug / "manual" / "knowledge"
        files = sorted(knowledge.glob("*.md"))
        assert len(files) == 2
        records = next(path for path in files if "synthetic-records" in path.name)
        rules = next(path for path in files if "rules-and-guardrails" in path.name)
        records_text = records.read_text(encoding="utf-8")
        rules_text = rules.read_text(encoding="utf-8")
        combined = f"{records_text}\n{rules_text}"
        lowered = combined.lower()

        assert records.stat().st_size > 2500
        assert rules.stat().st_size > 2500
        assert len(records_text.splitlines()) >= 50
        assert len(rules_text.splitlines()) >= 45
        assert "complete synthetic records" in records_text.lower()
        assert "locked-case evidence contract" in records_text.lower()
        assert "fixed-snapshot authority" in rules_text.lower()
        assert "external-side-effect prohibition" in rules_text.lower()
        assert "evidence-first response contract" in rules_text.lower()
        assert re.search(r"do\s+not\s+browse", lowered)
        assert not any(phrase in lowered for phrase in placeholder_phrases)

        cases = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")["cases"]
        transcripts = {
            item["case_id"]: item
            for item in read_json(
                ROOT / "solutions" / slug / "evals" / "transcripts.json"
            )["transcripts"]
        }
        for case in cases:
            assert case["prompt"] in combined
            for value in case["must_include"]:
                assert value.lower() in lowered, (slug, case["id"], value)
                assert value.lower() in transcripts[case["id"]][
                    "agent_logs"
                ].lower()

        for value in source_evidence[slug]:
            assert value.lower() in lowered, (slug, value)


def test_customer_and_procurement_operations_are_read_only():
    _module, customer = load_agent(
        "ai-customer-assistant", *SOLUTIONS["ai-customer-assistant"]
    )
    for operation in customer.metadata["parameters"]["properties"]["operation"]["enum"]:
        output = customer.perform(operation=operation, inquiry_id="INQ-4003")
        assert "No customer message is sent" in output
        assert "no case is changed" in output
    default_escalation = customer.perform(operation="escalation_routing")
    assert "INQ-4003" in default_escalation
    assert "Tier 2 Engineering" in default_escalation
    assert "2 hours" in default_escalation
    assert "full brief before responding" in customer.metadata["description"]
    high_priority_escalation = customer.perform(
        operation="escalation_routing", inquiry_id="INQ-4001"
    )
    assert "2 hours" in high_priority_escalation

    for slug in ("procurement-agent", "procurement-support"):
        _module, agent = load_agent(slug, *SOLUTIONS[slug])
        for operation in agent.metadata["parameters"]["properties"]["operation"]["enum"]:
            output = agent.perform(operation=operation)
            assert "No purchase order is created" in output or (
                "No supplier is selected" in output
            )
    _module, procurement = load_agent(
        "procurement-agent", *SOLUTIONS["procurement-agent"]
    )
    assert "walk through the cloud-upgrade request" in procurement.metadata[
        "description"
    ]
    procurement_default = procurement.perform(operation="purchase_request")
    for value in ("PR-5001", "$125,000", "CFO"):
        assert value in procurement_default

    _module, discount_finder = load_agent(
        "procurement-support", *SOLUTIONS["procurement-support"]
    )
    assert "scan upcoming healthcare purchases" in discount_finder.metadata[
        "description"
    ]
    discount_default = discount_finder.perform(operation="savings_scan")
    for value in ("DISC-101", "DISC-102", "not realized savings"):
        assert value in discount_default


def test_product_feedback_never_commits_a_roadmap_or_external_work():
    module, agent = load_agent(
        "product-feedback-synthesizer",
        *SOLUTIONS["product-feedback-synthesizer"],
    )
    assert {item["status"] for item in module.FEATURE_REQUESTS.values()} <= {
        "under_review",
        "candidate_for_review",
        "evidence_under_review",
    }
    for operation in agent.metadata["parameters"]["properties"]["operation"]["enum"]:
        output = agent.perform(operation=operation)
        assert "No roadmap commitment" in output
        assert "ticket" in output


def test_hr_never_submits_or_infers_a_sensitive_decision():
    module, agent = load_agent("ask-hr", *SOLUTIONS["ask-hr"])
    assert not hasattr(module, "_PENDING_REQUESTS")
    preview = agent.perform(
        operation="submit_time_off",
        employee_name="Jordan Chen",
        start_date="Sep 14, 2026",
        end_date="Sep 18, 2026",
        days=5,
    )
    assert "Not Submitted" in preview
    assert "No notification was sent" in preview
    assert "Time Off Request Submitted" not in preview
    assert "manager will be notified automatically" not in preview
    assert "must use submit_time_off" in agent.metadata["description"]
    for operation in (
        "parental_leave",
        "health_insurance",
        "remote_work",
        "benefits_summary",
    ):
        output = agent.perform(operation=operation, employee_name="Jordan Chen")
        assert "does not determine eligibility" in output
        assert "infer sensitive employee circumstances" in output


def test_customer_and_hr_strict_captures_match_locked_cases():
    for slug, (_source, class_name) in {
        key: SOLUTIONS[key]
        for key in (
            "ai-customer-assistant",
            "procurement-agent",
            "procurement-support",
            "ask-hr",
        )
    }.items():
        source = SOLUTIONS[slug][0]
        capture = read_json(ROOT / "solutions" / slug / "evals" / "transcripts.json")
        case_path = ROOT / "tests" / "demo_cases" / f"{slug}.json"
        cases = read_json(case_path)["cases"]
        assert capture["strict_isolation"] is True
        assert capture["loaded_tools_after_capture"] == [class_name]
        assert capture["agent_sources"] == [
            {
                "path": source,
                "sha256": hashlib.sha256((ROOT / source).read_bytes()).hexdigest(),
            }
        ]
        assert capture["case_file_sha256"] == hashlib.sha256(
            case_path.read_bytes()
        ).hexdigest()
        transcripts = {item["case_id"]: item for item in capture["transcripts"]}
        assert set(transcripts) == {case["id"] for case in cases}
        for case in cases:
            transcript = transcripts[case["id"]]
            assert transcript["prompt"] == case["prompt"]
            assert transcript["passed"] is True
            assert transcript["expected_agent"] == class_name
            for value in case["must_include"]:
                assert value.lower() in transcript["agent_logs"].lower()


def test_rollout_fragment_is_hand_authored_qualitative_copy():
    fragment = read_json(FRAGMENT)
    expected = {
        f"@aibast-agents-library/{slug}" for slug in SOLUTIONS
    }
    assert fragment["schema"] == "aibast-rollout-fragment/1.0"
    assert set(fragment["solutions"]) == expected
    entry_keys = {
        "display_name",
        "sales_headline",
        "card_pitch",
        "why_try",
        "customer_challenge",
        "microsoft_ai_story",
        "business_value",
        "search_terms",
        "journey_stage",
        "blueprint_role",
        "sample_prompts",
        "architecture",
    }
    architecture_keys = {
        "business_flow",
        "capabilities",
        "easy_mode",
        "local_install_prompt",
        "copilot_studio_prompt",
        "required_connections",
        "manual_commands",
        "acceptance_checks",
        "hard_mode",
    }
    for name, entry in fragment["solutions"].items():
        assert set(entry) == entry_keys, name
        assert set(entry["architecture"]) == architecture_keys, name
        assert all(
            set(prompt) == {"label", "prompt", "demo_url"}
            for prompt in entry["sample_prompts"]
        ), name
        public_copy = " ".join(
            [
                entry["sales_headline"],
                entry["card_pitch"],
                entry["why_try"],
                entry["customer_challenge"],
                entry["microsoft_ai_story"],
                entry["blueprint_role"],
                *entry["business_value"],
            ]
        )
        assert "%" not in public_copy, name
        assert "$" not in public_copy, name
        assert not re.search(r"\b\d+(?:\.\d+)?x\b", public_copy), name
        assert entry["sample_prompts"]
        assert entry["architecture"]["capabilities"]
        assert entry["architecture"]["acceptance_checks"]
        assert "Stop before publish" in entry["architecture"]["copilot_studio_prompt"]
