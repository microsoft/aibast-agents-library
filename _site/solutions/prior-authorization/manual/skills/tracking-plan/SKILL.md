---
name: prior-authorization-tracking-plan
description: Reproduce the deterministic Prior Authorization Agent tracking plan workflow, which proposes status checks, notifications and escalation without scheduling or sending anything.
---
<!-- bic:source=blank -->
# Prior Authorization Agent — tracking plan

## Locked persona prompt

`Set up tracking for Robert Chen's authorization and plan to notify everyone when it is approved.`

Route semantically equivalent requests here without requiring an operation name or an identifier; the demo patient is Robert Chen (PA-2024-892741) and the denied Medicare case is Michael Johnson (PA-2024-891977).

## Source

Use both packaged knowledge files and the exact reference response for this workflow.

## Required output contract

`# Tracking and Notification Plan (Proposed)`; preserve `every 4 hours`, `48 hours`, `Teams channel post drafted` and every identifier, value and status from the reference response.

## Review boundary

This is read-only synthetic evidence. Do not predict, grant, deny, submit, or change an authorization; never send a notification, post to Teams, or schedule anything. Packets, notifications and tracking plans are drafts for the coordinator.
