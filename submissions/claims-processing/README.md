# Claims Processing Agent

Automate claims processing workflows to deliver faster, consistent, and more compliant claim outcomes.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/claims-processing/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Claims Adjusters / Managers, SIU Teams, Operations Leaders
- **Industries:** Financial Services

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Process the incoming claims queue and identify which ones need immediate attention vs auto-adjudication.` | Claims intake triage |
| `What is missing from Jennifer Liu’s theft file before I can evaluate it?` | Claim-file readiness |
| `Yes, show me the fraud detection results and high-risk claims.` | SIU indicator review |
| `Show the policy-term estimates and state clearly whether any claim was approved or paid.` | Policy-term settlement estimate |
| `Yes, auto-adjudicate the eligible claims and show me the results.` | Auto-adjudication recommendations |
| `Yes, show me the metrics and where we can improve further.` | Processing metrics and improvements |
| `Yes, summarize everything we accomplished today.` | Session summary |

## What the agent does

- Classify and route claims instantly to automated or human workflows
- Flag suspected fraud early and generate SIU evidence packages
- Pre‑analyze complex claims and highlight missing documents
- Auto‑generate approval or denial recommendations aligned with guidelines

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_ClaimsProcessingPilot`) with instructions and a greeting that lists the sample prompts.
- 7 agent skills, one per operation:
  - `adjudication-review` - Use for claim-file readiness questions in the Claims Processing Agent synthetic pilot.
  - `auto-adjudication` - "Use when a claims manager asks something like \"Yes, auto-adjudicate the eligible claims and show me the results\""
  - `claim-intake` - Use for claims intake triage questions in the Claims Processing Agent synthetic pilot.
  - `fraud-flag` - Use for siu indicator review questions in the Claims Processing Agent synthetic pilot.
  - `processing-metrics` - "Use when a claims operations leader asks something like \"Yes, show me the metrics and where we can improve further\""
  - `session-summary` - "Use when a claims operations leader asks something like \"Yes, summarize everything we accomplished today\""
  - `settlement-recommendation` - Use for policy-term settlement estimate questions in the Claims Processing Agent synthetic pilot.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_claims-processing-controls-and-review.md`
  - `aibast_claims-processing-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Claims Processing Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Cut processing time dramatically with automated workflows
- Reduced fraud exposure with earlier detection and SIU referrals
- Accelerated adjudication with ready‑for‑review claim files
- Improved service quality with faster decisions and communications
- Increased operational capacity

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
