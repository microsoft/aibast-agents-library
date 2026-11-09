# Underwriting Support Agent

Automate commercial underwriting analysis to accelerate evaluations, improve pricing accuracy, and maintain full compliance.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/underwriting-support/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Underwriter, Risk Analyst
- **Industries:** Financial Services

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which submission needs the most experienced underwriter, and why?` | Submission risk evaluation |
| `Walk me through the rating factors and loss evidence for Riverside without issuing a quote.` | Illustrative pricing-factor review |
| `Which applications are outside a stated guideline or missing required evidence?` | Guideline and document alignment |
| `Prepare the exception file I need to review and state whether any coverage decision was made.` | Exception review queue |
| `Help me evaluate this commercial insurance application and tell me what is missing.` | Underwriter: Submission Review |
| `Show me the full risk assessment and the loss history for the Midwest Manufacturing submission.` | Risk Analyst: Risk Assessment |
| `What coverage structure, endorsements, and subjectivities do you recommend for Midwest Manufacturing?` | Underwriter: Coverage Structure |
| `Check compliance and authority before we finalize the Midwest Manufacturing recommendation.` | Senior Underwriter: Compliance Check |
| `Generate the complete underwriting summary for the Midwest Manufacturing submission.` | Senior Underwriter: Underwriting Summary |

## What the agent does

- Summarize key submission data and validate missing information
- Score risk across hazard, financial stability, loss experience, and operations
- Recommend pricing ranges and apply standard adjustments
- Identify coverage needs, limitations, and compliance considerations

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_UnderwritingSupportPilot`) with instructions and a greeting that lists the sample prompts.
- 9 agent skills, one per operation:
  - `compliance-check` - "Use when a senior underwriter asks something like \"Check compliance and authority before we finalize the Midwest Manufacturing recommendation\""
  - `coverage-structure` - "Use when an underwriter asks something like \"What coverage structure, endorsements, and subjectivities do you recommend for Midwest Manufacturing\""
  - `exception-review` - Use for exception review queue questions in the Underwriting Support Agent synthetic pilot.
  - `guideline-check` - Use for guideline and document alignment questions in the Underwriting Support Agent synthetic pilot.
  - `pricing-recommendation` - Use for illustrative pricing-factor review questions in the Underwriting Support Agent synthetic pilot.
  - `risk-assessment` - "Use when a risk analyst asks something like \"Show me the full risk assessment and the loss history for the Midwest Manufacturing submission\""
  - `risk-evaluation` - Use for submission risk evaluation questions in the Underwriting Support Agent synthetic pilot.
  - `submission-review` - "Use when an underwriter asks something like \"Help me evaluate this commercial insurance application and tell me what is missing\""
  - `underwriting-summary` - "Use when a senior underwriter asks something like \"Generate the complete underwriting summary for the Midwest Manufacturing submission\""
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_underwriting-support-controls-and-review.md`
  - `aibast_underwriting-support-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Underwriting Support Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reduced evaluation time with automated analysis and risk scoring
- Enhanced pricing consistency through standardized rating factors
- Strengthened compliance by checking authority limits and guideline alignment
- Increased underwriting capacity by freeing time for complex cases

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
