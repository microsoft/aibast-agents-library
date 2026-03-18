"""
Proposal Copilot Agent

Assists professional-services teams in building competitive proposals by
analyzing RFP requirements, generating pricing models, evaluating win
themes from past proposal history, and positioning against known
competitors.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/proposal-copilot",
    "version": "1.0.0",
    "display_name": "Proposal Copilot Agent",
    "description": "Generates competitive proposals with pricing models, win-theme analysis from historical data, and competitive positioning against known bidders.",
    "author": "AIBAST",
    "tags": ["proposal", "RFP", "pricing", "competitive-intelligence", "professional-services"],
    "category": "professional_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

RFP_REQUIREMENTS = {
    "RFP-2026-047": {
        "client": "GlobalManufacture Corp",
        "title": "Enterprise Digital Transformation",
        "budget": 10000000,
        "timeline_months": 18,
        "decision_date": "2026-04-12",
        "decision_makers": ["CIO", "CFO", "COO"],
        "scope_areas": [
            "ERP modernization across 14 sites",
            "Data platform and analytics",
            "Process automation",
            "Change management and training",
        ],
        "evaluation_criteria": {
            "technical_approach": 35,
            "past_performance": 25,
            "pricing": 25,
            "management_approach": 15,
        },
        "competitors": ["BigFour Consulting", "Global Advisory Group"],
    },
    "RFP-2026-048": {
        "client": "Summit Health Network",
        "title": "Clinical Workflow Optimization",
        "budget": 4500000,
        "timeline_months": 12,
        "decision_date": "2026-05-01",
        "decision_makers": ["CMIO", "VP Operations", "CFO"],
        "scope_areas": [
            "Clinical pathway redesign",
            "EHR workflow optimization",
            "Staff scheduling automation",
            "Patient throughput analytics",
        ],
        "evaluation_criteria": {
            "clinical_expertise": 40,
            "technical_approach": 25,
            "pricing": 20,
            "references": 15,
        },
        "competitors": ["HealthTech Solutions", "MedConsult Group"],
    },
}

PRICING_TEMPLATES = {
    "digital_transformation": {
        "assessment_pct": 8,
        "implementation_pct": 55,
        "data_analytics_pct": 18,
        "change_mgmt_pct": 12,
        "project_mgmt_pct": 7,
        "margin_target_pct": 32,
        "discount_threshold_pct": 15,
    },
    "clinical_optimization": {
        "discovery_pct": 10,
        "redesign_pct": 30,
        "technology_pct": 25,
        "training_pct": 20,
        "project_mgmt_pct": 15,
        "margin_target_pct": 28,
        "discount_threshold_pct": 10,
    },
}

PAST_PROPOSALS = [
    {"rfp": "AutoComponents Inc", "value": 8200000, "result": "Won", "win_themes": ["Industry accelerators", "Former client staff", "Aggressive timeline"],
     "competitor_beaten": "BigFour Consulting", "margin_pct": 34},
    {"rfp": "TechManufacturing Global", "value": 6500000, "result": "Won", "win_themes": ["14-site rollout experience", "Quick wins strategy"],
     "competitor_beaten": "Global Advisory Group", "margin_pct": 29},
    {"rfp": "Precision Parts Ltd", "value": 3800000, "result": "Won", "win_themes": ["On-time delivery track record", "Domain expertise"],
     "competitor_beaten": "Boutique Firm", "margin_pct": 31},
    {"rfp": "National Bank Corp", "value": 7100000, "result": "Lost", "win_themes": ["Price competitive"],
     "competitor_beaten": None, "margin_pct": 26, "loss_reason": "Incumbent advantage; client stayed with existing vendor"},
    {"rfp": "RetailGroup Holdings", "value": 5400000, "result": "Lost", "win_themes": ["Innovative approach"],
     "competitor_beaten": None, "margin_pct": 22, "loss_reason": "Budget reduced; chose lower-cost option"},
]

COMPETITOR_INTEL = {
    "BigFour Consulting": {
        "avg_price_premium_pct": 25,
        "strengths": ["Brand recognition", "Global reach", "Deep bench"],
        "weaknesses": ["High cost", "Junior staff on projects", "Slow to mobilize"],
        "typical_margin_pct": 40,
        "win_rate_against": 0.67,
    },
    "Global Advisory Group": {
        "avg_price_premium_pct": 18,
        "strengths": ["Strong analytics practice", "Government relationships"],
        "weaknesses": ["Limited manufacturing experience", "High turnover"],
        "typical_margin_pct": 35,
        "win_rate_against": 0.60,
    },
    "HealthTech Solutions": {
        "avg_price_premium_pct": 5,
        "strengths": ["Clinical domain expertise", "EHR certifications"],
        "weaknesses": ["Small team", "Limited scalability", "No change management practice"],
        "typical_margin_pct": 30,
        "win_rate_against": 0.50,
    },
    "MedConsult Group": {
        "avg_price_premium_pct": 10,
        "strengths": ["Strong physician network", "CMIO relationships"],
        "weaknesses": ["Technology integration gaps", "Limited data analytics capability"],
        "typical_margin_pct": 32,
        "win_rate_against": 0.55,
    },
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _win_rate():
    """Overall win rate from past proposals."""
    wins = sum(1 for p in PAST_PROPOSALS if p["result"] == "Won")
    return round(wins / len(PAST_PROPOSALS) * 100, 1)


def _avg_margin():
    """Average margin on won proposals."""
    won = [p for p in PAST_PROPOSALS if p["result"] == "Won"]
    if not won:
        return 0
    return round(sum(p["margin_pct"] for p in won) / len(won), 1)


def _top_win_themes():
    """Aggregate win themes from won proposals."""
    themes = {}
    for p in PAST_PROPOSALS:
        if p["result"] == "Won":
            for t in p["win_themes"]:
                themes[t] = themes.get(t, 0) + 1
    return sorted(themes.items(), key=lambda x: x[1], reverse=True)


def _pricing_breakdown(template_key, budget):
    """Generate a pricing breakdown from a template and budget."""
    tpl = PRICING_TEMPLATES.get(template_key, {})
    result = {}
    for key, pct in tpl.items():
        if key.endswith("_pct") and key not in ("margin_target_pct", "discount_threshold_pct"):
            label = key.replace("_pct", "").replace("_", " ").title()
            result[label] = round(budget * pct / 100, 2)
    return result


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class ProposalCopilotAgent(BasicAgent):
    """Generates competitive proposals with pricing and win-theme analysis."""

    def __init__(self):
        self.name = "ProposalCopilotAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "operations": [
                "generate_proposal",
                "pricing_model",
                "win_theme_analysis",
                "competitive_positioning",
            ],
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "generate_proposal")
        dispatch = {
            "generate_proposal": self._generate_proposal,
            "pricing_model": self._pricing_model,
            "win_theme_analysis": self._win_theme_analysis,
            "competitive_positioning": self._competitive_positioning,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)

    # ------------------------------------------------------------------
    def _generate_proposal(self, **kwargs) -> str:
        lines = ["## Active RFP Pipeline\n"]
        for rfp_id, rfp in RFP_REQUIREMENTS.items():
            lines.append(f"### {rfp_id} -- {rfp['client']}: {rfp['title']}")
            lines.append(f"- **Budget:** ${rfp['budget']:,.0f}")
            lines.append(f"- **Timeline:** {rfp['timeline_months']} months")
            lines.append(f"- **Decision date:** {rfp['decision_date']}")
            lines.append(f"- **Decision makers:** {', '.join(rfp['decision_makers'])}")
            lines.append(f"- **Competitors:** {', '.join(rfp['competitors'])}")
            lines.append("\n**Scope areas:**")
            for area in rfp["scope_areas"]:
                lines.append(f"- {area}")
            lines.append("\n**Evaluation weights:**")
            lines.append("| Criterion | Weight |")
            lines.append("|-----------|--------|")
            for crit, weight in rfp["evaluation_criteria"].items():
                label = crit.replace("_", " ").title()
                lines.append(f"| {label} | {weight}% |")
            lines.append("")

        lines.append(f"\n**Our overall win rate:** {_win_rate()}%")
        lines.append(f"**Our average margin on wins:** {_avg_margin()}%")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _pricing_model(self, **kwargs) -> str:
        lines = ["## Pricing Models\n"]
        models = [
            ("RFP-2026-047", "digital_transformation", RFP_REQUIREMENTS["RFP-2026-047"]),
            ("RFP-2026-048", "clinical_optimization", RFP_REQUIREMENTS["RFP-2026-048"]),
        ]
        for rfp_id, tpl_key, rfp in models:
            breakdown = _pricing_breakdown(tpl_key, rfp["budget"])
            tpl = PRICING_TEMPLATES[tpl_key]
            our_price = round(rfp["budget"] * (100 - tpl["discount_threshold_pct"]) / 100)
            lines.append(f"### {rfp_id} -- {rfp['client']}")
            lines.append(f"- **Client budget:** ${rfp['budget']:,.0f}")
            lines.append(f"- **Our proposed price:** ${our_price:,.0f}")
            lines.append(f"- **Target margin:** {tpl['margin_target_pct']}%\n")
            lines.append("| Phase | Allocation |")
            lines.append("|-------|-----------|")
            for label, amount in breakdown.items():
                lines.append(f"| {label} | ${amount:,.0f} |")
            lines.append(f"| **Total** | **${our_price:,.0f}** |")
            lines.append(f"\n**Pricing advantage vs competitors:** ${rfp['budget'] - our_price:,.0f} below budget")
            lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _win_theme_analysis(self, **kwargs) -> str:
        lines = ["## Win Theme Analysis\n"]
        lines.append("### Historical Performance\n")
        lines.append("| Proposal | Value | Result | Margin | Themes |")
        lines.append("|----------|-------|--------|--------|--------|")
        for p in PAST_PROPOSALS:
            themes_str = "; ".join(p["win_themes"][:2])
            lines.append(
                f"| {p['rfp']} | ${p['value']:,.0f} | **{p['result']}** | {p['margin_pct']}% | {themes_str} |"
            )

        lines.append(f"\n**Win rate:** {_win_rate()}%")
        lines.append(f"**Average winning margin:** {_avg_margin()}%\n")

        top_themes = _top_win_themes()
        lines.append("### Top Win Themes (from won proposals)\n")
        lines.append("| Theme | Frequency |")
        lines.append("|-------|-----------|")
        for theme, count in top_themes:
            lines.append(f"| {theme} | {count} |")

        lines.append("\n### Loss Analysis\n")
        for p in PAST_PROPOSALS:
            if p["result"] == "Lost":
                lines.append(f"- **{p['rfp']}** (${p['value']:,.0f}): {p.get('loss_reason', 'Unknown')}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _competitive_positioning(self, **kwargs) -> str:
        lines = ["## Competitive Positioning\n"]
        for comp, intel in COMPETITOR_INTEL.items():
            lines.append(f"### {comp}")
            lines.append(f"- **Our win rate against:** {intel['win_rate_against']*100:.0f}%")
            lines.append(f"- **Their price premium:** +{intel['avg_price_premium_pct']}% vs us")
            lines.append(f"- **Their typical margin:** {intel['typical_margin_pct']}%")
            lines.append("\n**Strengths to counter:**")
            for s in intel["strengths"]:
                lines.append(f"- {s}")
            lines.append("\n**Weaknesses to exploit:**")
            for w in intel["weaknesses"]:
                lines.append(f"- {w}")
            lines.append("")

        lines.append("### Positioning Summary\n")
        lines.append("| Competitor | Price Premium | Win Rate | Key Differentiator |")
        lines.append("|------------|-------------|----------|-------------------|")
        for comp, intel in COMPETITOR_INTEL.items():
            diff = intel["weaknesses"][0] if intel["weaknesses"] else "N/A"
            lines.append(
                f"| {comp} | +{intel['avg_price_premium_pct']}% | {intel['win_rate_against']*100:.0f}% | Target: {diff} |"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = ProposalCopilotAgent()
    for op in agent.metadata["operations"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
