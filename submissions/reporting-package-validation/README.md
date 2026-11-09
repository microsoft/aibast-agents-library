# Reporting Package Validation Agent

Validate a month-end reporting package before anyone builds the executive pack: file intake with source lineage, integrity checks that separate missing data from a reported zero, division variance against budget with explanation thresholds, driver bridge reconciliation, an owner-routed exception queue, and a draft executive summary. The agent is read-only; it never posts a journal, edits a submission, releases the package, or sends commentary.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/reporting-package-validation/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** FP&A Manager, Financial Controller, Finance Director
- **Industries:** Financial Services, Cross-Industry

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `The June reporting package just landed. What did we receive and where did each file come from?` | FP&A Manager: Package intake and lineage |
| `Run the integrity checks before anyone looks at the numbers.` | Financial Controller: Integrity checks |
| `How did each division do against budget, and which variances need an explanation?` | FP&A Manager: Variance against budget |
| `Does the driver bridge reconcile from budget to actual?` | FP&A Manager: Driver bridge reconciliation |
| `Route the exceptions to the right owners.` | Financial Controller: Exception routing |
| `Draft the executive summary for the leadership pack.` | Finance Director: Executive summary draft |

## What the agent does

- Freeze file lineage and run completeness checks on arrival
- Compare divisions to budget and reconcile the driver bridge
- Queue blocking, advisory and explanation items to named owners
- Draft the executive summary and hold it until sign-off

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_ReportingPackageManualBuild`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `driver-reconciliation` - Use when someone asks whether the budget-to-actual driver bridge reconciles.
  - `exception-queue` - Use when someone wants the exceptions listed and routed to their owners.
  - `executive-summary` - Use when someone asks for the draft executive summary or commentary for the leadership pack.
  - `integrity-checks` - Use when someone wants completeness, missing-versus-zero, tie-out and formula checks run before the numbers are read.
  - `package-intake` - Use when someone asks what files the reporting package contains and where each one came from.
  - `variance-analysis` - Use when someone asks how each division did against budget and which variances need an explanation.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_reporting-package-validation-rules-and-guardrails.md`
  - `aibast_reporting-package-validation-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Reporting Package Validation Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Caught package defects on the day files arrived
- Gave leadership commentary that explains what a flat total hides
- Released packages only after every blocking exception cleared

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
