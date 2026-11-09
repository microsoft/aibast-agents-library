# Inventory Rebalancing Agent

Intelligently optimize inventory portfolios to improve cash flow and warehouse efficiency while reducing waste.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/inventory-rebalancing/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Supply Chain Managers, Inventory Managers, Procurement Manager
- **Industries:** Manufacturing

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which distribution centers are tight on space, and which SKU positions should my team review first?` | Review warehouse and SKU pressure |
| `Where do we have forecast-relative shortages or excess that deserve a rebalancing review?` | Find shortages and slow-moving stock |
| `Show me the proposed warehouse moves, but do not move or reserve anything.` | Prepare proposed warehouse moves |
| `Where is inventory exposure concentrated, and what trade-offs should I take to the planning meeting?` | Compare inventory planning trade-offs |

## What the agent does

- Analyze inventory and classify items by velocity and strategic value
- Develop a phased recovery plan with flash sales, vendor returns, and safety stock adjustments
- Optimize reorder schedules
- Implement dynamic inventory policies and AI-driven alerts

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_InventoryRebalancingPilot`) with instructions and a greeting that lists the sample prompts.
- 10 agent skills, one per operation:
  - `aibast-cost-analysis` - Use when a procurement manager asks where synthetic holding and shortage exposure is concentrated.
  - `aibast-inventory-snapshot` - Use when a supply chain manager asks where capacity, stock, and reorder exposure need attention.
  - `aibast-rebalance-recommendation` - Use when an inventory manager asks where forecast-relative shortages and excess should be reviewed.
  - `aibast-transfer-plan` - Use when a supply chain manager asks for review-ready inter-warehouse move options.
  - `execution-timeline` - "Use when a supply chain manager asks something like \"Lay out the 90-day rollout with milestones I can share with stakeholders\""
  - `financial-impact` - "Use when a procurement manager asks something like \"What are the savings and the ROI if we do this\""
  - `monitoring-plan` - "Use when an inventory manager asks something like \"How do we keep inventory optimized after the 90 days\""
  - `portfolio-analysis` - "Use when a supply chain manager asks something like \"We have $5M inventory, 30 slow-moving, warehouse 95 full. Need optimization plan\""
  - `recovery-plan` - "Use when a supply chain manager asks something like \"Yes, show me a phased plan to recover cash from the slow-moving stock\""
  - `warehouse-impact` - "Use when an inventory manager asks something like \"What would that plan do to our warehouse space and operations\""
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_inventory-rebalancing-review-rules.md`
  - `aibast_inventory-rebalancing-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Inventory Rebalancing Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Freed up working capital
- Improved warehouse efficiency with space optimization and streamlined picking processes
- Reduced financial risk by minimizing obsolescence
- Enhanced operational agility with dynamic inventory policies and AI-driven demand alignment

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
