# Staffing Territory Planning Agent

Help staffing sales leaders size their territory, find where demand outruns recruiter coverage, read the competition and labor trends, and walk into the quarter with a draft plan grounded in the numbers.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/staffing-territory-planning/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Regional Sales Directors, Branch Managers, Sales Operations Analysts
- **Industries:** Professional Services, Consulting

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Give me a snapshot of my North Valley territory.` | Regional Sales Director: Territory snapshot |
| `How big is the staffing market in Granite Ridge?` | Regional Sales Director: Market sizing |
| `Where are our biggest coverage gaps?` | Sales Operations Analyst: Coverage gaps |
| `Who are we up against in each metro?` | Branch Manager: Competitive landscape |
| `What labor market trends should I plan around?` | Regional Sales Director: Labor trends |
| `Draft my quarterly territory plan.` | Regional Sales Director: Draft territory plan |

## What the agent does

- Summarizes the territory and sizes each metro's market
- Finds coverage gaps and ranks them by open spend
- Shows competitor share and labor trends by line
- Drafts the quarterly plan for leadership review

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_StaffingTerritoryManualBuild`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `competitive-landscape` - Use when a branch manager asks something like "Who are we up against in each metro"
  - `coverage-gaps` - Use when a sales operations analyst asks something like "Where are our biggest coverage gaps"
  - `labor-trends` - Use when a regional sales director asks something like "What labor market trends should I plan around"
  - `market-sizing` - Use when a regional sales director asks something like "How big is the staffing market in Granite Ridge"
  - `territory-plan` - Use when a regional sales director asks something like "Draft my quarterly territory plan"
  - `territory-snapshot` - Use when a regional sales director asks something like "Give me a snapshot of my North Valley territory"
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_staffing-territory-planning-rules-and-guardrails.md`
  - `aibast_staffing-territory-planning-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Staffing Territory Planning Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Faster, consistent territory reviews
- Recruiter capacity aimed at the biggest gaps
- Plans leadership can act on sooner

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
