"""
Supplier Claim Engagement Agent

Retail supplier-claims assistant: the open claims queue, claim triage against
supplier service terms, evidence-pack assembly, a draft claim notice to the
supplier, response-deadline tracking, evaluation of a supplier's response, and an
escalation brief for a missed deadline.

Where a real deployment would call the order system, receiving records, a case
system, and email, this agent uses a fixed synthetic snapshot for the fictional
Fabrikam Grocers so it runs anywhere without credentials. It never sends a claim,
accepts a credit, or escalates; it returns reviewable drafts.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/supplier-claim-engagement",
    "version": "1.0.0",
    "display_name": "Supplier Claim Engagement Agent",
    "description": "Help retail claims teams recover more from suppliers by triaging damage, shortage, quality, and pricing claims, assembling evidence packs, drafting supplier claim notices, tracking response deadlines, and evaluating supplier responses, while every send, credit acceptance, and escalation stays with an authorized coordinator.",
    "author": "AIBAST",
    "tags": ["retail", "supplier", "claims", "returns", "service-levels", "retail-cpg"],
    "category": "retail_cpg",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER (fixed snapshot: Fabrikam Grocers, Apr 14, 2026 10:00)
# ═══════════════════════════════════════════════════════════════

_RETAILER = "Fabrikam Grocers"
_NOW = (2026, 4, 14, 10)          # fixed demo clock: Tue Apr 14, 2026 10:00
_NOW_LABEL = "Apr 14, 2026 10:00"

# Response window (hours) and resolution window (business days) by claim type.
_TERMS = {
    "Quality": {"severity": "P1 - Critical", "response_h": 8, "resolve_bd": 3},
    "Damage": {"severity": "P2 - High", "response_h": 24, "resolve_bd": 5},
    "Shortage": {"severity": "P3 - Medium", "response_h": 36, "resolve_bd": 7},
    "Pricing": {"severity": "P4 - Low", "response_h": 60, "resolve_bd": 10},
}

_REQUIRED_EVIDENCE = {
    "Damage": ["Damage photos (2 or more)", "Receiving inspection report", "Delivery note signed with exception"],
    "Shortage": ["Delivery note signed with exception", "Receiving count sheet"],
    "Quality": ["Temperature log", "Receiving inspection report", "Product photos (2 or more)"],
    "Pricing": ["Purchase order price", "Supplier invoice", "Agreed price list"],
}

_CLAIMS = {
    "CLM-5201": {
        "id": "CLM-5201", "type": "Damage", "supplier": "Northwind Packaging", "po": "PO-77310",
        "store": "Distribution Center 2", "delivered": "Apr 10, 2026", "status": "Ready to draft",
        "lines": [("Sparkling water 12-pack", 18, 21.50), ("Pasta sauce glass jars, case of 12", 6, 34.00)],
        "evidence": {"Damage photos (2 or more)": "3 photos", "Receiving inspection report": "RIR-4471",
                     "Delivery note signed with exception": "DN-90318"},
        "sent_hour": None, "response": None,
    },
    "CLM-5202": {
        "id": "CLM-5202", "type": "Shortage", "supplier": "Tailspin Freight", "po": "PO-77288",
        "store": "Distribution Center 1", "delivered": "Apr 9, 2026", "status": "Sent, awaiting response",
        "lines": [("Whole-grain cereal, case of 10", 12, 28.75)],
        "evidence": {"Delivery note signed with exception": "DN-90207", "Receiving count sheet": "RC-2215"},
        "sent_hour": -38, "response": None,
    },
    "CLM-5203": {
        "id": "CLM-5203", "type": "Quality", "supplier": "Alpine Dairy Co-op", "po": "PO-77295",
        "store": "Distribution Center 2", "delivered": "Apr 13, 2026", "status": "Sent, awaiting response",
        "lines": [("Greek yogurt cups, case of 24", 32, 19.40)],
        "evidence": {"Temperature log": "TL-0412", "Receiving inspection report": "RIR-4466",
                     "Product photos (2 or more)": "4 photos"},
        "sent_hour": -7, "response": None,
    },
    "CLM-5204": {
        "id": "CLM-5204", "type": "Pricing", "supplier": "Litware Snacks", "po": "PO-77251",
        "store": "All stores", "delivered": "Apr 6, 2026", "status": "Supplier responded",
        "lines": [("Kettle chips, case of 24 (invoiced 16.90 vs agreed 15.40)", 50, 1.50)],
        "evidence": {"Purchase order price": "PO-77251", "Supplier invoice": "INV-L-6620",
                     "Agreed price list": "Price list effective Jan 5, 2026"},
        "sent_hour": -68, "response": {"received": "Apr 13, 2026 09:00", "hours_to_respond": 43,
                                       "position": "Partial acceptance", "accepted_units": 30,
                                       "reason": "Supplier says 20 cases shipped before the new price list took effect"},
    },
    "CLM-5205": {
        "id": "CLM-5205", "type": "Damage", "supplier": "Northwind Packaging", "po": "PO-77104",
        "store": "Distribution Center 1", "delivered": "Mar 27, 2026", "status": "Closed - credit received",
        "lines": [("Olive oil bottles, case of 6", 10, 41.00)],
        "evidence": {"Damage photos (2 or more)": "2 photos", "Receiving inspection report": "RIR-4398",
                     "Delivery note signed with exception": "DN-89955"},
        "sent_hour": None, "response": None, "recovered": 410.00,
    },
}

_ESCALATION_ROLE = "Category manager, pantry and beverages"

_GATE = (
    "Synthetic claims evidence only. This agent does not send a claim, contact a "
    "supplier, accept or reject a credit, escalate, or change a case; an authorized "
    "claims coordinator reviews every draft."
)
_SOURCE = "Source: [Synthetic Fabrikam Grocers Claims Snapshot]\nAgents: SupplierClaimEngagementAgent"

_OPERATIONS = [
    "claims_queue", "triage_claim", "evidence_pack", "draft_supplier_claim",
    "sla_tracker", "supplier_response", "escalation_brief",
]

_DEFAULT_CLAIM = {
    "triage_claim": "CLM-5201", "evidence_pack": "CLM-5201", "draft_supplier_claim": "CLM-5201",
    "supplier_response": "CLM-5204", "escalation_brief": "CLM-5202",
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _usd(amount):
    return f"${amount:,.2f}"


def _value(c):
    return round(sum(qty * unit for _, qty, unit in c["lines"]), 2)


def _resolve_claim(query, default_key):
    """Claim id such as CLM-5201 (any case); None when nothing matches (never another claim)."""
    if not query:
        return default_key
    q = str(query).strip().upper()
    return q if q in _CLAIMS else None


def _add_hours(hours):
    """Fixed demo clock plus hours -> 'Apr 15, 2026 10:00'."""
    import datetime
    t = datetime.datetime(*_NOW) + datetime.timedelta(hours=hours)
    return f"{t:%b} {t.day}, {t.year} {t:%H:%M}"


def _add_business_days(days):
    import datetime
    d = datetime.date(_NOW[0], _NOW[1], _NOW[2])
    while days > 0:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5:
            days -= 1
    return f"{d:%b} {d.day}, {d.year}"


def _sla(c):
    """(elapsed, remaining, status) for a sent claim with no response yet."""
    window = _TERMS[c["type"]]["response_h"]
    if c["response"]:
        return c["response"]["hours_to_respond"], window - c["response"]["hours_to_respond"], "Responded within window"
    if c["sent_hour"] is None:
        return None, window, "Not sent"
    elapsed = -c["sent_hour"]
    remaining = window - elapsed
    if remaining < 0:
        return elapsed, remaining, f"Breached by {-remaining} h"
    if remaining <= window * 0.25:
        return elapsed, remaining, f"At risk ({remaining} h left)"
    return elapsed, remaining, f"On track ({remaining} h left)"


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class SupplierClaimEngagementAgent(BasicAgent):
    """
    Supplier-claims coordinator assistant over a fixed synthetic snapshot.

    Operations:
        claims_queue          - open claims, values, severity and recovery to date
        triage_claim          - severity, responsible supplier and service terms for a claim
        evidence_pack         - required evidence, what is on file, claim value by line
        draft_supplier_claim  - draft claim notice to the supplier (Not Sent)
        sla_tracker           - response-window status across sent claims
        supplier_response     - compare a supplier's recorded response with the claim
        escalation_brief      - draft escalation for a claim past its response window
    """

    def __init__(self):
        self.name = "SupplierClaimEngagementAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Answers supplier-claim questions for the fictional retailer Fabrikam Grocers "
                "from a fixed synthetic snapshot (Apr 14, 2026 10:00). Use it for the open "
                "supplier claims queue, triaging a damaged, short, quality or pricing claim, "
                "what evidence a claim has, drafting the claim notice to a supplier, which "
                "claims are at risk of missing the supplier response deadline, what a "
                "supplier's response means, and an escalation for a claim past its deadline. "
                "Claims are CLM-5201 to CLM-5205. Call it first: every operation has demo "
                "defaults, so no claim id is needed to start. It never sends, accepts, or "
                "escalates anything; it returns drafts for an authorized coordinator."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "claims_queue for open claims or the claims overview; triage_claim "
                            "for severity, which supplier is responsible, or service terms; "
                            "evidence_pack for photos, documents, or claim value; "
                            "draft_supplier_claim to prepare or draft the claim to the supplier; "
                            "sla_tracker for deadlines, response windows, or claims at risk; "
                            "supplier_response for what a supplier replied or offered; "
                            "escalation_brief for escalating a late or overdue claim."
                        ),
                    },
                    "claim_id": {
                        "type": "string",
                        "enum": list(_CLAIMS),
                        "description": "Claim id such as 'CLM-5201' (optional; each operation has a demo default)",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation") or "claims_queue"
        handlers = {
            "claims_queue": self._claims_queue,
            "triage_claim": self._triage_claim,
            "evidence_pack": self._evidence_pack,
            "draft_supplier_claim": self._draft_supplier_claim,
            "sla_tracker": self._sla_tracker,
            "supplier_response": self._supplier_response,
            "escalation_brief": self._escalation_brief,
        }
        handler = handlers.get(op)
        if not handler:
            return f"Unknown operation: {op}. Choose one of: {', '.join(_OPERATIONS)}."
        if op not in _DEFAULT_CLAIM:
            return handler()
        key = _resolve_claim(kwargs.get("claim_id"), _DEFAULT_CLAIM[op])
        if key is None:
            ids = ", ".join(c["id"] for c in _CLAIMS.values())
            return (
                f"No synthetic claim matches '{kwargs.get('claim_id')}'. "
                f"Claims in the snapshot: {ids}.\n\n{_GATE}\n\n{_SOURCE}"
            )
        return handler(key)

    # ── claims_queue ──────────────────────────────────────────
    def _claims_queue(self):
        rows, open_value, open_count, recovered = [], 0.0, 0, 0.0
        for c in _CLAIMS.values():
            v = _value(c)
            closed = c["status"].startswith("Closed")
            if closed:
                recovered += c.get("recovered", 0.0)
            else:
                open_value += v
                open_count += 1
            rows.append(f"| {c['id']} | {c['type']} | {c['supplier']} | {_usd(v)} | "
                        f"{_TERMS[c['type']]['severity']} | {c['status']} |")
        return (
            f"**Supplier Claims Queue: {_RETAILER}, {_NOW_LABEL}**\n\n"
            f"| Claim | Type | Supplier | Value | Severity | Status |\n|---|---|---|---|---|---|\n"
            + "\n".join(rows) + "\n\n"
            f"| Measure | Value |\n|---|---|\n"
            f"| Open claims | {open_count} |\n| Open claim value | {_usd(open_value)} |\n"
            f"| Recovered this month | {_usd(recovered)} |\n\n"
            f"**Next step:** CLM-5201 is new and ready to draft; CLM-5202 is past its response window.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── triage_claim ──────────────────────────────────────────
    def _triage_claim(self, key):
        c = _CLAIMS[key]
        t = _TERMS[c["type"]]
        return (
            f"**Claim Triage: {c['id']}**\n\n"
            f"| Detail | Value |\n|---|---|\n"
            f"| Claim type | {c['type']} |\n| Severity | {t['severity']} |\n"
            f"| Responsible supplier | {c['supplier']} |\n| Purchase order | {c['po']} |\n"
            f"| Received at | {c['store']}, delivered {c['delivered']} |\n"
            f"| Claim value | {_usd(_value(c))} |\n"
            f"| Supplier response window | {t['response_h']} hours |\n"
            f"| Resolution window | {t['resolve_bd']} business days |\n"
            f"| Routing | Supplier claims coordinator, then {c['supplier']} claims desk |\n\n"
            f"**Next step:** check the evidence pack, then draft the supplier claim notice.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── evidence_pack ─────────────────────────────────────────
    def _evidence_pack(self, key):
        c = _CLAIMS[key]
        required = _REQUIRED_EVIDENCE[c["type"]]
        ev_rows = "\n".join(f"| {item} | {c['evidence'].get(item, 'Missing')} |" for item in required)
        missing = [item for item in required if item not in c["evidence"]]
        line_rows = "\n".join(f"| {name} | {qty} | {_usd(unit)} | {_usd(qty * unit)} |" for name, qty, unit in c["lines"])
        verdict = "Complete" if not missing else f"Incomplete - missing {', '.join(missing)}"
        return (
            f"**Evidence Pack: {c['id']} ({c['type']}, {c['supplier']})**\n\n"
            f"| Required Evidence | On File |\n|---|---|\n{ev_rows}\n\n"
            f"**Evidence status:** {verdict}\n\n"
            f"| Affected Item | Units | Unit Cost | Line Value |\n|---|---|---|---|\n{line_rows}\n"
            f"| **Total claim value** | | | **{_usd(_value(c))}** |\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── draft_supplier_claim ──────────────────────────────────
    def _draft_supplier_claim(self, key):
        c = _CLAIMS[key]
        t = _TERMS[c["type"]]
        items = "; ".join(f"{qty} x {name} ({_usd(qty * unit)})" for name, qty, unit in c["lines"])
        attachments = ", ".join(c["evidence"].values())
        return (
            f"**Supplier Claim Notice - Draft, Not Sent**\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| To | {c['supplier']} claims desk (synthetic) |\n"
            f"| Claim | {c['id']} - {c['type']}, {t['severity']} |\n"
            f"| Purchase order | {c['po']} delivered {c['delivered']} |\n"
            f"| Claim value | {_usd(_value(c))} |\n"
            f"| Evidence attached | {attachments} |\n"
            f"| Response due if sent now | {_add_hours(t['response_h'])} ({t['response_h']} h) |\n"
            f"| Resolution due if sent now | {_add_business_days(t['resolve_bd'])} ({t['resolve_bd']} business days) |\n\n"
            f"**Message draft:** \"{_RETAILER} is filing a {c['type'].lower()} claim on {c['po']}. "
            f"Affected items: {items}. Total {_usd(_value(c))}. The evidence pack is attached. Please "
            f"respond within {t['response_h']} hours with a credit or replacement proposal.\"\n\n"
            f"Status: Draft for coordinator review. Nothing was sent and no deadline clock was started.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── sla_tracker ───────────────────────────────────────────
    def _sla_tracker(self):
        rows, breached, at_risk = [], [], []
        for c in _CLAIMS.values():
            if c["status"].startswith("Closed"):
                continue
            elapsed, remaining, status = _sla(c)
            window = _TERMS[c["type"]]["response_h"]
            rows.append(f"| {c['id']} | {c['supplier']} | {window} h | "
                        f"{'-' if elapsed is None else str(elapsed) + ' h'} | {status} |")
            if status.startswith("Breached"):
                breached.append(c["id"])
            if status.startswith("At risk"):
                at_risk.append(c["id"])
        return (
            f"**Supplier Response Deadlines: {_NOW_LABEL}**\n\n"
            f"| Claim | Supplier | Window | Elapsed | Status |\n|---|---|---|---|---|\n"
            + "\n".join(rows) + "\n\n"
            f"**Breached:** {', '.join(breached) or 'None'}  \n"
            f"**At risk:** {', '.join(at_risk) or 'None'}\n\n"
            f"**Next step:** prepare the escalation brief for {', '.join(breached) or 'no claim'} and "
            f"a reminder draft for {', '.join(at_risk) or 'no claim'}.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── supplier_response ─────────────────────────────────────
    def _supplier_response(self, key):
        c = _CLAIMS[key]
        r = c["response"]
        if not r:
            return (
                f"**Supplier Response: {c['id']}**\n\nNo supplier response is on file. "
                f"Current status: {c['status']}.\n\n{_GATE}\n\n{_SOURCE}"
            )
        name, units, unit = c["lines"][0]
        claimed = _value(c)
        offered = round(r["accepted_units"] * unit, 2)
        gap = round(claimed - offered, 2)
        return (
            f"**Supplier Response: {c['id']} ({c['supplier']})**\n\n"
            f"| Detail | Value |\n|---|---|\n"
            f"| Received | {r['received']} ({r['hours_to_respond']} h, within the {_TERMS[c['type']]['response_h']} h window) |\n"
            f"| Position | {r['position']} |\n| Supplier reason | {r['reason']} |\n"
            f"| Claimed | {_usd(claimed)} ({units} units) |\n"
            f"| Credit offered | {_usd(offered)} ({r['accepted_units']} units) |\n"
            f"| Unrecovered gap | {_usd(gap)} ({units - r['accepted_units']} units) |\n\n"
            f"**Suggested next step:** ask the supplier for ship dates on the disputed units and compare them "
            f"with the agreed price list on file ({c['evidence']['Agreed price list']}). A coordinator decides "
            f"whether to accept the {_usd(offered)} credit or counter for the {_usd(gap)} gap.\n\n"
            f"No credit was accepted or rejected.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── escalation_brief ──────────────────────────────────────
    def _escalation_brief(self, key):
        c = _CLAIMS[key]
        elapsed, remaining, status = _sla(c)
        if not status.startswith("Breached"):
            return (
                f"**Escalation Check: {c['id']}**\n\nNo escalation needed: {status}.\n\n{_GATE}\n\n{_SOURCE}"
            )
        return (
            f"**Escalation Brief - Draft, Not Sent**\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| Claim | {c['id']} - {c['type']}, {_TERMS[c['type']]['severity']} |\n"
            f"| Supplier | {c['supplier']} |\n| Claim value | {_usd(_value(c))} |\n"
            f"| Response window | {_TERMS[c['type']]['response_h']} h |\n"
            f"| Elapsed without response | {elapsed} h ({status}) |\n"
            f"| Escalate to | {_ESCALATION_ROLE} |\n\n"
            f"**Draft:** \"{c['id']} with {c['supplier']} ({_usd(_value(c))}) has had no response for "
            f"{elapsed} hours against a {_TERMS[c['type']]['response_h']}-hour window. Please raise it with "
            f"the supplier's account contact and confirm a response date.\"\n\n"
            f"Status: Draft for coordinator approval. No escalation or message was sent.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )


if __name__ == "__main__":
    agent = SupplierClaimEngagementAgent()
    for op in _OPERATIONS:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
