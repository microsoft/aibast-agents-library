"""
Production Line Optimization Agent

Analyzes manufacturing line performance metrics including OEE, station
cycle times, and defect rates. Identifies bottlenecks, recommends
throughput improvements, and generates shift-level production plans
to maximize output while maintaining quality targets.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/production-line-optimization",
    "version": "1.0.0",
    "display_name": "Production Line Optimization Agent",
    "description": "Analyzes production line OEE, identifies bottleneck stations, and generates throughput optimization plans with shift-level scheduling.",
    "author": "AIBAST",
    "tags": ["production", "OEE", "bottleneck", "throughput", "manufacturing"],
    "category": "manufacturing",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

PRODUCTION_LINES = {
    "LINE-A": {
        "name": "Electronics Assembly Line A",
        "product": "Industrial Control Module ICM-400",
        "design_capacity_per_hour": 180,
        "actual_output_per_hour": 142,
        "availability_pct": 87.0,
        "performance_pct": 82.0,
        "quality_pct": 99.4,
    },
    "LINE-B": {
        "name": "Metal Fabrication Line B",
        "product": "Structural Bracket SB-220",
        "design_capacity_per_hour": 300,
        "actual_output_per_hour": 261,
        "availability_pct": 92.0,
        "performance_pct": 94.5,
        "quality_pct": 98.7,
    },
    "LINE-C": {
        "name": "Polymer Molding Line C",
        "product": "Enclosure Housing EH-150",
        "design_capacity_per_hour": 240,
        "actual_output_per_hour": 168,
        "availability_pct": 78.0,
        "performance_pct": 89.7,
        "quality_pct": 97.2,
    },
}

STATIONS = {
    "LINE-A": [
        {"id": "A1", "name": "SMT Placement", "cycle_time_s": 18.5, "takt_time_s": 20.0, "defect_rate_pct": 0.12},
        {"id": "A2", "name": "Reflow Soldering", "cycle_time_s": 22.1, "takt_time_s": 20.0, "defect_rate_pct": 0.08},
        {"id": "A3", "name": "AOI Inspection", "cycle_time_s": 15.0, "takt_time_s": 20.0, "defect_rate_pct": 0.01},
        {"id": "A4", "name": "Through-Hole Insert", "cycle_time_s": 19.8, "takt_time_s": 20.0, "defect_rate_pct": 0.15},
        {"id": "A5", "name": "Functional Test", "cycle_time_s": 25.3, "takt_time_s": 20.0, "defect_rate_pct": 0.04},
        {"id": "A6", "name": "Conformal Coating", "cycle_time_s": 16.2, "takt_time_s": 20.0, "defect_rate_pct": 0.02},
        {"id": "A7", "name": "Final Assembly", "cycle_time_s": 19.0, "takt_time_s": 20.0, "defect_rate_pct": 0.18},
    ],
    "LINE-B": [
        {"id": "B1", "name": "Laser Cutting", "cycle_time_s": 10.8, "takt_time_s": 12.0, "defect_rate_pct": 0.05},
        {"id": "B2", "name": "CNC Bending", "cycle_time_s": 11.4, "takt_time_s": 12.0, "defect_rate_pct": 0.22},
        {"id": "B3", "name": "Robotic Welding", "cycle_time_s": 14.2, "takt_time_s": 12.0, "defect_rate_pct": 0.30},
        {"id": "B4", "name": "Grinding/Deburr", "cycle_time_s": 9.5, "takt_time_s": 12.0, "defect_rate_pct": 0.06},
        {"id": "B5", "name": "Powder Coating", "cycle_time_s": 11.0, "takt_time_s": 12.0, "defect_rate_pct": 0.10},
        {"id": "B6", "name": "QC Measurement", "cycle_time_s": 8.2, "takt_time_s": 12.0, "defect_rate_pct": 0.00},
    ],
    "LINE-C": [
        {"id": "C1", "name": "Material Drying", "cycle_time_s": 12.0, "takt_time_s": 15.0, "defect_rate_pct": 0.02},
        {"id": "C2", "name": "Injection Molding", "cycle_time_s": 18.4, "takt_time_s": 15.0, "defect_rate_pct": 0.45},
        {"id": "C3", "name": "Trim/Deflash", "cycle_time_s": 10.5, "takt_time_s": 15.0, "defect_rate_pct": 0.08},
        {"id": "C4", "name": "Ultrasonic Weld", "cycle_time_s": 13.8, "takt_time_s": 15.0, "defect_rate_pct": 0.12},
        {"id": "C5", "name": "Dimensional Check", "cycle_time_s": 9.0, "takt_time_s": 15.0, "defect_rate_pct": 0.00},
        {"id": "C6", "name": "Packaging", "cycle_time_s": 7.5, "takt_time_s": 15.0, "defect_rate_pct": 0.05},
    ],
}

SHIFT_SCHEDULES = {
    "Day": {"start": "06:00", "end": "14:00", "hours": 8, "operators": 24, "premium": 1.0},
    "Swing": {"start": "14:00", "end": "22:00", "hours": 8, "operators": 22, "premium": 1.0},
    "Night": {"start": "22:00", "end": "06:00", "hours": 8, "operators": 18, "premium": 1.15},
}

DEFECT_CATEGORIES = {
    "LINE-A": {"solder_bridge": 38, "component_shift": 22, "missing_part": 15, "cosmetic": 14, "functional": 11},
    "LINE-B": {"weld_porosity": 42, "dimensional_oor": 28, "surface_scratch": 18, "bend_angle": 12},
    "LINE-C": {"short_shot": 35, "flash": 25, "sink_mark": 20, "weld_line": 12, "warpage": 8},
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _oee(line_id):
    """Calculate OEE for a production line."""
    pl = PRODUCTION_LINES[line_id]
    return round(pl["availability_pct"] * pl["performance_pct"] * pl["quality_pct"] / 10000, 1)


def _bottleneck_station(line_id):
    """Return the station with the longest cycle time (bottleneck)."""
    stations = STATIONS[line_id]
    return max(stations, key=lambda s: s["cycle_time_s"])


def _throughput_gap(line_id):
    """Units per hour lost vs. design capacity."""
    pl = PRODUCTION_LINES[line_id]
    return pl["design_capacity_per_hour"] - pl["actual_output_per_hour"]


def _daily_output(line_id):
    """Estimate daily output across all shifts."""
    pl = PRODUCTION_LINES[line_id]
    total_hours = sum(s["hours"] for s in SHIFT_SCHEDULES.values())
    return pl["actual_output_per_hour"] * total_hours


def _quality_cost_estimate(line_id):
    """Rough annual cost of quality defects for a line (scrap + rework)."""
    pl = PRODUCTION_LINES[line_id]
    defect_rate = (100 - pl["quality_pct"]) / 100
    annual_units = _daily_output(line_id) * 250
    scrap_cost_per_unit = 12.50  # average
    return round(annual_units * defect_rate * scrap_cost_per_unit, 2)


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class ProductionLineOptimizationAgent(BasicAgent):
    """Analyzes production lines for OEE, bottlenecks, and shift planning."""

    def __init__(self):
        self.name = "ProductionLineOptimizationAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "operations": [
                "line_efficiency",
                "bottleneck_analysis",
                "throughput_optimization",
                "shift_planning",
            ],
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "line_efficiency")
        dispatch = {
            "line_efficiency": self._line_efficiency,
            "bottleneck_analysis": self._bottleneck_analysis,
            "throughput_optimization": self._throughput_optimization,
            "shift_planning": self._shift_planning,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)

    # ------------------------------------------------------------------
    def _line_efficiency(self, **kwargs) -> str:
        lines = ["## Production Line Efficiency Report\n"]
        lines.append("| Line | Product | OEE | Availability | Performance | Quality | Actual/Design (uph) |")
        lines.append("|------|---------|-----|-------------|-------------|---------|---------------------|")
        for lid, pl in PRODUCTION_LINES.items():
            oee = _oee(lid)
            flag = " **BELOW TARGET**" if oee < 75 else ""
            lines.append(
                f"| {pl['name']} | {pl['product'][:24]} | {oee}%{flag} | "
                f"{pl['availability_pct']}% | {pl['performance_pct']}% | {pl['quality_pct']}% | "
                f"{pl['actual_output_per_hour']}/{pl['design_capacity_per_hour']} |"
            )

        lines.append("\n### Daily Output Summary\n")
        lines.append("| Line | Output/Day | Gap vs Design | Annual Quality Cost |")
        lines.append("|------|-----------|---------------|---------------------|")
        for lid, pl in PRODUCTION_LINES.items():
            daily = _daily_output(lid)
            gap = _throughput_gap(lid) * 24
            qcost = _quality_cost_estimate(lid)
            lines.append(f"| {pl['name']} | {daily:,} | {gap:,} units lost | ${qcost:,.2f} |")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _bottleneck_analysis(self, **kwargs) -> str:
        lines = ["## Bottleneck Analysis\n"]
        for lid in PRODUCTION_LINES:
            pl = PRODUCTION_LINES[lid]
            bn = _bottleneck_station(lid)
            lines.append(f"### {pl['name']}\n")
            lines.append(f"**Bottleneck station:** {bn['name']} ({bn['id']})")
            lines.append(f"- Cycle time: {bn['cycle_time_s']}s (takt: {bn['takt_time_s']}s)")
            over = round(bn['cycle_time_s'] - bn['takt_time_s'], 1)
            lines.append(f"- Over takt by: {over}s ({round(over/bn['takt_time_s']*100,1)}%)")
            lines.append(f"- Defect rate: {bn['defect_rate_pct']}%\n")

            lines.append("| Station | Cycle (s) | Takt (s) | Delta | Defect % |")
            lines.append("|---------|-----------|----------|-------|----------|")
            for st in STATIONS[lid]:
                delta = round(st["cycle_time_s"] - st["takt_time_s"], 1)
                flag = " **BN**" if st["id"] == bn["id"] else ""
                lines.append(
                    f"| {st['name']}{flag} | {st['cycle_time_s']} | {st['takt_time_s']} | "
                    f"{delta:+.1f} | {st['defect_rate_pct']}% |"
                )
            lines.append("")

            lines.append(f"**Top defect categories ({lid}):**")
            for defect, count in DEFECT_CATEGORIES.get(lid, {}).items():
                lines.append(f"- {defect}: {count}%")
            lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _throughput_optimization(self, **kwargs) -> str:
        lines = ["## Throughput Optimization Recommendations\n"]
        for lid in PRODUCTION_LINES:
            pl = PRODUCTION_LINES[lid]
            bn = _bottleneck_station(lid)
            gap = _throughput_gap(lid)
            lines.append(f"### {pl['name']} (gap: {gap} uph)\n")
            over = bn["cycle_time_s"] - bn["takt_time_s"]

            # Generate specific recommendations based on bottleneck
            lines.append(f"**Option 1 -- Reduce {bn['name']} cycle time**")
            target = round(bn["takt_time_s"] * 0.95, 1)
            lines.append(f"- Current: {bn['cycle_time_s']}s -> Target: {target}s")
            lines.append(f"- Method: Process re-engineering, tooling upgrade")
            gain1 = round(gap * 0.6)
            lines.append(f"- Expected gain: +{gain1} uph\n")

            lines.append(f"**Option 2 -- Parallel station at bottleneck**")
            lines.append(f"- Add second {bn['name']} unit")
            lines.append(f"- Effective cycle time: {round(bn['cycle_time_s']/2, 1)}s")
            gain2 = round(gap * 0.85)
            lines.append(f"- Expected gain: +{gain2} uph")
            lines.append(f"- Investment estimate: $45,000 - $120,000\n")

            lines.append(f"**Option 3 -- Quality improvement**")
            high_defect = max(STATIONS[lid], key=lambda s: s["defect_rate_pct"])
            lines.append(f"- Target station: {high_defect['name']} ({high_defect['defect_rate_pct']}% defect)")
            lines.append(f"- Reduce rework loop time and scrap")
            gain3 = round(gap * 0.2)
            lines.append(f"- Expected gain: +{gain3} uph\n")

            new_oee = round(_oee(lid) * 1.12, 1)
            lines.append(f"**Combined projected OEE:** {new_oee}% (from {_oee(lid)}%)")
            lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _shift_planning(self, **kwargs) -> str:
        lines = ["## Shift Production Plan\n"]
        lines.append("### Shift Schedule\n")
        lines.append("| Shift | Hours | Operators | Premium | Start | End |")
        lines.append("|-------|-------|-----------|---------|-------|-----|")
        for sname, s in SHIFT_SCHEDULES.items():
            lines.append(
                f"| {sname} | {s['hours']} | {s['operators']} | {s['premium']}x | {s['start']} | {s['end']} |"
            )

        lines.append("\n### Planned Output by Line and Shift\n")
        lines.append("| Line | Day Shift | Swing Shift | Night Shift | Daily Total |")
        lines.append("|------|-----------|-------------|-------------|-------------|")
        for lid, pl in PRODUCTION_LINES.items():
            uph = pl["actual_output_per_hour"]
            day_out = uph * SHIFT_SCHEDULES["Day"]["hours"]
            swing_out = uph * SHIFT_SCHEDULES["Swing"]["hours"]
            # Night shift typically runs at 90% efficiency
            night_out = round(uph * SHIFT_SCHEDULES["Night"]["hours"] * 0.9)
            total = day_out + swing_out + night_out
            lines.append(
                f"| {pl['name'][:28]} | {day_out:,} | {swing_out:,} | {night_out:,} | {total:,} |"
            )

        lines.append("\n### Operator Allocation\n")
        total_ops = sum(s["operators"] for s in SHIFT_SCHEDULES.values())
        lines.append(f"- Total operators across shifts: **{total_ops}**")
        lines.append(f"- Lines running: **{len(PRODUCTION_LINES)}**")
        lines.append(f"- Avg operators per line per shift: **{round(total_ops / len(PRODUCTION_LINES) / len(SHIFT_SCHEDULES), 1)}**")

        lines.append("\n### Weekly Capacity Summary\n")
        lines.append("| Line | Weekly Output (5 days) | Weekly Output (6 days) | Weekly Output (7 days) |")
        lines.append("|------|----------------------|----------------------|----------------------|")
        for lid, pl in PRODUCTION_LINES.items():
            d = _daily_output(lid)
            lines.append(f"| {pl['name'][:28]} | {d*5:,} | {d*6:,} | {d*7:,} |")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = ProductionLineOptimizationAgent()
    for op in agent.metadata["operations"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
