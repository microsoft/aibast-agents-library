"""
AI Customer Assistant Agent

AI-powered customer service assistant handling inquiries, knowledge base
searches, escalation routing, and satisfaction surveys.

Where a real deployment would connect to CRM, knowledge base, and ticketing
systems, this agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/ai-customer-assistant",
    "version": "1.1.0",
    "display_name": "Customer Escalations Agent",
    "description": "Automate back-office contact center escalation workflows to deliver better service outcomes and retention rates.",
    "author": "AIBAST",
    "tags": ["customer-service", "support", "knowledge-base", "escalation", "satisfaction"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_INQUIRIES = {
    "INQ-4001": {
        "id": "INQ-4001", "customer": "Acme Corp", "contact": "Lisa Park",
        "email": "lisa.park@acmecorp.com", "channel": "Live Chat",
        "subject": "Unable to generate monthly usage report",
        "description": "The export button on the analytics dashboard returns a 500 error when selecting date ranges longer than 30 days.",
        "category": "Technical Issue", "priority": "High",
        "created_at": "2025-11-14T09:23:00Z", "status": "Open",
        "account_tier": "Enterprise", "sentiment": "Frustrated",
    },
    "INQ-4002": {
        "id": "INQ-4002", "customer": "Bright Solutions", "contact": "Tom Reyes",
        "email": "tom.reyes@brightsol.com", "channel": "Email",
        "subject": "Pricing for additional user seats",
        "description": "We are expanding our team by 15 people next quarter and need pricing for additional seats on the Professional plan.",
        "category": "Billing & Pricing", "priority": "Medium",
        "created_at": "2025-11-14T10:05:00Z", "status": "Open",
        "account_tier": "Professional", "sentiment": "Neutral",
    },
    "INQ-4003": {
        "id": "INQ-4003", "customer": "Greenfield Inc", "contact": "Maria Santos",
        "email": "maria.santos@greenfield.io", "channel": "Phone",
        "subject": "SSO configuration not working after IdP migration",
        "description": "After migrating from Okta to Azure AD, SSO login redirects to a blank page. SAML assertion looks correct in dev tools.",
        "category": "Technical Issue", "priority": "Critical",
        "created_at": "2025-11-14T08:12:00Z", "status": "Open",
        "account_tier": "Enterprise", "sentiment": "Urgent",
    },
    "INQ-4004": {
        "id": "INQ-4004", "customer": "Summit Partners", "contact": "Jake Miller",
        "email": "jake.miller@summitpartners.com", "channel": "Support Portal",
        "subject": "Feature request: bulk user import via CSV",
        "description": "Currently we have to add users one at a time. We need CSV import capability for onboarding 200+ users.",
        "category": "Feature Request", "priority": "Low",
        "created_at": "2025-11-13T16:30:00Z", "status": "Open",
        "account_tier": "Professional", "sentiment": "Positive",
    },
    "INQ-4005": {
        "id": "INQ-4005", "customer": "Jennifer Adams", "contact": "Jennifer Adams",
        "email": "jennifer.adams@example.com", "channel": "Live Chat",
        "subject": "Unrecognized Premium Support charge",
        "description": "Charged $149 never ordered. Second time. Want refund/explanation or canceling.",
        "category": "Billing & Pricing", "priority": "High",
        "created_at": "2025-11-14T11:02:00Z", "status": "Open",
        "account_tier": "Gold", "sentiment": "Frustrated",
        "headline": "Billing dispute from long-term Gold customer - requires careful handling",
        "loyalty": "Gold (5 years)", "loyalty_years": 5, "base_monthly": 200,
        "sentiment_score": -0.6,
        "context": "Previous issue 8 months ago, charge from add-on auto-enrollment",
        "card": "Visa ****4521",
    },
}

# Billing-dispute playbook for INQ-4005 (the demo case). Every action is a prepared,
# approval-pending item: this agent never refunds, credits, cancels or sends anything.
_RESOLUTIONS = {
    "INQ-4005": {
        "addon": "Premium Support", "addon_monthly": 149,
        "immediate": [
            ("Full refund", "$149 (ready to process on approval)"),
            ("Cancel add-on", "Remove Premium Support from account"),
            ("Block auto-enroll", "Flag account against promo auto-enrollment"),
        ],
        "retention": [("Service credit", 50, "$50 goodwill"), ("Free month", 200, "$200 value")],
        "credit": 50,
        "refund_ref": "REF-892341", "credit_ref": "CRD-892342", "refund_days": "3-5 business days",
        "follow_up": [
            ("Satisfaction survey", "+24 hours", "Gauge resolution"),
            ("Check-in call", "+7 days", "Relationship"),
            ("Retention review", "+30 days", "Account health"),
        ],
        "email_subject": "Your Account Corrected - Refund Processed",
        "summary": {
            "issue": "Unauthorized $149 charge",
            "first_contact_resolution": "Yes", "handle_minutes": 8,
            "predicted_csat": 4.5, "retention_probability_pct": 94,
            "similar_cases": 23,
        },
    },
}

_KB_ARTICLES = {
    "KB-101": {
        "id": "KB-101", "title": "How to Export Analytics Reports",
        "category": "Analytics", "relevance_score": 0.95,
        "summary": "Step-by-step guide for exporting usage and analytics reports in CSV, PDF, and Excel formats.",
        "resolution_steps": [
            "Navigate to Analytics > Reports",
            "Select date range (max 90 days per export)",
            "Choose format (CSV, PDF, Excel)",
            "Click Export and wait for download link via email",
        ],
        "last_updated": "2025-10-20", "views": 1247, "helpful_votes": 892,
    },
    "KB-102": {
        "id": "KB-102", "title": "SSO Configuration Guide (SAML 2.0)",
        "category": "Authentication", "relevance_score": 0.92,
        "summary": "Complete guide for configuring SAML-based SSO with supported identity providers.",
        "resolution_steps": [
            "Go to Admin > Security > SSO Settings",
            "Upload IdP metadata XML or enter values manually",
            "Set Assertion Consumer Service URL to https://app.example.com/sso/callback",
            "Map attributes: email, firstName, lastName, groups",
            "Test with SSO debug mode enabled before enforcing",
        ],
        "last_updated": "2025-11-01", "views": 2034, "helpful_votes": 1567,
    },
    "KB-103": {
        "id": "KB-103", "title": "User Management and Seat Licensing",
        "category": "Billing", "relevance_score": 0.88,
        "summary": "Overview of seat-based licensing, adding users, and managing subscriptions.",
        "resolution_steps": [
            "View current seat count in Admin > Billing > Subscription",
            "Click Add Seats to purchase additional licenses",
            "New seats are prorated for the current billing cycle",
            "Bulk provisioning available via SCIM for Enterprise plans",
        ],
        "last_updated": "2025-09-15", "views": 3421, "helpful_votes": 2890,
    },
    "KB-104": {
        "id": "KB-104", "title": "Known Issue: Report Export Timeout for Large Date Ranges",
        "category": "Analytics", "relevance_score": 0.97,
        "summary": "Export fails with 500 error for date ranges exceeding 30 days. Workaround and fix timeline available.",
        "resolution_steps": [
            "Split export into 30-day segments as a workaround",
            "Engineering fix scheduled for v3.8.2 (target: Dec 2025)",
            "Contact support if you need a one-time bulk export",
        ],
        "last_updated": "2025-11-10", "views": 456, "helpful_votes": 398,
    },
    "KB-105": {
        "id": "KB-105", "title": "Known Issue: Premium Support Promo Auto-Enrollment Charges",
        "category": "Billing", "relevance_score": 0.98,
        "summary": "A promotion enrolled customers in a Premium Support add-on trial that converts to a paid charge. Charges are refund eligible.",
        "resolution_steps": [
            "Confirm the add-on was added by the promo auto-enrollment, not by the customer",
            "Refund the add-on charge in full (refund eligible within 30 days, no cancel penalty)",
            "Cancel the add-on and flag the account to block future auto-enrollment",
            "Log the case against the known issue for the product team",
        ],
        "finding": [
            ("Charge", "Premium Support $149/month"),
            ("Source", "Promo auto-enroll"),
            ("Timeline", "45 days ago promo enrollment > 30-day trial > charged 15 days ago"),
        ],
        "policy": "Refund eligible (within 30 days of the charge), no cancel penalty, agent has full refund authority",
        "similar_cases": "23 complaints this month (known issue)",
        "last_updated": "2025-11-12", "views": 312, "helpful_votes": 287,
    },
}

_ROUTING_RULES = {
    "Technical Issue": {
        "Critical": {"team": "Tier 2 Engineering", "sla_hours": 2, "auto_escalate": True},
        "High": {"team": "Tier 1 Technical Support", "sla_hours": 4, "auto_escalate": False},
        "Medium": {"team": "General Support", "sla_hours": 8, "auto_escalate": False},
        "Low": {"team": "General Support", "sla_hours": 24, "auto_escalate": False},
    },
    "Billing & Pricing": {
        "Critical": {"team": "Billing Escalations", "sla_hours": 2, "auto_escalate": True},
        "High": {"team": "Account Management", "sla_hours": 4, "auto_escalate": False},
        "Medium": {"team": "Account Management", "sla_hours": 8, "auto_escalate": False},
        "Low": {"team": "Self-Service Billing", "sla_hours": 24, "auto_escalate": False},
    },
    "Feature Request": {
        "Critical": {"team": "Product Management", "sla_hours": 8, "auto_escalate": False},
        "High": {"team": "Product Management", "sla_hours": 24, "auto_escalate": False},
        "Medium": {"team": "Product Backlog", "sla_hours": 72, "auto_escalate": False},
        "Low": {"team": "Product Backlog", "sla_hours": 168, "auto_escalate": False},
    },
}

_SATISFACTION_DATA = {
    "overall_csat": 4.3,
    "nps_score": 42,
    "response_time_avg_minutes": 12,
    "first_contact_resolution_rate": 0.78,
    "surveys": [
        {"inquiry_id": "INQ-3990", "score": 5, "comment": "Resolved quickly, great experience.", "date": "2025-11-13"},
        {"inquiry_id": "INQ-3988", "score": 4, "comment": "Helpful but took a while to connect.", "date": "2025-11-13"},
        {"inquiry_id": "INQ-3985", "score": 3, "comment": "Issue resolved but had to explain problem multiple times.", "date": "2025-11-12"},
        {"inquiry_id": "INQ-3982", "score": 5, "comment": "Agent was knowledgeable and proactive.", "date": "2025-11-12"},
        {"inquiry_id": "INQ-3979", "score": 2, "comment": "Still waiting for follow-up on my SSO issue.", "date": "2025-11-11"},
        {"inquiry_id": "INQ-3975", "score": 4, "comment": "Good resolution, would prefer faster initial response.", "date": "2025-11-11"},
    ],
    "trend": {"week_over_week": "+0.2", "month_over_month": "+0.1"},
}

_READ_ONLY_NOTICE = (
    "Synthetic decision support only. No customer message is sent, no case is "
    "changed, and every escalation or response requires an authorized reviewer."
)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

_DEFAULT_INQUIRY = "INQ-4005"


def _resolve_inquiry(query):
    """Inquiry ID or customer name; None when nothing matches (never another case)."""
    if not query:
        return _DEFAULT_INQUIRY
    q = query.lower().strip()
    for key, inq in _INQUIRIES.items():
        if key.lower() in q or q in inq["customer"].lower() or q in inq["contact"].lower():
            return key
    return None


def _match_kb_articles(inquiry_id):
    inq = _INQUIRIES.get(inquiry_id, {})
    subject = inq.get("subject", "").lower()
    matched = []
    for kb_id, article in _KB_ARTICLES.items():
        title_lower = article["title"].lower()
        if any(word in title_lower for word in subject.split() if len(word) > 3):
            matched.append(article)
    if not matched:
        matched = [list(_KB_ARTICLES.values())[0]]
    return sorted(matched, key=lambda a: a["relevance_score"], reverse=True)


def _get_routing(category, priority):
    cat_rules = _ROUTING_RULES.get(category, _ROUTING_RULES["Technical Issue"])
    return cat_rules.get(priority, cat_rules["Medium"])


def _compute_csat_breakdown():
    scores = [s["score"] for s in _SATISFACTION_DATA["surveys"]]
    dist = {i: scores.count(i) for i in range(1, 6)}
    promoters = sum(1 for s in scores if s >= 4)
    detractors = sum(1 for s in scores if s <= 2)
    total = len(scores)
    return dist, promoters, detractors, total


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

_OPERATIONS = [
    "handle_inquiry", "knowledge_search", "escalation_routing", "satisfaction_survey",
    "recommend_resolution", "prepare_actions", "follow_up_plan", "interaction_summary",
]


class AICustomerAssistantAgent(BasicAgent):
    """
    AI-powered customer service assistant.

    Operations:
        handle_inquiry       - triage and respond to a customer inquiry
        knowledge_search     - search knowledge base for relevant articles
        escalation_routing   - determine escalation path and SLA
        satisfaction_survey  - review CSAT scores and survey feedback
        recommend_resolution - resolution and retention recommendation for the case
        prepare_actions      - approval-pending refund/credit action package (never executed)
        follow_up_plan       - follow-up touchpoints and a draft customer email (never sent)
        interaction_summary  - session summary with quality metrics and value protected
    """

    def __init__(self):
        self.name = "AICustomerAssistantAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                f"{__manifest__['description']} Always use this tool for a "
                "back-office customer escalation brief, resolving a customer inquiry, "
                "inherited support case, billing dispute, export-error case, knowledge "
                "guidance, escalation queue or SLA, resolution recommendations, refunds and "
                "credits to approve, follow-up and response drafts, interaction summaries, "
                "and service-quality or CSAT review. The demo case is INQ-4005, Jennifer "
                "Adams' disputed $149 charge: if the user asks to resolve 'this customer "
                "inquiry' and gives no inquiry ID, use handle_inquiry with INQ-4005; if the "
                "user asks for the full brief before responding on the export-error case, use "
                "handle_inquiry with INQ-4001. Analyze only the synthetic snapshot; never send "
                "customer communications, update a case, process a refund or credit, or "
                "execute an escalation: actions come back as approval-pending drafts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "Choose handle_inquiry to resolve or brief a customer inquiry "
                            "(customer context, sentiment, risk); knowledge_search for knowledge "
                            "articles, what happened, approved guidance or resolution steps; "
                            "recommend_resolution for 'what should I do to resolve this'; "
                            "prepare_actions for 'process the refund and apply the credit' "
                            "(returns the approval-pending action package); follow_up_plan to "
                            "schedule follow-up and prepare the response email; "
                            "interaction_summary to summarize the interaction; "
                            "escalation_routing for the recommended queue, team, or response "
                            "target; and satisfaction_survey for CSAT, NPS, survey, or "
                            "service-quality questions."
                        ),
                    },
                    "inquiry_id": {
                        "type": "string",
                        "description": (
                            "Synthetic inquiry ID or customer name. INQ-4005 (Jennifer Adams "
                            "billing dispute) is the default; INQ-4001 is the analytics "
                            "export-error escalation and INQ-4003 the urgent SSO migration case."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "handle_inquiry")
        dispatch = {
            "handle_inquiry": self._handle_inquiry,
            "knowledge_search": self._knowledge_search,
            "escalation_routing": self._escalation_routing,
            "satisfaction_survey": self._satisfaction_survey,
            "recommend_resolution": self._recommend_resolution,
            "prepare_actions": self._prepare_actions,
            "follow_up_plan": self._follow_up_plan,
            "interaction_summary": self._interaction_summary,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        default_inquiry = "INQ-4003" if op == "escalation_routing" else _DEFAULT_INQUIRY
        inq_id = _resolve_inquiry(kwargs.get("inquiry_id") or default_inquiry)
        if inq_id is None:
            return (f"No synthetic inquiry matches '{kwargs.get('inquiry_id')}'. Known inquiries: "
                    f"{', '.join(_INQUIRIES)}. {_READ_ONLY_NOTICE}")
        if op in ("recommend_resolution", "prepare_actions", "follow_up_plan",
                  "interaction_summary") and inq_id not in _RESOLUTIONS:
            return (f"No resolution playbook is packaged for {inq_id}; the playbook covers "
                    f"{', '.join(_RESOLUTIONS)} (Jennifer Adams). Use the knowledge search and "
                    f"escalation routing for {inq_id}. {_READ_ONLY_NOTICE}")
        return handler(inq_id)

    # ── recommend_resolution ───────────────────────────────────
    def _recommend_resolution(self, inq_id):
        inq = _INQUIRIES[inq_id]
        r = _RESOLUTIONS[inq_id]
        imm = "\n".join(f"| {a} | {d} |" for a, d in r["immediate"])
        ret = "\n".join(f"| {a} | {label} |" for a, _v, label in r["retention"])
        return (
            f"**Resolution with customer retention focus: {inq['customer']} ({inq_id})**\n\n"
            f"**Immediate Resolution:**\n\n| Action | Details |\n|---|---|\n{imm}\n\n"
            f"**Retention Gesture:**\n\n| Offer | Value |\n|---|---|\n{ret}\n\n"
            f"**Script:** \"Processed ${r['addon_monthly']} refund ({r['refund_days'].replace(' business days', ' days')}). "
            f"Canceled add-on, flagged account. As thanks for {inq['loyalty_years']} years, adding "
            f"${r['credit']} credit.\" (use once the actions are approved and processed)\n\n"
            f"**Review gate:** recommendation only; the refund, cancellation and credit need your "
            f"approval in the billing system. {_READ_ONLY_NOTICE}\n\n"
            f"Source: [Synthetic Playbooks]\nAgents: AICustomerAssistantAgent\n\nExecute?"
        )

    # ── prepare_actions ────────────────────────────────────────
    def _prepare_actions(self, inq_id):
        inq = _INQUIRIES[inq_id]
        r = _RESOLUTIONS[inq_id]
        before = inq["base_monthly"] + r["addon_monthly"]
        after = inq["base_monthly"]
        return (
            f"**Actions ready for your approval: {inq['customer']} ({inq_id})**\n\n"
            f"| Action | Status | Reference |\n|---|---|---|\n"
            f"| Refund ${r['addon_monthly']} | Ready to process | {r['refund_ref']} (proposed) |\n"
            f"| Cancel add-on | Ready | Immediate on approval |\n"
            f"| Block auto-enroll | Ready | Account flag |\n"
            f"| Apply ${r['credit']} credit | Ready | {r['credit_ref']} (proposed) |\n\n"
            f"**Account after approval:**\n\n| Before | After |\n|---|---|\n"
            f"| Monthly: ${before} | Monthly: ${after} |\n"
            f"| Credits: $0 | Credits: ${r['credit']} |\n\n"
            f"- Refund: ${r['addon_monthly']} to {inq['card']}, {r['refund_days']} after processing\n"
            f"- Communication: confirmation email drafted in the follow-up step, sent only by you\n\n"
            f"**Review gate:** nothing has been processed. Approve and submit these in the billing "
            f"system; the references are proposed IDs. {_READ_ONLY_NOTICE}\n\n"
            f"Source: [Synthetic Billing + Account Management]\nAgents: AICustomerAssistantAgent\n\n"
            f"Set up follow-up?"
        )

    # ── follow_up_plan ─────────────────────────────────────────
    def _follow_up_plan(self, inq_id):
        inq = _INQUIRIES[inq_id]
        r = _RESOLUTIONS[inq_id]
        rows = "\n".join(f"| {a} | {t} | {p} |" for a, t, p in r["follow_up"])
        return (
            f"**Follow-up plan and response draft for {inq['customer']}**\n\n"
            f"| Touchpoint | Timing | Purpose |\n|---|---|---|\n{rows}\n\n"
            f"**Draft Email**\n\n"
            f"Subject: {r['email_subject']}\n\n"
            f"Body: \"Thank you for bringing this up, and sincere apologies. Here's what we did: "
            f"${r['addon_monthly']} refund ({r['refund_ref']}); canceled the add-on; ${r['credit']} credit "
            f"applied; blocked auto-enrollments. The refund appears in {r['refund_days'].replace(' business days', ' days')}, "
            f"the credit is available now. We value your {inq['loyalty_years']} years with us.\"\n\n"
            f"**Approval:** ready for you to send once the refund and credit are processed; the "
            f"touchpoints are a proposed schedule for your task list.\n\n"
            f"**Review gate:** {_READ_ONLY_NOTICE}\n\n"
            f"Source: [Synthetic Task Management + Email Templates]\nAgents: AICustomerAssistantAgent\n\n"
            f"Generate session summary?"
        )

    # ── interaction_summary ────────────────────────────────────
    def _interaction_summary(self, inq_id):
        inq = _INQUIRIES[inq_id]
        r = _RESOLUTIONS[inq_id]
        m = r["summary"]
        arr = inq["base_monthly"] * 12
        ltv = arr * inq["loyalty_years"]
        cost = r["addon_monthly"] + r["credit"]
        roi = ltv // cost
        return (
            f"**Interaction Summary: {inq['customer']} ({inq_id})**\n\n"
            f"| Item | Detail |\n|---|---|\n"
            f"| Issue | {m['issue']} |\n"
            f"| Resolution | Full refund + ${r['credit']} credit (prepared for approval) |\n"
            f"| Outcome | Retained (predicted) |\n\n"
            f"**Quality Metrics:**\n\n| Metric | Score |\n|---|---|\n"
            f"| First contact resolution | {m['first_contact_resolution']} |\n"
            f"| Handle time | {m['handle_minutes']} minutes |\n"
            f"| Predicted CSAT | {m['predicted_csat']}/5 |\n"
            f"| Retention probability | {m['retention_probability_pct']}% |\n\n"
            f"**Value Protected:** ${arr:,}/year ARR, ${ltv:,}+ lifetime value vs ${cost} resolution "
            f"cost ({roi}x ROI)\n\n"
            f"**System Learning:** recommend flagging the issue to the product team "
            f"({m['similar_cases']} similar cases) and adding this resolution to the knowledge base.\n\n"
            f"**Review gate:** {_READ_ONLY_NOTICE}\n\n"
            f"Source: [Synthetic Service Systems]\nAgents: AICustomerAssistantAgent"
        )

    # ── handle_inquiry ─────────────────────────────────────────
    def _handle_inquiry(self, inq_id):
        inq = _INQUIRIES[inq_id]
        if inq.get("loyalty"):
            value = inq["base_monthly"] * 12
            return (
                f"**{inq['headline']}** ({inq['id']})\n\n"
                f"| Element | Finding |\n|---|---|\n"
                f"| Customer | {inq['customer']} |\n"
                f"| Loyalty | {inq['loyalty']} |\n"
                f"| Account value | ${value:,}/year |\n"
                f"| Sentiment | {inq['sentiment']} ({inq['sentiment_score']}) |\n"
                f"| Channel | {inq['channel']} |\n\n"
                f"**Inquiry:** \"{inq['description']}\"\n\n"
                f"**Context:** {inq['context']}\n\n"
                f"**Risk:** High churn threat, ${value:,} at risk\n\n"
                f"**Review gate:** {_READ_ONLY_NOTICE}\n\n"
                f"Source: [Synthetic CRM + Billing]\nAgents: AICustomerAssistantAgent\n\n"
                f"Search knowledge base?"
            )
        kb_matches = _match_kb_articles(inq_id)
        routing = _get_routing(inq["category"], inq["priority"])
        top_kb = kb_matches[0] if kb_matches else None
        kb_line = f"- Suggested Article: [{top_kb['id']}] {top_kb['title']} (relevance: {top_kb['relevance_score']:.0%})" if top_kb else "- No matching articles found"
        return (
            f"**Customer Inquiry: {inq['id']}**\n\n"
            f"| Field | Detail |\n|---|---|\n"
            f"| Customer | {inq['customer']} ({inq['account_tier']}) |\n"
            f"| Contact | {inq['contact']} |\n"
            f"| Channel | {inq['channel']} |\n"
            f"| Category | {inq['category']} |\n"
            f"| Priority | {inq['priority']} |\n"
            f"| Sentiment | {inq['sentiment']} |\n\n"
            f"**Subject:** {inq['subject']}\n\n"
            f"**Description:** {inq['description']}\n\n"
            f"**Recommended Response:**\n"
            f"{kb_line}\n"
            f"- Assigned Team: {routing['team']}\n"
            f"- SLA Target: {routing['sla_hours']} hours\n"
            f"- Escalation Rule Triggered: {'Yes' if routing['auto_escalate'] else 'No'}\n\n"
            f"**Review gate:** This recommendation does not execute the route. "
            f"{_READ_ONLY_NOTICE}\n\n"
            f"Source: [Synthetic CRM + Knowledge Base + Ticketing Snapshot]\nAgents: AICustomerAssistantAgent"
        )

    # ── knowledge_search ───────────────────────────────────────
    def _knowledge_search(self, inq_id):
        articles = _match_kb_articles(inq_id)
        inq = _INQUIRIES[inq_id]
        top = articles[0]
        if top.get("finding"):
            rows = "\n".join(f"| {k} | {v} |" for k, v in top["finding"])
            return (
                f"**Issue identified - auto-enrollment promo, refund eligible** ({inq['id']})\n\n"
                f"Top match: [{top['id']}] {top['title']}\n\n"
                f"| Finding | Details |\n|---|---|\n{rows}\n\n"
                f"**Policy:** {top['policy']}\n\n"
                f"**Similar Cases:** {top['similar_cases']}\n\n"
                f"**Resolution Steps:**\n"
                + "\n".join(f"{i + 1}. {x}" for i, x in enumerate(top["resolution_steps"])) + "\n\n"
                f"**Review gate:** {_READ_ONLY_NOTICE}\n\n"
                f"Source: [Synthetic Knowledge Base + Billing]\nAgents: AICustomerAssistantAgent\n\n"
                f"Get recommended actions?"
            )
        rows = ""
        for a in articles:
            rows += f"| {a['id']} | {a['title']} | {a['relevance_score']:.0%} | {a['views']:,} |\n"
        top = articles[0] if articles else None
        steps = ""
        if top:
            steps = "\n".join(f"{i+1}. {s}" for i, s in enumerate(top["resolution_steps"]))
        return (
            f"**Knowledge Base Search Results**\n"
            f"Query: \"{inq['subject']}\"\n\n"
            f"| Article ID | Title | Relevance | Views |\n|---|---|---|---|\n"
            f"{rows}\n"
            f"**Top Match: {top['title'] if top else 'N/A'}**\n\n"
            f"**Summary:** {top['summary'] if top else 'N/A'}\n\n"
            f"**Resolution Steps:**\n{steps}\n\n"
            f"Last Updated: {top['last_updated'] if top else 'N/A'} | "
            f"Helpful Votes: {top['helpful_votes']:,} / {top['views']:,} views\n\n"
            f"**Review gate:** {_READ_ONLY_NOTICE}\n\n"
            f"Source: [Synthetic Knowledge Base]\nAgents: AICustomerAssistantAgent"
        )

    # ── escalation_routing ─────────────────────────────────────
    def _escalation_routing(self, inq_id):
        inq = _INQUIRIES[inq_id]
        routing = _get_routing(inq["category"], inq["priority"])
        all_routes = []
        for cat, priorities in _ROUTING_RULES.items():
            for pri, rule in priorities.items():
                all_routes.append(
                    f"| {cat} | {pri} | {rule['team']} | "
                    f"{rule['sla_hours']} hours |"
                )
        route_rows = "\n".join(all_routes)
        return (
            f"**Escalation Routing: {inq['id']}**\n\n"
            f"| Field | Detail |\n|---|---|\n"
            f"| Category | {inq['category']} |\n"
            f"| Priority | {inq['priority']} |\n"
            f"| Assigned Team | {routing['team']} |\n"
            f"| SLA Target | {routing['sla_hours']} hours |\n"
            f"| Escalation Rule Triggered | {'Yes' if routing['auto_escalate'] else 'No'} |\n\n"
            f"**Routing Matrix:**\n\n"
            f"| Category | Priority | Team | SLA |\n|---|---|---|---|\n"
            f"{route_rows}\n\n"
            f"**Review gate:** This recommendation does not execute the route. "
            f"{_READ_ONLY_NOTICE}\n\n"
            f"Source: [Synthetic Routing Rules + SLA Configuration]\nAgents: AICustomerAssistantAgent"
        )

    # ── satisfaction_survey ─────────────────────────────────────
    def _satisfaction_survey(self, inq_id):
        data = _SATISFACTION_DATA
        dist, promoters, detractors, total = _compute_csat_breakdown()
        survey_rows = ""
        for s in data["surveys"]:
            stars = "*" * s["score"]
            survey_rows += f"| {s['inquiry_id']} | {stars} ({s['score']}/5) | {s['comment'][:50]} | {s['date']} |\n"
        dist_rows = "\n".join(f"| {score} Star | {count} ({count/total*100:.0f}%) |" for score, count in sorted(dist.items(), reverse=True))
        return (
            f"**Customer Satisfaction Dashboard**\n\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| Overall CSAT | {data['overall_csat']}/5.0 |\n"
            f"| NPS Score | {data['nps_score']} |\n"
            f"| Avg Response Time | {data['response_time_avg_minutes']} minutes |\n"
            f"| First Contact Resolution | {data['first_contact_resolution_rate']:.0%} |\n\n"
            f"**Score Distribution:**\n\n"
            f"| Rating | Count |\n|---|---|\n"
            f"{dist_rows}\n\n"
            f"**Recent Surveys:**\n\n"
            f"| Inquiry | Rating | Comment | Date |\n|---|---|---|---|\n"
            f"{survey_rows}\n"
            f"**Trends:** WoW {data['trend']['week_over_week']}, MoM {data['trend']['month_over_month']}\n\n"
            f"All comments are fictional pilot records. {_READ_ONLY_NOTICE}\n\n"
            f"Source: [Synthetic Survey + CRM Analytics Snapshot]\nAgents: AICustomerAssistantAgent"
        )


if __name__ == "__main__":
    agent = AICustomerAssistantAgent()
    for op in ["handle_inquiry", "knowledge_search", "recommend_resolution", "prepare_actions",
               "follow_up_plan", "interaction_summary"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
