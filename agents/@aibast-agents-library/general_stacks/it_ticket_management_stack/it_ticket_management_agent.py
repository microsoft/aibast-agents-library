"""
IT Ticket Management Agent

Intelligent IT ticket management with dashboard views, priority assignment,
SLA tracking, and resolution reporting.

Where a real deployment would connect to ServiceNow or Jira Service Management,
this agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/it-ticket-management",
    "version": "1.0.0",
    "display_name": "IT Ticket Management",
    "description": "IT ticket management with dashboards, priority assignment, SLA tracking, and resolution reporting.",
    "author": "AIBAST",
    "tags": ["it", "tickets", "helpdesk", "sla", "priority", "resolution"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_TICKETS = {
    "TKT-8001": {"id": "TKT-8001", "subject": "Email server degradation - 847 users affected", "category": "Infrastructure", "severity": "P1-Critical", "status": "In Progress", "assignee": "Sarah Chen", "team": "Network Team", "created": "2025-11-14T08:15:00Z", "sla_target_hours": 1, "elapsed_hours": 0.5, "users_affected": 847, "description": "Exchange server memory at 98%, automatic restart needed"},
    "TKT-8002": {"id": "TKT-8002", "subject": "VPN connectivity failure for Finance dept", "category": "Network", "severity": "P1-Critical", "status": "In Progress", "assignee": "Mike Torres", "team": "Network Team", "created": "2025-11-14T08:30:00Z", "sla_target_hours": 1, "elapsed_hours": 0.25, "users_affected": 234, "description": "VPN profile corruption affecting Finance department users"},
    "TKT-8003": {"id": "TKT-8003", "subject": "CRM system timeout errors", "category": "Application", "severity": "P2-High", "status": "Assigned", "assignee": "James Martinez", "team": "Application Support", "created": "2025-11-14T09:00:00Z", "sla_target_hours": 4, "elapsed_hours": 0.1, "users_affected": 156, "description": "Dynamics 365 experiencing intermittent timeout errors"},
    "TKT-8004": {"id": "TKT-8004", "subject": "Password reset - batch of 12 new hires", "category": "Access Management", "severity": "P3-Medium", "status": "Open", "assignee": "Lisa Wong", "team": "Desktop Support", "created": "2025-11-14T09:15:00Z", "sla_target_hours": 8, "elapsed_hours": 0, "users_affected": 12, "description": "New hire onboarding batch needs initial password setup"},
    "TKT-8005": {"id": "TKT-8005", "subject": "Printer not working on 3rd floor", "category": "Hardware", "severity": "P3-Medium", "status": "Open", "assignee": "unassigned", "team": "Desktop Support", "created": "2025-11-14T09:30:00Z", "sla_target_hours": 8, "elapsed_hours": 0, "users_affected": 35, "description": "HP LaserJet on 3rd floor showing offline, paper jam cleared"},
    "TKT-8006": {"id": "TKT-8006", "subject": "Request for dual monitor setup", "category": "Hardware", "severity": "P4-Low", "status": "Open", "assignee": "unassigned", "team": "Desktop Support", "created": "2025-11-13T16:00:00Z", "sla_target_hours": 24, "elapsed_hours": 17, "users_affected": 1, "description": "Employee requesting second monitor for productivity"},
    "TKT-8007": {"id": "TKT-8007", "subject": "Software license request - Adobe Creative Suite", "category": "Software", "severity": "P4-Low", "status": "Pending Approval", "assignee": "Lisa Wong", "team": "Desktop Support", "created": "2025-11-13T14:00:00Z", "sla_target_hours": 24, "elapsed_hours": 19, "users_affected": 1, "description": "Marketing team member needs Adobe CC license"},
    "TKT-8008": {"id": "TKT-8008", "subject": "Conference room AV system not projecting", "category": "Hardware", "severity": "P2-High", "status": "In Progress", "assignee": "Mike Chen", "team": "Desktop Support", "created": "2025-11-14T08:45:00Z", "sla_target_hours": 4, "elapsed_hours": 0.3, "users_affected": 20, "description": "Board room projector showing no signal, executive meeting at 10 AM"},
}

_SLA_TARGETS = {
    "P1-Critical": {"response_hours": 0.25, "resolution_hours": 1, "escalation_after_hours": 0.5, "penalty_per_breach": 500},
    "P2-High": {"response_hours": 0.5, "resolution_hours": 4, "escalation_after_hours": 2, "penalty_per_breach": 200},
    "P3-Medium": {"response_hours": 2, "resolution_hours": 8, "escalation_after_hours": 6, "penalty_per_breach": 50},
    "P4-Low": {"response_hours": 4, "resolution_hours": 24, "escalation_after_hours": 20, "penalty_per_breach": 0},
}

_TEAM_CAPACITY = {
    "Network Team": {"members": 3, "current_tickets": 4, "capacity_pct": 72, "skills": ["Infrastructure", "Network", "Security"]},
    "Application Support": {"members": 4, "current_tickets": 6, "capacity_pct": 65, "skills": ["CRM", "ERP", "Custom Apps"]},
    "Desktop Support": {"members": 5, "current_tickets": 18, "capacity_pct": 88, "skills": ["Hardware", "Software", "Access Management"]},
    "Database Team": {"members": 2, "current_tickets": 2, "capacity_pct": 30, "skills": ["SQL Server", "Azure SQL", "Performance"]},
}

_RESOLUTION_HISTORY = {
    "this_week": {"resolved": 89, "avg_resolution_hours": 4.2, "sla_met_pct": 94.2, "first_call_resolution_pct": 67, "csat": 4.5},
    "last_week": {"resolved": 94, "avg_resolution_hours": 4.5, "sla_met_pct": 91.8, "first_call_resolution_pct": 62, "csat": 4.3},
    "this_month": {"resolved": 312, "avg_resolution_hours": 4.3, "sla_met_pct": 93.1, "first_call_resolution_pct": 65, "csat": 4.4},
    "top_categories": [
        {"category": "Password Resets", "count": 58, "pct": 18.6, "automation_candidate": True},
        {"category": "Software Access", "count": 47, "pct": 15.1, "automation_candidate": True},
        {"category": "VPN Issues", "count": 38, "pct": 12.2, "automation_candidate": False},
        {"category": "Hardware Requests", "count": 35, "pct": 11.2, "automation_candidate": False},
        {"category": "Email Issues", "count": 29, "pct": 9.3, "automation_candidate": False},
    ],
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _tickets_by_severity():
    by_sev = {}
    for t in _TICKETS.values():
        by_sev.setdefault(t["severity"], []).append(t)
    return by_sev


def _sla_at_risk():
    at_risk = []
    for t in _TICKETS.values():
        if t["status"] in ("Open", "In Progress", "Assigned"):
            sla = _SLA_TARGETS.get(t["severity"], {})
            remaining = sla.get("resolution_hours", 24) - t["elapsed_hours"]
            if remaining < sla.get("resolution_hours", 24) * 0.3:
                at_risk.append({**t, "remaining_hours": remaining})
    return sorted(at_risk, key=lambda x: x["remaining_hours"])


def _team_workload_summary():
    total_tickets = sum(tc["current_tickets"] for tc in _TEAM_CAPACITY.values())
    total_members = sum(tc["members"] for tc in _TEAM_CAPACITY.values())
    return total_tickets, total_members


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class ITTicketManagementAgent(BasicAgent):
    """
    IT ticket management agent.

    Operations:
        ticket_dashboard    - overview of all open tickets and queue status
        priority_assignment - assign priority and route tickets
        sla_tracking        - track SLA compliance and at-risk tickets
        resolution_report   - generate resolution metrics and trends
    """

    def __init__(self):
        self.name = "ITTicketManagementAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "ticket_dashboard", "priority_assignment",
                            "sla_tracking", "resolution_report",
                        ],
                        "description": "The ticket management operation to perform",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "ticket_dashboard")
        dispatch = {
            "ticket_dashboard": self._ticket_dashboard,
            "priority_assignment": self._priority_assignment,
            "sla_tracking": self._sla_tracking,
            "resolution_report": self._resolution_report,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler()

    # ── ticket_dashboard ───────────────────────────────────────
    def _ticket_dashboard(self):
        by_sev = _tickets_by_severity()
        sev_rows = ""
        for sev in ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]:
            tickets = by_sev.get(sev, [])
            sev_rows += f"| {sev} | {len(tickets)} | {_SLA_TARGETS[sev]['resolution_hours']}h |\n"
        ticket_rows = ""
        for t in sorted(_TICKETS.values(), key=lambda x: x["severity"]):
            ticket_rows += f"| {t['id']} | {t['subject'][:45]} | {t['severity']} | {t['status']} | {t['assignee']} |\n"
        total_tickets, total_members = _team_workload_summary()
        return (
            f"**IT Ticket Dashboard**\n\n"
            f"**Summary:** {len(_TICKETS)} open tickets | {total_members} team members\n\n"
            f"**By Severity:**\n\n"
            f"| Severity | Count | SLA Target |\n|---|---|---|\n"
            f"{sev_rows}\n"
            f"**All Tickets:**\n\n"
            f"| ID | Subject | Severity | Status | Assignee |\n|---|---|---|---|---|\n"
            f"{ticket_rows}\n\n"
            f"Source: [ServiceNow + IT Asset Management]\nAgents: ITTicketManagementAgent"
        )

    # ── priority_assignment ────────────────────────────────────
    def _priority_assignment(self):
        by_sev = _tickets_by_severity()
        assignment_rows = ""
        for t in _TICKETS.values():
            sla = _SLA_TARGETS[t["severity"]]
            assignment_rows += f"| {t['id']} | {t['severity']} | {t['team']} | {t['assignee']} | {t['users_affected']} | {sla['resolution_hours']}h |\n"
        team_rows = ""
        for team_name, tc in _TEAM_CAPACITY.items():
            team_rows += f"| {team_name} | {tc['members']} | {tc['current_tickets']} | {tc['capacity_pct']}% | {', '.join(tc['skills'][:2])} |\n"
        return (
            f"**Priority Assignment Matrix**\n\n"
            f"**Ticket Assignments:**\n\n"
            f"| ID | Priority | Team | Assignee | Users Affected | SLA |\n|---|---|---|---|---|---|\n"
            f"{assignment_rows}\n"
            f"**Team Capacity:**\n\n"
            f"| Team | Members | Tickets | Capacity | Skills |\n|---|---|---|---|---|\n"
            f"{team_rows}\n\n"
            f"Source: [ServiceNow + Workforce Management]\nAgents: ITTicketManagementAgent"
        )

    # ── sla_tracking ───────────────────────────────────────────
    def _sla_tracking(self):
        at_risk = _sla_at_risk()
        risk_rows = ""
        for t in at_risk:
            risk_rows += f"| {t['id']} | {t['severity']} | {t['remaining_hours']:.1f}h | {t['assignee']} | {t['subject'][:40]} |\n"
        if not risk_rows:
            risk_rows = "| None | - | - | - | All tickets on track |\n"
        sla_rows = ""
        for sev, targets in _SLA_TARGETS.items():
            sla_rows += f"| {sev} | {targets['response_hours']}h | {targets['resolution_hours']}h | {targets['escalation_after_hours']}h | ${targets['penalty_per_breach']} |\n"
        return (
            f"**SLA Tracking Dashboard**\n\n"
            f"**At-Risk Tickets:**\n\n"
            f"| Ticket | Severity | Time Remaining | Assignee | Subject |\n|---|---|---|---|---|\n"
            f"{risk_rows}\n"
            f"**SLA Targets:**\n\n"
            f"| Severity | Response | Resolution | Escalation | Breach Penalty |\n|---|---|---|---|---|\n"
            f"{sla_rows}\n"
            f"**Current SLA Compliance:** {_RESOLUTION_HISTORY['this_week']['sla_met_pct']}% (target: 95%)\n\n"
            f"Source: [ServiceNow SLA Engine]\nAgents: ITTicketManagementAgent"
        )

    # ── resolution_report ──────────────────────────────────────
    def _resolution_report(self):
        tw = _RESOLUTION_HISTORY["this_week"]
        lw = _RESOLUTION_HISTORY["last_week"]
        tm = _RESOLUTION_HISTORY["this_month"]
        trend_rows = (
            f"| This Week | {tw['resolved']} | {tw['avg_resolution_hours']}h | {tw['sla_met_pct']}% | {tw['first_call_resolution_pct']}% | {tw['csat']}/5 |\n"
            f"| Last Week | {lw['resolved']} | {lw['avg_resolution_hours']}h | {lw['sla_met_pct']}% | {lw['first_call_resolution_pct']}% | {lw['csat']}/5 |\n"
            f"| This Month | {tm['resolved']} | {tm['avg_resolution_hours']}h | {tm['sla_met_pct']}% | {tm['first_call_resolution_pct']}% | {tm['csat']}/5 |\n"
        )
        cat_rows = ""
        for cat in _RESOLUTION_HISTORY["top_categories"]:
            auto = "Yes" if cat["automation_candidate"] else "No"
            cat_rows += f"| {cat['category']} | {cat['count']} | {cat['pct']}% | {auto} |\n"
        return (
            f"**Resolution Report**\n\n"
            f"**Performance Trends:**\n\n"
            f"| Period | Resolved | Avg Resolution | SLA Met | FCR | CSAT |\n|---|---|---|---|---|---|\n"
            f"{trend_rows}\n"
            f"**Top Issue Categories (This Month):**\n\n"
            f"| Category | Count | % of Total | Automate? |\n|---|---|---|---|\n"
            f"{cat_rows}\n"
            f"**Recommendations:**\n"
            f"- Automate password resets (18.6% of volume) to save ~22 hours/week\n"
            f"- Implement self-service software access portal (15.1% of volume)\n"
            f"- Investigate recurring VPN issues (12.2% of volume)\n\n"
            f"Source: [ServiceNow Analytics + Power BI]\nAgents: ITTicketManagementAgent"
        )


if __name__ == "__main__":
    agent = ITTicketManagementAgent()
    for op in ["ticket_dashboard", "priority_assignment", "sla_tracking", "resolution_report"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
