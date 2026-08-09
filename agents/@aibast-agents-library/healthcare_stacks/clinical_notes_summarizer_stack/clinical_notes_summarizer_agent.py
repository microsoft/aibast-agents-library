"""Read-only summaries of synthetic clinical source text."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/clinical-notes-summarizer",
    "version": "1.1.0",
    "display_name": "Clinical Notes Summarizer Agent",
    "description": (
        "Handles synthetic clinical-note review: summarize encounters, list source-recorded "
        "medications, extract source-coded problem lists without confirming diagnoses, and summarize "
        "referral context. It requires clinician review and never diagnoses, recommends treatment, "
        "clears a patient, places a referral, schedules care, or changes a record."
    ),
    "author": "AIBAST",
    "tags": ["clinical-notes", "source-summary", "medication-inventory", "healthcare", "clinician-review"],
    "category": "healthcare",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

SAFETY = (
    "Synthetic demonstration data only. This is a read-only draft that may omit or misstate "
    "source details. A qualified clinician must compare it with the authorized record. It is not "
    "diagnosis, treatment advice, medical clearance, scheduling, or a record update. Human review is required."
)

ENCOUNTERS = {
    "SYN-ENC-001": {
        "patient_label": "Synthetic Patient Alpha",
        "date": "2026-07-28",
        "source_note": "Follow-up visit. Patient reports knee discomfort with stairs. No trauma recorded.",
        "source_problems": ["source-coded type 2 diabetes", "source-coded hypertension", "knee discomfort"],
        "source_observations": ["blood pressure field: 148/92", "laboratory field: HbA1c 8.2%"],
        "medications": ["Metformin 1000 mg twice daily", "Lisinopril 20 mg daily"],
        "referral": "Orthopedics referral draft recorded; status not confirmed.",
    },
    "SYN-ENC-002": {
        "patient_label": "Synthetic Patient Beta",
        "date": "2026-07-29",
        "source_note": "Urgent visit source note records intermittent chest tightness and shortness of breath.",
        "source_problems": ["source-coded chest pain", "source-coded reflux", "source-coded anxiety"],
        "source_observations": ["ECG field: normal sinus rhythm", "troponin field: negative in source note"],
        "medications": ["Omeprazole 20 mg daily", "Sertraline 100 mg daily"],
        "referral": "Cardiology referral draft recorded; status not confirmed.",
    },
}

ALIASES = {
    "summarize_encounter": "encounter_summary",
    "medication_review": "medication_inventory",
    "problem_list": "problem_list_extract",
    "referral_summary": "referral_context",
}


def _notice(title):
    return [f"# {title}", "", f"> {SAFETY}", ""]


def _selected_encounter(encounter_id):
    if not encounter_id:
        return ENCOUNTERS.items()
    if encounter_id not in ENCOUNTERS:
        return []
    return [(encounter_id, ENCOUNTERS[encounter_id])]


class ClinicalNotesSummarizerAgent(BasicAgent):
    """Extract source facts without clinical inference."""

    def __init__(self):
        self.name = "ClinicalNotesSummarizerAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["encounter_summary", "medication_inventory", "problem_list_extract", "referral_context"],
                        "description": (
                            "Route by intent: encounter_summary to summarize a synthetic encounter "
                            "using source facts only; medication_inventory to list source-recorded "
                            "medications for reconciliation; problem_list_extract to extract source-coded "
                            "problems without confirming a diagnosis; referral_context to report recorded "
                            "referral context and state that no referral was placed."
                        ),
                    },
                    "encounter_id": {
                        "type": "string",
                        "enum": sorted(ENCOUNTERS),
                        "description": "Optional synthetic encounter identifier.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = ALIASES.get(kwargs.get("operation", ""), kwargs.get("operation", ""))
        routes = {
            "encounter_summary": self._encounter_summary,
            "medication_inventory": self._medication_inventory,
            "problem_list_extract": self._problem_list_extract,
            "referral_context": self._referral_context,
        }
        if operation not in routes:
            return f"**Error:** Unknown operation `{operation}`. No action was taken."
        return routes[operation](kwargs.get("encounter_id"))

    def _encounter_summary(self, encounter_id=None):
        rows = list(_selected_encounter(encounter_id))
        if not rows:
            return f"# Encounter Summary\n\n> {SAFETY}\n\nNo synthetic encounter matched `{encounter_id}`."
        lines = _notice("Source-Grounded Encounter Summary")
        for eid, encounter in rows:
            lines.extend([
                f"## {encounter['patient_label']} ({eid}) — {encounter['date']}",
                f"- Source text: {encounter['source_note']}",
                f"- Source observations: {'; '.join(encounter['source_observations'])}",
                "- Clinical interpretation: not performed; clinician review required.",
                "",
            ])
        return "\n".join(lines)

    def _medication_inventory(self, encounter_id=None):
        rows = list(_selected_encounter(encounter_id))
        if not rows:
            return f"# Medication Inventory\n\n> {SAFETY}\n\nNo synthetic encounter matched `{encounter_id}`."
        lines = _notice("Medication Source Inventory")
        for eid, encounter in rows:
            lines.append(f"## {encounter['patient_label']} ({eid})")
            for medication in encounter["medications"]:
                lines.append(f"- Source-recorded: {medication}")
            lines.extend(["- Reconciliation, interactions, and changes require clinician/pharmacist review.", ""])
        return "\n".join(lines)

    def _problem_list_extract(self, encounter_id=None):
        rows = list(_selected_encounter(encounter_id))
        if not rows:
            return f"# Problem List Extract\n\n> {SAFETY}\n\nNo synthetic encounter matched `{encounter_id}`."
        lines = _notice("Problem-List Source Extract")
        for eid, encounter in rows:
            lines.append(f"## {encounter['patient_label']} ({eid})")
            for problem in encounter["source_problems"]:
                lines.append(f"- {problem}")
            lines.extend(["- No diagnosis was added, confirmed, or changed.", ""])
        return "\n".join(lines)

    def _referral_context(self, encounter_id=None):
        rows = list(_selected_encounter(encounter_id))
        if not rows:
            return f"# Referral Context\n\n> {SAFETY}\n\nNo synthetic encounter matched `{encounter_id}`."
        lines = _notice("Referral Context Extract")
        for eid, encounter in rows:
            lines.extend([
                f"## {encounter['patient_label']} ({eid})",
                f"- Source-recorded context: {encounter['referral']}",
                "- No referral was placed, scheduled, or changed.",
                "- Authorized clinician/staff review is required.",
                "",
            ])
        return "\n".join(lines)


if __name__ == "__main__":
    agent = ClinicalNotesSummarizerAgent()
    for op in agent.metadata["parameters"]["properties"]["operation"]["enum"]:
        print(agent.perform(operation=op))
