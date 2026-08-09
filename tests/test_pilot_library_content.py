import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COPY = ROOT / "solutions" / "catalog.json"
DEMO = ROOT / "solutions" / "_shared" / "m365-copilot-demo.html"
RECIPES = ROOT / "solutions"

PILOTS = {
    "@aibast-agents-library/building-permit-processing",
    "@aibast-agents-library/fs-regulatory-compliance",
    "@aibast-agents-library/production-line-optimization",
}
PENDING_SHARED_DEMO = {"@aibast-agents-library/fs-regulatory-compliance"}


def load_copy():
    return json.loads(COPY.read_text(encoding="utf-8"))["solutions"]


def test_pilot_copy_is_hand_authored_and_complete():
    solutions = load_copy()
    assert PILOTS <= set(solutions)
    assert len(solutions) == 51
    required = {
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
    for name, solution in solutions.items():
        assert required <= solution.keys(), name
        assert len(solution["business_value"]) == 3
        assert len(solution["sample_prompts"]) >= 3
        assert solution["architecture"]["local_install_prompt"]
        assert solution["architecture"]["copilot_studio_prompt"]
        assert solution["architecture"]["required_connections"]
        assert solution["architecture"]["manual_commands"]
        assert solution["architecture"]["acceptance_checks"]
        local_prompt = solution["architecture"]["local_install_prompt"]
        studio_prompt = solution["architecture"]["copilot_studio_prompt"]
        assert "Do not ask me to open a terminal" in local_prompt
        assert "raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/" in local_prompt
        assert "Microsoft Copilot Studio plugin" in studio_prompt
        assert "Stop before publish" in studio_prompt


def test_public_sales_copy_uses_qualitative_claims():
    solutions = load_copy()
    fields = (
        "sales_headline",
        "card_pitch",
        "why_try",
        "customer_challenge",
        "microsoft_ai_story",
        "blueprint_role",
    )
    for name, solution in solutions.items():
        public_copy = " ".join(
            [solution[field] for field in fields] + solution["business_value"]
        )
        assert "%" not in public_copy, name
        assert "$" not in public_copy, name
        assert not re.search(r"\b\d+(?:\.\d+)?x\b", public_copy, re.IGNORECASE), name


def test_every_pilot_prompt_opens_a_real_canned_demo():
    solutions = load_copy()
    demo_html = DEMO.read_text(encoding="utf-8")
    for name in PILOTS:
        solution = solutions[name]
        for prompt in solution["sample_prompts"]:
            match = re.search(r"[?&]scenario=([a-z0-9-]+)", prompt["demo_url"])
            assert match, (name, prompt)
            assert f'"{match.group(1)}": {{' in demo_html, (name, prompt["demo_url"])


def test_every_pilot_registry_entry_links_its_journey_package():
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
    agents = {item["name"]: item for item in registry["agents"]}
    for name in PILOTS:
        package = agents[name]["_solution"]["package"]
        assert (ROOT / package["quest_url"]).exists()
        assert (ROOT / package["manual_tutorial_url"]).exists()
        assert (ROOT / package["export_manifest_url"]).exists()


def test_deployment_recipes_point_to_real_sources_and_validate_the_agent():
    for path in sorted(RECIPES.glob("*/deployment.json")):
        recipe = json.loads(path.read_text(encoding="utf-8"))
        relative_source = recipe["source_url"].split("/main/", 1)[1]
        assert (ROOT / relative_source).exists(), path
        assert recipe["registry_url"].endswith("/registry.json")
        assert recipe["target_filename"].endswith("_agent.py")
        assert recipe["expected_tool"]
        assert recipe["smoke_test"]["prompt"]
        assert recipe["smoke_test"]["must_call"] == recipe["expected_tool"]
        assert recipe["brainstem"]["installers"]["macos_linux"].endswith("/install.sh")
        assert recipe["brainstem"]["installers"]["windows_powershell"].endswith("/install.ps1")
        assert recipe["copilot_studio"]["minimum_pac_version"] == "2.9.3"
        assert recipe["copilot_studio"]["publish_requires_confirmation"] is True
