---
name: prior-authorization-denial-review
description: Reproduce the deterministic Prior Authorization Agent denial review workflow, which summarizes the recorded denial reason, missing elements and appeal actions without deciding the appeal.
---
<!-- bic:source=blank -->
# Prior Authorization Agent — denial review

## Locked persona prompt

`Why was the Medicare sleep study request denied, and where does the appeal stand?`

Route semantically equivalent requests here without requiring an operation name or an identifier; the demo patient is Robert Chen (PA-2024-892741) and the denied Medicare case is Michael Johnson (PA-2024-891977).

## Source

Use both packaged knowledge files and the exact reference response for this workflow.

## Required output contract

`# Denial Details`; preserve `Epworth Sleepiness Scale`, `tomorrow 2 PM`, `5 business days` and every identifier, value and status from the reference response.

## Review boundary

This is read-only synthetic evidence. Do not predict, grant, deny, submit, or change an authorization; never send a notification, post to Teams, or schedule anything. Packets, notifications and tracking plans are drafts for the coordinator.
