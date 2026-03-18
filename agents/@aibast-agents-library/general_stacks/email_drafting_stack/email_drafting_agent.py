"""
Email Drafting Agent

AI-powered email composition for outreach, follow-ups, proposals, and
template management with personalization and tone control.

Where a real deployment would integrate with email services and CRM,
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
    "name": "@aibast-agents-library/email-drafting",
    "version": "1.0.0",
    "display_name": "Email Drafting",
    "description": "AI-powered email drafting for outreach, follow-ups, proposals, and template management with personalization.",
    "author": "AIBAST",
    "tags": ["email", "drafting", "outreach", "follow-up", "proposal", "templates"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_EMAIL_TEMPLATES = {
    "cold_outreach": {
        "name": "Cold Outreach", "category": "Prospecting",
        "subject_variants": [
            "{company_name} + {our_product} - Quick Question",
            "Idea for {company_name}'s {pain_point}",
            "{first_name}, saw your post on {topic}",
        ],
        "body": "Hi {first_name},\n\nI noticed {company_name} has been {observation}. Many {industry} leaders we work with have faced similar challenges around {pain_point}.\n\nWe helped {reference_customer} achieve {result} using our {product_name}.\n\nWould you be open to a 15-minute call next week to explore if we could deliver similar results for your team?\n\nBest regards,\n{sender_name}\n{sender_title}",
        "tone": "Professional, consultative",
        "avg_open_rate": 0.32, "avg_reply_rate": 0.08,
    },
    "follow_up_no_reply": {
        "name": "Follow-Up (No Reply)", "category": "Follow-Up",
        "subject_variants": [
            "Re: {original_subject}",
            "Quick follow-up, {first_name}",
            "Still relevant, {first_name}?",
        ],
        "body": "Hi {first_name},\n\nI wanted to follow up on my previous email about {topic}. I understand you're busy, so I'll keep this brief.\n\n{value_prop_one_liner}\n\nI have a few times available this week if you'd like to connect:\n- {time_slot_1}\n- {time_slot_2}\n\nIf the timing isn't right, no worries - just let me know and I'll circle back later.\n\nBest,\n{sender_name}",
        "tone": "Friendly, low-pressure",
        "avg_open_rate": 0.28, "avg_reply_rate": 0.12,
    },
    "proposal_intro": {
        "name": "Proposal Introduction", "category": "Proposal",
        "subject_variants": [
            "Proposal: {project_name} for {company_name}",
            "{company_name} Partnership Proposal",
        ],
        "body": "Dear {first_name},\n\nThank you for the productive conversation on {meeting_date}. As discussed, I'm pleased to share our proposal for {project_name}.\n\n**Executive Summary:**\n{executive_summary}\n\n**Investment:** {pricing}\n**Timeline:** {timeline}\n**Expected ROI:** {roi_projection}\n\nThe attached document contains the full proposal with technical specifications, implementation plan, and customer references.\n\nI'd welcome the opportunity to walk through this with your team. Would {proposed_meeting_date} work for a review session?\n\nBest regards,\n{sender_name}\n{sender_title}",
        "tone": "Formal, value-focused",
        "avg_open_rate": 0.65, "avg_reply_rate": 0.45,
    },
    "meeting_follow_up": {
        "name": "Post-Meeting Follow-Up", "category": "Follow-Up",
        "subject_variants": [
            "Great meeting, {first_name} - Next steps",
            "Summary: {meeting_topic} discussion",
        ],
        "body": "Hi {first_name},\n\nThank you for your time today discussing {meeting_topic}. Here's a quick recap:\n\n**Key Discussion Points:**\n{discussion_points}\n\n**Action Items:**\n{action_items}\n\n**Next Steps:**\n{next_steps}\n\nPlease let me know if I missed anything or if you have questions.\n\nBest,\n{sender_name}",
        "tone": "Professional, action-oriented",
        "avg_open_rate": 0.72, "avg_reply_rate": 0.38,
    },
}

_PERSONALIZATION_FIELDS = {
    "recipient": ["first_name", "last_name", "title", "company_name", "industry"],
    "context": ["pain_point", "observation", "topic", "meeting_date", "meeting_topic"],
    "value": ["product_name", "reference_customer", "result", "roi_projection", "pricing"],
    "sender": ["sender_name", "sender_title", "sender_email", "sender_phone"],
    "scheduling": ["time_slot_1", "time_slot_2", "proposed_meeting_date"],
}

_TONE_SETTINGS = {
    "professional": {"formality": "High", "warmth": "Medium", "urgency": "Low", "use_case": "Enterprise outreach, formal proposals"},
    "consultative": {"formality": "Medium", "warmth": "High", "urgency": "Low", "use_case": "Discovery calls, advisory communications"},
    "friendly": {"formality": "Low", "warmth": "High", "urgency": "Low", "use_case": "Follow-ups, relationship maintenance"},
    "urgent": {"formality": "Medium", "warmth": "Low", "urgency": "High", "use_case": "Time-sensitive offers, renewal deadlines"},
    "executive": {"formality": "High", "warmth": "Low", "urgency": "Medium", "use_case": "C-suite communications, board summaries"},
}

_SAMPLE_CONTEXT = {
    "first_name": "Jennifer", "last_name": "Walsh", "title": "VP of Operations",
    "company_name": "TechVantage Solutions", "industry": "Technology",
    "pain_point": "operational efficiency", "observation": "expanding rapidly into new markets",
    "topic": "digital transformation", "product_name": "Enterprise Platform",
    "reference_customer": "Meridian Corp", "result": "35% improvement in operational throughput",
    "sender_name": "Alex Rivera", "sender_title": "Account Executive",
    "meeting_date": "November 12", "meeting_topic": "platform evaluation",
    "pricing": "$185,000/year", "roi_projection": "3.2x within 18 months",
    "time_slot_1": "Tuesday 2:00 PM", "time_slot_2": "Thursday 10:00 AM",
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _render_template(template_key, context):
    template = _EMAIL_TEMPLATES.get(template_key, {})
    body = template.get("body", "")
    for key, value in context.items():
        body = body.replace(f"{{{key}}}", str(value))
    subject = template["subject_variants"][0] if template.get("subject_variants") else "No Subject"
    for key, value in context.items():
        subject = subject.replace(f"{{{key}}}", str(value))
    return subject, body


def _count_personalization_tokens(template_body):
    count = 0
    i = 0
    while i < len(template_body):
        if template_body[i] == '{':
            j = template_body.find('}', i)
            if j != -1:
                count += 1
                i = j + 1
            else:
                i += 1
        else:
            i += 1
    return count


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class EmailDraftingAgent(BasicAgent):
    """
    Email drafting assistant.

    Operations:
        draft_outreach   - compose initial outreach emails
        draft_follow_up  - compose follow-up emails
        draft_proposal   - compose proposal introduction emails
        template_library - browse and inspect email templates
    """

    def __init__(self):
        self.name = "EmailDraftingAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "draft_outreach", "draft_follow_up",
                            "draft_proposal", "template_library",
                        ],
                        "description": "The email drafting operation to perform",
                    },
                    "template_key": {
                        "type": "string",
                        "description": "Template key (e.g. 'cold_outreach')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "template_library")
        dispatch = {
            "draft_outreach": self._draft_outreach,
            "draft_follow_up": self._draft_follow_up,
            "draft_proposal": self._draft_proposal,
            "template_library": self._template_library,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(kwargs)

    # ── draft_outreach ─────────────────────────────────────────
    def _draft_outreach(self, params):
        subject, body = _render_template("cold_outreach", _SAMPLE_CONTEXT)
        t = _EMAIL_TEMPLATES["cold_outreach"]
        return (
            f"**Draft: Cold Outreach Email**\n\n"
            f"**To:** {_SAMPLE_CONTEXT['first_name']} {_SAMPLE_CONTEXT['last_name']} <{_SAMPLE_CONTEXT['first_name'].lower()}.{_SAMPLE_CONTEXT['last_name'].lower()}@techvantage.com>\n"
            f"**Subject:** {subject}\n"
            f"**Tone:** {t['tone']}\n\n"
            f"---\n\n{body}\n\n---\n\n"
            f"**Performance Benchmarks:**\n"
            f"- Avg Open Rate: {t['avg_open_rate']:.0%}\n"
            f"- Avg Reply Rate: {t['avg_reply_rate']:.0%}\n\n"
            f"**Subject Line Variants:**\n"
            + "\n".join(f"- {s}" for s in t["subject_variants"]) + "\n\n"
            f"Source: [Email Template Engine]\nAgents: EmailDraftingAgent"
        )

    # ── draft_follow_up ────────────────────────────────────────
    def _draft_follow_up(self, params):
        subject, body = _render_template("follow_up_no_reply", _SAMPLE_CONTEXT)
        t = _EMAIL_TEMPLATES["follow_up_no_reply"]
        return (
            f"**Draft: Follow-Up Email**\n\n"
            f"**To:** {_SAMPLE_CONTEXT['first_name']} {_SAMPLE_CONTEXT['last_name']}\n"
            f"**Subject:** {subject}\n"
            f"**Tone:** {t['tone']}\n\n"
            f"---\n\n{body}\n\n---\n\n"
            f"**Performance Benchmarks:**\n"
            f"- Avg Open Rate: {t['avg_open_rate']:.0%}\n"
            f"- Avg Reply Rate: {t['avg_reply_rate']:.0%}\n\n"
            f"**Best Practices:**\n"
            f"- Send 3-5 business days after initial email\n"
            f"- Keep under 100 words\n"
            f"- Include specific time slots\n"
            f"- Provide easy opt-out\n\n"
            f"Source: [Email Template Engine]\nAgents: EmailDraftingAgent"
        )

    # ── draft_proposal ─────────────────────────────────────────
    def _draft_proposal(self, params):
        subject, body = _render_template("proposal_intro", _SAMPLE_CONTEXT)
        t = _EMAIL_TEMPLATES["proposal_intro"]
        return (
            f"**Draft: Proposal Introduction Email**\n\n"
            f"**To:** {_SAMPLE_CONTEXT['first_name']} {_SAMPLE_CONTEXT['last_name']}\n"
            f"**Subject:** {subject}\n"
            f"**Tone:** {t['tone']}\n\n"
            f"---\n\n{body}\n\n---\n\n"
            f"**Performance Benchmarks:**\n"
            f"- Avg Open Rate: {t['avg_open_rate']:.0%}\n"
            f"- Avg Reply Rate: {t['avg_reply_rate']:.0%}\n\n"
            f"**Attachments Suggested:**\n"
            f"- Full proposal PDF\n"
            f"- ROI calculator spreadsheet\n"
            f"- Customer reference one-pager\n\n"
            f"Source: [Email Template Engine]\nAgents: EmailDraftingAgent"
        )

    # ── template_library ───────────────────────────────────────
    def _template_library(self, params):
        template_rows = ""
        for key, t in _EMAIL_TEMPLATES.items():
            tokens = _count_personalization_tokens(t["body"])
            template_rows += f"| {key} | {t['name']} | {t['category']} | {t['avg_open_rate']:.0%} | {t['avg_reply_rate']:.0%} | {tokens} |\n"
        tone_rows = ""
        for tone, settings in _TONE_SETTINGS.items():
            tone_rows += f"| {tone.title()} | {settings['formality']} | {settings['warmth']} | {settings['urgency']} | {settings['use_case'][:40]} |\n"
        field_categories = "\n".join(f"- **{cat.title()}:** {', '.join(fields)}" for cat, fields in _PERSONALIZATION_FIELDS.items())
        return (
            f"**Email Template Library**\n\n"
            f"| Key | Name | Category | Open Rate | Reply Rate | Tokens |\n|---|---|---|---|---|---|\n"
            f"{template_rows}\n"
            f"**Tone Settings:**\n\n"
            f"| Tone | Formality | Warmth | Urgency | Use Case |\n|---|---|---|---|---|\n"
            f"{tone_rows}\n"
            f"**Personalization Fields:**\n{field_categories}\n\n"
            f"Source: [Email Template Engine]\nAgents: EmailDraftingAgent"
        )


if __name__ == "__main__":
    agent = EmailDraftingAgent()
    for op in ["draft_outreach", "draft_follow_up", "draft_proposal", "template_library"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
