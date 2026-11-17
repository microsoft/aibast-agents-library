"""
Customer Sentiment & Churn Agent — Financial Services Stack

Analyzes customer sentiment, predicts churn risk, recommends retention
actions, and provides segment-level insights for financial institutions.

Demo scenario (synthetic): a regional bank with 180K customers. The agent
summarizes portfolio sentiment and churn-risk tiers, lists the early-warning
signals, profiles the five highest-value at-risk customers (led by Robert
Martinez), drafts a retention strategy per customer, and proposes an outreach
assignment and tracking plan for the manager to confirm. Nothing is sent,
offered or scheduled by the agent.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/customer-sentiment-churn",
    "version": "1.1.0",
    "display_name": "Customer Sentiment and Churn Prediction Agent",
    "description": "Deliver AI-powered sentiment intelligence that detects churn risk early and enables proactive retention strategies.",
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

DEMO_AS_OF = "2025-03-15"

# Portfolio-level sentiment and churn-model summary (180K customers)
PORTFOLIO_SUMMARY = {
    "customers": 180000,
    "sentiment": {"Promoters": 72000, "Passives": 81000, "Detractors": 27000},
    "risk_tiers": [
        {"tier": "Critical (>80%)", "customers": 840, "annual_revenue": 2800000},
        {"tier": "High (60-80%)", "customers": 1560, "annual_revenue": 5400000},
    ],
    "negative_drivers": [
        {"driver": "Digital banking", "mentions": 2400},
        {"driver": "Fee transparency", "mentions": 1800},
        {"driver": "Wait times", "mentions": 1200},
    ],
    "negative_trend_pct": 18,
}

EARLY_WARNING = {
    "lead_time": "30-60 days before leaving",
    "signals": [
        {"signal": "Reduced logins", "customers": 3400, "churn_rate_pct": 72},
        {"signal": "Competitor app download", "customers": 1200, "churn_rate_pct": 68},
        {"signal": "Direct deposit change", "customers": 890, "churn_rate_pct": 78},
        {"signal": "Balance decline >30%", "customers": 2100, "churn_rate_pct": 54},
    ],
    "combinations": [
        {"combination": "Competitor app + balance decline", "churn_rate_pct": 89},
        {"combination": "Deposit change + reduced logins", "churn_rate_pct": 82},
        {"combination": "2+ complaints", "churn_rate_pct": 67},
    ],
    "alerts_today": [
        {"customers": 47, "alert": "Competitor app detected"},
        {"customers": 23, "alert": "External transfers >$10K"},
        {"customers": 12, "alert": "Direct deposit changed"},
    ],
}

# The five highest-value at-risk customers (fictional), kept in priority order by annual revenue
CUSTOMER_INTERACTIONS = {
    "CUST-8001": {
        "name": "Robert Martinez",
        "segment": "affluent",
        "tenure_years": 12,
        "products": ["checking", "savings", "investment"],
        "deposits": 890000,
        "annual_revenue": 12000,
        "churn_probability_pct": 84,
        "behavior_signals": ["Competitor app download (Summit National Bank)", "Reduced logins"],
        "primary_signal": "competitor app",
        "nps_score": 4,
        "last_survey": "2025-02-01",
        "survey_verbatim": "Your app is years behind",
        "recent_contact": "Asked about wire fees",
        "recent_interactions": [
            {"date": "2025-03-05", "channel": "phone", "type": "fee_inquiry", "sentiment": "negative"},
            {"date": "2025-02-01", "channel": "survey", "type": "feedback", "sentiment": "negative"},
        ],
        "monthly_transactions": 22,
        "digital_engagement_score": 28,
        "complaint_count_12m": 1,
    },
    "CUST-8003": {
        "name": "Sarah Thompson",
        "segment": "affluent",
        "tenure_years": 9,
        "products": ["checking", "savings", "mortgage"],
        "deposits": 450000,
        "annual_revenue": 8000,
        "churn_probability_pct": 78,
        "behavior_signals": ["Direct deposit changed", "Rate comparison visits"],
        "primary_signal": "deposit changed",
        "nps_score": 6,
        "last_survey": "2024-11-20",
        "survey_verbatim": "Savings rate is not competitive",
        "recent_contact": "Asked about CD rates",
        "recent_interactions": [
            {"date": "2025-03-02", "channel": "branch", "type": "rate_inquiry", "sentiment": "neutral"},
            {"date": "2025-02-18", "channel": "mobile", "type": "deposit_change", "sentiment": "neutral"},
        ],
        "monthly_transactions": 18,
        "digital_engagement_score": 61,
        "complaint_count_12m": 0,
    },
    "CUST-8004": {
        "name": "James Lee",
        "segment": "emerging_affluent",
        "tenure_years": 6,
        "products": ["checking", "savings", "auto_loan"],
        "deposits": 340000,
        "annual_revenue": 6000,
        "churn_probability_pct": 76,
        "behavior_signals": ["3 complaints in 90 days", "Balance decline >30%"],
        "primary_signal": "3 complaints",
        "nps_score": 3,
        "last_survey": "2025-02-25",
        "survey_verbatim": "Nobody follows up on my issues",
        "recent_contact": "Third complaint about a delayed transfer",
        "recent_interactions": [
            {"date": "2025-03-08", "channel": "phone", "type": "complaint", "sentiment": "negative"},
            {"date": "2025-02-20", "channel": "branch", "type": "complaint", "sentiment": "negative"},
            {"date": "2025-01-30", "channel": "chat", "type": "complaint", "sentiment": "negative"},
        ],
        "monthly_transactions": 14,
        "digital_engagement_score": 44,
        "complaint_count_12m": 3,
    },
    "CUST-8002": {
        "name": "Marcus Johnson",
        "segment": "mass_market",
        "tenure_years": 3,
        "products": ["checking", "credit_card"],
        "deposits": 280000,
        "annual_revenue": 5000,
        "churn_probability_pct": 64,
        "behavior_signals": ["Fee disputes", "Repeated complaints"],
        "primary_signal": "5 complaints",
        "nps_score": 4,
        "last_survey": "2025-01-15",
        "survey_verbatim": "Too many surprise fees",
        "recent_contact": "Fee dispute in chat",
        "recent_interactions": [
            {"date": "2025-03-01", "channel": "phone", "type": "complaint", "sentiment": "negative"},
            {"date": "2025-02-10", "channel": "chat", "type": "fee_dispute", "sentiment": "negative"},
            {"date": "2025-01-25", "channel": "phone", "type": "complaint", "sentiment": "negative"},
        ],
        "monthly_transactions": 15,
        "digital_engagement_score": 35,
        "complaint_count_12m": 5,
    },
    "CUST-8005": {
        "name": "Priya Sharma",
        "segment": "emerging_affluent",
        "tenure_years": 5,
        "products": ["checking", "savings", "credit_card"],
        "deposits": 220000,
        "annual_revenue": 4000,
        "churn_probability_pct": 62,
        "behavior_signals": ["Reduced logins", "Competitor app download (Summit National Bank)"],
        "primary_signal": "reduced logins",
        "nps_score": 7,
        "last_survey": "2025-02-20",
        "survey_verbatim": "Mobile deposits keep failing",
        "recent_contact": "Mobile check deposit issue",
        "recent_interactions": [
            {"date": "2025-02-28", "channel": "mobile", "type": "transfer", "sentiment": "neutral"},
            {"date": "2025-02-05", "channel": "email", "type": "inquiry", "sentiment": "negative"},
        ],
        "monthly_transactions": 30,
        "digital_engagement_score": 52,
        "complaint_count_12m": 1,
    },
}

REPLACEMENT_COST = {"top5_if_lost": 16000}

# Per-customer retention strategy and proposed outreach owner (drafts for manager approval)
RETENTION_STRATEGIES = {
    "CUST-8001": {
        "strategy": "Tech preview + fee waiver",
        "approach": "VP-level personal call",
        "message": "We heard your app feedback",
        "offer": "Private beta access to the new mobile app",
        "incentive": "Waive fees 12 months",
        "incentive_value": 480,
        "urgency": "Within 24 hours",
        "success_pct": 72,
        "owner": "VP Chen",
        "channel": "Phone",
        "due": "Today 2 PM",
        "talk_track": (
            "Mr. Martinez, valued clients like you deserve our best. I saw your app feedback - I'd like you "
            "to be among the first to try our completely redesigned app."
        ),
    },
    "CUST-8003": {
        "strategy": "Rate match + review",
        "approach": "Relationship review with senior RM",
        "message": "Let's make sure your savings work as hard as you do",
        "offer": "Premium savings rate review",
        "incentive": "Premium rate for 12 months",
        "incentive_value": 150,
        "urgency": "Within 48 hours",
        "success_pct": 65,
        "owner": "Sr. RM Johnson",
        "channel": "Video call",
        "due": "Tomorrow",
        "talk_track": "Ms. Thompson, I'd like to review your savings and deposit setup with you this week.",
    },
    "CUST-8004": {
        "strategy": "Service recovery",
        "approach": "In-person service recovery meeting",
        "message": "We let you down and we will fix it",
        "offer": "Dedicated relationship manager",
        "incentive": "Service recovery escalation",
        "incentive_value": 50,
        "urgency": "Within 48 hours",
        "success_pct": 70,
        "owner": "Sr. RM Williams",
        "channel": "In-person",
        "due": "Tomorrow",
        "talk_track": "Mr. Lee, I'm your dedicated contact from today, and I'll personally close out your open issues.",
    },
    "CUST-8002": {
        "strategy": "Fee review + service recovery",
        "approach": "Relationship manager call",
        "message": "We reviewed your fees and complaints",
        "offer": "Complaint resolution with a fee review",
        "incentive": "Waive monthly maintenance fees for 6 months",
        "incentive_value": 72,
        "urgency": "Within 3 days",
        "success_pct": 55,
        "owner": "RM Patel",
        "channel": "Phone",
        "due": "Day 3",
        "talk_track": "Mr. Johnson, I reviewed your recent fee disputes and want to walk you through what we can fix.",
    },
    "CUST-8005": {
        "strategy": "Digital rescue",
        "approach": "Mobile app support session",
        "message": "Let's fix mobile deposits for you",
        "offer": "Guided setup of the new mobile app",
        "incentive": "Discounted product bundle with waived fees",
        "incentive_value": 200,
        "urgency": "Within 3 days",
        "success_pct": 60,
        "owner": "RM Garcia",
        "channel": "Phone + email",
        "due": "Day 3",
        "talk_track": "Ms. Sharma, I'd like to help you get mobile deposits working the way they should.",
    },
}

OUTREACH_TRACKING = {
    "tracking": [
        "Contact attempts: real-time",
        "Outcomes: RM updates",
        "Offer acceptance: immediate",
        "Account activity: 30-day monitoring",
    ],
    "escalations": [
        "No contact in 48 hours -> alert manager",
        "Declines offer -> escalate to VP",
        "Balance withdrawal -> immediate notification",
    ],
}

CHURN_INDICATORS = {
    "low_nps": {"threshold": 5, "weight": 25, "description": "NPS score below 5 indicates detractor status"},
    "declining_transactions": {"threshold": 0.5, "weight": 20, "description": "Monthly transactions below half of the segment average"},
    "high_complaints": {"threshold": 3, "weight": 20, "description": "3+ complaints in last 12 months"},
    "low_engagement": {"threshold": 30, "weight": 15, "description": "Digital engagement score below 30"},
    "single_product": {"threshold": 1, "weight": 10, "description": "Only one active product"},
    "stale_survey": {"threshold": 90, "weight": 10, "description": "Last survey response over 90 days before the demo date"},
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


SYNTHETIC_NOTICE = (
    "> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. "
    "Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, "
    "or account action has occurred.\n\n"
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _days_since(date_text):
    import datetime
    return (datetime.date.fromisoformat(DEMO_AS_OF) - datetime.date.fromisoformat(date_text)).days


def _churn_score(customer):
    """Rule-based review score (0-100) that explains the churn-model probability."""
    score = 0
    bench = SEGMENT_BENCHMARKS.get(customer["segment"], {"avg_transactions": 20})
    if customer["nps_score"] < CHURN_INDICATORS["low_nps"]["threshold"]:
        score += CHURN_INDICATORS["low_nps"]["weight"]
    if customer["monthly_transactions"] < bench["avg_transactions"] * CHURN_INDICATORS["declining_transactions"]["threshold"]:
        score += CHURN_INDICATORS["declining_transactions"]["weight"]
    if customer["complaint_count_12m"] >= CHURN_INDICATORS["high_complaints"]["threshold"]:
        score += CHURN_INDICATORS["high_complaints"]["weight"]
    if customer["digital_engagement_score"] < CHURN_INDICATORS["low_engagement"]["threshold"]:
        score += CHURN_INDICATORS["low_engagement"]["weight"]
    if len(customer["products"]) <= CHURN_INDICATORS["single_product"]["threshold"]:
        score += CHURN_INDICATORS["single_product"]["weight"]
    if _days_since(customer["last_survey"]) > CHURN_INDICATORS["stale_survey"]["threshold"]:
        score += CHURN_INDICATORS["stale_survey"]["weight"]
    return min(100, score)


def _risk_tier(probability):
    if probability > 80:
        return "critical"
    if probability >= 60:
        return "high"
    return "moderate"


def _ranked_customers():
    """At-risk customers in priority order (the records are kept ranked by annual revenue, highest first)."""
    return list(CUSTOMER_INTERACTIONS.items())


def _money_k(value):
    if value >= 1000000:
        return f"${value / 1000000:.2f}M".replace("0M", "M")
    return f"${value / 1000:g}K"


def _short_name(name):
    first, last = name.split(" ", 1)
    return f"{first[0]}. {last}"


def _sentiment_breakdown():
    """Compute the sample's interaction sentiment distribution."""
    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    total = 0
    for cust in CUSTOMER_INTERACTIONS.values():
        for interaction in cust["recent_interactions"]:
            sentiments[interaction["sentiment"]] += 1
            total += 1
    return sentiments, total


def _resolve_customer(query):
    """Customer ID or a (part of a) name; None when nothing matches (never another person)."""
    q = str(query).strip()
    if q in CUSTOMER_INTERACTIONS:
        return q
    q = q.lower()
    for cid, c in CUSTOMER_INTERACTIONS.items():
        if q and (q in c["name"].lower() or c["name"].lower() in q):
            return cid
    return None


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class CustomerSentimentChurnAgent(BasicAgent):
    """Customer sentiment and churn prediction agent."""

    def __init__(self):
        self.name = "CustomerSentimentChurnAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Customer Sentiment & Churn Agent",
            "description": (
                "Always call this tool for relationship-manager, retention, or customer-success requests "
                "about customer sentiment across the banking portfolio, accounts at highest churn risk, "
                "early warning signals, profiles of the highest-value at-risk customers, retention "
                "strategies for each customer or for a named customer such as Marcus before contact or a "
                "fee change, assigning outreach and tracking, or which segment is below benchmark. Every "
                "operation has demo defaults, so call it right away. Do not answer those requests from "
                "general knowledge. Uses fictional records only, does not infer protected traits, and "
                "never contacts a customer, changes fees, makes an offer, or takes account action without "
                "authorized human review."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Choose sentiment_dashboard to analyze customer sentiment across the banking "
                            "portfolio, NPS, negative drivers, or which accounts are at highest churn risk. "
                            "Choose early_warning_signals for the early warning signals to watch for. Choose "
                            "churn_prediction for profiles of the highest-value at-risk customers, who to "
                            "review first, or the evidence behind a churn score. Choose retention_actions for "
                            "retention strategies for each customer, or to prepare options for Marcus or "
                            "another customer before outreach, offers, or fee changes. Choose outreach_plan "
                            "to assign the outreach and set up tracking. Choose segment_analysis for segment "
                            "benchmarks or which segment is under its experience benchmark."
                        ),
                        "enum": [
                            "sentiment_dashboard",
                            "churn_prediction",
                            "retention_actions",
                            "segment_analysis",
                            "early_warning_signals",
                            "outreach_plan",
                        ],
                    },
                    "customer_id": {
                        "type": "string",
                        "description": (
                            "Synthetic customer mapping: Robert Martinez is CUST-8001; Marcus Johnson or "
                            "Marcus is CUST-8002; Sarah Thompson is CUST-8003; James Lee is CUST-8004; Priya "
                            "Sharma is CUST-8005. Omit for portfolio-wide reports and the top-5 views."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        record_id = kwargs.get("customer_id")
        if record_id:
            resolved = _resolve_customer(record_id)
            if resolved is None:
                return SYNTHETIC_NOTICE + f"**Not found:** No synthetic record `{record_id}` exists; no substitute record was used."
            kwargs["customer_id"] = resolved
        operation = kwargs.get("operation", "sentiment_dashboard")
        dispatch = {
            "sentiment_dashboard": self._sentiment_dashboard,
            "churn_prediction": self._churn_prediction,
            "retention_actions": self._retention_actions,
            "segment_analysis": self._segment_analysis,
            "early_warning_signals": self._early_warning_signals,
            "outreach_plan": self._outreach_plan,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return SYNTHETIC_NOTICE + handler(**kwargs)

    def _sentiment_dashboard(self, **kwargs) -> str:
        p = PORTFOLIO_SUMMARY
        high_risk = sum(t["customers"] for t in p["risk_tiers"])
        revenue = sum(t["annual_revenue"] for t in p["risk_tiers"])
        lines = ["# Customer Sentiment Dashboard\n"]
        lines.append(
            f"{p['customers'] // 1000}K customers analyzed. {high_risk:,} high churn risk representing "
            f"{_money_k(revenue)} annual revenue.\n"
        )
        lines.append("| Sentiment | Customers | % |")
        lines.append("|---|---|---|")
        for label, count in p["sentiment"].items():
            lines.append(f"| {label} | {count:,} | {round(count * 100 / p['customers'])}% |")
        lines.append("\n## High Risk\n")
        for t in p["risk_tiers"]:
            avg = round(t["annual_revenue"] / t["customers"])
            lines.append(f"- **{t['tier']}:** {t['customers']:,} customers, {_money_k(t['annual_revenue'])} revenue, ${avg:,} avg")
        drivers = ", ".join(f"{d['driver']} ({d['mentions']:,} mentions)" for d in p["negative_drivers"])
        lines.append(f"\n**Top Negative Drivers:** {drivers}.")
        lines.append(f"\n**Alert:** Negative sentiment up {p['negative_trend_pct']}% this month.")
        sentiments, total = _sentiment_breakdown()
        lines.append("\n## Highest-Value At-Risk Sample (interaction sentiment)\n")
        lines.append(f"Sample interactions analyzed: {total} (" + ", ".join(f"{k.title()} {v}" for k, v in sentiments.items()) + ")\n")
        lines.append("| Customer | Segment | NPS | Churn Probability | Recent Sentiment |")
        lines.append("|---|---|---|---|---|")
        for cid, c in _ranked_customers():
            recent = c["recent_interactions"][0]["sentiment"].title()
            lines.append(
                f"| {c['name']} ({cid}) | {c['segment'].replace('_', ' ').title()} | {c['nps_score']} "
                f"| {c['churn_probability_pct']}% ({_risk_tier(c['churn_probability_pct'])}) | {recent} |"
            )
        lines.append("\nNext step: see the early warning signals?")
        return "\n".join(lines)

    def _early_warning_signals(self, **kwargs) -> str:
        e = EARLY_WARNING
        lines = ["# Early Warning Signals\n"]
        lines.append(f"{len(e['signals'])} key predictive signals identified, shown {e['lead_time']}.\n")
        lines.append("| Signal | Customers | Churn Rate |")
        lines.append("|---|---|---|")
        for s in e["signals"]:
            lines.append(f"| {s['signal']} | {s['customers']:,} | {s['churn_rate_pct']}% |")
        lines.append("\n## Critical Combinations\n")
        for c in e["combinations"]:
            lines.append(f"- {c['combination']}: {c['churn_rate_pct']}% churn")
        lines.append("\n## Real-Time Alerts Today\n")
        for a in e["alerts_today"]:
            lines.append(f"- {a['customers']} customers: {a['alert']}")
        top = _ranked_customers()[:3]
        lines.append(
            "\n**High-Value at Risk:** "
            + ", ".join(f"{c['name']} ({_money_k(c['deposits'])}, {c['primary_signal']})" for _cid, c in top)
        )
        lines.append("\nNext step: profile the highest-value at-risk customers?")
        return "\n".join(lines)

    def _profile_lines(self, cid, c, rank):
        signals = ", ".join(c["behavior_signals"])
        return [
            f"### {c['name']} ({cid}) - Priority {rank}\n",
            f"- {_money_k(c['deposits'])} deposits, {_money_k(c['annual_revenue'])} annual revenue",
            f"- Risk: {c['churn_probability_pct']}% ({_risk_tier(c['churn_probability_pct'])}); review score {_churn_score(c)}/100",
            f"- Signals: {signals}",
            f"- Last survey: {'Detractor' if c['nps_score'] < 7 else 'Passive'} ({c['nps_score']}/10) - \"{c['survey_verbatim']}\"",
            f"- Recent contact: {c['recent_contact']}",
            f"- Segment: {c['segment'].replace('_', ' ').title()}, tenure {c['tenure_years']} years, products: {', '.join(c['products'])}",
            "",
        ]

    def _churn_prediction(self, **kwargs) -> str:
        ranked = _ranked_customers()
        cid = kwargs.get("customer_id")
        lines = ["# Churn Prediction Report: Highest-Value At-Risk Customers\n"]
        if cid:
            rank = 1
            for k, _c in ranked:
                if k == cid:
                    break
                rank += 1
            lines += self._profile_lines(cid, CUSTOMER_INTERACTIONS[cid], rank)
        else:
            lines.append(f"Top {len(ranked)} at-risk profiles prepared.\n")
            first_id, first = ranked[0]
            lines += self._profile_lines(first_id, first, 1)
            lines.append(f"## Top {len(ranked)} Summary\n")
            lines.append("| Priority | Customer | Deposits | Revenue | Risk | Key Signal |")
            lines.append("|---|---|---|---|---|---|")
            for r, (k, c) in enumerate(ranked, 1):
                lines.append(
                    f"| {r} | {_short_name(c['name'])} ({k}) | {_money_k(c['deposits'])} | {_money_k(c['annual_revenue'])} "
                    f"| {c['churn_probability_pct']}% | {c['primary_signal']} |"
                )
            deposits = sum(c["deposits"] for _k, c in ranked)
            revenue = sum(c["annual_revenue"] for _k, c in ranked)
            lines.append(
                f"\n**Combined Risk:** {_money_k(deposits)} deposits, {_money_k(revenue)} annual revenue at risk. "
                f"Replacement cost if lost: {_money_k(REPLACEMENT_COST['top5_if_lost'])}."
            )
        lines.append("\n## Churn Indicators Reference\n")
        for ind_id, ind in CHURN_INDICATORS.items():
            lines.append(f"- **{ind_id.replace('_', ' ').title()}** (weight: {ind['weight']}): {ind['description']}")
        lines.append("\nThese scores prioritize review; they do not predict an individual outcome.")
        lines.append("\nNext step: generate retention strategies?")
        return "\n".join(lines)

    def _strategy_lines(self, cid):
        c, s = CUSTOMER_INTERACTIONS[cid], RETENTION_STRATEGIES[cid]
        return [
            f"### {c['name']} ({cid}) Strategy\n",
            f"- Approach: {s['approach']}",
            f"- Message: \"{s['message']}\"",
            f"- Offer: {s['offer']}",
            f"- Incentive: {s['incentive']} (${s['incentive_value']} value)",
            f"- Urgency: {s['urgency']}",
            f"- Success probability (modeled): {s['success_pct']}%",
            f"- Draft talk track: \"{s['talk_track']}\"",
            "",
        ]

    def _retention_actions(self, **kwargs) -> str:
        cid = kwargs.get("customer_id")
        lines = ["# Retention Action Recommendations\n"]
        if cid:
            lines += self._strategy_lines(cid)
        else:
            ranked = _ranked_customers()
            lines.append("Personalized strategies drafted for each customer.\n")
            lines += self._strategy_lines(ranked[0][0])
            lines.append(f"## All {len(ranked)} Customers\n")
            lines.append("| Customer | Strategy | Offer | Incentive | Success % |")
            lines.append("|---|---|---|---|---|")
            for k, c in ranked:
                s = RETENTION_STRATEGIES[k]
                lines.append(f"| {_short_name(c['name'])} ({k}) | {s['strategy']} | {s['offer']} | ${s['incentive_value']} | {s['success_pct']}% |")
        lines.append("\n## Available Actions Catalog\n")
        lines.append("| Action | Description | Cost | Success Rate |")
        lines.append("|---|---|---|---|")
        for action_id, action in RETENTION_ACTIONS.items():
            lines.append(
                f"| {action_id.replace('_', ' ').title()} | {action['description']} "
                f"| ${action['cost']} | {action['success_rate']}% |"
            )
        lines.append(
            "\nEvery option requires relationship-manager review, policy validation, customer consent "
            "where applicable, and approved execution. No customer was contacted and no offer was made."
        )
        lines.append("\nNext step: assign the outreach and set up tracking?")
        return "\n".join(lines)

    def _outreach_plan(self, **kwargs) -> str:
        ranked = _ranked_customers()
        lines = ["# Proposed Outreach Assignments and Tracking\n"]
        lines.append(
            f"Outreach plan ready for the manager to confirm: all {len(ranked)} high-priority customers "
            "have a proposed owner, channel and due time.\n"
        )
        lines.append("| Customer | Assigned To | Channel | Due |")
        lines.append("|---|---|---|---|")
        for k, c in ranked:
            s = RETENTION_STRATEGIES[k]
            lines.append(f"| {_short_name(c['name'])} ({k}) | {s['owner']} | {s['channel']} | {s['due']} |")
        lines.append(
            "\n**Prepared for release (not sent):** customer briefs and talk tracks drafted, offers queued "
            "for approval, calendar holds proposed."
        )
        lines.append("\n## Tracking\n")
        lines += [f"- {t}" for t in OUTREACH_TRACKING["tracking"]]
        lines.append("\n## Escalation Rules\n")
        lines += [f"- {e}" for e in OUTREACH_TRACKING["escalations"]]
        lines.append(
            "\nNo customer was contacted, no offer was made, and no assignment, brief or calendar hold was "
            "sent; the manager confirms the plan in the CRM."
        )
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
# Main — the demo video's turns in order
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = CustomerSentimentChurnAgent()
    for op in ["sentiment_dashboard", "early_warning_signals", "churn_prediction", "retention_actions", "outreach_plan"]:
        print(agent.perform(operation=op))
        print("\n" + "=" * 80 + "\n")
