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

## Pre-op clearance patient 78392 (video walkthrough)

All values are fictional.

| Field | Value |
|---|---|
| patient_id | 78392 |
| name | John Martinez |
| age | 67 |
| sex | male |
| procedure | Right eye phacoemulsification |
| surgeon | Dr. Amanda Chen (Ophthalmology) |
| surgery_date | Next week, November 2 |
| asa_class | III (severe systemic disease) |
| encounters_reviewed | 14 |
| months_reviewed | 12 |
| data_sources | Recent labs, medication list, encounter notes, problem list |

### Cardiac findings

| Finding | Status |
|---|---|
| Chest pain event | 2 months ago - MI ruled out |
| ECG | Normal sinus 82 bpm (yesterday) |
| Cardiac risk | Low for MAC anesthesia (source-recorded cardiology assessment) |

### Respiratory findings

| Finding | Status |
|---|---|
| COPD stage | Stage 2, FEV1 68% predicted |
| Last exacerbation | 6 weeks ago (resolved) |
| Current therapy | Symbicort inhaler BID |
| O2 saturation | 94% room air (acceptable) |

Labs: Cr 1.1, eGFR 67, K 4.2 - all within the acceptable range

### Medications (12 active)

| Medication | Surgical plan (synthetic perioperative protocol) |
|---|---|
| Metoprolol 50mg BID | Continue through surgery |
| Lisinopril 10mg daily | HOLD morning of surgery |
| Metformin 1000mg BID | HOLD 24 hours before |
| Symbicort inhaler | Continue - use AM of surgery |
| Tamsulosin 0.4mg | ALERT: Floppy iris risk |
| Aspirin 81mg | Continue per ophthalmology |

Other medications with no surgical concerns: Atorvastatin 40mg daily; Omeprazole 20mg daily; Vitamin D3 1000 IU daily; Docusate 100mg daily; Acetaminophen 500mg as needed; Fluticasone nasal spray daily.

Critical alert: Tamsulosin causes intraoperative floppy iris syndrome - anesthesia team must be notified.

### Anesthesia considerations (protocol reference)

- MAC preferred (monitored anesthesia care): Lower respiratory risk vs general anesthesia; Better for COPD Stage 2 patients; Adequate for phacoemulsification
- Monitoring: Extended PACU - 2-3 hours with continuous pulse oximetry; Respiratory precautions - due to COPD history; Floppy iris alert - anesthesia team notification required; Afternoon slot - allows morning bronchodilator therapy

### ASA class III factors

| Factor | Classification impact |
|---|---|
| COPD Stage 2 | Severe systemic disease |
| FEV1 68% | Functionally limited |
| CAD history | Controlled but present |
| HTN | Well-controlled on meds |
| Recent exacerbation | 6 weeks ago |
| Age 67 | Risk factor consideration |

Risk assessment: Cardiac risk: Low (Goldman <1%); Respiratory risk: Moderate (COPD, recent exacerbation); Overall surgical risk: Moderate. Mitigation: MAC anesthesia, extended PACU, afternoon slot for optimal respiratory status.

### Re-evaluation criteria

- Immediate concerns: COPD exacerbation <2 weeks; Acute cardiac symptoms; O2 sat <90% on room air; Uncontrolled blood pressure >180/100
- Timing considerations: Active URI or bronchitis - delay 2-4 weeks; Medication changes - reassess stability; New cardiac symptoms - cardiology consult
- If general anesthesia required: Pulmonology consult mandatory; Formal PFTs recommended; Higher ASA class (consider IV); ICU bed availability check

### Clearance note draft

- Components: ASA Class III status documented; Cardiac clearance - stable CAD, controlled HTN; Pulmonary optimization - current bronchodilator therapy; Medication instructions - lisinopril, metformin holds; Anesthesia alert - floppy iris syndrome risk; MAC anesthesia recommendation; Post-op monitoring requirements
- Proposed distribution: Dr. Amanda Chen (Ophthalmology) - secure message; Anesthesia pre-op clinic - EHR notification; Surgical scheduling - clearance confirmation

