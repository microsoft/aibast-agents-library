"""
Competitive Intelligence Agent for Software/Digital Products.

Provides AI-powered competitive intelligence including market landscape analysis,
feature comparisons, pricing analysis, and threat assessments for SaaS companies
operating in competitive enterprise software markets.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/software-competitive-intel",
    "version": "1.0.0",
    "display_name": "Competitive Intelligence Agent",
    "description": "AI-powered competitive intelligence for SaaS market landscape analysis, feature comparisons, pricing analysis, and threat assessments.",
    "author": "AIBAST",
    "tags": ["competitive-intel", "market-analysis", "saas", "pricing", "threat-assessment"],
    "category": "software_digital_products",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data (fixed, no randomness)
# ---------------------------------------------------------------------------

COMPETITORS = {
    "COMP-001": {
        "name": "DataFlow AI",
        "segment": "Enterprise AI/ML Platform",
        "market_share_pct": 24.3,
        "revenue_mm": 312.0,
        "growth_rate_pct": 41.2,
        "founded_year": 2017,
        "headcount": 1420,
        "funding_mm": 285.0,
        "hq": "San Francisco, CA",
        "features": {
            "automl": True,
            "no_code_ui": True,
            "model_monitoring": True,
            "explainability": False,
            "on_prem_deploy": False,
            "soc2": True,
            "hipaa": False,
            "fedramp": False,
        },
        "pricing_tiers": {
            "starter": 999,
            "professional": 2999,
            "enterprise": 4999,
        },
        "recent_moves": [
            "Launched AutoML 3.0 with 25% price cut",
            "AWS Marketplace native listing",
            "340 new mid-market customers in Q1",
        ],
        "threat_level": "high",
    },
    "COMP-002": {
        "name": "NeuralStack",
        "segment": "Vertical AI Solutions",
        "market_share_pct": 15.8,
        "revenue_mm": 198.0,
        "growth_rate_pct": 28.5,
        "founded_year": 2018,
        "headcount": 870,
        "funding_mm": 195.0,
        "hq": "Boston, MA",
        "features": {
            "automl": True,
            "no_code_ui": False,
            "model_monitoring": True,
            "explainability": True,
            "on_prem_deploy": True,
            "soc2": True,
            "hipaa": True,
            "fedramp": False,
        },
        "pricing_tiers": {
            "starter": 1299,
            "professional": 3299,
            "enterprise": 5999,
        },
        "recent_moves": [
            "Expanded into healthcare vertical",
            "Suffered 4-hour production outage",
            "Acquired NLP startup for $32M",
        ],
        "threat_level": "medium",
    },
    "COMP-003": {
        "name": "Quantum ML",
        "segment": "Open Core ML Platform",
        "market_share_pct": 11.2,
        "revenue_mm": 142.0,
        "growth_rate_pct": 55.8,
        "founded_year": 2019,
        "headcount": 540,
        "funding_mm": 120.0,
        "hq": "Austin, TX",
        "features": {
            "automl": True,
            "no_code_ui": True,
            "model_monitoring": False,
            "explainability": True,
            "on_prem_deploy": True,
            "soc2": False,
            "hipaa": False,
            "fedramp": False,
        },
        "pricing_tiers": {
            "starter": 0,
            "professional": 1999,
            "enterprise": 3999,
        },
        "recent_moves": [
            "Open-sourced core inference engine",
            "Rapid fintech vertical growth",
            "Community reached 48K developers",
        ],
        "threat_level": "medium",
    },
}

OUR_COMPANY = {
    "name": "IntelliStack Technologies",
    "market_share_pct": 18.0,
    "revenue_mm": 228.0,
    "growth_rate_pct": 32.0,
    "features": {
        "automl": True,
        "no_code_ui": False,
        "model_monitoring": True,
        "explainability": True,
        "on_prem_deploy": True,
        "soc2": True,
        "hipaa": True,
        "fedramp": True,
    },
    "pricing_tiers": {
        "starter": 1499,
        "professional": 3499,
        "enterprise": 6999,
    },
    "model_accuracy_pct": 94.2,
    "avg_deal_size": 127000,
    "enterprise_win_rate_pct": 67,
    "midmarket_win_rate_pct": 31,
    "overall_win_rate_pct": 38,
    "data_residency_regions": 12,
}

PRODUCT_ROADMAPS = {
    "COMP-001": [
        {"initiative": "Enterprise SSO integration", "quarter": "Q2 2026", "impact": "high"},
        {"initiative": "On-prem deployment option", "quarter": "Q3 2026", "impact": "high"},
        {"initiative": "Model versioning 2.0", "quarter": "Q2 2026", "impact": "medium"},
    ],
    "COMP-002": [
        {"initiative": "Financial services vertical", "quarter": "Q2 2026", "impact": "medium"},
        {"initiative": "Real-time inference API", "quarter": "Q3 2026", "impact": "high"},
        {"initiative": "Automated compliance reports", "quarter": "Q4 2026", "impact": "medium"},
    ],
    "COMP-003": [
        {"initiative": "SOC2 certification", "quarter": "Q2 2026", "impact": "high"},
        {"initiative": "Managed cloud offering", "quarter": "Q3 2026", "impact": "high"},
        {"initiative": "Plugin marketplace", "quarter": "Q2 2026", "impact": "medium"},
    ],
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _compute_market_landscape():
    """Build market landscape summary from competitor data."""
    total_market = sum(c["revenue_mm"] for c in COMPETITORS.values()) + OUR_COMPANY["revenue_mm"]
    players = []
    for cid, comp in COMPETITORS.items():
        players.append({
            "id": cid,
            "name": comp["name"],
            "market_share_pct": comp["market_share_pct"],
            "revenue_mm": comp["revenue_mm"],
            "growth_rate_pct": comp["growth_rate_pct"],
            "threat_level": comp["threat_level"],
            "recent_moves": comp["recent_moves"],
        })
    players.sort(key=lambda x: x["market_share_pct"], reverse=True)
    return {
        "total_addressable_market_mm": round(total_market / 0.692, 1),
        "our_position": 2,
        "our_share_pct": OUR_COMPANY["market_share_pct"],
        "competitors": players,
    }


def _compute_feature_comparison():
    """Build feature-by-feature comparison grid."""
    feature_labels = {
        "automl": "AutoML",
        "no_code_ui": "No-Code UI",
        "model_monitoring": "Model Monitoring",
        "explainability": "Explainability",
        "on_prem_deploy": "On-Prem Deployment",
        "soc2": "SOC2 Type II",
        "hipaa": "HIPAA Compliance",
        "fedramp": "FedRAMP Authorization",
    }
    rows = []
    for key, label in feature_labels.items():
        row = {"feature": label, "us": OUR_COMPANY["features"].get(key, False)}
        for cid, comp in COMPETITORS.items():
            row[comp["name"]] = comp["features"].get(key, False)
        rows.append(row)
    our_count = sum(1 for v in OUR_COMPANY["features"].values() if v)
    comp_counts = {}
    for cid, comp in COMPETITORS.items():
        comp_counts[comp["name"]] = sum(1 for v in comp["features"].values() if v)
    return {"features": rows, "our_feature_count": our_count, "competitor_counts": comp_counts}


def _compute_pricing_analysis():
    """Compute pricing gaps across tiers."""
    analysis = []
    for tier in ["starter", "professional", "enterprise"]:
        our_price = OUR_COMPANY["pricing_tiers"][tier]
        for cid, comp in COMPETITORS.items():
            their_price = comp["pricing_tiers"][tier]
            gap_pct = round(((our_price - their_price) / their_price) * 100, 1) if their_price > 0 else 0
            analysis.append({
                "tier": tier,
                "competitor": comp["name"],
                "our_price": our_price,
                "their_price": their_price,
                "gap_pct": gap_pct,
            })
    avg_gap = round(sum(a["gap_pct"] for a in analysis) / len(analysis), 1)
    return {"tier_comparison": analysis, "average_gap_pct": avg_gap}


def _compute_threat_assessment():
    """Assess threat level and strategic recommendations per competitor."""
    assessments = []
    for cid, comp in COMPETITORS.items():
        roadmap = PRODUCT_ROADMAPS.get(cid, [])
        high_impact_items = [r for r in roadmap if r["impact"] == "high"]
        assessments.append({
            "competitor": comp["name"],
            "threat_level": comp["threat_level"],
            "market_share_pct": comp["market_share_pct"],
            "growth_rate_pct": comp["growth_rate_pct"],
            "roadmap_high_impact_count": len(high_impact_items),
            "roadmap_items": roadmap,
            "recent_moves": comp["recent_moves"],
        })
    assessments.sort(key=lambda x: x["growth_rate_pct"], reverse=True)
    return {"assessments": assessments, "highest_threat": "DataFlow AI"}


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class CompetitiveIntelAgent(BasicAgent):
    """Competitive intelligence agent for SaaS market analysis."""

    def __init__(self):
        self.name = "@aibast-agents-library/software-competitive-intel"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "market_landscape",
                            "feature_comparison",
                            "pricing_analysis",
                            "threat_assessment",
                        ],
                        "description": "The competitive intelligence operation to perform.",
                    },
                    "competitor_id": {
                        "type": "string",
                        "description": "Optional competitor ID to filter results.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "market_landscape")
        if operation == "market_landscape":
            return self._market_landscape()
        elif operation == "feature_comparison":
            return self._feature_comparison()
        elif operation == "pricing_analysis":
            return self._pricing_analysis()
        elif operation == "threat_assessment":
            return self._threat_assessment()
        return f"**Error:** Unknown operation `{operation}`."

    # ------------------------------------------------------------------
    def _market_landscape(self) -> str:
        data = _compute_market_landscape()
        lines = [
            "# Competitive Market Landscape",
            "",
            f"**Total Addressable Market:** ${data['total_addressable_market_mm']:.0f}M",
            f"**Our Position:** #{data['our_position']} with {data['our_share_pct']}% share",
            "",
            "| Rank | Competitor | Share | Revenue | Growth | Threat |",
            "|------|-----------|-------|---------|--------|--------|",
        ]
        for i, c in enumerate(data["competitors"], 1):
            threat_icon = "HIGH" if c["threat_level"] == "high" else "MED"
            lines.append(
                f"| {i} | {c['name']} | {c['market_share_pct']}% | ${c['revenue_mm']:.0f}M "
                f"| {c['growth_rate_pct']}% | {threat_icon} |"
            )
        lines.append("")
        lines.append("## Recent Competitor Moves")
        for c in data["competitors"]:
            lines.append(f"\n**{c['name']}**")
            for move in c["recent_moves"]:
                lines.append(f"- {move}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _feature_comparison(self) -> str:
        data = _compute_feature_comparison()
        comp_names = [c["name"] for c in COMPETITORS.values()]
        header = "| Feature | Us | " + " | ".join(comp_names) + " |"
        sep = "|---------|----| " + " | ".join(["---"] * len(comp_names)) + " |"
        lines = ["# Feature Comparison Matrix", "", header, sep]
        for row in data["features"]:
            us_val = "YES" if row["us"] else "NO"
            cells = [us_val]
            for cn in comp_names:
                cells.append("YES" if row.get(cn, False) else "NO")
            lines.append(f"| {row['feature']} | " + " | ".join(cells) + " |")
        lines.append("")
        lines.append(f"**Our Feature Coverage:** {data['our_feature_count']}/8")
        for name, count in data["competitor_counts"].items():
            lines.append(f"- {name}: {count}/8")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _pricing_analysis(self) -> str:
        data = _compute_pricing_analysis()
        lines = [
            "# Pricing Analysis",
            "",
            f"**Average Price Gap:** {data['average_gap_pct']}% above competitors",
            "",
            "| Tier | Competitor | Our Price | Their Price | Gap |",
            "|------|-----------|-----------|-------------|-----|",
        ]
        for row in data["tier_comparison"]:
            lines.append(
                f"| {row['tier'].title()} | {row['competitor']} "
                f"| ${row['our_price']:,}/mo | ${row['their_price']:,}/mo | {row['gap_pct']:+.1f}% |"
            )
        lines.append("")
        lines.append("## Recommendations")
        lines.append("- Consider matching enterprise tier pricing to defend large accounts.")
        lines.append("- Evaluate a free/community tier to compete with open-core entrants.")
        lines.append("- Emphasize compliance value to justify premium in regulated verticals.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _threat_assessment(self) -> str:
        data = _compute_threat_assessment()
        lines = [
            "# Threat Assessment",
            "",
            f"**Highest Overall Threat:** {data['highest_threat']}",
            "",
        ]
        for a in data["assessments"]:
            level_label = "HIGH" if a["threat_level"] == "high" else "MEDIUM"
            lines.append(f"## {a['competitor']} [{level_label}]")
            lines.append(f"- Market Share: {a['market_share_pct']}%")
            lines.append(f"- Growth Rate: {a['growth_rate_pct']}%")
            lines.append(f"- High-Impact Roadmap Items: {a['roadmap_high_impact_count']}")
            lines.append("")
            lines.append("**Roadmap:**")
            for item in a["roadmap_items"]:
                lines.append(f"- [{item['quarter']}] {item['initiative']} (impact: {item['impact']})")
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = CompetitiveIntelAgent()
    ops = ["market_landscape", "feature_comparison", "pricing_analysis", "threat_assessment"]
    for op in ops:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        result = agent.perform(operation=op)
        print(result)
