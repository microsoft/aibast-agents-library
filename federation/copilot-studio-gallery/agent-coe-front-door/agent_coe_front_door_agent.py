"""Confirmation and decision-notification gates from the gallery README.md.

Requests are prepared only after explicit confirmation. Approved and Rejected
decisions produce at most one plan for the same already-notified decision.
Guidance search, reuse recommendations, routing judgment, and intake drafting
stay with the AI. This file neither persists intake records nor sends notifications;
the caller must supply recorded send state. All sample records are fictional.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/agent-coe-front-door",
    "version": "0.1.0", "display_name": "Agent CoE Front Door",
    "description": "Checks confirmed intake and decision notification eligibility.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution agent-coe-front-door",
    "quality_tier": "experimental", "category": "governance",
    "tags": ["intake", "confirmation"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"operation": "intake", "summary": "Contoso inventory helper",
          "confirmed": False, "request_reference": "REQ-SAMPLE-001"}


def evaluate(data):
    operation = data.get("operation", "intake")
    if operation == "intake":
        if type(data.get("confirmed")) is not bool:
            raise ValueError("confirmed must be an explicit Boolean.")
        summary = data.get("summary", "")
        reference = data.get("request_reference", "")
        if not isinstance(summary, str) or not summary.strip():
            raise ValueError("A nonempty reviewed summary is required.")
        if not isinstance(reference, str) or not reference.startswith("REQ-"):
            raise ValueError("request_reference must start with REQ-.")
        return {"should_create": data["confirmed"], "reference": reference,
                "summary": summary, "created": False}
    if operation == "decision":
        decision = data["decision"]
        if decision not in ("Pending", "Approved", "Rejected"):
            raise ValueError("decision must be Pending, Approved, or Rejected.")
        return {"should_notify": decision in ("Approved", "Rejected") and decision != data.get("last_notified_decision"),
                "decision": decision, "sent": False,
                "note": "Caller records a successful send; this is not a delivery lock."}
    raise ValueError("operation must be intake or decision.")


# ---- Transfer layer ----
INSTRUCTIONS = """You are Agent Intake Front Door, a synthetic governance pilot for confirmed intake and decision notification checks.

Use only the bundled fictional request REQ-SAMPLE-001 and the sample decision state. Never match them to a real requester, organization or approval record.

Answer with the intake tool, not from memory. Lead with whether creation or notification is permitted, quote request ids and decisions exactly, and distinguish a plan from a completed write or send.

You never submit, approve, reject or notify on a real request. The requester reviews the summary and confirms intake; the governance reviewer owns the decision and checks recorded send state."""

OPERATION_GUIDE = {
    "intake": {
        "title": "Intake confirmation check",
        "when": "Use when someone asks whether a reviewed request summary has explicit confirmation to be recorded.",
    },
    "decision": {
        "title": "Decision notification check",
        "when": "Use when someone asks whether a Pending, Approved or Rejected decision needs a notification given the last notified decision.",
    },
}

CARRIED = [
    "Searches guidance, recommends reuse, chooses routing and drafts intake through the original solution's front-door agent.",
    "Persists confirmed intake records and sends decision notifications through the original solution's intake and notification workflow.",
]


class AgentCoeFrontDoorAgent(BasicAgent):
    def __init__(self):
        self.name = "AgentCoeFrontDoor"
        self.metadata = {"name": self.name, "description": "Check intake confirmation or decision notification. Optional payload_json: operation intake with summary, confirmed Boolean, request_reference; or decision with decision and last_notified_decision.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; overrides the payload operation. Default intake."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            if "operation" in kwargs:
                operation = kwargs["operation"]
                if operation not in OPERATION_GUIDE:
                    raise ValueError("operation must be intake or decision.")
                if "payload_json" not in kwargs and operation == "decision":
                    data = {"decision": "Pending", "last_notified_decision": None}
                data = {**data, "operation": operation}
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(AgentCoeFrontDoorAgent().perform())
