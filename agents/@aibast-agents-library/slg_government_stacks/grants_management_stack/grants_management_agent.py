"""
SLG Grants Management Agent — SLG Government Stack

Manages state and local government grant portfolios including
application tracking, reporting calendars, and budget monitoring.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/slg-grants-management",
    "version": "1.0.0",
    "display_name": "SLG Grants Management Agent",
    "description": "State and local government grants portfolio management with application tracking, reporting calendars, and budget monitoring.",
    "author": "AIBAST",
    "tags": ["grants", "budget", "reporting", "local-government", "state-government"],
    "category": "slg_government",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

GRANTS_PORTFOLIO = {
    "LG-2025-001": {
        "title": "Community Policing Initiative Grant",
        "grantor": "State Dept. of Justice",
        "amount": 475000,
        "match_required": 0.25,
        "local_match": 118750,
        "start_date": "2024-07-01",
        "end_date": "2026-06-30",
        "status": "active",
        "department": "Police Department",
        "spent": 198000,
        "encumbered": 52000,
    },
    "LG-2025-002": {
        "title": "Clean Water Infrastructure Improvement",
        "grantor": "EPA — State Revolving Fund",
        "amount": 2800000,
        "match_required": 0.20,
        "local_match": 560000,
        "start_date": "2025-01-01",
        "end_date": "2027-12-31",
        "status": "active",
        "department": "Public Works",
        "spent": 140000,
        "encumbered": 825000,
    },
    "LG-2025-003": {
        "title": "Youth Employment Summer Program",
        "grantor": "State Dept. of Labor",
        "amount": 165000,
        "match_required": 0.10,
        "local_match": 16500,
        "start_date": "2025-04-01",
        "end_date": "2025-09-30",
        "status": "pending_award",
        "department": "Parks & Recreation",
        "spent": 0,
        "encumbered": 0,
    },
    "LG-2025-004": {
        "title": "Broadband Expansion — Underserved Areas",
        "grantor": "NTIA — BEAD Program",
        "amount": 1250000,
        "match_required": 0.25,
        "local_match": 312500,
        "start_date": "2025-03-01",
        "end_date": "2028-02-28",
        "status": "application_submitted",
        "department": "IT Department",
        "spent": 0,
        "encumbered": 0,
    },
    "LG-2025-005": {
        "title": "Historic Downtown Revitalization",
        "grantor": "State Historic Preservation Office",
        "amount": 380000,
        "match_required": 0.50,
        "local_match": 190000,
        "start_date": "2024-10-01",
        "end_date": "2026-09-30",
        "status": "active",
        "department": "Community Development",
        "spent": 142500,
        "encumbered": 67000,
    },
}

APPLICATION_WORKFLOWS = {
    "pre_application": ["Identify funding opportunity", "Review NOFO requirements", "Assess eligibility", "Obtain internal authorization"],
    "application": ["Prepare project narrative", "Develop budget justification", "Gather required certifications", "Complete SF-424 forms", "Submit via grants.gov or state portal"],
    "post_submission": ["Confirm receipt", "Respond to clarification requests", "Await award notification"],
    "award_setup": ["Execute grant agreement", "Set up grant fund codes in ERP", "Establish reporting calendar", "Notify department leads"],
    "implementation": ["Procure goods/services per grant terms", "Track expenditures against budget", "Submit progress reports", "Monitor compliance"],
    "closeout": ["Complete final expenditure report", "Submit final performance report", "Return unused funds", "Archive documentation"],
}

REPORTING_REQUIREMENTS = {
    "LG-2025-001": [
        {"report": "Quarterly Financial Report", "due": "2025-04-15", "status": "upcoming"},
        {"report": "Semi-Annual Performance Report", "due": "2025-07-31", "status": "upcoming"},
        {"report": "Annual Single Audit (if applicable)", "due": "2025-12-31", "status": "upcoming"},
    ],
    "LG-2025-002": [
        {"report": "Monthly Draw Request", "due": "2025-04-10", "status": "upcoming"},
        {"report": "Quarterly Progress Report", "due": "2025-04-30", "status": "upcoming"},
        {"report": "Davis-Bacon Certified Payroll", "due": "2025-04-07", "status": "upcoming"},
    ],
    "LG-2025-005": [
        {"report": "Quarterly Expenditure Report", "due": "2025-04-15", "status": "upcoming"},
        {"report": "Photo Documentation Update", "due": "2025-06-30", "status": "upcoming"},
        {"report": "Historic Preservation Compliance Review", "due": "2025-09-30", "status": "upcoming"},
    ],
}

BUDGET_CATEGORIES = {
    "personnel": "Salaries, wages, and fringe benefits",
    "contractual": "Professional services and subcontracts",
    "equipment": "Capital equipment over $5,000",
    "supplies": "Office and operational supplies",
    "travel": "Staff travel and training",
    "indirect": "Indirect cost allocation",
    "other": "Miscellaneous direct costs",
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _portfolio_totals():
    """Aggregate portfolio financial totals."""
    total_awards = sum(g["amount"] for g in GRANTS_PORTFOLIO.values())
    total_match = sum(g["local_match"] for g in GRANTS_PORTFOLIO.values())
    total_spent = sum(g["spent"] for g in GRANTS_PORTFOLIO.values())
    total_encumbered = sum(g["encumbered"] for g in GRANTS_PORTFOLIO.values())
    available = total_awards - total_spent - total_encumbered
    return {
        "total_awards": total_awards,
        "total_match": total_match,
        "total_spent": total_spent,
        "total_encumbered": total_encumbered,
        "available": available,
    }


def _burn_rate(grant):
    """Calculate spending rate as percentage of award."""
    if grant["amount"] == 0:
        return 0.0
    return round(((grant["spent"] + grant["encumbered"]) / grant["amount"]) * 100, 1)


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class SLGGrantsManagementAgent(BasicAgent):
    """State and local government grants management agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/slg-grants-management"
        self.metadata = {
            "name": self.name,
            "display_name": "SLG Grants Management Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "grants_portfolio",
                            "application_status",
                            "reporting_calendar",
                            "budget_tracking",
                        ],
                    },
                    "grant_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "grants_portfolio")
        dispatch = {
            "grants_portfolio": self._grants_portfolio,
            "application_status": self._application_status,
            "reporting_calendar": self._reporting_calendar,
            "budget_tracking": self._budget_tracking,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _grants_portfolio(self, **kwargs) -> str:
        totals = _portfolio_totals()
        lines = ["# Grants Portfolio Overview\n"]
        lines.append(f"**Total Awards:** ${totals['total_awards']:,.0f}")
        lines.append(f"**Local Match Committed:** ${totals['total_match']:,.0f}")
        lines.append(f"**Spent:** ${totals['total_spent']:,.0f}")
        lines.append(f"**Encumbered:** ${totals['total_encumbered']:,.0f}")
        lines.append(f"**Available:** ${totals['available']:,.0f}\n")
        lines.append("| Grant ID | Title | Grantor | Amount | Status | Dept |")
        lines.append("|---|---|---|---|---|---|")
        for gid, g in GRANTS_PORTFOLIO.items():
            lines.append(
                f"| {gid} | {g['title']} | {g['grantor']} "
                f"| ${g['amount']:,.0f} | {g['status'].replace('_', ' ').title()} | {g['department']} |"
            )
        return "\n".join(lines)

    def _application_status(self, **kwargs) -> str:
        lines = ["# Grant Application Status\n"]
        pending = {k: v for k, v in GRANTS_PORTFOLIO.items() if v["status"] in ("pending_award", "application_submitted")}
        if pending:
            lines.append("## Pending Applications\n")
            for gid, g in pending.items():
                lines.append(f"### {gid}: {g['title']}\n")
                lines.append(f"- **Grantor:** {g['grantor']}")
                lines.append(f"- **Amount Requested:** ${g['amount']:,.0f}")
                lines.append(f"- **Match Required:** {g['match_required'] * 100:.0f}% (${g['local_match']:,.0f})")
                lines.append(f"- **Status:** {g['status'].replace('_', ' ').title()}")
                lines.append(f"- **Department:** {g['department']}\n")
        lines.append("## Application Workflow Reference\n")
        for phase, steps in APPLICATION_WORKFLOWS.items():
            lines.append(f"### {phase.replace('_', ' ').title()}\n")
            for i, step in enumerate(steps, 1):
                lines.append(f"{i}. {step}")
            lines.append("")
        return "\n".join(lines)

    def _reporting_calendar(self, **kwargs) -> str:
        lines = ["# Grant Reporting Calendar\n"]
        for gid, reports in REPORTING_REQUIREMENTS.items():
            grant = GRANTS_PORTFOLIO.get(gid, {})
            lines.append(f"## {gid}: {grant.get('title', 'Unknown')}\n")
            lines.append("| Report | Due Date | Status |")
            lines.append("|---|---|---|")
            for r in reports:
                lines.append(f"| {r['report']} | {r['due']} | {r['status'].title()} |")
            lines.append("")
        all_reports = []
        for gid, reports in REPORTING_REQUIREMENTS.items():
            for r in reports:
                all_reports.append({"grant": gid, "report": r["report"], "due": r["due"]})
        all_reports.sort(key=lambda x: x["due"])
        lines.append("## Upcoming Reports (All Grants)\n")
        lines.append("| Due Date | Grant | Report |")
        lines.append("|---|---|---|")
        for r in all_reports[:10]:
            lines.append(f"| {r['due']} | {r['grant']} | {r['report']} |")
        return "\n".join(lines)

    def _budget_tracking(self, **kwargs) -> str:
        grant_id = kwargs.get("grant_id")
        lines = ["# Grant Budget Tracking\n"]
        grants = {}
        if grant_id and grant_id in GRANTS_PORTFOLIO:
            grants = {grant_id: GRANTS_PORTFOLIO[grant_id]}
        else:
            grants = {k: v for k, v in GRANTS_PORTFOLIO.items() if v["status"] == "active"}
        for gid, g in grants.items():
            rate = _burn_rate(g)
            available = g["amount"] - g["spent"] - g["encumbered"]
            lines.append(f"## {gid}: {g['title']}\n")
            lines.append(f"- **Award Amount:** ${g['amount']:,.0f}")
            lines.append(f"- **Local Match:** ${g['local_match']:,.0f} ({g['match_required'] * 100:.0f}%)")
            lines.append(f"- **Spent:** ${g['spent']:,.0f}")
            lines.append(f"- **Encumbered:** ${g['encumbered']:,.0f}")
            lines.append(f"- **Available:** ${available:,.0f}")
            lines.append(f"- **Burn Rate:** {rate}%")
            lines.append(f"- **Period:** {g['start_date']} to {g['end_date']}\n")
        lines.append("## Budget Category Reference\n")
        for cat, desc in BUDGET_CATEGORIES.items():
            lines.append(f"- **{cat.title()}:** {desc}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = SLGGrantsManagementAgent()
    print(agent.perform(operation="grants_portfolio"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="application_status"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="reporting_calendar"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="budget_tracking"))
