"""Read-only, synthetic patient-intake readiness support."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/patient-intake",
    "version": "1.1.0",
    "display_name": "Patient Intake and Scheduling Agent",
    "description": (
        "Reviews synthetic intake, coverage, and appointment-readiness evidence for "
        "patient-access staff; it never verifies eligibility, books appointments, or changes records."
    ),
    "author": "AIBAST",
    "tags": ["intake", "coverage-evidence", "appointment-readiness", "healthcare", "human-review"],
    "category": "healthcare",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

SAFETY = (
    "Synthetic demonstration data only. Read-only draft for authorized patient-access staff. "
    "Confirm coverage and appointment details in approved source systems; do not use this output "
    "to determine eligibility, schedule care, or change a patient record. Human review is required."
)

PATIENTS = {
    "SYN-PT-001": {
        "label": "Synthetic Patient Alpha",
        "language": "English",
        "forms": ["contact details", "consent acknowledgement", "medication list"],
        "missing": ["emergency contact confirmation"],
        "coverage": {
            "payer": "Synthetic Health Plan",
            "recorded_status": "source record received",
            "evidence_date": "2026-07-30",
            "follow_up": "Confirm active coverage and network status in the payer portal.",
        },
        "visit": {"service": "new patient consultation", "provider": "Clinician A", "date": "2026-08-15"},
    },
    "SYN-PT-002": {
        "label": "Synthetic Patient Beta",
        "language": "Spanish",
        "forms": ["contact details", "consent acknowledgement"],
        "missing": ["preferred-language packet", "medication list"],
        "coverage": {
            "payer": "Synthetic Community Plan",
            "recorded_status": "referral evidence missing",
            "evidence_date": "2026-07-29",
            "follow_up": "Ask authorized staff to confirm referral and coverage evidence.",
        },
        "visit": {"service": "follow-up consultation", "provider": "Clinician B", "date": "2026-08-18"},
    },
}

AVAILABILITY = {
    "Clinician A": [
        {"date": "2026-08-20", "time": "10:30", "service": "new patient consultation"},
        {"date": "2026-08-22", "time": "14:00", "service": "follow-up consultation"},
    ],
    "Clinician B": [
        {"date": "2026-08-21", "time": "09:00", "service": "follow-up consultation"},
    ],
}

ALIASES = {
    "intake_form": "intake_readiness",
    "insurance_verification": "coverage_evidence",
    "appointment_scheduling": "appointment_availability",
}


def _notice(title):
    return [f"# {title}", "", f"> {SAFETY}", ""]


def _selected_patient(patient_id):
    if not patient_id:
        return PATIENTS.items()
    if patient_id not in PATIENTS:
        return []
    return [(patient_id, PATIENTS[patient_id])]


class PatientIntakeAgent(BasicAgent):
    """Prepare read-only intake evidence for human review."""

    def __init__(self):
        self.name = "PatientIntakeAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "intake_readiness",
                            "coverage_evidence",
                            "appointment_availability",
                            "pre_visit_summary",
                        ],
                        "description": "Read-only evidence operation.",
                    },
                    "patient_id": {
                        "type": "string",
                        "enum": sorted(PATIENTS),
                        "description": "Optional synthetic patient identifier.",
                    },
                    "provider": {
                        "type": "string",
                        "enum": sorted(AVAILABILITY),
                        "description": "Optional synthetic provider label for availability review.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = ALIASES.get(kwargs.get("operation", ""), kwargs.get("operation", ""))
        routes = {
            "intake_readiness": self._intake_readiness,
            "coverage_evidence": self._coverage_evidence,
            "appointment_availability": self._appointment_availability,
            "pre_visit_summary": self._pre_visit_summary,
        }
        if operation not in routes:
            return f"**Error:** Unknown operation `{operation}`. No action was taken."
        return routes[operation](kwargs.get("patient_id"), kwargs.get("provider"))

    def _intake_readiness(self, patient_id=None, _provider=None):
        rows = list(_selected_patient(patient_id))
        if not rows:
            return f"# Intake Readiness\n\n> {SAFETY}\n\nNo synthetic patient matched `{patient_id}`."
        lines = _notice("Intake Readiness Draft")
        for pid, patient in rows:
            lines.extend([
                f"## {patient['label']} ({pid})",
                f"- Preferred language recorded: {patient['language']}",
                f"- Forms present: {', '.join(patient['forms'])}",
                f"- Items for staff confirmation: {', '.join(patient['missing']) or 'none recorded'}",
                "",
            ])
        return "\n".join(lines)

    def _coverage_evidence(self, patient_id=None, _provider=None):
        rows = list(_selected_patient(patient_id))
        if not rows:
            return f"# Coverage Evidence\n\n> {SAFETY}\n\nNo synthetic patient matched `{patient_id}`."
        lines = _notice("Coverage Evidence Review")
        for pid, patient in rows:
            coverage = patient["coverage"]
            lines.extend([
                f"## {patient['label']} ({pid})",
                f"- Payer recorded in synthetic source: {coverage['payer']}",
                f"- Source-recorded state: {coverage['recorded_status']}",
                f"- Evidence date: {coverage['evidence_date']}",
                f"- Human follow-up: {coverage['follow_up']}",
                "",
            ])
        return "\n".join(lines)

    def _appointment_availability(self, _patient_id=None, provider=None):
        if provider and provider not in AVAILABILITY:
            return f"# Appointment Availability\n\n> {SAFETY}\n\nNo synthetic provider matched `{provider}`."
        lines = _notice("Appointment Availability Review")
        lines.append("These are candidate source slots for staff review; nothing has been reserved or booked.")
        lines.append("")
        providers = {provider: AVAILABILITY[provider]} if provider else AVAILABILITY
        for name, slots in providers.items():
            lines.append(f"## {name}")
            for slot in slots:
                lines.append(f"- {slot['date']} {slot['time']} — {slot['service']}")
            lines.append("")
        return "\n".join(lines)

    def _pre_visit_summary(self, patient_id=None, _provider=None):
        rows = list(_selected_patient(patient_id))
        if not rows:
            return f"# Pre-Visit Summary\n\n> {SAFETY}\n\nNo synthetic patient matched `{patient_id}`."
        lines = _notice("Pre-Visit Readiness Summary")
        for pid, patient in rows:
            visit = patient["visit"]
            lines.extend([
                f"## {patient['label']} ({pid})",
                f"- Source-recorded visit: {visit['service']} with {visit['provider']} on {visit['date']}",
                f"- Intake items requiring confirmation: {', '.join(patient['missing']) or 'none recorded'}",
                f"- Coverage follow-up: {patient['coverage']['follow_up']}",
                "- Required reviewer: authorized patient-access staff",
                "",
            ])
        return "\n".join(lines)


if __name__ == "__main__":
    agent = PatientIntakeAgent()
    for op in agent.metadata["parameters"]["properties"]["operation"]["enum"]:
        print(agent.perform(operation=op))
