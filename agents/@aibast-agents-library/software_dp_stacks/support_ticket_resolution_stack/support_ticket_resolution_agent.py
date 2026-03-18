"""
Support Ticket Resolution Agent for Software/Digital Products.

Provides intelligent ticket triage, knowledge base resolution search,
escalation routing, and SLA compliance dashboards for support operations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/support-ticket-resolution",
    "version": "1.0.0",
    "display_name": "Support Ticket Resolution Agent",
    "description": "Intelligent ticket triage, KB resolution search, escalation routing, and SLA compliance dashboards.",
    "author": "AIBAST",
    "tags": ["support", "tickets", "triage", "sla", "knowledge-base", "escalation"],
    "category": "software_digital_products",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

SUPPORT_TICKETS = {
    "TKT-8001": {
        "customer": "Meridian Healthcare Systems",
        "subject": "Dashboard loading timeout on large datasets",
        "severity": "P2",
        "category": "performance",
        "status": "open",
        "created": "2026-03-15T09:22:00",
        "sla_deadline": "2026-03-16T09:22:00",
        "assigned_to": "Tier 2 - Backend",
        "arr": 186000,
        "description": "Dashboard takes 45+ seconds to load when filtering by date ranges exceeding 90 days.",
    },
    "TKT-8002": {
        "customer": "ClearView Analytics",
        "subject": "SSO login failure after IdP certificate rotation",
        "severity": "P1",
        "category": "authentication",
        "status": "in_progress",
        "created": "2026-03-16T06:15:00",
        "sla_deadline": "2026-03-16T10:15:00",
        "assigned_to": "Tier 3 - Security",
        "arr": 72000,
        "description": "All users unable to authenticate via Okta SSO after certificate rotation. Entire org locked out.",
    },
    "TKT-8003": {
        "customer": "Skyline Hospitality Group",
        "subject": "API rate limit exceeded during bulk import",
        "severity": "P3",
        "category": "api",
        "status": "open",
        "created": "2026-03-14T14:30:00",
        "sla_deadline": "2026-03-17T14:30:00",
        "assigned_to": "Tier 1 - General",
        "arr": 360000,
        "description": "Bulk import process hitting 429 errors. Need temporary rate limit increase or batch guidance.",
    },
    "TKT-8004": {
        "customer": "BrightPath Education",
        "subject": "Report export generates corrupted CSV files",
        "severity": "P2",
        "category": "data_export",
        "status": "waiting_customer",
        "created": "2026-03-13T11:00:00",
        "sla_deadline": "2026-03-14T11:00:00",
        "assigned_to": "Tier 2 - Data",
        "arr": 96000,
        "description": "CSV exports for enrollment reports contain malformed UTF-8 characters. Affects downstream systems.",
    },
    "TKT-8005": {
        "customer": "Granite Construction Co",
        "subject": "Cannot add new users to workspace",
        "severity": "P2",
        "category": "user_management",
        "status": "open",
        "created": "2026-03-16T08:45:00",
        "sla_deadline": "2026-03-17T08:45:00",
        "assigned_to": "Tier 1 - General",
        "arr": 54000,
        "description": "Admin portal returns 500 error when attempting to invite new users. Seat count shows 12/20.",
    },
}

KB_ARTICLES = {
    "KB-101": {"title": "Optimizing Dashboard Performance for Large Datasets", "category": "performance", "views": 1842, "helpfulness": 87},
    "KB-102": {"title": "SSO Certificate Rotation Guide", "category": "authentication", "views": 956, "helpfulness": 92},
    "KB-103": {"title": "API Rate Limits and Bulk Import Best Practices", "category": "api", "views": 2103, "helpfulness": 78},
    "KB-104": {"title": "Troubleshooting CSV Export Encoding Issues", "category": "data_export", "views": 634, "helpfulness": 81},
    "KB-105": {"title": "User Management and Invitation Troubleshooting", "category": "user_management", "views": 1247, "helpfulness": 74},
    "KB-106": {"title": "SAML 2.0 Configuration Reference", "category": "authentication", "views": 712, "helpfulness": 89},
}

SLA_THRESHOLDS = {
    "P1": {"first_response_hrs": 1, "resolution_hrs": 4},
    "P2": {"first_response_hrs": 4, "resolution_hrs": 24},
    "P3": {"first_response_hrs": 8, "resolution_hrs": 72},
    "P4": {"first_response_hrs": 24, "resolution_hrs": 168},
}

RESOLUTION_HISTORY = {
    "performance": {"avg_resolution_hrs": 18.4, "first_contact_resolution_pct": 32},
    "authentication": {"avg_resolution_hrs": 3.2, "first_contact_resolution_pct": 45},
    "api": {"avg_resolution_hrs": 12.6, "first_contact_resolution_pct": 58},
    "data_export": {"avg_resolution_hrs": 22.1, "first_contact_resolution_pct": 28},
    "user_management": {"avg_resolution_hrs": 6.8, "first_contact_resolution_pct": 65},
}

ESCALATION_MATRIX = {
    "Tier 1 - General": {"escalates_to": "Tier 2 - Specialist", "manager": "Rachel Torres"},
    "Tier 2 - Backend": {"escalates_to": "Tier 3 - Engineering", "manager": "David Kim"},
    "Tier 2 - Data": {"escalates_to": "Tier 3 - Engineering", "manager": "David Kim"},
    "Tier 3 - Security": {"escalates_to": "VP Engineering", "manager": "Samira Patel"},
    "Tier 3 - Engineering": {"escalates_to": "VP Engineering", "manager": "Samira Patel"},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ticket_triage():
    triaged = []
    for tid, t in SUPPORT_TICKETS.items():
        kb_matches = [a for aid, a in KB_ARTICLES.items() if a["category"] == t["category"]]
        hist = RESOLUTION_HISTORY.get(t["category"], {})
        triaged.append({
            "id": tid, "subject": t["subject"], "severity": t["severity"],
            "category": t["category"], "customer": t["customer"],
            "arr": t["arr"], "status": t["status"],
            "kb_matches": len(kb_matches),
            "avg_resolution_hrs": hist.get("avg_resolution_hrs", 0),
            "fcr_pct": hist.get("first_contact_resolution_pct", 0),
        })
    severity_order = {"P1": 0, "P2": 1, "P3": 2, "P4": 3}
    triaged.sort(key=lambda x: (severity_order.get(x["severity"], 9), -x["arr"]))
    return {"tickets": triaged, "total": len(triaged)}


def _resolution_search(category=None):
    if category:
        matches = {aid: a for aid, a in KB_ARTICLES.items() if a["category"] == category}
    else:
        matches = KB_ARTICLES
    results = []
    for aid, a in matches.items():
        results.append({"id": aid, "title": a["title"], "category": a["category"],
                        "views": a["views"], "helpfulness": a["helpfulness"]})
    results.sort(key=lambda x: x["helpfulness"], reverse=True)
    return {"results": results, "total": len(results)}


def _escalation_routing():
    routes = []
    for tid, t in SUPPORT_TICKETS.items():
        esc = ESCALATION_MATRIX.get(t["assigned_to"], {})
        routes.append({
            "ticket_id": tid, "subject": t["subject"], "severity": t["severity"],
            "current_team": t["assigned_to"], "escalates_to": esc.get("escalates_to", "N/A"),
            "manager": esc.get("manager", "N/A"), "customer": t["customer"],
        })
    return {"routes": routes}


def _sla_dashboard():
    metrics = {"total": len(SUPPORT_TICKETS), "breached": 0, "at_risk": 0, "on_track": 0}
    details = []
    for tid, t in SUPPORT_TICKETS.items():
        sla = SLA_THRESHOLDS.get(t["severity"], {})
        # Simplified: mark P1 open/in_progress as at_risk, breached SLA for TKT-8004
        if tid == "TKT-8004":
            status = "breached"
            metrics["breached"] += 1
        elif t["severity"] == "P1":
            status = "at_risk"
            metrics["at_risk"] += 1
        else:
            status = "on_track"
            metrics["on_track"] += 1
        details.append({
            "ticket_id": tid, "severity": t["severity"], "customer": t["customer"],
            "sla_status": status, "resolution_target_hrs": sla.get("resolution_hrs", 0),
        })
    return {"metrics": metrics, "details": details}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class SupportTicketResolutionAgent(BasicAgent):
    """Support ticket triage, resolution, and SLA management agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/support-ticket-resolution"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "ticket_triage",
                            "resolution_search",
                            "escalation_routing",
                            "sla_dashboard",
                        ],
                        "description": "The support operation to perform.",
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter for resolution search.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "ticket_triage")
        if op == "ticket_triage":
            return self._ticket_triage()
        elif op == "resolution_search":
            return self._resolution_search(kwargs.get("category"))
        elif op == "escalation_routing":
            return self._escalation_routing()
        elif op == "sla_dashboard":
            return self._sla_dashboard()
        return f"**Error:** Unknown operation `{op}`."

    def _ticket_triage(self) -> str:
        data = _ticket_triage()
        lines = [
            "# Ticket Triage Queue",
            "",
            f"**Open Tickets:** {data['total']}",
            "",
            "| Priority | Ticket | Customer | Category | ARR | KB Matches | Avg Resolution |",
            "|----------|--------|----------|----------|-----|-----------|----------------|",
        ]
        for t in data["tickets"]:
            lines.append(
                f"| {t['severity']} | {t['id']} | {t['customer']} | {t['category']} "
                f"| ${t['arr']:,} | {t['kb_matches']} | {t['avg_resolution_hrs']}h |"
            )
        return "\n".join(lines)

    def _resolution_search(self, category=None) -> str:
        data = _resolution_search(category)
        filter_label = f" (filtered: {category})" if category else ""
        lines = [
            f"# Knowledge Base Search{filter_label}",
            "",
            f"**Results:** {data['total']}",
            "",
            "| Article | Category | Views | Helpfulness |",
            "|---------|----------|-------|------------|",
        ]
        for r in data["results"]:
            lines.append(
                f"| {r['title']} | {r['category']} | {r['views']:,} | {r['helpfulness']}% |"
            )
        return "\n".join(lines)

    def _escalation_routing(self) -> str:
        data = _escalation_routing()
        lines = [
            "# Escalation Routing Map",
            "",
            "| Ticket | Severity | Customer | Current Team | Escalates To | Manager |",
            "|--------|----------|----------|-------------|-------------|---------|",
        ]
        for r in data["routes"]:
            lines.append(
                f"| {r['ticket_id']} | {r['severity']} | {r['customer']} "
                f"| {r['current_team']} | {r['escalates_to']} | {r['manager']} |"
            )
        return "\n".join(lines)

    def _sla_dashboard(self) -> str:
        data = _sla_dashboard()
        m = data["metrics"]
        lines = [
            "# SLA Compliance Dashboard",
            "",
            f"**Total Tickets:** {m['total']}",
            f"- On Track: {m['on_track']}",
            f"- At Risk: {m['at_risk']}",
            f"- Breached: {m['breached']}",
            "",
            "| Ticket | Severity | Customer | SLA Status | Resolution Target |",
            "|--------|----------|----------|-----------|-------------------|",
        ]
        for d in data["details"]:
            lines.append(
                f"| {d['ticket_id']} | {d['severity']} | {d['customer']} "
                f"| {d['sla_status'].upper()} | {d['resolution_target_hrs']}h |"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = SupportTicketResolutionAgent()
    for op in ["ticket_triage", "resolution_search", "escalation_routing", "sla_dashboard"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
