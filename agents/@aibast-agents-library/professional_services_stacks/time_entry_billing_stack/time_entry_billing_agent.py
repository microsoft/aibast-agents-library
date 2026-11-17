"""
Time Entry & Billing Agent

Processes consultant time entries, validates against project budgets and
billing rules, identifies unbilled hours, and prepares invoice packages
with audit-ready documentation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/time-entry-billing",
    "version": "1.1.0",
    "display_name": "Time and Entry Billing Agent",
    "description": "Automate month-end billing cycles to accelerate invoicing, reduce risk, and ensure audit-ready compliance.",
    "author": "AIBAST",
    "tags": ["billing", "time-entry", "invoicing", "audit", "professional-services"],
    "category": "professional_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

TIME_ENTRIES = [
    {"id": "TE-9001", "consultant": "Elena Vasquez", "project": "TechCorp Transformation",
     "date": "2026-03-10", "hours": 8.0, "rate": 275, "category": "billable", "description": "Cloud architecture design workshop",
     "approved": True},
    {"id": "TE-9002", "consultant": "Elena Vasquez", "project": "TechCorp Transformation",
     "date": "2026-03-11", "hours": 9.5, "rate": 275, "category": "billable", "description": "Azure landing zone implementation",
     "approved": True},
    {"id": "TE-9003", "consultant": "Michael Chen", "project": "Apex Analytics Platform",
     "date": "2026-03-10", "hours": 7.5, "rate": 260, "category": "billable", "description": "Data pipeline development",
     "approved": True},
    {"id": "TE-9004", "consultant": "Michael Chen", "project": "Apex Analytics Platform",
     "date": "2026-03-11", "hours": 8.0, "rate": 260, "category": "billable", "description": "",
     "approved": False},
    {"id": "TE-9005", "consultant": "Priya Sharma", "project": "Pinnacle Energy ERP",
     "date": "2026-03-10", "hours": 10.0, "rate": 310, "category": "billable", "description": "Program status review and steering committee",
     "approved": True},
    {"id": "TE-9006", "consultant": "Priya Sharma", "project": "Pinnacle Energy ERP",
     "date": "2026-03-11", "hours": 8.0, "rate": 310, "category": "billable", "description": "Sprint planning and backlog grooming",
     "approved": True},
    {"id": "TE-9007", "consultant": "Lisa Tanaka", "project": "Atlas Security Audit",
     "date": "2026-03-10", "hours": 6.0, "rate": 290, "category": "billable", "description": "Identity and access management review",
     "approved": True},
    {"id": "TE-9008", "consultant": "Lisa Tanaka", "project": "Atlas Security Audit",
     "date": "2026-03-11", "hours": 8.5, "rate": 290, "category": "billable", "description": "Penetration test coordination",
     "approved": True},
    {"id": "TE-9009", "consultant": "Amanda Foster", "project": "Metro Transit Portal",
     "date": "2026-03-10", "hours": 8.0, "rate": 165, "category": "billable", "description": "User research session facilitation",
     "approved": True},
    {"id": "TE-9010", "consultant": "Amanda Foster", "project": "Metro Transit Portal",
     "date": "2026-03-11", "hours": 4.0, "rate": 165, "category": "non_billable", "description": "Internal design review",
     "approved": True},
    {"id": "TE-9011", "consultant": "Elena Vasquez", "project": "TechCorp Transformation",
     "date": "2026-03-12", "hours": 11.0, "rate": 412, "category": "billable", "description": "Weekend migration cutover",
     "approved": False},
    {"id": "TE-9012", "consultant": "David Okafor", "project": "Internal Training",
     "date": "2026-03-10", "hours": 8.0, "rate": 0, "category": "non_billable", "description": "Power BI certification prep",
     "approved": True},
]

BILLING_RATES = {
    "Elena Vasquez": {"standard": 275, "overtime": 412, "max_daily_hours": 10},
    "Michael Chen": {"standard": 260, "overtime": 390, "max_daily_hours": 10},
    "Priya Sharma": {"standard": 310, "overtime": 465, "max_daily_hours": 10},
    "Lisa Tanaka": {"standard": 290, "overtime": 435, "max_daily_hours": 10},
    "Amanda Foster": {"standard": 165, "overtime": 248, "max_daily_hours": 10},
}

PROJECT_BUDGETS = {
    "TechCorp Transformation": {"total_budget": 850000, "billed_to_date": 682400, "remaining": 167600,
                                  "contract_type": "T&M", "client": "TechCorp Industries"},
    "Apex Analytics Platform": {"total_budget": 520000, "billed_to_date": 398000, "remaining": 122000,
                                 "contract_type": "T&M", "client": "Apex Manufacturing"},
    "Pinnacle Energy ERP": {"total_budget": 1200000, "billed_to_date": 744000, "remaining": 456000,
                             "contract_type": "Fixed Fee", "client": "Pinnacle Energy"},
    "Atlas Security Audit": {"total_budget": 185000, "billed_to_date": 156600, "remaining": 28400,
                              "contract_type": "T&M", "client": "Atlas Financial Group"},
    "Metro Transit Portal": {"total_budget": 340000, "billed_to_date": 218000, "remaining": 122000,
                              "contract_type": "T&M", "client": "Metro Transit Authority"},
}

INVOICE_HISTORY = [
    {"invoice_id": "INV-2026-201", "client": "TechCorp Industries", "amount": 142500, "date": "2026-02-28",
     "status": "paid", "days_outstanding": 0},
    {"invoice_id": "INV-2026-202", "client": "Apex Manufacturing", "amount": 98800, "date": "2026-02-28",
     "status": "paid", "days_outstanding": 0},
    {"invoice_id": "INV-2026-203", "client": "Pinnacle Energy", "amount": 186000, "date": "2026-02-28",
     "status": "outstanding", "days_outstanding": 17},
    {"invoice_id": "INV-2026-204", "client": "Atlas Financial Group", "amount": 52200, "date": "2026-02-28",
     "status": "outstanding", "days_outstanding": 17},
    {"invoice_id": "INV-2026-205", "client": "Metro Transit Authority", "amount": 46200, "date": "2026-02-28",
     "status": "overdue", "days_outstanding": 45},
]

DISPUTES = [
    {
        "dispute_id": "DSP-303",
        "entry_id": "78 hrs (period)",
        "client": "MegaCorp Systems",
        "reason": "Client claims the architecture work is out of scope for Phase 2.",
        "evidence": "SOW Section 3.4 \"Technical architecture guidance\" covers this work; 4 meeting minutes showing client requests; 7 email threads requesting architecture input; Phase 2 deliverables require architecture decisions.",
        "recommended_action": "Send the drafted email with SOW references after review; delivery lead to call the PMO director.",
        "status": "client_review_pending",
        "hours": 78, "rate": 300, "resource": "Sarah Chen - Senior Cloud Architect",
        "root_cause": "New client PM not briefed on SOW terms",
        "win_probability": "85% (strong contractual basis)",
    },
    {
        "dispute_id": "DSP-301",
        "entry_id": "TE-9004",
        "client": "Apex Manufacturing",
        "reason": "Work description is missing, so the client cannot validate the charge.",
        "evidence": "Project assignment and time record exist; consultant narrative and manager approval are missing.",
        "recommended_action": "Return to Michael Chen for a factual description, then route to the project manager for approval.",
        "status": "evidence_required",
    },
    {
        "dispute_id": "DSP-302",
        "entry_id": "TE-9011",
        "client": "TechCorp Industries",
        "reason": "Premium-rate migration work requires written cutover authorization.",
        "evidence": "The entry uses the configured overtime rate, but approval is not attached.",
        "recommended_action": "Attach the approved cutover authorization and obtain billing-manager sign-off before invoicing.",
        "status": "approval_required",
    },
]

# Month-end close scenario (the demo default): firm-wide period totals behind the sample entries above.
MONTH_END = {
    "hours_logged": 15247,
    "billable_hours": 14122,
    "non_billable_hours": 1125,
    "non_billable_note": "training, admin",
    "invoice_value": 2847500,
    "clients": 67,
    "invoices": 67,
    "processing_minutes": 8,
    "manual_hours": 40,
    "premium_auto_approval_threshold": 25000,
    "deferred_fixed_fee": 427000,
}

# Hours flagged for review before final approval (45 + 78 + 144 = 267).
FLAGGED_ITEMS = {
    "missing_descriptions": {"entries": 45, "hours": 45,
                             "resolution": "Descriptions proposed from project context and task codes"},
    "disputed_scope": {"hours": 78, "client": "MegaCorp Systems", "amount": 23400,
                       "issue": "Phase 2 scope disagreement", "status": "Client review pending"},
    "premium_billing": {"hours": 144, "invoice_value": 892000, "projects": 8,
                        "largest_client": "TechCorp", "largest_value": 67000, "largest_status": "pre-approved",
                        "basis": "Weekend/overtime at premium rates"},
}

# Projects over 95% of budget. RetailCo's documented portion is billable; the rest is the write-off.
PROJECT_OVERRUNS = [
    {"client": "TechVentures", "contract_type": "Fixed Fee", "overage": 12000, "treatment": "absorbed"},
    {"client": "CloudStart", "contract_type": "Fixed Fee", "overage": 8000, "treatment": "absorbed"},
    {"client": "DataFlow", "contract_type": "Fixed Fee", "overage": 15000, "treatment": "absorbed"},
    {"client": "FinanceHub", "contract_type": "T&M", "overage": 47000, "treatment": "client approval",
     "issue": "Over Cap", "detail": "Exceeded approved purchase order", "cause": "Extended testing phase",
     "action": "Client approval for overage", "probability": "85% (justified scope)", "documented": 47000},
    {"client": "RetailCo", "contract_type": "T&M", "overage": 23200, "treatment": "bill documented, write off rest",
     "issue": "Over", "detail": "Work delivered beyond the approved budget",
     "cause": "Verbal requests, no change orders", "evidence": "Email threads, Teams chats",
     "documented": 15000, "draft_invoice": 166000},
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _total_billable_hours():
    """Sum of billable hours across all entries."""
    return sum(te["hours"] for te in TIME_ENTRIES if te["category"] == "billable")


def _total_billable_value():
    """Sum of billable dollar value."""
    return sum(te["hours"] * te["rate"] for te in TIME_ENTRIES if te["category"] == "billable")


def _unbilled_entries():
    """Entries that are billable but not yet approved."""
    return [te for te in TIME_ENTRIES if te["category"] == "billable" and not te["approved"]]


def _audit_flags():
    """Return entries with potential issues."""
    flags = []
    for te in TIME_ENTRIES:
        issues = []
        if not te["description"]:
            issues.append("Missing description")
        rates = BILLING_RATES.get(te["consultant"], {})
        if te["hours"] > rates.get("max_daily_hours", 10):
            issues.append(f"Exceeds {rates.get('max_daily_hours', 10)}-hour daily limit")
        if te["rate"] > rates.get("overtime", 999) and te["category"] == "billable":
            issues.append("Rate exceeds overtime cap")
        if te["rate"] != rates.get("standard", te["rate"]) and te["rate"] != rates.get("overtime", te["rate"]):
            issues.append(f"Non-standard rate (${te['rate']}/hr)")
        if issues:
            flags.append({"entry": te, "issues": issues})
    return flags


def _k(value):
    """$23K style (nearest thousand)."""
    return f"${(value + 500) // 1000:,}K"


def _overrun(client):
    for o in PROJECT_OVERRUNS:
        if o["client"].lower() == client.lower():
            return o
    return None


def _budget_status(project_name):
    """Return budget consumption percentage."""
    budget = PROJECT_BUDGETS.get(project_name, {})
    if not budget or budget["total_budget"] == 0:
        return 0
    return round(budget["billed_to_date"] / budget["total_budget"] * 100, 1)


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "unbilled_report", "billing_summary", "time_entry_audit", "invoice_preparation",
    "dispute_resolution", "month_end_close", "flagged_review", "budget_overruns", "final_invoices",
]


class TimeEntryBillingAgent(BasicAgent):
    """Processes time entries and generates billing reports."""

    def __init__(self):
        self.name = "TimeEntryBillingAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "The professional-services month-end billing agent. For the month-end close "
                "('15,000 hours logged ... process the full billing cycle') use month_end_close "
                "first; 'break down the flagged hours' uses flagged_review; budget overruns and "
                "write-off exposure use budget_overruns; the MegaCorp dispute uses dispute_resolution; "
                "'approve everything ... generate final invoices and revenue report' uses "
                "final_invoices (it applies the recommended RetailCo split: bill the documented $15K, write off the rest). "
                "Call it first; every operation has demo defaults. Use it for unapproved "
                "billable work, billing summaries, time-entry rule checks, invoice-package "
                "preparation, or disputed-hour evidence. Use unbilled_report for revenue "
                "leakage and outstanding invoices, billing_summary for project and consultant "
                "rollups, time_entry_audit for missing narratives, hours, rates, and budget "
                "checks, invoice_preparation for approval-gated T&M invoice packages and "
                "fixed-fee holds, and dispute_resolution for evidence-backed resolution "
                "recommendations. It never changes time, approves entries, recognizes revenue, "
                "creates an accounting posting, or sends an invoice: final packages are drafts "
                "ready for an authorized person to approve and send."
            ),
            "operations": list(_OPERATIONS),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "unbilled_report: find billable entries blocked from invoicing and "
                            "show outstanding invoices. billing_summary: summarize hours, value, "
                            "budgets, and consultant activity. time_entry_audit: identify missing "
                            "descriptions, excess hours, non-standard rates, and budget risk. "
                            "invoice_preparation: prepare approved T&M support and hold fixed-fee "
                            "work for milestone evidence. dispute_resolution: assemble the "
                            "evidence gap and recommended approval path for disputed hours, "
                            "including the MegaCorp scope dispute. month_end_close: the default; "
                            "process the full month-end billing cycle (hours, invoice drafts, flagged "
                            "hours). flagged_review: break down the flagged hours. budget_overruns: "
                            "projects over budget and write-off exposure. final_invoices: approve-and-"
                            "generate request; final invoice package and revenue recognition report "
                            "drafts with the RetailCo adjustment."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation") or "month_end_close"
        dispatch = {
            "month_end_close": self._month_end_close,
            "flagged_review": self._flagged_review,
            "budget_overruns": self._budget_overruns,
            "final_invoices": self._final_invoices,
            "unbilled_report": self._unbilled_report,
            "billing_summary": self._billing_summary,
            "time_entry_audit": self._time_entry_audit,
            "invoice_preparation": self._invoice_preparation,
            "dispute_resolution": self._dispute_resolution,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)

    # ------------------------------------------------------------------
    def _unbilled_report(self, **kwargs) -> str:
        lines = ["## Unbilled Hours Report\n"]
        unbilled = _unbilled_entries()
        total_unbilled_val = sum(te["hours"] * te["rate"] for te in unbilled)
        lines.append(f"**Unbilled entries:** {len(unbilled)}")
        lines.append(f"**Unbilled value:** ${total_unbilled_val:,.2f}\n")

        if unbilled:
            lines.append("| Entry ID | Consultant | Project | Date | Hours | Rate | Value | Issue |")
            lines.append("|----------|-----------|---------|------|-------|------|-------|-------|")
            for te in unbilled:
                val = te["hours"] * te["rate"]
                issue = "Needs approval"
                if not te["description"]:
                    issue += "; missing description"
                lines.append(
                    f"| {te['id']} | {te['consultant']} | {te['project']} | {te['date']} | "
                    f"{te['hours']} | ${te['rate']} | ${val:,.2f} | {issue} |"
                )
        else:
            lines.append("All billable entries are approved.")

        lines.append("\n### Outstanding Invoices\n")
        lines.append("| Invoice | Client | Amount | Date | Status | Days Out |")
        lines.append("|---------|--------|--------|------|--------|----------|")
        for inv in INVOICE_HISTORY:
            if inv["status"] != "paid":
                lines.append(
                    f"| {inv['invoice_id']} | {inv['client']} | ${inv['amount']:,.2f} | "
                    f"{inv['date']} | **{inv['status'].upper()}** | {inv['days_outstanding']} |"
                )
        total_outstanding = sum(inv["amount"] for inv in INVOICE_HISTORY if inv["status"] != "paid")
        lines.append(f"\n**Total outstanding:** ${total_outstanding:,.2f}")
        lines.append("\n> Synthetic month-end evidence; no entry or invoice status was changed.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _billing_summary(self, **kwargs) -> str:
        lines = ["## Billing Summary\n"]
        total_hrs = _total_billable_hours()
        total_val = _total_billable_value()
        non_billable = sum(te["hours"] for te in TIME_ENTRIES if te["category"] == "non_billable")
        total_all = total_hrs + non_billable
        billable_pct = round(total_hrs / total_all * 100, 1) if total_all else 0

        lines.append(f"**Total hours logged:** {total_all}")
        lines.append(f"**Billable hours:** {total_hrs} ({billable_pct}%)")
        lines.append(f"**Non-billable hours:** {non_billable}")
        lines.append(f"**Total billable value:** ${total_val:,.2f}\n")

        lines.append("### By Project\n")
        lines.append("| Project | Client | Type | Hours | Value | Budget Used | Remaining |")
        lines.append("|---------|--------|------|-------|-------|-------------|-----------|")
        project_hours = {}
        project_value = {}
        for te in TIME_ENTRIES:
            if te["category"] == "billable":
                project_hours[te["project"]] = project_hours.get(te["project"], 0) + te["hours"]
                project_value[te["project"]] = project_value.get(te["project"], 0) + te["hours"] * te["rate"]
        for proj in PROJECT_BUDGETS:
            hrs = project_hours.get(proj, 0)
            val = project_value.get(proj, 0)
            budget = PROJECT_BUDGETS[proj]
            used_pct = _budget_status(proj)
            lines.append(
                f"| {proj} | {budget['client']} | {budget['contract_type']} | "
                f"{hrs} | ${val:,.2f} | {used_pct}% | ${budget['remaining']:,.0f} |"
            )

        lines.append("\n### By Consultant\n")
        lines.append("| Consultant | Hours | Billable Value | Avg Rate |")
        lines.append("|-----------|-------|---------------|----------|")
        consultant_data = {}
        for te in TIME_ENTRIES:
            if te["category"] == "billable":
                name = te["consultant"]
                if name not in consultant_data:
                    consultant_data[name] = {"hours": 0, "value": 0}
                consultant_data[name]["hours"] += te["hours"]
                consultant_data[name]["value"] += te["hours"] * te["rate"]
        for name, data in sorted(consultant_data.items(), key=lambda x: x[1]["value"], reverse=True):
            avg_rate = round(data["value"] / data["hours"], 2) if data["hours"] else 0
            lines.append(f"| {name} | {data['hours']} | ${data['value']:,.2f} | ${avg_rate} |")
        lines.append("\n> Synthetic billing summary; amounts are not posted revenue.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _time_entry_audit(self, **kwargs) -> str:
        lines = ["## Time Entry Audit Report\n"]
        flags = _audit_flags()
        lines.append(f"**Total entries reviewed:** {len(TIME_ENTRIES)}")
        lines.append(f"**Entries flagged:** {len(flags)}\n")

        if flags:
            lines.append("| Entry ID | Consultant | Date | Hours | Rate | Issues |")
            lines.append("|----------|-----------|------|-------|------|--------|")
            for f in flags:
                te = f["entry"]
                issues_str = "; ".join(f["issues"])
                lines.append(
                    f"| {te['id']} | {te['consultant']} | {te['date']} | {te['hours']} | "
                    f"${te['rate']} | {issues_str} |"
                )
        else:
            lines.append("All entries pass audit checks.")

        lines.append("\n### Budget Alert\n")
        lines.append("| Project | Budget Used | Remaining | Status |")
        lines.append("|---------|------------|-----------|--------|")
        for proj, budget in PROJECT_BUDGETS.items():
            used = _budget_status(proj)
            status = "CRITICAL" if used >= 95 else "WARNING" if used >= 80 else "OK"
            lines.append(f"| {proj} | {used}% | ${budget['remaining']:,.0f} | **{status}** |")
        lines.append("\n> Flags require human correction and approval; the agent never rewrites a time entry.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _invoice_preparation(self, **kwargs) -> str:
        lines = ["## Invoice Preparation\n"]
        lines.append("### Invoices Ready to Generate\n")

        # Group approved billable T&M entries by project/client.
        by_project = {}
        for te in TIME_ENTRIES:
            budget = PROJECT_BUDGETS.get(te["project"], {})
            if (
                te["category"] == "billable"
                and te["approved"]
                and budget.get("contract_type") == "T&M"
            ):
                proj = te["project"]
                if proj not in by_project:
                    by_project[proj] = {"hours": 0, "value": 0, "entries": 0}
                by_project[proj]["hours"] += te["hours"]
                by_project[proj]["value"] += te["hours"] * te["rate"]
                by_project[proj]["entries"] += 1

        lines.append("| Project | Client | Entries | Hours | Invoice Amount | Contract Type |")
        lines.append("|---------|--------|---------|-------|---------------|---------------|")
        grand_total = 0
        for proj, data in by_project.items():
            budget = PROJECT_BUDGETS.get(proj, {})
            client = budget.get("client", "Unknown")
            ctype = budget.get("contract_type", "T&M")
            grand_total += data["value"]
            lines.append(
                f"| {proj} | {client} | {data['entries']} | {data['hours']} | "
                f"${data['value']:,.2f} | {ctype} |"
            )
        lines.append(f"\n**Grand total ready to invoice:** ${grand_total:,.2f}")

        unbilled = _unbilled_entries()
        unbilled_val = sum(te["hours"] * te["rate"] for te in unbilled)
        lines.append(f"**Pending approval (not included):** ${unbilled_val:,.2f}")
        fixed_fee_entries = [
            te for te in TIME_ENTRIES
            if te["category"] == "billable"
            and te["approved"]
            and PROJECT_BUDGETS.get(te["project"], {}).get("contract_type") == "Fixed Fee"
        ]
        if fixed_fee_entries:
            lines.append(
                "**Fixed-fee hold:** Pinnacle Energy ERP time is retained as delivery evidence; "
                "invoice value requires the contractual milestone schedule."
            )

        lines.append("\n### Invoice History\n")
        lines.append("| Invoice | Client | Amount | Date | Status |")
        lines.append("|---------|--------|--------|------|--------|")
        for inv in INVOICE_HISTORY:
            lines.append(
                f"| {inv['invoice_id']} | {inv['client']} | ${inv['amount']:,.2f} | "
                f"{inv['date']} | {inv['status']} |"
            )
        total_billed = sum(inv["amount"] for inv in INVOICE_HISTORY)
        total_collected = sum(inv["amount"] for inv in INVOICE_HISTORY if inv["status"] == "paid")
        lines.append(f"\n**Total billed (last cycle):** ${total_billed:,.2f}")
        lines.append(f"**Total collected:** ${total_collected:,.2f}")
        lines.append(f"**Collection rate:** {round(total_collected/total_billed*100,1)}%")
        lines.append("\n> Draft invoice support only; no invoice was generated, posted, or sent.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _dispute_resolution(self, **kwargs) -> str:
        lines = ["## Disputed Hours Resolution Brief\n"]
        lead = DISPUTES[0]
        amount = lead["hours"] * lead["rate"]
        lines.append(f"### {lead['client']} Dispute Analysis\n")
        lines.append(f"**Disputed Amount:** ${amount:,} ({lead['hours']} hrs @ ${lead['rate']}/hr)  ")
        lines.append(f"**Resource:** {lead['resource']}  ")
        lines.append(f"**Client Claim:** {lead['reason']}\n")
        lines.append("**Our Evidence:**")
        for item in lead["evidence"].rstrip(".").split("; "):
            lines.append(f"- {item}")
        lines.append(f"\n**Root Cause:** {lead['root_cause']}\n")
        lines.append("**Resolution Strategy:**")
        lines.append("- Email drafted with SOW references (ready for you to review and send)")
        lines.append("- Delivery lead to call PMO director")
        lines.append(f"- Win probability: {lead['win_probability']}\n")
        lines.append("### All Open Disputes\n")
        lines.append("| Dispute | Entry | Client | Status | Evidence Gap |")
        lines.append("|---------|-------|--------|--------|--------------|")
        for dispute in DISPUTES:
            lines.append(
                f"| {dispute['dispute_id']} | {dispute['entry_id']} | {dispute['client']} | "
                f"{dispute['status']} | {dispute['evidence']} |"
            )
        lines.append("\n### Recommended Resolution Path\n")
        for dispute in DISPUTES:
            lines.append(f"**{dispute['dispute_id']} — {dispute['reason']}**")
            lines.append(f"- Recommended: {dispute['recommended_action']}")
        lines.append(
            "\n> Synthetic decision support only; do not invent narratives, alter hours, "
            "waive charges, or contact a client without authorized review."
        )
        lines.append("\n**Next step:** Ready to finalize all invoices?")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _month_end_close(self, **kwargs) -> str:
        m = MONTH_END
        total = m["billable_hours"] + m["non_billable_hours"]
        pct = round(m["billable_hours"] * 100 / total, 1)
        flagged = sum(f["hours"] for f in FLAGGED_ITEMS.values())
        saved = round(100 - m["processing_minutes"] * 100 / (m["manual_hours"] * 60), 1)
        f = FLAGGED_ITEMS
        return (
            f"I've processed all time entries and prepared {m['invoices']} client invoice drafts totaling "
            f"${m['invoice_value'] / 1_000_000:.2f}M. Flagged {flagged} hours requiring manual review before final approval.\n\n"
            "## Month-End Summary\n\n"
            "| Metric | Value |\n|---|---|\n"
            f"| Total hours logged | {total:,} |\n"
            f"| Billable hours | {m['billable_hours']:,} ({pct}%) |\n"
            f"| Non-billable | {m['non_billable_hours']:,} ({m['non_billable_note']}) |\n"
            f"| Total invoice value | ${m['invoice_value']:,} |\n"
            f"| Active projects | {m['clients']} clients |\n"
            f"| Invoices ready | {m['invoices']} drafts generated |\n\n"
            f"**Flagged for Review: {flagged} hours**\n"
            f"- {f['missing_descriptions']['entries']} missing descriptions (descriptions proposed with AI for reviewer acceptance)\n"
            f"- {f['disputed_scope']['hours']} disputed hours (MegaCorp scope issue)\n"
            f"- {f['premium_billing']['hours']} premium overtime hours (over ${m['premium_auto_approval_threshold'] // 1000}K threshold)\n\n"
            f"**Processing Time:** {m['processing_minutes']} minutes vs {m['manual_hours']} hours manual ({saved}% less time)\n\n"
            "Source: [Synthetic D365 Project Ops + CRM snapshot]\n\n"
            "**Next step:** Want details on the flagged items?\n\n"
            "> Synthetic month-end evidence; invoice drafts only. No entry was approved or changed, and no invoice was posted or sent."
        )

    # ------------------------------------------------------------------
    def _flagged_review(self, **kwargs) -> str:
        f = FLAGGED_ITEMS
        md, ds, pb = f["missing_descriptions"], f["disputed_scope"], f["premium_billing"]
        over = [o for o in PROJECT_OVERRUNS]
        fixed = len([o for o in over if o["contract_type"] == "Fixed Fee"])
        tm = len(over) - fixed
        return (
            "Three categories requiring attention: missing descriptions (resolved as proposals), disputed scope, "
            "and premium billing over the approval threshold.\n\n"
            "## Flagged Items Breakdown\n\n"
            f"### Auto-Resolved as Proposals ({md['entries']} entries, {md['hours']} hours)\n"
            "- Missing task descriptions\n"
            f"- {md['resolution']}\n"
            "- Reviewer accepts the proposed text; no time entry is rewritten by the agent\n\n"
            f"### Disputed Scope ({ds['hours']} hours)\n"
            f"- Client: {ds['client']}\n"
            f"- Amount: ${ds['amount']:,} at risk\n"
            f"- Issue: {ds['issue']}\n"
            f"- Status: {ds['status']}\n\n"
            f"### Premium Billing ({pb['hours']} hours)\n"
            f"- {pb['basis']}\n"
            f"- Total value: {_k(pb['invoice_value'])} (over ${MONTH_END['premium_auto_approval_threshold'] // 1000}K auto-approval)\n"
            f"- Clients: {pb['projects']} projects\n"
            f"- Largest: {pb['largest_client']} {_k(pb['largest_value'])} ({pb['largest_status']})\n\n"
            f"**Budget Alerts:** {len(over)} projects over 95% budget consumed ({fixed} fixed-fee absorbed, "
            f"{tm} T&M need client approval)\n\n"
            "Source: [Synthetic billing rules engine + contract database]\n\n"
            "**Next step:** Want me to walk through those budget overrun projects?\n\n"
            "> Synthetic decision support; nothing was approved, changed, or sent."
        )

    # ------------------------------------------------------------------
    def _budget_overruns(self, **kwargs) -> str:
        fixed = [o for o in PROJECT_OVERRUNS if o["contract_type"] == "Fixed Fee"]
        tm = [o for o in PROJECT_OVERRUNS if o["contract_type"] == "T&M"]
        lines = [f"{len(PROJECT_OVERRUNS)} projects exceeded budgets. {len(fixed)} fixed-fee overruns are absorbed per "
                 f"contract. {len(tm)} time-and-materials projects have client approval issues.\n",
                 "## Budget Overruns and Write-Off Exposure\n", "### Fixed-Fee Overruns (Expected)"]
        for o in fixed:
            lines.append(f"- {o['client']}: {_k(o['overage'])} over ({o['treatment']})")
        lines.append("\n### T&M Overrun Issues")
        for o in tm:
            lines.append(f"\n**{o['client']} - {_k(o['overage'])} {o['issue']}**")
            lines.append(f"- {o['detail']}")
            lines.append(f"- Cause: {o['cause']}")
            if o.get("evidence"):
                lines.append(f"- Evidence: {o['evidence']}")
            if o.get("action"):
                lines.append(f"- Action needed: {o['action']}")
                lines.append(f"- Probability: {o['probability']}")
            else:
                lines.append(f"- Recommendation: Bill {_k(o['documented'])} (documented), write-off "
                             f"{_k(o['overage'] - o['documented'])} (goodwill + lesson)")
        recoverable = sum(o["overage"] for o in tm if o.get("action"))
        at_risk = sum(o["overage"] for o in tm if not o.get("action"))
        lines.append(f"\n**Total Exposure:** {_k(recoverable + at_risk)} ({_k(recoverable)} recoverable, {_k(at_risk)} at risk)")
        lines.append("\nSource: [Synthetic project analysis + communication records]")
        lines.append("\n**Next step:** What's your call on RetailCo?")
        lines.append("\n> Synthetic decision support; no write-off, charge, or client contact has been made.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _final_invoices(self, **kwargs) -> str:
        m = MONTH_END
        r = _overrun("RetailCo")
        billed = r["documented"]
        write_off = r["overage"] - billed
        total = m["invoice_value"] - write_off
        retail = r["draft_invoice"] - write_off
        mega = DISPUTES[0]
        pb = FLAGGED_ITEMS["premium_billing"]
        return (
            f"{m['invoices']} final invoice drafts ready with the RetailCo adjustment applied. Revenue recognition "
            "report drafted for the finance team.\n\n"
            "## Final Invoice Summary (ready for your approval)\n\n"
            "| Item | Value |\n|---|---|\n"
            f"| Invoices ready to approve | {m['invoices']} |\n"
            f"| Total revenue | ${total:,.0f} (after ${write_off:,.0f} write-off) |\n"
            f"| RetailCo adjusted | ${retail:,.0f} ({_k(billed)} billed, {_k(write_off)} written off) |\n"
            f"| MegaCorp status | ${mega['hours'] * mega['rate']:,} pending resolution "
            f"({mega['win_probability'].split(' ')[0]} recovery probability) |\n"
            f"| Premium billing | {_k(pb['invoice_value'])} ready to approve across {pb['projects']} projects |\n\n"
            "### Distribution (ready for you to send)\n"
            f"- Client portals: all {m['invoices']} invoice drafts prepared for upload\n"
            "- Email delivery: cover emails drafted with payment terms\n"
            "- Write-off: documentation drafted for the financial system\n\n"
            "### Revenue Recognition Report (draft for CFO review)\n"
            f"- Recognized: ${total:,.0f}\n"
            f"- Deferred: ${m['deferred_fixed_fee']:,} (fixed-fee projects)\n"
            "- Variance analysis: by project included (RetailCo write-off, MegaCorp pending, FinanceHub over cap)\n"
            "- Audit trail: every adjustment lists its approver field, evidence and source entry\n"
            "- Prepared for: CFO + finance team\n\n"
            "Source: [Synthetic CRM + financial systems + D365 snapshot]\n\n"
            "**Next step:** Need anything else for month-end close?\n\n"
            "> Draft package only; no invoice was posted or sent, no revenue was recognized in the ledger, "
            "and no write-off was posted. An authorized billing manager approves and sends."
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = TimeEntryBillingAgent()
    for op in ["month_end_close", "flagged_review", "budget_overruns", "dispute_resolution", "final_invoices"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
