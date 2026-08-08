import hashlib
import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents" / "@aibast-agents-library"
OPERATIONS = {
    "asset-maintenance-forecast": (
        AGENTS / "energy_stacks/asset_maintenance_forecast_stack/asset_maintenance_forecast_agent.py",
        "AssetMaintenanceForecastAgent",
    ),
    "permit-license-management": (
        AGENTS / "energy_stacks/permit_license_management_stack/permit_license_management_agent.py",
        "PermitLicenseManagementAgent",
    ),
    "energy-regulatory-reporting": (
        AGENTS / "energy_stacks/regulatory_reporting_stack/regulatory_reporting_agent.py",
        "RegulatoryReportingAgent",
    ),
    "emission-tracking": (
        AGENTS / "energy_stacks/emission_tracking_stack/emission_tracking_agent.py",
        "EmissionTrackingAgent",
    ),
    "field-service-dispatch": (
        AGENTS / "energy_stacks/field_service_dispatch_stack/field_service_dispatch_agent.py",
        "FieldServiceDispatchAgent",
    ),
    "utility-billing-assistance": (
        AGENTS / "slg_government_stacks/utility_billing_assistance_stack/utility_billing_assistance_agent.py",
        "UtilityBillingAssistanceAgent",
    ),
    "supply-chain-disruption-alert": (
        AGENTS / "retail_cpg_stacks/supply_chain_disruption_alert_stack/supply_chain_disruption_alert_agent.py",
        "SupplyChainDisruptionAlertAgent",
    ),
}

KNOWLEDGE_CONSTANTS = {
    "asset-maintenance-forecast": ["ASSETS", "BUDGET_RATES"],
    "permit-license-management": [
        "PERMITS",
        "APPLICATIONS",
        "REGULATORY_REQUIREMENTS",
    ],
    "energy-regulatory-reporting": [
        "REGULATORY_REPORTS",
        "DATA_VALIDATION_RULES",
        "AUDIT_FINDINGS",
    ],
    "emission-tracking": ["FACILITIES", "CARBON_OFFSETS", "REGULATIONS"],
    "field-service-dispatch": [
        "TECHNICIANS",
        "SERVICE_REQUESTS",
        "GEOGRAPHIC_ZONES",
    ],
    "utility-billing-assistance": [
        "UTILITY_ACCOUNTS",
        "USAGE_HISTORY",
        "RATE_STRUCTURES",
        "ASSISTANCE_PROGRAMS",
        "LEAK_ADJUSTMENT_POLICY",
    ],
    "supply-chain-disruption-alert": [
        "SUPPLY_ROUTES",
        "DISRUPTION_EVENTS",
        "RISK_SCORES",
        "MITIGATION_PLAYBOOKS",
        "ALTERNATIVE_SUPPLIERS",
    ],
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def extract_json_block(document, heading):
    match = re.search(
        rf"^## {re.escape(heading)}\n\n(?:>.*\n\n)?```json\n(.*?)\n```$",
        document,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match, heading
    return json.loads(match.group(1))


def load_agent(slug):
    source, class_name = OPERATIONS[slug]
    spec = importlib.util.spec_from_file_location(f"energy_category_{slug}", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, getattr(module, class_name)()


def test_persona_cases_route_directly_and_preserve_safety_boundaries():
    for slug in OPERATIONS:
        module, agent = load_agent(slug)
        cases = read_json(ROOT / "tests/demo_cases" / f"{slug}.json")["cases"]
        expected_operations = agent.metadata["parameters"]["properties"]["operation"]["enum"]
        assert [case["operation"] for case in cases] == expected_operations
        assert len({case["persona"] for case in cases}) == len(expected_operations)
        assert "future authenticated" in module.__manifest__["description"]
        for case in cases:
            output = agent.perform(**case["kwargs"])
            for value in case["must_include"]:
                assert value.lower() in output.lower(), (slug, case["operation"], value)


def test_each_operation_has_a_complete_manual_package():
    for slug, (source, _) in OPERATIONS.items():
        package = ROOT / "solutions" / slug
        deployment = read_json(package / "deployment.json")
        mapping = read_json(package / "evals/onepager-map.json")
        audit = read_json(package / "evals/source-audit.json")
        catalog = read_json(package / "catalog-entry.json")
        operations = deployment["copilot_studio"]["operations"]

        assert deployment["source_path"] == source.relative_to(ROOT).as_posix()
        assert deployment["write_controls"]["local_demo_performs_writes"] is False
        assert deployment["write_controls"]["explicit_human_approval_required"] is True
        assert audit["routing"]["status"] == "fixed"
        assert audit["schema"] == "aibast-source-audit/1.0"
        assert audit["interface_schema"]["status"] == "fixed"
        assert audit["behavior"]["status"] == "fixed"
        assert audit["safety"]["status"] == "fixed"
        assert [promise["operations"][0] for promise in mapping["promises"]] == operations
        assert all(len(promise["demo_cases"]) == 1 for promise in mapping["promises"])
        assert len(list((package / "manual/knowledge").glob("*.md"))) == 2
        skills = list((package / "manual/skills").glob("*/SKILL.md"))
        assert len(skills) == len(operations)
        assert all(path.read_text(encoding="utf-8").startswith("---\n") for path in skills)
        assert (package / "README.md").exists()
        assert (package / "architecture.md").exists()
        assert (package / "manual/GLOBAL-INSTRUCTIONS.md").exists()

        source_package = source.parent
        for duplicate in [
            "README.md",
            "architecture.md",
            "catalog-entry.json",
            "deployment.json",
            "evals",
            "manual",
        ]:
            assert not (source_package / duplicate).exists()

        qualitative = " ".join(
            str(catalog[key])
            for key in [
                "sales_headline",
                "card_pitch",
                "customer_challenge",
                "business_value",
                "why_try",
            ]
        )
        assert "%" not in qualitative


def test_energy_suite_remains_four_distinct_advertised_modules():
    suite_slugs = [
        "asset-maintenance-forecast",
        "permit-license-management",
        "energy-regulatory-reporting",
        "emission-tracking",
    ]
    expected_displays = {
        "Asset Maintenance Forecast Agent",
        "Permit Management Agent",
        "Regulatory Reporting Agent",
        "Emissions Tracking Agent",
    }
    displays = set()
    names = set()
    for slug in suite_slugs:
        package = ROOT / "solutions" / slug
        mapping = read_json(package / "evals/onepager-map.json")
        catalog = read_json(package / "catalog-entry.json")
        assert mapping["onepager"] == "Energy Operations Agent Suite one-pager (2).pptx"
        assert mapping["preserves_distinct_module"] is True
        displays.add(catalog["display_name"])
        names.add(catalog["name"])
    assert displays == expected_displays
    assert len(names) == 4
    assert all("grid-outage-response" not in name for name in names)


def test_unknown_identifiers_do_not_fall_back_to_unrelated_records():
    checks = [
        ("asset-maintenance-forecast", {"operation": "asset_health", "asset_id": "UNKNOWN"}, "Substation"),
        ("utility-billing-assistance", {"operation": "payment_plan", "account_id": "UNKNOWN"}, "Thompson"),
        ("supply-chain-disruption-alert", {"operation": "risk_assessment", "route_id": "UNKNOWN"}, "Asia-Pacific"),
    ]
    for slug, kwargs, forbidden in checks:
        _, agent = load_agent(slug)
        output = agent.perform(**kwargs)
        assert forbidden not in output


def test_cases_pin_exact_agent_file_stems():
    for slug, (source, _) in OPERATIONS.items():
        cases = read_json(ROOT / "tests/demo_cases" / f"{slug}.json")
        assert cases["agent_files"] == [source.stem]


def test_rollout_fragment_contains_full_catalog_entries():
    fragment = read_json(
        Path(
            "/Users/kodywildfeuer/.copilot/session-state/"
            "994e930b-0925-4d45-b127-e1be7576fff1/files/"
            "rollout-fragments/energy.json"
        )
    )
    assert set(fragment) == {"solutions"}
    expected_names = {
        read_json(ROOT / "tests/demo_cases" / f"{slug}.json")["agent"]
        for slug in OPERATIONS
    }
    assert set(fragment["solutions"]) == expected_names
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
    for slug in OPERATIONS:
        cases = read_json(ROOT / "tests/demo_cases" / f"{slug}.json")
        entry = fragment["solutions"][cases["agent"]]
        assert set(entry) == entry_keys
        assert set(entry["architecture"]) == architecture_keys
        assert [item["prompt"] for item in entry["sample_prompts"]] == [
            case["prompt"] for case in cases["cases"]
        ]
        assert [item["operation"] for item in entry["architecture"]["capabilities"]] == [
            case["operation"] for case in cases["cases"]
        ]


def test_strict_captures_cover_every_locked_case():
    for slug in OPERATIONS:
        cases = read_json(ROOT / "tests/demo_cases" / f"{slug}.json")
        artifact = read_json(ROOT / "solutions" / slug / "evals/transcripts.json")
        assert artifact["solution"] == cases["agent"]
        assert artifact["strict_isolation"] is True
        assert artifact["loaded_tools_after_capture"] == [
            cases["cases"][0]["expects_agent"]
        ]
        captured = {item["case_id"]: item for item in artifact["transcripts"]}
        assert set(captured) == {case["id"] for case in cases["cases"]}
        for case in cases["cases"]:
            transcript = captured[case["id"]]
            assert transcript["prompt"] == case["prompt"]
            assert transcript["passed"] is True
            for value in case["must_include"]:
                assert value.lower() in transcript["agent_logs"].lower()


def test_knowledge_records_exactly_match_deterministic_source_constants():
    for slug, (source, _) in OPERATIONS.items():
        module, _ = load_agent(slug)
        package = ROOT / "solutions" / slug
        records_path = (
            package
            / "manual"
            / "knowledge"
            / f"{slug}-synthetic-records.md"
        )
        records = records_path.read_text(encoding="utf-8")
        transcript = read_json(package / "evals/transcripts.json")

        assert records_path.stat().st_size > 4_000
        assert "COMPLETE SYNTHETIC PILOT DATA" in records
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        assert digest == transcript["agent_sources"][0]["sha256"]
        assert digest in records
        assert transcript["case_file_sha256"] in records

        for constant in KNOWLEDGE_CONSTANTS[slug]:
            assert extract_json_block(records, constant) == getattr(
                module, constant
            )

    utility_records = (
        ROOT
        / "solutions"
        / "utility-billing-assistance"
        / "manual"
        / "knowledge"
        / "utility-billing-assistance-synthetic-records.md"
    ).read_text(encoding="utf-8")
    assert extract_json_block(utility_records, "FPL_REFERENCE_2025") == {
        "1": 15650,
        "2": 21150,
        "3": 26650,
        "4": 32150,
        "5": 37650,
    }


def test_rules_files_embed_every_locked_prompt_and_exact_tool_output():
    for slug in OPERATIONS:
        package = ROOT / "solutions" / slug
        rules_path = (
            package
            / "manual"
            / "knowledge"
            / f"{slug}-rules-and-controls.md"
        )
        rules = rules_path.read_text(encoding="utf-8")
        cases = read_json(ROOT / "tests/demo_cases" / f"{slug}.json")
        transcript = read_json(package / "evals/transcripts.json")
        captured = {item["case_id"]: item for item in transcript["transcripts"]}

        assert rules_path.stat().st_size > 7_000
        assert "Deterministic operation rules" in rules
        assert "Shared authorization controls" in rules
        assert "explicit human confirmation" in rules
        assert "immutable audit logging" in rules

        for case in cases["cases"]:
            item = captured[case["id"]]
            assert case["prompt"] in rules
            metadata_match = re.search(
                rf"^### {re.escape(case['id'])} .*?```json\n(.*?)\n```",
                rules,
                flags=re.MULTILINE | re.DOTALL,
            )
            assert metadata_match
            metadata = json.loads(metadata_match.group(1))
            assert metadata["canonical_kwargs"] == case["kwargs"]
            assert item["agent_logs"] in rules
            for value in case["must_include"]:
                assert value.lower() in rules.lower()


def test_operation_skills_point_to_substantive_locked_evidence():
    for slug in OPERATIONS:
        package = ROOT / "solutions" / slug
        cases = read_json(ROOT / "tests/demo_cases" / f"{slug}.json")
        for case in cases["cases"]:
            skill = (
                package
                / "manual"
                / "skills"
                / f"aibast_{case['operation'].replace('_', '-')}"
                / "SKILL.md"
            ).read_text(encoding="utf-8")
            assert case["prompt"] in skill
            assert case["operation"] in skill
            assert "Read the synthetic knowledge records and controls." in skill
            for value in case["must_include"]:
                assert value in skill
