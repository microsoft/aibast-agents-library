---
name: purchase-request
description: Use when a procurement manager asks for request context and the applicable approval level.
---
<!-- bic:source=blank -->
# Purchase-request review

Use when a procurement manager asks for request context and the applicable approval level.

## Procedure

1. Use this uploaded `purchase-request` skill with
   `aibast_procurement-agent-synthetic-records.md` and
   `aibast_procurement-agent-rules-and-guardrails.md`. Retrieve and cite both.
   The default cloud-upgrade record is `PR-5001`; do not substitute it for a
   different explicitly requested but missing record.
2. Read the request fields and quote its source-recorded justification without
   treating it as independently verified. Read the category snapshot and
   approval thresholds; keep their values unchanged.
3. Choose the first threshold whose inclusive upper bound covers the request
   amount. Retain its cap and the `Unlimited` / `CEO + Board` tier.
   Do not invent dollar-only lower bounds or serial approval chains.
   The SLA is a source label, not evidence that a review clock or approval started.
   It is not a promise of approval.
   Do not invent an approver for unspecified spend.
4. The snapshot has no request-to-commitment mapping. Finance reconciliation
   must establish whether a request is already included in commitments.
   Do not infer inclusion from matching amounts or request status.
   Do not calculate hypothetical revised balances or utilization, or assert
   incremental budget effects without that mapping. Do not present a
   request-to-availability ratio as incremental consumption.
5. Preserve existing budget exceptions. Technology is already `At Risk`;
   report its recorded utilization and availability, not an unbreached starting
   condition or a revised balance. Identify the unresolved human reviews in
   the common rules, including Finance reconciliation, before any human action.

## Required response contract

Use these headings in order, with exact wording and capitalization. Populate
each section from the retrieved source; never output unfilled placeholders.
For `PR-5001`, the title is exactly `Purchase Request Review: PR-5001`.

```text
# Purchase Request Review: {request_id}
## Justification
## Approval gate
```

- Under the title, include a request table with ID, title, requester,
  department, category, amount, priority, status, preferred vendor and budget
  code. Under `Justification`, quote the recorded justification.
- Under `Approval gate`, show the selected approver, inclusive amount cap and
  source SLA for the request amount.
  The selected approver must review and decide; do not promise approval.
  Include the unchanged category budget, spent YTD, committed, available,
  utilization and status and the unknown request inclusion. Use the mandatory
  paragraph below for the complete unresolved human-review set.
- Before sending, check the literal heading is `Approval gate` (lowercase `g`),
  not `Approval Gate`. Do not title-case or rename it.

## Deterministic pilot evidence

- `PR-5001`
- `$125,000`
- `CFO`

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
