"""
Cart Abandonment Recovery Agent — B2C Sales Stack

Analyzes synthetic cart abandonment patterns, drafts recovery concepts,
compares incentive scenarios, and tracks aggregate conversion metrics.
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

ABANDONED_CARTS = {
    "CART-20001": {
        "shopper_label": "Synthetic returning-shopper cart",
        "contactable": True,
        "segment": "returning_shopper",
        "items": [
            {"name": "Wireless Noise-Canceling Headphones", "sku": "ELEC-4421", "price": 249.99, "qty": 1},
            {"name": "Premium Headphone Case", "sku": "ACC-1102", "price": 34.99, "qty": 1},
        ],
        "cart_value": 284.98,
        "abandoned_at": "2025-03-04T14:22:00",
        "page_exit": "shipping_options",
        "device": "mobile",
        "prior_purchases": 8,
        "recovery_status": "draft_stage_1_ready",
    },
    "CART-20002": {
        "shopper_label": "Synthetic first-session cart",
        "contactable": True,
        "segment": "new_visitor",
        "items": [
            {"name": "Smart Home Hub Pro", "sku": "SMRT-3305", "price": 179.99, "qty": 1},
            {"name": "Smart Bulb 4-Pack", "sku": "SMRT-1140", "price": 59.99, "qty": 2},
        ],
        "cart_value": 299.97,
        "abandoned_at": "2025-03-05T09:15:00",
        "page_exit": "account_creation",
        "device": "desktop",
        "prior_purchases": 0,
        "recovery_status": "not_contacted",
    },
    "CART-20003": {
        "shopper_label": "Synthetic established-shopper cart",
        "contactable": True,
        "segment": "established_shopper",
        "items": [
            {"name": "4K OLED Smart TV 65-inch", "sku": "TV-7720", "price": 1299.99, "qty": 1},
            {"name": "Soundbar System", "sku": "AUD-5501", "price": 449.99, "qty": 1},
            {"name": "HDMI Cable 6ft", "sku": "ACC-0042", "price": 14.99, "qty": 2},
        ],
        "cart_value": 1779.96,
        "abandoned_at": "2025-03-05T18:45:00",
        "page_exit": "payment",
        "device": "desktop",
        "prior_purchases": 12,
        "recovery_status": "not_contacted",
    },
    "CART-20004": {
        "shopper_label": "Synthetic guest cart",
        "contactable": False,
        "segment": "guest",
        "items": [
            {"name": "Running Shoes Pro X", "sku": "SHOE-2201", "price": 129.99, "qty": 1},
        ],
        "cart_value": 129.99,
        "abandoned_at": "2025-03-06T11:30:00",
        "page_exit": "cart_page",
        "device": "mobile",
        "prior_purchases": 0,
        "recovery_status": "unrecoverable",
    },
}

RECOVERY_CAMPAIGNS = {
    "email_1": {"name": "Draft Email Reminder", "delay_hours": 1, "subject": "Draft: neutral cart reminder", "incentive": None, "avg_open_rate": 45.2, "avg_conversion": 8.5},
    "email_2": {"name": "Draft Follow-Up", "delay_hours": 24, "subject": "Draft: availability-neutral follow-up", "incentive": None, "avg_open_rate": 38.1, "avg_conversion": 5.2},
    "email_3": {"name": "Draft Value Option", "delay_hours": 72, "subject": "Draft: approved value option, if eligible", "incentive": "Optional incentive concept", "avg_open_rate": 42.8, "avg_conversion": 12.1},
    "sms_1": {"name": "Draft SMS Reminder", "delay_hours": 2, "subject": "Draft: concise cart reminder", "incentive": None, "avg_open_rate": 98.0, "avg_conversion": 4.8},
    "retargeting_ad": {"name": "Draft Retargeting Concept", "delay_hours": 6, "subject": "Draft: consented product reminder concept", "incentive": None, "avg_open_rate": 0, "avg_conversion": 2.1},
}

INCENTIVE_OPTIONS = {
    "percent_off_10": {"description": "10% off cart total", "cost_margin_impact": 10.0, "conversion_lift": 35.0},
    "percent_off_15": {"description": "15% off cart total", "cost_margin_impact": 15.0, "conversion_lift": 48.0},
    "free_shipping": {"description": "Free standard shipping", "cost_margin_impact": 5.5, "conversion_lift": 28.0},
    "dollar_off_20": {"description": "$20 off orders over $150", "cost_margin_impact": 8.0, "conversion_lift": 22.0},
    "gift_with_purchase": {"description": "Free accessory with order", "cost_margin_impact": 6.0, "conversion_lift": 18.0},
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

def _abandonment_by_exit(carts=None):
    """Break down abandonment by exit page."""
    by_page = {}
    for cart in (carts or ABANDONED_CARTS).values():
        page = cart["page_exit"]
        by_page[page] = by_page.get(page, 0) + 1
    return by_page


def _recommended_incentive(cart):
    """Recommend optimal incentive based on cart value and customer segment."""
    if cart["segment"] == "established_shopper" and cart["cart_value"] > 500:
        return "percent_off_10"
    elif cart["segment"] == "returning_shopper":
        return "free_shipping"
    elif cart["segment"] == "new_visitor":
        return "percent_off_15"
    return "dollar_off_20"


def _total_abandoned_value():
    """Sum of all abandoned cart values."""
    return sum(c["cart_value"] for c in ABANDONED_CARTS.values())

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
    return [
        f"**Prepared for:** {role}",
        f"**Role focus:** {APPROVED_PERSONAS[role]}",
        "",
        SAFETY_NOTICE,
        "",
    ]


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class CartAbandonmentRecoveryAgent(BasicAgent):
    """Cart abandonment recovery agent for e-commerce."""

    def __init__(self):
        self.name = "CartAbandonmentRecoveryAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Cart Abandonment Recovery Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "abandonment_analysis",
                            "recovery_campaign",
                            "incentive_optimization",
                            "conversion_tracking",
                        ],
                    },
                    "cart_id": {"type": "string"},
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
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _abandonment_analysis(self, **kwargs) -> str:
        cart_id = kwargs.get("cart_id")
        carts = {cart_id: ABANDONED_CARTS[cart_id]} if cart_id else ABANDONED_CARTS
        total_value = sum(c["cart_value"] for c in carts.values())
        by_exit = _abandonment_by_exit(carts)
        lines = _response_header(kwargs.get("persona")) + ["# Synthetic Cart Abandonment Analysis\n"]
        lines.append(f"**Abandoned Carts:** {len(carts)}")
        lines.append(f"**Total Abandoned Value:** ${total_value:,.2f}")
        lines.append(f"**Abandonment Rate:** {CONVERSION_METRICS['overall_abandonment_rate']}%\n")
        lines.append("## Abandoned Carts Detail\n")
        lines.append("| Cart ID | Customer | Segment | Value | Exit Page | Device | Status |")
        lines.append("|---|---|---|---|---|---|---|")
        for cid, c in carts.items():
            lines.append(
                f"| {cid} | {c['shopper_label']} | {c['segment'].replace('_', ' ').title()} "
                f"| ${c['cart_value']:,.2f} | {c['page_exit'].replace('_', ' ').title()} "
                f"| {c['device'].title()} | {c['recovery_status'].replace('_', ' ').title()} |"
            )
        lines.append("\n## Exit Page Breakdown\n")
        for page, count in by_exit.items():
            lines.append(f"- {page.replace('_', ' ').title()}: {count}")
        return "\n".join(lines)

    def _recovery_campaign(self, **kwargs) -> str:
        lines = _response_header(kwargs.get("persona")) + ["# Draft Recovery Campaign Dashboard\n"]
        lines.append("## Proposed Sequence (not deployed)\n")
        lines.append("| Campaign | Delay | Subject | Incentive | Open Rate | Conversion |")
        lines.append("|---|---|---|---|---|---|")
        for cid, camp in RECOVERY_CAMPAIGNS.items():
            incentive = camp["incentive"] or "None"
            lines.append(
                f"| {camp['name']} | {camp['delay_hours']}h | {camp['subject']} "
                f"| {incentive} | {camp['avg_open_rate']}% | {camp['avg_conversion']}% |"
            )
        lines.append("\n## Carts Pending Recovery\n")
        cart_id = kwargs.get("cart_id")
        carts = {cart_id: ABANDONED_CARTS[cart_id]} if cart_id else ABANDONED_CARTS
        pending = {k: v for k, v in carts.items() if v["recovery_status"] != "unrecoverable" and v["contactable"]}
        for cid, cart in pending.items():
            lines.append(f"- **{cid}** ({cart['shopper_label']}): ${cart['cart_value']:,.2f} — Draft status: {cart['recovery_status'].replace('_', ' ').title()}")
        unrecoverable = sum(1 for c in carts.values() if c["recovery_status"] == "unrecoverable")
        lines.append(f"\n**No consented contact path in synthetic record:** {unrecoverable}")
        return "\n".join(lines)

    def _incentive_optimization(self, **kwargs) -> str:
        lines = _response_header(kwargs.get("persona")) + ["# Draft Incentive Scenario Comparison\n"]
        lines.append("## Available Incentives\n")
        lines.append("| Incentive | Description | Margin Impact | Conversion Lift |")
        lines.append("|---|---|---|---|")
        for iid, inc in INCENTIVE_OPTIONS.items():
            lines.append(f"| {iid.replace('_', ' ').title()} | {inc['description']} | {inc['cost_margin_impact']}% | +{inc['conversion_lift']}% |")
        lines.append("\n## Recommended Incentives by Cart\n")
        cart_id = kwargs.get("cart_id")
        carts = {cart_id: ABANDONED_CARTS[cart_id]} if cart_id else ABANDONED_CARTS
        for cid, cart in carts.items():
            if cart["recovery_status"] == "unrecoverable":
                continue
            rec = _recommended_incentive(cart)
            inc = INCENTIVE_OPTIONS[rec]
            lines.append(f"### {cid}: {cart['shopper_label']} (${cart['cart_value']:,.2f})\n")
            lines.append(f"- **Segment:** {cart['segment'].replace('_', ' ').title()}")
            lines.append(f"- **Scenario for approval:** {inc['description']}")
            lines.append(f"- **Expected Lift:** +{inc['conversion_lift']}%")
            est_recovery = cart["cart_value"] * (1 - inc["cost_margin_impact"] / 100)
            lines.append(f"- **Net Recovery Value:** ${est_recovery:,.2f}\n")
        return "\n".join(lines)

    def _conversion_tracking(self, **kwargs) -> str:
        m = CONVERSION_METRICS
        lines = _response_header(kwargs.get("persona")) + ["# Synthetic Conversion Tracking (30-Day)\n"]
        lines.append(f"- **Abandonment Rate:** {m['overall_abandonment_rate']}%")
        lines.append(f"- **Recovery Rate:** {m['recovery_rate']}%")
        lines.append(f"- **Avg Recovered Order Value:** ${m['avg_recovered_value']:,.2f}")
        lines.append(f"- **Total Abandoned Carts:** {m['total_abandoned_30d']:,}")
        lines.append(f"- **Total Recovered:** {m['total_recovered_30d']:,}")
        lines.append(f"- **Recovered Revenue:** ${m['total_recovered_revenue_30d']:,.0f}\n")
        lines.append("## Campaign Performance\n")
        lines.append("| Campaign | Open Rate | Conversion | Est. Recovered |")
        lines.append("|---|---|---|---|")
        for cid, camp in RECOVERY_CAMPAIGNS.items():
            est = round(m["total_abandoned_30d"] * camp["avg_conversion"] / 100 * m["avg_recovered_value"], 0)
            lines.append(f"| {camp['name']} | {camp['avg_open_rate']}% | {camp['avg_conversion']}% | ${est:,.0f} |")
        potential = _total_abandoned_value()
        lines.append(f"\n**Current Active Cart Value at Risk:** ${potential:,.2f}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = CartAbandonmentRecoveryAgent()
    print(agent.perform(operation="abandonment_analysis"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="recovery_campaign"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="incentive_optimization"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="conversion_tracking"))
