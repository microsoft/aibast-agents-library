"""Finalization checks from README.md, How it works.

Only Boolean true or trimmed case-insensitive Yes approves; false or No
rejects. Unknown answers authorize neither copy nor decision notification.
Approval requires the current draft's ID, path, size, and ETag to match the
reviewed draft; existing final files block copying.
Extraction, grounded proposal drafting, document creation, and verification
through connected tools stay with the AI. This file plans, never copies.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/rfp-response-manager",
    "version": "0.1.0", "display_name": "Proposal Finalization Checks",
    "description": "Checks explicit approval, draft identity, size, and ETag before a copy plan.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution rfp-response-manager",
    "quality_tier": "experimental", "category": "sales",
    "tags": ["proposal", "approval"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"approval": " Yes ", "reviewed": {"id": "D1", "path": "/drafts/contoso-proposal.docx", "etag": "v1", "size": 2048},
          "current": {"id": "D1", "path": "/drafts/contoso-proposal.docx", "etag": "v1", "size": 2048},
          "final_exists": False}


def evaluate(data):
    value = data.get("approval")
    decision = value if type(value) is bool else (
        True if isinstance(value, str) and value.strip().casefold() == "yes" else
        False if isinstance(value, str) and value.strip().casefold() == "no" else None)
    result = {"decision": decision, "may_copy": False, "may_notify_decision": False,
              "rewrite": False, "overwrite": False, "copied": False}
    if decision is None:
        return {**result, "error": "Missing or unrecognized approval; no decision action is authorized."}
    if decision is False:
        return {**result, "may_notify_decision": True, "next_step": "Notify owner with draft link for manual follow-up; leave draft unchanged."}
    reviewed, current = data["reviewed"], data["current"]
    for record in (reviewed, current):
        if any(not isinstance(record.get(field), str) or not record[field].strip() for field in ("id", "path", "etag")):
            raise ValueError("Both draft snapshots require nonempty id, path, and etag.")
        if type(record.get("size")) is not int or record["size"] <= 0:
            raise ValueError("Both draft snapshots require a positive integer size.")
    if type(data.get("final_exists")) is not bool:
        raise ValueError("final_exists must be an explicit Boolean.")
    mismatch = [field for field in ("id", "path", "etag", "size") if reviewed[field] != current[field]]
    if mismatch or data["final_exists"]:
        return {**result, "error": "Draft changed: " + ", ".join(mismatch) if mismatch else "Final file already exists."}
    return {**result, "may_copy": True, "source": current,
            "next_step": "Copy this exact draft, verify the final copy, then notify. No notification is authorized before verification."}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Proposal Finalization Checks, a synthetic sales-operations pilot checking approval and draft identity before a final-copy plan.

Use only the bundled fictional draft D1, its reviewed and current snapshots and the final-file flag. Never match them to a real customer, proposal or document store.

Answer with the finalization tool, not from memory. Lead with the decision and copy eligibility, quote draft ids, paths, sizes and version tags exactly, and block changed drafts, unknown approval and existing final files.

You never rewrite, copy, overwrite or send a proposal. A proposal owner reviews the exact draft; a person verifies the separate final copy before any approval notification."""

OPERATION_GUIDE = {
    "finalization_check": {
        "title": "Proposal finalization check",
        "when": "Use when someone asks whether explicit approval, unchanged draft snapshots and the absence of an existing final file allow a proposal copy plan.",
    },
}

CARRIED = [
    "Extracts request content, drafts a grounded proposal and creates the document through the original solution's proposal AI and document tools.",
    "Copies the approved draft, verifies the final file and notifies the owner through the original solution's finalization workflow.",
]


class RfpResponseManagerAgent(BasicAgent):
    def __init__(self):
        self.name = "ProposalFinalizationCheck"
        self.metadata = {"name": self.name, "description": "Check finalization without touching files. Optional payload_json: approval Boolean or Yes/No, reviewed/current {id,path,etag,size}, final_exists Boolean.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to finalization_check."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "finalization_check") not in OPERATION_GUIDE:
                raise ValueError("operation must be finalization_check.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(RfpResponseManagerAgent().perform())
