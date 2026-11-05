---
name: asset-maintenance-forecast-asset-health
description: "Use when a Reliability Engineer asks to triage turbine risk scores without making a safety determination"
---
# Asset Maintenance Forecast Agent: Asset Health

## Route

Use the `asset_health` operation. The canonical persona prompt is:

> Show me the weakest turbine condition and whether this is an operating authorization.

## Procedure

1. Read the synthetic knowledge records and controls.
2. Call or reproduce only the `asset_health` operation behavior; it has demo defaults, so call it before asking anything.
3. Lead with source-backed identifiers and evidence; keep the operation's figures and tables.
4. State uncertainty and the required authorized review.
5. End with the operation's no-write boundary.

## Required evidence

- Unit 12
- CRITICAL
- not a safety determination

Never imply that a live system, filing, account, crew, supplier, shipment, emissions claim, or inventory position was changed.
