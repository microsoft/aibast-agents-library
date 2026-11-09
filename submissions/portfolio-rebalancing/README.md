# Portfolio Rebalancing Agent

Provide intelligent, automated portfolio rebalancing that streamlines manual reviews and improves wealth management outcomes.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/portfolio-rebalancing/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Financial Advisor, Portfolio Manager, Paraplanner
- **Industries:** Capital Markets

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which portfolio is outside its drift guardrails, and where is the largest gap?` | Portfolio drift analysis |
| `Show me the allocation changes I should review with the client before anyone trades.` | Rebalancing candidates |
| `What tax assumptions should the advisor validate for the rebalance candidate?` | Illustrative tax impact |
| `Which positions are loss candidates, and what controls stop us from treating that as tax advice?` | Tax-loss-harvesting candidates |
| `Frame the retirement scenarios we need to model without inventing a success probability.` | Retirement scenario inputs |
| `Prepare the controlled implementation checklist and make clear whether any order was sent.` | Human-controlled implementation checklist |

## What the agent does

- Provide a single, actionable view of each client’s portfolio
- Automate drift detection and tax-loss harvesting to surface timely opportunities
- Runs retirement projection modeling and calculates success
- Generate presentations and implementation plans

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_PortfolioRebalancingPilot`) with instructions and a greeting that lists the sample prompts.
- 8 agent skills, one per operation:
  - `client-summary` - "Use when a financial advisor asks something like \"Prepare the client presentation and summarize what we accomplished for my client\""
  - `execution-plan` - Use for human-controlled implementation checklist questions in the Portfolio Rebalancing Agent synthetic pilot.
  - `portfolio-analysis` - Use for portfolio drift analysis questions in the Portfolio Rebalancing Agent synthetic pilot.
  - `rebalance-recommendation` - Use for rebalancing candidates questions in the Portfolio Rebalancing Agent synthetic pilot.
  - `retirement-scenario` - Use for retirement scenario inputs questions in the Portfolio Rebalancing Agent synthetic pilot.
  - `risk-comparison` - "Use when a financial advisor asks something like \"Compare the risk profile of my client's old allocation with the new one\""
  - `tax-impact` - Use for illustrative tax impact questions in the Portfolio Rebalancing Agent synthetic pilot.
  - `tax-loss-harvest` - Use for tax-loss-harvesting candidates questions in the Portfolio Rebalancing Agent synthetic pilot.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_portfolio-rebalancing-controls-and-review.md`
  - `aibast_portfolio-rebalancing-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Portfolio Rebalancing Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Increased retirement success probability via timely rebalancing
- Reduced portfolio review time dramatically
- Captured tax savings per client during market corrections
- Improved client satisfaction with proactive, personalized, and audit-ready recommendations

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
