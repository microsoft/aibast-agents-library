---
name: validate-payment
description: "Use when an analyst asks why a payment failed or passed validation against rail limits, currencies, account presence, and reference uniqueness."
---
# Scheme-rule validation

Use when an analyst asks why a payment failed or passed validation against rail limits, currencies, account presence, and reference uniqueness.

## Procedure

1. Use only the uploaded synthetic records and rules.
2. Lead with the specific evidence that answers the persona's question.
3. Keep the figures, identifiers, and tables exactly as recorded for case `PO-02`.
4. Explain uncertainty, prerequisites, and the authorized review needed next.
5. State that the result is synthetic decision support and that no external action occurred.

## Deterministic pilot evidence

- `AMOUNT_OVER_RAIL_LIMIT`
- `BENEFICIARY_ACCOUNT_MISSING`
- `Scheme Rule`

## Safety gate

Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a transaction. Stop at a reviewable brief or draft.
