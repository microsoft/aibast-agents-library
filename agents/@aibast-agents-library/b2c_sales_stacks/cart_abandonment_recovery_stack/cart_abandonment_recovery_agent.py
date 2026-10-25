"""
Cart Abandonment Recovery Agent — B2C Sales Stack

Analyzes today's synthetic abandoned carts by segment, drafts personalized
recovery strategies and multi-touch campaign sequences, forecasts recovery
revenue, recommends optimizations, compares incentive scenarios, and tracks
aggregate conversion metrics. Everything is a draft for human approval.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/cart-abandonment-recovery",
    "version": "1.0.0",
    "display_name": "Cart Abandonment Recovery Agent",
    "description": "Draft privacy-safe abandoned-cart analysis, recovery concepts, incentive scenarios, and aggregate conversion reporting for human review.",
    "author": "AIBAST",
    "tags": ["cart-abandonment", "recovery", "ecommerce", "conversion", "email", "b2c"],
    "category": "b2c_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

# Today's abandoned carts in aggregate. value = abandoned cart value in dollars; recovery_pct = modeled
# 48-hour recovery likelihood for the segment.
TODAY_SEGMENTS = [
    {"segment": "VIP", "carts": 34, "value": 18400, "recovery_pct": 45},
    {"segment": "Repeat buyers", "carts": 89, "value": 24200, "recovery_pct": 38},
    {"segment": "New visitors", "carts": 412, "value": 52800, "recovery_pct": 22},
    {"segment": "Other shoppers", "carts": 312, "value": 31600, "recovery_pct": 28},
]

ABANDON_REASONS = [
    {"reason": "shipping cost", "pct": 42},
    {"reason": "comparison shopping", "pct": 28},
    {"reason": "payment friction", "pct": 18},
    {"reason": "other", "pct": 12},
]

# Top recovery opportunities. shopper_label is a fictional first name + initial.
ABANDONED_CARTS = {
    "CART-20001": {
        "shopper_label": "Sarah M",
        "contactable": True,
        "segment": "vip",
        "items": [
            {"name": "Designer Leather Tote", "sku": "BAG-4421", "price": 489.00, "qty": 1},
            {"name": "Leather Crossbody Bag", "sku": "BAG-1102", "price": 403.00, "qty": 1},
        ],
        "cart_value": 892.00,
        "abandoned_at": "2025-03-05T14:22:00",
        "page_exit": "shipping_options",
        "device": "mobile",
        "prior_purchases": 14,
        "recovery_status": "draft_stage_1_ready",
    },
    "CART-20002": {
        "shopper_label": "James K",
        "contactable": True,
        "segment": "repeat_buyer",
        "items": [
            {"name": "Weekender Duffel", "sku": "BAG-3305", "price": 399.00, "qty": 1},
            {"name": "Leather Wallet", "sku": "ACC-1140", "price": 248.00, "qty": 1},
        ],
        "cart_value": 647.00,
        "abandoned_at": "2025-03-05T09:15:00",
        "page_exit": "payment",
        "device": "desktop",
        "prior_purchases": 5,
        "recovery_status": "not_contacted",
    },
    "CART-20003": {
        "shopper_label": "Emily R",
        "contactable": True,
        "segment": "repeat_buyer",
        "items": [
            {"name": "Travel Backpack", "sku": "BAG-7720", "price": 289.00, "qty": 1},
            {"name": "Packing Cube Set", "sku": "ACC-5501", "price": 245.00, "qty": 1},
        ],
        "cart_value": 534.00,
        "abandoned_at": "2025-03-05T18:45:00",
        "page_exit": "shipping_options",
        "device": "desktop",
        "prior_purchases": 3,
        "recovery_status": "not_contacted",
    },
    "CART-20004": {
        "shopper_label": "Guest shopper",
        "contactable": False,
        "segment": "guest",
        "items": [
            {"name": "Canvas Tote", "sku": "BAG-2201", "price": 129.99, "qty": 1},
        ],
        "cart_value": 129.99,
        "abandoned_at": "2025-03-05T11:30:00",
        "page_exit": "cart_page",
        "device": "mobile",
        "prior_purchases": 0,
        "recovery_status": "unrecoverable",
    },
}

# Personalized recovery strategies (proposed, awaiting approval).
RECOVERY_STRATEGIES = [
    {"audience": "Sarah M. ($892 VIP)", "offer": "\"Your favorite bags are 40% off\" + double points", "channel": "Email + SMS"},
    {"audience": "High-Value (8,400)", "offer": "VIP early access + 3X points", "channel": "Email"},
    {"audience": "Point Expiry (12,000)", "offer": "\"Use before they expire\" + 25% bonus", "channel": "Email + push"},
    {"audience": "Lapsed Browsers (13,600)", "offer": "Items viewed + 20% off + free shipping", "channel": "Email + retargeting"},
]

CAMPAIGN_AUDIENCES = [
    {"campaign": "High-value win-back", "members": 8400},
    {"campaign": "Point expiry alert", "members": 12000},
    {"campaign": "Lapsed browser", "members": 13600},
]

MULTI_TOUCH_SEQUENCES = [
    {"segment": "VIP", "steps": ["Personal note", "SMS 1hr", "Express shipping 4hr", "Call 24hr ($500+)"]},
    {"segment": "Repeat", "steps": ["Points reminder", "Push 2hr", "Free shipping hint 12hr"]},
    {"segment": "New", "steps": ["Welcome 10% off", "Retargeting", "Social proof 24hr"]},
]

BENCHMARKS = {
    "industry_recovery_pct": 18,
    "target_recovery_pct": 27,
    "optimized_recovery_pct": 35,
    "monthly_recovered_current": 172000,
    "monthly_recovered_optimized": 228000,
}

OPTIMIZATIONS = [
    {"opportunity": "Exit intent popup", "monthly_impact": 18000},
    {"opportunity": "SMS all segments", "monthly_impact": 12000},
    {"opportunity": "Dynamic pricing", "monthly_impact": 8000},
    {"opportunity": "Lower shipping ($75>$65)", "monthly_impact": 6000},
    {"opportunity": "Express wallet checkout", "monthly_impact": 4000},
]

OPTIMIZATION_NOTES = {
    "quick_win": "Exit intent popup - \"Wait! 10% off\" - 8-12% conversion, same-day implementation",
    "insight": "42% abandon at shipping reveal - lower threshold or flat $5 rate",
}

RECOVERY_CAMPAIGNS = {
    "email_1": {"name": "Draft Email Reminder", "delay_hours": 1, "subject": "Draft: neutral cart reminder", "incentive": None, "avg_open_rate": 45.2, "avg_conversion": 8.5},
    "sms_1": {"name": "Draft SMS Reminder", "delay_hours": 2, "subject": "Draft: concise cart reminder", "incentive": None, "avg_open_rate": 98.0, "avg_conversion": 4.8},
    "retargeting_ad": {"name": "Draft Retargeting Concept", "delay_hours": 6, "subject": "Draft: consented product reminder concept", "incentive": None, "avg_open_rate": 0, "avg_conversion": 2.1},
    "email_2": {"name": "Draft Follow-Up", "delay_hours": 24, "subject": "Draft: availability-neutral follow-up", "incentive": None, "avg_open_rate": 38.1, "avg_conversion": 5.2},
    "email_3": {"name": "Draft Value Option", "delay_hours": 72, "subject": "Draft: approved value option, if eligible", "incentive": "Optional incentive concept", "avg_open_rate": 42.8, "avg_conversion": 12.1},
}

# cost_margin_impact = % of cart value given up; flat_cost = fixed dollar cost (free shipping).
INCENTIVE_OPTIONS = {
    "percent_off_10": {"description": "10% off cart total", "cost_margin_impact": 10.0, "flat_cost": 0, "conversion_lift": 35.0},
    "percent_off_15": {"description": "15% off cart total", "cost_margin_impact": 15.0, "flat_cost": 0, "conversion_lift": 48.0},
    "free_shipping": {"description": "Free standard shipping", "cost_margin_impact": 0.0, "flat_cost": 12, "conversion_lift": 28.0},
    "dollar_off_20": {"description": "$20 off orders over $150", "cost_margin_impact": 0.0, "flat_cost": 20, "conversion_lift": 22.0},
    "gift_with_purchase": {"description": "Free accessory with order", "cost_margin_impact": 6.0, "flat_cost": 0, "conversion_lift": 18.0},
}

CONVERSION_METRICS = {
    "overall_abandonment_rate": 71.4,
    "recovery_rate": 12.8,
    "avg_recovered_value": 187.50,
    "total_abandoned_30d": 4250,
    "total_recovered_30d": 544,
    "total_recovered_revenue_30d": 102000,
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _k(dollars):
    """18400 -> '$18K', 172000 -> '$172K'."""
    return f"${round(dollars / 1000):,}K"


def _recommended_incentive(cart):
    """Recommend an incentive from cart value and segment."""
    if cart["segment"] == "vip":
        return "free_shipping"
    if cart["segment"] == "repeat_buyer" and cart["cart_value"] > 500:
        return "percent_off_10"
    if cart["segment"] == "new_visitor":
        return "percent_off_15"
    return "dollar_off_20"


def _recoverable_value():
    """Sum of contactable, recoverable sample cart values."""
    return sum(c["cart_value"] for c in ABANDONED_CARTS.values()
               if c["contactable"] and c["recovery_status"] != "unrecoverable")


APPROVED_PERSONAS = {
    "Marketing Manager": "margin-aware recovery planning and approval gates",
    "Digital Marketing Lead": "channel sequencing, consent, and draft content",
    "Growth Manager": "aggregate conversion scenarios and experiment design",
}

SAFETY_NOTICE = (
    "> Synthetic aggregate planning data. Drafts and scenarios only; no shopper "
    "is contacted, no message or offer is sent, and no cart or purchase is changed."
)


def _response_header(persona):
    role = persona if persona in APPROVED_PERSONAS else "Marketing Manager"
    return [f"**Prepared for:** {role} ({APPROVED_PERSONAS[role]})", ""]


def _footer():
    return ["", SAFETY_NOTICE]


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "abandonment_analysis",
    "recovery_campaign",
    "incentive_optimization",
    "conversion_tracking",
    "recovery_strategies",
    "recovery_forecast",
    "optimization_recommendations",
]


class CartAbandonmentRecoveryAgent(BasicAgent):
    """Cart abandonment recovery agent for e-commerce."""

    def __init__(self):
        self.name = "CartAbandonmentRecoveryAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Cart Abandonment Recovery Agent",
            "description": (
                __manifest__["description"] + " Always use this tool for today's abandoned carts. A marketer "
                "walks the operations in order: show today's abandoned carts / recover high-value ones -> "
                "abandonment_analysis; personalized recovery strategies -> recovery_strategies; launch the "
                "campaigns / full recovery program -> recovery_campaign (returns the draft program ready for "
                "approval; nothing is sent); tracking dashboard and expected results -> recovery_forecast; "
                "what else can improve recovery rates -> optimization_recommendations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "abandonment_analysis: today's abandoned carts by segment, top opportunities and "
                            "why shoppers abandon. recovery_strategies: personalized offers per segment and top "
                            "shopper. recovery_campaign: the campaigns and multi-touch sequences (launch request "
                            "-> draft program for approval). recovery_forecast: tracking dashboard, 48-hour "
                            "recovery forecast, benchmark and monthly impact. optimization_recommendations: "
                            "ways to improve recovery rates. incentive_optimization: compare incentive "
                            "scenarios by cart. conversion_tracking: past 30-day recovery metrics."
                        ),
                    },
                    "cart_id": {"type": "string", "description": "Optional cart, e.g. 'CART-20001'"},
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
        cart_id = kwargs.get("cart_id")
        if cart_id and cart_id not in ABANDONED_CARTS:
            return f"Unknown cart_id `{cart_id}`. Valid: {', '.join(ABANDONED_CARTS)}"
        operation = kwargs.get("operation", "abandonment_analysis")
        dispatch = {
            "abandonment_analysis": self._abandonment_analysis,
            "recovery_campaign": self._recovery_campaign,
            "incentive_optimization": self._incentive_optimization,
            "conversion_tracking": self._conversion_tracking,
            "recovery_strategies": self._recovery_strategies,
            "recovery_forecast": self._recovery_forecast,
            "optimization_recommendations": self._optimization_recommendations,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _abandonment_analysis(self, **kwargs) -> str:
        carts = sum(s["carts"] for s in TODAY_SEGMENTS)
        value = sum(s["value"] for s in TODAY_SEGMENTS)
        lines = _response_header(kwargs.get("persona")) + ["# Synthetic Cart Abandonment Analysis", ""]
        lines.append(f"Analyzed {carts} abandoned carts worth {_k(value)} today.")
        lines += ["", "| Segment | Carts | Value | Recovery |", "|---|---|---|---|"]
        for s in TODAY_SEGMENTS:
            lines.append(f"| {s['segment']} | {s['carts']} | {_k(s['value'])} | {s['recovery_pct']}% |")
        top = sorted(ABANDONED_CARTS.values(), key=lambda c: c["cart_value"], reverse=True)
        top = [c for c in top if c["contactable"]][:3]
        lines.append("")
        lines.append("**Top Opportunities:** " + ", ".join(f"{c['shopper_label']} (${c['cart_value']:,.0f})" for c in top))
        lines.append("**Why Abandoning:** " + ", ".join(f"{r['pct']}% {r['reason']}" for r in ABANDON_REASONS[:3]))
        lines += ["", "Source: [Commerce analytics + Cart events] (synthetic)", "", "Want personalized recovery strategies?"]
        return "\n".join(lines + _footer())

    def _recovery_strategies(self, **kwargs) -> str:
        lines = _response_header(kwargs.get("persona")) + ["# Personalized Recovery Strategies (Proposed)", ""]
        lines.append("Personalized strategies by segment, proposed for your approval:")
        lines += ["", "| Audience | Offer | Channel |", "|---|---|---|"]
        for s in RECOVERY_STRATEGIES:
            lines.append(f"| {s['audience']} | {s['offer']} | {s['channel']} |")
        lines += ["", "Offers stay within the approved discount guardrails; nothing is sent until you approve and launch.",
                  "", "Launch campaigns?"]
        return "\n".join(lines + _footer())

    def _recovery_campaign(self, **kwargs) -> str:
        lines = _response_header(kwargs.get("persona")) + ["# Draft Recovery Campaign Dashboard", ""]
        lines.append("Recovery program ready to launch (draft, not deployed - launch it from your marketing platform after approval):")
        lines += ["", "| Campaign | Members |", "|---|---|"]
        for c in CAMPAIGN_AUDIENCES:
            lines.append(f"| {c['campaign']} | {c['members']:,} |")
        lines += ["", "**Multi-Touch Sequences:**"]
        for seq in MULTI_TOUCH_SEQUENCES:
            lines.append(f"- {seq['segment']}: " + " -> ".join(seq["steps"]))
        lines += ["", "See real-time tracking?"]
        return "\n".join(lines + _footer())

    def _recovery_forecast(self, **kwargs) -> str:
        b = BENCHMARKS
        lines = _response_header(kwargs.get("persona")) + ["# Recovery Forecast (48 hours)", ""]
        lines += ["| Segment | Recovery | Revenue |", "|---|---|---|"]
        total_rev = 0
        total_val = 0
        for s in TODAY_SEGMENTS:
            rev = s["value"] * s["recovery_pct"] // 100
            total_rev += rev
            total_val += s["value"]
            lines.append(f"| {s['segment']} | {s['recovery_pct']}% | ${rev:,} |")
        lines.append(f"| **Total** | **{round(total_rev * 100 / total_val)}%** | **${total_rev:,}** |")
        gain = b["monthly_recovered_optimized"] - b["monthly_recovered_current"]
        lines += [
            "",
            f"**Benchmark:** Industry {b['industry_recovery_pct']}% -> Your target {b['target_recovery_pct']}%",
            f"**Monthly Impact:** Current {_k(b['monthly_recovered_current'])} -> Optimized "
            f"{_k(b['monthly_recovered_optimized'])} (+{_k(gain)}/month)",
            "",
            "Modeled forecast from synthetic segment recovery rates; not measured results.",
            "",
            "Generate optimization recommendations?",
        ]
        return "\n".join(lines + _footer())

    def _optimization_recommendations(self, **kwargs) -> str:
        b = BENCHMARKS
        lines = _response_header(kwargs.get("persona")) + ["# Recovery Optimization Recommendations", ""]
        lines.append(f"{len(OPTIMIZATIONS)} optimizations to push recovery {b['target_recovery_pct']}% -> {b['optimized_recovery_pct']}%:")
        lines += ["", "| Opportunity | Impact |", "|---|---|"]
        for o in OPTIMIZATIONS:
            lines.append(f"| {o['opportunity']} | +{_k(o['monthly_impact'])}/mo |")
        lines += [
            "",
            f"**Quick Win:** {OPTIMIZATION_NOTES['quick_win']}",
            f"**Insight:** {OPTIMIZATION_NOTES['insight']}",
            "",
            "Each change is a recommendation for approval; nothing is changed on the site.",
            "",
            "Summarize complete strategy?",
        ]
        return "\n".join(lines + _footer())

    def _incentive_optimization(self, **kwargs) -> str:
        lines = _response_header(kwargs.get("persona")) + ["# Draft Incentive Scenario Comparison", ""]
        lines.append("## Available Incentives\n")
        lines.append("| Incentive | Description | Cost | Conversion Lift |")
        lines.append("|---|---|---|---|")
        for iid, inc in INCENTIVE_OPTIONS.items():
            cost = f"${inc['flat_cost']} flat" if inc["flat_cost"] else f"{inc['cost_margin_impact']}% of cart"
            lines.append(f"| {iid.replace('_', ' ').title()} | {inc['description']} | {cost} | +{inc['conversion_lift']}% |")
        lines.append("\n## Recommended Incentives by Cart\n")
        cart_id = kwargs.get("cart_id")
        carts = {cart_id: ABANDONED_CARTS[cart_id]} if cart_id else ABANDONED_CARTS
        for cid, cart in carts.items():
            if cart["recovery_status"] == "unrecoverable":
                continue
            inc = INCENTIVE_OPTIONS[_recommended_incentive(cart)]
            net = cart["cart_value"] * (1 - inc["cost_margin_impact"] / 100) - inc["flat_cost"]
            lines.append(f"### {cid}: {cart['shopper_label']} (${cart['cart_value']:,.2f})\n")
            lines.append(f"- **Segment:** {cart['segment'].replace('_', ' ').title()}")
            lines.append(f"- **Scenario for approval:** {inc['description']}")
            lines.append(f"- **Expected Lift:** +{inc['conversion_lift']}%")
            lines.append(f"- **Net Recovery Value:** ${net:,.2f}\n")
        return "\n".join(lines + _footer())

    def _conversion_tracking(self, **kwargs) -> str:
        m = CONVERSION_METRICS
        lines = _response_header(kwargs.get("persona")) + ["# Synthetic Conversion Tracking (30-Day)", ""]
        lines.append(f"- **Abandonment Rate:** {m['overall_abandonment_rate']}%")
        lines.append(f"- **Recovery Rate:** {m['recovery_rate']}%")
        lines.append(f"- **Avg Recovered Order Value:** ${m['avg_recovered_value']:,.2f}")
        lines.append(f"- **Total Abandoned Carts:** {m['total_abandoned_30d']:,}")
        lines.append(f"- **Total Recovered:** {m['total_recovered_30d']:,}")
        lines.append(f"- **Recovered Revenue:** ${m['total_recovered_revenue_30d']:,.0f}\n")
        lines.append("## Campaign Performance (recovered revenue allocated by conversion share)\n")
        lines.append("| Campaign | Open Rate | Conversion | Est. Recovered |")
        lines.append("|---|---|---|---|")
        total_conv = sum(c["avg_conversion"] for c in RECOVERY_CAMPAIGNS.values())
        for camp in RECOVERY_CAMPAIGNS.values():
            est = round(m["total_recovered_revenue_30d"] * camp["avg_conversion"] / total_conv)
            lines.append(f"| {camp['name']} | {camp['avg_open_rate']}% | {camp['avg_conversion']}% | ${est:,} |")
        lines.append(f"\n**Recoverable Sample Cart Value (contactable carts only):** ${_recoverable_value():,.2f}")
        return "\n".join(lines + _footer())


# ---------------------------------------------------------------------------
# Main — the demo video's five turns, then the remaining operations
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = CartAbandonmentRecoveryAgent()
    for op in ["abandonment_analysis", "recovery_strategies", "recovery_campaign", "recovery_forecast",
               "optimization_recommendations", "incentive_optimization", "conversion_tracking"]:
        print("=" * 80)
        print(agent.perform(operation=op))
