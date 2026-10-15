---
name: prior-authorization-patient-auth-request
description: Reproduce the deterministic Prior Authorization Agent patient auth request workflow, which verifies the demo patient's request details (Robert Chen lumbar MRI) without submitting anything.
---
<!-- bic:source=blank -->
# Prior Authorization Agent — patient auth request

## Locked persona prompt

`Patient Robert Chen needs prior auth for a lumbar MRI ordered by Dr. Thompson for chronic back pain. Can you get the request ready?`

Route semantically equivalent requests here without requiring an operation name or an identifier; the demo patient is Robert Chen (PA-2024-892741) and the denied Medicare case is Michael Johnson (PA-2024-891977).

## Source

Use both packaged knowledge files and the exact reference response for this workflow.

## Required output contract

`# Prior Authorization Request`; preserve `MR-489327`, `72148`, `Dr. James Thompson` and every identifier, value and status from the reference response.

## Review boundary

This is read-only synthetic evidence. Do not predict, grant, deny, submit, or change an authorization; never send a notification, post to Teams, or schedule anything. Packets, notifications and tracking plans are drafts for the coordinator.
