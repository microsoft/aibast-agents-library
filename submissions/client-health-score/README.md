# Client Health Score Agent

Automate client portfolio health monitoring and planning to improve client relationships, protect revenue, and optimize financial performance.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/client-health-score/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Client Success Leaders, Account Manager
- **Industries:** Professional Services, Consulting

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which relationships are healthy, at risk, or critical, and where should my team focus first?` | Segment the portfolio |
| `What engagement signals are weakening across the portfolio, especially executive contact and escalations?` | Inspect engagement weakness |
| `Which client satisfaction trends are moving the wrong way, and what evidence supports that view?` | Review satisfaction movement |
| `Give me the accounts that need intervention now, the risk drivers, and the first recovery actions.` | Prioritize intervention |
| `Build the stakeholder map and executive engagement plan for each account that needs a turnaround.` | Prepare turnaround playbooks |

## What the agent does

- Implement real-time health scoring and churn probability modeling
- Segment accounts into critical, at-risk, and healthy categories for prioritization
- Develop tailored retention playbooks, stakeholder mapping, and executive engagement plans

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_ClientHealthScorePilot`) with instructions and a greeting that lists the sample prompts.
- 8 agent skills, one per operation:
  - `at-risk-client-prioritization` - Explains risk drivers and recovery actions for fictional accounts.
  - `client-engagement-analysis` - Finds fictional executive-contact, escalation, billing, and utilization signals.
  - `client-portfolio-health-dashboard` - Segments the fictional client portfolio and shows scenario churn indicators.
  - `client-retention-playbook` - Builds fictional stakeholder maps and approval-gated executive engagement plans.
  - `client-satisfaction-trend` - Compares the packaged fictional quarterly satisfaction history.
  - `qbr-summary` - "Use when a client success leader asks something like \"Wrap up my quarterly business review prep with a summary of the portfolio, the risks and the retention plan\""
  - `risk-analysis` - "Use when an account manager asks something like \"What's driving TechCorp's health score down so fast\""
  - `stakeholder-outreach` - "Use when an account manager asks something like \"Who is the first executive we need to reach at TechCorp, and in what order should we meet the others\""
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_client-health-retention-playbook.md`
  - `aibast_client-health-synthetic-portfolio.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Client Health Score Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Protected revenue by safeguarding high-value relationships through structured turnaround plans
- Identified relationship opportunities and improved client satisfaction
- Enabled proactive intervention and portfolio stabilization, reducing churn risk

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
