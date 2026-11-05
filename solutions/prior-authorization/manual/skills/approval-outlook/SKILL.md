---
name: prior-authorization-approval-outlook
description: Reproduce the deterministic Prior Authorization Agent approval outlook workflow, which lists documentation strengths, the historical approval rate and an appeal strategy without predicting an outcome.
---
<!-- bic:source=blank -->
# Prior Authorization Agent — approval outlook

## Locked persona prompt

`How strong is Robert Chen's lumbar MRI request, and what is our appeal strategy if it is denied?`

Route semantically equivalent requests here without requiring an operation name or an identifier; the demo patient is Robert Chen (PA-2024-892741) and the denied Medicare case is Michael Johnson (PA-2024-891977).

## Source

Use both packaged knowledge files and the exact reference response for this workflow.

## Required output contract

`# Approval Outlook and Appeal Strategy`; preserve `94% for similar cases`, `Peer-to-peer review with radiologist`, `Complete documentation package` and every identifier, value and status from the reference response.

## Review boundary

This is read-only synthetic evidence. Do not predict, grant, deny, submit, or change an authorization; never send a notification, post to Teams, or schedule anything. Packets, notifications and tracking plans are drafts for the coordinator.
