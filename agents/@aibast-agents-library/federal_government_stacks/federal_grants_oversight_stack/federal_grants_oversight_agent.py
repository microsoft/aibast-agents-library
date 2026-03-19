"""
Federal Grants Oversight Agent — Federal Government Stack

Monitors federal grant programs with dashboards, compliance tracking,
reporting status updates, and audit preparation support for grant
program managers and oversight officers.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/federal-grants-oversight",
    "version": "1.0.0",
    "display_name": "Federal Grants Oversight Agent",
    "description": "Federal grants monitoring with dashboards, compliance tracking, reporting status, and audit preparation.",
    "author": "AIBAST",
    "tags": ["grants", "oversight", "compliance", "audit", "federal", "reporting"],
    "category": "federal_government",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

FEDERAL_GRANTS = {
    "GRT-2025-4401": {
        "program": "Homeland Security Grant Program (HSGP)",
        "cfda": "97.067",
        "recipient": "State of Virginia — Dept. of Emergency Management",
        "award_amount": 8750000,
        "federal_share": 0.75,
        "period_start": "2024-10-01",
        "period_end": "2027-09-30",
        "status": "active",
        "funds_drawn": 3125000,
        "milestones": {
            "equipment_procurement": {"due": "2025-06-30", "status": "in_progress", "pct": 62},
            "training_exercises": {"due": "2025-12-31", "status": "on_track", "pct": 35},
            "final_report": {"due": "2027-09-30", "status": "pending", "pct": 0},
        },
    },
    "GRT-2025-4402": {
        "program": "Community Development Block Grant (CDBG)",
        "cfda": "14.218",
        "recipient": "City of Richmond — Housing Authority",
        "award_amount": 3200000,
        "federal_share": 1.0,
        "period_start": "2025-01-01",
        "period_end": "2026-12-31",
        "status": "active",
        "funds_drawn": 480000,
        "milestones": {
            "needs_assessment": {"due": "2025-03-31", "status": "complete", "pct": 100},
            "construction_phase_1": {"due": "2025-09-30", "status": "in_progress", "pct": 28},
            "construction_phase_2": {"due": "2026-06-30", "status": "pending", "pct": 0},
            "close_out": {"due": "2026-12-31", "status": "pending", "pct": 0},
        },
    },
    "GRT-2025-4403": {
        "program": "COPS Hiring Program (CHP)",
        "cfda": "16.710",
        "recipient": "Metro Police Department — District 5",
        "award_amount": 1875000,
        "federal_share": 0.75,
        "period_start": "2024-07-01",
        "period_end": "2027-06-30",
        "status": "active",
        "funds_drawn": 937500,
        "milestones": {
            "hiring_cohort_1": {"due": "2025-01-15", "status": "complete", "pct": 100},
            "hiring_cohort_2": {"due": "2025-07-15", "status": "in_progress", "pct": 45},
            "retention_review": {"due": "2026-07-15", "status": "pending", "pct": 0},
            "final_report": {"due": "2027-06-30", "status": "pending", "pct": 0},
        },
    },
    "GRT-2025-4404": {
        "program": "Title III — Strengthening Institutions",
        "cfda": "84.031",
        "recipient": "Westfield Community College",
        "award_amount": 2100000,
        "federal_share": 1.0,
        "period_start": "2024-10-01",
        "period_end": "2029-09-30",
        "status": "active",
        "funds_drawn": 420000,
        "milestones": {
            "curriculum_redesign": {"due": "2025-08-31", "status": "in_progress", "pct": 55},
            "technology_upgrade": {"due": "2026-03-31", "status": "pending", "pct": 0},
            "faculty_development": {"due": "2027-09-30", "status": "pending", "pct": 0},
            "sustainability_plan": {"due": "2029-06-30", "status": "pending", "pct": 0},
        },
    },
}

COMPLIANCE_REQUIREMENTS = {
    "2 CFR 200": {
        "title": "Uniform Administrative Requirements",
        "sections": {
            "200.302": {"name": "Financial Management", "frequency": "continuous"},
            "200.303": {"name": "Internal Controls", "frequency": "continuous"},
            "200.328": {"name": "Financial Reporting", "frequency": "quarterly"},
            "200.329": {"name": "Performance Reporting", "frequency": "semi-annual"},
            "200.344": {"name": "Closeout", "frequency": "end_of_grant"},
        },
    },
    "Single Audit": {
        "title": "Single Audit Act (A-133)",
        "sections": {
            "threshold": {"name": "Expenditure Threshold ($750K)", "frequency": "annual"},
            "findings": {"name": "Prior Year Findings Follow-up", "frequency": "annual"},
            "schedule": {"name": "Schedule of Expenditures (SEFA)", "frequency": "annual"},
        },
    },
}

AUDIT_FINDINGS = [
    {"id": "AF-2024-01", "grant": "GRT-2025-4401", "severity": "low", "finding": "Late submission of SF-425 Q2 report by 8 days", "status": "resolved", "corrective_action": "Automated reminders implemented"},
    {"id": "AF-2024-02", "grant": "GRT-2025-4402", "severity": "moderate", "finding": "Cost allocation methodology not documented for shared personnel", "status": "in_progress", "corrective_action": "Cost allocation plan under review"},
    {"id": "AF-2024-03", "grant": "GRT-2025-4403", "severity": "low", "finding": "Equipment inventory tags missing on 3 of 47 items", "status": "resolved", "corrective_action": "Physical inventory completed and reconciled"},
    {"id": "AF-2023-07", "grant": "GRT-2025-4404", "severity": "high", "finding": "Supplanting concern — state funding reduced concurrent with federal award", "status": "in_progress", "corrective_action": "MOE documentation being compiled by finance office"},
]

REPORTING_SCHEDULE = {
    "SF-425": {"name": "Federal Financial Report", "frequency": "quarterly", "next_due": "2025-04-30"},
    "SF-PPR": {"name": "Performance Progress Report", "frequency": "semi-annual", "next_due": "2025-06-30"},
    "A-133": {"name": "Single Audit Report", "frequency": "annual", "next_due": "2025-03-31"},
    "FFATA": {"name": "FFATA Sub-award Report", "frequency": "monthly", "next_due": "2025-04-15"},
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _portfolio_summary():
    """Compute aggregate portfolio metrics."""
    total_awarded = sum(g["award_amount"] for g in FEDERAL_GRANTS.values())
    total_drawn = sum(g["funds_drawn"] for g in FEDERAL_GRANTS.values())
    draw_rate = round((total_drawn / total_awarded) * 100, 1) if total_awarded else 0
    return {"total_awarded": total_awarded, "total_drawn": total_drawn, "draw_rate": draw_rate, "grant_count": len(FEDERAL_GRANTS)}


def _compliance_score(grant_id):
    """Compute compliance score for a grant based on findings."""
    findings = [f for f in AUDIT_FINDINGS if f["grant"] == grant_id]
    if not findings:
        return 100.0
    deductions = {"low": 5, "moderate": 15, "high": 30}
    total_deduction = sum(deductions.get(f["severity"], 0) for f in findings if f["status"] != "resolved")
    return max(0, 100 - total_deduction)


def _milestone_health(grant):
    """Assess milestone health across a grant."""
    milestones = grant["milestones"]
    total = len(milestones)
    complete = sum(1 for m in milestones.values() if m["status"] == "complete")
    at_risk = sum(1 for m in milestones.values() if m["status"] == "in_progress" and m["pct"] < 40)
    return {"total": total, "complete": complete, "at_risk": at_risk}


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class FederalGrantsOversightAgent(BasicAgent):
    """Federal grants oversight agent for program monitoring and compliance."""

    def __init__(self):
        self.name = "@aibast-agents-library/federal-grants-oversight"
        self.metadata = {
            "name": self.name,
            "display_name": "Federal Grants Oversight Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "grants_dashboard",
                            "compliance_monitoring",
                            "reporting_status",
                            "audit_preparation",
                        ],
                    },
                    "grant_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "grants_dashboard")
        dispatch = {
            "grants_dashboard": self._grants_dashboard,
            "compliance_monitoring": self._compliance_monitoring,
            "reporting_status": self._reporting_status,
            "audit_preparation": self._audit_preparation,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _grants_dashboard(self, **kwargs) -> str:
        summary = _portfolio_summary()
        lines = ["# Federal Grants Dashboard\n"]
        lines.append(f"**Total Awards:** {summary['grant_count']}")
        lines.append(f"**Total Awarded:** ${summary['total_awarded']:,.0f}")
        lines.append(f"**Total Drawn:** ${summary['total_drawn']:,.0f}")
        lines.append(f"**Draw Rate:** {summary['draw_rate']}%\n")
        lines.append("## Grant Portfolio\n")
        lines.append("| Grant ID | Program | Recipient | Award | Drawn | Status |")
        lines.append("|---|---|---|---|---|---|")
        for gid, g in FEDERAL_GRANTS.items():
            lines.append(
                f"| {gid} | {g['program']} | {g['recipient']} "
                f"| ${g['award_amount']:,.0f} | ${g['funds_drawn']:,.0f} | {g['status'].title()} |"
            )
        lines.append("\n## Milestone Summary\n")
        for gid, g in FEDERAL_GRANTS.items():
            health = _milestone_health(g)
            lines.append(f"- **{gid}:** {health['complete']}/{health['total']} complete, {health['at_risk']} at risk")
        return "\n".join(lines)

    def _compliance_monitoring(self, **kwargs) -> str:
        lines = ["# Compliance Monitoring Report\n"]
        lines.append("## Grant Compliance Scores\n")
        lines.append("| Grant ID | Program | Compliance Score |")
        lines.append("|---|---|---|")
        for gid, g in FEDERAL_GRANTS.items():
            score = _compliance_score(gid)
            lines.append(f"| {gid} | {g['program']} | {score}% |")
        lines.append("\n## Regulatory Framework\n")
        for reg_id, reg in COMPLIANCE_REQUIREMENTS.items():
            lines.append(f"### {reg_id} — {reg['title']}\n")
            for sec_id, sec in reg["sections"].items():
                lines.append(f"- **{sec_id}:** {sec['name']} ({sec['frequency']})")
            lines.append("")
        lines.append("## Active Findings\n")
        active = [f for f in AUDIT_FINDINGS if f["status"] != "resolved"]
        if active:
            lines.append("| Finding ID | Grant | Severity | Finding | Status |")
            lines.append("|---|---|---|---|---|")
            for f in active:
                lines.append(f"| {f['id']} | {f['grant']} | {f['severity'].upper()} | {f['finding']} | {f['status']} |")
        else:
            lines.append("No active findings.")
        return "\n".join(lines)

    def _reporting_status(self, **kwargs) -> str:
        lines = ["# Grant Reporting Status\n"]
        lines.append("## Upcoming Reports\n")
        lines.append("| Report | Name | Frequency | Next Due |")
        lines.append("|---|---|---|---|")
        for rid, r in REPORTING_SCHEDULE.items():
            lines.append(f"| {rid} | {r['name']} | {r['frequency'].title()} | {r['next_due']} |")
        lines.append("\n## Grant-Level Milestones\n")
        for gid, g in FEDERAL_GRANTS.items():
            lines.append(f"### {gid} — {g['program']}\n")
            lines.append("| Milestone | Due Date | Status | Progress |")
            lines.append("|---|---|---|---|")
            for mname, mdata in g["milestones"].items():
                display = mname.replace("_", " ").title()
                lines.append(f"| {display} | {mdata['due']} | {mdata['status'].replace('_', ' ').title()} | {mdata['pct']}% |")
            lines.append("")
        return "\n".join(lines)

    def _audit_preparation(self, **kwargs) -> str:
        lines = ["# Audit Preparation Report\n"]
        lines.append("## Prior Findings Status\n")
        lines.append("| Finding ID | Grant | Severity | Finding | Status | Corrective Action |")
        lines.append("|---|---|---|---|---|---|")
        for f in AUDIT_FINDINGS:
            lines.append(
                f"| {f['id']} | {f['grant']} | {f['severity'].upper()} "
                f"| {f['finding']} | {f['status'].replace('_', ' ').title()} | {f['corrective_action']} |"
            )
        resolved = sum(1 for f in AUDIT_FINDINGS if f["status"] == "resolved")
        total = len(AUDIT_FINDINGS)
        lines.append(f"\n**Findings Resolved:** {resolved}/{total}")
        lines.append("\n## Audit Readiness Checklist\n")
        checklist = [
            "Schedule of Expenditures of Federal Awards (SEFA) prepared",
            "Cost allocation plans current and documented",
            "Subrecipient monitoring documentation complete",
            "Equipment inventory reconciled",
            "Time-and-effort certifications on file",
            "Procurement documentation meets federal standards",
            "Financial reconciliation between GL and drawdowns",
            "Prior year corrective action plans implemented",
        ]
        for item in checklist:
            lines.append(f"- [ ] {item}")
        lines.append("\n## Single Audit Threshold Analysis\n")
        total_expended = sum(g["funds_drawn"] for g in FEDERAL_GRANTS.values())
        threshold = 750000
        lines.append(f"- **Total Federal Expenditures:** ${total_expended:,.0f}")
        lines.append(f"- **Single Audit Threshold:** ${threshold:,.0f}")
        above = "Yes" if total_expended >= threshold else "No"
        lines.append(f"- **Audit Required:** {above}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = FederalGrantsOversightAgent()
    print(agent.perform(operation="grants_dashboard"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="compliance_monitoring"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="reporting_status"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="audit_preparation"))
