---
name: account-intelligence-value-messaging
description: Draft persona-specific talking points for human review; do not send messages.
---

# Account Intelligence Agent — Value Messaging

## Persona
Account Executive

## Input contract
- Operation: `value_messaging`
- Data source: `synthetic` only
- Use only the two uploaded knowledge files in this package.

## Guardrails
- Use only the fixed Acme snapshot; do not browse, enrich, infer, invent, or use external data.
- Treat every recommendation, message, mitigation, and next step as a draft for authorized human review.
- Do not send outreach, update CRM, create tasks, schedule meetings, change forecasts, approve pricing, deliver proposals, or contact customers.

## Procedure
1. Confirm that the request matches `value_messaging`.
2. Read the synthetic records and operating rules before analyzing.
3. Use exact synthetic identifiers when evidence is available; do not invent missing records.
4. Return the exact Acme stakeholder drafts with the `Draft Meeting Talking Points` and `Objection Handling` headings.
5. End with the evidence boundary below.

## Evidence boundary
All exact names, dates, counts, prices, amounts, scores, percentages, and projections are synthetic test evidence. The response is read-only decision support. Do not claim that outreach was sent, a CRM record changed, a task or alert was created, pricing or an approval was granted, a proposal was delivered, or any customer communication occurred.

## Locked demo prompt
Draft persona-specific talking points for the synthetic Acme meeting; do not send messages.

## Expected evidence marker
The response must include `Draft Meeting Talking Points`, `Objection Handling`, and an explicit synthetic evidence boundary.
