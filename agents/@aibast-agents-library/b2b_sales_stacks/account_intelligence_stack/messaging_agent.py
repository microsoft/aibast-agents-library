"""
Account Messaging Agent

Generates personalized outreach sequences, follow-up emails, proposal
introductions, and multi-touch campaign sequences for enterprise B2B
accounts. Optimizes messaging based on stakeholder role, engagement
history, and response analytics.

Where a real deployment would call email platforms and CRM APIs, this
agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent
import json
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/account-messaging",
    "version": "1.0.0",
    "display_name": "Account Messaging",
    "description": "Generates personalized outreach, follow-ups, and campaign sequences for enterprise accounts.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "messaging", "outreach", "email-sequences"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_ACCOUNTS = {
    "acme": {
        "id": "acc-001", "name": "Acme Corporation", "industry": "Manufacturing",
        "revenue": 2_800_000_000, "employees": 12_400, "hq": "Chicago, IL",
        "current_spend": 1_200_000, "opportunity_value": 2_400_000,
        "pain_points": ["legacy ERP integration", "manual reporting", "supply chain visibility"],
    },
    "contoso": {
        "id": "acc-002", "name": "Contoso Ltd", "industry": "Technology",
        "revenue": 980_000_000, "employees": 4_200, "hq": "Redmond, WA",
        "current_spend": 680_000, "opportunity_value": 1_100_000,
        "pain_points": ["scaling data infrastructure", "EMEA compliance", "vendor consolidation"],
    },
    "fabrikam": {
        "id": "acc-003", "name": "Fabrikam Industries", "industry": "Manufacturing",
        "revenue": 1_500_000_000, "employees": 8_700, "hq": "Detroit, MI",
        "current_spend": 450_000, "opportunity_value": 890_000,
        "pain_points": ["production downtime analytics", "quality control automation", "workforce scheduling"],
    },
    "northwind": {
        "id": "acc-004", "name": "Northwind Traders", "industry": "Retail",
        "revenue": 620_000_000, "employees": 3_100, "hq": "Portland, OR",
        "current_spend": 220_000, "opportunity_value": 540_000,
        "pain_points": ["omnichannel inventory", "customer data platform", "last-mile logistics"],
    },
}

_STAKEHOLDERS = {
    "acme": [
        {"name": "Sarah Chen", "role": "CTO", "influence": "Decision Maker", "email_pref": "concise_technical", "last_email_days_ago": None, "open_rate": 0.0, "reply_rate": 0.0},
        {"name": "James Miller", "role": "VP Operations", "influence": "Champion", "email_pref": "roi_focused", "last_email_days_ago": 3, "open_rate": 0.82, "reply_rate": 0.45},
        {"name": "Lisa Park", "role": "CFO", "influence": "Economic Buyer", "email_pref": "executive_summary", "last_email_days_ago": 14, "open_rate": 0.65, "reply_rate": 0.20},
        {"name": "David Wong", "role": "IT Director", "influence": "Influencer", "email_pref": "concise_technical", "last_email_days_ago": 7, "open_rate": 0.78, "reply_rate": 0.35},
    ],
    "contoso": [
        {"name": "Alex Kim", "role": "CTO", "influence": "Decision Maker", "email_pref": "concise_technical", "last_email_days_ago": 5, "open_rate": 0.88, "reply_rate": 0.52},
        {"name": "Pat Johnson", "role": "CFO", "influence": "Economic Buyer", "email_pref": "executive_summary", "last_email_days_ago": 21, "open_rate": 0.55, "reply_rate": 0.15},
    ],
    "fabrikam": [
        {"name": "Chris Anderson", "role": "VP IT", "influence": "Decision Maker", "email_pref": "roi_focused", "last_email_days_ago": 10, "open_rate": 0.72, "reply_rate": 0.28},
        {"name": "Dana White", "role": "COO", "influence": "Champion", "email_pref": "roi_focused", "last_email_days_ago": 4, "open_rate": 0.85, "reply_rate": 0.40},
    ],
    "northwind": [
        {"name": "Jordan Lee", "role": "CTO", "influence": "Decision Maker", "email_pref": "concise_technical", "last_email_days_ago": 30, "open_rate": 0.50, "reply_rate": 0.10},
    ],
}

_EMAIL_TEMPLATES = {
    "concise_technical": {
        "subject_pattern": "Quick technical overview: {topic}",
        "tone": "Direct, data-driven, minimal fluff",
        "max_words": 150,
        "cta_style": "15-min technical walkthrough",
    },
    "roi_focused": {
        "subject_pattern": "{value_prop} for {company}",
        "tone": "Business outcome oriented, metrics-heavy",
        "max_words": 200,
        "cta_style": "ROI calculator review",
    },
    "executive_summary": {
        "subject_pattern": "Strategic alignment: {company} + {our_company}",
        "tone": "High-level, strategic, peer-to-peer",
        "max_words": 120,
        "cta_style": "Executive briefing (20 min)",
    },
}

_MESSAGING_HISTORY = {
    "acme": {
        "total_emails_sent": 34, "total_opens": 24, "total_replies": 11,
        "avg_open_rate": 0.71, "avg_reply_rate": 0.32,
        "best_subject": "3 manufacturing CTO references for your ERP modernization",
        "best_day": "Tuesday", "best_time": "9:15 AM CT",
        "sequences_active": 2, "sequences_completed": 3,
    },
    "contoso": {
        "total_emails_sent": 18, "total_opens": 14, "total_replies": 7,
        "avg_open_rate": 0.78, "avg_reply_rate": 0.39,
        "best_subject": "Scaling data infrastructure post Series D",
        "best_day": "Wednesday", "best_time": "10:30 AM PT",
        "sequences_active": 1, "sequences_completed": 2,
    },
    "fabrikam": {
        "total_emails_sent": 12, "total_opens": 8, "total_replies": 3,
        "avg_open_rate": 0.67, "avg_reply_rate": 0.25,
        "best_subject": "Production downtime reduction case study",
        "best_day": "Monday", "best_time": "8:00 AM ET",
        "sequences_active": 1, "sequences_completed": 1,
    },
    "northwind": {
        "total_emails_sent": 5, "total_opens": 2, "total_replies": 0,
        "avg_open_rate": 0.40, "avg_reply_rate": 0.0,
        "best_subject": "Omnichannel inventory for retail",
        "best_day": "Thursday", "best_time": "11:00 AM PT",
        "sequences_active": 0, "sequences_completed": 1,
    },
}

_RESPONSE_BENCHMARKS = {
    "cold_outreach": {"open_rate": 0.22, "reply_rate": 0.03},
    "warm_intro": {"open_rate": 0.55, "reply_rate": 0.18},
    "existing_relationship": {"open_rate": 0.72, "reply_rate": 0.35},
    "champion_referral": {"open_rate": 0.81, "reply_rate": 0.48},
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve_account(query):
    if not query:
        return "acme"
    q = query.lower().strip()
    for key in _ACCOUNTS:
        if key in q or q in _ACCOUNTS[key]["name"].lower():
            return key
    return "acme"


def _engagement_tier(stakeholder):
    """Classify stakeholder engagement level."""
    if stakeholder["last_email_days_ago"] is None:
        return "no_contact"
    if stakeholder["reply_rate"] >= 0.40:
        return "highly_engaged"
    if stakeholder["open_rate"] >= 0.60:
        return "moderately_engaged"
    return "low_engagement"


def _recommended_approach(stakeholder):
    """Determine messaging approach based on engagement."""
    tier = _engagement_tier(stakeholder)
    if tier == "no_contact":
        return "champion_referral"
    if tier == "highly_engaged":
        return "existing_relationship"
    if tier == "moderately_engaged":
        return "warm_intro"
    return "cold_outreach"


def _generate_subject(template_key, account, topic="platform capabilities"):
    tmpl = _EMAIL_TEMPLATES.get(template_key, _EMAIL_TEMPLATES["concise_technical"])
    return tmpl["subject_pattern"].format(
        topic=topic,
        value_prop=f"${account['opportunity_value']:,} efficiency opportunity",
        company=account["name"],
        our_company="TechVenture Solutions",
    )


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class MessagingAgent(BasicAgent):
    """
    Generates personalized B2B sales messaging.

    Operations:
        generate_outreach    - initial outreach emails per stakeholder
        create_follow_up     - follow-up drafts based on engagement
        draft_proposal_intro - proposal introduction email
        campaign_sequence    - multi-touch campaign plan
    """

    def __init__(self):
        self.name = "MessagingAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "generate_outreach", "create_follow_up",
                            "draft_proposal_intro", "campaign_sequence",
                        ],
                        "description": "The messaging operation to perform",
                    },
                    "account_name": {
                        "type": "string",
                        "description": "Account name (e.g. 'Acme Corporation')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "generate_outreach")
        key = _resolve_account(kwargs.get("account_name", ""))
        dispatch = {
            "generate_outreach": self._generate_outreach,
            "create_follow_up": self._create_follow_up,
            "draft_proposal_intro": self._draft_proposal_intro,
            "campaign_sequence": self._campaign_sequence,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`."
        return handler(key)

    # ── generate_outreach ─────────────────────────────────────
    def _generate_outreach(self, key):
        acct = _ACCOUNTS[key]
        stks = _STAKEHOLDERS.get(key, [])
        history = _MESSAGING_HISTORY.get(key, {})

        output = (
            f"**Outreach Drafts: {acct['name']}**\n\n"
            f"Account context: {acct['industry']}, ${acct['revenue']:,} revenue, "
            f"pain points: {', '.join(acct['pain_points'])}\n"
            f"Historical performance: {history.get('avg_open_rate', 0):.0%} open rate, "
            f"{history.get('avg_reply_rate', 0):.0%} reply rate\n"
            f"Best send window: {history.get('best_day', 'Tuesday')} at {history.get('best_time', '9:00 AM')}\n\n"
        )

        for s in stks:
            tier = _engagement_tier(s)
            approach = _recommended_approach(s)
            bench = _RESPONSE_BENCHMARKS[approach]
            tmpl = _EMAIL_TEMPLATES.get(s["email_pref"], _EMAIL_TEMPLATES["concise_technical"])
            subject = _generate_subject(s["email_pref"], acct, acct["pain_points"][0])

            output += (
                f"---\n**To: {s['name']} ({s['role']}) — {s['influence']}**\n"
                f"Engagement tier: {tier.replace('_', ' ').title()} | Approach: {approach.replace('_', ' ').title()}\n"
                f"Expected: {bench['open_rate']:.0%} open / {bench['reply_rate']:.0%} reply\n\n"
                f"**Subject:** {subject}\n"
                f"**Tone:** {tmpl['tone']} (max {tmpl['max_words']} words)\n"
                f"**CTA:** {tmpl['cta_style']}\n\n"
            )

        output += (
            f"Source: [Email Analytics + CRM Engagement History]\n"
            f"Agents: MessagingAgent"
        )
        return output

    # ── create_follow_up ──────────────────────────────────────
    def _create_follow_up(self, key):
        acct = _ACCOUNTS[key]
        stks = _STAKEHOLDERS.get(key, [])
        history = _MESSAGING_HISTORY.get(key, {})

        needs_follow_up = [s for s in stks if s["last_email_days_ago"] is not None and s["last_email_days_ago"] >= 7]
        if not needs_follow_up:
            needs_follow_up = [s for s in stks if s["last_email_days_ago"] is not None]

        output = (
            f"**Follow-Up Drafts: {acct['name']}**\n\n"
            f"Contacts needing follow-up: {len(needs_follow_up)}\n\n"
        )

        for s in needs_follow_up:
            days = s["last_email_days_ago"]
            urgency = "High" if days >= 14 else "Medium" if days >= 7 else "Low"
            opened = "Yes (engaged)" if s["open_rate"] >= 0.60 else "No (re-engage)"

            if s["reply_rate"] >= 0.30:
                follow_up_type = "Value-add: share relevant case study or insight"
            elif s["open_rate"] >= 0.60:
                follow_up_type = "Nudge: brief check-in referencing last conversation"
            else:
                follow_up_type = "Re-engage: new angle via different channel or champion intro"

            output += (
                f"---\n**{s['name']} ({s['role']})**\n"
                f"| Detail | Value |\n|---|---|\n"
                f"| Last Contact | {days} days ago |\n"
                f"| Urgency | {urgency} |\n"
                f"| Opens Previous | {opened} |\n"
                f"| Reply Rate | {s['reply_rate']:.0%} |\n"
                f"| Strategy | {follow_up_type} |\n\n"
            )

        output += (
            f"**Best practices for {acct['name']}:**\n"
            f"- Top-performing subject line: \"{history.get('best_subject', 'N/A')}\"\n"
            f"- Optimal send: {history.get('best_day', 'Tuesday')} at {history.get('best_time', '9:00 AM')}\n\n"
            f"Source: [Email Analytics + Engagement Tracking]\n"
            f"Agents: MessagingAgent"
        )
        return output

    # ── draft_proposal_intro ──────────────────────────────────
    def _draft_proposal_intro(self, key):
        acct = _ACCOUNTS[key]
        stks = _STAKEHOLDERS.get(key, [])

        decision_makers = [s for s in stks if s["influence"] in ("Decision Maker", "Economic Buyer")]
        champions = [s for s in stks if s["influence"] == "Champion"]

        pain_list = "\n".join(f"  {i}. {p.title()}" for i, p in enumerate(acct["pain_points"], 1))
        dm_list = "\n".join(f"  - {s['name']} ({s['role']})" for s in decision_makers) or "  - No decision makers mapped"
        champ_list = "\n".join(f"  - {s['name']} ({s['role']})" for s in champions) or "  - No champions identified"

        savings = int(acct["opportunity_value"] * 1.65)
        impl_weeks = 8 if acct["industry"] == "Manufacturing" else 6

        return (
            f"**Proposal Introduction: {acct['name']}**\n\n"
            f"**Context:**\n"
            f"- Industry: {acct['industry']} | Revenue: ${acct['revenue']:,}\n"
            f"- Current spend: ${acct['current_spend']:,}/yr | Opportunity: ${acct['opportunity_value']:,}\n\n"
            f"**Key Pain Points Addressed:**\n{pain_list}\n\n"
            f"**Proposal Highlights:**\n"
            f"- Projected 3-year savings: ${savings:,}\n"
            f"- Implementation timeline: {impl_weeks} weeks\n"
            f"- Risk-free 90-day pilot included\n"
            f"- Dedicated customer success manager\n\n"
            f"**Distribution:**\n"
            f"Decision Makers:\n{dm_list}\n"
            f"Champions (internal advocates):\n{champ_list}\n\n"
            f"**Recommended Subject:** \"Proposal: Addressing {acct['pain_points'][0]} at {acct['name']}\"\n\n"
            f"**Email Structure:**\n"
            f"1. Reference recent conversation or trigger event\n"
            f"2. Summarize 3 key pain points and proposed solutions\n"
            f"3. Highlight ROI: ${savings:,} over 3 years\n"
            f"4. Attach executive summary (2 pages) + full proposal\n"
            f"5. CTA: 30-minute proposal walkthrough\n\n"
            f"Source: [Proposal Engine + Value Engineering]\n"
            f"Agents: MessagingAgent"
        )

    # ── campaign_sequence ─────────────────────────────────────
    def _campaign_sequence(self, key):
        acct = _ACCOUNTS[key]
        stks = _STAKEHOLDERS.get(key, [])
        history = _MESSAGING_HISTORY.get(key, {})

        total_touches = 7
        sequence = [
            {"day": 1, "channel": "Email", "action": "Personalized intro referencing trigger event", "stakeholders": "All decision makers"},
            {"day": 3, "channel": "LinkedIn", "action": "Connect request with custom note", "stakeholders": "CTO, VP-level"},
            {"day": 5, "channel": "Email", "action": "Value-add: industry case study", "stakeholders": "Technical evaluators"},
            {"day": 8, "channel": "Phone", "action": "Champion check-in call", "stakeholders": "Champion only"},
            {"day": 10, "channel": "Email", "action": "ROI calculator + executive summary", "stakeholders": "Economic buyer"},
            {"day": 14, "channel": "Email", "action": "Peer reference offer", "stakeholders": "Decision maker"},
            {"day": 18, "channel": "Email", "action": "Meeting request with clear agenda", "stakeholders": "Full buying committee"},
        ]

        seq_rows = ""
        for s in sequence:
            seq_rows += f"| Day {s['day']} | {s['channel']} | {s['action']} | {s['stakeholders']} |\n"

        ab_variants = (
            "**A/B Testing Plan:**\n"
            "| Element | Variant A | Variant B |\n|---|---|---|\n"
            f"| Subject Line | Pain-point led | ROI-led |\n"
            f"| CTA | 15-min call | Calendar link |\n"
            f"| Send Time | {history.get('best_day', 'Tuesday')} AM | Thursday PM |\n"
            f"| Tone | Consultative | Direct |\n"
        )

        return (
            f"**Campaign Sequence: {acct['name']}**\n\n"
            f"**Account Profile:**\n"
            f"- {acct['industry']} | {acct['employees']:,} employees | ${acct['opportunity_value']:,} opportunity\n"
            f"- Active sequences: {history.get('sequences_active', 0)} | "
            f"Completed: {history.get('sequences_completed', 0)}\n\n"
            f"**{total_touches}-Touch Sequence:**\n\n"
            f"| Day | Channel | Action | Target |\n|---|---|---|---|\n"
            f"{seq_rows}\n"
            f"{ab_variants}\n"
            f"**Success Metrics:**\n"
            f"- Target open rate: 65%+ (current: {history.get('avg_open_rate', 0):.0%})\n"
            f"- Target reply rate: 30%+ (current: {history.get('avg_reply_rate', 0):.0%})\n"
            f"- Target meeting booked: by Day 18\n\n"
            f"Source: [Campaign Engine + Email Analytics + CRM]\n"
            f"Agents: MessagingAgent"
        )


if __name__ == "__main__":
    agent = MessagingAgent()
    for op in ["generate_outreach", "create_follow_up", "draft_proposal_intro", "campaign_sequence"]:
        print("=" * 60)
        print(agent.perform(operation=op, account_name="Acme Corporation"))
        print()
