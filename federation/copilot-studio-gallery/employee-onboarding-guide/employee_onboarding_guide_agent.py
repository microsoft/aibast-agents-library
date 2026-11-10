"""Onboarding checklist from README.md, How it works.

The source is a design-only demo. This file tracks the four stated stages;
policy answers, checklist authoring, access provisioning, and welcome delivery
remain with the AI, authorized tools, and people. All example data is fictional.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/employee-onboarding-guide",
    "version": "0.1.0", "display_name": "Employee Onboarding Guide",
    "description": "Tracks the documented onboarding stages without provisioning access.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution employee-onboarding-guide",
    "quality_tier": "experimental", "category": "hr",
    "tags": ["onboarding", "checklist"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
STEPS = ("Create checklist", "Provision access", "Send welcome plan", "Check progress")
SAMPLE = {"hire": "Contoso sample hire", "completed": ["Create checklist"]}


def evaluate(data):
    completed = data.get("completed", [])
    if not isinstance(completed, list) or completed != list(STEPS[:len(completed)]):
        raise ValueError("completed must be an ordered prefix of the documented stages.")
    return {"hire": data.get("hire", ""), "stages": list(STEPS), "completed": completed,
            "next_stage": STEPS[len(completed)] if len(completed) < len(STEPS) else None,
            "scope": "Design-only checklist; no accounts or messages are created.",
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Employee Onboarding Guide, a synthetic people-operations pilot tracking a hire's onboarding stages.

Use only the bundled fictional sample hire and supplied checklist progress. Never match them to a real employee, manager or account.

Answer with the onboarding checklist tool, not from memory. Lead with the next unchecked stage, quote hire ids and stage names exactly, and distinguish reported progress from verified provisioning or message delivery.

You never create an account, grant access or send a welcome message. A people-operations reviewer checks the plan and an authorized access owner reviews provisioning before real changes."""

OPERATION_GUIDE = {
    "onboarding_progress": {
        "title": "Onboarding checklist progress",
        "when": "Use when someone asks which onboarding stages are recorded as complete and whether access, the welcome plan or a progress check comes next.",
        "ask": "Where does onboarding stand for the Contoso sample hire, and what comes next?",
    },
}

CARRIED = [
    "Answers policy questions and authors the checklist in the original solution's design-only onboarding plan.",
    "Provisions access, delivers the welcome plan and checks progress through the original solution's proposed onboarding stages, which are not implemented here.",
]


class EmployeeOnboardingGuideAgent(BasicAgent):
    def __init__(self):
        self.name = "EmployeeOnboardingGuide"
        self.metadata = {"name": self.name, "description": "Show onboarding stages. Optional payload_json: hire and ordered completed stage names. With no payload_json it uses the sample on file: the Contoso sample hire.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to onboarding_progress."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "onboarding_progress") not in OPERATION_GUIDE:
                raise ValueError("operation must be onboarding_progress.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(EmployeeOnboardingGuideAgent().perform())
