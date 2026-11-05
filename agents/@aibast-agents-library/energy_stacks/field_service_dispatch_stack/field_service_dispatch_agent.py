"""
Field Service Dispatch Agent for Energy and utilities.

Read-only dispatch decision support for a metro electric utility, built on a synthetic snapshot of tomorrow's
12 service jobs and six field crews: a job dashboard, schedule (route) optimization, a crew's skill-matched route,
an emergency outage response draft, live outage status with customer impact, the post-incident review, and the
prevention work orders with the monthly operations report. Every dispatch, reroute, notification and work order
is a draft for a human dispatcher.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/field-service-dispatch",
    "version": "1.2.0",
    "display_name": "Field Service Dispatch Agent",
    "description": "Provide read-only field-service decision support from a synthetic metro-utility snapshot: tomorrow's job dashboard, schedule optimization with travel savings, skill-matched crew routes, an emergency outage response draft, live outage status with customer impact, the post-incident review, and prevention work orders with the monthly operations report. The agent never dispatches or reroutes a crew, changes a job, contacts a customer, stages inventory, creates a work order, or authorizes field action; a human dispatcher must approve work through future authenticated tools.",
    "author": "AIBAST",
    "tags": ["field-service", "dispatch", "routing", "technicians", "emergency", "energy"],
    "category": "energy",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data (fixed demo day: tomorrow's schedule for the metro service area)
# ---------------------------------------------------------------------------

CREWS = {
    "A-1": {"name": "Crew A-1 Marcus Chen", "lead": "Marcus Chen", "years": 12, "level": "Level 3", "truck": "#47",
            "certs": ["high_voltage", "underground_cable", "commercial_electrical"], "status": "scheduled",
            "location": "North service yard", "route_miles": 42},
    "B-2": {"name": "Crew B-2 Priya Nair", "lead": "Priya Nair", "years": 9, "level": "Level 3", "truck": "#22",
            "certs": ["high_voltage", "meter_service"], "status": "scheduled",
            "location": "East service yard", "route_miles": 38},
    "C-3": {"name": "Crew C-3 Diego Alvarez", "lead": "Diego Alvarez", "years": 7, "level": "Level 2", "truck": "#31",
            "certs": ["underground_cable", "high_voltage"], "status": "scheduled",
            "location": "South service yard", "route_miles": 35},
    "D-4": {"name": "Crew D-4 Hannah Brooks", "lead": "Hannah Brooks", "years": 5, "level": "Level 2", "truck": "#18",
            "certs": ["meter_service", "commercial_electrical"], "status": "scheduled",
            "location": "West service yard", "route_miles": 28},
    "E-7": {"name": "Crew E-7 Tom Okafor", "lead": "Tom Okafor", "years": 14, "level": "Level 3", "truck": "#7",
            "certs": ["high_voltage", "substation", "emergency_response"], "status": "standby",
            "location": "Downtown staging area", "route_miles": 0},
    "F-8": {"name": "Crew F-8 Lena Park", "lead": "Lena Park", "years": 10, "level": "Level 3", "truck": "#8",
            "certs": ["high_voltage", "transformer_assessment"], "status": "standby",
            "location": "2.4 mi from downtown", "route_miles": 0},
}

CERT_LABELS = {
    "high_voltage": "High-voltage certification",
    "underground_cable": "Underground cable certified",
    "commercial_electrical": "Commercial electrical license",
    "meter_service": "Meter service qualified",
    "substation": "Substation switching",
    "emergency_response": "Emergency response",
    "transformer_assessment": "Transformer assessment",
}

# Tomorrow's 12 jobs after geographic clustering; fit = skill-match score of the assigned crew for that job.
JOBS = [
    {"id": "J-101", "crew": "A-1", "stop": 1, "time": "7:00 AM", "location": "Oak Ridge Blvd", "job": "Transformer inspect", "hours": 1.5, "cert": "high_voltage", "fit": 100},
    {"id": "J-102", "crew": "A-1", "stop": 2, "time": "9:15 AM", "location": "Riverside Dr", "job": "Underground cable", "hours": 2.0, "cert": "underground_cable", "fit": 100},
    {"id": "J-103", "crew": "A-1", "stop": 3, "time": "12:00 PM", "location": "Commerce Pkwy", "job": "Meter upgrade", "hours": 1.5, "cert": "commercial_electrical", "fit": 100},
    {"id": "J-104", "crew": "A-1", "stop": 4, "time": "2:30 PM", "location": "Industrial Way", "job": "Switchgear maint", "hours": 1.0, "cert": "high_voltage", "fit": 100},
    {"id": "J-105", "crew": "B-2", "stop": 1, "time": "7:30 AM", "location": "Maple Ave", "job": "Pole transformer swap", "hours": 2.5, "cert": "high_voltage", "fit": 100},
    {"id": "J-106", "crew": "B-2", "stop": 2, "time": "10:30 AM", "location": "Harbor St", "job": "Smart meter install", "hours": 1.5, "cert": "meter_service", "fit": 95},
    {"id": "J-107", "crew": "B-2", "stop": 3, "time": "1:00 PM", "location": "Lakeview Dr", "job": "Service drop repair", "hours": 2.0, "cert": "high_voltage", "fit": 90},
    {"id": "J-108", "crew": "C-3", "stop": 1, "time": "7:30 AM", "location": "Elm St vault", "job": "Cable splice", "hours": 2.5, "cert": "underground_cable", "fit": 100},
    {"id": "J-109", "crew": "C-3", "stop": 2, "time": "10:45 AM", "location": "Park Plaza", "job": "Network protector test", "hours": 2.0, "cert": "high_voltage", "fit": 100},
    {"id": "J-110", "crew": "C-3", "stop": 3, "time": "1:30 PM", "location": "Union Sq", "job": "Vault inspection", "hours": 1.5, "cert": "underground_cable", "fit": 100},
    {"id": "J-111", "crew": "D-4", "stop": 1, "time": "8:00 AM", "location": "Westgate Mall", "job": "Commercial meter bank", "hours": 3.0, "cert": "commercial_electrical", "fit": 90},
    {"id": "J-112", "crew": "D-4", "stop": 2, "time": "12:30 PM", "location": "Cedar Ct", "job": "Meter upgrade", "hours": 1.5, "cert": "meter_service", "fit": 90},
]

SCHEDULE_BASELINE = {
    "baseline_jobs": 8,             # jobs the same crews completed per day before clustering
    "baseline_miles": 330,          # unclustered routing for the same 12 jobs
    "baseline_travel_hours": 37.1,
    "optimized_travel_hours": 24.5,
    "fuel_cost_per_mile": 1.00,
    "crew_hour_cost": 131.20,       # overtime-loaded crew hour
    "first_time_fix_projected": 96,
}

OUTAGE = {
    "area": "Downtown",
    "customers": 1247,
    "hospitals": 2,
    "initial_finding": "Primary feeder failure at Substation 7B",
    "target_restoration_hours": 2.5,
    "hospital_status": "Backup generators active (safe)",
    "dispatch": [
        {"crew": "E-7", "from": "Staging area", "eta_min": 8, "assignment": "Primary response"},
        {"crew": "F-8", "from": "2.4 mi away", "eta_min": 11, "assignment": "Assessment"},
        {"crew": "A-1", "from": "Redirected from Industrial Way", "eta_min": 18, "assignment": "Backup power"},
    ],
    "postponed_job": "J-104",
    "segments": [
        {"segment": "Hospitals", "impact_per_hour": 12400, "priority": "Critical", "restore_min": 48},
        {"segment": "Commercial", "impact_per_hour": 8700, "priority": "High", "restore_min": 63},
        {"segment": "Retail", "impact_per_hour": 4200, "priority": "Medium", "restore_min": 93},
        {"segment": "Residential", "impact_per_hour": 840, "priority": "Standard", "restore_min": 93},
    ],
}

LIVE_STATUS = {
    "minutes_since_outage": 16,
    "crews": [
        {"crew": "E-7", "status": "On site, cause confirmed",
         "details": ["Wildlife contact on Phase B insulator", "Rerouting through backup feeder", "ETA restoration: 45 minutes"]},
        {"crew": "F-8", "status": "Downtown assessment complete",
         "details": ["3 transformers checked, all intact", "Safe to re-energize"]},
    ],
}

INCIDENT_REVIEW = {
    "restored_min": 87,
    "metrics": [
        {"metric": "Response time", "target": 15, "actual": 8, "unit": "min"},
        {"metric": "Restoration", "target": 120, "actual": 87, "unit": "min"},
        {"metric": "First-time fix", "target": 95, "actual": 100, "unit": "%"},
    ],
    "value_protected": 37870,
    "response_cost": 4280,
    "prevention": [
        {"horizon": "Immediate (30 days)", "action": "Wildlife mitigation at Substation 7B", "cost": "$8,400", "benefit": "78% risk reduction"},
        {"horizon": "Immediate (30 days)", "action": "Vegetation management expansion", "cost": "$12,200/yr", "benefit": "prevents 3-4 outages"},
        {"horizon": "Long-term (6-12 months)", "action": "IoT sensors on 6 critical feeders", "cost": "$28,500", "benefit": "15-30 min early warning"},
        {"horizon": "Long-term (6-12 months)", "action": "Smart grid automation", "cost": "$340K", "benefit": "payback in 4.6 months"},
    ],
}

WORK_ORDERS = [
    {"id": "WO-2847", "action": "Wildlife mitigation", "owner": "Crew E-7", "due": "next week"},
    {"id": "WO-2848", "action": "Vegetation management", "owner": "Contractor", "due": "15 days"},
    {"id": "WO-2849", "action": "IoT sensor deployment", "owner": "Engineering", "due": "30 days"},
]

MONTHLY_OPS = {
    "emergency_response_min": [8, 14],
    "first_time_fix_pct": [96, 89],
    "csat_pct": 91.8,
    "fuel_cost": [18400, 24700],
    "overtime_savings": 22960,
    "emergencies": [
        {"event": "Downtown feeder outage (Substation 7B)", "revenue_protected": 37870},
        {"event": "Eastside substation breaker trip", "revenue_protected": 98400},
        {"event": "Industrial park cable fault", "revenue_protected": 81330},
        {"event": "Storm damage, north circuits", "revenue_protected": 52600},
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_crew(value):
    """Crew ID or part of the crew/lead name; empty -> A-1 (the demo crew); no match -> None."""
    if not value:
        return "A-1"
    q = str(value).lower().strip()
    for key in CREWS:
        if key.lower() in q or q in CREWS[key]["name"].lower():
            return key
    return None


def _crew_jobs(crew_id):
    return [j for j in JOBS if j["crew"] == crew_id]


def _schedule_summary():
    b = SCHEDULE_BASELINE
    crews = []
    for cid in CREWS:
        jobs = _crew_jobs(cid)
        if not jobs:
            continue
        crews.append({"crew": cid, "jobs": len(jobs), "miles": CREWS[cid]["route_miles"],
                      "skill_match": int(round(sum(j["fit"] for j in jobs) / len(jobs)))})
    miles = sum(c["miles"] for c in crews)
    miles_saved = b["baseline_miles"] - miles
    hours_saved = round(b["baseline_travel_hours"] - b["optimized_travel_hours"], 1)
    travel_cut = int(round(hours_saved / b["baseline_travel_hours"] * 100))
    savings = int(round(miles_saved * b["fuel_cost_per_mile"] + hours_saved * b["crew_hour_cost"]))
    jobs = sum(c["jobs"] for c in crews)
    return {"crews": crews, "miles": miles, "miles_saved": miles_saved, "hours_saved": hours_saved,
            "travel_cut": travel_cut, "savings": savings, "jobs": jobs,
            "jobs_lift": int(round((jobs - b["baseline_jobs"]) / b["baseline_jobs"] * 100))}


def _revenue_at_risk():
    return sum(s["impact_per_hour"] for s in OUTAGE["segments"])


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

OPERATIONS = [
    "dispatch_dashboard", "route_optimization", "technician_assignment", "emergency_response",
    "incident_status", "post_incident_review", "work_orders_report",
]


class FieldServiceDispatchAgent(BasicAgent):
    """Field service dispatch and crew management agent (read-only, synthetic)."""

    def __init__(self):
        self.name = "FieldServiceDispatchAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"] + " Always call this tool for field-service dispatch requests: "
                "optimizing tomorrow's technician schedules or service calls, a crew's detailed route, an urgent "
                "power outage that needs emergency crews, live outage updates and customer impact, the "
                "post-incident review once the outage is resolved, and creating prevention work orders with the "
                "monthly operations report. Short follow-ups ('yes, ...') continue the same workflow. Call it "
                "right away; every operation has demo defaults."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(OPERATIONS),
                        "description": (
                            "dispatch_dashboard for tomorrow's job list by crew and crew status; route_optimization "
                            "to optimize field technician schedules / service calls for tomorrow (travel and cost "
                            "savings); technician_assignment for a crew's detailed route with skill matches (e.g. "
                            "Crew A-1); emergency_response for an urgent outage that needs emergency crews "
                            "dispatched; incident_status for live updates and customer impact during the outage; "
                            "post_incident_review once the outage is resolved (performance, ROI, prevention "
                            "actions); work_orders_report to create the prevention work orders and show the "
                            "monthly operations report."
                        ),
                    },
                    "crew_id": {
                        "type": "string",
                        "description": "Crew ID such as A-1 (Marcus Chen, the default) or a crew lead's name.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "dispatch_dashboard")
        crew_id = _resolve_crew(kwargs.get("crew_id"))
        if crew_id is None:
            return (f"# Unknown Crew\n\nNo synthetic crew matches `{kwargs.get('crew_id')}`; no substitute crew was "
                    f"used. Crews: {', '.join(CREWS)}.\n\n> No job, crew, route, customer message, or inventory "
                    "record was changed.")
        handlers = {
            "dispatch_dashboard": self._dispatch_dashboard,
            "route_optimization": self._route_optimization,
            "technician_assignment": self._technician_assignment,
            "emergency_response": self._emergency_response,
            "incident_status": self._incident_status,
            "post_incident_review": self._post_incident_review,
            "work_orders_report": self._work_orders_report,
        }
        handler = handlers.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`."
        return handler(crew_id)

    def _dispatch_dashboard(self, crew_id) -> str:
        lines = [
            "# Field Service Dispatch Dashboard - Tomorrow",
            "",
            f"**Jobs:** {len(JOBS)} | **Scheduled crews:** {sum(1 for c in CREWS.values() if c['status'] == 'scheduled')} "
            f"| **Standby crews:** {sum(1 for c in CREWS.values() if c['status'] == 'standby')}",
            "",
            "| Job | Crew | Time | Location | Work | Hours |",
            "|-----|------|------|----------|------|-------|",
        ]
        for j in JOBS:
            lines.append(f"| {j['id']} | {j['crew']} | {j['time']} | {j['location']} | {j['job']} | {j['hours']} |")
        lines.append("")
        lines.append("| Crew | Lead | Status | Location |")
        lines.append("|------|------|--------|----------|")
        for cid, c in CREWS.items():
            lines.append(f"| {cid} | {c['lead']} | {c['status']} | {c['location']} |")
        lines.append("")
        lines.append("> Read-only synthetic dashboard. No job, crew, route, customer message, or inventory record was changed.")
        return "\n".join(lines)

    def _route_optimization(self, crew_id) -> str:
        s = _schedule_summary()
        b = SCHEDULE_BASELINE
        lines = [
            "# Optimized Schedule - Tomorrow",
            "",
            f"Geographic clustering across the metro area cuts travel time by {s['travel_cut']}%, saving "
            f"{s['miles_saved']} miles and {s['hours_saved']} billable hours.",
            "",
            "| Crew | Jobs | Miles | Skill Match |",
            "|------|------|-------|-------------|",
        ]
        for c in s["crews"]:
            lines.append(f"| {c['crew']} | {c['jobs']} | {c['miles']} mi | {c['skill_match']}% |")
        lines += [
            "",
            "**Impact:**",
            f"- Efficiency: +{s['jobs_lift']}% jobs ({s['jobs']} vs {b['baseline_jobs']} baseline)",
            f"- First-time fix: {b['first_time_fix_projected']}% projected",
            f"- Cost savings: ${s['savings']:,}/day in fuel and overtime",
            f"- Travel: {b['baseline_miles']} -> {s['miles']} miles; {b['baseline_travel_hours']} -> "
            f"{b['optimized_travel_hours']} travel hours",
            "",
            "Routes are ready to sync to Field Service and the customer SMS confirmations are drafted; both go out "
            "after dispatcher approval.",
            "",
            "Next: see Crew A-1's detailed route.",
            "",
            "> Draft schedule only. A dispatcher must validate travel, safety, labor, and SLA constraints before rerouting.",
        ]
        return "\n".join(lines)

    def _technician_assignment(self, crew_id) -> str:
        c = CREWS[crew_id]
        jobs = _crew_jobs(crew_id)
        if not jobs:
            return (f"# Crew {crew_id} - No Scheduled Route\n\n{c['lead']} is on {c['status']} at {c['location']}; "
                    "no jobs are scheduled for tomorrow.\n\n> Recommendation only. No technician has been assigned, "
                    "notified, or dispatched.")
        lines = [
            f"# Crew {crew_id} Route - {len(jobs)} Stops, Zero Backtracking",
            "",
            f"**Lead:** {c['lead']} ({c['years']} yrs, {c['level']}) | **Truck:** {c['truck']} fully stocked | "
            f"**Route:** {c['route_miles']} miles",
            "",
            "| Time | Location | Job | Duration | Skill Needed |",
            "|------|----------|-----|----------|--------------|",
        ]
        for j in jobs:
            unit = "hr" if j["hours"] == 1 else "hrs"
            lines.append(f"| {j['time']} | {j['location']} | {j['job']} | {j['hours']} {unit} | {CERT_LABELS[j['cert']]} |")
        lines += ["", "**Skills Matched:**"]
        for cert in c["certs"]:
            stops = [str(j["stop"]) for j in jobs if j["cert"] == cert]
            if stops:
                label = "stop" if len(stops) == 1 else "stops"
                lines.append(f"- {CERT_LABELS[cert]} ({label} {', '.join(stops)})")
        lines += [
            "",
            "Parts are pre-staged on the truck; 30-min arrival alerts are drafted for each customer.",
            "",
            "> Recommendation only. No technician has been assigned, notified, or dispatched.",
        ]
        return "\n".join(lines)

    def _emergency_response(self, crew_id) -> str:
        o = OUTAGE
        postponed = next(j for j in JOBS if j["id"] == o["postponed_job"])
        unaffected = len(JOBS) - 1
        lines = [
            "# Emergency Response Draft - Ready for Dispatcher Approval",
            "",
            f"**{o['area']} outage:** {o['customers']:,} customers including {o['hospitals']} hospitals. "
            f"{o['initial_finding']}.",
            "",
            "| Crew | Location | ETA | Assignment |",
            "|------|----------|-----|------------|",
        ]
        for d in o["dispatch"]:
            lines.append(f"| {d['crew']} | {d['from']} | {d['eta_min']} min | {d['assignment']} |")
        lines += [
            "",
            "**Customer Impact:**",
            f"- Hospitals: {o['hospital_status']}",
            f"- Revenue at risk: ${_revenue_at_risk():,}/hour",
            f"- Target restoration: {o['target_restoration_hours']} hours max",
            "",
            "**Adjusted Schedule:**",
            f"- A-1's {postponed['location']} {postponed['job'].lower()} job postponed (customer notice drafted)",
            f"- Remaining {unaffected} jobs unaffected",
            "",
            "> Dispatcher approval and established emergency procedures are mandatory. No crew was dispatched and no "
            "customer notification was sent.",
        ]
        return "\n".join(lines)

    def _incident_status(self, crew_id) -> str:
        st = LIVE_STATUS
        lines = [f"# Live Status - {st['minutes_since_outage']} Minutes Since Outage", ""]
        for c in st["crews"]:
            lines.append(f"**Crew {c['crew']} - {c['status']}**")
            for d in c["details"]:
                lines.append(f"- {d}")
            lines.append("")
        lines += ["**Customer Breakdown:**", "", "| Segment | Impact/Hr | Priority |", "|---------|-----------|----------|"]
        for s in OUTAGE["segments"]:
            lines.append(f"| {s['segment']} | ${s['impact_per_hour']:,} | {s['priority']} |")
        lines.append(f"| **Total** | **${_revenue_at_risk():,}** | |")
        hospitals = next(s for s in OUTAGE["segments"] if s["segment"] == "Hospitals")
        commercial = next(s for s in OUTAGE["segments"] if s["segment"] == "Commercial")
        full = max(s["restore_min"] for s in OUTAGE["segments"])
        lines += [
            "",
            "**Timeline:**",
            f"- Hospitals: {hospitals['restore_min']} min",
            f"- Commercial: {commercial['restore_min']} min",
            f"- Full restoration: {full} min",
            "",
            "> Synthetic status snapshot (not live telemetry). Customer updates are drafts for dispatcher approval.",
        ]
        return "\n".join(lines)

    def _post_incident_review(self, crew_id) -> str:
        r = INCIDENT_REVIEW
        roi = int(round((r["value_protected"] - r["response_cost"]) / r["response_cost"] * 100))
        lines = [
            f"# Outage Resolved - All Customers Restored in {r['restored_min']} Minutes",
            "",
            "| Metric | Target | Actual | Status |",
            "|--------|--------|--------|--------|",
        ]
        for m in r["metrics"]:
            better = m["actual"] >= m["target"] if m["unit"] == "%" else m["actual"] <= m["target"]
            target = f"{m['target']}%" if m["unit"] == "%" else f"<{m['target']} min"
            actual = f"{m['actual']}%" if m["unit"] == "%" else f"{m['actual']} min"
            lines.append(f"| {m['metric']} | {target} | {actual} | {'Beat' if better else 'Missed'} |")
        lines += [
            "",
            f"**Value Protected:** ${r['value_protected']:,} revenue vs ${r['response_cost']:,} response cost = {roi}% ROI",
            "",
            "**Prevention Actions:**",
        ]
        horizon = None
        for p in r["prevention"]:
            if p["horizon"] != horizon:
                horizon = p["horizon"]
                lines.append(f"- {horizon}:")
            lines.append(f"  - {p['action']} ({p['cost']}, {p['benefit']})")
        lines += ["", "Next: generate work orders for the prevention actions.", "",
                  "> Review summary only. No work order, budget, or field action was created or approved."]
        return "\n".join(lines)

    def _work_orders_report(self, crew_id) -> str:
        m = MONTHLY_OPS
        fuel_savings = m["fuel_cost"][1] - m["fuel_cost"][0]
        savings = fuel_savings + m["overtime_savings"]
        protected = sum(e["revenue_protected"] for e in m["emergencies"])
        lines = ["# Prevention Work Orders (Drafts) and Monthly Operations Report", "", "**Work orders ready for you to create:**", ""]
        lines += ["| Work Order | Action | Owner | Due |", "|------------|--------|-------|-----|"]
        for w in WORK_ORDERS:
            lines.append(f"| {w['id']} | {w['action']} | {w['owner']} | {w['due']} |")
        lines += [
            "",
            "**Monthly Operations Summary:**",
            "",
            "| Metric | This Month | Last Month |",
            "|--------|------------|------------|",
            f"| Emergency response | {m['emergency_response_min'][0]} min avg | {m['emergency_response_min'][1]} min |",
            f"| First-time fix | {m['first_time_fix_pct'][0]}% | {m['first_time_fix_pct'][1]}% |",
            f"| Customer satisfaction | {m['csat_pct']}% | - |",
            f"| Fuel costs | ${m['fuel_cost'][0]:,} | ${m['fuel_cost'][1]:,} |",
            "",
            f"**Cost Savings:** ${savings:,}/month through route optimization (fuel ${fuel_savings:,} + overtime "
            f"${m['overtime_savings']:,})",
            f"**Revenue Protected:** ${protected:,} ({len(m['emergencies'])} emergency responses)",
            "",
            "> Work orders are drafts: none was created or assigned. Report figures are synthetic.",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = FieldServiceDispatchAgent()
    for op in OPERATIONS:
        print(f"\n{'=' * 60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
