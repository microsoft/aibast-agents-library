"""
Production Line Optimization Agent

Analyzes manufacturing line performance metrics including OEE, station
cycle times, and defect rates. Identifies bottlenecks, recommends
throughput improvements, and generates shift-level production plans
to maximize output while maintaining quality targets.

The demo scenario is Production Line 3 (consumer electronics assembly)
preparing for a 40% holiday demand surge: line analysis, optimization
plan, 4-week implementation plan, risk mitigation, financial analysis
and a real-time monitoring plan. All figures are synthetic.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/production-line-optimization",
    "version": "1.2.0",
    "display_name": "Product Line Optimization Agent",
    "description": "Provide intelligent production capacity analysis and optimization planning to boost throughput and efficiency while maintaining quality.",
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
    "LINE-3": {
        "name": "Production Line 3",
        "product": "Consumer electronics assembly",
        "design_capacity_per_hour": 120,
        "actual_output_per_hour": 100,
        "availability_pct": 87.0,
        "performance_pct": 82.0,
        "quality_pct": 99.4,
    },
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
    # Line 3 takt is set by the holiday demand (86,400 s / 3,360 units = 25.7 s).
    "LINE-3": [
        {"id": "3A", "name": "Solder Paste Print", "cycle_time_s": 30.5, "takt_time_s": 25.7, "defect_rate_pct": 0.05},
        {"id": "3B", "name": "SMT Placement Station 3B", "cycle_time_s": 35.3, "takt_time_s": 25.7, "defect_rate_pct": 0.10},
        {"id": "3C", "name": "Reflow Soldering", "cycle_time_s": 31.0, "takt_time_s": 25.7, "defect_rate_pct": 0.08},
        {"id": "3D", "name": "Functional Test", "cycle_time_s": 34.6, "takt_time_s": 25.7, "defect_rate_pct": 0.04},
        {"id": "3E", "name": "Packaging", "cycle_time_s": 33.9, "takt_time_s": 25.7, "defect_rate_pct": 0.02},
    ],
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
    "LINE-3": {"component_shift": 34, "solder_bridge": 28, "tombstoning": 18, "cosmetic": 12, "functional": 8},
    "LINE-A": {"solder_bridge": 38, "component_shift": 22, "missing_part": 15, "cosmetic": 14, "functional": 11},
    "LINE-B": {"weld_porosity": 42, "dimensional_oor": 28, "surface_scratch": 18, "bend_angle": 12},
    "LINE-C": {"short_shot": 35, "flash": 25, "sink_mark": 20, "weld_line": 12, "warpage": 8},
}

# Holiday surge scenario for Production Line 3 (the demo line).
HOLIDAY_SURGE = {
    "line_id": "LINE-3",
    "surge_pct": 40,
    "ramp_weeks": 4,
    "season_days": 45,
    "world_class_oee": 85,
    "bottleneck": "SMT Placement Station 3B",
    "bottleneck_cap_per_day": 2450,
    "second_constraint": "Functional Test",
}

# Optimization options: (name, units/day gain, investment label, one-time $, weekly $, timeline)
OPTIMIZATIONS = [
    ("SMT reprogram", 180, "$5K", 5000, 0, "3 days"),
    ("4th shift overlap", 400, "$18K/week", 0, 18000, "Immediate"),
    ("2nd test station", 200, "$85K", 85000, 0, "Week 1-2"),
    ("Packaging robots (2)", 150, "$240K", 240000, 0, "Week 1-2"),
    ("Preventive maint blitz", 100, "$12K", 12000, 0, "Week 1"),
]

# Ramp milestones: new crew and equipment run below full efficiency until week 4.
IMPLEMENTATION_WEEKS = [
    ("Week 1: Quick Wins", [
        "SMT placement sequence optimization (Engineering: 3 days)",
        "4th shift staffing: Hire 12 operators (recruiting active)",
        "Preventive maintenance blitz: All equipment serviced",
        "Parts staging: $2.3M inventory secured",
    ], 2700),
    ("Week 2: Equipment Installation", [
        "Test station #2 delivery and install",
        "Robot integration team on-site",
        "Operator training: 40 hours (all shifts)",
        "Trial production runs: Quality validation",
    ], 3000),
    ("Week 3: Optimization", [
        "Robots deployed to packaging line",
        "Material flow optimization",
        "Buffer stock positioning",
        "Performance tuning",
    ], 3200),
    ("Week 4: Full Capacity", [
        "System integration complete",
        "Full production testing",
        "Quality systems validated",
        "Go-live: Week 4 end",
    ], None),
]

RISKS = [
    ("Component Supply Chain", [
        ("Concern", "Semiconductor lead times"),
        ("Mitigation", "45-day safety stock secured"),
        ("Backup", "3 alternative suppliers qualified"),
        ("Confidence", "94%"),
    ]),
    ("Labor Availability", [
        ("Concern", "Holiday hiring competition"),
        ("Mitigation", "12 temps hired + 8 backup"),
        ("Training", "Cross-trained existing staff"),
        ("Confidence", "92%"),
    ]),
    ("Quality Maintenance", [
        ("Concern", "Speed vs. quality trade-off"),
        ("Mitigation", "Additional QC station added"),
        ("Monitoring", "Real-time defect tracking"),
        ("Target", "99.4% maintained"),
    ]),
    ("Equipment Reliability", [
        ("Concern", "Increased wear at higher output"),
        ("Mitigation", "Preventive maintenance schedule"),
        ("Backup", "Critical spare parts on-site"),
        ("MTBF target", ">1,200 hours"),
    ]),
]

# Synthetic finance assumptions for the ROI summary.
FINANCE = {
    "contribution_margin_per_unit": 45,
    "production_days_per_week": 5,
}

MONITORING = {
    "dashboards": [
        "Hourly output tracking (target: {hourly} units/hr)",
        "OEE by station (identify bottlenecks)",
        "Quality metrics (real-time defect rate)",
        "Cycle time variance (+/-5% threshold)",
        "Material consumption vs. plan",
    ],
    "alerts": [
        "Output <90% target: Supervisor notification",
        "Quality <99%: QC immediate review",
        "Equipment anomaly: Predictive maint alert",
        "Material shortage warning: 4-hour buffer",
    ],
    "standups": [
        "Output vs. target", "Bottleneck identification", "Quality issues",
        "Labor efficiency", "Next-day planning",
    ],
}

_NOTE = ("Synthetic figures for demonstration; this is a recommendation only. No hiring, purchase, "
         "schedule change or equipment order is executed by this agent.")


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
    """Daily output across all shifts (the one figure used everywhere)."""
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


def _surge():
    """Baseline, target and plan result for Production Line 3 (fixed 40% holiday scenario)."""
    pct = HOLIDAY_SURGE["surge_pct"]
    baseline = _daily_output(HOLIDAY_SURGE["line_id"])
    target = round(baseline * (100 + pct) / 100)
    gain = sum(o[1] for o in OPTIMIZATIONS)
    after = baseline + gain
    return {
        "pct": pct, "baseline": baseline, "target": target, "gain": gain, "after": after,
        "margin": round(after * 100 / target), "hourly": round(target / 24),
        "season_units": target * HOLIDAY_SURGE["season_days"],
    }


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "line_efficiency",
    "bottleneck_analysis",
    "throughput_optimization",
    "shift_planning",
    "line_analysis",
    "optimization_plan",
    "implementation_plan",
    "risk_mitigation",
    "financial_analysis",
    "monitoring_plan",
]


class ProductionLineOptimizationAgent(BasicAgent):
    """Analyzes production lines for OEE, bottlenecks, surge plans and shift planning."""

    def __init__(self):
        self.name = "ProductionLineOptimizationAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "The manufacturing production-line performance agent. Use this for questions "
                "about Production Line 3 and its holiday demand surge plan, and about which line "
                "needs attention, OEE, availability, performance, quality, output, bottlenecks, "
                "improvement options, implementation, risks, ROI, monitoring or shift plans. "
                "The demo line is Production Line 3 (consumer electronics assembly, 2,400 "
                "units/day, 40% holiday surge). The guided Line 3 sequence is: line_analysis for "
                "'analyze production line 3 performance and optimize for the holiday surge'; "
                "optimization_plan for 'show the optimization plan'; implementation_plan for "
                "'show implementation details'; risk_mitigation for 'show risk mitigation'; "
                "financial_analysis for 'show financial analysis' or ROI; monitoring_plan for "
                "'show monitoring plan'. Plant-wide views across all four synthetic lines "
                "(Production Line 3, Electronics Assembly Line A, Metal Fabrication Line B, "
                "Polymer Molding Line C): line_efficiency for 'which line needs attention today'; "
                "bottleneck_analysis for the constraining station on each line; "
                "throughput_optimization for generic per-line options; shift_planning for day, "
                "swing, and night production planning."
            ),
            "operations": list(_OPERATIONS),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "Production Line 3 holiday-surge sequence: line_analysis (analyze Line 3 "
                            "performance, OEE, surge target and primary bottleneck); optimization_plan "
                            "(show the optimization plan: bottleneck solutions table, total gain, "
                            "safety margin); implementation_plan (implementation details, 4-week plan); "
                            "risk_mitigation (risk mitigation strategy); financial_analysis (financial "
                            "analysis, ROI, payback); monitoring_plan (real-time monitoring plan, alert "
                            "thresholds, success metrics). Plant-wide, every line: line_efficiency "
                            "(which line needs attention today); bottleneck_analysis (bottleneck on each "
                            "line); throughput_optimization (per-line options with quality tradeoffs); "
                            "shift_planning (day, swing, and night shift plan)."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "line_analysis")
        dispatch = {
            "line_efficiency": self._line_efficiency,
            "bottleneck_analysis": self._bottleneck_analysis,
            "throughput_optimization": self._throughput_optimization,
            "shift_planning": self._shift_planning,
            "line_analysis": self._line_analysis,
            "optimization_plan": self._optimization_plan,
            "implementation_plan": self._implementation_plan,
            "risk_mitigation": self._risk_mitigation,
            "financial_analysis": self._financial_analysis,
            "monitoring_plan": self._monitoring_plan,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)

    # ------------------------------------------------------------------
    def _line_analysis(self, **kwargs) -> str:
        s = _surge()
        lid = HOLIDAY_SURGE["line_id"]
        pl = PRODUCTION_LINES[lid]
        return (
            f"## Production Line 3 Analysis: {s['pct']:g}% Holiday Surge\n\n"
            f"**Current Performance:**\n"
            f"- Line: {pl['product']}\n"
            f"- Output: {s['baseline']:,} units/day\n"
            f"- OEE: {round(_oee(lid))}% (world-class: {HOLIDAY_SURGE['world_class_oee']}%)\n"
            f"- Availability: {pl['availability_pct']:g}% | Performance: {pl['performance_pct']:g}% "
            f"| Quality: {pl['quality_pct']:g}%\n\n"
            f"**Holiday Requirement:**\n"
            f"- Target: {s['target']:,} units/day ({s['pct']:g}% increase)\n"
            f"- Timeline: {HOLIDAY_SURGE['ramp_weeks']} weeks to ramp\n"
            f"- Production days: {HOLIDAY_SURGE['season_days']} days (holiday season)\n\n"
            f"**Primary Bottleneck:** {HOLIDAY_SURGE['bottleneck']} (limiting to "
            f"{HOLIDAY_SURGE['bottleneck_cap_per_day']:,} units/day); second constraint: "
            f"{HOLIDAY_SURGE['second_constraint']}.\n\n"
            f"Source: [MES + IoT Sensors + OEE Tracking] (synthetic)\n\n"
            f"Shall I show the optimization plan?"
        )

    # ------------------------------------------------------------------
    def _optimization_plan(self, **kwargs) -> str:
        s = _surge()
        rows = "\n".join(
            f"| {name} | +{gain} units/day | {label} | {timeline} |"
            for name, gain, label, _one, _wk, timeline in OPTIMIZATIONS
        )
        return (
            f"## Production Optimization Plan: Production Line 3\n\n"
            f"**Bottleneck Solutions:**\n\n"
            f"| Optimization | Output Gain | Investment | Timeline |\n|---|---|---|---|\n{rows}\n\n"
            f"**Total Capacity Gain:** +{s['gain']:,} units/day\n\n"
            f"**Result:**\n"
            f"- Baseline: {s['baseline']:,} units/day\n"
            f"- After optimization: {s['after']:,} units/day\n"
            f"- Target needed: {s['target']:,} units/day\n"
            f"- Safety margin: {s['margin']}% of target\n\n"
            f"Source: [Capacity Analysis + Engineering] (synthetic)\n\n"
            f"{_NOTE}\n\n"
            f"Want to see the implementation details?"
        )

    # ------------------------------------------------------------------
    def _implementation_plan(self, **kwargs) -> str:
        s = _surge()
        parts = [f"## {HOLIDAY_SURGE['ramp_weeks']}-Week Implementation Plan: Production Line 3\n"]
        for title, steps, output in IMPLEMENTATION_WEEKS:
            parts.append(f"**{title}**")
            parts.extend(f"- {step}" for step in steps)
            if output is None:
                parts.append(f"- Expected output: {s['after']:,} units/day (target {s['target']:,})\n")
            else:
                parts.append(f"- Expected output: {output:,} units/day\n")
        parts.append("Weekly outputs are ramp milestones: new crew and equipment run below full "
                     "efficiency until week 4.\n")
        parts.append("Source: [Project Plan + Operations] (synthetic)\n")
        parts.append(_NOTE + "\n")
        parts.append("Shall I show the risk mitigation?")
        return "\n".join(parts)

    # ------------------------------------------------------------------
    def _risk_mitigation(self, **kwargs) -> str:
        parts = ["## Risk Mitigation Strategy: Production Line 3\n"]
        for i, (title, items) in enumerate(RISKS, 1):
            parts.append(f"**Risk {i}: {title}**")
            parts.extend(f"- {k}: {v}" for k, v in items)
            parts.append("")
        parts.append("Source: [Risk Assessment + Historical Data] (synthetic)\n")
        parts.append("Want to see the financial analysis?")
        return "\n".join(parts)

    # ------------------------------------------------------------------
    def _financial_analysis(self, **kwargs) -> str:
        s = _surge()
        days = HOLIDAY_SURGE["season_days"]
        weeks = days / FINANCE["production_days_per_week"]
        one_time = sum(o[3] for o in OPTIMIZATIONS)
        weekly = sum(o[4] for o in OPTIMIZATIONS)
        running = round(weekly * weeks)
        total = one_time + running
        extra_per_day = s["target"] - s["baseline"]
        extra_units = extra_per_day * days
        margin = FINANCE["contribution_margin_per_unit"]
        benefit = extra_units * margin
        net = benefit - total
        roi = round(net * 100 / total)
        payback = round(total / (extra_per_day * margin), 1)
        rows = "\n".join(
            f"| {name} | {label} |" for name, _g, label, _one, _wk, _t in OPTIMIZATIONS
        )
        return (
            f"## Financial Analysis: Production Line 3 Holiday Plan\n\n"
            f"| Investment | Cost |\n|---|---|\n{rows}\n\n"
            f"- One-time investment: ${one_time:,}\n"
            f"- 4th shift overlap: ${weekly:,}/week x {weeks:g} weeks ({days} production days) = ${running:,}\n"
            f"- **Total investment: ${total:,}**\n\n"
            f"**Return (holiday season):**\n"
            f"- Incremental output: {extra_per_day:,} units/day x {days} days = {extra_units:,} units\n"
            f"- Contribution margin: ${margin}/unit (synthetic)\n"
            f"- Incremental contribution: ${benefit:,}\n"
            f"- Net benefit: ${net:,}\n"
            f"- **ROI: {roi}%**  |  Payback: {payback:g} production days\n\n"
            f"Parts staging ($2.3M inventory) is working capital recovered as units ship, not part "
            f"of the investment.\n\n"
            f"Source: [Finance Model + Capacity Plan] (synthetic)\n\n"
            f"{_NOTE}\n\n"
            f"Shall I show the monitoring plan?"
        )

    # ------------------------------------------------------------------
    def _monitoring_plan(self, **kwargs) -> str:
        s = _surge()
        dash = "\n".join("- " + d.format(hourly=s["hourly"]) for d in MONITORING["dashboards"])
        alerts = "\n".join("- " + a for a in MONITORING["alerts"])
        stand = "\n".join("- " + a for a in MONITORING["standups"])
        return (
            f"## Real-Time Performance Monitoring: Production Line 3\n\n"
            f"**Production Dashboards:**\n{dash}\n\n"
            f"**Alert Thresholds:**\n{alerts}\n\n"
            f"**Daily Stand-ups:**\n{stand}\n\n"
            f"**Success Metrics (Holiday Season):**\n"
            f"- Units produced: {s['season_units']:,} target ({HOLIDAY_SURGE['season_days']} days)\n"
            f"- Daily output: {s['target']:,} units/day ({s['hourly']} units/hr)\n"
            f"- Quality: 99.4% maintained\n"
            f"- OEE: from {round(_oee(HOLIDAY_SURGE['line_id']))}% toward {HOLIDAY_SURGE['world_class_oee']}% world-class\n\n"
            f"Source: [MES + IoT Sensors + OEE Tracking] (synthetic)"
        )

    # ------------------------------------------------------------------
    def _line_efficiency(self, **kwargs) -> str:
        lines = ["## Production Line Efficiency Report\n"]
        lines.append("| Line | Product | OEE | Availability | Performance | Quality | Actual/Design (uph) |")
        lines.append("|------|---------|-----|-------------|-------------|---------|---------------------|")
        for lid, pl in PRODUCTION_LINES.items():
            oee = _oee(lid)
            flag = " **BELOW TARGET**" if oee < 75 else ""
            lines.append(
                f"| {pl['name']} | {pl['product'][:30]} | {oee}%{flag} | "
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

            # Projected OEE follows the performance recovered by option 1, capped at world-class.
            pl_perf = min(100.0, pl["performance_pct"] * (pl["actual_output_per_hour"] + gain1)
                          / pl["actual_output_per_hour"])
            cap = max(85.0, _oee(lid))
            new_oee = min(cap, round(pl["availability_pct"] * pl_perf * pl["quality_pct"] / 10000, 1))
            lines.append(f"**Projected OEE after option 1:** {new_oee}% (from {_oee(lid)}%, capped at {cap}%)")
            lines.append("")
        lines.append("For the Production Line 3 holiday surge plan with costs and timelines, ask for the optimization plan.")
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
            night_out = uph * SHIFT_SCHEDULES["Night"]["hours"]
            total = day_out + swing_out + night_out
            lines.append(
                f"| {pl['name'][:28]} | {day_out:,} | {swing_out:,} | {night_out:,} | {total:,} |"
            )

        lines.append("\n### Operator Allocation\n")
        total_ops = sum(s["operators"] for s in SHIFT_SCHEDULES.values())
        lines.append(f"- Total operators across shifts: **{total_ops}**")
        lines.append(f"- Lines running: **{len(PRODUCTION_LINES)}**")
        lines.append(f"- Avg operators per line per shift: **{round(total_ops / len(PRODUCTION_LINES) / len(SHIFT_SCHEDULES), 1)}**")
        lines.append("- Holiday surge on Production Line 3: a 4th shift overlap adds 12 operators (+400 units/day)")

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
    for op in ["line_analysis", "optimization_plan", "implementation_plan",
               "risk_mitigation", "financial_analysis", "monitoring_plan"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
