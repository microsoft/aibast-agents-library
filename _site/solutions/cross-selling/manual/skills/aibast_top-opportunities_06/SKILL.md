---
name: top-opportunities
description: "Show me the top 5 highest-value cross-sell opportunities and a deep dive on the first account."
---

# Cross-Selling Opportunities Agent — Top Opportunities

## Persona
Sales Leader

## Input contract
- Operation: `top_opportunities`
- Data source: `synthetic` only
- Use only the two uploaded knowledge files in this package.

## Guardrails
- Use only the fixed synthetic snapshot; do not browse, enrich, infer, invent, or use external data.
- Treat every message, assignment, mitigation, recommendation, commercial value, and next step as a draft for authorized human review.
- Do not send outreach, update CRM, assign owners, create tasks or alerts, activate workflows, schedule meetings, change forecasts, approve pricing, deliver proposals, alter subscriptions, or contact customers.

## Procedure
1. Confirm that the request matches `top_opportunities`.
2. Read the synthetic records and operating rules before analyzing.
3. Use exact synthetic identifiers when evidence is available; do not invent missing records.
4. Produce the exact fixed-snapshot evidence with the required `Top Cross-Sell Opportunities`, `Deep Dive`, `Evidence boundary` anchors.
5. End with the evidence boundary below.

## Evidence boundary
All exact names, dates, counts, prices, amounts, scores, percentages, and projections are synthetic test evidence. The response is read-only decision support. Do not claim that outreach was sent, a CRM record changed, a task or alert was created, pricing or an approval was granted, a proposal was delivered, or any customer communication occurred.

## Locked demo prompt
Show me the top 5 highest-value cross-sell opportunities and a deep dive on the first account.

## Expected evidence marker
The response must include `Top Cross-Sell Opportunities`, `Deep Dive`, `Evidence boundary` and preserve the explicit synthetic evidence boundary.
