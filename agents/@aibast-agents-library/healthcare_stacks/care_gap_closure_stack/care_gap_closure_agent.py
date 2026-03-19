"""
Care Gap Closure Agent for Healthcare.

Analyzes HEDIS quality measure gaps, prioritizes patient outreach,
manages outreach campaigns, and provides HEDIS compliance dashboards
for population health management teams.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/care-gap-closure",
    "version": "1.0.0",
    "display_name": "Care Gap Closure Agent",
    "description": "Analyzes HEDIS quality measure gaps, prioritizes patient outreach, manages campaigns, and provides HEDIS compliance dashboards.",
    "author": "AIBAST",
    "tags": ["hedis", "care-gaps", "quality-measures", "outreach", "population-health", "healthcare"],
    "category": "healthcare",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

HEDIS_MEASURES = {
    "BCS": {
        "name": "Breast Cancer Screening",
        "description": "Women 50-74 with mammogram in past 2 years",
        "eligible_patients": 4280,
        "compliant_patients": 3210,
        "gap_rate_pct": 25.0,
        "revenue_per_closure": 45,
        "national_benchmark_pct": 78.2,
        "star_rating_impact": "4-star threshold at 76%",
    },
    "CDC-HBA1C": {
        "name": "Diabetes HbA1c Testing",
        "description": "Diabetic patients 18-75 with HbA1c test in past year",
        "eligible_patients": 6120,
        "compliant_patients": 5202,
        "gap_rate_pct": 15.0,
        "revenue_per_closure": 62,
        "national_benchmark_pct": 88.5,
        "star_rating_impact": "5-star threshold at 90%",
    },
    "COL": {
        "name": "Colorectal Cancer Screening",
        "description": "Adults 45-75 with appropriate colorectal screening",
        "eligible_patients": 8940,
        "compliant_patients": 5810,
        "gap_rate_pct": 35.0,
        "revenue_per_closure": 38,
        "national_benchmark_pct": 72.1,
        "star_rating_impact": "4-star threshold at 68%",
    },
    "CBP": {
        "name": "Controlling Blood Pressure",
        "description": "Hypertensive patients 18-85 with BP adequately controlled",
        "eligible_patients": 7650,
        "compliant_patients": 5355,
        "gap_rate_pct": 30.0,
        "revenue_per_closure": 55,
        "national_benchmark_pct": 65.8,
        "star_rating_impact": "4-star threshold at 64%",
    },
    "AWC": {
        "name": "Adolescent Well-Care Visits",
        "description": "Adolescents 12-21 with at least one well-care visit",
        "eligible_patients": 3200,
        "compliant_patients": 1920,
        "gap_rate_pct": 40.0,
        "revenue_per_closure": 28,
        "national_benchmark_pct": 58.4,
        "star_rating_impact": "3-star threshold at 54%",
    },
}

PATIENT_SEGMENTS = {
    "multi_gap_high_risk": {
        "count": 1842,
        "description": "Patients with 3+ open gaps and chronic conditions",
        "avg_risk_score": 3.8,
        "preferred_outreach": "phone_call",
        "response_rate_pct": 42,
    },
    "single_gap_engaged": {
        "count": 5610,
        "description": "Patients with 1 open gap and recent visit history",
        "avg_risk_score": 1.4,
        "preferred_outreach": "patient_portal",
        "response_rate_pct": 68,
    },
    "unreachable": {
        "count": 890,
        "description": "Patients with no valid contact info or repeated no-shows",
        "avg_risk_score": 2.9,
        "preferred_outreach": "mail",
        "response_rate_pct": 8,
    },
    "recently_compliant": {
        "count": 3420,
        "description": "Patients who closed gaps in last 90 days",
        "avg_risk_score": 1.1,
        "preferred_outreach": "none",
        "response_rate_pct": 0,
    },
}

OUTREACH_CHANNELS = {
    "phone_call": {"cost_per_contact": 4.50, "avg_response_rate_pct": 38, "avg_conversion_pct": 22},
    "patient_portal": {"cost_per_contact": 0.25, "avg_response_rate_pct": 52, "avg_conversion_pct": 31},
    "sms": {"cost_per_contact": 0.15, "avg_response_rate_pct": 45, "avg_conversion_pct": 18},
    "mail": {"cost_per_contact": 2.80, "avg_response_rate_pct": 12, "avg_conversion_pct": 6},
    "email": {"cost_per_contact": 0.08, "avg_response_rate_pct": 28, "avg_conversion_pct": 14},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _gap_analysis():
    analysis = []
    for mid, m in HEDIS_MEASURES.items():
        gap_count = m["eligible_patients"] - m["compliant_patients"]
        current_rate = round((m["compliant_patients"] / m["eligible_patients"]) * 100, 1)
        revenue_opportunity = gap_count * m["revenue_per_closure"]
        analysis.append({
            "measure_id": mid, "name": m["name"],
            "eligible": m["eligible_patients"], "compliant": m["compliant_patients"],
            "gap_count": gap_count, "compliance_rate": current_rate,
            "gap_rate_pct": m["gap_rate_pct"],
            "benchmark": m["national_benchmark_pct"],
            "revenue_opportunity": revenue_opportunity,
            "star_impact": m["star_rating_impact"],
        })
    analysis.sort(key=lambda x: x["revenue_opportunity"], reverse=True)
    total_rev = sum(a["revenue_opportunity"] for a in analysis)
    return {"measures": analysis, "total_revenue_opportunity": total_rev}


def _patient_prioritization():
    segments = []
    for seg_id, seg in PATIENT_SEGMENTS.items():
        segments.append({
            "segment": seg_id.replace("_", " ").title(),
            "count": seg["count"],
            "description": seg["description"],
            "risk_score": seg["avg_risk_score"],
            "preferred_channel": seg["preferred_outreach"],
            "expected_response_pct": seg["response_rate_pct"],
        })
    segments.sort(key=lambda x: x["risk_score"], reverse=True)
    return {"segments": segments}


def _outreach_campaign():
    campaigns = []
    for mid, m in HEDIS_MEASURES.items():
        gap_count = m["eligible_patients"] - m["compliant_patients"]
        best_channel = max(OUTREACH_CHANNELS.items(), key=lambda x: x[1]["avg_conversion_pct"])
        channel_name, channel = best_channel
        projected_closures = round(gap_count * channel["avg_conversion_pct"] / 100)
        cost = round(gap_count * channel["cost_per_contact"], 2)
        revenue = projected_closures * m["revenue_per_closure"]
        campaigns.append({
            "measure": m["name"], "gap_count": gap_count,
            "channel": channel_name, "projected_closures": projected_closures,
            "cost": cost, "projected_revenue": revenue,
            "roi": round(revenue / cost, 1) if cost > 0 else 0,
        })
    campaigns.sort(key=lambda x: x["roi"], reverse=True)
    return {"campaigns": campaigns}


def _hedis_dashboard():
    dashboard = []
    for mid, m in HEDIS_MEASURES.items():
        current_rate = round((m["compliant_patients"] / m["eligible_patients"]) * 100, 1)
        vs_benchmark = round(current_rate - m["national_benchmark_pct"], 1)
        dashboard.append({
            "measure_id": mid, "name": m["name"],
            "current_rate": current_rate, "benchmark": m["national_benchmark_pct"],
            "vs_benchmark": vs_benchmark,
            "star_impact": m["star_rating_impact"],
            "eligible": m["eligible_patients"],
        })
    return {"measures": dashboard}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class CareGapClosureAgent(BasicAgent):
    """HEDIS care gap analysis and outreach management agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/care-gap-closure"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "gap_analysis",
                            "patient_prioritization",
                            "outreach_campaign",
                            "hedis_dashboard",
                        ],
                        "description": "The care gap closure operation to perform.",
                    },
                    "measure_id": {
                        "type": "string",
                        "description": "Optional HEDIS measure ID to filter results.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "gap_analysis")
        if op == "gap_analysis":
            return self._gap_analysis()
        elif op == "patient_prioritization":
            return self._patient_prioritization()
        elif op == "outreach_campaign":
            return self._outreach_campaign()
        elif op == "hedis_dashboard":
            return self._hedis_dashboard()
        return f"**Error:** Unknown operation `{op}`."

    def _gap_analysis(self) -> str:
        data = _gap_analysis()
        lines = [
            "# Care Gap Analysis",
            "",
            f"**Total Revenue Opportunity:** ${data['total_revenue_opportunity']:,}",
            "",
            "| Measure | Eligible | Compliant | Gaps | Rate | Benchmark | Revenue Opp | Star Impact |",
            "|---------|----------|-----------|------|------|-----------|------------|-------------|",
        ]
        for m in data["measures"]:
            lines.append(
                f"| {m['name']} | {m['eligible']:,} | {m['compliant']:,} | {m['gap_count']:,} "
                f"| {m['compliance_rate']}% | {m['benchmark']}% | ${m['revenue_opportunity']:,} | {m['star_impact']} |"
            )
        return "\n".join(lines)

    def _patient_prioritization(self) -> str:
        data = _patient_prioritization()
        lines = [
            "# Patient Prioritization",
            "",
            "| Segment | Count | Risk Score | Preferred Channel | Expected Response |",
            "|---------|-------|-----------|-------------------|-------------------|",
        ]
        for s in data["segments"]:
            lines.append(
                f"| {s['segment']} | {s['count']:,} | {s['risk_score']} "
                f"| {s['preferred_channel']} | {s['expected_response_pct']}% |"
            )
        lines.append("")
        lines.append("## Recommendations")
        lines.append("- Prioritize multi-gap high-risk patients with phone outreach for highest impact.")
        lines.append("- Leverage patient portal messaging for single-gap engaged patients (lowest cost).")
        lines.append("- Initiate address verification campaign for unreachable segment.")
        return "\n".join(lines)

    def _outreach_campaign(self) -> str:
        data = _outreach_campaign()
        lines = [
            "# Outreach Campaign Plan",
            "",
            "| Measure | Gaps | Channel | Projected Closures | Cost | Revenue | ROI |",
            "|---------|------|---------|--------------------|------|---------|-----|",
        ]
        for c in data["campaigns"]:
            lines.append(
                f"| {c['measure']} | {c['gap_count']:,} | {c['channel']} "
                f"| {c['projected_closures']:,} | ${c['cost']:,.2f} | ${c['projected_revenue']:,} | {c['roi']}x |"
            )
        return "\n".join(lines)

    def _hedis_dashboard(self) -> str:
        data = _hedis_dashboard()
        lines = [
            "# HEDIS Dashboard",
            "",
            "| Measure | Current Rate | Benchmark | vs Benchmark | Eligible | Star Impact |",
            "|---------|-------------|-----------|-------------|----------|-------------|",
        ]
        for m in data["measures"]:
            direction = "+" if m["vs_benchmark"] >= 0 else ""
            lines.append(
                f"| {m['name']} | {m['current_rate']}% | {m['benchmark']}% "
                f"| {direction}{m['vs_benchmark']}% | {m['eligible']:,} | {m['star_impact']} |"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = CareGapClosureAgent()
    for op in ["gap_analysis", "patient_prioritization", "outreach_campaign", "hedis_dashboard"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
