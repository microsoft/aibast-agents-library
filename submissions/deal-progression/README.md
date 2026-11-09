# Deal Progression Agent

Automate sales pipeline management to keep deals moving, increase forecast confidence, and improve team productivity.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/deal-progression/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Account Executive, Sales Director
- **Industries:** Cross-Industry

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which opportunities need attention in the synthetic pipeline, and what evidence should I review before changing the forecast?` | Review pipeline health |
| `What blocker evidence explains the loss of momentum on our two largest stalled synthetic deals?` | Diagnose stalled deals |
| `Draft reviewable intervention plans for our two largest stalled synthetic deals, but do not assign work or contact anyone.` | Draft intervention plans |
| `Which synthetic timing options could move pipeline review forward without turning scenario value into a forecast commitment?` | Compare acceleration options |
| `Map candidate follow-up work to the synthetic rep capacity for my review; do not create tasks or alerts.` | Map candidate tasks |
| `Give me a leadership-ready summary of the synthetic pipeline findings and the decisions that still require human review.` | Prepare the leadership summary |

## What the agent does

- Get a real-time pipeline assessment
- Identify stalled deals, then run gap analysis and stakeholder tracking
- Diagnose the exact blockers to deal momentum like legal delays
- Generate tailored action plans with tasks, deadlines, and talk tracks for each stalled opportunity

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_DealProgressionPilot`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `deal-progression-acceleration` - Compare synthetic acceleration options and clearly separate scenario value from forecast commitments.
  - `deal-progression-action-plans` - Draft reviewable action plans for the synthetic stalled deals; do not assign tasks.
  - `deal-progression-assign-tasks` - Prepare a draft task-mapping plan for manager review; do not create assignments or alerts.
  - `deal-progression-executive-summary` - Summarize the synthetic pipeline analysis and draft next steps for a leadership review.
  - `deal-progression-pipeline-health` - Review the synthetic pipeline and show which opportunities need attention without changing the forecast.
  - `deal-progression-stalled-deals` - Diagnose the synthetic stalled deals and show the evidence behind each blocker.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_deal-progression-operating-rules.md`
  - `aibast_deal-progression-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Deal Progression Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Protected their pipeline health, reducing at-risk deals
- Accelerated deal momentum with shorter sales cycles
- Improved forecast confidence    and reduced slippage
- Reduced hours of manual review, enabling managers to focus on high-impact opportunities

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
