"""
Stakeholder Engagement Agent

Tracks stakeholder engagement across active deals, maps relationship
networks within buying committees, generates targeted engagement plans,
and analyzes sentiment signals from meetings and communications. Ensures
multi-threaded relationships and proactive stakeholder management.

Where a real deployment would call Salesforce, Gong, LinkedIn Sales
Navigator, etc., this agent uses a synthetic data layer so it runs
anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ===================================================================
# RAPP AGENT MANIFEST
# ===================================================================
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/deal-stakeholder-engagement",
    "version": "1.0.0",
    "display_name": "Stakeholder Engagement",
    "description": "Engagement scoring, relationship mapping, engagement planning, and sentiment analysis for deal stakeholders.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "stakeholder-engagement", "deal-progression", "relationships"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ===================================================================
# SYNTHETIC DATA LAYER
# ===================================================================

_STAKEHOLDERS = {
    "TechCorp Industries": {
        "deal_id": "OPP-001", "value": 890000, "stage": "Proposal", "owner": "Mike Chen",
        "contacts": [
            {"name": "Mark Reynolds", "title": "VP of IT", "role": "Economic Buyer",
             "emails": 8, "meetings": 2, "last_touch_days": 18, "sentiment": "neutral",
             "influence": "high", "support_level": "unknown"},
            {"name": "Jennifer Walsh", "title": "Director of Engineering", "role": "Technical Evaluator",
             "emails": 12, "meetings": 3, "last_touch_days": 22, "sentiment": "positive",
             "influence": "medium", "support_level": "supporter"},
            {"name": "Robert Kim", "title": "CIO", "role": "Executive Sponsor",
             "emails": 2, "meetings": 0, "last_touch_days": 45, "sentiment": "unknown",
             "influence": "very_high", "support_level": "unknown"},
            {"name": "Amanda Chen", "title": "Procurement Manager", "role": "Procurement",
             "emails": 4, "meetings": 1, "last_touch_days": 12, "sentiment": "neutral",
             "influence": "medium", "support_level": "neutral"},
            {"name": "David Park", "title": "IT Manager", "role": "End User",
             "emails": 6, "meetings": 2, "last_touch_days": 8, "sentiment": "positive",
             "influence": "low", "support_level": "champion"},
        ],
    },
    "Global Manufacturing": {
        "deal_id": "OPP-002", "value": 720000, "stage": "Negotiation", "owner": "Lisa Torres",
        "contacts": [
            {"name": "Rachel Green", "title": "Dir. Operations", "role": "Champion",
             "emails": 18, "meetings": 5, "last_touch_days": 5, "sentiment": "frustrated",
             "influence": "high", "support_level": "champion"},
            {"name": "Tom Bennett", "title": "CFO", "role": "Economic Buyer",
             "emails": 4, "meetings": 1, "last_touch_days": 14, "sentiment": "cautious",
             "influence": "very_high", "support_level": "neutral"},
            {"name": "Lisa Park", "title": "Legal Counsel", "role": "Legal",
             "emails": 10, "meetings": 2, "last_touch_days": 3, "sentiment": "neutral",
             "influence": "medium", "support_level": "blocker"},
            {"name": "James Miller", "title": "VP Manufacturing", "role": "Executive Sponsor",
             "emails": 3, "meetings": 1, "last_touch_days": 20, "sentiment": "positive",
             "influence": "very_high", "support_level": "supporter"},
        ],
    },
    "Apex Financial": {
        "deal_id": "OPP-003", "value": 580000, "stage": "Discovery", "owner": "James Park",
        "contacts": [
            {"name": "David Liu", "title": "CTO", "role": "Technical Buyer",
             "emails": 5, "meetings": 1, "last_touch_days": 12, "sentiment": "cautious",
             "influence": "very_high", "support_level": "neutral"},
            {"name": "Sarah Kim", "title": "VP Compliance", "role": "Compliance",
             "emails": 2, "meetings": 0, "last_touch_days": 30, "sentiment": "unknown",
             "influence": "high", "support_level": "unknown"},
            {"name": "Mike Torres", "title": "IT Director", "role": "Technical Evaluator",
             "emails": 3, "meetings": 1, "last_touch_days": 15, "sentiment": "neutral",
             "influence": "medium", "support_level": "neutral"},
        ],
    },
    "Metro Healthcare": {
        "deal_id": "OPP-004", "value": 440000, "stage": "Proposal", "owner": "Mike Chen",
        "contacts": [
            {"name": "Sandra Patel", "title": "VP Digital", "role": "Champion",
             "emails": 14, "meetings": 4, "last_touch_days": 9, "sentiment": "positive",
             "influence": "high", "support_level": "champion"},
            {"name": "Dr. Karen Lee", "title": "CMO", "role": "Executive Sponsor",
             "emails": 3, "meetings": 1, "last_touch_days": 14, "sentiment": "positive",
             "influence": "very_high", "support_level": "supporter"},
            {"name": "Brian Walsh", "title": "IT Security Manager", "role": "Technical Evaluator",
             "emails": 8, "meetings": 2, "last_touch_days": 7, "sentiment": "positive",
             "influence": "medium", "support_level": "supporter"},
            {"name": "Nancy Drew", "title": "Finance Director", "role": "Budget Holder",
             "emails": 2, "meetings": 0, "last_touch_days": 28, "sentiment": "unknown",
             "influence": "high", "support_level": "unknown"},
        ],
    },
    "Pacific Telecom": {
        "deal_id": "OPP-013", "value": 780000, "stage": "Negotiation", "owner": "Lisa Torres",
        "contacts": [
            {"name": "Diana Cruz", "title": "SVP Operations", "role": "Executive Sponsor",
             "emails": 16, "meetings": 5, "last_touch_days": 3, "sentiment": "very_positive",
             "influence": "very_high", "support_level": "champion"},
            {"name": "Alex Huang", "title": "VP Engineering", "role": "Technical Buyer",
             "emails": 12, "meetings": 4, "last_touch_days": 5, "sentiment": "positive",
             "influence": "high", "support_level": "supporter"},
            {"name": "Maria Santos", "title": "Procurement Director", "role": "Procurement",
             "emails": 8, "meetings": 2, "last_touch_days": 2, "sentiment": "neutral",
             "influence": "medium", "support_level": "neutral"},
            {"name": "Kevin O'Brien", "title": "CTO", "role": "Economic Buyer",
             "emails": 6, "meetings": 2, "last_touch_days": 7, "sentiment": "positive",
             "influence": "very_high", "support_level": "supporter"},
            {"name": "Priya Sharma", "title": "Data Analytics Lead", "role": "End User",
             "emails": 10, "meetings": 3, "last_touch_days": 4, "sentiment": "very_positive",
             "influence": "low", "support_level": "champion"},
        ],
    },
}

_SENTIMENT_SIGNALS = {
    "very_positive": {"score": 90, "label": "Strong advocate", "risk": "low"},
    "positive": {"score": 70, "label": "Favorable", "risk": "low"},
    "neutral": {"score": 50, "label": "Undecided", "risk": "medium"},
    "cautious": {"score": 35, "label": "Hesitant", "risk": "medium"},
    "frustrated": {"score": 30, "label": "Frustrated but engaged", "risk": "high"},
    "negative": {"score": 15, "label": "Opposed", "risk": "critical"},
    "unknown": {"score": 40, "label": "No signal", "risk": "medium"},
}


# ===================================================================
# HELPERS
# ===================================================================

def _engagement_score(contact):
    """Calculate engagement score for a single contact."""
    email_score = min(contact["emails"] * 5, 30)
    meeting_score = min(contact["meetings"] * 15, 30)
    recency_score = max(0, 25 - contact["last_touch_days"]) * 1.5
    sentiment_data = _SENTIMENT_SIGNALS.get(contact["sentiment"], {"score": 40})
    sentiment_score = sentiment_data["score"] * 0.2
    return round(min(100, email_score + meeting_score + recency_score + sentiment_score))


def _deal_engagement_score(deal_name):
    """Calculate aggregate engagement score for a deal."""
    deal = _STAKEHOLDERS.get(deal_name, {})
    contacts = deal.get("contacts", [])
    if not contacts:
        return 0
    influence_weights = {"very_high": 3, "high": 2, "medium": 1.5, "low": 1}
    weighted_sum = 0
    weight_total = 0
    for c in contacts:
        w = influence_weights.get(c["influence"], 1)
        weighted_sum += _engagement_score(c) * w
        weight_total += w
    return round(weighted_sum / max(weight_total, 1))


def _relationship_gaps(deal_name):
    """Identify gaps in relationship coverage."""
    deal = _STAKEHOLDERS.get(deal_name, {})
    contacts = deal.get("contacts", [])
    gaps = []
    has_champion = any(c["support_level"] == "champion" for c in contacts)
    has_exec = any(c["role"] in ("Executive Sponsor", "Economic Buyer") and c["last_touch_days"] <= 14 for c in contacts)
    has_technical = any(c["role"] == "Technical Evaluator" and c["sentiment"] in ("positive", "very_positive") for c in contacts)

    if not has_champion:
        gaps.append("No active champion identified")
    if not has_exec:
        gaps.append("Executive sponsor not recently engaged")
    if not has_technical:
        gaps.append("Technical evaluator not positively engaged")
    for c in contacts:
        if c["last_touch_days"] >= 21 and c["influence"] in ("high", "very_high"):
            gaps.append(f"{c['name']} ({c['title']}) -- no contact in {c['last_touch_days']} days")
    if len(contacts) < 3:
        gaps.append(f"Only {len(contacts)} contacts -- recommend 4+ for multi-threading")
    return gaps


# ===================================================================
# AGENT CLASS
# ===================================================================

class StakeholderEngagementAgent(BasicAgent):
    """
    Tracks and optimizes stakeholder engagement for pipeline deals.

    Operations:
        engagement_score   - per-deal and per-contact engagement scoring
        relationship_map   - buying committee mapping with gaps
        engagement_plan    - targeted outreach plan per deal
        sentiment_analysis - sentiment signals and risk assessment
    """

    def __init__(self):
        self.name = "StakeholderEngagementAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["engagement_score", "relationship_map", "engagement_plan", "sentiment_analysis"],
                        "description": "The analysis to perform",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "engagement_score")
        dispatch = {
            "engagement_score": self._engagement_score,
            "relationship_map": self._relationship_map,
            "engagement_plan": self._engagement_plan,
            "sentiment_analysis": self._sentiment_analysis,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation '{op}'. Valid: {', '.join(dispatch.keys())}"
        return handler()

    # -- engagement_score ----------------------------------------------
    def _engagement_score(self) -> str:
        sections = []
        for deal_name in sorted(_STAKEHOLDERS.keys(), key=lambda d: -_STAKEHOLDERS[d]["value"]):
            deal = _STAKEHOLDERS[deal_name]
            deal_score = _deal_engagement_score(deal_name)
            grade = "A" if deal_score >= 75 else ("B" if deal_score >= 55 else ("C" if deal_score >= 40 else "D"))

            contact_rows = ""
            for c in sorted(deal["contacts"], key=lambda x: -_engagement_score(x)):
                score = _engagement_score(c)
                contact_rows += (f"| {c['name']} | {c['title']} | {c['role']} | "
                                 f"{score}/100 | {c['last_touch_days']}d ago | {c['influence']} |\n")

            sections.append(
                f"**{deal_name} -- ${deal['value']:,} ({deal['stage']})**\n"
                f"Deal Engagement: **{deal_score}/100 [{grade}]** | "
                f"Contacts: {len(deal['contacts'])} | Owner: {deal['owner']}\n\n"
                f"| Contact | Title | Role | Score | Last Touch | Influence |\n"
                f"|---------|-------|------|-------|-----------|----------|\n"
                f"{contact_rows}"
            )

        return (
            f"**Stakeholder Engagement Scores**\n\n"
            + "\n---\n\n".join(sections)
            + f"\n\nSource: [CRM + Email Analytics + Calendar]\n"
            f"Agents: EngagementScoringEngine"
        )

    # -- relationship_map ----------------------------------------------
    def _relationship_map(self) -> str:
        sections = []
        for deal_name in sorted(_STAKEHOLDERS.keys(), key=lambda d: -_STAKEHOLDERS[d]["value"]):
            deal = _STAKEHOLDERS[deal_name]
            gaps = _relationship_gaps(deal_name)

            map_rows = ""
            for c in deal["contacts"]:
                support_icon = {"champion": "CHAMPION", "supporter": "Supporter",
                                "neutral": "Neutral", "blocker": "BLOCKER",
                                "unknown": "Unknown"}.get(c["support_level"], "Unknown")
                map_rows += (f"| {c['name']} | {c['title']} | {c['role']} | "
                             f"{c['influence']} | {support_icon} |\n")

            gap_lines = "\n".join(f"  - {g}" for g in gaps) if gaps else "  - No critical gaps identified"

            sections.append(
                f"**{deal_name} -- ${deal['value']:,}**\n"
                f"Buying Committee ({len(deal['contacts'])} mapped):\n\n"
                f"| Contact | Title | Role | Influence | Support |\n"
                f"|---------|-------|------|----------|--------|\n"
                f"{map_rows}\n"
                f"**Relationship Gaps:**\n{gap_lines}\n"
            )

        return (
            f"**Relationship Map -- Buying Committee Analysis**\n\n"
            + "\n---\n\n".join(sections)
            + f"\n\nSource: [CRM Contacts + LinkedIn + Meeting History]\n"
            f"Agents: RelationshipMappingAgent"
        )

    # -- engagement_plan -----------------------------------------------
    def _engagement_plan(self) -> str:
        sections = []
        for deal_name in sorted(_STAKEHOLDERS.keys(), key=lambda d: -_STAKEHOLDERS[d]["value"]):
            deal = _STAKEHOLDERS[deal_name]
            contacts = deal["contacts"]

            actions = []
            for c in sorted(contacts, key=lambda x: _engagement_score(x)):
                score = _engagement_score(c)
                if score < 40:
                    actions.append(f"- **{c['name']} ({c['title']}):** Re-engagement outreach -- "
                                   f"personalized email + meeting request (Score: {score}/100)")
                elif c["last_touch_days"] >= 14:
                    actions.append(f"- **{c['name']} ({c['title']}):** Schedule touchpoint -- "
                                   f"{c['last_touch_days']} days since last contact")
                elif c["support_level"] == "unknown":
                    actions.append(f"- **{c['name']} ({c['title']}):** Sentiment discovery -- "
                                   f"informal 1:1 to assess support level")

            if not actions:
                actions.append("- All stakeholders adequately engaged -- maintain cadence")

            sections.append(
                f"**{deal_name} -- ${deal['value']:,}**\n"
                f"Owner: {deal['owner']} | Stage: {deal['stage']}\n\n"
                + "\n".join(actions)
            )

        return (
            f"**Engagement Plans -- Targeted Outreach**\n\n"
            + "\n\n---\n\n".join(sections)
            + f"\n\n**General Best Practices:**\n"
            f"- Touch all high-influence contacts at least every 10 days\n"
            f"- Multi-thread to 4+ contacts before Proposal stage\n"
            f"- Confirm champion support monthly with direct conversation\n"
            f"- Engage executive sponsor before any pricing discussion\n\n"
            f"Source: [Engagement Data + Best Practice Playbook]\n"
            f"Agents: EngagementPlannerAgent"
        )

    # -- sentiment_analysis --------------------------------------------
    def _sentiment_analysis(self) -> str:
        sections = []
        for deal_name in sorted(_STAKEHOLDERS.keys(), key=lambda d: -_STAKEHOLDERS[d]["value"]):
            deal = _STAKEHOLDERS[deal_name]

            rows = ""
            risk_contacts = 0
            for c in deal["contacts"]:
                sig = _SENTIMENT_SIGNALS.get(c["sentiment"], {"score": 40, "label": "Unknown", "risk": "medium"})
                rows += (f"| {c['name']} | {c['title']} | {c['sentiment']} | "
                         f"{sig['score']}/100 | {sig['label']} | {sig['risk']} |\n")
                if sig["risk"] in ("high", "critical"):
                    risk_contacts += 1

            avg_sentiment = round(sum(
                _SENTIMENT_SIGNALS.get(c["sentiment"], {"score": 40})["score"]
                for c in deal["contacts"]
            ) / max(len(deal["contacts"]), 1))

            overall_risk = "HIGH" if risk_contacts >= 2 else ("MEDIUM" if risk_contacts >= 1 else "LOW")

            sections.append(
                f"**{deal_name} -- ${deal['value']:,}**\n"
                f"Avg Sentiment: {avg_sentiment}/100 | Risk Contacts: {risk_contacts} | Overall: {overall_risk}\n\n"
                f"| Contact | Title | Sentiment | Score | Label | Risk |\n"
                f"|---------|-------|-----------|-------|-------|------|\n"
                f"{rows}"
            )

        return (
            f"**Sentiment Analysis -- Stakeholder Signals**\n\n"
            + "\n---\n\n".join(sections)
            + f"\n\n**Signal Interpretation:**\n"
            f"- Very Positive (90): Strong internal advocate\n"
            f"- Positive (70): Favorable, continue engagement\n"
            f"- Neutral (50): Needs value reinforcement\n"
            f"- Cautious (35): Address concerns proactively\n"
            f"- Frustrated (30): Engaged but at risk -- resolve issues quickly\n"
            f"- Unknown (40): Requires direct interaction to assess\n\n"
            f"Source: [Gong Call Analysis + Email Sentiment + Meeting Notes]\n"
            f"Agents: SentimentAnalysisEngine"
        )


if __name__ == "__main__":
    agent = StakeholderEngagementAgent()
    for op in ["engagement_score", "relationship_map", "engagement_plan", "sentiment_analysis"]:
        print("=" * 70)
        print(agent.perform(operation=op))
        print()
