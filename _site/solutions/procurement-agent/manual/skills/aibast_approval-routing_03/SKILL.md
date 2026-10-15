---
name: approval-routing
description: Use when a department approver asks which authorization threshold applies to a request.
---
<!-- bic:source=blank -->
# Approval-path recommendation

Use when a department approver asks which authorization threshold applies to a request.

## Procedure

1. Use only the uploaded synthetic records and rules.
2. Lead with the specific evidence that answers the persona's question.
3. Explain uncertainty, prerequisites, and the authorized review needed next.
4. State that the result is synthetic decision support and that no external action occurred.

## Deterministic pilot evidence

- `PR-5001`
- `CFO`
- `does not record an approval`

## Safety gate

Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a transaction. Stop at a reviewable brief or draft.

## Required response contract

Use this uploaded `approval-routing` skill with
`aibast_procurement-agent-synthetic-records.md` and
`aibast_procurement-agent-rules-and-guardrails.md`. Retrieve and cite both.
The default infrastructure record is `PR-5001`; do not substitute it for a
different explicitly requested but missing record.

Choose the first threshold whose inclusive upper bound covers the request
amount. Retain its cap and the `Unlimited` / `CEO + Board` tier.
Do not invent dollar-only lower bounds or serial approval chains.
The SLA is a source label, not evidence that a review clock or approval started.
It is not a promise of approval.
Do not invent an approver for unspecified spend.
Keep recorded request status unchanged; do not infer budget clearance, request
inclusion in commitments or completed reviews. Follow the rules' reconciliation
and inference limits.

Use these headings in order, with exact wording and capitalization. Populate
each section from the retrieved source; do not replace the table with prose.
For `PR-5001`, the title is exactly `Approval Routing: PR-5001`.

```text
# Approval Routing: {request_id}
## Approval Thresholds
```

- Include the request amount, selected tier with its inclusive amount cap and SLA
  in the request-specific section (`CFO`, `$500,000` and `48 hours` for `PR-5001`).
  The selected approver must review and decide; do not promise approval.
- Under `Approval Thresholds`, include all five source threshold rows in source
  order with columns `Amount up to and including`, `Required approver` and
  `Approval SLA`, including `Unlimited` / `CEO + Board`.
- Before the final footer, include exactly:
  `This recommendation does not record an approval.`
  Use the mandatory paragraph below for the complete unresolved human-review set.

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
