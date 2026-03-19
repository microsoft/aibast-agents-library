"""
Maintenance Scheduling Agent

Manages predictive and preventive maintenance for manufacturing equipment.
Analyzes sensor telemetry, failure probability models, and technician
availability to generate optimized work-order schedules that minimize
unplanned downtime while controlling maintenance spend.
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
    "description": "Generates predictive maintenance schedules from equipment telemetry and failure models, optimizing technician assignments to minimize unplanned downtime.",
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
    "EQ-CNC-01": {
        "name": "CNC Milling Center #1",
        "type": "CNC Mill",
        "install_date": "2019-03-14",
        "last_service": "2025-11-02",
        "runtime_hours": 18420,
        "mtbf_hours": 4200,
        "status": "running",
    },
    "EQ-CNC-02": {
        "name": "CNC Milling Center #2",
        "type": "CNC Mill",
        "install_date": "2021-07-22",
        "last_service": "2026-01-18",
        "runtime_hours": 9840,
        "mtbf_hours": 4200,
        "status": "running",
    },
    "EQ-PRS-01": {
        "name": "Hydraulic Press 400T",
        "type": "Press",
        "install_date": "2017-11-05",
        "last_service": "2025-09-30",
        "runtime_hours": 26100,
        "mtbf_hours": 5500,
        "status": "warning",
    },
    "EQ-WLD-01": {
        "name": "Robotic Welder Cell A",
        "type": "Welder",
        "install_date": "2022-01-10",
        "last_service": "2026-02-05",
        "runtime_hours": 7200,
        "mtbf_hours": 3800,
        "status": "running",
    },
    "EQ-INJ-01": {
        "name": "Injection Molder 220T",
        "type": "Injection Molder",
        "install_date": "2018-06-18",
        "last_service": "2025-08-12",
        "runtime_hours": 22800,
        "mtbf_hours": 4800,
        "status": "critical",
    },
    "EQ-ASM-01": {
        "name": "Assembly Line Conveyor",
        "type": "Conveyor",
        "install_date": "2020-04-01",
        "last_service": "2026-01-05",
        "runtime_hours": 14600,
        "mtbf_hours": 7000,
        "status": "running",
    },
}

SENSOR_READINGS = {
    "EQ-CNC-01": {"vibration_mm_s": 4.2, "temp_c": 62, "oil_pressure_bar": 48, "spindle_load_pct": 78},
    "EQ-CNC-02": {"vibration_mm_s": 2.1, "temp_c": 55, "oil_pressure_bar": 51, "spindle_load_pct": 64},
    "EQ-PRS-01": {"vibration_mm_s": 7.8, "temp_c": 74, "oil_pressure_bar": 38, "hydraulic_level_pct": 62},
    "EQ-WLD-01": {"vibration_mm_s": 1.9, "temp_c": 48, "arc_stability_pct": 96, "wire_feed_mpm": 8.4},
    "EQ-INJ-01": {"vibration_mm_s": 9.3, "temp_c": 88, "barrel_pressure_bar": 1420, "cycle_time_s": 34.7},
    "EQ-ASM-01": {"vibration_mm_s": 1.4, "temp_c": 38, "belt_tension_n": 620, "motor_current_a": 12.3},
}

FAILURE_PROBABILITIES = {
    "EQ-CNC-01": {"30_day": 0.12, "60_day": 0.28, "90_day": 0.41, "failure_mode": "Spindle bearing wear"},
    "EQ-CNC-02": {"30_day": 0.03, "60_day": 0.08, "90_day": 0.14, "failure_mode": "Normal wear"},
    "EQ-PRS-01": {"30_day": 0.35, "60_day": 0.58, "90_day": 0.74, "failure_mode": "Hydraulic seal degradation"},
    "EQ-WLD-01": {"30_day": 0.05, "60_day": 0.11, "90_day": 0.19, "failure_mode": "Wire feed mechanism"},
    "EQ-INJ-01": {"30_day": 0.62, "60_day": 0.84, "90_day": 0.93, "failure_mode": "Barrel heater band failure"},
    "EQ-ASM-01": {"30_day": 0.02, "60_day": 0.06, "90_day": 0.10, "failure_mode": "Belt splice fatigue"},
}

TECHNICIANS = {
    "TECH-201": {"name": "Marcus Rivera", "certifications": ["CNC Mill", "Press", "General"],
                  "shift": "Day", "available_hours_week": 40, "committed_hours": 24},
    "TECH-202": {"name": "Karen Oduya", "certifications": ["Welder", "Conveyor", "General"],
                  "shift": "Day", "available_hours_week": 40, "committed_hours": 16},
    "TECH-203": {"name": "James Whitfield", "certifications": ["Injection Molder", "Press", "CNC Mill"],
                  "shift": "Night", "available_hours_week": 40, "committed_hours": 30},
    "TECH-204": {"name": "Lin Zhao", "certifications": ["CNC Mill", "Welder", "Injection Molder", "General"],
                  "shift": "Day", "available_hours_week": 40, "committed_hours": 20},
}

MAINTENANCE_HISTORY = [
    {"eq_id": "EQ-INJ-01", "date": "2025-08-12", "type": "Preventive", "hours": 6, "cost": 2400.00,
     "notes": "Replaced heater bands 3 and 4, calibrated barrel sensors"},
    {"eq_id": "EQ-PRS-01", "date": "2025-09-30", "type": "Corrective", "hours": 12, "cost": 8750.00,
     "notes": "Emergency hydraulic seal replacement, fluid flush"},
    {"eq_id": "EQ-CNC-01", "date": "2025-11-02", "type": "Preventive", "hours": 4, "cost": 1200.00,
     "notes": "Spindle bearing inspection, oil change, alignment check"},
    {"eq_id": "EQ-ASM-01", "date": "2026-01-05", "type": "Preventive", "hours": 3, "cost": 650.00,
     "notes": "Belt tension adjustment, roller lubrication"},
    {"eq_id": "EQ-CNC-02", "date": "2026-01-18", "type": "Preventive", "hours": 4, "cost": 1100.00,
     "notes": "Tool holder inspection, coolant system flush"},
    {"eq_id": "EQ-WLD-01", "date": "2026-02-05", "type": "Preventive", "hours": 5, "cost": 1800.00,
     "notes": "Wire feed calibration, torch tip replacement, gas flow test"},
]

DOWNTIME_COST_PER_HOUR = {
    "CNC Mill": 850, "Press": 1200, "Welder": 600,
    "Injection Molder": 1400, "Conveyor": 2200,
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _risk_priority(eq_id):
    """Return a 0-100 risk score combining failure probability and sensor anomalies."""
    fp = FAILURE_PROBABILITIES[eq_id]["30_day"]
    sensor = SENSOR_READINGS[eq_id]
    vib_score = min(sensor.get("vibration_mm_s", 0) / 10.0, 1.0)
    temp_score = min(sensor.get("temp_c", 20) / 100.0, 1.0)
    return round((fp * 60 + vib_score * 25 + temp_score * 15) * 100 / 100, 1)


def _best_technician(eq_type):
    """Find the best-fit available technician for an equipment type."""
    candidates = []
    for tid, tech in TECHNICIANS.items():
        if eq_type in tech["certifications"] or "General" in tech["certifications"]:
            free = tech["available_hours_week"] - tech["committed_hours"]
            if free > 0:
                candidates.append((tid, tech, free))
    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates[0] if candidates else None


def _estimated_downtime_cost(eq_id, hours):
    """Calculate cost of downtime for given equipment and hours."""
    eq_type = EQUIPMENT[eq_id]["type"]
    return hours * DOWNTIME_COST_PER_HOUR.get(eq_type, 500)


def _work_order_hours(failure_prob_30):
    """Estimate work-order hours from 30-day failure probability."""
    if failure_prob_30 >= 0.50:
        return 8
    elif failure_prob_30 >= 0.25:
        return 5
    elif failure_prob_30 >= 0.10:
        return 3
    return 2


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class MaintenanceSchedulingAgent(BasicAgent):
    """Predictive maintenance scheduling for manufacturing equipment."""

    def __init__(self):
        self.name = "MaintenanceSchedulingAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "operations": [
                "schedule_overview",
                "predictive_alerts",
                "work_order_plan",
                "downtime_analysis",
            ],
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "schedule_overview")
        dispatch = {
            "schedule_overview": self._schedule_overview,
            "predictive_alerts": self._predictive_alerts,
            "work_order_plan": self._work_order_plan,
            "downtime_analysis": self._downtime_analysis,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)

    # ------------------------------------------------------------------
    def _schedule_overview(self, **kwargs) -> str:
        lines = ["## Maintenance Schedule Overview\n"]
        lines.append("### Equipment Status\n")
        lines.append("| ID | Equipment | Type | Status | Runtime (hrs) | Last Service | Risk Score |")
        lines.append("|----|-----------|------|--------|---------------|--------------|------------|")
        for eq_id, eq in EQUIPMENT.items():
            risk = _risk_priority(eq_id)
            status_label = {"running": "OK", "warning": "WARN", "critical": "CRIT"}.get(eq["status"], eq["status"])
            lines.append(
                f"| {eq_id} | {eq['name']} | {eq['type']} | **{status_label}** | "
                f"{eq['runtime_hours']:,} | {eq['last_service']} | {risk} |"
            )

        lines.append("\n### Technician Availability\n")
        lines.append("| Technician | Shift | Certifications | Avail Hrs/Wk | Committed | Free |")
        lines.append("|------------|-------|----------------|-------------|-----------|------|")
        for tid, tech in TECHNICIANS.items():
            free = tech["available_hours_week"] - tech["committed_hours"]
            certs = ", ".join(tech["certifications"])
            lines.append(
                f"| {tech['name']} | {tech['shift']} | {certs} | "
                f"{tech['available_hours_week']} | {tech['committed_hours']} | {free} |"
            )

        lines.append("\n### Recent Maintenance History\n")
        lines.append("| Date | Equipment | Type | Hours | Cost |")
        lines.append("|------|-----------|------|-------|------|")
        for rec in MAINTENANCE_HISTORY[-5:]:
            eq_name = EQUIPMENT.get(rec["eq_id"], {}).get("name", rec["eq_id"])
            lines.append(
                f"| {rec['date']} | {eq_name} | {rec['type']} | {rec['hours']} | ${rec['cost']:,.2f} |"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _predictive_alerts(self, **kwargs) -> str:
        lines = ["## Predictive Maintenance Alerts\n"]
        alerts = []
        for eq_id in EQUIPMENT:
            fp = FAILURE_PROBABILITIES[eq_id]
            risk = _risk_priority(eq_id)
            if fp["30_day"] >= 0.10:
                severity = "CRITICAL" if fp["30_day"] >= 0.50 else "WARNING" if fp["30_day"] >= 0.25 else "WATCH"
                alerts.append((severity, eq_id, fp, risk))
        alerts.sort(key=lambda x: x[3], reverse=True)

        if not alerts:
            lines.append("No predictive alerts at this time. All equipment within normal parameters.")
            return "\n".join(lines)

        for severity, eq_id, fp, risk in alerts:
            eq = EQUIPMENT[eq_id]
            sensor = SENSOR_READINGS[eq_id]
            lines.append(f"### [{severity}] {eq['name']} ({eq_id})")
            lines.append(f"- **Failure mode:** {fp['failure_mode']}")
            lines.append(f"- **30-day failure probability:** {fp['30_day']*100:.0f}%")
            lines.append(f"- **60-day failure probability:** {fp['60_day']*100:.0f}%")
            lines.append(f"- **90-day failure probability:** {fp['90_day']*100:.0f}%")
            lines.append(f"- **Risk score:** {risk}/100")
            lines.append("- **Current sensor readings:**")
            for k, v in sensor.items():
                lines.append(f"  - {k}: {v}")
            lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _work_order_plan(self, **kwargs) -> str:
        lines = ["## Work Order Plan\n"]
        lines.append("Priority-ranked work orders for the next 30 days:\n")
        lines.append("| Priority | Equipment | Work Description | Est Hours | Assigned Tech | Shift |")
        lines.append("|----------|-----------|------------------|-----------|---------------|-------|")

        ranked = sorted(EQUIPMENT.keys(), key=lambda e: _risk_priority(e), reverse=True)
        priority = 0
        total_hours = 0
        for eq_id in ranked:
            fp = FAILURE_PROBABILITIES[eq_id]
            if fp["30_day"] < 0.10:
                continue
            priority += 1
            eq = EQUIPMENT[eq_id]
            tech_match = _best_technician(eq["type"])
            tech_name = tech_match[1]["name"] if tech_match else "UNASSIGNED"
            shift = tech_match[1]["shift"] if tech_match else "-"
            est_hours = _work_order_hours(fp["30_day"])
            total_hours += est_hours
            lines.append(
                f"| P{priority} | {eq['name']} | {fp['failure_mode']} -- preventive service | "
                f"{est_hours} | {tech_name} | {shift} |"
            )

        lines.append(f"\n**Total work orders:** {priority}")
        lines.append(f"**Total estimated labor hours:** {total_hours}")
        lines.append("\n**Scheduling notes:**")
        lines.append("- P1 work orders should be completed within 7 days")
        lines.append("- P2 work orders within 14 days")
        lines.append("- P3+ within 30 days")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _downtime_analysis(self, **kwargs) -> str:
        lines = ["## Downtime & Cost Analysis\n"]
        lines.append("### Unplanned Downtime Risk (Next 90 Days)\n")
        lines.append("| Equipment | 30-Day P(Fail) | Est Downtime (hrs) | Downtime Cost | Prevention Cost | Net Savings |")
        lines.append("|-----------|----------------|--------------------|--------------:|----------------:|------------:|")
        total_dt_cost = 0.0
        total_prev_cost = 0.0
        for eq_id, eq in EQUIPMENT.items():
            fp = FAILURE_PROBABILITIES[eq_id]
            p = fp["30_day"]
            if p < 0.10:
                continue
            dt_hrs = round(p * 24, 1)
            dt_cost = _estimated_downtime_cost(eq_id, dt_hrs)
            prev_cost = round(dt_cost * 0.25, 2)
            savings = round(dt_cost - prev_cost, 2)
            total_dt_cost += dt_cost
            total_prev_cost += prev_cost
            lines.append(
                f"| {eq['name']} | {p*100:.0f}% | {dt_hrs} | "
                f"${dt_cost:,.2f} | ${prev_cost:,.2f} | ${savings:,.2f} |"
            )

        lines.append(f"\n**Total downtime cost exposure:** ${total_dt_cost:,.2f}")
        lines.append(f"**Total preventive maintenance cost:** ${total_prev_cost:,.2f}")
        lines.append(f"**Net savings from preventive action:** ${total_dt_cost - total_prev_cost:,.2f}")

        lines.append("\n### Historical Maintenance Spend\n")
        total_hist = sum(r["cost"] for r in MAINTENANCE_HISTORY)
        prev_count = sum(1 for r in MAINTENANCE_HISTORY if r["type"] == "Preventive")
        corr_count = sum(1 for r in MAINTENANCE_HISTORY if r["type"] == "Corrective")
        lines.append(f"- Total spend (last 12 months): **${total_hist:,.2f}**")
        lines.append(f"- Preventive work orders: **{prev_count}**")
        lines.append(f"- Corrective (unplanned) work orders: **{corr_count}**")
        lines.append(f"- Preventive-to-corrective ratio: **{prev_count}:{corr_count}** (target 5:1)")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = MaintenanceSchedulingAgent()
    for op in agent.metadata["operations"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
