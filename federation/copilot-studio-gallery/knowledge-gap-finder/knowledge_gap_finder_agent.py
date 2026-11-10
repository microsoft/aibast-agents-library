"""Knowledge gap checklist from the design-only gallery README.md.

No article corpus, clustering method, or priority rubric ships with the demo.
This cartridge tracks its stated stages, not semantic question clusters.
Clustering, gap judgments, prioritization, and outlines stay with the AI.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/knowledge-gap-finder",
    "version": "0.1.0", "display_name": "Knowledge Gap Finder",
    "description": "Tracks the documented knowledge gap checklist.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution knowledge-gap-finder",
    "quality_tier": "experimental", "category": "knowledge",
    "tags": ["knowledge", "checklist"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
STEPS = ("Cluster questions", "Find missing topics", "Prioritize gaps", "Draft article outlines")
SAMPLE = {"review": "Fabrikam help desk sample", "completed": []}


def evaluate(data):
    completed = data.get("completed", [])
    if not isinstance(completed, list) or completed != list(STEPS[:len(completed)]):
        raise ValueError("completed must be an ordered prefix of the documented stages.")
    return {"review": data.get("review", ""), "stages": list(STEPS), "completed": completed,
            "next_stage": STEPS[len(completed)] if len(completed) < len(STEPS) else None,
            "scope": "Design-only checklist; no clusters or priorities are invented.",
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Knowledge Gap Finder, a synthetic knowledge-management pilot tracking a help desk knowledge review checklist.

Use only the bundled fictional help desk review and supplied completed stages. Never match them to real support questions, articles or customers.

Answer with the knowledge checklist tool, not from memory. Lead with the next unchecked stage, quote review ids and stage names exactly, and say that no question clusters or priorities have been inferred.

You never invent a missing-topic finding, priority rubric or article corpus. A knowledge owner reviews question grouping, evidence for gaps, priorities and article outlines before accepting them."""

OPERATION_GUIDE = {
    "gap_review_progress": {
        "title": "Knowledge gap review progress",
        "when": "Use when someone asks which knowledge review stages are recorded as complete and whether clustering, gap identification, prioritization or outlines come next.",
        "ask": "Where does the Fabrikam help desk sample review stand, and what is the next step?",
    },
}

CARRIED = [
    "Clusters questions and judges missing topics in the original solution's design-only knowledge review stages.",
    "Prioritizes gaps and drafts article outlines in the original solution's proposed prioritization and writing stages, which are not implemented here.",
]


class KnowledgeGapFinderAgent(BasicAgent):
    def __init__(self):
        self.name = "KnowledgeGapFinder"
        self.metadata = {"name": self.name, "description": "Show knowledge gap stages. Optional payload_json: review and ordered completed stage names. With no payload_json it uses the sample on file: the Fabrikam help desk sample review.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to gap_review_progress."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "gap_review_progress") not in OPERATION_GUIDE:
                raise ValueError("operation must be gap_review_progress.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(KnowledgeGapFinderAgent().perform())
