"""Dispatch checklist from README.md, How it works.

The source is a design-only demo with no technician or scheduling data.
This file tracks the documented stages. Request assessment and technician
selection stay with the AI; reservations and notifications stay external.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/field-service-dispatch",
    "version": "0.1.0", "display_name": "Field Service Dispatch",
    "description": "Tracks the dispatch checklist without claiming a booked technician.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution field-service-dispatch",
    "quality_tier": "experimental", "category": "operations",
    "tags": ["dispatch", "checklist"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
STEPS = ("Assess request", "Find technician", "Reserve slot", "Notify customer")
SAMPLE = {"request": "Northwind sample service request", "completed": []}


def evaluate(data):
    completed = data.get("completed", [])
    if not isinstance(completed, list) or completed != list(STEPS[:len(completed)]):
        raise ValueError("completed must be an ordered prefix of the documented stages.")
    return {"request": data.get("request", ""), "stages": list(STEPS), "completed": completed,
            "next_stage": STEPS[len(completed)] if len(completed) < len(STEPS) else None,
            "scope": "Design-only checklist; no technician or slot is reserved.",
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Field Service Dispatch, a synthetic service-operations pilot tracking a request through a dispatch checklist.

Use only the bundled fictional sample service request and supplied completed stages. Never match them to a real customer, technician, location or booking.

Answer with the dispatch checklist tool, not from memory. Lead with the next unchecked stage, quote request ids and stage names exactly, and say that no technician or slot has been reserved.

You never assess a real service request, select or book a technician or notify a customer. A dispatcher reviews the request, technician choice and reservation before any customer notification."""

OPERATION_GUIDE = {
    "dispatch_progress": {
        "title": "Dispatch checklist progress",
        "when": "Use when someone asks which dispatch stages are recorded as complete and whether request assessment, technician search, reservation or notification is next.",
    },
}

CARRIED = [
    "Assesses the request and selects a technician in the original solution's design-only dispatch stages.",
    "Reserves slots and notifies customers through the original solution's proposed booking and notification stages, which are not implemented here.",
]


class FieldServiceDispatchAgent(BasicAgent):
    def __init__(self):
        self.name = "FieldServiceDispatch"
        self.metadata = {"name": self.name, "description": "Show dispatch stages. For defaults, omit payload_json; do not reconstruct the sample. Optional payload_json: request and ordered completed stage names.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to dispatch_progress."},
                             "payload_json": {"type": "string", "description": "Omit or leave blank for the exact bundled sample; otherwise send a JSON object."}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "dispatch_progress") not in OPERATION_GUIDE:
                raise ValueError("operation must be dispatch_progress.")
            raw = kwargs.get("payload_json", "")
            data = SAMPLE if isinstance(raw, str) and not raw.strip() else json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(FieldServiceDispatchAgent().perform())
