# Supply Chain Disruption Alert Agent

Detects and manages supply chain risks to defend against disruptions, protect revenue, and maintain operational continuity.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/supply-chain-disruption-alert/quest.html), Microsoft's catalog of industry agent templates.

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which active disruption has the largest modeled impact and what is affected?` | Customer Fulfillment Lead: Active disruption brief |
| `Why is RT-APAC-01 high risk?` | Supply Chain Planner: Route risk explanation |
| `Draft a DISR-002 mitigation scenario without rerouting or moving inventory.` | Operations Leader: Approval-gated mitigation scenario |
| `Show Electronics alternatives without activating a supplier.` | Procurement Manager: Supplier due-diligence candidates |
| `I'm seeing unusual inventory movement at our Northwest stores. Can you help me understand what's happening?` | Regional Retail Manager: Northwest root-cause analysis |
| `What are our emergency options and costs?` | Regional Operations Director: Emergency response options |
| `Approved. Execute both Seattle and the 5 additional stores.` | Store Operations Manager: Ready-to-release transfer plan |
| `Activate tracking and show me the Portland DC recovery plan.` | Distribution Center Manager: DC recovery plan |
| `Create the executive report with financial impact.` | Finance Business Partner: Executive incident report |
| `Distribute the report and summarize what we accomplished.` | Supply Chain Director: Crisis response summary |

## What the agent does

- Detect supplier issues and logistics disruptions in real time
- Score severity and determine impacted SKUs, orders, and revenue exposure
- Compare backup sourcing, inventory shifts, and routing alternatives
- Recommend the best mitigation plan based on cost and lead time

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_SupplyChainDisruptionAlert`) with instructions and a greeting that lists the sample prompts.
- 10 agent skills, one per operation:
  - `emergency-options` - "Use when a Regional Operations Director asks What are our emergency options and costs?"
  - `incident-report` - "Use when a Finance Business Partner asks Create the executive report with financial impact."
  - `incident-summary` - "Use when a Supply Chain Director asks Distribute the report and summarize what we accomplished."
  - `recovery-plan` - "Use when a Distribution Center Manager asks Activate tracking and show me the Portland DC recovery plan."
  - `root-cause-analysis` - "Use when a Regional Retail Manager asks I'm seeing unusual inventory movement at our Northwest stores. Can you help me understand what's happening?"
  - `supply-chain-disruption-alert-disruption-dashboard` - Use when a Customer Fulfillment Lead asks to summarize active disruption evidence.
  - `supply-chain-disruption-alert-mitigation-plan` - Use when a Operations Leader asks to compare approval-gated mitigation options.
  - `supply-chain-disruption-alert-risk-assessment` - Use when a Supply Chain Planner asks to explain route risk factors.
  - `supply-chain-disruption-alert-supplier-alternatives` - Use when a Procurement Manager asks to prepare supplier candidates for due diligence.
  - `transfer-plan` - "Use when a Store Operations Manager asks Approved. Execute both Seattle and the 5 additional stores."
- 2 knowledge files holding the synthetic records and operating rules:
  - `supply-chain-disruption-alert-rules-and-controls.md`
  - `supply-chain-disruption-alert-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Supply Chain Disruption Alert Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Acted early enough to reduce risk and protect commitments
- Boosted resilience by finding single‑source and geographic risks
- Activated alternate suppliers and shifted inventory to avoid delay
- Improved continuity and planning confidence during disruption events

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
