---
name: trade-reporting-and-execution-surveillance
description: "Use for the breakdown of the transaction reporting issues, regulator-rejection, venue, LEI or timestamp questions."
---

<!-- bic:source=blank -->
# Trade reporting and execution surveillance

## Deterministic findings

- 24 transaction-report issues: Venue ID mismatch 11 (auto-fix, High), Counterparty LEI 8 (auto-fix, High), Timestamp format 4 (auto-fix, Medium), Manual review needed 1 (no auto-fix, Critical).
- Critical trade APX-2024-8847: counterparty LEI expired during settlement; client Standard National Bank; resolution is an updated LEI from the client.
- 23 trades can be amended in one batch, about 8 minutes, submitted only after authorized approval.

## Procedure

1. Lead with the category table and the critical trade.
2. Do not claim that every exception is a regulator rejection.
3. Label all values as synthetic; no correction or filing has occurred.
