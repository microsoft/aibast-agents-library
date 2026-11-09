# Time Entry and Billing Agent

Automate month-end billing cycles to accelerate invoicing, reduce risk, and ensure audit-ready compliance.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/time-entry-billing/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Finance VP, Billing Manager
- **Industries:** Professional Services, Consulting

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What billable work is still blocked from this close, and what has to happen before it can move?` | Find close blockers |
| `Give me the month-end billing rollup by project and consultant without treating it as posted revenue.` | Review the billing rollup |
| `Which time cards would fail our billing review because of narrative, hours, rate, or budget concerns?` | Audit time cards |
| `Prepare the invoice support that is actually ready, and keep anything without the right approval or milestone evidence out.` | Prepare eligible invoice support |
| `What evidence is missing on the disputed hours, and what is the safest resolution path before we go back to the clients?` | Resolve disputed-hour evidence |

## What the agent does

- Validate time entries/billing rules and generate invoices
- Complete missing descriptions and classify billable hours
- Flag disputed hours, premium billing, and budget overruns
- Generate CFO-ready revenue recognition reports and audit trails

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_TimeEntryandBillingPilot`) with instructions and a greeting that lists the sample prompts.
- 9 agent skills, one per operation:
  - `approval-gated-invoice-support` - Prepares fictional T&M support while holding unapproved and fixed-fee work.
  - `billing-close-summary` - Produces project and consultant rollups from the synthetic ledger.
  - `budget-overruns` - "Use when a finance vice president asks something like \"Show me the budget overruns and write-off exposure\""
  - `disputed-hours-evidence-brief` - Explains evidence gaps and approval paths for fictional disputes.
  - `final-invoices` - "Use when a billing manager asks something like \"Bill RetailCo $15K, approve everything else, and generate the final invoices and revenue report\""
  - `flagged-review` - "Use when a billing manager asks something like \"Break down the hours that were flagged for review before final approval\""
  - `month-end-billing-blockers` - Finds fictional billable work blocked from invoice preparation.
  - `month-end-close` - "Use when a finance vice president asks something like \"Month-end close is here. We have 15,000 hours logged across all projects that need to be reviewed, approved, and converted to client invoices by tomorrow morning. Can you process the full billing cycle\""
  - `time-entry-audit` - Flags narrative, hours, rate, approval, and budget issues.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_billing-rules-and-disputes.md`
  - `aibast_billing-synthetic-ledger.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Time Entry and Billing Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reduced billing cycles from multi-day process to minutes
- Achieved a higher billable rate via accurate classification
- Protected revenue by recovering disputed hours and preventing leakage
- Delivered audit-ready invoices and compliance documentation

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
