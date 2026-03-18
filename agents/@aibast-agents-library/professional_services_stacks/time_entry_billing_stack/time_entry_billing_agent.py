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
    "version": "1.0.0",
    "display_name": "Time Entry & Billing Agent",
    "description": "Processes time entries against billing rules, surfaces unbilled hours, audits entries for compliance, and prepares invoice packages.",
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


def _budget_status(project_name):
    """Return budget consumption percentage."""
    budget = PROJECT_BUDGETS.get(project_name, {})
    if not budget or budget["total_budget"] == 0:
        return 0
    return round(budget["billed_to_date"] / budget["total_budget"] * 100, 1)


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class TimeEntryBillingAgent(BasicAgent):
    """Processes time entries and generates billing reports."""

    def __init__(self):
        self.name = "TimeEntryBillingAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "operations": [
                "unbilled_report",
                "billing_summary",
                "time_entry_audit",
                "invoice_preparation",
            ],
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "unbilled_report")
        dispatch = {
            "unbilled_report": self._unbilled_report,
            "billing_summary": self._billing_summary,
            "time_entry_audit": self._time_entry_audit,
            "invoice_preparation": self._invoice_preparation,
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
                    f"| {te['id']} | {te['consultant']} | {te['project'][:20]} | {te['date']} | "
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
                f"| {proj[:24]} | {budget['client'][:18]} | {budget['contract_type']} | "
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
            lines.append(f"| {proj[:24]} | {used}% | ${budget['remaining']:,.0f} | **{status}** |")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _invoice_preparation(self, **kwargs) -> str:
        lines = ["## Invoice Preparation\n"]
        lines.append("### Invoices Ready to Generate\n")

        # Group approved billable entries by project/client
        by_project = {}
        for te in TIME_ENTRIES:
            if te["category"] == "billable" and te["approved"]:
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
                f"| {proj[:24]} | {client[:18]} | {data['entries']} | {data['hours']} | "
                f"${data['value']:,.2f} | {ctype} |"
            )
        lines.append(f"\n**Grand total ready to invoice:** ${grand_total:,.2f}")

        unbilled = _unbilled_entries()
        unbilled_val = sum(te["hours"] * te["rate"] for te in unbilled)
        lines.append(f"**Pending approval (not included):** ${unbilled_val:,.2f}")

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
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = TimeEntryBillingAgent()
    for op in agent.metadata["operations"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
