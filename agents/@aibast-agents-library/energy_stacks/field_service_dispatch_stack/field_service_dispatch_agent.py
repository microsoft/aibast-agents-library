"""
Field Service Dispatch Agent for Energy sector.

Manages field service operations including dispatch dashboards, route
optimization, technician assignment based on skills, and emergency response
coordination for energy infrastructure maintenance.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/field-service-dispatch",
    "version": "1.1.0",
    "display_name": "Field Service Dispatch Agent",
    "description": "Provide read-only field-service decision support from a synthetic request and technician snapshot: priority dashboards, zone capacity, skill matching, and emergency response drafts. The agent never dispatches or reroutes a crew, changes a job, contacts a customer, stages inventory, or authorizes field action; a human dispatcher must approve work through future authenticated tools.",
    "author": "AIBAST",
    "tags": ["field-service", "dispatch", "routing", "technicians", "emergency", "energy"],
    "category": "energy",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

TECHNICIANS = {
    "TECH-201": {
        "name": "Carlos Rivera",
        "certifications": ["electrical_high_voltage", "transformer_maintenance", "confined_space"],
        "zone": "West",
        "status": "available",
        "current_location": "Sacramento, CA",
        "jobs_today": 1,
        "max_jobs": 4,
        "efficiency_rating": 94,
        "years_experience": 12,
    },
    "TECH-202": {
        "name": "Amy Blackwell",
        "certifications": ["wind_turbine", "electrical_high_voltage", "crane_operation"],
        "zone": "Central",
        "status": "on_job",
        "current_location": "Sweetwater, TX",
        "jobs_today": 2,
        "max_jobs": 4,
        "efficiency_rating": 91,
        "years_experience": 8,
    },
    "TECH-203": {
        "name": "Raj Patel",
        "certifications": ["gas_turbine", "combustion_systems", "electrical_high_voltage"],
        "zone": "West",
        "status": "available",
        "current_location": "Bakersfield, CA",
        "jobs_today": 0,
        "max_jobs": 4,
        "efficiency_rating": 97,
        "years_experience": 15,
    },
    "TECH-204": {
        "name": "Sarah Johansson",
        "certifications": ["pipeline_inspection", "welding_api1104", "hazmat"],
        "zone": "Northeast",
        "status": "available",
        "current_location": "Scranton, PA",
        "jobs_today": 1,
        "max_jobs": 4,
        "efficiency_rating": 88,
        "years_experience": 6,
    },
    "TECH-205": {
        "name": "Marcus Thompson",
        "certifications": ["electrical_high_voltage", "transformer_maintenance", "scada_systems"],
        "zone": "Central",
        "status": "on_break",
        "current_location": "Denver, CO",
        "jobs_today": 2,
        "max_jobs": 4,
        "efficiency_rating": 92,
        "years_experience": 10,
    },
}

SERVICE_REQUESTS = {
    "SR-4001": {
        "title": "Transformer oil leak - Ridgeline Substation",
        "priority": "high",
        "type": "corrective",
        "required_certs": ["transformer_maintenance", "electrical_high_voltage"],
        "zone": "Central",
        "location": "Moffat County, CO",
        "equipment": "Substation Transformer B-12",
        "estimated_hours": 6,
        "status": "unassigned",
    },
    "SR-4002": {
        "title": "Quarterly turbine blade inspection - Sweetwater",
        "priority": "medium",
        "type": "preventive",
        "required_certs": ["wind_turbine"],
        "zone": "Central",
        "location": "Nolan County, TX",
        "equipment": "Wind Turbine Alpha-7",
        "estimated_hours": 4,
        "status": "assigned",
    },
    "SR-4003": {
        "title": "Gas turbine fuel nozzle replacement",
        "priority": "high",
        "type": "corrective",
        "required_certs": ["gas_turbine", "combustion_systems"],
        "zone": "West",
        "location": "Sacramento, CA",
        "equipment": "Gas Turbine GT-3A",
        "estimated_hours": 8,
        "status": "unassigned",
    },
    "SR-4004": {
        "title": "Pipeline cathodic protection survey",
        "priority": "medium",
        "type": "preventive",
        "required_certs": ["pipeline_inspection"],
        "zone": "Northeast",
        "location": "Lackawanna County, PA",
        "equipment": "Gas Pipeline Segment NE-14",
        "estimated_hours": 5,
        "status": "unassigned",
    },
    "SR-4005": {
        "title": "Emergency: SCADA communication failure",
        "priority": "critical",
        "type": "emergency",
        "required_certs": ["scada_systems", "electrical_high_voltage"],
        "zone": "Central",
        "location": "Denver, CO",
        "equipment": "Ridgeline Substation SCADA",
        "estimated_hours": 3,
        "status": "unassigned",
    },
}

GEOGRAPHIC_ZONES = {
    "West": {"states": ["CA", "NV", "OR", "WA"], "technicians": 2, "open_requests": 1},
    "Central": {"states": ["TX", "CO", "OK", "KS", "NM"], "technicians": 2, "open_requests": 3},
    "Northeast": {"states": ["PA", "NY", "NJ", "CT", "MA"], "technicians": 1, "open_requests": 1},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _selected_requests(zone=None, service_request_id=None):
    selected = SERVICE_REQUESTS
    if zone:
        selected = {sid: request for sid, request in selected.items() if request["zone"].casefold() == zone.casefold()}
    if service_request_id:
        selected = {sid: request for sid, request in selected.items() if sid == service_request_id}
    return selected


def _dispatch_dashboard(zone=None, service_request_id=None):
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    requests = []
    selected = _selected_requests(zone, service_request_id)
    for sid, sr in selected.items():
        requests.append({
            "id": sid, "title": sr["title"], "priority": sr["priority"],
            "type": sr["type"], "zone": sr["zone"], "location": sr["location"],
            "status": sr["status"], "estimated_hours": sr["estimated_hours"],
        })
    requests.sort(key=lambda x: priority_order.get(x["priority"], 9))
    available = sum(
        1 for t in TECHNICIANS.values()
        if t["status"] == "available" and (not zone or t["zone"].casefold() == zone.casefold())
    )
    unassigned = sum(1 for sr in selected.values() if sr["status"] == "unassigned")
    return {"requests": requests, "available_techs": available, "unassigned_requests": unassigned,
            "total_requests": len(requests)}


def _route_optimization(zone_filter=None):
    routes = []
    for zone_name, zone in GEOGRAPHIC_ZONES.items():
        if zone_filter and zone_name.casefold() != zone_filter.casefold():
            continue
        zone_techs = [t for t in TECHNICIANS.values() if t["zone"] == zone_name]
        zone_reqs = [sr for sr in SERVICE_REQUESTS.values() if sr["zone"] == zone_name]
        total_hrs = sum(sr["estimated_hours"] for sr in zone_reqs)
        tech_capacity = sum(t["max_jobs"] - t["jobs_today"] for t in zone_techs)
        routes.append({
            "zone": zone_name, "states": zone["states"],
            "technicians": len(zone_techs), "open_requests": len(zone_reqs),
            "total_hours": total_hrs, "remaining_capacity": tech_capacity,
            "utilization_pct": round((1 - tech_capacity / (len(zone_techs) * 4)) * 100, 1) if zone_techs else 0,
        })
    return {"routes": routes}


def _technician_assignment(zone=None, service_request_id=None):
    assignments = []
    for sid, sr in _selected_requests(zone, service_request_id).items():
        if sr["status"] != "unassigned":
            continue
        candidates = []
        for tid, t in TECHNICIANS.items():
            has_certs = all(c in t["certifications"] for c in sr["required_certs"])
            in_zone = t["zone"] == sr["zone"]
            available = t["status"] in ("available", "on_break")
            has_capacity = t["jobs_today"] < t["max_jobs"]
            if has_certs and has_capacity:
                candidates.append({
                    "tech_id": tid, "name": t["name"],
                    "in_zone": in_zone, "status": t["status"],
                    "efficiency": t["efficiency_rating"],
                    "score": t["efficiency_rating"] + (10 if in_zone else 0) + (5 if available else 0),
                })
        candidates.sort(key=lambda x: x["score"], reverse=True)
        assignments.append({
            "request_id": sid, "title": sr["title"], "priority": sr["priority"],
            "required_certs": sr["required_certs"],
            "best_candidate": candidates[0] if candidates else None,
            "total_candidates": len(candidates),
        })
    return {"assignments": assignments}


def _emergency_response(zone=None, service_request_id=None):
    emergencies = [
        sr for sr in _selected_requests(zone, service_request_id).values()
        if sr["type"] == "emergency" or sr["priority"] == "critical"
    ]
    response_plan = []
    for em in emergencies:
        eligible = []
        for tid, t in TECHNICIANS.items():
            if all(c in t["certifications"] for c in em["required_certs"]):
                eligible.append({"id": tid, "name": t["name"], "status": t["status"], "location": t["current_location"]})
        response_plan.append({
            "title": em["title"], "priority": em["priority"],
            "location": em["location"], "equipment": em["equipment"],
            "estimated_hours": em["estimated_hours"],
            "eligible_responders": eligible,
        })
    return {"emergencies": response_plan, "total": len(response_plan)}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class FieldServiceDispatchAgent(BasicAgent):
    """Field service dispatch and technician management agent."""

    def __init__(self):
        self.name = "FieldServiceDispatchAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "dispatch_dashboard",
                            "route_optimization",
                            "technician_assignment",
                            "emergency_response",
                        ],
                        "description": "Choose dispatch_dashboard for request triage, route_optimization for zone capacity, technician_assignment for a non-binding skill-match recommendation, or emergency_response for a dispatcher-reviewed response draft.",
                    },
                    "zone": {
                        "type": "string",
                        "description": "Optional geographic zone filter.",
                    },
                    "service_request_id": {
                        "type": "string",
                        "description": "Optional synthetic service request ID such as SR-4005.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "dispatch_dashboard")
        zone = kwargs.get("zone")
        service_request_id = kwargs.get("service_request_id")
        if op == "dispatch_dashboard":
            return self._dispatch_dashboard(zone, service_request_id)
        elif op == "route_optimization":
            return self._route_optimization(zone)
        elif op == "technician_assignment":
            return self._technician_assignment(zone, service_request_id)
        elif op == "emergency_response":
            return self._emergency_response(zone, service_request_id)
        return f"**Error:** Unknown operation `{op}`."

    def _dispatch_dashboard(self, zone=None, service_request_id=None) -> str:
        data = _dispatch_dashboard(zone, service_request_id)
        lines = [
            "# Field Service Dispatch Dashboard",
            "",
            f"**Total Requests:** {data['total_requests']} | "
            f"**Unassigned:** {data['unassigned_requests']} | "
            f"**Available Techs:** {data['available_techs']}",
            "",
            "| Priority | Request | Type | Zone | Location | Hours | Status |",
            "|----------|---------|------|------|----------|-------|--------|",
        ]
        for r in data["requests"]:
            lines.append(
                f"| {r['priority'].upper()} | {r['title']} | {r['type']} "
                f"| {r['zone']} | {r['location']} | {r['estimated_hours']}h | {r['status']} |"
            )
        lines.append("")
        lines.append("> Read-only synthetic dashboard. No job, crew, route, customer message, or inventory record was changed.")
        return "\n".join(lines)

    def _route_optimization(self, zone=None) -> str:
        data = _route_optimization(zone)
        lines = [
            "# Route Optimization by Zone",
            "",
            "| Zone | States | Technicians | Open Requests | Total Hours | Capacity | Utilization |",
            "|------|--------|------------|---------------|-------------|----------|-------------|",
        ]
        for r in data["routes"]:
            lines.append(
                f"| {r['zone']} | {', '.join(r['states'])} | {r['technicians']} "
                f"| {r['open_requests']} | {r['total_hours']}h | {r['remaining_capacity']} slots | {r['utilization_pct']}% |"
            )
        lines.append("")
        lines.append("> Capacity comparison only. A dispatcher must validate travel, safety, labor, and SLA constraints before rerouting.")
        return "\n".join(lines)

    def _technician_assignment(self, zone=None, service_request_id=None) -> str:
        data = _technician_assignment(zone, service_request_id)
        lines = ["# Technician Assignment Recommendations", ""]
        for a in data["assignments"]:
            lines.append(f"## {a['request_id']}: {a['title']}")
            lines.append(f"Priority: {a['priority'].upper()} | Required Certs: {', '.join(a['required_certs'])}")
            lines.append(f"Candidates: {a['total_candidates']}")
            if a["best_candidate"]:
                bc = a["best_candidate"]
                lines.append(f"**Candidate for dispatcher review:** {bc['name']} (score: {bc['score']}, efficiency: {bc['efficiency']}%, in-zone: {bc['in_zone']})")
            else:
                lines.append("**No eligible technicians available.**")
            lines.append("")
        lines.append("> Recommendation only. No technician has been assigned, notified, or dispatched.")
        return "\n".join(lines)

    def _emergency_response(self, zone=None, service_request_id=None) -> str:
        data = _emergency_response(zone, service_request_id)
        if data["total"] == 0:
            return "# Emergency Response Draft\n\nNo matching active emergencies in the synthetic snapshot.\n\n> No field action or customer notification has occurred."
        lines = [
            "# Emergency Response Draft",
            "",
            f"**Active Emergencies:** {data['total']}",
            "",
        ]
        for em in data["emergencies"]:
            lines.append(f"## {em['title']}")
            lines.append(f"- Priority: {em['priority'].upper()}")
            lines.append(f"- Location: {em['location']}")
            lines.append(f"- Equipment: {em['equipment']}")
            lines.append(f"- Estimated Hours: {em['estimated_hours']}")
            lines.append("")
            lines.append("**Eligible Responders:**")
            lines.append("")
            lines.append("| Technician | Status | Current Location |")
            lines.append("|-----------|--------|-----------------|")
            for r in em["eligible_responders"]:
                lines.append(f"| {r['name']} | {r['status']} | {r['location']} |")
            lines.append("")
        lines.append("> Dispatcher approval and established emergency procedures are mandatory. No field action or customer notification has occurred.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = FieldServiceDispatchAgent()
    for op in ["dispatch_dashboard", "route_optimization", "technician_assignment", "emergency_response"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
