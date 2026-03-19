"""
Resource Utilization Agent

Tracks consultant utilization, billable hours, and capacity across a
professional-services firm. Forecasts demand, identifies bench resources,
and generates staffing recommendations to hit utilization targets.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/resource-utilization",
    "version": "1.0.0",
    "display_name": "Resource Utilization Agent",
    "description": "Tracks consultant utilization and capacity, forecasts demand, analyzes bench costs, and generates staffing recommendations to meet targets.",
    "author": "AIBAST",
    "tags": ["utilization", "staffing", "capacity", "bench", "professional-services"],
    "category": "professional_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

CONSULTANTS = {
    "CON-401": {"name": "Elena Vasquez", "level": "Senior", "skills": ["Cloud Architecture", "Azure", "DevOps"],
                 "rate_hr": 275, "utilization_pct": 92, "status": "billable",
                 "current_project": "TechCorp Transformation", "project_end": "2026-06-30"},
    "CON-402": {"name": "Michael Chen", "level": "Senior", "skills": ["Data Engineering", "Databricks", "Python"],
                 "rate_hr": 260, "utilization_pct": 88, "status": "billable",
                 "current_project": "Apex Analytics Platform", "project_end": "2026-05-15"},
    "CON-403": {"name": "Priya Sharma", "level": "Manager", "skills": ["Program Management", "Agile", "Change Mgmt"],
                 "rate_hr": 310, "utilization_pct": 95, "status": "billable",
                 "current_project": "Pinnacle Energy ERP", "project_end": "2026-08-31"},
    "CON-404": {"name": "David Okafor", "level": "Mid", "skills": ["Data Analytics", "Power BI", "SQL"],
                 "rate_hr": 175, "utilization_pct": 0, "status": "bench",
                 "current_project": None, "project_end": None},
    "CON-405": {"name": "Sarah Kim", "level": "Mid", "skills": ["Cloud Architecture", "AWS", "Terraform"],
                 "rate_hr": 185, "utilization_pct": 0, "status": "bench",
                 "current_project": None, "project_end": None},
    "CON-406": {"name": "James Wright", "level": "Junior", "skills": ["Business Analysis", "Requirements", "Jira"],
                 "rate_hr": 125, "utilization_pct": 0, "status": "bench",
                 "current_project": None, "project_end": None},
    "CON-407": {"name": "Lisa Tanaka", "level": "Senior", "skills": ["Cybersecurity", "Identity", "Compliance"],
                 "rate_hr": 290, "utilization_pct": 78, "status": "billable",
                 "current_project": "Atlas Security Audit", "project_end": "2026-04-10"},
    "CON-408": {"name": "Robert Garcia", "level": "Mid", "skills": ["ERP", "D365", "Integration"],
                 "rate_hr": 195, "utilization_pct": 0, "status": "bench",
                 "current_project": None, "project_end": None},
    "CON-409": {"name": "Amanda Foster", "level": "Mid", "skills": ["UX Design", "Research", "Figma"],
                 "rate_hr": 165, "utilization_pct": 85, "status": "billable",
                 "current_project": "Metro Transit Portal", "project_end": "2026-05-01"},
    "CON-410": {"name": "Chen Wei", "level": "Senior", "skills": ["AI/ML", "Python", "Azure ML"],
                 "rate_hr": 295, "utilization_pct": 0, "status": "bench",
                 "current_project": None, "project_end": None},
}

PROJECT_PIPELINE = [
    {"name": "FinanceHub Cloud Migration", "start": "2026-04-01", "months": 6,
     "needs": [("Cloud Architecture", "Senior", 1), ("DevOps", "Mid", 2)], "probability": 0.85},
    {"name": "Healthcare Digital Transformation", "start": "2026-04-15", "months": 12,
     "needs": [("Program Management", "Manager", 1), ("Data Analytics", "Mid", 2), ("Business Analysis", "Junior", 1)], "probability": 0.75},
    {"name": "Retail Analytics Platform", "start": "2026-05-01", "months": 8,
     "needs": [("AI/ML", "Senior", 1), ("Data Engineering", "Mid", 1)], "probability": 0.60},
    {"name": "Government Cyber Assessment", "start": "2026-04-01", "months": 3,
     "needs": [("Cybersecurity", "Senior", 2), ("Compliance", "Mid", 1)], "probability": 0.90},
]

UTILIZATION_TARGETS = {
    "Senior": 85,
    "Manager": 80,
    "Mid": 80,
    "Junior": 75,
    "firm_target": 85,
}

BENCH_COST_PER_MONTH = {
    "Senior": 22000,
    "Manager": 25000,
    "Mid": 14000,
    "Junior": 10000,
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _firm_utilization():
    """Average utilization across all consultants."""
    rates = [c["utilization_pct"] for c in CONSULTANTS.values()]
    return round(sum(rates) / len(rates), 1)


def _bench_consultants():
    """Return list of bench consultants."""
    return {cid: c for cid, c in CONSULTANTS.items() if c["status"] == "bench"}


def _monthly_bench_cost():
    """Total monthly cost of bench consultants."""
    total = 0
    for c in CONSULTANTS.values():
        if c["status"] == "bench":
            total += BENCH_COST_PER_MONTH.get(c["level"], 14000)
    return total


def _skill_match(consultant, required_skill):
    """Check if a consultant has a matching skill."""
    return any(required_skill.lower() in s.lower() for s in consultant["skills"])


def _find_matches_for_pipeline():
    """Match bench consultants to pipeline project needs."""
    matches = []
    bench = _bench_consultants()
    for proj in PROJECT_PIPELINE:
        for skill, level, count in proj["needs"]:
            candidates = [
                (cid, c) for cid, c in bench.items()
                if c["level"] == level and _skill_match(c, skill)
            ]
            for cid, c in candidates[:count]:
                matches.append({
                    "consultant_id": cid,
                    "consultant_name": c["name"],
                    "project": proj["name"],
                    "skill_matched": skill,
                    "level": level,
                    "probability": proj["probability"],
                    "start": proj["start"],
                })
    return matches


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class ResourceUtilizationAgent(BasicAgent):
    """Tracks consultant utilization and generates staffing plans."""

    def __init__(self):
        self.name = "ResourceUtilizationAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "operations": [
                "utilization_dashboard",
                "capacity_forecast",
                "bench_analysis",
                "staffing_recommendation",
            ],
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "utilization_dashboard")
        dispatch = {
            "utilization_dashboard": self._utilization_dashboard,
            "capacity_forecast": self._capacity_forecast,
            "bench_analysis": self._bench_analysis,
            "staffing_recommendation": self._staffing_recommendation,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)

    # ------------------------------------------------------------------
    def _utilization_dashboard(self, **kwargs) -> str:
        lines = ["## Resource Utilization Dashboard\n"]
        firm_util = _firm_utilization()
        target = UTILIZATION_TARGETS["firm_target"]
        gap = round(target - firm_util, 1)
        bench = _bench_consultants()
        lines.append(f"**Firm utilization:** {firm_util}% (target: {target}%, gap: {gap}pp)")
        lines.append(f"**Total headcount:** {len(CONSULTANTS)}")
        lines.append(f"**Billable:** {len(CONSULTANTS) - len(bench)}")
        lines.append(f"**Bench:** {len(bench)}")
        lines.append(f"**Monthly bench cost:** ${_monthly_bench_cost():,.0f}\n")

        lines.append("| ID | Name | Level | Rate/Hr | Util % | Status | Project | End Date |")
        lines.append("|----|------|-------|---------|--------|--------|---------|----------|")
        for cid, c in CONSULTANTS.items():
            proj = c["current_project"] or "-"
            end = c["project_end"] or "-"
            flag = " **BENCH**" if c["status"] == "bench" else ""
            lines.append(
                f"| {cid} | {c['name']} | {c['level']} | ${c['rate_hr']} | "
                f"{c['utilization_pct']}% | {c['status']}{flag} | {proj[:22]} | {end} |"
            )

        lines.append("\n### Utilization by Level\n")
        lines.append("| Level | Headcount | Avg Util | Target | Status |")
        lines.append("|-------|-----------|----------|--------|--------|")
        for level in ("Senior", "Manager", "Mid", "Junior"):
            members = [c for c in CONSULTANTS.values() if c["level"] == level]
            if not members:
                continue
            avg = round(sum(c["utilization_pct"] for c in members) / len(members), 1)
            tgt = UTILIZATION_TARGETS.get(level, 80)
            status = "On Track" if avg >= tgt else "Below Target"
            lines.append(f"| {level} | {len(members)} | {avg}% | {tgt}% | {status} |")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _capacity_forecast(self, **kwargs) -> str:
        lines = ["## Capacity Forecast (Next 90 Days)\n"]
        lines.append("### Upcoming Project Endings\n")
        lines.append("| Consultant | Project | End Date | Level | Skills |")
        lines.append("|------------|---------|----------|-------|--------|")
        ending_soon = [(cid, c) for cid, c in CONSULTANTS.items()
                       if c["project_end"] and c["project_end"] <= "2026-06-30"]
        for cid, c in sorted(ending_soon, key=lambda x: x[1]["project_end"]):
            lines.append(
                f"| {c['name']} | {c['current_project']} | {c['project_end']} | "
                f"{c['level']} | {', '.join(c['skills'][:2])} |"
            )

        lines.append("\n### Pipeline Demand\n")
        lines.append("| Project | Start | Duration | Probability | Roles Needed |")
        lines.append("|---------|-------|----------|-------------|--------------|")
        for proj in PROJECT_PIPELINE:
            roles = "; ".join(f"{s} ({l})" for s, l, _ in proj["needs"])
            lines.append(
                f"| {proj['name']} | {proj['start']} | {proj['months']}mo | "
                f"{proj['probability']*100:.0f}% | {roles} |"
            )

        total_roles = sum(count for proj in PROJECT_PIPELINE for _, _, count in proj["needs"])
        lines.append(f"\n**Total roles in pipeline:** {total_roles}")
        lines.append(f"**Bench available:** {len(_bench_consultants())}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _bench_analysis(self, **kwargs) -> str:
        lines = ["## Bench Analysis\n"]
        bench = _bench_consultants()
        monthly_cost = _monthly_bench_cost()
        lines.append(f"**Bench headcount:** {len(bench)}")
        lines.append(f"**Monthly bench cost:** ${monthly_cost:,.0f}")
        lines.append(f"**Annualized bench cost:** ${monthly_cost * 12:,.0f}\n")

        lines.append("| ID | Name | Level | Rate/Hr | Skills | Monthly Cost | Days on Bench |")
        lines.append("|----|------|-------|---------|--------|-------------|---------------|")
        for cid, c in bench.items():
            mc = BENCH_COST_PER_MONTH.get(c["level"], 14000)
            skills = ", ".join(c["skills"][:2])
            lines.append(
                f"| {cid} | {c['name']} | {c['level']} | ${c['rate_hr']} | {skills} | ${mc:,.0f} | est. 30+ |"
            )

        lines.append("\n### Skill Inventory on Bench\n")
        skill_counts = {}
        for c in bench.values():
            for s in c["skills"]:
                skill_counts[s] = skill_counts.get(s, 0) + 1
        lines.append("| Skill | Available |")
        lines.append("|-------|-----------|")
        for s, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"| {s} | {count} |")

        lines.append(f"\n**Revenue opportunity if deployed:** ${sum(c['rate_hr'] * 160 for c in bench.values()):,.0f}/month")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _staffing_recommendation(self, **kwargs) -> str:
        lines = ["## Staffing Recommendations\n"]
        matches = _find_matches_for_pipeline()

        if matches:
            lines.append("### Bench-to-Pipeline Matches\n")
            lines.append("| Consultant | Project | Skill Match | Level | Probability | Start |")
            lines.append("|------------|---------|-------------|-------|-------------|-------|")
            for m in matches:
                lines.append(
                    f"| {m['consultant_name']} | {m['project']} | {m['skill_matched']} | "
                    f"{m['level']} | {m['probability']*100:.0f}% | {m['start']} |"
                )
            deployed_ids = {m["consultant_id"] for m in matches}
            deployed_cost = sum(
                BENCH_COST_PER_MONTH.get(CONSULTANTS[cid]["level"], 14000) for cid in deployed_ids
            )
            lines.append(f"\n**Bench cost saved if deployed:** ${deployed_cost:,.0f}/month")
        else:
            lines.append("No direct bench-to-pipeline matches found.\n")

        # Unmatched bench
        matched_ids = {m["consultant_id"] for m in matches}
        unmatched = {cid: c for cid, c in _bench_consultants().items() if cid not in matched_ids}
        if unmatched:
            lines.append("\n### Unmatched Bench Resources\n")
            lines.append("| Consultant | Level | Skills | Recommendation |")
            lines.append("|------------|-------|--------|----------------|")
            for cid, c in unmatched.items():
                rec = "Upskill to cloud/AI" if c["level"] in ("Mid", "Junior") else "Internal innovation project"
                lines.append(f"| {c['name']} | {c['level']} | {', '.join(c['skills'][:2])} | {rec} |")

        # Utilization projection
        bench = _bench_consultants()
        current_util = _firm_utilization()
        deployable = len(matches)
        total = len(CONSULTANTS)
        currently_billable = total - len(bench)
        projected_billable = currently_billable + deployable
        projected_util = round(projected_billable / total * 100 * 0.87, 1)  # weighted avg
        lines.append(f"\n### Projected Utilization Impact")
        lines.append(f"- Current firm utilization: **{current_util}%**")
        lines.append(f"- Projected after deployment: **{projected_util}%**")
        lines.append(f"- Target: **{UTILIZATION_TARGETS['firm_target']}%**")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = ResourceUtilizationAgent()
    for op in agent.metadata["operations"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
