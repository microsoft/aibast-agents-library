---
name: risk-dashboard
description: Use for total spend, elevated-risk spend, ranked supplier risk, composite health, and incident counts.
---
# Supplier risk dashboard

## Required knowledge

Use both uploaded files together:

- `aibast_supplier-risk-monitoring-synthetic-records.md` — complete exact source records.
- `aibast_supplier-risk-monitoring-review-rules.md` — locked-case routing, calculation rules, and exact deterministic outputs.

Do not browse, substitute live-looking facts, or invent missing records.

## Procedure

1. Route this request to `risk_dashboard`.
2. Read the matching canonical output under **Exact deterministic operation outputs**.
3. Ground the answer in the complete source records and preserve exact identifiers,
   names, measurements, costs, dates, schedules, statuses, and headings needed by
   the question.
4. Separate source facts from derived synthetic analysis and recommendations.
5. State the required human approval and the external action that was not performed.
6. Label every exact value as synthetic pilot evidence, not a customer outcome.

## Locked validation case

- Persona: **Supply Chain Director**
- Prompt: “Where is supplier exposure concentrated, and which relationships should leadership review first?”
- Required deterministic evidence: `TechnoCore Semiconductor`, `CRITICAL`

## Authorization boundary

Never contact a supplier, change an allocation, qualify or disqualify a supplier, select or award a supplier, execute a contract, place an order, or approve sourcing. Authorized procurement owners must use approved procurement and supplier-management tools for any action.
