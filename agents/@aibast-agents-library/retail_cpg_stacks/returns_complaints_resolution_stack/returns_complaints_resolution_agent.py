"""
Returns & Complaints Resolution Agent — Retail & CPG Stack

Provides synthetic return review, complaint classification, resolution-option
recommendations, and trend analysis for retail customer service teams.
"""

import sys
import os

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"),
)
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/returns-complaints-resolution",
    "version": "1.0.0",
    "display_name": "Returns and Complaints Resolution Agent",
    "description": (
        "Draft privacy-safe return reviews, complaint classifications, resolution options, and aggregate trend analysis for authorized human decision-makers."
    ),
    "author": "AIBAST",
    "tags": [
        "returns",
        "complaints",
        "customer-service",
        "resolution",
        "retail",
    ],
    "category": "retail_cpg",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic Data — Return Requests
# ---------------------------------------------------------------------------

RETURN_REQUESTS = {
    "RET-4001": {
        "order_id": "ORD-88712",
        "case_label": "Synthetic size-mismatch case",
        "product": "Classic Denim Jacket",
        "sku": "SKU-1001",
        "purchase_price": 89.99,
        "purchase_date": "2026-02-14",
        "request_date": "2026-03-02",
        "reason": "wrong_size",
        "condition": "unworn_tags_attached",
        "channel": "online",
        "status": "pending_review",
        "notes": "Ordered size M, needs size L. Willing to exchange.",
    },
    "RET-4002": {
        "order_id": "ORD-89234",
        "case_label": "Synthetic device-defect case",
        "product": "Smart Fitness Tracker",
        "sku": "SKU-1004",
        "purchase_price": 129.99,
        "purchase_date": "2026-01-20",
        "request_date": "2026-03-10",
        "reason": "defective",
        "condition": "non_functional",
        "channel": "in_store",
        "status": "policy_match_candidate",
        "notes": "Heart rate sensor stopped working after 3 weeks. Under warranty.",
    },
    "RET-4003": {
        "order_id": "ORD-87455",
        "case_label": "Synthetic description-mismatch case",
        "product": "Premium Running Shoes",
        "sku": "SKU-1005",
        "purchase_price": 149.99,
        "purchase_date": "2026-02-28",
        "request_date": "2026-03-08",
        "reason": "not_as_described",
        "condition": "lightly_used",
        "channel": "online",
        "status": "pending_review",
        "notes": "Color shown online was navy but received was dark grey.",
    },
    "RET-4004": {
        "order_id": "ORD-90100",
        "case_label": "Synthetic changed-mind case",
        "product": "Wireless Earbuds Pro",
        "sku": "SKU-1002",
        "purchase_price": 59.99,
        "purchase_date": "2026-03-01",
        "request_date": "2026-03-12",
        "reason": "changed_mind",
        "condition": "opened_unused",
        "channel": "online",
        "status": "pending_review",
        "notes": "Found a better deal elsewhere. Wants full refund.",
    },
    "RET-4005": {
        "order_id": "ORD-86321",
        "case_label": "Synthetic warranty-escalation case",
        "product": "Leather Crossbody Bag",
        "sku": "SKU-1007",
        "purchase_price": 79.99,
        "purchase_date": "2025-12-18",
        "request_date": "2026-03-14",
        "reason": "defective",
        "condition": "damaged",
        "channel": "in_store",
        "status": "escalated",
        "notes": "Strap broke after normal use. Outside 60-day window but claims manufacturing defect.",
    },
    "RET-4006": {
        "order_id": "ORD-91005",
        "case_label": "Synthetic wrong-item case",
        "product": "UV Protection Sunglasses",
        "sku": "SKU-1008",
        "purchase_price": 44.99,
        "purchase_date": "2026-03-05",
        "request_date": "2026-03-15",
        "reason": "wrong_item",
        "condition": "unopened",
        "channel": "online",
        "status": "policy_match_candidate",
        "notes": "Received aviator style instead of ordered wayfarer style.",
    },
}

COMPLAINT_CATEGORIES = {
    "product_quality": {
        "label": "Product Quality",
        "severity_weight": 0.85,
        "avg_resolution_hours": 36,
        "escalation_rate": 0.15,
        "keywords": ["defective", "broken", "poor quality", "fell apart", "not durable"],
        "monthly_volume": 142,
    },
    "order_fulfillment": {
        "label": "Order Fulfillment",
        "severity_weight": 0.70,
        "avg_resolution_hours": 24,
        "escalation_rate": 0.08,
        "keywords": ["wrong item", "missing", "late delivery", "not received", "damaged in shipping"],
        "monthly_volume": 98,
    },
    "pricing_billing": {
        "label": "Pricing & Billing",
        "severity_weight": 0.65,
        "avg_resolution_hours": 18,
        "escalation_rate": 0.05,
        "keywords": ["overcharged", "wrong price", "coupon not applied", "double charged"],
        "monthly_volume": 67,
    },
    "service_experience": {
        "label": "Service Experience",
        "severity_weight": 0.60,
        "avg_resolution_hours": 48,
        "escalation_rate": 0.22,
        "keywords": ["rude staff", "long wait", "unhelpful", "no response", "poor communication"],
        "monthly_volume": 53,
    },
}

RESOLUTION_PLAYBOOKS = {
    "full_refund": {
        "label": "Full Refund",
        "applicable_reasons": ["defective", "wrong_item", "not_as_described"],
        "applicable_conditions": ["non_functional", "unopened", "damaged"],
        "max_days_since_purchase": 90,
        "cost_impact": "high",
        "csat_impact": "high",
        "steps": [
            "Review the synthetic eligibility evidence",
            "Draft a full-refund option for authorized approval",
            "List any return-shipping requirements without generating a label",
            "Draft neutral confirmation language without sending it",
            "State that no refund or return is processed by this agent",
        ],
    },
    "exchange": {
        "label": "Product Exchange",
        "applicable_reasons": ["wrong_size", "wrong_item", "not_as_described"],
        "applicable_conditions": ["unworn_tags_attached", "unopened", "opened_unused"],
        "max_days_since_purchase": 60,
        "cost_impact": "medium",
        "csat_impact": "very_high",
        "steps": [
            "Review the requested replacement and verify availability separately",
            "Draft exchange eligibility for authorized approval",
            "List logistics considerations without creating shipments",
            "Draft tracking-language requirements without sending a message",
            "State that no exchange or reservation is performed",
        ],
    },
    "store_credit": {
        "label": "Store Credit",
        "applicable_reasons": ["changed_mind", "wrong_size"],
        "applicable_conditions": ["opened_unused", "lightly_used", "unworn_tags_attached"],
        "max_days_since_purchase": 45,
        "cost_impact": "low",
        "csat_impact": "moderate",
        "steps": [
            "Review whether the condition appears to meet the synthetic policy",
            "Draft a store-credit option without issuing value or a bonus",
            "Require authorized review before any loyalty-account change",
            "Draft disclosure language without sending a message",
        ],
    },
    "warranty_replacement": {
        "label": "Warranty Replacement",
        "applicable_reasons": ["defective"],
        "applicable_conditions": ["non_functional", "damaged"],
        "max_days_since_purchase": 365,
        "cost_impact": "medium",
        "csat_impact": "high",
        "steps": [
            "Review whether the synthetic record is within the warranty period",
            "List the documentation an authorized reviewer should inspect",
            "Draft a manufacturer-claim summary without submitting it",
            "List replacement considerations without reserving or shipping stock",
            "State that no return label or replacement is created",
        ],
    },
    "partial_refund": {
        "label": "Partial Refund",
        "applicable_reasons": ["not_as_described", "changed_mind"],
        "applicable_conditions": ["lightly_used"],
        "max_days_since_purchase": 30,
        "cost_impact": "medium",
        "csat_impact": "moderate",
        "steps": [
            "Review item-condition evidence and model a policy range",
            "Identify any disclosed fee rule for authorized review",
            "Draft a partial-refund option without processing funds",
            "Draft timeline language without notifying a customer",
        ],
    },
}

TREND_DATA = {
    "months": ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"],
    "total_returns": [312, 345, 498, 387, 328, 360],
    "return_rate_pct": [4.1, 4.5, 6.2, 5.0, 4.3, 4.7],
    "top_return_reasons": {
        "wrong_size": [98, 112, 160, 125, 105, 115],
        "defective": [72, 68, 95, 82, 71, 78],
        "changed_mind": [65, 78, 130, 88, 70, 80],
        "not_as_described": [45, 52, 68, 55, 48, 52],
        "wrong_item": [32, 35, 45, 37, 34, 35],
    },
    "avg_resolution_hours": [28.5, 30.2, 38.7, 32.1, 27.8, 29.4],
    "csat_score": [4.1, 4.0, 3.6, 3.9, 4.2, 4.1],
    "refund_total_usd": [18720.00, 21450.00, 34200.00, 24800.00, 19650.00, 22100.00],
}

# ---------------------------------------------------------------------------
# Synthetic Data — escalated VIP complaint (the demo case)
# ---------------------------------------------------------------------------

ESCALATED_CASES = {
    "CMP-5001": {
        "customer": "David Chen",
        "alias": "chen",
        "tier": "Diamond VIP",
        "lifetime_value": 18400,
        "purchases": 47,
        "expected_next_12m_revenue": 3200,
        "churn_risk_pct": 87,
        "churn_driver": "elevated due to poor service experience",
        "frustration": "High - 2 failed support calls",
        "product": "ProBook Elite 15\"",
        "price": 1899,
        "days_since_purchase": 3,
        "issue": "Display flickering, won't boot",
        "warranty": "Active (2-year standard)",
        "support_history": ["Call 1: 45 min hold, transferred 3 times", "Call 2: Troubleshooting failed, no resolution"],
        "upgrade_model": "ProBook Elite Plus",
        "upgrade_value": 2299,
        "courier_eta": "4:30 PM today (about 4 hours)",
        "talking_points": [
            ["Apologize sincerely", "I'm sorry for your experience, David. We failed your expectations."],
            ["Acknowledge VIP status", "As a Diamond member with 47 purchases, you deserve better."],
            ["Present upgrade", "We're sending the Elite Plus model - better processor, more RAM."],
            ["Emphasize speed", "Courier delivers in 4 hours, not days."],
            ["Highlight credit", "$200 store credit for the inconvenience."],
            ["Show commitment", "I'm personally overseeing this. Here's my direct line."],
        ],
    },
}

# Recovery tiers: cost to company = upgrade cost + credit + delivery.
RECOVERY_TIERS = [
    {"tier": 1, "name": "Premium Recovery", "replacement": "Upgrade to ProBook Elite Plus ($2,299 value)", "delivery": "Same-day courier delivery", "credit": 200, "return_extension_days": 90, "upgrade_cost": 300, "delivery_cost": 40, "retention_pct": 94, "min_tier": "Diamond VIP"},
    {"tier": 2, "name": "Standard Plus", "replacement": "Same model replacement", "delivery": "2-day shipping", "credit": 100, "return_extension_days": 0, "upgrade_cost": 0, "delivery_cost": 80, "retention_pct": 65, "min_tier": "Gold"},
    {"tier": 3, "name": "Standard", "replacement": "Same model replacement only", "delivery": "Standard shipping (5 days)", "credit": 0, "return_extension_days": 0, "upgrade_cost": 0, "delivery_cost": 0, "retention_pct": 35, "min_tier": "Any"},
]

FOLLOW_UP_PLAN = [
    ["Today (post-delivery)", "6:00 PM: automated delivery confirmation SMS"],
    ["Today (post-delivery)", "7:00 PM: \"How's your new laptop?\" email from you"],
    ["Day 3", "Check-in call from the customer success team"],
    ["Day 3", "Satisfaction survey (track NPS score)"],
    ["Day 7", "\"Tech tips for your Elite Plus\" email series begins"],
    ["Day 7", "Exclusive VIP promotion (accessories 25% off)"],
    ["Day 30", "Relationship health check"],
    ["Day 30", "Invitation to VIP appreciation event"],
]

FOLLOW_UP_MONITORING = ["Support ticket auto-priority for 90 days", "Churn risk score tracking", "Purchase behavior analysis"]

RECOVERY_PROGRAM = {
    "period": "last quarter",
    "metrics": [
        ["Resolution time", "4.2 hours", "3-5 days"],
        ["Customer retention", "94%", "68%"],
        ["NPS recovery", "+47 points", "+18 points"],
        ["Repeat purchase rate", "76% (6 months)", "34%"],
    ],
    "quarterly_investment": 127000,
    "revenue_protected": 4800000,
    "session_minutes": 12,
}

APPROVED_PERSONAS = {
    "Customer Service Agent": "empathetic review summaries and clear human-approval next steps",
    "Quality Team": "aggregate defect patterns and product-quality evidence",
    "Loss Prevention Team": "policy exceptions and suspicious aggregate patterns without accusation",
    "Service Manager": "VIP escalations, recovery options, and follow-up plans for approval",
}

SAFETY_NOTICE = (
    "> Synthetic case data. Decision support and draft language only; no return, "
    "refund, credit, replacement, shipment, reservation, account change, or "
    "customer message is approved, created, or sent."
)


def _response_header(persona):
    role = persona if persona in APPROVED_PERSONAS else "Customer Service Agent"
    return [
        f"**Prepared for:** {role}",
        f"**Role focus:** {APPROVED_PERSONAS[role]}",
        "",
        SAFETY_NOTICE,
        "",
    ]


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def _days_since_purchase(ret):
    """Calendar days between purchase and return request."""
    import datetime
    p = ret["purchase_date"].split("-")
    r = ret["request_date"].split("-")
    start = datetime.date(int(p[0]), int(p[1]), int(p[2]))
    end = datetime.date(int(r[0]), int(r[1]), int(r[2]))
    return (end - start).days


def _resolve_case(query):
    """Case ID or customer name; CMP-5001 when empty; None when nothing matches."""
    if not query:
        return "CMP-5001"
    q = str(query).lower().strip()
    for cid, case in ESCALATED_CASES.items():
        if cid.lower() in q or case["alias"] in q or q in case["customer"].lower():
            return cid
    return None


def _tier_cost(tier):
    return tier["upgrade_cost"] + tier["credit"] + tier["delivery_cost"]


def _recommended_tier(case):
    for tier in RECOVERY_TIERS:
        if tier["min_tier"] == case["tier"]:
            return tier
    return RECOVERY_TIERS[1]


def _program_net():
    return RECOVERY_PROGRAM["revenue_protected"] - RECOVERY_PROGRAM["quarterly_investment"]


def _classify_complaint(text):
    """Classify complaint text into a category based on keyword matching."""
    text_lower = text.lower()
    best_cat = "service_experience"
    best_score = 0
    for cat_id, cat in COMPLAINT_CATEGORIES.items():
        score = sum(1 for kw in cat["keywords"] if kw in text_lower)
        if score > best_score:
            best_score = score
            best_cat = cat_id
    return best_cat


def _recommend_resolution(ret):
    """Pick best resolution playbook for a return request."""
    reason = ret["reason"]
    condition = ret["condition"]
    days = _days_since_purchase(ret)
    best_match = None
    for pb_id, pb in RESOLUTION_PLAYBOOKS.items():
        if reason in pb["applicable_reasons"] and condition in pb["applicable_conditions"]:
            if days <= pb["max_days_since_purchase"]:
                if best_match is None or pb["csat_impact"] in ("very_high", "high"):
                    best_match = pb_id
    return best_match or "store_credit"


def _return_rate_trend():
    """Calculate return-rate trend direction."""
    rates = TREND_DATA["return_rate_pct"]
    recent_avg = sum(rates[-3:]) / 3
    earlier_avg = sum(rates[:3]) / 3
    if recent_avg < earlier_avg - 0.3:
        return "improving"
    elif recent_avg > earlier_avg + 0.3:
        return "worsening"
    return "stable"


# ---------------------------------------------------------------------------
# Agent Class
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "return_processing",
    "complaint_classification",
    "resolution_recommendation",
    "trend_analysis",
    "escalation_snapshot",
    "recovery_tiers",
    "resolution_execution_plan",
    "follow_up_plan",
    "recovery_performance",
    "executive_summary",
]


class ReturnsComplaintsResolutionAgent(BasicAgent):
    """Agent for automated returns processing and complaint resolution."""

    def __init__(self):
        self.name = "returns-complaints-resolution-agent"
        self.metadata = {
            "name": self.name,
            "description": (
                f"{__manifest__['description']} Always call this tool for returns and "
                "complaints work. For an escalated customer complaint (the demo case: David "
                "Chen, Diamond VIP, defective ProBook laptop, case CMP-5001) use "
                "`escalation_snapshot` first, then `recovery_tiers` for resolution options that "
                "keep a VIP satisfied, `resolution_execution_plan` when a tier is approved and "
                "talking points are needed, `follow_up_plan` after the call, `recovery_performance` "
                "for service recovery performance and financial impact, and `executive_summary` to "
                "recap. Route return queue, case evidence, or approval-boundary questions to "
                "`return_processing`; complaint category questions to `complaint_classification`; "
                "policy-grounded resolution options for a return to `resolution_recommendation`; "
                "and aggregate patterns to `trend_analysis`. When no ID is named, omit it: the "
                "escalation operations use CMP-5001 and return_processing returns the synthetic "
                "review queue, instead of asking a follow-up question. For a request to classify "
                "'this product concern' without quoted text, call `complaint_classification` and "
                "omit complaint_text; the operation uses the packaged canonical synthetic "
                "product-quality concern."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Required routing key. escalation_snapshot for an escalated "
                            "customer complaint (customer profile, purchase, support history, "
                            "churn risk); recovery_tiers for resolution options that keep a VIP "
                            "satisfied; resolution_execution_plan when a tier is approved / "
                            "'execute Tier 1' and talking points; follow_up_plan for the "
                            "follow-up plan after the call; recovery_performance for service "
                            "recovery performance and financial impact; executive_summary for "
                            "the executive summary / recap. return_processing for an anonymous "
                            "return review, case evidence, queue, or approval boundary (do not "
                            "ask for a case ID and do not substitute resolution_recommendation); "
                            "complaint_classification, resolution_recommendation and "
                            "trend_analysis as named."
                        ),
                        "enum": list(_OPERATIONS),
                    },
                    "return_id": {
                        "type": "string",
                        "description": (
                            "Synthetic return ID when a specific case is requested. "
                            "The size-mismatch case is RET-4001."
                        ),
                    },
                    "case_id": {
                        "type": "string",
                        "description": (
                            "Escalated complaint case or customer name: David Chen is CMP-5001 "
                            "(the default). Omit when the prompt names no case."
                        ),
                    },
                    "complaint_text": {
                        "type": "string",
                        "description": (
                            "Synthetic concern text for classification only. Omit it "
                            "when the prompt says 'this product concern'; the agent "
                            "uses the packaged canonical product-quality concern and "
                            "must not ask the user to repeat it."
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

    def _return_processing(self, **kwargs):
        return_id = kwargs.get("return_id")
        if return_id and return_id in RETURN_REQUESTS:
            returns = {return_id: RETURN_REQUESTS[return_id]}
        else:
            returns = RETURN_REQUESTS
        lines = _response_header(kwargs.get("persona")) + ["# Draft Return Review Queue", ""]
        lines.append("| Return ID | Synthetic Case | Product | Reason | Condition | Days | Status |")
        lines.append("|-----------|----------|---------|--------|-----------|------|--------|")
        for rid, ret in returns.items():
            days = _days_since_purchase(ret)
            lines.append(
                f"| {rid} | {ret['case_label']} | {ret['product']} "
                f"| {ret['reason'].replace('_', ' ')} | {ret['condition'].replace('_', ' ')} "
                f"| {days} | {ret['status'].replace('_', ' ')} |"
            )
        lines.append("")
        for rid, ret in returns.items():
            lines.append(f"### {rid} — {ret['product']}")
            lines.append("")
            lines.append(f"- **Order:** {ret['order_id']}")
            lines.append(f"- **Case:** {ret['case_label']}")
            lines.append(f"- **Purchase Date:** {ret['purchase_date']} | **Request Date:** {ret['request_date']}")
            lines.append(f"- **Channel:** {ret['channel']}")
            lines.append(f"- **Price:** ${ret['purchase_price']:.2f}")
            lines.append(f"- **Notes:** {ret['notes']}")
            lines.append("")
        pending = sum(1 for r in RETURN_REQUESTS.values() if r["status"] == "pending_review")
        total_value = sum(r["purchase_price"] for r in returns.values())
        lines.append(f"**Pending Reviews:** {pending} | **Queue Value:** ${total_value:,.2f}")
        return "\n".join(lines)

    def _complaint_classification(self, **kwargs):
        complaint_text = (
            kwargs.get("complaint_text")
            or "The synthetic item stopped working after a week."
        )
        lines = _response_header(kwargs.get("persona")) + ["# Draft Complaint Classification", ""]
        if complaint_text:
            cat_id = _classify_complaint(complaint_text)
            cat = COMPLAINT_CATEGORIES[cat_id]
            lines.append(f"**Classified As:** {cat['label']} (`{cat_id}`)")
            lines.append(f"**Severity Weight:** {cat['severity_weight']}")
            lines.append(f"**Avg Resolution Time:** {cat['avg_resolution_hours']}h")
            lines.append(f"**Escalation Rate:** {cat['escalation_rate']*100:.0f}%")
            lines.append("")
        lines.append("## Complaint Category Reference")
        lines.append("")
        lines.append("| Category | Monthly Volume | Severity | Avg Resolution | Escalation Rate |")
        lines.append("|----------|---------------|----------|----------------|-----------------|")
        total_volume = 0
        for cat_id, cat in COMPLAINT_CATEGORIES.items():
            total_volume += cat["monthly_volume"]
            lines.append(
                f"| {cat['label']} | {cat['monthly_volume']} "
                f"| {cat['severity_weight']:.2f} | {cat['avg_resolution_hours']}h "
                f"| {cat['escalation_rate']*100:.0f}% |"
            )
        lines.append("")
        lines.append(f"**Total Monthly Complaints:** {total_volume}")
        return "\n".join(lines)

    def _resolution_recommendation(self, **kwargs):
        return_id = kwargs.get("return_id")
        if return_id and return_id in RETURN_REQUESTS:
            returns = {return_id: RETURN_REQUESTS[return_id]}
        else:
            returns = {k: v for k, v in RETURN_REQUESTS.items() if v["status"] == "pending_review"}
        lines = _response_header(kwargs.get("persona")) + ["# Draft Resolution Options", ""]
        for rid, ret in returns.items():
            rec_id = _recommend_resolution(ret)
            playbook = RESOLUTION_PLAYBOOKS[rec_id]
            lines.append(f"## {rid} — {ret['case_label']}")
            lines.append("")
            lines.append(f"- **Product:** {ret['product']} (${ret['purchase_price']:.2f})")
            lines.append(f"- **Reason:** {ret['reason'].replace('_', ' ')}")
            lines.append(f"- **Option for authorized review:** {playbook['label']}")
            lines.append(f"- **Cost Impact:** {playbook['cost_impact']} | **CSAT Impact:** {playbook['csat_impact']}")
            lines.append("")
            lines.append("**Review Steps:**")
            for i, step in enumerate(playbook["steps"], 1):
                lines.append(f"  {i}. {step}")
            lines.append("")
        lines.append("## Available Resolution Playbooks")
        lines.append("")
        for pb_id, pb in RESOLUTION_PLAYBOOKS.items():
            lines.append(f"- **{pb['label']}** (`{pb_id}`): Window {pb['max_days_since_purchase']}d, "
                         f"Cost: {pb['cost_impact']}, CSAT: {pb['csat_impact']}")
        return "\n".join(lines)

    def _trend_analysis(self, **kwargs):
        trend_dir = _return_rate_trend()
        lines = _response_header(kwargs.get("persona")) + [
            "# Synthetic Returns & Complaints Trend Analysis",
            "",
            f"**Overall Trend:** {trend_dir.upper()}",
            "",
            "## Monthly Returns Overview",
            "",
            "| Month | Total Returns | Return Rate | Avg Resolution | CSAT | Refund Total |",
            "|-------|--------------|-------------|----------------|------|--------------|",
        ]
        for i, month in enumerate(TREND_DATA["months"]):
            lines.append(
                f"| {month} | {TREND_DATA['total_returns'][i]} "
                f"| {TREND_DATA['return_rate_pct'][i]}% "
                f"| {TREND_DATA['avg_resolution_hours'][i]}h "
                f"| {TREND_DATA['csat_score'][i]}/5.0 "
                f"| ${TREND_DATA['refund_total_usd'][i]:,.2f} |"
            )
        lines.append("")
        lines.append("## Return Reasons Breakdown (Last 6 Months)")
        lines.append("")
        for reason, volumes in TREND_DATA["top_return_reasons"].items():
            total = sum(volumes)
            avg = round(total / len(volumes), 1)
            lines.append(f"- **{reason.replace('_', ' ').title()}:** {total} total, {avg} avg/month")
        lines.append("")
        total_refunded = sum(TREND_DATA["refund_total_usd"])
        lines.append(f"**Total Refunded (6 months):** ${total_refunded:,.2f}")
        lines.append("")
        lines.append("## Key Insights")
        lines.append("")
        tr = TREND_DATA["total_returns"]
        spike = round((tr[2] - tr[1]) * 100 / tr[1])
        hours = TREND_DATA["avg_resolution_hours"]
        change = round((hours[-1] - hours[0]) * 100 / hours[0], 1)
        direction = "slower" if change > 0 else "faster"
        lines.append(f"- Holiday season (Dec) drove a {spike}% spike in returns, primarily changed-mind returns")
        lines.append("- Wrong-size returns consistently highest — consider enhanced size guide implementation")
        lines.append(f"- Resolution time is {abs(change)}% {direction} than at the start of the period ({hours[0]}h -> {hours[-1]}h)")
        lines.append("- CSAT recovered to 4.1 after post-holiday dip to 3.6")
        return "\n".join(lines)

    # -- escalated VIP complaint (demo video) --------------------------------
    def _case(self, kwargs):
        cid = _resolve_case(kwargs.get("case_id"))
        return cid, ESCALATED_CASES[cid]

    def _header(self, kwargs):
        return _response_header(kwargs.get("persona") or "Service Manager")

    def _escalation_snapshot(self, **kwargs):
        cid, c = self._case(kwargs)
        lines = self._header(kwargs) + [f"# Escalated Complaint {cid}: {c['customer']}", ""]
        lines.append(
            f"{c['customer']} is a {c['tier']} customer with ${c['lifetime_value']:,} lifetime value. "
            "Immediate resolution recommended."
        )
        lines.append("")
        lines.append("**Customer Profile:**")
        lines.append("")
        lines.append("| Detail | Information |")
        lines.append("|---|---|")
        lines.append(f"| Name | {c['customer']} |")
        lines.append(f"| Tier | {c['tier']} |")
        lines.append(f"| Lifetime value | ${c['lifetime_value']:,} ({c['purchases']} purchases) |")
        lines.append(f"| Issue | Laptop defect (day {c['days_since_purchase']}) |")
        lines.append(f"| Frustration level | {c['frustration']} |")
        lines.append("")
        lines.append("**Purchase Details:**")
        lines.append("")
        lines.append(f"- Product: {c['product']} (${c['price']:,})")
        lines.append(f"- Purchased: {c['days_since_purchase']} days ago")
        lines.append(f"- Issue: {c['issue']}")
        lines.append(f"- Warranty: {c['warranty']}")
        lines.append("")
        lines.append("**Previous Support:**")
        lines.append("")
        for call in c["support_history"]:
            lines.append(f"- {call}")
        lines.append("")
        lines.append(f"**Churn Risk:** {c['churn_risk_pct']}% ({c['churn_driver']})")
        lines.append("")
        lines.append("Source: [CRM + Support History + Purchase Records] (synthetic)")
        lines.append("")
        lines.append("**Next step:** prepare resolution options for this customer?")
        return "\n".join(lines)

    def _recovery_tiers(self, **kwargs):
        cid, c = self._case(kwargs)
        rec = _recommended_tier(c)
        lines = self._header(kwargs) + [f"# Resolution Options: {c['customer']} ({cid})", ""]
        lines.append(f"Three resolution tiers; Tier {rec['tier']} recommended for this {c['tier']} customer to protect retention.")
        lines.append("")
        for t in RECOVERY_TIERS:
            tag = " (Recommended)" if t["tier"] == rec["tier"] else ""
            lines.append(f"## Tier {t['tier']}: {t['name']}{tag}")
            lines.append("")
            lines.append(f"- {t['replacement']}")
            lines.append(f"- {t['delivery']}")
            if t["credit"]:
                lines.append(f"- ${t['credit']} store credit for inconvenience")
            if t["return_extension_days"]:
                lines.append(f"- {t['return_extension_days']}-day return extension")
            if t["tier"] == rec["tier"]:
                lines.append(f"- Cost to company: ${_tier_cost(t):,} | Retention value: ${c['lifetime_value']:,}")
            else:
                lines.append(f"- Cost: ${_tier_cost(t):,} | Retention: {t['retention_pct']}%")
            lines.append("")
        roi = c["lifetime_value"] // _tier_cost(rec)
        lines.append(
            f"**Recommendation:** Tier {rec['tier']} protects ${c['lifetime_value'] / 1000:.1f}K customer lifetime value "
            f"for a ${_tier_cost(rec):,} investment ({roi}:1 ROI)."
        )
        lines.append("")
        lines.append("Source: [Customer Analytics + Inventory + Retention Models] (synthetic)")
        lines.append("")
        lines.append(f"**Next step:** approve the Tier {rec['tier']} resolution?")
        return "\n".join(lines)

    def _resolution_execution_plan(self, **kwargs):
        cid, c = self._case(kwargs)
        t = _recommended_tier(c)
        lines = self._header(kwargs) + [f"# Tier {t['tier']} Resolution — ready for authorized execution ({cid})", ""]
        lines.append(
            "Approved option prepared. Each action below is ready for you to execute in the order, "
            "shipping and loyalty systems; the agent has not dispatched, credited or generated anything."
        )
        lines.append("")
        lines.append("| Action | Detail | Status |")
        lines.append("|---|---|---|")
        lines.append(f"| Dispatch upgrade | {c['upgrade_model']} (${c['upgrade_value']:,} value) | Ready to dispatch |")
        lines.append(f"| Courier | Same-day delivery, expected {c['courier_eta']} | Ready to book |")
        lines.append(f"| Store credit | ${t['credit']} to the customer account | Ready to apply |")
        lines.append("| Return label | For the defective unit | Ready to generate |")
        lines.append(f"| Return extension | {t['return_extension_days']} days | Ready to activate |")
        lines.append("")
        lines.append("**Your Talking Points:**")
        lines.append("")
        n = 0
        for label, text in c["talking_points"]:
            n += 1
            lines.append(f"{n}. {label} - \"{text}\"")
        lines.append("")
        lines.append("Source: [Service Recovery Playbook + CRM] (synthetic)")
        lines.append("")
        lines.append("**Next step:** make the call once the actions are confirmed.")
        return "\n".join(lines)

    def _follow_up_plan(self, **kwargs):
        cid, c = self._case(kwargs)
        lines = self._header(kwargs) + [f"# Follow-Up Plan: {c['customer']} ({cid})", ""]
        lines.append("Proposed touchpoints to confirm satisfaction and prevent future issues; ready for you to schedule.")
        lines.append("")
        current = ""
        for when, step in FOLLOW_UP_PLAN:
            if when != current:
                lines.append(f"**{when}:**")
                current = when
            lines.append(f"- {step}")
        lines.append("")
        lines.append("**Monitoring to activate:**")
        lines.append("")
        for item in FOLLOW_UP_MONITORING:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("Nothing has been scheduled or sent by the agent.")
        lines.append("")
        lines.append("Source: [Customer Success Automation + CRM] (synthetic)")
        lines.append("")
        lines.append("**Next step:** see the service recovery metrics?")
        return "\n".join(lines)

    def _recovery_performance(self, **kwargs):
        cid, c = self._case(kwargs)
        t = _recommended_tier(c)
        cost = _tier_cost(t)
        pr = RECOVERY_PROGRAM
        lines = self._header(kwargs) + ["# Service Recovery Performance and Financial Impact", ""]
        lines.append(f"**Program Performance ({pr['period']}):**")
        lines.append("")
        lines.append("| Metric | Result | Industry Avg |")
        lines.append("|---|---|---|")
        for metric, result, avg in pr["metrics"]:
            lines.append(f"| {metric} | {result} | {avg} |")
        lines.append("")
        lines.append(f"**Financial Impact - This Case ({cid}):**")
        lines.append("")
        lines.append(f"- Investment: ${cost:,} (upgrade ${t['upgrade_cost']} + credit ${t['credit']} + courier ${t['delivery_cost']})")
        lines.append(f"- Customer lifetime value protected: ${c['lifetime_value']:,}")
        lines.append(f"- Expected next 12-month revenue: ${c['expected_next_12m_revenue']:,}")
        lines.append(
            f"- ROI: {c['lifetime_value'] // cost}:1 on retention, "
            f"{round(c['expected_next_12m_revenue'] / cost)}:1 on near-term revenue"
        )
        lines.append("")
        lines.append("**Program Economics:**")
        lines.append("")
        lines.append(f"- Quarterly recovery investment: ${pr['quarterly_investment']:,}")
        lines.append(f"- Revenue protected: ${pr['revenue_protected'] / 1000000:.1f}M")
        lines.append(f"- Net value: ${_program_net() / 1000000:.2f}M")
        lines.append("")
        lines.append("Source: [Service Analytics + Financial Data] (synthetic)")
        lines.append("")
        lines.append("**Next step:** generate the executive summary for leadership?")
        return "\n".join(lines)

    def _executive_summary(self, **kwargs):
        cid, c = self._case(kwargs)
        t = _recommended_tier(c)
        cost = _tier_cost(t)
        pr = RECOVERY_PROGRAM
        lines = self._header(kwargs) + [f"# Executive Summary: Service Recovery {cid} (draft for leadership)", ""]
        lines.append(f"What this {pr['session_minutes']}-minute session prepared:")
        lines.append("")
        lines.append(f"- Customer analysis — {c['customer']}: {c['tier']}, ${c['lifetime_value'] / 1000:.1f}K lifetime value, {c['churn_risk_pct']}% churn risk")
        lines.append(f"- Solution designed — Tier {t['tier']} {t['name'].lower()}: upgrade + same-day delivery + ${t['credit']} credit")
        lines.append(f"- Execution — {c['upgrade_model']} dispatch and 4-hour courier prepared for authorized execution")
        lines.append("- Call support — talking points, apology framework, commitment statements")
        lines.append("- Follow-up — 30-day touchpoint series, satisfaction tracking, VIP monitoring (proposed)")
        lines.append(f"- Performance — {pr['metrics'][1][1]} retention, {c['lifetime_value'] // cost}:1 ROI, ${_program_net() / 1000000:.2f}M quarterly program value")
        lines.append("")
        lines.append(
            f"**Customer Outcome:** issue resolved in about 4 hours vs the 3-5 day standard once the actions are "
            f"executed; upgraded product, ${t['credit']} credit, personal manager relationship."
        )
        lines.append(f"**Business Value:** ${c['lifetime_value']:,} customer retained for a ${cost:,} investment, {c['lifetime_value'] // cost}:1 ROI model.")
        lines.append("")
        lines.append("Draft summary ready for you to share in Teams; nothing has been sent.")
        lines.append("")
        lines.append("Source: [All connected systems] (synthetic)")
        return "\n".join(lines)

    def perform(self, **kwargs):
        if kwargs.get("data_source", "synthetic") != "synthetic":
            return "data_source must be `synthetic` for this package."
        return_id = kwargs.get("return_id")
        if return_id and return_id not in RETURN_REQUESTS:
            return (
                f"Unknown return_id `{return_id}`. Valid synthetic IDs: "
                f"{', '.join(RETURN_REQUESTS)}"
            )
        operation = kwargs.get("operation", "return_processing")
        dispatch = {
            "return_processing": self._return_processing,
            "complaint_classification": self._complaint_classification,
            "resolution_recommendation": self._resolution_recommendation,
            "trend_analysis": self._trend_analysis,
            "escalation_snapshot": self._escalation_snapshot,
            "recovery_tiers": self._recovery_tiers,
            "resolution_execution_plan": self._resolution_execution_plan,
            "follow_up_plan": self._follow_up_plan,
            "recovery_performance": self._recovery_performance,
            "executive_summary": self._executive_summary,
        }
        case_query = kwargs.get("case_id")
        if case_query and _resolve_case(case_query) is None:
            return (
                f"Unknown case_id `{case_query}`. Valid synthetic cases: "
                f"{', '.join(ESCALATED_CASES)} (David Chen)"
            )
        handler = dispatch.get(operation)
        if not handler:
            return f"Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)


# ---------------------------------------------------------------------------
# Main — exercise all operations
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = ReturnsComplaintsResolutionAgent()
    print("=" * 80)
    print(agent.perform(operation="return_processing"))
    print("\n" + "=" * 80)
    print(agent.perform(operation="complaint_classification", complaint_text="The product fell apart after one week, poor quality stitching"))
    print("\n" + "=" * 80)
    print(agent.perform(operation="resolution_recommendation", return_id="RET-4001"))
    print("\n" + "=" * 80)
    print(agent.perform(operation="trend_analysis"))
    for op in _OPERATIONS[4:]:
        print("=" * 80)
        print(agent.perform(operation=op))
