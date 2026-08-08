import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "state" / "onepager_content.json"
SOLUTIONS = ROOT / "solutions.json"


def test_every_onepager_reference_has_extracted_slide_content():
    content = json.loads(CONTENT.read_text(encoding="utf-8"))
    solutions = json.loads(SOLUTIONS.read_text(encoding="utf-8"))
    extracted = content["onepagers"]

    assert content["stats"]["onepagers"] == 48
    for solution in solutions["solutions"]:
        onepager = solution.get("onepager")
        if onepager:
            assert onepager in extracted, (
                f"{solution.get('repo_agent')} references missing slide {onepager}"
            )


def test_extracted_slides_expose_the_full_sales_story():
    extracted = json.loads(CONTENT.read_text(encoding="utf-8"))["onepagers"]
    for filename, slide in extracted.items():
        assert slide["title"], filename
        assert slide["executive_summary"], filename
        assert slide["scenario_name"], filename
        assert slide["personas"], filename
        assert slide["agent_requirements"], filename
        assert slide["featured_tools"], filename
        assert len(slide["customer_challenge"]["items"]) >= 2, filename
        assert len(slide["agent_actions"]["items"]) >= 2, filename
        assert len(slide["business_outcomes"]["items"]) >= 2, filename
        assert len(slide["opportunity_statements"]) >= 3 or slide["modules"], filename


def test_energy_suite_preserves_four_distinct_modules():
    extracted = json.loads(CONTENT.read_text(encoding="utf-8"))["onepagers"]
    energy = extracted["Energy Operations Agent Suite one-pager (2).pptx"]
    names = {module["name"] for module in energy["modules"]}
    assert names == {
        "Asset Maintenance Forecast Agent",
        "Permit Management Agent",
        "Regulatory Reporting Agent",
        "Emissions Tracking Agent",
    }
