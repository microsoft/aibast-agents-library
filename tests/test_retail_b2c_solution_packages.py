import ast
import importlib.util
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOLUTIONS = ROOT / "solutions"

PACKAGES = {
    "personalized-marketing": {
        "name": "@aibast-agents-library/personalized-marketing",
        "source": "agents/@aibast-agents-library/retail_cpg_stacks/personalized_marketing_stack/personalized_marketing_agent.py",
        "class": "PersonalizedMarketingAgent",
        "tool": "personalized-marketing-agent",
        "onepager": "Personalized Marketing Agent one-pager.pptx",
        "sha": "23919bc754c1151fb7d83ca300caeea6b6dadd4372733ceb8da30c859e222d50",
        "slot": 14,
        "operations": ["customer_segmentation", "campaign_design", "content_personalization", "performance_analysis"],
        "personas": ["Marketing Director", "Campaign Manager"],
    },
    "store-associate-copilot": {
        "name": "@aibast-agents-library/store-associate-copilot",
        "source": "agents/@aibast-agents-library/retail_cpg_stacks/store_associate_copilot_stack/store_associate_copilot_agent.py",
        "class": "StoreAssociateCopilotAgent",
        "tool": "store-associate-copilot-agent",
        "onepager": "24. Retail Store Associate Copilot one-pager.pptx",
        "sha": "2d63f12e857eeb0e2cc65c0e84e92814621f60d15a15f760e0ba45ab5ed42c9b",
        "slot": 21,
        "operations": ["product_lookup", "customer_assist", "task_checklist", "performance_dashboard"],
        "personas": ["Store Associate", "Sales Manager", "Floor Specialist"],
    },
    "cart-abandonment-recovery": {
        "name": "@aibast-agents-library/cart-abandonment-recovery",
        "source": "agents/@aibast-agents-library/b2c_sales_stacks/cart_abandonment_recovery_stack/cart_abandonment_recovery_agent.py",
        "class": "CartAbandonmentRecoveryAgent",
        "tool": "CartAbandonmentRecoveryAgent",
        "onepager": "25. Cart Abandonment Recovery Agent one-pager.pptx",
        "sha": "725f5bde43dc70a3642cd14fe182fc9bc852c1fde193ec06934bd21e163f9b75",
        "slot": 22,
        "operations": ["abandonment_analysis", "recovery_campaign", "incentive_optimization", "conversion_tracking"],
        "personas": ["Marketing Manager", "Digital Marketing Lead", "Growth Manager"],
    },
    "omnichannel-engagement": {
        "name": "@aibast-agents-library/omnichannel-engagement",
        "source": "agents/@aibast-agents-library/b2c_sales_stacks/omnichannel_engagement_stack/omnichannel_engagement_agent.py",
        "class": "OmnichannelEngagementAgent",
        "tool": "OmnichannelEngagementAgent",
        "onepager": "30. Omnichannel Engagement Agent one-pager.pptx",
        "sha": "20e386757fdbe988502bfae46e4da93f4bbecc4f21fee54b98efc5b7cf14f55b",
        "slot": 27,
        "operations": ["channel_performance", "journey_analysis", "engagement_optimization", "campaign_attribution"],
        "personas": ["Customer Experience Leader", "Digital Engagement Manager", "Contact Center Supervisor"],
    },
    "inventory-visibility": {
        "name": "@aibast-agents-library/inventory-visibility",
        "source": "agents/@aibast-agents-library/retail_cpg_stacks/inventory_visibility_stack/inventory_visibility_agent.py",
        "class": "InventoryVisibilityAgent",
        "tool": "inventory-visibility-agent",
        "onepager": "34. Inventory Visibility Agent one-pager.pptx",
        "sha": "7b1a45e0f07c66822200638cabe6e21fa7f150bf410a135d1835aa8db94182a6",
        "slot": 31,
        "operations": ["inventory_dashboard", "stock_alerts", "replenishment_plan", "channel_allocation"],
        "personas": ["Inventory Planner", "Store Manager", "Category Manager"],
    },
    "personalized-shopping-assistant": {
        "name": "@aibast-agents-library/personalized-shopping-assistant",
        "source": "agents/@aibast-agents-library/b2c_sales_stacks/personalized_shopping_assistant_stack/personalized_shopping_assistant_agent.py",
        "class": "PersonalizedShoppingAssistantAgent",
        "tool": "PersonalizedShoppingAssistantAgent",
        "onepager": "41. Personalized Shopping Agent one-pager.pptx",
        "sha": "2e9d0648f0eddddc95ce8cf68c520f39f7c88990c50302d7f2b454c133bad7da",
        "slot": 38,
        "operations": ["product_recommendations", "style_profile", "inventory_check", "outfit_builder"],
        "personas": ["Personal Shopper", "Clienteling Specialist", "Retail Manager"],
    },
    "returns-complaints-resolution": {
        "name": "@aibast-agents-library/returns-complaints-resolution",
        "source": "agents/@aibast-agents-library/retail_cpg_stacks/returns_complaints_resolution_stack/returns_complaints_resolution_agent.py",
        "class": "ReturnsComplaintsResolutionAgent",
        "tool": "returns-complaints-resolution-agent",
        "onepager": "51. Returns and Complaints Resolution Agent one-pager 2026 02 23.pptx",
        "sha": "25a7b558af80dff03229fe225fec4b045ba2ce0093730094d9d98b6fba4d23c8",
        "slot": 41,
        "operations": ["return_processing", "complaint_classification", "resolution_recommendation", "trend_analysis"],
        "personas": ["Customer Service Agent", "Quality Team", "Loss Prevention Team"],
    },
    "customer-loyalty-rewards": {
        "name": "@aibast-agents-library/customer-loyalty-rewards",
        "source": "agents/@aibast-agents-library/b2c_sales_stacks/customer_loyalty_rewards_stack/customer_loyalty_rewards_agent.py",
        "class": "CustomerLoyaltyRewardsAgent",
        "tool": "CustomerLoyaltyRewardsAgent",
        "onepager": "45. Customer Loyalty and Rewards Agent one-pager.pptx",
        "sha": "2487138b852c55f0aeb77a7a4e0a9f186caba5a4d28bc54b1852542abfc25ad3",
        "slot": 43,
        "operations": ["loyalty_dashboard", "points_summary", "reward_recommendations", "tier_analysis"],
        "personas": ["Loyalty Program Director", "CRM Manager", "Marketing Leader"],
    },
}

KNOWLEDGE_CONSTANTS = {
    "personalized-marketing": [
        "CUSTOMER_SEGMENTS",
        "CAMPAIGN_TEMPLATES",
        "AB_TEST_RESULTS",
        "CONTENT_BLOCKS",
    ],
    "store-associate-copilot": [
        "PRODUCT_CATALOG",
        "CUSTOMER_INTERACTION_SCRIPTS",
        "DAILY_TASK_LIST",
        "ASSOCIATE_PERFORMANCE",
        "COMPLEMENTARY_PRODUCTS",
    ],
    "cart-abandonment-recovery": [
        "ABANDONED_CARTS",
        "RECOVERY_CAMPAIGNS",
        "INCENTIVE_OPTIONS",
        "CONVERSION_METRICS",
    ],
    "omnichannel-engagement": [
        "CHANNELS",
        "CUSTOMER_JOURNEYS",
        "CAMPAIGN_RESULTS",
    ],
    "inventory-visibility": [
        "STORES",
        "WAREHOUSES",
        "SKUS",
        "INVENTORY",
        "SAFETY_STOCK",
        "LEAD_TIMES_DAYS",
        "CHANNEL_DEMAND",
        "DAILY_SELL_THROUGH",
    ],
    "personalized-shopping-assistant": [
        "PRODUCT_CATALOG",
        "CUSTOMER_PREFERENCES",
        "OUTFIT_TEMPLATES",
    ],
    "returns-complaints-resolution": [
        "RETURN_REQUESTS",
        "COMPLAINT_CATEGORIES",
        "RESOLUTION_PLAYBOOKS",
        "TREND_DATA",
    ],
    "customer-loyalty-rewards": [
        "LOYALTY_MEMBERS",
        "TIER_STRUCTURE",
        "REDEMPTION_CATALOG",
        "ENGAGEMENT_ACTIVITIES",
    ],
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_literals(path):
    values = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            try:
                values[node.targets[0].id] = ast.literal_eval(node.value)
            except (TypeError, ValueError):
                pass
    return values


def load_agent(config, slug):
    path = ROOT / config["source"]
    spec = importlib.util.spec_from_file_location(f"retail_b2c_{slug}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, config["class"])()


def package_folder(config):
    return SOLUTIONS / config["name"].rsplit("/", 1)[-1]


def deterministic_rows():
    document = read_json(ROOT / "solutions.json")
    if isinstance(document, list):
        return document
    rows = document.get("solutions", document)
    return list(rows.values()) if isinstance(rows, dict) else rows


def test_packages_match_approved_slides_and_deterministic_source():
    onepagers = read_json(ROOT / "state" / "onepager_content.json")["onepagers"]
    rows = {row["repo_agent"]: row for row in deterministic_rows()}
    for slug, config in PACKAGES.items():
        source = onepagers[config["onepager"]]
        row = rows[config["name"]]
        package = package_folder(config)
        promise_map = read_json(package / "evals" / "onepager-map.json")
        audit = read_json(package / "evals" / "source-audit.json")
        assert source["source_sha256"] == config["sha"]
        assert row["slot"] == config["slot"]
        assert row["onepager"] == config["onepager"]
        assert promise_map["source_slide_sha256"] == config["sha"]
        assert promise_map["source_audit"] == {
            "approved_slide_hash_match": True,
            "deterministic_source": "solutions.json",
            "deterministic_slot": config["slot"],
            "content_snapshot": "state/onepager_content.json",
        }
        assert audit["schema"] == "aibast-source-audit/1.0"
        assert audit["solution"] == config["name"]
        assert audit["approved_source"]["hash_match"] is True
        assert audit["deterministic_source"]["matches"] is True
        assert all(audit[area]["status"] == "fixed" for area in [
            "routing",
            "interface_schema",
            "behavior",
            "safety",
        ])


def test_packages_include_complete_educational_surfaces():
    for slug, config in PACKAGES.items():
        folder = package_folder(config)
        assert (folder / "README.md").exists()
        assert (folder / "deployment.json").exists()
        assert (folder / "evals" / "onepager-map.json").exists()
        assert (folder / "evals" / "source-audit.json").exists()
        assert (folder / "manual" / "GLOBAL-INSTRUCTIONS.md").exists()
        assert (folder / "FIELD-GUIDE.md").exists()
        assert (folder / "quest.html").exists()
        assert (folder / "manual-tutorial.html").exists()
        assert (folder / "export-manifest.json").exists()
        assert (folder / "exports" / f"{slug}-source.zip").exists()
        assert (folder / "screenshots" / "assisted" / "browserfilm.json").exists()
        assert (
            folder
            / "screenshots"
            / "assisted"
            / "copilot-assisted-walkthrough.gif"
        ).exists()
        assert (folder / "screenshots" / "manual" / "browserfilm.json").exists()
        assert (
            folder
            / "screenshots"
            / "manual"
            / "manual-build-walkthrough.gif"
        ).exists()
        knowledge = sorted((folder / "manual" / "knowledge").glob("*.md"))
        skills = sorted((folder / "manual" / "skills").glob("*/SKILL.md"))
        assert len(knowledge) == 2, slug
        assert len(skills) == len(config["operations"]), slug
        assert {path.parent.name.replace("-", "_") for path in skills} == set(config["operations"])
        export_manifest = read_json(folder / "export-manifest.json")
        assert all(item["status"] == "ready" for item in export_manifest["files"])
        source_package = (ROOT / config["source"]).parent
        assert not (source_package / "README.md").exists()
        assert not (source_package / "deployment.json").exists()
        assert not (source_package / "evals").exists()
        assert not (source_package / "manual").exists()


def test_deployment_and_skills_preserve_draft_only_safety():
    for slug, config in PACKAGES.items():
        folder = package_folder(config)
        recipe = read_json(folder / "deployment.json")
        assert recipe["name"] == config["name"]
        assert recipe["source_path"] == config["source"]
        assert recipe["source_url"].endswith(config["source"])
        assert recipe["target_filename"].endswith("_agent.py")
        assert recipe["expected_tool"] == config["class"]
        assert recipe["operations"] == config["operations"]
        assert recipe["manual_instructions"] == "manual/GLOBAL-INSTRUCTIONS.md"
        assert recipe["manual_authoring"] == {
            "knowledge_files": 2,
            "skills": 4,
            "status": "source-assets-only",
            "publish": False,
        }
        assert recipe["manual_skill_count"] == 4
        assert len(recipe["manual_knowledge_files"]) == 2
        assert recipe["write_controls"]["local_demo_performs_writes"] is False
        assert recipe["write_controls"]["explicit_human_approval_required"] is True
        studio = recipe["copilot_studio"]
        assert studio["authoring_mode"] == "manual-upload"
        assert studio["status"] == "not_initialized"
        assert studio["operations"] == config["operations"]
        assert len(studio["manual_knowledge_files"]) == 2
        assert studio["manual_skill_count"] == 4
        assert studio["publish_requires_confirmation"] is True
        assert "never" in recipe["safety_boundary"].lower()
        assert recipe["safety"]["mode"] in {
            "draft-only",
            "advisory-only",
            "read-only",
            "recommendation-only",
            "decision-support-only",
            "informational-only",
        }
        for skill in (folder / "manual" / "skills").glob("*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            assert text.startswith("---\nname:")
            assert "\ndescription:" in text
            assert re.search(r"\b(no|not|never|do not|without)\b", text, re.IGNORECASE)


def test_knowledge_files_are_complete_exact_records_not_placeholders():
    forbidden_placeholder_text = {
        "todo",
        "tbd",
        "full portable agent contains",
        "see the source agent for complete records",
    }
    for slug, config in PACKAGES.items():
        knowledge = package_folder(config) / "manual" / "knowledge"
        records_path = next(knowledge.glob("*-synthetic-records.md"))
        rules_path = next(knowledge.glob("*-rules-and-safety.md"))
        records = records_path.read_text(encoding="utf-8")
        rules = rules_path.read_text(encoding="utf-8")
        literals = source_literals(ROOT / config["source"])

        assert len(records) >= 5_000, slug
        assert len(rules) >= 7_000, slug
        assert "## Complete deterministic record sets" in records
        assert "## Locked deterministic reference responses" in rules
        assert records.count("```json") == len(KNOWLEDGE_CONSTANTS[slug])
        assert rules.count("```markdown") == len(config["operations"])
        for phrase in forbidden_placeholder_text:
            assert phrase not in records.lower(), (slug, phrase)
            assert phrase not in rules.lower(), (slug, phrase)
        for constant in KNOWLEDGE_CONSTANTS[slug]:
            assert f"### `{constant}`" in records
            exact_records = json.dumps(literals[constant], indent=2, sort_keys=False)
            assert exact_records in records, (slug, constant)


def test_knowledge_files_embed_every_locked_case_and_transcript_evidence():
    for slug, config in PACKAGES.items():
        knowledge = package_folder(config) / "manual" / "knowledge"
        records = next(knowledge.glob("*-synthetic-records.md")).read_text(
            encoding="utf-8"
        )
        rules = next(knowledge.glob("*-rules-and-safety.md")).read_text(
            encoding="utf-8"
        )
        contract = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")
        artifact = read_json(package_folder(config) / "evals" / "transcripts.json")
        captured = {item["case_id"]: item for item in artifact["transcripts"]}

        assert "## Exact no-side-effect boundary" in rules
        assert "Never claim an action was sent, scheduled, approved" in rules
        for case in contract["cases"]:
            arguments = json.dumps(
                case.get("arguments", {}),
                sort_keys=True,
                separators=(",", ":"),
            )
            assert f"`{case['id']}`" in records
            assert f"`{case['operation']}`" in records
            assert f"`{arguments}`" in records
            assert case["prompt"] in rules
            normalized_logs = "\n".join(
                line.rstrip()
                for line in captured[case["id"]]["agent_logs"].splitlines()
            )
            assert normalized_logs in rules
            for marker in case["must_include"]:
                assert marker.lower() in rules.lower(), (case["id"], marker)


def test_onepager_promises_cover_every_operation_and_case():
    for slug, config in PACKAGES.items():
        promise_map = read_json(package_folder(config) / "evals" / "onepager-map.json")
        cases = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")["cases"]
        contract = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")
        assert contract["agent_files"] == [Path(config["source"]).stem]
        mapped_operations = {
            operation
            for promise in promise_map["promises"]
            for operation in promise["operations"]
        }
        mapped_cases = {
            case
            for promise in promise_map["promises"]
            for case in promise["demo_cases"]
        }
        assert mapped_operations == set(config["operations"])
        assert mapped_cases == {case["id"] for case in cases}
        assert all(promise["synthetic_evidence"] for promise in promise_map["promises"])


def test_persona_language_case_exists_and_runs_for_every_operation():
    for slug, config in PACKAGES.items():
        cases = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")["cases"]
        assert len(cases) == len(config["operations"])
        assert {case["operation"] for case in cases} == set(config["operations"])
        assert {case["persona"] for case in cases} <= set(config["personas"])
        agent = load_agent(config, slug)
        assert agent.name == config["tool"]
        persona_enum = agent.metadata["parameters"]["properties"]["persona"]["enum"]
        assert persona_enum == config["personas"]
        for case in cases:
            arguments = dict(case["arguments"])
            arguments.update(operation=case["operation"], persona=case["persona"])
            output = agent.perform(**arguments)
            assert case["persona"].lower() in output.lower(), case["id"]
            assert "synthetic" in output.lower(), case["id"]
            for expected in case["must_include"]:
                assert expected.lower() in output.lower(), (case["id"], expected)


def test_owned_sources_remove_direct_identifiers_and_sensitive_demographics():
    email = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
    forbidden_tokens = {"customer_name", "gender_split", "avg_age", "birthday_month"}
    for config in PACKAGES.values():
        text = (ROOT / config["source"]).read_text(encoding="utf-8")
        assert not email.search(text), config["source"]
        for token in forbidden_tokens:
            assert token not in text, (config["source"], token)


def test_agents_reject_non_synthetic_sources_and_unknown_identifiers():
    invalid = {
        "personalized-marketing": {"segment_id": "UNKNOWN"},
        "store-associate-copilot": {"sku_id": "UNKNOWN"},
        "cart-abandonment-recovery": {"cart_id": "UNKNOWN"},
        "omnichannel-engagement": {"channel": "UNKNOWN"},
        "inventory-visibility": {"location_id": "UNKNOWN"},
        "personalized-shopping-assistant": {"customer_id": "UNKNOWN"},
        "returns-complaints-resolution": {"return_id": "UNKNOWN"},
        "customer-loyalty-rewards": {"member_id": "UNKNOWN"},
    }
    for slug, config in PACKAGES.items():
        agent = load_agent(config, slug)
        operation = config["operations"][0]
        assert "must be `synthetic`" in agent.perform(
            operation=operation,
            data_source="production",
        )
        output = agent.perform(operation=operation, **invalid[slug])
        assert "unknown" in output.lower()


def test_capture_contract_resolves_exact_owned_source_stems():
    capture_path = ROOT / "tools" / "capture_demo_transcripts.py"
    spec = importlib.util.spec_from_file_location("retail_capture_contract", capture_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for slug, config in PACKAGES.items():
        contract = read_json(ROOT / "tests" / "demo_cases" / f"{slug}.json")
        assert len(contract["agent_files"]) == 1
        resolved = module.find_agent(contract["agent_files"][0])
        assert resolved == ROOT / config["source"]


def test_strict_transcripts_are_persisted_and_current():
    for slug, config in PACKAGES.items():
        package = package_folder(config)
        artifact = read_json(package / "evals" / "transcripts.json")
        contract_path = ROOT / "tests" / "demo_cases" / f"{slug}.json"
        contract = read_json(contract_path)
        source_path = ROOT / config["source"]

        assert artifact["solution"] == config["name"]
        assert artifact["strict_isolation"] is True
        assert artifact["case_file"] == contract_path.relative_to(ROOT).as_posix()
        assert artifact["case_file_sha256"] == hashlib.sha256(
            contract_path.read_bytes()
        ).hexdigest()
        assert artifact["agent_sources"] == [
            {
                "path": config["source"],
                "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
            }
        ]
        assert artifact["loaded_tools_after_capture"] == [config["tool"]]

        captured = {item["case_id"]: item for item in artifact["transcripts"]}
        assert set(captured) == {case["id"] for case in contract["cases"]}
        for case in contract["cases"]:
            item = captured[case["id"]]
            assert item["passed"] is True
            assert item["prompt"] == case["prompt"]
            for marker in case["must_include"]:
                assert marker.lower() in item["agent_logs"].lower()
