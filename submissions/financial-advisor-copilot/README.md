# Financial Advisor Agent

Automate branch banking and advisory workflows to streamline customer interactions, strengthen compliance, and improve financial guidance.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/financial-advisor-copilot/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Branch Bankers, Financial Advisors, Compliance Officers
- **Industries:** Financial Services

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Who is waiting, what do they need, and where should I route them after identity checks?` | Service intake and routing |
| `Summarize the advisor book and show which client is already retired.` | Client review |
| `Show the Whitfield allocation drift before our review meeting.` | Portfolio context |
| `Prepare discussion candidates for Angela without giving advice or creating an order.` | Advisor-review considerations |
| `Which client requires senior-investor controls, and what other checkpoints apply?` | Compliance checkpoints |
| `Draft the Whitfield handoff with request, identity status, risk context, and compliance flags.` | Banker-to-advisor handoff |

## What the agent does

- Automate customer intake, identity verification, and routing
- Guide bankers through account opening, investment services, etc.
- Provide real‑time risk assessments and financial research
- Transfer case notes, risk data, and conversation history to advisors

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_FinancialAdvisorPilot`) with instructions and a greeting that lists the sample prompts.
- 12 agent skills, one per operation:
  - `account-onboarding` - "Use when a branch customer asks something like \"Great, let's open a 529 account. Emma was born on March 15, 2019, and her SSN ends in 4321. I'd like to start with a $1,000 initial deposit and set up the $300 monthly contribution\""
  - `advisor-handoff` - Use for banker-to-advisor handoff questions in the Financial Advisor Agent synthetic pilot.
  - `client-review` - Use for client review questions in the Financial Advisor Agent synthetic pilot.
  - `college-cost-projection` - "Use when a branch customer asks something like \"Can you show me what college might cost when Emma turns 18? I want to understand if $300 per month will be enough\""
  - `compliance-check` - Use for compliance checkpoints questions in the Financial Advisor Agent synthetic pilot.
  - `enrollment-checklist` - "Use when a branch customer asks something like \"Can you walk me through what's needed to complete the 529 enrollment? I want to make sure I have all the required documents\""
  - `plan-research` - "Use when a branch customer asks something like \"I'd like to understand what 529 plan options are available. My daughter Emma is 5 years old, and we're in California. We can contribute about $300 per month\""
  - `portfolio-summary` - Use for portfolio context questions in the Financial Advisor Agent synthetic pilot.
  - `recommendation-engine` - Use for advisor-review considerations questions in the Financial Advisor Agent synthetic pilot.
  - `risk-assessment` - "Use when a branch customer asks something like \"I'm 35 years old, our household income is $125,000, and we have about $50,000 in liquid savings. I've done some basic investing before but nothing extensive. We also have a mortgage of about $300,000\""
  - `schedule-followup` - "Use when a branch customer asks something like \"I'd like to schedule a follow-up meeting with a financial advisor to review the investment options in more detail. Can we set something up, preferably Tuesday afternoon? I prefer a Teams call\""
  - `service-intake` - Use for service intake and routing questions in the Financial Advisor Agent synthetic pilot.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_financial-advisor-copilot-controls-and-review.md`
  - `aibast_financial-advisor-copilot-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Financial Advisor Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Delivered smoother, enhanced branch experiences
- Ensured compliance through embedded policy guidance and validation checkpoints
- Elevated the quality of financial guidance with risk insights and contextual financial research
- Improved banker–advisor coordination efforts

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
