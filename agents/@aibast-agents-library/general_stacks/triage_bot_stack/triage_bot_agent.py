"""
Triage Bot Agent

Classifies incoming inquiries, routes to appropriate teams, assesses priority,
and generates handoff summaries for seamless escalation.

Where a real deployment would connect to ticketing and routing systems, this
agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/triage-bot",
    "version": "1.0.0",
    "display_name": "Triage Bot",
    "description": "Inquiry classification, routing, priority assessment, and handoff summary generation.",
    "author": "AIBAST",
    "tags": ["triage", "classification", "routing", "priority", "handoff"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_INQUIRY_CATEGORIES = {
    "technical_support": {"label": "Technical Support", "description": "Product issues, bugs, performance problems", "team": "Technical Support", "avg_handle_min": 25, "sla_hours": 4},
    "billing": {"label": "Billing & Payments", "description": "Invoices, payment issues, plan changes", "team": "Billing Team", "avg_handle_min": 15, "sla_hours": 8},
    "sales": {"label": "Sales Inquiry", "description": "Pricing, demos, new purchases", "team": "Sales Team", "avg_handle_min": 20, "sla_hours": 2},
    "account_management": {"label": "Account Management", "description": "Renewals, upgrades, account changes", "team": "Account Management", "avg_handle_min": 30, "sla_hours": 8},
    "feature_request": {"label": "Feature Request", "description": "New feature suggestions, enhancements", "team": "Product Team", "avg_handle_min": 10, "sla_hours": 72},
    "security": {"label": "Security Concern", "description": "Security incidents, compliance, data privacy", "team": "Security Team", "avg_handle_min": 35, "sla_hours": 1},
}

_ROUTING_RULES = {
    "technical_support": {"primary_team": "Technical Support", "escalation_team": "Engineering", "auto_assign": True, "skill_required": "product_knowledge", "after_hours": "On-Call Engineer"},
    "billing": {"primary_team": "Billing Team", "escalation_team": "Finance", "auto_assign": True, "skill_required": "billing_systems", "after_hours": "Billing Queue"},
    "sales": {"primary_team": "Sales Team", "escalation_team": "Sales Management", "auto_assign": False, "skill_required": "sales_qualification", "after_hours": "Lead Queue"},
    "account_management": {"primary_team": "Account Management", "escalation_team": "VP Customer Success", "auto_assign": True, "skill_required": "account_strategy", "after_hours": "CSM Queue"},
    "feature_request": {"primary_team": "Product Team", "escalation_team": "Product Management", "auto_assign": False, "skill_required": "product_strategy", "after_hours": "Product Backlog"},
    "security": {"primary_team": "Security Team", "escalation_team": "CISO", "auto_assign": True, "skill_required": "security_ops", "after_hours": "Security On-Call"},
}

_PRIORITY_MATRIX = {
    "impact_high_urgency_high": {"priority": "P1-Critical", "response_min": 15, "resolution_hours": 1, "auto_escalate": True},
    "impact_high_urgency_medium": {"priority": "P2-High", "response_min": 30, "resolution_hours": 4, "auto_escalate": False},
    "impact_high_urgency_low": {"priority": "P3-Medium", "response_min": 60, "resolution_hours": 8, "auto_escalate": False},
    "impact_medium_urgency_high": {"priority": "P2-High", "response_min": 30, "resolution_hours": 4, "auto_escalate": False},
    "impact_medium_urgency_medium": {"priority": "P3-Medium", "response_min": 60, "resolution_hours": 8, "auto_escalate": False},
    "impact_medium_urgency_low": {"priority": "P4-Low", "response_min": 120, "resolution_hours": 24, "auto_escalate": False},
    "impact_low_urgency_high": {"priority": "P3-Medium", "response_min": 60, "resolution_hours": 8, "auto_escalate": False},
    "impact_low_urgency_medium": {"priority": "P4-Low", "response_min": 120, "resolution_hours": 24, "auto_escalate": False},
    "impact_low_urgency_low": {"priority": "P5-Informational", "response_min": 240, "resolution_hours": 72, "auto_escalate": False},
}

_HANDOFF_TEMPLATES = {
    "technical_escalation": {
        "template_name": "Technical Escalation", "sections": ["Customer Information", "Issue Description", "Steps Taken", "Environment Details", "Business Impact", "Recommended Next Steps"],
    },
    "management_escalation": {
        "template_name": "Management Escalation", "sections": ["Customer Information", "Account Value", "Issue History", "Customer Sentiment", "Risk Assessment", "Recommended Action"],
    },
    "cross_team": {
        "template_name": "Cross-Team Handoff", "sections": ["Customer Information", "Original Category", "Reason for Transfer", "Context Summary", "Outstanding Questions"],
    },
}

_SAMPLE_INQUIRIES = [
    {"id": "INQ-T001", "text": "Our entire sales team can't access the platform. Getting 500 errors for the past 30 minutes.", "customer": "Meridian Corp", "tier": "Enterprise", "impact": "high", "urgency": "high", "classified_as": "technical_support", "confidence": 0.97},
    {"id": "INQ-T002", "text": "I'd like to understand the pricing for your Analytics Pro module for 200 users.", "customer": "New Prospect", "tier": "Unknown", "impact": "low", "urgency": "medium", "classified_as": "sales", "confidence": 0.94},
    {"id": "INQ-T003", "text": "We received a duplicate invoice for November. Can you check?", "customer": "Atlas Digital", "tier": "Mid-Market", "impact": "medium", "urgency": "low", "classified_as": "billing", "confidence": 0.96},
    {"id": "INQ-T004", "text": "We noticed unauthorized API calls from an unknown IP. Need immediate investigation.", "customer": "BlueHorizon Health", "tier": "Enterprise", "impact": "high", "urgency": "high", "classified_as": "security", "confidence": 0.99},
]


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _classify_inquiry(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["error", "not working", "can't access", "bug", "crash"]):
        return "technical_support", 0.95
    if any(w in text_lower for w in ["pricing", "demo", "purchase", "quote"]):
        return "sales", 0.92
    if any(w in text_lower for w in ["invoice", "payment", "billing", "charge"]):
        return "billing", 0.94
    if any(w in text_lower for w in ["security", "unauthorized", "breach", "privacy"]):
        return "security", 0.97
    if any(w in text_lower for w in ["feature", "enhancement", "wish", "suggestion"]):
        return "feature_request", 0.88
    return "account_management", 0.75


def _assess_priority(impact, urgency):
    key = f"impact_{impact}_urgency_{urgency}"
    return _PRIORITY_MATRIX.get(key, _PRIORITY_MATRIX["impact_medium_urgency_medium"])


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class TriageBotAgent(BasicAgent):
    """
    Inquiry triage and routing agent.

    Operations:
        classify_inquiry    - classify an inquiry by category
        route_request       - determine routing for an inquiry
        priority_assessment - assess priority based on impact/urgency
        handoff_summary     - generate a handoff summary for escalation
    """

    def __init__(self):
        self.name = "TriageBotAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "classify_inquiry", "route_request",
                            "priority_assessment", "handoff_summary",
                        ],
                        "description": "The triage operation to perform",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "classify_inquiry")
        dispatch = {
            "classify_inquiry": self._classify_inquiry,
            "route_request": self._route_request,
            "priority_assessment": self._priority_assessment,
            "handoff_summary": self._handoff_summary,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler()

    def _classify_inquiry(self):
        rows = ""
        for inq in _SAMPLE_INQUIRIES:
            cat = _INQUIRY_CATEGORIES[inq["classified_as"]]
            rows += f"| {inq['id']} | {inq['text'][:45]}... | {cat['label']} | {inq['confidence']:.0%} | {inq['customer']} |\n"
        cat_rows = ""
        for key, cat in _INQUIRY_CATEGORIES.items():
            cat_rows += f"| {cat['label']} | {cat['description'][:40]} | {cat['team']} | {cat['sla_hours']}h |\n"
        return (
            f"**Inquiry Classification Results**\n\n"
            f"| ID | Inquiry | Category | Confidence | Customer |\n|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Category Definitions:**\n\n"
            f"| Category | Description | Team | SLA |\n|---|---|---|---|\n"
            f"{cat_rows}\n\n"
            f"Source: [Classification Engine + NLP]\nAgents: TriageBotAgent"
        )

    def _route_request(self):
        route_rows = ""
        for cat_key, rule in _ROUTING_RULES.items():
            cat = _INQUIRY_CATEGORIES[cat_key]
            auto = "Yes" if rule["auto_assign"] else "No"
            route_rows += f"| {cat['label']} | {rule['primary_team']} | {rule['escalation_team']} | {auto} | {rule['after_hours']} |\n"
        sample = _SAMPLE_INQUIRIES[0]
        sample_route = _ROUTING_RULES[sample["classified_as"]]
        return (
            f"**Routing Configuration**\n\n"
            f"| Category | Primary Team | Escalation | Auto-Assign | After Hours |\n|---|---|---|---|---|\n"
            f"{route_rows}\n"
            f"**Example Routing: {sample['id']}**\n"
            f"- Inquiry: {sample['text'][:50]}...\n"
            f"- Route to: {sample_route['primary_team']}\n"
            f"- Skill required: {sample_route['skill_required']}\n"
            f"- Auto-assign: {'Yes' if sample_route['auto_assign'] else 'No'}\n\n"
            f"Source: [Routing Engine]\nAgents: TriageBotAgent"
        )

    def _priority_assessment(self):
        priority_rows = ""
        for key, p in _PRIORITY_MATRIX.items():
            parts = key.split("_")
            impact = parts[1]
            urgency = parts[3]
            auto = "Yes" if p["auto_escalate"] else "No"
            priority_rows += f"| {impact.title()} | {urgency.title()} | {p['priority']} | {p['response_min']}m | {p['resolution_hours']}h | {auto} |\n"
        sample_rows = ""
        for inq in _SAMPLE_INQUIRIES:
            p = _assess_priority(inq["impact"], inq["urgency"])
            sample_rows += f"| {inq['id']} | {inq['impact'].title()} | {inq['urgency'].title()} | {p['priority']} | {p['response_min']}m |\n"
        return (
            f"**Priority Assessment**\n\n"
            f"**Sample Inquiries:**\n\n"
            f"| ID | Impact | Urgency | Priority | Response Time |\n|---|---|---|---|---|\n"
            f"{sample_rows}\n"
            f"**Priority Matrix:**\n\n"
            f"| Impact | Urgency | Priority | Response | Resolution | Auto-Escalate |\n|---|---|---|---|---|---|\n"
            f"{priority_rows}\n\n"
            f"Source: [Priority Engine]\nAgents: TriageBotAgent"
        )

    def _handoff_summary(self):
        inq = _SAMPLE_INQUIRIES[0]
        p = _assess_priority(inq["impact"], inq["urgency"])
        route = _ROUTING_RULES[inq["classified_as"]]
        template = _HANDOFF_TEMPLATES["technical_escalation"]
        sections = "\n".join(f"- {s}" for s in template["sections"])
        return (
            f"**Handoff Summary: {inq['id']}**\n\n"
            f"**Customer:** {inq['customer']} ({inq['tier']})\n"
            f"**Category:** {_INQUIRY_CATEGORIES[inq['classified_as']]['label']}\n"
            f"**Priority:** {p['priority']}\n\n"
            f"**Issue:** {inq['text']}\n\n"
            f"**Routing:**\n"
            f"- Assigned to: {route['primary_team']}\n"
            f"- Escalation path: {route['escalation_team']}\n"
            f"- Response SLA: {p['response_min']} minutes\n"
            f"- Resolution SLA: {p['resolution_hours']} hours\n"
            f"- Auto-escalate: {'Yes' if p['auto_escalate'] else 'No'}\n\n"
            f"**Handoff Template:** {template['template_name']}\n"
            f"**Sections:**\n{sections}\n\n"
            f"Source: [Triage Engine + Routing]\nAgents: TriageBotAgent"
        )


if __name__ == "__main__":
    agent = TriageBotAgent()
    for op in ["classify_inquiry", "route_request", "priority_assessment", "handoff_summary"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
