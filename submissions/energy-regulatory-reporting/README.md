# Regulatory Reporting Agent

Deliver real-time insights, automate critical workflows, and enable guided decision making—boosting efficiency while reducing operational and compliance risk for energy organizations.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/energy-regulatory-reporting/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Plant Manager / Reliability Engineer, Compliance Manager, Sustainability Lead, Data Analyst
- **Industries:** Energy and Utilities

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which filing is overdue and who owns it?` | Regulatory Reporting Lead: Reporting portfolio status |
| `Which report data is incomplete or below quality threshold?` | Data Analyst: Source-data validation screening |
| `Show filing state and confirm you did not transmit anything.` | Compliance Manager: Read-only filing-state tracker |
| `What high-severity reporting evidence is still open?` | Internal Auditor: Audit evidence triage |
| `I need to prepare our quarterly EPA emissions report. Can you pull the data?` | Environmental Manager: Quarterly emissions summary |
| `Generate the EPA submission file for the quarter and show me any compliance risks.` | Regulatory Affairs Director: Draft EPA submission package |

## What the agent does

- Predict failures with real-time analysis and automated planning
- Automate permit tracking and renewals with intelligent workflows
- Generate audit-ready reports quickly with streamlined data collection
- Consolidate fragmented data into real-time insights for easy centralized monitoring

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_RegulatoryReportingPilot`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `energy-regulatory-reporting-audit-readiness` - Use when a Internal Auditor asks to triage audit evidence without predicting outcomes.
  - `energy-regulatory-reporting-data-validation` - Use when a Data Analyst asks to screen source-data quality before certification.
  - `energy-regulatory-reporting-emissions-summary` - "Use when an Environmental Manager asks for the quarterly emissions summary."
  - `energy-regulatory-reporting-prepare-submission` - "Use when a Regulatory Affairs Director asks for the draft epa submission package."
  - `energy-regulatory-reporting-report-status` - Use when a Regulatory Reporting Lead asks to summarize the synthetic reporting portfolio.
  - `energy-regulatory-reporting-submission-tracker` - Use when a Compliance Manager asks to track recorded filing state without transmission.
- 2 knowledge files holding the synthetic records and operating rules:
  - `energy-regulatory-reporting-rules-and-controls.md`
  - `energy-regulatory-reporting-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Regulatory Reporting Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Improved asset reliability, reducing unplanned downtime and costs
- Maintained compliance and operational continuity across facilities
- Streamlined compliance reporting and minimized audit risk
- Gained real-time visibility and strategic planning support to achieve emissions goals

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
