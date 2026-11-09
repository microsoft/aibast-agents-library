# Product Line Optimization Agent

Provide intelligent production capacity analysis and optimization planning to boost throughput and efficiency while maintaining quality.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/product-line-optimization/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Plant Manager, Production Engineer, Operations Director
- **Industries:** Manufacturing

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which production line needs attention today, and what is driving the loss?` | See which production line needs attention |
| `Where is the bottleneck on each line, and which station should the plant team address first?` | Find the constraining station |
| `Give me the practical options to improve throughput without hiding the quality tradeoffs.` | Compare throughput improvement options |
| `Translate the current line performance into a day, swing, and night shift plan.` | Build the three-shift production plan |

## What the agent does

- Perform real-time analysis on key production metrics across stations and lines
- Identify and propose solutions to  throughput constraints
- Plan to optimize processes, crew allocation, and investments
- Scale capacity to meet the seasonal demand surge

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_ProductLineOptimizationPilot`) with instructions and a greeting that lists the sample prompts.
- 4 agent skills, one per operation:
  - `constraining-station-identification` - Routes the Production Engineer prompt "Where is the bottleneck on each line, and which station should the plant team address first?" using cycle-versus-takt and defect evidence.
  - `day-swing-night-production-plan` - Routes the Plant Manager prompt "Translate the current line performance into a day, swing, and night shift plan." using the packaged schedule and staffing records.
  - `improvement-option-comparison` - Routes the Operations Director prompt "Give me the practical options to improve throughput without hiding the quality tradeoffs." with three evidence-backed choices per line.
  - `plant-wide-operating-health-review` - Routes the Plant Manager prompt "Which production line needs attention today, and what is driving the loss?" by ranking all three synthetic lines and naming the drivers.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_production-line-synthetic-records.md`
  - `aibast_production-optimization-rules.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Product Line Optimization Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Increased line capacity and reduced cycle times through targeted optimizations
- Higher Overall Equipment Effectiveness (OEE) and throughput, exceeding holiday targets
- Consistent high quality and increased ROI on investments

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
