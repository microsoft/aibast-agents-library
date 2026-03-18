"""
Voice to CRM ServiceNow Agent

Creates ServiceNow incidents from voice input, searches knowledge articles,
routes assignments, and tracks status updates.

Where a real deployment would connect to ServiceNow APIs, this agent uses
a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/voice-to-crm-servicenow",
    "version": "1.0.0",
    "display_name": "Voice to CRM (ServiceNow)",
    "description": "ServiceNow integration for incident creation, knowledge search, assignment routing, and status updates.",
    "author": "AIBAST",
    "tags": ["servicenow", "itsm", "incidents", "knowledge-base", "routing"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_INCIDENTS = {
    "INC-20001": {
        "number": "INC-20001", "short_description": "Email server unresponsive - 500+ users affected",
        "description": "Exchange Online hybrid connector failing. Users unable to send/receive emails since 8:15 AM. Cloud-to-on-prem sync broken.",
        "category": "Infrastructure", "subcategory": "Email",
        "impact": 1, "urgency": 1, "priority": "P1-Critical",
        "state": "In Progress", "assigned_to": "Sarah Chen",
        "assignment_group": "Network Operations",
        "caller": "Marcus Thompson", "opened_at": "2025-11-14T08:20:00Z",
        "sla_breach_at": "2025-11-14T09:20:00Z",
        "work_notes": "Exchange hybrid connector logs show certificate expiry. Renewing certificate now.",
    },
    "INC-20002": {
        "number": "INC-20002", "short_description": "VPN authentication failing for remote workers",
        "description": "Pulse Secure VPN returning authentication errors for users with MFA enabled. Started after last night's Azure AD update.",
        "category": "Network", "subcategory": "VPN",
        "impact": 2, "urgency": 2, "priority": "P2-High",
        "state": "Assigned", "assigned_to": "Mike Torres",
        "assignment_group": "Network Operations",
        "caller": "Lisa Wong", "opened_at": "2025-11-14T08:45:00Z",
        "sla_breach_at": "2025-11-14T12:45:00Z",
        "work_notes": "Investigating Azure AD conditional access policy changes from last night.",
    },
    "INC-20003": {
        "number": "INC-20003", "short_description": "Printer offline on Floor 3 - Board room",
        "description": "HP LaserJet Pro M428 in Board Room 3A showing offline. Executive presentation at 10 AM requires printing.",
        "category": "Hardware", "subcategory": "Printer",
        "impact": 3, "urgency": 2, "priority": "P3-Medium",
        "state": "Open", "assigned_to": "unassigned",
        "assignment_group": "Desktop Support",
        "caller": "Jennifer Walsh", "opened_at": "2025-11-14T09:00:00Z",
        "sla_breach_at": "2025-11-14T17:00:00Z",
        "work_notes": "",
    },
}

_KB_ARTICLES = {
    "KB0010234": {"number": "KB0010234", "title": "Exchange Hybrid Connector - Certificate Renewal", "category": "Email", "views": 1247, "rating": 4.8, "resolution_steps": ["Open Exchange Admin Center", "Navigate to Organization > Sharing", "Renew federation certificate", "Restart MSExchangeHybridService", "Verify mail flow with Test-MailFlow cmdlet"], "last_updated": "2025-10-15"},
    "KB0010198": {"number": "KB0010198", "title": "VPN MFA Authentication Troubleshooting", "category": "Network", "views": 2340, "rating": 4.5, "resolution_steps": ["Check Azure AD Conditional Access policies", "Verify MFA service health at status.azure.com", "Clear VPN client cached credentials", "Re-register MFA method at aka.ms/mfasetup", "Test with basic authentication first"], "last_updated": "2025-11-01"},
    "KB0010156": {"number": "KB0010156", "title": "HP LaserJet Printer Offline Recovery", "category": "Hardware", "views": 3890, "rating": 4.2, "resolution_steps": ["Power cycle the printer (30 second wait)", "Check network cable / WiFi connection", "Run printer troubleshooter on client PC", "Reinstall printer driver if needed", "Clear print queue and restart spooler"], "last_updated": "2025-09-20"},
    "KB0010301": {"number": "KB0010301", "title": "ServiceNow Incident Escalation Procedures", "category": "Process", "views": 890, "rating": 4.6, "resolution_steps": ["Verify incident priority matrix", "Contact assignment group lead", "Update incident with escalation notes", "Notify management per escalation policy", "Track response time against SLA"], "last_updated": "2025-10-28"},
}

_ASSIGNMENT_GROUPS = {
    "Network Operations": {"manager": "David Kim", "members": 6, "active_incidents": 8, "avg_resolution_hours": 3.5, "sla_met_pct": 96.2},
    "Desktop Support": {"manager": "Lisa Park", "members": 8, "active_incidents": 22, "avg_resolution_hours": 5.2, "sla_met_pct": 92.8},
    "Application Support": {"manager": "James Mitchell", "members": 5, "active_incidents": 12, "avg_resolution_hours": 4.8, "sla_met_pct": 94.5},
    "Database Administration": {"manager": "Maria Santos", "members": 3, "active_incidents": 4, "avg_resolution_hours": 6.1, "sla_met_pct": 97.0},
    "Security Operations": {"manager": "Frank O'Brien", "members": 4, "active_incidents": 3, "avg_resolution_hours": 2.8, "sla_met_pct": 98.5},
}

_SLA_DATA = {
    "P1-Critical": {"response_min": 15, "resolution_hours": 1, "notification": "VP IT + On-Call Manager", "update_frequency_min": 15},
    "P2-High": {"response_min": 30, "resolution_hours": 4, "notification": "Assignment Group Manager", "update_frequency_min": 30},
    "P3-Medium": {"response_min": 60, "resolution_hours": 8, "notification": "Assignment Group", "update_frequency_min": 60},
    "P4-Low": {"response_min": 240, "resolution_hours": 24, "notification": "Queue", "update_frequency_min": 240},
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _match_kb_article(category):
    matches = [kb for kb in _KB_ARTICLES.values() if kb["category"] == category]
    return sorted(matches, key=lambda x: x["views"], reverse=True)


def _incident_summary():
    by_priority = {}
    for inc in _INCIDENTS.values():
        by_priority.setdefault(inc["priority"], []).append(inc)
    return by_priority


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class VoiceToCRMServiceNowAgent(BasicAgent):
    """
    Voice-to-CRM agent for ServiceNow.

    Operations:
        incident_create     - create a new incident from voice input
        knowledge_search    - search KB articles for resolution
        assignment_routing  - route incidents to appropriate teams
        status_update       - update incident status and work notes
    """

    def __init__(self):
        self.name = "VoiceToCRMServiceNowAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "incident_create", "knowledge_search",
                            "assignment_routing", "status_update",
                        ],
                        "description": "The ServiceNow operation to perform",
                    },
                    "incident_number": {
                        "type": "string",
                        "description": "Incident number (e.g. 'INC-20001')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "incident_create")
        inc_num = kwargs.get("incident_number", "INC-20001")
        dispatch = {
            "incident_create": self._incident_create,
            "knowledge_search": self._knowledge_search,
            "assignment_routing": self._assignment_routing,
            "status_update": self._status_update,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(inc_num)

    def _incident_create(self, inc_num):
        rows = ""
        for inc in _INCIDENTS.values():
            rows += f"| {inc['number']} | {inc['short_description'][:40]} | {inc['priority']} | {inc['state']} | {inc['assignment_group']} |\n"
        inc = _INCIDENTS.get(inc_num, list(_INCIDENTS.values())[0])
        return (
            f"**ServiceNow Incidents**\n\n"
            f"| Number | Description | Priority | State | Group |\n|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Detail: {inc['number']}**\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| Short Description | {inc['short_description']} |\n"
            f"| Category | {inc['category']} / {inc['subcategory']} |\n"
            f"| Priority | {inc['priority']} (Impact: {inc['impact']}, Urgency: {inc['urgency']}) |\n"
            f"| State | {inc['state']} |\n"
            f"| Assigned To | {inc['assigned_to']} |\n"
            f"| Caller | {inc['caller']} |\n"
            f"| SLA Breach | {inc['sla_breach_at']} |\n\n"
            f"**Description:** {inc['description']}\n\n"
            f"Source: [ServiceNow Instance]\nAgents: VoiceToCRMServiceNowAgent"
        )

    def _knowledge_search(self, inc_num):
        inc = _INCIDENTS.get(inc_num, list(_INCIDENTS.values())[0])
        matches = _match_kb_article(inc["category"])
        kb_rows = ""
        for kb in matches:
            kb_rows += f"| {kb['number']} | {kb['title'][:40]} | {kb['category']} | {kb['rating']}/5 | {kb['views']:,} |\n"
        if not kb_rows:
            kb_rows = "| No matches | - | - | - | - |\n"
        top = matches[0] if matches else None
        steps = ""
        if top:
            steps = "\n".join(f"{i+1}. {s}" for i, s in enumerate(top["resolution_steps"]))
        return (
            f"**Knowledge Search: {inc['category']}**\n\n"
            f"For Incident: {inc['number']} - {inc['short_description'][:40]}\n\n"
            f"| Article | Title | Category | Rating | Views |\n|---|---|---|---|---|\n"
            f"{kb_rows}\n"
            f"**Top Match: {top['title'] if top else 'N/A'}**\n\n"
            f"**Resolution Steps:**\n{steps}\n\n"
            f"Last Updated: {top['last_updated'] if top else 'N/A'}\n\n"
            f"Source: [ServiceNow Knowledge Base]\nAgents: VoiceToCRMServiceNowAgent"
        )

    def _assignment_routing(self, inc_num):
        group_rows = ""
        for name, grp in _ASSIGNMENT_GROUPS.items():
            group_rows += f"| {name} | {grp['manager']} | {grp['members']} | {grp['active_incidents']} | {grp['avg_resolution_hours']}h | {grp['sla_met_pct']}% |\n"
        sla_rows = ""
        for pri, sla in _SLA_DATA.items():
            sla_rows += f"| {pri} | {sla['response_min']}m | {sla['resolution_hours']}h | {sla['notification']} | {sla['update_frequency_min']}m |\n"
        return (
            f"**Assignment Routing**\n\n"
            f"**Assignment Groups:**\n\n"
            f"| Group | Manager | Members | Active | Avg Resolution | SLA Met |\n|---|---|---|---|---|---|\n"
            f"{group_rows}\n"
            f"**SLA Targets:**\n\n"
            f"| Priority | Response | Resolution | Notification | Updates |\n|---|---|---|---|---|\n"
            f"{sla_rows}\n\n"
            f"Source: [ServiceNow CMDB + SLA Engine]\nAgents: VoiceToCRMServiceNowAgent"
        )

    def _status_update(self, inc_num):
        inc = _INCIDENTS.get(inc_num, list(_INCIDENTS.values())[0])
        sla = _SLA_DATA.get(inc["priority"], _SLA_DATA["P3-Medium"])
        by_priority = _incident_summary()
        summary_rows = ""
        for pri in ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]:
            count = len(by_priority.get(pri, []))
            summary_rows += f"| {pri} | {count} |\n"
        return (
            f"**Status Update: {inc['number']}**\n\n"
            f"| Field | Current | Updated |\n|---|---|---|\n"
            f"| State | {inc['state']} | {inc['state']} |\n"
            f"| Assigned To | {inc['assigned_to']} | {inc['assigned_to']} |\n"
            f"| Priority | {inc['priority']} | {inc['priority']} |\n\n"
            f"**Work Notes:** {inc['work_notes'] or 'No work notes yet'}\n\n"
            f"**SLA Status:**\n"
            f"- Response SLA: {sla['response_min']} minutes\n"
            f"- Resolution SLA: {sla['resolution_hours']} hours\n"
            f"- Breach Time: {inc['sla_breach_at']}\n"
            f"- Update Frequency: Every {sla['update_frequency_min']} minutes\n\n"
            f"**Overall Queue:**\n\n"
            f"| Priority | Count |\n|---|---|\n"
            f"{summary_rows}\n\n"
            f"Source: [ServiceNow Instance]\nAgents: VoiceToCRMServiceNowAgent"
        )


if __name__ == "__main__":
    agent = VoiceToCRMServiceNowAgent()
    for op in ["incident_create", "knowledge_search", "assignment_routing", "status_update"]:
        print("=" * 60)
        print(agent.perform(operation=op, incident_number="INC-20001"))
        print()
