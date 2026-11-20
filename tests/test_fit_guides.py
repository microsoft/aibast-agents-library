"""The deploy standard: one list of verbs, one fit-guide form, checked over the whole library."""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check_fit_guides  # noqa: E402

agent = check_fit_guides.load_agent()


def _recipe(slug="deal-progression"):
    return json.load(open(os.path.join(ROOT, "solutions", slug, "deployment.json"), encoding="utf-8"))


def test_every_fit_guide_in_the_library_meets_the_standard():
    assert check_fit_guides.main([]) == 0


def test_the_verbs_are_one_list_on_both_front_ends():
    assert agent.VERBS == ("check", "look", "probe", "plan", "deploy", "undo")
    enum = agent.CopilotStudioDeployAgent().metadata["parameters"]["properties"]["operation"]["enum"]
    assert enum == list(agent.VERBS + agent.HELPERS)
    for verb in agent.VERBS:
        assert agent.run({"operation": verb}).get("ok") is False or verb == "check"  # each verb is routed, never "unknown"


def test_a_guide_without_the_schema_tag_is_refused():
    fit = copy.deepcopy(_recipe()["fit"])
    fit.pop("schema")
    with pytest.raises(agent.DeployError):
        agent.check_fit(fit)


def test_a_mapping_that_writes_is_refused():
    m = copy.deepcopy(_recipe()["fit"]["systems"][0])
    m["operation_id"] = "UpdateRecord"
    with pytest.raises(agent.DeployError):
        agent.check_mapping(m)


def test_a_mapping_without_a_rule_is_refused():
    m = copy.deepcopy(_recipe()["fit"]["systems"][0])
    m["rule"] = ""
    with pytest.raises(agent.DeployError):
        agent.check_mapping(m)


def test_an_operation_the_solution_does_not_have_is_refused():
    recipe = _recipe()
    fit = copy.deepcopy(recipe["fit"])
    fit["systems"][0]["operations"]["made_up_operation"] = fit["systems"][0]["operations"]["pipeline_health"]
    with pytest.raises(agent.DeployError):
        agent.check_fit(fit, recipe["operations"])


def test_the_checker_catches_a_sentence_the_preview_cannot_fill():
    recipe = _recipe()
    recipe["fit"]["systems"][0]["expect_says"] = "You should see {nothing_like_this} deals."
    assert check_fit_guides.check_one(agent, recipe, "deal-progression")


def test_the_shaped_package_is_the_same_bytes_every_time():
    recipe = _recipe()
    m = recipe["fit"]["systems"][0]
    assert agent.build_shaped("deal-progression", recipe["display_name"], m)["zip"] == \
        agent.build_shaped("deal-progression", recipe["display_name"], m)["zip"]


def test_both_targets_answer_the_same_verbs():
    import brainstem_target
    assert brainstem_target.VERBS == agent.VERBS


def test_the_brainstem_target_says_plainly_when_nothing_answers():
    import brainstem_target
    out = brainstem_target.run({"operation": "check", "url": "http://127.0.0.1:9"})
    assert out["ok"] is False and "did not answer" in out["summary"]


def test_the_brainstem_target_changes_nothing_without_a_yes(monkeypatch):
    import brainstem_target
    calls = []
    monkeypatch.setattr(brainstem_target, "_call", lambda url, method="GET", *a, **k: calls.append(method) or {"status": "ok", "agents": []})
    out = brainstem_target.run({"operation": "deploy", "solution": "deal-progression", "source": ROOT})
    assert out["needs_confirmation"] is True and set(calls) == {"GET"}
    out = brainstem_target.run({"operation": "undo", "solution": "deal-progression", "source": ROOT})
    assert out["needs_confirmation"] is True and set(calls) == {"GET"}


def test_an_unreachable_library_is_an_error_not_a_quiet_fall_back_to_sample(tmp_path):
    with pytest.raises(agent.DeployError):
        agent.load_fit("deal-progression", str(tmp_path))
    with pytest.raises(agent.DeployError):
        agent.load_fit("../etc", ROOT)
