# Sales Qualification Agent

Automate lead scoring and qualification to accelerate pipeline generation, improve conversion rates, and drive proactive sales.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/sales-qualification/quest.html), Microsoft's catalog of industry agent templates.

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which bundled synthetic leads should my team review first, and why did they score that way?` | Prioritize synthetic leads |
| `Show the BANT evidence and missing qualification details for the strongest synthetic leads.` | Review BANT evidence |
| `Draft outreach ideas for the synthetic hot leads, but do not send or schedule any communication.` | Draft outreach ideas |
| `Recommend synthetic lead routing for manager review without assigning CRM owners.` | Recommend lead routing |
| `Draft an SLA and escalation plan for the synthetic leads without activating alerts or automations.` | Draft the SLA plan |
| `Summarize the synthetic qualified pipeline and clearly label every conversion and value assumption.` | Summarize qualification evidence |

## What the agent does

- Enrich leads with firmographic, technographic, and intent data
- Score and segment leads using ICP and BANT criteria for prioritization
- Generate tailored outreach sequences and talking points
- Automate SLA tracking and alerts to ensure timely follow-up

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_SalesQualificationPilot`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `sales-qualification-assign-leads` - Recommend lead routing for manager review without assigning CRM owners.
  - `sales-qualification-bant-analysis` - Review BANT evidence for the top synthetic leads and surface missing qualification data.
  - `sales-qualification-create-outreach` - Draft outreach ideas for synthetic hot leads; do not send or schedule any communication.
  - `sales-qualification-qualification-report` - Summarize the synthetic qualified pipeline and recommended review actions without conversion claims.
  - `sales-qualification-score-leads` - Score and segment the bundled synthetic leads using the documented ICP model.
  - `sales-qualification-setup-tracking` - Draft an SLA tracking and escalation plan without activating alerts or automations.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_sales-qualification-operating-rules.md`
  - `aibast_sales-qualification-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Sales Qualification Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reduced lead qualification time from hours to minutes
- Increased lead-to-meeting conversion through personalized engagement
- Balanced workload across sales reps while maintaining SLAs
- Freed team capacity to focus on strategic, high-value opportunities

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
