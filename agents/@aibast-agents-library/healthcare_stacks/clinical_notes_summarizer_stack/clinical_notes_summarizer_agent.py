"""Read-only summaries of synthetic clinical source text."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/clinical-notes-summarizer",
    "version": "1.2.0",
    "display_name": "Clinical Notes Summarizer Agent",
    "description": (
        "Handles synthetic clinical-note review: summarize encounters, list source-recorded "
        "medications, extract source-coded problem lists without confirming diagnoses, and summarize "
        "referral context; for pre-op clearance it assembles a patient snapshot, cardiopulmonary "
        "findings, a perioperative medication review, protocol-matched anesthesia considerations, ASA "
        "risk factors, re-evaluation criteria and a draft clearance note for physician signature. It "
        "requires clinician review and never diagnoses, recommends treatment, clears a patient, places a "
        "referral, schedules care, sends a message, or changes a record."
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

# Pre-op clearance demo patient (video scenario). Every value is fictional.
PREOP_PATIENT = {
    "patient_id": "78392",
    "name": "John Martinez",
    "age": 67,
    "sex": "male",
    "procedure": "Right eye phacoemulsification",
    "surgeon": "Dr. Amanda Chen (Ophthalmology)",
    "surgery_date": "Next week, November 2",
    "asa_class": "III (severe systemic disease)",
    "encounters_reviewed": 14,
    "months_reviewed": 12,
    "data_sources": "Recent labs, medication list, encounter notes, problem list",
}

CARDIAC_FINDINGS = [
    ["Chest pain event", "2 months ago - MI ruled out"],
    ["ECG", "Normal sinus 82 bpm (yesterday)"],
    ["Cardiac risk", "Low for MAC anesthesia (source-recorded cardiology assessment)"],
]

RESPIRATORY_FINDINGS = [
    ["COPD stage", "Stage 2, FEV1 68% predicted"],
    ["Last exacerbation", "6 weeks ago (resolved)"],
    ["Current therapy", "Symbicort inhaler BID"],
    ["O2 saturation", "94% room air (acceptable)"],
]

PREOP_LABS = "Cr 1.1, eGFR 67, K 4.2 - all within the acceptable range"

PERIOP_MEDICATIONS = [
    ["Metoprolol 50mg BID", "Continue through surgery"],
    ["Lisinopril 10mg daily", "HOLD morning of surgery"],
    ["Metformin 1000mg BID", "HOLD 24 hours before"],
    ["Symbicort inhaler", "Continue - use AM of surgery"],
    ["Tamsulosin 0.4mg", "ALERT: Floppy iris risk"],
    ["Aspirin 81mg", "Continue per ophthalmology"],
]

OTHER_MEDICATIONS = [
    "Atorvastatin 40mg daily",
    "Omeprazole 20mg daily",
    "Vitamin D3 1000 IU daily",
    "Docusate 100mg daily",
    "Acetaminophen 500mg as needed",
    "Fluticasone nasal spray daily",
]

FLOPPY_IRIS_ALERT = "Tamsulosin causes intraoperative floppy iris syndrome - anesthesia team must be notified"

ANESTHESIA_CONSIDERATIONS = {
    "preferred": "MAC preferred (monitored anesthesia care)",
    "reasons": [
        "Lower respiratory risk vs general anesthesia",
        "Better for COPD Stage 2 patients",
        "Adequate for phacoemulsification",
    ],
    "monitoring": [
        "Extended PACU - 2-3 hours with continuous pulse oximetry",
        "Respiratory precautions - due to COPD history",
        "Floppy iris alert - anesthesia team notification required",
        "Afternoon slot - allows morning bronchodilator therapy",
    ],
}

ASA_FACTORS = [
    ["COPD Stage 2", "Severe systemic disease"],
    ["FEV1 68%", "Functionally limited"],
    ["CAD history", "Controlled but present"],
    ["HTN", "Well-controlled on meds"],
    ["Recent exacerbation", "6 weeks ago"],
    ["Age 67", "Risk factor consideration"],
]

RISK_ASSESSMENT = [
    "Cardiac risk: Low (Goldman <1%)",
    "Respiratory risk: Moderate (COPD, recent exacerbation)",
    "Overall surgical risk: Moderate",
]

RISK_MITIGATION = "MAC anesthesia, extended PACU, afternoon slot for optimal respiratory status"

REEVALUATION_CRITERIA = {
    "Immediate concerns": [
        "COPD exacerbation <2 weeks",
        "Acute cardiac symptoms",
        "O2 sat <90% on room air",
        "Uncontrolled blood pressure >180/100",
    ],
    "Timing considerations": [
        "Active URI or bronchitis - delay 2-4 weeks",
        "Medication changes - reassess stability",
        "New cardiac symptoms - cardiology consult",
    ],
    "If general anesthesia required": [
        "Pulmonology consult mandatory",
        "Formal PFTs recommended",
        "Higher ASA class (consider IV)",
        "ICU bed availability check",
    ],
}

CLEARANCE_NOTE_COMPONENTS = [
    "ASA Class III status documented",
    "Cardiac clearance - stable CAD, controlled HTN",
    "Pulmonary optimization - current bronchodilator therapy",
    "Medication instructions - lisinopril, metformin holds",
    "Anesthesia alert - floppy iris syndrome risk",
    "MAC anesthesia recommendation",
    "Post-op monitoring requirements",
]

CLEARANCE_DISTRIBUTION = [
    "Dr. Amanda Chen (Ophthalmology) - secure message",
    "Anesthesia pre-op clinic - EHR notification",
    "Surgical scheduling - clearance confirmation",
]

PREOP_OPERATIONS = [
    "preop_snapshot", "cardiopulmonary_review", "perioperative_medication_review",
    "anesthesia_considerations", "risk_factor_summary", "reevaluation_criteria", "clearance_note_draft",
]

ALIASES = {
    "summarize_encounter": "encounter_summary",
    "medication_review": "medication_inventory",
    "problem_list": "problem_list_extract",
    "referral_summary": "referral_context",
    "pre_op_clearance": "preop_snapshot",
}


def _notice(title):
    return [f"# {title}", "", f"> {SAFETY}", ""]


def _preop_patient(query):
    """Patient ID / MRN or name (e.g. '78392', 'John Martinez'); None when it is not the pre-op patient."""
    if not query:
        return PREOP_PATIENT
    q = str(query).lower().strip()
    if PREOP_PATIENT["patient_id"] in q or q in PREOP_PATIENT["name"].lower():
        return PREOP_PATIENT
    return None


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
                        "enum": ["encounter_summary", "medication_inventory", "problem_list_extract", "referral_context"] + PREOP_OPERATIONS,
                        "description": (
                            "Pre-op clearance walkthrough for patient 78392 (call right away, no ID "
                            "needed): preop_snapshot for a pre-op clearance summary; "
                            "cardiopulmonary_review for cardiac and respiratory status with recent "
                            "testing; perioperative_medication_review to review medications and flag "
                            "surgical concerns; anesthesia_considerations for anesthesia and monitoring "
                            "recommendations; risk_factor_summary for the ASA class and risk factors; "
                            "reevaluation_criteria for what would change the recommendation or when to "
                            "reconsider clearance; clearance_note_draft to generate the clearance note "
                            "and send it to ophthalmology (returns a draft for physician signature, never "
                            "sends). "
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
                    "patient_id": {
                        "type": "string",
                        "description": "Optional patient ID / MRN or name for the pre-op operations (default 78392).",
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
        preop = {
            "preop_snapshot": self._preop_snapshot,
            "cardiopulmonary_review": self._cardiopulmonary_review,
            "perioperative_medication_review": self._perioperative_medication_review,
            "anesthesia_considerations": self._anesthesia_considerations,
            "risk_factor_summary": self._risk_factor_summary,
            "reevaluation_criteria": self._reevaluation_criteria,
            "clearance_note_draft": self._clearance_note_draft,
        }
        if operation in preop:
            patient = _preop_patient(kwargs.get("patient_id"))
            if patient is None:
                return (f"# Pre-Op Clearance\n\n> {SAFETY}\n\nNo synthetic patient matched "
                        f"`{kwargs.get('patient_id')}`. The pre-op record in this synthetic set is "
                        f"{PREOP_PATIENT['name']} (Patient ID {PREOP_PATIENT['patient_id']}).")
            return preop[operation](patient)
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

    # ── pre-op clearance walkthrough (patient 78392) ──
    def _preop_snapshot(self, p):
        lines = _notice("Pre-Op Clearance Summary")
        lines.append(f"Reviewed {p['encounters_reviewed']} encounters over the past {p['months_reviewed']} months "
                     "from the synthetic record to assemble the pre-operative snapshot.")
        lines.append("")
        lines.append("| Detail | Value |")
        lines.append("|---|---|")
        lines.append(f"| Patient | {p['name']}, {p['age']}yo {p['sex']} |")
        lines.append(f"| MRN | {p['patient_id']} |")
        lines.append(f"| Procedure | {p['procedure']} |")
        lines.append(f"| Surgeon | {p['surgeon']} |")
        lines.append(f"| Surgery date | {p['surgery_date']} |")
        lines.append(f"| ASA class | {p['asa_class']} (source-recorded) |")
        lines.append("")
        lines.append(f"**Data sources:** {p['data_sources']} integrated.")
        lines.append("**Next:** see the cardiac and respiratory assessment?")
        return "\n".join(lines)

    def _cardiopulmonary_review(self, p):
        lines = _notice("Cardiopulmonary Assessment")
        lines.append("Source-recorded findings: stable cardiac status, moderate respiratory risk requiring attention.")
        lines.append("")
        lines.append("**Cardiac Assessment - Stable**")
        lines.append("")
        lines.append("| Finding | Status |")
        lines.append("|---|---|")
        for f in CARDIAC_FINDINGS:
            lines.append(f"| {f[0]} | {f[1]} |")
        lines.append("")
        lines.append("**Respiratory - Moderate Risk**")
        lines.append("")
        lines.append("| Finding | Status |")
        lines.append("|---|---|")
        for f in RESPIRATORY_FINDINGS:
            lines.append(f"| {f[0]} | {f[1]} |")
        lines.append("")
        lines.append(f"**Lab Results:** {PREOP_LABS}")
        lines.append("**Next:** check the medication list for surgical concerns?")
        return "\n".join(lines)

    def _perioperative_medication_review(self, p):
        total = len(PERIOP_MEDICATIONS) + len(OTHER_MEDICATIONS)
        lines = _notice(f"Medications - {total} Active")
        lines.append("Source-recorded medications with the synthetic perioperative protocol flag; the prescriber confirms every change.")
        lines.append("")
        lines.append("| Medication | Surgical plan (per protocol) |")
        lines.append("|---|---|")
        for m in PERIOP_MEDICATIONS:
            lines.append(f"| {m[0]} | {m[1]} |")
        lines.append("")
        lines.append(f"**Critical Alert:** {FLOPPY_IRIS_ALERT}")
        lines.append(f"**Other Meds:** {len(OTHER_MEDICATIONS)} additional medications reconciled with no surgical concerns "
                     f"({'; '.join(OTHER_MEDICATIONS)}).")
        lines.append("**Next:** see anesthesia considerations?")
        return "\n".join(lines)

    def _anesthesia_considerations(self, p):
        a = ANESTHESIA_CONSIDERATIONS
        lines = _notice("Anesthesia and Monitoring Considerations")
        lines.append("Protocol-matched considerations for the anesthesiologist and the physician's clearance decision.")
        lines.append("")
        lines.append(f"**Anesthesia plan:** {a['preferred']}")
        for r in a["reasons"]:
            lines.append(f"- {r}")
        lines.append("")
        lines.append("**Post-op monitoring:**")
        for r in a["monitoring"]:
            lines.append(f"- {r}")
        lines.append("")
        lines.append("**Clearance status:** Ready for physician sign-off with documented precautions "
                     "(the clearance decision is the physician's).")
        lines.append("**Next:** generate the formal clearance note draft?")
        return "\n".join(lines)

    def _risk_factor_summary(self, p):
        lines = _notice("ASA Class III Justification")
        lines.append("ASA classification factors from the source-recorded systemic diseases.")
        lines.append("")
        lines.append("| Factor | Classification impact |")
        lines.append("|---|---|")
        for f in ASA_FACTORS:
            lines.append(f"| {f[0]} | {f[1]} |")
        lines.append("")
        lines.append("**Risk assessment (source-recorded calculators):**")
        for r in RISK_ASSESSMENT:
            lines.append(f"- {r}")
        lines.append(f"\n**Mitigation:** {RISK_MITIGATION}")
        lines.append("**Next:** see what would change the recommendation?")
        return "\n".join(lines)

    def _reevaluation_criteria(self, p):
        lines = _notice("Clearance Re-evaluation Criteria")
        lines.append("Criteria for reconsidering clearance and alternative scenarios (synthetic protocol reference).")
        for group, items in REEVALUATION_CRITERIA.items():
            lines.append("")
            lines.append(f"**{group}:**")
            for i in items:
                lines.append(f"- {i}")
        lines.append("")
        lines.append("**Current status:** No re-evaluation trigger is present in the record; plan as documented with MAC, "
                     "pending the physician's clearance decision.")
        lines.append("**Next:** generate the clearance note draft?")
        return "\n".join(lines)

    def _clearance_note_draft(self, p):
        lines = _notice("Pre-Operative Clearance Note - Draft")
        lines.append(f"Draft note for {p['name']} (MRN {p['patient_id']}), {p['procedure']}, {p['surgery_date']}.")
        lines.append("")
        lines.append("**Note components:**")
        for c in CLEARANCE_NOTE_COMPONENTS:
            lines.append(f"- {c}")
        lines.append("")
        lines.append("**Proposed distribution (sent after physician signature):**")
        for d in CLEARANCE_DISTRIBUTION:
            lines.append(f"- {d}")
        lines.append("")
        lines.append("**Status:** Draft ready for physician e-signature, to file under 'Pre-Op Evaluation'. "
                     "Not signed, not filed, and nothing was sent.")
        return "\n".join(lines)


if __name__ == "__main__":
    agent = ClinicalNotesSummarizerAgent()
    for op in PREOP_OPERATIONS:
        print(agent.perform(operation=op))
        print()
