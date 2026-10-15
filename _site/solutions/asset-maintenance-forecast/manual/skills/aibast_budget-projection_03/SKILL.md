---
name: asset-maintenance-forecast-budget-projection
description: "Use when a Finance Business Partner asks to compare planned and emergency repair cost as a non-binding maintenance budget estimate"
---
# Asset Maintenance Forecast Agent: Budget Projection

## Route

Use the `budget_projection` operation. The canonical persona prompt is:

> What maintenance funding should I reserve for the at-risk turbines?

## Procedure

1. Read the synthetic knowledge records and controls.
2. Call or reproduce only the `budget_projection` operation behavior; it has demo defaults, so call it before asking anything.
3. Lead with source-backed identifiers and evidence; keep the operation's figures and tables.
4. State uncertainty and the required authorized review.
5. End with the operation's no-write boundary.

## Required evidence

- $70,200
- $227,000
- Synthetic planning estimate

Never imply that a live system, filing, account, crew, supplier, shipment, emissions claim, or inventory position was changed.
