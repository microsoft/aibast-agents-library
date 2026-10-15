---
name: performance-dashboard
description: "Use for the order and customer performance dashboard: this order, 12-month account metrics, delay management effectiveness and lessons learned."
---
# Order and customer performance

## Required knowledge

Use both uploaded files together:

- `aibast_order-status-communication-synthetic-records.md` — complete exact source records.
- `aibast_order-status-communication-review-rules.md` — locked-case routing, calculation rules, and exact deterministic outputs.

Do not browse, substitute live-looking facts, or invent missing records.

## Procedure

1. Route this request to `performance_dashboard`.
2. Read the matching canonical output under **Exact deterministic operation outputs**.
3. Ground the answer in the complete source records and preserve exact identifiers,
   names, measurements, costs, dates, schedules, statuses, and headings needed by
   the question.
4. Separate source facts from derived synthetic analysis and recommendations.
5. State the required human approval and the external action that was not performed.
6. Label every exact value as synthetic pilot evidence, not a customer outcome.

## Locked validation case

- Persona: **Operations Leader**
- Prompt: “Show the performance dashboard for the E-Cars Corp account and this order.”
- Required deterministic evidence: `96.2%`, `$14.2M`, `Lessons learned`

## Authorization boundary

Never change an order, production schedule, shipment, sourcing decision, logistics action, or recovery plan. Never send email, EDI, portal, Teams, or any other customer communication. An approved communication tool and authorized sender are required.
