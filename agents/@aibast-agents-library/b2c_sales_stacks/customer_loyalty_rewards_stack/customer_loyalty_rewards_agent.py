"""
Customer Loyalty & Rewards Agent — B2C Sales Stack

Manages loyalty program dashboards, points summaries, reward
recommendations, and tier analysis for customer retention.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/customer-loyalty-rewards",
    "version": "1.0.0",
    "display_name": "Customer Loyalty and Rewards Agent",
    "description": "Provide synthetic loyalty insights, points summaries, reward-option drafts, and tier analysis without issuing or redeeming benefits.",
    "author": "AIBAST",
    "tags": ["loyalty", "rewards", "points", "retention", "tier", "b2c"],
    "category": "b2c_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

LOYALTY_MEMBERS = {
    "LM-10001": {
        "name": "Synthetic Platinum Member",
        "tier": "platinum",
        "points_balance": 48250,
        "points_earned_ytd": 12400,
        "points_redeemed_ytd": 8000,
        "member_since": "2018-03-15",
        "total_spend_ytd": 6200,
        "engagement_score": 92,
        "preferred_rewards": ["travel", "dining"],
    },
    "LM-10002": {
        "name": "Synthetic Gold Member",
        "tier": "gold",
        "points_balance": 22100,
        "points_earned_ytd": 6800,
        "points_redeemed_ytd": 2500,
        "member_since": "2020-08-22",
        "total_spend_ytd": 3400,
        "engagement_score": 75,
        "preferred_rewards": ["merchandise", "gift_cards"],
    },
    "LM-10003": {
        "name": "Synthetic Silver Member",
        "tier": "silver",
        "points_balance": 8450,
        "points_earned_ytd": 3200,
        "points_redeemed_ytd": 0,
        "member_since": "2023-01-10",
        "total_spend_ytd": 1600,
        "engagement_score": 58,
        "preferred_rewards": ["discounts"],
    },
    "LM-10004": {
        "name": "Synthetic Bronze Member",
        "tier": "bronze",
        "points_balance": 2100,
        "points_earned_ytd": 900,
        "points_redeemed_ytd": 0,
        "member_since": "2024-06-05",
        "total_spend_ytd": 450,
        "engagement_score": 32,
        "preferred_rewards": ["discounts", "free_shipping"],
    },
}

TIER_STRUCTURE = {
    "bronze": {"min_spend": 0, "points_multiplier": 1.0, "perks": ["Birthday bonus points", "Member-only sales access"], "next_tier": "silver", "spend_to_next": 1000},
    "silver": {"min_spend": 1000, "points_multiplier": 1.25, "perks": ["Bronze perks", "Free standard shipping", "Early access to new products"], "next_tier": "gold", "spend_to_next": 3000},
    "gold": {"min_spend": 3000, "points_multiplier": 1.5, "perks": ["Silver perks", "Free express shipping", "Exclusive gold events", "Annual gift"], "next_tier": "platinum", "spend_to_next": 6000},
    "platinum": {"min_spend": 6000, "points_multiplier": 2.0, "perks": ["Gold perks", "Personal shopping advisor", "Free returns", "VIP lounge access", "Quarterly bonus"], "next_tier": None, "spend_to_next": 0},
}

REDEMPTION_CATALOG = {
    "travel_voucher_500": {"name": "$500 Travel Voucher", "points_cost": 25000, "category": "travel", "value": 500},
    "dining_card_100": {"name": "$100 Dining Gift Card", "points_cost": 5000, "category": "dining", "value": 100},
    "merch_headphones": {"name": "Premium Wireless Headphones", "points_cost": 15000, "category": "merchandise", "value": 249},
    "gift_card_50": {"name": "$50 Store Gift Card", "points_cost": 2500, "category": "gift_cards", "value": 50},
    "discount_20pct": {"name": "20% Off Next Purchase", "points_cost": 3000, "category": "discounts", "value": 0},
    "free_shipping_3mo": {"name": "Free Shipping for 3 Months", "points_cost": 1500, "category": "free_shipping", "value": 30},
}

ENGAGEMENT_ACTIVITIES = [
    {"activity": "Purchase", "points": "2 per $1 spent", "frequency": "per_transaction"},
    {"activity": "Product Review", "points": "100 bonus", "frequency": "per_review"},
    {"activity": "Referral Signup", "points": "500 bonus", "frequency": "per_referral"},
    {"activity": "Birthday", "points": "Double points for birthday month", "frequency": "annual"},
    {"activity": "Social Share", "points": "50 bonus", "frequency": "per_share"},
    {"activity": "App Download", "points": "250 one-time bonus", "frequency": "once"},
]

APPROVED_PERSONAS = {
    "Loyalty Program Director": "program health, liability, governance, and structural options",
    "CRM Manager": "aggregate engagement patterns and consented preference quality",
    "Marketing Leader": "review-ready campaign concepts and qualitative value",
}

SAFETY_NOTICE = (
    "> Synthetic loyalty planning data. Informational options only; no member is "
    "contacted or enrolled, and no points, tier, offer, reward, redemption, refund, "
    "order, or purchase is issued or changed."
)


def _response_header(persona):
    role = persona if persona in APPROVED_PERSONAS else "Loyalty Program Director"
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

def _points_value(points):
    """Convert points to dollar value (1 point = $0.02)."""
    return round(points * 0.02, 2)


def _tier_progress(member):
    """Calculate progress toward next tier."""
    tier_info = TIER_STRUCTURE.get(member["tier"], {})
    if tier_info["next_tier"] is None:
        return 100.0
    spend_needed = tier_info["spend_to_next"]
    if spend_needed == 0:
        return 100.0
    current_spend = member["total_spend_ytd"]
    return min(100.0, round((current_spend / spend_needed) * 100, 1))


def _recommended_rewards(member):
    """Recommend rewards based on preferences and points balance."""
    recs = []
    for rid, reward in REDEMPTION_CATALOG.items():
        if reward["category"] in member["preferred_rewards"] and reward["points_cost"] <= member["points_balance"]:
            recs.append((rid, reward))
    return recs


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class CustomerLoyaltyRewardsAgent(BasicAgent):
    """Customer loyalty and rewards management agent."""

    def __init__(self):
        self.name = "CustomerLoyaltyRewardsAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Customer Loyalty & Rewards Agent",
            "description": (
                f"{__manifest__['description']} Route program-health questions to "
                "`loyalty_dashboard`; member balance, ledger, earned, or redeemed "
                "points questions to `points_summary`; reward-option questions to "
                "`reward_recommendations`; and tier structure or progress questions "
                "to `tier_analysis`."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Required routing key. Use points_summary for any member "
                            "balance or ledger explanation, including a Gold member; "
                            "do not substitute loyalty_dashboard."
                        ),
                        "enum": [
                            "loyalty_dashboard",
                            "points_summary",
                            "reward_recommendations",
                            "tier_analysis",
                        ],
                    },
                    "member_id": {
                        "type": "string",
                        "description": (
                            "Synthetic member ID when the prompt identifies a member. "
                            "Synthetic Gold Member is LM-10002."
                        ),
                    },
                    "persona": {
                        "type": "string",
                        "enum": list(APPROVED_PERSONAS),
                        "description": "Copy the role stated in the request.",
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
        member_id = kwargs.get("member_id")
        if member_id and member_id not in LOYALTY_MEMBERS:
            return (
                f"Unknown member_id `{member_id}`. Valid synthetic IDs: "
                f"{', '.join(LOYALTY_MEMBERS)}"
            )
        operation = kwargs.get("operation", "loyalty_dashboard")
        dispatch = {
            "loyalty_dashboard": self._loyalty_dashboard,
            "points_summary": self._points_summary,
            "reward_recommendations": self._reward_recommendations,
            "tier_analysis": self._tier_analysis,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _loyalty_dashboard(self, **kwargs) -> str:
        total_members = len(LOYALTY_MEMBERS)
        total_points = sum(m["points_balance"] for m in LOYALTY_MEMBERS.values())
        total_spend = sum(m["total_spend_ytd"] for m in LOYALTY_MEMBERS.values())
        lines = _response_header(kwargs.get("persona")) + ["# Synthetic Loyalty Program Dashboard\n"]
        lines.append(f"**Total Members:** {total_members}")
        lines.append(f"**Total Points Outstanding:** {total_points:,} (${_points_value(total_points):,.2f})")
        lines.append(f"**Total Member Spend YTD:** ${total_spend:,.0f}\n")
        lines.append("| Member | Tier | Points | Spend YTD | Engagement | Since |")
        lines.append("|---|---|---|---|---|---|")
        for mid, m in LOYALTY_MEMBERS.items():
            lines.append(
                f"| {m['name']} ({mid}) | {m['tier'].title()} | {m['points_balance']:,} "
                f"| ${m['total_spend_ytd']:,.0f} | {m['engagement_score']} | {m['member_since']} |"
            )
        lines.append("\n## Tier Distribution\n")
        tier_counts = {}
        for m in LOYALTY_MEMBERS.values():
            tier_counts[m["tier"]] = tier_counts.get(m["tier"], 0) + 1
        for tier in ["platinum", "gold", "silver", "bronze"]:
            lines.append(f"- {tier.title()}: {tier_counts.get(tier, 0)}")
        return "\n".join(lines)

    def _points_summary(self, **kwargs) -> str:
        member_id = kwargs.get("member_id")
        if member_id and member_id in LOYALTY_MEMBERS:
            m = LOYALTY_MEMBERS[member_id]
            lines = _response_header(kwargs.get("persona")) + [f"# Synthetic Points Summary: {m['name']}\n"]
            lines.append(f"- **Tier:** {m['tier'].title()}")
            lines.append(f"- **Points Balance:** {m['points_balance']:,} (${_points_value(m['points_balance']):,.2f})")
            lines.append(f"- **Earned YTD:** {m['points_earned_ytd']:,}")
            lines.append(f"- **Redeemed YTD:** {m['points_redeemed_ytd']:,}")
            lines.append(f"- **Multiplier:** {TIER_STRUCTURE[m['tier']]['points_multiplier']}x\n")
            lines.append("## Earning Opportunities\n")
            for act in ENGAGEMENT_ACTIVITIES:
                lines.append(f"- **{act['activity']}:** {act['points']}")
            return "\n".join(lines)

        lines = _response_header(kwargs.get("persona")) + ["# Synthetic Points Summary — All Members\n"]
        lines.append("| Member | Tier | Balance | Earned YTD | Redeemed YTD | Value |")
        lines.append("|---|---|---|---|---|---|")
        for mid, m in LOYALTY_MEMBERS.items():
            lines.append(
                f"| {m['name']} ({mid}) | {m['tier'].title()} | {m['points_balance']:,} "
                f"| {m['points_earned_ytd']:,} | {m['points_redeemed_ytd']:,} | ${_points_value(m['points_balance']):,.2f} |"
            )
        return "\n".join(lines)

    def _reward_recommendations(self, **kwargs) -> str:
        lines = _response_header(kwargs.get("persona")) + ["# Draft Reward Option Recommendations\n"]
        member_id = kwargs.get("member_id")
        members = {member_id: LOYALTY_MEMBERS[member_id]} if member_id else LOYALTY_MEMBERS
        for mid, m in members.items():
            recs = _recommended_rewards(m)
            lines.append(f"## {m['name']} ({mid}) — {m['points_balance']:,} points\n")
            if recs:
                lines.append("| Reward | Points Cost | Category | Value |")
                lines.append("|---|---|---|---|")
                for rid, reward in recs:
                    val = f"${reward['value']}" if reward["value"] else "Discount"
                    lines.append(f"| {reward['name']} | {reward['points_cost']:,} | {reward['category'].replace('_', ' ').title()} | {val} |")
            else:
                lines.append("No matching informational reward options at the current synthetic balance.")
            lines.append("")
        lines.append("## Full Redemption Catalog\n")
        lines.append("| Reward | Points | Category | Value |")
        lines.append("|---|---|---|---|")
        for rid, r in REDEMPTION_CATALOG.items():
            val = f"${r['value']}" if r["value"] else "Discount"
            lines.append(f"| {r['name']} | {r['points_cost']:,} | {r['category'].replace('_', ' ').title()} | {val} |")
        return "\n".join(lines)

    def _tier_analysis(self, **kwargs) -> str:
        lines = _response_header(kwargs.get("persona")) + ["# Synthetic Tier Analysis\n"]
        lines.append("## Tier Structure\n")
        lines.append("| Tier | Min Spend | Multiplier | Key Perks |")
        lines.append("|---|---|---|---|")
        for tier, info in TIER_STRUCTURE.items():
            perks = "; ".join(info["perks"][:2])
            lines.append(f"| {tier.title()} | ${info['min_spend']:,.0f} | {info['points_multiplier']}x | {perks} |")
        lines.append("\n## Member Tier Progress\n")
        for mid, m in LOYALTY_MEMBERS.items():
            progress = _tier_progress(m)
            tier_info = TIER_STRUCTURE[m["tier"]]
            lines.append(f"### {m['name']} ({mid}) — {m['tier'].title()}\n")
            lines.append(f"- Spend YTD: ${m['total_spend_ytd']:,.0f}")
            lines.append(f"- Engagement Score: {m['engagement_score']}")
            if tier_info["next_tier"]:
                remaining = max(0, tier_info["spend_to_next"] - m["total_spend_ytd"])
                lines.append(f"- Progress to {tier_info['next_tier'].title()}: {progress}%")
                lines.append(f"- Spend Remaining: ${remaining:,.0f}")
            else:
                lines.append(f"- Status: Top Tier Achieved")
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = CustomerLoyaltyRewardsAgent()
    print(agent.perform(operation="loyalty_dashboard"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="points_summary", member_id="LM-10001"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="reward_recommendations"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="tier_analysis"))
