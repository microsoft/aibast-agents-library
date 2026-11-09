# Personalized Marketing Agent

Automate personalized campaign design and execution to boost engagement, accelerate revenue, and strengthen customer loyalty.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/personalized-marketing/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Marketing Director, Campaign Manager
- **Industries:** Retail

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Summarize the aggregate customer groups without demographic traits and identify portfolio review priorities.` | Review aggregate segments |
| `Outline the review-only win-back sequence, assumptions, and approval gates.` | Design a governed campaign concept |
| `Draft neutral content ideas for New Explorers and explain the non-sensitive signals used.` | Draft privacy-safe content |
| `Compare the synthetic tests and call out measurement limitations before any decision.` | Evaluate synthetic performance |

## What the agent does

- Automatically segment customers based on real behavior and value signals
- Design multi-wave campaigns with tailored messaging, offers, and timing
- Continuously optimize engagement through automated testing and workflows

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_PersonalizedMarketingPilot`) with instructions and a greeting that lists the sample prompts.
- 7 agent skills, one per operation:
  - `campaign-workflow` - "Use when a campaign manager asks something like \"As Campaign Manager, plan the VIP wave launch for tomorrow morning and show me the automation workflow for approval\""
  - `consent-aware-content-personalization` - Drafts segment-level content ideas for a Campaign Manager without sensitive profiling or message delivery.
  - `executive-brief` - "Use when a marketing director asks something like \"As Marketing Director, create the executive brief summarizing our holiday campaign strategy\""
  - `privacy-safe-customer-segmentation` - Gives a Marketing Director an aggregate segment overview using only the packaged synthetic commercial signals.
  - `revenue-projection` - "Use when a marketing director asks something like \"As Marketing Director, break down the revenue projection scenarios for the VIP wave\""
  - `review-only-campaign-design` - Helps a Campaign Manager compare multi-wave campaign concepts without launching outreach or creating offers.
  - `synthetic-marketing-performance-analysis` - Summarizes fixed A/B and campaign scenarios for a Marketing Director without claiming live results.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_personalized-marketing-rules-and-safety.md`
  - `aibast_personalized-marketing-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Personalized Marketing Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Drove higher conversion rates via precision-targeted campaigns
- Reduced campaign planning cycles from weeks to hours
- Increased repeat purchases and average order value
- Provided leaders with real-time performance insights to guide decisions during peak periods

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
