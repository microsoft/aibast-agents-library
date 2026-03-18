"""
Emission Tracking Agent for Energy sector.

Monitors greenhouse gas emissions across facilities, tracks regulatory
compliance, develops reduction plans, and analyzes carbon offset opportunities.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/emission-tracking",
    "version": "1.0.0",
    "display_name": "Emission Tracking Agent",
    "description": "Monitors GHG emissions by facility, tracks regulatory compliance, develops reduction plans, and analyzes carbon offset opportunities.",
    "author": "AIBAST",
    "tags": ["emissions", "carbon", "compliance", "ghg", "sustainability", "energy"],
    "category": "energy",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

FACILITIES = {
    "FAC-E01": {
        "name": "Riverside Generating Station",
        "location": "Sacramento, CA",
        "type": "natural_gas_plant",
        "capacity_mw": 340,
        "emissions": {
            "scope_1": {"co2_tonnes": 482000, "ch4_tonnes": 1240, "n2o_tonnes": 85},
            "scope_2": {"co2_tonnes": 12400, "ch4_tonnes": 0, "n2o_tonnes": 0},
            "scope_3": {"co2_tonnes": 38500, "ch4_tonnes": 280, "n2o_tonnes": 15},
        },
        "regulatory_threshold_co2": 500000,
        "reduction_target_pct": 15,
        "baseline_year": 2022,
        "baseline_co2": 545000,
    },
    "FAC-E02": {
        "name": "Sweetwater Wind Farm",
        "location": "Nolan County, TX",
        "type": "wind_farm",
        "capacity_mw": 180,
        "emissions": {
            "scope_1": {"co2_tonnes": 0, "ch4_tonnes": 0, "n2o_tonnes": 0},
            "scope_2": {"co2_tonnes": 3200, "ch4_tonnes": 0, "n2o_tonnes": 0},
            "scope_3": {"co2_tonnes": 8400, "ch4_tonnes": 12, "n2o_tonnes": 2},
        },
        "regulatory_threshold_co2": 25000,
        "reduction_target_pct": 5,
        "baseline_year": 2022,
        "baseline_co2": 14200,
    },
    "FAC-E03": {
        "name": "Ridgeline Coal Station",
        "location": "Moffat County, CO",
        "type": "coal_plant",
        "capacity_mw": 520,
        "emissions": {
            "scope_1": {"co2_tonnes": 1420000, "ch4_tonnes": 3800, "n2o_tonnes": 420},
            "scope_2": {"co2_tonnes": 18200, "ch4_tonnes": 0, "n2o_tonnes": 0},
            "scope_3": {"co2_tonnes": 95000, "ch4_tonnes": 1200, "n2o_tonnes": 85},
        },
        "regulatory_threshold_co2": 1500000,
        "reduction_target_pct": 30,
        "baseline_year": 2022,
        "baseline_co2": 1780000,
    },
    "FAC-E04": {
        "name": "Bayshore Refinery",
        "location": "Beaumont, TX",
        "type": "refinery",
        "capacity_mw": 0,
        "emissions": {
            "scope_1": {"co2_tonnes": 890000, "ch4_tonnes": 5600, "n2o_tonnes": 210},
            "scope_2": {"co2_tonnes": 42000, "ch4_tonnes": 0, "n2o_tonnes": 0},
            "scope_3": {"co2_tonnes": 2100000, "ch4_tonnes": 8400, "n2o_tonnes": 320},
        },
        "regulatory_threshold_co2": 1000000,
        "reduction_target_pct": 20,
        "baseline_year": 2022,
        "baseline_co2": 1050000,
    },
}

CARBON_OFFSETS = {
    "OFF-001": {"project": "Appalachian Reforestation", "type": "forestry", "credits_available": 45000, "price_per_tonne": 18.50, "vintage": 2025, "verified_by": "Verra VCS"},
    "OFF-002": {"project": "Texas Wind REC Bundle", "type": "renewable_energy", "credits_available": 120000, "price_per_tonne": 12.75, "vintage": 2026, "verified_by": "Green-e"},
    "OFF-003": {"project": "Montana Methane Capture", "type": "methane_capture", "credits_available": 28000, "price_per_tonne": 24.00, "vintage": 2025, "verified_by": "ACR"},
    "OFF-004": {"project": "Iowa Agricultural Soil Carbon", "type": "soil_carbon", "credits_available": 35000, "price_per_tonne": 22.00, "vintage": 2026, "verified_by": "Gold Standard"},
}

REGULATIONS = {
    "EPA_GHGRP": {"name": "EPA GHG Reporting Program", "threshold_co2": 25000, "deadline": "2026-03-31"},
    "CA_CAPANDTRADE": {"name": "California Cap-and-Trade", "threshold_co2": 25000, "deadline": "2026-04-01"},
    "EPA_NSPS": {"name": "EPA New Source Performance Standards", "threshold_co2": 0, "deadline": "2026-06-30"},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _emissions_dashboard():
    dashboard = []
    for fid, f in FACILITIES.items():
        s1 = f["emissions"]["scope_1"]["co2_tonnes"]
        s2 = f["emissions"]["scope_2"]["co2_tonnes"]
        s3 = f["emissions"]["scope_3"]["co2_tonnes"]
        total = s1 + s2 + s3
        dashboard.append({
            "id": fid, "name": f["name"], "type": f["type"],
            "scope_1": s1, "scope_2": s2, "scope_3": s3, "total": total,
            "threshold": f["regulatory_threshold_co2"],
            "pct_of_threshold": round(s1 / f["regulatory_threshold_co2"] * 100, 1) if f["regulatory_threshold_co2"] else 0,
        })
    total_all = sum(d["total"] for d in dashboard)
    return {"facilities": dashboard, "total_emissions": total_all}


def _compliance_status():
    statuses = []
    for fid, f in FACILITIES.items():
        s1 = f["emissions"]["scope_1"]["co2_tonnes"]
        threshold = f["regulatory_threshold_co2"]
        compliant = s1 <= threshold
        gap = s1 - threshold if not compliant else 0
        current_reduction = round((1 - s1 / f["baseline_co2"]) * 100, 1) if f["baseline_co2"] else 0
        statuses.append({
            "id": fid, "name": f["name"],
            "scope_1_co2": s1, "threshold": threshold,
            "compliant": compliant, "gap_tonnes": gap,
            "target_reduction_pct": f["reduction_target_pct"],
            "actual_reduction_pct": current_reduction,
            "on_track": current_reduction >= f["reduction_target_pct"],
        })
    return {"statuses": statuses}


def _reduction_plan():
    plans = []
    for fid, f in FACILITIES.items():
        s1 = f["emissions"]["scope_1"]["co2_tonnes"]
        target = round(f["baseline_co2"] * (1 - f["reduction_target_pct"] / 100))
        remaining = max(0, s1 - target)
        actions = []
        if f["type"] == "coal_plant":
            actions = [
                {"action": "Fuel switching to natural gas", "reduction_tonnes": 400000, "cost_mm": 85.0},
                {"action": "Carbon capture retrofit", "reduction_tonnes": 300000, "cost_mm": 120.0},
                {"action": "Efficiency upgrades", "reduction_tonnes": 50000, "cost_mm": 12.0},
            ]
        elif f["type"] == "natural_gas_plant":
            actions = [
                {"action": "Heat recovery optimization", "reduction_tonnes": 25000, "cost_mm": 4.5},
                {"action": "Turbine efficiency upgrade", "reduction_tonnes": 18000, "cost_mm": 8.0},
                {"action": "Methane leak detection and repair", "reduction_tonnes": 8000, "cost_mm": 1.2},
            ]
        elif f["type"] == "refinery":
            actions = [
                {"action": "Process electrification", "reduction_tonnes": 120000, "cost_mm": 45.0},
                {"action": "Flare gas recovery", "reduction_tonnes": 35000, "cost_mm": 6.0},
                {"action": "Hydrogen integration", "reduction_tonnes": 80000, "cost_mm": 55.0},
            ]
        plans.append({
            "id": fid, "name": f["name"], "current_co2": s1,
            "target_co2": target, "remaining_reduction": remaining,
            "actions": actions,
        })
    return {"plans": plans}


def _carbon_offset_analysis():
    total_gap = 0
    for f in FACILITIES.values():
        s1 = f["emissions"]["scope_1"]["co2_tonnes"]
        target = round(f["baseline_co2"] * (1 - f["reduction_target_pct"] / 100))
        total_gap += max(0, s1 - target)
    offsets = []
    for oid, o in CARBON_OFFSETS.items():
        total_cost = round(o["credits_available"] * o["price_per_tonne"])
        offsets.append({
            "id": oid, "project": o["project"], "type": o["type"],
            "credits": o["credits_available"], "price": o["price_per_tonne"],
            "total_cost": total_cost, "verified_by": o["verified_by"],
        })
    total_credits = sum(o["credits"] for o in offsets)
    total_cost = sum(o["total_cost"] for o in offsets)
    return {"offsets": offsets, "total_credits": total_credits,
            "total_cost": total_cost, "emission_gap": total_gap}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class EmissionTrackingAgent(BasicAgent):
    """GHG emission monitoring and compliance tracking agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/emission-tracking"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "emissions_dashboard",
                            "compliance_status",
                            "reduction_plan",
                            "carbon_offset_analysis",
                        ],
                        "description": "The emission tracking operation to perform.",
                    },
                    "facility_id": {
                        "type": "string",
                        "description": "Optional facility ID to filter results.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "emissions_dashboard")
        if op == "emissions_dashboard":
            return self._emissions_dashboard()
        elif op == "compliance_status":
            return self._compliance_status()
        elif op == "reduction_plan":
            return self._reduction_plan()
        elif op == "carbon_offset_analysis":
            return self._carbon_offset_analysis()
        return f"**Error:** Unknown operation `{op}`."

    def _emissions_dashboard(self) -> str:
        data = _emissions_dashboard()
        lines = [
            "# Emissions Dashboard",
            "",
            f"**Total Portfolio Emissions:** {data['total_emissions']:,} tonnes CO2e",
            "",
            "| Facility | Type | Scope 1 | Scope 2 | Scope 3 | Total | % of Threshold |",
            "|----------|------|---------|---------|---------|-------|---------------|",
        ]
        for f in data["facilities"]:
            lines.append(
                f"| {f['name']} | {f['type']} | {f['scope_1']:,} | {f['scope_2']:,} "
                f"| {f['scope_3']:,} | {f['total']:,} | {f['pct_of_threshold']}% |"
            )
        return "\n".join(lines)

    def _compliance_status(self) -> str:
        data = _compliance_status()
        lines = [
            "# Compliance Status",
            "",
            "| Facility | Scope 1 CO2 | Threshold | Compliant | Gap | Target Reduction | Actual |",
            "|----------|-------------|-----------|-----------|-----|-----------------|--------|",
        ]
        for s in data["statuses"]:
            comp = "YES" if s["compliant"] else "NO"
            track = "On Track" if s["on_track"] else "Behind"
            lines.append(
                f"| {s['name']} | {s['scope_1_co2']:,} | {s['threshold']:,} "
                f"| {comp} | {s['gap_tonnes']:,} | {s['target_reduction_pct']}% | {s['actual_reduction_pct']}% ({track}) |"
            )
        return "\n".join(lines)

    def _reduction_plan(self) -> str:
        data = _reduction_plan()
        lines = ["# Emission Reduction Plans", ""]
        for p in data["plans"]:
            if not p["actions"]:
                continue
            lines.append(f"## {p['name']}")
            lines.append(f"Current: {p['current_co2']:,} tonnes | Target: {p['target_co2']:,} tonnes | Gap: {p['remaining_reduction']:,} tonnes")
            lines.append("")
            lines.append("| Action | Reduction (tonnes) | Cost ($M) |")
            lines.append("|--------|-------------------|----------|")
            for a in p["actions"]:
                lines.append(f"| {a['action']} | {a['reduction_tonnes']:,} | ${a['cost_mm']}M |")
            lines.append("")
        return "\n".join(lines)

    def _carbon_offset_analysis(self) -> str:
        data = _carbon_offset_analysis()
        lines = [
            "# Carbon Offset Analysis",
            "",
            f"**Emission Gap to Cover:** {data['emission_gap']:,} tonnes",
            f"**Total Credits Available:** {data['total_credits']:,} tonnes",
            f"**Total Offset Cost:** ${data['total_cost']:,}",
            "",
            "| Project | Type | Credits | Price/t | Total Cost | Verified By |",
            "|---------|------|---------|---------|-----------|-------------|",
        ]
        for o in data["offsets"]:
            lines.append(
                f"| {o['project']} | {o['type']} | {o['credits']:,} "
                f"| ${o['price']:.2f} | ${o['total_cost']:,} | {o['verified_by']} |"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = EmissionTrackingAgent()
    for op in ["emissions_dashboard", "compliance_status", "reduction_plan", "carbon_offset_analysis"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
