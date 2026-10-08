---
name: engagement-plan
description: "Use for customer touchpoints and multi-channel engagement: email, EDI 856 ASN, supplier portal, follow-up call, monitoring and CRM note, all prepared and not sent."
---
# Multi-channel customer engagement

## Required knowledge

Use both uploaded files together:

- `aibast_order-status-communication-synthetic-records.md` — complete exact source records.
- `aibast_order-status-communication-review-rules.md` — locked-case routing, calculation rules, and exact deterministic outputs.

Do not browse, substitute live-looking facts, or invent missing records.

## Procedure

1. Route this request to `engagement_plan`.
2. Read the matching canonical output under **Exact deterministic operation outputs**.
3. Ground the answer in the complete source records and preserve exact identifiers,
   names, measurements, costs, dates, schedules, statuses, and headings needed by
   the question.
4. Separate source facts from derived synthetic analysis and recommendations.
5. State the required human approval and the external action that was not performed.
6. Label every exact value as synthetic pilot evidence, not a customer outcome.

## Locked validation case

- Persona: **Production Manager**
- Prompt: “Show the customer touchpoints planned for the E-Cars Corp delay across email, EDI, portal and the follow-up call.”
- Required deterministic evidence: `EDI 856 ASN`, `Today 2 PM EST`, `Ready to send`

## Authorization boundary

Never change an order, production schedule, shipment, sourcing decision, logistics action, or recovery plan. Never send email, EDI, portal, Teams, or any other customer communication. An approved communication tool and authorized sender are required.
