"""
Returns & Complaints Resolution Agent — Retail & CPG Stack

Handles return processing, complaint classification, resolution
recommendation, and trend analysis for retail customer service operations.
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
    "display_name": "Returns & Complaints Resolution Agent",
    "description": (
        "Automates return processing, classifies customer complaints, "
        "recommends optimal resolutions, and identifies complaint trends "
        "for retail and CPG customer service teams."
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
        "customer_id": "CUST-2041",
        "customer_name": "Sarah Mitchell",
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
        "customer_id": "CUST-3178",
        "customer_name": "James Kowalski",
        "product": "Smart Fitness Tracker",
        "sku": "SKU-1004",
        "purchase_price": 129.99,
        "purchase_date": "2026-01-20",
        "request_date": "2026-03-10",
        "reason": "defective",
        "condition": "non_functional",
        "channel": "in_store",
        "status": "approved",
        "notes": "Heart rate sensor stopped working after 3 weeks. Under warranty.",
    },
    "RET-4003": {
        "order_id": "ORD-87455",
        "customer_id": "CUST-1590",
        "customer_name": "Maria Chen",
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
        "customer_id": "CUST-4422",
        "customer_name": "David Okafor",
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
        "customer_id": "CUST-0887",
        "customer_name": "Linda Park",
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
        "customer_id": "CUST-5610",
        "customer_name": "Robert Fernandez",
        "product": "UV Protection Sunglasses",
        "sku": "SKU-1008",
        "purchase_price": 44.99,
        "purchase_date": "2026-03-05",
        "request_date": "2026-03-15",
        "reason": "wrong_item",
        "condition": "unopened",
        "channel": "online",
        "status": "approved",
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
            "Verify purchase and return eligibility",
            "Approve full refund to original payment method",
            "Generate prepaid return shipping label",
            "Send confirmation email with refund timeline",
            "Process refund within 3-5 business days",
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
            "Confirm desired replacement item and availability",
            "Generate prepaid return label for original item",
            "Ship replacement item with expedited shipping",
            "Send tracking information for both shipments",
            "Follow up after delivery to confirm satisfaction",
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
            "Verify item condition meets return standards",
            "Issue store credit for full purchase amount plus 10% bonus",
            "Credit applied to customer loyalty account",
            "Send email with credit balance and expiration date",
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
            "Verify product is within warranty period",
            "Collect defect documentation and photos",
            "Submit warranty claim to manufacturer",
            "Ship replacement from warranty stock",
            "Allow customer to keep defective unit or provide return label",
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
            "Assess item condition and determine refund percentage",
            "Apply restocking fee if applicable (15% for opened items)",
            "Process partial refund to original payment method",
            "Notify customer of refund amount and timeline",
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
# Helper Functions
# ---------------------------------------------------------------------------

def _days_since_purchase(ret):
    """Calculate days between purchase and return request (simplified)."""
    purchase_parts = ret["purchase_date"].split("-")
    request_parts = ret["request_date"].split("-")
    p_days = int(purchase_parts[0]) * 365 + int(purchase_parts[1]) * 30 + int(purchase_parts[2])
    r_days = int(request_parts[0]) * 365 + int(request_parts[1]) * 30 + int(request_parts[2])
    return r_days - p_days


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

class ReturnsComplaintsResolutionAgent(BasicAgent):
    """Agent for automated returns processing and complaint resolution."""

    def __init__(self):
        self.name = "returns-complaints-resolution-agent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "return_processing",
                            "complaint_classification",
                            "resolution_recommendation",
                            "trend_analysis",
                        ],
                    },
                    "return_id": {"type": "string"},
                    "complaint_text": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def _return_processing(self, **kwargs):
        return_id = kwargs.get("return_id")
        if return_id and return_id in RETURN_REQUESTS:
            returns = {return_id: RETURN_REQUESTS[return_id]}
        else:
            returns = RETURN_REQUESTS
        lines = ["# Return Processing Queue", ""]
        lines.append("| Return ID | Customer | Product | Reason | Condition | Days | Status |")
        lines.append("|-----------|----------|---------|--------|-----------|------|--------|")
        for rid, ret in returns.items():
            days = _days_since_purchase(ret)
            lines.append(
                f"| {rid} | {ret['customer_name']} | {ret['product']} "
                f"| {ret['reason'].replace('_', ' ')} | {ret['condition'].replace('_', ' ')} "
                f"| {days} | {ret['status'].replace('_', ' ')} |"
            )
        lines.append("")
        for rid, ret in returns.items():
            lines.append(f"### {rid} — {ret['product']}")
            lines.append("")
            lines.append(f"- **Order:** {ret['order_id']}")
            lines.append(f"- **Customer:** {ret['customer_name']} (`{ret['customer_id']}`)")
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
        complaint_text = kwargs.get("complaint_text", "")
        lines = ["# Complaint Classification", ""]
        if complaint_text:
            cat_id = _classify_complaint(complaint_text)
            cat = COMPLAINT_CATEGORIES[cat_id]
            lines.append(f"**Input:** \"{complaint_text}\"")
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
        lines = ["# Resolution Recommendations", ""]
        for rid, ret in returns.items():
            rec_id = _recommend_resolution(ret)
            playbook = RESOLUTION_PLAYBOOKS[rec_id]
            lines.append(f"## {rid} — {ret['customer_name']}")
            lines.append("")
            lines.append(f"- **Product:** {ret['product']} (${ret['purchase_price']:.2f})")
            lines.append(f"- **Reason:** {ret['reason'].replace('_', ' ')}")
            lines.append(f"- **Recommended Resolution:** {playbook['label']}")
            lines.append(f"- **Cost Impact:** {playbook['cost_impact']} | **CSAT Impact:** {playbook['csat_impact']}")
            lines.append("")
            lines.append("**Resolution Steps:**")
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
        lines = [
            "# Returns & Complaints Trend Analysis",
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
        lines.append("- Holiday season (Dec) drove a 44% spike in returns, primarily changed-mind returns")
        lines.append("- Wrong-size returns consistently highest — consider enhanced size guide implementation")
        lines.append("- Resolution time improved 8% over the period despite volume increases")
        lines.append("- CSAT recovered to 4.1 after post-holiday dip to 3.6")
        return "\n".join(lines)

    def perform(self, **kwargs):
        operation = kwargs.get("operation", "return_processing")
        dispatch = {
            "return_processing": self._return_processing,
            "complaint_classification": self._complaint_classification,
            "resolution_recommendation": self._resolution_recommendation,
            "trend_analysis": self._trend_analysis,
        }
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
    print("=" * 80)
