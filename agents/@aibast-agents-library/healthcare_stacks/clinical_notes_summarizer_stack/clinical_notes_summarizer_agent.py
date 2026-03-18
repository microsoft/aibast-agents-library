"""
Clinical Notes Summarizer Agent for Healthcare.

Summarizes patient encounters, performs medication reviews, generates
problem lists, and produces referral summaries from clinical documentation
for healthcare providers and care coordinators.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/clinical-notes-summarizer",
    "version": "1.0.0",
    "display_name": "Clinical Notes Summarizer Agent",
    "description": "Summarizes patient encounters, performs medication reviews, generates problem lists, and produces referral summaries.",
    "author": "AIBAST",
    "tags": ["clinical-notes", "ehr", "encounters", "medications", "referrals", "healthcare"],
    "category": "healthcare",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

PATIENT_ENCOUNTERS = {
    "ENC-2001": {
        "patient_id": "PT-10045",
        "patient_name": "Margaret Sullivan",
        "age": 68,
        "gender": "Female",
        "encounter_date": "2026-03-12",
        "encounter_type": "Office Visit",
        "provider": "Dr. Anita Patel",
        "chief_complaint": "Follow-up for diabetes management and new onset left knee pain",
        "clinical_notes": (
            "Patient presents for routine diabetes follow-up. Reports increased thirst and "
            "urination over past 2 weeks. Also complains of left knee pain, worse with stairs, "
            "onset 3 weeks ago. No trauma. HbA1c drawn today. Blood pressure elevated at 148/92. "
            "Weight 187 lbs, up 4 lbs from last visit. Bilateral pedal edema noted. "
            "Left knee with mild effusion, no instability. ROM slightly decreased."
        ),
        "vital_signs": {
            "bp_systolic": 148, "bp_diastolic": 92, "heart_rate": 78,
            "temperature_f": 98.4, "respiratory_rate": 16, "weight_lbs": 187,
            "bmi": 31.2, "spo2_pct": 97,
        },
        "diagnoses": [
            {"code": "E11.65", "description": "Type 2 diabetes with hyperglycemia", "status": "active"},
            {"code": "I10", "description": "Essential hypertension", "status": "active"},
            {"code": "M17.12", "description": "Primary osteoarthritis, left knee", "status": "new"},
            {"code": "E66.01", "description": "Morbid obesity due to excess calories", "status": "active"},
        ],
        "lab_results": [
            {"test": "HbA1c", "value": "8.2%", "reference": "<7.0%", "flag": "high"},
            {"test": "Fasting Glucose", "value": "182 mg/dL", "reference": "70-100 mg/dL", "flag": "high"},
            {"test": "eGFR", "value": "62 mL/min", "reference": ">60 mL/min", "flag": "borderline"},
            {"test": "Creatinine", "value": "1.1 mg/dL", "reference": "0.6-1.2 mg/dL", "flag": "normal"},
        ],
    },
    "ENC-2002": {
        "patient_id": "PT-10078",
        "patient_name": "Robert Kim",
        "age": 52,
        "gender": "Male",
        "encounter_date": "2026-03-14",
        "encounter_type": "Urgent Care",
        "provider": "Dr. James Wright",
        "chief_complaint": "Chest tightness and shortness of breath for 2 days",
        "clinical_notes": (
            "52-year-old male with history of GERD and anxiety presents with 2 days of intermittent "
            "chest tightness, worse with exertion. Denies radiation to arm or jaw. Reports occasional "
            "SOB climbing stairs. No syncope, diaphoresis, or palpitations. Family history of MI in "
            "father at age 58. Current smoker, 1 PPD x 20 years. EKG shows normal sinus rhythm, "
            "no ST changes. Troponin negative x2. CXR clear."
        ),
        "vital_signs": {
            "bp_systolic": 138, "bp_diastolic": 86, "heart_rate": 92,
            "temperature_f": 98.6, "respiratory_rate": 18, "weight_lbs": 215,
            "bmi": 29.8, "spo2_pct": 96,
        },
        "diagnoses": [
            {"code": "R07.9", "description": "Chest pain, unspecified", "status": "new"},
            {"code": "K21.0", "description": "GERD with esophagitis", "status": "active"},
            {"code": "F41.1", "description": "Generalized anxiety disorder", "status": "active"},
            {"code": "F17.210", "description": "Nicotine dependence, cigarettes", "status": "active"},
        ],
        "lab_results": [
            {"test": "Troponin I", "value": "<0.01 ng/mL", "reference": "<0.04 ng/mL", "flag": "normal"},
            {"test": "BNP", "value": "45 pg/mL", "reference": "<100 pg/mL", "flag": "normal"},
            {"test": "Total Cholesterol", "value": "248 mg/dL", "reference": "<200 mg/dL", "flag": "high"},
            {"test": "LDL", "value": "168 mg/dL", "reference": "<100 mg/dL", "flag": "high"},
        ],
    },
}

MEDICATIONS = {
    "PT-10045": [
        {"name": "Metformin", "dose": "1000mg", "frequency": "BID", "route": "oral", "indication": "Type 2 Diabetes", "status": "active", "start_date": "2022-05-10"},
        {"name": "Lisinopril", "dose": "20mg", "frequency": "daily", "route": "oral", "indication": "Hypertension", "status": "active", "start_date": "2021-03-15"},
        {"name": "Atorvastatin", "dose": "40mg", "frequency": "daily", "route": "oral", "indication": "Hyperlipidemia", "status": "active", "start_date": "2023-01-20"},
        {"name": "Aspirin", "dose": "81mg", "frequency": "daily", "route": "oral", "indication": "Cardiovascular prevention", "status": "active", "start_date": "2023-01-20"},
        {"name": "Meloxicam", "dose": "15mg", "frequency": "daily", "route": "oral", "indication": "Osteoarthritis", "status": "new", "start_date": "2026-03-12"},
    ],
    "PT-10078": [
        {"name": "Omeprazole", "dose": "20mg", "frequency": "daily", "route": "oral", "indication": "GERD", "status": "active", "start_date": "2024-08-05"},
        {"name": "Sertraline", "dose": "100mg", "frequency": "daily", "route": "oral", "indication": "Anxiety", "status": "active", "start_date": "2023-11-12"},
        {"name": "Atorvastatin", "dose": "80mg", "frequency": "daily", "route": "oral", "indication": "Hyperlipidemia", "status": "new", "start_date": "2026-03-14"},
        {"name": "Aspirin", "dose": "81mg", "frequency": "daily", "route": "oral", "indication": "Cardiovascular prevention", "status": "new", "start_date": "2026-03-14"},
    ],
}

REFERRALS = {
    "REF-3001": {
        "patient_id": "PT-10045",
        "patient_name": "Margaret Sullivan",
        "from_provider": "Dr. Anita Patel",
        "to_specialty": "Orthopedics",
        "to_provider": "Dr. Michael Torres",
        "reason": "Left knee osteoarthritis evaluation - possible injection or surgical consult",
        "urgency": "routine",
        "encounter_id": "ENC-2001",
    },
    "REF-3002": {
        "patient_id": "PT-10078",
        "patient_name": "Robert Kim",
        "from_provider": "Dr. James Wright",
        "to_specialty": "Cardiology",
        "to_provider": "Dr. Sarah Lin",
        "reason": "Stress test and cardiac risk stratification - chest pain with cardiac risk factors",
        "urgency": "urgent",
        "encounter_id": "ENC-2002",
    },
    "REF-3003": {
        "patient_id": "PT-10078",
        "patient_name": "Robert Kim",
        "from_provider": "Dr. James Wright",
        "to_specialty": "Pulmonology",
        "to_provider": "Dr. David Huang",
        "reason": "Smoking cessation program and pulmonary function evaluation",
        "urgency": "routine",
        "encounter_id": "ENC-2002",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _summarize_encounter(encounter_id=None):
    encounters = PATIENT_ENCOUNTERS if not encounter_id else {encounter_id: PATIENT_ENCOUNTERS[encounter_id]}
    summaries = []
    for eid, enc in encounters.items():
        abnormal_labs = [l for l in enc["lab_results"] if l["flag"] != "normal"]
        summaries.append({
            "encounter_id": eid, "patient": enc["patient_name"], "age": enc["age"],
            "date": enc["encounter_date"], "type": enc["encounter_type"],
            "provider": enc["provider"], "chief_complaint": enc["chief_complaint"],
            "diagnoses": enc["diagnoses"], "abnormal_labs": abnormal_labs,
            "bp": f"{enc['vital_signs']['bp_systolic']}/{enc['vital_signs']['bp_diastolic']}",
            "bmi": enc["vital_signs"]["bmi"],
        })
    return {"summaries": summaries}


def _medication_review(patient_id=None):
    if patient_id:
        meds = {patient_id: MEDICATIONS.get(patient_id, [])}
    else:
        meds = MEDICATIONS
    reviews = []
    for pid, med_list in meds.items():
        active = [m for m in med_list if m["status"] == "active"]
        new = [m for m in med_list if m["status"] == "new"]
        reviews.append({
            "patient_id": pid, "total_medications": len(med_list),
            "active": active, "new": new,
            "polypharmacy_flag": len(med_list) >= 5,
        })
    return {"reviews": reviews}


def _problem_list():
    problems = {}
    for eid, enc in PATIENT_ENCOUNTERS.items():
        pid = enc["patient_id"]
        if pid not in problems:
            problems[pid] = {"patient": enc["patient_name"], "active": [], "new": []}
        for dx in enc["diagnoses"]:
            entry = {"code": dx["code"], "description": dx["description"]}
            if dx["status"] == "new":
                problems[pid]["new"].append(entry)
            else:
                problems[pid]["active"].append(entry)
    return {"patients": problems}


def _referral_summary():
    refs = []
    for rid, ref in REFERRALS.items():
        refs.append({
            "id": rid, "patient": ref["patient_name"],
            "from": ref["from_provider"], "to_specialty": ref["to_specialty"],
            "to_provider": ref["to_provider"], "reason": ref["reason"],
            "urgency": ref["urgency"],
        })
    return {"referrals": refs, "total": len(refs)}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class ClinicalNotesSummarizerAgent(BasicAgent):
    """Clinical notes summarization and medication review agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/clinical-notes-summarizer"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "summarize_encounter",
                            "medication_review",
                            "problem_list",
                            "referral_summary",
                        ],
                        "description": "The clinical notes operation to perform.",
                    },
                    "encounter_id": {
                        "type": "string",
                        "description": "Optional encounter ID to filter results.",
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
        op = kwargs.get("operation", "summarize_encounter")
        if op == "summarize_encounter":
            return self._summarize_encounter()
        elif op == "medication_review":
            return self._medication_review()
        elif op == "problem_list":
            return self._problem_list()
        elif op == "referral_summary":
            return self._referral_summary()
        return f"**Error:** Unknown operation `{op}`."

    def _summarize_encounter(self) -> str:
        data = _summarize_encounter()
        lines = ["# Encounter Summaries", ""]
        for s in data["summaries"]:
            lines.append(f"## {s['patient']} (Age {s['age']}) - {s['date']}")
            lines.append(f"**Type:** {s['type']} | **Provider:** {s['provider']}")
            lines.append(f"**Chief Complaint:** {s['chief_complaint']}")
            lines.append(f"**BP:** {s['bp']} | **BMI:** {s['bmi']}")
            lines.append("")
            lines.append("**Diagnoses:**")
            for dx in s["diagnoses"]:
                status_tag = " [NEW]" if dx["status"] == "new" else ""
                lines.append(f"- {dx['code']}: {dx['description']}{status_tag}")
            if s["abnormal_labs"]:
                lines.append("")
                lines.append("**Abnormal Labs:**")
                lines.append("")
                lines.append("| Test | Value | Reference | Flag |")
                lines.append("|------|-------|-----------|------|")
                for lab in s["abnormal_labs"]:
                    lines.append(f"| {lab['test']} | {lab['value']} | {lab['reference']} | {lab['flag'].upper()} |")
            lines.append("")
        return "\n".join(lines)

    def _medication_review(self) -> str:
        data = _medication_review()
        lines = ["# Medication Review", ""]
        for r in data["reviews"]:
            poly = " [POLYPHARMACY FLAG]" if r["polypharmacy_flag"] else ""
            lines.append(f"## Patient {r['patient_id']}{poly}")
            lines.append(f"**Total Medications:** {r['total_medications']}")
            lines.append("")
            lines.append("| Medication | Dose | Frequency | Route | Indication | Status |")
            lines.append("|-----------|------|-----------|-------|-----------|--------|")
            for m in r["active"] + r["new"]:
                lines.append(
                    f"| {m['name']} | {m['dose']} | {m['frequency']} "
                    f"| {m['route']} | {m['indication']} | {m['status'].upper()} |"
                )
            lines.append("")
        return "\n".join(lines)

    def _problem_list(self) -> str:
        data = _problem_list()
        lines = ["# Problem Lists", ""]
        for pid, pl in data["patients"].items():
            lines.append(f"## {pl['patient']} ({pid})")
            if pl["active"]:
                lines.append("\n**Active Problems:**")
                for p in pl["active"]:
                    lines.append(f"- [{p['code']}] {p['description']}")
            if pl["new"]:
                lines.append("\n**New Problems:**")
                for p in pl["new"]:
                    lines.append(f"- [{p['code']}] {p['description']}")
            lines.append("")
        return "\n".join(lines)

    def _referral_summary(self) -> str:
        data = _referral_summary()
        lines = [
            "# Referral Summary",
            "",
            f"**Total Referrals:** {data['total']}",
            "",
            "| Patient | From | To Specialty | To Provider | Urgency | Reason |",
            "|---------|------|-------------|-------------|---------|--------|",
        ]
        for r in data["referrals"]:
            lines.append(
                f"| {r['patient']} | {r['from']} | {r['to_specialty']} "
                f"| {r['to_provider']} | {r['urgency'].upper()} | {r['reason']} |"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = ClinicalNotesSummarizerAgent()
    for op in ["summarize_encounter", "medication_review", "problem_list", "referral_summary"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
