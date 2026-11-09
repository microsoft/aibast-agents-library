# Ask HR Agent

Provide self-service HR inquiry handling that transforms the process from a manual ticket-based system to intelligent, automated resolutions.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/ask-hr/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Employees, Managers, HR Operations Staff
- **Industries:** Cross-Industry

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What does my fictional leave snapshot show, and what notice rules should I review?` | Employee: Leave-balance explanation |
| `Preview five vacation days for September 14 through September 18; do not submit anything.` | Employee: Time-off draft preview |
| `Explain the published parental-leave example without deciding whether I qualify or asking for family details.` | Employee: Parental-leave policy guidance |
| `Summarize the fictional health-plan snapshot and tell me what the benefits administrator must verify.` | Employee: Health-plan policy explanation |
| `What does the sample remote-work policy say, without inferring why an employee asked?` | Manager: Remote-work policy guidance |
| `Show the fictional benefits snapshot without estimating compensation or making an eligibility decision.` | HR Operations Specialist: Benefits snapshot explanation |

## What the agent does

- Give employees instant, personalized answers based on their profile, location, and benefits
- Surface relevant policy guidance and upcoming deadlines
- Automate time‑off requests, form pre‑population, and approval routing
- Reduce dependency on HR staff for routine questions and tasks

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_AskHRPilot`) with instructions and a greeting that lists the sample prompts.
- 8 agent skills, one per operation:
  - `benefits-summary` - Use when HR operations needs a concise fictional profile summary without estimating compensation or deciding eligibility.
  - `health-insurance` - Use when an employee asks what the fictional plan snapshot says and what must be verified with benefits staff.
  - `leave-balance` - Use when an employee asks for the fictional balance snapshot and published time-off rules.
  - `parental-leave` - Use for published leave-policy questions without inferring a family or medical circumstance or deciding eligibility.
  - `reminders` - "Use when an employee asks something like \"Is there anything else I should know about my benefits or time off before the end of the year\""
  - `remote-work` - Use when an employee or manager asks for published remote-work rules without inferring a sensitive circumstance.
  - `submit-time-off` - Use when an employee wants to preview dates and projected balance before using the approved submission workflow.
  - `time-off-check` - "Use when an employee asks something like \"I want to take 5 days off next month for a family trip. Is that okay with my balance and the policy\""
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_ask-hr-rules-and-guardrails.md`
  - `aibast_ask-hr-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Ask HR Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Resolved common HR inquiries instantly, without tickets
- Eliminated bottlenecks in time‑off management with automated routing and notifications
- Reduced HR workloads, freeing up time for higher-value work
- Improved the employee experience through clear, consistent guidance

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
