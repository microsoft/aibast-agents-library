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
    "display_name": "Account Intelligence Agent",
    "description": "Automate account research and strategy planning to help sellers prepare faster, win more, and elevate deal quality.",
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
        # CRM account-health and opportunity fields (synthetic)
        "health_score": 78, "feature_adoption_pct": 67, "csat": 4.2,
        "touchpoints_30d": 30, "renewal_risk_pct": 5,
        "win_probability": 68, "close_target_days": 21,
        "key_signals": [
            "New CTO hired 6 weeks ago (opportunity)",
            "CEO mentioned digital transformation",
        ],
        "recent_news": [
            {"headline": "CEO mentioned digital transformation in Q3 earnings call", "age_days": 12},
            {"headline": "New CTO Sarah Chen hired 6 weeks ago", "age_days": 42},
            {"headline": "Competitor RFP issued for operations platform", "age_days": 30},
        ],
    },
    "contoso": {
        "id": "acc-002", "name": "Contoso Ltd", "industry": "Technology",
        "revenue": 980_000_000, "employees": 4_200, "hq": "Redmond, WA",
        "current_spend": 680_000, "opportunity_value": 1_100_000,
        "products_owned": ["Platform Core"],
        "contract_renewal": "3 months",
        "health_score": 66, "feature_adoption_pct": 33, "csat": 4.3,
        "touchpoints_30d": 20, "renewal_risk_pct": 5,
        "win_probability": 71, "close_target_days": 45,
        "key_signals": ["Series D funding of $120M announced", "Expanding EMEA operations"],
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
        "health_score": 49, "feature_adoption_pct": 33, "csat": 4.0,
        "touchpoints_30d": 10, "renewal_risk_pct": 15,
        "win_probability": 59, "close_target_days": 60,
        "key_signals": ["Q2 revenue up 18% YoY", "New VP of IT appointed"],
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
        "health_score": 11, "feature_adoption_pct": 0, "csat": 3.0,
        "touchpoints_30d": 1, "renewal_risk_pct": 48,
        "win_probability": 54, "close_target_days": 90,
        "key_signals": ["Launched e-commerce platform"],
        "recent_news": [
            {"headline": "Launched e-commerce platform", "age_days": 15},
        ],
    },
}

# status = relationship status shown in the stakeholder map; gap = coverage gap note (empty when none);
# influence_score = 0-100 synthetic weight in the buying decision.
_STAKEHOLDERS = {
    "acme": [
        {"name": "Sarah Chen",  "role": "CTO (New)",     "influence": "Decision Maker", "influence_score": 95, "sentiment": "Unknown",  "status": "Need intro", "meetings": 0,  "gap": "CTO controls tech budget (no relationship)", "notes": "New CTO, hired 6 weeks ago. Controls tech budget."},
        {"name": "James Miller", "role": "VP Operations", "influence": "Champion",       "influence_score": 85, "sentiment": "Positive", "status": "Champion",   "meetings": 14, "gap": "", "notes": "Promoted to VP last quarter. Advocated for 3 vendor decisions."},
        {"name": "Lisa Park",    "role": "CFO",           "influence": "Economic Buyer", "influence_score": 90, "sentiment": "Neutral",  "status": "Needs ROI",  "meetings": 2,  "gap": "CFO wants business case", "notes": "Requested business case and ROI validation."},
        {"name": "David Wong",   "role": "IT Director",   "influence": "Influencer",     "influence_score": 70, "sentiment": "Positive", "status": "Positive",   "meetings": 8,  "gap": "", "notes": "Technical evaluator. Likes our API-first approach."},
        {"name": "Rachel Torres","role": "Procurement",    "influence": "Gatekeeper",     "influence_score": 50, "sentiment": "Neutral",  "status": "Neutral",    "meetings": 1,  "gap": "", "notes": "Standard procurement process, 4-6 week cycle."},
        {"name": "Kevin Park",   "role": "VP Engineering", "influence": "Influencer",     "influence_score": 60, "sentiment": "Positive", "status": "Positive",   "meetings": 5,  "gap": "", "notes": "Attended 2 product demos."},
        {"name": "Maria Lopez",  "role": "Director of Strategy", "influence": "Influencer", "influence_score": 40, "sentiment": "Unknown", "status": "No contact", "meetings": 0, "gap": "", "notes": "No contact yet."},
        {"name": "Tom Bradley",  "role": "CEO",           "influence": "Executive Sponsor", "influence_score": 80, "sentiment": "Unknown", "status": "Aware",  "meetings": 0, "gap": "", "notes": "Mentioned digital transformation in earnings call."},
    ],
    "contoso": [
        {"name": "Alex Kim",    "role": "CTO",        "influence": "Decision Maker", "influence_score": 90, "sentiment": "Positive", "status": "Positive", "meetings": 10, "gap": "", "notes": "Strong advocate."},
        {"name": "Pat Johnson",  "role": "CFO",        "influence": "Economic Buyer", "influence_score": 85, "sentiment": "Neutral",  "status": "Needs ROI", "meetings": 3,  "gap": "CFO is budget cautious", "notes": "Budget cautious."},
        {"name": "Sam Rivera",   "role": "VP Product", "influence": "Champion",       "influence_score": 75, "sentiment": "Positive", "status": "Champion", "meetings": 7,  "gap": "", "notes": "Wants expansion."},
    ],
    "fabrikam": [
        {"name": "Chris Anderson","role": "VP IT",       "influence": "Decision Maker", "influence_score": 90, "sentiment": "Neutral",  "status": "Neutral",  "meetings": 4, "gap": "New decision maker, sentiment unclear", "notes": "New to role."},
        {"name": "Dana White",    "role": "COO",         "influence": "Champion",       "influence_score": 80, "sentiment": "Positive", "status": "Champion", "meetings": 6, "gap": "", "notes": "Drives operational efficiency."},
    ],
    "northwind": [
        {"name": "Jordan Lee",  "role": "CTO",    "influence": "Decision Maker", "influence_score": 90, "sentiment": "Unknown", "status": "Discovery", "meetings": 1, "gap": "Only one discovery call so far", "notes": "Initial discovery call."},
        {"name": "Casey Brown",  "role": "CEO",    "influence": "Executive Sponsor", "influence_score": 80, "sentiment": "Unknown", "status": "No contact", "meetings": 0, "gap": "No executive sponsor contact", "notes": "No contact yet."},
    ],
}

_COMPETITORS = {
    "acme": [
        {"name": "CompetitorA", "relationship": "Medium", "product_fit": 78, "pricing": "15% discount", "impl_weeks": 14, "activity": "On-site demo last week, aggressive discount offered"},
        {"name": "CompetitorB", "relationship": "Weak",   "product_fit": 82, "pricing": "10% premium",  "impl_weeks": 10, "activity": "Early conversations only, no formal proposal"},
    ],
    "contoso": [
        {"name": "CompetitorA", "relationship": "Strong", "product_fit": 85, "pricing": "Market",       "impl_weeks": 12, "activity": "Incumbent on analytics module"},
    ],
    "fabrikam": [
        {"name": "CompetitorC", "relationship": "Weak",   "product_fit": 70, "pricing": "20% discount", "impl_weeks": 18, "activity": "Low-cost proposal submitted"},
    ],
    "northwind": [],
}

_OUR_PROFILE = {
    "relationship": "Strong", "product_fit": 94, "pricing": "Market",
    "impl_weeks": 8,
    "advantages": [
        "ERP integration (3-week head start)",
        "champion relationship",
        "manufacturing references",
    ],
    "tco_lower_pct": 23, "similar_deployments": 47, "deployment_success_pct": 94,
}

# Deal risks per account. action = the seller's to-do before the meeting (empty when none).
_RISKS = {
    "acme": [
        {"risk": "No CTO relationship", "severity": "High",   "mitigation": "Champion intro today",   "action": "Call James for CTO intro"},
        {"risk": "Competitor pricing",  "severity": "High",   "mitigation": "TCO analysis ready",     "action": "Send CFO ROI calculator"},
        {"risk": "Budget timing",       "severity": "Medium", "mitigation": "Q1 confirmed",           "action": ""},
        {"risk": "CFO business case",   "severity": "Medium", "mitigation": "ROI calculator drafted", "action": ""},
    ],
    "contoso": [
        {"risk": "CFO budget caution",  "severity": "Medium", "mitigation": "ROI calculator drafted", "action": ""},
    ],
    "fabrikam": [
        {"risk": "Competitor pricing",  "severity": "High",   "mitigation": "TCO analysis ready",     "action": "Prepare TCO comparison for Chris Anderson"},
    ],
    "northwind": [],
}


# ═══════════════════════════════════════════════════════════════
# HELPERS — real computation, synthetic inputs
# ═══════════════════════════════════════════════════════════════

def _resolve_account(query):
    """Account key, full name or part of it; None when nothing matches (never another account)."""
    if not query:
        return "acme"
    q = query.lower().strip()
    for key in _ACCOUNTS:
        if key in q or q in _ACCOUNTS[key]["name"].lower():
            return key
    return None


def _short_money(value):
    """2_800_000_000 -> '$2.8B', 1_200_000 -> '$1.2M', 540_000 -> '$540K'."""
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value / 1_000:.0f}K"


def _critical(risks):
    return [r for r in risks if r["severity"] == "High"]


def _checklist(key):
    """Before-meeting to-dos: each critical risk's action, then the competitor counter-strategy review."""
    items = [r["action"] for r in _RISKS.get(key, []) if r["action"]]
    if _COMPETITORS.get(key):
        items.append("Review competitor counter-strategy")
    return items


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
            "description": (
                f"{__manifest__['description']} Uses bundled synthetic account records and "
                "returns read-only research, draft messaging, and planning options only. "
                "Route requests for persona-specific talking points, meeting messaging, "
                "conversation hooks, or objection handling to `value_messaging`; this operation "
                "returns the required `Draft Meeting Talking Points` and `Objection Handling` "
                "sections. Use `executive_briefing` only at the END of the research, when the user "
                "asks for the executive briefing summary, briefing document or pre-meeting checklist. "
                "The demo account is Acme Corporation (the default). A seller preparing for a meeting "
                "walks the operations in order: first ask, 'I need a complete intelligence briefing on "
                "<account>' -> account_overview (revenue, spend, health score, key signals); "
                "key stakeholders and influence -> stakeholder_map; competitive landscape -> "
                "competitive_intel; talking points and value messaging -> value_messaging; deal "
                "risks and mitigation -> risk_assessment; executive briefing summary -> executive_briefing."
            ),
            "operations": [
                "account_overview", "stakeholder_map", "competitive_intel",
                "value_messaging", "risk_assessment", "executive_briefing",
            ],
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
                        "description": (
                            "Select exactly one operation from the user's requested deliverable. "
                            "account_overview: an intelligence briefing on an account (revenue, spend, "
                            "opportunity, health score, key signals). "
                            "stakeholder_map: buying committee, influence, champions, and relationship gaps. "
                            "competitive_intel: competitor activity, comparison, and positioning. "
                            "value_messaging: REQUIRED for persona-specific talking points, meeting messaging, "
                            "conversation hooks, or objection handling; returns Draft Meeting Talking Points "
                            "and Objection Handling. risk_assessment: deal risks and candidate mitigations. "
                            "executive_briefing: the closing executive briefing summary and pre-meeting "
                            "checklist (not the first 'intelligence briefing' ask, which is account_overview); "
                            "do not use it as a substitute for value_messaging."
                        ),
                    },
                    "account_name": {
                        "type": "string",
                        "enum": ["Acme Corporation", "Contoso Ltd", "Fabrikam Industries", "Northwind Traders"],
                        "description": "Account name to analyze (e.g. 'Acme Corporation')",
                    },
                    "data_source": {
                        "type": "string",
                        "enum": ["synthetic"],
                        "description": "Deterministic source route. Only bundled synthetic evidence is supported.",
                    },
                },
                "required": ["operation"],
                "additionalProperties": False,
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "account_overview")
        source = kwargs.get("data_source", "synthetic")
        if source != "synthetic":
            return "**Error:** `data_source` must be `synthetic`."
        key = _resolve_account(kwargs.get("account_name", ""))
        if key is None:
            return (
                "**Error:** Unknown `account_name`. Valid synthetic accounts: Acme Corporation, "
                "Contoso Ltd, Fabrikam Industries, Northwind Traders."
            )
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
        output = handler(key)
        return (
            output.replace("Source: [", "Synthetic source model: [")
            + "\n\n**Evidence boundary:** Exact names, values, scores, percentages, news, "
            "stakeholder details, and competitor signals are synthetic planning evidence. "
            "Messaging is a draft for human review. No CRM record, task, message, meeting, "
            "proposal, or customer communication was created or changed."
        )

    # ── account_overview ──────────────────────────────────────
    def _account_overview(self, key):
        acct = _ACCOUNTS[key]
        signals = "\n".join(f"- {s}" for s in acct["key_signals"])
        news = "\n".join(f"- {n['headline']} ({n['age_days']} days ago)" for n in acct["recent_news"])
        return (
            f"**Account Overview: {acct['name']}** (intelligence briefing)\n\n"
            f"| Attribute | Details |\n|---|---|\n"
            f"| Revenue | {_short_money(acct['revenue'])} |\n"
            f"| Current spend | {_short_money(acct['current_spend'])}/year |\n"
            f"| Opportunity | {_short_money(acct['opportunity_value'])} expansion |\n"
            f"| Health Score | {acct['health_score']}/100 |\n"
            f"| Industry | {acct['industry']} ({acct['employees']:,} employees, HQ {acct['hq']}) |\n\n"
            f"**Account Health Score: {acct['health_score']}/100**\n\n"
            f"**Key Signals:**\n{signals}\n"
            f"- {acct['feature_adoption_pct']}% feature adoption, {acct['csat']}/5 CSAT\n\n"
            f"**Recent Activity:**\n{news}\n\n"
            f"Next: want to see the stakeholder map?\n\n"
            f"Source: [CRM + LinkedIn]\n"
            f"Agents: AccountProfileAgent, AccountHealthScoreAgent"
        )

    # ── stakeholder_map ───────────────────────────────────────
    def _stakeholder_map(self, key):
        stks = _STAKEHOLDERS.get(key, [])
        if not stks:
            return "No stakeholders mapped for this account yet."
        champion = any(s["influence"] == "Champion" and s["sentiment"] == "Positive" for s in stks)
        buyer = [s for s in stks if s["influence"] == "Economic Buyer" and s["sentiment"] != "Positive"]
        headline = f"{len(stks)} stakeholders mapped."
        if champion:
            headline += " Champion strong"
            headline += ", need CFO alignment." if buyer else "."
        table = "| Name | Role | Influence | Influence Score | Status |\n|---|---|---|---|---|\n"
        for s in stks:
            table += f"| {s['name']} | {s['role']} | {s['influence']} | {s['influence_score']} | {s['status']} |\n"
        gaps = [s["gap"] for s in stks if s["gap"]]
        gap_text = ", ".join(gaps) if gaps else "None recorded"
        champ = next((s for s in stks if s["influence"] == "Champion"), None)
        need_intro = next((s for s in stks if s["status"] == "Need intro"), None)
        action = ""
        if champ and need_intro:
            short = need_intro["role"].split(" ")[0]
            action = f"**Action:** Get {short} intro through {champ['name'].split(' ')[0]} before meeting\n\n"
        return (
            f"**Stakeholder Map ({len(stks)} contacts):** {headline}\n\n"
            f"{table}\n"
            f"**Relationship Gaps:** {gap_text}\n\n"
            f"{action}"
            "Next: want competitive positioning?\n\n"
            "Source: [LinkedIn Sales Navigator + CRM Contacts + Meeting History]\n"
            "Agents: StakeholderMappingAgent"
        )

    # ── competitive_intel ─────────────────────────────────────
    def _competitive_intel(self, key):
        comps = _COMPETITORS.get(key, [])
        if not comps:
            return "No active competitors identified for this account."
        count = {1: "One competitor", 2: "Two competitors", 3: "Three competitors"}.get(len(comps), f"{len(comps)} competitors")
        threats = [c for c in comps if "discount" in c["pricing"]]
        headline = f"{count} active. You lead on fit"
        headline += ", they're aggressive on price." if threats else "."
        header = "| Factor | You |" + "".join(f" {c['name']} |" for c in comps) + "\n"
        sep = "|---|---|" + "".join("---|" for _ in comps) + "\n"
        rows = (
            f"| Product fit | {_OUR_PROFILE['product_fit']}% |" + "".join(f" {c['product_fit']}% |" for c in comps) + "\n"
            f"| Implementation | {_OUR_PROFILE['impl_weeks']} weeks |" + "".join(f" {c['impl_weeks']} weeks |" for c in comps) + "\n"
            f"| Pricing | {_OUR_PROFILE['pricing']} |" + "".join(f" {c['pricing']} |" for c in comps) + "\n"
        )
        activity = "\n**Competitor Activity:**\n" + "".join(f"- {c['name']}: {c['activity']}\n" for c in comps)
        advantages = "\n**Your Advantages:** " + ", ".join(_OUR_PROFILE["advantages"]) + "\n"
        risk = f"\n**Risk:** {threats[0]['name']}'s discount may appeal to CFO\n" if threats else ""
        return (
            f"**Competitive Intelligence:** {headline}\n\n{header}{sep}{rows}{advantages}{risk}{activity}\n"
            "Next: prepare counter-positioning?\n\n"
            "Source: [Competitive Intel + Win/Loss Database]\nAgents: CompetitiveIntelligenceAgent"
        )

    # ── value_messaging ───────────────────────────────────────
    def _value_messaging(self, key):
        acct = _ACCOUNTS[key]
        stks = _STAKEHOLDERS.get(key, [])
        comps = _COMPETITORS.get(key, [])
        if not stks:
            return "No decision-maker or champion contacts mapped yet."
        their_weeks = max([c["impl_weeks"] for c in comps], default=0)
        savings = acct["opportunity_value"] * 1.75
        lines = []
        ordered = [s for role in ("Decision Maker", "Economic Buyer", "Champion")
                   for s in stks if s["influence"] == role]
        for s in ordered:
            first = s["name"].split(" ")[0]
            if s["influence"] == "Decision Maker":
                lines.append(f"- **{s['role'].split(' ')[0]} {first}:** API-first ERP integration, "
                             f"3 {s['role'].split(' ')[0]} references available")
            elif s["influence"] == "Economic Buyer":
                speed = f", {_OUR_PROFILE['impl_weeks']}-week vs {their_weeks}-week implementation" if their_weeks else ""
                lines.append(f"- **{s['role']} {first}:** {_short_money(savings)} savings over 3 years{speed}, "
                             f"90-day risk-free pilot")
            elif s["influence"] == "Champion":
                lines.append(f"- **Champion {first}:** Positions ops team as transformation leaders")
        return (
            "**Draft Meeting Talking Points (human review required):** tailored talking points by stakeholder\n\n"
            + "\n".join(lines) + "\n\n"
            "**Objection Handling:**\n"
            f"- Price: TCO is {_OUR_PROFILE['tco_lower_pct']}% lower with implementation/support\n"
            f"- Risk: {_OUR_PROFILE['similar_deployments']} similar deployments, "
            f"{_OUR_PROFILE['deployment_success_pct']}% success rate (synthetic reference set; "
            "validate approved references before use)\n\n"
            "Next: want the deal risk assessment?\n\n"
            "Source: [Value Engineering + Reference Database]\nAgents: ValueMessagingAgent"
        )

    # ── risk_assessment ───────────────────────────────────────
    def _risk_assessment(self, key):
        acct = _ACCOUNTS[key]
        risks = _RISKS.get(key, [])
        if not risks:
            return f"No significant risks identified for {acct['name']}. Win probability: {acct['win_probability']}%."
        critical = _critical(risks)
        table = "| Risk | Severity | Mitigation |\n|---|---|---|\n"
        for r in risks:
            table += f"| {r['risk']} | {r['severity']} | {r['mitigation']} |\n"
        actions = [r["action"] for r in risks if r["action"]]
        steps = "".join(f"{i}. {a}\n" for i, a in enumerate(actions, 1))
        return (
            f"**Deal Risk Assessment: {acct['name']}** — {len(risks)} risks identified, "
            f"{len(critical)} need action before tomorrow\n\n{table}\n"
            f"**Immediate Actions (before the meeting):**\n{steps}\n"
            f"**Win probability:** {acct['win_probability']}% | **Close target:** {acct['close_target_days']} days\n"
            f"**Opportunity Value:** {_short_money(acct['opportunity_value'])}\n\n"
            "Next: generate the briefing document?\n\n"
            "Source: [Deal Analytics + Risk Models]\nAgents: DealRiskAssessmentAgent"
        )

    # ── executive_briefing ────────────────────────────────────
    def _executive_briefing(self, key):
        acct = _ACCOUNTS[key]
        risks = _RISKS.get(key, [])
        stks = _STAKEHOLDERS.get(key, [])
        checklist = "".join(f"- {item}\n" for item in _checklist(key))
        return (
            f"**Account Intelligence Briefing: {acct['name']}** — briefing complete.\n\n"
            f"| Summary | Status |\n|---|---|\n"
            f"| Deal value | {_short_money(acct['opportunity_value'])} |\n"
            f"| Win probability | {acct['win_probability']}% |\n"
            f"| Stakeholders | {len(stks)} mapped |\n"
            f"| Risks | {len(risks)} ({len(_critical(risks))} critical) |\n\n"
            f"**Pre-Meeting Checklist:**\n{checklist}\n"
            "You're prepared with full account intelligence, stakeholder insights, and competitive positioning.\n\n"
            "Source: [All Intelligence Systems]\nAgents: BriefingDocumentAgent (orchestrating all agents)"
        )


if __name__ == "__main__":
    agent = AccountIntelligenceAgent()
    for op in ["account_overview", "stakeholder_map", "competitive_intel",
               "value_messaging", "risk_assessment", "executive_briefing"]:
        print("=" * 60)
        print(agent.perform(operation=op, account_name="Acme Corporation"))
        print()
