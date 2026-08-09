import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONFIG = {
    "contract-risk-review": {
        "source": ROOT / "agents/@aibast-agents-library/professional_services_stacks/contract_risk_review_stack/contract_risk_review_agent.py",
        "class": "ContractRiskReviewAgent",
        "onepager": "Contract Risk Review Agent one-pager.pptx",
        "skills": 4,
    },
    "time-entry-billing": {
        "source": ROOT / "agents/@aibast-agents-library/professional_services_stacks/time_entry_billing_stack/time_entry_billing_agent.py",
        "class": "TimeEntryBillingAgent",
        "onepager": "Time and Entry Billing Agent one-pager.pptx",
        "skills": 5,
    },
    "resource-utilization": {
        "source": ROOT / "agents/@aibast-agents-library/professional_services_stacks/resource_utilization_stack/resource_utilization_agent.py",
        "class": "ResourceUtilizationAgent",
        "onepager": "Resource Utilization Agent one-pager.pptx",
        "skills": 5,
    },
    "client-health-score": {
        "source": ROOT / "agents/@aibast-agents-library/professional_services_stacks/client_health_score_stack/client_health_score_agent.py",
        "class": "ClientHealthScoreAgent",
        "onepager": "Client Health Score Agent one-pager.pptx",
        "skills": 5,
    },
}

SOURCE_CONSTANTS = {
    "contract-risk-review": [
        "CONTRACTS",
        "CLAUSES",
        "COMPLIANCE_REQUIREMENTS",
        "RENEWAL_CALENDAR",
    ],
    "time-entry-billing": [
        "TIME_ENTRIES",
        "BILLING_RATES",
        "PROJECT_BUDGETS",
        "INVOICE_HISTORY",
        "DISPUTES",
    ],
    "resource-utilization": [
        "CONSULTANTS",
        "PROJECT_PIPELINE",
        "UTILIZATION_TARGETS",
        "BENCH_COST_PER_MONTH",
        "WORKFORCE_PATHS",
    ],
    "client-health-score": ["CLIENTS", "STAKEHOLDERS"],
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_agent_module(slug, config):
    spec = importlib.util.spec_from_file_location(f"professional_services_{slug}", config["source"])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_agent(slug, config):
    module = load_agent_module(slug, config)
    return getattr(module, config["class"])()


def iter_leaf_values(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from iter_leaf_values(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from iter_leaf_values(child)
    else:
        yield value


def numeric_evidence_forms(value):
    forms = {str(value), f"{value:,}"}
    if isinstance(value, float):
        forms.add(f"{value:.1f}")
    forms.update({f"${form}" for form in list(forms)})
    if 0 <= value <= 1:
        forms.add(f"{value * 100:g}%")
    else:
        forms.add(f"{value:g}%")
    return forms


def test_locked_cases_cover_every_routable_operation():
    for slug, config in CONFIG.items():
        agent = load_agent(slug, config)
        case_doc = read_json(ROOT / "tests/demo_cases" / f"{slug}.json")
        cases = case_doc["cases"]
        operations = agent.metadata["parameters"]["properties"]["operation"]["enum"]
        assert case_doc["agent_files"] == [config["source"].stem]
        assert agent.metadata["parameters"]["required"] == ["operation"]
        assert agent.metadata["operations"] == operations
        assert [case["operation"] for case in cases] == operations
        assert len({case["persona"] for case in cases}) >= 2

        for case in cases:
            output = agent.perform(operation=case["operation"])
            for value in case["must_include"]:
                assert value.lower() in output.lower(), (slug, case["id"], value)
            for value in case["must_not_include"]:
                assert value.lower() not in output.lower(), (slug, case["id"], value)


def test_contract_metadata_routes_persona_language_without_operation_terms():
    agent = load_agent("contract-risk-review", CONFIG["contract-risk-review"])
    tool_description = agent.metadata["description"].lower()
    operation_description = agent.metadata["parameters"]["properties"]["operation"][
        "description"
    ].lower()
    for phrase in [
        "which agreements need",
        "liability-cap",
        "ip ownership",
        "internal policy",
        "negotiation positions",
    ]:
        assert phrase in tool_description
    for phrase in [
        "counsel first",
        "payment terms",
        "incomplete file",
        "fallbacks",
    ]:
        assert phrase in operation_description


def test_contract_strict_isolation_capture_covers_every_persona_case():
    artifact = read_json(ROOT / "solutions/contract-risk-review/evals/transcripts.json")
    cases = read_json(ROOT / "tests/demo_cases/contract-risk-review.json")["cases"]
    captured = {item["case_id"]: item for item in artifact["transcripts"]}
    assert artifact["strict_isolation"] is True
    assert artifact["loaded_tools_after_capture"] == ["ContractRiskReviewAgent"]
    assert set(captured) == {case["id"] for case in cases}
    for case in cases:
        transcript = captured[case["id"]]
        assert transcript["passed"] is True
        assert transcript["prompt"] == case["prompt"]
        assert "ContractRiskReviewAgent" in transcript["agent_logs"]
        for value in case["must_include"]:
            assert value.lower() in transcript["agent_logs"].lower()


def test_client_health_metadata_routes_exact_persona_language():
    agent = load_agent("client-health-score", CONFIG["client-health-score"])
    tool_description = agent.metadata["description"].lower()
    operation_description = agent.metadata["parameters"]["properties"]["operation"][
        "description"
    ].lower()
    for phrase in [
        "engagement signals are weakening",
        "executive contact",
        "escalations",
        "satisfaction trends are moving the wrong way",
        "stakeholder map",
    ]:
        assert phrase in tool_description
    for phrase in [
        "healthy, at risk, or critical",
        "declining billing trend",
        "accounts needing intervention now",
        "executive engagement plans",
    ]:
        assert phrase in operation_description


def test_client_health_strict_isolation_capture_covers_every_persona_case():
    artifact = read_json(ROOT / "solutions/client-health-score/evals/transcripts.json")
    cases = read_json(ROOT / "tests/demo_cases/client-health-score.json")["cases"]
    captured = {item["case_id"]: item for item in artifact["transcripts"]}
    assert artifact["strict_isolation"] is True
    assert artifact["loaded_tools_after_capture"] == ["ClientHealthScoreAgent"]
    assert set(captured) == {case["id"] for case in cases}
    for case in cases:
        transcript = captured[case["id"]]
        assert transcript["passed"] is True
        assert transcript["prompt"] == case["prompt"]
        assert "ClientHealthScoreAgent" in transcript["agent_logs"]
        for value in case["must_include"]:
            assert value.lower() in transcript["agent_logs"].lower()


def test_packages_map_approved_evidence_and_manual_assets():
    onepagers = read_json(ROOT / "state/onepager_content.json")["onepagers"]
    for slug, config in CONFIG.items():
        package = ROOT / "solutions" / slug
        mapping = read_json(package / "evals/onepager-map.json")
        deployment = read_json(package / "deployment.json")
        cases = read_json(ROOT / "tests/demo_cases" / f"{slug}.json")["cases"]
        operations = [case["operation"] for case in cases]

        assert mapping["onepager"] == config["onepager"]
        assert mapping["source_slide_sha256"] == onepagers[config["onepager"]]["source_sha256"]
        assert {case_id for promise in mapping["promises"] for case_id in promise["demo_cases"]} == {
            case["id"] for case in cases
        }
        assert deployment["copilot_studio"]["operations"] == operations
        assert deployment["copilot_studio"]["manual_skill_count"] == config["skills"]
        assert len(list((package / "manual/knowledge").glob("*.md"))) == 2
        skills = list((package / "manual/skills").glob("*/SKILL.md"))
        assert len(skills) == config["skills"]
        assert all(skill.read_text(encoding="utf-8").startswith("---\n") for skill in skills)


def test_manual_knowledge_is_complete_not_placeholder_only():
    prohibited = ["todo", "tbd", "placeholder", "schema-only", "coming soon"]
    for slug in CONFIG:
        files = sorted((ROOT / "solutions" / slug / "manual/knowledge").glob("*.md"))
        assert len(files) == 2
        for path in files:
            text = path.read_text(encoding="utf-8")
            assert len(text) >= 2500, (slug, path.name, len(text))
            assert text.count("\n## ") >= 3, (slug, path.name)
            assert text.count("|---") >= 2, (slug, path.name)
            lowered = text.lower()
            assert not any(term in lowered for term in prohibited), (slug, path.name)


def test_packaged_knowledge_contains_every_source_record_value():
    for slug, config in CONFIG.items():
        module = load_agent_module(slug, config)
        knowledge = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / "solutions" / slug / "manual/knowledge").glob("*.md"))
        )
        lowered = knowledge.lower()
        normalized = " ".join(lowered.split())
        for constant in SOURCE_CONSTANTS[slug]:
            for value in iter_leaf_values(getattr(module, constant)):
                if value is None:
                    assert "none" in lowered
                elif isinstance(value, bool):
                    continue
                elif isinstance(value, str):
                    assert " ".join(value.lower().split()) in normalized, (
                        slug,
                        constant,
                        value,
                    )
                elif isinstance(value, (int, float)):
                    assert any(form in knowledge for form in numeric_evidence_forms(value)), (
                        slug,
                        constant,
                        value,
                    )


def test_every_locked_case_has_factual_evidence_in_manual_knowledge():
    for slug in CONFIG:
        knowledge = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / "solutions" / slug / "manual/knowledge").glob("*.md"))
        ).lower()
        cases = read_json(ROOT / "tests/demo_cases" / f"{slug}.json")["cases"]
        transcript = read_json(ROOT / "solutions" / slug / "evals/transcripts.json")
        captured = {item["case_id"]: item for item in transcript["transcripts"]}
        assert set(captured) == {case["id"] for case in cases}
        for case in cases:
            assert captured[case["id"]]["passed"] is True
            for fact in case["must_include"]:
                assert fact.lower() in knowledge, (slug, case["id"], fact)


def test_time_entry_easy_mode_is_literal_github_copilot_chat():
    package = ROOT / "solutions" / "time-entry-billing"
    personless = (package / "EASY-MODE-PERSONLESS.md").read_text(
        encoding="utf-8"
    )
    prompts = (package / "EASY-MODE-COPILOT-CHAT.md").read_text(
        encoding="utf-8"
    )
    brainstem_skill = (
        ROOT / "skills/aibast-easy-mode-brainstem/SKILL.md"
    ).read_text(
        encoding="utf-8"
    )
    copilot_skill = (
        ROOT / "skills/aibast-easy-mode-copilot/SKILL.md"
    ).read_text(
        encoding="utf-8"
    )
    quest = (package / "quest.html").read_text(encoding="utf-8")
    visual_audit = (package / "VISUAL-EVIDENCE-AUDIT.md").read_text(
        encoding="utf-8"
    )
    manual_tutorial = (package / "manual-tutorial.html").read_text(
        encoding="utf-8"
    )
    cases = read_json(ROOT / "tests/demo_cases/time-entry-billing.json")[
        "cases"
    ]

    for marker in (
        "drag `SKILL.md` into the",
        "Give me Time Entry and Billing using Easy Mode and test it for me.",
        "Deploy it into Copilot Studio for me.",
        "AIBASTWorkshopAgent",
        "Generic workshop engine",
        "status: complete",
        "published: false",
    ):
        assert marker in personless
    for marker in (
        "Copilot-only Easy mode comparison",
        "Attach the Copilot-only skill",
        "drag `SKILL.md` into the",
        "Give me Time Entry and Billing using Easy Mode and test it for me.",
        "Deploy it into Copilot Studio for me.",
    ):
        assert marker in prompts
    for marker in (
        "personal, on-device training AI",
        "http://localhost:7071/health",
        "@aibast-agents-library/workshop",
        "Never ask the user",
        "Never publish",
    ):
        assert marker in brainstem_skill
    for marker in (
        "AIBAST Easy Mode — GitHub Copilot",
        "tests/demo_cases/<slug>.json",
        "must_include",
        "must_not_include",
        "one immutable commit SHA",
        "Never ask the user",
        "Never publish",
    ):
        assert marker in copilot_skill
    assert "brainstem" not in copilot_skill.lower()
    assert len(cases) == 5

    assert "GitHub Copilot + Brainstem" in quest
    assert "GitHub Copilot only" in quest
    assert "Personless harness" in quest
    assert "Skeptic comparison" in quest
    assert "aibast:workshop-engine" in quest
    assert "data-easy-lane-button" not in quest
    assert "Workshop settings" in quest
    assert quest.count("data-copy-target=") == 9
    assert "Download Brainstem SKILL.md" in quest
    assert "Download Copilot-only SKILL.md" in quest
    assert quest.count('download="SKILL.md"') == 2
    assert "Give me Time Entry and Billing using Easy Mode and test it for me." in quest
    assert "using Easy Mode without Brainstem" not in quest
    assert "Deploy it into Copilot Studio for me." in quest
    assert "Compare and contrast while you build" not in quest
    assert "What you will learn" in quest
    assert "Before you begin" in quest
    assert "Confirm the Draft in Copilot Studio Preview" in quest
    assert "Open the Copilot Studio Draft" in quest
    assert "Know what “done” looks like" in quest
    assert "5/5 locked cases passed" in quest
    assert "Draft · published false" in quest
    assert "Final expected verdict" in quest
    assert "Troubleshooting" in quest
    assert "Evidence report" in quest
    assert "Reshoot required" not in quest
    assert "No approved visual checkpoint" not in quest
    for case in cases:
        assert case["id"] in quest
        assert case["prompt"] in quest
        for value in case["must_include"]:
            assert value in quest
        for value in case["must_not_include"]:
            assert value in quest
    assert "Raw resources" not in quest
    assert 'src="manual-tutorial.html?embedded=1"' in quest
    assert ">Open the manual tutorial<" not in quest
    assert manual_tutorial.count(
        'data-copy-target="hard-copy-'
    ) == 7
    assert "Copy agent name" in manual_tutorial
    assert "Copy instructions" in manual_tutorial
    assert manual_tutorial.count("Copy Preview prompt") == 5
    assert "Time Entry and Billing Manual" in manual_tutorial
    for case in cases:
        assert case["prompt"] in manual_tutorial
    for marker in (
        "**Needs remediation.**",
        "| Pass | 4 |",
        "| Partial | 15 |",
        "| Fail | 7 |",
        "Nine Hard-mode screenshots are byte-for-byte identical",
        "grounding files are not present",
        "All 26 source screenshots are low-resolution legacy captures",
        "2560×1440",
        "use AI upscaling as a substitute",
        "Do not present the current Hard-mode run as proven end to end",
    ):
        assert marker in visual_audit


def test_contract_screen_never_passes_missing_evidence():
    agent = load_agent("contract-risk-review", CONFIG["contract-risk-review"])
    output = agent.perform(operation="compliance_check")
    assert "CTR-5002 -- Meridian Healthcare -- **REVIEW REQUIRED**" in output
    assert "CTR-5004 -- Orion Defense Systems -- **REVIEW REQUIRED**" in output
    assert "CTR-5002 -- Meridian Healthcare -- **PASS**" not in output


def test_invoice_package_excludes_fixed_fee_and_unapproved_time():
    agent = load_agent("time-entry-billing", CONFIG["time-entry-billing"])
    output = agent.perform(operation="invoice_preparation")
    assert "Fixed-fee hold" in output
    assert "Pinnacle Energy ERP | Pinnacle Energy" not in output
    assert "TE-9004" not in output
    assert "TE-9011" not in output
    assert "no invoice was generated, posted, or sent" in output


def test_staffing_projection_counts_unique_people_and_is_approval_gated():
    agent = load_agent("resource-utilization", CONFIG["resource-utilization"])
    output = agent.perform(operation="staffing_recommendation")
    assert "Robert Garcia" in output
    assert "no assignment was made" in output
    assert "Projected after deployment: **69.6%**" in output


def test_client_retention_plan_has_stakeholders_and_no_side_effects():
    agent = load_agent("client-health-score", CONFIG["client-health-score"])
    output = agent.perform(operation="retention_plan")
    for value in ["Morgan Lee", "Jordan Patel", "Taylor Brooks", "Approval gate"]:
        assert value in output
    assert "no meeting, message, concession, renewal, or CRM update has been created" in output
