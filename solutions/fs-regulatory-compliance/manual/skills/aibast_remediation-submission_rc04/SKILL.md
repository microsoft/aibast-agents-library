---
name: regulatory-correction-and-submission-preparation
description: Use to stage source-backed corrections and prepare new or correction-report payloads for an Approved Reporting Mechanism.
---
<!-- bic:source=blank -->
# Regulatory correction and submission preparation

## Source-backed corrections

| Trade | Field | Staged value | Evidence |
|---|---|---|---|
| TRD-88117 | field 57 | `T-2041` | order-management record |
| TRD-88129 | field 36 | `XPAR` | verified execution-venue record |
| TRD-88133 | field 59 | `T-2107` | order-management record |
| TRD-88133 | field 7 | `549300XKQZ2P4NLK7T18` | reporting-entity record |
| TRD-88150 | field 36 | `XLON` | verified execution-venue record |

## Procedure

1. Prepare correction reports for TRD-88117, TRD-88129, and TRD-88150.
2. Prepare a new submission for TRD-88133.
3. Show each value and its evidence source.
4. Mark the entire result as a synthetic dry run.
5. Require an authorized compliance reviewer to approve the payload before an
   authenticated ARM connector can transmit it.

Never claim that a correction was applied or a filing was sent.
