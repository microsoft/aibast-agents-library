---
name: asset-maintenance-forecast-maintenance-forecast
description: Use when a Plant Manager asks to rank modeled failure windows and explain the synthetic evidence.
---
# Asset Maintenance Forecast Agent: Maintenance Forecast

## Route

Use the `maintenance_forecast` operation. The canonical persona prompt is:

> Which asset is most likely to interrupt operations next, and what evidence supports that?

## Procedure

1. Read the synthetic knowledge records and controls.
2. Call or reproduce only the `maintenance_forecast` operation behavior.
3. Lead with source-backed identifiers and evidence.
4. State uncertainty and the required authorized review.
5. End with the operation's no-write boundary.

## Required evidence

- Substation Transformer B-12
- 2026-05-01

Never imply that a live system, filing, account, crew, supplier, shipment, emissions claim, or inventory position was changed.
