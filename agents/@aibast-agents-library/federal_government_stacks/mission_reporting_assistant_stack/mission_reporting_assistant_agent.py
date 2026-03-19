"""
Mission Reporting Assistant Agent — Federal Government Stack

Generates mission summaries, KPI dashboards, stakeholder briefs, and
trend analyses for federal program and mission managers.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/mission-reporting-assistant",
    "version": "1.0.0",
    "display_name": "Mission Reporting Assistant Agent",
    "description": "Generates mission summaries, KPI dashboards, stakeholder briefs, and trend analyses for federal programs.",
    "author": "AIBAST",
    "tags": ["mission", "reporting", "KPI", "stakeholder", "federal", "dashboard"],
    "category": "federal_government",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

MISSION_OBJECTIVES = {
    "MO-001": {
        "name": "Cybersecurity Posture Improvement",
        "strategic_goal": "SG-2: Secure Federal Networks",
        "lead_office": "Office of the CISO",
        "status": "on_track",
        "priority": "critical",
        "start_date": "2024-10-01",
        "target_date": "2025-09-30",
        "budget_allocated": 14500000,
        "budget_spent": 7250000,
        "description": "Improve agency cybersecurity posture across all FISMA systems to achieve 95% compliance.",
    },
    "MO-002": {
        "name": "Customer Experience Modernization",
        "strategic_goal": "SG-4: Deliver Excellent Service",
        "lead_office": "Office of Customer Experience",
        "status": "at_risk",
        "priority": "high",
        "start_date": "2024-10-01",
        "target_date": "2026-03-31",
        "budget_allocated": 8200000,
        "budget_spent": 4920000,
        "description": "Modernize public-facing digital services to achieve 80% customer satisfaction.",
    },
    "MO-003": {
        "name": "Workforce Transformation Initiative",
        "strategic_goal": "SG-5: Build Future Workforce",
        "lead_office": "Office of Human Capital",
        "status": "on_track",
        "priority": "high",
        "start_date": "2025-01-01",
        "target_date": "2027-09-30",
        "budget_allocated": 5600000,
        "budget_spent": 840000,
        "description": "Recruit, reskill, and retain critical technology talent across the agency.",
    },
}

KPIS = {
    "KPI-101": {"name": "FISMA Compliance Rate", "mission": "MO-001", "target": 95.0, "current": 87.3, "unit": "%", "trend": "improving"},
    "KPI-102": {"name": "Mean Time to Remediate (Critical)", "mission": "MO-001", "target": 15, "current": 22, "unit": "days", "trend": "improving"},
    "KPI-103": {"name": "Phishing Click Rate", "mission": "MO-001", "target": 3.0, "current": 4.8, "unit": "%", "trend": "stable"},
    "KPI-201": {"name": "Customer Satisfaction Score", "mission": "MO-002", "target": 80.0, "current": 68.5, "unit": "%", "trend": "declining"},
    "KPI-202": {"name": "Digital Service Adoption", "mission": "MO-002", "target": 70.0, "current": 52.1, "unit": "%", "trend": "improving"},
    "KPI-203": {"name": "Average Transaction Time", "mission": "MO-002", "target": 5.0, "current": 8.3, "unit": "minutes", "trend": "improving"},
    "KPI-301": {"name": "Critical Position Fill Rate", "mission": "MO-003", "target": 90.0, "current": 72.0, "unit": "%", "trend": "improving"},
    "KPI-302": {"name": "Employee Engagement Score", "mission": "MO-003", "target": 75.0, "current": 69.4, "unit": "%", "trend": "stable"},
    "KPI-303": {"name": "Training Completion Rate", "mission": "MO-003", "target": 85.0, "current": 61.5, "unit": "%", "trend": "improving"},
}

STAKEHOLDERS = {
    "SH-01": {"name": "Deputy Secretary", "role": "Executive Sponsor", "briefing_frequency": "monthly", "interest": "strategic_outcomes"},
    "SH-02": {"name": "CFO", "role": "Budget Oversight", "briefing_frequency": "quarterly", "interest": "financial_performance"},
    "SH-03": {"name": "CIO", "role": "Technology Lead", "briefing_frequency": "bi-weekly", "interest": "it_modernization"},
    "SH-04": {"name": "CHCO", "role": "Workforce Lead", "briefing_frequency": "monthly", "interest": "workforce_metrics"},
    "SH-05": {"name": "OMB Desk Officer", "role": "External Oversight", "briefing_frequency": "quarterly", "interest": "performance_targets"},
    "SH-06": {"name": "Congressional Liaison", "role": "Legislative Affairs", "briefing_frequency": "as_needed", "interest": "appropriations_alignment"},
}

QUARTERLY_TRENDS = {
    "Q1-FY24": {"KPI-101": 78.1, "KPI-201": 72.0, "KPI-301": 65.0},
    "Q2-FY24": {"KPI-101": 80.5, "KPI-201": 71.2, "KPI-301": 67.5},
    "Q3-FY24": {"KPI-101": 83.2, "KPI-201": 70.0, "KPI-301": 69.0},
    "Q4-FY24": {"KPI-101": 85.0, "KPI-201": 69.1, "KPI-301": 70.8},
    "Q1-FY25": {"KPI-101": 87.3, "KPI-201": 68.5, "KPI-301": 72.0},
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _kpi_status(kpi):
    """Determine KPI status relative to target."""
    if kpi["unit"] in ("days", "minutes"):
        pct = (kpi["target"] / kpi["current"]) * 100 if kpi["current"] else 100
    else:
        pct = (kpi["current"] / kpi["target"]) * 100 if kpi["target"] else 0
    if pct >= 95:
        return "On Target"
    elif pct >= 75:
        return "Near Target"
    else:
        return "Below Target"


def _budget_utilization(mission):
    """Compute budget utilization percentage."""
    if mission["budget_allocated"] == 0:
        return 0.0
    return round((mission["budget_spent"] / mission["budget_allocated"]) * 100, 1)


def _trend_direction(values):
    """Determine trend direction from a list of values."""
    if len(values) < 2:
        return "insufficient_data"
    recent = values[-1]
    previous = values[-2]
    if recent > previous * 1.02:
        return "improving"
    elif recent < previous * 0.98:
        return "declining"
    return "stable"


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class MissionReportingAssistantAgent(BasicAgent):
    """Mission reporting assistant for federal program management."""

    def __init__(self):
        self.name = "@aibast-agents-library/mission-reporting-assistant"
        self.metadata = {
            "name": self.name,
            "display_name": "Mission Reporting Assistant Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "mission_summary",
                            "kpi_dashboard",
                            "stakeholder_brief",
                            "trend_analysis",
                        ],
                    },
                    "mission_id": {"type": "string"},
                    "stakeholder_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "mission_summary")
        dispatch = {
            "mission_summary": self._mission_summary,
            "kpi_dashboard": self._kpi_dashboard,
            "stakeholder_brief": self._stakeholder_brief,
            "trend_analysis": self._trend_analysis,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _mission_summary(self, **kwargs) -> str:
        lines = ["# Mission Summary Report\n"]
        for mid, m in MISSION_OBJECTIVES.items():
            util = _budget_utilization(m)
            lines.append(f"## {mid}: {m['name']}\n")
            lines.append(f"- **Strategic Goal:** {m['strategic_goal']}")
            lines.append(f"- **Lead Office:** {m['lead_office']}")
            lines.append(f"- **Status:** {m['status'].replace('_', ' ').title()}")
            lines.append(f"- **Priority:** {m['priority'].title()}")
            lines.append(f"- **Period:** {m['start_date']} to {m['target_date']}")
            lines.append(f"- **Budget:** ${m['budget_allocated']:,.0f} allocated / ${m['budget_spent']:,.0f} spent ({util}%)")
            lines.append(f"- **Description:** {m['description']}\n")
            mission_kpis = {k: v for k, v in KPIS.items() if v["mission"] == mid}
            if mission_kpis:
                lines.append("| KPI | Current | Target | Status |")
                lines.append("|---|---|---|---|")
                for kid, kpi in mission_kpis.items():
                    status = _kpi_status(kpi)
                    lines.append(f"| {kpi['name']} | {kpi['current']} {kpi['unit']} | {kpi['target']} {kpi['unit']} | {status} |")
            lines.append("")
        return "\n".join(lines)

    def _kpi_dashboard(self, **kwargs) -> str:
        lines = ["# KPI Dashboard\n"]
        lines.append("| KPI ID | Name | Mission | Current | Target | Unit | Trend | Status |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for kid, kpi in KPIS.items():
            status = _kpi_status(kpi)
            lines.append(
                f"| {kid} | {kpi['name']} | {kpi['mission']} "
                f"| {kpi['current']} | {kpi['target']} | {kpi['unit']} "
                f"| {kpi['trend'].title()} | {status} |"
            )
        on_target = sum(1 for k in KPIS.values() if _kpi_status(k) == "On Target")
        near = sum(1 for k in KPIS.values() if _kpi_status(k) == "Near Target")
        below = sum(1 for k in KPIS.values() if _kpi_status(k) == "Below Target")
        lines.append(f"\n**Summary:** {on_target} on target, {near} near target, {below} below target")
        return "\n".join(lines)

    def _stakeholder_brief(self, **kwargs) -> str:
        lines = ["# Stakeholder Briefing Guide\n"]
        lines.append("## Stakeholder Registry\n")
        lines.append("| ID | Name | Role | Briefing Frequency | Interest Area |")
        lines.append("|---|---|---|---|---|")
        for sid, s in STAKEHOLDERS.items():
            lines.append(
                f"| {sid} | {s['name']} | {s['role']} "
                f"| {s['briefing_frequency'].replace('_', ' ').title()} | {s['interest'].replace('_', ' ').title()} |"
            )
        lines.append("\n## Executive Brief\n")
        for mid, m in MISSION_OBJECTIVES.items():
            lines.append(f"### {m['name']} — {m['status'].replace('_', ' ').title()}\n")
            mission_kpis = {k: v for k, v in KPIS.items() if v["mission"] == mid}
            highlights = []
            for kid, kpi in mission_kpis.items():
                status = _kpi_status(kpi)
                if status == "Below Target":
                    highlights.append(f"- **Action Needed:** {kpi['name']} at {kpi['current']}{kpi['unit']} vs target {kpi['target']}{kpi['unit']}")
                elif status == "On Target":
                    highlights.append(f"- **On Track:** {kpi['name']} at {kpi['current']}{kpi['unit']}")
            for h in highlights:
                lines.append(h)
            lines.append("")
        return "\n".join(lines)

    def _trend_analysis(self, **kwargs) -> str:
        lines = ["# Trend Analysis\n"]
        tracked_kpis = ["KPI-101", "KPI-201", "KPI-301"]
        for kid in tracked_kpis:
            kpi = KPIS[kid]
            lines.append(f"## {kid}: {kpi['name']}\n")
            lines.append(f"**Target:** {kpi['target']} {kpi['unit']}\n")
            lines.append("| Quarter | Value |")
            lines.append("|---|---|")
            values = []
            for qtr, data in QUARTERLY_TRENDS.items():
                val = data.get(kid)
                if val is not None:
                    values.append(val)
                    lines.append(f"| {qtr} | {val} {kpi['unit']} |")
            direction = _trend_direction(values)
            lines.append(f"\n**Trend:** {direction.title()}")
            if values:
                change = round(values[-1] - values[0], 1)
                lines.append(f"**Net Change:** {'+' if change >= 0 else ''}{change} {kpi['unit']} over {len(values)} quarters\n")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = MissionReportingAssistantAgent()
    print(agent.perform(operation="mission_summary"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="kpi_dashboard"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="stakeholder_brief"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="trend_analysis"))
