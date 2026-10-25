"""
Payments Operations Agent

Payments operations assistant for a bank's release desk: the morning release
queue, scheme-rule validation, exception repair plans, pre-release risk review,
settlement-account reconciliation, payment status answers, and a daily KPI brief.

Where a real deployment would call a payments hub, a screening service, a fraud
model, and the settlement ledger, this agent uses a fixed synthetic snapshot for
the fictional Woodgrove Bank so it runs anywhere without credentials. It never
releases, holds, repairs, returns, or files anything; it returns reviewable drafts.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/payments-operations",
    "version": "1.0.0",
    "display_name": "Payments Operations Agent",
    "description": "Help payments operations teams clear the daily release queue faster by validating payments against scheme rules, planning exception repairs, reviewing pre-release risk, reconciling settlement accounts, and answering status questions with evidence, while every release decision stays with an authorized analyst.",
    "author": "AIBAST",
    "tags": ["payments", "operations", "exceptions", "reconciliation", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER (fixed snapshot: Woodgrove Bank, value date 2026-03-12)
# ═══════════════════════════════════════════════════════════════

_BANK = "Woodgrove Bank"
_VALUE_DATE = "Mar 12, 2026"
_PRIOR_DATE = "Mar 11, 2026"

_RAILS = {
    "Domestic Instant": {"max": 1000000, "currencies": ["USD"], "cutoff": "24x7"},
    "Domestic Batch": {"max": 5000000, "currencies": ["USD"], "cutoff": "17:00"},
    "Domestic High-Value": {"max": 50000000, "currencies": ["USD"], "cutoff": "18:00"},
    "Cross-Border Wire": {"max": 50000000, "currencies": ["USD", "EUR", "GBP", "JPY"], "cutoff": "16:00"},
}

_PAYMENTS = {
    "PAY-3101": {"id": "PAY-3101", "ref": "E2E-88410", "rail": "Domestic Instant", "amount": 4850.00,
                 "currency": "USD", "originator": "Fourth Coffee", "beneficiary": "Coho Winery",
                 "account": True, "stage": "settled", "avg": 5200.00, "new_beneficiary": False,
                 "hour": 9, "screen_score": 0.12},
    "PAY-3102": {"id": "PAY-3102", "ref": "E2E-88411", "rail": "Domestic Batch", "amount": 126400.00,
                 "currency": "USD", "originator": "Adventure Works", "beneficiary": "Adventure Works payroll",
                 "account": True, "stage": "released", "avg": 124000.00, "new_beneficiary": False,
                 "hour": 7, "screen_score": 0.05},
    "PAY-3103": {"id": "PAY-3103", "ref": "E2E-88412", "rail": "Cross-Border Wire", "amount": 48200.00,
                 "currency": "EUR", "originator": "Wide World Importers", "beneficiary": "Lucerne Publishing",
                 "account": True, "stage": "scheme_ack", "avg": 45000.00, "new_beneficiary": False,
                 "hour": 8, "screen_score": 0.22},
    "PAY-3104": {"id": "PAY-3104", "ref": "E2E-88413", "rail": "Domestic High-Value", "amount": 2750000.00,
                 "currency": "USD", "originator": "Alpine Ski House", "beneficiary": "Wingtip Toys",
                 "account": True, "stage": "held_for_review", "avg": 310000.00, "new_beneficiary": True,
                 "hour": 23, "screen_score": 0.41},
    "PAY-3105": {"id": "PAY-3105", "ref": "E2E-88414", "rail": "Domestic Instant", "amount": 1240000.00,
                 "currency": "USD", "originator": "Proseware", "beneficiary": "Trey Research",
                 "account": False, "stage": "exception", "avg": 980000.00, "new_beneficiary": False,
                 "hour": 10, "screen_score": 0.08},
    "PAY-3106": {"id": "PAY-3106", "ref": "E2E-88415", "rail": "Cross-Border Wire", "amount": 212500.00,
                 "currency": "USD", "originator": "Margie's Travel", "beneficiary": "Litware",
                 "account": True, "stage": "validated", "avg": 198000.00, "new_beneficiary": False,
                 "hour": 9, "screen_score": 0.18},
    "PAY-3107": {"id": "PAY-3107", "ref": "E2E-88410", "rail": "Domestic Batch", "amount": 18900.00,
                 "currency": "USD", "originator": "Fourth Coffee", "beneficiary": "Coho Winery",
                 "account": True, "stage": "exception", "avg": 5200.00, "new_beneficiary": False,
                 "hour": 11, "screen_score": 0.12},
    "PAY-3108": {"id": "PAY-3108", "ref": "E2E-88417", "rail": "Domestic Instant", "amount": 920.00,
                 "currency": "USD", "originator": "Graphic Design Institute", "beneficiary": "Lucerne Publishing",
                 "account": True, "stage": "settled", "avg": 1100.00, "new_beneficiary": False,
                 "hour": 10, "screen_score": 0.03},
}

_STAGE_LABEL = {
    "settled": "Settled", "released": "Released to scheme", "scheme_ack": "Scheme acknowledged",
    "validated": "Validated, awaiting release", "held_for_review": "Held for analyst review",
    "exception": "Exception queue",
}

_STATUS_TIMELINE = {
    "PAY-3103": [("Ingested", "08:02"), ("Validated", "08:03"), ("Screened", "08:05"),
                 ("Risk checked", "08:06"), ("Released to scheme", "08:15"),
                 ("Scheme acknowledged", "08:21")],
}
_STATUS_EXPECTED = {"PAY-3103": "Settlement expected by 15:00 on Mar 12, 2026 (beneficiary bank cutoff)"}

_REPAIR_PLAYBOOK = {
    "AMOUNT_OVER_RAIL_LIMIT": "Re-route to a rail whose limit covers the amount, or split below the rail limit with originator approval",
    "BENEFICIARY_ACCOUNT_MISSING": "Request the beneficiary account number from the originator through the approved channel",
    "CURRENCY_NOT_ON_RAIL": "Re-route to a rail that carries the currency, or convert before submission with originator approval",
    "DUPLICATE_REFERENCE": "Confirm with the originator whether this is a true duplicate before any resubmission",
}
_PRIORITY = {"DUPLICATE_REFERENCE": "P1"}

_SCREEN_THRESHOLD = 0.85

_RECON = {
    "account": "WGB-SETTLE-USD-01", "value_date": _PRIOR_DATE,
    "statement_items": 240, "matched": 236,
    "breaks": [
        {"id": "BRK-01", "type": "Amount mismatch", "delta": 1250.00, "ref": "PAY-2987"},
        {"id": "BRK-02", "type": "Missing on internal ledger", "delta": -18400.00, "ref": "Statement line 118"},
        {"id": "BRK-03", "type": "Missing on bank statement", "delta": 7615.50, "ref": "PAY-3011"},
        {"id": "BRK-04", "type": "Amount mismatch", "delta": -312.40, "ref": "PAY-3046"},
    ],
}

_KPI = [
    {"rail": "Domestic Instant", "volume": 182400, "exceptions": 1094},
    {"rail": "Domestic Batch", "volume": 96250, "exceptions": 1155},
    {"rail": "Domestic High-Value", "volume": 4120, "exceptions": 103},
    {"rail": "Cross-Border Wire", "volume": 7830, "exceptions": 352},
]

_GATE = (
    "Synthetic payments evidence only. This agent does not release, hold, repair, "
    "return, or resubmit a payment, contact a customer, or post to a ledger; every "
    "decision stays with an authorized payments analyst."
)
_SOURCE = "Source: [Synthetic Woodgrove Bank Payments Snapshot]\nAgents: PaymentsOperationsAgent"

_OPERATIONS = [
    "queue_overview", "validate_payment", "repair_plan", "release_risk_review",
    "reconcile_settlement", "payment_status", "daily_kpi_brief",
]

_DEFAULT_PAYMENT = {
    "validate_payment": "PAY-3105", "repair_plan": "PAY-3105",
    "release_risk_review": "PAY-3104", "payment_status": "PAY-3103",
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _money(amount, currency="USD"):
    return f"{currency} {amount:,.2f}"


def _resolve_payment(query, default_key):
    """Payment id such as PAY-3105 (any case); None when nothing matches (never another payment)."""
    if not query:
        return default_key
    q = str(query).strip().upper()
    return q if q in _PAYMENTS else None


def _validation_errors(p):
    errors = []
    rule = _RAILS[p["rail"]]
    if p["amount"] > rule["max"]:
        errors.append(("AMOUNT_OVER_RAIL_LIMIT",
                       f"{p['rail']} limit is {_money(rule['max'], 'USD')}; payment is {_money(p['amount'], p['currency'])}"))
    if p["currency"] not in rule["currencies"]:
        errors.append(("CURRENCY_NOT_ON_RAIL", f"{p['rail']} carries {', '.join(rule['currencies'])}"))
    if not p["account"]:
        errors.append(("BENEFICIARY_ACCOUNT_MISSING", "Beneficiary account number is blank"))
    for other in _PAYMENTS.values():
        if other["id"] != p["id"] and other["ref"] == p["ref"]:
            errors.append(("DUPLICATE_REFERENCE",
                           f"End-to-end reference {p['ref']} already used by {other['id']}"))
    return errors


def _risk(p):
    drivers, score = [], 0.05
    ratio = p["amount"] / p["avg"] if p["avg"] else 0
    if ratio > 5:
        score += 0.30
        drivers.append(f"Amount is {ratio:.1f} times the originator's 90-day average ({_money(p['avg'], p['currency'])})")
    if p["new_beneficiary"]:
        score += 0.25
        drivers.append("First payment from this originator to this beneficiary")
    if p["hour"] < 5 or p["hour"] > 22:
        score += 0.15
        drivers.append(f"Submitted out of hours ({p['hour']:02d}:00 local)")
    if p["amount"] > 1000000:
        score += 0.10
        drivers.append("High-value payment above USD 1,000,000.00")
    score = round(min(score, 0.99), 2)
    band = "Low" if score < 0.30 else ("Medium" if score < 0.65 else "High")
    return score, band, drivers or ["No notable risk signals"]


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class PaymentsOperationsAgent(BasicAgent):
    """
    Payments release-desk assistant over a fixed synthetic snapshot.

    Operations:
        queue_overview        - today's release queue by stage, value and exceptions
        validate_payment      - scheme-rule checks for one payment
        repair_plan           - draft repair plan for a failed payment (never executed)
        release_risk_review   - screening and pre-release risk drivers (analyst decides)
        reconcile_settlement  - settlement-account matches and open breaks
        payment_status        - stage timeline plus a draft reply for a status inquiry
        daily_kpi_brief       - straight-through processing and exceptions by rail
    """

    def __init__(self):
        self.name = "PaymentsOperationsAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Answers payments release-desk questions for the fictional Woodgrove Bank "
                "from a fixed synthetic snapshot (value date Mar 12, 2026). Use it for the "
                "morning release queue or exceptions overview, why a payment failed validation, "
                "how to repair a failed payment, whether a large or unusual payment looks safe "
                "to release, settlement or nostro account reconciliation breaks, where a "
                "payment is for a status inquiry, and the daily payments KPI brief by rail. "
                "Payments are PAY-3101 to PAY-3108. Call it first: every operation has demo "
                "defaults, so no payment id is needed to start. It never releases, holds, "
                "repairs, or resubmits a payment and never contacts anyone; it returns "
                "evidence and drafts for an authorized analyst."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "queue_overview for the release queue, today's payments or "
                            "exceptions overview; validate_payment for why a payment failed "
                            "or passed validation; repair_plan for how to fix or repair a "
                            "failed payment; release_risk_review for whether a payment is safe "
                            "to release, fraud or screening risk, or held payments; "
                            "reconcile_settlement for settlement, nostro or reconciliation "
                            "breaks; payment_status for where a payment is or what to tell a "
                            "relationship manager; daily_kpi_brief for KPIs, straight-through "
                            "processing or a daily brief by rail."
                        ),
                    },
                    "payment_id": {
                        "type": "string",
                        "enum": list(_PAYMENTS),
                        "description": "Payment id such as 'PAY-3105' (optional; each operation has a demo default)",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation") or "queue_overview"
        handlers = {
            "queue_overview": self._queue_overview,
            "validate_payment": self._validate_payment,
            "repair_plan": self._repair_plan,
            "release_risk_review": self._release_risk_review,
            "reconcile_settlement": self._reconcile_settlement,
            "payment_status": self._payment_status,
            "daily_kpi_brief": self._daily_kpi_brief,
        }
        handler = handlers.get(op)
        if not handler:
            return f"Unknown operation: {op}. Choose one of: {', '.join(_OPERATIONS)}."
        if op not in _DEFAULT_PAYMENT:
            return handler()
        key = _resolve_payment(kwargs.get("payment_id"), _DEFAULT_PAYMENT[op])
        if key is None:
            ids = ", ".join(p["id"] for p in _PAYMENTS.values())
            return (
                f"No synthetic payment matches '{kwargs.get('payment_id')}'. "
                f"Payments in the snapshot: {ids}.\n\n{_GATE}\n\n{_SOURCE}"
            )
        return handler(key)

    # ── queue_overview ────────────────────────────────────────
    def _queue_overview(self):
        rows, counts, usd_total, eur_total = [], {}, 0.0, 0.0
        for p in _PAYMENTS.values():
            label = _STAGE_LABEL[p["stage"]]
            counts[label] = counts.get(label, 0) + 1
            if p["currency"] == "USD":
                usd_total += p["amount"]
            else:
                eur_total += p["amount"]
            rows.append(f"| {p['id']} | {p['originator']} | {p['rail']} | {_money(p['amount'], p['currency'])} | {label} |")
        attention = [p for p in _PAYMENTS.values() if p["stage"] in ("exception", "held_for_review")]
        attention_lines = "\n".join(
            f"- **{p['id']}** ({_STAGE_LABEL[p['stage']]}): "
            + ("; ".join(code for code, _ in _validation_errors(p)) if p["stage"] == "exception"
               else f"risk band {_risk(p)[1]}")
            for p in attention
        )
        summary = "\n".join(f"| {k} | {v} |" for k, v in counts.items())
        return (
            f"**Release Queue: {_BANK}, value date {_VALUE_DATE}**\n\n"
            f"| Payment | Originator | Rail | Amount | Stage |\n|---|---|---|---|---|\n"
            + "\n".join(rows) + "\n\n"
            f"| Stage | Payments |\n|---|---|\n{summary}\n\n"
            f"**Queue value:** {_money(usd_total)} plus {_money(eur_total, 'EUR')} across {len(_PAYMENTS)} payments.\n\n"
            f"**Needs attention ({len(attention)}):**\n{attention_lines}\n\n"
            f"**Next step:** start with PAY-3105 validation, then the PAY-3104 risk review.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── validate_payment ──────────────────────────────────────
    def _validate_payment(self, key):
        p = _PAYMENTS[key]
        rule = _RAILS[p["rail"]]
        errors = _validation_errors(p)
        codes = {code for code, _ in errors}
        checks = [
            ("Amount within rail limit", "AMOUNT_OVER_RAIL_LIMIT" not in codes, f"limit {_money(rule['max'])}"),
            ("Currency carried by rail", "CURRENCY_NOT_ON_RAIL" not in codes, ", ".join(rule["currencies"])),
            ("Beneficiary account present", "BENEFICIARY_ACCOUNT_MISSING" not in codes, "required on every rail"),
            ("Unique end-to-end reference", "DUPLICATE_REFERENCE" not in codes, p["ref"]),
        ]
        table = "\n".join(f"| {name} | {'Pass' if ok else 'Fail'} | {detail} |" for name, ok, detail in checks)
        failures = "\n".join(f"- `{code}`: {detail}" for code, detail in errors) or "- None"
        result = "Fail" if errors else "Pass"
        return (
            f"**Validation: {p['id']} — {result}**\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| Originator | {p['originator']} |\n| Beneficiary | {p['beneficiary']} |\n"
            f"| Rail | {p['rail']} |\n| Amount | {_money(p['amount'], p['currency'])} |\n\n"
            f"| Scheme Rule | Result | Detail |\n|---|---|---|\n{table}\n\n"
            f"**Failure codes ({len(errors)}):**\n{failures}\n\n"
            f"**Next step:** {'ask for the repair plan before any resubmission.' if errors else 'eligible for the release-risk review.'}\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── repair_plan ───────────────────────────────────────────
    def _repair_plan(self, key):
        p = _PAYMENTS[key]
        errors = _validation_errors(p)
        if not errors:
            return (
                f"**Repair Plan: {p['id']}**\n\nNo validation failures; no repair is needed. "
                f"Current stage: {_STAGE_LABEL[p['stage']]}.\n\n{_GATE}\n\n{_SOURCE}"
            )
        fits = [name for name, r in _RAILS.items()
                if p["amount"] <= r["max"] and p["currency"] in r["currencies"] and name != p["rail"]
                and name.split()[0] == p["rail"].split()[0]]
        priority = "P1" if any(_PRIORITY.get(code) for code, _ in errors) else "P2"
        steps = "\n".join(f"{i}. **{code}** — {_REPAIR_PLAYBOOK[code]}." for i, (code, _) in enumerate(errors, 1))
        needs_route = any(code in ("AMOUNT_OVER_RAIL_LIMIT", "CURRENCY_NOT_ON_RAIL") for code, _ in errors)
        reroute = (f"| Rails that accept this amount and currency | {', '.join(fits)} |\n"
                   if fits and needs_route else "")
        asks = {"AMOUNT_OVER_RAIL_LIMIT": f"approval to re-route to {' or '.join(fits) if fits else 'another rail'}",
                "BENEFICIARY_ACCOUNT_MISSING": "the beneficiary account number",
                "CURRENCY_NOT_ON_RAIL": "approval to re-route or convert the currency",
                "DUPLICATE_REFERENCE": "confirmation that this is not a duplicate of an earlier payment"}
        need = "; ".join(asks[code] for code, _ in errors)
        return (
            f"**Repair Plan Draft: {p['id']} — Not Executed**\n\n"
            f"| Detail | Value |\n|---|---|\n"
            f"| Priority | {priority} |\n| Failure codes | {', '.join(code for code, _ in errors)} |\n"
            f"| Current rail | {p['rail']} |\n{reroute}"
            f"| Assigned queue | Payments repair analysts |\n\n"
            f"**Proposed repair steps:**\n{steps}\n\n"
            f"**Draft note to originator ({p['originator']}):** \"Your payment {p['id']} for "
            f"{_money(p['amount'], p['currency'])} could not be processed as submitted. To complete it we need: "
            f"{need}.\"\n\n"
            f"Status: Draft for analyst review. No repair, re-route, or message was executed.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── release_risk_review ───────────────────────────────────
    def _release_risk_review(self, key):
        p = _PAYMENTS[key]
        score, band, drivers = _risk(p)
        screen = "Clear" if p["screen_score"] < _SCREEN_THRESHOLD else "Potential match — hold"
        recommended = {"Low": "Eligible for release by an analyst",
                       "Medium": "Analyst review before release",
                       "High": "Hold for analyst review and call-back to the originator"}[band]
        driver_lines = "\n".join(f"- {d}" for d in drivers)
        return (
            f"**Pre-Release Risk Review: {p['id']}**\n\n"
            f"| Check | Result |\n|---|---|\n"
            f"| Originator -> Beneficiary | {p['originator']} -> {p['beneficiary']} |\n"
            f"| Amount | {_money(p['amount'], p['currency'])} on {p['rail']} |\n"
            f"| Watchlist screening | {screen} (best match score {p['screen_score']:.2f}, threshold {_SCREEN_THRESHOLD:.2f}) |\n"
            f"| Risk score | {score:.2f} |\n| Risk band | {band} |\n\n"
            f"**Risk drivers:**\n{driver_lines}\n\n"
            f"**Recommended handling:** {recommended}. The release decision belongs to an "
            f"authorized analyst; the payment was not released or held by this agent.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── reconcile_settlement ──────────────────────────────────
    def _reconcile_settlement(self):
        r = _RECON
        open_breaks = len(r["breaks"])
        net = sum(b["delta"] for b in r["breaks"])
        gross = sum(abs(b["delta"]) for b in r["breaks"])
        rate = 100.0 * r["matched"] / r["statement_items"]
        rows = "\n".join(f"| {b['id']} | {b['type']} | USD {b['delta']:+,.2f} | {b['ref']} |" for b in r["breaks"])
        largest = max(r["breaks"], key=lambda b: abs(b["delta"]))
        return (
            f"**Settlement Reconciliation: {r['account']}, value date {r['value_date']}**\n\n"
            f"| Measure | Value |\n|---|---|\n"
            f"| Statement items | {r['statement_items']} |\n| Matched | {r['matched']} ({rate:.1f}%) |\n"
            f"| Open breaks | {open_breaks} |\n| Net difference | USD {net:+,.2f} |\n"
            f"| Gross break value | USD {gross:,.2f} |\n\n"
            f"| Break | Type | Delta | Reference |\n|---|---|---|---|\n{rows}\n\n"
            f"**Work first:** {largest['id']} ({largest['type'].lower()}, USD {largest['delta']:+,.2f}) "
            f"is the largest break.\n\n"
            f"Proposed adjustments are drafts only; no ledger entry was posted.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── payment_status ────────────────────────────────────────
    def _payment_status(self, key):
        p = _PAYMENTS[key]
        timeline = _STATUS_TIMELINE.get(key)
        if timeline:
            rows = "\n".join(f"| {stage} | {at} |" for stage, at in timeline)
            history = f"| Stage | Time ({_VALUE_DATE}) |\n|---|---|\n{rows}\n\n"
        else:
            history = ""
        expected = _STATUS_EXPECTED.get(key, "Ask the payments desk for the next checkpoint")
        current = _STAGE_LABEL[p["stage"]]
        return (
            f"**Payment Status: {p['id']}**\n\n"
            f"| Detail | Value |\n|---|---|\n"
            f"| Current stage | {current} |\n| Rail | {p['rail']} |\n"
            f"| Amount | {_money(p['amount'], p['currency'])} |\n"
            f"| Originator -> Beneficiary | {p['originator']} -> {p['beneficiary']} |\n"
            f"| Expected | {expected} |\n\n"
            f"{history}"
            f"**Draft reply to the relationship manager (not sent):** \"{p['id']} for "
            f"{_money(p['amount'], p['currency'])} is at stage '{current}'. {expected}. "
            f"I will confirm once settlement is reported.\"\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── daily_kpi_brief ───────────────────────────────────────
    def _daily_kpi_brief(self):
        rows, vol_total, exc_total = [], 0, 0
        worst = None
        for k in _KPI:
            stp = 100.0 * (1 - k["exceptions"] / k["volume"])
            vol_total += k["volume"]
            exc_total += k["exceptions"]
            if worst is None or stp < worst[1]:
                worst = (k["rail"], stp)
            rows.append(f"| {k['rail']} | {k['volume']:,} | {k['exceptions']:,} | {stp:.2f}% |")
        stp_total = 100.0 * (1 - exc_total / vol_total)
        return (
            f"**Daily Payments KPI Brief: {_BANK}, {_PRIOR_DATE}**\n\n"
            f"| Rail | Volume | Exceptions | Straight-Through Rate |\n|---|---|---|---|\n"
            + "\n".join(rows) + "\n"
            f"| **Total** | **{vol_total:,}** | **{exc_total:,}** | **{stp_total:.2f}%** |\n\n"
            f"**Watch item:** {worst[0]} has the lowest straight-through rate ({worst[1]:.2f}%).\n"
            f"**Today's open items:** 2 exceptions (PAY-3105, PAY-3107), 1 payment held for review "
            f"(PAY-3104), 4 settlement breaks on WGB-SETTLE-USD-01.\n\n"
            f"Draft brief for the payments operations lead; nothing was distributed.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )


if __name__ == "__main__":
    agent = PaymentsOperationsAgent()
    for op in _OPERATIONS:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
