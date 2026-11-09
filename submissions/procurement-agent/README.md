# Procurement Agent

Automate purchase order management and vendor selection to enable faster and more cost-effective purchasing.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/procurement-agent/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Procurement Manager, Finance Director, Department Approver
- **Industries:** Cross-Industry

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Walk me through the cloud-upgrade request and tell me whose review it needs before anything moves.` | Procurement Manager: Purchase-request review |
| `Give me a neutral comparison of the approved cloud vendors; do not pick a winner.` | Category Buyer: Vendor evidence comparison |
| `This infrastructure request landed in my queue. What is the recommended approval path?` | Department Approver: Approval-path recommendation |
| `Where is the purchasing budget under pressure, and what should we review before approving more spend?` | Finance Director: Spend and budget review |

## What the agent does

- Analyze approved vendors and contract terms in seconds
- Identify best-value supplier and apply volume discounts
- Automatically create and route purchase orders while flagging duplicate software licenses
- Track budget and ensure compliance

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_ProcurementPilot`) with instructions and a greeting that lists the sample prompts.
- 8 agent skills, one per operation:
  - `approval-routing` - Use when a department approver asks which authorization threshold applies to a request.
  - `budget-impact` - "Use when a finance director asks something like \"How does the engineering laptop order affect our Q4 IT budget\""
  - `draft-purchase-order` - "Use when a procurement manager asks something like \"Create the purchase order for the 50 Dell Latitude 7440 laptops for the new engineering team\""
  - `draft-rfq` - "Use when a category buyer asks something like \"We also need an RFQ for office furniture for the same engineering team\""
  - `expedite-approval` - "Use when a procurement manager asks something like \"The engineering laptop order is stuck in approval. Can you expedite it with urgency notifications\""
  - `purchase-request` - Use when a procurement manager asks for request context and the applicable approval level.
  - `spend-analysis` - Use when a finance director asks which synthetic category is over budget or approaching a limit.
  - `vendor-comparison` - Use when a category buyer wants a neutral view of synthetic vendor ratings, terms, and tiers.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_procurement-agent-rules-and-guardrails.md`
  - `aibast_procurement-agent-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Procurement Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reduced procurement cycle time from hours to minutes
- Captured volume discounts and flagged duplicate spending
- Delivered equipment on time while maintaining budget compliance
- Freed team capacity for strategic vendor negotiations

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
