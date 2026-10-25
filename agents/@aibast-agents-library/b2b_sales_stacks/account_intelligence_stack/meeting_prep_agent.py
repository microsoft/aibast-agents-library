"""
Meeting Prep Agent

Generates pre-meeting briefings, talking points, objection preparation,
and follow-up templates for enterprise B2B sales meetings. Combines
account intelligence, stakeholder data, and competitive context into
actionable meeting materials.

Where a real deployment would call CRM and calendar APIs, this agent
uses a synthetic data layer so it runs anywhere without credentials.
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
    "name": "@aibast-agents-library/meeting-prep",
    "version": "1.0.0",
    "display_name": "Meeting Prep",
    "description": "Generates pre-meeting briefs, talking points, objection prep, and follow-up templates.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "meeting-prep", "briefing", "objection-handling"],
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
        "revenue": 2_800_000_000, "employees": 12_400,
        "current_spend": 1_200_000, "opportunity_value": 2_400_000,
        "products_owned": ["Platform Core", "Analytics Module"],
        "pain_points": ["legacy ERP integration", "manual reporting", "supply chain visibility"],
    },
    "contoso": {
        "id": "acc-002", "name": "Contoso Ltd", "industry": "Technology",
        "revenue": 980_000_000, "employees": 4_200,
        "current_spend": 680_000, "opportunity_value": 1_100_000,
        "products_owned": ["Platform Core"],
        "pain_points": ["scaling data infrastructure", "EMEA compliance", "vendor consolidation"],
    },
    "fabrikam": {
        "id": "acc-003", "name": "Fabrikam Industries", "industry": "Manufacturing",
        "revenue": 1_500_000_000, "employees": 8_700,
        "current_spend": 450_000, "opportunity_value": 890_000,
        "products_owned": ["Analytics Module"],
        "pain_points": ["production downtime analytics", "quality control automation", "workforce scheduling"],
    },
    "northwind": {
        "id": "acc-004", "name": "Northwind Traders", "industry": "Retail",
        "revenue": 620_000_000, "employees": 3_100,
        "current_spend": 220_000, "opportunity_value": 540_000,
        "products_owned": [],
        "pain_points": ["omnichannel inventory", "customer data platform", "last-mile logistics"],
    },
}

_UPCOMING_MEETINGS = {
    "acme": [
        {
            "id": "mtg-001", "title": "Executive Strategy Review",
            "date": "2025-03-15", "time": "10:00 AM CT", "duration_min": 60,
            "location": "Zoom (Executive Boardroom)",
            "our_attendees": ["Michael Torres (AE)", "Jennifer Walsh (SE)", "Mark Stevens (VP Sales)"],
            "their_attendees": [
                {"name": "Sarah Chen", "role": "CTO", "sentiment": "Unknown", "meetings_prior": 0},
                {"name": "James Miller", "role": "VP Operations", "sentiment": "Positive", "meetings_prior": 14},
                {"name": "Lisa Park", "role": "CFO", "sentiment": "Neutral", "meetings_prior": 2},
            ],
            "objective": "Present expansion proposal and secure CTO alignment",
            "deal_stage": "Proposal", "deal_value": 2_400_000,
        },
    ],
    "contoso": [
        {
            "id": "mtg-002", "title": "Renewal Discussion + Expansion",
            "date": "2025-03-18", "time": "2:00 PM PT", "duration_min": 45,
            "location": "Microsoft Teams",
            "our_attendees": ["Michael Torres (AE)", "Sarah Kim (CSM)"],
            "their_attendees": [
                {"name": "Alex Kim", "role": "CTO", "sentiment": "Positive", "meetings_prior": 10},
                {"name": "Pat Johnson", "role": "CFO", "sentiment": "Neutral", "meetings_prior": 3},
            ],
            "objective": "Finalize renewal terms and introduce expansion options",
            "deal_stage": "Negotiation", "deal_value": 1_100_000,
        },
    ],
    "fabrikam": [
        {
            "id": "mtg-003", "title": "Discovery Workshop",
            "date": "2025-03-21", "time": "9:00 AM ET", "duration_min": 90,
            "location": "On-site (Detroit office)",
            "our_attendees": ["Michael Torres (AE)", "Jennifer Walsh (SE)"],
            "their_attendees": [
                {"name": "Chris Anderson", "role": "VP IT", "sentiment": "Neutral", "meetings_prior": 4},
                {"name": "Dana White", "role": "COO", "sentiment": "Positive", "meetings_prior": 6},
            ],
            "objective": "Deep-dive into production analytics requirements",
            "deal_stage": "Discovery", "deal_value": 890_000,
        },
    ],
    "northwind": [
        {
            "id": "mtg-004", "title": "Initial Discovery Call",
            "date": "2025-03-22", "time": "11:00 AM PT", "duration_min": 30,
            "location": "Zoom",
            "our_attendees": ["Michael Torres (AE)"],
            "their_attendees": [
                {"name": "Jordan Lee", "role": "CTO", "sentiment": "Unknown", "meetings_prior": 1},
            ],
            "objective": "Understand e-commerce platform needs and qualify opportunity",
            "deal_stage": "Qualification", "deal_value": 540_000,
        },
    ],
}

_MEETING_HISTORY = {
    "acme": [
        {"date": "2025-03-10", "title": "Technical Architecture Review", "attendees": 4, "outcome": "Positive — David Wong endorsed API approach", "action_items": ["Send integration guide", "Schedule SE deep dive"]},
        {"date": "2025-02-28", "title": "CFO Business Case Review", "attendees": 3, "outcome": "Neutral — Lisa requested ROI calculator", "action_items": ["Build customized ROI model", "Send reference customer contacts"]},
        {"date": "2025-02-15", "title": "Procurement Introduction", "attendees": 2, "outcome": "Neutral — standard process initiated", "action_items": ["Submit vendor questionnaire", "Provide security documentation"]},
    ],
    "contoso": [
        {"date": "2025-03-11", "title": "Product Roadmap Preview", "attendees": 3, "outcome": "Positive — Sam excited about new features", "action_items": ["Send beta access details", "Schedule expansion discussion"]},
    ],
    "fabrikam": [
        {"date": "2025-03-04", "title": "Platform Demo", "attendees": 2, "outcome": "Neutral — Chris wants to see manufacturing-specific features", "action_items": ["Prepare manufacturing demo environment", "Share case study"]},
    ],
    "northwind": [
        {"date": "2025-02-12", "title": "Initial Intro Call", "attendees": 2, "outcome": "Positive — Jordan interested in omnichannel capabilities", "action_items": ["Send retail case studies", "Prepare discovery questions"]},
    ],
}

_COMMON_OBJECTIONS = {
    "price": {
        "objection": "Your solution is more expensive than alternatives",
        "response": "When factoring total cost of ownership including implementation, support, and time-to-value, our 3-year TCO is actually 23% lower. Let me walk you through the comparison.",
        "proof_points": ["47 similar deployments at 94% success rate", "8-week implementation vs 14+ weeks for alternatives", "Dedicated CSM included at no extra cost"],
    },
    "risk": {
        "objection": "We're concerned about implementation risk and disruption",
        "response": "We offer a 90-day proof-of-value pilot with full rollback capability. In manufacturing deployments our size, we've achieved 94% on-time delivery.",
        "proof_points": ["Phased rollout approach minimizes disruption", "Dedicated implementation team", "3 reference customers in your industry available"],
    },
    "incumbent": {
        "objection": "We already have a solution that works",
        "response": "I understand the value of continuity. Our customers who switched found that integration capabilities and real-time analytics delivered ROI within the first quarter.",
        "proof_points": ["Average 3.2x productivity improvement", "Native ERP integration vs custom connectors", "Real-time dashboards vs batch reporting"],
    },
    "timing": {
        "objection": "This isn't the right time / we need to wait until next budget cycle",
        "response": "I understand budget timing. Our flexible licensing allows us to start with a pilot this quarter and scale in the next budget cycle. This gives your team a head start.",
        "proof_points": ["Pilot program with deferred billing", "Quarterly payment options", "ROI typically visible within 90 days"],
    },
    "internal": {
        "objection": "We're considering building this internally",
        "response": "Build vs buy is an important consideration. Our analysis shows that internal builds take 3-5x longer and cost 2-4x more when factoring in maintenance and opportunity cost.",
        "proof_points": ["Average internal build takes 18+ months", "Ongoing maintenance costs often exceed license fees", "Our roadmap delivers features faster than internal teams"],
    },
}

_FOLLOW_UP_TEMPLATES = {
    "executive": {
        "subject": "Follow-up: {meeting_title} — Next Steps",
        "sections": ["Thank you and key takeaways", "Agreed action items with owners", "Proposed timeline", "Attached materials"],
        "tone": "Professional, concise, action-oriented",
        "send_within": "2 hours",
    },
    "technical": {
        "subject": "Technical Follow-up: {meeting_title}",
        "sections": ["Technical requirements summary", "Architecture recommendations", "Integration approach", "POC proposal"],
        "tone": "Technical, detailed, solution-focused",
        "send_within": "4 hours",
    },
    "discovery": {
        "subject": "Great conversation — {meeting_title} Summary",
        "sections": ["Pain points discussed", "Proposed approach", "Suggested next steps", "Relevant resources"],
        "tone": "Consultative, educational, helpful",
        "send_within": "Same day",
    },
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


def _attendee_prep_level(attendee):
    """Classify how much prep is needed for each attendee."""
    if attendee["meetings_prior"] == 0:
        return "Full Research"
    if attendee["sentiment"] == "Unknown":
        return "Sentiment Discovery"
    if attendee["sentiment"] == "Neutral":
        return "Value Reinforcement"
    return "Relationship Building"


def _meeting_risk_level(meeting):
    """Assess meeting risk based on attendee composition."""
    unknown_sentiment = sum(1 for a in meeting["their_attendees"] if a["sentiment"] == "Unknown")
    first_meetings = sum(1 for a in meeting["their_attendees"] if a["meetings_prior"] == 0)
    if first_meetings >= 2 or unknown_sentiment >= 2:
        return "High"
    if first_meetings >= 1 or unknown_sentiment >= 1:
        return "Medium"
    return "Low"


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class MeetingPrepAgent(BasicAgent):
    """
    Prepares comprehensive meeting materials for B2B sales.

    Operations:
        pre_meeting_brief  - full meeting briefing document
        talking_points     - stakeholder-specific talking points
        objection_prep     - objection handling preparation
        follow_up_template - post-meeting follow-up draft
    """

    def __init__(self):
        self.name = "MeetingPrepAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "pre_meeting_brief", "talking_points",
                            "objection_prep", "follow_up_template",
                        ],
                        "description": "The meeting prep operation",
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
        op = kwargs.get("operation", "pre_meeting_brief")
        key = _resolve_account(kwargs.get("account_name", ""))
        dispatch = {
            "pre_meeting_brief": self._pre_meeting_brief,
            "talking_points": self._talking_points,
            "objection_prep": self._objection_prep,
            "follow_up_template": self._follow_up_template,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`."
        return handler(key)

    # ── pre_meeting_brief ─────────────────────────────────────
    def _pre_meeting_brief(self, key):
        acct = _ACCOUNTS[key]
        meetings = _UPCOMING_MEETINGS.get(key, [])
        history = _MEETING_HISTORY.get(key, [])

        if not meetings:
            return f"**Meeting Brief: {acct['name']}**\n\nNo upcoming meetings scheduled."

        mtg = meetings[0]
        risk_level = _meeting_risk_level(mtg)

        attendee_rows = ""
        for a in mtg["their_attendees"]:
            prep = _attendee_prep_level(a)
            attendee_rows += (
                f"| {a['name']} | {a['role']} | {a['sentiment']} | "
                f"{a['meetings_prior']} | {prep} |\n"
            )

        our_team = "\n".join(f"- {a}" for a in mtg["our_attendees"])

        recent_history = ""
        if history:
            recent_history = "\n**Recent Meeting History:**\n"
            for h in history[:3]:
                recent_history += f"- {h['date']}: {h['title']} — {h['outcome']}\n"
                if h["action_items"]:
                    for ai in h["action_items"]:
                        recent_history += f"  - Action: {ai}\n"

        return (
            f"**Pre-Meeting Brief: {mtg['title']}**\n\n"
            f"| Detail | Value |\n|---|---|\n"
            f"| Account | {acct['name']} ({acct['industry']}) |\n"
            f"| Date/Time | {mtg['date']} at {mtg['time']} |\n"
            f"| Duration | {mtg['duration_min']} minutes |\n"
            f"| Location | {mtg['location']} |\n"
            f"| Objective | {mtg['objective']} |\n"
            f"| Deal Stage | {mtg['deal_stage']} |\n"
            f"| Deal Value | ${mtg['deal_value']:,} |\n"
            f"| Meeting Risk | {risk_level} |\n\n"
            f"**Their Attendees:**\n\n"
            f"| Name | Role | Sentiment | Prior Meetings | Prep Level |\n|---|---|---|---|---|\n"
            f"{attendee_rows}\n"
            f"**Our Team:**\n{our_team}\n\n"
            f"**Account Context:**\n"
            f"- Revenue: ${acct['revenue']:,} | Employees: {acct['employees']:,}\n"
            f"- Current spend: ${acct['current_spend']:,}/yr | Opportunity: ${acct['opportunity_value']:,}\n"
            f"- Products owned: {', '.join(acct['products_owned']) or 'None'}\n"
            f"- Pain points: {', '.join(acct['pain_points'])}\n"
            f"{recent_history}\n"
            f"Source: [CRM + Calendar + Meeting Intelligence]\n"
            f"Agents: MeetingPrepAgent"
        )

    # ── talking_points ────────────────────────────────────────
    def _talking_points(self, key):
        acct = _ACCOUNTS[key]
        meetings = _UPCOMING_MEETINGS.get(key, [])

        if not meetings:
            return f"**Talking Points: {acct['name']}**\n\nNo upcoming meetings scheduled."

        mtg = meetings[0]
        output = f"**Talking Points: {mtg['title']}**\n\n"

        for a in mtg["their_attendees"]:
            role = a["role"]
            output += f"---\n**For {a['name']} ({role}):**\n\n"

            if any(t in role for t in ("CTO", "IT", "Engineering", "VP IT")):
                output += (
                    f"**Theme: Technical Vision & Architecture**\n"
                    f"- \"Our API-first architecture integrates natively with your existing {acct['industry'].lower()} systems\"\n"
                    f"- \"We've reduced integration timelines by 60% with our pre-built connectors\"\n"
                    f"- \"Three {acct['industry'].lower()} CTOs are available for a peer conversation\"\n\n"
                )
            elif any(t in role for t in ("CFO", "Finance")):
                savings = int(acct["opportunity_value"] * 1.75)
                output += (
                    f"**Theme: ROI & Business Value**\n"
                    f"- \"${savings:,} projected savings over 3 years based on similar deployments\"\n"
                    f"- \"8-week implementation means faster time-to-value than any alternative\"\n"
                    f"- \"90-day proof-of-value pilot — no commitment until you see results\"\n\n"
                )
            elif any(t in role for t in ("Operations", "COO")):
                output += (
                    f"**Theme: Operational Excellence**\n"
                    f"- \"Real-time dashboards replace manual reporting, saving 15+ hours per week\"\n"
                    f"- \"Predictive analytics identify issues before they impact production\"\n"
                    f"- \"Your team becomes the transformation leaders within {acct['name']}\"\n\n"
                )
            elif any(t in role for t in ("Product", "VP Product")):
                output += (
                    f"**Theme: Product Capability & Roadmap**\n"
                    f"- \"Our platform scales with your growth — supporting 10x current volume\"\n"
                    f"- \"Co-innovation partnership for industry-specific features\"\n"
                    f"- \"Quarterly product council with direct influence on roadmap\"\n\n"
                )
            else:
                output += (
                    f"**Theme: Strategic Partnership**\n"
                    f"- \"We're investing in long-term partnership, not just a transaction\"\n"
                    f"- \"Dedicated executive sponsor and customer success team\"\n"
                    f"- \"Quarterly business reviews to ensure continuous value delivery\"\n\n"
                )

        output += (
            f"**Universal Proof Points:**\n"
            f"- 94% customer retention rate\n"
            f"- 47 deployments in {acct['industry'].lower()} industry\n"
            f"- 8-week average implementation time\n"
            f"- 24/7 dedicated support with named CSM\n\n"
            f"Source: [Sales Playbook + Value Engineering + References]\n"
            f"Agents: MeetingPrepAgent"
        )
        return output

    # ── objection_prep ────────────────────────────────────────
    def _objection_prep(self, key):
        acct = _ACCOUNTS[key]
        meetings = _UPCOMING_MEETINGS.get(key, [])

        # Determine likely objections based on meeting context
        likely = []
        if meetings:
            mtg = meetings[0]
            for a in mtg["their_attendees"]:
                if "CFO" in a["role"] or "Finance" in a["role"]:
                    likely.extend(["price", "timing"])
                if a["sentiment"] == "Unknown":
                    likely.extend(["risk", "incumbent"])
                if a["meetings_prior"] == 0:
                    likely.append("risk")

        likely = list(dict.fromkeys(likely))  # dedupe preserving order
        if not likely:
            likely = list(_COMMON_OBJECTIONS.keys())

        output = f"**Objection Preparation: {acct['name']}**\n\n"
        output += f"Likely objections based on attendee analysis: {len(likely)}\n\n"

        for obj_key in likely:
            obj = _COMMON_OBJECTIONS.get(obj_key)
            if not obj:
                continue

            output += (
                f"---\n**Objection: \"{obj['objection']}\"**\n\n"
                f"**Recommended Response:**\n"
                f"\"{obj['response']}\"\n\n"
                f"**Proof Points:**\n"
                + "".join(f"- {p}\n" for p in obj["proof_points"])
                + "\n"
            )

        output += (
            f"**General Objection Handling Tips:**\n"
            f"1. Acknowledge the concern before responding\n"
            f"2. Ask clarifying questions to understand the root issue\n"
            f"3. Use specific data points and customer references\n"
            f"4. Offer concrete next steps to address the concern\n\n"
            f"Source: [Sales Playbook + Win/Loss Analysis + Customer References]\n"
            f"Agents: MeetingPrepAgent"
        )
        return output

    # ── follow_up_template ────────────────────────────────────
    def _follow_up_template(self, key):
        acct = _ACCOUNTS[key]
        meetings = _UPCOMING_MEETINGS.get(key, [])
        history = _MEETING_HISTORY.get(key, [])

        if not meetings:
            return f"**Follow-Up Template: {acct['name']}**\n\nNo upcoming meetings to prepare follow-up for."

        mtg = meetings[0]

        # Select template based on meeting type
        if mtg["deal_stage"] in ("Qualification", "Discovery"):
            tmpl = _FOLLOW_UP_TEMPLATES["discovery"]
        elif any("CTO" in a["role"] or "Engineering" in a["role"] for a in mtg["their_attendees"]):
            tmpl = _FOLLOW_UP_TEMPLATES["technical"]
        else:
            tmpl = _FOLLOW_UP_TEMPLATES["executive"]

        subject = tmpl["subject"].format(meeting_title=mtg["title"])
        sections = "\n".join(f"  {i}. {s}" for i, s in enumerate(tmpl["sections"], 1))

        # Build action items from recent history
        recent_actions = ""
        if history:
            recent_actions = "\n**Open Action Items from Previous Meetings:**\n"
            for h in history[:2]:
                for ai in h.get("action_items", []):
                    recent_actions += f"- {ai} (from {h['date']})\n"

        attendee_list = ", ".join(f"{a['name']} ({a['role']})" for a in mtg["their_attendees"])

        return (
            f"**Follow-Up Template: {mtg['title']}**\n\n"
            f"| Detail | Value |\n|---|---|\n"
            f"| Subject | {subject} |\n"
            f"| Tone | {tmpl['tone']} |\n"
            f"| Send Within | {tmpl['send_within']} |\n"
            f"| Recipients | {attendee_list} |\n\n"
            f"**Email Structure:**\n{sections}\n\n"
            f"**Draft Opening:**\n"
            f"\"Thank you for your time today discussing {mtg['objective'].lower()}. "
            f"I wanted to summarize our key discussion points and confirm next steps.\"\n\n"
            f"**Key Attachments to Include:**\n"
            f"- Meeting summary (1 page)\n"
            f"- Relevant case study for {acct['industry'].lower()}\n"
            f"- Proposal or technical documentation as discussed\n"
            f"- Calendar invite for next meeting\n"
            f"{recent_actions}\n"
            f"**Draft Closing:**\n"
            f"\"I'll follow up on [action items] by [date]. In the meantime, please don't "
            f"hesitate to reach out with any questions. Looking forward to our next conversation.\"\n\n"
            f"Source: [Meeting Templates + CRM + Action Items]\n"
            f"Agents: MeetingPrepAgent"
        )


if __name__ == "__main__":
    agent = MeetingPrepAgent()
    for op in ["pre_meeting_brief", "talking_points", "objection_prep", "follow_up_template"]:
        print("=" * 60)
        print(agent.perform(operation=op, account_name="Acme Corporation"))
        print()
