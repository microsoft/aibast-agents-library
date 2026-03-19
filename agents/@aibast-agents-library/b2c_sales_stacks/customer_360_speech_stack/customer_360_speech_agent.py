"""
Customer 360 & Speech Agent — B2C Sales Stack

Provides unified customer profiles, interaction history, sentiment
analysis, and next-best-action recommendations across all channels.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/customer-360-speech",
    "version": "1.0.0",
    "display_name": "Customer 360 & Speech Agent",
    "description": "Unified customer profiles with interaction history, sentiment analysis, and next-best-action recommendations.",
    "author": "AIBAST",
    "tags": ["customer-360", "speech", "sentiment", "omnichannel", "profile", "b2c"],
    "category": "b2c_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

CUSTOMER_PROFILES = {
    "C360-001": {
        "name": "Jessica Alvarez",
        "email": "j.alvarez@example.com",
        "phone": "(555) 234-5678",
        "segment": "premium",
        "lifetime_value": 12450,
        "member_since": "2019-06-15",
        "preferred_channel": "mobile_app",
        "preferences": {"categories": ["electronics", "home"], "communication": "email", "language": "en"},
        "purchase_history_summary": {"total_orders": 47, "avg_order_value": 264.89, "last_order": "2025-02-28", "return_rate": 4.2},
    },
    "C360-002": {
        "name": "Brian O'Connell",
        "email": "b.oconnell@example.com",
        "phone": "(555) 876-1234",
        "segment": "standard",
        "lifetime_value": 3280,
        "member_since": "2022-01-10",
        "preferred_channel": "website",
        "preferences": {"categories": ["sports", "outdoor"], "communication": "sms", "language": "en"},
        "purchase_history_summary": {"total_orders": 15, "avg_order_value": 218.67, "last_order": "2025-01-15", "return_rate": 8.0},
    },
    "C360-003": {
        "name": "Mei Lin Zhang",
        "email": "m.zhang@example.com",
        "phone": "(555) 445-9012",
        "segment": "at_risk",
        "lifetime_value": 5890,
        "member_since": "2020-09-22",
        "preferred_channel": "phone",
        "preferences": {"categories": ["fashion", "beauty"], "communication": "email", "language": "en"},
        "purchase_history_summary": {"total_orders": 28, "avg_order_value": 210.36, "last_order": "2024-10-05", "return_rate": 12.5},
    },
}

INTERACTION_HISTORY = {
    "C360-001": [
        {"date": "2025-03-05", "channel": "mobile_app", "type": "purchase", "details": "Order #ORD-88421 — Wireless Speaker", "sentiment": "positive", "agent": None},
        {"date": "2025-02-20", "channel": "chat", "type": "inquiry", "details": "Asked about loyalty points redemption", "sentiment": "positive", "agent": "ChatBot"},
        {"date": "2025-02-10", "channel": "email", "type": "campaign_click", "details": "Clicked spring sale email — viewed 3 products", "sentiment": "neutral", "agent": None},
        {"date": "2025-01-28", "channel": "phone", "type": "support", "details": "Delivery delay on order #ORD-87910", "sentiment": "negative", "agent": "Agent_Kelly"},
    ],
    "C360-002": [
        {"date": "2025-01-15", "channel": "website", "type": "purchase", "details": "Order #ORD-85220 — Hiking Boots", "sentiment": "positive", "agent": None},
        {"date": "2025-01-02", "channel": "email", "type": "campaign_open", "details": "Opened New Year promotion email", "sentiment": "neutral", "agent": None},
    ],
    "C360-003": [
        {"date": "2024-12-15", "channel": "phone", "type": "complaint", "details": "Wrong size shipped on order #ORD-84100 — requested refund", "sentiment": "negative", "agent": "Agent_Marcus"},
        {"date": "2024-10-05", "channel": "website", "type": "purchase", "details": "Order #ORD-82450 — Fall collection items", "sentiment": "neutral", "agent": None},
        {"date": "2024-09-20", "channel": "chat", "type": "support", "details": "Sizing guidance for dresses", "sentiment": "positive", "agent": "ChatBot"},
        {"date": "2024-08-14", "channel": "phone", "type": "complaint", "details": "Late delivery — order arrived 5 days after estimate", "sentiment": "negative", "agent": "Agent_Kelly"},
    ],
}

NEXT_BEST_ACTIONS = {
    "premium_engagement": {"action": "Send personalized VIP preview of new collection", "channel": "email", "timing": "immediate", "expected_conversion": 22.5},
    "win_back": {"action": "Send win-back offer with 20% discount and free shipping", "channel": "email", "timing": "immediate", "expected_conversion": 15.0},
    "loyalty_nurture": {"action": "Remind of loyalty points balance and redemption options", "channel": "mobile_push", "timing": "next_3_days", "expected_conversion": 18.0},
    "service_recovery": {"action": "Proactive outreach from manager with apology and store credit", "channel": "phone", "timing": "immediate", "expected_conversion": 35.0},
    "cross_sell": {"action": "Recommend complementary products based on purchase history", "channel": "email", "timing": "next_7_days", "expected_conversion": 12.0},
    "reactivation_sms": {"action": "Send SMS with limited-time exclusive offer", "channel": "sms", "timing": "next_3_days", "expected_conversion": 10.5},
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _overall_sentiment(customer_id):
    """Calculate overall sentiment score from interactions."""
    interactions = INTERACTION_HISTORY.get(customer_id, [])
    if not interactions:
        return "neutral", 0.0
    scores = {"positive": 1, "neutral": 0, "negative": -1}
    total = sum(scores.get(i["sentiment"], 0) for i in interactions)
    avg = total / len(interactions)
    if avg > 0.3:
        return "positive", round(avg, 2)
    elif avg < -0.3:
        return "negative", round(avg, 2)
    return "neutral", round(avg, 2)


def _recommend_action(profile, sentiment_label):
    """Determine best next action based on segment and sentiment."""
    if sentiment_label == "negative" and profile["segment"] == "at_risk":
        return "service_recovery"
    if profile["segment"] == "premium":
        return "premium_engagement"
    if profile["segment"] == "at_risk":
        return "win_back"
    return "cross_sell"


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class Customer360SpeechAgent(BasicAgent):
    """Customer 360 and speech analytics agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/customer-360-speech"
        self.metadata = {
            "name": self.name,
            "display_name": "Customer 360 & Speech Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "customer_profile",
                            "interaction_history",
                            "sentiment_analysis",
                            "next_best_action",
                        ],
                    },
                    "customer_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "customer_profile")
        dispatch = {
            "customer_profile": self._customer_profile,
            "interaction_history": self._interaction_history,
            "sentiment_analysis": self._sentiment_analysis,
            "next_best_action": self._next_best_action,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _customer_profile(self, **kwargs) -> str:
        customer_id = kwargs.get("customer_id")
        if customer_id and customer_id in CUSTOMER_PROFILES:
            p = CUSTOMER_PROFILES[customer_id]
            ph = p["purchase_history_summary"]
            sentiment, score = _overall_sentiment(customer_id)
            lines = [f"# Customer Profile: {p['name']} ({customer_id})\n"]
            lines.append(f"- **Email:** {p['email']}")
            lines.append(f"- **Phone:** {p['phone']}")
            lines.append(f"- **Segment:** {p['segment'].replace('_', ' ').title()}")
            lines.append(f"- **Lifetime Value:** ${p['lifetime_value']:,.0f}")
            lines.append(f"- **Member Since:** {p['member_since']}")
            lines.append(f"- **Preferred Channel:** {p['preferred_channel'].replace('_', ' ').title()}")
            lines.append(f"- **Overall Sentiment:** {sentiment.title()} ({score})\n")
            lines.append("## Purchase Summary\n")
            lines.append(f"- Total Orders: {ph['total_orders']}")
            lines.append(f"- Avg Order Value: ${ph['avg_order_value']:,.2f}")
            lines.append(f"- Last Order: {ph['last_order']}")
            lines.append(f"- Return Rate: {ph['return_rate']}%\n")
            lines.append("## Preferences\n")
            lines.append(f"- Categories: {', '.join(p['preferences']['categories'])}")
            lines.append(f"- Communication: {p['preferences']['communication'].upper()}")
            return "\n".join(lines)

        lines = ["# Customer 360 Overview\n"]
        lines.append("| ID | Name | Segment | LTV | Orders | Last Order | Sentiment |")
        lines.append("|---|---|---|---|---|---|---|")
        for cid, p in CUSTOMER_PROFILES.items():
            sentiment, _ = _overall_sentiment(cid)
            ph = p["purchase_history_summary"]
            lines.append(
                f"| {cid} | {p['name']} | {p['segment'].replace('_', ' ').title()} "
                f"| ${p['lifetime_value']:,.0f} | {ph['total_orders']} | {ph['last_order']} | {sentiment.title()} |"
            )
        total_ltv = sum(p["lifetime_value"] for p in CUSTOMER_PROFILES.values())
        lines.append(f"\n**Total Customer LTV:** ${total_ltv:,.0f}")
        return "\n".join(lines)

    def _interaction_history(self, **kwargs) -> str:
        customer_id = kwargs.get("customer_id", "C360-001")
        profile = CUSTOMER_PROFILES.get(customer_id, list(CUSTOMER_PROFILES.values())[0])
        interactions = INTERACTION_HISTORY.get(customer_id, [])
        lines = [f"# Interaction History: {profile['name']}\n"]
        if interactions:
            lines.append("| Date | Channel | Type | Details | Sentiment | Agent |")
            lines.append("|---|---|---|---|---|---|")
            for i in interactions:
                agent = i["agent"] or "Self-Service"
                lines.append(
                    f"| {i['date']} | {i['channel'].replace('_', ' ').title()} | {i['type'].replace('_', ' ').title()} "
                    f"| {i['details']} | {i['sentiment'].title()} | {agent} |"
                )
        else:
            lines.append("No interaction history available.")
        lines.append(f"\n**Total Interactions:** {len(interactions)}")
        return "\n".join(lines)

    def _sentiment_analysis(self, **kwargs) -> str:
        lines = ["# Sentiment Analysis Report\n"]
        lines.append("| Customer | Segment | Sentiment | Score | Interactions | Negative Count |")
        lines.append("|---|---|---|---|---|---|")
        for cid, p in CUSTOMER_PROFILES.items():
            sentiment, score = _overall_sentiment(cid)
            interactions = INTERACTION_HISTORY.get(cid, [])
            neg_count = sum(1 for i in interactions if i["sentiment"] == "negative")
            lines.append(
                f"| {p['name']} ({cid}) | {p['segment'].replace('_', ' ').title()} "
                f"| {sentiment.title()} | {score} | {len(interactions)} | {neg_count} |"
            )
        lines.append("\n## At-Risk Customers (Negative Sentiment)\n")
        for cid, p in CUSTOMER_PROFILES.items():
            sentiment, score = _overall_sentiment(cid)
            if sentiment == "negative":
                interactions = INTERACTION_HISTORY.get(cid, [])
                neg_interactions = [i for i in interactions if i["sentiment"] == "negative"]
                lines.append(f"### {p['name']} ({cid})\n")
                for i in neg_interactions:
                    lines.append(f"- [{i['date']}] {i['channel']}: {i['details']}")
                lines.append("")
        return "\n".join(lines)

    def _next_best_action(self, **kwargs) -> str:
        lines = ["# Next Best Action Recommendations\n"]
        for cid, p in CUSTOMER_PROFILES.items():
            sentiment, score = _overall_sentiment(cid)
            action_key = _recommend_action(p, sentiment)
            action = NEXT_BEST_ACTIONS[action_key]
            lines.append(f"## {p['name']} ({cid})\n")
            lines.append(f"- **Segment:** {p['segment'].replace('_', ' ').title()}")
            lines.append(f"- **Sentiment:** {sentiment.title()} ({score})")
            lines.append(f"- **Recommended Action:** {action['action']}")
            lines.append(f"- **Channel:** {action['channel'].replace('_', ' ').title()}")
            lines.append(f"- **Timing:** {action['timing'].replace('_', ' ').title()}")
            lines.append(f"- **Expected Conversion:** {action['expected_conversion']}%\n")
        lines.append("## Action Library\n")
        lines.append("| Action | Channel | Timing | Conversion |")
        lines.append("|---|---|---|---|")
        for aid, a in NEXT_BEST_ACTIONS.items():
            lines.append(f"| {a['action']} | {a['channel'].replace('_', ' ').title()} | {a['timing'].replace('_', ' ').title()} | {a['expected_conversion']}% |")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = Customer360SpeechAgent()
    print(agent.perform(operation="customer_profile"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="customer_profile", customer_id="C360-001"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="interaction_history", customer_id="C360-003"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="sentiment_analysis"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="next_best_action"))
