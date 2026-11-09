# Maintenance Scheduling Agent

Perform predictive maintenance analysis and scheduling orchestration to prevent unplanned downtime and protect production capacity.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/maintenance-scheduling/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Maintenance Manager, Production Supervisor, Operation Leader
- **Industries:** Manufacturing

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Give me the equipment and technician-capacity picture I should review before the weekly maintenance meeting.` | Review equipment and technician capacity |
| `Which asset signals deserve immediate human review before the next production run?` | Find asset signals needing review |
| `Draft the maintenance candidates with crew, parts, and backup checks, but do not create or dispatch work orders.` | Draft maintenance candidates safely |
| `What synthetic downtime exposure and preventive trade-offs should leadership review?` | Compare downtime trade-offs |

## What the agent does

- Analyze IoT sensor data and predict time-to-failure
- Identify optimal maintenance windows
- Automate crew assignments and parts staging for readiness
- Validate backup equipment availability

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_MaintenanceSchedulingPilot`) with instructions and a greeting that lists the sample prompts.
- 7 agent skills, one per operation:
  - `downtime-analysis` - Use when an operations leader asks for synthetic exposure and preventive trade-offs.
  - `maintenance-calendar` - "Use when an operations leader asks something like \"What does the maintenance calendar look like for the next 30 days\""
  - `optimization-plan` - "Use when an operations leader asks something like \"What long-term changes would cut our maintenance cost and unplanned downtime\""
  - `predictive-alerts` - Use when a production supervisor asks which assets deserve condition review.
  - `schedule-overview` - Use when a maintenance manager asks for equipment condition and technician-capacity context.
  - `work-order-draft` - "Use when a maintenance manager asks something like \"Line up the crew and parts for the machine 7 overhaul so I can approve it\""
  - `work-order-plan` - Use when a maintenance manager asks for windows, technician candidates, parts checks, and backup checks.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_maintenance-scheduling-review-rules.md`
  - `aibast_maintenance-scheduling-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Maintenance Scheduling Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Prevented unplanned downtime and maintained delivery commitments
- Reduced emergency repair costs through proactive scheduling
- Extended equipment lifespan while sustaining quality standards
- Improved production schedule adherence, reducing disruptions

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
