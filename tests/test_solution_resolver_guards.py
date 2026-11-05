"""Guards for the tiered huddle board, predictive asset maintenance and procurement and supplier collaboration
agents: an incidental word never stands in for an answer, a number or voltage in the request picks the record that
carries it (or none), a mitigated item is not escalated, and a viewer named by first name, last name or with a
title still sees what is waiting on them."""

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents" / "@aibast-agents-library"


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, AGENTS / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HUDDLE = load("healthcare_stacks/tiered_huddle_board_stack/tiered_huddle_board_agent.py", "thb_guards")
GRID = load("energy_stacks/grid_asset_maintenance_stack/grid_asset_maintenance_agent.py", "gam_guards")
PROCUREMENT = load(
    "energy_stacks/procurement_supplier_collaboration_stack/procurement_supplier_collaboration_agent.py",
    "psc_guards",
)


def supplier(question):
    return PROCUREMENT.ProcurementSupplierCollaborationAgent().perform(operation="supplier_query", question=question)


def work_order(asset):
    return GRID.GridAssetMaintenanceAgent().perform(operation="work_order_draft", asset=asset)


def huddle(**kwargs):
    return HUDDLE.TieredHuddleBoardAgent().perform(**kwargs)


# -- procurement: one incidental keyword is not an answer ----------------------------

@pytest.mark.parametrize("question", [
    "When is payment due after delivery?",
    "Where can I download the tender documents?",
    "Who bears the risk of loss in transit?",
    "Can we split the order between two suppliers?",
    "Do you accept a sealed or a conservator tank?",
    "What warranty period applies to the transformers?",
])
def test_supplier_question_on_a_subject_the_pack_does_not_cover_goes_to_all_bidders(question):
    answer = supplier(question)
    assert "Not answered by the published RFQ pack" in answer
    assert "CL-2" in answer
    assert "without changing the terms for other bidders" not in answer
    assert "No new clarification is needed" not in answer
    assert "## Draft answer from the published RFQ pack" not in answer


def test_partly_clarified_question_names_what_the_published_clarification_does_not_cover():
    answer = supplier("Do you accept a sealed or a conservator tank?")
    assert "conservator" in answer.split("**Clarifications already published")[0].lower()
    assert "Already answered in published clarification" not in answer


@pytest.mark.parametrize("question, topic", [
    ("A bidder asks if they can deliver all 24 units in two lots instead of three.", "Delivery lots"),
    ("Can the units be delivered in two batches?", "Delivery lots"),
    ("When are bids due?", "Closing date"),
    ("Which quality documents do we need to include?", "Quality documents"),
    ("What load loss tolerance applies?", "Specification"),
    ("How is the RFQ weighted between price and lead time?", "Evaluation"),
])
def test_supplier_question_the_pack_does_answer_still_answers_from_it(question, topic):
    answer = supplier(question)
    assert f"- **{topic}:**" in answer
    assert "Not answered by the published RFQ pack" not in answer


# -- predictive asset maintenance: numbers and voltages disambiguate -----------------

@pytest.mark.parametrize("words", ["11 kV overhead line", "the 11 kV line", "11kV overhead line"])
def test_eleven_kv_line_is_the_eleven_kv_line(words):
    assert GRID._resolve(words, "TX-0417", GRID._assets(), "id")["id"] == "OH-3302"
    answer = work_order(words)
    assert "OH-3310" not in answer
    assert "33 kV line" not in answer


def test_thirty_three_kv_line_still_resolves():
    assert GRID._resolve("33 kV overhead line", "TX-0417", GRID._assets(), "id")["id"] == "OH-3310"


@pytest.mark.parametrize("words", ["Ashby Road panel 2", "panel 2", "T1 at Millbrook", "Millbrook T1",
                                   "Quarry Road feeder 7"])
def test_a_number_that_no_matching_asset_carries_is_unknown_not_a_substitute(words):
    assert GRID._resolve(words, "TX-0417", GRID._assets(), "id") is None
    answer = work_order(words)
    assert answer.startswith("# Unknown Asset")
    assert "Work Order Draft" not in answer
    assert "SG-1123" not in answer.split("Known:")[0]


@pytest.mark.parametrize("words, expected", [
    ("Ashby Road panel 4", "SG-1123"),
    ("Millbrook T2", "TX-0417"),
    ("Calder Lane T1", "TX-0388"),
    ("feeder 12", "CB-2215"),
    ("feeder 7", "CB-2208"),
    ("Millbrook transformer", "TX-0417"),
])
def test_a_number_the_asset_carries_still_resolves(words, expected):
    assert GRID._resolve(words, "TX-0417", GRID._assets(), "id")["id"] == expected


def test_completed_job_panel_number_still_picks_its_job():
    jobs = GRID._completed_jobs()
    assert GRID._resolve("Ashby Road panel 2", "WO-55097", jobs, "work_order")["work_order"] == "WO-55102"
    assert GRID._resolve("Ashby Road panel 4", "WO-55097", jobs, "work_order") is None


# -- tiered huddle board: a mitigated item is on its hold period ----------------------

@pytest.mark.parametrize("issue_id, originator", [("HB-2038", "Jordan Pike"), ("HB-2033", "Amir Sadeghi")])
def test_mitigated_item_is_not_escalated(issue_id, originator):
    answer = huddle(operation="escalation_draft", issue=issue_id)
    assert "mitigated" in answer.lower()
    assert originator in answer
    assert "cannot resolve this" not in answer
    assert "New clock" not in answer
    assert "Page in Microsoft Teams" not in answer
    assert " to Tier " not in answer.splitlines()[0]


def test_open_item_still_escalates():
    answer = huddle(operation="escalation_draft", issue="HB-2041")
    assert answer.startswith("# Escalation Draft - HB-2041: Tier 1 to Tier 2")


# -- tiered huddle board: who is asking ----------------------------------------------

@pytest.mark.parametrize("viewer", ["Elena", "Brooks", "Elena Brooks, Nurse Manager", "elena brooks",
                                    "Nurse Manager Elena Brooks", "I'm Elena"])
def test_viewer_by_first_name_last_name_or_with_a_title_sees_their_items(viewer):
    answer = huddle(operation="board_view", viewer=viewer)
    assert "**Waiting on Elena Brooks:** 1" in answer
    assert "- HB-2041:" in answer.split("## Waiting on")[1]
    assert "Nothing on the board is waiting on" not in answer


def test_viewer_jordan_sees_the_bed_alarm():
    answer = huddle(operation="board_view", viewer="Jordan")
    assert "**Waiting on Jordan Pike:** 1" in answer
    assert "- HB-2038:" in answer.split("## Waiting on")[1]


def test_unrecognized_viewer_is_said_so_not_told_their_list_is_clear():
    answer = huddle(operation="board_view", viewer="Sam Patel")
    assert "Nothing on the board is waiting on" not in answer
    assert "not a name on this board" in answer


def test_named_viewer_with_nothing_waiting_is_still_told_so():
    answer = huddle(operation="board_view", viewer="Naomi Carter")
    assert "Nothing on the board is waiting on Naomi Carter." in answer


def test_group_waiting_on_value_still_matches_exactly():
    answer = huddle(operation="board_view", viewer="Case management")
    assert "- HB-2035:" in answer.split("## Waiting on")[1]
