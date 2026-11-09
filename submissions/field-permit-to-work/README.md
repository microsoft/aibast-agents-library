# Field Permit to Work Agent

Keep every field permit safe and on time: draft the risk assessment, check the isolation plan against the live switching state, track sign-offs and crew briefings, and verify close-out, so no crew starts work on an unconfirmed isolation.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/field-permit-to-work/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Permit Coordinator, Authorized Person, Crew Lead, Operations Manager, Safety Auditor
- **Industries:** Energy and Utilities

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which work permits are waiting for today?` | Permit Coordinator: Daily permit queue |
| `Draft the risk assessment for the Cedar Hill transformer job.` | Permit Coordinator: Risk assessment draft |
| `Is the isolation for the Cedar Hill job actually in place?` | Authorized Person: Isolation check |
| `Where is the Cedar Hill permit in the sign-off chain, and will it be ready for the 11:00 start?` | Permit Coordinator: Sign-off route and timing |
| `Has the Cedar Hill crew acknowledged the briefing?` | Crew Lead: Crew briefing status |
| `The Cedar Hill crew has finished. Can we close the permit?` | Authorized Person: Permit clearance check |
| `How are we doing on permit safety this month?` | Operations Manager: Permit safety roll-up |
| `Is the Hilltop pole replacement request ready to raise a permit?` | Crew Lead: Work request check |
| `Has the control room confirmed the isolation for the Hilltop Line 3 job? Draft the crew notice.` | Permit Coordinator: Control room isolation confirmation |
| `Can my crew accept the Cedar Hill permit on site yet?` | Crew Lead: Permit acceptance readiness |
| `Pull the audit trail for the archived Riverside link box permit. Is anything missing?` | Safety Auditor: Archived permit audit trail |

## What the agent does

- Checks each work request before a permit is raised
- Drafts the risk assessment with hazards, controls and PPE
- Confirms the isolation with the control room before the crew accepts
- Reconciles close-out and rebuilds the signed audit trail

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_FieldPermitToWorkManualBuild`) with instructions and a greeting that lists the sample prompts.
- 11 agent skills, one per operation:
  - `acceptance-readiness` - Use when a crew lead asks whether the crew can accept the permit on site yet.
  - `audit-trail` - Use when someone asks for the audit trail or chain of custody of an archived permit.
  - `authorization-route` - Use when someone asks where a permit is in the sign-off chain and whether it will be ready on time.
  - `clearance-check` - Use when the crew has finished and someone asks whether the permit can be closed.
  - `crew-briefing` - Use when someone asks whether the crew has acknowledged the safety briefing.
  - `isolation-check` - Use when someone asks whether the isolation for a job is actually in place.
  - `isolation-confirmation` - Use when someone asks whether the control room has confirmed the isolation and wants the permit update and crew notice drafted.
  - `permit-queue` - Use when someone asks which permits are waiting today and what is blocking them.
  - `risk-assessment` - Use when someone asks to draft the hazards, controls, PPE and residual risk for a permit.
  - `safety-kpis` - Use when a manager asks how permit safety is performing this month.
  - `work-request-check` - Use when someone asks whether a new work request is complete enough to raise a permit.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_field-permit-to-work-rules-and-guardrails.md`
  - `aibast_field-permit-to-work-synthetic-records.md`
- 1 tools:
  - `Work IQ MCP Server` - 

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

This package declares these connections. Importing asks you to pick or create a connection for each; nothing is read until you do:

- Work IQ MCP (`shared_workiqmcp`)

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Field Permit to Work Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Every crew starts on a confirmed isolation
- Sign-offs are visible against each planned start
- Close-out and the permit record are complete and signed

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-30.
