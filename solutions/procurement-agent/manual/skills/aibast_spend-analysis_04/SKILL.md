---
name: spend-analysis
description: Use when a finance director asks which synthetic category is over budget or approaching a limit.
---
<!-- bic:source=blank -->
# Spend and budget review

Use when a finance director asks which synthetic category is over budget or approaching a limit.

## Procedure

1. Use this uploaded `spend-analysis` skill with
   `aibast_procurement-agent-synthetic-records.md` and
   `aibast_procurement-agent-rules-and-guardrails.md`. Retrieve and cite both.
2. Use `available = budget - spent YTD - committed`. Sum all category balances
   once, including negative values. Never subtract a category deficit again.
   Reconcile this with total budget minus total spent YTD minus total committed.
   Category balances are not freely transferable.
3. Use `(spent YTD + committed) / budget` for utilization and the rules'
   status thresholds. Preserve existing budget exceptions. Technology is already
   `At Risk`; Software is `Over Budget`. Keep the snapshot unchanged.
4. The snapshot has no request-to-commitment mapping. Finance reconciliation
   must establish whether a request is already included in commitments.
   Do not infer inclusion from matching amounts or request status.
   Do not calculate hypothetical revised balances or utilization, or assert
   incremental budget effects without that mapping. Do not introduce
   request-specific projections or attribute a category deficit to a request.
5. Do not invent periods, causal mappings or executed/reversible statuses.
   Report recorded trends only; do not extrapolate a quarter or forecast.
6. For amount-based human review of a source-backed request amount, use the rule:
   Choose the first threshold whose inclusive upper bound covers the request
   amount. Retain its cap and the `Unlimited` / `CEO + Board` tier.
   Do not invent dollar-only lower bounds or serial approval chains.
   The selected approver must review and decide; do not promise approval.
   Do not invent an approver for unspecified spend.
   The SLA is a source label, not evidence that a review clock or approval started.
   It is not a promise of approval.

## Required response contract

Use these headings in order, with exact wording and capitalization. Populate
each section from the retrieved source; do not replace the tables with prose.

```text
# Spend Analysis
## By Category
## Alerts
```

- Under `Spend Analysis`, include a portfolio totals table with Total budget,
  Spent YTD, Committed and Available, preserving the source amounts and labels.
- Under `By Category`, include all five source category rows in source order:
  Technology, Software, Office Supplies, Professional Services and Travel.
  Keep all columns: Category, Budget, Spent YTD, Committed, Available,
  Utilization, Status and Trend.
- Under `Alerts`, retain the existing exceptions and their source-backed
  amounts, including exactly `Software category over budget by $60,000` for
  this snapshot. Explain the inclusion and transfer limits. For a specified
  request amount, identify its source-threshold reviewer here; otherwise do not
  name one. Use the mandatory paragraph below for the complete unresolved
  human-review set.
- Before the final footer, include exactly `No purchase order is created.`

## Deterministic pilot evidence

- `Software`
- `$60,000`
- `No purchase order is created`

## Safety gate

Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a transaction. Stop at a reviewable brief or draft.
Retain the global policy's exact terminal safety footer verbatim.

## Mandatory human-review paragraph

Copy this paragraph verbatim once in every final answer, after all case-specific
content and citations, immediately before the final safety footer. Never shorten,
split, paraphrase or duplicate it. These controls are unresolved in this review,
not a serial chain or a denial of recorded historical statuses.

Required human reviews remain unresolved: Finance for budget validation and reconciliation; procurement for request and supplier review; legal, security, competition, supplier diversity, conflicts of interest, business-owner, delegated-authority and explicit publication review by the corresponding authorized owners.

## Shared final footer

End every response with this exact final standalone paragraph, once.
Put case-specific boundaries and citations before this footer; append nothing
after it.

Synthetic procurement evidence; decision support only. No approval, supplier action, purchase order, or spend commitment occurred.
