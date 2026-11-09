# Clinical Notes Summarizer Agent — complete synthetic records

> **Fictional demonstration data only.** These records reproduce the deterministic `ClinicalNotesSummarizerAgent`. Never combine them with live patient information or treat them as diagnosis, treatment, clearance, urgency, or a record update.

## Synthetic encounter: SYN-ENC-001

- **Patient label:** Synthetic Patient Alpha
- **Encounter date:** 2026-07-28
- **Exact source note:** Follow-up visit. Patient reports knee discomfort with stairs. No trauma recorded.
- **Source-coded problems, in order:** source-coded type 2 diabetes; source-coded hypertension; knee discomfort
- **Source observations, in order:** blood pressure field: 148/92; laboratory field: HbA1c 8.2%
- **Source-recorded medications, in order:** Metformin 1000 mg twice daily; Lisinopril 20 mg daily
- **Exact referral context:** Orthopedics referral draft recorded; status not confirmed.

## Synthetic encounter: SYN-ENC-002

- **Patient label:** Synthetic Patient Beta
- **Encounter date:** 2026-07-29
- **Exact source note:** Urgent visit source note records intermittent chest tightness and shortness of breath.
- **Source-coded problems, in order:** source-coded chest pain; source-coded reflux; source-coded anxiety
- **Source observations, in order:** ECG field: normal sinus rhythm; troponin field: negative in source note
- **Source-recorded medications, in order:** Omeprazole 20 mg daily; Sertraline 100 mg daily
- **Exact referral context:** Cardiology referral draft recorded; status not confirmed.

## Fixed source facts used by the locked cases

- CN-01 must preserve SYN-ENC-001, 2026-07-28, the exact source note, both exact observations, and `Clinical interpretation: not performed; clinician review required.`
- CN-02 must preserve `Metformin 1000 mg twice daily`, `Lisinopril 20 mg daily`, and clinician/pharmacist reconciliation review.
- CN-03 must preserve `source-coded type 2 diabetes`, `source-coded hypertension`, `knee discomfort`, and `No diagnosis was added, confirmed, or changed.`
- CN-04 must preserve `Orthopedics referral draft recorded; status not confirmed.`, `No referral was placed, scheduled, or changed.`, and authorized clinician/staff review.
