"""Synthetic patient intake and scheduling support: new-patient registration drafts, coverage evidence,
provider availability, appointment request drafts, specialty intake packets, and reminder plans."""

import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/patient-intake",
    "version": "1.2.0",
    "display_name": "Patient Intake and Scheduling Agent",
    "description": (
        "Prepares synthetic new-patient intake, coverage evidence, provider availability, appointment "
        "request drafts, specialty intake packets, and reminder plans for patient-access staff; it never "
        "determines eligibility, books appointments, sends messages, or changes records."
    ),
    "author": "AIBAST",
    "tags": ["intake", "scheduling", "coverage-evidence", "reminders", "healthcare", "human-review"],
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
    "SYN-PT-003": {
        "label": "Sarah Martinez",
        "patient_type": "New Patient",
        "language": "English",
        "chief_complaint": "Chronic migraines",
        "timeframe_days": 14,
        "request_date": "2024-01-23",
        "forms": [],
        "missing": ["intake packet not yet completed"],
        "coverage": {
            "payer": "Blue Cross Blue Shield",
            "recorded_status": "Active",
            "evidence_date": "2024-01-23",
            "follow_up": "Confirm active coverage and network status in the payer portal.",
            "policy_number": "XXX-XX-7392",
            "group_number": "84721",
            "specialist_copay": 35,
            "deductible_met": 450,
            "deductible": 1500,
            "prior_auth": "No (initial consult exempt)",
            "network": "In-network, Tier 1",
        },
        "visit": {"service": "New Patient Consultation", "provider": "Dr. James Anderson", "date": "2024-01-30"},
    },
}

PROVIDERS = {
    "Dr. James Anderson": {"credential": "MD", "specialty": "Neurology", "location": "Neurology Clinic - Suite 405"},
}

AVAILABILITY = {
    "Clinician A": [
        {"date": "2026-08-20", "time": "10:30", "service": "new patient consultation"},
        {"date": "2026-08-22", "time": "14:00", "service": "follow-up consultation"},
    ],
    "Clinician B": [
        {"date": "2026-08-21", "time": "09:00", "service": "follow-up consultation"},
    ],
    "Dr. James Anderson": [
        {"date": "2024-01-30", "time": "14:30", "service": "new patient consultation", "label": "Tuesday 2:30 PM"},
        {"date": "2024-02-01", "time": "10:00", "service": "new patient consultation", "label": "Thursday 10:00 AM"},
    ],
}

PROVIDER_KEYS = {
    "anderson": "Dr. James Anderson",
    "clinician a": "Clinician A",
    "clinician b": "Clinician B",
}

NEW_PATIENT_VISIT_MINUTES = 60

INTAKE_PACKETS = {
    "base": [
        "Demographics Form: Name, DOB, contact info, emergency contact",
        "Insurance Verification: Photo upload for card front/back",
        "Medical History: Current medications, allergies, prior surgeries",
        "HIPAA Authorization: Digital signature required",
        "Financial Policy: Payment terms and copay acknowledgment",
    ],
    "Neurology": ["Migraine Questionnaire: HIT-6 headache impact assessment"],
}

REMINDER_PROTOCOL = {
    "touchpoints": [
        {"name": "72-Hour Reminder", "hours_before": 72, "channel": "SMS + Email"},
        {"name": "24-Hour Reminder", "hours_before": 24, "channel": "SMS + Voice call option"},
        {"name": "2-Hour Reminder", "hours_before": 2, "channel": "Final SMS"},
    ],
    "forms_alert_days_before": 1,
    "reschedule_keyword": "RESCHEDULE",
    "waitlist_rule": "Auto-fill the slot if she cancels with >24hr notice",
    "historical_no_show_rate": "8% for new patients with this protocol",
    "protocol_name": "40% no-show reduction protocol",
}

ALIASES = {
    "intake_form": "intake_readiness",
    "insurance_verification": "coverage_evidence",
    "appointment_scheduling": "appointment_availability",
}

OPERATIONS = [
    "intake_readiness",
    "coverage_evidence",
    "appointment_availability",
    "pre_visit_summary",
    "new_patient_intake",
    "appointment_hold_draft",
    "intake_packet",
    "reminder_plan",
]

DEFAULT_PATIENT = "SYN-PT-003"


def _notice(title):
    return [f"# {title}", "", f"> {SAFETY}", ""]


def _resolve_patient(query):
    """Patient ID, label or part of it ('Alpha', 'Sarah Martinez'); default the demo patient; None on a miss."""
    if not query:
        return DEFAULT_PATIENT
    q = str(query).lower().strip()
    for pid, patient in PATIENTS.items():
        if pid.lower() in q or q in patient["label"].lower():
            return pid
    return None


def _resolve_provider(query, pid):
    """Provider name or part of it; default the patient's requested provider; None on a miss."""
    if not query:
        return PATIENTS[pid]["visit"]["provider"]
    q = str(query).lower().strip()
    for key, name in PROVIDER_KEYS.items():
        if key in q or q in name.lower():
            return name
    return None


def _pick_slot(provider, slot_text):
    """'Tuesday 2:30' / 'Thursday' / '2024-02-01' picks that slot; default the first slot."""
    slots = AVAILABILITY[provider]
    q = str(slot_text or "").lower()
    for slot in slots:
        label = slot.get("label", "").lower()
        if q and (slot["date"] in q or (label and label.split()[0][:3] in q)):
            return slot
    return slots[0]


def _slot_datetime(slot):
    return datetime.datetime.strptime(f"{slot['date']} {slot['time']}", "%Y-%m-%d %H:%M")


def _fmt_day_time(moment):
    hour = moment.hour % 12 or 12
    return f"{moment:%A} {hour}:{moment:%M} {'AM' if moment.hour < 12 else 'PM'}"


def _fmt_long(moment):
    hour = moment.hour % 12 or 12
    return f"{moment:%A, %B} {moment.day}, {moment.year}", f"{hour}:{moment:%M} {'AM' if moment.hour < 12 else 'PM'}"


def _slot_label(slot):
    return slot.get("label") or f"{slot['date']} {slot['time']}"


class PatientIntakeAgent(BasicAgent):
    """Prepare intake and scheduling drafts for human review."""

    def __init__(self):
        self.name = "PatientIntakeAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"] + " Always use this tool for patient intake and "
                "scheduling. The demo patient is Sarah Martinez (SYN-PT-003, new patient, chronic "
                "migraines, Blue Cross Blue Shield, Dr. James Anderson, Neurology); call it without "
                "asking for IDs. Demo flow: a new patient called requesting a consultation -> "
                "new_patient_intake; provider availability and insurance coverage -> "
                "appointment_availability and coverage_evidence; book her for a slot -> "
                "appointment_hold_draft; what forms are in the intake packet -> intake_packet; set "
                "up reminders / reduce no-shows -> reminder_plan."
            ),
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(OPERATIONS),
                        "description": (
                            "new_patient_intake: register a new patient who called for a "
                            "consultation. appointment_availability: the provider's open slots. "
                            "coverage_evidence: verify insurance coverage, copay, deductible, prior "
                            "auth, network. appointment_hold_draft: book her for a slot (returns a "
                            "booking request for staff). intake_packet: which forms a new patient's "
                            "digital intake packet contains (HIPAA consent, medication history). "
                            "reminder_plan: automated reminders and no-show reduction. "
                            "intake_readiness: what is still missing from a patient's intake (e.g. "
                            "Patient Alpha, SYN-PT-001). pre_visit_summary: pre-visit readiness "
                            "summary for a patient."
                        ),
                    },
                    "patient_id": {
                        "type": "string",
                        "description": "Optional patient ID or name (default SYN-PT-003, Sarah Martinez).",
                    },
                    "provider": {
                        "type": "string",
                        "description": "Optional provider (default the patient's requested provider, Dr. James Anderson).",
                    },
                    "slot": {
                        "type": "string",
                        "description": "Requested slot for appointment_hold_draft / reminder_plan, e.g. 'Tuesday 2:30 PM'.",
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
            "new_patient_intake": self._new_patient_intake,
            "appointment_hold_draft": self._appointment_hold_draft,
            "intake_packet": self._intake_packet,
            "reminder_plan": self._reminder_plan,
        }
        if operation not in routes:
            return f"**Error:** Unknown operation `{operation}`. No action was taken."
        pid = _resolve_patient(kwargs.get("patient_id"))
        if pid is None:
            return f"# Patient Lookup\n\n> {SAFETY}\n\nNo synthetic patient matched `{kwargs.get('patient_id')}`."
        provider = _resolve_provider(kwargs.get("provider"), pid)
        if provider is None:
            return f"# Appointment Availability\n\n> {SAFETY}\n\nNo synthetic provider matched `{kwargs.get('provider')}`."
        return routes[operation](pid, provider, kwargs.get("slot"))

    # ── existing-patient readiness ─────────────────────────────
    def _intake_readiness(self, pid, _provider, _slot):
        patient = PATIENTS[pid]
        lines = _notice("Intake Readiness Draft")
        lines.extend([
            f"## {patient['label']} ({pid})",
            f"- Preferred language recorded: {patient['language']}",
            f"- Forms present: {', '.join(patient['forms']) or 'none yet'}",
            f"- Items for staff confirmation: {', '.join(patient['missing']) or 'none recorded'}",
            "",
        ])
        return "\n".join(lines)

    def _pre_visit_summary(self, pid, _provider, _slot):
        patient = PATIENTS[pid]
        visit = patient["visit"]
        lines = _notice("Pre-Visit Readiness Summary")
        lines.extend([
            f"## {patient['label']} ({pid})",
            f"- Source-recorded visit: {visit['service']} with {visit['provider']} on {visit['date']}",
            f"- Intake items requiring confirmation: {', '.join(patient['missing']) or 'none recorded'}",
            f"- Coverage follow-up: {patient['coverage']['follow_up']}",
            "- Required reviewer: authorized patient-access staff",
            "",
        ])
        return "\n".join(lines)

    # ── video turn 1 ───────────────────────────────────────────
    def _new_patient_intake(self, pid, provider, _slot):
        patient = PATIENTS[pid]
        info = PROVIDERS.get(provider, {"specialty": "General", "credential": ""})
        lines = _notice("New Patient Registration Draft")
        lines.extend([
            f"I'll prepare {patient['label']}'s new-patient registration and check {provider}'s "
            f"{info['specialty'].lower()} schedule and her {patient['coverage']['payer']} coverage.",
            "",
            "**Patient Registration - Draft (ready for staff to create in the registration system)**",
            f"- Patient Name: {patient['label']} ({pid})",
            f"- Type: {patient.get('patient_type', 'Existing Patient')}",
            f"- Requested Provider: {provider}, {info['specialty']}",
            f"- Chief Complaint: {patient.get('chief_complaint', 'See visit record')}",
            f"- Insurance: {patient['coverage']['payer']}",
            f"- Timeframe: Within {patient.get('timeframe_days', 14)} days",
            "- Source System: Registration module (synthetic)",
            "",
            f"Next: check {provider}'s availability and verify her insurance coverage for this visit.",
        ])
        return "\n".join(lines)

    # ── video turn 2 ───────────────────────────────────────────
    def _coverage_lines(self, patient):
        cov = patient["coverage"]
        lines = [
            f"- Payer recorded in synthetic source: {cov['payer']}",
            f"- Source-recorded state: {cov['recorded_status']}",
            f"- Evidence date: {cov['evidence_date']}",
        ]
        if "specialist_copay" in cov:
            lines.extend([
                f"- Policy Number: {cov['policy_number']} | Group Number: {cov['group_number']}",
                f"- Copay: ${cov['specialist_copay']} specialist visit",
                f"- Deductible: ${cov['deductible_met']:,} met of ${cov['deductible']:,}",
                f"- Prior Auth Required: {cov['prior_auth']}",
                f"- Network: {cov['network']}",
            ])
        lines.append(f"- Human follow-up: {cov['follow_up']}")
        return lines

    def _coverage_evidence(self, pid, provider, _slot):
        patient = PATIENTS[pid]
        lines = _notice("Coverage Evidence Review")
        lines.append(f"## {patient['label']} ({pid})")
        lines.extend(self._coverage_lines(patient))
        slots = ", ".join(_slot_label(s) for s in AVAILABILITY.get(provider, []))
        lines.extend(["", f"**{provider} availability:** {slots}", ""])
        return "\n".join(lines)

    def _appointment_availability(self, pid, provider, _slot):
        patient = PATIENTS[pid]
        lines = _notice("Appointment Availability Review")
        lines.append("These are candidate source slots for staff review; nothing has been reserved or booked.")
        lines.append("")
        lines.append(f"## {provider}")
        for slot in AVAILABILITY[provider]:
            when = f" ({slot['date']} {slot['time']})" if slot.get("label") else ""
            lines.append(f"- {_slot_label(slot)}{when} — {slot['service']}")
        if "specialist_copay" in patient["coverage"]:
            cov = patient["coverage"]
            lines.extend([
                "",
                f"**Coverage snapshot for {patient['label']}:** {cov['recorded_status']} {cov['payer']}, "
                f"${cov['specialist_copay']} specialist copay, deductible ${cov['deductible_met']:,} met of "
                f"${cov['deductible']:,}, prior auth {cov['prior_auth']}, {cov['network']}.",
            ])
        lines.append("")
        return "\n".join(lines)

    # ── video turn 3 ───────────────────────────────────────────
    def _appointment_hold_draft(self, pid, provider, slot_text):
        patient = PATIENTS[pid]
        slot = _pick_slot(provider, slot_text)
        day, time = _fmt_long(_slot_datetime(slot))
        info = PROVIDERS.get(provider, {"credential": "", "location": "See scheduling system", "specialty": ""})
        packet = INTAKE_PACKETS["base"] + INTAKE_PACKETS.get(info.get("specialty", ""), [])
        names = ", ".join(item.split(":")[0] for item in packet)
        lines = _notice("Appointment Request Draft")
        lines.extend([
            f"Appointment request prepared for {patient['label']} — ready for staff to book and confirm "
            "in the scheduling system; nothing has been reserved or booked yet.",
            "",
            f"- Date: {day}",
            f"- Time: {time}",
            f"- Duration: {NEW_PATIENT_VISIT_MINUTES} minutes (new patient)",
            f"- Provider: {provider}, {info['credential']}".rstrip(", "),
            f"- Location: {info['location']}",
            f"- Visit Type: {slot['service'].title()}",
            "- Confirmation: SMS & email confirmation drafted for staff to send after booking",
            "",
            f"**Intake forms she needs before the visit:** {names}.",
            "",
        ])
        return "\n".join(lines)

    # ── video turn 4 ───────────────────────────────────────────
    def _intake_packet(self, pid, provider, _slot):
        patient = PATIENTS[pid]
        specialty = PROVIDERS.get(provider, {}).get("specialty", "")
        packet = INTAKE_PACKETS["base"][:3] + INTAKE_PACKETS.get(specialty, []) + INTAKE_PACKETS["base"][3:]
        lines = _notice("Digital Intake Packet Draft")
        lines.append(
            f"Packet tailored to {specialty or 'the visit'} for {patient['label']}: it includes HIPAA "
            "authorization and medication history. Ready for staff to send to her patient portal; "
            "she can complete it on her phone."
        )
        lines.append("")
        for item in packet:
            lines.append(f"- {item}")
        lines.extend(["- Portal Link: ready to send via SMS to the mobile number on file", ""])
        return "\n".join(lines)

    # ── video turn 5 ───────────────────────────────────────────
    def _reminder_plan(self, pid, provider, slot_text):
        patient = PATIENTS[pid]
        proto = REMINDER_PROTOCOL
        slot = _pick_slot(provider, slot_text)
        visit = _slot_datetime(slot)
        lines = _notice("No-Show Prevention Reminder Plan")
        lines.append(
            f"Recommended multi-channel reminder sequence for {patient['label']}'s {_slot_label(slot)} "
            f"visit, based on the {proto['protocol_name']} (ready for staff to activate):"
        )
        lines.append("")
        for tp in proto["touchpoints"]:
            when = visit - datetime.timedelta(hours=tp["hours_before"])
            lines.append(f"- {tp['name']}: {tp['channel']} ({_fmt_day_time(when)})")
        alert = visit - datetime.timedelta(days=proto["forms_alert_days_before"])
        lines.extend([
            f"- Forms Completion Alert: Reminder if not completed by {alert:%A}",
            f"- Easy Reschedule: Reply {proto['reschedule_keyword']} to SMS anytime",
            f"- Waitlist Automation: {proto['waitlist_rule']}",
            f"- Historical No-Show Rate: {proto['historical_no_show_rate']}",
            "",
        ])
        return "\n".join(lines)


if __name__ == "__main__":
    agent = PatientIntakeAgent()
    print(agent.perform(operation="new_patient_intake"))
    print(agent.perform(operation="appointment_availability"))
    print(agent.perform(operation="coverage_evidence"))
    print(agent.perform(operation="appointment_hold_draft", slot="Tuesday at 2:30"))
    print(agent.perform(operation="intake_packet"))
    print(agent.perform(operation="reminder_plan"))
