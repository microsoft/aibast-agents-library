"""Round-4 guards for the procurement and supplier collaboration, predictive asset maintenance and tiered huddle
board agents: a common English word does not turn a question the RFQ pack answers into a new clarification, a
number said in words counts the same as one written in digits, an RMU named without its hyphen is still found, and
a viewer named by their paging-roster role sees what is waiting on them."""

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


HUDDLE = load("healthcare_stacks/tiered_huddle_board_stack/tiered_huddle_board_agent.py", "thb_round4")
GRID = load("energy_stacks/grid_asset_maintenance_stack/grid_asset_maintenance_agent.py", "gam_round4")
PROCUREMENT = load(
    "energy_stacks/procurement_supplier_collaboration_stack/procurement_supplier_collaboration_agent.py",
    "psc_round4",
)


def supplier(question):
    return PROCUREMENT.ProcurementSupplierCollaborationAgent().perform(
        operation="supplier_query", rfq="RFQ-3301", question=question
    )


def resolve(words):
    return GRID._resolve(words, "TX-0417", GRID._assets(), "id")


def work_order(asset):
    return GRID.GridAssetMaintenanceAgent().perform(operation="work_order_draft", asset=asset)


def board(viewer):
    return HUDDLE.TieredHuddleBoardAgent().perform(operation="board_view", viewer=viewer)


# -- procurement: common words are not off-pack subjects -----------------------------

@pytest.mark.parametrize("question, topic", [
    ("How much weight do you pay to lead time in the evaluation?", "Evaluation"),
    ("Does the evaluation panel need access to our ISO 9001 certificate?", "Quality documents"),
    ("What is the risk of a bid being scored down if the type test certificate is missing?", "Quality documents"),
    ("Is there a risk of a lower quality score without ISO 9001?", "Quality documents"),
    ("Is a bid at risk of half marks if the type test certificate is missing?", "Quality documents"),
    ("What is the title of the specification document for the transformer?", "Specification"),
])
def test_question_the_pack_answers_is_not_turned_into_a_new_clarification(question, topic):
    answer = supplier(question)
    assert "## Draft answer from the published RFQ pack" in answer
    assert f"- **{topic}:**" in answer
    assert "Not answered by the published RFQ pack" not in answer
    assert "CL-2" not in answer


def test_sealed_tank_question_with_the_word_risk_reuses_cl1():
    answer = supplier("Is a sealed tank design acceptable? We want to reduce the risk of oil leaks.")
    assert "Already answered in published clarification CL-1" in answer
    assert "No new clarification is needed" in answer
    assert "Not answered by the published RFQ pack" not in answer
    assert "CL-2" not in answer


@pytest.mark.parametrize("question, subject", [
    ("When will you pay us after delivery?", "payment terms"),
    ("Do you pay on delivery or at the end of the month?", "payment terms"),
    ("Who carries the risk while the units are in transit?", "risk, insurance and liability"),
    ("When does title transfer to the buyer?", "risk, insurance and liability"),
    ("Who pays if a unit is damaged in transit?", "risk, insurance and liability"),
    ("I cannot get portal access, can you help?", "access to the tender documents"),
    ("Where do I download the specification?", "access to the tender documents"),
])
def test_specific_off_pack_phrases_still_go_to_all_bidders(question, subject):
    answer = supplier(question)
    assert "Not answered by the published RFQ pack" in answer
    assert subject in answer
    assert "CL-2" in answer
    assert "## Draft answer from the published RFQ pack" not in answer


# -- predictive asset maintenance: spelled-out numbers --------------------------------

@pytest.mark.parametrize("words", ["Ashby Road panel two", "panel two", "Millbrook transformer number 1",
                                   "Millbrook transformer 1", "Millbrook transformer one", "Quarry Road feeder seven",
                                   "T one at Millbrook"])
def test_a_spelled_number_no_matching_asset_carries_is_unknown(words):
    assert resolve(words) is None
    answer = work_order(words)
    assert answer.startswith("# Unknown Asset")
    assert "Work Order Draft" not in answer


def test_panel_two_never_drafts_panel_four():
    answer = work_order("Ashby Road panel two")
    assert "SG-1123" not in answer.split("Known:")[0]
    assert "panel 4" not in answer


@pytest.mark.parametrize("words, expected", [
    ("the eleven kV overhead line", "OH-3302"),
    ("eleven kv line", "OH-3302"),
    ("thirty three kV overhead line", "OH-3310"),
    ("thirty-three kV line", "OH-3310"),
    ("Ashby Road panel four", "SG-1123"),
    ("feeder seven", "CB-2208"),
    ("feeder twelve", "CB-2215"),
    ("Millbrook transformer number 2", "TX-0417"),
    ("Millbrook T two", "TX-0417"),
    ("Calder Lane transformer one", "TX-0388"),
])
def test_a_spelled_number_the_asset_carries_resolves(words, expected):
    assert resolve(words)["id"] == expected


def test_completed_job_spelled_panel_number_picks_its_job():
    jobs = GRID._completed_jobs()
    assert GRID._resolve("Ashby Road panel two", "WO-55097", jobs, "work_order")["work_order"] == "WO-55102"


# -- predictive asset maintenance: RMU without its hyphen ------------------------------

@pytest.mark.parametrize("words", ["RMU 22", "RMU22", "rmu-22", "the RMU 22 at Orchard Way", "ring main unit RMU 22",
                                   "RMU twenty two"])
def test_rmu_named_without_its_hyphen_is_sg_1140(words):
    assert resolve(words)["id"] == "SG-1140"
    answer = work_order(words)
    assert answer.startswith("# Preventive Work Order Draft - SG-1140")


def test_an_rmu_number_nobody_carries_is_unknown():
    assert resolve("RMU 21") is None


# -- tiered huddle board: a viewer named by roster role ------------------------------

@pytest.mark.parametrize("viewer, person, item", [
    ("Charge Nurse, 4 West", "Jordan Pike", "HB-2038"),
    ("charge nurse", "Jordan Pike", "HB-2038"),
    ("Nurse Manager", "Elena Brooks", "HB-2041"),
    ("Nurse Manager, 4 West", "Elena Brooks", "HB-2041"),
    ("I'm the charge nurse", "Jordan Pike", "HB-2038"),
])
def test_viewer_named_by_roster_role_sees_their_items(viewer, person, item):
    answer = board(viewer)
    assert f"**Waiting on {person}:**" in answer
    assert f"- {item}:" in answer.split("## Waiting on")[1]
    assert "not a name on this board" not in answer


def test_role_on_a_department_lane_names_the_person():
    answer = board("Staffing Office Manager")
    assert "**Waiting on Lena Ford:**" in answer
    assert "- HB-2043:" in answer.split("## Waiting on")[1]
    assert "not a name on this board" not in answer


def test_role_shared_by_several_people_asks_which_person():
    answer = board("Director")
    section = answer.split("## Waiting on")[1]
    assert "matches more than one person" in section
    assert "Rachel Ng" in section and "Victor Hale" in section
    assert "Nothing on the board is waiting on" not in answer


def test_unknown_viewer_message_does_not_deny_a_role_the_roster_has():
    answer = board("Sam Patel")
    assert "not a name on this board" in answer
    assert "Nothing on the board is waiting on" not in answer
