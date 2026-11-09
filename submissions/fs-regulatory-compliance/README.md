# Regulatory Compliance Agent

Automate compliance monitoring and regulatory reporting to achieve proactive risk management with real-time surveillance.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/fs-regulatory-compliance/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Chief Compliance Officers, Compliance Managers, Trading Desk Supervisors
- **Industries:** Financial Services

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Are we going to fail our next MiFID audit? What's actually broken on the desk right now?` | See what threatens audit readiness |
| `Which of my traders can't legally trade today, and who do I have to call?` | Find who cannot trade today |
| `We executed a few hundred trades this week. Which ones will the regulator reject, and why exactly?` | Identify reports likely to be rejected |
| `Is anything about to go live that shouldn't?` | Block an unsafe algorithm go-live |
| `My head of trading says the reporting is fine. Prove him wrong with specifics I can take to the board.` | Prepare board-ready reporting evidence |

## What the agent does

- Scan all executed trades for reporting accuracy, required fields, and best‑execution performance
- Flag missing or outdated documentation
- Automate corrections and submissions to the regulatory portal
- Identify upcoming certification expirations and enroll traders

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_RegulatoryCompliancePilot`) with instructions and a greeting that lists the sample prompts.
- 7 agent skills, one per operation:
  - `algorithm-documentation-and-go-live-review` - Use when an algorithm or strategy is about to go live, needs sign-off, or may be running with incomplete or expired documentation.
  - `best-execution-analysis` - "Use when a compliance manager asks something like \"How did best execution hold up last quarter, venue by venue\""
  - `compliance-dashboard-and-audit-readiness` - Use for whole-desk audit readiness, what is broken, board evidence, or cross-domain compliance-risk questions.
  - `executive-summary` - "Use when a chief compliance officer asks something like \"Generate the executive report and summarize what we accomplished in this review\""
  - `regulatory-correction-and-submission-preparation` - Use to stage source-backed corrections and prepare new or correction-report payloads for an Approved Reporting Mechanism.
  - `trade-reporting-and-execution-surveillance` - Use for regulator-rejection, missing-field, venue, late-reporting, slippage, best-execution, or trade-level exception questions.
  - `trader-certification-readiness` - Use for who may trade, lapsed or upcoming certifications, supervisor escalation, and training-session planning.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_fs-regulatory-compliance-rules-and-controls.md`
  - `aibast_fs-regulatory-compliance-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Regulatory Compliance Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Ensured near‑perfect reporting accuracy and reduced exposure to regulatory penalties
- Validated algorithm documentation before go‑live
- Reduced compliance workload by automating reviews and reporting
- Maintained certification readiness across the desk with automated scheduling and alerts

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
