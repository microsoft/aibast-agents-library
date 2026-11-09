"""Account brief checklist from README.md, How it works.

The source is a design-only demo without CRM sample records. This file tracks
the four documented stages. CRM access, news retrieval, risk interpretation,
and grounded narrative drafting remain with the AI and connected tools.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/sales-account-brief",
    "version": "0.1.0", "display_name": "Sales Account Brief",
    "description": "Tracks the documented account briefing checklist.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution sales-account-brief",
    "quality_tier": "experimental", "category": "sales",
    "tags": ["account", "checklist"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
STEPS = ("Load CRM account", "Find recent signals", "Summarize risks", "Create brief")
SAMPLE = {"account": "Northwind Traders", "completed": ["Load CRM account"]}


def evaluate(data):
    completed = data.get("completed", [])
    if not isinstance(completed, list) or completed != list(STEPS[:len(completed)]):
        raise ValueError("completed must be an ordered prefix of the documented stages.")
    return {"account": data.get("account", ""), "stages": list(STEPS), "completed": completed,
            "next_stage": STEPS[len(completed)] if len(completed) < len(STEPS) else None,
            "scope": "Design-only checklist; no account facts or news are invented.",
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Sales Account Brief, a synthetic sales pilot tracking an account briefing checklist.

Use only the bundled fictional sample account and supplied completed stages. Never match them to a real company, customer relationship record or news story.

Answer with the account checklist tool, not from memory. Lead with the next unchecked stage, quote account ids and stage names exactly, and never invent account facts, recent signals or risks.

You never read live customer records, research current news or claim to create a grounded brief from progress alone. An account owner reviews source records, recent signals and risk interpretation before using a brief."""

OPERATION_GUIDE = {
    "brief_progress": {
        "title": "Account briefing progress",
        "when": "Use when someone asks which account briefing stages are recorded as complete and whether recent signals, risk summary or brief creation is next.",
    },
}

CARRIED = [
    "Loads CRM account records and retrieves recent news in the original solution's proposed connected briefing stages.",
    "Interprets risks and drafts a grounded brief in the original solution's design-only account workflow, which is not implemented here.",
]


class SalesAccountBriefAgent(BasicAgent):
    def __init__(self):
        self.name = "SalesAccountBrief"
        self.metadata = {"name": self.name, "description": "Show account brief stages. Optional payload_json: account and ordered completed stage names.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to brief_progress."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "brief_progress") not in OPERATION_GUIDE:
                raise ValueError("operation must be brief_progress.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(SalesAccountBriefAgent().perform())
