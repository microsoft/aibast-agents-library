---
name: synthetic-permit-fee-estimate
description: Use for permit cost, fee breakdown, or formula questions to calculate all seven synthetic fee categories from declared valuation and label the result as an estimate.
---
<!-- bic:source=blank -->
# Synthetic permit fee estimate

Use this skill for permit cost, fee estimate, breakdown, or formula
questions.

## Fixed formula

For every category:
`amount = base + (valuation / 1000) × rate`, rounded to cents.

Use all seven categories in schedule order: Plan Review, Building Permit,
Electrical, Plumbing, Mechanical, Fire Review, Technology Surcharge.
Their bases total $850 and rates total $19.25 per $1,000.

## Precomputed totals

- BP-2025-0101: $81,700.00
- BP-2025-0102: $4,411.25
- BP-2025-0103: $7,010.00
- BP-2025-0104: $131,750.00
- BP-2025-0105: $81,700.00
- BP-2025-0106: $11,245.00

## Output

Lead with the estimated total, then show the seven line items when the user
asks for a breakdown or how the total was calculated. For a hypothetical
valuation, apply the same formula and label it hypothetical. For an unknown
permit ID, ask for the valuation or list the known IDs; never silently
calculate all permits.

Always label the result a synthetic estimate from declared valuation, not
an invoice, charge, balance, or payment record. Never waive or alter a fee.
