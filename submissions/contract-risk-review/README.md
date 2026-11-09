# Contract Risk Review Agent

Automate contract review processes to enable faster, lower-risk, and more successful negotiations.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/contract-risk-review/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Legal Operations, Attorneys, Executives
- **Industries:** Professional Services, Consulting

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which agreements should I put in front of counsel first, and what is driving the priority?` | Prioritize the contract queue |
| `Walk me through the liability, IP ownership, and payment-term language that needs attention in the MSA.` | Inspect the MSA clauses |
| `Compare the available contract evidence with our internal policy and tell me where the file is incomplete.` | Find policy and evidence gaps |
| `Prepare the negotiation positions, fallbacks, and escalation points for the highest-risk agreements.` | Prepare negotiation positions |

## What the agent does

- Analyze the agreement in seconds, highlighting key issues and risks
- Identify gaps in liability protection, IP ownership, and payment terms compared to industry standards
- Generate a prioritized list of amendments and negotiation strategies

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_ContractRiskReviewPilot`) with instructions and a greeting that lists the sample prompts.
- 9 agent skills, one per operation:
  - `additional-risks` - "Use when a legal operations director asks something like \"What other risk factors did you find beyond liability and IP\""
  - `contract-clause-analysis` - Explains documented liability, IP, payment, and other clause findings.
  - `contract-overview` - "Use when a commercial attorney asks something like \"Legal just sent over the NovaTech Systems master services agreement. Can you review it before our signing meeting tomorrow\""
  - `contract-policy-screen` - Compares available fictional clauses with the synthetic internal policy.
  - `contract-portfolio-risk-scan` - Ranks the fictional contract portfolio for counsel review.
  - `contract-renegotiation-brief` - Drafts prioritized amendment positions and counsel escalation points.
  - `ip-analysis` - "Use when a commercial attorney asks something like \"Show me the IP ownership problems in the NovaTech agreement\""
  - `liability-analysis` - "Use when a commercial attorney asks something like \"What specifically is wrong with the liability provisions in the NovaTech agreement\""
  - `redline-summary` - "Use when a general counsel asks something like \"Generate the redline and an executive summary for our legal team\""
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_contract-risk-policy-playbook.md`
  - `aibast_contract-risk-synthetic-agreements.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Contract Risk Review Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reduced liability exposure and safeguarded intellectual property and proprietary assets
- Improved financial outcomes by optimizing payment terms
- Lowered legal costs and accelerated deal closure

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
