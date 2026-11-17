"""
Asset Maintenance Forecast Agent for Energy sector.

Provides predictive maintenance forecasting, asset health monitoring,
budget projections, and draft work-order planning for a wind-farm fleet:
risk scores from synthetic IoT telemetry, failure windows, planned versus
emergency repair cost, and a bundled maintenance plan for a low-wind window.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/asset-maintenance-forecast",
    "version": "1.2.0",
    "display_name": "Asset Maintenance Forecast Agent",
    "description": "Analyze a synthetic wind-farm telemetry snapshot for turbine risk, failure forecasting, maintenance budgets, and a draft bundled maintenance plan. Use for reliability and maintenance-planning questions only. The agent never creates work orders, schedules crews, or directs field work; a qualified asset owner must approve any action through future authenticated tools.",
    "author": "AIBAST",
    "tags": ["maintenance", "asset-health", "energy", "predictive", "work-orders", "budget", "wind"],
    "category": "energy",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data (the demo default: one wind farm)
# ---------------------------------------------------------------------------

FLEET = {
    "site": "wind farm",
    "turbines": 45,
    "model": "GE 2.5MW",
    "telemetry": "Azure IoT Hub",
    "other_units_offline": 1,
    "other_offline_note": "Unit 41 in a scheduled blade inspection",
}

# Turbines flagged by the synthetic telemetry model; the other 41 online turbines score below 3.0.
ASSETS = {
    "Unit 12": {
        "risk_score": 8.7,
        "risk_label": "Failure Imminent",
        "failure_mode": "Main bearing end-of-life wear",
        "repair": "bearing",
        "days_to_failure": "18-30",
        "emergency_cost": 227000,
        "labor_cost": 30250,
        "parts_cost": 28000,
        "duration_days": 3,
        "crew": "Crew A",
        "dates": "March 18-20",
    },
    "Unit 23": {
        "risk_score": 6.2,
        "risk_label": "Elevated",
        "failure_mode": "Gearbox oil contamination",
        "repair": "oil",
        "days_to_failure": "45",
        "emergency_cost": 98000,
        "labor_cost": 1500,
        "parts_cost": 5000,
        "duration_days": 2,
        "crew": "Crew A",
        "dates": "March 21-22",
    },
    "Unit 37": {
        "risk_score": 3.8,
        "risk_label": "Watch",
        "failure_mode": "Generator slip ring wear",
        "repair": "slip ring",
        "days_to_failure": "90",
        "emergency_cost": 41000,
        "labor_cost": 1000,
        "parts_cost": 3000,
        "duration_days": 1,
        "crew": "Crew B",
        "dates": "March 22",
    },
}

# Per-mobilization costs: every separate job rents its own crane and pays crew travel.
MOBILIZATION = {
    "crane_per_job": 6000,
    "crew_travel_per_job": 850,
    "bulk_parts_discount_pct": 15,
}

BUNDLE_WINDOW = {
    "dates": "March 18-22",
    "days": 5,
    "forecast": "low-wind forecast",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _selected_assets(asset_id=None):
    """All flagged turbines, or the one named ('Unit 12' or '12'); an unknown name returns none."""
    if not asset_id:
        return ASSETS
    q = str(asset_id).lower().strip()
    if q.isdigit():
        q = "unit " + q
    return {k: v for k, v in ASSETS.items() if k.lower() in q}


def _status(score):
    if score >= 8:
        return "CRITICAL"
    if score >= 5:
        return "WARNING"
    return "WATCH"


def _k(value):
    """$227K / $1.7K style."""
    if value % 1000 == 0:
        return f"${value // 1000}K"
    return f"${value / 1000:.1f}K"


def _planned_cost(unit):
    """Stand-alone planned repair: labor + parts + one crane and one crew mobilization."""
    a = ASSETS[unit]
    return a["labor_cost"] + a["parts_cost"] + MOBILIZATION["crane_per_job"] + MOBILIZATION["crew_travel_per_job"]


def _bundle_numbers():
    m = MOBILIZATION
    jobs = len(ASSETS)
    labor = sum(a["labor_cost"] for a in ASSETS.values())
    parts = sum(a["parts_cost"] for a in ASSETS.values())
    separate = sum(_planned_cost(u) for u in ASSETS)
    crane_saving = (jobs - 1) * m["crane_per_job"]
    travel_saving = (jobs - 1) * m["crew_travel_per_job"]
    parts_saving = parts * m["bulk_parts_discount_pct"] // 100
    bundled = labor + parts - parts_saving + m["crane_per_job"] + m["crew_travel_per_job"]
    savings = separate - bundled
    lead = ASSETS["Unit 12"]
    avoided = lead["emergency_cost"] - _planned_cost("Unit 12")
    total_value = avoided + savings
    roi = round(total_value * 100 / bundled)
    before = round((FLEET["turbines"] - jobs) * 100 / FLEET["turbines"], 1)
    after = round((FLEET["turbines"] - FLEET["other_units_offline"]) * 100 / FLEET["turbines"], 1)
    return {"separate": separate, "bundled": bundled, "savings": savings, "crane": crane_saving,
            "travel": travel_saving, "parts": parts_saving, "avoided": avoided, "total_value": total_value,
            "roi": roi, "before": before, "after": after}


_GATE = ("> Synthetic planning evidence only. Draft approval queue only: no work order, schedule, crew "
         "assignment, or field instruction has been created in Dynamics or any other system.")


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class AssetMaintenanceForecastAgent(BasicAgent):
    """Predictive maintenance and asset health agent for a wind-farm fleet."""

    def __init__(self):
        self.name = "AssetMaintenanceForecastAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"] + " Always call it first for wind farm or turbine analysis: "
                "'I need immediate analysis on our wind farm turbines' uses maintenance_forecast; "
                "'show the bundled maintenance plan' or 'yes, bundle them' uses work_order_plan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "maintenance_forecast",
                            "asset_health",
                            "budget_projection",
                            "work_order_plan",
                        ],
                        "description": (
                            "maintenance_forecast: the default; immediate fleet analysis with the critical "
                            "alert, additional risks and the bundling recommendation. asset_health: condition "
                            "triage by risk score. budget_projection: planned versus emergency repair funding. "
                            "work_order_plan: the bundled maintenance plan for the low-wind window as a draft "
                            "approval queue (cost comparison, savings, ROI, fleet availability)."
                        ),
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "Optional turbine such as 'Unit 12'. Unknown names return an empty result, never invented data.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation") or "maintenance_forecast"
        asset_id = kwargs.get("asset_id")
        if op == "maintenance_forecast":
            return self._maintenance_forecast(asset_id)
        elif op == "asset_health":
            return self._asset_health(asset_id)
        elif op == "budget_projection":
            return self._budget_projection(asset_id)
        elif op == "work_order_plan":
            return self._work_order_plan(asset_id)
        return f"**Error:** Unknown operation `{op}`."

    def _maintenance_forecast(self, asset_id=None) -> str:
        selected = _selected_assets(asset_id)
        lines = [
            "# Maintenance Forecast",
            "",
            f"Analyzing your {FLEET['turbines']} {FLEET['model']} turbines through {FLEET['telemetry']} (synthetic telemetry snapshot).",
            "",
        ]
        if not selected:
            lines.append("No matching synthetic asset was found.")
            lines.append("")
            lines.append(_GATE)
            return "\n".join(lines)
        ranked = sorted(selected.items(), key=lambda x: x[1]["risk_score"], reverse=True)
        unit, lead = ranked[0]
        lines.append(f"## Critical Alert - {unit}")
        lines.append(f"- **Risk Score:** {lead['risk_score']}/10 ({lead['risk_label']})")
        lines.append(f"- **Issue:** {lead['failure_mode']}")
        lines.append(f"- **Timeline:** {lead['days_to_failure']} days to failure")
        lines.append(f"- **Impact:** {_k(lead['emergency_cost'])} emergency cost vs {_k(_planned_cost(unit) // 1000 * 1000)} planned repair")
        if len(ranked) > 1:
            lines.append("")
            lines.append("## Additional Risks")
            for u, a in ranked[1:]:
                lines.append(f"- {u} ({a['risk_score']}/10) - {a['failure_mode']}, {a['days_to_failure']} days")
        if not asset_id:
            b = _bundle_numbers()
            lines.append("")
            lines.append(f"**Recommendation:** Bundle all {len(ASSETS)} units during the {BUNDLE_WINDOW['dates']} low-wind window")
            lines.append(f"- Save {_k(b['savings'] // 1000 * 1000)} on mobilization")
            lines.append(f"- Avoid {_k(lead['emergency_cost'])} catastrophic failure")
            lines.append(f"- Total investment: {_k(b['bundled'] // 1000 * 1000)}")
            lines.append("")
            lines.append("**Next step:** See the detailed bundled maintenance plan?")
        lines.append("")
        lines.append("> Synthetic planning evidence only. Confirm against live telemetry and engineering review before maintenance or field action.")
        return "\n".join(lines)

    def _asset_health(self, asset_id=None) -> str:
        selected = _selected_assets(asset_id)
        lines = [
            "# Asset Health Dashboard",
            "",
            f"**Fleet:** {FLEET['turbines']} {FLEET['model']} turbines; {len(ASSETS)} flagged by the synthetic risk model.",
            "",
            "| Turbine | Risk Score | Status | Failure Mode | Days to Failure |",
            "|---------|-----------|--------|--------------|-----------------|",
        ]
        for u, a in sorted(selected.items(), key=lambda x: x[1]["risk_score"], reverse=True):
            lines.append(f"| {u} | {a['risk_score']}/10 | {_status(a['risk_score'])} | {a['failure_mode']} | {a['days_to_failure']} |")
        if not selected:
            lines.append("| - | - | - | No matching synthetic asset was found. | - |")
        lines.append("")
        lines.append("Status rule: CRITICAL at 8.0 or above, WARNING from 5.0, WATCH below 5.0.")
        lines.append("")
        lines.append("> Advisory condition screening only; it is not a safety determination or authorization to operate.")
        return "\n".join(lines)

    def _budget_projection(self, asset_id=None) -> str:
        selected = _selected_assets(asset_id)
        lines = [
            "# Maintenance Budget Projection",
            "",
            "| Turbine | Planned Repair (stand-alone) | Emergency Cost if It Fails |",
            "|---------|------------------------------|----------------------------|",
        ]
        for u, a in sorted(selected.items(), key=lambda x: x[1]["risk_score"], reverse=True):
            lines.append(f"| {u} | ${_planned_cost(u):,} | ${a['emergency_cost']:,} |")
        if not selected:
            lines.append("| - | No matching synthetic asset was found. | - |")
        if not asset_id:
            b = _bundle_numbers()
            lines.append("")
            lines.append(f"**Reserve (bundled plan):** ${b['bundled']:,} versus ${b['separate']:,} as separate jobs.")
            lines.append(f"**Emergency exposure avoided on Unit 12:** ${b['avoided']:,}.")
        lines.append("")
        lines.append("> Synthetic planning estimate; finance and asset owners must validate and approve any commitment.")
        return "\n".join(lines)

    def _work_order_plan(self, asset_id=None) -> str:
        b = _bundle_numbers()
        work = " + ".join(f"{u} {a['repair']} ({a['duration_days']}d)" for u, a in ASSETS.items())
        lines = [
            f"Bundling saves {_k(b['savings'] // 1000 * 1000)} and maximizes efficiency.",
            "",
            "# Bundled Maintenance Plan",
            "",
            f"**Window:** {BUNDLE_WINDOW['dates']} ({BUNDLE_WINDOW['days']} days, {BUNDLE_WINDOW['forecast']})",
            f"**Work:** {work}",
            "",
            "| Turbine | Work | Crew | Dates |",
            "|---------|------|------|-------|",
        ]
        for u, a in ASSETS.items():
            lines.append(f"| {u} | {a['failure_mode']} repair ({a['duration_days']}d) | {a['crew']} | {a['dates']} |")
        lines += [
            "",
            "## Cost Comparison",
            "",
            "| Approach | Total Cost | Savings |",
            "|----------|-----------|---------|",
            f"| Separate Jobs | ${b['separate']:,} | - |",
            f"| Bundled Job | ${b['bundled']:,} | -${b['savings']:,} |",
            "",
            "## Savings Sources",
            f"- Single crane rental vs {len(ASSETS)} separate: -{_k(b['crane'])}",
            f"- Shared crew travel: -{_k(b['travel'])}",
            f"- Bulk parts discount ({MOBILIZATION['bulk_parts_discount_pct']}%): -{_k(b['parts'])}",
            "",
            "## ROI Summary",
            f"- Investment: ${b['bundled']:,}",
            f"- Avoided failure: ${b['avoided']:,}",
            f"- Bundling savings: ${b['savings']:,}",
            f"- Total value: ${b['total_value']:,}",
            f"- ROI: {b['roi']}%",
            "",
            f"**Outcome:** Fleet availability {b['before']}% -> {b['after']}%",
            "",
            "Ready for the asset owner to approve and schedule in Dynamics.",
            "",
            _GATE,
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = AssetMaintenanceForecastAgent()
    for op in ["maintenance_forecast", "asset_health", "budget_projection", "work_order_plan"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
