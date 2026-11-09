# Prior Authorization Agent

Automate insurance approval workflows to accelerate authorization processes, improve documentation accuracy, and reduce care delays.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/prior-authorization/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Utilization Management Coordinators, Nurse Case Managers, Radiology Schedulers
- **Industries:** Healthcare, Financial Services

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What evidence is present or missing for synthetic request SYN-AUTH-001?` | Inventory request evidence |
| `Show the synthetic criteria checklist for SYN-AUTH-001 without deciding medical necessity.` | Crosswalk the policy checklist |
| `What workflow state is recorded for SYN-AUTH-001, and what does it not mean?` | Read the recorded status |
| `Prepare a minimum-necessary reconsideration evidence outline for SYN-AUTH-001.` | Prepare review material |

## What the agent does

- Pull payer‑specific requirements and match them with EHR data
- Compile the full clinical evidence packet needed for medical review
- Submit requests directly to payer portals and send real‑time updates
- Flag cases requiring additional documentation and prepare appeal materials proactively

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_PriorAuthorizationPilot`) with instructions and a greeting that lists the sample prompts.
- 11 agent skills, one per operation:
  - `prior-authorization-appeal-evidence-packet` - Prepares a minimum-necessary outline without filing or recommending an appeal.
  - `prior-authorization-approval-outlook` - Reproduce the deterministic Prior Authorization Agent approval outlook workflow, which lists documentation strengths, the historical approval rate and an appeal strategy without predicting an outcome.
  - `prior-authorization-criteria-evidence` - Presents synthetic checklist items for qualified utilization review.
  - `prior-authorization-denial-review` - Reproduce the deterministic Prior Authorization Agent denial review workflow, which summarizes the recorded denial reason, missing elements and appeal actions without deciding the appeal.
  - `prior-authorization-patient-auth-request` - Reproduce the deterministic Prior Authorization Agent patient auth request workflow, which verifies the demo patient's request details (Robert Chen lumbar MRI) without submitting anything.
  - `prior-authorization-payer-requirements-check` - Reproduce the deterministic Prior Authorization Agent payer requirements check workflow, which matches payer requirements for CPT 72148 to the documentation for utilization review.
  - `prior-authorization-portfolio-status` - Reproduce the deterministic Prior Authorization Agent portfolio status workflow, which lists the five demo authorizations and portfolio metrics as source-recorded statuses.
  - `prior-authorization-request-evidence` - Inventories synthetic request evidence without submitting or deciding the request.
  - `prior-authorization-status-summary` - Transcribes a synthetic workflow state without making an authorization outcome.
  - `prior-authorization-submission-packet` - Reproduce the deterministic Prior Authorization Agent submission packet workflow, which assembles the ready-to-submit packet and drafted notifications; never submits or sends.
  - `prior-authorization-tracking-plan` - Reproduce the deterministic Prior Authorization Agent tracking plan workflow, which proposes status checks, notifications and escalation without scheduling or sending anything.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_prior-authorization-review-rules.md`
  - `aibast_prior-authorization-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Prior Authorization Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Completed authorizations faster by relying on fewer manual steps
- Met payer criteria consistently, reducing denials
- Received timely notifications, enabling earlier appointment booking
- Gained clear visibility into authorization progress, reducing anxiety and delays

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
