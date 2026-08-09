# Portfolio Rebalancing Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/portfolio_rebalancing_stack/portfolio_rebalancing_agent.py`
- Source SHA-256: `76086d7010b614eee9b9600e10aef69923d0360968e983fab1355c41884e7a2a`
- Expected tool: `PortfolioRebalancingAgent`
- Snapshot behavior: fixed to the packaged source revision; no live connection or current-data claim.

## Complete deterministic source records

The following objects reproduce every packaged identifier, name, value, amount, date, status, rule, threshold, mapping, and relationship used by the agent. Keys and values are exact.

### `PORTFOLIOS`

```json
{
  "PORT-5001": {
    "benchmark": "60/40 Growth Blend",
    "drift_threshold": 3.0,
    "holdings": {
      "Cash": {
        "cost_basis": 746250,
        "current_pct": 6.0,
        "target_pct": 5.0,
        "ticker": "VMFXX",
        "value": 746250
      },
      "Emerging Markets": {
        "cost_basis": 680000,
        "current_pct": 5.0,
        "target_pct": 5.0,
        "ticker": "VWO",
        "value": 622500
      },
      "Intl Developed": {
        "cost_basis": 1600000,
        "current_pct": 12.0,
        "target_pct": 15.0,
        "ticker": "VEA",
        "value": 1493750
      },
      "REITs": {
        "cost_basis": 550000,
        "current_pct": 5.0,
        "target_pct": 5.0,
        "ticker": "VNQ",
        "value": 622500
      },
      "TIPS": {
        "cost_basis": 600000,
        "current_pct": 5.0,
        "target_pct": 5.0,
        "ticker": "VTIP",
        "value": 622500
      },
      "US Aggregate Bond": {
        "cost_basis": 3200000,
        "current_pct": 25.0,
        "target_pct": 25.0,
        "ticker": "BND",
        "value": 3112500
      },
      "US Large Cap": {
        "cost_basis": 3800000,
        "current_pct": 35.0,
        "target_pct": 30.0,
        "ticker": "VTI",
        "value": 4357500
      },
      "US Small Cap": {
        "cost_basis": 750000,
        "current_pct": 7.0,
        "target_pct": 10.0,
        "ticker": "VB",
        "value": 872500
      }
    },
    "manager": "Victoria Reeves, CFA",
    "name": "Growth Allocation Fund",
    "rebalance_frequency": "quarterly",
    "strategy": "growth",
    "total_value": 12450000
  },
  "PORT-5002": {
    "benchmark": "30/70 Income Blend",
    "drift_threshold": 2.0,
    "holdings": {
      "Cash": {
        "cost_basis": 410000,
        "current_pct": 5.0,
        "target_pct": 5.0,
        "ticker": "VMFXX",
        "value": 410000
      },
      "High Yield": {
        "cost_basis": 460000,
        "current_pct": 6.0,
        "target_pct": 5.0,
        "ticker": "VWEHX",
        "value": 492000
      },
      "Intl Dividend": {
        "cost_basis": 700000,
        "current_pct": 8.0,
        "target_pct": 10.0,
        "ticker": "VYMI",
        "value": 656000
      },
      "Municipal Bonds": {
        "cost_basis": 1200000,
        "current_pct": 14.0,
        "target_pct": 15.0,
        "ticker": "VTEB",
        "value": 1148000
      },
      "Preferred Stock": {
        "cost_basis": 420000,
        "current_pct": 5.0,
        "target_pct": 5.0,
        "ticker": "PFF",
        "value": 410000
      },
      "US Investment Grade": {
        "cost_basis": 2250000,
        "current_pct": 26.0,
        "target_pct": 25.0,
        "ticker": "VCIT",
        "value": 2132000
      },
      "US Large Cap Dividend": {
        "cost_basis": 1100000,
        "current_pct": 16.0,
        "target_pct": 15.0,
        "ticker": "VYM",
        "value": 1312000
      },
      "US Treasury": {
        "cost_basis": 1700000,
        "current_pct": 20.0,
        "target_pct": 20.0,
        "ticker": "VGIT",
        "value": 1640000
      }
    },
    "manager": "Daniel Kim, CFP",
    "name": "Conservative Income Portfolio",
    "rebalance_frequency": "semi-annual",
    "strategy": "income",
    "total_value": 8200000
  }
}
```

### `TAX_RATES`

```json
{
  "long_term_capital_gains": 0.2,
  "net_investment_income_tax": 0.038,
  "ordinary_income": 0.37,
  "qualified_dividends": 0.2,
  "short_term_capital_gains": 0.37
}
```

## Locked-case deterministic outputs

These are direct `perform()` results for the locked operation and arguments. Preserve the headings, identifiers, values, and boundary language.

### PRB-01 — Portfolio Manager

- Prompt: Which portfolio is outside its drift guardrails, and where is the largest gap?
- Operation: `portfolio_analysis`
- Arguments: `{"portfolio_id": "PORT-5001"}`
- Required factual anchors: `PORT-5001`, `VTI`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

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

- Prompt: Show me the allocation changes I should review with the client before anyone trades.
- Operation: `rebalance_recommendation`
- Arguments: `{"portfolio_id": "PORT-5001"}`
- Required factual anchors: `VTI`, `candidate`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

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

- Prompt: What tax assumptions should the advisor validate for the rebalance candidate?
- Operation: `tax_impact`
- Arguments: `{"portfolio_id": "PORT-5001"}`
- Required factual anchors: `Illustrative Tax Estimate`, `VTI`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

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

- Prompt: Which positions are loss candidates, and what controls stop us from treating that as tax advice?
- Operation: `tax_loss_harvest`
- Arguments: `{"portfolio_id": "PORT-5001"}`
- Required factual anchors: `VEA`, `wash-sale`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

# Tax-Loss-Harvesting Candidates: Growth Allocation Fund

| Asset | Ticker | Illustrative Unrealized Loss | Review Status |
|---|---|---|---|
| Intl Developed | VEA | $106,250 | Candidate only — tax-lot and wash-sale review required |
| Emerging Markets | VWO | $57,500 | Candidate only — tax-lot and wash-sale review required |
| US Aggregate Bond | BND | $87,500 | Candidate only — tax-lot and wash-sale review required |

A qualified tax professional must validate tax lots, holding periods, account type, wash-sale exposure, and client suitability. No sale has been recommended or placed.
```

### PRB-05 — Retirement Planning Specialist

- Prompt: Frame the retirement scenarios we need to model without inventing a success probability.
- Operation: `retirement_scenario`
- Arguments: `{"portfolio_id": "PORT-5001"}`
- Required factual anchors: `25 years`, `No success probability`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

# Retirement Planning Scenario Inputs: Growth Allocation Fund

- **Starting portfolio:** $12,450,000
- **Illustrative horizon:** 25 years
- **Illustrative annual withdrawal:** 4.0% of starting value
- **Scenarios to model:** lower-return, base, and higher-volatility

No success probability is asserted because contribution, withdrawal, inflation, tax, fee, longevity, and capital-market assumptions require advisor and client validation.
```

### PRB-06 — Trading Supervisor

- Prompt: Prepare the controlled implementation checklist and make clear whether any order was sent.
- Operation: `execution_plan`
- Arguments: `{"portfolio_id": "PORT-5001"}`
- Required factual anchors: `VTI`, `No order`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

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

## Evidence boundary

This snapshot does not authorize investment, tax, legal, retirement, or financial advice; suitability findings; tax outcomes; retirement-success claims; client approval; order creation, routing, settlement, or execution. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
