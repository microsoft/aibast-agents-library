# Clinical Notes Summarizer Agent

Transform complex clinical histories into clear, actionable summaries for faster decision-making, better coordination, and safer care.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/clinical-notes-summarizer/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Primary care physicians, Surgeons, Anesthesia teams
- **Industries:** Healthcare

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Summarize synthetic encounter SYN-ENC-001 using source facts only.` | Summarize the source encounter |
| `List the source-recorded medications for SYN-ENC-001 for reconciliation.` | Inventory recorded medications |
| `Extract the source-coded problems for SYN-ENC-001 without confirming a diagnosis.` | Extract the problem list |
| `What referral context is recorded for SYN-ENC-001, and what action has not occurred?` | Review referral context |

## What the agent does

- Automatically generate concise, clinically relevant patient summaries
- Surface key risks, comorbidities, and medication considerations
- Standardize documentation to support smoother surgical and anesthesia workflows
- Send summaries through EHR and secure messaging systems

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_ClinicalNotesSummarizerPilo`) with instructions and a greeting that lists the sample prompts.
- 4 agent skills, one per operation:
  - `clinical-notes-summarizer-encounter-summary` - Extracts synthetic encounter facts without clinical inference.
  - `clinical-notes-summarizer-medication-inventory` - Lists source-recorded synthetic medications for clinician or pharmacist reconciliation.
  - `clinical-notes-summarizer-problem-list-extract` - Extracts source-coded problems without confirming or changing a diagnosis.
  - `clinical-notes-summarizer-referral-context` - Summarizes source-recorded referral context without placing or scheduling it.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_clinical-notes-summarizer-review-rules.md`
  - `aibast_clinical-notes-summarizer-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Clinical Notes Summarizer Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Completed chart reviews faster with consistent output
- Improved clinical safety by proactively flagging conditions and medications
- Reduced coordination delays across care teams with complete, ready‑to‑use summaries
- Improved physician productivity and rate of clearances delivered

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
