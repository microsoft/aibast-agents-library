"""ReplyNeeded gate from README.md, How it works.

Accepts the structured output of the research agent and preserves the triggering
message ID. Only Yes proceeds to a reply plan; No ends without replying.
Question extraction, source research, citations, follow-ups, and HTML drafting
stay with the AI. This file cannot send mail or choose another recipient.
The bundled source-shaped example is fictional.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/outlook-triggered-workflow-agent",
    "version": "0.1.0", "display_name": "Knowledge Inbox Reply Gate",
    "description": "Applies the explicit reply-needed branch to the original message.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution outlook-triggered-workflow-agent",
    "quality_tier": "experimental", "category": "knowledge",
    "tags": ["email", "routing"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"message_id": "CONTOSO-SAMPLE-M1", "ReplyNeeded": "No", "EmailReply": ""}


def evaluate(data):
    decision = data["ReplyNeeded"]
    if decision not in ("Yes", "No"):
        raise ValueError("ReplyNeeded must be Yes or No, as returned by the research step.")
    if decision == "No":
        return {"should_reply": False, "reply_plan": None, "sent": False}
    message_id, body = data["message_id"], data["EmailReply"]
    if not isinstance(message_id, str) or not message_id.strip() or not isinstance(body, str) or not body.strip():
        raise ValueError("A Yes reply requires the triggering message_id and nonempty EmailReply.")
    return {"should_reply": True, "reply_plan": {"message_id": message_id, "html_body": body,
                                               "recipient": "Original message sender, resolved by reply action"},
            "sent": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Knowledge Inbox Reply Gate, a synthetic knowledge-service pilot checking an already-researched reply decision.

Use only the bundled fictional message CONTOSO-SAMPLE-M1 and its reply-needed result. Never match them to a real sender, mailbox or research request.

Answer with the reply gate tool, not from memory. Lead with whether a reply is needed, quote the triggering message id and decision exactly, and require a nonempty reply body for Yes without choosing a different recipient.

You never research live sources or send mail. A knowledge reviewer checks research, citations and the complete reply before the separate reply action addresses the original sender."""

OPERATION_GUIDE = {
    "reply_gate": {
        "title": "Knowledge inbox reply gate",
        "when": "Use when someone asks whether a research result marked Yes or No should produce a reply plan for the original triggering message.",
        "ask": "Does the research result for the sample email on file mean we should reply to the original message?",
    },
}

CARRIED = [
    "Extracts questions, researches sources, adds citations, handles follow-ups and drafts HTML through the original solution's research agent.",
    "Triggers on incoming mail and replies to the original message through the original solution's Outlook workflow.",
]


class OutlookTriggeredWorkflowAgent(BasicAgent):
    def __init__(self):
        self.name = "KnowledgeInboxReplyGate"
        self.metadata = {"name": self.name, "description": "Check research output. Optional payload_json: triggering message_id, ReplyNeeded Yes/No, EmailReply HTML. No alternate recipient is accepted. With no payload_json it uses the sample on file: the sample triggering email and its research result.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to reply_gate."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "reply_gate") not in OPERATION_GUIDE:
                raise ValueError("operation must be reply_gate.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(OutlookTriggeredWorkflowAgent().perform())
