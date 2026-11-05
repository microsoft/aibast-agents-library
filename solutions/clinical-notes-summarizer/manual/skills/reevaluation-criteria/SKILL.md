---
name: clinical-notes-summarizer-reevaluation-criteria
description: Reproduce the deterministic Clinical Notes Agent reevaluation criteria workflow, which lists red flags, timing considerations and general-anesthesia criteria.
---
<!-- bic:source=blank -->
# Clinical Notes Agent — reevaluation criteria

## Locked persona prompt

`What would change the recommendation, and when should I reconsider clearance?`

Route semantically equivalent requests here without requiring an operation name or an identifier; the pre-op patient is John Martinez (Patient ID / MRN 78392).

## Source

Use both packaged knowledge files and the exact reference response for this workflow.

## Required output contract

`# Clearance Re-evaluation Criteria`; preserve `COPD exacerbation <2 weeks`, `delay 2-4 weeks`, `ICU bed availability` and every value, medication and status from the reference response.

## Review boundary

This is read-only synthetic evidence. Do not diagnose, recommend treatment, or clear the patient; the clearance decision and signature are the physician's. Never sign, file, or send the note or notify a team; protocol flags and the distribution list are drafts.
