# Utility Billing and Assistance Agent

Automate leak detection and billing processes to improve customer satisfaction, ensure policy compliance, and protect municipal revenue.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/utility-billing-assistance/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Customer Service Rep, Billing Specialist, Assistance Coordinator
- **Industries:** Energy and Utilities, State and Local Government

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Explain ACCT-90003 balances without changing the account.` | Customer Service Representative: Read-only account explanation |
| `Does ACCT-90003 show a possible leak and what draft adjustment evidence is needed?` | Billing Specialist: Leak and usage screening |
| `Show ACCT-90003 payment-plan options, but do not set one up.` | Revenue Services Supervisor: Draft payment-plan options |
| `What assistance programs could help the Maple Drive resident on a fixed income, and do they qualify?` | Assistance Coordinator: Resident assistance eligibility |
| `Does the Maple Drive household qualify for a leak credit, and how much would it be?` | Leak Adjustment Analyst: Leak adjustment credit draft |
| `Get the payment plan and the water-assistance application ready for the Maple Drive resident. What paperwork do they need?` | Enrollment Specialist: Payment plan and application packet |
| `Can we help the Maple Drive resident fix the leak at no cost?` | Water Conservation Coordinator: Repair assistance program |
| `Pull everything together for the Maple Drive resident so we can send it and close out the account notes.` | Customer Resolution Manager: Complete assistance package |
| `Screen a two-person household earning 25000 with a 70-year-old applicant.` | Eligibility Screener: Preliminary household screening |

## What the agent does

- Automate smart meter analysis for leak detection and usage anomalies
- Apply municipal code rules to calculate credits and adjust bills
- Screen income eligibility and pre-fill applications for assistance programs
- Set up payment plans and schedule repairs in one efficient workflow

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_UtilityBillingandAssistance`) with instructions and a greeting that lists the sample prompts.
- 9 agent skills, one per operation:
  - `utility-billing-assistance-application-packet` - "Use when an Enrollment Specialist asks to prepare the payment plan and assistance application and the documents needed."
  - `utility-billing-assistance-assistance-programs` - Use when a Assistance Coordinator asks to perform preliminary, non-binding program screening.
  - `utility-billing-assistance-billing-inquiry` - Use when a Customer Service Representative asks to provide a read-only account explanation.
  - `utility-billing-assistance-income-screen` - "Use when an Eligibility Screener asks to screen a household from a stated size, income, and age."
  - `utility-billing-assistance-leak-adjustment` - "Use when a Leak Adjustment Analyst asks whether a leak qualifies for the Municipal Code 18.42 credit and how much it is."
  - `utility-billing-assistance-payment-plan` - Use when a Revenue Services Supervisor asks to draft installment options without account changes.
  - `utility-billing-assistance-repair-assistance` - "Use when a Water Conservation Coordinator asks about free repair assistance for a leak."
  - `utility-billing-assistance-resolution-summary` - "Use when a Customer Resolution Manager asks to assemble the complete assistance package and account notes."
  - `utility-billing-assistance-usage-analysis` - Use when a Billing Specialist asks to screen smart-meter history and prepare a non-binding estimate.
- 2 knowledge files holding the synthetic records and operating rules:
  - `utility-billing-assistance-rules-and-controls.md`
  - `utility-billing-assistance-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Utility Billing and Assistance Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Resolved complex billing disputes in a single interaction
- Increased assistance enrollment while reducing delinquent accounts
- Eliminated cross-system manual checks to improve productivity and consistency
- Strengthened customer trust with transparent, compliant resolution

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
