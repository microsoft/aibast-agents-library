"""
Procurement and Supplier Collaboration Agent for Energy and Utilities.

Read-only procurement support for an electricity distribution company's buyers, category managers, supplier
quality and accounts payable teams, built on a synthetic snapshot of its source-to-pay records for network
materials: requisitions raised from the maintenance plan, capital projects and stock replenishment, the
recommended procurement route and eligible supplier shortlist, answers to supplier questions from the published
request for quotation (RFQ) pack, weighted bid scoring, purchase order acknowledgement and advance shipping
notice (ASN) tracking, and the three-way match of purchase order, goods receipt and invoice. Today the snapshot
is a set of constants; in production the same accessors read the Dataverse tables that Power Automate fills from
the ERP and the Power Apps supplier portal. Every award, order, message and payment is a draft for an authorized
person to approve.
"""

import sys
import os
import re
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/procurement-supplier-collaboration",
    "version": "1.0.0",
    "display_name": "Procurement and Supplier Collaboration Agent",
    "description": "Run a utility's source-to-pay cycle for network materials from a synthetic snapshot: requisitions from the maintenance plan, capital projects and stock replenishment with the recommended route (framework direct award, mini-competition or open tender) and eligible supplier shortlist, answers to supplier questions from the published RFQ pack, weighted bid scoring with a ranked recommendation, purchase order acknowledgement and ASN delivery deviations, and the three-way match of purchase order, goods receipt and invoice. The agent never awards, orders, messages a supplier or approves a payment; an authorized person approves every step through future authenticated tools.",
    "author": "AIBAST",
    "tags": ["procurement", "sourcing", "supplier-collaboration", "bid-evaluation", "three-way-match", "energy", "utilities"],
    "category": "energy",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---- DATA PLANE ------------------------------------------------------------
# Synthetic today; swap this block for the Dataverse tables that Power Automate fills from the ERP (requisitions,
# frameworks, purchase orders, goods receipts, invoices) and the Power Apps supplier portal (RFQs, questions, bids,
# acknowledgements, ASNs). Nothing below this block reads the constants directly; it calls _policy(),
# _requisitions(), _suppliers(), _rfqs(), _bids(), _orders() and _invoices().

COMPANY = "Northcombe Power Distribution"

# Route rules: a framework order up to the direct-award limit is a direct award; above it, a mini-competition among
# the framework's suppliers; with no framework, an open tender above the tender threshold, otherwise three quotes.
# Shortlist rules: active framework supplier, on-time-in-full at or above the floor, no open major nonconformance.
POLICY = {"direct_award_limit": 250000, "open_tender_threshold": 500000, "otif_floor": 90,
          "price_tolerance_pct": 2, "weights": {"price": 50, "lead_time": 20, "quality": 20, "sustainability": 10}}

REQUISITIONS = [
    {"id": "REQ-7712", "item": "Distribution transformer, 500 kVA 11/0.433 kV", "qty": 24, "unit_estimate": 28000,
     "source": "Stock replenishment model: Central Stores below reorder point (6 on hand, 30-unit reorder level)",
     "framework": "FW-DT-22", "category": "Distribution transformers", "critical": True, "need_in_days": 126,
     "keywords": ["req-7712", "transformer", "500 kva"]},
    {"id": "REQ-7710", "item": "33 kV XLPE cable, 3 x 300 mm2", "qty": "6 km", "unit_estimate": None,
     "value": 1380000, "source": "Capital project: Fenwick 33 kV reinforcement", "framework": None,
     "category": "HV cable", "critical": True, "need_in_days": 160,
     "keywords": ["req-7710", "33 kv cable", "xlpe", "cable", "fenwick"]},
    {"id": "REQ-7715", "item": "Pole-top fuse kit, 11 kV", "qty": 400, "unit_estimate": 95,
     "source": "Maintenance plan: overhead line refurbishment, quarter 1", "framework": "FW-OH-19",
     "category": "Overhead line fittings", "critical": False, "need_in_days": 45,
     "keywords": ["req-7715", "fuse", "pole-top"]},
]

SUPPLIERS = [
    {"name": "Brightwater Transformers", "framework": "FW-DT-22", "otif": 97, "open_ncr": "None"},
    {"name": "Halden Transformer Works", "framework": "FW-DT-22", "otif": 94, "open_ncr": "None"},
    {"name": "Kelso Electrical Supply", "framework": "FW-DT-22", "otif": 92, "open_ncr": "1 minor"},
    {"name": "Marlow Power Products", "framework": "FW-DT-22", "otif": 84, "open_ncr": "1 major (oil leaks)"},
    {"name": "Ferris Line Fittings", "framework": "FW-OH-19", "otif": 98, "open_ncr": "None"},
]

RFQS = [
    {"id": "RFQ-3301", "requisition": "REQ-7712", "route": "Mini-competition under framework FW-DT-22",
     "closes_in_days": 6, "invited": ["Brightwater Transformers", "Halden Transformer Works",
                                      "Kelso Electrical Supply"],
     "keywords": ["rfq-3301", "req-7712", "transformer", "distribution transformer", "500 kva", "fw-dt-22"],
     "pack": [
         {"topic": "Delivery lots", "keywords": ["lot", "deliver", "delivery", "split"],
          "answer": "Delivery is 24 units in three lots of 8 to Central Stores. Lot dates are set at award from each "
                    "bidder's quoted lead time. A different lot plan may be offered only as a variant bid under "
                    "section 5.3, alongside a compliant bid."},
         {"topic": "Specification", "keywords": ["spec", "specification", "vector", "dyn11", "loss", "rating"],
          "answer": "500 kVA, 11/0.433 kV, vector group Dyn11, losses as set in specification ES-DT-04 (no "
                    "tolerance on load losses)."},
         {"topic": "Quality documents", "keywords": ["iso", "certificate", "type test", "quality", "documents"],
          "anchors": ["iso", "certificate", "type test", "quality"],
          "answer": "Bids must include an ISO 9001 certificate and type test certificates for the offered design. "
                    "A bid missing a type test certificate scores half marks on quality."},
         {"topic": "Evaluation", "keywords": ["evaluate", "evaluated", "evaluation", "weight", "weighting", "score", "scored",
                                                    "scoring", "criteria"],
          "anchors": ["evaluate", "evaluation", "weight", "weighting", "score", "scoring", "criteria", "marks"],
          "answer": "Price 50%, lead time 20%, quality 20%, sustainability 10%."},
         {"topic": "Closing date", "keywords": ["close", "closing", "deadline", "extension", "due"],
          "answer": "The RFQ closes at 12:00 on the closing day shown in the portal. Extensions apply to all "
                    "bidders and are published as a clarification."},
     ],
     "clarifications": [
         {"id": "CL-1", "question": "Is a sealed tank design acceptable?",
          "answer": "Yes, if it meets ES-DT-04; published to all bidders.",
          "keywords": ["sealed tank", "sealed"]},
     ],
     # Subjects the published pack and its clarifications are silent on. A question that raises one of them is a
     # new clarification for every bidder, even when it also contains a word the pack does cover ('payment due
     # after delivery' is about payment, not the closing date or the delivery lots). A subject is raised two ways:
     # by a keyword that only that subject uses ('insurance', 'payment terms'), or by a pair: a subject word
     # ('risk', 'pay', 'download') and a word that frames it as that subject ('bears', 'until', 'where') in the
     # same sentence, in any order and any common word form. A common word on its own ('pay attention', 'the risk
     # of half marks', 'access to our certificate', 'the title of the specification') says nothing about the
     # subject and must not turn a question the pack answers into a new clarification.
     #
     # A pair is a weak reading: its words are everyday English. A pack topic's "anchors" are the words that make a
     # question about how a bid is assessed (its score, weights, marks, certificates, quality). When the question
     # names an anchor, the everyday reading wins over a pair: 'a risk of a lower score', 'how much weight do you
     # pay', 'the panel access our certificate through the portal', 'marks lost until the certificate arrives'.
     # A subject's own keyword is a strong reading and always wins ('Is the warranty scored?' is about warranty).
    "not_covered": [
        {"subject": "payment terms",
         "keywords": ["payment", "invoice", "invoicing", "retention", "deposit", "upfront", "pay us", "paid us",
                      "pay the supplier", "be paid", "get paid"],
         "pairs": [[["pay", "paid"],
                    ["us", "supplier", "suppliers", "when", "soon", "after", "within", "before", "advance",
                     "upfront", "on delivery", "on receipt", "day", "week", "month", "net", "terms"]]]},
        {"subject": "access to the tender documents",
         "keywords": ["portal access", "portal login", "log in", "login", "password", "download link"],
         "pairs": [[["download", "access"],
                    ["where", "how do i", "how can i", "cannot", "can't", "unable", "link", "portal",
                     "tender documents", "rfq documents", "tender pack", "rfq pack"]]]},
        {"subject": "risk, insurance and liability",
         "keywords": ["insurance", "insured", "insure", "liability", "liable", "incoterm", "in transit",
                      "transit risk", "title transfer", "transfer of title", "passing of title"],
         "pairs": [[["risk", "lost", "damage", "damaged", "title"],
                    ["bear", "bore", "borne", "carry", "hold", "pass", "transfer", "responsible",
                     "who pays", "who covers", "covered", "until", "during delivery", "on delivery",
                     "after delivery", "before delivery", "transit", "ship", "shipped", "shipping", "shipment",
                     "arrive", "arrival", "unloading"]]]},
         {"subject": "splitting the award between suppliers", "keywords": [
             "two suppliers", "multiple suppliers", "several suppliers", "more than one supplier",
             "between suppliers", "split award", "dual award", "joint bid", "consortium", "subcontract"]},
         {"subject": "conservator tank designs", "keywords": ["conservator"]},
         {"subject": "warranty", "keywords": ["warranty", "guarantee", "defects liability"]},
         {"subject": "price adjustment and currency", "keywords": ["price adjustment", "indexation", "index-linked",
                                                                  "currency", "exchange rate", "escalation"]},
         {"subject": "penalties", "keywords": ["penalty", "liquidated damages"]},
         {"subject": "the budget", "keywords": ["budget"]},
     ]},
]

# Bids received for RFQ-3301; lead_weeks from order; sustainability is the evaluator's 0-10 score.
BIDS = [
    {"rfq": "RFQ-3301", "supplier": "Brightwater Transformers", "price": 648000, "lead_weeks": 9,
     "quality_complete": True, "sustainability": 9, "sustainability_note": "Environmental product declaration; "
     "30% recycled core steel"},
    {"rfq": "RFQ-3301", "supplier": "Halden Transformer Works", "price": 630000, "lead_weeks": 10,
     "quality_complete": True, "sustainability": 6, "sustainability_note": "Environmental product declaration"},
    {"rfq": "RFQ-3301", "supplier": "Kelso Electrical Supply", "price": 612000, "lead_weeks": 13,
     "quality_complete": False, "sustainability": 2, "sustainability_note": "None offered",
     "quality_gap": "Type test certificate missing for the offered design"},
]

# Purchase orders in flight; days are counted from today (negative = past).
ORDERS = [
    {"po": "PO-88017", "supplier": "Corran Cables", "item": "11 kV cable drums, 500 m", "qty": 6,
     "acknowledged": True, "committed_in_days": 4, "asn": {"qty": 4, "ship_in_days": 3, "arrive_in_days": 4},
     "remaining_note": "ASN shows the last 2 drums arriving in 13 days",
     "remaining_arrive_in_days": 13, "impact": "Feeder 7 section replacement at Harbour Street is planned to "
     "start in 10 days and needs all 6 drums on site", "keywords": ["po-88017", "corran", "cable drums"]},
    {"po": "PO-88044", "supplier": "Ardmore Switchgear", "item": "11 kV switchboard panels", "qty": 8,
     "acknowledged": False, "issued_days_ago": 5, "committed_in_days": 70, "asn": None,
     "impact": "Ashby Road switchboard replacement", "keywords": ["po-88044", "ardmore", "switchgear"]},
    {"po": "PO-88031", "supplier": "Ferris Line Fittings", "item": "Pole-top fuse kits, 11 kV", "qty": 400,
     "acknowledged": True, "committed_in_days": 12, "asn": {"qty": 400, "ship_in_days": 9, "arrive_in_days": 11},
     "impact": "Overhead line refurbishment", "keywords": ["po-88031", "ferris", "fuse"]},
]

INVOICES = [
    {"invoice": "INV-55120", "supplier": "Corran Cables", "po": "PO-88010", "item": "11 kV cable drums, 500 m",
     "po_qty": 4, "po_price": 41500, "gr_qty": 4, "inv_qty": 4, "inv_price": 41500,
     "keywords": ["inv-55120", "po-88010"]},
    {"invoice": "INV-55133", "supplier": "Halden Transformer Works", "po": "PO-88022",
     "item": "Distribution transformer, 315 kVA", "po_qty": 10, "po_price": 26800, "gr_qty": 9, "inv_qty": 10,
     "inv_price": 26800, "gr_note": "1 unit rejected at receipt: damaged radiator",
     "keywords": ["inv-55133", "po-88022", "halden"]},
    {"invoice": "INV-55141", "supplier": "Ferris Line Fittings", "po": "PO-88003", "item": "Line clamps, 33 kV",
     "po_qty": 200, "po_price": 61, "gr_qty": 200, "inv_qty": 200, "inv_price": 64,
     "keywords": ["inv-55141", "po-88003", "clamps"]},
]

DEFAULT_REQUISITION = "REQ-7712"
DEFAULT_RFQ = "RFQ-3301"
DEFAULT_QUESTION = "Can we deliver all 24 units in two lots instead of three?"


def _policy():
    """Replace with the procurement policy table. Everything downstream is unchanged."""
    return POLICY


def _requisitions():
    """Replace with the open requisitions query (ERP). Everything downstream is unchanged."""
    return REQUISITIONS


def _suppliers():
    """Replace with the framework supplier performance query. Everything downstream is unchanged."""
    return SUPPLIERS


def _rfqs():
    """Replace with the supplier portal RFQ and clarification tables. Everything downstream is unchanged."""
    return RFQS


def _bids():
    """Replace with the supplier portal bid table. Everything downstream is unchanged."""
    return BIDS


def _orders():
    """Replace with the open purchase order, acknowledgement and ASN query. Everything downstream is unchanged."""
    return ORDERS


def _invoices():
    """Replace with the invoices awaiting match (ERP). Everything downstream is unchanged."""
    return INVOICES

# ---- END DATA PLANE --------------------------------------------------------


BOUNDARY = ("> Read-only synthetic snapshot of a fictional utility. Nothing was awarded, ordered, sent to a supplier "
            "or approved for payment; an authorized person approves every step.")


def _now():
    return datetime.now()


def _date(days):
    return f"{_now() + timedelta(days=days):%d %b %Y}"


def _money(value):
    return f"${value:,.0f}"


def _value(req):
    return req.get("value") or req["qty"] * req["unit_estimate"]


def _route(req):
    policy = _policy()
    value = _value(req)
    if req["framework"]:
        if value <= policy["direct_award_limit"]:
            return f"Direct award under framework {req['framework']}", f"framework order up to {_money(policy['direct_award_limit'])}"
        return (f"Mini-competition under framework {req['framework']}",
                f"framework order above the {_money(policy['direct_award_limit'])} direct-award limit")
    if value > policy["open_tender_threshold"]:
        return "Open tender", f"no framework covers it and it is above the {_money(policy['open_tender_threshold'])} tender threshold"
    return "Three written quotes", "no framework covers it and it is below the tender threshold"


def _keyword_pattern(keyword):
    """Whole words, a hyphen or space between words optional, and the common endings on the last word.

    'close' must not hit 'disclose' and 'rating' must not hit 'operating' (the match starts on a word boundary),
    while 'weight' meets 'weighted', 'deliver' meets 'delivered', 'delivery' meets 'deliveries', 'loss' meets
    'losses' and 'nurse call' meets 'nurse-call'.
    """
    parts = [p for p in re.split(r"[\s-]+", keyword.strip().lower()) if p]
    last = parts[-1]
    if len(last) > 2 and last.endswith("y") and last[-2] not in "aeiou":
        tail = re.escape(last[:-1]) + r"(?:y|ies|ied)"
    else:
        tail = re.escape(last) + r"(?:s|es|d|ed|ing)?"
    return r"\b" + r"[\s-]*".join([re.escape(p) for p in parts[:-1]] + [tail]) + r"\b"


def _join(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _keyword_hit(keyword, text):
    """Whole-word match on the keyword or a common word form of it (see _keyword_pattern)."""
    return re.search(_keyword_pattern(keyword), text) is not None


def _raises(subject, text, anchored=False):
    """True when the question raises an off-pack subject: one of its own keywords anywhere, or a subject word and a
    framing word of one of its pairs in the same sentence ('who bears risk during delivery', 'risk passes on
    delivery', 'where can I download'), never a common word on its own ('the risk of half marks').

    anchored: the question names a pack anchor (it is about how a bid is assessed), so a pair, the weak everyday
    reading, does not raise the subject; only the subject's own keywords do."""
    if any(_keyword_hit(k, text) for k in subject.get("keywords", [])):
        return True
    if anchored:
        return False
    for sentence in re.split(r"[.?!;]+", text):
        for topic, frame in subject.get("pairs", []):
            if any(_keyword_hit(k, sentence) for k in topic) and any(_keyword_hit(k, sentence) for k in frame):
                return True
    return False


def _id_named(item_id, text):
    """True when the id appears anywhere in the text, with its hyphen, a space or nothing: 'REQ-7712', 'req 7712'
    and 'req7712' all name REQ-7712."""
    parts = [re.escape(p) for p in str(item_id).lower().split("-") if p]
    return re.search(r"\b" + r"[\s-]?".join(parts) + r"\b", text) is not None


def _find(value, default, items, key):
    """Id or words; empty -> the default; no match -> None; a tie -> the tied records (a list).

    Keywords match whole words only, and each record scores the words in the keywords it matches, so 'Fenwick
    cable' finds the cable requisition and a request that fits two records equally is asked about, not guessed.
    """
    if not value:
        return next(i for i in items if i[key] == default)
    q = str(value).lower().strip()
    for item in items:
        if q == item[key].lower():
            return item
    named = [item for item in items if _id_named(item[key], q)]
    if named:
        return named[0] if len(named) == 1 else named
    scores = []
    for item in items:
        score = sum(len(k.split()) for k in item.get("keywords", []) if _keyword_hit(k, q))
        if score:
            scores.append((score, item))
    if not scores:
        return None
    best = max(score for score, _ in scores)
    tied = [item for score, item in scores if score == best]
    return tied[0] if len(tied) == 1 else tied


def _scores(rfq_id):
    weights = _policy()["weights"]
    bids = [b for b in _bids() if b["rfq"] == rfq_id]
    low = min(b["price"] for b in bids)
    fast = min(b["lead_weeks"] for b in bids)
    rows = []
    for b in bids:
        price = weights["price"] * low / b["price"]
        lead = weights["lead_time"] * fast / b["lead_weeks"]
        quality = weights["quality"] * (1 if b["quality_complete"] else 0.5)
        sustain = weights["sustainability"] * b["sustainability"] / 10
        rows.append({**b, "s_price": price, "s_lead": lead, "s_quality": quality, "s_sust": sustain,
                     "total": price + lead + quality + sustain})
    return sorted(rows, key=lambda r: -r["total"])


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

OPERATIONS = ["sourcing_plan", "supplier_query", "bid_evaluation", "delivery_tracking", "invoice_match"]


class ProcurementSupplierCollaborationAgent(BasicAgent):
    """Source-to-pay agent for network materials with a supplier portal (read-only, synthetic)."""

    def __init__(self):
        self.name = "ProcurementSupplierCollaborationAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Answers source-to-pay questions for the utility's network materials: which requisitions are open "
                "and which procurement route and supplier shortlist each needs, what to tell a supplier who asks a "
                "question about an open RFQ, how the bids score and which supplier ranks first, which purchase "
                "orders are unacknowledged or have delivery deviations against the committed date, and which "
                "invoices pass the three-way match. Always call this tool for requisition, sourcing route, RFQ, "
                "supplier question, bid, purchase order, ASN, delivery, goods receipt or invoice match questions "
                "from buyers, category managers, expediters and accounts payable. Call it right away; every "
                "operation has demo defaults. It is read-only: it drafts but never awards, orders, messages a "
                "supplier or approves a payment, so never offer to do those."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(OPERATIONS),
                        "description": (
                            "sourcing_plan for open requisitions with the recommended route (framework direct "
                            "award, mini-competition or open tender) and the eligible supplier shortlist; "
                            "supplier_query to draft the answer to a supplier's question about an open RFQ from "
                            "the published pack; bid_evaluation for weighted bid scores across price, lead time, "
                            "quality and sustainability with a ranked recommendation; delivery_tracking for "
                            "purchase order acknowledgements and ASN delivery deviations; invoice_match for the "
                            "three-way match of purchase order, goods receipt and invoice."
                        ),
                    },
                    "requisition": {
                        "type": "string",
                        "description": "Requisition id such as REQ-7712 or words such as 'transformers'. Optional; "
                                       "the shortlist defaults to REQ-7712.",
                    },
                    "rfq": {
                        "type": "string",
                        "description": "RFQ id such as RFQ-3301 or words such as 'transformer RFQ'. Optional; "
                                       "defaults to RFQ-3301.",
                    },
                    "question": {
                        "type": "string",
                        "description": "The supplier's question in their words. Optional; defaults to a question "
                                       "about delivering in two lots.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "sourcing_plan")
        handlers = {
            "sourcing_plan": self._sourcing_plan,
            "supplier_query": self._supplier_query,
            "bid_evaluation": self._bid_evaluation,
            "delivery_tracking": self._delivery_tracking,
            "invoice_match": self._invoice_match,
        }
        handler = handlers.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`. Operations: {', '.join(OPERATIONS)}."
        return handler(**kwargs)

    # -- sourcing_plan ----------------------------------------------------------
    def _sourcing_plan(self, **kwargs) -> str:
        focus = _find(kwargs.get("requisition"), DEFAULT_REQUISITION, _requisitions(), "id")
        if focus is None:
            return self._unknown("requisition", kwargs.get("requisition"), [r["id"] for r in _requisitions()])
        if isinstance(focus, list):
            return self._ambiguous("requisition", kwargs.get("requisition"),
                                   [f"{r['id']} ({r['item']})" for r in focus])
        policy = _policy()
        lines = [f"# Sourcing Plan - {COMPANY}", "",
                 f"**Open requisitions:** {len(_requisitions())} | **Shortlist shown for:** {focus['id']}", "",
                 "| Requisition | Item | Quantity | Estimated value | Demand source | Need by | Recommended route |",
                 "|-------------|------|----------|-----------------|---------------|---------|-------------------|"]
        for r in _requisitions():
            route, _ = _route(r)
            lines.append(f"| {r['id']} | {r['item']} | {r['qty']} | {_money(_value(r))} | {r['source']} | "
                         f"{_date(r['need_in_days'])} | {route} |")
        route, why = _route(focus)
        lines += ["", f"## {focus['id']}: {route}", f"Why: {why}."
                  + (" Critical network material." if focus["critical"] else "")]
        if focus["framework"]:
            lines += ["", f"**Eligible supplier shortlist (framework {focus['framework']}):**", "",
                      "| Supplier | On-time in full | Open nonconformance | Eligible |",
                      "|----------|-----------------|---------------------|----------|"]
            for s in _suppliers():
                if s["framework"] != focus["framework"]:
                    continue
                reasons = []
                if s["otif"] < policy["otif_floor"]:
                    reasons.append(f"on-time in full below {policy['otif_floor']}%")
                if "major" in s["open_ncr"]:
                    reasons.append("open major nonconformance")
                verdict = "Yes" if not reasons else "No: " + "; ".join(reasons)
                lines.append(f"| {s['name']} | {s['otif']}% | {s['open_ncr']} | {verdict} |")
        else:
            lines += ["", "No framework covers this category; the tender is advertised openly and any qualified "
                          "supplier may bid."]
        lines += ["", "**Status:** Recommendation - the category manager confirms the route and shortlist before "
                      "the RFQ is issued in the supplier portal. Nothing has been issued.", "", BOUNDARY]
        return "\n".join(lines)

    # -- supplier_query ---------------------------------------------------------
    def _supplier_query(self, **kwargs) -> str:
        rfq = _find(kwargs.get("rfq"), DEFAULT_RFQ, _rfqs(), "id")
        if rfq is None:
            return self._unknown("RFQ", kwargs.get("rfq"), [r["id"] for r in _rfqs()])
        if isinstance(rfq, list):
            return self._ambiguous("RFQ", kwargs.get("rfq"), [f"{r['id']} ({r['route']})" for r in rfq])
        question = (kwargs.get("question") or DEFAULT_QUESTION).strip()
        q = question.lower()
        exact = [c for c in rfq["clarifications"] if q.rstrip("?. ") == c["question"].lower().rstrip("?. ")]
        hits = [p for p in rfq["pack"] if any(_keyword_hit(k, q) for k in p["keywords"])]
        asked_before = exact or [c for c in rfq["clarifications"]
                                 if any(_keyword_hit(k, q) for k in c.get("keywords", []))]
        # One incidental pack word does not answer a question about a subject the pack is silent on: the whole
        # question goes to every bidder as a new clarification; related pack text is shown only as context (the
        # published clarifications are listed below in any case).
        anchored = any(_keyword_hit(k, q) for p in rfq["pack"] for k in p.get("anchors", []))
        uncovered = [] if exact else [u["subject"] for u in rfq.get("not_covered", []) if _raises(u, q, anchored)]
        lines = [f"# Supplier Question - {rfq['id']}", "",
                 f"**RFQ:** {rfq['id']} ({rfq['route']}), closes {_date(rfq['closes_in_days'])} "
                 f"(in {rfq['closes_in_days']} days)",
                 f"**Question:** \"{question}\"", ""]
        if uncovered:
            lines += ["**Not answered by the published RFQ pack.** The question asks about "
                      f"{_join(uncovered)}, which neither the pack nor any published clarification covers. Draft "
                      f"for the buyer: log it as a new clarification (CL-{len(rfq['clarifications']) + 1}) and "
                      f"publish the answer to all {len(rfq['invited'])} invited bidders, so every bidder works "
                      "from the same information. Do not send a partial answer to this supplier alone."]
            related = [f"- **{p['topic']}:** {p['answer']}" for p in hits]
            if related:
                lines += ["", "**Related published text (context for the buyer; it does not answer the whole "
                              "question):**"] + related
            hits, asked_before = [], []
        elif hits:
            lines += ["## Draft answer from the published RFQ pack"]
            lines += [f"- **{p['topic']}:** {p['answer']}" for p in hits]
            lines += ["", "Because the answer is already in the published pack, it can go to this supplier without "
                          "changing the terms for other bidders."]
        if asked_before:
            if hits:
                lines += [""]
            lines += [f"## Already answered in published clarification {', '.join(c['id'] for c in asked_before)}"]
            lines += [f"- **{c['id']}:** {c['question']} {c['answer']}" for c in asked_before]
            lines += ["", "This answer has already been published to all bidders, so the same reply can go to this "
                          "supplier. No new clarification is needed."]
        if not hits and not asked_before and not uncovered:
            lines += ["**Not answered by the published RFQ pack.** Draft for the buyer: log it as a new "
                      f"clarification (CL-{len(rfq['clarifications']) + 1}) and publish the answer to all "
                      f"{len(rfq['invited'])} invited bidders, so every bidder works from the same information."]
        lines += ["", "**Clarifications already published to all bidders:** "
                  + "; ".join(f"{c['id']} {c['question']} {c['answer']}" for c in rfq["clarifications"]),
                  "", "**Status:** Draft - the buyer approves and sends the reply in the supplier portal. Nothing "
                      "has been sent.", "", BOUNDARY]
        return "\n".join(lines)

    # -- bid_evaluation ---------------------------------------------------------
    def _bid_evaluation(self, **kwargs) -> str:
        rfq = _find(kwargs.get("rfq"), DEFAULT_RFQ, _rfqs(), "id")
        if rfq is None:
            return self._unknown("RFQ", kwargs.get("rfq"), [r["id"] for r in _rfqs()])
        if isinstance(rfq, list):
            return self._ambiguous("RFQ", kwargs.get("rfq"), [f"{r['id']} ({r['route']})" for r in rfq])
        weights = _policy()["weights"]
        rows = _scores(rfq["id"])
        top, runner = rows[0], rows[1]
        cheapest = min(rows, key=lambda r: r["price"])
        lines = [f"# Bid Evaluation - {rfq['id']}", "",
                 f"**Weights:** price {weights['price']}, lead time {weights['lead_time']}, quality "
                 f"{weights['quality']}, sustainability {weights['sustainability']} | **Bids:** {len(rows)}", "",
                 "| Rank | Supplier | Price | Lead time | Quality | Sustainability | Score |",
                 "|------|----------|-------|-----------|---------|----------------|-------|"]
        for i, r in enumerate(rows, 1):
            quality = "Complete" if r["quality_complete"] else "Incomplete"
            lines.append(f"| {i} | {r['supplier']} | {_money(r['price'])} ({r['s_price']:.1f}) | "
                         f"{r['lead_weeks']} weeks ({r['s_lead']:.1f}) | {quality} ({r['s_quality']:.1f}) | "
                         f"{r['sustainability']}/10 ({r['s_sust']:.1f}) | **{r['total']:.1f}** |")
        lines += ["", "## Evaluation narrative",
                  f"- **{top['supplier']}** ranks first at {top['total']:.1f}, {top['total'] - runner['total']:.1f} "
                  f"points ahead of {runner['supplier']}: {top['lead_weeks']}-week lead time, complete quality "
                  f"documents, and {top['sustainability_note'].lower()}."]
        if cheapest is not top:
            lines.append(f"- **{cheapest['supplier']}** is the lowest price at {_money(cheapest['price'])} "
                         f"({_money(top['price'] - cheapest['price'])} below the first-ranked bid) but scores lower"
                         + (f": {cheapest['quality_gap'].lower()}" if cheapest.get("quality_gap") else "")
                         + f" and a {cheapest['lead_weeks']}-week lead time.")
        lines += [f"- Recommended award: {top['supplier']} at {_money(top['price'])}, subject to the award panel.",
                  "", "**Status:** Recommendation - the award panel decides and records the award. No supplier "
                      "has been told the outcome.", "", BOUNDARY]
        return "\n".join(lines)

    # -- delivery_tracking ------------------------------------------------------
    def _delivery_tracking(self, **kwargs) -> str:
        alerts, on_track = [], []
        for o in _orders():
            if not o["acknowledged"]:
                alerts.append((o, f"Not acknowledged {o['issued_days_ago']} days after issue; the committed date "
                                  f"{_date(o['committed_in_days'])} is unconfirmed. Draft a reminder to "
                                  f"{o['supplier']}."))
                continue
            asn = o["asn"]
            late = o.get("remaining_arrive_in_days", asn["arrive_in_days"]) - o["committed_in_days"]
            if asn["qty"] < o["qty"] or late > 0:
                alerts.append((o, f"ASN covers {asn['qty']} of {o['qty']} arriving {_date(asn['arrive_in_days'])}; "
                                  f"{o['remaining_note']} ({_date(o['remaining_arrive_in_days'])}), {late} days after "
                                  f"the committed {_date(o['committed_in_days'])}. Impact: {o['impact']}."))
            else:
                on_track.append(o)
        lines = [f"# Delivery Tracking - {COMPANY}", "",
                 f"**Open purchase orders:** {len(_orders())} | **Needing action:** {len(alerts)} | "
                 f"**On track:** {len(on_track)}", "", "## Needing action"]
        for o, text in alerts:
            lines.append(f"- **{o['po']}** {o['supplier']}, {o['item']} x{o['qty']}: {text}")
        lines += ["", "## On track"]
        for o in on_track:
            lines.append(f"- {o['po']} {o['supplier']}, {o['item']} x{o['qty']}: ASN matches, arriving "
                         f"{_date(o['asn']['arrive_in_days'])} against {_date(o['committed_in_days'])}.")
        lines += ["", "**Status:** Alerts only - the buyer contacts suppliers and the project team re-plans. No "
                      "message was sent and no order was changed.", "", BOUNDARY]
        return "\n".join(lines)

    # -- invoice_match ----------------------------------------------------------
    def _invoice_match(self, **kwargs) -> str:
        tol = _policy()["price_tolerance_pct"]
        lines = [f"# Three-Way Match - {COMPANY}", "",
                 f"**Invoices awaiting match:** {len(_invoices())} | **Price tolerance:** {tol}%", "",
                 "| Invoice | Supplier | PO | PO qty | Received | Invoiced | PO unit price | Invoiced unit price | "
                 "Invoice total | Result |",
                 "|---------|----------|----|--------|----------|----------|---------------|---------------------|"
                 "---------------|--------|"]
        notes = []
        for inv in _invoices():
            issues = []
            if inv["inv_qty"] > inv["gr_qty"]:
                issues.append(f"invoiced {inv['inv_qty']} but received {inv['gr_qty']}")
            variance = (inv["inv_price"] - inv["po_price"]) / inv["po_price"] * 100
            if abs(variance) > tol:
                issues.append(f"price {variance:+.1f}% against the PO, outside the {tol}% tolerance")
            result = "Matched: ready for payment approval" if not issues else "Hold"
            lines.append(f"| {inv['invoice']} | {inv['supplier']} | {inv['po']} | {inv['po_qty']} | {inv['gr_qty']} | "
                         f"{inv['inv_qty']} | {_money(inv['po_price'])} | {_money(inv['inv_price'])} | "
                         f"{_money(inv['inv_qty'] * inv['inv_price'])} | {result} |")
            if issues:
                extra = f" ({inv['gr_note']})" if inv.get("gr_note") else ""
                hold = inv["inv_qty"] * inv["inv_price"] - min(inv["inv_qty"], inv["gr_qty"]) * inv["po_price"]
                notes.append(f"- **{inv['invoice']}** {inv['supplier']}: {'; '.join(issues)}{extra}. Amount in "
                             f"question {_money(hold)}. Draft: ask the supplier for a credit note or corrected "
                             "invoice.")
        lines += ["", "## Holds"] + notes
        lines += ["", "**Status:** Draft - accounts payable approves matched invoices for payment in the finance "
                      "module and resolves holds with the supplier. Nothing has been paid or sent.", "", BOUNDARY]
        return "\n".join(lines)

    def _ambiguous(self, kind, value, candidates) -> str:
        return (f"# Which {kind} did you mean?\n\n`{value}` matches more than one {kind} equally well, so none was "
                f"picked. Name one of these by its id:\n\n" + "\n".join(f"- {c}" for c in candidates)
                + f"\n\n{BOUNDARY}")

    def _unknown(self, kind, value, ids) -> str:
        return (f"# Unknown {kind}\n\nNo {kind} in the synthetic snapshot matches `{value}`; no substitute was "
                f"used. Known: {', '.join(ids)}.\n\n{BOUNDARY}")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = ProcurementSupplierCollaborationAgent()
    for op in OPERATIONS:
        print(f"\n{'=' * 60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
