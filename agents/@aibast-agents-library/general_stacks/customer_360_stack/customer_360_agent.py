"""
Customer 360 Agent

Provides unified customer profiles by merging CRM, support, and billing data,
with interaction timelines, health scores, and next-best-action recommendations.

Where a real deployment would integrate with multiple customer data sources,
this agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/customer-360",
    "version": "1.0.0",
    "display_name": "Customer 360",
    "description": "Unified customer profiles merging CRM, support, and billing data with health scores and next-best-action recommendations.",
    "author": "AIBAST",
    "tags": ["customer-360", "unified-profile", "health-score", "next-best-action", "crm"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_CUSTOMER_PROFILES = {
    "CUST-3001": {
        "name": "TechVantage Solutions", "segment": "Enterprise",
        "industry": "Technology", "arr": 185000, "mrr": 15417,
        "primary_contact": "Jennifer Walsh", "contact_email": "jennifer.walsh@techvantage.com",
        "account_manager": "Sarah Chen", "csm": "Mike Torres",
        "contract_start": "2023-06-15", "contract_end": "2026-06-14",
        "products": ["Enterprise Platform", "Analytics Pro", "Integration Hub", "Premium Support"],
        "employees_using": 420, "licenses_purchased": 500,
        "crm_data": {"lead_source": "Partner Referral", "deal_cycle_days": 62, "original_deal_size": 145000},
        "billing_data": {"payment_method": "ACH", "payment_terms": "Net 30", "last_payment": "2025-11-01", "outstanding_balance": 0, "lifetime_value": 462500},
        "support_data": {"total_tickets": 47, "open_tickets": 2, "avg_resolution_hours": 4.2, "csat_avg": 4.6, "escalations": 3},
    },
    "CUST-3002": {
        "name": "Greenridge Partners", "segment": "Mid-Market",
        "industry": "Financial Services", "arr": 72000, "mrr": 6000,
        "primary_contact": "David Park", "contact_email": "david.park@greenridge.com",
        "account_manager": "Tom Rivera", "csm": "Lisa Wong",
        "contract_start": "2024-01-10", "contract_end": "2025-01-09",
        "products": ["Core Platform", "Analytics Standard"],
        "employees_using": 85, "licenses_purchased": 100,
        "crm_data": {"lead_source": "Website", "deal_cycle_days": 45, "original_deal_size": 72000},
        "billing_data": {"payment_method": "Credit Card", "payment_terms": "Net 15", "last_payment": "2025-10-15", "outstanding_balance": 6000, "lifetime_value": 72000},
        "support_data": {"total_tickets": 18, "open_tickets": 4, "avg_resolution_hours": 8.7, "csat_avg": 3.8, "escalations": 2},
    },
    "CUST-3003": {
        "name": "BlueHorizon Health", "segment": "Enterprise",
        "industry": "Healthcare", "arr": 240000, "mrr": 20000,
        "primary_contact": "Dr. Maria Santos", "contact_email": "maria.santos@bluehorizon.org",
        "account_manager": "Sarah Chen", "csm": "Mike Torres",
        "contract_start": "2022-03-01", "contract_end": "2025-02-28",
        "products": ["Enterprise Platform", "Analytics Pro", "Security Suite", "Integration Hub", "Premium Support", "Training Package"],
        "employees_using": 1200, "licenses_purchased": 1500,
        "crm_data": {"lead_source": "Conference", "deal_cycle_days": 120, "original_deal_size": 180000},
        "billing_data": {"payment_method": "ACH", "payment_terms": "Net 45", "last_payment": "2025-11-05", "outstanding_balance": 0, "lifetime_value": 720000},
        "support_data": {"total_tickets": 92, "open_tickets": 1, "avg_resolution_hours": 3.1, "csat_avg": 4.8, "escalations": 1},
    },
}

_INTERACTION_LOGS = {
    "CUST-3001": [
        {"date": "2025-11-12", "type": "Support Ticket", "channel": "Portal", "summary": "Dashboard loading timeout - resolved with cache clear", "sentiment": "Neutral"},
        {"date": "2025-11-08", "type": "QBR Meeting", "channel": "Teams", "summary": "Quarterly business review - discussed expansion to APAC team", "sentiment": "Positive"},
        {"date": "2025-10-25", "type": "Support Ticket", "channel": "Email", "summary": "SSO integration issue post-update - escalated and resolved", "sentiment": "Frustrated"},
        {"date": "2025-10-15", "type": "Product Feedback", "channel": "In-App", "summary": "Requested advanced filtering in analytics module", "sentiment": "Positive"},
        {"date": "2025-10-01", "type": "Billing", "channel": "Portal", "summary": "Added 50 user licenses for Q4 onboarding", "sentiment": "Positive"},
    ],
    "CUST-3002": [
        {"date": "2025-11-10", "type": "Support Ticket", "channel": "Portal", "summary": "Report export failing for large date ranges", "sentiment": "Frustrated"},
        {"date": "2025-11-05", "type": "Support Ticket", "channel": "Email", "summary": "User access permissions not syncing with AD", "sentiment": "Frustrated"},
        {"date": "2025-10-28", "type": "CSM Check-in", "channel": "Phone", "summary": "Discussed adoption challenges, team training needed", "sentiment": "Concerned"},
        {"date": "2025-10-20", "type": "Billing", "channel": "Portal", "summary": "Late payment notice - payment received Oct 22", "sentiment": "Neutral"},
    ],
    "CUST-3003": [
        {"date": "2025-11-14", "type": "Renewal Discussion", "channel": "Teams", "summary": "Renewal meeting - expanding from 1500 to 2000 licenses", "sentiment": "Positive"},
        {"date": "2025-11-01", "type": "Executive Sponsor", "channel": "In-Person", "summary": "CIO dinner - strong relationship, considering additional modules", "sentiment": "Positive"},
        {"date": "2025-10-20", "type": "Product Feedback", "channel": "Email", "summary": "Requested HIPAA compliance reporting enhancements", "sentiment": "Positive"},
    ],
}

_HEALTH_SCORE_WEIGHTS = {
    "product_adoption": 0.25,
    "support_satisfaction": 0.20,
    "engagement_frequency": 0.20,
    "billing_health": 0.15,
    "relationship_strength": 0.20,
}

_NEXT_BEST_ACTIONS = {
    "high_health": [
        {"action": "Schedule expansion discussion", "priority": "Medium", "reason": "Strong health score indicates readiness for upsell"},
        {"action": "Invite to customer advisory board", "priority": "Low", "reason": "Champion potential for reference program"},
        {"action": "Share product roadmap preview", "priority": "Medium", "reason": "Deepen partnership and gather feedback"},
    ],
    "medium_health": [
        {"action": "Schedule adoption review", "priority": "High", "reason": "Usage below potential, identify barriers"},
        {"action": "Offer training session", "priority": "High", "reason": "Improve feature utilization"},
        {"action": "CSM check-in call", "priority": "Medium", "reason": "Proactive relationship maintenance"},
    ],
    "low_health": [
        {"action": "Executive escalation meeting", "priority": "Critical", "reason": "Churn risk - requires immediate attention"},
        {"action": "Create success plan", "priority": "Critical", "reason": "Define clear path to value realization"},
        {"action": "Resolve open support tickets", "priority": "High", "reason": "Outstanding issues impacting satisfaction"},
    ],
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve_customer(query):
    if not query:
        return "CUST-3001"
    q = query.upper().strip()
    for key in _CUSTOMER_PROFILES:
        if key in q:
            return key
    q_lower = query.lower()
    for key, cust in _CUSTOMER_PROFILES.items():
        if q_lower in cust["name"].lower():
            return key
    return "CUST-3001"


def _compute_health_score(cust_id):
    cust = _CUSTOMER_PROFILES[cust_id]
    adoption = min(100, (cust["employees_using"] / cust["licenses_purchased"]) * 100 * 1.2)
    support_sat = cust["support_data"]["csat_avg"] / 5.0 * 100
    interactions = len(_INTERACTION_LOGS.get(cust_id, []))
    engagement = min(100, interactions * 20)
    billing = 100 if cust["billing_data"]["outstanding_balance"] == 0 else 60
    positive = sum(1 for i in _INTERACTION_LOGS.get(cust_id, []) if i["sentiment"] == "Positive")
    total_interactions = max(1, interactions)
    relationship = (positive / total_interactions) * 100
    w = _HEALTH_SCORE_WEIGHTS
    score = (adoption * w["product_adoption"] + support_sat * w["support_satisfaction"] +
             engagement * w["engagement_frequency"] + billing * w["billing_health"] +
             relationship * w["relationship_strength"])
    return round(score), {"adoption": round(adoption), "support": round(support_sat),
                           "engagement": round(engagement), "billing": round(billing),
                           "relationship": round(relationship)}


def _get_nba(health_score):
    if health_score >= 80:
        return _NEXT_BEST_ACTIONS["high_health"]
    elif health_score >= 60:
        return _NEXT_BEST_ACTIONS["medium_health"]
    return _NEXT_BEST_ACTIONS["low_health"]


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class Customer360Agent(BasicAgent):
    """
    Unified customer profile agent.

    Operations:
        unified_profile      - complete customer profile from all data sources
        interaction_timeline - chronological interaction history
        health_score         - compute and explain customer health score
        next_best_action     - recommend next actions based on health
    """

    def __init__(self):
        self.name = "Customer360Agent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "unified_profile", "interaction_timeline",
                            "health_score", "next_best_action",
                        ],
                        "description": "The customer 360 operation to perform",
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (e.g. 'CUST-3001')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "unified_profile")
        cust_id = _resolve_customer(kwargs.get("customer_id", ""))
        dispatch = {
            "unified_profile": self._unified_profile,
            "interaction_timeline": self._interaction_timeline,
            "health_score": self._health_score,
            "next_best_action": self._next_best_action,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(cust_id)

    # ── unified_profile ────────────────────────────────────────
    def _unified_profile(self, cust_id):
        cust = _CUSTOMER_PROFILES[cust_id]
        score, _ = _compute_health_score(cust_id)
        products_list = "\n".join(f"- {p}" for p in cust["products"])
        return (
            f"**Customer 360: {cust['name']}**\n\n"
            f"| Field | Detail |\n|---|---|\n"
            f"| Segment | {cust['segment']} |\n"
            f"| Industry | {cust['industry']} |\n"
            f"| ARR | ${cust['arr']:,} |\n"
            f"| Health Score | {score}/100 |\n"
            f"| Primary Contact | {cust['primary_contact']} |\n"
            f"| Account Manager | {cust['account_manager']} |\n"
            f"| CSM | {cust['csm']} |\n"
            f"| Contract | {cust['contract_start']} to {cust['contract_end']} |\n\n"
            f"**Products ({len(cust['products'])}):**\n{products_list}\n\n"
            f"**Usage:** {cust['employees_using']}/{cust['licenses_purchased']} licenses active ({cust['employees_using']/cust['licenses_purchased']*100:.0f}%)\n\n"
            f"**Support:** {cust['support_data']['open_tickets']} open tickets | CSAT {cust['support_data']['csat_avg']}/5.0 | Avg resolution: {cust['support_data']['avg_resolution_hours']}h\n\n"
            f"**Billing:** {cust['billing_data']['payment_method']} | {cust['billing_data']['payment_terms']} | LTV: ${cust['billing_data']['lifetime_value']:,}\n\n"
            f"Source: [CRM + Support + Billing + Product Usage]\nAgents: Customer360Agent"
        )

    # ── interaction_timeline ───────────────────────────────────
    def _interaction_timeline(self, cust_id):
        cust = _CUSTOMER_PROFILES[cust_id]
        logs = _INTERACTION_LOGS.get(cust_id, [])
        timeline_rows = ""
        for log in logs:
            timeline_rows += f"| {log['date']} | {log['type']} | {log['channel']} | {log['summary'][:60]} | {log['sentiment']} |\n"
        sentiment_counts = {}
        for log in logs:
            sentiment_counts[log["sentiment"]] = sentiment_counts.get(log["sentiment"], 0) + 1
        sentiment_summary = " | ".join(f"{s}: {c}" for s, c in sentiment_counts.items())
        return (
            f"**Interaction Timeline: {cust['name']}**\n\n"
            f"Total Interactions: {len(logs)} | Sentiment: {sentiment_summary}\n\n"
            f"| Date | Type | Channel | Summary | Sentiment |\n|---|---|---|---|---|\n"
            f"{timeline_rows}\n\n"
            f"Source: [CRM + Support + Billing + CSM Notes]\nAgents: Customer360Agent"
        )

    # ── health_score ───────────────────────────────────────────
    def _health_score(self, cust_id):
        cust = _CUSTOMER_PROFILES[cust_id]
        score, components = _compute_health_score(cust_id)
        comp_rows = ""
        for name, weight in _HEALTH_SCORE_WEIGHTS.items():
            comp_val = components.get(name.split("_")[0], components.get(name, 0))
            weighted = comp_val * weight
            comp_rows += f"| {name.replace('_', ' ').title()} | {comp_val}/100 | {weight:.0%} | {weighted:.1f} |\n"
        status = "Healthy" if score >= 80 else ("At Risk" if score >= 60 else "Critical")
        return (
            f"**Health Score: {cust['name']}**\n\n"
            f"**Overall Score: {score}/100 ({status})**\n\n"
            f"| Component | Score | Weight | Weighted |\n|---|---|---|---|\n"
            f"{comp_rows}\n"
            f"**Key Indicators:**\n"
            f"- License utilization: {cust['employees_using']}/{cust['licenses_purchased']} ({cust['employees_using']/cust['licenses_purchased']*100:.0f}%)\n"
            f"- Support CSAT: {cust['support_data']['csat_avg']}/5.0\n"
            f"- Open tickets: {cust['support_data']['open_tickets']}\n"
            f"- Outstanding balance: ${cust['billing_data']['outstanding_balance']:,}\n\n"
            f"Source: [Health Score Engine]\nAgents: Customer360Agent"
        )

    # ── next_best_action ───────────────────────────────────────
    def _next_best_action(self, cust_id):
        cust = _CUSTOMER_PROFILES[cust_id]
        score, _ = _compute_health_score(cust_id)
        actions = _get_nba(score)
        action_rows = ""
        for a in actions:
            action_rows += f"| {a['action']} | {a['priority']} | {a['reason']} |\n"
        return (
            f"**Next Best Actions: {cust['name']}**\n\n"
            f"Health Score: {score}/100 | Segment: {cust['segment']} | ARR: ${cust['arr']:,}\n\n"
            f"| Action | Priority | Rationale |\n|---|---|---|\n"
            f"{action_rows}\n"
            f"**Context:**\n"
            f"- Contract ends: {cust['contract_end']}\n"
            f"- Open tickets: {cust['support_data']['open_tickets']}\n"
            f"- Last interaction: {_INTERACTION_LOGS.get(cust_id, [{}])[0].get('date', 'N/A')}\n\n"
            f"Source: [NBA Engine + CRM + Health Score]\nAgents: Customer360Agent"
        )


if __name__ == "__main__":
    agent = Customer360Agent()
    for op in ["unified_profile", "interaction_timeline", "health_score", "next_best_action"]:
        print("=" * 60)
        print(agent.perform(operation=op, customer_id="CUST-3001"))
        print()
