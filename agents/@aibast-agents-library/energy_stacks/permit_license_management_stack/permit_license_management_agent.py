"""
Permit and License Management Agent for Energy sector.

Tracks permits and licenses across a renewables portfolio, computes days
left against a fixed snapshot date, flags critical renewals, prepares the
emergency renewal package, identifies compliance gaps, and monitors
application status for regulatory requirements.
"""

import sys
import os
import datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/permit-license-management",
    "version": "1.2.0",
    "display_name": "Permit Management Agent",
    "description": "Review a synthetic renewables permit portfolio: status, permits expiring soon, renewal calendar, the emergency renewal package, compliance gaps, and application status. Use for permit and license tracking or audit-readiness questions. The agent never submits, renews, amends, or represents approval of a permit, and never sends notices; authorized staff must review and use future authenticated filing tools.",
    "author": "AIBAST",
    "tags": ["permits", "licenses", "compliance", "regulatory", "energy", "renewals"],
    "category": "energy",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data (the demo default: a renewables permit portfolio)
# ---------------------------------------------------------------------------

AS_OF = "2026-03-02"  # fixed snapshot date; days left are computed from it, never from the clock

PORTFOLIO = {
    "active_permits": 240,
    "expiring_120_days": 63,
    "critical_days": 30,
    "renewal_investment_63": 2340000,
    "production_at_risk_63": 47000000,
}

# The critical permits (< 30 days left) in the snapshot. Renewal costs total $685,000; production $13.8M.
PERMITS = {
    "PRM-8101": {"facility": "Imperial Valley Solar", "type": "Air Quality", "authority": "County air pollution control district",
                 "expiration_date": "2026-03-20", "renewal_lead_days": 90, "renewal_cost": 185000,
                 "production_at_risk": 4200000,
                 "renewal_path": "Expedited air quality renewal application prepared, ready for you to submit"},
    "PRM-8102": {"facility": "Reno Wind Farm", "type": "Environmental", "authority": "State environmental protection division",
                 "expiration_date": "2026-03-24", "renewal_lead_days": 120, "renewal_cost": 140000,
                 "production_at_risk": 3100000,
                 "renewal_path": "Environmental permit vendor shortlisted (2-week turnaround); engagement request drafted"},
    "PRM-8103": {"facility": "Phoenix Solar", "type": "Water Use", "authority": "County water resources department",
                 "expiration_date": "2026-03-28", "renewal_lead_days": 60, "renewal_cost": 95000,
                 "production_at_risk": 2200000,
                 "renewal_path": "County approval fast-track request drafted"},
    "PRM-8104": {"facility": "Bakersfield Solar", "type": "Hazmat", "authority": "County environmental health department",
                 "expiration_date": "2026-03-30", "renewal_lead_days": 60, "renewal_cost": 80000,
                 "production_at_risk": 1600000,
                 "renewal_path": "Hazmat documentation compiled, ready to submit"},
    "PRM-8105": {"facility": "Tehachapi Wind", "type": "Avian Protection", "authority": "Federal wildlife agency",
                 "expiration_date": "2026-03-31", "renewal_lead_days": 90, "renewal_cost": 60000,
                 "production_at_risk": 1100000,
                 "renewal_path": "Monitoring report assembled for the renewal filing"},
    "PRM-8106": {"facility": "Palm Springs Wind", "type": "Noise Variance", "authority": "County planning department",
                 "expiration_date": "2026-03-31", "renewal_lead_days": 45, "renewal_cost": 45000,
                 "production_at_risk": 700000,
                 "renewal_path": "Variance renewal letter drafted"},
    "PRM-8107": {"facility": "Yuma Solar", "type": "Grading", "authority": "County building and grading office",
                 "expiration_date": "2026-03-31", "renewal_lead_days": 45, "renewal_cost": 40000,
                 "production_at_risk": 500000,
                 "renewal_path": "Grading plan resubmittal package prepared"},
    "PRM-8108": {"facility": "Mojave Storage", "type": "Fire Code", "authority": "County fire authority",
                 "expiration_date": "2026-03-31", "renewal_lead_days": 45, "renewal_cost": 40000,
                 "production_at_risk": 400000,
                 "renewal_path": "Fire code inspection request drafted"},
}

STAKEHOLDERS = ["Facility managers", "Legal"]

APPLICATIONS = {
    "APP-7101": {
        "permit_name": "Reno Wind Farm Repowering Environmental Review",
        "facility": "Reno Wind Farm",
        "submitted_date": "2025-11-12",
        "authority": "State environmental protection division",
        "status": "under_review",
        "expected_decision": "2026-05-15",
        "comments_received": 4,
    },
    "APP-7102": {
        "permit_name": "Imperial Valley Solar Phase 2 Conditional Use Permit",
        "facility": "Imperial Valley Solar",
        "submitted_date": "2026-01-20",
        "authority": "County planning commission",
        "status": "public_comment",
        "expected_decision": "2026-06-30",
        "comments_received": 12,
    },
    "APP-7103": {
        "permit_name": "Phoenix Solar Battery Storage Building Permit",
        "facility": "Phoenix Solar",
        "submitted_date": "2026-02-10",
        "authority": "County water resources department",
        "status": "submitted",
        "expected_decision": "2026-04-15",
        "comments_received": 0,
    },
}

REGULATORY_REQUIREMENTS = {
    "Air Quality": ["Dust control plan", "Annual emissions inventory", "Quarterly compliance reports"],
    "Environmental": ["Habitat monitoring", "Annual environmental report", "Mitigation plan updates"],
    "Water Use": ["Monthly water use reporting", "Annual allocation review", "Conservation plan"],
    "Hazmat": ["Hazardous materials business plan", "Annual inventory certification", "Emergency response plan"],
    "Avian Protection": ["Post-construction fatality monitoring", "Annual avian report", "Adaptive management plan"],
    "Noise Variance": ["Quarterly noise monitoring", "Community complaint log"],
    "Grading": ["Erosion control inspection", "Grading completion certification"],
    "Fire Code": ["Annual fire inspection", "Battery hazard mitigation analysis"],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _days_left(expiration):
    as_of = datetime.date.fromisoformat(AS_OF)
    return (datetime.date.fromisoformat(expiration) - as_of).days


def _selected_permits(facility=None):
    if not facility:
        return PERMITS
    query = facility.casefold()
    return {pid: permit for pid, permit in PERMITS.items() if query in permit["facility"].casefold()}


def _by_days(selected):
    return sorted(selected.items(), key=lambda x: _days_left(x[1]["expiration_date"]))


def _m(value):
    return f"${value / 1_000_000:.1f}M"


def _risk(days):
    if days < PORTFOLIO["critical_days"]:
        return "CRITICAL"
    return "AT RISK"


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class PermitLicenseManagementAgent(BasicAgent):
    """Permit and license tracking and compliance management agent."""

    def __init__(self):
        self.name = "PermitLicenseManagementAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"] + " Always call it first: 'show me our permit status and any "
                "expiring soon' uses permit_inventory; 'start emergency renewals for the critical permits' "
                "uses renewal_plan (a prepared package; nothing is submitted or sent)."
            ),
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
                            "renewal_plan",
                        ],
                        "description": (
                            "permit_inventory: the default; permit status, permits expiring soon and the critical "
                            "permits (<30 days). renewal_calendar: renewal deadlines with days left and lead times. "
                            "compliance_gaps: evidence requiring review, such as missed renewal lead times. "
                            "application_status: already-submitted application tracking. renewal_plan: start or "
                            "prepare emergency renewals for the critical permits (per-permit prepared action, "
                            "investment, production protected, draft stakeholder alerts)."
                        ),
                    },
                    "facility": {
                        "type": "string",
                        "description": "Optional facility name or substring used to filter the synthetic snapshot, e.g. 'Reno'.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation") or "permit_inventory"
        facility = kwargs.get("facility")
        if op == "permit_inventory":
            return self._permit_inventory(facility)
        elif op == "renewal_calendar":
            return self._renewal_calendar(facility)
        elif op == "compliance_gaps":
            return self._compliance_gaps(facility)
        elif op == "application_status":
            return self._application_status(facility)
        elif op == "renewal_plan":
            return self._renewal_plan(facility)
        return f"**Error:** Unknown operation `{op}`."

    def _permit_inventory(self, facility=None) -> str:
        p = PORTFOLIO
        selected = _selected_permits(facility)
        critical = [(pid, x) for pid, x in _by_days(selected) if _days_left(x["expiration_date"]) < p["critical_days"]]
        lines = [
            "# Permit & License Inventory",
            "",
            f"I've analyzed all {p['active_permits']} active permits across your facilities. You have "
            f"{p['expiring_120_days']} permits expiring in the next 120 days, including {len(PERMITS)} critical ones "
            "needing immediate attention.",
            "",
            f"## Critical Permits (<{p['critical_days']} Days) as of {AS_OF}",
            "",
            "| ID | Facility | Permit Type | Days Left | Risk |",
            "|----|----------|-------------|-----------|------|",
        ]
        for pid, x in critical:
            d = _days_left(x["expiration_date"])
            lines.append(f"| {pid} | {x['facility']} | {x['type']} | {d} | {_risk(d)} |")
        if not critical:
            lines.append("| - | No matching synthetic permit was found. | - | - | - |")
        lines.append("")
        lines.append(f"**Total Renewal Investment:** ${p['renewal_investment_63'] / 1_000_000:.2f}M across {p['expiring_120_days']} permits")
        lines.append(f"**Production at Risk:** ${p['production_at_risk_63'] // 1_000_000}M if permits lapse")
        lines.append("")
        lines.append("Source: [Synthetic D365 + SharePoint permit register]")
        lines.append("")
        lines.append("**Next step:** Should I prepare the emergency renewal package for the critical permits?")
        lines.append("")
        lines.append("> Synthetic register only. Verify status with the issuing authority before relying on it.")
        return "\n".join(lines)

    def _renewal_calendar(self, facility=None) -> str:
        lines = [
            "# Permit Renewal Calendar",
            "",
            f"Days left are computed from the snapshot date {AS_OF}.",
            "",
            "| Permit | Facility | Expiration | Days Left | Lead Time | Lead Time Status |",
            "|--------|----------|-----------|-----------|-----------|------------------|",
        ]
        for pid, x in _by_days(_selected_permits(facility)):
            d = _days_left(x["expiration_date"])
            status = "MISSED" if d < x["renewal_lead_days"] else "On track"
            lines.append(
                f"| {pid} {x['type']} | {x['facility']} | {x['expiration_date']} | {d} "
                f"| {x['renewal_lead_days']} days | {status} |"
            )
        lines.append("")
        lines.append("> Planning reminders only. No renewal, notice, or authority submission has been initiated.")
        return "\n".join(lines)

    def _compliance_gaps(self, facility=None) -> str:
        gaps = []
        for pid, x in _by_days(_selected_permits(facility)):
            d = _days_left(x["expiration_date"])
            if d < x["renewal_lead_days"]:
                gaps.append((pid, x, "renewal_lead_time_missed", "CRITICAL" if d < PORTFOLIO["critical_days"] else "HIGH",
                             f"{d} days left vs {x['renewal_lead_days']}-day lead time; at risk: "
                             + ", ".join(REGULATORY_REQUIREMENTS.get(x["type"], []))))
        if not gaps:
            return "# Compliance Gaps\n\nNo gaps appear in the selected synthetic records; this is not a legal compliance determination."
        lines = [
            "# Compliance Gap Analysis",
            "",
            f"**Total Gaps:** {len(gaps)} | **Critical:** {sum(1 for g in gaps if g[3] == 'CRITICAL')}",
            "",
            "| Permit | Facility | Gap Type | Severity | Detail |",
            "|--------|----------|----------|----------|--------|",
        ]
        for pid, x, gap, sev, detail in gaps:
            lines.append(f"| {pid} {x['type']} | {x['facility']} | {gap} | {sev} | {detail} |")
        lines.append("")
        lines.append("> Triage evidence only, not legal advice. Authorized permit staff must validate obligations and approve remediation.")
        return "\n".join(lines)

    def _application_status(self, facility=None) -> str:
        query = facility.casefold() if facility else None
        rows = [(aid, a) for aid, a in APPLICATIONS.items() if not query or query in a["facility"].casefold()]
        lines = [
            "# Permit Application Status",
            "",
            f"**Active Applications:** {len(rows)}",
            "",
            "| ID | Application | Facility | Authority | Submitted | Status | Decision Date | Comments |",
            "|----|-------------|----------|-----------|-----------|--------|--------------|----------|",
        ]
        for aid, a in rows:
            lines.append(
                f"| {aid} | {a['permit_name']} | {a['facility']} | {a['authority']} | {a['submitted_date']} "
                f"| {a['status']} | {a['expected_decision']} | {a['comments_received']} |"
            )
        lines.append("")
        lines.append("> Read-only synthetic tracking. The agent cannot submit, amend, withdraw, or approve an application.")
        return "\n".join(lines)

    def _renewal_plan(self, facility=None) -> str:
        selected = _selected_permits(facility)
        critical = [(pid, x) for pid, x in _by_days(selected) if _days_left(x["expiration_date"]) < PORTFOLIO["critical_days"]]
        invest = sum(x["renewal_cost"] for _, x in critical)
        protected = sum(x["production_at_risk"] for _, x in critical)
        lines = [
            f"Emergency renewal package prepared for all {len(critical)} critical permits, ready for your approval. "
            "Expedited processing requests and stakeholder alerts are drafted, not sent.",
            "",
            "# Emergency Renewal Plan",
            "",
            "| ID | Facility | Permit Type | Days Left | Prepared Action | Renewal Cost |",
            "|----|----------|-------------|-----------|-----------------|--------------|",
        ]
        for pid, x in critical:
            lines.append(
                f"| {pid} | {x['facility']} | {x['type']} | {_days_left(x['expiration_date'])} "
                f"| {x['renewal_path']} | ${x['renewal_cost']:,} |"
            )
        lines += [
            "",
            f"**Investment Required:** ${invest:,} for critical renewals",
            f"**Production Protected:** {_m(protected)} (combined facility capacity)",
            f"**Stakeholder Alerts (drafts for Teams and Outlook):** {', '.join(STAKEHOLDERS)}",
            "",
            "Draft alert: \"Critical permit renewals: " + str(len(critical)) + " permits expire within "
            + str(PORTFOLIO["critical_days"]) + " days. The renewal package is ready for approval; please confirm "
            "owners today.\"",
            "",
            "**Monitoring:** daily status review with executive escalation if a renewal slips (recommended cadence).",
            "",
            "Source: [Synthetic D365 vendor management + SharePoint]",
            "",
            "**Next step:** Would you like me to analyze the Reno Wind Farm permit to see what's needed?",
            "",
            "> Prepared for approval only. No application was submitted, no vendor was engaged, and no Teams or "
            "Outlook message was sent.",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = PermitLicenseManagementAgent()
    for op in ["permit_inventory", "renewal_plan", "renewal_calendar", "compliance_gaps", "application_status"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
