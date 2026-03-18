"""
Financial Services Regulatory Compliance Agent — Financial Services Stack

Manages compliance dashboards, regulation tracking, remediation planning,
and examination preparation for financial institution compliance teams.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/fs-regulatory-compliance",
    "version": "1.0.0",
    "display_name": "FS Regulatory Compliance Agent",
    "description": "Financial services regulatory compliance with SOX, Dodd-Frank, BSA tracking, remediation planning, and examiner preparation.",
    "author": "AIBAST",
    "tags": ["compliance", "SOX", "Dodd-Frank", "BSA", "AML", "regulatory", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

REGULATIONS = {
    "SOX": {
        "full_name": "Sarbanes-Oxley Act",
        "sections": {"302": "CEO/CFO Certification", "404": "Internal Controls Assessment", "409": "Real-Time Disclosure"},
        "regulator": "SEC",
        "compliance_score": 92.0,
        "last_assessment": "2025-01-31",
        "next_assessment": "2025-07-31",
    },
    "Dodd-Frank": {
        "full_name": "Dodd-Frank Wall Street Reform Act",
        "sections": {"Volcker": "Proprietary Trading Restrictions", "Title VII": "Derivatives Regulation", "Title X": "Consumer Protection"},
        "regulator": "Fed / OCC / CFPB",
        "compliance_score": 87.5,
        "last_assessment": "2024-12-15",
        "next_assessment": "2025-06-15",
    },
    "BSA-AML": {
        "full_name": "Bank Secrecy Act / Anti-Money Laundering",
        "sections": {"CDD": "Customer Due Diligence", "SAR": "Suspicious Activity Reporting", "CTR": "Currency Transaction Reporting"},
        "regulator": "FinCEN / OCC",
        "compliance_score": 84.0,
        "last_assessment": "2025-02-28",
        "next_assessment": "2025-08-31",
    },
    "GLBA": {
        "full_name": "Gramm-Leach-Bliley Act",
        "sections": {"Privacy": "Financial Privacy Rule", "Safeguards": "Safeguards Rule", "Pretexting": "Pretexting Protection"},
        "regulator": "FTC / Fed",
        "compliance_score": 95.0,
        "last_assessment": "2025-01-15",
        "next_assessment": "2026-01-15",
    },
    "FCRA": {
        "full_name": "Fair Credit Reporting Act",
        "sections": {"Accuracy": "Information Accuracy", "Disputes": "Consumer Dispute Resolution", "Furnishing": "Data Furnisher Requirements"},
        "regulator": "CFPB",
        "compliance_score": 89.0,
        "last_assessment": "2024-11-30",
        "next_assessment": "2025-05-31",
    },
}

EXAMINATION_FINDINGS = [
    {"id": "EF-2024-01", "regulation": "BSA-AML", "finding": "SAR filing timeliness below 90% threshold", "severity": "moderate", "status": "remediation_in_progress", "due": "2025-06-30", "owner": "BSA Officer"},
    {"id": "EF-2024-02", "regulation": "BSA-AML", "finding": "CDD refresh cycle exceeding 24-month requirement for high-risk customers", "severity": "significant", "status": "open", "due": "2025-04-30", "owner": "BSA Officer"},
    {"id": "EF-2024-03", "regulation": "SOX", "finding": "Access control review documentation incomplete for 2 IT systems", "severity": "moderate", "status": "remediation_in_progress", "due": "2025-05-31", "owner": "IT Audit Manager"},
    {"id": "EF-2024-04", "regulation": "Dodd-Frank", "finding": "Consumer complaint response time exceeded 15-day requirement in 8% of cases", "severity": "low", "status": "closed", "due": "2025-03-31", "owner": "Consumer Compliance"},
    {"id": "EF-2024-05", "regulation": "FCRA", "finding": "Dispute resolution letters missing required disclosures in 3 cases", "severity": "low", "status": "closed", "due": "2025-02-28", "owner": "Operations Manager"},
]

REMEDIATION_PLANS = [
    {"finding": "EF-2024-01", "action": "Implement automated SAR filing workflow with deadline alerts", "milestone": "2025-05-15", "pct": 60, "owner": "BSA Officer"},
    {"finding": "EF-2024-02", "action": "Accelerate CDD refresh for 142 high-risk customers", "milestone": "2025-04-15", "pct": 35, "owner": "BSA Officer"},
    {"finding": "EF-2024-03", "action": "Complete access review documentation for Oracle EBS and Salesforce", "milestone": "2025-04-30", "pct": 70, "owner": "IT Audit Manager"},
]

UPCOMING_EXAMINATIONS = [
    {"examiner": "OCC", "type": "Safety & Soundness", "scheduled": "2025-05-12", "duration_weeks": 3, "lead_examiner": "Regional Examiner — District 4"},
    {"examiner": "FinCEN", "type": "BSA/AML Targeted Review", "scheduled": "2025-07-01", "duration_weeks": 2, "lead_examiner": "FinCEN Enforcement Division"},
    {"examiner": "CFPB", "type": "Consumer Compliance", "scheduled": "2025-09-15", "duration_weeks": 2, "lead_examiner": "CFPB Supervision — Region III"},
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _overall_compliance():
    """Weighted overall compliance score."""
    weights = {"SOX": 0.25, "Dodd-Frank": 0.20, "BSA-AML": 0.25, "GLBA": 0.15, "FCRA": 0.15}
    score = sum(REGULATIONS[r]["compliance_score"] * w for r, w in weights.items())
    return round(score, 1)


def _open_findings_count():
    """Count open findings."""
    return sum(1 for f in EXAMINATION_FINDINGS if f["status"] not in ("closed",))


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class FSRegulatoryComplianceAgent(BasicAgent):
    """Financial services regulatory compliance agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/fs-regulatory-compliance"
        self.metadata = {
            "name": self.name,
            "display_name": "FS Regulatory Compliance Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "compliance_dashboard",
                            "regulation_tracker",
                            "remediation_plan",
                            "examiner_prep",
                        ],
                    },
                    "regulation": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "compliance_dashboard")
        dispatch = {
            "compliance_dashboard": self._compliance_dashboard,
            "regulation_tracker": self._regulation_tracker,
            "remediation_plan": self._remediation_plan,
            "examiner_prep": self._examiner_prep,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _compliance_dashboard(self, **kwargs) -> str:
        overall = _overall_compliance()
        open_count = _open_findings_count()
        lines = ["# FS Regulatory Compliance Dashboard\n"]
        lines.append(f"**Overall Compliance Score:** {overall}%")
        lines.append(f"**Open Findings:** {open_count}\n")
        lines.append("## Regulation Scores\n")
        lines.append("| Regulation | Full Name | Regulator | Score | Last Assessed | Next Due |")
        lines.append("|---|---|---|---|---|---|")
        for reg_id, reg in REGULATIONS.items():
            lines.append(
                f"| {reg_id} | {reg['full_name']} | {reg['regulator']} "
                f"| {reg['compliance_score']}% | {reg['last_assessment']} | {reg['next_assessment']} |"
            )
        lines.append("\n## Findings Summary\n")
        by_status = {}
        for f in EXAMINATION_FINDINGS:
            by_status[f["status"]] = by_status.get(f["status"], 0) + 1
        for status, count in by_status.items():
            lines.append(f"- {status.replace('_', ' ').title()}: {count}")
        return "\n".join(lines)

    def _regulation_tracker(self, **kwargs) -> str:
        regulation = kwargs.get("regulation")
        regs = REGULATIONS
        if regulation and regulation in REGULATIONS:
            regs = {regulation: REGULATIONS[regulation]}
        lines = ["# Regulation Tracker\n"]
        for reg_id, reg in regs.items():
            lines.append(f"## {reg_id} — {reg['full_name']}\n")
            lines.append(f"- **Regulator:** {reg['regulator']}")
            lines.append(f"- **Compliance Score:** {reg['compliance_score']}%")
            lines.append(f"- **Last Assessment:** {reg['last_assessment']}")
            lines.append(f"- **Next Assessment:** {reg['next_assessment']}\n")
            lines.append("### Key Sections\n")
            for sec_id, sec_name in reg["sections"].items():
                lines.append(f"- **{sec_id}:** {sec_name}")
            findings = [f for f in EXAMINATION_FINDINGS if f["regulation"] == reg_id]
            if findings:
                lines.append(f"\n### Findings ({len(findings)})\n")
                for f in findings:
                    lines.append(f"- **{f['id']}** [{f['severity'].upper()}]: {f['finding']} — {f['status'].replace('_', ' ').title()}")
            lines.append("")
        return "\n".join(lines)

    def _remediation_plan(self, **kwargs) -> str:
        lines = ["# Remediation Plan Status\n"]
        lines.append("| Finding | Action | Owner | Milestone | Progress |")
        lines.append("|---|---|---|---|---|")
        for r in REMEDIATION_PLANS:
            lines.append(
                f"| {r['finding']} | {r['action']} | {r['owner']} "
                f"| {r['milestone']} | {r['pct']}% |"
            )
        avg_progress = sum(r["pct"] for r in REMEDIATION_PLANS) / len(REMEDIATION_PLANS) if REMEDIATION_PLANS else 0
        lines.append(f"\n**Average Progress:** {avg_progress:.0f}%")
        lines.append("\n## Open Findings Requiring Remediation\n")
        open_findings = [f for f in EXAMINATION_FINDINGS if f["status"] != "closed"]
        for f in open_findings:
            lines.append(f"- **{f['id']}** ({f['regulation']}) — {f['finding']} [Due: {f['due']}]")
        return "\n".join(lines)

    def _examiner_prep(self, **kwargs) -> str:
        lines = ["# Examination Preparation\n"]
        lines.append("## Upcoming Examinations\n")
        lines.append("| Examiner | Type | Scheduled | Duration | Lead |")
        lines.append("|---|---|---|---|---|")
        for exam in UPCOMING_EXAMINATIONS:
            lines.append(
                f"| {exam['examiner']} | {exam['type']} | {exam['scheduled']} "
                f"| {exam['duration_weeks']} weeks | {exam['lead_examiner']} |"
            )
        lines.append("\n## Pre-Examination Checklist\n")
        checklist = [
            "Board and committee minutes prepared and indexed",
            "Policies and procedures current with regulatory changes",
            "Internal audit reports available for last 3 years",
            "Compliance testing results documented",
            "Prior MRA/MRIA status updates prepared",
            "Capital adequacy and stress test results available",
            "BSA/AML independent testing report current",
            "Consumer complaint log updated",
            "IT risk assessment and SOC reports available",
            "Organizational chart and key personnel list current",
        ]
        for item in checklist:
            lines.append(f"- [ ] {item}")
        lines.append("\n## Prior Finding Status for Examiners\n")
        lines.append("| Finding | Regulation | Severity | Status | Due |")
        lines.append("|---|---|---|---|---|")
        for f in EXAMINATION_FINDINGS:
            lines.append(
                f"| {f['id']} | {f['regulation']} | {f['severity'].title()} "
                f"| {f['status'].replace('_', ' ').title()} | {f['due']} |"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = FSRegulatoryComplianceAgent()
    print(agent.perform(operation="compliance_dashboard"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="regulation_tracker", regulation="BSA-AML"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="remediation_plan"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="examiner_prep"))
