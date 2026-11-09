# Inventory Visibility Agent

Deliver real-time cross-channel inventory intelligence to prevent stockouts, reduce overstock, and maximize omnichannel retail performance.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/inventory-visibility/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Inventory Planners, Store Managers, Category Managers
- **Industries:** Retail

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Summarize the store snapshot and verification boundary.` | Review an inventory snapshot |
| `Identify urgent review candidates without issuing transfer or replenishment commands.` | Inspect stock exceptions |
| `Show the replenishment scenario and its assumptions.` | Model replenishment |
| `Compare the channel planning scenario without reserving any stock.` | Compare channel allocation |

## What the agent does

- Identify real‑time stock levels across stores, warehouses, and ecommerce
- Detect critical stockouts and instantly locate nearest available inventory
- Recommend same‑day transfers and scheduled replenishment
- Evaluate category health to flag overstock, slow movers, and seasonal demand patterns

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_InventoryVisibilityPilot`) with instructions and a greeting that lists the sample prompts.
- 8 agent skills, one per operation:
  - `automation-recommendations` - "Use when an inventory planner asks something like \"Yes, optimize all 8 and show me the warehouse automation recommendations\""
  - `category-channel-allocation-scenario` - Helps a Category Manager compare channel planning weights without reserving or allocating stock.
  - `draft-replenishment-scenario` - Gives an Inventory Planner a fourteen-day replenishment scenario without creating orders or transfers.
  - `investment-proposal` - "Use when an inventory planner asks something like \"Yes, create the investment proposal with 3-year financial projections\""
  - `network-health` - "Use when an inventory planner asks something like \"Approved. Execute both phases and show me system-wide inventory health\""
  - `read-only-inventory-visibility` - Gives an Inventory Planner a synthetic network snapshot with explicit verification requirements.
  - `store-stock-review-candidates` - Helps a Store Manager review critical and low-stock candidates without executing inventory actions.
  - `transfer-plan` - "Use when an inventory planner asks something like \"Yes, create the reallocation plan with cost and timing details\""
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_inventory-visibility-rules-and-safety.md`
  - `aibast_inventory-visibility-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Inventory Visibility Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Resolved urgent stockouts quickly and avoided lost sales
- Identified excess inventory and highlighted opportunities
- Enhanced demand planning with more reliable forecasts
- Improved inventory efficiency and accelerated store decision‑making

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
