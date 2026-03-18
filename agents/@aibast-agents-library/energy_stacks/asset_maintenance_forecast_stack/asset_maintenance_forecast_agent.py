"""
Asset Maintenance Forecast Agent for Energy sector.

Provides predictive maintenance forecasting, asset health monitoring,
budget projections, and work order planning for energy infrastructure
including turbines, transformers, and pipelines.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/asset-maintenance-forecast",
    "version": "1.0.0",
    "display_name": "Asset Maintenance Forecast Agent",
    "description": "Predictive maintenance forecasting, asset health monitoring, budget projections, and work order planning for energy infrastructure.",
    "author": "AIBAST",
    "tags": ["maintenance", "asset-health", "energy", "predictive", "work-orders", "budget"],
    "category": "energy",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

ASSETS = {
    "AST-T001": {
        "name": "Wind Turbine Alpha-7",
        "type": "wind_turbine",
        "location": "Sweetwater Wind Farm, TX",
        "installed_year": 2016,
        "age_years": 10,
        "capacity_mw": 3.2,
        "condition_score": 68,
        "last_major_service": "2025-06-15",
        "operating_hours": 72480,
        "failure_rate_annual_pct": 4.2,
        "maintenance_history": [
            {"date": "2025-06-15", "type": "major", "cost": 48000, "description": "Gearbox bearing replacement"},
            {"date": "2025-11-20", "type": "minor", "cost": 8200, "description": "Blade pitch calibration"},
            {"date": "2026-01-10", "type": "inspection", "cost": 3500, "description": "Annual structural inspection"},
        ],
        "predicted_next_failure": "2026-08-15",
        "replacement_cost": 2400000,
    },
    "AST-X002": {
        "name": "Substation Transformer B-12",
        "type": "transformer",
        "location": "Ridgeline Substation, CO",
        "installed_year": 2008,
        "age_years": 18,
        "capacity_mw": 120.0,
        "condition_score": 42,
        "last_major_service": "2024-09-22",
        "operating_hours": 148920,
        "failure_rate_annual_pct": 8.7,
        "maintenance_history": [
            {"date": "2024-09-22", "type": "major", "cost": 125000, "description": "Oil filtration and bushing replacement"},
            {"date": "2025-04-11", "type": "minor", "cost": 18500, "description": "Cooling fan motor replacement"},
            {"date": "2025-12-05", "type": "inspection", "cost": 6200, "description": "DGA oil analysis - elevated acetylene"},
        ],
        "predicted_next_failure": "2026-05-01",
        "replacement_cost": 4800000,
    },
    "AST-P003": {
        "name": "Gas Pipeline Segment NE-14",
        "type": "pipeline",
        "location": "Northeast Corridor, PA",
        "installed_year": 2012,
        "age_years": 14,
        "capacity_mw": 0,
        "condition_score": 75,
        "last_major_service": "2025-08-30",
        "operating_hours": 0,
        "failure_rate_annual_pct": 1.8,
        "maintenance_history": [
            {"date": "2025-08-30", "type": "major", "cost": 210000, "description": "Corrosion remediation and recoating"},
            {"date": "2025-11-15", "type": "inspection", "cost": 15000, "description": "Inline inspection pig run"},
            {"date": "2026-02-20", "type": "minor", "cost": 9800, "description": "Valve actuator servicing"},
        ],
        "predicted_next_failure": "2027-03-01",
        "replacement_cost": 12000000,
    },
    "AST-T004": {
        "name": "Gas Turbine GT-3A",
        "type": "gas_turbine",
        "location": "Riverside Generating Station, CA",
        "installed_year": 2019,
        "age_years": 7,
        "capacity_mw": 85.0,
        "condition_score": 88,
        "last_major_service": "2025-10-12",
        "operating_hours": 38200,
        "failure_rate_annual_pct": 1.2,
        "maintenance_history": [
            {"date": "2025-10-12", "type": "major", "cost": 340000, "description": "Hot gas path inspection"},
            {"date": "2026-01-28", "type": "minor", "cost": 22000, "description": "Fuel nozzle cleaning"},
        ],
        "predicted_next_failure": "2027-10-01",
        "replacement_cost": 18000000,
    },
}

BUDGET_RATES = {
    "major": {"wind_turbine": 52000, "transformer": 135000, "pipeline": 225000, "gas_turbine": 360000},
    "minor": {"wind_turbine": 9000, "transformer": 20000, "pipeline": 12000, "gas_turbine": 25000},
    "inspection": {"wind_turbine": 4000, "transformer": 7000, "pipeline": 16000, "gas_turbine": 15000},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _maintenance_forecast():
    forecasts = []
    for aid, a in ASSETS.items():
        forecasts.append({
            "id": aid, "name": a["name"], "type": a["type"],
            "condition_score": a["condition_score"],
            "failure_rate_pct": a["failure_rate_annual_pct"],
            "predicted_failure": a["predicted_next_failure"],
            "last_service": a["last_major_service"],
            "location": a["location"],
        })
    forecasts.sort(key=lambda x: x["predicted_failure"])
    return {"forecasts": forecasts}


def _asset_health():
    health = []
    for aid, a in ASSETS.items():
        status = "critical" if a["condition_score"] < 50 else ("warning" if a["condition_score"] < 70 else "good")
        health.append({
            "id": aid, "name": a["name"], "type": a["type"],
            "condition_score": a["condition_score"], "status": status,
            "age_years": a["age_years"], "operating_hours": a["operating_hours"],
            "replacement_cost": a["replacement_cost"],
        })
    health.sort(key=lambda x: x["condition_score"])
    return {"assets": health, "avg_condition": round(sum(a["condition_score"] for a in ASSETS.values()) / len(ASSETS), 1)}


def _budget_projection():
    total = 0
    projections = []
    for aid, a in ASSETS.items():
        atype = a["type"]
        annual = BUDGET_RATES["major"][atype] + BUDGET_RATES["minor"][atype] * 2 + BUDGET_RATES["inspection"][atype]
        if a["condition_score"] < 50:
            annual = round(annual * 1.5)
        total += annual
        projections.append({
            "id": aid, "name": a["name"], "type": atype,
            "annual_budget": annual, "replacement_cost": a["replacement_cost"],
            "condition_score": a["condition_score"],
        })
    projections.sort(key=lambda x: x["annual_budget"], reverse=True)
    return {"projections": projections, "total_annual": total}


def _work_order_plan():
    orders = []
    priority = 1
    for aid, a in sorted(ASSETS.items(), key=lambda x: x[1]["condition_score"]):
        atype = a["type"]
        if a["condition_score"] < 50:
            orders.append({
                "priority": priority, "asset_id": aid, "asset_name": a["name"],
                "work_type": "major", "description": f"Urgent major service - condition score {a['condition_score']}",
                "estimated_cost": BUDGET_RATES["major"][atype],
                "target_date": "2026-Q2",
            })
            priority += 1
        if a["condition_score"] < 70:
            orders.append({
                "priority": priority, "asset_id": aid, "asset_name": a["name"],
                "work_type": "inspection", "description": f"Detailed condition assessment required",
                "estimated_cost": BUDGET_RATES["inspection"][atype],
                "target_date": "2026-Q2",
            })
            priority += 1
        orders.append({
            "priority": priority, "asset_id": aid, "asset_name": a["name"],
            "work_type": "minor", "description": "Scheduled preventive maintenance",
            "estimated_cost": BUDGET_RATES["minor"][atype],
            "target_date": "2026-Q3",
        })
        priority += 1
    return {"work_orders": orders, "total_cost": sum(o["estimated_cost"] for o in orders)}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class AssetMaintenanceForecastAgent(BasicAgent):
    """Predictive maintenance and asset health agent for energy infrastructure."""

    def __init__(self):
        self.name = "@aibast-agents-library/asset-maintenance-forecast"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
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
                        "description": "The maintenance operation to perform.",
                    },
                    "asset_id": {
                        "type": "string",
                        "description": "Optional asset ID to filter results.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "maintenance_forecast")
        if op == "maintenance_forecast":
            return self._maintenance_forecast()
        elif op == "asset_health":
            return self._asset_health()
        elif op == "budget_projection":
            return self._budget_projection()
        elif op == "work_order_plan":
            return self._work_order_plan()
        return f"**Error:** Unknown operation `{op}`."

    def _maintenance_forecast(self) -> str:
        data = _maintenance_forecast()
        lines = [
            "# Maintenance Forecast",
            "",
            "| Asset | Type | Condition | Failure Rate | Predicted Failure | Last Service |",
            "|-------|------|-----------|-------------|-------------------|--------------|",
        ]
        for f in data["forecasts"]:
            lines.append(
                f"| {f['name']} | {f['type']} | {f['condition_score']} "
                f"| {f['failure_rate_pct']}% | {f['predicted_failure']} | {f['last_service']} |"
            )
        lines.append("")
        lines.append("## Action Items")
        lines.append("- Substation Transformer B-12 requires immediate attention (predicted failure Q2 2026).")
        lines.append("- Wind Turbine Alpha-7 approaching maintenance window (predicted failure Q3 2026).")
        return "\n".join(lines)

    def _asset_health(self) -> str:
        data = _asset_health()
        lines = [
            "# Asset Health Dashboard",
            "",
            f"**Average Condition Score:** {data['avg_condition']}",
            "",
            "| Asset | Type | Condition | Status | Age | Operating Hours | Replacement Cost |",
            "|-------|------|-----------|--------|-----|----------------|-----------------|",
        ]
        for a in data["assets"]:
            hrs = f"{a['operating_hours']:,}" if a["operating_hours"] else "N/A"
            lines.append(
                f"| {a['name']} | {a['type']} | {a['condition_score']} "
                f"| {a['status'].upper()} | {a['age_years']}yr | {hrs} | ${a['replacement_cost']:,} |"
            )
        return "\n".join(lines)

    def _budget_projection(self) -> str:
        data = _budget_projection()
        lines = [
            "# Maintenance Budget Projection",
            "",
            f"**Total Annual Budget:** ${data['total_annual']:,}",
            "",
            "| Asset | Type | Condition | Annual Budget | Replacement Cost |",
            "|-------|------|-----------|--------------|-----------------|",
        ]
        for p in data["projections"]:
            lines.append(
                f"| {p['name']} | {p['type']} | {p['condition_score']} "
                f"| ${p['annual_budget']:,} | ${p['replacement_cost']:,} |"
            )
        return "\n".join(lines)

    def _work_order_plan(self) -> str:
        data = _work_order_plan()
        lines = [
            "# Work Order Plan",
            "",
            f"**Total Planned Cost:** ${data['total_cost']:,}",
            "",
            "| Priority | Asset | Work Type | Description | Est. Cost | Target |",
            "|----------|-------|-----------|-------------|----------|--------|",
        ]
        for wo in data["work_orders"]:
            lines.append(
                f"| {wo['priority']} | {wo['asset_name']} | {wo['work_type'].upper()} "
                f"| {wo['description']} | ${wo['estimated_cost']:,} | {wo['target_date']} |"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = AssetMaintenanceForecastAgent()
    for op in ["maintenance_forecast", "asset_health", "budget_projection", "work_order_plan"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
