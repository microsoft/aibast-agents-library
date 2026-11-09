"""Thread evidence view and posting gates from README.md, Agent and actions.

Recap entries are supplied as exact quotations with message IDs. This file
checks those references and renders an evidence view, with no invented owners
or dates. Thread selection, synthesis, and confidentiality judgment stay with
the AI. Only reviewed, non-confidential recaps with a confirmed standard
channel get a posting plan. No mail or channel is read or changed.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/email-thread-synthesis",
    "version": "0.1.0", "display_name": "Project Thread Evidence View",
    "description": "Checks recap quotations and confirmed standard-channel posting gates.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution email-thread-synthesis",
    "quality_tier": "experimental", "category": "productivity",
    "tags": ["email", "evidence"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"messages": [{"id": "M1", "body": "Contoso launch remains on hold pending budget approval."}],
          "recap": [{"category": "risk", "message_id": "M1",
                     "quote": "Contoso launch remains on hold pending budget approval."}],
          "confidential": False, "recap_reviewed": True, "destination_confirmed": False,
          "team": "Contoso delivery", "channel": "Project updates", "channel_type": "standard"}


def evaluate(data):
    messages = {}
    for message in data["messages"]:
        if not isinstance(message["body"], str) or message["id"] in messages:
            raise ValueError("Messages need unique IDs and text bodies.")
        messages[message["id"]] = message["body"]
    recap = data["recap"]
    for item in recap:
        if item["category"] not in ("decision", "action", "question", "risk"):
            raise ValueError("Recap category must be decision, action, question, or risk.")
        quote = item["quote"]
        if not isinstance(quote, str) or not quote.strip() or quote not in messages.get(item["message_id"], ""):
            raise ValueError("Every recap quote must occur in its referenced message.")
    for field in ("confidential", "recap_reviewed", "destination_confirmed"):
        if type(data.get(field)) is not bool:
            raise ValueError(field + " must be an explicit Boolean.")
    allowed = (bool(recap) and not data["confidential"] and data["recap_reviewed"]
               and data["destination_confirmed"] and data.get("channel_type") == "standard"
               and bool(data.get("team", "").strip()) and bool(data.get("channel", "").strip()))
    return {"evidence_view": recap, "may_post": allowed,
            "destination": {"team": data.get("team", ""), "channel": data.get("channel", "")} if allowed else None,
            "posted": False, "mail_modified": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Project Thread Evidence View, a synthetic collaboration pilot checking recap quotations and channel-posting gates.

Use only the bundled fictional message M1, its quoted risk and the sample destination and review flags. Never match them to a real mailbox, project or conversation.

Answer with the thread evidence tool, not from memory. Lead with the checked recap and posting eligibility, quote message ids and supporting text exactly, and never invent an action owner or due date.

You never read or modify live mail or post a recap. A project reviewer checks confidentiality and the full recap, then confirms the destination before any standard-channel posting."""

OPERATION_GUIDE = {
    "recap_check": {
        "title": "Recap evidence and posting check",
        "when": "Use when someone asks whether recap quotations occur in their referenced messages and whether review, confidentiality and destination gates allow posting.",
    },
}

CARRIED = [
    "Selects the email thread, synthesizes the recap and judges confidentiality through the original solution's thread-synthesis agent.",
    "Reads messages and posts the reviewed recap to a confirmed standard Teams channel through the original solution's actions.",
]


class EmailThreadSynthesisAgent(BasicAgent):
    def __init__(self):
        self.name = "ThreadEvidenceView"
        self.metadata = {"name": self.name, "description": "Check quoted recap evidence and posting eligibility. Optional payload_json: messages [{id,body}], recap [{category,message_id,quote}], confidential, recap_reviewed, destination_confirmed Booleans, team, channel, channel_type.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to recap_check."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "recap_check") not in OPERATION_GUIDE:
                raise ValueError("operation must be recap_check.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(EmailThreadSynthesisAgent().perform())
