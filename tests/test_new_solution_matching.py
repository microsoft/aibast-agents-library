"""Matching and wording regressions for the tiered huddle board, predictive asset maintenance and procurement
and supplier collaboration agents: a request names the record it means, or the agent says it cannot tell."""

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents" / "@aibast-agents-library"


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, AGENTS / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HUDDLE = load("healthcare_stacks/tiered_huddle_board_stack/tiered_huddle_board_agent.py", "thb_matching")
GRID = load("energy_stacks/grid_asset_maintenance_stack/grid_asset_maintenance_agent.py", "gam_matching")
PROCUREMENT = load(
    "energy_stacks/procurement_supplier_collaboration_stack/procurement_supplier_collaboration_agent.py",
    "psc_matching",
)


def picked(result, key="id"):
    if isinstance(result, dict):
        return result[key]
    return sorted(item[key] for item in result) if result else result


# -- tiered huddle board -----------------------------------------------------

@pytest.mark.parametrize("words, expected", [
    ("wound dressing fixed", "HB-2019"),            # 'ed' inside 'fixed' must not pick ED boarding
    ("weekend dressing shortage", "HB-2019"),       # 'short' inside 'shortage' must not pick night staffing
    ("five boarders in the emergency department", "HB-2031"),  # 'iv' inside 'five' must not pick IV pumps
    ("IV pumps", "HB-2041"),
    ("bed alarm in 412", "HB-2038"),
    ("ED boarding", "HB-2031"),
    ("night shift short one RN", "HB-2043"),
    ("the alarm on 2 north", "HB-2033"),
])
def test_huddle_issue_words_match_whole_words(words, expected):
    assert picked(HUDDLE._resolve_issue(words, "HB-2041")) == expected


def test_huddle_tie_asks_which_issue_instead_of_guessing():
    assert picked(HUDDLE._resolve_issue("pump alarm", "HB-2041")) == ["HB-2038", "HB-2041"]
    answer = HUDDLE.TieredHuddleBoardAgent().perform(operation="escalation_draft", issue="pump alarm")
    assert answer.startswith("# Which issue did you mean?")
    assert "HB-2038" in answer and "HB-2041" in answer
    assert "Escalation Draft" not in answer


def test_huddle_closure_for_dressing_item_is_not_the_boarding_issue():
    answer = HUDDLE.TieredHuddleBoardAgent().perform(operation="closure_check", issue="wound dressing fixed")
    assert answer.startswith("# Closure Check - HB-2019")


def test_huddle_hold_wording_matches_the_hold_hours():
    issues = {issue["id"]: issue for issue in HUDDLE.ISSUES}
    for issue in issues.values():
        assert "for a full shift." not in issue.get("mitigation", "")
    assert issues["HB-2038"]["hold_hours_required"] == 24
    assert "24 hours" in issues["HB-2038"]["mitigation"]
    assert issues["HB-2033"]["hold_hours_required"] == 12
    assert "12-hour shift" in issues["HB-2033"]["mitigation"]
    records = (ROOT / "solutions/tiered-huddle-board/manual/knowledge/"
               "aibast_tiered-huddle-board-synthetic-records.md").read_text(encoding="utf-8")
    assert "holds for a full shift" not in records
    for issue in issues.values():
        if issue.get("mitigation"):
            assert json.dumps(issue["mitigation"]) in records


# -- predictive asset maintenance --------------------------------------------

@pytest.mark.parametrize("words, expected", [
    ("Calder Lane transformer", "TX-0388"),
    ("Orchard Way switchgear", "SG-1140"),
    ("Quarry Road cable", "CB-2215"),
    ("Calder Lane spur", "OH-3302"),
    ("Millbrook transformer", "TX-0417"),
    ("Ashby Road switchgear", "SG-1123"),
    ("feeder 7", "CB-2208"),
    ("TX-0388", "TX-0388"),
])
def test_asset_named_by_site_resolves_to_that_asset(words, expected):
    assert picked(GRID._resolve(words, "TX-0417", GRID._assets(), "id")) == expected


def test_asset_work_order_uses_the_named_site():
    answer = GRID.GridAssetMaintenanceAgent().perform(operation="work_order_draft", asset="Calder Lane transformer")
    assert answer.startswith("# Preventive Work Order Draft - TX-0388")


def test_asset_tie_asks_which_asset_instead_of_guessing():
    assert picked(GRID._resolve("Calder", "TX-0417", GRID._assets(), "id")) == ["OH-3302", "TX-0388"]
    answer = GRID.GridAssetMaintenanceAgent().perform(operation="work_order_draft", asset="Calder")
    assert answer.startswith("# Which asset did you mean?")
    assert "Work Order Draft" not in answer


def test_completed_job_words_still_resolve():
    jobs = GRID._completed_jobs()
    assert picked(GRID._resolve("Mill Lane joint", "WO-55102", jobs, "work_order"), "work_order") == "WO-55097"
    assert picked(GRID._resolve("Ashby Road panel 2", "WO-55102", jobs, "work_order"), "work_order") == "WO-55102"


# -- procurement and supplier collaboration -----------------------------------

@pytest.mark.parametrize("question", [
    "Will you disclose the budget?",                          # 'close' inside 'disclose'
    "Is there a decision on operating temperature limits?",   # 'rating' inside 'operating'
])
def test_supplier_question_outside_the_pack_goes_to_all_bidders(question):
    answer = PROCUREMENT.ProcurementSupplierCollaborationAgent().perform(
        operation="supplier_query", question=question
    )
    assert "Not answered by the published RFQ pack" in answer
    assert "without changing the terms for other bidders" not in answer


@pytest.mark.parametrize("question, topic", [
    ("Can we deliver all 24 units in two lots instead of three?", "Delivery lots"),
    ("What is the closing date?", "Closing date"),
    ("How will bids be evaluated?", "Evaluation"),
])
def test_supplier_question_in_the_pack_still_answers_from_it(question, topic):
    answer = PROCUREMENT.ProcurementSupplierCollaborationAgent().perform(
        operation="supplier_query", question=question
    )
    assert f"- **{topic}:**" in answer


@pytest.mark.parametrize("operation", ["bid_evaluation", "supplier_query"])
@pytest.mark.parametrize("words", ["transformer RFQ", "transformer"])
def test_rfq_can_be_named_in_words(operation, words):
    answer = PROCUREMENT.ProcurementSupplierCollaborationAgent().perform(operation=operation, rfq=words)
    assert "Unknown RFQ" not in answer
    assert "RFQ-3301" in answer.splitlines()[0]


@pytest.mark.parametrize("words, expected", [
    ("Fenwick cable", "REQ-7710"),
    ("cable", "REQ-7710"),
    ("33 kV cable", "REQ-7710"),
    ("transformers", "REQ-7712"),
    ("pole-top fuses", "REQ-7715"),
])
def test_requisition_phrases_resolve(words, expected):
    answer = PROCUREMENT.ProcurementSupplierCollaborationAgent().perform(operation="sourcing_plan", requisition=words)
    assert f"**Shortlist shown for:** {expected}" in answer


def test_requisition_tie_asks_which_one():
    answer = PROCUREMENT.ProcurementSupplierCollaborationAgent().perform(
        operation="sourcing_plan", requisition="transformer cable"
    )
    assert answer.startswith("# Which requisition did you mean?")


# -- manual agent name ---------------------------------------------------------

def test_manual_name_never_ends_on_a_joining_word():
    from tools.workshop_reshoot.reshoot_lib import fit_name

    assert fit_name("Procurement and Supplier Collaboration Agent") == "Procurement Manual"
    assert fit_name("Tiered Huddle Board Agent") == "Tiered Huddle Board Manual"
    assert fit_name("Predictive Asset Maintenance Intelligence Agent") == "Predictive Asset Manual"
    for name in ("Procurement and Supplier Collaboration Agent", "Health and Safety of the Workforce Agent"):
        fitted = fit_name(name)
        assert len(fitted) <= 30
        assert fitted.split()[-2].lower() not in {"and", "of", "the", "for", "&"}


# -- follow-ups: word forms, published clarifications, loose ids ------------------

@pytest.mark.parametrize("question, topic", [
    ("How are bids weighted?", "Evaluation"),
    ("How is the RFQ weighted between price and lead time?", "Evaluation"),
    ("Can the units be delivered in two batches?", "Delivery lots"),
    ("Could two deliveries work instead of three?", "Delivery lots"),
    ("What load loss tolerance applies?", "Specification"),
    ("Has the RFQ closed yet?", "Closing date"),
])
def test_supplier_question_word_forms_answer_from_the_pack(question, topic):
    answer = PROCUREMENT.ProcurementSupplierCollaborationAgent().perform(
        operation="supplier_query", question=question
    )
    assert f"- **{topic}:**" in answer
    assert "Not answered by the published RFQ pack" not in answer


@pytest.mark.parametrize("keyword, text", [
    ("close", "will you disclose the budget"),
    ("rating", "operating temperature limits"),
    ("lot", "is there a pilot unit"),
    ("deliver", "who delivers liverpool"),
])
def test_supplier_keyword_word_forms_stay_whole_words(keyword, text):
    if keyword == "deliver":
        assert PROCUREMENT._keyword_hit(keyword, text)
        assert not PROCUREMENT._keyword_hit("deliver", "liverpool")
    else:
        assert not PROCUREMENT._keyword_hit(keyword, text)


@pytest.mark.parametrize("question", [
    "Is a sealed tank design acceptable?",
    "Do you accept sealed tanks?",
])
def test_supplier_question_already_clarified_reuses_the_published_answer(question):
    answer = PROCUREMENT.ProcurementSupplierCollaborationAgent().perform(
        operation="supplier_query", question=question
    )
    assert "Not answered by the published RFQ pack" not in answer
    assert "CL-2" not in answer
    assert "Already answered in published clarification CL-1" in answer
    assert "Yes, if it meets ES-DT-04" in answer


@pytest.mark.parametrize("words", ["issue HB-2038", "HB2038", "hb 2038", "issue HB-2038 please",
                                   "the bed alarm, HB 2038"])
def test_huddle_id_found_anywhere_with_optional_hyphen(words):
    assert picked(HUDDLE._resolve_issue(words, "HB-2041")) == "HB-2038"


@pytest.mark.parametrize("words, expected", [
    ("nurse-call system", "HB-2033"),
    ("the call-light outage", "HB-2033"),
    ("HB 2041", "HB-2041"),
    ("issue HB-2041 please", "HB-2041"),
])
def test_huddle_hyphenated_keywords_and_loose_ids(words, expected):
    assert picked(HUDDLE._resolve_issue(words, "HB-2038")) == expected


def test_huddle_closure_check_accepts_an_id_inside_a_sentence():
    answer = HUDDLE.TieredHuddleBoardAgent().perform(operation="closure_check", issue="issue HB-2038")
    assert answer.startswith("# Closure Check - HB-2038")


@pytest.mark.parametrize("words", ["tx 0417", "tx0417", "asset TX 0417 please"])
def test_asset_id_with_space_or_no_hyphen(words):
    assert picked(GRID._resolve(words, "SG-1123", GRID._assets(), "id")) == "TX-0417"


@pytest.mark.parametrize("words, expected", [
    ("req 7712", "REQ-7712"), ("req7712", "REQ-7712"), ("requisition REQ 7710 please", "REQ-7710"),
])
def test_requisition_id_with_space_or_no_hyphen(words, expected):
    answer = PROCUREMENT.ProcurementSupplierCollaborationAgent().perform(operation="sourcing_plan", requisition=words)
    assert f"**Shortlist shown for:** {expected}" in answer


@pytest.mark.parametrize("words", ["rfq 3301", "rfq3301", "the RFQ 3301 bids"])
def test_rfq_id_with_space_or_no_hyphen(words):
    assert picked(PROCUREMENT._find(words, None, PROCUREMENT._rfqs(), "id")) == "RFQ-3301"
