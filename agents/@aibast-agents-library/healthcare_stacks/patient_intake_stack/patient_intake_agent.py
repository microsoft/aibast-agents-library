"""
Patient Intake Agent for Healthcare.

Manages patient intake workflows including form generation, insurance
verification, appointment scheduling, and pre-visit summary preparation
for front desk and clinical staff.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/patient-intake",
    "version": "1.0.0",
    "display_name": "Patient Intake Agent",
    "description": "Manages patient intake forms, insurance verification, appointment scheduling, and pre-visit summary preparation.",
    "author": "AIBAST",
    "tags": ["intake", "insurance", "scheduling", "patient", "registration", "healthcare"],
    "category": "healthcare",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

PATIENTS = {
    "PT-20001": {
        "name": "Jennifer Walsh",
        "dob": "1978-04-22",
        "gender": "Female",
        "phone": "555-0142",
        "email": "j.walsh@email.com",
        "address": "142 Oak Street, Springfield, IL 62701",
        "emergency_contact": {"name": "Michael Walsh", "relation": "Spouse", "phone": "555-0143"},
        "primary_language": "English",
        "race": "White",
        "ethnicity": "Non-Hispanic",
    },
    "PT-20002": {
        "name": "David Nguyen",
        "dob": "1992-11-08",
        "gender": "Male",
        "phone": "555-0255",
        "email": "d.nguyen@email.com",
        "address": "88 Maple Avenue, Springfield, IL 62702",
        "emergency_contact": {"name": "Linh Nguyen", "relation": "Mother", "phone": "555-0256"},
        "primary_language": "English",
        "race": "Asian",
        "ethnicity": "Non-Hispanic",
    },
    "PT-20003": {
        "name": "Maria Gonzalez",
        "dob": "1965-07-15",
        "gender": "Female",
        "phone": "555-0388",
        "email": "m.gonzalez@email.com",
        "address": "305 Elm Drive, Springfield, IL 62703",
        "emergency_contact": {"name": "Carlos Gonzalez", "relation": "Son", "phone": "555-0389"},
        "primary_language": "Spanish",
        "race": "White",
        "ethnicity": "Hispanic",
    },
}

INSURANCE_PLANS = {
    "PT-20001": {
        "primary": {
            "payer": "Blue Cross Blue Shield of Illinois",
            "plan": "PPO Gold",
            "member_id": "BCBS-884721",
            "group_number": "GRP-44210",
            "effective_date": "2025-01-01",
            "copay_office": 25,
            "copay_specialist": 50,
            "deductible": 1500,
            "deductible_met": 875,
            "coinsurance_pct": 20,
            "verification_status": "verified",
            "last_verified": "2026-03-10",
        },
        "secondary": None,
    },
    "PT-20002": {
        "primary": {
            "payer": "Aetna",
            "plan": "HMO Select",
            "member_id": "AET-552190",
            "group_number": "GRP-88104",
            "effective_date": "2025-07-01",
            "copay_office": 20,
            "copay_specialist": 40,
            "deductible": 2000,
            "deductible_met": 320,
            "coinsurance_pct": 25,
            "verification_status": "verified",
            "last_verified": "2026-03-12",
        },
        "secondary": None,
    },
    "PT-20003": {
        "primary": {
            "payer": "Medicare Part B",
            "plan": "Original Medicare",
            "member_id": "1EG4-TE5-MK72",
            "group_number": "N/A",
            "effective_date": "2025-07-15",
            "copay_office": 0,
            "copay_specialist": 0,
            "deductible": 257,
            "deductible_met": 257,
            "coinsurance_pct": 20,
            "verification_status": "verified",
            "last_verified": "2026-03-14",
        },
        "secondary": {
            "payer": "AARP Medigap Plan F",
            "plan": "Supplemental",
            "member_id": "AARP-MG-88421",
            "group_number": "N/A",
            "effective_date": "2025-07-15",
            "verification_status": "pending",
            "last_verified": None,
        },
    },
}

PROVIDER_SCHEDULES = {
    "Dr. Anita Patel": {
        "specialty": "Internal Medicine",
        "location": "Main Clinic - Suite 200",
        "available_slots": [
            {"date": "2026-03-18", "time": "09:00", "duration_min": 30, "type": "follow_up"},
            {"date": "2026-03-18", "time": "10:30", "duration_min": 60, "type": "new_patient"},
            {"date": "2026-03-19", "time": "14:00", "duration_min": 30, "type": "follow_up"},
            {"date": "2026-03-20", "time": "08:30", "duration_min": 60, "type": "new_patient"},
        ],
    },
    "Dr. James Wright": {
        "specialty": "Family Medicine",
        "location": "Main Clinic - Suite 105",
        "available_slots": [
            {"date": "2026-03-18", "time": "11:00", "duration_min": 30, "type": "follow_up"},
            {"date": "2026-03-19", "time": "09:30", "duration_min": 60, "type": "new_patient"},
            {"date": "2026-03-19", "time": "15:00", "duration_min": 30, "type": "follow_up"},
        ],
    },
    "Dr. Sarah Lin": {
        "specialty": "Cardiology",
        "location": "Cardiology Center - Suite 400",
        "available_slots": [
            {"date": "2026-03-20", "time": "10:00", "duration_min": 45, "type": "consultation"},
            {"date": "2026-03-21", "time": "13:00", "duration_min": 45, "type": "consultation"},
        ],
    },
}

INTAKE_QUESTIONNAIRES = {
    "new_patient": {
        "sections": ["Demographics", "Medical History", "Surgical History", "Family History",
                     "Social History", "Medications", "Allergies", "Review of Systems"],
        "estimated_time_min": 15,
    },
    "follow_up": {
        "sections": ["Medication Changes", "New Symptoms", "Vital Signs Update"],
        "estimated_time_min": 5,
    },
    "annual_wellness": {
        "sections": ["Demographics Update", "Health Risk Assessment", "PHQ-9 Depression Screen",
                     "Fall Risk Assessment", "Advance Directives", "Preventive Services Review"],
        "estimated_time_min": 20,
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _intake_form(patient_id=None):
    forms = []
    pats = {patient_id: PATIENTS[patient_id]} if patient_id and patient_id in PATIENTS else PATIENTS
    for pid, pat in pats.items():
        ins = INSURANCE_PLANS.get(pid, {})
        forms.append({
            "patient_id": pid, "name": pat["name"], "dob": pat["dob"],
            "gender": pat["gender"], "phone": pat["phone"],
            "address": pat["address"],
            "emergency_contact": pat["emergency_contact"],
            "insurance_payer": ins.get("primary", {}).get("payer", "Unknown"),
            "member_id": ins.get("primary", {}).get("member_id", "Unknown"),
        })
    return {"forms": forms}


def _insurance_verification():
    results = []
    for pid, ins in INSURANCE_PLANS.items():
        pname = PATIENTS.get(pid, {}).get("name", "Unknown")
        primary = ins.get("primary", {})
        secondary = ins.get("secondary")
        ded_remaining = primary.get("deductible", 0) - primary.get("deductible_met", 0)
        results.append({
            "patient_id": pid, "name": pname,
            "payer": primary.get("payer", "N/A"),
            "plan": primary.get("plan", "N/A"),
            "member_id": primary.get("member_id", "N/A"),
            "status": primary.get("verification_status", "unknown"),
            "copay": primary.get("copay_office", 0),
            "deductible_remaining": max(0, ded_remaining),
            "has_secondary": secondary is not None,
            "secondary_status": secondary.get("verification_status", "N/A") if secondary else "N/A",
        })
    return {"verifications": results}


def _appointment_scheduling():
    schedule = []
    for provider, info in PROVIDER_SCHEDULES.items():
        for slot in info["available_slots"]:
            schedule.append({
                "provider": provider, "specialty": info["specialty"],
                "location": info["location"],
                "date": slot["date"], "time": slot["time"],
                "duration_min": slot["duration_min"],
                "type": slot["type"],
            })
    schedule.sort(key=lambda x: (x["date"], x["time"]))
    return {"available_slots": schedule, "total_slots": len(schedule)}


def _pre_visit_summary():
    summaries = []
    for pid, pat in PATIENTS.items():
        ins = INSURANCE_PLANS.get(pid, {}).get("primary", {})
        copay = ins.get("copay_office", 0)
        ded_remaining = max(0, ins.get("deductible", 0) - ins.get("deductible_met", 0))
        summaries.append({
            "patient_id": pid, "name": pat["name"], "dob": pat["dob"],
            "phone": pat["phone"], "language": pat["primary_language"],
            "payer": ins.get("payer", "N/A"),
            "copay": copay, "deductible_remaining": ded_remaining,
            "verification_status": ins.get("verification_status", "unknown"),
        })
    return {"summaries": summaries}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class PatientIntakeAgent(BasicAgent):
    """Patient intake workflow and insurance verification agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/patient-intake"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "intake_form",
                            "insurance_verification",
                            "appointment_scheduling",
                            "pre_visit_summary",
                        ],
                        "description": "The intake operation to perform.",
                    },
                    "patient_id": {
                        "type": "string",
                        "description": "Optional patient ID to filter results.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "intake_form")
        if op == "intake_form":
            return self._intake_form()
        elif op == "insurance_verification":
            return self._insurance_verification()
        elif op == "appointment_scheduling":
            return self._appointment_scheduling()
        elif op == "pre_visit_summary":
            return self._pre_visit_summary()
        return f"**Error:** Unknown operation `{op}`."

    def _intake_form(self) -> str:
        data = _intake_form()
        lines = ["# Patient Intake Forms", ""]
        for f in data["forms"]:
            ec = f["emergency_contact"]
            lines.append(f"## {f['name']} ({f['patient_id']})")
            lines.append(f"- DOB: {f['dob']} | Gender: {f['gender']}")
            lines.append(f"- Phone: {f['phone']}")
            lines.append(f"- Address: {f['address']}")
            lines.append(f"- Emergency Contact: {ec['name']} ({ec['relation']}) - {ec['phone']}")
            lines.append(f"- Insurance: {f['insurance_payer']} (ID: {f['member_id']})")
            lines.append("")
        return "\n".join(lines)

    def _insurance_verification(self) -> str:
        data = _insurance_verification()
        lines = [
            "# Insurance Verification",
            "",
            "| Patient | Payer | Plan | Member ID | Status | Copay | Ded. Remaining | Secondary |",
            "|---------|-------|------|-----------|--------|-------|---------------|-----------|",
        ]
        for v in data["verifications"]:
            sec = f"Yes ({v['secondary_status']})" if v["has_secondary"] else "No"
            lines.append(
                f"| {v['name']} | {v['payer']} | {v['plan']} | {v['member_id']} "
                f"| {v['status'].upper()} | ${v['copay']} | ${v['deductible_remaining']:,} | {sec} |"
            )
        return "\n".join(lines)

    def _appointment_scheduling(self) -> str:
        data = _appointment_scheduling()
        lines = [
            "# Available Appointments",
            "",
            f"**Total Available Slots:** {data['total_slots']}",
            "",
            "| Date | Time | Provider | Specialty | Location | Duration | Type |",
            "|------|------|----------|-----------|----------|----------|------|",
        ]
        for s in data["available_slots"]:
            lines.append(
                f"| {s['date']} | {s['time']} | {s['provider']} | {s['specialty']} "
                f"| {s['location']} | {s['duration_min']}min | {s['type']} |"
            )
        return "\n".join(lines)

    def _pre_visit_summary(self) -> str:
        data = _pre_visit_summary()
        lines = ["# Pre-Visit Summaries", ""]
        for s in data["summaries"]:
            lines.append(f"## {s['name']} ({s['patient_id']})")
            lines.append(f"- DOB: {s['dob']} | Language: {s['language']}")
            lines.append(f"- Insurance: {s['payer']} ({s['verification_status'].upper()})")
            lines.append(f"- Copay: ${s['copay']} | Deductible Remaining: ${s['deductible_remaining']:,}")
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = PatientIntakeAgent()
    for op in ["intake_form", "insurance_verification", "appointment_scheduling", "pre_visit_summary"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
