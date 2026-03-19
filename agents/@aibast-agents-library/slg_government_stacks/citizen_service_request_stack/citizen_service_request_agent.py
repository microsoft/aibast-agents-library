"""
Citizen Service Request Agent — SLG Government Stack

Handles citizen service request intake, department routing, status
updates, and resolution summaries for municipal 311-style systems.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/citizen-service-request",
    "version": "1.0.0",
    "display_name": "Citizen Service Request Agent",
    "description": "Municipal service request management with intake, routing, status tracking, and resolution summaries.",
    "author": "AIBAST",
    "tags": ["311", "citizen-services", "municipal", "routing", "SLA", "local-government"],
    "category": "slg_government",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

SERVICE_REQUESTS = {
    "SR-2025-10001": {
        "category": "pothole_repair",
        "description": "Large pothole on Main St between 3rd and 4th Ave, approximately 18 inches wide",
        "location": "142 Main Street",
        "ward": 3,
        "submitted": "2025-02-28",
        "submitter": "Maria Gonzalez",
        "channel": "web_portal",
        "priority": "high",
        "status": "assigned",
        "department": "Public Works — Streets Division",
        "assigned_to": "Crew 7-B",
        "sla_target": "2025-03-07",
    },
    "SR-2025-10002": {
        "category": "streetlight_outage",
        "description": "Streetlight at intersection of Pine and Oak has been out for 2 weeks",
        "location": "Pine St & Oak Ave",
        "ward": 5,
        "submitted": "2025-03-01",
        "submitter": "David Kim",
        "channel": "phone_311",
        "priority": "medium",
        "status": "in_progress",
        "department": "Public Works — Electrical",
        "assigned_to": "Tech Unit 3",
        "sla_target": "2025-03-15",
    },
    "SR-2025-10003": {
        "category": "trash_collection_missed",
        "description": "Missed residential trash pickup on scheduled collection day (Tuesday)",
        "location": "2847 Elm Drive",
        "ward": 2,
        "submitted": "2025-03-04",
        "submitter": "Linda Park",
        "channel": "mobile_app",
        "priority": "medium",
        "status": "resolved",
        "department": "Sanitation Services",
        "assigned_to": "Route 12-A",
        "sla_target": "2025-03-06",
        "resolved_date": "2025-03-05",
        "resolution": "Special pickup completed. Route schedule updated to prevent recurrence.",
    },
    "SR-2025-10004": {
        "category": "graffiti_removal",
        "description": "Graffiti on retaining wall along Riverside Park walking path",
        "location": "Riverside Park — east entrance",
        "ward": 4,
        "submitted": "2025-03-05",
        "submitter": "Anonymous",
        "channel": "web_portal",
        "priority": "low",
        "status": "pending",
        "department": "Parks & Recreation",
        "assigned_to": None,
        "sla_target": "2025-03-19",
    },
    "SR-2025-10005": {
        "category": "water_main_break",
        "description": "Water bubbling up from street surface near fire hydrant, flooding sidewalk",
        "location": "600 block of Washington Blvd",
        "ward": 1,
        "submitted": "2025-03-06",
        "submitter": "James Walker",
        "channel": "phone_311",
        "priority": "critical",
        "status": "in_progress",
        "department": "Water & Sewer — Emergency",
        "assigned_to": "Emergency Crew Alpha",
        "sla_target": "2025-03-07",
    },
}

DEPARTMENT_ROUTING = {
    "pothole_repair": {"department": "Public Works — Streets Division", "sla_days": 7, "priority_default": "high"},
    "streetlight_outage": {"department": "Public Works — Electrical", "sla_days": 14, "priority_default": "medium"},
    "trash_collection_missed": {"department": "Sanitation Services", "sla_days": 2, "priority_default": "medium"},
    "graffiti_removal": {"department": "Parks & Recreation", "sla_days": 14, "priority_default": "low"},
    "water_main_break": {"department": "Water & Sewer — Emergency", "sla_days": 1, "priority_default": "critical"},
    "sidewalk_damage": {"department": "Public Works — Streets Division", "sla_days": 21, "priority_default": "low"},
    "noise_complaint": {"department": "Code Enforcement", "sla_days": 3, "priority_default": "medium"},
    "abandoned_vehicle": {"department": "Police — Non-Emergency", "sla_days": 7, "priority_default": "low"},
    "tree_hazard": {"department": "Public Works — Urban Forestry", "sla_days": 5, "priority_default": "high"},
    "illegal_dumping": {"department": "Sanitation Services", "sla_days": 7, "priority_default": "medium"},
}

SLA_TARGETS = {
    "critical": {"response_hours": 4, "resolution_days": 1},
    "high": {"response_hours": 24, "resolution_days": 7},
    "medium": {"response_hours": 48, "resolution_days": 14},
    "low": {"response_hours": 72, "resolution_days": 21},
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _sla_compliance():
    """Calculate SLA compliance metrics."""
    total = len(SERVICE_REQUESTS)
    resolved = [sr for sr in SERVICE_REQUESTS.values() if sr["status"] == "resolved"]
    on_time = sum(1 for sr in resolved if sr.get("resolved_date", "9999") <= sr["sla_target"])
    resolution_rate = round((len(resolved) / total) * 100, 1) if total else 0
    sla_rate = round((on_time / len(resolved)) * 100, 1) if resolved else 0
    return {"total": total, "resolved": len(resolved), "resolution_rate": resolution_rate, "sla_compliance": sla_rate}


def _category_breakdown():
    """Count requests by category."""
    breakdown = {}
    for sr in SERVICE_REQUESTS.values():
        cat = sr["category"]
        breakdown[cat] = breakdown.get(cat, 0) + 1
    return breakdown


def _ward_breakdown():
    """Count requests by ward."""
    breakdown = {}
    for sr in SERVICE_REQUESTS.values():
        ward = sr["ward"]
        breakdown[ward] = breakdown.get(ward, 0) + 1
    return breakdown


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class CitizenServiceRequestAgent(BasicAgent):
    """Citizen service request management agent for municipalities."""

    def __init__(self):
        self.name = "@aibast-agents-library/citizen-service-request"
        self.metadata = {
            "name": self.name,
            "display_name": "Citizen Service Request Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "request_intake",
                            "routing_assignment",
                            "status_update",
                            "resolution_summary",
                        ],
                    },
                    "request_id": {"type": "string"},
                    "category": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "request_intake")
        dispatch = {
            "request_intake": self._request_intake,
            "routing_assignment": self._routing_assignment,
            "status_update": self._status_update,
            "resolution_summary": self._resolution_summary,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _request_intake(self, **kwargs) -> str:
        lines = ["# Service Request Intake Dashboard\n"]
        metrics = _sla_compliance()
        lines.append(f"**Total Requests:** {metrics['total']}")
        lines.append(f"**Resolved:** {metrics['resolved']} ({metrics['resolution_rate']}%)")
        lines.append(f"**SLA Compliance:** {metrics['sla_compliance']}%\n")
        lines.append("## Active Requests\n")
        lines.append("| SR ID | Category | Location | Priority | Status | Department |")
        lines.append("|---|---|---|---|---|---|")
        for srid, sr in SERVICE_REQUESTS.items():
            cat = sr["category"].replace("_", " ").title()
            lines.append(
                f"| {srid} | {cat} | {sr['location']} "
                f"| {sr['priority'].title()} | {sr['status'].replace('_', ' ').title()} | {sr['department']} |"
            )
        lines.append("\n## Requests by Category\n")
        for cat, count in _category_breakdown().items():
            lines.append(f"- {cat.replace('_', ' ').title()}: {count}")
        lines.append("\n## Requests by Ward\n")
        for ward, count in sorted(_ward_breakdown().items()):
            lines.append(f"- Ward {ward}: {count}")
        return "\n".join(lines)

    def _routing_assignment(self, **kwargs) -> str:
        lines = ["# Service Request Routing Guide\n"]
        lines.append("## Category Routing Table\n")
        lines.append("| Category | Department | SLA (days) | Default Priority |")
        lines.append("|---|---|---|---|")
        for cat, routing in DEPARTMENT_ROUTING.items():
            lines.append(
                f"| {cat.replace('_', ' ').title()} | {routing['department']} "
                f"| {routing['sla_days']} | {routing['priority_default'].title()} |"
            )
        lines.append("\n## SLA Response Standards\n")
        lines.append("| Priority | Response Time | Resolution Target |")
        lines.append("|---|---|---|")
        for priority, sla in SLA_TARGETS.items():
            lines.append(f"| {priority.title()} | {sla['response_hours']} hours | {sla['resolution_days']} days |")
        lines.append("\n## Pending Assignment\n")
        unassigned = {k: v for k, v in SERVICE_REQUESTS.items() if v["assigned_to"] is None}
        if unassigned:
            for srid, sr in unassigned.items():
                routing = DEPARTMENT_ROUTING.get(sr["category"], {})
                lines.append(f"- **{srid}:** {sr['category'].replace('_', ' ').title()} -> {routing.get('department', 'TBD')}")
        else:
            lines.append("All requests currently assigned.")
        return "\n".join(lines)

    def _status_update(self, **kwargs) -> str:
        request_id = kwargs.get("request_id")
        if request_id and request_id in SERVICE_REQUESTS:
            sr = SERVICE_REQUESTS[request_id]
            lines = [f"# Status Update: {request_id}\n"]
            lines.append(f"- **Category:** {sr['category'].replace('_', ' ').title()}")
            lines.append(f"- **Description:** {sr['description']}")
            lines.append(f"- **Location:** {sr['location']} (Ward {sr['ward']})")
            lines.append(f"- **Submitted:** {sr['submitted']} via {sr['channel'].replace('_', ' ').title()}")
            lines.append(f"- **Priority:** {sr['priority'].title()}")
            lines.append(f"- **Status:** {sr['status'].replace('_', ' ').title()}")
            lines.append(f"- **Department:** {sr['department']}")
            lines.append(f"- **Assigned To:** {sr['assigned_to'] or 'Unassigned'}")
            lines.append(f"- **SLA Target:** {sr['sla_target']}")
            if sr.get("resolved_date"):
                lines.append(f"- **Resolved:** {sr['resolved_date']}")
            if sr.get("resolution"):
                lines.append(f"- **Resolution:** {sr['resolution']}")
            return "\n".join(lines)

        lines = ["# Request Status Summary\n"]
        lines.append("| SR ID | Category | Status | Assigned To | SLA Target |")
        lines.append("|---|---|---|---|---|")
        for srid, sr in SERVICE_REQUESTS.items():
            lines.append(
                f"| {srid} | {sr['category'].replace('_', ' ').title()} "
                f"| {sr['status'].replace('_', ' ').title()} | {sr['assigned_to'] or 'Unassigned'} | {sr['sla_target']} |"
            )
        return "\n".join(lines)

    def _resolution_summary(self, **kwargs) -> str:
        lines = ["# Resolution Summary Report\n"]
        metrics = _sla_compliance()
        lines.append(f"**Resolution Rate:** {metrics['resolution_rate']}%")
        lines.append(f"**SLA Compliance:** {metrics['sla_compliance']}%\n")
        resolved = {k: v for k, v in SERVICE_REQUESTS.items() if v["status"] == "resolved"}
        if resolved:
            lines.append("## Resolved Requests\n")
            for srid, sr in resolved.items():
                lines.append(f"### {srid}: {sr['category'].replace('_', ' ').title()}\n")
                lines.append(f"- **Location:** {sr['location']}")
                lines.append(f"- **Submitted:** {sr['submitted']}")
                lines.append(f"- **Resolved:** {sr.get('resolved_date', 'N/A')}")
                lines.append(f"- **SLA Target:** {sr['sla_target']}")
                met = "Yes" if sr.get("resolved_date", "9999") <= sr["sla_target"] else "No"
                lines.append(f"- **SLA Met:** {met}")
                lines.append(f"- **Resolution:** {sr.get('resolution', 'N/A')}\n")
        open_requests = {k: v for k, v in SERVICE_REQUESTS.items() if v["status"] != "resolved"}
        if open_requests:
            lines.append("## Open Requests\n")
            lines.append("| SR ID | Category | Priority | Status | SLA Target |")
            lines.append("|---|---|---|---|---|")
            for srid, sr in open_requests.items():
                lines.append(
                    f"| {srid} | {sr['category'].replace('_', ' ').title()} "
                    f"| {sr['priority'].title()} | {sr['status'].replace('_', ' ').title()} | {sr['sla_target']} |"
                )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = CitizenServiceRequestAgent()
    print(agent.perform(operation="request_intake"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="routing_assignment"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="status_update", request_id="SR-2025-10001"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="resolution_summary"))
