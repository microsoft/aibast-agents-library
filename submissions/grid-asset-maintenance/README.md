# Predictive Asset Maintenance Intelligence Agent

Help an electricity distribution company maintain its grid by condition, not by calendar: rank transformers, switchgear, cables and overhead lines by 30, 90 and 180-day failure probability, draft preventive work orders with the parts and crew they need, check field records before the asset register changes, and show the replacement plan and capital by year.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/grid-asset-maintenance/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Reliability Engineer, Maintenance Planner, Asset Manager
- **Industries:** Energy and Utilities

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which of our grid assets are most likely to fail in the next 90 days, and what's driving it?` | Reliability Engineer: Risk ranking |
| `Get a preventive work order ready for the Millbrook transformer, with the parts and crew we need. Don't raise it yet.` | Maintenance Planner: Work order draft |
| `The Mill Lane cable joint job closed yesterday. Is the field record complete enough to update the asset register?` | Reliability Engineer: Register update check |
| `For the investment committee, how healthy is the fleet and what replacements and capital do we need over the next few years?` | Director of Asset Management: Replacement plan |

## What the agent does

- Rank assets by 30, 90 and 180-day failure risk
- Draft work orders with history, parts and crew
- Hold register updates until the record is complete
- Show fleet health and replacement capital by year

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_PredictiveAssetManualBuild`) with instructions and a greeting that lists the sample prompts.
- 4 agent skills, one per operation:
  - `register-update` - Use when someone asks whether a completed maintenance job's field record is complete enough to update the asset register or fixed asset register.
  - `replacement-plan` - Use when an asset manager or director asks about fleet health by asset class, the replacement pipeline, or capital needed by year.
  - `risk-ranking` - Use when a reliability engineer or planner asks which grid assets are most likely to fail in the next 30, 90 or 180 days, what is driving the risk, or what the maintenance backlog should be.
  - `work-order-draft` - Use when a maintenance planner asks to prepare a preventive work order for an asset, with its history, materials, long-lead parts, crew or outage; returns a draft that is never raised.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_grid-asset-maintenance-rules-and-guardrails.md`
  - `aibast_grid-asset-maintenance-synthetic-records.md`
- 1 tools:
  - `Work IQ MCP Server` - 

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Predictive Asset Maintenance Intelligence Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Sent crews to the riskiest assets first
- Ordered long-lead parts in time for the work
- Kept the asset register complete and current
- Built its replacement plan on condition data

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-29.
