"""Read-only query-plan checks from README.md, Agent and Automation.

This is deliberately a small, fully matched KQL subset, not a general KQL
security validator. Only a table followed by count, take, project, or count
summaries is supported. Anything else is explicitly unsupported.
Natural-language translation, full KQL interpretation, execution, and grounded
explanations stay with the AI and authorized data tools. No query or mail runs.
"""
import json
import re

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/kusto-analytics-agent",
    "version": "0.1.0", "display_name": "Kusto Read-only Query Plan",
    "description": "Checks a narrow read-only KQL subset and invoking-user-only email plans.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution kusto-analytics-agent",
    "quality_tier": "experimental", "category": "analytics",
    "tags": ["kql", "read-only"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"cluster": "contoso-sample", "database": "SalesSample",
          "query": "Sales | summarize count() by Region | take 10",
          "invoking_user": "analyst@contoso.example", "recipient": "analyst@contoso.example"}
IDENTIFIER = r"[A-Za-z_][A-Za-z0-9_]*"
OPERATORS = (
    r"count",
    r"take\s+[1-9][0-9]*",
    rf"project\s+{IDENTIFIER}(?:\s*,\s*{IDENTIFIER})*",
    rf"summarize\s+count\(\)(?:\s+by\s+{IDENTIFIER}(?:\s*,\s*{IDENTIFIER})*)?",
)


def evaluate(data):
    for field in ("cluster", "database", "query"):
        if not isinstance(data.get(field), str) or not data[field].strip() or "<" in data[field] or ">" in data[field]:
            raise ValueError(field + " must be supplied without placeholder values.")
    query = data["query"]
    segments = [part.strip() for part in query.split("|")]
    supported = bool(re.fullmatch(IDENTIFIER, segments[0])) and all(
        any(re.fullmatch(pattern, segment) for pattern in OPERATORS) for segment in segments[1:])
    user = data.get("invoking_user", "")
    recipient = data.get("recipient", "")
    if recipient and (not user or recipient.strip().casefold() != user.strip().casefold()):
        raise ValueError("Scheduled summaries may target only the invoking user's own address.")
    return {"supported_read_only_subset": supported, "query": query,
            "cluster": data["cluster"], "database": data["database"],
            "recipient": recipient or None, "executed": False, "sent": False,
            "note": "Supported local query plan only." if supported else "Unsupported KQL; interpreter review required. Nothing will execute."}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Read-only Query Plan, a synthetic analytics pilot checking a small tabular-query subset and a self-addressed summary plan.

Use only the bundled fictional sales query, database, cluster and analyst address. Never match them to a real data service, user or dataset.

Answer with the query plan tool, not from memory. Lead with whether the query is supported locally, quote query text, database names and ids exactly, and identify unsupported syntax rather than treating this check as general query security validation.

You never execute a query, access live data, schedule a summary or send mail. An authorized analyst reviews query meaning and permissions; summary recipients must remain the invoking user."""

OPERATION_GUIDE = {
    "query_plan": {
        "title": "Read-only query plan check",
        "when": "Use when someone asks whether a supplied query fits the narrow local subset and whether a summary recipient matches the invoking user.",
    },
}

CARRIED = [
    "Translates natural-language questions, interprets full KQL and explains grounded results through the original solution's analytics agent.",
    "Executes queries and schedules invoking-user-only email summaries through the original solution's authorized data and automation tools.",
]


class KustoAnalyticsAgent(BasicAgent):
    def __init__(self):
        self.name = "KustoReadOnlyPlan"
        self.metadata = {"name": self.name, "description": "Check a narrow KQL plan without executing. Optional payload_json: cluster, database, query, optional invoking_user and recipient.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to query_plan."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "query_plan") not in OPERATION_GUIDE:
                raise ValueError("operation must be query_plan.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(KustoAnalyticsAgent().perform())
