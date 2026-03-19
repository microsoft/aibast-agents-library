"""
Workforce Clearance & Onboarding Agent — Federal Government Stack

Manages security clearance tracking, onboarding checklists, background
check status, and access provisioning for federal workforce management.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/workforce-clearance-onboarding",
    "version": "1.0.0",
    "display_name": "Workforce Clearance & Onboarding Agent",
    "description": "Federal workforce clearance tracking, onboarding checklists, background check monitoring, and access provisioning.",
    "author": "AIBAST",
    "tags": ["clearance", "onboarding", "background-check", "workforce", "federal", "access"],
    "category": "federal_government",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

EMPLOYEES = {
    "EMP-5001": {
        "name": "Sarah Mitchell",
        "position": "Cybersecurity Analyst (GS-13)",
        "office": "Office of the CISO",
        "hire_date": "2025-03-01",
        "clearance_level": "Top Secret/SCI",
        "clearance_status": "pending_adjudication",
        "investigation_type": "T5",
        "investigation_opened": "2024-11-15",
        "interim_clearance": True,
        "eod_date": "2025-03-15",
    },
    "EMP-5002": {
        "name": "James Thornton",
        "position": "Program Analyst (GS-12)",
        "office": "Office of Acquisition Management",
        "hire_date": "2025-02-01",
        "clearance_level": "Secret",
        "clearance_status": "active",
        "investigation_type": "T3",
        "investigation_opened": "2024-09-01",
        "interim_clearance": False,
        "eod_date": "2025-02-10",
    },
    "EMP-5003": {
        "name": "Priya Desai",
        "position": "Data Scientist (GS-14)",
        "office": "Office of Data Analytics",
        "hire_date": "2025-04-01",
        "clearance_level": "Top Secret",
        "clearance_status": "investigation_in_progress",
        "investigation_type": "T5",
        "investigation_opened": "2025-01-10",
        "interim_clearance": False,
        "eod_date": None,
    },
    "EMP-5004": {
        "name": "Robert Chen",
        "position": "IT Specialist (GS-11)",
        "office": "Office of Information Technology",
        "hire_date": "2025-01-15",
        "clearance_level": "Public Trust (MBI)",
        "clearance_status": "active",
        "investigation_type": "T2",
        "investigation_opened": "2024-10-01",
        "interim_clearance": False,
        "eod_date": "2025-01-20",
    },
}

ONBOARDING_STEPS = {
    "pre_arrival": [
        {"step": "Tentative offer accepted", "required": True, "days_before_eod": 30},
        {"step": "SF-86 submitted to DCSA", "required": True, "days_before_eod": 28},
        {"step": "Drug test completed", "required": True, "days_before_eod": 21},
        {"step": "Official offer letter issued", "required": True, "days_before_eod": 14},
        {"step": "PIV card pre-enrollment", "required": True, "days_before_eod": 7},
    ],
    "day_one": [
        {"step": "Oath of office administered", "required": True},
        {"step": "PIV card issued and activated", "required": True},
        {"step": "Building access badge provisioned", "required": True},
        {"step": "IT equipment issued (laptop, phone)", "required": True},
        {"step": "Orientation briefing attended", "required": True},
    ],
    "first_week": [
        {"step": "Network account activated", "required": True},
        {"step": "Email and collaboration tools provisioned", "required": True},
        {"step": "Mandatory cyber awareness training", "required": True},
        {"step": "Records management training", "required": True},
        {"step": "Meet with supervisor — IDP discussion", "required": True},
    ],
    "first_30_days": [
        {"step": "Complete all required TMS training modules", "required": True},
        {"step": "Ethics briefing and financial disclosure (if applicable)", "required": False},
        {"step": "Telework agreement signed", "required": False},
        {"step": "Benefits enrollment confirmed", "required": True},
        {"step": "Performance plan established", "required": True},
    ],
}

INVESTIGATION_TIMELINES = {
    "T1": {"name": "Tier 1 (Low Risk)", "avg_days": 30, "target_days": 40},
    "T2": {"name": "Tier 2 (Moderate Risk / Public Trust)", "avg_days": 60, "target_days": 80},
    "T3": {"name": "Tier 3 (Secret)", "avg_days": 90, "target_days": 120},
    "T4": {"name": "Tier 4 (High Risk Public Trust)", "avg_days": 120, "target_days": 150},
    "T5": {"name": "Tier 5 (Top Secret / SCI)", "avg_days": 180, "target_days": 240},
}

ACCESS_REQUIREMENTS = {
    "Top Secret/SCI": {
        "network_access": ["JWICS", "SIPRNet", "NIPRNet"],
        "physical_access": ["SCIF", "Classified Workspace", "General Building"],
        "systems": ["XKEYSCORE-SIM", "SIGINT-Portal", "IC-Cloud"],
        "additional": ["SCI indoctrination briefing", "Polygraph (if CI)"],
    },
    "Top Secret": {
        "network_access": ["SIPRNet", "NIPRNet"],
        "physical_access": ["Classified Workspace", "General Building"],
        "systems": ["SIPR-Email", "Classified-SharePoint"],
        "additional": ["TS indoctrination briefing"],
    },
    "Secret": {
        "network_access": ["SIPRNet", "NIPRNet"],
        "physical_access": ["General Building"],
        "systems": ["SIPR-Email"],
        "additional": [],
    },
    "Public Trust (MBI)": {
        "network_access": ["NIPRNet"],
        "physical_access": ["General Building"],
        "systems": ["Agency-Email", "Agency-VPN", "SharePoint"],
        "additional": [],
    },
}

ONBOARDING_STATUS = {
    "EMP-5001": {"pre_arrival": "complete", "day_one": "complete", "first_week": "in_progress", "first_30_days": "pending"},
    "EMP-5002": {"pre_arrival": "complete", "day_one": "complete", "first_week": "complete", "first_30_days": "complete"},
    "EMP-5003": {"pre_arrival": "in_progress", "day_one": "pending", "first_week": "pending", "first_30_days": "pending"},
    "EMP-5004": {"pre_arrival": "complete", "day_one": "complete", "first_week": "complete", "first_30_days": "in_progress"},
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _clearance_days_elapsed(emp):
    """Calculate approximate days since investigation opened."""
    parts = emp["investigation_opened"].split("-")
    opened_ordinal = int(parts[0]) * 365 + int(parts[1]) * 30 + int(parts[2])
    current_ordinal = 2025 * 365 + 3 * 30 + 15
    return max(0, current_ordinal - opened_ordinal)


def _onboarding_pct(emp_id):
    """Calculate onboarding completion percentage."""
    status = ONBOARDING_STATUS.get(emp_id, {})
    phases = ["pre_arrival", "day_one", "first_week", "first_30_days"]
    complete = sum(1 for p in phases if status.get(p) == "complete")
    return round((complete / len(phases)) * 100, 0)


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class WorkforceClearanceOnboardingAgent(BasicAgent):
    """Federal workforce clearance and onboarding management agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/workforce-clearance-onboarding"
        self.metadata = {
            "name": self.name,
            "display_name": "Workforce Clearance & Onboarding Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "clearance_status",
                            "onboarding_checklist",
                            "background_check_tracker",
                            "access_provisioning",
                        ],
                    },
                    "employee_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "clearance_status")
        dispatch = {
            "clearance_status": self._clearance_status,
            "onboarding_checklist": self._onboarding_checklist,
            "background_check_tracker": self._background_check_tracker,
            "access_provisioning": self._access_provisioning,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _clearance_status(self, **kwargs) -> str:
        lines = ["# Security Clearance Status\n"]
        lines.append("| Employee | Position | Clearance | Status | Investigation | Interim |")
        lines.append("|---|---|---|---|---|---|")
        for eid, emp in EMPLOYEES.items():
            interim = "Yes" if emp["interim_clearance"] else "No"
            status = emp["clearance_status"].replace("_", " ").title()
            lines.append(
                f"| {emp['name']} ({eid}) | {emp['position']} | {emp['clearance_level']} "
                f"| {status} | {emp['investigation_type']} | {interim} |"
            )
        pending = sum(1 for e in EMPLOYEES.values() if e["clearance_status"] != "active")
        lines.append(f"\n**Pending Clearances:** {pending}/{len(EMPLOYEES)}")
        active = sum(1 for e in EMPLOYEES.values() if e["clearance_status"] == "active")
        lines.append(f"**Active Clearances:** {active}/{len(EMPLOYEES)}")
        return "\n".join(lines)

    def _onboarding_checklist(self, **kwargs) -> str:
        employee_id = kwargs.get("employee_id")
        if employee_id and employee_id in EMPLOYEES:
            emp = EMPLOYEES[employee_id]
            status = ONBOARDING_STATUS.get(employee_id, {})
            pct = _onboarding_pct(employee_id)
            lines = [f"# Onboarding Checklist: {emp['name']}\n"]
            lines.append(f"- **Position:** {emp['position']}")
            lines.append(f"- **Office:** {emp['office']}")
            lines.append(f"- **EOD Date:** {emp['eod_date'] or 'TBD'}")
            lines.append(f"- **Completion:** {pct}%\n")
            for phase, steps in ONBOARDING_STEPS.items():
                phase_status = status.get(phase, "pending")
                lines.append(f"## {phase.replace('_', ' ').title()} — {phase_status.replace('_', ' ').title()}\n")
                for s in steps:
                    check = "x" if phase_status == "complete" else " "
                    req = " (required)" if s["required"] else ""
                    lines.append(f"- [{check}] {s['step']}{req}")
                lines.append("")
            return "\n".join(lines)

        lines = ["# Onboarding Status Summary\n"]
        lines.append("| Employee | Position | EOD | Completion |")
        lines.append("|---|---|---|---|")
        for eid, emp in EMPLOYEES.items():
            pct = _onboarding_pct(eid)
            lines.append(f"| {emp['name']} ({eid}) | {emp['position']} | {emp['eod_date'] or 'TBD'} | {pct}% |")
        return "\n".join(lines)

    def _background_check_tracker(self, **kwargs) -> str:
        lines = ["# Background Check Tracker\n"]
        lines.append("## Investigation Timeline Reference\n")
        lines.append("| Tier | Name | Avg Days | Target Days |")
        lines.append("|---|---|---|---|")
        for tid, t in INVESTIGATION_TIMELINES.items():
            lines.append(f"| {tid} | {t['name']} | {t['avg_days']} | {t['target_days']} |")
        lines.append("\n## Active Investigations\n")
        lines.append("| Employee | Type | Opened | Days Elapsed | Target | Status |")
        lines.append("|---|---|---|---|---|---|")
        for eid, emp in EMPLOYEES.items():
            days = _clearance_days_elapsed(emp)
            inv = INVESTIGATION_TIMELINES.get(emp["investigation_type"], {})
            target = inv.get("target_days", 0)
            overdue = " (OVERDUE)" if days > target and emp["clearance_status"] != "active" else ""
            lines.append(
                f"| {emp['name']} | {emp['investigation_type']} | {emp['investigation_opened']} "
                f"| {days} | {target} | {emp['clearance_status'].replace('_', ' ').title()}{overdue} |"
            )
        return "\n".join(lines)

    def _access_provisioning(self, **kwargs) -> str:
        employee_id = kwargs.get("employee_id")
        if employee_id and employee_id in EMPLOYEES:
            emp = EMPLOYEES[employee_id]
            access = ACCESS_REQUIREMENTS.get(emp["clearance_level"], {})
            lines = [f"# Access Provisioning: {emp['name']}\n"]
            lines.append(f"- **Clearance Level:** {emp['clearance_level']}")
            lines.append(f"- **Status:** {emp['clearance_status'].replace('_', ' ').title()}\n")
            lines.append("## Network Access\n")
            for net in access.get("network_access", []):
                lines.append(f"- [ ] {net}")
            lines.append("\n## Physical Access\n")
            for phys in access.get("physical_access", []):
                lines.append(f"- [ ] {phys}")
            lines.append("\n## System Access\n")
            for sys_name in access.get("systems", []):
                lines.append(f"- [ ] {sys_name}")
            if access.get("additional"):
                lines.append("\n## Additional Requirements\n")
                for add in access["additional"]:
                    lines.append(f"- [ ] {add}")
            return "\n".join(lines)

        lines = ["# Access Provisioning Summary\n"]
        lines.append("| Clearance Level | Networks | Physical | Systems |")
        lines.append("|---|---|---|---|")
        for level, access in ACCESS_REQUIREMENTS.items():
            lines.append(
                f"| {level} | {', '.join(access['network_access'])} "
                f"| {', '.join(access['physical_access'])} | {', '.join(access['systems'])} |"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = WorkforceClearanceOnboardingAgent()
    print(agent.perform(operation="clearance_status"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="onboarding_checklist"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="onboarding_checklist", employee_id="EMP-5001"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="background_check_tracker"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="access_provisioning", employee_id="EMP-5001"))
