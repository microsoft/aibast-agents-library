"""Campaign kit checklist from README.md, How it works.

The source is a design-only demo, not an implemented publishing workflow.
This cartridge tracks its stated stages; drafting, brand judgments, review,
and publishing stay with the AI, people, and connected tools. No work is sent.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/campaign-content-engine",
    "version": "0.1.0", "display_name": "Campaign Content Engine",
    "description": "Tracks the documented campaign checklist without publishing.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution campaign-content-engine",
    "quality_tier": "experimental", "category": "marketing",
    "tags": ["campaign", "checklist"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
STEPS = ("Read brief", "Load brand voice", "Draft channels", "Review content", "Publish kit")
SAMPLE = {"campaign": "Contoso autumn launch", "completed": ["Read brief"]}


def evaluate(data):
    completed = data.get("completed", [])
    if not isinstance(completed, list) or completed != list(STEPS[:len(completed)]):
        raise ValueError("completed must be an ordered prefix of the documented stages.")
    return {"campaign": data.get("campaign", ""), "stages": list(STEPS),
            "completed": completed, "next_stage": STEPS[len(completed)] if len(completed) < len(STEPS) else None,
            "scope": "Design-only checklist; completion is supplied, not verified.",
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Campaign Content Engine, a synthetic marketing pilot tracking a campaign kit from brief through publication readiness.

Use only the bundled fictional autumn launch and its supplied checklist progress. Never match it to a real company, brand or campaign.

Answer with the campaign checklist tool, not from memory. Lead with the next unchecked stage, quote campaign ids and stage names exactly, and state that reported completion is supplied rather than verified.

You never claim to draft, approve or publish a kit from checklist progress. A campaign owner reviews content and brand fit before any external publication."""

OPERATION_GUIDE = {
    "campaign_progress": {
        "title": "Campaign checklist progress",
        "when": "Use when someone asks which campaign stages are recorded as complete and what comes next in the design-only checklist.",
        "ask": "Where does the Contoso autumn launch campaign stand, and what is the next step?",
    },
}

CARRIED = [
    "Reads the brief, loads brand voice and drafts channel content in the original solution's design-only campaign stages.",
    "Reviews content and publishes the kit through the original solution's proposed review and publishing stages, which are not implemented here.",
]


class CampaignContentEngineAgent(BasicAgent):
    def __init__(self):
        self.name = "CampaignContentEngine"
        self.metadata = {"name": self.name, "description": "Show campaign stages and the next unchecked stage. Optional payload_json: campaign and ordered completed stage names. With no payload_json it uses the sample on file: the Contoso autumn launch campaign.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to campaign_progress."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "campaign_progress") not in OPERATION_GUIDE:
                raise ValueError("operation must be campaign_progress.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(CampaignContentEngineAgent().perform())
