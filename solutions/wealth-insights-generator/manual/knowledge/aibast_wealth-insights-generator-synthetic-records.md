# Wealth Insights Generator Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/wealth_insights_generator_stack/wealth_insights_generator_agent.py`
- Source SHA-256: `230447b12117df1be4b4a2c6327d924a2b243139a896e8335cd4aaf885cc0109`
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
    "life_events": [
      "Daughter starting college next fall"
    ],
    "name": "Harrison Family Trust",
    "next_review": "Q2 review",
    "risk_profile": "moderate",
    "strategy": "balanced_growth",
    "ytd_return": 5.2
  },
  "WM-002": {
    "alpha": 1.6,
    "aum": 3200000,
    "benchmark_return": 6.2,
    "held_away_assets": 1100000,
    "life_events": [
      "Planning practice sale in 2-3 years"
    ],
    "name": "Dr. Anita Rao",
    "next_review": "Q3 review",
    "risk_profile": "aggressive",
    "strategy": "aggressive_growth",
    "ytd_return": 7.8
  },
  "WM-003": {
    "alpha": 0.3,
    "aum": 12400000,
    "benchmark_return": 1.8,
    "held_away_assets": 1850000,
    "life_events": [
      "Estate plan revision needed",
      "RMD optimization"
    ],
    "name": "George & Martha Kensington",
    "next_review": "Q2 review",
    "risk_profile": "conservative",
    "strategy": "capital_preservation",
    "ytd_return": 2.1
  },
  "WM-004": {
    "alpha": -0.2,
    "aum": 5700000,
    "benchmark_return": 4.1,
    "held_away_assets": 900000,
    "life_events": [
      "Considering real estate exit strategy"
    ],
    "name": "Tidewater Ventures LLC",
    "next_review": "Q3 review",
    "risk_profile": "moderate_aggressive",
    "strategy": "alternative_focused",
    "ytd_return": 3.9
  },
  "WM-005": {
    "alias": "morrison",
    "alpha": 0.5,
    "aum": 12000000,
    "benchmark_return": 4.1,
    "concentration": {
      "asset": "Company stock",
      "rsu_vesting_next_quarter": 800000,
      "sector": "tech",
      "value": 8000000
    },
    "contact": "David Morrison",
    "conversation_trigger": "David mentioned 5-year retirement timeline, showed concern about tech layoffs",
    "held_away_assets": 16000000,
    "held_away_breakdown": [
      [
        "Company stock",
        8000000,
        "Diversification"
      ],
      [
        "Real estate",
        6000000,
        "1031 exchange"
      ],
      [
        "Cash",
        2000000,
        "Yield enhancement"
      ]
    ],
    "life_events": [
      "5-year retirement timeline",
      "Concern about tech layoffs",
      "$800K RSUs vesting next quarter"
    ],
    "name": "Morrison Family",
    "next_review": "Retirement readiness review (proposed)",
    "risk_profile": "moderate",
    "strategy": "balanced_growth",
    "ytd_return": 4.6
  },
  "WM-006": {
    "alias": "chen",
    "alpha": 0.3,
    "aum": 6400000,
    "benchmark_return": 4.1,
    "held_away_assets": 3800000,
    "life_events": [
      "Business sale closing this year"
    ],
    "name": "Chen Family",
    "next_review": "Call this week",
    "risk_profile": "moderate",
    "strategy": "balanced_growth",
    "ytd_return": 4.4
  },
  "WM-007": {
    "alias": "thompson",
    "alpha": 0.6,
    "aum": 9100000,
    "benchmark_return": 1.8,
    "held_away_assets": 5200000,
    "life_events": [
      "Next generation joining the family office"
    ],
    "name": "Thompson Family",
    "next_review": "Introduction next week",
    "risk_profile": "conservative",
    "strategy": "capital_preservation",
    "ytd_return": 2.4
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
    "action": "Personal call this week to propose a retirement readiness review",
    "client": "WM-005",
    "description": "Single tech stock is 29% of family wealth with $800K RSUs vesting next quarter; 5-year retirement timeline",
    "impact_usd": 48000,
    "priority": "high",
    "readiness": "High",
    "type": "concentration_and_retirement"
  },
  {
    "action": "Schedule meeting to review education funding plan",
    "client": "WM-001",
    "description": "529 plan contribution deadline approaching; daughter's college enrollment next fall",
    "impact_usd": 6000,
    "priority": "high",
    "readiness": "High",
    "type": "education_funding"
  },
  {
    "action": "Engage tax advisor for sale structuring",
    "client": "WM-002",
    "description": "Practice sale in 2-3 years; begin pre-sale tax and asset protection planning",
    "impact_usd": 22000,
    "priority": "high",
    "readiness": "Medium",
    "type": "liquidity_event"
  },
  {
    "action": "Call this week to discuss proceeds planning",
    "client": "WM-006",
    "description": "Business sale closing this year; proceeds likely held away",
    "impact_usd": 23000,
    "priority": "medium",
    "readiness": "High",
    "type": "liquidity_event"
  },
  {
    "action": "Introduction meeting next week",
    "client": "WM-007",
    "description": "Next generation joining the family office; $5.2M held away",
    "impact_usd": 31000,
    "priority": "medium",
    "readiness": "Medium",
    "type": "wallet_share"
  },
  {
    "action": "Coordinate with estate attorney for plan update",
    "client": "WM-003",
    "description": "Estate plan last updated 2019; tax law changes require revision",
    "impact_usd": 12000,
    "priority": "medium",
    "readiness": "Medium",
    "type": "estate_planning"
  },
  {
    "action": "Model QCD scenarios vs standard RMD",
    "client": "WM-003",
    "description": "Client age 74; review Qualified Charitable Distribution strategy",
    "impact_usd": 4000,
    "priority": "medium",
    "readiness": "Medium",
    "type": "rmd_optimization"
  },
  {
    "action": "Prepare alternative manager review presentation",
    "client": "WM-004",
    "description": "Portfolio underperforming benchmark; alternative allocation review needed",
    "impact_usd": 9000,
    "priority": "medium",
    "readiness": "Low",
    "type": "reallocation"
  }
]
```

### `BOOK_SUMMARY`

```json
{
  "assets_in_play": 840000000,
  "aum_managed": 2400000000,
  "families": 85,
  "held_away_est": 4100000000,
  "segment": "UHNW",
  "target_wallet_share_pct": 55,
  "top_opportunity": "WM-005"
}
```

### `OPPORTUNITY_CATEGORIES`

```json
[
  [
    "Wallet share growth",
    34,
    4200000
  ],
  [
    "Planning gaps",
    28,
    1800000
  ],
  [
    "Life events",
    12,
    2100000
  ]
]
```

### `PLANNING_GAPS`

```json
{
  "WM-005": {
    "advisory_fee_pct": 0.6,
    "areas": [
      [
        "Investment",
        "Strong (concentration to diversify)",
        "High"
      ],
      [
        "Estate planning",
        "Outdated (8 yrs)",
        "High"
      ],
      [
        "Tax planning",
        "Reactive",
        "High"
      ]
    ],
    "estate_gaps": [
      "Will from 2016 (pre-TCJA)",
      "No living trust",
      "Beneficiaries unchecked"
    ],
    "tax_opportunities": [
      [
        "Stock diversification",
        240000,
        "over 5 years"
      ],
      [
        "RSU coordination",
        45000,
        "per year"
      ],
      [
        "Charitable giving",
        80000,
        "one time"
      ]
    ],
    "transfer_usd": 8000000
  }
}
```

### `ENGAGEMENT_PLANS`

```json
{
  "WM-005": {
    "key_messages": [
      "5 years to do this right",
      "Manage taxes while reducing risk",
      "Estate plan needs checkup"
    ],
    "phase_1": [
      "Personal call (reconnect on retirement)",
      "Share article (stock concentration risk)",
      "Propose meeting (\"Retirement readiness review\")"
    ],
    "phase_2_topics": [
      [
        "Retirement vision",
        "Timeline confirmation"
      ],
      [
        "Legacy goals",
        "Family intentions"
      ],
      [
        "Company outlook",
        "Confidence level"
      ]
    ],
    "touches": [
      "Client dinner next month",
      "Intro to estate attorney partner"
    ]
  }
}
```

### `OUTREACH_MATERIALS`

```json
{
  "WM-005": {
    "agenda": [
      [
        "0-10 min",
        "Personal catch-up"
      ],
      [
        "10-25 min",
        "Retirement vision"
      ],
      [
        "25-40 min",
        "Current situation review"
      ],
      [
        "40-55 min",
        "Opportunities presentation"
      ],
      [
        "55-60 min",
        "Next steps agreement"
      ]
    ],
    "body": "David, I've been thinking about your 5-year retirement horizon. With market changes and your significant company stock position, let's map out a retirement readiness review - allocation alignment, tax-smart RSU strategies, and estate plan review. No pressure, just strategic conversation. Available in the next two weeks?",
    "subject": "Catching Up + Retirement Readiness Thoughts"
  }
}
```

### `IMMEDIATE_ACTIONS`

```json
[
  [
    "Send Morrison email",
    "today"
  ],
  [
    "Chen call",
    "this week"
  ],
  [
    "Thompson intro",
    "next week"
  ]
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

**Named-client AUM in this snapshot:** $57,300,000
```

### WIG-02 — Wealth Advisor

- Prompt: Which household has the largest held-away opportunity and what life event needs validation?
- Operation: `client_insights`
- Arguments: `{}`
- Required factual anchors: `WM-005`, `Held Away`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Client Insights Report

**Named-client AUM:** $57,300,000
**Average Alpha:** 0.6%
**Largest held-away opportunity:** Morrison Family (WM-005)

| Client | Managed AUM | Held Away | Strategy | YTD | Alpha | Health | Next Review |
|---|---|---|---|---|---|---|---|
| Harrison Family Trust (WM-001) | $8,500,000 | $620,000 | Balanced Growth | +5.2% | +1.1% | Strong | Q2 review |
| Dr. Anita Rao (WM-002) | $3,200,000 | $1,100,000 | Aggressive Growth | +7.8% | +1.6% | Strong | Q3 review |
| George & Martha Kensington (WM-003) | $12,400,000 | $1,850,000 | Capital Preservation | +2.1% | +0.3% | Satisfactory | Q2 review |
| Tidewater Ventures LLC (WM-004) | $5,700,000 | $900,000 | Alternative Focused | +3.9% | -0.2% | Attention Needed | Q3 review |
| Morrison Family (WM-005) | $12,000,000 | $16,000,000 | Balanced Growth | +4.6% | +0.5% | Satisfactory | Retirement readiness review (proposed) |
| Chen Family (WM-006) | $6,400,000 | $3,800,000 | Balanced Growth | +4.4% | +0.3% | Satisfactory | Call this week |
| Thompson Family (WM-007) | $9,100,000 | $5,200,000 | Capital Preservation | +2.4% | +0.6% | Satisfactory | Introduction next week |

## Life Events & Planning Needs

- **Harrison Family Trust (WM-001):** Daughter starting college next fall
- **Dr. Anita Rao (WM-002):** Planning practice sale in 2-3 years
- **George & Martha Kensington (WM-003):** Estate plan revision needed; RMD optimization
- **Tidewater Ventures LLC (WM-004):** Considering real estate exit strategy
- **Morrison Family (WM-005):** 5-year retirement timeline; Concern about tech layoffs; $800K RSUs vesting next quarter
- **Chen Family (WM-006):** Business sale closing this year
- **Thompson Family (WM-007):** Next generation joining the family office
```

### WIG-03 — Relationship Manager

- Prompt: Which clients have high-priority planning signals for advisor review?
- Operation: `opportunity_alerts`
- Arguments: `{}`
- Required factual anchors: `Harrison Family Trust`, `Dr. Anita Rao`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Opportunity Alerts (ranked by relationship readiness, then impact)

## High Priority

| Client | Signal | Est. annual impact | Readiness | Recommended action |
|---|---|---|---|---|
| Morrison Family | Single tech stock is 29% of family wealth with $800K RSUs vesting next quarter; 5-year retirement timeline | $48,000 | High | Personal call this week to propose a retirement readiness review |
| Harrison Family Trust | 529 plan contribution deadline approaching; daughter's college enrollment next fall | $6,000 | High | Schedule meeting to review education funding plan |
| Dr. Anita Rao | Practice sale in 2-3 years; begin pre-sale tax and asset protection planning | $22,000 | Medium | Engage tax advisor for sale structuring |

## Medium Priority

| Client | Signal | Est. annual impact | Readiness | Recommended action |
|---|---|---|---|---|
| Chen Family | Business sale closing this year; proceeds likely held away | $23,000 | High | Call this week to discuss proceeds planning |
| Thompson Family | Next generation joining the family office; $5.2M held away | $31,000 | Medium | Introduction meeting next week |
| George & Martha Kensington | Estate plan last updated 2019; tax law changes require revision | $12,000 | Medium | Coordinate with estate attorney for plan update |
| George & Martha Kensington | Client age 74; review Qualified Charitable Distribution strategy | $4,000 | Medium | Model QCD scenarios vs standard RMD |
| Tidewater Ventures LLC | Portfolio underperforming benchmark; alternative allocation review needed | $9,000 | Low | Prepare alternative manager review presentation |

**Total Alerts:** 8
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
| Morrison Family | Balanced Growth | +4.6% | +4.1% | +0.5% | Allocation |
| Chen Family | Balanced Growth | +4.4% | +4.1% | +0.3% | Allocation |
| Thompson Family | Capital Preservation | +2.4% | +1.8% | +0.6% | Allocation |

**AUM-Weighted Alpha:** +0.53%
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
- **Next review:** Q2 review

## Validate With the Client

- Estate plan revision needed
- RMD optimization

## Discussion Prompts

- Estate plan last updated 2019; tax law changes require revision
- Client age 74; review Qualified Charitable Distribution strategy

This is preparation material, not a recommendation or customer communication. The advisor must validate facts, suitability, consent, and approved disclosures.
```

### WIG-06 — Wealth Advisor

- Prompt: Generate wealth insights for my top clients and identify opportunities to deepen relationships.
- Operation: `book_insights`
- Arguments: `{}`
- Required factual anchors: `85 families`, `37% (target 55%)`, `$4.2M/year`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Wealth Insights: 85 UHNW Families

Analyzed 85 UHNW clients - $840M in held-away assets in play across wallet share and planning gaps; $8.1M/year revenue potential.

| Metric | Value |
|---|---|
| Total clients | 85 families |
| AUM managed | $2.4B |
| Held-away (est.) | $4.1B |
| Wallet share | 37% (target 55%) |

**Opportunities:**

| Category | Clients | Revenue Potential |
|---|---|---|
| Wallet share growth | 34 | $4.2M/year |
| Planning gaps | 28 | $1.8M/year |
| Life events | 12 | $2.1M/year |

**Top Opportunity:** Morrison Family - $8M outside stock concentration

Source: [Portfolio + Wealth Estimates] Agents: WealthAnalyticsAgent, OpportunityIdentificationAgent

**Next step:** dive into the Morrison Family?
```

### WIG-07 — Wealth Advisor

- Prompt: What planning gaps does the Morrison Family have?
- Operation: `planning_gaps`
- Arguments: `{"client_id": "WM-005"}`
- Required factual anchors: `Outdated (8 yrs)`, `pre-TCJA`, `+$48K annual fees`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Planning Gaps: Morrison Family (WM-005)

3 areas need attention.

| Area | Status | Priority |
|---|---|---|
| Investment | Strong (concentration to diversify) | High |
| Estate planning | Outdated (8 yrs) | High |
| Tax planning | Reactive | High |

**Estate Gaps:** Will from 2016 (pre-TCJA), No living trust, Beneficiaries unchecked

**Tax Opportunities:** Stock diversification $240K+ (over 5 years); RSU coordination $45K (per year); Charitable giving $80K (one time)

**Service Expansion:** +$48K annual fees on a $8M transfer; about $545K of 5-year tax opportunities, 10x+ the annual fee.

Estimates for advisor review; validate with the client's tax and estate professionals.

Source: [Planning System] Agents: PlanningGapAgent, ClientInsightsAgent

**Next step:** develop the engagement strategy?
```

### WIG-08 — Relationship Manager

- Prompt: How should I approach the Morrison relationship expansion?
- Operation: `engagement_strategy`
- Arguments: `{"client_id": "WM-005"}`
- Required factual anchors: `Phase 1`, `Retirement readiness review`, `Legacy goals`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Engagement Strategy: Morrison Family Relationship Expansion

**Phase 1: Immediate (This Week)**

- Personal call (reconnect on retirement)
- Share article (stock concentration risk)
- Propose meeting ("Retirement readiness review")

**Phase 2: Discovery Meeting (2 Weeks)**

| Topic | Focus |
|---|---|
| Retirement vision | Timeline confirmation |
| Legacy goals | Family intentions |
| Company outlook | Confidence level |

**Key Messages:** "5 years to do this right", "Manage taxes while reducing risk", "Estate plan needs checkup"

**Touches:** Client dinner next month, Intro to estate attorney partner

Source: [CRM + Engagement] Agents: RelationshipStrategyAgent

**Next step:** draft the outreach?
```

### WIG-09 — Advisory Director

- Prompt: Give me the complete wealth insights summary with the immediate actions.
- Operation: `insights_summary`
- Arguments: `{}`
- Required factual anchors: `$8.1M`, `Chen call (this week)`, `Thompson intro (next week)`

```text
> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Wealth Insights Summary: $8.1M Revenue Opportunity

| Analysis | Result |
|---|---|
| Clients analyzed | 85 UHNW families |
| Total AUM | $2.4B |
| Wallet share | 37% -> 55% target |

**Pipeline:**

| Category | Revenue |
|---|---|
| Wallet share growth | $4.2M/year |
| Planning gaps | $1.8M/year |
| Life events | $2.1M/year |
| **Total** | **$8.1M/year** |

**Morrison:** $8M transfer, $48K/year fees, $240K+ tax savings

**Immediate Actions:** Send Morrison email (today), Chen call (this week), Thompson intro (next week)

Revenue figures are synthetic estimates for advisor planning; no outreach has been sent.

Source: [Portfolio + CRM + Planning] Agents: WealthAnalyticsAgent, RelationshipStrategyAgent
```

## Evidence boundary

This snapshot does not authorize current-market claims; investment, tax, legal, estate, retirement, or financial advice; suitability findings; performance promises; outreach, CRM changes, live aggregation, opportunity creation, orders, or transactions. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
