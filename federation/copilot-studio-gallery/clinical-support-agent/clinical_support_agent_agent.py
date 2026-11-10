"""Approved-source routing table from README.md, Capabilities and Agent.

Routes an already-selected information category for one of the three named
roles. No medical facts or patient recommendations are generated. Clinical
interpretation, search, source evaluation, and role-appropriate explanation
remain with the AI and qualified reviewers. No patient data should be supplied.
This educational sample is not clinically validated or intended for care.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/clinical-support-agent",
    "version": "0.1.0", "display_name": "Clinical Information Source Router",
    "description": "Lists approved general-information sources, not clinical advice.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution clinical-support-agent",
    "quality_tier": "experimental", "category": "healthcare",
    "tags": ["education", "routing"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
ROLES = {"Nurses": "Simplified protocols and actionable information",
         "Clinicians": "Detailed clinical guidance and reference information",
         "Admin Staff": "Procedural and compliance-focused information"}
SOURCES = {"protocol": "Internal Clinical SOPs", "reference": "Medical Reference Quick Q&A",
           "literature": "CDC/NIH Guidelines, Journal Articles"}
SAMPLE = {"role": "Nurses", "category": "protocol",
          "patient_specific": False, "contains_phi": False, "emergency": False}


def evaluate(data):
    for field in ("patient_specific", "contains_phi", "emergency"):
        if type(data.get(field)) is not bool:
            raise ValueError(field + " must be an explicit Boolean.")
    if any(data[field] for field in ("patient_specific", "contains_phi", "emergency")):
        return {"allowed": False, "reason": "Not for patient care, emergencies, or patient-identifiable information.",
                "source": None}
    role, category = data["role"], data["category"]
    if role not in ROLES or category not in SOURCES:
        raise ValueError("Choose role Nurses, Clinicians, or Admin Staff and category protocol, reference, or literature.")
    return {"allowed": True, "role": role, "presentation": ROLES[role], "source": SOURCES[category],
            "disclaimer": "Educational routing only; no clinical advice or validated care guidance."}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Clinical Information Source Router, a synthetic educational pilot routing general information by staff role and source category.

Use only the bundled fictional role, category and safety flags and the bundled source routing table. Never match them to real staff, patients or care records.

Answer with the source routing tool, not from memory. Lead with whether routing is allowed and the named source, quote category names and ids exactly, and stop for emergencies, patient-specific questions or identifiable patient information.

You never diagnose, recommend treatment, handle patient data or claim validated clinical guidance. A qualified clinical reviewer evaluates source material; actual patient care belongs to qualified professionals."""

OPERATION_GUIDE = {
    "source_routing": {
        "title": "Educational source routing",
        "when": "Use when someone asks which bundled general-information source fits a staff role and category, or whether the safety flags prohibit routing.",
        "ask": "Which approved information source should a nurse use for the sample question on file, and is it safe to route?",
    },
}

CARRIED = [
    "Searches clinical sources, evaluates their authority and explains information for each role through the original solution's clinical information agent.",
    "Interprets clinical material with qualified reviewers using the original solution's internal procedures, reference knowledge and literature sources.",
]


class ClinicalSupportAgent(BasicAgent):
    def __init__(self):
        self.name = "ClinicalSourceRouter"
        self.metadata = {"name": self.name, "description": "Route general information only. Optional payload_json: role, category, explicit patient_specific, contains_phi, emergency Booleans. Do not include patient data. With no payload_json it uses the sample on file: the sample nurse question.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to source_routing."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "source_routing") not in OPERATION_GUIDE:
                raise ValueError("operation must be source_routing.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(ClinicalSupportAgent().perform())
