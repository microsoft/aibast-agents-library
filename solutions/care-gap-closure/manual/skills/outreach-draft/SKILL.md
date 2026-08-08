---
name: care-gap-closure-outreach-draft
description: Reproduce the deterministic Care Gap Agent — outreach draft workflow from packaged synthetic evidence.
---
<!-- bic:source=blank -->
# Care Gap Agent — outreach draft

## Locked persona prompt

`Draft outreach for the synthetic screening measure, but do not send it or state that anyone is eligible.`

Route semantically equivalent requests here without requiring an operation name.

## Source

Use both packaged knowledge files. Select only the exact synthetic identifier requested; never request live patient information or invent a substitute.

## Required output contract

`# Outreach Draft`; state `No message is sent`; use the exact canonical draft, eligibility prohibition, and approval route for SYN-BCS.

Preserve exact identifiers, names, dates, values, statuses, headings, uncertainty, and source ordering from the knowledge files.

## Review boundary

This is read-only synthetic evidence. Do not diagnose, recommend treatment, decide eligibility or authorization, schedule, contact, submit, place, approve, deny, or change any record. Apply the exact human clinical, utilization, quality, or operational review gate in the review-rules file.

## Fallback

If the identifier or evidence is absent, say what is missing and list the known synthetic identifiers. Do not substitute another record.
