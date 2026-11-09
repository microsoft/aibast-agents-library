# Field Service Dispatch Agent

Automates field service scheduling and coordination to reduce response times, optimize resource use, and improve customer satisfaction.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/field-service-dispatch/quest.html), Microsoft's catalog of industry agent templates.

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What does tomorrow's job list look like by crew, and which crews are on standby?` | Field Operations Manager: Job dashboard |
| `I need help optimizing our field technician schedules for tomorrow. We have 15 service calls.` | Service Director: Schedule optimization |
| `Yes, show me Crew A-1's detailed route` | Dispatch Coordinator: Crew route and skill match |
| `URGENT: Major power outage downtown - 1,200 customers affected. Dispatch emergency crews now!` | Emergency Duty Manager: Emergency response draft |
| `Yes, give me live updates and customer impact` | Control Room Operator: Live outage status |
| `The outage is resolved. Show me the post-incident review and how we prevent the next one.` | Reliability Engineer: Post-incident review |
| `Yes, create the work orders and show me the monthly operations report` | Operations Analyst: Work orders and monthly report |

## What the agent does

- Detect outages via real-time IoT sensors, prioritizing critical facilities
- Dispatch nearest crews and reroute in-progress jobs automatically
- Provide real-time dashboards and automated customer notifications
- Optimize inventory staging and handle crew assignments

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_FieldServiceDispatchPilot`) with instructions and a greeting that lists the sample prompts.
- 7 agent skills, one per operation:
  - `field-service-dispatch-dispatch-dashboard` - Use when a Field Operations Manager asks to prioritize the read-only service-request queue.
  - `field-service-dispatch-emergency-response` - Use when a Emergency Duty Manager asks to prepare an approval-gated emergency response draft.
  - `field-service-dispatch-incident-status` - "Use when a Control Room Operator asks for the live outage status."
  - `field-service-dispatch-post-incident-review` - "Use when a Reliability Engineer asks for the post-incident review."
  - `field-service-dispatch-route-optimization` - Use when a Service Director asks to compare zone capacity without rerouting.
  - `field-service-dispatch-technician-assignment` - Use when a Dispatch Coordinator asks to recommend a skill-matched candidate for human review.
  - `field-service-dispatch-work-orders-report` - "Use when a Operations Analyst asks for the work orders and monthly report."
- 2 knowledge files holding the synthetic records and operating rules:
  - `field-service-dispatch-rules-and-controls.md`
  - `field-service-dispatch-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Field Service Dispatch Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reduced emergency response times
- Improved first-time fix rates and eliminated redundant travel
- Delivered proactive customer updates, improving satisfaction
- Protected revenue and demonstrated operational excellence during crisis events

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
