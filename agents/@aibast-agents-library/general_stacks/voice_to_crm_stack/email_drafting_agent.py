"""
Voice to CRM Email Drafting Agent

Generates meeting recaps, extracts action items, drafts follow-up emails,
and manages distribution lists from voice-captured meeting data.

Where a real deployment would integrate with calendar and email systems,
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
    "name": "@aibast-agents-library/voice-to-crm-email",
    "version": "1.0.0",
    "display_name": "Voice to CRM Email",
    "description": "Meeting recap generation, action item extraction, follow-up email drafting, and distribution list management.",
    "author": "AIBAST",
    "tags": ["voice", "email", "meeting-recap", "action-items", "follow-up"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_MEETING_TRANSCRIPTS = {
    "MTG-001": {
        "id": "MTG-001", "title": "TechVantage Solutions - Quarterly Business Review",
        "date": "2025-11-12", "duration_min": 55,
        "attendees": [
            {"name": "Jennifer Walsh", "role": "VP Operations", "company": "TechVantage Solutions", "email": "jennifer.walsh@techvantage.com"},
            {"name": "Sam Patel", "role": "IT Director", "company": "TechVantage Solutions", "email": "sam.patel@techvantage.com"},
            {"name": "Alex Rivera", "role": "Account Executive", "company": "Our Company", "email": "alex.rivera@ourcompany.com"},
            {"name": "Sarah Chen", "role": "Account Manager", "company": "Our Company", "email": "sarah.chen@ourcompany.com"},
        ],
        "key_topics": ["Q3 usage review", "APAC expansion plans", "Analytics upgrade discussion", "Contract renewal timeline"],
        "decisions": ["Proceed with Analytics Pro evaluation", "Schedule technical deep-dive with IT team", "Begin renewal discussions in January"],
        "sentiment": "Positive",
    },
}

_ACTION_ITEMS = {
    "MTG-001": [
        {"id": "AI-001", "action": "Send Analytics Pro product brief and pricing", "owner": "Alex Rivera", "due_date": "2025-11-15", "status": "Open", "priority": "High"},
        {"id": "AI-002", "action": "Schedule technical deep-dive session with IT team", "owner": "Sarah Chen", "due_date": "2025-11-19", "status": "Open", "priority": "High"},
        {"id": "AI-003", "action": "Provide APAC deployment case studies", "owner": "Alex Rivera", "due_date": "2025-11-22", "status": "Open", "priority": "Medium"},
        {"id": "AI-004", "action": "Share Q3 usage analytics dashboard", "owner": "Sarah Chen", "due_date": "2025-11-14", "status": "Open", "priority": "High"},
        {"id": "AI-005", "action": "Prepare renewal proposal framework", "owner": "Alex Rivera", "due_date": "2025-12-15", "status": "Open", "priority": "Medium"},
        {"id": "AI-006", "action": "Evaluate SSO integration requirements for APAC", "owner": "Sam Patel", "due_date": "2025-12-01", "status": "Open", "priority": "Medium"},
    ],
}

_EMAIL_TEMPLATES = {
    "meeting_recap": {
        "subject": "Meeting Recap: {meeting_title} - {date}",
        "body": "Hi {attendee_names},\n\nThank you for a productive meeting today. Here's a summary of our discussion:\n\n**Key Topics:**\n{topics}\n\n**Decisions Made:**\n{decisions}\n\n**Action Items:**\n{action_items}\n\nPlease review and let me know if I missed anything. Looking forward to our next steps.\n\nBest regards,\n{sender_name}",
    },
    "follow_up": {
        "subject": "Follow-up: {action_item} - {meeting_title}",
        "body": "Hi {recipient_name},\n\nFollowing up on our meeting on {date} regarding {meeting_title}.\n\nAs discussed, I wanted to share the following:\n\n{content}\n\nPlease let me know if you have any questions or need additional information.\n\nBest,\n{sender_name}",
    },
}

_DISTRIBUTION_LISTS = {
    "MTG-001": {
        "all_attendees": ["jennifer.walsh@techvantage.com", "sam.patel@techvantage.com", "alex.rivera@ourcompany.com", "sarah.chen@ourcompany.com"],
        "external_only": ["jennifer.walsh@techvantage.com", "sam.patel@techvantage.com"],
        "internal_only": ["alex.rivera@ourcompany.com", "sarah.chen@ourcompany.com"],
        "action_item_owners": ["alex.rivera@ourcompany.com", "sarah.chen@ourcompany.com", "sam.patel@techvantage.com"],
    },
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve_meeting(query):
    if not query:
        return "MTG-001"
    q = query.upper().strip()
    for key in _MEETING_TRANSCRIPTS:
        if key in q:
            return key
    return "MTG-001"


def _format_action_items(meeting_id):
    items = _ACTION_ITEMS.get(meeting_id, [])
    lines = []
    for item in items:
        lines.append(f"- [{item['priority']}] {item['action']} (Owner: {item['owner']}, Due: {item['due_date']})")
    return "\n".join(lines)


def _render_recap_email(meeting_id):
    mtg = _MEETING_TRANSCRIPTS[meeting_id]
    topics = "\n".join(f"- {t}" for t in mtg["key_topics"])
    decisions = "\n".join(f"- {d}" for d in mtg["decisions"])
    action_items = _format_action_items(meeting_id)
    attendee_names = ", ".join(a["name"] for a in mtg["attendees"])
    template = _EMAIL_TEMPLATES["meeting_recap"]
    subject = template["subject"].replace("{meeting_title}", mtg["title"]).replace("{date}", mtg["date"])
    body = template["body"].replace("{attendee_names}", attendee_names).replace("{topics}", topics).replace("{decisions}", decisions).replace("{action_items}", action_items).replace("{sender_name}", "Alex Rivera")
    return subject, body


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class VoiceToCRMEmailAgent(BasicAgent):
    """
    Voice-to-CRM email agent for meeting follow-ups.

    Operations:
        meeting_recap      - generate meeting recap from voice transcript
        action_items       - extract and organize action items
        follow_up_draft    - draft follow-up emails for action items
        distribution_list  - manage email distribution lists
    """

    def __init__(self):
        self.name = "VoiceToCRMEmailAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "meeting_recap", "action_items",
                            "follow_up_draft", "distribution_list",
                        ],
                        "description": "The email operation to perform",
                    },
                    "meeting_id": {
                        "type": "string",
                        "description": "Meeting ID (e.g. 'MTG-001')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "meeting_recap")
        mtg_id = _resolve_meeting(kwargs.get("meeting_id", ""))
        dispatch = {
            "meeting_recap": self._meeting_recap,
            "action_items": self._action_items,
            "follow_up_draft": self._follow_up_draft,
            "distribution_list": self._distribution_list,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(mtg_id)

    def _meeting_recap(self, mtg_id):
        mtg = _MEETING_TRANSCRIPTS[mtg_id]
        subject, body = _render_recap_email(mtg_id)
        attendee_rows = ""
        for a in mtg["attendees"]:
            attendee_rows += f"| {a['name']} | {a['role']} | {a['company']} | {a['email']} |\n"
        return (
            f"**Meeting Recap: {mtg['title']}**\n\n"
            f"| Field | Detail |\n|---|---|\n"
            f"| Date | {mtg['date']} |\n"
            f"| Duration | {mtg['duration_min']} minutes |\n"
            f"| Sentiment | {mtg['sentiment']} |\n\n"
            f"**Attendees:**\n\n"
            f"| Name | Role | Company | Email |\n|---|---|---|---|\n"
            f"{attendee_rows}\n"
            f"**Draft Email:**\n\n"
            f"**Subject:** {subject}\n\n"
            f"---\n{body}\n---\n\n"
            f"Source: [Meeting Transcript + AI Summary]\nAgents: VoiceToCRMEmailAgent"
        )

    def _action_items(self, mtg_id):
        items = _ACTION_ITEMS.get(mtg_id, [])
        rows = ""
        for item in items:
            rows += f"| {item['id']} | {item['action'][:40]} | {item['owner']} | {item['due_date']} | {item['priority']} | {item['status']} |\n"
        by_owner = {}
        for item in items:
            by_owner.setdefault(item["owner"], []).append(item)
        owner_summary = "\n".join(f"- {owner}: {len(items)} items" for owner, items in by_owner.items())
        return (
            f"**Action Items: {mtg_id}**\n\n"
            f"| ID | Action | Owner | Due Date | Priority | Status |\n|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**By Owner:**\n{owner_summary}\n\n"
            f"**Total Items:** {len(items)} | **High Priority:** {sum(1 for i in items if i['priority'] == 'High')}\n\n"
            f"Source: [Meeting Transcript + NLP Extraction]\nAgents: VoiceToCRMEmailAgent"
        )

    def _follow_up_draft(self, mtg_id):
        mtg = _MEETING_TRANSCRIPTS[mtg_id]
        items = _ACTION_ITEMS.get(mtg_id, [])
        high_priority = [i for i in items if i["priority"] == "High"]
        drafts = ""
        for item in high_priority[:2]:
            drafts += (
                f"**To:** {item['owner']}\n"
                f"**Subject:** Follow-up: {item['action'][:50]} - {mtg['title']}\n"
                f"**Due:** {item['due_date']}\n\n"
                f"Hi {item['owner'].split()[0]},\n\n"
                f"Following up on our meeting on {mtg['date']}. As discussed, the next step is:\n\n"
                f"- {item['action']}\n\n"
                f"Please let me know if you need any additional information.\n\n"
                f"Best, Alex\n\n---\n\n"
            )
        return (
            f"**Follow-Up Drafts: {mtg['title']}**\n\n"
            f"Generated {len(high_priority)} high-priority follow-up emails.\n\n"
            f"{drafts}"
            f"Source: [Email Template Engine]\nAgents: VoiceToCRMEmailAgent"
        )

    def _distribution_list(self, mtg_id):
        lists = _DISTRIBUTION_LISTS.get(mtg_id, {})
        list_rows = ""
        for list_name, emails in lists.items():
            list_rows += f"| {list_name.replace('_', ' ').title()} | {len(emails)} | {', '.join(emails[:2])}{'...' if len(emails) > 2 else ''} |\n"
        return (
            f"**Distribution Lists: {mtg_id}**\n\n"
            f"| List | Recipients | Members |\n|---|---|---|\n"
            f"{list_rows}\n"
            f"**Recommended for Recap:** All Attendees ({len(lists.get('all_attendees', []))} recipients)\n"
            f"**Recommended for Action Items:** Action Item Owners ({len(lists.get('action_item_owners', []))} recipients)\n\n"
            f"Source: [Meeting Metadata + Contact Directory]\nAgents: VoiceToCRMEmailAgent"
        )


if __name__ == "__main__":
    agent = VoiceToCRMEmailAgent()
    for op in ["meeting_recap", "action_items", "follow_up_draft", "distribution_list"]:
        print("=" * 60)
        print(agent.perform(operation=op, meeting_id="MTG-001"))
        print()
