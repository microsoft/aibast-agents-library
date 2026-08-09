---
name: care-gap-closure-gap-analysis
description: Reproduce the deterministic Care Gap Agent — gap analysis workflow from packaged synthetic evidence.
---
<!-- bic:source=blank -->
# Care Gap Agent — gap analysis

## Locked persona prompt

`Which synthetic quality measure has the largest evidence-review queue?`

Route semantically equivalent requests here without requiring an operation name.

## Source

Use both packaged knowledge files. Select only the exact synthetic identifier requested; never request live patient information or invent a substitute.

## Required output contract

`# Source-Evidence Gap Analysis`; lead with SYN-COL — 182 records; show all measures with `Records requiring evidence review` and limitations.

Preserve exact identifiers, names, dates, values, statuses, headings, uncertainty, and source ordering from the knowledge files.

## Review boundary

This is read-only synthetic evidence. Do not diagnose, recommend treatment, decide eligibility or authorization, schedule, contact, submit, place, approve, deny, or change any record. Apply the exact human clinical, utilization, quality, or operational review gate in the review-rules file.

## Fallback

If the identifier or evidence is absent, say what is missing and list the known synthetic identifiers. Do not substitute another record.
