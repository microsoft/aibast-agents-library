"""Project status checklist from README.md, How it works.

The source is a design-only demo. Ordered progress is deterministic; collecting
live delivery signals, interpreting risks, and writing the narrative remain
with the AI and connected tools. This file does not send an update.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/project-status-narrator",
    "version": "0.1.0", "display_name": "Project Status Narrator",
    "description": "Tracks the documented status update checklist.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution project-status-narrator",
    "quality_tier": "experimental", "category": "productivity",
    "tags": ["project", "checklist"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
STEPS = ("Collect delivery signals", "Summarize progress", "Highlight risks", "Send update")
SAMPLE = {"project": "Contoso warehouse refresh", "completed": ["Collect delivery signals"]}


def evaluate(data):
    completed = data.get("completed", [])
    if not isinstance(completed, list) or completed != list(STEPS[:len(completed)]):
        raise ValueError("completed must be an ordered prefix of the documented stages.")
    return {"project": data.get("project", ""), "stages": list(STEPS), "completed": completed,
            "next_stage": STEPS[len(completed)] if len(completed) < len(STEPS) else None,
            "scope": "Design-only checklist; no status narrative or message is generated.",
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Project Status Narrator, a synthetic delivery pilot tracking the preparation of a project status update.

Use only the bundled fictional warehouse refresh and supplied completed stages. Never match them to a real project, team or delivery signal.

Answer with the project checklist tool, not from memory. Lead with the next unchecked stage, quote project ids and stage names exactly, and do not invent progress, risks or a narrative from the checklist.

You never collect live delivery data or send an update. A project owner reviews source signals, the progress summary and highlighted risks before a separate communication is sent."""

OPERATION_GUIDE = {
    "status_progress": {
        "title": "Project update progress",
        "when": "Use when someone asks which project update stages are recorded as complete and whether progress summary, risk review or sending is next.",
        "ask": "Where does the Contoso warehouse refresh status update stand, and what is the next step?",
    },
}

CARRIED = [
    "Collects live delivery signals through the original solution's proposed connected collection stage.",
    "Interprets progress and risks, drafts the narrative and sends updates in the original solution's design-only status workflow, which is not implemented here.",
]


class ProjectStatusNarratorAgent(BasicAgent):
    def __init__(self):
        self.name = "ProjectStatusNarrator"
        self.metadata = {"name": self.name, "description": "Show project update stages. Optional payload_json: project and ordered completed stage names. With no payload_json it uses the sample on file: the Contoso warehouse refresh project.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to status_progress."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "status_progress") not in OPERATION_GUIDE:
                raise ValueError("operation must be status_progress.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(ProjectStatusNarratorAgent().perform())
