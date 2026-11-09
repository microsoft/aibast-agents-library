# Customer Onboarding Agent

Orchestrate client onboarding journeys with unified workflows to accelerate revenue and mitigate compliance risk.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/fs-customer-onboarding/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Onboarding Specialist, Relationship Manager, Compliance Officer
- **Industries:** Cross-Industry, Financial Services

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What is holding up the enhanced due diligence case, and which checks need my review?` | KYC evidence review |
| `Which approved-looking file is ready for account setup review, and what product is being prepared?` | Account setup preparation |
| `Give me the business onboarding document list for Blackwood before I call them.` | Document readiness |
| `Where is the onboarding queue stuck, and who owns each application?` | Onboarding pipeline |

## What the agent does

- Automate identity verification, document collection, and analysis
- Perform sanctions screening and regulatory checks
- Configure accounts, treasury services, and credit facilities
- Gain real-time updates on client profiles and KYC processes

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_CustomerOnboardingPilot`) with instructions and a greeting that lists the sample prompts.
- 9 agent skills, one per operation:
  - `account-setup` - Use for account setup preparation questions in the Customer Onboarding Agent synthetic pilot.
  - `beneficial-ownership` - "Use when a compliance officer asks something like \"What about beneficial ownership on the Nexus file? We need to be compliant with FinCEN rules\""
  - `document-checklist` - Use for document readiness questions in the Customer Onboarding Agent synthetic pilot.
  - `initiate-onboarding` - "Use when a relationship manager asks something like \"I need to onboard a new corporate client, Nexus Industries, for commercial banking treasury management, a credit line and FX. It's a high-priority relationship worth about $8M a year\""
  - `kyc-verification` - Use for kyc evidence review questions in the Customer Onboarding Agent synthetic pilot.
  - `onboarding-status` - Use for onboarding pipeline questions in the Customer Onboarding Agent synthetic pilot.
  - `onboarding-timeline` - "Use when a relationship manager asks something like \"When can Nexus actually start using the account? What's the timeline\""
  - `risk-assessment` - "Use when a compliance officer asks something like \"Are there any risks or red flags I should be aware of for Nexus Industries\""
  - `status-summary` - "Use when a head of onboarding asks something like \"Send me a status summary for the Nexus onboarding\""
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_fs-customer-onboarding-controls-and-review.md`
  - `aibast_fs-customer-onboarding-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Customer Onboarding Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reduce onboarding from weeks to days while improve revenue and customer experience
- Boost accuracy of compliance checks, limiting regulatory risk
- Reduce manual coordination and labor costs and free up FTEs with a highly scalable workflow

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
