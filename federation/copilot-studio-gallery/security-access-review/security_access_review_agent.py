"""Access review checklist from README.md, How it works.

The source is a design-only demo with no anomaly rules. Only the stated stage
order is coded. Anomaly interpretation stays with the AI and reviewers; access
lookup, evidence collection, and actual decisions remain external. This file
never grants, revokes, or certifies access.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/security-access-review",
    "version": "0.1.0", "display_name": "Security Access Review",
    "description": "Tracks documented access review stages without deciding access.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution security-access-review",
    "quality_tier": "experimental", "category": "governance",
    "tags": ["access", "checklist"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
STEPS = ("Load access list", "Detect anomalies", "Collect evidence", "Record decision")
SAMPLE = {"review": "Contoso sample quarterly review", "completed": ["Load access list"]}


def evaluate(data):
    completed = data.get("completed", [])
    if not isinstance(completed, list) or completed != list(STEPS[:len(completed)]):
        raise ValueError("completed must be an ordered prefix of the documented stages.")
    return {"review": data.get("review", ""), "stages": list(STEPS), "completed": completed,
            "next_stage": STEPS[len(completed)] if len(completed) < len(STEPS) else None,
            "scope": "Design-only checklist; no access decision is made or recorded.",
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Security Access Review, a synthetic governance pilot tracking a quarterly access review checklist.

Use only the bundled fictional quarterly review and supplied completed stages. Never match them to a real user, permission, system or access decision.

Answer with the access checklist tool, not from memory. Lead with the next unchecked stage, quote review ids and stage names exactly, and do not infer anomalies or authorization from recorded progress.

You never grant, revoke, certify or record real access. An authorized access reviewer evaluates evidence and makes the decision before any permission change or certification."""

OPERATION_GUIDE = {
    "access_review_progress": {
        "title": "Access review progress",
        "when": "Use when someone asks which access review stages are recorded as complete and whether anomaly review, evidence collection or decision recording is next.",
    },
}

CARRIED = [
    "Loads access records and collects evidence in the original solution's proposed connected review stages.",
    "Interprets anomalies and records reviewed decisions in the original solution's design-only access workflow, which is not implemented here.",
]


class SecurityAccessReviewAgent(BasicAgent):
    def __init__(self):
        self.name = "SecurityAccessReview"
        self.metadata = {"name": self.name, "description": "Show access review stages. Optional payload_json: review and ordered completed stage names.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to access_review_progress."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "access_review_progress") not in OPERATION_GUIDE:
                raise ValueError("operation must be access_review_progress.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(SecurityAccessReviewAgent().perform())
