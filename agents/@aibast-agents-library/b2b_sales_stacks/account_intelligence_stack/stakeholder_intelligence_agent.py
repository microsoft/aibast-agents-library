"""
Stakeholder Intelligence Agent

Maps organizational hierarchies, analyzes buying committees, identifies
engagement gaps, and scores relationship strength for enterprise B2B
accounts. Provides actionable recommendations for stakeholder engagement
and champion development.

Where a real deployment would call LinkedIn Sales Navigator and CRM APIs,
this agent uses a synthetic data layer so it runs anywhere without
credentials.
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
    "name": "@aibast-agents-library/stakeholder-intelligence",
    "version": "1.0.0",
    "display_name": "Stakeholder Intelligence",
    "description": "Maps org charts, analyzes buying committees, and scores relationship strength for enterprise accounts.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "stakeholder-mapping", "org-chart", "buying-committee"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_ACCOUNTS = {
    "acme": {"id": "acc-001", "name": "Acme Corporation", "industry": "Manufacturing", "employees": 12_400},
    "contoso": {"id": "acc-002", "name": "Contoso Ltd", "industry": "Technology", "employees": 4_200},
    "fabrikam": {"id": "acc-003", "name": "Fabrikam Industries", "industry": "Manufacturing", "employees": 8_700},
    "northwind": {"id": "acc-004", "name": "Northwind Traders", "industry": "Retail", "employees": 3_100},
}

_ORG_HIERARCHIES = {
    "acme": [
        {"name": "Tom Bradley", "role": "CEO", "reports_to": None, "department": "Executive", "level": "C-Suite", "tenure_years": 8},
        {"name": "Sarah Chen", "role": "CTO", "reports_to": "Tom Bradley", "department": "Technology", "level": "C-Suite", "tenure_years": 0.1},
        {"name": "Lisa Park", "role": "CFO", "reports_to": "Tom Bradley", "department": "Finance", "level": "C-Suite", "tenure_years": 5},
        {"name": "James Miller", "role": "VP Operations", "reports_to": "Tom Bradley", "department": "Operations", "level": "VP", "tenure_years": 3},
        {"name": "Kevin Park", "role": "VP Engineering", "reports_to": "Sarah Chen", "department": "Engineering", "level": "VP", "tenure_years": 2},
        {"name": "David Wong", "role": "IT Director", "reports_to": "Sarah Chen", "department": "IT", "level": "Director", "tenure_years": 4},
        {"name": "Maria Lopez", "role": "Director of Strategy", "reports_to": "Tom Bradley", "department": "Strategy", "level": "Director", "tenure_years": 1},
        {"name": "Rachel Torres", "role": "Procurement Manager", "reports_to": "Lisa Park", "department": "Procurement", "level": "Manager", "tenure_years": 6},
    ],
    "contoso": [
        {"name": "Alex Kim", "role": "CTO", "reports_to": "CEO", "department": "Technology", "level": "C-Suite", "tenure_years": 4},
        {"name": "Pat Johnson", "role": "CFO", "reports_to": "CEO", "department": "Finance", "level": "C-Suite", "tenure_years": 3},
        {"name": "Sam Rivera", "role": "VP Product", "reports_to": "Alex Kim", "department": "Product", "level": "VP", "tenure_years": 2},
    ],
    "fabrikam": [
        {"name": "Chris Anderson", "role": "VP IT", "reports_to": "CEO", "department": "IT", "level": "VP", "tenure_years": 0.5},
        {"name": "Dana White", "role": "COO", "reports_to": "CEO", "department": "Operations", "level": "C-Suite", "tenure_years": 6},
    ],
    "northwind": [
        {"name": "Jordan Lee", "role": "CTO", "reports_to": "Casey Brown", "department": "Technology", "level": "C-Suite", "tenure_years": 2},
        {"name": "Casey Brown", "role": "CEO", "reports_to": None, "department": "Executive", "level": "C-Suite", "tenure_years": 10},
    ],
}

_BUYING_COMMITTEE = {
    "acme": [
        {"name": "Sarah Chen", "role": "CTO", "committee_role": "Decision Maker", "budget_authority": True, "veto_power": True, "priority": "Technical architecture and scalability"},
        {"name": "Lisa Park", "role": "CFO", "committee_role": "Economic Buyer", "budget_authority": True, "veto_power": True, "priority": "ROI and total cost of ownership"},
        {"name": "James Miller", "role": "VP Operations", "committee_role": "Champion", "budget_authority": False, "veto_power": False, "priority": "Operational efficiency gains"},
        {"name": "David Wong", "role": "IT Director", "committee_role": "Technical Evaluator", "budget_authority": False, "veto_power": False, "priority": "Integration and security"},
        {"name": "Rachel Torres", "role": "Procurement", "committee_role": "Gatekeeper", "budget_authority": False, "veto_power": True, "priority": "Compliance and vendor terms"},
        {"name": "Tom Bradley", "role": "CEO", "committee_role": "Executive Sponsor", "budget_authority": True, "veto_power": True, "priority": "Strategic alignment"},
    ],
    "contoso": [
        {"name": "Alex Kim", "role": "CTO", "committee_role": "Decision Maker", "budget_authority": True, "veto_power": True, "priority": "Platform consolidation"},
        {"name": "Pat Johnson", "role": "CFO", "committee_role": "Economic Buyer", "budget_authority": True, "veto_power": True, "priority": "Budget optimization"},
        {"name": "Sam Rivera", "role": "VP Product", "committee_role": "Champion", "budget_authority": False, "veto_power": False, "priority": "Product expansion"},
    ],
    "fabrikam": [
        {"name": "Chris Anderson", "role": "VP IT", "committee_role": "Decision Maker", "budget_authority": True, "veto_power": True, "priority": "IT modernization"},
        {"name": "Dana White", "role": "COO", "committee_role": "Champion", "budget_authority": False, "veto_power": False, "priority": "Operational efficiency"},
    ],
    "northwind": [
        {"name": "Jordan Lee", "role": "CTO", "committee_role": "Decision Maker", "budget_authority": True, "veto_power": True, "priority": "E-commerce technology"},
        {"name": "Casey Brown", "role": "CEO", "committee_role": "Executive Sponsor", "budget_authority": True, "veto_power": True, "priority": "Growth strategy"},
    ],
}

_ENGAGEMENT_DATA = {
    "acme": {
        "Sarah Chen": {"meetings": 0, "emails_sent": 0, "emails_opened": 0, "last_touch": None, "sentiment": "Unknown", "content_downloaded": []},
        "James Miller": {"meetings": 14, "emails_sent": 22, "emails_opened": 18, "last_touch": "2025-03-12", "sentiment": "Positive", "content_downloaded": ["ROI Calculator", "Case Study: Manufacturing"]},
        "Lisa Park": {"meetings": 2, "emails_sent": 8, "emails_opened": 5, "last_touch": "2025-02-28", "sentiment": "Neutral", "content_downloaded": ["Executive Summary"]},
        "David Wong": {"meetings": 8, "emails_sent": 15, "emails_opened": 12, "last_touch": "2025-03-10", "sentiment": "Positive", "content_downloaded": ["API Docs", "Security Whitepaper", "Integration Guide"]},
        "Rachel Torres": {"meetings": 1, "emails_sent": 3, "emails_opened": 2, "last_touch": "2025-02-15", "sentiment": "Neutral", "content_downloaded": []},
        "Kevin Park": {"meetings": 5, "emails_sent": 10, "emails_opened": 8, "last_touch": "2025-03-08", "sentiment": "Positive", "content_downloaded": ["Technical Architecture"]},
        "Maria Lopez": {"meetings": 0, "emails_sent": 2, "emails_opened": 0, "last_touch": None, "sentiment": "Unknown", "content_downloaded": []},
        "Tom Bradley": {"meetings": 0, "emails_sent": 0, "emails_opened": 0, "last_touch": None, "sentiment": "Unknown", "content_downloaded": []},
    },
    "contoso": {
        "Alex Kim": {"meetings": 10, "emails_sent": 18, "emails_opened": 16, "last_touch": "2025-03-13", "sentiment": "Positive", "content_downloaded": ["Platform Overview", "Roadmap"]},
        "Pat Johnson": {"meetings": 3, "emails_sent": 6, "emails_opened": 3, "last_touch": "2025-02-20", "sentiment": "Neutral", "content_downloaded": []},
        "Sam Rivera": {"meetings": 7, "emails_sent": 12, "emails_opened": 10, "last_touch": "2025-03-11", "sentiment": "Positive", "content_downloaded": ["Product Demo", "Expansion Guide"]},
    },
    "fabrikam": {
        "Chris Anderson": {"meetings": 4, "emails_sent": 8, "emails_opened": 6, "last_touch": "2025-03-04", "sentiment": "Neutral", "content_downloaded": ["Overview Deck"]},
        "Dana White": {"meetings": 6, "emails_sent": 10, "emails_opened": 9, "last_touch": "2025-03-10", "sentiment": "Positive", "content_downloaded": ["Ops Case Study"]},
    },
    "northwind": {
        "Jordan Lee": {"meetings": 1, "emails_sent": 3, "emails_opened": 1, "last_touch": "2025-02-12", "sentiment": "Unknown", "content_downloaded": []},
        "Casey Brown": {"meetings": 0, "emails_sent": 0, "emails_opened": 0, "last_touch": None, "sentiment": "Unknown", "content_downloaded": []},
    },
}

_INFLUENCE_SCORES = {
    "acme": {
        "Sarah Chen": 92, "Tom Bradley": 95, "Lisa Park": 85, "James Miller": 78,
        "David Wong": 62, "Kevin Park": 58, "Rachel Torres": 55, "Maria Lopez": 50,
    },
    "contoso": {"Alex Kim": 90, "Pat Johnson": 82, "Sam Rivera": 70},
    "fabrikam": {"Chris Anderson": 85, "Dana White": 80},
    "northwind": {"Jordan Lee": 88, "Casey Brown": 95},
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


def _relationship_score(engagement):
    """Compute 0-100 relationship score from engagement data."""
    meetings_score = min(40, engagement["meetings"] * 3)
    email_score = min(20, engagement["emails_opened"])
    recency_score = 0
    if engagement["last_touch"]:
        days_since = 14  # synthetic approximation
        recency_score = max(0, 25 - days_since)
    content_score = min(15, len(engagement["content_downloaded"]) * 5)
    sentiment_bonus = {"Positive": 10, "Neutral": 3, "Unknown": 0}
    total = meetings_score + email_score + recency_score + content_score + sentiment_bonus.get(engagement["sentiment"], 0)
    return min(100, total)


def _engagement_gap_severity(engagement, committee_member):
    """Assess gap severity based on role importance and engagement level."""
    score = _relationship_score(engagement)
    has_veto = committee_member.get("veto_power", False)
    has_budget = committee_member.get("budget_authority", False)

    if score == 0 and (has_veto or has_budget):
        return "Critical"
    if score < 20 and has_veto:
        return "High"
    if score < 30:
        return "Medium"
    return "Low"


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class StakeholderIntelligenceAgent(BasicAgent):
    """
    Provides deep stakeholder intelligence for enterprise accounts.

    Operations:
        map_org_chart           - organizational hierarchy mapping
        analyze_buying_committee - buying committee analysis with roles
        engagement_gaps         - identify and prioritize engagement gaps
        relationship_strength   - score and rank all relationships
    """

    def __init__(self):
        self.name = "StakeholderIntelligenceAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "map_org_chart", "analyze_buying_committee",
                            "engagement_gaps", "relationship_strength",
                        ],
                        "description": "The stakeholder analysis to perform",
                    },
                    "account_name": {
                        "type": "string",
                        "description": "Account name (e.g. 'Acme Corporation')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "map_org_chart")
        key = _resolve_account(kwargs.get("account_name", ""))
        dispatch = {
            "map_org_chart": self._map_org_chart,
            "analyze_buying_committee": self._analyze_buying_committee,
            "engagement_gaps": self._engagement_gaps,
            "relationship_strength": self._relationship_strength,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`."
        return handler(key)

    # ── map_org_chart ─────────────────────────────────────────
    def _map_org_chart(self, key):
        acct = _ACCOUNTS[key]
        org = _ORG_HIERARCHIES.get(key, [])

        if not org:
            return f"**Org Chart: {acct['name']}**\n\nNo organizational data mapped yet."

        org_rows = ""
        for p in org:
            reports = p["reports_to"] or "Board"
            tenure = f"{p['tenure_years']:.1f}" if p["tenure_years"] < 1 else str(int(p["tenure_years"]))
            org_rows += f"| {p['name']} | {p['role']} | {p['department']} | {p['level']} | {reports} | {tenure}yr |\n"

        c_suite = [p for p in org if p["level"] == "C-Suite"]
        vp_level = [p for p in org if p["level"] == "VP"]
        directors = [p for p in org if p["level"] in ("Director", "Manager")]
        new_hires = [p for p in org if p["tenure_years"] < 1]

        new_hire_note = ""
        if new_hires:
            new_hire_note = "\n**Recent Changes:**\n" + "".join(
                f"- {p['name']} ({p['role']}): New to role ({p['tenure_years']:.1f}yr tenure)\n" for p in new_hires
            )

        return (
            f"**Org Chart: {acct['name']}**\n\n"
            f"| Name | Role | Department | Level | Reports To | Tenure |\n|---|---|---|---|---|---|\n"
            f"{org_rows}\n"
            f"**Structure Summary:**\n"
            f"- C-Suite: {len(c_suite)} executives\n"
            f"- VP Level: {len(vp_level)} leaders\n"
            f"- Director/Manager: {len(directors)} contacts\n"
            f"- Total Mapped: {len(org)} stakeholders\n"
            f"{new_hire_note}\n"
            f"Source: [LinkedIn Sales Navigator + CRM + Org Intelligence]\n"
            f"Agents: StakeholderIntelligenceAgent"
        )

    # ── analyze_buying_committee ──────────────────────────────
    def _analyze_buying_committee(self, key):
        acct = _ACCOUNTS[key]
        committee = _BUYING_COMMITTEE.get(key, [])
        engagement = _ENGAGEMENT_DATA.get(key, {})

        if not committee:
            return f"**Buying Committee: {acct['name']}**\n\nNo buying committee mapped yet."

        rows = ""
        for m in committee:
            eng = engagement.get(m["name"], {})
            meetings = eng.get("meetings", 0)
            sentiment = eng.get("sentiment", "Unknown")
            rows += (
                f"| {m['name']} | {m['role']} | {m['committee_role']} | "
                f"{'Yes' if m['budget_authority'] else 'No'} | "
                f"{'Yes' if m['veto_power'] else 'No'} | "
                f"{meetings} mtgs | {sentiment} |\n"
            )

        veto_holders = [m for m in committee if m["veto_power"]]
        budget_holders = [m for m in committee if m["budget_authority"]]
        champions = [m for m in committee if m["committee_role"] == "Champion"]

        champion_intel = ""
        if champions:
            c = champions[0]
            c_eng = engagement.get(c["name"], {})
            champion_intel = (
                f"\n**Champion Profile: {c['name']}**\n"
                f"- Role: {c['role']} | Priority: {c['priority']}\n"
                f"- Meetings: {c_eng.get('meetings', 0)} | Sentiment: {c_eng.get('sentiment', 'Unknown')}\n"
                f"- Content engaged: {', '.join(c_eng.get('content_downloaded', ['None']))}\n"
            )

        return (
            f"**Buying Committee Analysis: {acct['name']}**\n\n"
            f"| Name | Role | Committee Role | Budget Auth | Veto | Engagement | Sentiment |\n|---|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Committee Composition:**\n"
            f"- Total members: {len(committee)}\n"
            f"- Veto holders: {len(veto_holders)} ({', '.join(v['name'] for v in veto_holders)})\n"
            f"- Budget authority: {len(budget_holders)} ({', '.join(b['name'] for b in budget_holders)})\n"
            f"- Champions: {len(champions)}\n"
            f"{champion_intel}\n"
            f"Source: [LinkedIn + CRM + Meeting History]\n"
            f"Agents: StakeholderIntelligenceAgent"
        )

    # ── engagement_gaps ───────────────────────────────────────
    def _engagement_gaps(self, key):
        acct = _ACCOUNTS[key]
        committee = _BUYING_COMMITTEE.get(key, [])
        engagement = _ENGAGEMENT_DATA.get(key, {})

        gaps = []
        for m in committee:
            eng = engagement.get(m["name"], {"meetings": 0, "emails_sent": 0, "emails_opened": 0, "last_touch": None, "sentiment": "Unknown", "content_downloaded": []})
            score = _relationship_score(eng)
            severity = _engagement_gap_severity(eng, m)
            if score < 50:
                gaps.append({
                    "name": m["name"], "role": m["role"],
                    "committee_role": m["committee_role"],
                    "relationship_score": score, "severity": severity,
                    "veto_power": m["veto_power"],
                    "meetings": eng.get("meetings", 0),
                    "last_touch": eng.get("last_touch"),
                    "priority": m["priority"],
                })

        gaps.sort(key=lambda g: {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(g["severity"], 4))

        if not gaps:
            return f"**Engagement Gaps: {acct['name']}**\n\nNo significant engagement gaps identified. All key stakeholders are adequately engaged."

        gap_rows = ""
        for g in gaps:
            last = g["last_touch"] or "Never"
            gap_rows += (
                f"| {g['name']} | {g['role']} | {g['committee_role']} | "
                f"{g['severity']} | {g['relationship_score']}/100 | {g['meetings']} | {last} |\n"
            )

        actions = "\n**Recommended Actions:**\n"
        for i, g in enumerate(gaps[:5], 1):
            if g["severity"] == "Critical":
                actions += f"{i}. **Urgent:** Get champion intro to {g['name']} ({g['role']}) — controls {g['priority']}\n"
            elif g["severity"] == "High":
                actions += f"{i}. **This week:** Schedule meeting with {g['name']} — {g['priority']}\n"
            else:
                actions += f"{i}. Plan touchpoint with {g['name']} ({g['role']})\n"

        return (
            f"**Engagement Gaps: {acct['name']}**\n\n"
            f"Gaps identified: {len(gaps)} stakeholders below engagement threshold\n\n"
            f"| Name | Role | Committee Role | Severity | Score | Meetings | Last Touch |\n|---|---|---|---|---|---|---|\n"
            f"{gap_rows}"
            f"{actions}\n"
            f"Source: [CRM Engagement + Meeting History + Email Analytics]\n"
            f"Agents: StakeholderIntelligenceAgent"
        )

    # ── relationship_strength ─────────────────────────────────
    def _relationship_strength(self, key):
        acct = _ACCOUNTS[key]
        engagement = _ENGAGEMENT_DATA.get(key, {})
        influence = _INFLUENCE_SCORES.get(key, {})

        scored = []
        for name, eng in engagement.items():
            rel_score = _relationship_score(eng)
            inf_score = influence.get(name, 50)
            weighted = int(rel_score * 0.6 + inf_score * 0.4)
            scored.append({
                "name": name, "relationship_score": rel_score,
                "influence_score": inf_score, "weighted_score": weighted,
                "meetings": eng["meetings"], "sentiment": eng["sentiment"],
                "content": len(eng["content_downloaded"]),
            })

        scored.sort(key=lambda s: s["weighted_score"], reverse=True)

        rows = ""
        for s in scored:
            rows += (
                f"| {s['name']} | {s['relationship_score']}/100 | "
                f"{s['influence_score']}/100 | {s['weighted_score']}/100 | "
                f"{s['meetings']} | {s['sentiment']} | {s['content']} |\n"
            )

        avg_rel = int(sum(s["relationship_score"] for s in scored) / max(len(scored), 1))
        strong = sum(1 for s in scored if s["weighted_score"] >= 60)
        weak = sum(1 for s in scored if s["weighted_score"] < 30)

        top = scored[0] if scored else None
        weakest = scored[-1] if scored else None

        summary = ""
        if top and weakest:
            summary = (
                f"\n**Key Insights:**\n"
                f"- Strongest relationship: {top['name']} (score: {top['weighted_score']})\n"
                f"- Weakest relationship: {weakest['name']} (score: {weakest['weighted_score']})\n"
                f"- Average relationship score: {avg_rel}/100\n"
                f"- Strong relationships (60+): {strong}\n"
                f"- Weak relationships (<30): {weak}\n"
            )

        return (
            f"**Relationship Strength: {acct['name']}**\n\n"
            f"| Name | Relationship | Influence | Weighted | Meetings | Sentiment | Content |\n|---|---|---|---|---|---|---|\n"
            f"{rows}"
            f"{summary}\n"
            f"Source: [CRM + LinkedIn + Meeting History + Content Analytics]\n"
            f"Agents: StakeholderIntelligenceAgent"
        )


if __name__ == "__main__":
    agent = StakeholderIntelligenceAgent()
    for op in ["map_org_chart", "analyze_buying_committee", "engagement_gaps", "relationship_strength"]:
        print("=" * 60)
        print(agent.perform(operation=op, account_name="Acme Corporation"))
        print()
