---
name: prior-authorization-submission-packet
description: Reproduce the deterministic Prior Authorization Agent submission packet workflow, which assembles the ready-to-submit packet and drafted notifications; never submits or sends.
---
<!-- bic:source=blank -->
# Prior Authorization Agent — submission packet

## Locked persona prompt

`Get Robert Chen's lumbar MRI authorization ready to submit and give me the confirmation details.`

Route semantically equivalent requests here without requiring an operation name or an identifier; the demo patient is Robert Chen (PA-2024-892741) and the denied Medicare case is Michael Johnson (PA-2024-891977).

## Source

Use both packaged knowledge files and the exact reference response for this workflow.

## Required output contract

`# Submission Packet — Ready for You to Submit`; preserve `PA-2024-892741`, `Case #4729183`, `Not submitted` and every identifier, value and status from the reference response.

## Review boundary

This is read-only synthetic evidence. Do not predict, grant, deny, submit, or change an authorization; never send a notification, post to Teams, or schedule anything. Packets, notifications and tracking plans are drafts for the coordinator.
