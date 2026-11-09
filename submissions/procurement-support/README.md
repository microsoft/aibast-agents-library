# Discount Finder Agent

Identifies and optimizes savings opportunities across vendors, contracts, and purchasing cycles to reduce costs and increase procurement efficiency.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/procurement-support/quest.html), Microsoft's catalog of industry agent templates.

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `I need to identify all available discounts for our upcoming purchase orders: office supplies, IT equipment, and software licenses.` | Procurement Manager: Savings Scan |
| `Which IT equipment deals expire this week, and what should we lock in immediately?` | Category Buyer: Time Sensitive Deals |
| `Model the office-supply bulk order strategy and the total savings projection for the quarter.` | Finance Director: Consolidation Analysis |
| `Create the implementation plan with the deadlines and the savings at risk, without placing anything.` | Category Buyer: Purchase Timing |
| `Prepare the Dell laptop and monitor PO for my approval and show the software license savings.` | Procurement Manager: Draft Purchase Order |
| `Which software licenses should move to annual or enterprise terms, and do we pay for any duplicate licenses?` | IT Asset Manager: License Optimization |

## What the agent does

- Scan upcoming purchases and surface saving opportunities
- Flag time‑sensitive promotions from medical supply and device vendors
- Identify categories suitable for consolidated, bulk purchasing
- Recommend optimal timing for major purchases and renewals

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_DiscountFinderPilot`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `consolidation-analysis` - Use when a finance director asks whether fragmented facility demand may qualify for structured sourcing review.
  - `draft-purchase-order` - "Use when a procurement manager asks something like \"Prepare the Dell laptop and monitor PO for my approval and show the software license savings\""
  - `license-optimization` - "Use when an it asset manager asks something like \"Which software licenses should move to annual or enterprise terms, and do we pay for any duplicate licenses\""
  - `purchase-timing` - Use when a category buyer asks how to sequence review of renewals, volume tiers, and announced price changes.
  - `savings-scan` - Use when a procurement manager asks which synthetic contracts or forecasts contain reviewable savings signals.
  - `time-sensitive-deals` - Use when a category buyer asks which offers or price notices need review first.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_procurement-support-rules-and-guardrails.md`
  - `aibast_procurement-support-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Discount Finder Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Captured savings with timely renewals and vendor discounts
- Streamlined decision-making with clear, ROI‑driven recommendations
- Reduced manual contract review, freeing staff for high-value work
- Improved budgeting accuracy through early visibility into savings

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
