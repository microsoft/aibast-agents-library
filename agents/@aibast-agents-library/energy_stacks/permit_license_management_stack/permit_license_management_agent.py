"""
Permit and License Management Agent for Energy sector.

Tracks permits and licenses across energy facilities, manages renewal
calendars, identifies compliance gaps, and monitors application status
for regulatory requirements.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/permit-license-management",
    "version": "1.1.0",
    "display_name": "Permit Management Agent",
    "description": "Review a synthetic energy permit inventory, renewal calendar, compliance gaps, and application status. Use for permit and license tracking or audit-readiness questions. The agent never submits, renews, amends, or represents approval of a permit; authorized staff must review and use future authenticated filing tools.",
    "author": "AIBAST",
    "tags": ["permits", "licenses", "compliance", "regulatory", "energy", "renewals"],
    "category": "energy",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

PERMITS = {
    "PRM-6001": {
        "name": "Title V Air Operating Permit",
        "facility": "Riverside Generating Station",
        "issuing_authority": "CA Air Resources Board",
        "permit_number": "AOP-CA-2024-1847",
        "issued_date": "2024-06-15",
        "expiration_date": "2029-06-15",
        "status": "active",
        "type": "air_quality",
        "renewal_lead_days": 365,
        "conditions": 24,
        "last_inspection": "2025-09-22",
    },
    "PRM-6002": {
        "name": "NPDES Stormwater Discharge Permit",
        "facility": "Riverside Generating Station",
        "issuing_authority": "CA State Water Board",
        "permit_number": "NPDES-CA-0052841",
        "issued_date": "2023-03-01",
        "expiration_date": "2026-03-01",
        "status": "expired",
        "type": "water_discharge",
        "renewal_lead_days": 180,
        "conditions": 18,
        "last_inspection": "2025-07-14",
    },
    "PRM-6003": {
        "name": "RCRA Hazardous Waste Generator",
        "facility": "Bayshore Refinery",
        "issuing_authority": "EPA Region 6",
        "permit_number": "TXD-0489-2215",
        "issued_date": "2022-01-10",
        "expiration_date": "2027-01-10",
        "status": "active",
        "type": "waste_management",
        "renewal_lead_days": 270,
        "conditions": 32,
        "last_inspection": "2025-11-05",
    },
    "PRM-6004": {
        "name": "Pipeline Operating License",
        "facility": "Northeast Corridor Pipeline",
        "issuing_authority": "PHMSA",
        "permit_number": "PHMSA-NE-7742",
        "issued_date": "2021-08-20",
        "expiration_date": "2026-08-20",
        "status": "active",
        "type": "pipeline_operation",
        "renewal_lead_days": 365,
        "conditions": 28,
        "last_inspection": "2025-10-30",
    },
    "PRM-6005": {
        "name": "Coal Combustion Residuals Permit",
        "facility": "Ridgeline Coal Station",
        "issuing_authority": "CO Dept of Public Health",
        "permit_number": "CCR-CO-2023-0091",
        "issued_date": "2023-04-01",
        "expiration_date": "2026-04-01",
        "status": "active",
        "type": "waste_management",
        "renewal_lead_days": 180,
        "conditions": 21,
        "last_inspection": "2025-08-18",
    },
    "PRM-6006": {
        "name": "Spill Prevention Control Plan",
        "facility": "Bayshore Refinery",
        "issuing_authority": "EPA Region 6",
        "permit_number": "SPCC-TX-2024-3340",
        "issued_date": "2024-02-15",
        "expiration_date": "2029-02-15",
        "status": "active",
        "type": "spill_prevention",
        "renewal_lead_days": 365,
        "conditions": 15,
        "last_inspection": "2025-06-02",
    },
}

APPLICATIONS = {
    "APP-7001": {
        "permit_name": "NPDES Stormwater Discharge Permit Renewal",
        "facility": "Riverside Generating Station",
        "submitted_date": "2025-09-01",
        "authority": "CA State Water Board",
        "status": "under_review",
        "expected_decision": "2026-04-15",
        "comments_received": 3,
    },
    "APP-7002": {
        "permit_name": "New Source Review - Gas Turbine Expansion",
        "facility": "Riverside Generating Station",
        "submitted_date": "2026-01-20",
        "authority": "CA Air Resources Board",
        "status": "public_comment",
        "expected_decision": "2026-06-30",
        "comments_received": 12,
    },
    "APP-7003": {
        "permit_name": "Pipeline Integrity Management Plan Update",
        "facility": "Northeast Corridor Pipeline",
        "submitted_date": "2026-02-10",
        "authority": "PHMSA",
        "status": "submitted",
        "expected_decision": "2026-05-15",
        "comments_received": 0,
    },
}

REGULATORY_REQUIREMENTS = {
    "air_quality": ["Continuous emissions monitoring", "Annual stack testing", "Quarterly compliance reports"],
    "water_discharge": ["Monthly effluent sampling", "Annual DMR submission", "Stormwater pollution prevention plan"],
    "waste_management": ["Biennial hazardous waste report", "Manifest tracking", "Land disposal restrictions compliance"],
    "pipeline_operation": ["Integrity management program", "Operator qualification records", "Emergency response plan"],
    "spill_prevention": ["Annual SPCC plan review", "Integrity testing of containers", "Discharge prevention briefings"],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _selected_permits(facility=None):
    if not facility:
        return PERMITS
    query = facility.casefold()
    return {pid: permit for pid, permit in PERMITS.items() if query in permit["facility"].casefold()}


def _permit_inventory(facility=None):
    inventory = []
    selected = _selected_permits(facility)
    for pid, p in selected.items():
        inventory.append({
            "id": pid, "name": p["name"], "facility": p["facility"],
            "authority": p["issuing_authority"], "permit_number": p["permit_number"],
            "status": p["status"], "type": p["type"],
            "expiration": p["expiration_date"], "conditions": p["conditions"],
        })
    active = sum(1 for p in selected.values() if p["status"] == "active")
    expired = sum(1 for p in selected.values() if p["status"] == "expired")
    return {"permits": inventory, "total": len(inventory), "active": active, "expired": expired}


def _renewal_calendar(facility=None):
    calendar = []
    for pid, p in _selected_permits(facility).items():
        calendar.append({
            "id": pid, "name": p["name"], "facility": p["facility"],
            "expiration": p["expiration_date"], "status": p["status"],
            "renewal_lead_days": p["renewal_lead_days"],
        })
    calendar.sort(key=lambda x: x["expiration"])
    return {"calendar": calendar}


def _compliance_gaps(facility=None):
    gaps = []
    for pid, p in _selected_permits(facility).items():
        if p["status"] == "expired":
            gaps.append({
                "id": pid, "name": p["name"], "facility": p["facility"],
                "gap_type": "expired_permit", "severity": "critical",
                "detail": f"Permit {p['permit_number']} expired on {p['expiration_date']}",
            })
        reqs = REGULATORY_REQUIREMENTS.get(p["type"], [])
        if p["type"] == "water_discharge" and p["status"] == "expired":
            for req in reqs:
                gaps.append({
                    "id": pid, "name": p["name"], "facility": p["facility"],
                    "gap_type": "requirement_at_risk", "severity": "high",
                    "detail": f"Requirement '{req}' at risk due to expired permit",
                })
    return {"gaps": gaps, "total": len(gaps), "critical": sum(1 for g in gaps if g["severity"] == "critical")}


def _application_status(facility=None):
    statuses = []
    query = facility.casefold() if facility else None
    for aid, a in APPLICATIONS.items():
        if query and query not in a["facility"].casefold():
            continue
        statuses.append({
            "id": aid, "name": a["permit_name"], "facility": a["facility"],
            "authority": a["authority"], "submitted": a["submitted_date"],
            "status": a["status"], "expected_decision": a["expected_decision"],
            "comments": a["comments_received"],
        })
    return {"applications": statuses, "total": len(statuses)}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class PermitLicenseManagementAgent(BasicAgent):
    """Permit and license tracking and compliance management agent."""

    def __init__(self):
        self.name = "PermitLicenseManagementAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "permit_inventory",
                            "renewal_calendar",
                            "compliance_gaps",
                            "application_status",
                        ],
                        "description": "Choose permit_inventory for the register, renewal_calendar for deadlines, compliance_gaps for evidence requiring review, or application_status for already-submitted application tracking.",
                    },
                    "facility": {
                        "type": "string",
                        "description": "Optional facility name or substring used to filter the synthetic snapshot.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "permit_inventory")
        facility = kwargs.get("facility")
        if op == "permit_inventory":
            return self._permit_inventory(facility)
        elif op == "renewal_calendar":
            return self._renewal_calendar(facility)
        elif op == "compliance_gaps":
            return self._compliance_gaps(facility)
        elif op == "application_status":
            return self._application_status(facility)
        return f"**Error:** Unknown operation `{op}`."

    def _permit_inventory(self, facility=None) -> str:
        data = _permit_inventory(facility)
        lines = [
            "# Permit & License Inventory",
            "",
            f"**Total Permits:** {data['total']} | **Active:** {data['active']} | **Expired:** {data['expired']}",
            "",
            "| ID | Permit | Facility | Authority | Status | Expiration | Conditions |",
            "|----|--------|----------|-----------|--------|-----------|-----------|",
        ]
        for p in data["permits"]:
            lines.append(
                f"| {p['id']} | {p['name']} | {p['facility']} "
                f"| {p['authority']} | {p['status'].upper()} | {p['expiration']} | {p['conditions']} |"
            )
        lines.append("")
        lines.append("> Synthetic register only. Verify status with the issuing authority before relying on it.")
        return "\n".join(lines)

    def _renewal_calendar(self, facility=None) -> str:
        data = _renewal_calendar(facility)
        lines = [
            "# Permit Renewal Calendar",
            "",
            "| Permit | Facility | Expiration | Status | Lead Time |",
            "|--------|----------|-----------|--------|-----------|",
        ]
        for c in data["calendar"]:
            lines.append(
                f"| {c['name']} | {c['facility']} | {c['expiration']} "
                f"| {c['status'].upper()} | {c['renewal_lead_days']} days |"
            )
        lines.append("")
        lines.append("> Planning reminders only. No renewal, notice, or authority submission has been initiated.")
        return "\n".join(lines)

    def _compliance_gaps(self, facility=None) -> str:
        data = _compliance_gaps(facility)
        if data["total"] == 0:
            return "# Compliance Gaps\n\nNo gaps appear in the selected synthetic records; this is not a legal compliance determination."
        lines = [
            "# Compliance Gap Analysis",
            "",
            f"**Total Gaps:** {data['total']} | **Critical:** {data['critical']}",
            "",
            "| Permit | Facility | Gap Type | Severity | Detail |",
            "|--------|----------|----------|----------|--------|",
        ]
        for g in data["gaps"]:
            lines.append(
                f"| {g['name']} | {g['facility']} | {g['gap_type']} "
                f"| {g['severity'].upper()} | {g['detail']} |"
            )
        lines.append("")
        lines.append("> Triage evidence only, not legal advice. Authorized permit staff must validate obligations and approve remediation.")
        return "\n".join(lines)

    def _application_status(self, facility=None) -> str:
        data = _application_status(facility)
        lines = [
            "# Permit Application Status",
            "",
            f"**Active Applications:** {data['total']}",
            "",
            "| ID | Application | Facility | Authority | Submitted | Status | Decision Date | Comments |",
            "|----|-------------|----------|-----------|-----------|--------|--------------|----------|",
        ]
        for a in data["applications"]:
            lines.append(
                f"| {a['id']} | {a['name']} | {a['facility']} "
                f"| {a['authority']} | {a['submitted']} | {a['status']} "
                f"| {a['expected_decision']} | {a['comments']} |"
            )
        lines.append("")
        lines.append("> Read-only synthetic tracking. The agent cannot submit, amend, withdraw, or approve an application.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = PermitLicenseManagementAgent()
    for op in ["permit_inventory", "renewal_calendar", "compliance_gaps", "application_status"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
