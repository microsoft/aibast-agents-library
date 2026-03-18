"""
Product Feedback Synthesizer Agent for Software/Digital Products.

Aggregates and synthesizes customer feedback, feature requests, sentiment
analysis, and roadmap impact assessments for product management teams.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/product-feedback-synthesizer",
    "version": "1.0.0",
    "display_name": "Product Feedback Synthesizer Agent",
    "description": "Aggregates customer feedback, feature requests, sentiment analysis, and roadmap impact assessments for product teams.",
    "author": "AIBAST",
    "tags": ["feedback", "product", "feature-requests", "sentiment", "roadmap", "nps"],
    "category": "software_digital_products",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

FEEDBACK_ENTRIES = {
    "FB-5001": {
        "customer": "Meridian Healthcare Systems",
        "channel": "support_ticket",
        "date": "2026-02-14",
        "category": "usability",
        "sentiment": "negative",
        "score": 2,
        "text": "The dashboard takes too many clicks to get to key metrics. We need a customizable home view.",
        "arr_impact": 186000,
    },
    "FB-5002": {
        "customer": "Apex Financial Group",
        "channel": "nps_survey",
        "date": "2026-02-20",
        "category": "feature_gap",
        "sentiment": "neutral",
        "score": 6,
        "text": "Product is solid but missing real-time alerting capabilities that competitors offer.",
        "arr_impact": 240000,
    },
    "FB-5003": {
        "customer": "Skyline Hospitality Group",
        "channel": "qbr",
        "date": "2026-03-01",
        "category": "praise",
        "sentiment": "positive",
        "score": 9,
        "text": "Integration with our POS system has been seamless. Would love to see mobile app improvements.",
        "arr_impact": 360000,
    },
    "FB-5004": {
        "customer": "Vanguard Logistics",
        "channel": "support_ticket",
        "date": "2026-01-28",
        "category": "bug_report",
        "sentiment": "negative",
        "score": 1,
        "text": "Data export fails consistently for reports over 10K rows. This is blocking our migration.",
        "arr_impact": 84000,
    },
    "FB-5005": {
        "customer": "BrightPath Education",
        "channel": "in_app",
        "date": "2026-03-05",
        "category": "feature_gap",
        "sentiment": "neutral",
        "score": 5,
        "text": "Need role-based access controls for student data. Currently everyone sees everything.",
        "arr_impact": 96000,
    },
    "FB-5006": {
        "customer": "Orion Manufacturing",
        "channel": "sales_call",
        "date": "2026-03-10",
        "category": "feature_gap",
        "sentiment": "positive",
        "score": 8,
        "text": "Great product overall. If you add workflow automation we would double our seat count.",
        "arr_impact": 312000,
    },
}

FEATURE_REQUESTS = {
    "FR-001": {
        "title": "Customizable Dashboard Home View",
        "votes": 87,
        "arr_weight": 612000,
        "status": "under_review",
        "effort": "medium",
        "category": "usability",
        "linked_feedback": ["FB-5001"],
    },
    "FR-002": {
        "title": "Real-Time Alerting Engine",
        "votes": 134,
        "arr_weight": 780000,
        "status": "planned_q3",
        "effort": "high",
        "category": "feature_gap",
        "linked_feedback": ["FB-5002"],
    },
    "FR-003": {
        "title": "Mobile App Enhancements",
        "votes": 62,
        "arr_weight": 420000,
        "status": "in_progress",
        "effort": "medium",
        "category": "usability",
        "linked_feedback": ["FB-5003"],
    },
    "FR-004": {
        "title": "Large Dataset Export Fix",
        "votes": 41,
        "arr_weight": 264000,
        "status": "in_progress",
        "effort": "low",
        "category": "bug_fix",
        "linked_feedback": ["FB-5004"],
    },
    "FR-005": {
        "title": "Role-Based Access Controls (RBAC)",
        "votes": 156,
        "arr_weight": 960000,
        "status": "planned_q2",
        "effort": "high",
        "category": "security",
        "linked_feedback": ["FB-5005"],
    },
    "FR-006": {
        "title": "Workflow Automation Builder",
        "votes": 203,
        "arr_weight": 1140000,
        "status": "planned_q3",
        "effort": "high",
        "category": "feature_gap",
        "linked_feedback": ["FB-5006"],
    },
}

NPS_SCORES = {
    "2025-Q4": {"promoters": 142, "passives": 88, "detractors": 45, "score": 35},
    "2026-Q1": {"promoters": 158, "passives": 91, "detractors": 51, "score": 36},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _feedback_summary():
    by_sentiment = {"positive": 0, "neutral": 0, "negative": 0}
    by_category = {}
    by_channel = {}
    total_arr = 0
    for fb in FEEDBACK_ENTRIES.values():
        by_sentiment[fb["sentiment"]] += 1
        by_category[fb["category"]] = by_category.get(fb["category"], 0) + 1
        by_channel[fb["channel"]] = by_channel.get(fb["channel"], 0) + 1
        total_arr += fb["arr_impact"]
    avg_score = round(sum(fb["score"] for fb in FEEDBACK_ENTRIES.values()) / len(FEEDBACK_ENTRIES), 1)
    return {
        "total_entries": len(FEEDBACK_ENTRIES),
        "by_sentiment": by_sentiment,
        "by_category": by_category,
        "by_channel": by_channel,
        "avg_score": avg_score,
        "total_arr_represented": total_arr,
    }


def _feature_request_ranking():
    ranked = sorted(FEATURE_REQUESTS.values(), key=lambda x: x["arr_weight"], reverse=True)
    return {"requests": ranked, "total_requests": len(ranked)}


def _sentiment_analysis():
    results = []
    for fid, fb in FEEDBACK_ENTRIES.items():
        results.append({
            "id": fid, "customer": fb["customer"], "sentiment": fb["sentiment"],
            "score": fb["score"], "category": fb["category"], "channel": fb["channel"],
            "excerpt": fb["text"][:80],
        })
    pos = sum(1 for r in results if r["sentiment"] == "positive")
    neg = sum(1 for r in results if r["sentiment"] == "negative")
    return {"entries": results, "positive_pct": round(pos / len(results) * 100, 1),
            "negative_pct": round(neg / len(results) * 100, 1), "nps_trend": NPS_SCORES}


def _roadmap_impact():
    impacts = []
    for frid, fr in FEATURE_REQUESTS.items():
        impacts.append({
            "id": frid, "title": fr["title"], "votes": fr["votes"],
            "arr_weight": fr["arr_weight"], "effort": fr["effort"],
            "status": fr["status"], "category": fr["category"],
            "priority_score": round(fr["arr_weight"] / 1000 / (3 if fr["effort"] == "high" else 2 if fr["effort"] == "medium" else 1), 1),
        })
    impacts.sort(key=lambda x: x["priority_score"], reverse=True)
    return {"items": impacts}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class ProductFeedbackSynthesizerAgent(BasicAgent):
    """Product feedback synthesis and roadmap impact agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/product-feedback-synthesizer"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "feedback_summary",
                            "feature_requests",
                            "sentiment_analysis",
                            "roadmap_impact",
                        ],
                        "description": "The feedback operation to perform.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "feedback_summary")
        if op == "feedback_summary":
            return self._feedback_summary()
        elif op == "feature_requests":
            return self._feature_requests()
        elif op == "sentiment_analysis":
            return self._sentiment_analysis()
        elif op == "roadmap_impact":
            return self._roadmap_impact()
        return f"**Error:** Unknown operation `{op}`."

    def _feedback_summary(self) -> str:
        data = _feedback_summary()
        lines = [
            "# Product Feedback Summary",
            "",
            f"**Total Feedback Entries:** {data['total_entries']}",
            f"**Avg Satisfaction Score:** {data['avg_score']}/10",
            f"**ARR Represented:** ${data['total_arr_represented']:,}",
            "",
            "## Sentiment Breakdown",
            "",
            "| Sentiment | Count |",
            "|-----------|-------|",
        ]
        for s, c in data["by_sentiment"].items():
            lines.append(f"| {s.title()} | {c} |")
        lines.append("")
        lines.append("## By Category")
        lines.append("")
        lines.append("| Category | Count |")
        lines.append("|----------|-------|")
        for cat, c in data["by_category"].items():
            lines.append(f"| {cat.replace('_', ' ').title()} | {c} |")
        lines.append("")
        lines.append("## By Channel")
        lines.append("")
        lines.append("| Channel | Count |")
        lines.append("|---------|-------|")
        for ch, c in data["by_channel"].items():
            lines.append(f"| {ch.replace('_', ' ').title()} | {c} |")
        return "\n".join(lines)

    def _feature_requests(self) -> str:
        data = _feature_request_ranking()
        lines = [
            "# Feature Requests (Ranked by ARR Weight)",
            "",
            f"**Total Requests:** {data['total_requests']}",
            "",
            "| Rank | Feature | Votes | ARR Weight | Effort | Status |",
            "|------|---------|-------|-----------|--------|--------|",
        ]
        for i, fr in enumerate(data["requests"], 1):
            lines.append(
                f"| {i} | {fr['title']} | {fr['votes']} | ${fr['arr_weight']:,} "
                f"| {fr['effort'].upper()} | {fr['status']} |"
            )
        return "\n".join(lines)

    def _sentiment_analysis(self) -> str:
        data = _sentiment_analysis()
        lines = [
            "# Sentiment Analysis",
            "",
            f"**Positive:** {data['positive_pct']}% | **Negative:** {data['negative_pct']}%",
            "",
            "## NPS Trend",
            "",
            "| Quarter | Promoters | Passives | Detractors | NPS |",
            "|---------|-----------|----------|------------|-----|",
        ]
        for q, nps in data["nps_trend"].items():
            lines.append(f"| {q} | {nps['promoters']} | {nps['passives']} | {nps['detractors']} | {nps['score']} |")
        lines.append("")
        lines.append("## Recent Feedback")
        lines.append("")
        lines.append("| Customer | Sentiment | Score | Category | Excerpt |")
        lines.append("|----------|-----------|-------|----------|---------|")
        for e in data["entries"]:
            lines.append(
                f"| {e['customer']} | {e['sentiment'].upper()} | {e['score']} "
                f"| {e['category']} | {e['excerpt']}... |"
            )
        return "\n".join(lines)

    def _roadmap_impact(self) -> str:
        data = _roadmap_impact()
        lines = [
            "# Roadmap Impact Assessment",
            "",
            "| Rank | Feature | Priority Score | ARR Weight | Effort | Status |",
            "|------|---------|---------------|-----------|--------|--------|",
        ]
        for i, item in enumerate(data["items"], 1):
            lines.append(
                f"| {i} | {item['title']} | {item['priority_score']} "
                f"| ${item['arr_weight']:,} | {item['effort'].upper()} | {item['status']} |"
            )
        lines.append("")
        lines.append("## Recommendations")
        lines.append("- RBAC and Workflow Automation are highest priority by ARR-weighted scoring.")
        lines.append("- Large Dataset Export fix is quick win with low effort and active churn risk.")
        lines.append("- Real-Time Alerting should be accelerated given competitive pressure.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = ProductFeedbackSynthesizerAgent()
    for op in ["feedback_summary", "feature_requests", "sentiment_analysis", "roadmap_impact"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
