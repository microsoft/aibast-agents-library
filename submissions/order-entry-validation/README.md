# Order Entry Validation Agent

Turn inbound customer purchase orders into validated draft sales orders: extract every PO field, check prices and terms against the accepted quote, catch invalid product configurations, classify the order, and hand a specialist a draft with each exception called out before entry.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/order-entry-validation/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Sales Operations Specialists, Sales Operations Managers, Product Configuration Analysts
- **Industries:** Manufacturing

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What's in my PO queue this morning?` | Sales Operations Specialist: Pending PO queue |
| `Read PO-4471 and pull out the order details.` | Sales Operations Specialist: Purchase order extraction |
| `Does PO-4471 match the quote?` | Sales Operations Specialist: Quote validation |
| `Check the product configuration on the Coho Refining order.` | Product Configuration Analyst: Configuration check |
| `What order type, class and sales channel should PO-4471 go in as?` | Sales Operations Specialist: Order classification |
| `Prepare the sales order for PO-4471 so I can enter it.` | Sales Operations Specialist: Draft sales order |
| `Across the whole queue, which orders are ready to enter and which need a fix?` | Sales Operations Manager: Queue readiness review |

## What the agent does

- Reads each PO into structured fields and shows the queue
- Validates the PO against the accepted quote with a per-line price tolerance
- Checks the configuration and classifies the order
- Prepares a draft sales order with every exception for the specialist

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_OrderEntryValidationManualBuild`) with instructions and a greeting that lists the sample prompts.
- 7 agent skills, one per operation:
  - `configuration-check` - Use when someone asks to check an order's product configuration, kits or pairings.
  - `draft-sales-order` - Use when someone asks to prepare or draft the sales order for a PO.
  - `extract-po` - Use when someone asks to read a purchase order or pull out its fields.
  - `order-classification` - Use when someone asks which order type, order class or sales channel applies.
  - `order-queue` - Use when someone asks what is in the purchase-order queue.
  - `queue-review` - Use when someone asks which orders across the queue are ready to enter and which need a fix.
  - `quote-validation` - Use when someone asks whether a PO matches its quote, prices or terms.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_order-entry-validation-rules-and-guardrails.md`
  - `aibast_order-entry-validation-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Order Entry Validation Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Validates orders without manual re-keying
- Stops errors before they reach the ERP
- Enters ready orders first and routes exceptions with a reason

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
