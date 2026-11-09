# Omnichannel Engagement Agent

Deliver a single, unified view of cross-channel interactions for more strategic, streamlined support and stronger engagement.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/omnichannel-engagement/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Customer Experience Leader, Digital Engagement Manager, Contact Center Supervisor
- **Industries:** Cross-Industry, Retail

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `As Customer Experience Leader, compare the aggregate channel picture and call out continuity risks.` | Compare aggregate channels |
| `As Contact Center Supervisor, identify handoff friction across the aggregate journey archetypes.` | Find journey friction |
| `As Digital Engagement Manager, propose consent-aware experiments with frequency caps and no outreach.` | Draft consent-aware experiments |
| `As Digital Engagement Manager, summarize the synthetic attribution view and avoid causal claims.` | Review attribution evidence |
| `Show me the customer's journey across all channels and help me pick up where they left off.` | Contact Center Supervisor: Customer Journey |
| `Show me what Sarah has been asking about and where we dropped the ball.` | Contact Center Supervisor: Unresolved Issues |
| `Which channel and timing should we use to reach Sarah for this issue and in the future?` | Digital Engagement Manager: Channel Recommendation |
| `What proactive engagement should we plan for Sarah after this purchase, or if she doesn't convert?` | Digital Engagement Manager: Proactive Plan |
| `Prepare the context in case Sarah needs to be handed off to another agent.` | Customer Experience Leader: Handoff Package |

## What the agent does

- Consolidate interactions into a single, continuous customer view
- Surface unresolved questions and journey friction instantly
- Recommend the best channel and message timing for each customer
- Strengthen continuity across touchpoints to deliver a consistent, connected customer experience

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_OmnichannelEngagementPilot`) with instructions and a greeting that lists the sample prompts.
- 9 agent skills, one per operation:
  - `campaign-attribution` - "Summarizes fixed attribution examples for a Digital Engagement Manager without claiming causality or live performance."
  - `channel-performance` - "Gives a Customer Experience Leader an aggregate channel view without identity stitching."
  - `channel-recommendation` - "Use when a digital engagement manager asks something like \"Which channel and timing should we use to reach Sarah for this issue and in the future\""
  - `customer-journey` - "Use when a contact center supervisor asks something like \"Show me the customer's journey across all channels and help me pick up where they left off\""
  - `engagement-optimization` - "Drafts channel optimization options for a Digital Engagement Manager without outreach."
  - `handoff-package` - "Use when a customer experience leader asks something like \"Prepare the context in case Sarah needs to be handed off to another agent\""
  - `journey-analysis` - "Helps a Contact Center Supervisor review aggregate journey friction without reconstructing individual behavior."
  - `proactive-plan` - "Use when a digital engagement manager asks something like \"What proactive engagement should we plan for Sarah after this purchase, or if she doesn't convert\""
  - `unresolved-issues` - "Use when a contact center supervisor asks something like \"Show me what Sarah has been asking about and where we dropped the ball\""
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_omnichannel-rules-and-safety.md`
  - `aibast_omnichannel-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Omnichannel Engagement Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Resolved issues in a single interaction with complete context
- Increased conversion by delivering the right content at key moments
- Reduced repeat contacts across channels
- Improved customer satisfaction through consistent, personalized engagement

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
