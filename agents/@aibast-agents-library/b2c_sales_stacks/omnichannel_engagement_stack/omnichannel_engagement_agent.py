"""
Omnichannel Engagement Agent — B2C Sales Stack

Analyzes channel performance, maps customer journeys, optimizes
engagement strategies, and provides campaign attribution insights.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/omnichannel-engagement",
    "version": "1.0.0",
    "display_name": "Omnichannel Engagement Agent",
    "description": "Unify one customer's interactions across channels so service and sales teams pick up where the customer left off: journey, unresolved questions, best channel and timing, proactive engagement drafts, and handoff context; plus aggregate channel analytics.",
    "author": "AIBAST",
    "tags": ["omnichannel", "engagement", "journey", "attribution", "campaign", "b2c"],
    "category": "b2c_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

CHANNELS = {
    "email": {"sessions_30d": 145000, "conversions_30d": 4350, "revenue_30d": 870000, "cost_30d": 12500, "avg_order_value": 200.0, "bounce_rate": 18.5},
    "sms": {"sessions_30d": 62000, "conversions_30d": 1860, "revenue_30d": 325500, "cost_30d": 8200, "avg_order_value": 175.0, "bounce_rate": 5.2},
    "social_media": {"sessions_30d": 230000, "conversions_30d": 2760, "revenue_30d": 552000, "cost_30d": 45000, "avg_order_value": 200.0, "bounce_rate": 42.0},
    "web_organic": {"sessions_30d": 480000, "conversions_30d": 9600, "revenue_30d": 1920000, "cost_30d": 18000, "avg_order_value": 200.0, "bounce_rate": 35.0},
    "web_paid": {"sessions_30d": 185000, "conversions_30d": 5550, "revenue_30d": 1110000, "cost_30d": 95000, "avg_order_value": 200.0, "bounce_rate": 28.0},
    "mobile_app": {"sessions_30d": 310000, "conversions_30d": 12400, "revenue_30d": 2480000, "cost_30d": 22000, "avg_order_value": 200.0, "bounce_rate": 12.0},
    "in_store": {"sessions_30d": 95000, "conversions_30d": 28500, "revenue_30d": 5700000, "cost_30d": 180000, "avg_order_value": 200.0, "bounce_rate": 0},
}

CUSTOMER_JOURNEYS = {
    "journey_discovery": {
        "name": "Discovery to Purchase",
        "touchpoints": ["social_media_ad", "website_browse", "email_signup", "email_promo", "website_purchase"],
        "avg_days": 14,
        "conversion_rate": 3.2,
        "avg_touchpoints": 5,
    },
    "journey_repeat": {
        "name": "Repeat Purchase",
        "touchpoints": ["email_promo", "mobile_app_browse", "mobile_app_purchase"],
        "avg_days": 3,
        "conversion_rate": 18.5,
        "avg_touchpoints": 3,
    },
    "journey_winback": {
        "name": "Win-Back",
        "touchpoints": ["email_winback", "sms_offer", "website_browse", "website_purchase"],
        "avg_days": 21,
        "conversion_rate": 8.4,
        "avg_touchpoints": 4,
    },
    "journey_impulse": {
        "name": "Impulse Purchase",
        "touchpoints": ["social_media_ad", "website_purchase"],
        "avg_days": 0,
        "conversion_rate": 1.8,
        "avg_touchpoints": 2,
    },
}

CAMPAIGN_RESULTS = {
    "CAMP-301": {"name": "Spring Collection Launch", "channel": "email", "sent": 250000, "opens": 62500, "clicks": 18750, "conversions": 2250, "revenue": 450000, "cost": 5000},
    "CAMP-302": {"name": "Flash Sale — 48 Hours", "channel": "sms", "sent": 120000, "opens": 115200, "clicks": 24000, "conversions": 3600, "revenue": 540000, "cost": 6000},
    "CAMP-303": {"name": "Influencer Partnership", "channel": "social_media", "sent": 0, "opens": 0, "clicks": 85000, "conversions": 1700, "revenue": 340000, "cost": 35000},
    "CAMP-304": {"name": "Google Shopping Ads", "channel": "web_paid", "sent": 0, "opens": 0, "clicks": 45000, "conversions": 2700, "revenue": 540000, "cost": 42000},
    "CAMP-305": {"name": "App Push — Loyalty Members", "channel": "mobile_app", "sent": 85000, "opens": 42500, "clicks": 17000, "conversions": 5100, "revenue": 765000, "cost": 2000},
}


# One consented customer service/CRM record (synthetic) for the cross-channel demo.
CUSTOMERS = {
    "CUST-SM-001": {
        "name": "Sarah Mitchell",
        "tier": "Gold",
        "lifetime_value": 2400,
        "cart": {"item": "Alpine Parka", "value": 289, "age_days": 3},
        "timeline": [
            {"day": "3 days ago", "channel": "Mobile app", "action": "Checkout started", "issue": "Payment declined"},
            {"day": "2 days ago", "channel": "Chat", "action": "Sizing question", "issue": "Disconnected"},
            {"day": "Yesterday", "channel": "Email", "action": "Cart reminder", "issue": "No action"},
            {"day": "Today", "channel": "Phone", "action": "Support call", "issue": "Currently holding"},
        ],
        "channel_counts_30d": [
            {"channel": "Mobile app", "interactions": 12, "note": "primary"},
            {"channel": "Website", "interactions": 8, "note": "secondary"},
            {"channel": "Chat", "interactions": 3, "note": "frustrated"},
        ],
        "chat_questions": [
            {"question": "Does Alpine Parka run true to size?", "outcome": "Agent: \"Let me check...\" (disconnected)"},
            {"question": "Do you have it in navy?", "outcome": "Never answered"},
        ],
        "issues": [
            {"issue": "Sizing guidance", "status": "Unanswered", "impact": "Blocking purchase"},
            {"issue": "Color availability", "status": "Unanswered", "impact": "Blocking purchase"},
            {"issue": "Payment", "status": "Card declined", "impact": "Needs resolution"},
        ],
        "minutes_trying": 18,
        "channel_engagement": [
            {"channel": "Mobile push", "engagement": "82% open", "best_for": "Urgent updates"},
            {"channel": "SMS", "engagement": "76% response", "best_for": "Order status"},
            {"channel": "Email", "engagement": "34% open", "best_for": "Avoid urgency"},
            {"channel": "Chat", "engagement": "Frustrated", "best_for": "Avoid short-term"},
        ],
        "peak_engagement": "7-9 PM",
        "signals": "Responds to urgency, values fit guidance",
    },
}

PRODUCT_FACTS = {
    "Alpine Parka": {"fit": "runs one size small", "colors": "Navy in stock, S-XL"},
}

PROACTIVE_PLAN = {
    "after_purchase": [
        "Order complete: Size guide via SMS",
        "Delivery day: Styling tips via mobile push (82% engagement)",
        "7 days post: Review request in-app",
    ],
    "upcoming": [
        "3 days: Winter accessories bundle offer",
        "6 weeks: Birthday loyalty bonus",
        "8 weeks: Spring preview early access",
    ],
    "win_back": [
        "Hour 1: SMS \"Your coat is waiting\"",
        "Hour 4: Mobile push \"Low stock\"",
        "Day 2: SMS 10% off code",
        "Day 5: Personal stylist call",
    ],
    "avoid": "Email campaigns (34% open), chat offers (negative history), generic messaging",
}

HANDOFF_CONTEXT = {
    "transfer": [
        "Payments: Card decline history, alternatives",
        "Styling: Size preferences, past purchases",
        "Store pickup: Location, inventory",
        "Loyalty: Points, tier benefits",
    ],
    "script": "I'm connecting you with [Name]. I've shared your complete history - no need to repeat anything.",
    "attachments": "CRM note, cart link, conversation summary",
}

APPROVED_PERSONAS = {
    "Customer Experience Leader": "cross-channel continuity, service quality, and governance",
    "Digital Engagement Manager": "channel strategy, consent, and measurement",
    "Contact Center Supervisor": "handoff friction, unresolved needs, and service consistency",
}

SAFETY_NOTICE = (
    "> Synthetic records. Recommendations only; uses only the consented service record "
    "already linked to the customer; no identity stitching, sensitive profiling, outreach, "
    "message, offer, reward, transfer, or purchase action occurs."
)


def _response_header(persona):
    role = persona if persona in APPROVED_PERSONAS else "Customer Experience Leader"
    return [
        f"**Prepared for:** {role}",
        f"**Role focus:** {APPROVED_PERSONAS[role]}",
        "",
        SAFETY_NOTICE,
        "",
    ]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _resolve_customer(query):
    """Customer ID or (part of) the name; default CUST-SM-001; None when nothing matches."""
    if not query:
        return "CUST-SM-001"
    q = str(query).lower().strip()
    for key, cust in CUSTOMERS.items():
        if key.lower() in q or q in cust["name"].lower() or cust["name"].lower() in q:
            return key
    return None


def _channel_conversion_rate(channel):
    """Calculate conversion rate for a channel."""
    if channel["sessions_30d"] == 0:
        return 0
    return round((channel["conversions_30d"] / channel["sessions_30d"]) * 100, 2)


def _channel_roas(channel):
    """Calculate return on ad spend."""
    if channel["cost_30d"] == 0:
        return 0
    return round(channel["revenue_30d"] / channel["cost_30d"], 2)


def _campaign_roi(campaign):
    """Calculate campaign ROI."""
    if campaign["cost"] == 0:
        return 0
    return round(((campaign["revenue"] - campaign["cost"]) / campaign["cost"]) * 100, 1)


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

OPERATIONS = [
    "channel_performance",
    "journey_analysis",
    "engagement_optimization",
    "campaign_attribution",
    "customer_journey",
    "unresolved_issues",
    "channel_recommendation",
    "proactive_plan",
    "handoff_package",
]

CUSTOMER_OPERATIONS = [
    "customer_journey",
    "unresolved_issues",
    "channel_recommendation",
    "proactive_plan",
    "handoff_package",
]


class OmnichannelEngagementAgent(BasicAgent):
    """Omnichannel engagement agent: one customer's unified cross-channel view plus aggregate analytics."""

    def __init__(self):
        self.name = "OmnichannelEngagementAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Omnichannel Engagement Agent",
            "description": (
                __manifest__["description"] + " Always use this tool when someone asks about "
                "the customer's journey across channels, picking up where they left off, what "
                "she has been asking about, the best channel, proactive engagement, or a "
                "handoff. The demo customer is Sarah Mitchell (CUST-SM-001); call it without "
                "asking for a customer. Demo flow: journey across all channels -> "
                "customer_journey; what she's been asking / where we dropped the ball -> "
                "unresolved_issues; optimal channel strategy -> channel_recommendation; "
                "proactive engagement opportunities -> proactive_plan; prepare context for a "
                "handoff -> handoff_package. Aggregate marketing views: channel_performance, "
                "journey_analysis, engagement_optimization, campaign_attribution. Messages and "
                "handoffs are drafts; nothing is sent or transferred."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(OPERATIONS),
                        "description": (
                            "customer_journey: the customer's journey across all channels and "
                            "where to pick up. unresolved_issues: what she asked, unanswered "
                            "questions, where we dropped the ball, opening line. "
                            "channel_recommendation: optimal channel and timing for this "
                            "customer. proactive_plan: proactive engagement opportunities "
                            "after purchase and win-back. handoff_package: context to hand "
                            "off to another agent. channel_performance / journey_analysis / "
                            "engagement_optimization / campaign_attribution: aggregate "
                            "marketing analytics across all customers."
                        ),
                    },
                    "customer_id": {"type": "string", "description": "Customer ID or name (default CUST-SM-001, Sarah Mitchell)"},
                    "channel": {"type": "string"},
                    "campaign_id": {"type": "string"},
                    "persona": {
                        "type": "string",
                        "enum": list(APPROVED_PERSONAS),
                    },
                    "data_source": {"type": "string", "enum": ["synthetic"]},
                },
                "required": ["operation"],
                "additionalProperties": False,
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        if kwargs.get("data_source", "synthetic") != "synthetic":
            return "data_source must be `synthetic` for this package."
        channel = kwargs.get("channel")
        campaign_id = kwargs.get("campaign_id")
        if channel and channel not in CHANNELS:
            return f"Unknown channel `{channel}`. Valid: {', '.join(CHANNELS)}"
        if campaign_id and campaign_id not in CAMPAIGN_RESULTS:
            return (
                f"Unknown campaign_id `{campaign_id}`. Valid: "
                f"{', '.join(CAMPAIGN_RESULTS)}"
            )
        operation = kwargs.get("operation", "customer_journey")
        if operation in CUSTOMER_OPERATIONS:
            key = _resolve_customer(kwargs.get("customer_id"))
            if key is None:
                return (
                    f"Unknown customer_id `{kwargs.get('customer_id')}`. Valid: "
                    f"{', '.join(CUSTOMERS)} (Sarah Mitchell)"
                )
            kwargs["customer_key"] = key
        dispatch = {
            "customer_journey": self._customer_journey,
            "unresolved_issues": self._unresolved_issues,
            "channel_recommendation": self._channel_recommendation,
            "proactive_plan": self._proactive_plan,
            "handoff_package": self._handoff_package,
            "channel_performance": self._channel_performance,
            "journey_analysis": self._journey_analysis,
            "engagement_optimization": self._engagement_optimization,
            "campaign_attribution": self._campaign_attribution,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    # ── customer view (video turns 1-5) ────────────────────────
    def _customer_journey(self, **kwargs) -> str:
        c = CUSTOMERS[kwargs["customer_key"]]
        channels = []
        for row in c["timeline"]:
            if row["channel"] not in channels:
                channels.append(row["channel"])
        for row in c["channel_counts_30d"]:
            if row["channel"] not in channels:
                channels.append(row["channel"])
        lines = _response_header(kwargs.get("persona")) + [
            f"# Customer Journey: {c['name']}\n",
            f"{c['name']}'s journey across {len(channels)} channels unified. She's been trying "
            f"to buy for {c['cart']['age_days']} days.\n",
            "| Day | Channel | Action | Issue |",
            "|---|---|---|---|",
        ]
        for row in c["timeline"]:
            lines.append(f"| {row['day']} | {row['channel']} | {row['action']} | {row['issue']} |")
        lines.append("\n**Channel Preferences (30 Days):**")
        for row in c["channel_counts_30d"]:
            lines.append(f"- {row['channel']}: {row['interactions']} interactions ({row['note']})")
        lines.append(
            f"\n**Current:** ${c['cart']['value']} cart ({c['cart']['item']}), "
            f"{c['cart']['age_days']} days old. Issues: payment declined, sizing unanswered. "
            "Mood: likely frustrated (declined payment, chat disconnect)."
        )
        lines.append("\nSource: [All Channels + CDP]\n")
        lines.append("See full conversation context?")
        return "\n".join(lines)

    def _unresolved_issues(self, **kwargs) -> str:
        c = CUSTOMERS[kwargs["customer_key"]]
        facts = PRODUCT_FACTS[c["cart"]["item"]]
        unanswered = sum(1 for i in c["issues"] if i["status"] == "Unanswered")
        lines = _response_header(kwargs.get("persona")) + [
            f"# Unresolved Questions: {c['name']}\n",
            f"Context retrieved. {unanswered} unresolved questions from the chat disconnect.\n",
            "**Chat Session (2 Days Ago):**",
        ]
        for q in c["chat_questions"]:
            lines.append(f"- Q \"{q['question']}\" -> {q['outcome']}")
        lines += ["", "| Issue | Status | Impact |", "|---|---|---|"]
        for i in c["issues"]:
            lines.append(f"| {i['issue']} | {i['status']} | {i['impact']} |")
        lines.append(
            f"\n**Context:** She's spent {c['minutes_trying']} minutes trying to buy. Likely "
            "frustrated about the chat disconnect."
        )
        lines.append(
            f"\n**Draft opening:** \"Hi {c['name'].split()[0]}, I see you've been trying to order "
            f"the {c['cart']['item']}. I apologize for the disconnect - let me answer your "
            "questions and complete this order.\""
        )
        lines.append(f"\n**Ready answers:** {c['cart']['item']} {facts['fit']}. {facts['colors']}.")
        lines.append("\nSource: [Chat Logs + Inventory]\n")
        lines.append("Get optimal channel strategy?")
        return "\n".join(lines)

    def _channel_recommendation(self, **kwargs) -> str:
        c = CUSTOMERS[kwargs["customer_key"]]
        lines = _response_header(kwargs.get("persona")) + [
            f"# Channel Strategy: {c['name']}\n",
            "Channel analysis: she prefers mobile/SMS, not email.\n",
            "| Channel | Engagement | Best For |",
            "|---|---|---|",
        ]
        for row in c["channel_engagement"]:
            lines.append(f"| {row['channel']} | {row['engagement']} | {row['best_for']} |")
        lines += [
            "\n**For This Issue:** Phone (resolve now) -> SMS confirmation. Avoid email.",
            "\n**Future Strategy:**",
            "- Order updates: SMS (real-time)",
            "- Promotions: Mobile push at 10 AM",
            "- Service: Phone callback (avoid chat)",
            f"\n**Signals:** {c['signals']}, peak engagement {c['peak_engagement']}.",
            "\nSource: [Engagement Analytics]\n",
            "Show proactive engagement opportunities?",
        ]
        return "\n".join(lines)

    def _proactive_plan(self, **kwargs) -> str:
        c = CUSTOMERS[kwargs["customer_key"]]
        p = PROACTIVE_PLAN
        lines = _response_header(kwargs.get("persona")) + [
            f"# Proactive Engagement Plan (Draft): {c['name']}\n",
            "Proactive engagement opportunities identified; every message is a draft for approval.\n",
            "**Immediate (After Purchase):**",
        ]
        lines += [f"- {x}" for x in p["after_purchase"]]
        lines.append("\n**Upcoming:**")
        lines += [f"- {x}" for x in p["upcoming"]]
        lines.append("\n**Win-Back (If She Doesn't Convert):**")
        lines += [f"- {x}" for x in p["win_back"]]
        lines.append(f"\n**Avoid:** {p['avoid']}.")
        lines.append("\nSource: [Behavioral Analytics]\n")
        lines.append("Prepare a seamless handoff?")
        return "\n".join(lines)

    def _handoff_package(self, **kwargs) -> str:
        c = CUSTOMERS[kwargs["customer_key"]]
        h = HANDOFF_CONTEXT
        lines = _response_header(kwargs.get("persona")) + [
            f"# Handoff Package: {c['name']}\n",
            "Handoff package prepared with full context (ready for you to transfer).\n",
            "**Quick Context (Any Agent):**",
            f"- {c['name']} ({c['tier']}, ${c['lifetime_value']:,} LTV)",
            f"- Trying to buy {c['cart']['item']} x {c['cart']['age_days']} days",
            "- Blockers: Sizing (resolved), payment (in progress)",
            "- Mood: Previously frustrated, now engaged",
            "\n**Transfer Context Ready:**",
        ]
        lines += [f"- {x}" for x in h["transfer"]]
        lines.append(f"\n**Script:** \"{h['script']}\"")
        lines.append(f"\n**Attach on transfer:** {h['attachments']}.")
        lines.append("\nSource: [Context Store + Routing]\n")
        lines.append("See session impact?")
        return "\n".join(lines)

    def _channel_performance(self, **kwargs) -> str:
        channel = kwargs.get("channel")
        channels = {channel: CHANNELS[channel]} if channel else CHANNELS
        total_revenue = sum(c["revenue_30d"] for c in channels.values())
        total_conversions = sum(c["conversions_30d"] for c in channels.values())
        lines = _response_header(kwargs.get("persona")) + ["# Synthetic Channel Performance (30-Day)\n"]
        lines.append(f"**Total Revenue:** ${total_revenue:,.0f}")
        lines.append(f"**Total Conversions:** {total_conversions:,}\n")
        lines.append("| Channel | Sessions | Conversions | CVR | Revenue | Cost | ROAS |")
        lines.append("|---|---|---|---|---|---|---|")
        for ch_name, ch in channels.items():
            cvr = _channel_conversion_rate(ch)
            roas = _channel_roas(ch)
            lines.append(
                f"| {ch_name.replace('_', ' ').title()} | {ch['sessions_30d']:,} | {ch['conversions_30d']:,} "
                f"| {cvr}% | ${ch['revenue_30d']:,.0f} | ${ch['cost_30d']:,.0f} | {roas}x |"
            )
        lines.append("\n## Revenue Share by Channel\n")
        for ch_name, ch in channels.items():
            share = round((ch["revenue_30d"] / total_revenue) * 100, 1) if total_revenue else 0
            lines.append(f"- {ch_name.replace('_', ' ').title()}: {share}%")
        return "\n".join(lines)

    def _journey_analysis(self, **kwargs) -> str:
        lines = _response_header(kwargs.get("persona")) + ["# Aggregate Customer Journey Analysis\n"]
        for jid, j in CUSTOMER_JOURNEYS.items():
            lines.append(f"## {j['name']}\n")
            lines.append(f"- **Avg Duration:** {j['avg_days']} days")
            lines.append(f"- **Avg Touchpoints:** {j['avg_touchpoints']}")
            lines.append(f"- **Conversion Rate:** {j['conversion_rate']}%\n")
            lines.append("**Touchpoint Sequence:**\n")
            for i, tp in enumerate(j["touchpoints"], 1):
                arrow = " -> " if i < len(j["touchpoints"]) else ""
                lines.append(f"{i}. {tp.replace('_', ' ').title()}{arrow}")
            lines.append("")
        lines.append("## Journey Optimization Opportunities\n")
        lines.append("- **Discovery:** Shorten path by enabling social commerce checkout")
        lines.append("- **Repeat:** Leverage push notifications for faster re-engagement")
        lines.append("- **Win-Back:** Test a consented service reminder window in a controlled experiment")
        lines.append("- **Impulse:** Optimize social ad creative for direct conversion")
        return "\n".join(lines)

    def _engagement_optimization(self, **kwargs) -> str:
        lines = _response_header(kwargs.get("persona")) + ["# Draft Engagement Optimization Report\n"]
        lines.append("## Channel Efficiency Ranking\n")
        ranked = []
        for ch_name, ch in CHANNELS.items():
            roas = _channel_roas(ch)
            cvr = _channel_conversion_rate(ch)
            ranked.append((ch_name, roas, cvr, ch))
        ranked.sort(key=lambda x: x[1], reverse=True)
        lines.append("| Rank | Channel | ROAS | CVR | Bounce Rate | Recommendation |")
        lines.append("|---|---|---|---|---|---|")
        for i, (name, roas, cvr, ch) in enumerate(ranked, 1):
            if roas > 50:
                rec = "Scale investment"
            elif roas > 10:
                rec = "Optimize spend"
            else:
                rec = "Review ROI"
            lines.append(
                f"| {i} | {name.replace('_', ' ').title()} | {roas}x | {cvr}% "
                f"| {ch['bounce_rate']}% | {rec} |"
            )
        total_cost = sum(c["cost_30d"] for c in CHANNELS.values())
        total_rev = sum(c["revenue_30d"] for c in CHANNELS.values())
        lines.append(f"\n**Total Marketing Spend:** ${total_cost:,.0f}")
        lines.append(f"**Total Revenue:** ${total_rev:,.0f}")
        lines.append(f"**Blended ROAS:** {round(total_rev / total_cost, 1)}x")
        lines.append("\n## Optimization Actions\n")
        lines.append("1. Model a budget shift from social media to consented app engagement")
        lines.append("2. Ask only for optional preferences needed to improve service")
        lines.append("3. Design an A/B test for the web-paid checkout journey")
        lines.append("4. Review contact frequency caps across consented aggregate cohorts")
        return "\n".join(lines)

    def _campaign_attribution(self, **kwargs) -> str:
        lines = _response_header(kwargs.get("persona")) + ["# Synthetic Campaign Attribution Report\n"]
        lines.append("| Campaign | Channel | Conversions | Revenue | Cost | ROI |")
        lines.append("|---|---|---|---|---|---|")
        total_rev = 0
        total_cost = 0
        campaign_id = kwargs.get("campaign_id")
        campaigns = (
            {campaign_id: CAMPAIGN_RESULTS[campaign_id]}
            if campaign_id
            else CAMPAIGN_RESULTS
        )
        for cid, c in campaigns.items():
            roi = _campaign_roi(c)
            total_rev += c["revenue"]
            total_cost += c["cost"]
            lines.append(
                f"| {c['name']} ({cid}) | {c['channel'].replace('_', ' ').title()} "
                f"| {c['conversions']:,} | ${c['revenue']:,.0f} | ${c['cost']:,.0f} | {roi}% |"
            )
        lines.append(f"\n**Total Campaign Revenue:** ${total_rev:,.0f}")
        lines.append(f"**Total Campaign Cost:** ${total_cost:,.0f}")
        overall_roi = round(((total_rev - total_cost) / total_cost) * 100, 1) if total_cost else 0
        lines.append(f"**Overall Campaign ROI:** {overall_roi}%")
        lines.append("\n## Campaign Detail\n")
        for cid, c in campaigns.items():
            lines.append(f"### {c['name']} ({cid})\n")
            if c["sent"] > 0:
                open_rate = round((c["opens"] / c["sent"]) * 100, 1)
                ctr = round((c["clicks"] / c["sent"]) * 100, 1)
                lines.append(f"- Sent: {c['sent']:,} | Opens: {c['opens']:,} ({open_rate}%) | Clicks: {c['clicks']:,} ({ctr}%)")
            else:
                lines.append(f"- Clicks: {c['clicks']:,}")
            conv_rate = round((c["conversions"] / c["clicks"]) * 100, 1) if c["clicks"] else 0
            lines.append(f"- Conversions: {c['conversions']:,} ({conv_rate}% click-to-conversion)")
            lines.append(f"- Revenue: ${c['revenue']:,.0f} | Cost: ${c['cost']:,.0f}\n")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = OmnichannelEngagementAgent()
    for op in CUSTOMER_OPERATIONS:
        print(agent.perform(operation=op))
        print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="channel_performance"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="journey_analysis"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="engagement_optimization"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="campaign_attribution"))
