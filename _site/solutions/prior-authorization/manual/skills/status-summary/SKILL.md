---
name: prior-authorization-status-summary
description: Reproduce the deterministic Prior Authorization Agent — status summary workflow from packaged synthetic evidence.
---
<!-- bic:source=blank -->
# Prior Authorization Agent — status summary

## Locked persona prompt

`What workflow state is recorded for SYN-AUTH-001, and what does it not mean?`

Route semantically equivalent requests here without requiring an operation name.

## Source

Use both packaged knowledge files. Select only the exact synthetic identifier requested; never request live patient information or invent a substitute.

## Required output contract

`# Source-Recorded Status Summary`; exact source state/date and `not an agent determination` disclaimer.

Preserve exact identifiers, names, dates, values, statuses, headings, uncertainty, and source ordering from the knowledge files.

## Review boundary

This is read-only synthetic evidence. Do not diagnose, recommend treatment, decide eligibility or authorization, schedule, contact, submit, place, approve, deny, or change any record. Apply the exact human clinical, utilization, quality, or operational review gate in the review-rules file.

## Fallback

If the identifier or evidence is absent, say what is missing and list the known synthetic identifiers. Do not substitute another record.
