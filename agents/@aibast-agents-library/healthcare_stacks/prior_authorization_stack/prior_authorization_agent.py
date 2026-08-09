"""Read-only, synthetic prior-authorization evidence support."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/prior-authorization",
    "version": "1.1.0",
    "display_name": "Prior Authorization Agent",
    "description": (
        "Assembles synthetic payer and clinical evidence for human utilization review; it never "
        "predicts, grants, denies, submits, or changes an authorization."
    ),
    "author": "AIBAST",
    "tags": ["prior-auth", "evidence-packet", "payer-criteria", "healthcare", "human-review"],
    "category": "healthcare",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

SAFETY = (
    "Synthetic demonstration data only. This output is a read-only evidence draft, not an "
    "authorization, eligibility, medical-necessity, diagnosis, or treatment decision. A qualified "
    "utilization reviewer must verify payer policy and clinical evidence before any submission."
)

REQUESTS = {
    "SYN-AUTH-001": {
        "service": "synthetic knee imaging request",
        "payer": "Synthetic Health Plan",
        "source_status": "additional evidence requested",
        "source_date": "2026-07-30",
        "policy_id": "SYN-POL-IMG-01",
        "evidence": {
            "encounter note": "present",
            "prior imaging report": "present",
            "conservative-care duration": "not found in synthetic source",
        },
    },
    "SYN-AUTH-002": {
        "service": "synthetic outpatient procedure request",
        "payer": "Synthetic Community Plan",
        "source_status": "payer response recorded",
        "source_date": "2026-07-31",
        "policy_id": "SYN-POL-PROC-02",
        "evidence": {
            "encounter note": "present",
            "specialist note": "present",
            "current payer policy confirmation": "requires human review",
        },
    },
}

POLICIES = {
    "SYN-POL-IMG-01": {
        "title": "Synthetic Imaging Evidence Checklist",
        "requirements": ["relevant encounter note", "prior imaging evidence", "documented duration fields"],
        "effective_date": "2026-07-01",
    },
    "SYN-POL-PROC-02": {
        "title": "Synthetic Procedure Evidence Checklist",
        "requirements": ["relevant encounter note", "specialist documentation", "current policy version"],
        "effective_date": "2026-07-01",
    },
}

ALIASES = {
    "auth_request": "request_evidence",
    "clinical_criteria_check": "criteria_evidence",
    "status_tracking": "status_summary",
    "appeal_preparation": "appeal_evidence_packet",
}


def _notice(title):
    return [f"# {title}", "", f"> {SAFETY}", ""]


def _selected_request(auth_id):
    if not auth_id:
        return REQUESTS.items()
    if auth_id not in REQUESTS:
        return []
    return [(auth_id, REQUESTS[auth_id])]


class PriorAuthorizationAgent(BasicAgent):
    """Assemble evidence without making an authorization outcome."""

    def __init__(self):
        self.name = "PriorAuthorizationAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["request_evidence", "criteria_evidence", "status_summary", "appeal_evidence_packet"],
                        "description": "Read-only utilization-review evidence operation.",
                    },
                    "auth_id": {
                        "type": "string",
                        "enum": sorted(REQUESTS),
                        "description": "Optional synthetic request identifier.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = ALIASES.get(kwargs.get("operation", ""), kwargs.get("operation", ""))
        routes = {
            "request_evidence": self._request_evidence,
            "criteria_evidence": self._criteria_evidence,
            "status_summary": self._status_summary,
            "appeal_evidence_packet": self._appeal_evidence_packet,
        }
        if operation not in routes:
            return f"**Error:** Unknown operation `{operation}`. No action was taken."
        return routes[operation](kwargs.get("auth_id"))

    def _request_evidence(self, auth_id=None):
        rows = list(_selected_request(auth_id))
        if not rows:
            return f"# Request Evidence\n\n> {SAFETY}\n\nNo synthetic request matched `{auth_id}`."
        lines = _notice("Prior-Authorization Evidence Inventory")
        for rid, request in rows:
            lines.extend([
                f"## {rid}: {request['service']}",
                f"- Payer in synthetic source: {request['payer']}",
                f"- Source-recorded workflow state: {request['source_status']} ({request['source_date']})",
                f"- Referenced policy: {request['policy_id']}",
                "",
            ])
            for item, state in request["evidence"].items():
                lines.append(f"- {item}: {state}")
            lines.append("")
        return "\n".join(lines)

    def _criteria_evidence(self, auth_id=None):
        rows = list(_selected_request(auth_id))
        if not rows:
            return f"# Criteria Evidence\n\n> {SAFETY}\n\nNo synthetic request matched `{auth_id}`."
        lines = _notice("Criteria-to-Evidence Crosswalk")
        for rid, request in rows:
            policy = POLICIES[request["policy_id"]]
            lines.extend([
                f"## {rid} — {policy['title']}",
                f"- Synthetic policy effective date: {policy['effective_date']}",
                "- Checklist only; presence does not establish medical necessity or authorization.",
            ])
            for requirement in policy["requirements"]:
                lines.append(f"- Reviewer check: {requirement}")
            lines.append("")
        return "\n".join(lines)

    def _status_summary(self, auth_id=None):
        rows = list(_selected_request(auth_id))
        if not rows:
            return f"# Status Summary\n\n> {SAFETY}\n\nNo synthetic request matched `{auth_id}`."
        lines = _notice("Source-Recorded Status Summary")
        for rid, request in rows:
            lines.extend([
                f"- {rid}: {request['source_status']} as recorded on {request['source_date']}",
                "  - This is a source transcription, not an agent determination.",
            ])
        return "\n".join(lines)

    def _appeal_evidence_packet(self, auth_id=None):
        rows = list(_selected_request(auth_id))
        if not rows:
            return f"# Appeal Evidence Packet\n\n> {SAFETY}\n\nNo synthetic request matched `{auth_id}`."
        lines = _notice("Reconsideration Evidence Draft")
        lines.append("A reviewer must confirm that reconsideration or appeal is appropriate and permitted.")
        lines.append("")
        for rid, request in rows:
            lines.extend([
                f"## {rid}",
                f"- Source workflow state: {request['source_status']}",
                f"- Policy reference to verify: {request['policy_id']}",
                "- Include only authorized, minimum-necessary evidence.",
                "- Human utilization reviewer owns rationale, completeness, and submission.",
                "",
            ])
        return "\n".join(lines)


if __name__ == "__main__":
    agent = PriorAuthorizationAgent()
    for op in agent.metadata["parameters"]["properties"]["operation"]["enum"]:
        print(agent.perform(operation=op))
