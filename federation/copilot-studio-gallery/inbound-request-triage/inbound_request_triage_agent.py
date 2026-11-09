"""Classification branch and configured-team check from the gallery README.md.

Only Actionable request continues; Noise and Other stop. A proposed team must
be in supplied RoutingEmails. Classifying free text, choosing a team, composing
acknowledgments, and summarizing the request stay with the AI.
No email is sent. Sample addresses use fictional Contoso data.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/inbound-request-triage",
    "version": "0.1.0", "display_name": "Inbound Request Routing Check",
    "description": "Checks the documented actionable branch and configured routing destination.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution inbound-request-triage",
    "quality_tier": "experimental", "category": "operations",
    "tags": ["intake", "routing"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"classification": "Actionable request", "RoutingEmails": {"Finance": "finance@contoso.example", "Facilities": "facilities@contoso.example"},
          "routingTeamEmail": "facilities@contoso.example"}


def evaluate(data):
    classification = data["classification"]
    if classification not in ("Actionable request", "Noise", "Other"):
        raise ValueError("classification must be Actionable request, Noise, or Other.")
    if classification != "Actionable request":
        return {"continue": False, "acknowledge": False, "route_to": None, "sent": False}
    routes = data["RoutingEmails"]
    if not isinstance(routes, dict) or not routes or any(not isinstance(value, str) or not value.strip() for value in routes.values()):
        raise ValueError("RoutingEmails must map team names to nonempty addresses.")
    destination = data["routingTeamEmail"]
    if destination not in routes.values():
        raise ValueError("routingTeamEmail is not an allowed configured destination.")
    return {"continue": True, "acknowledge": True, "route_to": destination, "sent": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Inbound Request Routing Check, a synthetic operations pilot checking an already-classified request against configured routing addresses.

Use only the bundled fictional classification and Finance and Facilities routing entries. Never match them to a real sender, mailbox or department.

Answer with the routing tool, not from memory. Lead with whether processing continues and the permitted destination, quote classification values, addresses and ids exactly, and stop Noise and Other without acknowledgment.

You never classify live mail, invent a destination, acknowledge or forward a request. An intake reviewer checks the classification, team choice and message draft before any send."""

OPERATION_GUIDE = {
    "routing_check": {
        "title": "Inbound routing check",
        "when": "Use when someone asks whether a supplied classification continues and whether the chosen routing address is one of the configured team destinations.",
    },
}

CARRIED = [
    "Classifies free text, chooses a team, summarizes the request and composes an acknowledgment through the original solution's triage AI steps.",
    "Sends acknowledgments and routes actionable mail through the original solution's email workflow.",
]


class InboundRequestTriageAgent(BasicAgent):
    def __init__(self):
        self.name = "InboundRequestRoutingCheck"
        self.metadata = {"name": self.name, "description": "Check a supplied classification and routing choice. Optional payload_json: classification, RoutingEmails object mapping team to address, routingTeamEmail.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to routing_check."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "routing_check") not in OPERATION_GUIDE:
                raise ValueError("operation must be routing_check.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(InboundRequestTriageAgent().perform())
