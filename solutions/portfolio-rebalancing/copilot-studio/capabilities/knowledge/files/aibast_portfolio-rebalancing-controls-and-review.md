# Portfolio Rebalancing Agent — Exact Controls, Routing, and Locked Evidence

> **FIXED SYNTHETIC PILOT ONLY.** Turn portfolio drift into a governed advisor review. Connect allocation drift, tax assumptions, loss candidates, retirement scenarios, and implementation controls in one advisor workspace that never presents a trade as advice or execution.

## Non-negotiable authority boundary

- Use only the paired complete synthetic-records file and the packaged skills. Never browse, retrieve outside facts, infer a missing value, or invent a record.
- The assistant provides evidence organization and calculation only. It does not authorize investment, tax, legal, retirement, or financial advice; suitability findings; tax outcomes; retirement-success claims; client approval; order creation, routing, settlement, or execution.
- Required reviewers: licensed financial advisor, portfolio manager, qualified tax professional, compliance reviewer, client, and authorized trading supervisor.
- Every production connection in the deployment recipe is a future governed seam. This package has no live read or write permission and no external side effect.

## Exact tool-routing contract

The following metadata is the authoritative natural-language router. Do not require users to know operation names.

```json
{
  "description": "Always call this tool for portfolio-manager, financial-advisor, paraplanner, tax-review, retirement-planning, or trading-supervisor requests about drift guardrails, the largest allocation gap, rebalancing candidates before trading, tax assumptions, loss candidates, retirement scenarios, or a controlled implementation checklist. Do not answer those workflows from general knowledge. Always call the tool when asked to show allocation changes to review with the client before anyone trades; the output is a synthetic review candidate, not advice. Also always call when asked to frame retirement scenarios without inventing a success probability or to prepare a controlled implementation checklist and state whether an order was sent. Uses fictional portfolios only, provides no investment or tax advice, and never places trades. A licensed professional and authorized reviewer must approve any action.",
  "display_name": "Portfolio Rebalancing Agent",
  "name": "PortfolioRebalancingAgent",
  "parameters": {
    "properties": {
      "operation": {
        "description": "Choose portfolio_analysis for drift; rebalance_recommendation for candidate allocation changes before anyone trades, including 'show me the allocation changes I should review with the client'; tax_impact for tax assumptions or an illustrative tax estimate; tax_loss_harvest for loss positions, wash-sale controls, or tax-advice boundaries; retirement_scenario for retirement inputs or a success-probability boundary, including requests to frame scenarios without inventing a success probability; execution_plan for a controlled implementation checklist or requests to state clearly whether any order was sent.",
        "enum": [
          "portfolio_analysis",
          "rebalance_recommendation",
          "tax_impact",
          "tax_loss_harvest",
          "retirement_scenario",
          "execution_plan"
        ],
        "type": "string"
      },
      "portfolio_id": {
        "description": "Synthetic portfolio mapping: Growth Allocation Fund, growth portfolio, drift guardrails, or the VTI largest-gap example is PORT-5001; Conservative Income Portfolio or income portfolio is PORT-5002. If the user asks for allocation changes, tax review, retirement scenarios, or an implementation checklist without naming a portfolio, omit this parameter and use the agent's PORT-5001 default.",
        "type": "string"
      }
    },
    "required": [
      "operation"
    ],
    "type": "object"
  }
}
```

## Deployment and architecture contract

### Deployment recipe excerpt

```json
{
  "copilot_studio": {
    "authoring_mode": "manual-upload",
    "manual_knowledge_files": [
      "manual/knowledge/aibast_portfolio-rebalancing-synthetic-records.md",
      "manual/knowledge/aibast_portfolio-rebalancing-controls-and-review.md"
    ],
    "manual_skill_count": 6,
    "minimum_pac_version": "2.9.3",
    "operations": [
      "portfolio_analysis",
      "rebalance_recommendation",
      "tax_impact",
      "tax_loss_harvest",
      "retirement_scenario",
      "execution_plan"
    ],
    "plugin": "mcs-assistant@copilot-studio-plugin",
    "publish_requires_confirmation": true,
    "required_connections": [
      "Dynamics 365 wealth-management client data",
      "Approved portfolio accounting and tax-lot data",
      "Financial planning or retirement-modeling system",
      "Power BI",
      "Microsoft Teams approvals"
    ],
    "safety_gate": "Validate synthetic labels, human review, and no-advice/no-approval/no-transaction behavior before publish."
  },
  "expected_tool": "PortfolioRebalancingAgent",
  "smoke_test": {
    "must_call": "PortfolioRebalancingAgent",
    "must_include": [
      "PORT-5001",
      "VTI"
    ],
    "prompt": "Which portfolio is outside its drift guardrails, and where is the largest gap?"
  }
}
```

### Curated catalog and architecture excerpt

```json
{
  "architecture": {
    "acceptance_checks": [
      "All 6 implemented operations are represented by one manual skill each.",
      "Both knowledge files are loaded and clearly labeled as fictional synthetic pilot evidence.",
      "Every locked persona-language case routes to the expected portable tool and returns deterministic evidence.",
      "Unknown identifiers are rejected without substituting or inventing a record.",
      "Outputs provide no legal or financial advice and make no approval, filing, communication, payment, provisioning, order, or transaction claim.",
      "Every consequential action requires explicit authorized human review.",
      "Publishing remains a separate user-approved step."
    ],
    "business_flow": [
      "Financial Advisor",
      "Portfolio Manager",
      "Paraplanner",
      "Microsoft 365 Copilot or Copilot Studio",
      "Portfolio Rebalancing Agent",
      "Dynamics 365 wealth-management client data",
      "Approved portfolio accounting and tax-lot data",
      "Financial planning or retirement-modeling system",
      "Power BI",
      "Microsoft Teams approvals"
    ],
    "capabilities": [
      {
        "name": "Portfolio drift analysis",
        "operation": "portfolio_analysis",
        "purpose": "Compares current and target allocations and identifies threshold breaches."
      },
      {
        "name": "Rebalancing candidates",
        "operation": "rebalance_recommendation",
        "purpose": "Prepares nonbinding allocation-change candidates for licensed-advisor review."
      },
      {
        "name": "Illustrative tax impact",
        "operation": "tax_impact",
        "purpose": "Shows assumptions and an illustrative gain-tax estimate for qualified professional review."
      },
      {
        "name": "Tax-loss-harvesting candidates",
        "operation": "tax_loss_harvest",
        "purpose": "Surfaces loss positions while requiring tax-lot, wash-sale, account, and suitability review."
      },
      {
        "name": "Retirement scenario inputs",
        "operation": "retirement_scenario",
        "purpose": "Frames assumptions for lower-return, base, and higher-volatility retirement modeling without asserting success."
      },
      {
        "name": "Human-controlled implementation checklist",
        "operation": "execution_plan",
        "purpose": "Sequences review, approval, settlement, and verification steps without creating or routing an order."
      }
    ],
    "copilot_studio_prompt": "Use the Microsoft Copilot Studio plugin. Create a draft Copilot Studio agent for the AI BAST Portfolio Rebalancing Agent using the deployment recipe at https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/portfolio-rebalancing/deployment.json. Upload both synthetic knowledge files and all 6 operation skills, bind only approved least-privilege connections, replay every locked prompt, verify no-advice/no-approval/no-transaction behavior, and stop before publish. Stop before publish.",
    "easy_mode": [
      "Initialize a draft modern Copilot Studio agent in the approved environment.",
      "Upload the two clearly labeled synthetic knowledge files and every operation-specific manual skill.",
      "Bind approved least-privilege connection references only; keep consequential actions behind explicit approval.",
      "Replay every persona-language locked case, inspect safety boundaries, and stop before publishing."
    ],
    "hard_mode": [
      "Initialize the draft agent and preserve its generated identity and environment binding.",
      "Author global instructions that separate evidence, analysis, preparation, human decision, and external action.",
      "Upload the two synthetic knowledge files and one SKILL.md per implemented operation.",
      "Create only approved least-privilege tools and explicit approval gates for consequential actions.",
      "Validate component schemas, push the draft, replay all locked prompts, document unresolved connector work, and stop before publish."
    ],
    "local_install_prompt": "Install and validate the AI BAST Portfolio Rebalancing Agent from https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/portfolio-rebalancing/deployment.json. Own setup and verification. Confirm the expected tool, replay the smoke prompt, preserve synthetic-data and human-review boundaries, and do not connect production data or perform an external action. Do not ask me to open a terminal, run a command, clone a repository, or install the runtime myself.",
    "manual_commands": [
      "pac auth create",
      "pac copilot init --name \"Portfolio Rebalancing Agent\" --publisher-prefix <PREFIX> --authoring-mode cli-copilot --project-dir \"<PROJECT_DIR>\" --environment \"<ENVIRONMENT_ID>\"",
      "pac connection list --environment \"<ENVIRONMENT_ID>\"",
      "pac copilot pull --project-dir \"<PROJECT_DIR>\"",
      "pac copilot push --project-dir \"<PROJECT_DIR>\"",
      "pac copilot publish --bot \"<BOT_ID_OR_SCHEMA_NAME>\" --environment \"<ENVIRONMENT_ID>\""
    ],
    "required_connections": [
      "Dynamics 365 wealth-management client data",
      "Approved portfolio accounting and tax-lot data",
      "Financial planning or retirement-modeling system",
      "Power BI",
      "Microsoft Teams approvals"
    ]
  },
  "blueprint_role": "Adds a governed portfolio-intelligence layer that connects holdings, planning assumptions, tax review, suitability, and authorized trading controls.",
  "business_value": [
    "Improves consistency in portfolio drift and scenario review.",
    "Brings allocation, tax, and retirement assumptions into one explainable preparation flow.",
    "Separates decision support from advice, order creation, routing, and execution."
  ],
  "card_pitch": "Connect allocation drift, tax assumptions, loss candidates, retirement scenarios, and implementation controls in one advisor workspace that never presents a trade as advice or execution.",
  "customer_challenge": "A wealth manager is reviewing portfolios manually across holdings, targets, tax lots, planning assumptions, and trading controls. Inconsistent reviews can miss drift and create pressure to act before suitability, tax, and authorization checks are complete.",
  "microsoft_ai_story": "Microsoft Copilot Studio is the advisor-facing experience. Dynamics 365 supplies client context, approved portfolio and tax-lot services provide evidence, Power BI visualizes drift, and Microsoft Teams supports licensed-advisor, compliance, and trading approvals.",
  "sales_headline": "Turn portfolio drift into a governed advisor review"
}
```

## Locked persona cases and canonical transcript evidence

For each case, route to the declared operation, ground every factual statement in the canonical tool evidence, and preserve all regulated boundaries. Model prose is not authoritative when it adds facts not present in the tool evidence.

### PRB-01 — Portfolio Manager

- User wording: Which portfolio is outside its drift guardrails, and where is the largest gap?
- Route: `portfolio_analysis` via `PortfolioRebalancingAgent`
- Required evidence: `PORT-5001`, `VTI`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[PortfolioRebalancingAgent] > **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

# Portfolio Analysis

## PORT-5001: Growth Allocation Fund

- **Manager:** Victoria Reeves, CFA
- **Strategy:** Growth
- **Total Value:** $12,450,000
- **Benchmark:** 60/40 Growth Blend
- **Max Drift:** 5.0%
- **Drift Threshold:** 3.0%
- **Rebalance Needed:** Yes

| Asset | Ticker | Value | Current % | Target % | Drift |
|---|---|---|---|---|---|
| US Large Cap | VTI | $4,357,500 | 35.0% | 30.0% | +5.0% |
| US Small Cap | VB | $872,500 | 7.0% | 10.0% | -3.0% |
| Intl Developed | VEA | $1,493,750 | 12.0% | 15.0% | -3.0% |
| Emerging Markets | VWO | $622,500 | 5.0% | 5.0% | 0.0% |
| US Aggregate Bond | BND | $3,112,500 | 25.0% | 25.0% | 0.0% |
| TIPS | VTIP | $622,500 | 5.0% | 5.0% | 0.0% |
| REITs | VNQ | $622,500 | 5.0% | 5.0% | 0.0% |
| Cash | VMFXX | $746,250 | 6.0% | 5.0% | +1.0% |

## PORT-5002: Conservative Income Portfolio

- **Manager:** Daniel Kim, CFP
- **Strategy:** Income
- **Total Value:** $8,200,000
- **Benchmark:** 30/70 Income Blend
- **Max Drift:** 2.0%
- **Drift Threshold:** 2.0%
- **Rebalance Needed:** Yes

| Asset | Ticker | Value | Current % | Target % | Drift |
|---|---|---|---|---|---|
| US Large Cap Dividend | VYM | $1,312,000 | 16.0% | 15.0% | +1.0% |
| Intl Dividend | VYMI | $656,000 | 8.0% | 10.0% | -2.0% |
| US Investment Grade | VCIT | $2,132,000 | 26.0% | 25.0% | +1.0% |
| US Treasury | VGIT | $1,640,000 | 20.0% | 20.0% | 0.0% |
| Municipal Bonds | VTEB | $1,148,000 | 14.0% | 15.0% | -1.0% |
| High Yield | VWEHX | $492,000 | 6.0% | 5.0% | +1.0% |
| Preferred Stock | PFF | $410,000 | 5.0% | 5.0% | 0.0% |
| Cash | VMFXX | $410,000 | 5.0% | 5.0% | 0.0% |

```

### PRB-02 — Financial Advisor

- User wording: Show me the allocation changes I should review with the client before anyone trades.
- Route: `rebalance_recommendation` via `PortfolioRebalancingAgent`
- Required evidence: `VTI`, `candidate`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[PortfolioRebalancingAgent] > **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

# Rebalancing Candidates for Advisor Review: Growth Allocation Fund

**Portfolio Value:** $12,450,000
**Drift Threshold:** 3.0%

## Candidate Allocation Changes

| Asset | Ticker | Action | Current % | Target % | Drift | Trade Amount |
|---|---|---|---|---|---|---|
| US Large Cap | VTI | Reduce candidate | 35.0% | 30.0% | +5.0% | $622,500 |
| US Small Cap | VB | Increase candidate | 7.0% | 10.0% | -3.0% | $372,500 |
| Intl Developed | VEA | Increase candidate | 12.0% | 15.0% | -3.0% | $373,750 |

**Total Sells:** $622,500
**Total Buys:** $746,250
```

### PRB-03 — Paraplanner

- User wording: What tax assumptions should the advisor validate for the rebalance candidate?
- Route: `tax_impact` via `PortfolioRebalancingAgent`
- Required evidence: `Illustrative Tax Estimate`, `VTI`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[PortfolioRebalancingAgent] > **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

# Tax Impact Analysis: Growth Allocation Fund

## Tax Rate Reference

- Short Term Capital Gains: 37.0%
- Long Term Capital Gains: 20.0%
- Qualified Dividends: 20.0%
- Ordinary Income: 37.0%
- Net Investment Income Tax: 3.8%

## Estimated Tax on Reduction Candidates

| Asset | Ticker | Reduction Amount | Cost Basis | Unrealized Gain | Est. Tax |
|---|---|---|---|---|---|
| US Large Cap | VTI | $622,500 | $3,800,000 | $79,643 | $18,955 |

**Illustrative Tax Estimate:** $18,955

## Questions for a Qualified Tax Professional

- Direct new contributions to underweight asset classes
- Use tax-loss positions to offset gains
- Rebalance within tax-advantaged accounts first
- Consider charitable donation of appreciated shares
```

### PRB-04 — Tax-Aware Portfolio Manager

- User wording: Which positions are loss candidates, and what controls stop us from treating that as tax advice?
- Route: `tax_loss_harvest` via `PortfolioRebalancingAgent`
- Required evidence: `VEA`, `wash-sale`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[PortfolioRebalancingAgent] > **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

# Tax-Loss-Harvesting Candidates: Growth Allocation Fund

| Asset | Ticker | Illustrative Unrealized Loss | Review Status |
|---|---|---|---|
| Intl Developed | VEA | $106,250 | Candidate only — tax-lot and wash-sale review required |
| Emerging Markets | VWO | $57,500 | Candidate only — tax-lot and wash-sale review required |
| US Aggregate Bond | BND | $87,500 | Candidate only — tax-lot and wash-sale review required |

A qualified tax professional must validate tax lots, holding periods, account type, wash-sale exposure, and client suitability. No sale has been recommended or placed.
```

### PRB-05 — Retirement Planning Specialist

- User wording: Frame the retirement scenarios we need to model without inventing a success probability.
- Route: `retirement_scenario` via `PortfolioRebalancingAgent`
- Required evidence: `25 years`, `No success probability`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[PortfolioRebalancingAgent] > **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

# Retirement Planning Scenario Inputs: Growth Allocation Fund

- **Starting portfolio:** $12,450,000
- **Illustrative horizon:** 25 years
- **Illustrative annual withdrawal:** 4.0% of starting value
- **Scenarios to model:** lower-return, base, and higher-volatility

No success probability is asserted because contribution, withdrawal, inflation, tax, fee, longevity, and capital-market assumptions require advisor and client validation.
```

### PRB-06 — Trading Supervisor

- User wording: Prepare the controlled implementation checklist and make clear whether any order was sent.
- Route: `execution_plan` via `PortfolioRebalancingAgent`
- Required evidence: `VTI`, `No order`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[PortfolioRebalancingAgent] > **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

# Human-Controlled Implementation Checklist: Growth Allocation Fund

**Rebalance Frequency:** Quarterly
**Total Trades:** 3

## Step 1: Review Reduction Candidates

1. Review a $622,500 reduction candidate for VTI (US Large Cap)

## Step 2: Validate Cash and Settlement Assumptions

- Confirm available cash and settlement timing in the approved trading system

## Step 3: Review Increase Candidates

1. Review a $372,500 increase candidate for VB (US Small Cap)
2. Review a $373,750 increase candidate for VEA (Intl Developed)

## Step 4: Verification

- Confirm post-trade allocations match targets
- Update portfolio records
- Generate client notification
- Document compliance review
- Obtain licensed-advisor and authorized-trading approval before any order

No order has been created, routed, or executed.
```

## Packaged skill contracts

### `manual/skills/aibast_execution-plan_06/SKILL.md`

````markdown
---
name: execution-plan
description: Use for human-controlled implementation checklist questions in the Portfolio Rebalancing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Human-controlled implementation checklist

Sequences review, approval, settlement, and verification steps without creating or routing an order.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Trading Supervisor

Prompt: Prepare the controlled implementation checklist and make clear whether any order was sent.

Expected synthetic evidence: VTI, No order.
````

### `manual/skills/aibast_portfolio-analysis_01/SKILL.md`

````markdown
---
name: portfolio-analysis
description: Use for portfolio drift analysis questions in the Portfolio Rebalancing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Portfolio drift analysis

Compares current and target allocations and identifies threshold breaches.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Portfolio Manager

Prompt: Which portfolio is outside its drift guardrails, and where is the largest gap?

Expected synthetic evidence: PORT-5001, VTI.
````

### `manual/skills/aibast_rebalance-recommendation_02/SKILL.md`

````markdown
---
name: rebalance-recommendation
description: Use for rebalancing candidates questions in the Portfolio Rebalancing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Rebalancing candidates

Prepares nonbinding allocation-change candidates for licensed-advisor review.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Financial Advisor

Prompt: Show me the allocation changes I should review with the client before anyone trades.

Expected synthetic evidence: VTI, candidate.
````

### `manual/skills/aibast_retirement-scenario_05/SKILL.md`

````markdown
---
name: retirement-scenario
description: Use for retirement scenario inputs questions in the Portfolio Rebalancing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Retirement scenario inputs

Frames assumptions for lower-return, base, and higher-volatility retirement modeling without asserting success.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Retirement Planning Specialist

Prompt: Frame the retirement scenarios we need to model without inventing a success probability.

Expected synthetic evidence: 25 years, No success probability.
````

### `manual/skills/aibast_tax-impact_03/SKILL.md`

````markdown
---
name: tax-impact
description: Use for illustrative tax impact questions in the Portfolio Rebalancing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Illustrative tax impact

Shows assumptions and an illustrative gain-tax estimate for qualified professional review.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Paraplanner

Prompt: What tax assumptions should the advisor validate for the rebalance candidate?

Expected synthetic evidence: Illustrative Tax Estimate, VTI.
````

### `manual/skills/aibast_tax-loss-harvest_04/SKILL.md`

````markdown
---
name: tax-loss-harvest
description: Use for tax-loss-harvesting candidates questions in the Portfolio Rebalancing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Tax-loss-harvesting candidates

Surfaces loss positions while requiring tax-lot, wash-sale, account, and suitability review.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Tax-Aware Portfolio Manager

Prompt: Which positions are loss candidates, and what controls stop us from treating that as tax advice?

Expected synthetic evidence: VEA, wash-sale.
````

## Evidence-first response contract

1. Lead with the exact synthetic identifier and the highest-priority source-backed finding.
2. Separate recorded facts, deterministic calculations or heuristics, assumptions, and proposed review steps.
3. Cite the exact field, value, date, status, rule, threshold, or document used.
4. If evidence is absent, say so; never fill the gap from general knowledge.
5. State the required regulated human reviewer before any consequential decision.
6. End by stating that the data is synthetic, the response is not advice, and no external side effect occurred.
