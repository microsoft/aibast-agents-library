"""Support case checklist from README.md, How it works.

The source is a design-only demo without classification or risk thresholds.
This file tracks stages only. Classification, grounded drafting, and risk
judgment remain with the AI; review and case updates remain external.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/customer-support-triage",
    "version": "0.1.0", "display_name": "Customer Support Triage",
    "description": "Shows the documented support case checklist, including human review.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution customer-support-triage",
    "quality_tier": "experimental", "category": "service",
    "tags": ["support", "checklist"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
STEPS = ("Classify case", "Search knowledge", "Draft response", "Human review", "Update case")
SAMPLE = {"case": "Contoso sample case", "completed": ["Classify case", "Search knowledge"]}


def evaluate(data):
    completed = data.get("completed", [])
    if not isinstance(completed, list) or completed != list(STEPS[:len(completed)]):
        raise ValueError("completed must be an ordered prefix of the documented stages.")
    return {"case": data.get("case", ""), "stages": list(STEPS), "completed": completed,
            "next_stage": STEPS[len(completed)] if len(completed) < len(STEPS) else None,
            "scope": "Design-only checklist; no case is classified, answered, or updated.",
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Customer Support Triage, a synthetic service pilot tracking a case from classification to a reviewed response and case update.

Use only the bundled fictional sample case and its supplied checklist progress. Never match it to a real customer, support ticket or knowledge record.

Answer with the support checklist tool, not from memory. Lead with the next unchecked stage, quote case ids and stage names exactly, and state that progress does not prove a case was classified or answered.

You never invent classification thresholds, send a customer response or update a real case. A support reviewer checks the grounded response and risk judgment before any customer communication."""

OPERATION_GUIDE = {
    "case_progress": {
        "title": "Support case progress",
        "when": "Use when someone asks which support case stages are recorded as complete or whether drafting, human review or a case update is next.",
    },
}

CARRIED = [
    "Classifies the case, searches knowledge and drafts a grounded response in the original solution's design-only support stages.",
    "Performs human review and updates the case through the original solution's proposed review and case-update stages, which are not implemented here.",
]


class CustomerSupportTriageAgent(BasicAgent):
    def __init__(self):
        self.name = "CustomerSupportTriage"
        self.metadata = {"name": self.name, "description": "Show support case stages. Optional payload_json: case and ordered completed stage names.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to case_progress."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "case_progress") not in OPERATION_GUIDE:
                raise ValueError("operation must be case_progress.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(CustomerSupportTriageAgent().perform())
