---
name: clinical-notes-summarizer-anesthesia-considerations
description: Reproduce the deterministic Clinical Notes Agent anesthesia considerations workflow, which surfaces protocol-matched anesthesia and monitoring considerations for the physician.
---
<!-- bic:source=blank -->
# Clinical Notes Agent — anesthesia considerations

## Locked persona prompt

`Give me anesthesia and monitoring considerations for his eye surgery.`

Route semantically equivalent requests here without requiring an operation name or an identifier; the pre-op patient is John Martinez (Patient ID / MRN 78392).

## Source

Use both packaged knowledge files and the exact reference response for this workflow.

## Required output contract

`# Anesthesia and Monitoring Considerations`; preserve `MAC preferred`, `Extended PACU`, `Afternoon slot` and every value, medication and status from the reference response.

## Review boundary

This is read-only synthetic evidence. Do not diagnose, recommend treatment, or clear the patient; the clearance decision and signature are the physician's. Never sign, file, or send the note or notify a team; protocol flags and the distribution list are drafts.
