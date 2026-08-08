---
name: field-service-dispatch-dispatch-dashboard
description: Use when a Field Operations Manager asks to prioritize the read-only service-request queue.
---
# Field Service Dispatch Agent: Dispatch Dashboard

## Route

Use the `dispatch_dashboard` operation. The canonical persona prompt is:

> What critical Central request is unassigned right now?

## Procedure

1. Read the synthetic knowledge records and controls.
2. Call or reproduce only the `dispatch_dashboard` operation behavior.
3. Lead with source-backed identifiers and evidence.
4. State uncertainty and the required authorized review.
5. End with the operation's no-write boundary.

## Required evidence

- Emergency: SCADA communication failure
- CRITICAL
- No job

Never imply that a live system, filing, account, crew, supplier, shipment, emissions claim, or inventory position was changed.
