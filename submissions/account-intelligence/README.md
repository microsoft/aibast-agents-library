# Account Intelligence Agent

Automate account research and strategy planning to help sellers prepare faster, win more, and elevate deal quality.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/account-intelligence/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Account Executive, Sales Director, Customer Success Manager
- **Industries:** Cross-Industry

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Prepare a synthetic Acme Corporation account overview and show the evidence that deserves seller attention.` | Review the account |
| `Map the synthetic Acme buying committee and show the relationship gaps without creating outreach tasks.` | Map the buying committee |
| `Compare the synthetic competitor signals and positioning considerations for Acme Corporation.` | Compare competitor signals |
| `Draft persona-specific talking points for the synthetic Acme meeting; do not send messages.` | Draft meeting talking points |
| `Assess the synthetic Acme deal risks and mitigation options without changing a forecast or CRM record.` | Assess deal risks |
| `Prepare a concise synthetic Acme pre-meeting briefing and review checklist.` | Prepare the executive briefing |

## What the agent does

- Get a single unified view of account signals across diverse sources
- Create stakeholder maps with influence scores/relationship gaps
- Deliver competitive insights and risk mitigation strategies
- Produced talking points and pre-meeting checklists

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_AccountIntelligenceManualBuild`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `account-intelligence-account-overview` - Create a synthetic Acme account overview and identify evidence that merits seller attention.
  - `account-intelligence-competitive-intel` - Compare synthetic competitor signals and positioning considerations for Acme.
  - `account-intelligence-executive-briefing` - Prepare a concise synthetic pre-meeting briefing and review checklist.
  - `account-intelligence-risk-assessment` - Assess synthetic deal risks and mitigation options without changing a forecast or CRM record.
  - `account-intelligence-stakeholder-map` - Map the synthetic buying committee and relationship gaps without creating outreach tasks.
  - `account-intelligence-value-messaging` - Draft persona-specific talking points for human review; do not send messages.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_account-intelligence-operating-rules.md`
  - `aibast_account-intelligence-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Account Intelligence Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Improved win rates via better stakeholder coverage and competitive positioning
- Reduced account research time from hours to minutes
- Elevated deal quality with tailored messaging and risk mitigation
- Enabled real-time team alignment with automated alerts and updates

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
