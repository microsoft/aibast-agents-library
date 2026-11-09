# Customer Escalations Agent

Automate back-office contact center escalation workflows to deliver better service outcomes and retention rates.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/ai-customer-assistant/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Back-Office Agent, Escalation Manager, Quality Analyst
- **Industries:** Cross-Industry, Contact Center

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `I just inherited the export-error escalation. Give me the full brief before I respond.` | Back-Office Agent: Inquiry triage brief |
| `What approved guidance should I review for the customer who cannot export a long analytics range?` | Back-Office Agent: Knowledge evidence search |
| `The SSO migration case is urgent. Which queue and response target does our rulebook recommend?` | Escalation Manager: Escalation routing review |
| `What does the latest service-quality snapshot say, and which signals need human review?` | Quality Analyst: Quality and satisfaction review |

## What the agent does

- Instantly retrieve full customer profile, interaction history, and open issues
- Classify intent, detect multi‑issue cases, and score escalation risk
- Match cases to playbooks and verify policy/eligibility in real time

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_CustomerEscalationsPilot`) with instructions and a greeting that lists the sample prompts.
- 8 agent skills, one per operation:
  - `escalation-routing` - Use when an escalation manager asks which team and SLA rule apply, without executing the route.
  - `follow-up-plan` - "Use when a back-office agent asks something like \"Schedule the follow-up for Jennifer Adams and prepare the response email\""
  - `handle-inquiry` - Use when a back-office agent asks what is happening on a specific case and what should be reviewed next.
  - `interaction-summary` - "Use when an escalation manager asks something like \"Summarize the Jennifer Adams interaction for me\""
  - `knowledge-search` - Use when a support agent needs the most relevant approved article and resolution steps for an inquiry.
  - `prepare-actions` - "Use when a back-office agent asks something like \"Go ahead and get the refund and the credit ready for Jennifer Adams\""
  - `recommend-resolution` - "Use when a back-office agent asks something like \"Jennifer Adams was charged $149 for an add-on she never ordered. What should I do to resolve this\""
  - `satisfaction-survey` - Use when a quality analyst asks for the fictional CSAT distribution and recurring service themes.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_ai-customer-assistant-rules-and-guardrails.md`
  - `aibast_ai-customer-assistant-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Customer Escalations Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reach a successful resolution in minutes, saving FTEs time
- Reduce retention risk and number of future escalations
- Drive higher satisfaction and loyalty with customers
- Flag issues with product team based on similar cases

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
