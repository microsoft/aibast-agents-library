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
    "version": "1.1.0",
    "display_name": "Resource Utilization Agent",
    "description": "Provide intelligent resource analysis and recommendations to maximize billable utilization and reduce costs.",
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

WORKFORCE_PATHS = {
    "CON-408": {
        "path": "D365 integration accelerator",
        "duration_weeks": 4,
        "training_cost": 3200,
        "target_demand": "FinanceHub Cloud Migration integration work",
        "monthly_value_at_rate": 31200,
    },
}

# Firm-wide scenario (the demo default). The named roster above is a sample of these 200 consultants.
FIRM_PROFILE = {
    "headcount": 200,
    "billable": 144,
    "target_pct": 85,
    "bench_by_level": [
        {"level": "Senior consultants", "count": 12, "avg_rate_hr": 275, "monthly_cost_per_head": 22000},
        {"level": "Mid-level", "count": 28, "avg_rate_hr": 175, "monthly_cost_per_head": 14000},
        {"level": "Junior/analysts", "count": 16, "avg_rate_hr": 125, "monthly_cost_per_head": 10000},
    ],
    "bench_overhead_monthly": 24000,
    "skill_surplus": "8 data analysts (market oversaturated)",
    "critical_gap": "Need 5 cloud architects for pipeline",
    "upskilling_opportunity": "8 completing cloud certs this month",
}

# Deployment tiers for the bench (15 confirmed + 8 high-probability + 7 innovation + 4 upskilling = 34 viable).
DEPLOYMENT_PIPELINE = {
    "Week 1 Confirmed Starts": [
        ("TechCorp transformation", "4 senior + 3 mid-level", 7),
        ("FinanceHub cloud migration", "3 cloud architects", 3),
        ("RetailCo analytics", "2 data analysts", 2),
        ("Manufacturing ERP", "3 consultants", 3),
    ],
    "High Probability (75%+)": [
        ("Healthcare digital", "3 mid-level (proposal stage)", 3),
        ("Energy modernization", "2 senior (verbal approval)", 2),
        ("Logistics optimization", "3 analysts (contract review)", 3),
    ],
    "Innovation Projects (billable to R&D)": [
        ("Internal tools development", "3 consultants", 3),
        ("Methodology enhancement", "2 consultants", 2),
        ("Accelerator creation", "2 consultants", 2),
    ],
}
UPSKILLING_TRACK = 4  # near certification; deployable after the 90-day window starts

SHADOW_COHORT = {
    "consultants": 5,
    "profile": "mid-level infrastructure consultants 80% through cloud certifications",
    "certifications": [("cloud certifications", 3), ("platform certifications", 2)],
    "time_to_cert": "12-18 days",
    "experience": "All have 5+ years infrastructure experience",
    "rate_now": 175,
    "rate_after": 250,
    "days_to_premium": 30,
    "clients_preapproved": 3,
    "training_cost": 15000,
    "roi_12_months_pct": 580,
}

FINANCIAL_MODEL = {
    "monthly_bench_savings": 390000,
    "monthly_new_revenue": 1290000,
    "gross_margin_before_pct": 8.5,
    "gross_margin_after_pct": 14.2,
}

_GATE = ("Synthetic planning scenario; recommendations only. No consultant was assigned, no employment "
         "status changed, no revenue was booked, and no dashboard or report was deployed or sent.")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _k(value):
    """$264K style."""
    return f"${value // 1000:,}K"


def _firm_numbers():
    f = FIRM_PROFILE
    bench = sum(b["count"] for b in f["bench_by_level"])
    cost = sum(b["count"] * b["monthly_cost_per_head"] for b in f["bench_by_level"]) + f["bench_overhead_monthly"]
    target = f["headcount"] * f["target_pct"] // 100
    tiers = {name: sum(n for _, _, n in rows) for name, rows in DEPLOYMENT_PIPELINE.items()}
    return {"bench": bench, "cost": cost, "target": target, "needed": target - f["billable"],
            "current_pct": f["billable"] * 100 // f["headcount"], "tiers": tiers,
            "confirmed": tiers["Week 1 Confirmed Starts"], "pipeline": tiers["High Probability (75%+)"],
            "innovation": tiers["Innovation Projects (billable to R&D)"]}


def _money_m(value):
    return f"${value / 1_000_000:.1f}M"

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

_OPERATIONS = [
    "utilization_dashboard", "capacity_forecast", "bench_analysis", "staffing_recommendation",
    "workforce_plan", "optimization_plan", "financial_impact", "executive_summary",
]


class ResourceUtilizationAgent(BasicAgent):
    """Tracks consultant utilization and generates staffing plans."""

    def __init__(self):
        self.name = "ResourceUtilizationAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "The professional-services resource and capacity agent. For the board goal "
                "('utilization to 85%, 200 consultants at 72% billable, need an optimization plan') "
                "use optimization_plan first; 'where the expensive capacity is sitting idle' uses "
                "bench_analysis; 'confirmed project pipeline' uses staffing_recommendation; the "
                "skill mismatch / 5 cloud architects uses workforce_plan; 'complete financial "
                "impact' uses financial_impact; 'create tracking dashboard and summarize' uses "
                "executive_summary. Call it first; every operation has demo defaults. Use it for firm and "
                "level utilization, upcoming availability, bench cost and skill inventory, "
                "pipeline staffing matches, or upskilling and innovation planning. Use "
                "utilization_dashboard for the current portfolio, capacity_forecast for the "
                "next ninety days, bench_analysis for available talent and cost, "
                "staffing_recommendation for skill-and-level matches to weighted pipeline, and "
                "workforce_plan for unmatched-resource pathways and synthetic upskilling ROI. "
                "It recommends options only and never assigns people, changes employment "
                "status, books revenue, or contacts employees or clients."
            ),
            "operations": list(_OPERATIONS),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "utilization_dashboard: show current utilization, targets, and "
                            "availability. capacity_forecast: compare upcoming project endings "
                            "with weighted pipeline demand. bench_analysis: inventory bench "
                            "skills and synthetic carrying cost. staffing_recommendation: match "
                            "qualified available consultants to pipeline needs. workforce_plan: "
                            "model upskilling and internal-innovation options for unmatched "
                            "resources without making assignments; leads with the cloud-architect "
                            "shadow model for the skill mismatch. optimization_plan: the default; "
                            "plan to lift utilization from 72% to 85%. financial_impact: monthly, "
                            "quarterly and annual value and margin. executive_summary: summarize the "
                            "session and draft the tracking dashboard specification."
                        ),
                    }
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation") or "optimization_plan"
        dispatch = {
            "optimization_plan": self._optimization_plan,
            "financial_impact": self._financial_impact,
            "executive_summary": self._executive_summary,
            "utilization_dashboard": self._utilization_dashboard,
            "capacity_forecast": self._capacity_forecast,
            "bench_analysis": self._bench_analysis,
            "staffing_recommendation": self._staffing_recommendation,
            "workforce_plan": self._workforce_plan,
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
        lines.append("\n> Synthetic planning snapshot; utilization is not a live PSA reading.")
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
        lines.append("\n> Pipeline probabilities are synthetic planning inputs, not committed work.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _bench_analysis(self, **kwargs) -> str:
        f, n = FIRM_PROFILE, _firm_numbers()
        senior = f["bench_by_level"][0]
        lines = [f"Your biggest cost drain is {senior['count']} senior consultants at ${senior['avg_rate_hr']}/hour "
                 f"average - that's {_k(senior['count'] * senior['monthly_cost_per_head'])} monthly on the bench.\n",
                 "## Bench Breakdown by Level\n",
                 "| Level | Count | Avg Rate | Monthly Cost |", "|---|---|---|---|"]
        for b in f["bench_by_level"]:
            lines.append(f"| {b['level']} | {b['count']} | ${b['avg_rate_hr']}/hr | {_k(b['count'] * b['monthly_cost_per_head'])} |")
        lines.append(f"| Bench overhead (training, tools) | | | {_k(f['bench_overhead_monthly'])} |")
        lines.append(f"| **Total bench ({n['bench']})** | | | **{_k(n['cost'])}** |\n")
        lines.append("### Critical Findings\n")
        lines.append(f"- **Skill surplus:** {f['skill_surplus']}")
        lines.append(f"- **Critical gap:** {f['critical_gap']}")
        lines.append(f"- **Upskilling opportunity:** {f['upskilling_opportunity']}")
        lines.append("\n**Senior Bench Problem:** Cloud architects and transformation leads billing at premium rates "
                     "sitting idle while pipeline needs exactly these skills.\n")
        lines.append("Source: [Synthetic skills database + market analysis]\n")
        lines.append("**Next step:** Want to see the confirmed project pipeline?\n")
        lines.append("## Bench Analysis (named sample of the bench)\n")
        bench = _bench_consultants()
        monthly_cost = _monthly_bench_cost()
        lines.append(f"**Bench headcount:** {len(bench)}")
        lines.append(f"**Monthly bench cost:** ${monthly_cost:,.0f}")
        lines.append(f"**Annualized bench cost:** ${monthly_cost * 12:,.0f}\n")

        lines.append("| ID | Name | Level | Rate/Hr | Skills | Monthly Cost |")
        lines.append("|----|------|-------|---------|--------|-------------|")
        for cid, c in bench.items():
            mc = BENCH_COST_PER_MONTH.get(c["level"], 14000)
            skills = ", ".join(c["skills"][:2])
            lines.append(
                f"| {cid} | {c['name']} | {c['level']} | ${c['rate_hr']} | {skills} | ${mc:,.0f} |"
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
        lines.append("\n> Opportunity values are synthetic scenarios; no deployment or revenue is committed.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _staffing_recommendation(self, **kwargs) -> str:
        n = _firm_numbers()
        immediate = n["confirmed"] + n["pipeline"]
        deployed = immediate + n["innovation"]
        lines = [f"{immediate} consultants can deploy immediately through confirmed projects and high-probability "
                 f"pipeline - that's {immediate * 100 // n['needed']}% of your {n['needed']}-person target.\n",
                 "## Deployment Pipeline\n"]
        for tier, rows in DEPLOYMENT_PIPELINE.items():
            lines.append(f"### {tier}: {n['tiers'][tier]} consultants")
            for name, detail, _ in rows:
                lines.append(f"- {name}: {detail}")
            lines.append("")
        lines.append(f"**Total: {deployed} deployed vs {n['needed']} needed = {deployed - n['needed']} buffer** "
                     f"(projected utilization {(FIRM_PROFILE['billable'] + deployed) * 100 // FIRM_PROFILE['headcount']}%)\n")
        lines.append("Source: [Synthetic sales pipeline + project forecasting]\n")
        lines.append("**Next step:** How do we address the 5 cloud architects we need?\n")
        lines.append("## Staffing Recommendations (named sample)\n")
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
        deployable = len({m["consultant_id"] for m in matches})
        total = len(CONSULTANTS)
        currently_billable = total - len(bench)
        current_util = round(currently_billable / total * 100, 1)
        projected_billable = currently_billable + deployable
        projected_util = round(projected_billable / total * 100, 1)
        lines.append(f"\n### Projected Utilization Impact (named sample)")
        lines.append(f"- Current sample billable share: **{current_util}%**")
        lines.append(f"- Projected after deployment: **{projected_util}%**")
        lines.append(f"- Target: **{UTILIZATION_TARGETS['firm_target']}%**")
        lines.append("\n> Recommendations require resource-manager confirmation; no assignment was made.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _workforce_plan(self, **kwargs) -> str:
        c = SHADOW_COHORT
        lines = [f"I've identified {c['consultants']} {c['profile']} - they can shadow senior architects immediately "
                 f"and bill at mid-tier rates now, premium rates in {c['days_to_premium']} days.\n",
                 "## Upskilling Strategy\n", "**Near-Ready Resources:**"]
        for cert, count in c["certifications"]:
            lines.append(f"- {count} completing {cert} ({c['time_to_cert']})")
        lines.append(f"- {c['experience']}\n")
        lines.append("**Shadow Model:**")
        lines.append("- Pair with billable senior cloud architects now")
        lines.append(f"- Bill at ${c['rate_now']}/hr (mid-level) immediately")
        lines.append(f"- Upgrade to ${c['rate_after']}/hr (architect) in {c['days_to_premium']} days post-cert\n")
        lines.append(f"**Client Acceptance:** {c['clients_preapproved']} clients pre-approved shadow arrangements\n")
        lines.append("**Financial Impact:**")
        lines.append(f"- Training investment: {_k(c['training_cost'])} (already budgeted)")
        lines.append(f"- Immediate revenue: ${c['rate_now']}/hr billable now")
        lines.append(f"- Future premium: ${c['rate_after']}/hr in {c['days_to_premium']} days")
        lines.append(f"- ROI: {c['roi_12_months_pct']}% over 12 months\n")
        lines.append("Source: [Synthetic skills database + certification tracker]\n")
        lines.append("**Next step:** Want to see the total financial impact?\n")
        lines.append("## Strategic Workforce Plan (named sample)\n")
        lines.append("### Upskilling Pathways\n")
        lines.append("| Consultant | Path | Duration | Cost | Target Demand | Monthly Scenario Value |")
        lines.append("|------------|------|----------|------|---------------|------------------------|")
        for cid, path in WORKFORCE_PATHS.items():
            consultant = CONSULTANTS[cid]
            lines.append(
                f"| {consultant['name']} | {path['path']} | {path['duration_weeks']} weeks | "
                f"${path['training_cost']:,.0f} | {path['target_demand']} | "
                f"${path['monthly_value_at_rate']:,.0f} |"
            )
            payback_days = round(path["training_cost"] * 30 / path["monthly_value_at_rate"])
            lines.append(
                f"\n**Synthetic payback scenario for {consultant['name']}:** about "
                f"{payback_days} days of billable deployment after the pathway."
            )
        lines.append("\n### Innovation and Capability-Building Options\n")
        lines.append("- Robert Garcia: contribute to the D365 integration accelerator while completing the pathway.")
        lines.append("- Sarah Kim: document reusable Terraform patterns between pipeline staffing decisions.")
        lines.append("- Chen Wei: prototype an internal AI delivery playbook if the retail opportunity does not proceed.")
        lines.append(
            "\n> Scenario modeling only; training, internal work, staffing, and financial "
            "benefits require leadership approval and validated demand."
        )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _optimization_plan(self, **kwargs) -> str:
        f, n, m = FIRM_PROFILE, _firm_numbers(), FINANCIAL_MODEL
        viable = n["confirmed"] + n["pipeline"] + n["innovation"] + UPSKILLING_TRACK
        quarterly = (m["monthly_bench_savings"] + m["monthly_new_revenue"]) * 3
        return (
            f"I've analyzed your {f['headcount']}-person consulting team and identified viable paths to deploy "
            f"{viable} of the {n['bench']} bench consultants - exceeding your {n['needed']}-person target to hit "
            f"{f['target_pct']}%.\n\n"
            "## Current State\n\n"
            "| Metric | Current | Target |\n|---|---|---|\n"
            f"| Total consultants | {f['headcount']} | {f['headcount']} |\n"
            f"| Currently billable | {f['billable']} ({n['current_pct']}%) | {n['target']} ({f['target_pct']}%) |\n"
            f"| Bench resources | {n['bench']} | {n['bench'] - n['needed']} |\n"
            f"| Monthly bench cost | {_k(n['cost'])} | |\n\n"
            "## Deployment Opportunities\n\n"
            f"- Confirmed projects: {n['confirmed']} start next week (easy wins)\n"
            f"- Pipeline (75% probability): {n['pipeline']} consultants\n"
            f"- Innovation projects: {n['innovation']} billable to R&D budget\n"
            f"- Upskilling track: {UPSKILLING_TRACK} near certification\n\n"
            f"**Impact:** {_k(m['monthly_bench_savings'])} monthly savings + {_money_m(m['monthly_new_revenue'])} "
            f"additional revenue = {_money_m(quarterly)} quarterly improvement\n\n"
            "Quality guardrail: only skill-and-level matches are proposed; every placement needs resource-manager "
            "confirmation.\n\n"
            "Source: [Synthetic Workday + D365 HR + pipeline data]\n\n"
            "**Next step:** Should I break down the bench by seniority and cost?\n\n"
            f"> {_GATE}"
        )

    # ------------------------------------------------------------------
    def _financial_impact(self, **kwargs) -> str:
        m = FINANCIAL_MODEL
        monthly = m["monthly_bench_savings"] + m["monthly_new_revenue"]
        c = SHADOW_COHORT
        return (
            "## Complete Financial Impact\n\n"
            "| Horizon | Value |\n|---|---|\n"
            f"| Monthly cost savings (bench) | {_k(m['monthly_bench_savings'])} |\n"
            f"| Monthly new revenue | ${m['monthly_new_revenue'] / 1_000_000:.2f}M |\n"
            f"| Monthly improvement | ${monthly / 1_000_000:.2f}M |\n"
            f"| Quarterly contribution improvement | {_money_m(monthly * 3)} |\n"
            f"| Annual bottom-line impact | {_money_m(monthly * 12)} |\n"
            f"| Gross margin | {m['gross_margin_before_pct']}% -> {m['gross_margin_after_pct']}% |\n\n"
            f"Includes the cloud-architect shadow model ({_k(c['training_cost'])} training, "
            f"{c['roi_12_months_pct']}% ROI over 12 months).\n\n"
            "Source: [Synthetic finance model + pipeline data]\n\n"
            "**Next step:** Shall I create the tracking dashboard and summarize what we accomplished?\n\n"
            f"> {_GATE}"
        )

    # ------------------------------------------------------------------
    def _executive_summary(self, **kwargs) -> str:
        f, n, m = FIRM_PROFILE, _firm_numbers(), FINANCIAL_MODEL
        viable = n["confirmed"] + n["pipeline"] + n["innovation"] + UPSKILLING_TRACK
        deployed = n["confirmed"] + n["pipeline"] + n["innovation"]
        monthly = m["monthly_bench_savings"] + m["monthly_new_revenue"]
        senior = f["bench_by_level"][0]
        immediate = n["confirmed"] + n["pipeline"]
        return (
            "Tracking dashboard specification ready for Power BI with weekly reporting (draft; not deployed). "
            "Here's everything we covered:\n\n"
            "## Session Summary\n\n"
            f"- **Gap analysis:** {n['current_pct']}% -> {f['target_pct']}% requires {n['needed']} consultants, identified {viable} viable\n"
            f"- **Bench breakdown:** {_k(senior['count'] * senior['monthly_cost_per_head'])} senior cost drain, skill surplus/gaps mapped\n"
            f"- **Deployment plan:** {n['confirmed']} confirmed + {n['pipeline']} pipeline + {n['innovation']} innovation = {deployed} total\n"
            f"- **Upskilling strategy:** {SHADOW_COHORT['consultants']} cloud architects via shadow model in {SHADOW_COHORT['days_to_premium']} days\n"
            f"- **Financial model:** ${monthly / 1_000_000:.2f}M monthly improvement, {_money_m(monthly * 3)} quarterly\n"
            "- **Executive dashboard:** weekly tracking with red/yellow/green status\n\n"
            "## Value Created\n\n"
            f"- Monthly: {_k(m['monthly_bench_savings'])} cost savings + ${m['monthly_new_revenue'] / 1_000_000:.2f}M new revenue\n"
            f"- Quarterly: {_money_m(monthly * 3)} contribution improvement\n"
            f"- Annual: {_money_m(monthly * 12)} bottom-line impact\n"
            f"- Margin: {m['gross_margin_before_pct']}% -> {m['gross_margin_after_pct']}% gross margin\n\n"
            "## Dashboard Specification (draft)\n\n"
            "| KPI | Green | Yellow | Red |\n|---|---|---|---|\n"
            f"| Firm utilization | >= {f['target_pct']}% | 80-84% | < 80% |\n"
            f"| Consultants deployed vs plan | >= {deployed} | {n['needed']}-{deployed - 1} | < {n['needed']} |\n"
            f"| Bench cost (monthly) | <= {_k(n['cost'] - m['monthly_bench_savings'])} | | > {_k(n['cost'])} |\n\n"
            f"Cadence: Monday report to leadership (draft for you to schedule); deployment tracker at {immediate * 100 // n['needed']}% of "
            f"target with buffer for an {f['target_pct']}% landing.\n\n"
            "Source: [Synthetic session outputs]\n\n"
            f"> {_GATE}"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = ResourceUtilizationAgent()
    for op in ["optimization_plan", "bench_analysis", "staffing_recommendation", "workforce_plan",
               "financial_impact", "executive_summary"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
