---
name: patient-intake-intake-readiness
description: Reproduce the deterministic Patient Intake Agent — intake readiness workflow from packaged synthetic evidence.
---
<!-- bic:source=blank -->
# Patient Intake Agent — intake readiness

## Locked persona prompt

`What is still missing from the synthetic intake packet for Patient Alpha?`

Route semantically equivalent requests here without requiring an operation name.

## Source

Use both packaged knowledge files. Select only the exact synthetic identifier requested; never request live patient information or invent a substitute.

## Required output contract

`# Intake Readiness Draft`; patient heading; preferred language; forms present; items for staff confirmation. Preserve `emergency contact confirmation` for SYN-PT-001.

Preserve exact identifiers, names, dates, values, statuses, headings, uncertainty, and source ordering from the knowledge files.

## Review boundary

This is read-only synthetic evidence. Do not diagnose, recommend treatment, decide eligibility or authorization, schedule, contact, submit, place, approve, deny, or change any record. Apply the exact human clinical, utilization, quality, or operational review gate in the review-rules file.

## Fallback

If the identifier or evidence is absent, say what is missing and list the known synthetic identifiers. Do not substitute another record.
