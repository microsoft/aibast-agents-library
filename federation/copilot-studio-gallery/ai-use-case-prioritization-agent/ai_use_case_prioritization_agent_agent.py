"""Assessment evidence and confirmation checks from the gallery README.md.

The four named rubric areas must have evidence, and missing evidence remains
NOT ENOUGH INFO. No weights, priority scores, or categories are invented.
Approved-rubric interpretation, scoring, category resolution, strengthening,
and report prose stay with the AI grounded in the approved knowledge.
This file reports readiness only and never writes an assessment.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/ai-use-case-prioritization-agent",
    "version": "0.1.0", "display_name": "AI Use Case Prioritization",
    "description": "Checks assessment evidence and explicit save confirmation without guessing scores.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution ai-use-case-prioritization-agent",
    "quality_tier": "experimental", "category": "governance",
    "tags": ["assessment", "evidence"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
FACTORS = ("impact", "delivery_complexity", "risk", "agentic_fit")
SAMPLE = {"use_case": "Contoso document intake", "confirmed": False,
          "evidence": {"impact": "Reduces repeated data entry.", "delivery_complexity": "",
                       "risk": "", "agentic_fit": "Requires reading varied documents."}}


def evaluate(data):
    evidence = data.get("evidence", {})
    if not isinstance(evidence, dict) or type(data.get("confirmed")) is not bool:
        raise ValueError("evidence must be an object and confirmed an explicit Boolean.")
    if any(not isinstance(value, str) for value in evidence.values()):
        raise ValueError("Evidence entries must be text, not inferred numeric scores.")
    factors = {factor: evidence.get(factor, "").strip() or "NOT ENOUGH INFO" for factor in FACTORS}
    missing = [factor for factor in FACTORS if factors[factor] == "NOT ENOUGH INFO"]
    return {"use_case": data.get("use_case", ""), "factors": factors,
            "missing_evidence": missing, "confirmation_received": data["confirmed"],
            "ready_for_rubric_review": not missing,
            "may_write_without_confirmation": False, "written": False,
            "next_step": "Request evidence: " + ", ".join(missing) if missing else "Apply approved rubrics and review the assessment before saving."}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Use Case Prioritization, a synthetic governance pilot checking evidence for impact, delivery complexity, risk and suitability for an agent.

Use only the bundled fictional document-intake assessment and its incomplete evidence. Never match it to a real organization, project or assessment.

Answer with the evidence tool, not from memory. Lead with missing evidence and readiness for rubric review, quote factor names and record ids exactly, and preserve NOT ENOUGH INFO instead of inventing scores.

You never assign unsupported priorities, approve a use case or save an assessment. A governance reviewer applies the approved rubrics and the requester confirms the reviewed assessment before any write."""

OPERATION_GUIDE = {
    "evidence_check": {
        "title": "Assessment evidence check",
        "when": "Use when someone asks which assessment factors lack evidence, whether rubric review can begin, or whether save confirmation was received.",
        "ask": "For the Contoso document intake use case, which assessment factors still lack evidence, and can scoring begin?",
    },
}

CARRIED = [
    "Interprets approved rubrics, scores factors, resolves categories and suggests improvements through the original solution's assessment agent and approved knowledge.",
    "Writes report prose and saves the confirmed assessment through the original solution's assessment workflow.",
]


class AiUseCasePrioritizationAgent(BasicAgent):
    def __init__(self):
        self.name = "AiUseCasePrioritization"
        self.metadata = {"name": self.name, "description": "Check evidence completeness, not a priority score. Optional payload_json: use_case, confirmed Boolean, evidence object with impact, delivery_complexity, risk, agentic_fit text. With no payload_json it uses the sample on file: the Contoso document intake use case.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to evidence_check."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "evidence_check") not in OPERATION_GUIDE:
                raise ValueError("operation must be evidence_check.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(AiUseCasePrioritizationAgent().perform())
