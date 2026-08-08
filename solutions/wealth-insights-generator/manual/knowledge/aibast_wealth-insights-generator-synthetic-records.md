# Wealth Insights Generator Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/wealth_insights_generator_stack/wealth_insights_generator_agent.py`
- Source SHA-256: `aec5aca3409747d4df2364772c4e92a0a7ae4f94f650d4a0bd7dcd55a5ca2355`
- Expected tool: `WealthInsightsGeneratorAgent`
- Snapshot behavior: fixed to the packaged source revision; no live connection or current-data claim.

## Complete deterministic source records

The following objects reproduce every packaged identifier, name, value, amount, date, status, rule, threshold, mapping, and relationship used by the agent. Keys and values are exact.

### `MARKET_DATA`

```json
{
  "10-Year Treasury": {
    "current": 4.28,
    "dividend_yield": 4.28,
    "pe_ratio": 0,
    "ytd_return": 0
  },
  "Bloomberg US Agg Bond": {
    "current": 98.45,
    "dividend_yield": 4.45,
    "pe_ratio": 0,
    "ytd_return": 1.2
  },
  "Dow Jones Industrial": {
    "current": 39180.5,
    "dividend_yield": 1.82,
    "pe_ratio": 19.8,
    "ytd_return": 3.1
  },
  "Gold (per oz)": {
    "current": 2185.3,
    "dividend_yield": 0,
    "pe_ratio": 0,
    "ytd_return": 8.1
  },
  "MSCI EAFE": {
    "current": 2385.7,
    "dividend_yield": 2.95,
    "pe_ratio": 15.2,
    "ytd_return": 5.5
  },
  "NASDAQ Composite": {
    "current": 16742.15,
    "dividend_yield": 0.72,
    "pe_ratio": 28.5,
    "ytd_return": 6.2
  },
  "S&P 500": {
    "current": 5285.42,
    "dividend_yield": 1.35,
    "pe_ratio": 22.1,
    "ytd_return": 4.8
  }
}
```

### `CLIENT_PORTFOLIOS`

```json
{
  "WM-001": {
    "alpha": 1.1,
    "aum": 8500000,
    "benchmark_return": 4.1,
    "held_away_assets": 620000,
    "last_contact": "2025-02-20",
    "life_events": [
      "Daughter starting college Fall 2025"
    ],
    "name": "Harrison Family Trust",
    "next_review": "2025-04-15",
    "risk_profile": "moderate",
    "strategy": "balanced_growth",
    "ytd_return": 5.2
  },
  "WM-002": {
    "alpha": 1.6,
    "aum": 3200000,
    "benchmark_return": 6.2,
    "held_away_assets": 1100000,
    "last_contact": "2025-03-01",
    "life_events": [
      "Planning practice sale in 2-3 years"
    ],
    "name": "Dr. Anita Rao",
    "next_review": "2025-06-01",
    "risk_profile": "aggressive",
    "strategy": "aggressive_growth",
    "ytd_return": 7.8
  },
  "WM-003": {
    "alpha": 0.3,
    "aum": 12400000,
    "benchmark_return": 1.8,
    "held_away_assets": 1850000,
    "last_contact": "2025-01-15",
    "life_events": [
      "Estate plan revision needed",
      "RMD optimization"
    ],
    "name": "George & Martha Kensington",
    "next_review": "2025-04-01",
    "risk_profile": "conservative",
    "strategy": "capital_preservation",
    "ytd_return": 2.1
  },
  "WM-004": {
    "alpha": -0.2,
    "aum": 5700000,
    "benchmark_return": 4.1,
    "held_away_assets": 900000,
    "last_contact": "2025-02-10",
    "life_events": [
      "Considering real estate exit strategy"
    ],
    "name": "Tidewater Ventures LLC",
    "next_review": "2025-05-15",
    "risk_profile": "moderate_aggressive",
    "strategy": "alternative_focused",
    "ytd_return": 3.9
  }
}
```

### `PERFORMANCE_BENCHMARKS`

```json
{
  "aggressive_growth": {
    "1yr": 18.2,
    "3yr": 10.5,
    "5yr": 11.8,
    "benchmark": "80/20 Growth"
  },
  "alternative_focused": {
    "1yr": 8.4,
    "3yr": 6.1,
    "5yr": 7.2,
    "benchmark": "HFRI Fund Weighted"
  },
  "balanced_growth": {
    "1yr": 12.5,
    "3yr": 8.2,
    "5yr": 9.1,
    "benchmark": "60/40 Balanced"
  },
  "capital_preservation": {
    "1yr": 5.8,
    "3yr": 3.9,
    "5yr": 4.5,
    "benchmark": "20/80 Conservative"
  }
}
```

### `OPPORTUNITY_SIGNALS`

```json
[
  {
    "action": "Schedule meeting to review education funding plan",
    "client": "WM-001",
    "description": "529 plan contribution deadline approaching; daughter's college enrollment Fall 2025",
    "priority": "high",
    "type": "education_funding"
  },
  {
    "action": "Engage tax advisor for sale structuring",
    "client": "WM-002",
    "description": "Practice sale in 2-3 years; begin pre-sale tax and asset protection planning",
    "priority": "high",
    "type": "liquidity_event"
  },
  {
    "action": "Coordinate with estate attorney for plan update",
    "client": "WM-003",
    "description": "Estate plan last updated 2019; tax law changes require revision",
    "priority": "medium",
    "type": "estate_planning"
  },
  {
    "action": "Model QCD scenarios vs standard RMD",
    "client": "WM-003",
    "description": "Client age 74; review Qualified Charitable Distribution strategy",
    "priority": "medium",
    "type": "rmd_optimization"
  },
  {
    "action": "Prepare alternative manager review presentation",
    "client": "WM-004",
    "description": "Portfolio underperforming benchmark; alternative allocation review needed",
    "priority": "medium",
    "type": "reallocation"
  }
]
```

## Locked-case deterministic outputs

These are direct `perform()` results for the locked operation and arguments. Preserve the headings, identifiers, values, and boundary language.

### WIG-01 — Advisory Director

- Prompt: Give me the fixed market snapshot for the morning huddle and label whether it is current data.
- Operation: `market_brief`
- Arguments: `{}`
- Required factual anchors: `NASDAQ Composite`, `Fixed Synthetic`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Fixed Synthetic Market Snapshot

## Index Performance

| Index | Current | YTD Return | P/E | Yield |
|---|---|---|---|---|
| S&P 500 | 5,285.42 | +4.8% | 22.1 | 1.35% |
| NASDAQ Composite | 16,742.15 | +6.2% | 28.5 | 0.72% |
| Dow Jones Industrial | 39,180.50 | +3.1% | 19.8 | 1.82% |
| MSCI EAFE | 2,385.70 | +5.5% | 15.2 | 2.95% |
| Bloomberg US Agg Bond | 98.45 | +1.2% | N/A | 4.45% |
| 10-Year Treasury | 4.28 | +0.0% | N/A | 4.28% |
| Gold (per oz) | 2,185.30 | +8.1% | N/A | N/A |

## Key Observations

- Equity markets continue positive YTD momentum; NASDAQ leading at +6.2%
- International developed markets (EAFE) outperforming on weaker dollar
- Fixed income subdued with 10-Year Treasury at 4.28%
- Gold rally continues (+8.1% YTD) on geopolitical uncertainty

**Total Practice AUM:** $29,800,000
```

### WIG-02 — Wealth Advisor

- Prompt: Which household has the largest held-away opportunity and what life event needs validation?
- Operation: `client_insights`
- Arguments: `{}`
- Required factual anchors: `WM-003`, `Held Away`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Client Insights Report

**Total AUM:** $29,800,000
**Average Alpha:** 0.7%

| Client | Managed AUM | Held Away | Strategy | YTD | Alpha | Health | Next Review |
|---|---|---|---|---|---|---|---|
| Harrison Family Trust (WM-001) | $8,500,000 | $620,000 | Balanced Growth | +5.2% | +1.1% | Strong | 2025-04-15 |
| Dr. Anita Rao (WM-002) | $3,200,000 | $1,100,000 | Aggressive Growth | +7.8% | +1.6% | Strong | 2025-06-01 |
| George & Martha Kensington (WM-003) | $12,400,000 | $1,850,000 | Capital Preservation | +2.1% | +0.3% | Satisfactory | 2025-04-01 |
| Tidewater Ventures LLC (WM-004) | $5,700,000 | $900,000 | Alternative Focused | +3.9% | -0.2% | Attention Needed | 2025-05-15 |

## Life Events & Planning Needs

### Harrison Family Trust (WM-001)

- Daughter starting college Fall 2025

### Dr. Anita Rao (WM-002)

- Planning practice sale in 2-3 years

### George & Martha Kensington (WM-003)

- Estate plan revision needed
- RMD optimization

### Tidewater Ventures LLC (WM-004)

- Considering real estate exit strategy

```

### WIG-03 — Relationship Manager

- Prompt: Which clients have high-priority planning signals for advisor review?
- Operation: `opportunity_alerts`
- Arguments: `{}`
- Required factual anchors: `Harrison Family Trust`, `Dr. Anita Rao`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Opportunity Alerts

## High Priority

### Harrison Family Trust — Education Funding

- **Description:** 529 plan contribution deadline approaching; daughter's college enrollment Fall 2025
- **Recommended Action:** Schedule meeting to review education funding plan

### Dr. Anita Rao — Liquidity Event

- **Description:** Practice sale in 2-3 years; begin pre-sale tax and asset protection planning
- **Recommended Action:** Engage tax advisor for sale structuring

## Medium Priority

### George & Martha Kensington — Estate Planning

- **Description:** Estate plan last updated 2019; tax law changes require revision
- **Recommended Action:** Coordinate with estate attorney for plan update

### George & Martha Kensington — Rmd Optimization

- **Description:** Client age 74; review Qualified Charitable Distribution strategy
- **Recommended Action:** Model QCD scenarios vs standard RMD

### Tidewater Ventures LLC — Reallocation

- **Description:** Portfolio underperforming benchmark; alternative allocation review needed
- **Recommended Action:** Prepare alternative manager review presentation

**Total Alerts:** 5
```

### WIG-04 — Portfolio Strategist

- Prompt: Which synthetic client is below its benchmark, and what does the attribution label say?
- Operation: `performance_attribution`
- Arguments: `{}`
- Required factual anchors: `Tidewater Ventures`, `Underperformance`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Performance Attribution

## Strategy Benchmarks

| Strategy | Benchmark | 1-Year | 3-Year | 5-Year |
|---|---|---|---|---|
| Balanced Growth | 60/40 Balanced | 12.5% | 8.2% | 9.1% |
| Aggressive Growth | 80/20 Growth | 18.2% | 10.5% | 11.8% |
| Capital Preservation | 20/80 Conservative | 5.8% | 3.9% | 4.5% |
| Alternative Focused | HFRI Fund Weighted | 8.4% | 6.1% | 7.2% |

## Client Performance vs Benchmark

| Client | Strategy | YTD | Benchmark | Alpha | Attribution |
|---|---|---|---|---|---|
| Harrison Family Trust | Balanced Growth | +5.2% | +4.1% | +1.1% | Selection + Allocation |
| Dr. Anita Rao | Aggressive Growth | +7.8% | +6.2% | +1.6% | Selection + Allocation |
| George & Martha Kensington | Capital Preservation | +2.1% | +1.8% | +0.3% | Allocation |
| Tidewater Ventures LLC | Alternative Focused | +3.9% | +4.1% | -0.2% | Underperformance |

**AUM-Weighted Alpha:** +0.57%
```

### WIG-05 — Wealth Advisor

- Prompt: Prepare my review brief for the Kensington household without turning it into advice or outreach.
- Operation: `meeting_brief`
- Arguments: `{"client_id": "WM-003"}`
- Required factual anchors: `George & Martha Kensington`, `preparation material`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Draft Advisor Meeting Brief: George & Martha Kensington

- **Managed AUM:** $12,400,000
- **Held-away assets in synthetic snapshot:** $1,850,000
- **Risk profile:** Conservative
- **Next review:** 2025-04-01

## Validate With the Client

- Estate plan revision needed
- RMD optimization

## Discussion Prompts

- Estate plan last updated 2019; tax law changes require revision
- Client age 74; review Qualified Charitable Distribution strategy

This is preparation material, not a recommendation or customer communication. The advisor must validate facts, suitability, consent, and approved disclosures.
```

## Evidence boundary

This snapshot does not authorize current-market claims; investment, tax, legal, estate, retirement, or financial advice; suitability findings; performance promises; outreach, CRM changes, live aggregation, opportunity creation, orders, or transactions. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
