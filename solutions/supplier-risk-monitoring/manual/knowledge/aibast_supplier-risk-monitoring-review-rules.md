# Supply Risk Monitoring Agent — Exact Review Rules and Locked Outputs

> **SYNTHETIC PILOT RULES.** Use this file with the complete synthetic source
> records. It contains the exact deterministic operation outputs captured by the
> source agent. These outputs are evidence and recommendations, not completed
> operational side effects or customer outcomes.

## Locked case routing

| Case | Persona | Operation | Exact prompt | Required deterministic evidence |
|---|---|---|---|---|
| SR-01 | Supply Chain Director | `risk_dashboard` | Where is supplier exposure concentrated, and which relationships should leadership review first? | `TechnoCore Semiconductor`; `HIGH RISK` |
| SR-02 | Procurement Manager | `supplier_scorecard` | Explain why TechnoCore is elevated and show me the evidence by risk dimension. | `SUP-101`; `Geopolitical` |
| SR-03 | Supply Chain Director | `disruption_alerts` | Which recorded disruptions could threaten continuity, and what exposure should we validate? | `SUP-104`; `force majeure` |
| SR-04 | Procurement Manager | `alternative_sourcing` | Compare backup sourcing options for review, but do not contact, qualify, select, or order from any supplier. | `Kansai Passive Components`; `No supplier was contacted` |
| SR-05 | Procurement Manager | `mitigation_plan` | What mitigation strategies do you recommend for each of our semiconductor suppliers? | `Increase safety stock`; `MONITOR CLOSELY`; `OPPORTUNITY` |
| SR-06 | Supply Chain Director | `financial_impact` | What would those mitigations cost us, and is the investment worth it? | `$1.098M`; `65% reduction`; `Break-even` |
| SR-07 | Supply Chain Director | `implementation_roadmap` | Lay out a twelve-month plan for putting these protections in place. | `Phase 1 (Months 1-3)`; `60% Taiwan / 40% Korea`; `Risk score target` |
| SR-08 | Procurement Manager | `monitoring_plan` | How would we keep watching these suppliers after the plan is in place? | `Alert Thresholds`; `Automated Actions`; `Early warning` |

Demo walk-through order: monitor risks for the critical semiconductor suppliers (`risk_dashboard`), detailed risk assessment (`supplier_scorecard`), mitigation strategies (`mitigation_plan`), financial impact (`financial_impact`), implementation roadmap (`implementation_roadmap`), monitoring approach (`monitoring_plan`).

## Deterministic calculation and interpretation rules

- Composite health uses the source weighting: quality 30%, delivery 25%, financial 25%, and geopolitical 20%.
- Risk levels are HIGH at or above 7.0, MEDIUM at or above 5.0, and LOW below 5.0.
- Money is shown short: $840K, $1.098M, $12.4M.
- Exposure reduction is (current - after) / current, rounded; break-even probability is total investment / current exposure, truncated to one decimal.
- Incident evidence is a fixed synthetic record and must be validated against approved supplier, logistics, quality, financial, and external-risk sources.
- Backup qualification labels are synthetic source states, not completed procurement decisions.

## Exact deterministic operation outputs

### `risk_dashboard` — Supplier risk dashboard (semiconductor exposure)

Use for monitoring the critical semiconductor suppliers in Taiwan, China, and Malaysia: supply exposure by country and the risk categories monitored.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Supplier Risk Dashboard — Semiconductor Supply Chain

> Fixed synthetic snapshot; no live financial, logistics, ERP, or supplier feed was queried.

Risk profiles for your semiconductor supply chain across Taiwan, China, Malaysia: geopolitical, financial, operational, quality, and logistics risk.

**Supply Chain Exposure:**
- Taiwan: 40% of MCU supply (TechnoCore)
- China: 35% of passive components (Shenzhen Electronics)
- Malaysia: 25% of power ICs (Malaysia Semicon)

**Risk Categories Monitored:**
- Geopolitical stability
- Financial health
- Operational capacity
- Quality metrics
- Logistics reliability

**Annual semiconductor spend:** $10,100,000
**Spend at elevated risk (score >= 5.0):** $8,000,000 (79.2%)

| Supplier | Country | Share | Spend | Risk Score | Risk Level |
|----------|---------|-------|-------|------------|------------|
| TechnoCore Semiconductor (Taiwan) | Taiwan | 40% of MCU supply | $4,800,000 | 8.2/10 | **HIGH RISK** |
| Shenzhen Electronics Co. | China | 35% of passives | $3,200,000 | 6.5/10 | **MEDIUM RISK** |
| Malaysia Semicon Pte Ltd | Malaysia | 25% of power ICs | $2,100,000 | 3.8/10 | **LOW RISK** |

Other monitored suppliers (outside this semiconductor review): Midwest Casting & Forge 4.9/10; Rheinland Precision GmbH 2.4/10.

Source: [Risk Intelligence + news wires + D365] (synthetic)

Shall I show the detailed risk assessment?
```

### `supplier_scorecard` — Detailed supply risk assessment

Use for the detailed risk assessment: HIGH / MEDIUM / LOW per supplier with concerns, financial, quality, strengths, and dimension scores.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Supply Risk Assessment

> Synthetic evidence for procurement review; scores are not customer or third-party ratings.

### HIGH RISK: TechnoCore Taiwan (SUP-101)
- **Risk score:** 8.2/10
- **Impact:** 40% of MCU supply
- **Primary concern:** Cross-strait geopolitical tensions
- **Secondary:** Single facility concentration
- **Recent events:** Military exercises within 50nm
- **Dimension scores (0-100):** Quality 82 | Delivery 74 | Financial 68 | Geopolitical 42 (composite health 68.5/100)

### MEDIUM RISK: Shenzhen Electronics (SUP-102)
- **Risk score:** 6.5/10
- **Impact:** 35% of passives
- **Concerns:** Trade restrictions, IP protection
- **Financial:** Debt-to-equity +35% (stressed)
- **Quality:** Defect rate 2.3% (up from 1.8%)
- **Dimension scores (0-100):** Quality 71 | Delivery 78 | Financial 55 | Geopolitical 58 (composite health 66.2/100)

### LOW RISK: Malaysia Semicon (SUP-103)
- **Risk score:** 3.8/10
- **Impact:** 25% of power ICs
- **Strengths:** Political stability, diversified base
- **Capacity:** 120% of our demand available
- **Dimension scores (0-100):** Quality 91 | Delivery 88 | Financial 84 | Geopolitical 82 (composite health 86.7/100)

Source: [Risk Intelligence + Financial Data] (synthetic)

Want to see mitigation strategies?
```

### `disruption_alerts` — Active disruption alerts

Use for recorded incidents and the exposure to validate.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Active Disruption Alerts

> Recorded synthetic incidents only; validate against approved sources before action.

| Severity | Date | Supplier | Description |
|----------|------|----------|-------------|
| **HIGH** | 2026-02-28 | TechnoCore Semiconductor (Taiwan) (SUP-101) | Military exercises within 50nm of the facility; 5-day port closure delayed 3 shipments |
| **HIGH** | 2026-03-10 | Midwest Casting & Forge (SUP-104) | Equipment failure at foundry; force majeure declared, 7-day production halt |
| **MEDIUM** | 2026-03-05 | Shenzhen Electronics Co. (SUP-102) | Quality excursion: capacitor lot C-4410 at 2.3% defect rate (up from 1.8%; spec 0.5%) |
| **LOW** | 2026-03-12 | Shenzhen Electronics Co. (SUP-102) | New export control regulations announced; compliance review underway |

### Impact Assessment

**TechnoCore Semiconductor (Taiwan)**
- Annual spend exposed: $4,800,000
- Category: Microcontrollers
- Backup suppliers available: Yes

**Midwest Casting & Forge**
- Annual spend exposed: $5,600,000
- Category: Aluminum Castings
- Backup suppliers available: Yes

```

### `alternative_sourcing` — Alternative sourcing options

Use for comparing backup suppliers for procurement review.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Alternative Sourcing Options

> Synthetic recommendation only. No supplier was contacted, qualified, selected, or awarded business; no order, payment term, contract, or alert was changed or activated.

### Alternatives for TechnoCore Semiconductor (Taiwan) (Microcontrollers)
- **Current spend:** $4,800,000
- **Current risk:** 8.2/10

| Alternative Supplier | Lead Time | Qual Status | Cost Premium |
|---------------------|-----------|-------------|--------------|
| Hanseong Foundry (Korea) | 26 weeks | In Progress | +8% |
| Lakeside Foundry (USA) | 16 weeks | Not Started | +15% |

**Review option:** Ask authorized procurement owners whether to assess Lakeside Foundry (USA) (16-week lead; synthetic status: Not Started)

### Alternatives for Shenzhen Electronics Co. (Passive Components)
- **Current spend:** $3,200,000
- **Current risk:** 6.5/10

| Alternative Supplier | Lead Time | Qual Status | Cost Premium |
|---------------------|-----------|-------------|--------------|
| Kansai Passive Components (Japan) | 6 weeks | In Qualification | +5% |
| Keystone Passives (USA) | 4 weeks | In Qualification | +12% |

**Review option:** Ask authorized procurement owners whether to assess Keystone Passives (USA) (4-week lead; synthetic status: In Qualification)

### Alternatives for Midwest Casting & Forge (Aluminum Castings)
- **Current spend:** $5,600,000
- **Current risk:** 4.9/10

| Alternative Supplier | Lead Time | Qual Status | Cost Premium |
|---------------------|-----------|-------------|--------------|
| Great Lakes Precision Castings (USA) | 8 weeks | In Progress | +6% |

**Review option:** Ask authorized procurement owners whether to assess Great Lakes Precision Castings (USA) (8-week lead; synthetic status: In Progress)

**Estimated annual cost of full diversification:** $880,000
**Spend represented by the modeled review scope:** $13,600,000

This agent does not contact suppliers, change allocations, place orders, or approve qualification.
```

### `mitigation_plan` — Risk mitigation plan

Use for mitigation strategies per supplier.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Risk Mitigation Plan

> Synthetic recommendations for authorized procurement approval; nothing below has been executed.

### TechnoCore (Taiwan) - HIGH PRIORITY
**Immediate (30 days):**
- Increase safety stock: 30 -> 45 days ($840K investment)
- Dual sourcing: Korean supplier qualification started
- Alternative qualified: 6 months
- Air freight contingency: $2.1M capacity to reserve

### Shenzhen Electronics (China) - MONITOR CLOSELY
**Actions:**
- Payment terms: Net-30 -> COD (protect exposure)
- Quality inspection: 100% incoming (was sampling)
- Contract updates: Stronger IP protections
- Backup identified: 2 suppliers in qualification

### Malaysia Semicon (Malaysia) - OPPORTUNITY
**Optimization:**
- Volume increase: +20% (tier discount available)
- Strategic partnership discussions
- Co-development program for custom ICs

Source: [Supply Chain + Procurement] (synthetic)

Synthetic recommendation only. No supplier was contacted, qualified, selected, or awarded business; no order, payment term, contract, or alert was changed or activated.

Shall I show the financial impact?
```

### `financial_impact` — Mitigation investment analysis

Use for mitigation costs, exposure reduction, and the ROI / break-even scenario.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Risk Mitigation Investment Analysis

> Synthetic planning model; values are estimates for review, not committed budget.

**Mitigation Costs:**

| Action | Investment | Benefit |
|--------|------------|---------|
| Safety stock increase | $840K | 45 days buffer |
| Dual sourcing program | $125K | Supply security |
| Enhanced inspection | $48K/year | Quality protection |
| Alternative qualification | $85K | Reduced dependency |
| **Total Investment** | **$1.098M** | Risk reduction |

**Risk Exposure Reduction:**
- Current supply risk: $12.4M (potential disruption)
- After mitigation: $4.3M (65% reduction)
- Expected probability: 15% -> 4%

**ROI Scenario:**
- Avoided disruption value: $12.4M
- Implementation cost: $1.098M
- Break-even: 8.8% disruption probability
- Current probability: 15% (favorable)

Source: [Finance + Risk Model] (synthetic)

Want to see the 12-month implementation roadmap?
```

### `implementation_roadmap` — 12-month implementation roadmap

Use for the 12-month implementation roadmap.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## 12-Month Implementation Roadmap

> Synthetic recommended plan for procurement approval; no order, contract, or term change is made.

**Phase 1 (Months 1-3): Immediate Protection**
- Week 1: Increase TechnoCore orders (safety stock)
- Week 2: COD terms with Shenzhen Electronics
- Week 3: 100% inspection protocol starts
- Week 4: Korean supplier identification complete

**Phase 2 (Months 4-6): Qualification**
- Month 4: Korean supplier initial samples
- Month 5: Testing and validation
- Month 6: First production orders (10% volume)

**Phase 3 (Months 7-9): Optimization**
- Malaysia partnership negotiations
- Volume consolidation planning
- Contract updates completed

**Phase 4 (Months 10-12): Full Resilience**
- Dual sourcing: 60% Taiwan / 40% Korea
- Malaysia strategic partnership signed
- Risk score target: <4.0 (from 8.2)

Source: [Project Management + Procurement] (synthetic)

Want to see ongoing monitoring?
```

### `monitoring_plan` — Real-time risk monitoring design

Use for the ongoing monitoring approach.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Real-Time Risk Monitoring System

> Synthetic recommended monitoring design; no feed, alert, or automated action is activated by this agent.

**Data Sources (24/7 Scanning):**
- Geopolitical: news wires, government advisories
- Financial: credit ratings, stock prices, filings
- Operational: supplier portals, IoT, certifications
- Logistics: shipping data, port congestion, weather
- Legal: sanctions lists, trade restrictions

**Alert Thresholds:**
- Critical: Immediate escalation to VP
- Warning: Daily digest to procurement
- Info: Weekly risk report

**Automated Actions (recommended rules, each requires approval to activate):**
- Risk score >7.5: Trigger mitigation protocols
- Financial deterioration: Payment terms adjustment
- Quality issues: Inspection level increase
- Capacity concerns: Backup supplier activation

**Success Metrics (synthetic pilot benchmarks):**
- Supply continuity: 99.7% (target: 99.5%)
- Risk-adjusted cost: -12% vs. reactive approach
- Early warning: 18 days average lead time

Source: [Azure AI + Power Platform + Risk Intelligence] (synthetic)

Your supply chain now has a ready-to-approve design for enterprise-grade risk monitoring and mitigation.
```

## Authorization and no-side-effect boundary

Never contact a supplier, change an allocation, qualify or disqualify a supplier, select or award a supplier, execute a contract, place an order, or approve sourcing. Authorized procurement owners must use approved procurement and supplier-management tools for any action.

Always distinguish: **source record**, **derived synthetic analysis**,
**recommendation**, **required human approval**, and **external action not performed**.
If a requested fact is absent from the complete records, say it is not present in
the fixed synthetic snapshot rather than inventing it.
