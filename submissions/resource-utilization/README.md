# Resource Utilization Agent

Provide intelligent resource analysis and recommendations to maximize billable utilization and reduce costs.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/resource-utilization/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Operations Leader, Resource Manager, Finance Director
- **Industries:** Professional Services, Consulting

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Where are we under target today, and which parts of the workforce are sitting available?` | See utilization and availability |
| `What capacity is coming free, and how does it line up with the opportunities expected over the next quarter?` | Compare capacity with demand |
| `Show me who is on the bench, the skills we are carrying, and the cost exposure we need to address.` | Understand the bench |
| `Which available consultants fit the strongest pipeline needs, and who still needs another path?` | Match people to pipeline |
| `Give me an upskilling and internal-innovation plan for the people we cannot place directly, including the business case.` | Plan capability building |

## What the agent does

- Implement real-time utilization tracking and capacity analysis
- Give data-driven recommendations for balancing skills and capacity
- Match consultants to projects and high-probability opportunities
- Identify consultants for upskilling pathways and innovation initiatives

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_ResourceUtilizationPilot`) with instructions and a greeting that lists the sample prompts.
- 8 agent skills, one per operation:
  - `executive-summary` - "Use when an operations leader asks something like \"Create a tracking dashboard and summarize what we accomplished\""
  - `financial-impact` - "Use when a finance director asks something like \"What is the complete financial impact of this plan by month, quarter, and year\""
  - `optimization-plan` - "Use when an operations leader asks something like \"Our board wants utilization up to 85 by next quarter. We have 200 consultants currently at 72 billable. I need an optimization plan that shows how we get there without compromising quality\""
  - `pipeline-staffing-recommendation` - Matches qualified fictional bench consultants to pipeline needs.
  - `professional-services-bench-analysis` - Inventories fictional bench skills and carrying-cost scenarios.
  - `strategic-workforce-plan` - Models fictional upskilling and internal-innovation pathways.
  - `workforce-capacity-forecast` - Compares near-term project endings with weighted fictional demand.
  - `workforce-utilization-dashboard` - Shows current fictional utilization, targets, and availability.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_resource-pipeline-and-workforce-rules.md`
  - `aibast_resource-synthetic-roster.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Resource Utilization Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reduced bench costs and improved billable utilization beyond targets
- Accelerated project staffing while maintaining quality standards
- Enabled proactive workforce planning and strategic capability building

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
