# Win/Loss Analysis Agent

Automates competitive deal analysis to uncover root causes, improve win rates, and guide strategic sales enablement.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/win-loss-analysis/quest.html), Microsoft's catalog of industry agent templates.

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Compare the bundled synthetic Q3 and Q2 win and loss patterns and show where the decline is concentrated.` | Compare win and loss patterns |
| `Identify the evidence-backed synthetic loss drivers and buyer feedback themes that enablement should review.` | Find the root causes |
| `Draft counter-strategy and talk-track options from the synthetic loss evidence for enablement review.` | Draft counter-strategies |
| `Model synthetic intervention scenarios without presenting them as realized or committed revenue.` | Model value scenarios |
| `Draft a board-level synthetic win and loss narrative with all investment and performance values labeled as scenarios.` | Draft the board narrative |
| `Summarize the synthetic findings and candidate next steps without activating programs or approvals.` | Summarize next steps |

## What the agent does

- Aggregate and analyze historical deal data for trend identification
- Synthesize buyer feedback and competitor patterns into actionable insights
- Develop targeted counter-strategies and enablement playbooks for reps
- Model revenue recovery scenarios for leadership decision-making

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_WinLossAnalysisPilot`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `win-loss-analysis-action-summary` - Summarize findings and candidate next steps without activating programs or approvals.
  - `win-loss-analysis-board-presentation` - Draft a board-level narrative that labels all exact values as synthetic scenarios.
  - `win-loss-analysis-counter-strategies` - Draft counter-strategy and talk-track options for enablement review.
  - `win-loss-analysis-revenue-impact` - Model synthetic intervention scenarios without presenting them as realized or committed revenue.
  - `win-loss-analysis-root-cause-analysis` - Identify evidence-backed synthetic loss drivers and buyer-feedback themes.
  - `win-loss-analysis-win-loss-overview` - Compare the bundled synthetic Q3 and Q2 win/loss patterns.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_win-loss-analysis-operating-rules.md`
  - `aibast_win-loss-analysis-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Win/Loss Analysis Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Identified top loss drivers and prioritized addressable gaps
- Equipped sales teams with data-driven objection handling and competitive talk tracks
- Reversed declining win rates through targeted interventions
- Delivered board-ready insights and recovery plans in hours, not weeks

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
