---
name: clinical-notes-summarizer-cardiopulmonary-review
description: Reproduce the deterministic Clinical Notes Agent cardiopulmonary review workflow, which reports source-recorded cardiac and respiratory findings and labs.
---
<!-- bic:source=blank -->
# Clinical Notes Agent — cardiopulmonary review

## Locked persona prompt

`Show me his cardiac and respiratory status with recent testing.`

Route semantically equivalent requests here without requiring an operation name or an identifier; the pre-op patient is John Martinez (Patient ID / MRN 78392).

## Source

Use both packaged knowledge files and the exact reference response for this workflow.

## Required output contract

`# Cardiopulmonary Assessment`; preserve `82 bpm`, `FEV1 68%`, `eGFR 67` and every value, medication and status from the reference response.

## Review boundary

This is read-only synthetic evidence. Do not diagnose, recommend treatment, or clear the patient; the clearance decision and signature are the physician's. Never sign, file, or send the note or notify a team; protocol flags and the distribution list are drafts.
