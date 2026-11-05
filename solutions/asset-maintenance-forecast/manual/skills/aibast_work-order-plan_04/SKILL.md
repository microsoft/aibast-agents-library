---
name: asset-maintenance-forecast-work-order-plan
description: "Use when a Maintenance Planner asks to prepare the bundled low-wind-window maintenance plan as an approval-gated draft queue"
---
# Asset Maintenance Forecast Agent: Work Order Plan

## Route

Use the `work_order_plan` operation. The canonical persona prompt is:

> Draft the bundled maintenance plan for the at-risk turbines, but do not create any work orders.

## Procedure

1. Read the synthetic knowledge records and controls.
2. Call or reproduce only the `work_order_plan` operation behavior; it has demo defaults, so call it before asking anything.
3. Lead with source-backed identifiers and evidence; keep the operation's figures and tables.
4. State uncertainty and the required authorized review.
5. End with the operation's no-write boundary.

## Required evidence

- Bundled Maintenance Plan
- 258%
- No work order

Never imply that a live system, filing, account, crew, supplier, shipment, emissions claim, or inventory position was changed.
