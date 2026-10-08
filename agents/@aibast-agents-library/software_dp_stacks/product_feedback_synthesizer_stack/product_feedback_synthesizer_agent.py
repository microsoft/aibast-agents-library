"""
Product Feedback Synthesizer Agent for Software/Digital Products.

Synthesizes last quarter's customer feedback across support tickets, feature
requests and app-store / review-site reviews: the summary, top pain points,
most-requested features, a Q1 priority ranking, the sentiment trend, and
Jira ticket drafts for the top priorities. Everything is review evidence and
drafts; nothing is created in Jira or sent to a team.
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
    "description": "Turn fragmented feedback into actionable insights that accelerate product improvements, prevent churn, and optimize engineering priorities.",
    "author": "AIBAST",
    "tags": ["feedback", "product", "feature-requests", "sentiment", "roadmap", "nps"],
    "category": "software_digital_products",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data — last quarter (Q3)
# ---------------------------------------------------------------------------

QUARTER = "Q3"
PRIOR_QUARTER = "Q2"

FEEDBACK_SOURCES = [
    {"source": "Zendesk Support Tickets", "items": 8500},
    {"source": "Jira Feature Requests", "items": 1200},
    {"source": "App Store Reviews", "items": 280},
    {"source": "G2 Reviews", "items": 170},
]

SENTIMENT_COUNTS = {"positive": 6293, "neutral": 2335, "negative": 1522}

SENTIMENT_TREND = {
    "Q2": {"positive_pct": 56.1, "neutral_pct": 23.0, "negative_pct": 20.9, "score": 6.8},
    "Q3": {"positive_pct": 62.0, "neutral_pct": 23.0, "negative_pct": 15.0, "score": 7.2},
}

PAIN_POINTS = [
    {"rank": 1, "title": "Performance & Load Times", "share_pct": 27,
     "symptoms": ["Slow page loads during peak hours (especially dashboard & reporting screens)",
                  "Notable on mobile devices and in regions with weaker network infrastructure"],
     "impact": "Frustration -> decreased daily active usage",
     "recommendation": "Optimize database queries, enable CDN edge caching for heavy static content."},
    {"rank": 2, "title": "Integration Reliability", "share_pct": 22,
     "symptoms": ["Frequent sync failures with third-party CRMs (Salesforce & Dynamics)",
                  "Error handling isn't informative, causing repeated support calls"],
     "impact": "Data inconsistency and repeat support contacts",
     "recommendation": "Implement retry logic, API health checks, and clearer error messages."},
    {"rank": 3, "title": "Mobile App Stability", "share_pct": 18,
     "symptoms": ["App crashes on Android 13 reported after latest update",
                  "iOS users seeing session/logout issues when switching between apps"],
     "impact": "Lower mobile engagement",
     "recommendation": "Add regression test suite for critical mobile flows, hotfix crash bugs."},
    {"rank": 4, "title": "Search Accuracy & Filters", "share_pct": 15,
     "symptoms": ["Global search returning incomplete or irrelevant results",
                  "Filters not persisting between sessions"],
     "impact": "Time lost re-running searches",
     "recommendation": "Expand search index fields, store filter states per user profile."},
    {"rank": 5, "title": "Onboarding Complexity", "share_pct": 12,
     "symptoms": ["New users find setup overwhelming, requiring multiple support interactions",
                  "Confusion over required vs. optional fields during initial configuration"],
     "impact": "Slower time to value for new accounts",
     "recommendation": "Create quick-start templates and guided walkthroughs."},
]

AT_RISK_SIGNALS = [
    "Churn risk: enterprise accounts citing CRM sync failures (Integration Reliability, 22% of complaints)",
    "Competitive gap: reporting depth versus competitors (Advanced Reporting, 31% of feature requests)",
]

FEATURE_REQUESTS = {
    "FR-001": {"title": "Advanced Reporting & Analytics", "share_pct": 31, "status": "candidate_for_review",
               "themes": ["Customizable dashboards", "Export to Excel/CSV with full data set",
                          "Scheduled email reports with filters applied"],
               "impact": "Strong demand from enterprise accounts"},
    "FR-002": {"title": "Expanded Integrations", "share_pct": 24, "status": "candidate_for_review",
               "themes": ["Priority targets: Slack, Microsoft Teams, HubSpot CRM",
                          "Webhooks for custom workflow automation"],
               "impact": "Would reduce manual data handoffs"},
    "FR-003": {"title": "Offline Mode", "share_pct": 18, "status": "under_review",
               "themes": ["Ability to view and edit data without internet",
                          "Sync changes automatically when reconnected"],
               "impact": "Field service and mobile-heavy teams are the main drivers"},
    "FR-004": {"title": "Role-Based Access Control (RBAC)", "share_pct": 14, "status": "under_review",
               "themes": ["Granular permissions by job function", "Audit logs for compliance"],
               "impact": "Critical for regulated industries (finance, healthcare)"},
    "FR-005": {"title": "In-App Training & Help", "share_pct": 9, "status": "evidence_under_review",
               "themes": ["Guided tours for new features", "Contextual \"how-to\" tips"],
               "impact": "Cuts onboarding friction and reduces support dependency"},
}

PRIORITY_RANKING = [
    {"rank": 1, "priority": "P0", "title": "Performance & Load Time Optimization",
     "evidence": "Pain Point: Slow page loads (27% of complaints)",
     "business_impact": "High - directly affects all users, impacts engagement & churn risk",
     "effort": "Medium",
     "verdict": "Tackle Immediately - improves retention, NPS, and supports all incoming features",
     "ticket_summary": "Optimize dashboard and reporting load times across all platforms.",
     "ticket_description": ["Investigate slow load times during peak usage, focusing on dashboard & reporting modules.",
                            "Implement database query optimizations and edge CDN caching for heavy static assets.",
                            "Target mobile devices and low-bandwidth regions."],
     "labels": ["performance", "optimization", "Q1"]},
    {"rank": 2, "priority": "P0", "title": "Integration Reliability Fix",
     "evidence": "Pain Point/Request: Sync failures with CRMs (22%) + demand for new integrations (24%)",
     "business_impact": "Very High - enterprise customers, prevents data inconsistency & lost sales signals",
     "effort": "Medium-High (API resilience + partner onboarding)",
     "verdict": "High ROI - stabilizing integrations sets groundwork for requested connectors (Slack, Teams, HubSpot)",
     "ticket_summary": "Resolve CRM sync failures and improve API resilience.",
     "ticket_description": ["Address sync failure patterns with Salesforce and Dynamics.",
                            "Add retry logic, API health checks, and clearer error messaging.",
                            "Lay foundation for upcoming Slack, Teams, and HubSpot integrations."],
     "labels": ["integrations", "reliability", "Q1"]},
    {"rank": 3, "priority": "P1", "title": "Advanced Reporting & Analytics",
     "evidence": "Request: Custom dashboards, exports, scheduling (31% of feature requests)",
     "business_impact": "High - drives upsells to enterprise tier, differentiator in competitive landscape",
     "effort": "Medium",
     "verdict": "Strategic Move - positions product as analytical hub",
     "ticket_summary": "Implement customizable dashboards with export and scheduling options.",
     "ticket_description": ["Build dashboard customization tools per user role.",
                            "Add full-data Excel/CSV export.",
                            "Add scheduled email reports with saved filters."],
     "labels": ["reporting", "analytics", "Q1"]},
    {"rank": 4, "priority": "P2", "title": "Mobile App Stability & Offline Mode",
     "evidence": "Pain Point + Request: Crashes (18%) + offline capability (18%)",
     "business_impact": "Medium-High - critical for field teams; improves mobile engagement",
     "effort": "High (offline sync logic)",
     "verdict": "Bundle Fix + Feature - improves reliability AND adds high-value capability in one release",
     "ticket_summary": "", "ticket_description": [], "labels": []},
    {"rank": 5, "priority": "P2", "title": "Role-Based Access Control (RBAC)",
     "evidence": "Request: Granular permissions + audit logs (14%)",
     "business_impact": "Medium - important for compliance-heavy industries, opens regulated market segments",
     "effort": "Medium-High",
     "verdict": "Schedule after mobile/offline unless targeting finance/healthcare immediately",
     "ticket_summary": "", "ticket_description": [], "labels": []},
]

FEEDBACK_ENTRIES = {
    "FB-5001": {"customer": "Meridian Healthcare Systems", "source": "Zendesk Support Tickets", "sentiment": "negative",
                "text": "Dashboards crawl every morning at peak; reporting screens take 20+ seconds to load.",
                "pain_point": "Performance & Load Times"},
    "FB-5002": {"customer": "Apex Financial Group", "source": "Zendesk Support Tickets", "sentiment": "negative",
                "text": "CRM sync failed again overnight and the error message tells us nothing.",
                "pain_point": "Integration Reliability"},
    "FB-5003": {"customer": "Skyline Hospitality Group", "source": "App Store Reviews", "sentiment": "negative",
                "text": "Since the last update the Android app crashes when I open a record.",
                "pain_point": "Mobile App Stability"},
    "FB-5004": {"customer": "Vanguard Logistics", "source": "G2 Reviews", "sentiment": "neutral",
                "text": "Search misses records and my filters reset every time I log in.",
                "pain_point": "Search Accuracy & Filters"},
    "FB-5005": {"customer": "BrightPath Education", "source": "Zendesk Support Tickets", "sentiment": "neutral",
                "text": "Setup took three support calls; unclear which fields are required.",
                "pain_point": "Onboarding Complexity"},
    "FB-5006": {"customer": "Orion Manufacturing", "source": "Jira Feature Requests", "sentiment": "positive",
                "text": "Love the product since the stability fixes. Scheduled reports would make it perfect.",
                "pain_point": ""},
}

TEAMS_NOTIFICATION_DRAFT = (
    "Heads-up engineering: three Q1 ticket drafts from last quarter's feedback synthesis are ready for review - "
    "two P0 (Performance & Load Time Optimization, Integration Reliability Fix) and one P1 (Advanced Reporting & "
    "Analytics). Please review scope and estimates before sprint planning."
)

_PRODUCT_GATE = (
    "Synthetic insight only. No roadmap commitment, Jira ticket, customer "
    "outreach, or account action is created; product owners must validate the evidence."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _total_items():
    return sum(s["items"] for s in FEEDBACK_SOURCES)


def _pct(part, whole):
    return round(part * 100 / whole, 1)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "feedback_summary",
    "feature_requests",
    "sentiment_analysis",
    "roadmap_impact",
    "pain_points",
    "draft_jira_tickets",
]


class ProductFeedbackSynthesizerAgent(BasicAgent):
    """Product feedback synthesis and roadmap impact agent."""

    def __init__(self):
        self.name = "ProductFeedbackSynthesizerAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                f"{__manifest__['description']} Synthesize only fictional pilot "
                "feedback and provide non-binding review candidates; never commit "
                "a roadmap, create an engineering ticket, or contact a customer. Always use this tool for "
                "last quarter's product feedback. A product manager walks the operations in order: analyze "
                "feedback -> feedback_summary; top pain points -> pain_points; most-requested features -> "
                "feature_requests; prioritization / Q1 priority matrix -> roadmap_impact; sentiment trend over "
                "time -> sentiment_analysis; create Jira tickets for P0/P1 items and notify engineering -> "
                "draft_jira_tickets (returns ticket drafts and a draft team message; nothing is created or sent)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "feedback_summary: analyze last quarter's feedback (sources, volume, sentiment). "
                            "pain_points: top customer pain points with recommendations and churn / competitive "
                            "signals. feature_requests: features customers request most. roadmap_impact: Q1 "
                            "priority ranking by impact vs effort. sentiment_analysis: sentiment trend Q2 -> Q3. "
                            "draft_jira_tickets: Jira ticket drafts for the P0 and P1 items plus a draft "
                            "engineering notification."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "feedback_summary")
        dispatch = {
            "feedback_summary": self._feedback_summary,
            "feature_requests": self._feature_requests,
            "sentiment_analysis": self._sentiment_analysis,
            "roadmap_impact": self._roadmap_impact,
            "pain_points": self._pain_points,
            "draft_jira_tickets": self._draft_jira_tickets,
        }
        handler = dispatch.get(op)
        if handler is None:
            return f"**Error:** Unknown operation `{op}`."
        return handler()

    def _feedback_summary(self) -> str:
        total = _total_items()
        now, prev = SENTIMENT_TREND[QUARTER], SENTIMENT_TREND[PRIOR_QUARTER]
        lines = [
            f"# Feedback Analysis Complete ({QUARTER}, last quarter)",
            "",
            "| Metric | Value |",
            "|---|---|",
            f"| Total Feedback Items | {total:,} analyzed |",
        ]
        for s in FEEDBACK_SOURCES:
            lines.append(f"| {s['source']} | {s['items']:,} ({_pct(s['items'], total)}%) |")
        lines.append(f"| Overall Sentiment Score | {now['score']}/10 (up from {prev['score']} in {PRIOR_QUARTER}) |")
        lines += ["", "## Sentiment Breakdown", "", "| Sentiment | Count | Percentage | Trend |", "|---|---|---|---|"]
        for key in ["positive", "neutral", "negative"]:
            count = SENTIMENT_COUNTS[key]
            delta = round(now[f"{key}_pct"] - prev[f"{key}_pct"], 1)
            trend = "Stable" if delta == 0 else f"{delta:+g} pts vs {PRIOR_QUARTER}"
            lines.append(f"| {key.title()} | {count:,} items | {round(_pct(count, total))}% | {trend} |")
        lines += [
            "",
            "**Key Finding:** Overall sentiment is improving despite some technical pain points.",
            "",
            "Next: drill into the specific pain points and feature requests to build the prioritized roadmap.",
            "",
            f"**Review gate:** {_PRODUCT_GATE}",
        ]
        return "\n".join(lines)

    def _pain_points(self) -> str:
        lines = ["# Top Customer Pain Points", ""]
        for p in PAIN_POINTS:
            lines.append(f"**{p['rank']}. {p['title']} ({p['share_pct']}%)**")
            for s in p["symptoms"]:
                lines.append(f"- {s}")
            lines.append(f"- Impact: {p['impact']}")
            lines.append(f"- Recommendation: {p['recommendation']}")
            verbatim = [f for f in FEEDBACK_ENTRIES.values() if f["pain_point"] == p["title"]]
            if verbatim:
                lines.append(f"- Sample verbatim ({verbatim[0]['source']}): \"{verbatim[0]['text']}\"")
            lines.append("")
        lines.append("**At-risk signals for team alerts:**")
        for s in AT_RISK_SIGNALS:
            lines.append(f"- {s}")
        lines += [
            "",
            "**Overall Insight:** These pain points link heavily to speed, reliability, and ease-of-use - fixing the "
            "top three would improve sentiment and retention significantly.",
            "",
            "Next: map these pain points to revenue impact to rank which fixes give the highest ROI next quarter?",
            "",
            f"**Review gate:** {_PRODUCT_GATE}",
        ]
        return "\n".join(lines)

    def _feature_requests(self) -> str:
        jira = next(s["items"] for s in FEEDBACK_SOURCES if s["source"] == "Jira Feature Requests")
        lines = ["# Top Requested Features", ""]
        for i, (frid, fr) in enumerate(FEATURE_REQUESTS.items(), 1):
            votes = jira * fr["share_pct"] // 100
            lines.append(f"**{i}. {fr['title']} ({fr['share_pct']}%)** - `{frid}`, ~{votes:,} requests, {fr['status']}")
            for t in fr["themes"]:
                lines.append(f"- {t}")
            lines.append(f"- Impact: {fr['impact']}")
            lines.append("")
        lines += [
            "**Trend:** The requests largely center around empowering teams via better data visibility, smoother "
            "collaboration, and mobile reliability.",
            "",
            "Next: combine these feature requests with the pain point data into a Q1 prioritization matrix "
            "(effort vs. impact)?",
            "",
            f"**Review gate:** {_PRODUCT_GATE}",
        ]
        return "\n".join(lines)

    def _roadmap_impact(self) -> str:
        lines = ["# Q1 Priority Ranking (Highest Business Impact First)", ""]
        for item in PRIORITY_RANKING:
            lines.append(f"**{item['rank']}. {item['title']}** ({item['priority']})")
            lines.append(f"- {item['evidence']}")
            lines.append(f"- Business Impact: {item['business_impact']}")
            lines.append(f"- Effort Estimate: {item['effort']}")
            lines.append(f"- {item['verdict']}")
            lines.append("")
        lines.append("**Recommended sequence for maximum Q1 impact:** "
                     + " -> ".join(i["title"] for i in PRIORITY_RANKING))
        lines += [
            "",
            "## Review Candidates",
            "- Validate the P0 items (Performance, Integration Reliability) with engineering capacity before sprint planning.",
            "- Confirm the P1 Advanced Reporting scope with enterprise customers.",
            "- Schedule RBAC after Mobile + Offline unless targeting finance/healthcare immediately.",
            "",
            "Next: layer in projected revenue uplift for each item?",
            "",
            f"**Review gate:** {_PRODUCT_GATE}",
        ]
        return "\n".join(lines)

    def _sentiment_analysis(self) -> str:
        prev, now = SENTIMENT_TREND[PRIOR_QUARTER], SENTIMENT_TREND[QUARTER]
        pos_delta = round(now["positive_pct"] - prev["positive_pct"], 1)
        neg_delta = round(prev["negative_pct"] - now["negative_pct"], 1)
        lines = [
            "# Sentiment Trend Analysis",
            "",
            "| Quarter | Positive | Neutral | Negative | Score |",
            "|---|---|---|---|---|",
        ]
        for q in [PRIOR_QUARTER, QUARTER]:
            t = SENTIMENT_TREND[q]
            lines.append(f"| {q} | {t['positive_pct']:g}% | {t['neutral_pct']:g}% | {t['negative_pct']:g}% | {t['score']} |")
        lines += [
            "",
            "**Trend Insights:**",
            f"- Positive feedback grew by +{pos_delta:g} percentage points quarter-over-quarter.",
            f"- Negative feedback dropped {neg_delta:g} points, showing a clear improvement in customer experience.",
            "- Neutral sentiment stayed stable.",
            f"- The sentiment score rose from {prev['score']} to {now['score']}, mostly driven by product stability "
            "patches and faster support resolution times.",
            "",
            "**Overall Direction:** Improving, with the strongest gains among enterprise customers after recent bug fixes.",
            "",
            "Next: forecast Q4 sentiment assuming the top two pain points are addressed immediately?",
            "",
            "All feedback figures and account names are fictional pilot data.",
            f"**Review gate:** {_PRODUCT_GATE}",
        ]
        return "\n".join(lines)

    def _draft_jira_tickets(self) -> str:
        lines = ["# Jira Ticket Drafts (Not Created)", ""]
        drafts = [i for i in PRIORITY_RANKING if i["priority"] in ("P0", "P1")]
        for item in drafts:
            critical = " (Critical)" if item["priority"] == "P0" else " (High)"
            lines.append(f"**{item['priority']}: {item['title']}**")
            lines.append(f"- Summary: {item['ticket_summary']}")
            lines.append("- Description:")
            for d in item["ticket_description"]:
                lines.append(f"  - {d}")
            lines.append(f"- Priority: {item['priority']}{critical}")
            lines.append(f"- Labels: {', '.join(item['labels'])}")
            lines.append("")
        lines += [
            "**Draft engineering notification (Teams):**",
            f"> {TEAMS_NOTIFICATION_DRAFT}",
            "",
            f"{len(drafts)} ticket drafts ready for you to create in Jira and a message ready for you to post; "
            "no Jira ticket was created and no message was sent.",
            "",
            f"**Review gate:** {_PRODUCT_GATE}",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = ProductFeedbackSynthesizerAgent()
    for op in ["feedback_summary", "pain_points", "feature_requests", "roadmap_impact",
               "sentiment_analysis", "draft_jira_tickets"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
