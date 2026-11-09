# Campaign Delivery Optimizer Agent

Help ad sales and ad operations teams keep every advertiser campaign on plan by tracking weekly delivered reach against plan, finding placements with extra reach to close a delivery gap, and drafting the recommendation for the sales lead to approve, while nothing is booked or shared with an advertiser without a person's approval.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/campaign-delivery-optimizer/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Ad Operations Manager, Campaign Manager, Ad Sales Lead
- **Industries:** Media & Entertainment, Advertising

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Is the Harborlight Streaming campaign falling behind this week, and by how much?` | Ad Operations Manager: Campaign risk check |
| `Where can we find extra reach this week to close the Harborlight gap?` | Campaign Manager: Available reach |
| `Draft the make-good for Harborlight so Maya can review it. Don't send anything to the advertiser yet.` | Ad Sales Lead: Recommendation draft for approval |

## What the agent does

- Track each campaign's weekly reach against its plan
- Flag at-risk campaigns as soon as delivery falls behind
- Find placements with extra reach to close the gap
- Draft recommendations for the sales lead to approve and share

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_CampaignDeliveryManualBuild`) with instructions and a greeting that lists the sample prompts.
- 3 agent skills, one per operation:
  - `approval-recommendation` - Use when someone asks for the recommendation or make-good for a campaign, its approval status, or who approves it; returns a draft that is never shared.
  - `available-reach` - Use when someone asks which placements have extra reach this week to close a campaign's delivery gap.
  - `campaign-risk` - Use when someone asks whether a campaign is behind plan this week, how big the delivery gap is, or why it is at risk.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_campaign-delivery-optimizer-rules-and-guardrails.md`
  - `aibast_campaign-delivery-optimizer-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Campaign Delivery Optimizer Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Caught under-delivering campaigns within the week
- Recovered reach with the right placements
- Helped every campaign hit its goals
- Kept advertisers coming back

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-23.
