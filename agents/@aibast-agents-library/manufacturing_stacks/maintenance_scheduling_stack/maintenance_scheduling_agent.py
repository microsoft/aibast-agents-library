"""
Maintenance Scheduling Agent

Manages predictive and preventive maintenance for manufacturing equipment.
Analyzes sensor telemetry, production commitments, crew availability and
parts to propose the lowest-impact maintenance window, a cost-benefit case,
a draft work order, a 30-day calendar and a long-term optimization plan.

Demo scenario (the default): Line 3 injection molding. Machine #7 (IM-2000
series) shows 78% screw wear before a 50,000-unit order of automotive
brackets; the agent proposes a Saturday 6-10 AM overhaul ($3,200 vs $18,500
exposure, ROI 478%) with Team B. Everything is a draft for approval.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/maintenance-scheduling",
    "version": "1.0.0",
    "display_name": "Maintenance Scheduling Agent",
    "description": "Analyze a fixed synthetic maintenance snapshot and prepare review-ready alerts, schedule options, cost cases, draft work orders, calendars and optimization plans. Never control equipment, create or dispatch work orders, assign technicians, send notifications, or reserve parts.",
    "author": "AIBAST",
    "tags": ["maintenance", "predictive", "scheduling", "manufacturing", "IoT"],
    "category": "manufacturing",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

EQUIPMENT = {
    "IM-05": {"name": "Machine #5", "line": "Line 3", "type": "IM-2000 injection molder", "status": "running",
              "weekly_capacity_units": 17500},
    "IM-06": {"name": "Machine #6", "line": "Line 3", "type": "IM-2000 injection molder", "status": "running",
              "weekly_capacity_units": 17500},
    "IM-07": {"name": "Machine #7", "line": "Line 3", "type": "IM-2000 injection molder", "status": "warning",
              "weekly_capacity_units": 17000},
    "IM-08": {"name": "Machine #8", "line": "Line 3", "type": "IM-2000 injection molder", "status": "running",
              "weekly_capacity_units": 17000},
    "IM-09": {"name": "Machine #9", "line": "Line 2", "type": "IM-2000 injection molder", "status": "standby",
              "weekly_capacity_units": 17000},
    "IM-03": {"name": "Machine #3", "line": "Line 1", "type": "IM-2000 injection molder", "status": "running",
              "weekly_capacity_units": 16000},
    "IM-12": {"name": "Machine #12", "line": "Line 2", "type": "IM-2000 injection molder", "status": "watch",
              "weekly_capacity_units": 16000},
    "CV-01": {"name": "Line 1 conveyor", "line": "Line 1", "type": "Conveyor", "status": "running",
              "weekly_capacity_units": 0},
    "CH-02": {"name": "Chiller #2", "line": "Utilities", "type": "Chiller", "status": "running",
              "weekly_capacity_units": 0},
}

SENSOR_READINGS = {
    "IM-07": {"screw_wear_pct": 78, "barrel_temp_variance_c": 3, "time_to_failure_hours": 120,
              "vibration_days_to_threshold": 0},
    "IM-12": {"screw_wear_pct": 41, "barrel_temp_variance_c": 1, "time_to_failure_hours": 0,
              "vibration_days_to_threshold": 30},
    "IM-05": {"screw_wear_pct": 35, "barrel_temp_variance_c": 0, "time_to_failure_hours": 0,
              "vibration_days_to_threshold": 0},
    "IM-06": {"screw_wear_pct": 42, "barrel_temp_variance_c": 1, "time_to_failure_hours": 0,
              "vibration_days_to_threshold": 0},
    "IM-08": {"screw_wear_pct": 29, "barrel_temp_variance_c": 0, "time_to_failure_hours": 0,
              "vibration_days_to_threshold": 0},
}

ALERT_RULES = {"screw_wear_yellow_pct": 75, "screw_wear_red_pct": 90}

REPAIR_PLANS = {
    "IM-07": {
        "work": "Screw and barrel overhaul",
        "overhaul_hours": 4,
        "parts_status": "In stock",
        "safe_run_hours": 48,
        "parts": [
            {"part": "Screw assembly #IM-2000-SC47", "short": "screw assembly", "bin": "12-A", "cost": 1100},
            {"part": "Heating bands (set of 4)", "short": "heating bands", "bin": "18-C", "cost": 300},
        ],
        "parts_transfer": "Friday 4 PM to staging",
        "quality_check": "Sunday 7 AM",
    },
}

PRODUCTION_ORDERS = [
    {"order": "PO-5521", "product": "automotive brackets", "units": 50000, "week": "Next week",
     "line": "Line 3", "ship": "Thursday shipment", "status": "on track"},
]

MAINTENANCE_WINDOWS = [
    {"window": "Wednesday 2 PM - 6 PM", "day": "Wednesday", "day_short": "Wed", "start_hour": 14, "units_lost": 2900, "crew": "Team A"},
    {"window": "Friday 10 PM - Saturday 2 AM", "day": "Friday", "day_short": "Fri", "start_hour": 22, "units_lost": 1400, "crew": "Team C"},
    {"window": "Saturday 6 AM - 10 AM", "day": "Saturday", "day_short": "Sat", "start_hour": 6, "units_lost": 0, "crew": "Team B"},
]

TECHNICIANS = {
    "TECH-301": {"name": "Marcus Chen", "team": "Team B", "role": "Lead", "years": 12,
                 "certifications": ["IM-2000"], "level": "IM-2000 specialist", "available_saturday": True},
    "TECH-302": {"name": "Sarah Park", "team": "Team B", "role": "Tech", "years": 6,
                 "certifications": ["IM-2000"], "level": "Level 3 certified", "available_saturday": True},
    "TECH-201": {"name": "Marcus Rivera", "team": "Team A", "role": "Tech", "years": 9,
                 "certifications": ["Conveyor", "Chiller"], "level": "Level 2 certified", "available_saturday": False},
    "TECH-204": {"name": "Lin Zhao", "team": "Team C", "role": "Tech", "years": 7,
                 "certifications": ["IM-2000", "Chiller"], "level": "Level 2 certified", "available_saturday": False},
}

COST_MODEL = {
    "weekend_rate_per_tech_hour": 225,
    "crew_size": 2,
    "emergency_repair": 12500,
    "delay_days": 2,
    "delay_cost_per_day": 3000,
    "weekend_overtime_avoided": 4200,
    "lifespan_extension": "18-24 months",
}

CALENDAR_30_DAYS = [
    {"date": "Sat (2 days)", "equipment": "Machine #7", "type": "Overhaul", "impact": "Zero"},
    {"date": "Week 2", "equipment": "Line 1 conveyor", "type": "Lubrication", "impact": "2 hrs"},
    {"date": "Week 3", "equipment": "Chiller #2", "type": "Filter swap", "impact": "Minimal"},
    {"date": "Week 4", "equipment": "Machine #3", "type": "Calibration", "impact": "4 hrs"},
]

SYSTEM_CHECKS = [
    {"system": "Hydraulic system", "status": "All nominal"},
    {"system": "Electrical panels", "status": "No issues"},
]

EFFICIENCY = {
    "planned_work_orders": 26,
    "reactive_work_orders": 4,
    "planned_target_pct": 80,
    "mtbf_hours_last_year": 310,
    "mtbf_hours_this_year": 415,
    "annual_maintenance_cost": 96000,
    "annual_units": 1200000,
    "industry_cost_per_unit": 0.14,
}

OPTIMIZATION = {
    "quick_wins": [
        "Extend oil change intervals using synthetic oil (save $8,400/year)",
        "Consolidate Line 2 & 3 maintenance windows (save 12 hrs/month)",
        "Predictive sensors on aging equipment (ROI: 240%)",
    ],
    "investments": [
        "CMMS mobile app: $12K -> save 180 hrs/year",
        "Spare parts optimization: free $47K working capital",
        "Reliability-centered maintenance training: 3 staff, $18K",
    ],
    "downtime_now_pct": 4.2,
    "downtime_target_pct": 2.1,
    "cost_reduction": 124000,
    "availability_now_pct": 94,
    "availability_target_pct": 97,
    "lifespan_gain_years": 2.5,
    "next_steps": "Run pilot on Line 3, scale to all lines by Q3",
}

DRAFT_WORK_ORDER_ID = "WO-2024-3847"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _resolve_machine(query):
    """Equipment ID or name ('#7', 'machine 7', 'IM-07'); default Machine #7; None when nothing matches."""
    if not query:
        return "IM-07"
    q = str(query).lower().strip()
    short = q.replace("machine", "").replace(" ", "")
    if short and short[0] != "#":
        short = "#" + short
    for eq_id, eq in EQUIPMENT.items():
        name = eq["name"].lower()
        if q == eq_id.lower() or q == name or short == name.replace("machine ", ""):
            return eq_id
    return None


def _alert_level(eq_id):
    """Yellow / red from screw wear; watch when vibration trends toward its threshold."""
    s = SENSOR_READINGS.get(eq_id)
    if not s:
        return "Normal"
    if s["screw_wear_pct"] >= ALERT_RULES["screw_wear_red_pct"]:
        return "Red Alert - Stop and repair"
    if s["screw_wear_pct"] >= ALERT_RULES["screw_wear_yellow_pct"]:
        return "Yellow Alert - Preventive maintenance required"
    if s["vibration_days_to_threshold"] > 0:
        return "Monitor"
    return "Normal"


def _capacity_without(eq_id):
    """Line capacity for the week with one machine offline (backups excluded)."""
    line = EQUIPMENT[eq_id]["line"]
    return sum(e["weekly_capacity_units"] for k, e in EQUIPMENT.items()
               if e["line"] == line and k != eq_id)


def _best_window():
    """The maintenance window with the fewest lost units (first one on a tie)."""
    best = MAINTENANCE_WINDOWS[0]
    for w in MAINTENANCE_WINDOWS:
        if w["units_lost"] < best["units_lost"]:
            best = w
    return best


def _crew(team):
    """Technicians of a team certified for IM-2000 and available Saturday; lead first."""
    lead = [t for t in TECHNICIANS.values() if t["team"] == team and "IM-2000" in t["certifications"]
            and t["available_saturday"] and t["role"] == "Lead"]
    techs = [t for t in TECHNICIANS.values() if t["team"] == team and "IM-2000" in t["certifications"]
             and t["available_saturday"] and t["role"] != "Lead"]
    return lead + techs


def _standby():
    """The first machine on standby (the backup)."""
    for e in EQUIPMENT.values():
        if e["status"] == "standby":
            return e
    return None


def _cost_case(eq_id):
    """Preventive cost (labor + parts) against the breakdown exposure; ROI = (exposure - cost) / cost."""
    plan = REPAIR_PLANS[eq_id]
    labor = plan["overhaul_hours"] * COST_MODEL["crew_size"] * COST_MODEL["weekend_rate_per_tech_hour"]
    parts = sum(p["cost"] for p in plan["parts"])
    cost = labor + parts
    delay = COST_MODEL["delay_days"] * COST_MODEL["delay_cost_per_day"]
    exposure = COST_MODEL["emergency_repair"] + delay
    roi = int((exposure - cost) * 100 / cost)
    return {"labor": labor, "parts": parts, "cost": cost, "delay": delay, "exposure": exposure, "roi": roi}


def _pct_change(old, new):
    return int((new - old) * 100 / old + 0.5)


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "schedule_overview",
    "predictive_alerts",
    "work_order_plan",
    "downtime_analysis",
    "work_order_draft",
    "maintenance_calendar",
    "optimization_plan",
]


class MaintenanceSchedulingAgent(BasicAgent):
    """Predictive maintenance scheduling for manufacturing equipment."""

    def __init__(self):
        self.name = "MaintenanceSchedulingAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"]
                + " Always use this tool for Line 3 injection molding maintenance. 'Schedule maintenance for "
                "Line 3 ... machine #7 is showing wear indicators' uses predictive_alerts; 'show me the "
                "schedule' uses work_order_plan; 'cost analysis' uses downtime_analysis; 'schedule everything' "
                "(crew and parts) uses work_order_draft; 'full maintenance calendar' uses maintenance_calendar; "
                "'long-term optimization recommendations' uses optimization_plan. Machine #7 is the default; "
                "call the tool without asking for details."
            ),
            "operations": list(_OPERATIONS),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "schedule_overview: equipment status and crew capacity. "
                            "predictive_alerts: machine condition (wear, temperature, time to failure) with the "
                            "production order context. work_order_plan: the optimized maintenance window, coverage "
                            "machines, backup, crew, parts and capacity check, for planner approval; never dispatch. "
                            "downtime_analysis: cost-benefit (preventive cost vs breakdown exposure, ROI). "
                            "work_order_draft: 'schedule everything' - draft work order, crew, parts bins, transfer "
                            "and production coordination, ready for approval. maintenance_calendar: next-30-day "
                            "calendar, predictive alerts and efficiency KPIs. optimization_plan: long-term quick "
                            "wins, investments and impact projection."
                        ),
                    },
                    "machine": {
                        "type": "string",
                        "description": "Machine number or ID, e.g. '#7' or 'IM-07' (default Machine #7)",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "schedule_overview")
        dispatch = {
            "schedule_overview": self._schedule_overview,
            "predictive_alerts": self._predictive_alerts,
            "work_order_plan": self._work_order_plan,
            "downtime_analysis": self._downtime_analysis,
            "work_order_draft": self._work_order_draft,
            "maintenance_calendar": self._maintenance_calendar,
            "optimization_plan": self._optimization_plan,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        eq_id = _resolve_machine(kwargs.get("machine"))
        if eq_id is None:
            return (f"**Unknown machine** `{kwargs.get('machine')}` in the synthetic snapshot. Known: "
                    + ", ".join(e["name"] for e in EQUIPMENT.values()) + ".")
        return handler(eq_id)

    # ------------------------------------------------------------------
    def _schedule_overview(self, eq_id) -> str:
        lines = ["## Maintenance Schedule Overview\n",
                 "> Synthetic planning snapshot; no equipment was queried or controlled.\n",
                 "### Equipment Status\n",
                 "| ID | Equipment | Line | Type | Status | Alert |",
                 "|----|-----------|------|------|--------|-------|"]
        for k, eq in EQUIPMENT.items():
            lines.append(f"| {k} | {eq['name']} | {eq['line']} | {eq['type']} | {eq['status']} | {_alert_level(k)} |")
        lines += ["\n### Technician Availability\n",
                  "| Technician | Team | Role | Certification | Saturday |",
                  "|------------|------|------|---------------|----------|"]
        for t in TECHNICIANS.values():
            lines.append(f"| {t['name']} | {t['team']} | {t['role']} | {t['level']} | "
                         f"{'Available' if t['available_saturday'] else 'Not available'} |")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _predictive_alerts(self, eq_id) -> str:
        eq = EQUIPMENT[eq_id]
        s = SENSOR_READINGS.get(eq_id)
        order = PRODUCTION_ORDERS[0]
        lines = ["## Predictive Maintenance Alerts\n",
                 "> Synthetic advisory signals only; verify against approved condition-monitoring systems before action.\n",
                 f"Optimizing the maintenance schedule to protect next week's production while addressing "
                 f"{eq['name']}'s condition (wear indicators, production capacity, crew availability).\n",
                 f"### {eq['name']} Status ({eq_id}, {eq['line']})\n",
                 f"- **{_alert_level(eq_id)}**"]
        if s:
            lines.append(f"- Screw wear at {s['screw_wear_pct']}%, barrel temp variance +{s['barrel_temp_variance_c']}°C")
            if s["time_to_failure_hours"]:
                lines.append(f"- Estimated time to failure: {s['time_to_failure_hours']} operating hours")
        plan = REPAIR_PLANS.get(eq_id)
        if plan:
            lines.append(f"- Required maintenance: {plan['overhaul_hours']}-hour overhaul")
            lines.append(f"- Parts needed: {plan['parts_status']}")
        lines += ["\n### Production Context\n",
                  f"- Next week order: {order['units']:,} units ({order['product']})",
                  f"- Current capacity without {eq['name'].replace('Machine ', '')}: {_capacity_without(eq_id):,} units",
                  f"- Delivery: {order['ship']} ({order['status']})",
                  "\n### Other Signals\n"]
        for k in SENSOR_READINGS:
            if k != eq_id and _alert_level(k) != "Normal":
                lines.append(f"- {EQUIPMENT[k]['name']}: {_alert_level(k)} "
                             f"(vibration {SENSOR_READINGS[k]['vibration_days_to_threshold']} days to threshold)")
        lines.append("\nSource: [IoT Sensors + D365 Production + EAM]\n")
        lines.append("Next: shall I create the optimized schedule?")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _work_order_plan(self, eq_id) -> str:
        eq = EQUIPMENT[eq_id]
        plan = REPAIR_PLANS.get(eq_id, REPAIR_PLANS["IM-07"])
        window = _best_window()
        order = PRODUCTION_ORDERS[0]
        cover = [e["name"].replace("Machine ", "") for k, e in EQUIPMENT.items()
                 if e["line"] == eq["line"] and k != eq_id]
        backup = _standby()
        capacity = _capacity_without(eq_id)
        margin = int(capacity * 100 / order["units"])
        parts = " + ".join(p["short"] for p in plan["parts"])
        lines = ["## Proposed Work Order Plan\n",
                 "> Fixed synthetic plan for planner review. No work order is created or dispatched, no technician is assigned, and no part is reserved.\n",
                 "### Optimized Maintenance Schedule\n",
                 f"**Maintenance Window:** {window['window']}\n",
                 "**Why This Works:**",
                 f"- Zero production impact - using machines {', '.join(cover)}" if window["units_lost"] == 0
                 else f"- {window['units_lost']:,} units at risk",
                 f"- Backup ready: {backup['name']} from {backup['line']} on standby",
                 f"- Weekend labor: {window['crew']} certified for IM-2000 series",
                 f"- Parts staged: {parts}",
                 f"\n**Immediate Action:** Run {eq['name']} for the current batch only (safe for "
                 f"{plan['safe_run_hours']} hours), then take it offline.\n",
                 "### Production Continuity\n",
                 "| Metric | Value |", "|--------|-------|",
                 f"| Capacity without {eq['name'].replace('Machine ', '')} | {capacity:,} units |",
                 f"| Required capacity | {order['units']:,} units |",
                 f"| Safety margin | {margin}% |",
                 f"| Quality risk | {'Low' if margin >= 100 else 'High'} |",
                 "\nOther windows considered: "
                 + "; ".join(f"{w['window']} ({w['units_lost']:,} units lost)" for w in MAINTENANCE_WINDOWS if w != window),
                 "\nSource: [D365 Production + EAM]\n",
                 "Next: want to see the cost analysis?"]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _downtime_analysis(self, eq_id) -> str:
        eq_id = eq_id if eq_id in REPAIR_PLANS else "IM-07"
        plan = REPAIR_PLANS[eq_id]
        c = _cost_case(eq_id)
        team = _best_window()["crew"]
        parts = " + ".join(p["short"] for p in plan["parts"])
        lines = ["## Downtime & Cost Analysis\n",
                 "> All probabilities, hours, and costs are synthetic planning estimates.\n",
                 "### Cost-Benefit Analysis\n",
                 "**Preventive Maintenance Investment:**",
                 f"- Labor: ${c['labor']:,} ({plan['overhaul_hours']} hrs, {team} weekend rate)",
                 f"- Parts: ${c['parts']:,} ({parts})",
                 f"- Total: ${c['cost']:,}\n",
                 "**Avoided Breakdown Costs:**",
                 f"- Emergency repair: ${COST_MODEL['emergency_repair']:,}",
                 f"- Production delay: {COST_MODEL['delay_days']} days = ${c['delay']:,}",
                 f"- Total exposure: ${c['exposure']:,}\n",
                 f"**ROI: {c['roi']}%** by avoiding unplanned downtime "
                 f"((${c['exposure']:,} - ${c['cost']:,}) / ${c['cost']:,})\n",
                 f"**Modeled avoided-cost opportunity:** ${c['exposure'] - c['cost']:,}\n",
                 "**Additional Benefits:**",
                 f"- Weekend overtime avoided (${COST_MODEL['weekend_overtime_avoided']:,} saved)",
                 "- Quality maintained (no rushed repairs)",
                 "- Customer confidence (on-time delivery)",
                 f"- Machine lifespan extended {COST_MODEL['lifespan_extension']}",
                 "\nSource: [EAM Cost Data + Historical]\n",
                 "Next: ready to schedule the crew and parts?"]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _work_order_draft(self, eq_id) -> str:
        eq_id = eq_id if eq_id in REPAIR_PLANS else "IM-07"
        eq = EQUIPMENT[eq_id]
        plan = REPAIR_PLANS[eq_id]
        window = _best_window()
        crew = _crew(window["crew"])
        backup = _standby()
        end_hour = window["start_hour"] + plan["overhaul_hours"]
        lines = ["## Maintenance Schedule Ready for Approval\n",
                 "> Synthetic draft only. No work order is created or dispatched, no technician is booked, no notification "
                 "is sent, and no part is reserved until you approve it in the maintenance system.\n",
                 f"**Draft Work Order:** {DRAFT_WORK_ORDER_ID} ({plan['work']}, {eq['name']}, {window['window']})\n",
                 "**Proposed Crew:**"]
        for t in crew:
            label = "Lead" if t["role"] == "Lead" else "Tech"
            detail = f"{t['years']} yrs, {t['level']}" if t["role"] == "Lead" else t["level"]
            lines.append(f"- {label}: {t['name']} ({detail})")
        lines += ["- Notification: Teams message drafted for the crew (not sent)",
                  f"- Availability: {'Both' if len(crew) == 2 else len(crew)} available {window['day']}\n",
                  "**Parts to Reserve (on approval):**"]
        for p in plan["parts"]:
            lines.append(f"- {p['part']}: Bin {p['bin']}")
        lines += [f"- Transfer proposed: {plan['parts_transfer']}\n",
                  "**Production Coordination (drafts):**",
                  f"- Operations notice: {eq['name']} offline {window['day_short']} "
                  f"{window['start_hour']}-{end_hour} AM",
                  f"- Backup plan: {backup['name']} prepped ({backup['line']})",
                  f"- Quality check: {plan['quality_check']}",
                  "\nSource: [EAM + D365 + Teams]\n",
                  "Next: want to see the full maintenance calendar?"]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _maintenance_calendar(self, eq_id) -> str:
        e = EFFICIENCY
        planned = int(e["planned_work_orders"] * 100 / (e["planned_work_orders"] + e["reactive_work_orders"]) + 0.5)
        mtbf = _pct_change(e["mtbf_hours_last_year"], e["mtbf_hours_this_year"])
        per_unit = e["annual_maintenance_cost"] / e["annual_units"]
        lines = ["## Predictive Maintenance Calendar - Next 30 Days\n",
                 "> Synthetic planning calendar; nothing is booked.\n",
                 "### Upcoming Maintenance\n",
                 "| Date | Equipment | Type | Impact |", "|------|-----------|------|--------|"]
        for c in CALENDAR_30_DAYS:
            lines.append(f"| {c['date']} | {c['equipment']} | {c['type']} | {c['impact']} |")
        lines.append("\n### Predictive Alerts\n")
        for k, s in SENSOR_READINGS.items():
            if s["vibration_days_to_threshold"] > 0:
                lines.append(f"- {EQUIPMENT[k]['name']}: Monitor vibration ({s['vibration_days_to_threshold']} days to threshold)")
        for c in SYSTEM_CHECKS:
            lines.append(f"- {c['system']}: {c['status']}")
        lines += ["\n### Maintenance Efficiency\n",
                  f"- Planned vs. reactive: {planned}% planned (target: {e['planned_target_pct']}%)",
                  f"- MTBF improvement: +{mtbf}% year-over-year",
                  f"- Cost per unit: ${per_unit:.2f} (industry avg: ${e['industry_cost_per_unit']:.2f})",
                  "\nSource: [EAM + IoT + Power BI]\n",
                  "Next: want to see long-term optimization recommendations?"]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _optimization_plan(self, eq_id) -> str:
        o = OPTIMIZATION
        halved = " (halved)" if o["downtime_target_pct"] * 2 == o["downtime_now_pct"] else ""
        lines = ["## Strategic Maintenance Optimization\n",
                 "> Synthetic recommendations for leadership review; no purchase or change is made.\n",
                 "### Quick Wins (Next Quarter)\n"]
        lines += [f"- {q}" for q in o["quick_wins"]]
        lines.append("\n### Investment Opportunities\n")
        lines += [f"- {i}" for i in o["investments"]]
        lines += ["\n### Impact Projection\n",
                  f"- Unplanned downtime: {o['downtime_now_pct']}% -> {o['downtime_target_pct']}%{halved}",
                  f"- Maintenance cost: -${o['cost_reduction'] // 1000}K annually",
                  f"- Production availability: {o['availability_now_pct']}% -> {o['availability_target_pct']}%",
                  f"- Equipment lifespan: +{o['lifespan_gain_years']} years average",
                  f"\n**Next Steps:** {o['next_steps']}",
                  "\nSource: [Historical Data + Industry Benchmarks]"]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main — the demo video's turns in order
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = MaintenanceSchedulingAgent()
    for op in ["predictive_alerts", "work_order_plan", "downtime_analysis", "work_order_draft",
               "maintenance_calendar", "optimization_plan", "schedule_overview"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
