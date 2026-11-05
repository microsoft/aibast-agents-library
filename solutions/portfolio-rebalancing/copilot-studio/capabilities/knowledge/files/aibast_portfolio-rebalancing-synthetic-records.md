# Portfolio Rebalancing Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/portfolio_rebalancing_stack/portfolio_rebalancing_agent.py`
- Source SHA-256: `0c22d8185e82d91cd34ec848031de12f55c437824964e19b9686167e4ac3ce61`
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

### `CLIENT_PORTFOLIOS`

```json
{
  "CLIENT-001": {
    "age": 55,
    "buys": [
      {
        "action": "Buy investment-grade and municipal bonds",
        "amount": 180600,
        "note": "Tax-exempt munis"
      },
      {
        "action": "Buy Treasury securities",
        "amount": 28200,
        "note": "State-tax free"
      }
    ],
    "current_pct": {
      "Cash": 2,
      "Equities": 80,
      "Fixed Income": 18
    },
    "federal_bracket": 0.32,
    "harvest_lots": [
      {
        "holding": "US Growth Equity Fund",
        "loss": 21400,
        "proceeds": 128000,
        "substitute": "US Total Market Index Fund"
      },
      {
        "holding": "International Equity Fund",
        "loss": 13700,
        "proceeds": 101000,
        "substitute": "Developed Markets Index Fund"
      }
    ],
    "market_drop_pct": 15,
    "monte_carlo": {
      "median": 4010000,
      "p10": 2920000,
      "p90": 5470000,
      "success_new_pct": 94,
      "success_old_pct": 78
    },
    "name": "Pre-retiree client portfolio",
    "other_sell_lots": [
      {
        "gain": 0,
        "holding": "US Large Cap Value Fund",
        "proceeds": 32000
      }
    ],
    "projection": [
      [
        "Current",
        1740000
      ],
      [
        "Year 5",
        2480000
      ],
      [
        "Year 10",
        4010000
      ],
      [
        "Year 20",
        3840000
      ]
    ],
    "risk_new": {
      "crash_impact": 199000,
      "delay_risk": "LOW",
      "max_drawdown": 20,
      "recovery_years": 2.1,
      "sharpe": 0.92,
      "volatility": 10.4
    },
    "risk_old": {
      "crash_impact": 348000,
      "delay_risk": "HIGH",
      "max_drawdown": 35,
      "recovery_years": 4.2,
      "sharpe": 0.68,
      "volatility": 18.2
    },
    "risk_tolerance": "Moderate (currently too aggressive)",
    "social_security": 42000,
    "target_pct": {
      "Cash": 5,
      "Equities": 65,
      "Fixed Income": 30
    },
    "total_value": 1740000,
    "trading_costs": 847,
    "value_before": 2000000,
    "weeks": [
      [
        "Week 1: Tax-Loss Harvesting",
        [
          "Sell harvest lots (${harvest:,}) and rebalancing lot (${other:,})",
          "Document cost basis for tax reporting",
          "Buy substitute securities (wash-sale compliant)"
        ]
      ],
      [
        "Week 2: Fixed Income Build",
        [
          "Purchase municipal bonds ($125,000) - tax-exempt",
          "Add Treasury ladder ($28,200) - state-tax free",
          "Monitor for wash-sale compliance"
        ]
      ],
      [
        "Week 3: Dollar-Cost Average",
        [
          "Remaining bond purchases ($55,600)",
          "Rebalance within tax-advantaged accounts",
          "No tax impact on IRA reallocations"
        ]
      ],
      [
        "Week 4: Final Positioning",
        [
          "Cash reserve +$52,200 (to 5%)",
          "Portfolio monitoring activation",
          "Client review meeting to schedule"
        ]
      ]
    ],
    "withdrawal_rate": 0.04,
    "years_to_retirement": 10
  }
}
```

## Demo scenario: CLIENT-001 pre-retiree portfolio after a market correction (default record)

The guided conversation, in order: "My client has a $2M portfolio that's drifted significantly after the recent market correction. Can you review it?" (`portfolio_analysis`); "Yes, show me the rebalancing strategy with tax optimization" (`rebalance_recommendation`); "Yes, show me the implementation timeline" (`execution_plan`); "Yes, show me the 10-year retirement projection" (`retirement_scenario`); "Yes, compare the risk profiles" (`risk_comparison`); "Yes, prepare the client presentation and summarize what we accomplished" (`client_summary`). PORT-5001 and PORT-5002 are only used when named.

| Fact | Value |
|---|---|
| Portfolio | $2.0M before a 15% market drop, $1.74M now (-13%) |
| Allocation | current 80% equities / 18% fixed income / 2% cash; target 65/30/5 (equities +15, fixed income -12, cash -3) |
| Client profile | age 55, retiring in 10 years, moderate risk tolerance (currently too aggressive), 32% federal bracket |
| Trades (computed from $1.74M) | sell equities $261,000 = harvest lots $229,000 (realized losses $35,100) + rebalancing lot $32,000 at cost; buy investment-grade and municipal bonds $180,600 + Treasury securities $28,200 (fixed income $208,800); cash reserve +$52,200 |
| Tax-loss harvesting | $35,100 x 32% = $11,232 illustrative tax savings; wash sale compliant via substitute securities (US Growth Equity Fund -> US Total Market Index Fund; International Equity Fund -> Developed Markets Index Fund) |
| 4-week timeline | Week 1 harvest sells; Week 2 municipal bonds $125,000 + Treasury ladder $28,200; Week 3 remaining bonds $55,600; Week 4 cash reserve +$52,200; trading costs $847 (0.18% of $469,800 traded); net benefit $10,385 |
| 10-year projection | $1.74M now, Year 5 $2.48M, Year 10 $4.01M (4% withdrawal $160,400), Year 20 $3.84M ($153,600); synthetic Monte Carlo illustration 94% vs 78% (+16 pts), median $4.01M, P10 $2.92M, P90 $5.47M; Social Security +$42,000 -> $202,400/year |
| Risk comparison | volatility 18.2% -> 10.4% (43% lower); max drawdown -35% -> -20%; recovery 4.2 -> 2.1 years (50% faster); Sharpe 0.68 -> 0.92 (+0.24); 2008-style crash -$348K -> -$199K; retirement delay risk HIGH -> LOW |
| Session summary | value delivered: tax savings $11,232; risk reduction 43%; success +16 pts; projected $4.01M; presentation outline only; nothing saved, shared or scheduled; no order created |

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

### PRB-07 — Financial Advisor

- Prompt: Compare the risk profile of my client's old allocation with the new one.
- Operation: `risk_comparison`
- Arguments: `{}`
- Required factual anchors: `18.2%`, `10.4%`, `2008-style crash`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

The new allocation reduces volatility, and with it sequence-of-returns risk, by 43%: critical for a pre-retiree.

# Risk Comparison Analysis: CLIENT-001

| Risk Metric | Old (80/18/2) | New (65/30/5) |
|---|---|---|
| Annual volatility | 18.2% | 10.4% |
| Max drawdown | -35% | -20% |
| Recovery time | 4.2 years | 2.1 years |
| Sharpe ratio | 0.68 | 0.92 |

**Sequence Risk Protection:**
- 2008-style crash impact: -$348K -> -$199K
- Recovery to breakeven: 4.2 yrs -> 2.1 yrs (50% faster)
- Retirement delay risk: HIGH -> LOW

**Why This Matters at Age 55:** less time to recover from major losses; approaching the withdrawal phase; income stability over growth optimization.

Shall I prepare the client presentation with recommendations?
```

### PRB-08 — Financial Advisor

- Prompt: Prepare the client presentation and summarize what we accomplished for my client.
- Operation: `client_summary`
- Arguments: `{}`
- Required factual anchors: `Session Summary`, `$11,232`, `Nothing has been saved, shared or scheduled`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.

# Session Summary: CLIENT-001

- Portfolio analyzed: $1.74M post-correction, 80% equity (too aggressive)
- Rebalancing designed: 65/30/5 target allocation, $261,000 in sells
- Tax optimization: $11,232 in tax-loss harvesting savings identified
- Implementation planned: 4-week execution minimizing market impact
- Projection modeled: $4.01M at retirement (94% simulated success)
- Risk reduced: 43% lower volatility, 50% faster recovery time

**Value Delivered:**

| Benefit | Amount |
|---|---|
| Tax savings | $11,232 |
| Risk reduction | 43% |
| Success probability | +16 pts |
| Projected retirement value | $4.01M |

**Client presentation outline (draft for you to build in PowerPoint):** 1) where the portfolio stands after the correction; 2) the recommended allocation and trades; 3) tax-loss harvesting value; 4) 10-year projection; 5) risk comparison; 6) next steps and approvals.

Nothing has been saved, shared or scheduled: save the presentation and book the client review meeting (for example tomorrow at 2 PM) yourself. No order has been created.
```

## Evidence boundary

This snapshot does not authorize investment, tax, legal, retirement, or financial advice; suitability findings; tax outcomes; retirement-success claims; client approval; order creation, routing, settlement, or execution. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
