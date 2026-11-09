# Order Status Communications Agent

Automate proactive order updates, delay management, and customer communications to protect relationships and revenue.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/order-status-communication/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Customer Service Rep, Account Manager, Operations Leader
- **Industries:** Manufacturing

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which orders are on track or delayed, and where should customer service focus its review?` | Review orders needing attention |
| `What shipment evidence is recorded for the shipped order, and what still needs carrier validation?` | Validate recorded shipment evidence |
| `Prepare the internal delay and recovery review for the at-risk customer order without changing any schedule.` | Prepare an internal delay review |
| `Draft the customer updates for approval, but do not send an email, portal update, EDI message, or Teams message.` | Draft customer updates for approval |

## What the agent does

- Identify delays proactively with automated monitoring
- Generate recovery plans like schedule adjustments, alternative sourcing, and expedited logistics
- Communicate updates across channels with consistent messaging
- Tailor notifications and actions to the customer tier and preferences

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_OrderStatusCommunicationsPi`) with instructions and a greeting that lists the sample prompts.
- 7 agent skills, one per operation:
  - `customer-update` - Use when an account manager asks for customer-ready wording.
  - `delay-notification` - Use when operations asks for delay, recovery, owner, and channel context.
  - `engagement-plan` - "Use for customer touchpoints and multi-channel engagement: email, EDI 856 ASN, supplier portal, follow-up call, monitoring and CRM note, all prepared and not sent."
  - `order-lookup` - Use when customer service asks which orders are progressing or at risk.
  - `performance-dashboard` - "Use for the order and customer performance dashboard: this order, 12-month account metrics, delay management effectiveness and lessons learned."
  - `quality-validation` - "Use for quality assurance and validation: incoming material checks, production quality, final validation and customer-specific requirements."
  - `shipment-tracking` - Use when an account manager asks for recorded shipment evidence.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_order-status-communication-review-rules.md`
  - `aibast_order-status-communication-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Order Status Communications Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reduced delivery delays with faster recovery plan activation
- Gave timely, transparent updates that increased customer trust
- Minimized inquiry volume with proactive updates and next steps
- Preserved account health and supplier ratings through consistent disruption handling

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
