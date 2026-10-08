---
name: clinical-notes-summarizer-risk-factor-summary
description: Reproduce the deterministic Clinical Notes Agent risk factor summary workflow, which explains the source-recorded ASA class factors and risk calculators.
---
<!-- bic:source=blank -->
# Clinical Notes Agent — risk factor summary

## Locked persona prompt

`Explain his ASA class III and the factors behind it.`

Route semantically equivalent requests here without requiring an operation name or an identifier; the pre-op patient is John Martinez (Patient ID / MRN 78392).

## Source

Use both packaged knowledge files and the exact reference response for this workflow.

## Required output contract

`# ASA Class III Justification`; preserve `ASA Class III Justification`, `Goldman <1%`, `FEV1 68%` and every value, medication and status from the reference response.

## Review boundary

This is read-only synthetic evidence. Do not diagnose, recommend treatment, or clear the patient; the clearance decision and signature are the physician's. Never sign, file, or send the note or notify a team; protocol flags and the distribution list are drafts.
