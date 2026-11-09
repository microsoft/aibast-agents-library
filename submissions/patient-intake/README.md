# Patient Intake and Scheduling Agent

Automate patient intake workflows to streamline operations, protect revenue from avoidable losses, and deliver a smoother patient experience.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/patient-intake/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Front Desk Staff, Scheduling Coordinators, Patient Access Reps
- **Industries:** Healthcare

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What is still missing from the synthetic intake packet for Patient Alpha?` | Front Desk Staff: Intake Readiness |
| `What coverage evidence is recorded for Synthetic Patient Alpha, and what must staff still confirm?` | Patient Access Representative: Coverage Evidence |
| `Show the candidate source slots for Clinician A without booking anything.` | Scheduling Coordinator: Appointment Availability |
| `Prepare a pre-visit readiness summary for Synthetic Patient Alpha.` | Front Desk Staff: Pre Visit Summary |
| `New patient Sarah Martinez called requesting a neurology consultation for chronic migraines within the next two weeks; start her registration.` | Front Desk Staff: New Patient Intake |
| `Book Sarah Martinez for Tuesday at 2:30 and tell me which intake forms she needs.` | Scheduling Coordinator: Appointment Hold Draft |
| `Which forms go in Sarah Martinez's intake packet, and does it include HIPAA consent and medication history?` | Patient Access Representative: Intake Packet |
| `Recommend automated reminders for Sarah Martinez's visit to reduce no-shows.` | Scheduling Coordinator: Reminder Plan |

## What the agent does

- Verify insurance, referrals, and network status during patient intake
- Deliver tailored digital packets with all required pre‑visit forms
- Automate reminders across multiple scheduled touchpoints
- Ensure clinicians’ availability and readiness through up‑to‑date scheduling data

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_PatientIntakeandScheduling`) with instructions and a greeting that lists the sample prompts.
- 8 agent skills, one per operation:
  - `appointment-availability` - "Reproduce the deterministic Patient Intake Agent — appointment availability workflow from packaged synthetic evidence."
  - `appointment-hold-draft` - "Use when a scheduling coordinator asks something like \"Book Sarah Martinez for Tuesday at 230 and tell me which intake forms she needs\""
  - `coverage-evidence` - "Reproduce the deterministic Patient Intake Agent — coverage evidence workflow from packaged synthetic evidence."
  - `intake-packet` - "Use when a patient access representative asks something like \"Which forms go in Sarah Martinez's intake packet, and does it include HIPAA consent and medication history\""
  - `intake-readiness` - "Reproduce the deterministic Patient Intake Agent — intake readiness workflow from packaged synthetic evidence."
  - `new-patient-intake` - "Use when a front desk staff asks something like \"New patient Sarah Martinez called requesting a neurology consultation for chronic migraines within the next two weeks; start her registration\""
  - `pre-visit-summary` - "Reproduce the deterministic Patient Intake Agent — pre-visit summary workflow from packaged synthetic evidence."
  - `reminder-plan` - "Use when a scheduling coordinator asks something like \"Recommend automated reminders for Sarah Martinez's visit to reduce no-shows\""
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_patient-intake-review-rules.md`
  - `aibast_patient-intake-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Patient Intake and Scheduling Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reduced no‑shows with automated reminders, avoiding lost revenue
- Improved visit readiness by resolving eligibility and referral requirements upfront
- Streamlined digital intake, reducing manual data entry and wait‑times
- Freed staff capacity by automating routine scheduling, verification, and follow‑up tasks

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
