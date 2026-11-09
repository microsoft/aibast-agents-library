# Retail Store Associate Copilot

Deliver real-time product intelligence and transaction support to deliver faster service and boost sales performance.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/store-associate-copilot/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Store Associate, Sales Manager, Floor Specialist
- **Industries:** Retail

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Give me the product facts, floor location, optional complements, and availability caveat for the running shoes.` | Look up a product safely |
| `Draft respectful language for acknowledging a complaint while keeping the decision with an authorized reviewer.` | Draft customer-assistance language |
| `Turn the opening work into a prioritized planning checklist without claiming execution.` | Plan the store shift |
| `Summarize aggregate role-cohort coaching signals without ranking employees.` | Review aggregate coaching signals |

## What the agent does

- Surface product specs, comparisons, and current promotions instantly
- Confirm inventory and suggest alternatives for out-of-stock items
- Recommend accessories and warranties with conversion tips
- Prepare transactions with loyalty discounts and financing options automatically

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_RetailStoreAssociateCopilot`) with instructions and a greeting that lists the sample prompts.
- 7 agent skills, one per operation:
  - `accessory-recommendations` - "Use when a store associate asks something like \"What accessories go with the TechPro headphones, and what would I earn on the whole package\""
  - `aggregate-store-coaching-review` - Gives a Sales Manager role-cohort coaching signals without profiling workers or making employment decisions.
  - `prepare-transaction` - "Use when a store associate asks something like \"My Gold member customer is taking the TechPro with the warranty and cleaning kit. Get the sale ready\""
  - `product-compare` - "Use when a store associate asks something like \"The shopper is torn between the TechPro and the SoundMax Pro. How do they stack up\""
  - `respectful-customer-assistance-draft` - Drafts pressure-free language for a Store Associate without sending a message or performing a transaction.
  - `store-shift-planning-checklist` - Helps a Floor Specialist review opening, midday, or closing work without claiming execution.
  - `verified-product-lookup-draft` - Gives a Store Associate product facts and a synthetic availability snapshot with a verification gate.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_store-associate-rules-and-safety.md`
  - `aibast_store-associate-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Retail Store Associate Copilot** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reduced interaction time dramatically
- Increased accessory attach rates and average transaction value
- Eliminated pricing errors and improved checkout speed
- Enabled associates to serve more customers and boost commission

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
