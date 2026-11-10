"""Store feedback checklist from the design-only gallery README.md.

There is no feedback corpus or sentiment rule in the source. This file tracks
the documented stages only. Sentiment, theme grouping, and recommended actions
remain with the AI and operations reviewers, not keyword-based guesses.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/store-feedback-analyzer",
    "version": "0.1.0", "display_name": "Store Feedback Analyzer",
    "description": "Tracks documented feedback stages without inventing sentiment rules.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution store-feedback-analyzer",
    "quality_tier": "experimental", "category": "retail",
    "tags": ["feedback", "checklist"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
STEPS = ("Collect feedback", "Detect sentiment", "Group themes", "Recommend actions")
SAMPLE = {"store": "Contoso sample shop", "completed": ["Collect feedback"]}


def evaluate(data):
    completed = data.get("completed", [])
    if not isinstance(completed, list) or completed != list(STEPS[:len(completed)]):
        raise ValueError("completed must be an ordered prefix of the documented stages.")
    return {"store": data.get("store", ""), "stages": list(STEPS), "completed": completed,
            "next_stage": STEPS[len(completed)] if len(completed) < len(STEPS) else None,
            "scope": "Design-only checklist; no sentiment or themes are inferred.",
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Store Feedback Analyzer, a synthetic retail pilot tracking a store feedback review checklist.

Use only the bundled fictional sample shop and supplied completed stages. Never match them to real customers, feedback entries or stores.

Answer with the feedback checklist tool, not from memory. Lead with the next unchecked stage, quote store ids and stage names exactly, and state that sentiment, themes and recommendations have not been inferred.

You never invent a feedback corpus or sentiment rule or claim to change store operations. An operations reviewer checks the feedback evidence, theme interpretation and proposed actions before adopting recommendations."""

OPERATION_GUIDE = {
    "feedback_progress": {
        "title": "Feedback review progress",
        "when": "Use when someone asks which store feedback stages are recorded as complete and whether sentiment, theme grouping or recommendations come next.",
        "ask": "Where does the feedback review for the Contoso sample shop stand, and what is the next step?",
    },
}

CARRIED = [
    "Collects feedback in the original solution's proposed collection stage.",
    "Interprets sentiment, groups themes and recommends actions in the original solution's design-only feedback stages, which are not implemented here.",
]


class StoreFeedbackAnalyzerAgent(BasicAgent):
    def __init__(self):
        self.name = "StoreFeedbackAnalyzer"
        self.metadata = {"name": self.name, "description": "Show feedback review stages. Optional payload_json: store and ordered completed stage names. With no payload_json it uses the sample on file: the Contoso sample shop.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to feedback_progress."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "feedback_progress") not in OPERATION_GUIDE:
                raise ValueError("operation must be feedback_progress.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(StoreFeedbackAnalyzerAgent().perform())
