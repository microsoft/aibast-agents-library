# Customer Sentiment and Churn Prediction Agent

Deliver AI-powered sentiment intelligence that detects churn risk early and enables proactive retention strategies.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/customer-sentiment-churn/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Relationship Managers, Retention Specialists, Customer Success Teams
- **Industries:** Financial Services

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Analyze customer sentiment across our banking portfolio and identify accounts at highest churn risk.` | Cross-channel sentiment view |
| `Show me profiles of our highest-value at-risk customers.` | Churn-review prioritization |
| `Prepare options for Marcus that I can review before anyone contacts him or changes a fee.` | Retention option preparation |
| `Which segment is under its experience benchmark, and what should we investigate?` | Segment context |
| `Yes, what are the early warning signals we should watch for?` | Early warning signals |
| `Yes, assign the outreach and set up tracking.` | Outreach assignment plan |

## What the agent does

- Analyze sentiment across all customer touchpoints
- Score churn risk by unifying sentiment, behavior, and all activity
- Identify the customers most likely to leave and most valuable to retain
- Generate targeted retention strategies and recommended outreach plans

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_CustomerSentimentandChurnP`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `churn-prediction` - Use for churn-review prioritization questions in the Customer Sentiment and Churn Prediction Agent synthetic pilot.
  - `early-warning-signals` - "Use when a retention specialist asks something like \"Yes, what are the early warning signals we should watch for\""
  - `outreach-plan` - "Use when a customer success lead asks something like \"Yes, assign the outreach and set up tracking\""
  - `retention-actions` - Use for retention option preparation questions in the Customer Sentiment and Churn Prediction Agent synthetic pilot.
  - `segment-analysis` - Use for segment context questions in the Customer Sentiment and Churn Prediction Agent synthetic pilot.
  - `sentiment-dashboard` - Use for cross-channel sentiment view questions in the Customer Sentiment and Churn Prediction Agent synthetic pilot.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_customer-sentiment-churn-controls-and-review.md`
  - `aibast_customer-sentiment-churn-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Customer Sentiment and Churn Prediction Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Acted before churn intent surfaced
- Prioritized high‑risk, high‑value customers
- Empowered relationship managers with personalized resources
- Protected revenue and reduced replacement costs
- Improved overall customer experience

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
