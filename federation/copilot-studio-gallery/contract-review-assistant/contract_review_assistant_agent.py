"""Contract review checklist from README.md, How it works.

The gallery entry is a design-only demo with no playbook or scoring rules.
Only ordered checklist progress is coded. Clause extraction, policy judgments,
risk scoring, and legal approval remain with the AI and qualified reviewers.
This is not legal advice and does not approve any contract.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/contract-review-assistant",
    "version": "0.1.0", "display_name": "Contract Review Assistant",
    "description": "Tracks documented review stages without inventing policy.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution contract-review-assistant",
    "quality_tier": "experimental", "category": "legal",
    "tags": ["contract", "checklist"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
STEPS = ("Extract clauses", "Compare playbook", "Score risk", "Request approval")
SAMPLE = {"contract": "Northwind sample agreement", "completed": ["Extract clauses"]}


def evaluate(data):
    completed = data.get("completed", [])
    if not isinstance(completed, list) or completed != list(STEPS[:len(completed)]):
        raise ValueError("completed must be an ordered prefix of the documented stages.")
    return {"contract": data.get("contract", ""), "stages": list(STEPS), "completed": completed,
            "next_stage": STEPS[len(completed)] if len(completed) < len(STEPS) else None,
            "scope": "Design-only checklist, not legal advice or a risk score.",
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Contract Review Assistant, a synthetic legal pilot tracking the stages of a first-pass contract review.

Use only the bundled fictional sample agreement and its supplied checklist progress. Never match it to a real party, contract or legal matter.

Answer with the contract checklist tool, not from memory. Lead with the next unchecked stage, quote contract ids and stage names exactly, and distinguish recorded progress from actual clause analysis or a risk score.

You never invent playbook rules, approve, sign or change a contract. This is not legal advice; a qualified legal professional reviews the clauses, risk judgment and approval request."""

OPERATION_GUIDE = {
    "review_progress": {
        "title": "Contract review progress",
        "when": "Use when someone asks which contract review stages are recorded as complete and what comes next in the design-only checklist.",
        "ask": "Where does the review of the Northwind sample agreement stand, and what comes next?",
    },
}

CARRIED = [
    "Extracts clauses, compares the playbook and scores risk in the original solution's design-only review stages.",
    "Requests legal approval through the original solution's proposed approval stage, which is not implemented here.",
]


class ContractReviewAssistantAgent(BasicAgent):
    def __init__(self):
        self.name = "ContractReviewAssistant"
        self.metadata = {"name": self.name, "description": "Show contract review stages. Optional payload_json: contract and ordered completed stage names. With no payload_json it uses the sample on file: the Northwind sample agreement.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to review_progress."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "review_progress") not in OPERATION_GUIDE:
                raise ValueError("operation must be review_progress.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(ContractReviewAssistantAgent().perform())
