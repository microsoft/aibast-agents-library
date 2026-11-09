# Fraud Detection and Alert Agent

Deploy AI-driven fraud monitoring and identification to accelerate investigations, enhance detection rates, and improve prevention.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/fraud-detection-alert/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Fraud Analysts, SIU Investigators, Risk Leaders
- **Industries:** Financial Services

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Review overnight fraud activity and show me what needs immediate attention.` | Alert triage |
| `Yes, investigate the account takeover ring and show me the accounts.` | Transaction evidence review |
| `Yes, show me the pattern analysis and connected activity.` | Fraud-pattern hypotheses |
| `Yes, create investigation cases and take protective action.` | Case preparation and routing |
| `Yes, show me our fraud prevention performance and any concerning trends.` | Prevention performance and trends |
| `Yes, summarize everything and give me the action items.` | Morning summary and action items |

## What the agent does

- Process all alerts instantly and surface the most urgent threats
- Identify coordinated rings across account‑takeover, card testing, and wire fraud
- Auto‑generate complete case files with evidence and recommendations
- Route critical alerts to SIU, card fraud, or wire ops teams rapidly

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_FraudDetectionandAlertPilo`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `alert-triage` - Use for alert triage questions in the Fraud Detection and Alert Agent synthetic pilot.
  - `investigation-summary` - Use for case preparation and routing questions in the Fraud Detection and Alert Agent synthetic pilot.
  - `morning-summary` - "Use when a fraud operations manager asks something like \"Yes, summarize everything and give me the action items\""
  - `pattern-detection` - Use for fraud-pattern hypotheses questions in the Fraud Detection and Alert Agent synthetic pilot.
  - `prevention-metrics` - "Use when a risk leader asks something like \"Yes, show me our fraud prevention performance and any concerning trends\""
  - `transaction-analysis` - Use for transaction evidence review questions in the Fraud Detection and Alert Agent synthetic pilot.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_fraud-detection-alert-controls-and-review.md`
  - `aibast_fraud-detection-alert-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Fraud Detection and Alert Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Responded faster to critical events while reducing alert noise
- Stopped coordinated fraud schemes before funds were lost
- Accelerated investigations via automated workflows and routing
- Strengthened compliance and increased productivity with automated prioritization and documentation

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
