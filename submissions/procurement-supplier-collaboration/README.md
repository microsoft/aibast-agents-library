# Procurement and Supplier Collaboration Agent

Help a utility buy critical network materials faster: recommend the procurement route and supplier shortlist for every requisition, answer supplier questions from the RFQ pack, score bids on price, lead time, quality and sustainability, flag late deliveries, and hold invoices that fail the three-way match, while every award and payment stays with an authorized person.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/procurement-supplier-collaboration/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Category Manager, Buyer, Accounts Payable Lead
- **Industries:** Energy and Utilities

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What requisitions are waiting, how should we buy each one, and who should we invite for the transformer order?` | Category Manager: Sourcing plan |
| `A bidder on the transformer RFQ asks if they can deliver all 24 units in two lots instead of three. What should I tell them?` | Buyer: Supplier question |
| `The transformer bids are in. How do they score, and who should the award panel pick?` | Category Manager: Bid evaluation |
| `Which of our open orders have delivery problems I need to chase today?` | Expediter: Delivery tracking |
| `Which supplier invoices can go for payment approval today, and which ones need to be held?` | Accounts Payable Lead: Three-way match |

## What the agent does

- Recommend the route and supplier shortlist
- Answer bidders from the published RFQ pack
- Score bids on price, lead time and quality
- Flag late deliveries and unmatched invoices

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_ProcurementAndManualBuild`) with instructions and a greeting that lists the sample prompts.
- 5 agent skills, one per operation:
  - `bid-evaluation` - Use when someone asks how the bids score on price, lead time, quality and sustainability, or which supplier the award panel should pick.
  - `delivery-tracking` - Use when an expediter or buyer asks which purchase orders are unacknowledged or have delivery problems against the committed date.
  - `invoice-match` - Use when accounts payable asks which invoices pass the three-way match for payment approval and which must be held.
  - `sourcing-plan` - Use when a category manager or buyer asks which requisitions are open, how each should be bought (framework direct award, mini-competition or open tender), or which suppliers to invite.
  - `supplier-query` - Use when a buyer asks what to tell a supplier who has a question about an open RFQ; returns a draft reply from the published pack that is never sent.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_procurement-supplier-collaboration-rules-and-guardrails.md`
  - `aibast_procurement-supplier-collaboration-synthetic-records.md`
- 1 tools:
  - `Work IQ MCP Server` - 

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Procurement and Supplier Collaboration Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Shortened the cycle for routine orders
- Treated every bidder the same way
- Gave the award panel a clear recommendation
- Paid only invoices that matched the order

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-30.
