"""
Customer Sentiment & Churn Agent — Financial Services Stack

Analyzes customer sentiment, predicts churn risk, recommends retention
actions, and provides segment-level insights for financial institutions.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/customer-sentiment-churn",
    "version": "1.0.0",
    "display_name": "Customer Sentiment & Churn Agent",
    "description": "Customer sentiment analysis, churn prediction, retention action planning, and segment analytics for financial services.",
    "author": "AIBAST",
    "tags": ["sentiment", "churn", "retention", "NPS", "analytics", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

CUSTOMER_INTERACTIONS = {
    "CUST-8001": {
        "name": "Elizabeth Warren-Hayes",
        "segment": "affluent",
        "tenure_years": 12,
        "products": ["checking", "savings", "mortgage", "investment"],
        "nps_score": 9,
        "last_survey": "2025-02-01",
        "recent_interactions": [
            {"date": "2025-02-15", "channel": "branch", "type": "inquiry", "sentiment": "positive"},
            {"date": "2025-01-20", "channel": "phone", "type": "account_service", "sentiment": "neutral"},
        ],
        "monthly_transactions": 48,
        "digital_engagement_score": 72,
        "complaint_count_12m": 0,
    },
    "CUST-8002": {
        "name": "Marcus Johnson",
        "segment": "mass_market",
        "tenure_years": 3,
        "products": ["checking", "credit_card"],
        "nps_score": 4,
        "last_survey": "2025-01-15",
        "recent_interactions": [
            {"date": "2025-03-01", "channel": "phone", "type": "complaint", "sentiment": "negative"},
            {"date": "2025-02-10", "channel": "chat", "type": "fee_dispute", "sentiment": "negative"},
            {"date": "2025-01-25", "channel": "phone", "type": "complaint", "sentiment": "negative"},
        ],
        "monthly_transactions": 15,
        "digital_engagement_score": 35,
        "complaint_count_12m": 5,
    },
    "CUST-8003": {
        "name": "Priya Sharma",
        "segment": "emerging_affluent",
        "tenure_years": 5,
        "products": ["checking", "savings", "credit_card", "auto_loan"],
        "nps_score": 7,
        "last_survey": "2025-02-20",
        "recent_interactions": [
            {"date": "2025-02-28", "channel": "mobile", "type": "transfer", "sentiment": "neutral"},
            {"date": "2025-02-05", "channel": "email", "type": "inquiry", "sentiment": "positive"},
        ],
        "monthly_transactions": 32,
        "digital_engagement_score": 88,
        "complaint_count_12m": 1,
    },
    "CUST-8004": {
        "name": "Gerald Thompson",
        "segment": "mass_market",
        "tenure_years": 8,
        "products": ["checking"],
        "nps_score": 3,
        "last_survey": "2024-11-01",
        "recent_interactions": [
            {"date": "2024-12-15", "channel": "branch", "type": "withdrawal", "sentiment": "neutral"},
        ],
        "monthly_transactions": 4,
        "digital_engagement_score": 12,
        "complaint_count_12m": 2,
    },
    "CUST-8005": {
        "name": "Diana Castellano",
        "segment": "small_business",
        "tenure_years": 6,
        "products": ["business_checking", "business_credit", "merchant_services"],
        "nps_score": 6,
        "last_survey": "2025-01-10",
        "recent_interactions": [
            {"date": "2025-02-20", "channel": "phone", "type": "fee_dispute", "sentiment": "negative"},
            {"date": "2025-01-30", "channel": "branch", "type": "inquiry", "sentiment": "neutral"},
        ],
        "monthly_transactions": 120,
        "digital_engagement_score": 55,
        "complaint_count_12m": 3,
    },
}

CHURN_INDICATORS = {
    "low_nps": {"threshold": 5, "weight": 25, "description": "NPS score below 5 indicates detractor status"},
    "declining_transactions": {"threshold": 10, "weight": 20, "description": "Monthly transactions below segment average"},
    "high_complaints": {"threshold": 3, "weight": 20, "description": "3+ complaints in last 12 months"},
    "low_engagement": {"threshold": 30, "weight": 15, "description": "Digital engagement score below 30"},
    "single_product": {"threshold": 1, "weight": 10, "description": "Only one active product"},
    "stale_survey": {"threshold": 90, "weight": 10, "description": "Last survey response over 90 days ago"},
}

RETENTION_ACTIONS = {
    "fee_waiver": {"description": "Waive monthly maintenance fees for 6 months", "cost": 72, "success_rate": 45},
    "rate_upgrade": {"description": "Offer premium savings rate for 12 months", "cost": 150, "success_rate": 35},
    "personal_outreach": {"description": "Schedule call with relationship manager", "cost": 25, "success_rate": 55},
    "product_bundle": {"description": "Offer discounted product bundle with waived fees", "cost": 200, "success_rate": 60},
    "loyalty_bonus": {"description": "Credit loyalty bonus to account", "cost": 100, "success_rate": 50},
    "complaint_resolution": {"description": "Escalate to service recovery team", "cost": 50, "success_rate": 65},
}

SEGMENT_BENCHMARKS = {
    "affluent": {"avg_nps": 8.2, "avg_products": 4.1, "avg_tenure": 10, "avg_transactions": 55},
    "emerging_affluent": {"avg_nps": 7.0, "avg_products": 3.2, "avg_tenure": 5, "avg_transactions": 35},
    "mass_market": {"avg_nps": 6.5, "avg_products": 2.0, "avg_tenure": 4, "avg_transactions": 20},
    "small_business": {"avg_nps": 6.8, "avg_products": 3.0, "avg_tenure": 5, "avg_transactions": 90},
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _churn_score(customer):
    """Calculate churn risk score (0-100)."""
    score = 0
    if customer["nps_score"] < CHURN_INDICATORS["low_nps"]["threshold"]:
        score += CHURN_INDICATORS["low_nps"]["weight"]
    if customer["monthly_transactions"] < CHURN_INDICATORS["declining_transactions"]["threshold"]:
        score += CHURN_INDICATORS["declining_transactions"]["weight"]
    if customer["complaint_count_12m"] >= CHURN_INDICATORS["high_complaints"]["threshold"]:
        score += CHURN_INDICATORS["high_complaints"]["weight"]
    if customer["digital_engagement_score"] < CHURN_INDICATORS["low_engagement"]["threshold"]:
        score += CHURN_INDICATORS["low_engagement"]["weight"]
    if len(customer["products"]) <= CHURN_INDICATORS["single_product"]["threshold"]:
        score += CHURN_INDICATORS["single_product"]["weight"]
    return min(100, score)


def _sentiment_breakdown():
    """Compute overall sentiment distribution."""
    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    total = 0
    for cust in CUSTOMER_INTERACTIONS.values():
        for interaction in cust["recent_interactions"]:
            sentiments[interaction["sentiment"]] += 1
            total += 1
    return sentiments, total


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class CustomerSentimentChurnAgent(BasicAgent):
    """Customer sentiment and churn prediction agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/customer-sentiment-churn"
        self.metadata = {
            "name": self.name,
            "display_name": "Customer Sentiment & Churn Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "sentiment_dashboard",
                            "churn_prediction",
                            "retention_actions",
                            "segment_analysis",
                        ],
                    },
                    "customer_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "sentiment_dashboard")
        dispatch = {
            "sentiment_dashboard": self._sentiment_dashboard,
            "churn_prediction": self._churn_prediction,
            "retention_actions": self._retention_actions,
            "segment_analysis": self._segment_analysis,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _sentiment_dashboard(self, **kwargs) -> str:
        sentiments, total = _sentiment_breakdown()
        avg_nps = sum(c["nps_score"] for c in CUSTOMER_INTERACTIONS.values()) / len(CUSTOMER_INTERACTIONS)
        lines = ["# Customer Sentiment Dashboard\n"]
        lines.append(f"**Average NPS:** {avg_nps:.1f}")
        lines.append(f"**Total Interactions Analyzed:** {total}\n")
        lines.append("## Sentiment Distribution\n")
        for sent, count in sentiments.items():
            pct = round((count / total) * 100, 1) if total else 0
            lines.append(f"- **{sent.title()}:** {count} ({pct}%)")
        lines.append("\n## Customer NPS Scores\n")
        lines.append("| Customer | Segment | NPS | Products | Complaints (12m) |")
        lines.append("|---|---|---|---|---|")
        for cid, c in CUSTOMER_INTERACTIONS.items():
            lines.append(
                f"| {c['name']} ({cid}) | {c['segment'].replace('_', ' ').title()} "
                f"| {c['nps_score']} | {len(c['products'])} | {c['complaint_count_12m']} |"
            )
        return "\n".join(lines)

    def _churn_prediction(self, **kwargs) -> str:
        lines = ["# Churn Prediction Report\n"]
        lines.append("| Customer | Segment | Churn Score | NPS | Transactions | Complaints |")
        lines.append("|---|---|---|---|---|---|")
        at_risk = []
        for cid, c in CUSTOMER_INTERACTIONS.items():
            score = _churn_score(c)
            risk = "High" if score >= 50 else "Medium" if score >= 25 else "Low"
            lines.append(
                f"| {c['name']} ({cid}) | {c['segment'].replace('_', ' ').title()} "
                f"| {score} ({risk}) | {c['nps_score']} | {c['monthly_transactions']} | {c['complaint_count_12m']} |"
            )
            if score >= 50:
                at_risk.append((cid, c, score))
        if at_risk:
            lines.append("\n## High-Risk Customers\n")
            for cid, c, score in at_risk:
                lines.append(f"### {c['name']} ({cid}) — Score: {score}\n")
                lines.append(f"- Segment: {c['segment'].replace('_', ' ').title()}")
                lines.append(f"- Tenure: {c['tenure_years']} years")
                lines.append(f"- Products: {', '.join(c['products'])}")
                lines.append(f"- Recent sentiment: {c['recent_interactions'][-1]['sentiment'] if c['recent_interactions'] else 'N/A'}\n")
        lines.append("\n## Churn Indicators Reference\n")
        for ind_id, ind in CHURN_INDICATORS.items():
            lines.append(f"- **{ind_id.replace('_', ' ').title()}** (weight: {ind['weight']}): {ind['description']}")
        return "\n".join(lines)

    def _retention_actions(self, **kwargs) -> str:
        lines = ["# Retention Action Recommendations\n"]
        lines.append("## Available Actions\n")
        lines.append("| Action | Description | Cost | Success Rate |")
        lines.append("|---|---|---|---|")
        for action_id, action in RETENTION_ACTIONS.items():
            lines.append(
                f"| {action_id.replace('_', ' ').title()} | {action['description']} "
                f"| ${action['cost']} | {action['success_rate']}% |"
            )
        lines.append("\n## Recommended Actions by Customer\n")
        for cid, c in CUSTOMER_INTERACTIONS.items():
            score = _churn_score(c)
            if score < 25:
                continue
            lines.append(f"### {c['name']} ({cid}) — Churn Score: {score}\n")
            if c["complaint_count_12m"] >= 3:
                lines.append(f"1. **Complaint Resolution** — {RETENTION_ACTIONS['complaint_resolution']['description']}")
            if c["nps_score"] < 5:
                lines.append(f"2. **Personal Outreach** — {RETENTION_ACTIONS['personal_outreach']['description']}")
            if len(c["products"]) <= 2:
                lines.append(f"3. **Product Bundle** — {RETENTION_ACTIONS['product_bundle']['description']}")
            else:
                lines.append(f"3. **Loyalty Bonus** — {RETENTION_ACTIONS['loyalty_bonus']['description']}")
            lines.append("")
        return "\n".join(lines)

    def _segment_analysis(self, **kwargs) -> str:
        lines = ["# Segment Analysis\n"]
        lines.append("## Segment Benchmarks\n")
        lines.append("| Segment | Avg NPS | Avg Products | Avg Tenure | Avg Transactions |")
        lines.append("|---|---|---|---|---|")
        for seg, bench in SEGMENT_BENCHMARKS.items():
            lines.append(
                f"| {seg.replace('_', ' ').title()} | {bench['avg_nps']} "
                f"| {bench['avg_products']} | {bench['avg_tenure']} yrs | {bench['avg_transactions']}/mo |"
            )
        segments = {}
        for cid, c in CUSTOMER_INTERACTIONS.items():
            seg = c["segment"]
            if seg not in segments:
                segments[seg] = []
            segments[seg].append(c)
        lines.append("\n## Current Customer Performance vs Benchmark\n")
        for seg, customers in segments.items():
            bench = SEGMENT_BENCHMARKS.get(seg, {})
            avg_nps = sum(c["nps_score"] for c in customers) / len(customers)
            avg_products = sum(len(c["products"]) for c in customers) / len(customers)
            lines.append(f"### {seg.replace('_', ' ').title()} ({len(customers)} customers)\n")
            lines.append(f"- NPS: {avg_nps:.1f} (benchmark: {bench.get('avg_nps', 'N/A')})")
            lines.append(f"- Products: {avg_products:.1f} (benchmark: {bench.get('avg_products', 'N/A')})")
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = CustomerSentimentChurnAgent()
    print(agent.perform(operation="sentiment_dashboard"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="churn_prediction"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="retention_actions"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="segment_analysis"))
