"""One cumulative corpus per matcher, seeded from every repro and control in review rounds 1 to 6.

These matchers were patched round by round, and each narrow patch broke a case an earlier round had fixed. This
file keeps every case in one place so a change to either matcher is checked against all of them at once.

The corpus only grows. Never delete or weaken a case to make a change pass. If two cases truly conflict, stop and
raise it for a decision instead.

- Procurement supplier_query routing: a supplier question either gets a published pack answer (topic named), reuses
  the published clarification CL-1, or becomes a new clarification for every bidder (CL-2, off-pack subject named
  when the agent knows it).
- Predictive asset maintenance resolver: a request names one asset id, a tie the agent asks about, or no monitored
  asset (Unknown asset, never a substitute).
"""

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


GRID = load("energy_stacks/grid_asset_maintenance_stack/grid_asset_maintenance_agent.py", "gam_corpus")
PROCUREMENT = load(
    "energy_stacks/procurement_supplier_collaboration_stack/procurement_supplier_collaboration_agent.py",
    "psc_corpus",
)

PACK, CL1, NEW = "pack", "cl1", "new"
PAYMENT = "payment terms"
ACCESS = "access to the tender documents"
RISK = "risk, insurance and liability"
SPLIT = "splitting the award between suppliers"

# (question, outcome, detail). PACK -> the pack topic that answers it; CL1 -> reuse the published CL-1;
# NEW -> a new all-bidder clarification, detail = the off-pack subject the reply must name (None when no subject).
SUPPLIER_CORPUS = [
    # round 1: substring hits must not answer
    ("Will you disclose the budget?", NEW, "the budget"),
    ("Is there a decision on operating temperature limits?", NEW, None),
    ("Can we deliver all 24 units in two lots instead of three?", PACK, "Delivery lots"),
    ("What is the closing date?", PACK, "Closing date"),
    ("How will bids be evaluated?", PACK, "Evaluation"),
    # round 2: word forms answer from the pack; the published clarification is reused
    ("How are bids weighted?", PACK, "Evaluation"),
    ("How is the RFQ weighted between price and lead time?", PACK, "Evaluation"),
    ("Can the units be delivered in two batches?", PACK, "Delivery lots"),
    ("Could two deliveries work instead of three?", PACK, "Delivery lots"),
    ("What load loss tolerance applies?", PACK, "Specification"),
    ("Has the RFQ closed yet?", PACK, "Closing date"),
    ("Is a sealed tank design acceptable?", CL1, None),
    ("Do you accept sealed tanks?", CL1, None),
    # round 3: one incidental pack word is not an answer to an off-pack subject
    ("When is payment due after delivery?", NEW, PAYMENT),
    ("Where can I download the tender documents?", NEW, ACCESS),
    ("Who bears the risk of loss in transit?", NEW, RISK),
    ("Can we split the order between two suppliers?", NEW, SPLIT),
    ("Do you accept a sealed or a conservator tank?", NEW, "conservator tank designs"),
    ("What are the payment terms?", NEW, PAYMENT),
    ("What warranty period applies to the transformers?", NEW, "warranty"),
    ("A bidder asks if they can deliver all 24 units in two lots instead of three.", PACK, "Delivery lots"),
    ("When are bids due?", PACK, "Closing date"),
    ("Which quality documents do we need to include?", PACK, "Quality documents"),
    # round 4: a common English word is not an off-pack subject
    ("How much weight do you pay to lead time in the evaluation?", PACK, "Evaluation"),
    ("Does the evaluation panel need access to our ISO 9001 certificate?", PACK, "Quality documents"),
    ("What is the risk of a bid being scored down if the type test certificate is missing?", PACK,
     "Quality documents"),
    ("Is there a risk of a lower quality score without ISO 9001?", PACK, "Quality documents"),
    ("Is a bid at risk of half marks if the type test certificate is missing?", PACK, "Quality documents"),
    ("What is the title of the specification document for the transformer?", PACK, "Specification"),
    ("Is a sealed tank design acceptable? We want to reduce the risk of oil leaks.", CL1, None),
    ("When will you pay us after delivery?", NEW, PAYMENT),
    ("Do you pay on delivery or at the end of the month?", NEW, PAYMENT),
    ("Who carries the risk while the units are in transit?", NEW, RISK),
    ("When does title transfer to the buyer?", NEW, RISK),
    ("Who pays if a unit is damaged in transit?", NEW, RISK),
    ("I cannot get portal access, can you help?", NEW, ACCESS),
    ("Where do I download the specification?", NEW, ACCESS),
    # round 5: risk in delivery without the article, and 'arrives damaged'
    ("Who bears risk during delivery?", NEW, RISK),
    ("Who carries risk until the units are delivered?", NEW, RISK),
    ("Who pays if a lot arrives damaged?", NEW, RISK),
    # other phrasings of the same subjects, so the next fix is not another phrase list
    ("Who holds the risk while the transformers are being shipped?", NEW, RISK),
    ("Who is responsible if a unit is damaged during delivery?", NEW, RISK),
    ("Does risk pass to you on delivery?", NEW, RISK),
    ("Who is liable for transit damage?", NEW, RISK),
    ("How soon after delivery do you pay?", NEW, PAYMENT),
    ("Can we be paid in advance?", NEW, PAYMENT),
    ("How do I log in to the portal?", NEW, ACCESS),
    ("Is there any risk that a bid without type test certificates is scored lower?", PACK, "Quality documents"),
    ("Is the delivery split into lots?", PACK, "Delivery lots"),
    ("Are bids scored on sustainability?", PACK, "Evaluation"),
    ("What is the deadline for bids?", PACK, "Closing date"),
    ("Where can I find the evaluation weights?", PACK, "Evaluation"),
    ("Is there a risk of losing marks for late certificates?", PACK, "Quality documents"),
    ("Does the loss tolerance apply on delivery?", PACK, "Specification"),
    # round 6: a framing word ('until', 'shipping', 'weeks', 'in terms of', 'portal') next to an everyday 'risk',
    # 'lost', 'pay' or 'access' does not turn a question about how a bid is scored or which quality documents it
    # needs into an off-pack subject
    ("Is a bid at risk until the type test certificate is provided?", PACK, "Quality documents"),
    ("Is there a risk of a lower score if our shipping lead time is 13 weeks?", PACK, "Evaluation"),
    ("Are marks lost until the certificate arrives?", PACK, "Quality documents"),
    ("How much weight do you pay to lead time in weeks?", PACK, "Evaluation"),
    ("In terms of evaluation, how much weight do you pay to price?", PACK, "Evaluation"),
    ("Does the evaluation panel access our ISO 9001 certificate through the portal?", PACK, "Quality documents"),
    # other phrasings of the same rule, and controls that must stay off-pack
    ("Do we lose marks if the ISO certificate arrives after the deadline?", PACK, "Quality documents"),
    ("Is the quality score at risk if shipping documents are late?", PACK, "Quality documents"),
    ("Is the warranty scored in the evaluation?", NEW, "warranty"),
    ("Who bears the risk if the certificate is lost in transit?", NEW, RISK),
    ("When do you pay us for a scored bid?", NEW, PAYMENT),
    ("Where can I download the tender documents?", NEW, ACCESS),
]


def supplier(question):
    return PROCUREMENT.ProcurementSupplierCollaborationAgent().perform(
        operation="supplier_query", rfq="RFQ-3301", question=question
    )


@pytest.mark.parametrize("question, outcome, detail", SUPPLIER_CORPUS, ids=[c[0] for c in SUPPLIER_CORPUS])
def test_supplier_question_routing_corpus(question, outcome, detail):
    answer = supplier(question)
    head = answer.split("**Clarifications already published")[0]
    if outcome == PACK:
        assert "## Draft answer from the published RFQ pack" in head
        assert f"- **{detail}:**" in head
        assert "Not answered by the published RFQ pack" not in answer
        assert "CL-2" not in answer
    elif outcome == CL1:
        assert "Already answered in published clarification CL-1" in head
        assert "Yes, if it meets ES-DT-04" in head
        assert "No new clarification is needed" in head
        assert "Not answered by the published RFQ pack" not in answer
        assert "CL-2" not in answer
    else:
        assert "Not answered by the published RFQ pack" in head
        assert "CL-2" in head
        assert "## Draft answer from the published RFQ pack" not in answer
        assert "without changing the terms for other bidders" not in answer
        assert "Already answered in published clarification" not in answer
        assert "No new clarification is needed" not in answer
        if detail:
            assert detail in head


# (request, expected). A string is the asset id; None is Unknown asset (no substitute); a tuple is a tie the agent
# asks about.
ASSET_CORPUS = [
    # round 1: a site outranks a class word
    ("Calder Lane transformer", "TX-0388"),
    ("Orchard Way switchgear", "SG-1140"),
    ("Quarry Road cable", "CB-2215"),
    ("Calder Lane spur", "OH-3302"),
    ("Millbrook transformer", "TX-0417"),
    ("Ashby Road switchgear", "SG-1123"),
    ("feeder 7", "CB-2208"),
    ("TX-0388", "TX-0388"),
    ("Calder", ("OH-3302", "TX-0388")),
    # round 2: ids with a space or no hyphen
    ("tx 0417", "TX-0417"),
    ("tx0417", "TX-0417"),
    ("asset TX 0417 please", "TX-0417"),
    ("TX-0417", "TX-0417"),
    ("asset TX-0417", "TX-0417"),
    ("SG-1131", None),
    # round 3: a voltage or number in the request picks the record that carries it, or none
    ("11 kV overhead line", "OH-3302"),
    ("the 11 kV line", "OH-3302"),
    ("11kV overhead line", "OH-3302"),
    ("33 kV overhead line", "OH-3310"),
    ("OH-3302", "OH-3302"),
    ("Ashby Road panel 2", None),
    ("panel 2", None),
    ("T1 at Millbrook", None),
    ("Millbrook T1", None),
    ("Quarry Road feeder 7", None),
    ("Ashby Road panel 4", "SG-1123"),
    ("Millbrook T2", "TX-0417"),
    ("Calder Lane T1", "TX-0388"),
    ("feeder 12", "CB-2215"),
    # round 4: spelled numbers, transformer numbers, RMU without its hyphen
    ("Ashby Road panel two", None),
    ("panel two", None),
    ("Millbrook transformer number 1", None),
    ("Millbrook transformer 1", None),
    ("Millbrook transformer one", None),
    ("Quarry Road feeder seven", None),
    ("T one at Millbrook", None),
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
    ("RMU 22", "SG-1140"),
    ("RMU22", "SG-1140"),
    ("rmu-22", "SG-1140"),
    ("RMU-22", "SG-1140"),
    ("the RMU 22 at Orchard Way", "SG-1140"),
    ("ring main unit RMU 22", "SG-1140"),
    ("ring main unit RMU-22", "SG-1140"),
    ("RMU twenty two", "SG-1140"),
    ("RMU 21", None),
    # round 5: a voltage after 'transformer' is not a transformer number; 'one' as a pronoun is not a number
    ("Millbrook transformer 33/11 kV", "TX-0417"),
    ("the Millbrook primary transformer 33/11kV", "TX-0417"),
    ("transformer 33 kV at Calder Lane", "TX-0388"),
    ("the Millbrook one", "TX-0417"),
    # other phrasings of the same rules
    ("the Orchard Way one", "SG-1140"),
    ("the one at Quarry Road", "CB-2215"),
    ("Harbour Street feeder seven", "CB-2208"),
    ("panel number four at Ashby Road", "SG-1123"),
    ("feeder number 7", "CB-2208"),
    ("the transformer at Calder Lane, 33/11 kV", "TX-0388"),
    ("Millbrook transformer 20 MVA", "TX-0417"),
    ("Millbrook transformer thirty three eleven kV", "TX-0417"),
    ("the 1.2 km section", "CB-2208"),
    # round 6: a stated rating that differs rules an asset out, the way a voltage does
    ("the 15 MVA transformer", "TX-0388"),
    ("15 MVA transformer", "TX-0388"),
    ("the 20 MVA transformer", "TX-0417"),
    ("fifteen MVA transformer", "TX-0388"),
    ("the 15MVA transformer at Calder Lane", "TX-0388"),
    ("Millbrook 15 MVA transformer", None),
    ("the 40 MVA transformer", None),
    ("the 1.2 km feeder 7 section", "CB-2208"),
    ("feeder 7, 2 km section", None),
]


def resolve(words, default="TX-0417"):
    return GRID._resolve(words, default, GRID._assets(), "id")


def outcome(result, key="id"):
    if result is None:
        return None
    if isinstance(result, list):
        return tuple(sorted(item[key] for item in result))
    return result[key]


@pytest.mark.parametrize("words, expected", ASSET_CORPUS, ids=[c[0] for c in ASSET_CORPUS])
def test_asset_resolver_corpus(words, expected):
    assert outcome(resolve(words)) == expected
    answer = GRID.GridAssetMaintenanceAgent().perform(operation="work_order_draft", asset=words)
    title = answer.splitlines()[0]
    if expected is None:
        assert title == "# Unknown Asset"
        assert "Work Order Draft" not in answer
    elif isinstance(expected, tuple):
        assert title == "# Which asset did you mean?"
        assert all(asset in answer for asset in expected)
    else:
        assert title == f"# Preventive Work Order Draft - {expected}"


def test_asset_resolver_empty_request_is_the_default():
    assert outcome(resolve("")) == "TX-0417"
    assert outcome(resolve(None, "SG-1123")) == "SG-1123"


# (request, default, expected work order) for completed jobs, which share the same resolver.
JOB_CORPUS = [
    ("Ashby Road panel 2", "WO-55097", "WO-55102"),
    ("Ashby Road panel 2", "WO-55102", "WO-55102"),
    ("Ashby Road panel 4", "WO-55097", None),
    ("Ashby Road panel two", "WO-55097", "WO-55102"),
    ("Mill Lane joint", "WO-55102", "WO-55097"),
]


@pytest.mark.parametrize("words, default, expected", JOB_CORPUS, ids=[f"{c[0]}|{c[1]}" for c in JOB_CORPUS])
def test_completed_job_resolver_corpus(words, default, expected):
    jobs = GRID._completed_jobs()
    assert outcome(GRID._resolve(words, default, jobs, "work_order"), "work_order") == expected
