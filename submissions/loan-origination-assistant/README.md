# Loan Origination Assistant

Streamline mortgage origination with intelligent automation, enabling faster, more accurate loan decisions.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/loan-origination-assistant/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Loan Officers, Processors, Underwriters
- **Industries:** Financial Services

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What is in my mortgage pipeline, and which application is still in document review?` | Application intake |
| `Pre-analyze Kevin Nguyen’s ratios and show every stated eligibility exception.` | Eligibility and ratio analysis |
| `Build the VA document checklist for Sandra so I can verify the file.` | Document readiness |
| `Which files meet the limited criteria, and did the assistant approve any loan?` | Nonbinding underwriting findings |
| `Which conditions are still open on the commercial refinance, and is a closing date promised?` | Condition and timeline review |

## What the agent does

- Auto‑ingest applications and organize borrower documentation
- Produce instant loan program comparisons and eligibility recommendations
- Pre‑analyze credit and property data to surface risks and readiness signals
- Track conditions, reminders, and closing requirements in real time

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_LoanOriginationAssistantPil`) with instructions and a greeting that lists the sample prompts.
- 8 agent skills, one per operation:
  - `application-intake` - "Use when a loan officer asks something like \"Process the Martinez mortgage application and give me an eligibility assessment with documentation status\""
  - `application-review` - Use for application intake questions in the Loan Origination Assistant synthetic pilot.
  - `condition-tracking` - Use for condition and timeline review questions in the Loan Origination Assistant synthetic pilot.
  - `credit-analysis` - Use for eligibility and ratio analysis questions in the Loan Origination Assistant synthetic pilot.
  - `decision-recommendation` - Use for nonbinding underwriting findings questions in the Loan Origination Assistant synthetic pilot.
  - `document-verification` - Use for document readiness questions in the Loan Origination Assistant synthetic pilot.
  - `processing-summary` - "Use when a loan officer asks something like \"Give me the complete loan processing summary for the Martinez file\""
  - `program-comparison` - "Use when a loan officer asks something like \"Which loan programs are the Martinezes eligible for, and which one do you recommend\""
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_loan-origination-assistant-controls-and-review.md`
  - `aibast_loan-origination-assistant-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Loan Origination Assistant** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Accelerated intake and reduced manual document handling
- Delivered same‑day eligibility guidance to borrowers
- Improved underwriting quality by highlighting risk factors early
- Shortened closing timelines with automated condition tracking
- Freed teams for high-value tasks

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
