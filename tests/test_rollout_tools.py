import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent


def load(name):
    path = ROOT / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_catalog_fragment_merge_accepts_disjoint_entries():
    module = load("merge_solution_catalog_fragments")
    entry = {
        field: [] for field in module.REQUIRED_ENTRY_FIELDS
    }
    entry.update({
        "display_name": "Two",
        "sales_headline": "Headline",
        "card_pitch": "Pitch",
        "why_try": "Why",
        "customer_challenge": "Challenge",
        "microsoft_ai_story": "Story",
        "business_value": ["One", "Two", "Three"],
        "search_terms": ["term"],
        "journey_stage": "Govern",
        "blueprint_role": "Role",
        "sample_prompts": [
            {"label": "Prompt", "prompt": "Ask", "demo_url": "demo"}
        ],
        "architecture": {
            field: [] for field in module.REQUIRED_ARCHITECTURE_FIELDS
        },
    })
    entry["architecture"]["local_install_prompt"] = (
        "Do not ask me to open a terminal"
    )
    entry["architecture"]["copilot_studio_prompt"] = "Stop before publish"
    result = module.merge(
        {},
        [
            (
                Path("two.json"),
                {"@aibast/two": entry},
            )
        ],
    )
    assert set(result) == {"@aibast/two"}


def test_catalog_fragment_merge_rejects_conflicts():
    module = load("merge_solution_catalog_fragments")
    with pytest.raises(ValueError):
        module.merge(
            {"@aibast/one": {"display_name": "One"}},
            [
                (
                    Path("conflict.json"),
                    {"@aibast/one": {"display_name": "Different"}},
                )
            ],
        )


def test_catalog_entry_validation_rejects_partial_shorthand():
    module = load("merge_solution_catalog_fragments")
    with pytest.raises(ValueError, match="missing catalog fields"):
        module.validate_entry(
            "@aibast/partial",
            {"display_name": "Partial", "business": {}},
        )


def test_catalog_entry_normalization_enforces_hands_off_gates():
    module = load("merge_solution_catalog_fragments")
    entry = {
        "architecture": {
            "local_install_prompt": "Own setup.",
            "copilot_studio_prompt": "Validate the agent.",
        }
    }
    normalized = module.normalize_entry(entry)
    assert "Do not ask me to open a terminal" in (
        normalized["architecture"]["local_install_prompt"]
    )
    assert "Stop before publish" in (
        normalized["architecture"]["copilot_studio_prompt"]
    )
    assert "Microsoft Copilot Studio plugin" in (
        normalized["architecture"]["copilot_studio_prompt"]
    )


def test_deployment_normalization_adds_standard_runtime_contract():
    module = load("normalize_deployment_recipes")
    agent = {
        "name": "@aibast/test",
        "display_name": "Test Agent",
        "_file": "agents/@aibast/test_agent.py",
    }
    recipe = {
        "name": "@aibast/test",
        "expected_tool": "TestAgent",
        "smoke_test": {"prompt": "test"},
        "copilot_studio": {},
    }
    normalized = module.normalize(recipe, agent)
    assert normalized["source_url"].endswith(agent["_file"])
    assert normalized["brainstem"]["health_url"].endswith("/health")
    assert normalized["smoke_test"]["must_call"] == "TestAgent"
    assert normalized["copilot_studio"]["minimum_pac_version"] == "2.9.3"
    assert normalized["copilot_studio"]["publish_requires_confirmation"] is True


def test_draft_promoter_renders_cli_settings_and_skill(tmp_path):
    module = load("promote_solution_draft")
    assert (
        module.display_name({"display_name": "Product Line Optimization Agent"})
        == "Product Line Optimization"
    )
    assert (
        module.display_name(
            {
                "name": "@aibast-agents-library/product-feedback-synthesizer",
                "display_name": "Product Feedback Synthesizer Agent",
            }
        )
        == "Product Feedback Pilot"
    )
    settings = module.render_settings(
        "Test Pilot",
        "aibast_TestPilot",
        "# Role\n\nSynthetic only.",
    )
    assert 'displayName: "Test Pilot"' in settings
    assert "series: Sonnet46" in settings
    assert "Synthetic only." in settings

    skill = tmp_path / "SKILL.md"
    skill.write_text(
        "---\nname: test-skill\ndescription: Routes a test.\n---\n# Test\n",
        encoding="utf-8",
    )
    rendered, fields = module.render_skill(skill)
    assert fields["name"] == "test-skill"
    assert "kind: InlineAgentSkill" in rendered
    assert "Routes a test." in rendered


def test_draft_promoter_refreshes_an_existing_project(tmp_path, monkeypatch):
    module = load("promote_solution_draft")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    package = tmp_path / "solutions" / "test-solution"
    (package / "manual" / "skills" / "review").mkdir(parents=True)
    (package / "manual" / "knowledge").mkdir(parents=True)
    (package / "deployment.json").write_text(
        json.dumps({"display_name": "Test Agent"}),
        encoding="utf-8",
    )
    (package / "manual" / "GLOBAL-INSTRUCTIONS.md").write_text(
        "# Role\n\nUse only synthetic evidence.",
        encoding="utf-8",
    )
    (package / "manual" / "skills" / "review" / "SKILL.md").write_text(
        "---\nname: review\ndescription: Review synthetic evidence.\n---\n# Review\n",
        encoding="utf-8",
    )
    (package / "manual" / "knowledge" / "records.md").write_text(
        "# Records\n",
        encoding="utf-8",
    )

    project = tmp_path / "project"
    (project / "behaviors").mkdir(parents=True)
    (project / "capabilities" / "knowledge" / "files").mkdir(parents=True)
    (project / "settings.mcs.yml").write_text(
        "displayName: Old\nschemaName: aibast_TestPilot\n",
        encoding="utf-8",
    )
    (project / "agent.sync.yaml").write_text("components: []\n", encoding="utf-8")
    (project / "behaviors" / "stale.mcs.yml").write_text("stale\n", encoding="utf-8")
    (project / "capabilities" / "knowledge" / "files" / "stale.md").write_text(
        "stale\n",
        encoding="utf-8",
    )

    result = module.promote(
        "test-solution",
        project,
        "environment-id",
        "aibast",
        False,
        update_existing=True,
    )

    assert result["initialized"] is False
    assert result["updated"] is True
    assert result["display_name"] == "Old"
    assert not (project / "behaviors" / "stale.mcs.yml").exists()
    assert (project / "behaviors" / "aibast_review.mcs.yml").exists()
    assert not (
        project / "capabilities" / "knowledge" / "files" / "stale.md"
    ).exists()
    assert (
        project / "capabilities" / "knowledge" / "files" / "records.md"
    ).exists()
    assert (package / "copilot-studio" / "settings.mcs.yml").exists()


def test_promotion_batch_selects_only_missing_studio_sources(tmp_path, monkeypatch):
    module = load("promote_rollout_batch")
    registry = {
        "agents": [
            {
                "name": "@aibast/one",
                "_solution": {"has_onepager": True, "slot": 1},
                "_demo": {"slug": "one"},
            },
            {
                "name": "@aibast/two",
                "_solution": {"has_onepager": True, "slot": 2},
                "_demo": {"slug": "two"},
            },
        ]
    }
    source = tmp_path / "solutions" / "one" / "copilot-studio"
    source.mkdir(parents=True)
    (source / "settings.mcs.yml").write_text("displayName: one", encoding="utf-8")
    for slug in ("one", "two"):
        manual = tmp_path / "solutions" / slug / "manual"
        manual.mkdir(parents=True, exist_ok=True)
        (manual / "GLOBAL-INSTRUCTIONS.md").write_text("# Role\n", encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    assert module.candidates(registry) == ["two"]
    assert module.candidates(registry, refresh_existing=True) == ["one", "two"]


def test_batch_capture_selects_only_missing_corpora(tmp_path, monkeypatch):
    module = load("capture_rollout_batch")
    cases = tmp_path / "tests" / "demo_cases"
    cases.mkdir(parents=True)
    for slug in ("one", "two"):
        (cases / f"{slug}.json").write_text(
            json.dumps({"agent": slug, "agent_files": [], "cases": []}),
            encoding="utf-8",
        )
    transcript = tmp_path / "solutions" / "one" / "evals"
    transcript.mkdir(parents=True)
    (transcript / "transcripts.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(module, "REPO", tmp_path)
    monkeypatch.setattr(module, "CASES", cases)
    assert [path.stem for path in module.case_paths([], True)] == ["two"]
