"""
Account Intelligence Agent

Surfaces org charts, news, stakeholder interests, competitive positioning,
and deal risk assessment for enterprise accounts. Produces executive-ready
briefing documents from CRM, enrichment, and engagement data.

Where a real deployment would call Salesforce/D365, LinkedIn Sales Navigator,
ZoomInfo, etc., this agent uses a synthetic data layer so it runs anywhere
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
    "name": "@aibast-agents-library/account-intelligence",
    "version": "1.0.0",
    "display_name": "Account Intelligence",
    "description": "360-degree account briefings with stakeholder mapping, competitive analysis, and deal risk assessment.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "account-intelligence", "stakeholder-mapping", "competitive-intel"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# Stands in for CRM, LinkedIn, ZoomInfo, D&B, etc.
# ═══════════════════════════════════════════════════════════════

_ACCOUNTS = {
    "acme": {
        "id": "acc-001", "name": "Acme Corporation", "industry": "Manufacturing",
        "revenue": 2_800_000_000, "employees": 12_400, "hq": "Chicago, IL",
        "current_spend": 1_200_000, "opportunity_value": 2_400_000,
        "products_owned": ["Platform Core", "Analytics Module"],
        "contract_renewal": "8 months",
        "recent_news": [
            {"headline": "CEO mentioned digital transformation in Q3 earnings call", "age_days": 12},
            {"headline": "New CTO Sarah Chen hired from AWS", "age_days": 42},
            {"headline": "Competitor RFP issued for operations platform", "age_days": 30},
        ],
    },
    "contoso": {
        "id": "acc-002", "name": "Contoso Ltd", "industry": "Technology",
        "revenue": 980_000_000, "employees": 4_200, "hq": "Redmond, WA",
        "current_spend": 680_000, "opportunity_value": 1_100_000,
        "products_owned": ["Platform Core"],
        "contract_renewal": "3 months",
        "recent_news": [
            {"headline": "Series D funding of $120M announced", "age_days": 18},
            {"headline": "Expanding EMEA operations with new London office", "age_days": 45},
        ],
    },
    "fabrikam": {
        "id": "acc-003", "name": "Fabrikam Industries", "industry": "Manufacturing",
        "revenue": 1_500_000_000, "employees": 8_700, "hq": "Detroit, MI",
        "current_spend": 450_000, "opportunity_value": 890_000,
        "products_owned": ["Analytics Module"],
        "contract_renewal": "14 months",
        "recent_news": [
            {"headline": "Q2 revenue up 18% YoY", "age_days": 25},
            {"headline": "New VP of IT appointed", "age_days": 60},
        ],
    },
    "northwind": {
        "id": "acc-004", "name": "Northwind Traders", "industry": "Retail",
        "revenue": 620_000_000, "employees": 3_100, "hq": "Portland, OR",
        "current_spend": 220_000, "opportunity_value": 540_000,
        "products_owned": [],
        "contract_renewal": None,
        "recent_news": [
            {"headline": "Launched e-commerce platform", "age_days": 15},
        ],
    },
}

_STAKEHOLDERS = {
    "acme": [
        {"name": "Sarah Chen",  "role": "CTO",           "influence": "Decision Maker", "sentiment": "Unknown",  "meetings": 0,  "notes": "New hire from AWS, 6 weeks ago. Controls tech budget."},
        {"name": "James Miller", "role": "VP Operations", "influence": "Champion",       "sentiment": "Positive", "meetings": 14, "notes": "Promoted to VP last quarter. Advocated for 3 vendor decisions."},
        {"name": "Lisa Park",    "role": "CFO",           "influence": "Economic Buyer", "sentiment": "Neutral",  "meetings": 2,  "notes": "Requested business case and ROI validation."},
        {"name": "David Wong",   "role": "IT Director",   "influence": "Influencer",     "sentiment": "Positive", "meetings": 8,  "notes": "Technical evaluator. Likes our API-first approach."},
        {"name": "Rachel Torres","role": "Procurement",    "influence": "Gatekeeper",     "sentiment": "Neutral",  "meetings": 1,  "notes": "Standard procurement process, 4-6 week cycle."},
        {"name": "Kevin Park",   "role": "VP Engineering", "influence": "Influencer",     "sentiment": "Positive", "meetings": 5,  "notes": "Attended 2 product demos."},
        {"name": "Maria Lopez",  "role": "Director of Strategy", "influence": "Influencer", "sentiment": "Unknown", "meetings": 0, "notes": "No contact yet."},
        {"name": "Tom Bradley",  "role": "CEO",           "influence": "Executive Sponsor", "sentiment": "Unknown", "meetings": 0, "notes": "Mentioned digital transformation in earnings call."},
    ],
    "contoso": [
        {"name": "Alex Kim",    "role": "CTO",        "influence": "Decision Maker", "sentiment": "Positive", "meetings": 10, "notes": "Strong advocate."},
        {"name": "Pat Johnson",  "role": "CFO",        "influence": "Economic Buyer", "sentiment": "Neutral",  "meetings": 3,  "notes": "Budget cautious."},
        {"name": "Sam Rivera",   "role": "VP Product", "influence": "Champion",       "sentiment": "Positive", "meetings": 7,  "notes": "Wants expansion."},
    ],
    "fabrikam": [
        {"name": "Chris Anderson","role": "VP IT",       "influence": "Decision Maker", "sentiment": "Neutral",  "meetings": 4, "notes": "New to role."},
        {"name": "Dana White",    "role": "COO",         "influence": "Champion",       "sentiment": "Positive", "meetings": 6, "notes": "Drives operational efficiency."},
    ],
    "northwind": [
        {"name": "Jordan Lee",  "role": "CTO",    "influence": "Decision Maker", "sentiment": "Unknown", "meetings": 1, "notes": "Initial discovery call."},
        {"name": "Casey Brown",  "role": "CEO",    "influence": "Executive Sponsor", "sentiment": "Unknown", "meetings": 0, "notes": "No contact yet."},
    ],
}

_COMPETITORS = {
    "acme": [
        {"name": "CompetitorA", "relationship": "Medium", "product_fit": 78, "pricing": "-15% below market", "impl_weeks": 14, "activity": "On-site demo last week, aggressive discount offered"},
        {"name": "CompetitorB", "relationship": "Weak",   "product_fit": 82, "pricing": "+10% above market", "impl_weeks": 10, "activity": "Early conversations only, no formal proposal"},
    ],
    "contoso": [
        {"name": "CompetitorA", "relationship": "Strong", "product_fit": 85, "pricing": "Market rate",      "impl_weeks": 12, "activity": "Incumbent on analytics module"},
    ],
    "fabrikam": [
        {"name": "CompetitorC", "relationship": "Weak",   "product_fit": 70, "pricing": "-20% below market", "impl_weeks": 18, "activity": "Low-cost proposal submitted"},
    ],
    "northwind": [],
}

_OUR_PROFILE = {
    "relationship": "Strong", "product_fit": 94, "pricing": "Market rate",
    "impl_weeks": 8,
    "advantages": [
        "Existing integration with customer ERP (3-week head start)",
        "Champion relationship established",
        "Superior customer references in target industry",
    ],
}


# ═══════════════════════════════════════════════════════════════
# HELPERS — real computation, synthetic inputs
# ═══════════════════════════════════════════════════════════════

def _resolve_account(query):
    """Fuzzy-match an account name to our synthetic data."""
    if not query:
        return "acme"
    q = query.lower().strip()
    for key in _ACCOUNTS:
        if key in q or q in _ACCOUNTS[key]["name"].lower():
            return key
    return "acme"


def _health_score(key):
    """Compute account health from engagement signals."""
    stks = _STAKEHOLDERS.get(key, [])
    acct = _ACCOUNTS[key]

    total_meetings = sum(s["meetings"] for s in stks)
    positive_ratio = sum(1 for s in stks if s["sentiment"] == "Positive") / max(len(stks), 1)
    product_depth = len(acct["products_owned"]) / 3

    engagement = min(100, int(total_meetings * 3.5))
    adoption = int(product_depth * 100)
    sentiment = int(positive_ratio * 100)
    renewal_risk = max(5, 50 - total_meetings * 2 - int(positive_ratio * 30))

    overall = int(engagement * 0.3 + adoption * 0.2 + sentiment * 0.3 + (100 - renewal_risk) * 0.2)
    return {
        "overall": overall,
        "engagement": engagement,
        "adoption": adoption,
        "sentiment_score": sentiment,
        "renewal_risk_pct": renewal_risk,
        "touchpoints_30d": total_meetings,
        "csat": round(3.0 + positive_ratio * 2, 1),
    }


def _deal_risks(key):
    """Compute deal risks from stakeholder and competitive data."""
    stks = _STAKEHOLDERS.get(key, [])
    comps = _COMPETITORS.get(key, [])
    risks = []

    for s in stks:
        if s["influence"] == "Decision Maker" and s["meetings"] == 0:
            risks.append({"risk": f"No relationship with {s['role']} ({s['name']})",
                          "severity": "High", "mitigation": "Champion intro this week", "owner": "You"})
    for c in comps:
        if "-" in c["pricing"]:
            risks.append({"risk": f"{c['name']} pricing pressure ({c['pricing']})",
                          "severity": "High", "mitigation": "TCO analysis showing lower total cost", "owner": "You"})
    for s in stks:
        if s["influence"] == "Economic Buyer" and s["sentiment"] != "Positive":
            risks.append({"risk": f"{s['role']} needs ROI validation",
                          "severity": "Medium", "mitigation": "Send customized ROI calculator", "owner": "Finance"})

    champion_count = sum(1 for s in stks if s["influence"] == "Champion" and s["sentiment"] == "Positive")
    blocker_count = len([r for r in risks if r["severity"] == "High"])
    win_prob = min(95, max(20, 50 + champion_count * 15 - blocker_count * 10 + len(stks) * 2))
    return risks, win_prob


def _value_messaging(key):
    """Generate stakeholder-specific talking points."""
    stks = _STAKEHOLDERS.get(key, [])
    acct = _ACCOUNTS[key]
    messaging = {}
    for s in stks:
        if s["influence"] not in ("Decision Maker", "Economic Buyer", "Champion"):
            continue
        role = s["role"]
        if any(t in role for t in ("CTO", "IT", "Engineering")):
            messaging[s["name"]] = {"role": role, "focus": "Tech Vision", "points": [
                "Platform aligns with digital transformation roadmap",
                "API-first architecture integrates with existing systems",
                f"3 {acct['industry']} CTO references available for peer conversation",
            ]}
        elif any(t in role for t in ("CFO", "Finance")):
            savings = int(acct["opportunity_value"] * 1.75)
            messaging[s["name"]] = {"role": role, "focus": "ROI", "points": [
                f"${savings:,} projected savings over 3 years",
                f"{_OUR_PROFILE['impl_weeks']}-week implementation vs competitor's longer timeline",
                "Risk-free pilot: 90-day proof of value before full commitment",
            ]}
        elif s["influence"] == "Champion":
            messaging[s["name"]] = {"role": role, "focus": "Internal Positioning", "points": [
                "Positions your team as transformation leaders",
                "Executive visibility on project success metrics",
                "Co-innovation partnership opportunity",
            ]}
    return messaging


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class AccountIntelligenceAgent(BasicAgent):
    """
    Produces 360-degree account intelligence briefings.

    Operations:
        account_overview  - firmographics, health score, recent news
        stakeholder_map   - org chart, buying committee, relationship gaps
        competitive_intel - landscape analysis and positioning
        value_messaging   - stakeholder-specific talking points
        risk_assessment   - deal risks with mitigation actions
        executive_briefing - full compiled briefing
    """

    def __init__(self):
        self.name = "AccountIntelligenceAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "account_overview", "stakeholder_map",
                            "competitive_intel", "value_messaging",
                            "risk_assessment", "executive_briefing",
                        ],
                        "description": "The analysis to perform",
                    },
                    "account_name": {
                        "type": "string",
                        "description": "Account name to analyze (e.g. 'Acme Corporation')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "account_overview")
        key = _resolve_account(kwargs.get("account_name", ""))
        dispatch = {
            "account_overview": self._account_overview,
            "stakeholder_map": self._stakeholder_map,
            "competitive_intel": self._competitive_intel,
            "value_messaging": self._value_messaging,
            "risk_assessment": self._risk_assessment,
            "executive_briefing": self._executive_briefing,
        }
        handler = dispatch.get(op)
        if not handler:
            return json.dumps({"status": "error", "message": f"Unknown operation: {op}"})
        return handler(key)

    # ── account_overview ──────────────────────────────────────
    def _account_overview(self, key):
        acct = _ACCOUNTS[key]
        h = _health_score(key)
        news = "\n".join(f"- {n['headline']} ({n['age_days']} days ago)" for n in acct["recent_news"])
        return (
            f"**Account Overview: {acct['name']}**\n\n"
            f"| Attribute | Details |\n|---|---|\n"
            f"| Industry | {acct['industry']} |\n"
            f"| Revenue | ${acct['revenue']:,} |\n"
            f"| Employees | {acct['employees']:,} globally |\n"
            f"| HQ | {acct['hq']} |\n"
            f"| Current spend | ${acct['current_spend']:,}/year |\n"
            f"| Opportunity | ${acct['opportunity_value']:,} expansion |\n\n"
            f"**Account Health Score: {h['overall']}/100**\n"
            f"- Engagement: {h['engagement']}% ({h['touchpoints_30d']} touchpoints last 30 days)\n"
            f"- Product adoption: {h['adoption']}% feature utilization\n"
            f"- Support sentiment: {h['csat']}/5 CSAT\n"
            f"- Renewal risk: {h['renewal_risk_pct']}%\n\n"
            f"**Recent Activity:**\n{news}\n\n"
            f"Source: [CRM + News Intelligence + LinkedIn]\n"
            f"Agents: AccountProfileAgent, AccountHealthScoreAgent"
        )

    # ── stakeholder_map ───────────────────────────────────────
    def _stakeholder_map(self, key):
        stks = _STAKEHOLDERS.get(key, [])
        if not stks:
            return "No stakeholders mapped for this account yet."

        table = "| Name | Role | Influence | Sentiment | Engagement |\n|---|---|---|---|---|\n"
        for s in stks:
            eng = f"{s['meetings']} meetings" if s["meetings"] > 0 else "Schedule intro"
            table += f"| {s['name']} | {s['role']} | {s['influence']} | {s['sentiment']} | {eng} |\n"

        gaps = [s for s in stks if s["meetings"] == 0 and s["influence"] in ("Decision Maker", "Economic Buyer", "Executive Sponsor")]
        gap_lines = ""
        if gaps:
            gap_lines = "\n**Relationship Gaps:**\n"
            for g in gaps:
                gap_lines += f"- {g['name']} ({g['role']}): {g['notes']}\n"

        champions = [s for s in stks if s["influence"] == "Champion" and s["sentiment"] == "Positive"]
        champ_lines = ""
        if champions:
            c = champions[0]
            champ_lines = f"\n**Champion Intelligence:**\n{c['name']} — {c['notes']}\n"

        return (
            f"**Stakeholder Map ({len(stks)} contacts):**\n\n"
            f"{table}{gap_lines}{champ_lines}\n"
            "Source: [LinkedIn Sales Navigator + CRM Contacts + Meeting History]\n"
            "Agents: StakeholderMappingAgent"
        )

    # ── competitive_intel ─────────────────────────────────────
    def _competitive_intel(self, key):
        comps = _COMPETITORS.get(key, [])
        if not comps:
            return "No active competitors identified for this account."

        header = "| Factor | You |" + "".join(f" {c['name']} |" for c in comps) + "\n"
        sep = "|---|---|" + "".join("---|" for _ in comps) + "\n"
        rows_data = [
            ("Relationship depth", _OUR_PROFILE["relationship"], [c["relationship"] for c in comps]),
            ("Product fit", f"{_OUR_PROFILE['product_fit']}%", [f"{c['product_fit']}%" for c in comps]),
            ("Pricing", _OUR_PROFILE["pricing"], [c["pricing"] for c in comps]),
            ("Implementation", f"{_OUR_PROFILE['impl_weeks']} weeks", [f"{c['impl_weeks']} weeks" for c in comps]),
        ]
        rows = ""
        for label, ours, theirs in rows_data:
            rows += f"| {label} | {ours} |" + "".join(f" {t} |" for t in theirs) + "\n"

        activity = "\n**Competitor Activity:**\n" + "".join(f"- {c['name']}: {c['activity']}\n" for c in comps)
        advantages = "\n**Your Advantages:**\n" + "".join(f"{i}. {a}\n" for i, a in enumerate(_OUR_PROFILE["advantages"], 1))

        price_threats = [c for c in comps if "-" in c["pricing"]]
        risk = f"\n**Risk Alert:** {price_threats[0]['name']}'s discount may appeal to economic buyer.\n" if price_threats else ""

        return f"**Competitive Intelligence:**\n\n{header}{sep}{rows}{activity}{advantages}{risk}\nSource: [Competitive Intel + Win/Loss Database]\nAgents: CompetitiveIntelligenceAgent"

    # ── value_messaging ───────────────────────────────────────
    def _value_messaging(self, key):
        messaging = _value_messaging(key)
        if not messaging:
            return "No decision-maker or champion contacts mapped yet."

        output = "**Meeting Talking Points:**\n\n"
        for name, data in messaging.items():
            output += f"**For {name} ({data['role']} — {data['focus']}):**\n"
            for pt in data["points"]:
                output += f'- "{pt}"\n'
            output += "\n"

        output += (
            "**Objection Handling:**\n"
            '- Price concern: "Total cost of ownership is 23% lower when factoring implementation and support"\n'
            '- Risk concern: "Deployed at 47 similar companies with 94% success rate"\n\n'
            "Source: [Value Engineering + Reference Database]\nAgents: ValueMessagingAgent"
        )
        return output

    # ── risk_assessment ───────────────────────────────────────
    def _risk_assessment(self, key):
        acct = _ACCOUNTS[key]
        risks, win_prob = _deal_risks(key)
        if not risks:
            return f"No significant risks identified for {acct['name']}. Win probability: {win_prob}%."

        table = "| Risk | Severity | Mitigation | Owner |\n|---|---|---|---|\n"
        for r in risks:
            table += f"| {r['risk']} | {r['severity']} | {r['mitigation']} | {r['owner']} |\n"

        high = [r for r in risks if r["severity"] == "High"]
        actions = ""
        if high:
            actions = "\n**Immediate Actions:**\n" + "".join(f"{i}. {r['mitigation']} — {r['owner']}\n" for i, r in enumerate(high, 1))

        return (
            f"**Deal Risk Assessment: {acct['name']}**\n\n{table}\n"
            f"**Win Probability:** {win_prob}%\n"
            f"**Opportunity Value:** ${acct['opportunity_value']:,}\n"
            f"{actions}\nSource: [Deal Analytics + Risk Models]\nAgents: DealRiskAssessmentAgent"
        )

    # ── executive_briefing ────────────────────────────────────
    def _executive_briefing(self, key):
        acct = _ACCOUNTS[key]
        h = _health_score(key)
        risks, win_prob = _deal_risks(key)
        stks = _STAKEHOLDERS.get(key, [])
        comps = _COMPETITORS.get(key, [])
        gaps = sum(1 for s in stks if s["meetings"] == 0)

        checklist = "".join(f"- {r['mitigation']}\n" for r in risks if r["severity"] == "High")
        return (
            f"**Account Intelligence Briefing: {acct['name']}**\n\n"
            f"**Opportunity Summary:**\n"
            f"- Deal value: ${acct['opportunity_value']:,} (expansion from ${acct['current_spend']:,} current)\n"
            f"- Win probability: {win_prob}%\n"
            f"- Account health: {h['overall']}/100\n\n"
            f"| Analysis | Key Finding |\n|---|---|\n"
            f"| Account health | {h['engagement']}% engagement, {h['adoption']}% adoption, {h['renewal_risk_pct']}% churn risk |\n"
            f"| Stakeholders | {len(stks)} mapped, {gaps} need intro, {sum(1 for s in stks if s['influence']=='Champion')} champions |\n"
            f"| Competition | {len(comps)} active, you lead on fit/speed |\n"
            f"| Risks | {len(risks)} identified, {sum(1 for r in risks if r['severity']=='High')} critical |\n\n"
            f"**Pre-Meeting Checklist:**\n{checklist}\n"
            "Source: [All Intelligence Systems]\nAgents: BriefingDocumentAgent (orchestrating all agents)"
        )


if __name__ == "__main__":
    agent = AccountIntelligenceAgent()
    for op in ["account_overview", "stakeholder_map", "competitive_intel",
               "value_messaging", "risk_assessment", "executive_briefing"]:
        print("=" * 60)
        print(agent.perform(operation=op, account_name="Acme Corporation"))
        print()
