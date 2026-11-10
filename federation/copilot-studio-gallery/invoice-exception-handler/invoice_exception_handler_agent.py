"""Invoice exception checklist from README.md, How it works.

The source is a design-only demo with no purchase order or tolerance rules.
Only its stage order is implemented. Extraction, matching judgments, and
exception classification stay with the AI; finance approval stays human.
No invoice is posted or approved here.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/invoice-exception-handler",
    "version": "0.1.0", "display_name": "Invoice Exception Handler",
    "description": "Tracks invoice exception stages without inventing tolerance limits.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution invoice-exception-handler",
    "quality_tier": "experimental", "category": "finance",
    "tags": ["invoice", "checklist"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
STEPS = ("Read invoice", "Match purchase order", "Classify exception", "Request approval", "Post result")
SAMPLE = {"invoice": "NW-SAMPLE-001", "completed": ["Read invoice", "Match purchase order"]}


def evaluate(data):
    completed = data.get("completed", [])
    if not isinstance(completed, list) or completed != list(STEPS[:len(completed)]):
        raise ValueError("completed must be an ordered prefix of the documented stages.")
    return {"invoice": data.get("invoice", ""), "stages": list(STEPS), "completed": completed,
            "next_stage": STEPS[len(completed)] if len(completed) < len(STEPS) else None,
            "scope": "Design-only checklist, not a financial approval or posting.",
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Invoice Exception Handler, a synthetic accounts payable pilot tracking an invoice exception checklist.

Use only the bundled fictional invoice NW-SAMPLE-001 and supplied completed stages. Never match them to a real vendor, invoice or purchase order.

Answer with the exception checklist tool, not from memory. Lead with the next unchecked stage, quote invoice ids and stage names exactly, and distinguish recorded matching progress from a verified match or tolerance decision.

You never invent tolerance limits, approve an invoice or post a result. A finance reviewer checks the extracted invoice, purchase order and exception before any approval or posting."""

OPERATION_GUIDE = {
    "exception_progress": {
        "title": "Invoice exception progress",
        "when": "Use when someone asks which invoice exception stages are recorded as complete and whether classification, approval or posting comes next.",
        "ask": "Where does invoice NW-SAMPLE-001 stand in the exception process, and what comes next?",
    },
}

CARRIED = [
    "Reads invoices, judges purchase-order matches and classifies exceptions in the original solution's design-only invoice stages.",
    "Requests finance approval and posts results through the original solution's proposed approval and posting stages, which are not implemented here.",
]


class InvoiceExceptionHandlerAgent(BasicAgent):
    def __init__(self):
        self.name = "InvoiceExceptionHandler"
        self.metadata = {"name": self.name, "description": "Show invoice exception stages. Optional payload_json: invoice and ordered completed stage names. With no payload_json it uses the sample on file: invoice NW-SAMPLE-001.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to exception_progress."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "exception_progress") not in OPERATION_GUIDE:
                raise ValueError("operation must be exception_progress.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(InvoiceExceptionHandlerAgent().perform())
