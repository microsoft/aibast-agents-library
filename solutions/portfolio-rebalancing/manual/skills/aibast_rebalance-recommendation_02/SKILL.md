---
name: rebalance-recommendation
description: Use for rebalancing candidates questions in the Portfolio Rebalancing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Rebalancing candidates

Prepare nonbinding allocation-change evidence for licensed-advisor and client review. Retrieve the paired synthetic records and controls. Use the requested fictional portfolio, or the configured PORT-5001 default; never substitute another record for an unknown ID.

## Bind the quantities

The portfolio record's drift_threshold is the configured guardrail. A holding's drift is an observed percentage-point difference, not a threshold. For PORT-5001 the configured guardrail is 3.0%; VTI's observed gap is +5.0 percentage points. Equality with the configured absolute-drift threshold is flagged.

Use the canonical candidate table and totals for the scoped record. Preserve its exact dollar amounts; do not recompute them from rounded displayed percentages. If a requested calculation is not supplied, use the actual source holding value and target dollar value, explicitly label the calculation, and leave missing inputs unknown.

## Response shape

Return only these sections, in order:

1. Portfolio ID, name, total value, configured drift threshold and source citation.
2. Candidate table: asset, ticker, candidate action, current allocation, target allocation, observed drift in percentage points, and candidate dollar amount.
3. Total reduction candidates and total increase candidates.
4. Required human reviews: licensed-advisor suitability and client consent; qualified-tax review; compliance review; authorized-trading approval. These are pending requirements, not approvals.
5. The no-order statement and footer below.

The table is the client-review evidence. Do not append per-ticker discussion, a "what to discuss" essay, another drift ceiling, risk rankings, a funding conclusion, tax-benefit explanation or system recommendation. Maximum observed drift belongs to drift analysis, not a second limit in this candidate report.

No order has been created, routed, or executed.

End every substantive answer with exactly:

Synthetic portfolio evidence only; not investment, tax, legal, retirement, or financial advice. No order or transaction occurred. Licensed human review required.

## Locked example

Persona: Financial Advisor

Prompt: Show me the allocation changes I should review with the client before anyone trades.

Expected synthetic evidence: VTI, candidate.
