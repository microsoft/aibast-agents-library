---
name: permit-license-management-application-status
description: "Use when a Environmental Counsel asks to track already-submitted applications read-only"
---
# Permit Management Agent: Application Status

## Route

Use the `application_status` operation. The canonical persona prompt is:

> Where does the Imperial Valley Solar Phase 2 application stand, and did we submit anything today?

## Procedure

1. Read the synthetic knowledge records and controls.
2. Call or reproduce only the `application_status` operation behavior; it has demo defaults, so call it before asking anything.
3. Lead with source-backed identifiers and evidence; keep the operation's figures and tables.
4. State uncertainty and the required authorized review.
5. End with the operation's no-write boundary.

## Required evidence

- APP-7102
- public_comment
- cannot submit

Never imply that a live system, filing, account, crew, supplier, shipment, emissions claim, or inventory position was changed.
