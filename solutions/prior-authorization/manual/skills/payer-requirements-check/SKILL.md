---
name: prior-authorization-payer-requirements-check
description: Reproduce the deterministic Prior Authorization Agent payer requirements check workflow, which matches payer requirements for CPT 72148 to the documentation for utilization review.
---
<!-- bic:source=blank -->
# Prior Authorization Agent — payer requirements check

## Locked persona prompt

`Check Robert Chen's payer requirements for the lumbar MRI against his documentation.`

Route semantically equivalent requests here without requiring an operation name or an identifier; the demo patient is Robert Chen (PA-2024-892741) and the denied Medicare case is Michael Johnson (PA-2024-891977).

## Source

Use both packaged knowledge files and the exact reference response for this workflow.

## Required output contract

`# Insurance Requirements`; preserve `PT x6 weeks`, `Red flag screening`, `All required criteria met` and every identifier, value and status from the reference response.

## Review boundary

This is read-only synthetic evidence. Do not predict, grant, deny, submit, or change an authorization; never send a notification, post to Teams, or schedule anything. Packets, notifications and tracking plans are drafts for the coordinator.
