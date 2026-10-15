---
name: regulatory-correction-and-submission-preparation
description: "Use to execute or stage the batch fix: prepare correction-report and new-submission payloads for authorized review, never transmitted."
---

<!-- bic:source=blank -->
# Regulatory correction and submission preparation

## Staged batch

| Issue type | Trades | Payload |
|---|---|---|
| Venue ID mismatch | 11 | correction report |
| Counterparty LEI | 8 | correction report |
| Timestamp format | 4 | correction report |

- 23 amendments staged for FCA submission via the firm's ARM; reporting entity Northgate Asset Management LLP, LEI `549300XKQZ2P4NLK7T18`.
- 1 trade pending: APX-2024-8847, Standard National Bank must supply an updated LEI; it then goes as a new submission.
- The same answer shows the Strategy #5 documentation gaps.

## Procedure

1. Mark the result as a synthetic dry run.
2. Require an authorized compliance reviewer to approve the payload before an authenticated ARM connector can transmit it.

Never claim that a correction was applied or a filing was sent.
