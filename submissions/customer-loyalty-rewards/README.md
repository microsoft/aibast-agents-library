# Customer Loyalty and Rewards Agent

Deliver AI-driven loyalty insights and planning to reduce points liability, improve engagement results, and boost member retention.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/customer-loyalty-rewards/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Loyalty Program Director, CRM Manager, Marketing Leader
- **Industries:** Cross-Industry

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Summarize the synthetic program health and governance boundary.` | Review loyalty program health |
| `Explain the synthetic Gold member balance without changing the ledger.` | Explain an informational balance |
| `Show review-only reward options without creating offers or issuing benefits.` | Compare reward options |
| `Review the synthetic tier structure without changing member status.` | Analyze tier structure |

## What the agent does

- Segment members by engagement level, churn risk, and point expiration
- Tailor offers and incentives based on purchase behavior and preferences
- Deliver targeted outreach through the highest‑engagement channels
- Recommend structural program improvements to reduce liability and improve redemption

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_CustomerLoyaltyandRewardsP`) with instructions and a greeting that lists the sample prompts.
- 10 agent skills, one per operation:
  - `at-risk-churn-segments` - Helps a Marketing Leader identify loyalty members at risk of churning across the 450K-member synthetic program without contacting anyone.
  - `campaign-launch-plan` - Prepares the three win-back campaigns as a launch-ready plan with projected 14-day results; the user launches them, the agent never sends anything.
  - `informational-points-summary` - Helps a CRM Manager explain a synthetic points balance without changing a ledger.
  - `loyalty-program-improvements` - Recommends high-impact structural loyalty program improvements without changing the program.
  - `loyalty-session-summary` - Summarizes the loyalty session results and next steps as a Teams-ready recap draft without posting it.
  - `loyalty-tier-structure-analysis` - Helps a Loyalty Program Director review tier structure and synthetic progress without changing status.
  - `review-only-reward-options` - Gives a Marketing Leader preference-matched reward options without creating offers or issuing benefits.
  - `synthetic-loyalty-program-health` - Gives a Loyalty Program Director an aggregate synthetic health view without changing the program.
  - `top-at-risk-member-profiles` - Shows a Marketing Leader the top at-risk members, their points and last purchase, and the lead member profile and trigger without contacting them.
  - `win-back-offer-drafts` - Drafts personalized win-back offers for Linda M. and the three at-risk segments without issuing an offer.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_loyalty-rewards-rules-and-safety.md`
  - `aibast_loyalty-rewards-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Customer Loyalty and Rewards Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Re‑engaged at‑risk members with timely, personalized campaigns
- Reduced point liability by prompting relevant and high‑value redemptions
- Improved program ROI with precise targeting and optimized reward strategies
- Strengthened loyalty with offers aligned to individual intent

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
