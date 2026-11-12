"""
Competitive Intelligence Agent

Analyzes competitive landscapes, reviews win/loss records, generates
positioning guides, and builds battlecards for enterprise B2B sales
engagements. Provides actionable competitive insights and counter-
positioning strategies.

Where a real deployment would call competitive intelligence platforms
and CRM APIs, this agent uses a synthetic data layer so it runs anywhere
without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent
import json
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/competitive-intelligence",
    "version": "1.0.0",
    "display_name": "Competitive Intelligence",
    "description": "Analyzes competitive landscapes, win/loss patterns, and generates battlecards for enterprise deals.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "competitive-intelligence", "battlecards", "win-loss"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_ACCOUNTS = {
    "acme": {"id": "acc-001", "name": "Acme Corporation", "industry": "Manufacturing", "opportunity_value": 2_400_000},
    "contoso": {"id": "acc-002", "name": "Contoso Ltd", "industry": "Technology", "opportunity_value": 1_100_000},
    "fabrikam": {"id": "acc-003", "name": "Fabrikam Industries", "industry": "Manufacturing", "opportunity_value": 890_000},
    "northwind": {"id": "acc-004", "name": "Northwind Traders", "industry": "Retail", "opportunity_value": 540_000},
}

_COMPETITORS = {
    "acme": [
        {
            "name": "DataForge Solutions", "relationship": "Medium", "product_fit": 78,
            "pricing": "-15% below market", "impl_weeks": 14,
            "activity": "On-site demo last week, aggressive discount offered",
            "strengths": ["Lower upfront cost", "Established in automotive manufacturing", "Local implementation team"],
            "weaknesses": ["Limited API ecosystem", "No real-time analytics", "Poor mobile experience"],
        },
        {
            "name": "CloudOps Platform", "relationship": "Weak", "product_fit": 82,
            "pricing": "+10% above market", "impl_weeks": 10,
            "activity": "Early conversations only, no formal proposal",
            "strengths": ["Modern cloud architecture", "Strong analytics suite", "Good developer tools"],
            "weaknesses": ["No manufacturing references", "Longer sales cycle", "Limited ERP integration"],
        },
    ],
    "contoso": [
        {
            "name": "DataForge Solutions", "relationship": "Strong", "product_fit": 85,
            "pricing": "Market rate", "impl_weeks": 12,
            "activity": "Incumbent on analytics module, pushing expansion",
            "strengths": ["Existing relationship", "Analytics depth", "Familiar to IT team"],
            "weaknesses": ["Platform fragmentation", "Scaling challenges", "Limited innovation pace"],
        },
    ],
    "fabrikam": [
        {
            "name": "ValueStack Inc", "relationship": "Weak", "product_fit": 70,
            "pricing": "-20% below market", "impl_weeks": 18,
            "activity": "Low-cost proposal submitted, basic feature set",
            "strengths": ["Lowest price point", "Simple deployment", "Basic manufacturing templates"],
            "weaknesses": ["Limited customization", "No enterprise support", "Feature gaps in analytics"],
        },
    ],
    "northwind": [],
}

_OUR_PROFILE = {
    "name": "TechVenture Solutions",
    "relationship": "Strong", "product_fit": 94, "pricing": "Market rate",
    "impl_weeks": 8,
    "strengths": [
        "Deepest ERP integration ecosystem",
        "Real-time analytics with AI insights",
        "94% customer retention rate",
        "Fastest implementation in category",
    ],
    "weaknesses": [
        "Premium pricing vs low-cost alternatives",
        "Complex initial configuration",
    ],
}

_WIN_LOSS_RECORDS = {
    "DataForge Solutions": {
        "total_encounters": 28, "wins": 18, "losses": 10,
        "win_rate": 0.643,
        "avg_deal_size_won": 1_850_000, "avg_deal_size_lost": 920_000,
        "common_win_reasons": ["Superior integration", "Customer references", "Implementation speed"],
        "common_loss_reasons": ["Price sensitivity", "Existing relationship", "Feature parity perception"],
        "recent_trend": "Improving — won 4 of last 5 encounters",
    },
    "CloudOps Platform": {
        "total_encounters": 15, "wins": 11, "losses": 4,
        "win_rate": 0.733,
        "avg_deal_size_won": 2_100_000, "avg_deal_size_lost": 1_400_000,
        "common_win_reasons": ["Manufacturing expertise", "Faster deployment", "Better support"],
        "common_loss_reasons": ["Cloud-native preference", "Developer tooling", "Modern UI"],
        "recent_trend": "Stable — consistent 70%+ win rate",
    },
    "ValueStack Inc": {
        "total_encounters": 12, "wins": 9, "losses": 3,
        "win_rate": 0.750,
        "avg_deal_size_won": 780_000, "avg_deal_size_lost": 340_000,
        "common_win_reasons": ["Enterprise features", "Scalability", "Support quality"],
        "common_loss_reasons": ["Price-driven buyer", "SMB scope", "Budget constraints"],
        "recent_trend": "Strong — rarely lose on enterprise deals",
    },
}

_FEATURE_COMPARISON = {
    "Real-time Analytics": {"us": "Full", "DataForge Solutions": "Limited", "CloudOps Platform": "Full", "ValueStack Inc": "None"},
    "ERP Integration": {"us": "Native (SAP, Oracle, D365)", "DataForge Solutions": "Partial (SAP only)", "CloudOps Platform": "API-based", "ValueStack Inc": "CSV Import"},
    "Mobile Experience": {"us": "Native iOS/Android", "DataForge Solutions": "Web only", "CloudOps Platform": "Progressive web app", "ValueStack Inc": "None"},
    "AI/ML Capabilities": {"us": "Predictive + Prescriptive", "DataForge Solutions": "Basic reporting", "CloudOps Platform": "Predictive only", "ValueStack Inc": "None"},
    "Implementation Time": {"us": "8 weeks", "DataForge Solutions": "14 weeks", "CloudOps Platform": "10 weeks", "ValueStack Inc": "18 weeks"},
    "Customer Support": {"us": "24/7 dedicated CSM", "DataForge Solutions": "Business hours", "CloudOps Platform": "24/7 ticketing", "ValueStack Inc": "Email only"},
    "Security Certifications": {"us": "SOC2, ISO27001, GDPR", "DataForge Solutions": "SOC2", "CloudOps Platform": "SOC2, ISO27001", "ValueStack Inc": "SOC2"},
    "API Ecosystem": {"us": "500+ integrations", "DataForge Solutions": "120 integrations", "CloudOps Platform": "300+ integrations", "ValueStack Inc": "40 integrations"},
}

_PRICING_INTEL = {
    "DataForge Solutions": {"base_per_user": 85, "enterprise_discount": "15-25%", "typical_tcl_3yr": 1_200_000, "pricing_model": "Per user/month", "hidden_costs": "Implementation services billed separately"},
    "CloudOps Platform": {"base_per_user": 120, "enterprise_discount": "10-15%", "typical_tcl_3yr": 1_800_000, "pricing_model": "Per user/month + data volume", "hidden_costs": "Data egress fees, premium support tier"},
    "ValueStack Inc": {"base_per_user": 45, "enterprise_discount": "5-10%", "typical_tcl_3yr": 650_000, "pricing_model": "Flat per user/month", "hidden_costs": "Customization professional services"},
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve_account(query):
    if not query:
        return "acme"
    q = query.lower().strip()
    for key in _ACCOUNTS:
        if key in q or q in _ACCOUNTS[key]["name"].lower():
            return key
    return "acme"


def _competitive_threat_score(competitor):
    """Score 0-100 threat level from competitor attributes."""
    rel_scores = {"Strong": 30, "Medium": 20, "Weak": 10}
    fit_score = competitor["product_fit"] * 0.4
    rel_score = rel_scores.get(competitor["relationship"], 10)
    price_score = 20 if "-" in competitor["pricing"] else 10 if "Market" in competitor["pricing"] else 5
    return min(100, int(fit_score + rel_score + price_score))


def _overall_competitive_position(key):
    """Assess our overall position vs competitors for an account."""
    comps = _COMPETITORS.get(key, [])
    if not comps:
        return "Dominant", 95
    max_threat = max(_competitive_threat_score(c) for c in comps)
    if max_threat >= 70:
        return "Contested", 100 - max_threat + 30
    if max_threat >= 50:
        return "Favorable", 100 - max_threat + 40
    return "Strong", 90


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class CompetitiveIntelligenceAgent(BasicAgent):
    """
    Provides competitive intelligence for enterprise deals.

    Operations:
        landscape_analysis  - competitive landscape for an account
        win_loss_review     - win/loss analysis per competitor
        positioning_guide   - positioning recommendations
        battlecard          - detailed competitor battlecard
    """

    def __init__(self):
        self.name = "CompetitiveIntelligenceAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "landscape_analysis", "win_loss_review",
                            "positioning_guide", "battlecard",
                        ],
                        "description": "The competitive intelligence operation",
                    },
                    "account_name": {
                        "type": "string",
                        "description": "Account name (e.g. 'Acme Corporation')",
                    },
                    "competitor": {
                        "type": "string",
                        "description": "Specific competitor name for battlecard",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "landscape_analysis")
        key = _resolve_account(kwargs.get("account_name", ""))
        dispatch = {
            "landscape_analysis": self._landscape_analysis,
            "win_loss_review": self._win_loss_review,
            "positioning_guide": self._positioning_guide,
            "battlecard": self._battlecard,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`."
        return handler(key, **kwargs)

    # ── landscape_analysis ────────────────────────────────────
    def _landscape_analysis(self, key, **kwargs):
        acct = _ACCOUNTS[key]
        comps = _COMPETITORS.get(key, [])

        if not comps:
            return (
                f"**Competitive Landscape: {acct['name']}**\n\n"
                f"No active competitors identified for this account.\n"
                f"This represents a greenfield opportunity.\n\n"
                f"Source: [Competitive Intel Database]\nAgents: CompetitiveIntelligenceAgent"
            )

        position, confidence = _overall_competitive_position(key)

        header = "| Factor | {name} |".format(name=_OUR_PROFILE["name"]) + "".join(f" {c['name']} |" for c in comps) + "\n"
        sep = "|---|---|" + "".join("---|" for _ in comps) + "\n"
        rows_data = [
            ("Relationship", _OUR_PROFILE["relationship"], [c["relationship"] for c in comps]),
            ("Product Fit", f"{_OUR_PROFILE['product_fit']}%", [f"{c['product_fit']}%" for c in comps]),
            ("Pricing", _OUR_PROFILE["pricing"], [c["pricing"] for c in comps]),
            ("Implementation", f"{_OUR_PROFILE['impl_weeks']} weeks", [f"{c['impl_weeks']} weeks" for c in comps]),
        ]
        rows = ""
        for label, ours, theirs in rows_data:
            rows += f"| {label} | {ours} |" + "".join(f" {t} |" for t in theirs) + "\n"

        activity = "\n**Competitor Activity:**\n" + "".join(f"- {c['name']}: {c['activity']}\n" for c in comps)

        threat_rows = ""
        for c in comps:
            score = _competitive_threat_score(c)
            level = "High" if score >= 65 else "Medium" if score >= 45 else "Low"
            threat_rows += f"| {c['name']} | {score}/100 | {level} |\n"

        return (
            f"**Competitive Landscape: {acct['name']}**\n\n"
            f"**Our Position: {position}** (confidence: {confidence}%)\n"
            f"Opportunity value: ${acct['opportunity_value']:,}\n\n"
            f"{header}{sep}{rows}"
            f"{activity}\n"
            f"**Threat Assessment:**\n\n"
            f"| Competitor | Threat Score | Level |\n|---|---|---|\n"
            f"{threat_rows}\n"
            f"Source: [Competitive Intel + Win/Loss Database + Field Intelligence]\n"
            f"Agents: CompetitiveIntelligenceAgent"
        )

    # ── win_loss_review ───────────────────────────────────────
    def _win_loss_review(self, key, **kwargs):
        acct = _ACCOUNTS[key]
        comps = _COMPETITORS.get(key, [])
        comp_names = [c["name"] for c in comps] if comps else list(_WIN_LOSS_RECORDS.keys())

        output = f"**Win/Loss Review: {acct['name']}**\n\n"

        for name in comp_names:
            record = _WIN_LOSS_RECORDS.get(name)
            if not record:
                continue

            output += (
                f"---\n**vs {name}:**\n\n"
                f"| Metric | Value |\n|---|---|\n"
                f"| Total Encounters | {record['total_encounters']} |\n"
                f"| Wins | {record['wins']} |\n"
                f"| Losses | {record['losses']} |\n"
                f"| Win Rate | {record['win_rate']:.0%} |\n"
                f"| Avg Deal Won | ${record['avg_deal_size_won']:,} |\n"
                f"| Avg Deal Lost | ${record['avg_deal_size_lost']:,} |\n"
                f"| Trend | {record['recent_trend']} |\n\n"
                f"**Why We Win:**\n"
                + "".join(f"- {r}\n" for r in record["common_win_reasons"])
                + f"\n**Why We Lose:**\n"
                + "".join(f"- {r}\n" for r in record["common_loss_reasons"])
                + "\n"
            )

        output += (
            f"Source: [Win/Loss Database + CRM Deal History]\n"
            f"Agents: CompetitiveIntelligenceAgent"
        )
        return output

    # ── positioning_guide ─────────────────────────────────────
    def _positioning_guide(self, key, **kwargs):
        acct = _ACCOUNTS[key]
        comps = _COMPETITORS.get(key, [])

        output = (
            f"**Positioning Guide: {acct['name']}**\n\n"
            f"**Our Key Differentiators:**\n"
            + "".join(f"- {s}\n" for s in _OUR_PROFILE["strengths"])
            + "\n"
        )

        for c in comps:
            record = _WIN_LOSS_RECORDS.get(c["name"], {})
            pricing = _PRICING_INTEL.get(c["name"], {})

            output += (
                f"---\n**vs {c['name']}:**\n\n"
                f"**Attack Points (their weaknesses):**\n"
                + "".join(f"- {w}\n" for w in c["weaknesses"])
                + f"\n**Defend Against (their strengths):**\n"
                + "".join(f"- {s}\n" for s in c["strengths"])
                + "\n**Recommended Talk Track:**\n"
            )

            if "-" in c["pricing"]:
                output += (
                    f"- Reframe from upfront cost to TCO: their 3-year TCO is ${pricing.get('typical_tcl_3yr', 0):,} vs our superior value\n"
                    f"- Highlight hidden costs: {pricing.get('hidden_costs', 'N/A')}\n"
                )
            else:
                output += "- Focus on differentiated capabilities and faster time-to-value\n"

            output += (
                f"- Reference win rate: {record.get('win_rate', 0):.0%} when we compete directly\n"
                f"- Key proof point: {record.get('common_win_reasons', ['Superior platform'])[0]}\n\n"
            )

        if not comps:
            output += "No active competitors — focus on value creation vs status quo.\n\n"

        output += (
            f"Source: [Sales Playbook + Win/Loss Analysis + Field Intelligence]\n"
            f"Agents: CompetitiveIntelligenceAgent"
        )
        return output

    # ── battlecard ────────────────────────────────────────────
    def _battlecard(self, key, **kwargs):
        acct = _ACCOUNTS[key]
        comps = _COMPETITORS.get(key, [])
        target_name = kwargs.get("competitor", "")

        # Find the target competitor or use first one
        target = None
        for c in comps:
            if target_name.lower() in c["name"].lower():
                target = c
                break
        if not target and comps:
            target = comps[0]
        if not target:
            return f"**Battlecard: {acct['name']}**\n\nNo competitors identified for this account."

        record = _WIN_LOSS_RECORDS.get(target["name"], {})
        pricing = _PRICING_INTEL.get(target["name"], {})
        threat = _competitive_threat_score(target)

        # Feature comparison for this competitor
        feature_rows = ""
        for feature, scores in _FEATURE_COMPARISON.items():
            our_val = scores.get("us", "N/A")
            their_val = scores.get(target["name"], "N/A")
            advantage = "Us" if our_val != "None" and (their_val == "None" or their_val == "Limited") else "Them" if our_val == "None" else "Even"
            feature_rows += f"| {feature} | {our_val} | {their_val} | {advantage} |\n"

        return (
            f"**Battlecard: {_OUR_PROFILE['name']} vs {target['name']}**\n"
            f"Account: {acct['name']} | Opportunity: ${acct['opportunity_value']:,}\n\n"
            f"**Threat Level: {threat}/100**\n\n"
            f"| Attribute | Us | Them |\n|---|---|---|\n"
            f"| Relationship | {_OUR_PROFILE['relationship']} | {target['relationship']} |\n"
            f"| Product Fit | {_OUR_PROFILE['product_fit']}% | {target['product_fit']}% |\n"
            f"| Pricing | {_OUR_PROFILE['pricing']} | {target['pricing']} |\n"
            f"| Implementation | {_OUR_PROFILE['impl_weeks']} weeks | {target['impl_weeks']} weeks |\n"
            f"| Win Rate (head-to-head) | {record.get('win_rate', 0):.0%} | {1 - record.get('win_rate', 0):.0%} |\n\n"
            f"**Feature Comparison:**\n\n"
            f"| Feature | Us | {target['name']} | Advantage |\n|---|---|---|---|\n"
            f"{feature_rows}\n"
            f"**Their Strengths (defend):**\n"
            + "".join(f"- {s}\n" for s in target["strengths"])
            + f"\n**Their Weaknesses (attack):**\n"
            + "".join(f"- {w}\n" for w in target["weaknesses"])
            + f"\n**Pricing Intel:**\n"
            f"- Base price: ${pricing.get('base_per_user', 0)}/user/month\n"
            f"- Enterprise discount: {pricing.get('enterprise_discount', 'Unknown')}\n"
            f"- 3-year TCO: ${pricing.get('typical_tcl_3yr', 0):,}\n"
            f"- Hidden costs: {pricing.get('hidden_costs', 'None identified')}\n\n"
            f"**Killer Questions to Ask the Prospect:**\n"
            f"1. \"How important is real-time analytics for your operations team?\"\n"
            f"2. \"What's your timeline for ERP integration — weeks or months?\"\n"
            f"3. \"Have you factored in implementation services and hidden costs?\"\n\n"
            f"Source: [Competitive Intel + Win/Loss + Pricing Intelligence]\n"
            f"Agents: CompetitiveIntelligenceAgent"
        )


if __name__ == "__main__":
    agent = CompetitiveIntelligenceAgent()
    for op in ["landscape_analysis", "win_loss_review", "positioning_guide", "battlecard"]:
        print("=" * 60)
        print(agent.perform(operation=op, account_name="Acme Corporation"))
        print()
