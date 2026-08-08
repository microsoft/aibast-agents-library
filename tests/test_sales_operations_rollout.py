import importlib.util
import hashlib
import inspect
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ONEPAGERS = ROOT / "state" / "onepager_content.json"
LIBRARY = ROOT / "agents" / "@aibast-agents-library"
FRAGMENT = Path(
    "/Users/kodywildfeuer/.copilot/session-state/"
    "994e930b-0925-4d45-b127-e1be7576fff1/files/"
    "rollout-fragments/sales.json"
)

SOLUTIONS = {
    "@aibast-agents-library/deal-progression": {
        "slug": "deal-progression",
        "source": "agents/@aibast-agents-library/b2b_sales_stacks/deal_progression_stack/deal_progression_agent.py",
        "class": "DealProgressionAgent",
        "slot": 12,
        "onepager": "Deal Progression Agent one-pager.pptx",
        "agent_files": ["deal_progression_agent"],
    },
    "@aibast-agents-library/proposal-generation": {
        "slug": "proposal-generation",
        "source": "agents/@aibast-agents-library/b2b_sales_stacks/proposal_generation_stack/proposal_generation_agent.py",
        "class": "ProposalGenerationAgent",
        "slot": 13,
        "onepager": "Proposal Generation Agent one-pager.pptx",
        "agent_files": ["proposal_generation_agent"],
    },
    "@aibast-agents-library/account-intelligence": {
        "slug": "account-intelligence",
        "source": "agents/@aibast-agents-library/b2b_sales_stacks/account_intelligence_stack/account_intelligence_agent.py",
        "class": "AccountIntelligenceAgent",
        "slot": 19,
        "onepager": "Account Intelligence Agent one-pager.pptx",
        "agent_files": ["account_intelligence_agent"],
    },
    "@aibast-agents-library/sales-qualification": {
        "slug": "sales-qualification",
        "source": "agents/@aibast-agents-library/b2b_sales_stacks/sales_qualification_stack/sales_qualification_agent.py",
        "class": "SalesQualificationAgent",
        "slot": 21,
        "onepager": "21. Sales Qualification Agent one-pager.pptx",
        "agent_files": ["sales_qualification_agent"],
    },
    "@aibast-agents-library/win-loss-analysis": {
        "slug": "win-loss-analysis",
        "source": "agents/@aibast-agents-library/b2b_sales_stacks/win_loss_analysis_stack/win_loss_analysis_agent.py",
        "class": "WinLossAnalysisAgent",
        "slot": 22,
        "onepager": "22. Win Loss Analysis Agent one-pager.pptx",
        "agent_files": ["win_loss_analysis_agent"],
    },
    "@aibast-agents-library/license-renewal-expansion": {
        "slug": "license-renewal-expansion",
        "source": "agents/@aibast-agents-library/software_dp_stacks/license_renewal_expansion_stack/license_renewal_expansion_agent.py",
        "class": "LicenseRenewalExpansionAgent",
        "slot": 33,
        "onepager": "36. License Renewal and Expansion Agent one-pager.pptx",
        "agent_files": ["license_renewal_expansion_agent"],
    },
    "@aibast-agents-library/cross-selling": {
        "slug": "cross-selling",
        "source": "agents/@aibast-agents-library/general_stacks/cross_selling_opportunities_stack/cross_selling_agent.py",
        "class": "CrossSellingAgent",
        "slot": 25,
        "onepager": "28. Cross Selling Opportunities Agent one-pager.pptx",
        "agent_files": ["cross_selling_agent"],
    },
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_agent(config):
    module = load_agent_module(config)
    return getattr(module, config["class"])()


def load_agent_module(config):
    source = ROOT / config["source"]
    module_name = f"sales_rollout_{config['slug'].replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_source_value(value):
    if isinstance(value, dict):
        return {
            key: normalize_source_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [normalize_source_value(item) for item in value]
    if isinstance(value, set):
        return sorted(normalize_source_value(item) for item in value)
    return value


def case_document(config):
    return read_json(
        ROOT / "tests" / "demo_cases" / f"{config['slug']}.json"
    )


def test_locked_persona_cases_cover_every_operation_directly():
    total_cases = 0
    for name, config in SOLUTIONS.items():
        document = case_document(config)
        agent = load_agent(config)
        operations = agent.metadata["operations"]
        cases = document["cases"]
        total_cases += len(cases)
        assert document["agent"] == name
        assert document["slot"] == config["slot"]
        assert document["onepager"] == config["onepager"]
        assert document["agent_files"] == config["agent_files"]
        assert [case["operation"] for case in cases] == operations
        assert len({case["persona"] for case in cases}) >= 2
        assert agent.metadata["parameters"]["additionalProperties"] is False
        assert agent.metadata["parameters"]["properties"]["data_source"]["enum"] == [
            "synthetic"
        ]
        for case in cases:
            output = agent.perform(**case["arguments"])
            for marker in case["must_include"]:
                assert marker.lower() in output.lower(), (name, case["id"], marker)
            assert "synthetic" in output.lower()
            assert "source: [" not in output.lower()
            for unsafe_claim in [
                "task assignments completed",
                "monitoring activated:",
                "auto-update opportunity stage",
                "legal review: approved",
                "pricing approval: confirmed",
                "action plan activated",
                "email sequence starts automatically",
                "**incremental revenue:",
            ]:
                assert unsafe_claim not in output.lower(), (
                    name,
                    case["id"],
                    unsafe_claim,
                )
    assert total_cases == 38


def test_agents_reject_unsupported_sources_and_unknown_identifiers():
    for name, config in SOLUTIONS.items():
        agent = load_agent(config)
        operation = agent.metadata["operations"][0]
        output = agent.perform(operation=operation, data_source="crm")
        assert "must be `synthetic`" in output

    invalid_inputs = {
        "@aibast-agents-library/proposal-generation": {"rfp_name": "Unknown RFP"},
        "@aibast-agents-library/account-intelligence": {
            "account_name": "Unknown Account"
        },
        "@aibast-agents-library/license-renewal-expansion": {
            "license_id": "LIC-9999"
        },
        "@aibast-agents-library/cross-selling": {"customer_id": "CUST-999"},
    }
    for name, kwargs in invalid_inputs.items():
        agent = load_agent(SOLUTIONS[name])
        output = agent.perform(
            operation=agent.metadata["operations"][0],
            data_source="synthetic",
            **kwargs,
        )
        assert "unknown" in output.lower()


def test_approved_onepager_behaviors_are_visible_and_governed():
    checks = {
        "@aibast-agents-library/deal-progression": {
            "stalled_deals": ["Diagnosis", "Champion"],
            "action_plans": ["Planning Objective", "Suggested Resource"],
        },
        "@aibast-agents-library/proposal-generation": {
            "analyze_rfp": ["Requirements Analysis", "Existing Assets Found"],
            "compile_proposal": ["Required Human Review Before Delivery"],
        },
        "@aibast-agents-library/account-intelligence": {
            "stakeholder_map": ["Relationship Gaps", "Influence"],
            "value_messaging": ["Draft Meeting Talking Points"],
        },
        "@aibast-agents-library/sales-qualification": {
            "score_leads": ["Lead Qualification Summary", "Recommended Action"],
            "setup_tracking": ["Draft SLA Tracking Plan", "not activated"],
        },
        "@aibast-agents-library/win-loss-analysis": {
            "root_cause_analysis": ["Root Cause Analysis", "Buyer"],
            "revenue_impact": ["Synthetic Revenue Scenario Model", "not measured"],
        },
        "@aibast-agents-library/license-renewal-expansion": {
            "renewal_pipeline": ["Draft Renewal Preparation Checklist"],
            "expansion_opportunities": ["Draft Packaging Options"],
            "churn_risk": ["Synthetic Switching-Cost Review"],
        },
        "@aibast-agents-library/cross-selling": {
            "opportunity_scan": [
                "Synthetic Usage Signals",
                "Synthetic Buying Signals",
                "Budget timing assumption",
            ],
            "recommendation_engine": ["Draft Engagement Plan", "not sent"],
        },
    }
    arguments = {}
    for name, config in SOLUTIONS.items():
        for case in case_document(config)["cases"]:
            arguments[(name, case["operation"])] = case["arguments"]
    for name, operation_checks in checks.items():
        agent = load_agent(SOLUTIONS[name])
        for operation, markers in operation_checks.items():
            output = agent.perform(**arguments[(name, operation)])
            for marker in markers:
                assert marker.lower() in output.lower(), (name, operation, marker)


def test_solution_packages_match_onepager_evidence_and_manual_contract():
    onepagers = read_json(ONEPAGERS)["onepagers"]
    for name, config in SOLUTIONS.items():
        package = ROOT / "solutions" / config["slug"]
        assert package.parent == ROOT / "solutions"
        assert package.is_dir()
        deployment = read_json(package / "deployment.json")
        demo = read_json(package / "evals" / "demo-cases.json")
        promise_map = read_json(package / "evals" / "onepager-map.json")
        source = onepagers[promise_map["onepager"]]

        assert deployment["name"] == name
        assert deployment["source_path"] == config["source"]
        assert deployment["data_source"] == "synthetic"
        studio = deployment["copilot_studio"]
        assert studio["status"] == "package-ready-not-created"
        assert studio["publish"] is False
        assert studio["publish_requires_confirmation"] is True
        assert studio["external_actions"] == "not-configured"
        assert studio["minimum_pac_version"] == "2.9.3"
        assert promise_map["solution"] == name
        assert promise_map["source_slide_sha256"] == source["source_sha256"]
        assert demo["locked"] is True
        assert demo["canonical_capture_contract"] == (
            f"tests/demo_cases/{config['slug']}.json"
        )
        assert [case["operation"] for case in demo["cases"]] == deployment["operations"]
        assert [case["id"] for case in demo["cases"]] == [
            case["id"] for case in case_document(config)["cases"]
        ]
        assert deployment["manual_package"]["locked_demo_cases"] == (
            f"tests/demo_cases/{config['slug']}.json"
        )

        knowledge = list((package / "manual" / "knowledge").glob("*.md"))
        skills = list((package / "manual" / "skills").glob("*/SKILL.md"))
        assert len(knowledge) == 2
        assert len(skills) == len(deployment["operations"])
        assert deployment["manual_package"]["skill_count"] == len(skills)
        assert all(path.read_text(encoding="utf-8").startswith("---\n") for path in skills)
        assert all("Evidence boundary" in path.read_text(encoding="utf-8") for path in skills)


def test_per_solution_files_satisfy_capture_contract():
    assert not (ROOT / "tests" / "demo_cases" / "sales-operations.json").exists()
    for name, config in SOLUTIONS.items():
        document = case_document(config)
        assert set(document) >= {
            "solution",
            "slot",
            "agent",
            "onepager",
            "agent_files",
            "note",
            "cases",
            "assertion_principle",
        }
        assert document["agent"] == name
        assert document["onepager"] == config["onepager"]
        assert document["agent_files"] == config["agent_files"]
        for stem in document["agent_files"]:
            matches = list(LIBRARY.rglob(f"{stem}.py"))
            assert len(matches) == 1, (stem, matches)
        agent = load_agent(config)
        assert {case["operation"] for case in document["cases"]} == set(
            agent.metadata["operations"]
        )
        for case in document["cases"]:
            assert case["persona"]
            assert case["onepager_bullet"]
            assert case["prompt"]
            assert case["operation"] not in case["prompt"]
            assert case["arguments"]["operation"] == case["operation"]
            assert case["arguments"]["data_source"] == "synthetic"
            assert case["must_include"]
            assert case["must_not_include"]
            assert case["min_words"] >= 25
            assert case["expects_agent"] == config["class"]


def test_strict_captures_prove_corrected_sales_routing():
    checks = {
        "account-intelligence": (
            "AI-04",
            ["Draft Meeting Talking Points", "Objection Handling"],
        ),
        "cross-selling": (
            "CS-02",
            ["Product Affinity Matrix", "Response Assumption"],
        ),
        "deal-progression": (
            "DP-04",
            ["Pipeline Acceleration Strategy", "Synthetic Scenario"],
        ),
        "license-renewal-expansion": (
            "LRE-04",
            ["Synthetic Revenue Scenario", "Illustrative midpoint assumption"],
        ),
        "proposal-generation": (
            "PG-05",
            ["Proposal Package", "Required Human Review Before Delivery"],
        ),
        "win-loss-analysis": (
            "WL-06",
            ["Complete Summary", "Draft Next-Step Options"],
        ),
    }
    by_slug = {config["slug"]: (name, config) for name, config in SOLUTIONS.items()}
    for slug, (case_id, markers) in checks.items():
        name, config = by_slug[slug]
        artifact_path = ROOT / "solutions" / slug / "evals" / "transcripts.json"
        artifact = read_json(artifact_path)
        cases = case_document(config)["cases"]
        source = ROOT / config["source"]
        case_path = ROOT / "tests" / "demo_cases" / f"{slug}.json"

        assert artifact["solution"] == name
        assert artifact["strict_isolation"] is True
        assert artifact["loaded_tools_after_capture"] == [config["class"]]
        assert artifact["case_file"] == f"tests/demo_cases/{slug}.json"
        assert artifact["case_file_sha256"] == hashlib.sha256(
            case_path.read_bytes()
        ).hexdigest()
        assert artifact["agent_sources"] == [
            {
                "path": source.relative_to(ROOT).as_posix(),
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        ]
        assert [item["case_id"] for item in artifact["transcripts"]] == [
            case["id"] for case in cases
        ]
        assert all(item["passed"] is True for item in artifact["transcripts"])
        corrected = next(
            item for item in artifact["transcripts"] if item["case_id"] == case_id
        )
        for marker in [*markers, "Evidence boundary"]:
            assert marker in corrected["agent_logs"], (slug, case_id, marker)
        deployment = read_json(ROOT / "solutions" / slug / "deployment.json")
        assert deployment["manual_package"]["strict_capture_evidence"] == (
            "evals/transcripts.json"
        )


def test_account_intelligence_manual_knowledge_is_complete_not_placeholder():
    package = ROOT / "solutions" / "account-intelligence"
    records = (
        package
        / "manual"
        / "knowledge"
        / "aibast_account-intelligence-synthetic-records.md"
    ).read_text(encoding="utf-8")
    rules = (
        package
        / "manual"
        / "knowledge"
        / "aibast_account-intelligence-operating-rules.md"
    ).read_text(encoding="utf-8")

    assert len(records.splitlines()) >= 75
    assert len(rules.splitlines()) >= 150
    assert "Four fictional accounts contain firmographics" not in records
    assert "Do not browse, enrich, substitute, or invent records." in records
    assert "Never browse or use external CRM" in rules
    assert "No CRM record, task, meeting, message, proposal, forecast, price, approval" in records
    for exact_source_value in [
        "acc-001",
        "Acme Corporation",
        "$2,800,000,000",
        "12,400",
        "Chicago, IL",
        "$1,200,000 per year",
        "$2,400,000 expansion",
        "Platform Core; Analytics Module",
        "CEO mentioned digital transformation in Q3 earnings call",
        "New CTO Sarah Chen hired from AWS",
        "Competitor RFP issued for operations platform",
        "Sarah Chen",
        "James Miller",
        "Lisa Park",
        "David Wong",
        "Rachel Torres",
        "Kevin Park",
        "Maria Lopez",
        "Tom Bradley",
        "CompetitorA",
        "CompetitorB",
        "Existing integration with customer ERP (3-week head start)",
        "Champion relationship established",
        "Superior customer references in target industry",
    ]:
        assert exact_source_value in records

    for computed_evidence in [
        "Account Health Score: 73/100",
        "Engagement: 100% (30 touchpoints last 30 days)",
        "Product adoption: 66% feature utilization",
        "Support sentiment: 3.8/5 CSAT",
        "Renewal risk: 5%",
        "Draft Meeting Talking Points",
        "Objection Handling",
        "$4,200,000 projected savings over 3 years",
        "Synthetic Win-Probability Indicator: 61%",
        "Risks: 3 identified, 2 critical",
        "Sarah Chen, Maria Lopez, and Tom Bradley",
        "Pre-Meeting Checklist",
    ]:
        assert computed_evidence in rules

    cases = case_document(SOLUTIONS["@aibast-agents-library/account-intelligence"])[
        "cases"
    ]
    for case in cases:
        skill = (
            package
            / "manual"
            / "skills"
            / case["operation"].replace("_", "-")
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        assert case["prompt"] in skill
        assert "do not browse, enrich, infer, invent, or use external data" in skill
        assert "authorized human review" in skill
        assert "Do not send outreach, update CRM, create tasks" in skill
        packaged_evidence = "\n".join([records, rules, skill])
        for marker in case["must_include"]:
            assert marker in packaged_evidence, (case["id"], marker)


def test_other_sales_manual_knowledge_serializes_source_and_locked_evidence():
    names = [
        "@aibast-agents-library/deal-progression",
        "@aibast-agents-library/proposal-generation",
        "@aibast-agents-library/sales-qualification",
        "@aibast-agents-library/win-loss-analysis",
        "@aibast-agents-library/license-renewal-expansion",
        "@aibast-agents-library/cross-selling",
    ]
    for name in names:
        config = SOLUTIONS[name]
        package = ROOT / "solutions" / config["slug"]
        knowledge = package / "manual" / "knowledge"
        records_path = next(knowledge.glob("*-synthetic-records.md"))
        rules_path = next(knowledge.glob("*-operating-rules.md"))
        records = records_path.read_text(encoding="utf-8")
        rules = rules_path.read_text(encoding="utf-8")
        module = load_agent_module(config)
        agent = getattr(module, config["class"])()
        cases = case_document(config)["cases"]
        transcripts = {
            item["case_id"]: item
            for item in read_json(package / "evals" / "transcripts.json")[
                "transcripts"
            ]
        }

        assert len(records.splitlines()) >= 150, config["slug"]
        assert len(rules.splitlines()) >= 200, config["slug"]
        assert "complete serialization of the deterministic datasets" in records
        assert "Do not browse, enrich, substitute, infer, or invent records" in records
        assert "No outreach may be sent" in records
        assert "Never browse or use external CRM" in rules
        assert "Require authorized human review" in rules

        datasets = {
            key: normalize_source_value(value)
            for key, value in vars(module).items()
            if (
                key.isupper()
                or (key.startswith("_") and key[1:].isupper())
            )
            and isinstance(value, (dict, list, tuple, set))
        }
        assert datasets
        for dataset_name, value in datasets.items():
            assert f"## Exact dataset `{dataset_name}`" in records
            serialized = json.dumps(
                value,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            assert serialized in records, (config["slug"], dataset_name)

        helpers = {
            helper_name: helper
            for helper_name, helper in vars(module).items()
            if helper_name.startswith("_")
            and not helper_name.startswith("__")
            and inspect.isfunction(helper)
            and helper.__module__ == module.__name__
        }
        assert helpers
        for helper_name, helper in helpers.items():
            assert f"### `{helper_name}`" in rules
            assert inspect.getsource(helper).strip() in rules

        for case in cases:
            output = agent.perform(**case["arguments"])
            transcript = transcripts[case["id"]]
            skill = (
                package
                / "manual"
                / "skills"
                / case["operation"].replace("_", "-")
                / "SKILL.md"
            ).read_text(encoding="utf-8")
            assert case["prompt"] in skill
            assert case["prompt"] in rules
            comparable_output = output
            comparable_logs = transcript["agent_logs"]
            comparable_rules = rules
            if case["id"] == "DP-04":
                _, _, stalled = module._classify_deals()
                tied_rows = {}
                for owner, deals in module._deals_by_owner(stalled).items():
                    counts = {
                        blocker: sum(
                            deal["blocker"] == blocker for deal in deals
                        )
                        for blocker in {
                            deal["blocker"] for deal in deals
                        }
                    }
                    top_count = max(counts.values())
                    if sum(count == top_count for count in counts.values()) > 1:
                        tied_rows[owner] = len(deals)

                def normalize_tied_action_rows(text):
                    normalized = []
                    for line in text.splitlines():
                        for owner, deal_count in tied_rows.items():
                            prefix = f"| {owner} | {deal_count} | "
                            if line.startswith(prefix):
                                line = f"{prefix}[tied blocker] |"
                                break
                        normalized.append(line)
                    return "\n".join(normalized)

                comparable_output = normalize_tied_action_rows(
                    comparable_output
                )
                comparable_logs = normalize_tied_action_rows(comparable_logs)
                comparable_rules = normalize_tied_action_rows(comparable_rules)
            assert comparable_output in comparable_logs
            assert comparable_output in comparable_rules
            assert "do not browse, enrich, infer, invent, or use external data" in skill
            assert "authorized human review" in skill
            assert "Do not send outreach, update CRM, assign owners" in skill
            for marker in dict.fromkeys(case["must_include"]):
                assert marker.lower() in output.lower(), (
                    config["slug"],
                    case["id"],
                    marker,
                )
                assert marker in skill
                assert marker in rules


def test_fragment_uses_full_catalog_entry_and_capture_url_shape():
    fragment = read_json(FRAGMENT)
    assert fragment["schema"] == "aibast-solution-copy/1.0"
    assert set(fragment["solutions"]) == set(SOLUTIONS)
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
    for name, config in SOLUTIONS.items():
        entry = fragment["solutions"][name]
        assert set(entry) == entry_keys
        assert "business" not in entry
        assert len(entry["business_value"]) == 3
        assert entry["search_terms"]
        assert set(entry["architecture"]) == architecture_keys
        assert entry["architecture"]["business_flow"]
        assert {
            capability["operation"]
            for capability in entry["architecture"]["capabilities"]
        } == set(load_agent(config).metadata["operations"])
        assert entry["architecture"]["required_connections"]
        assert entry["architecture"]["acceptance_checks"]
        assert entry["architecture"]["hard_mode"]
        assert "stop before publish" in entry["architecture"][
            "copilot_studio_prompt"
        ].lower()
        prompts = entry["sample_prompts"]
        assert len(prompts) == len(case_document(config)["cases"])
        for prompt, case in zip(prompts, case_document(config)["cases"]):
            assert set(prompt) == {"label", "prompt", "demo_url"}
            assert prompt["prompt"] == case["prompt"]
            scenario = (
                f"{config['slug']}-{case['operation'].replace('_', '-')}"
            )
            assert prompt["demo_url"].endswith(f"?scenario={scenario}")


def test_public_package_copy_keeps_business_claims_qualitative():
    forbidden = [
        "customer outcome achieved",
        "revenue increased",
        "conversion increased",
        "proposal was sent",
        "crm record updated",
        "pricing approved",
    ]
    for config in SOLUTIONS.values():
        package = ROOT / "solutions" / config["slug"]
        public_copy = (package / "README.md").read_text(encoding="utf-8").lower()
        public_copy += (package / "deployment.json").read_text(encoding="utf-8").lower()
        assert all(claim not in public_copy for claim in forbidden)
        assert "synthetic" in public_copy
        assert "human" in public_copy
