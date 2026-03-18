"""
Speech to CRM Agent

Transcribes sales calls, extracts entities, maps to CRM fields, and generates
update previews for CRM record enrichment.

Where a real deployment would integrate with speech-to-text APIs and CRM,
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
    "name": "@aibast-agents-library/speech-to-crm",
    "version": "1.0.0",
    "display_name": "Speech to CRM",
    "description": "Transcribes sales calls, extracts entities, maps to CRM fields, and previews record updates.",
    "author": "AIBAST",
    "tags": ["speech", "transcription", "crm", "entity-extraction", "nlp"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_CALL_TRANSCRIPTS = {
    "CALL-T001": {
        "id": "CALL-T001", "duration_sec": 1847, "date": "2025-11-14",
        "participants": ["Alex Rivera (Sales)", "Jennifer Walsh (TechVantage Solutions)"],
        "transcript_segments": [
            {"speaker": "Alex Rivera", "timestamp": "00:00:15", "text": "Hi Jennifer, thanks for making time today. I wanted to follow up on our demo last Tuesday."},
            {"speaker": "Jennifer Walsh", "timestamp": "00:00:28", "text": "Hi Alex, yes absolutely. We really liked what we saw, especially the analytics dashboard. Our team has been struggling with reporting."},
            {"speaker": "Alex Rivera", "timestamp": "00:00:45", "text": "That's great to hear. Can you tell me more about the reporting challenges? How many people are affected?"},
            {"speaker": "Jennifer Walsh", "timestamp": "00:01:02", "text": "About 150 people across our operations and finance teams. We spend roughly 20 hours a week manually compiling reports from three different systems."},
            {"speaker": "Alex Rivera", "timestamp": "00:01:25", "text": "That's significant. At your team's average cost, that's roughly $50,000 a year in labor just on reporting. Our platform could automate about 80% of that."},
            {"speaker": "Jennifer Walsh", "timestamp": "00:01:48", "text": "That ROI is compelling. We have budget approval for up to $200,000 for this initiative. Our CEO, Mark Davidson, wants to see a formal proposal by December 15th."},
            {"speaker": "Alex Rivera", "timestamp": "00:02:15", "text": "Perfect. I'll have a proposal ready by December 10th. Should we schedule a review meeting with your team for December 12th?"},
            {"speaker": "Jennifer Walsh", "timestamp": "00:02:30", "text": "That works. Include our IT Director, Sam Patel, in that meeting. He'll need to evaluate the technical integration with our SAP system."},
        ],
        "confidence_score": 0.96,
    },
}

_ENTITY_EXTRACTION_RULES = {
    "person": {"pattern": "Named individuals mentioned", "examples": ["Jennifer Walsh", "Mark Davidson", "Sam Patel"]},
    "organization": {"pattern": "Company or department names", "examples": ["TechVantage Solutions", "Operations", "Finance"]},
    "money": {"pattern": "Dollar amounts or budget references", "examples": ["$200,000", "$50,000"]},
    "date": {"pattern": "Dates and deadlines", "examples": ["December 15th", "December 10th", "December 12th"]},
    "product": {"pattern": "Product or feature mentions", "examples": ["analytics dashboard", "reporting", "platform"]},
    "pain_point": {"pattern": "Challenges or problems described", "examples": ["manually compiling reports", "three different systems", "20 hours a week"]},
    "action_item": {"pattern": "Commitments or next steps", "examples": ["formal proposal", "review meeting", "evaluate technical integration"]},
    "competitor": {"pattern": "Competitor or alternative mentions", "examples": ["SAP"]},
}

_CRM_FIELD_MAPPINGS = {
    "opportunity": {
        "name": {"source": "organization + context", "mapped_value": "TechVantage Solutions - Enterprise Platform"},
        "amount": {"source": "money entity", "mapped_value": 200000},
        "close_date": {"source": "date entity", "mapped_value": "2025-12-15"},
        "stage": {"source": "conversation context", "mapped_value": "Proposal"},
        "probability": {"source": "engagement signals", "mapped_value": 65},
        "next_step": {"source": "action_item entity", "mapped_value": "Send proposal by Dec 10, review meeting Dec 12"},
    },
    "contact": {
        "name": {"source": "person entity", "mapped_value": "Jennifer Walsh"},
        "title": {"source": "inferred from context", "mapped_value": "VP of Operations"},
        "account": {"source": "organization entity", "mapped_value": "TechVantage Solutions"},
    },
    "activity": {
        "type": {"source": "call metadata", "mapped_value": "Phone Call"},
        "subject": {"source": "conversation summary", "mapped_value": "Discovery follow-up - proposal requested"},
        "description": {"source": "full transcript", "mapped_value": "Discussed reporting challenges, 150 users affected. Budget approved up to $200K. CEO Mark Davidson wants proposal by Dec 15. Technical review with IT Director Sam Patel needed."},
        "duration_min": {"source": "call metadata", "mapped_value": 31},
    },
    "new_contacts": [
        {"name": "Mark Davidson", "title": "CEO", "role": "Economic Buyer", "account": "TechVantage Solutions"},
        {"name": "Sam Patel", "title": "IT Director", "role": "Technical Evaluator", "account": "TechVantage Solutions"},
    ],
}

_EXTRACTED_ENTITIES = [
    {"type": "person", "value": "Jennifer Walsh", "confidence": 0.99, "context": "Primary contact, VP Operations"},
    {"type": "person", "value": "Mark Davidson", "confidence": 0.97, "context": "CEO, economic buyer, wants proposal by Dec 15"},
    {"type": "person", "value": "Sam Patel", "confidence": 0.98, "context": "IT Director, technical evaluator"},
    {"type": "organization", "value": "TechVantage Solutions", "confidence": 0.99, "context": "Prospect account"},
    {"type": "money", "value": "$200,000", "confidence": 0.98, "context": "Approved budget for initiative"},
    {"type": "money", "value": "$50,000", "confidence": 0.95, "context": "Annual cost of manual reporting"},
    {"type": "date", "value": "December 15", "confidence": 0.97, "context": "CEO deadline for proposal"},
    {"type": "date", "value": "December 12", "confidence": 0.96, "context": "Proposed review meeting date"},
    {"type": "pain_point", "value": "20 hours/week manual reporting", "confidence": 0.94, "context": "150 people affected across ops and finance"},
    {"type": "action_item", "value": "Send proposal by Dec 10", "confidence": 0.97, "context": "Alex committed to deliver proposal"},
    {"type": "action_item", "value": "Schedule Dec 12 review meeting", "confidence": 0.95, "context": "Include Sam Patel for technical evaluation"},
]


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _format_transcript(call_id):
    call = _CALL_TRANSCRIPTS.get(call_id)
    if not call:
        return "Transcript not found."
    lines = []
    for seg in call["transcript_segments"]:
        lines.append(f"[{seg['timestamp']}] **{seg['speaker']}:** {seg['text']}")
    return "\n\n".join(lines)


def _entity_summary():
    by_type = {}
    for e in _EXTRACTED_ENTITIES:
        by_type.setdefault(e["type"], []).append(e)
    return by_type


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class SpeechToCRMAgent(BasicAgent):
    """
    Speech-to-CRM pipeline agent.

    Operations:
        transcribe_call   - transcribe and display call recording
        extract_entities  - extract named entities from transcript
        crm_mapping       - map extracted entities to CRM fields
        update_preview    - preview CRM record updates before applying
    """

    def __init__(self):
        self.name = "SpeechToCRMAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "transcribe_call", "extract_entities",
                            "crm_mapping", "update_preview",
                        ],
                        "description": "The speech-to-CRM operation to perform",
                    },
                    "call_id": {
                        "type": "string",
                        "description": "Call ID (e.g. 'CALL-T001')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "transcribe_call")
        call_id = kwargs.get("call_id", "CALL-T001")
        dispatch = {
            "transcribe_call": self._transcribe_call,
            "extract_entities": self._extract_entities,
            "crm_mapping": self._crm_mapping,
            "update_preview": self._update_preview,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(call_id)

    def _transcribe_call(self, call_id):
        call = _CALL_TRANSCRIPTS.get(call_id, list(_CALL_TRANSCRIPTS.values())[0])
        transcript = _format_transcript(call["id"])
        return (
            f"**Call Transcription: {call['id']}**\n\n"
            f"| Field | Detail |\n|---|---|\n"
            f"| Date | {call['date']} |\n"
            f"| Duration | {call['duration_sec'] // 60}m {call['duration_sec'] % 60}s |\n"
            f"| Participants | {', '.join(call['participants'])} |\n"
            f"| Confidence | {call['confidence_score']:.0%} |\n\n"
            f"**Transcript:**\n\n{transcript}\n\n"
            f"Source: [Speech-to-Text Engine]\nAgents: SpeechToCRMAgent"
        )

    def _extract_entities(self, call_id):
        entity_rows = ""
        for e in _EXTRACTED_ENTITIES:
            entity_rows += f"| {e['type'].title()} | {e['value']} | {e['confidence']:.0%} | {e['context'][:45]} |\n"
        by_type = _entity_summary()
        summary = "\n".join(f"- {t.title()}: {len(entities)}" for t, entities in by_type.items())
        return (
            f"**Entity Extraction Results**\n\n"
            f"| Type | Value | Confidence | Context |\n|---|---|---|---|\n"
            f"{entity_rows}\n"
            f"**Summary by Type:**\n{summary}\n\n"
            f"**Total Entities:** {len(_EXTRACTED_ENTITIES)}\n\n"
            f"Source: [NLP Entity Extraction Engine]\nAgents: SpeechToCRMAgent"
        )

    def _crm_mapping(self, call_id):
        opp = _CRM_FIELD_MAPPINGS["opportunity"]
        opp_rows = "\n".join(f"| {field} | {info['source']} | {info['mapped_value']} |" for field, info in opp.items())
        contact = _CRM_FIELD_MAPPINGS["contact"]
        contact_rows = "\n".join(f"| {field} | {info['source']} | {info['mapped_value']} |" for field, info in contact.items())
        new_contacts = _CRM_FIELD_MAPPINGS["new_contacts"]
        new_rows = "\n".join(f"| {c['name']} | {c['title']} | {c['role']} |" for c in new_contacts)
        return (
            f"**CRM Field Mapping**\n\n"
            f"**Opportunity Update:**\n\n"
            f"| Field | Source | Mapped Value |\n|---|---|---|\n"
            f"{opp_rows}\n\n"
            f"**Contact Update:**\n\n"
            f"| Field | Source | Mapped Value |\n|---|---|---|\n"
            f"{contact_rows}\n\n"
            f"**New Contacts to Create:**\n\n"
            f"| Name | Title | Role |\n|---|---|---|\n"
            f"{new_rows}\n\n"
            f"Source: [CRM Mapping Engine]\nAgents: SpeechToCRMAgent"
        )

    def _update_preview(self, call_id):
        opp = _CRM_FIELD_MAPPINGS["opportunity"]
        activity = _CRM_FIELD_MAPPINGS["activity"]
        new_contacts = _CRM_FIELD_MAPPINGS["new_contacts"]
        return (
            f"**CRM Update Preview**\n\n"
            f"**1. Update Opportunity**\n"
            f"- Name: {opp['name']['mapped_value']}\n"
            f"- Amount: ${opp['amount']['mapped_value']:,}\n"
            f"- Stage: {opp['stage']['mapped_value']}\n"
            f"- Close Date: {opp['close_date']['mapped_value']}\n"
            f"- Probability: {opp['probability']['mapped_value']}%\n"
            f"- Next Step: {opp['next_step']['mapped_value']}\n\n"
            f"**2. Log Activity**\n"
            f"- Type: {activity['type']['mapped_value']}\n"
            f"- Subject: {activity['subject']['mapped_value']}\n"
            f"- Duration: {activity['duration_min']['mapped_value']} minutes\n\n"
            f"**3. Create Contacts ({len(new_contacts)}):**\n"
            + "\n".join(f"- {c['name']} ({c['title']}, {c['role']})" for c in new_contacts)
            + "\n\n"
            f"**Status:** Ready to apply | Requires confirmation\n\n"
            f"Source: [CRM Update Engine]\nAgents: SpeechToCRMAgent"
        )


if __name__ == "__main__":
    agent = SpeechToCRMAgent()
    for op in ["transcribe_call", "extract_entities", "crm_mapping", "update_preview"]:
        print("=" * 60)
        print(agent.perform(operation=op, call_id="CALL-T001"))
        print()
