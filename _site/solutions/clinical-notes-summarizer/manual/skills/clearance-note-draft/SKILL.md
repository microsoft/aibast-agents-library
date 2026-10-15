---
name: clinical-notes-summarizer-clearance-note-draft
description: Reproduce the deterministic Clinical Notes Agent clearance note draft workflow, which assembles a draft clearance note and proposed distribution for physician signature; never signs, files or sends.
---
<!-- bic:source=blank -->
# Clinical Notes Agent — clearance note draft

## Locked persona prompt

`Generate the clearance note and send it to ophthalmology.`

Route semantically equivalent requests here without requiring an operation name or an identifier; the pre-op patient is John Martinez (Patient ID / MRN 78392).

## Source

Use both packaged knowledge files and the exact reference response for this workflow.

## Required output contract

`# Pre-Operative Clearance Note - Draft`; preserve `Dr. Amanda Chen`, `Draft ready for physician e-signature`, `nothing was sent` and every value, medication and status from the reference response.

## Review boundary

This is read-only synthetic evidence. Do not diagnose, recommend treatment, or clear the patient; the clearance decision and signature are the physician's. Never sign, file, or send the note or notify a team; protocol flags and the distribution list are drafts.
