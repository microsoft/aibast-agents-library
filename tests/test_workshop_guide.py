"""The workshop engine as a library guide: choose, answer, adapt."""

import hashlib
import json
from pathlib import Path

from tests.test_workshop_agent import ROOT, build_agent


def _find(agent, text):
    return json.loads(agent.perform(operation="find", solution=text))


# Feature 1: several matches -> ask, never an error.

def test_exact_name_wins(tmp_path):
    _m, agent, _d = build_agent(tmp_path)
    result = _find(agent, "Procurement Agent")
    assert result["status"] == "match"
    assert result["solution"]["solution"] == "procurement-agent"


def test_several_matches_return_a_choice_list(tmp_path):
    _m, agent, _d = build_agent(tmp_path)
    result = _find(agent, "I need a procurement agent")
    assert result["status"] == "choose"
    slugs = {choice["solution"] for choice in result["choices"]}
    assert {
        "procurement-agent",
        "procurement-support",
        "procurement-supplier-collaboration",
    } <= slugs
    for choice in result["choices"]:
        assert choice["name"] and choice["industry"] and choice["summary"]
    assert "error" not in result


def test_build_and_test_asks_instead_of_failing(tmp_path):
    _m, agent, _d = build_agent(tmp_path)
    result = json.loads(
        agent.perform(operation="build_and_test", solution="procurement")
    )
    assert result["status"] == "choose"
    assert not agent.state_path.exists()


def test_one_fitting_solution_is_used(tmp_path):
    _m, agent, _d = build_agent(tmp_path)
    result = _find(agent, "daily huddles")
    assert result["status"] == "match"
    assert result["solution"]["solution"] == "tiered-huddle-board"


def test_no_match_suggests_closest(tmp_path):
    _m, agent, _d = build_agent(tmp_path)
    result = _find(agent, "zzqx qqvv")
    assert result["status"] == "no_match"
    assert "closest" in result


# Feature 2: seller questions.

def test_about_answers_the_seller_questions(tmp_path):
    _m, agent, _d = build_agent(tmp_path)
    result = json.loads(
        agent.perform(operation="about", solution="Tiered Huddle Board")
    )
    assert result["status"] == "about"
    assert "background" in result["first_ask"]
    real = result["is_it_real"]
    assert real["where_it_came_from"].startswith("Catalog solution")
    assert real["test_cases"] == 4
    assert real["copilot_studio_preview"]["cases_passed"] == 4
    demo = result["how_to_demo"]
    assert demo["workshop"].endswith("solutions/tiered-huddle-board/quest.html")
    assert "Easy Mode" in demo["easy_mode"]
    assert demo["video"] is None and "No demo video" in demo["video_note"]
    assert "No customer results are published" in result["customer_results"]
    talk = result["who_to_talk_to"]
    assert talk["request_form"].endswith("request-info.html")
    assert "Thursdays" in talk["office_hours"]["when"]
    assert result["assets"]["one_pager"].endswith(".pptx")
    text = json.dumps(result).lower()
    assert "azure" not in text


def test_about_reports_a_published_video(tmp_path):
    _m, agent, _d = build_agent(tmp_path)
    result = json.loads(
        agent.perform(operation="about", solution="Account Intelligence")
    )
    assert result["how_to_demo"]["video"].endswith(".mp4")
    assert result["how_to_demo"]["video_note"] is None


# Feature 3: industry adaptation.

def test_adapt_first_returns_the_kit(tmp_path):
    _m, agent, _d = build_agent(tmp_path)
    result = json.loads(agent.perform(
        operation="adapt",
        solution="Tiered Huddle Board",
        industry="dental clinics",
    ))
    assert result["status"] == "adaptation_kit"
    assert "Nurse Manager" in result["original"]["roles"]
    assert "synthetic" in result["next"]
    assert result["original_unchanged"] is True


def test_adapt_writes_a_local_copy_and_keeps_the_original(tmp_path):
    _m, agent, _d = build_agent(tmp_path)
    original = (
        ROOT / "agents/@aibast-agents-library/healthcare_stacks"
        / "tiered_huddle_board_stack/tiered_huddle_board_agent.py"
    )
    before = hashlib.sha256(original.read_bytes()).hexdigest()
    result = json.loads(agent.perform(
        operation="adapt",
        solution="Tiered Huddle Board",
        industry="dental clinics",
        replacements=json.dumps([
            {"from": "Nurse Manager", "to": "Practice Manager",
             "why": "Dental clinics are run by a practice manager."},
        ]),
    ))
    assert result["status"] == "adapted"
    assert result["changes"][0]["count"] > 0
    copy = Path(result["local_copy"])
    assert copy.is_relative_to(tmp_path)
    assert "Practice Manager" in copy.read_text()
    record = json.loads((copy.parent / "adaptation.json").read_text())
    assert record["synthetic_data_only"] and record["original_unchanged"]
    assert hashlib.sha256(original.read_bytes()).hexdigest() == before


# The written guides carry the same three behaviors.

def test_easy_mode_chat_guides_answer_seller_questions():
    guides = sorted((ROOT / "solutions").glob("*/EASY-MODE-COPILOT-CHAT.md"))
    assert guides
    for guide in guides:
        text = guide.read_text(encoding="utf-8")
        assert "## Questions before you show it" in text, guide
        assert "## Adapt it to another industry" in text, guide
        assert "never edited" in text and "synthetic" in text, guide


def test_root_skill_routes_seller_questions():
    text = (ROOT / "skill.md").read_text(encoding="utf-8")
    for needle in (
        'operation: "find"', 'operation: "about"', 'operation: "adapt"',
        "background on the idea", "none is published yet",
        "request form", "office hours", "never edited",
    ):
        assert needle in text, needle


def test_find_reports_industries_so_the_guide_can_offer_adapt(tmp_path):
    _m, agent, _d = build_agent(tmp_path)
    result = _find(agent, "dental clinic chain daily huddles")
    assert result["status"] == "match"
    assert "Healthcare" in result["industries"]
    assert "adapt" in result["next"]


def test_about_without_a_solution_still_routes_the_person(tmp_path):
    _m, agent, _d = build_agent(tmp_path)
    result = json.loads(agent.perform(operation="about"))
    assert result["who_to_talk_to"]["request_form"].endswith(
        "request-info.html"
    )
    assert "office_hours" in result["who_to_talk_to"]
