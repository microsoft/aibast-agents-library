# Product Feedback Synthesizer Agent

Turn fragmented feedback into actionable insights that accelerate product improvements, prevent churn, and optimize engineering priorities.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/product-feedback-synthesizer/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Product Manager, Engineering Lead, Director of Product
- **Industries:** Cross-Industry

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Give me the cross-channel feedback picture before the weekly product review.` | Product Manager: Cross-channel feedback summary |
| `Rank the feature-request evidence for review, but do not turn it into a roadmap.` | Engineering Lead: Feature-request evidence ranking |
| `What are the strongest sentiment signals in the fictional customer snapshot?` | Director of Product: Sentiment and NPS evidence |
| `Frame the impact tradeoffs the product trio should validate before sequencing work.` | Product Manager: Roadmap review candidates |

## What the agent does

- Aggregate customer feedback from diverse sources into a single view
- Analyze sentiment and identify top pain points and feature requests
- Prioritize items based on impact and automate Jira ticket creation
- Alert teams to churn risks and competitive gaps for proactive intervention

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_ProductFeedbackSynthesizerP`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `draft-jira-tickets` - "Use when an engineering lead asks something like \"Write up engineering tickets for the most urgent fixes and a heads-up message for the team\""
  - `feature-requests` - Use when an engineering lead wants review candidates sorted by the supplied synthetic ARR weight.
  - `feedback-summary` - Use when a product manager asks for a compact view of volume, channels, categories, and synthetic commercial context.
  - `pain-points` - "Use when a product manager asks something like \"What are the biggest problems customers keep running into with the product\""
  - `roadmap-impact` - Use when a product trio wants a non-binding impact view with explicit validation gates.
  - `sentiment-analysis` - Use when a director of product asks for the fictional sentiment split and recent excerpts.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_product-feedback-synthesizer-rules-and-guardrails.md`
  - `aibast_product-feedback-synthesizer-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Product Feedback Synthesizer Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reduced feedback analysis time from weeks to minutes
- Delivered data-driven prioritization for roadmap planning
- Prevented churn through early detection of at-risk accounts
- Accelerated feature delivery and improved customer satisfaction

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
