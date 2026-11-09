# Payments Operations Agent

Help payments operations teams clear the daily release queue faster by validating payments against scheme rules, planning exception repairs, reviewing pre-release risk, reconciling settlement accounts, and answering status questions with evidence, while every release decision stays with an authorized analyst.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/payments-operations/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Payments Operations Lead, Payments Analyst, Payments Repair Analyst, Reconciliation Analyst, Head of Payments Operations, Compliance Analyst, Treasury Analyst
- **Industries:** Financial Services, Banking

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What's in this morning's payment release queue, and which payments need attention?` | Payments Operations Lead: Release queue overview |
| `Why did payment PAY-3105 fail validation?` | Payments Analyst: Scheme-rule validation |
| `What's the repair plan for PAY-3105? Don't change anything yet.` | Payments Repair Analyst: Exception repair plan |
| `Is the 2.75 million dollar payment PAY-3104 to Wingtip Toys safe to release?` | Payments Analyst: Pre-release risk review |
| `Reconcile yesterday's USD settlement account. Which breaks are still open?` | Reconciliation Analyst: Settlement reconciliation |
| `A relationship manager is asking where PAY-3103 is. What should I tell them?` | Payments Operations Lead: Payment status answer |
| `Give me yesterday's payments KPI brief by rail.` | Head of Payments Operations: Daily payments KPI brief |
| `Which sanctions alerts should I review first, and what do I compare?` | Compliance Analyst: Sanctions review queue |
| `Are we close to any correspondent limits today, and do any nostro accounts need funding?` | Treasury Analyst: Correspondent limits and nostro funding |
| `PAY-3130 to Coho Winery was flagged. How should we verify it with the customer?` | Payments Analyst: Customer verification draft |

## What the agent does

- Validates payments against scheme rules and plans repairs
- Prepares sanctions alerts and verification calls
- Reconciles settlements and tracks nostro funding
- Answers payment status inquiries and builds the daily KPI brief by rail

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_PaymentsOperationsManualBuild`) with instructions and a greeting that lists the sample prompts.
- 10 agent skills, one per operation:
  - `correspondent-limits` - Use when someone asks about correspondent limit use, projected nostro balances, or a funding request for treasury.
  - `customer-verification` - Use when someone asks how to verify a flagged payment with the customer; the call goes to the contact on file and the analyst decides.
  - `daily-kpi-brief` - Use when leadership asks for volume, exceptions, and straight-through rate by rail plus today's open items.
  - `payment-status` - Use when someone asks where a payment is; returns the stage timeline, expected settlement, and a draft reply that is not sent.
  - `queue-overview` - Use when the payments lead asks what is in today's release queue, how payments are staged, or which payments need attention.
  - `reconcile-settlement` - Use when someone asks about settlement or nostro account matching, open breaks, or the net difference for the prior value date.
  - `release-risk-review` - Use when an analyst asks whether a large or unusual payment is safe to release; shows screening, risk score, and drivers while the analyst decides.
  - `repair-plan` - Use when an analyst asks how to fix a failed payment; returns a priority, repair steps, and a draft originator note that is never executed.
  - `sanctions-review-queue` - Use when a compliance analyst asks which sanctions alerts to review first and what evidence to compare; flags come from the screening service and the analyst decides.
  - `validate-payment` - Use when an analyst asks why a payment failed or passed validation against rail limits, currencies, account presence, and reference uniqueness.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_payments-operations-rules-and-guardrails.md`
  - `aibast_payments-operations-synthetic-records.md`
- 1 tools:
  - `Work IQ MCP Server` - 

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Payments Operations Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Faster triage: failed payments arrive with a repair plan
- Better releases: flags and evidence in one view
- Earlier break resolution: breaks are ranked by value before the cutoff

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-30.
