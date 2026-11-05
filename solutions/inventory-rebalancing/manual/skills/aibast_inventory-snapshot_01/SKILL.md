---
name: aibast-inventory-snapshot
description: Use when a supply chain manager asks where capacity, stock, and reorder exposure need attention.
---
<!-- bic:source=blank -->
# Inventory snapshot

## Use

Use when the user asks a capacity- or stock-level question in their own
language. Route the exact locked persona prompt "Which distribution centers are tight on space, and which SKU positions should my team review first?" here. Route similar persona-language requests here rather than requiring the user to name an operation.

## Required inputs

None required. If the user names a specific facility or SKU, scope the
summary to it; otherwise summarize all four facilities and all six SKUs
from the synthetic snapshot knowledge source.

## Clarifying questions

- If the request is ambiguous between a facility-level utilization view and
  a SKU-level reorder view, ask which the user wants — or provide both if
  the request is broad (e.g. "which SKU positions should my team review").
- If the user asks about a facility or SKU not present in the synthetic
  snapshot, say so instead of guessing.

## Procedure

1. Use only the facility-and-SKU synthetic snapshot knowledge source. Do not
   invent or browse for additional facilities, SKUs, or figures.
2. Summarize facility utilization (name, region, capacity used vs. total,
   utilization %) and flag any facility above 90% utilization as a
   facility-pressure review priority — name it explicitly, e.g. "Dallas
   Fulfillment Center" at its synthetic utilization level.
3. Summarize SKU on-hand levels across all four facilities and flag any SKU
   that is below its fixed synthetic reorder point at a given facility,
   citing the SKU identifier explicitly (e.g. `SKU-4406`).
4. Cite the stable synthetic identifiers (facility names/IDs, SKU IDs) that
   support each conclusion.
5. Separate observed evidence (the snapshot numbers) from any recommendation
   (which positions to review first) and from the required authorization
   gate for any follow-on action.
6. State plainly that every figure is synthetic pilot evidence from a fixed
   snapshot, not a live ERP or warehouse-management query.

## Output

A concise facility-utilization summary plus a SKU-level reorder-exposure
summary, each citing specific facility and SKU identifiers, ending with a
one-line note on which positions deserve first review and a reminder that
this is a fixed synthetic snapshot.

## Safety boundary (no side effects)

This skill only reads and summarizes the synthetic snapshot. It never
reserves, picks, ships, reorders, or otherwise moves inventory, and it never
changes a reorder point or other inventory policy. Any follow-on action
requires an authorized ERP/WMS system owner and an approved production
tool — state this whenever the summary implies next steps.

## Assumptions

- The synthetic snapshot is fixed and does not reflect real-time conditions.
- "Tight on space" means utilization approaching or above the facility's
  synthetic capacity, not a live available-to-promise signal.
