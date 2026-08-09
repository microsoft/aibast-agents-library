"""
Energy Regulatory Reporting Agent.

Manages regulatory report status tracking, data validation, submission
workflows, and audit readiness assessments for EPA, FERC, and state
regulatory filings.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/energy-regulatory-reporting",
    "version": "1.1.0",
    "display_name": "Regulatory Reporting Agent",
    "description": "Review synthetic energy regulatory-report status, data-validation exceptions, submission tracking, and audit-readiness findings. Use for EPA, FERC, PHMSA, or state reporting preparation. The agent never files, certifies, signs, or transmits a report; an authorized regulatory owner must approve a source-backed package through future authenticated tools.",
    "author": "AIBAST",
    "tags": ["regulatory", "reporting", "epa", "ferc", "audit", "compliance", "energy"],
    "category": "energy",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

REGULATORY_REPORTS = {
    "RPT-9001": {
        "name": "EPA GHG Reporting Program (Subpart C)",
        "authority": "EPA",
        "facility": "Riverside Generating Station",
        "reporting_period": "CY 2025",
        "deadline": "2026-03-31",
        "status": "in_progress",
        "data_quality_score": 87,
        "completeness_pct": 78,
        "assignee": "Environmental Compliance Team",
        "last_updated": "2026-03-10",
    },
    "RPT-9002": {
        "name": "FERC Form 1 Annual Report",
        "authority": "FERC",
        "facility": "Corporate (All Facilities)",
        "reporting_period": "CY 2025",
        "deadline": "2026-04-18",
        "status": "in_progress",
        "data_quality_score": 92,
        "completeness_pct": 65,
        "assignee": "Regulatory Affairs",
        "last_updated": "2026-03-12",
    },
    "RPT-9003": {
        "name": "TCEQ Annual Emissions Inventory",
        "authority": "State - Texas",
        "facility": "Bayshore Refinery",
        "reporting_period": "CY 2025",
        "deadline": "2026-03-31",
        "status": "submitted",
        "data_quality_score": 95,
        "completeness_pct": 100,
        "assignee": "Environmental Compliance Team",
        "last_updated": "2026-03-05",
    },
    "RPT-9004": {
        "name": "Colorado Air Quality Control Division Report",
        "authority": "State - Colorado",
        "facility": "Ridgeline Coal Station",
        "reporting_period": "CY 2025",
        "deadline": "2026-04-30",
        "status": "not_started",
        "data_quality_score": 0,
        "completeness_pct": 0,
        "assignee": "Environmental Compliance Team",
        "last_updated": None,
    },
    "RPT-9005": {
        "name": "EPA Toxics Release Inventory (TRI)",
        "authority": "EPA",
        "facility": "Bayshore Refinery",
        "reporting_period": "CY 2025",
        "deadline": "2026-07-01",
        "status": "in_progress",
        "data_quality_score": 74,
        "completeness_pct": 42,
        "assignee": "Health & Safety Team",
        "last_updated": "2026-02-28",
    },
    "RPT-9006": {
        "name": "PHMSA Annual Pipeline Safety Report",
        "authority": "PHMSA",
        "facility": "Northeast Corridor Pipeline",
        "reporting_period": "CY 2025",
        "deadline": "2026-03-15",
        "status": "overdue",
        "data_quality_score": 81,
        "completeness_pct": 90,
        "assignee": "Pipeline Operations",
        "last_updated": "2026-03-14",
    },
}

DATA_VALIDATION_RULES = {
    "emissions_data": {
        "rules": ["Non-negative values", "Year-over-year variance < 25%", "Mass balance check", "Unit conversion validation"],
        "source_systems": ["CEMS", "Fuel metering", "Production logs"],
    },
    "financial_data": {
        "rules": ["Reconciliation to GL", "Rate base validation", "Depreciation schedule check", "Intercompany elimination"],
        "source_systems": ["SAP", "PowerPlan", "Hyperion"],
    },
    "safety_data": {
        "rules": ["Incident classification verification", "Mileage data reconciliation", "Leak survey completeness"],
        "source_systems": ["PIMS", "GIS", "Inspection database"],
    },
}

AUDIT_FINDINGS = {
    "AUD-001": {"report": "RPT-9001", "finding": "Missing CEMS calibration records for Q3", "severity": "medium", "status": "open", "due_date": "2026-03-25"},
    "AUD-002": {"report": "RPT-9002", "finding": "Depreciation schedule mismatch with PowerPlan", "severity": "high", "status": "remediated", "due_date": "2026-03-15"},
    "AUD-003": {"report": "RPT-9005", "finding": "Threshold calculation methodology not documented", "severity": "low", "status": "open", "due_date": "2026-05-01"},
    "AUD-004": {"report": "RPT-9006", "finding": "Pipeline mileage discrepancy between GIS and PIMS", "severity": "high", "status": "open", "due_date": "2026-03-20"},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _selected_reports(report_id=None):
    if report_id:
        return {report_id: REGULATORY_REPORTS[report_id]} if report_id in REGULATORY_REPORTS else {}
    return REGULATORY_REPORTS


def _report_status(report_id=None):
    reports = []
    for rid, r in _selected_reports(report_id).items():
        reports.append({
            "id": rid, "name": r["name"], "authority": r["authority"],
            "facility": r["facility"], "deadline": r["deadline"],
            "status": r["status"], "completeness_pct": r["completeness_pct"],
            "data_quality": r["data_quality_score"], "assignee": r["assignee"],
        })
    reports.sort(key=lambda x: x["deadline"])
    overdue = sum(1 for r in reports if r["status"] == "overdue")
    submitted = sum(1 for r in reports if r["status"] == "submitted")
    return {"reports": reports, "total": len(reports), "overdue": overdue, "submitted": submitted}


def _data_validation(report_id=None):
    validations = []
    for rid, r in _selected_reports(report_id).items():
        if r["status"] in ("not_started",):
            continue
        issues = []
        if r["data_quality_score"] < 80:
            issues.append(f"Data quality score below threshold ({r['data_quality_score']}/100)")
        if r["completeness_pct"] < 100 and r["status"] != "submitted":
            issues.append(f"Data collection incomplete ({r['completeness_pct']}%)")
        validations.append({
            "report_id": rid, "name": r["name"],
            "quality_score": r["data_quality_score"],
            "completeness": r["completeness_pct"],
            "issues": issues, "passed": len(issues) == 0,
        })
    return {"validations": validations, "pass_rate": round(sum(1 for v in validations if v["passed"]) / len(validations) * 100, 1) if validations else 0}


def _submission_tracker(report_id=None):
    tracker = []
    for rid, r in _selected_reports(report_id).items():
        tracker.append({
            "id": rid, "name": r["name"], "authority": r["authority"],
            "deadline": r["deadline"], "status": r["status"],
            "last_updated": r["last_updated"] or "N/A",
            "assignee": r["assignee"],
        })
    tracker.sort(key=lambda x: x["deadline"])
    return {"submissions": tracker}


def _audit_readiness(report_id=None):
    findings_by_report = {}
    for aid, af in AUDIT_FINDINGS.items():
        rid = af["report"]
        if report_id and rid != report_id:
            continue
        if rid not in findings_by_report:
            findings_by_report[rid] = []
        findings_by_report[rid].append({
            "id": aid, "finding": af["finding"],
            "severity": af["severity"], "status": af["status"],
            "due_date": af["due_date"],
        })
    selected_findings = [af for af in AUDIT_FINDINGS.values() if not report_id or af["report"] == report_id]
    open_findings = sum(1 for af in selected_findings if af["status"] == "open")
    high_sev = sum(1 for af in selected_findings if af["severity"] == "high" and af["status"] == "open")
    return {"findings_by_report": findings_by_report, "total_findings": len(selected_findings),
            "open_findings": open_findings, "high_severity_open": high_sev}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class RegulatoryReportingAgent(BasicAgent):
    """Regulatory reporting status and audit readiness agent."""

    def __init__(self):
        self.name = "RegulatoryReportingAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "report_status",
                            "data_validation",
                            "submission_tracker",
                            "audit_readiness",
                        ],
                        "description": "Choose report_status for the reporting portfolio, data_validation for source-quality exceptions, submission_tracker for read-only filing state, or audit_readiness for open evidence gaps.",
                    },
                    "report_id": {
                        "type": "string",
                        "description": "Optional synthetic report ID such as RPT-9006. Unknown IDs return an empty result.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "report_status")
        report_id = kwargs.get("report_id")
        if op == "report_status":
            return self._report_status(report_id)
        elif op == "data_validation":
            return self._data_validation(report_id)
        elif op == "submission_tracker":
            return self._submission_tracker(report_id)
        elif op == "audit_readiness":
            return self._audit_readiness(report_id)
        return f"**Error:** Unknown operation `{op}`."

    def _report_status(self, report_id=None) -> str:
        data = _report_status(report_id)
        lines = [
            "# Regulatory Report Status",
            "",
            f"**Total Reports:** {data['total']} | **Submitted:** {data['submitted']} | **Overdue:** {data['overdue']}",
            "",
            "| Report | Authority | Facility | Owner | Deadline | Status | Complete | Quality |",
            "|--------|-----------|----------|-------|----------|--------|---------|---------|",
        ]
        for r in data["reports"]:
            lines.append(
                f"| {r['name']} | {r['authority']} | {r['facility']} | {r['assignee']} "
                f"| {r['deadline']} | {r['status'].upper()} | {r['completeness_pct']}% | {r['data_quality']}/100 |"
            )
        lines.append("")
        lines.append("> Synthetic status snapshot. Confirm deadlines and filing state in the system of record.")
        return "\n".join(lines)

    def _data_validation(self, report_id=None) -> str:
        data = _data_validation(report_id)
        lines = [
            "# Data Validation Results",
            "",
            f"**Validation Pass Rate:** {data['pass_rate']}%",
            "",
            "| Report | Quality Score | Completeness | Issues | Passed |",
            "|--------|-------------|-------------|--------|--------|",
        ]
        for v in data["validations"]:
            passed = "YES" if v["passed"] else "NO"
            issue_str = "; ".join(v["issues"]) if v["issues"] else "None"
            lines.append(
                f"| {v['name']} | {v['quality_score']}/100 | {v['completeness']}% | {issue_str} | {passed} |"
            )
        lines.append("")
        lines.append("> Validation screening only. An authorized report owner must resolve and attest source evidence.")
        return "\n".join(lines)

    def _submission_tracker(self, report_id=None) -> str:
        data = _submission_tracker(report_id)
        lines = [
            "# Submission Tracker",
            "",
            "| Report | Authority | Owner | Deadline | Status | Last Updated |",
            "|--------|-----------|-------|----------|--------|-------------|",
        ]
        for s in data["submissions"]:
            lines.append(
                f"| {s['name']} | {s['authority']} | {s['assignee']} | {s['deadline']} "
                f"| {s['status'].upper()} | {s['last_updated']} |"
            )
        lines.append("")
        lines.append("> Read-only tracking. No regulator filing, certification, signature, or transmission has occurred.")
        return "\n".join(lines)

    def _audit_readiness(self, report_id=None) -> str:
        data = _audit_readiness(report_id)
        lines = [
            "# Audit Readiness Assessment",
            "",
            f"**Total Findings:** {data['total_findings']} | "
            f"**Open:** {data['open_findings']} | "
            f"**High Severity Open:** {data['high_severity_open']}",
            "",
        ]
        for rid, findings in data["findings_by_report"].items():
            rpt_name = REGULATORY_REPORTS.get(rid, {}).get("name", rid)
            lines.append(f"## {rpt_name}")
            lines.append("")
            lines.append("| Finding | Severity | Status | Due Date |")
            lines.append("|---------|----------|--------|----------|")
            for f in findings:
                lines.append(f"| {f['finding']} | {f['severity'].upper()} | {f['status'].upper()} | {f['due_date']} |")
            lines.append("")
        lines.append("> Readiness triage is not legal advice and cannot predict an audit outcome.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = RegulatoryReportingAgent()
    for op in ["report_status", "data_validation", "submission_tracker", "audit_readiness"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
