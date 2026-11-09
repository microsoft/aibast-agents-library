# Wealth Insights Generator Agent

Deliver AI-powered portfolio intelligence to uncover hidden asset opportunities, strengthen client relationships, and drive advisory growth at scale.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/wealth-insights-generator/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Wealth Advisor, Relationship Managers, Advisory Directors
- **Industries:** Financial Services

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Give me the fixed market snapshot for the morning huddle and label whether it is current data.` | Fixed market snapshot |
| `Which household has the largest held-away opportunity and what life event needs validation?` | Unified wealth insights |
| `Which clients have high-priority planning signals for advisor review?` | Planning-gap signals |
| `Which synthetic client is below its benchmark, and what does the attribution label say?` | Performance context |
| `Prepare my review brief for the Kensington household without turning it into advice or outreach.` | Advisor meeting preparation |

## What the agent does

- Aggregate held‑away assets into a unified wealth picture and form a comprehensive client profile
- Surface planning gaps, diversification needs, and upcoming life events
- Generate personalized outreach content and meeting materials
- Prioritize actions based on potential impact and relationship readiness

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_WealthInsightsGeneratorPilo`) with instructions and a greeting that lists the sample prompts.
- 9 agent skills, one per operation:
  - `book-insights` - "Use when a wealth advisor asks something like \"Generate wealth insights for my top clients and identify opportunities to deepen relationships\""
  - `client-insights` - Use for unified wealth insights questions in the Wealth Insights Generator Agent synthetic pilot.
  - `engagement-strategy` - "Use when a relationship manager asks something like \"How should I approach the Morrison relationship expansion\""
  - `insights-summary` - "Use when an advisory director asks something like \"Give me the complete wealth insights summary with the immediate actions\""
  - `market-brief` - Use for fixed market snapshot questions in the Wealth Insights Generator Agent synthetic pilot.
  - `meeting-brief` - Use for advisor meeting preparation questions in the Wealth Insights Generator Agent synthetic pilot.
  - `opportunity-alerts` - Use for planning-gap signals questions in the Wealth Insights Generator Agent synthetic pilot.
  - `performance-attribution` - Use for performance context questions in the Wealth Insights Generator Agent synthetic pilot.
  - `planning-gaps` - "Use when a wealth advisor asks something like \"What planning gaps does the Morrison Family have\""
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_wealth-insights-generator-controls-and-review.md`
  - `aibast_wealth-insights-generator-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Wealth Insights Generator Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Identified high‑value opportunities that enabled targeted engagement
- Strengthened client relationships with personalized communication
- Equipped advisors with complete materials and action plans
- Improved advisor productivity by replacing hours of manual research with instant insights

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
