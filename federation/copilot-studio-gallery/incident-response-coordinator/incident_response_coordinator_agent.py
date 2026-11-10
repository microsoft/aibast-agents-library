"""Incident checklist from README.md, How it works.

The source is a design-only demo without severity rules. Only ordered progress
is coded. Signal interpretation and updates remain with the AI and responders;
telemetry collection, bridge creation, and incident closure remain external.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/incident-response-coordinator",
    "version": "0.1.0", "display_name": "Incident Response Coordinator",
    "description": "Tracks documented incident stages without inventing severity rules.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution incident-response-coordinator",
    "quality_tier": "experimental", "category": "operations",
    "tags": ["incident", "checklist"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
STEPS = ("Collect telemetry", "Assess severity", "Open bridge", "Post updates", "Close incident")
SAMPLE = {"incident": "Fabrikam sample outage", "completed": ["Collect telemetry"]}


def evaluate(data):
    completed = data.get("completed", [])
    if not isinstance(completed, list) or completed != list(STEPS[:len(completed)]):
        raise ValueError("completed must be an ordered prefix of the documented stages.")
    return {"incident": data.get("incident", ""), "stages": list(STEPS), "completed": completed,
            "next_stage": STEPS[len(completed)] if len(completed) < len(STEPS) else None,
            "scope": "Design-only checklist; no bridge or incident record is changed.",
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Incident Response Coordinator, a synthetic operations pilot tracking an incident response checklist.

Use only the bundled fictional sample outage and supplied completed stages. Never match them to a real service, incident or responder.

Answer with the incident checklist tool, not from memory. Lead with the next unchecked stage, quote incident ids and stage names exactly, and do not turn recorded progress into a severity judgment.

You never collect live telemetry, open a bridge, publish an update or close an incident. An incident commander reviews signal interpretation, severity and communications before responders take action."""

OPERATION_GUIDE = {
    "incident_progress": {
        "title": "Incident checklist progress",
        "when": "Use when someone asks which incident stages are recorded as complete and whether severity assessment, a bridge, updates or closure is next.",
        "ask": "Where does the Fabrikam sample outage stand, and what is the next step?",
    },
}

CARRIED = [
    "Interprets signals, assesses severity and drafts updates in the original solution's design-only response stages.",
    "Collects telemetry, opens a bridge, posts updates and closes the incident through the original solution's proposed connected stages, which are not implemented here.",
]


class IncidentResponseCoordinatorAgent(BasicAgent):
    def __init__(self):
        self.name = "IncidentResponseCoordinator"
        self.metadata = {"name": self.name, "description": "Show incident stages. Optional payload_json: incident and ordered completed stage names. With no payload_json it uses the sample on file: the Fabrikam sample outage.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to incident_progress."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "incident_progress") not in OPERATION_GUIDE:
                raise ValueError("operation must be incident_progress.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(IncidentResponseCoordinatorAgent().perform())
