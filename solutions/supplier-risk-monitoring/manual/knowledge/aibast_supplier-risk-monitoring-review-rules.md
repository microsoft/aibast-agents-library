# Supply Risk Monitoring Agent — Exact Review Rules and Locked Outputs

> **SYNTHETIC PILOT RULES.** Use this file with the complete synthetic source
> records. It contains the exact deterministic operation outputs captured by the
> source agent. These outputs are evidence and recommendations, not completed
> operational side effects or customer outcomes.

## Locked case routing

| Case | Persona | Operation | Exact prompt | Required deterministic evidence |
|---|---|---|---|---|
| SR-01 | Supply Chain Director | `risk_dashboard` | Where is supplier exposure concentrated, and which relationships should leadership review first? | `TechnoCore Semiconductor`; `CRITICAL` |
| SR-02 | Procurement Manager | `supplier_scorecard` | Explain why TechnoCore is elevated and show me the evidence by risk dimension. | `SUP-101`; `Geopolitical` |
| SR-03 | Supply Chain Director | `disruption_alerts` | Which recorded disruptions could threaten continuity, and what exposure should we validate? | `SUP-104`; `force majeure` |
| SR-04 | Procurement Manager | `alternative_sourcing` | Compare backup sourcing options for review, but do not contact, qualify, select, or order from any supplier. | `Murata Electronics`; `No supplier was contacted` |

## Deterministic calculation and interpretation rules

- Composite health uses the source weighting: quality 30%, delivery 25%, financial 25%, and geopolitical 20%.
- Risk tiers are CRITICAL at or above 7.0, HIGH at or above 5.0, MODERATE at or above 3.0, and LOW below 3.0.
- Dimension status is Good at or above 80, Watch at or above 60, and At Risk below 60.
- Incident evidence is a fixed synthetic record and must be validated against approved supplier, logistics, quality, financial, and external-risk sources.
- Backup qualification labels are synthetic source states, not completed procurement decisions.

## Exact deterministic operation outputs

### `risk_dashboard` — Supplier risk dashboard

Use for total spend, elevated-risk spend, ranked supplier risk, composite health, and incident counts.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Supplier Risk Dashboard

> Fixed synthetic snapshot; no live financial, logistics, ERP, or supplier feed was queried.

**Total annual supplier spend:** $19,500,000
**Spend at elevated risk (score >= 5.0):** $8,000,000 (41.0%)

| Supplier | Category | Country | Spend | Risk Score | Risk Tier | Composite Health |
|----------|----------|---------|-------|------------|-----------|------------------|
| TechnoCore Semiconductor (Taiwan | Microcontrollers | Taiwan | $4,800,000 | 8.2 | **CRITICAL** | 68.5/100 |
| Shenzhen Electronics Co. | Passive Components | China | $3,200,000 | 6.5 | **HIGH** | 66.2/100 |
| Midwest Casting & Forge | Aluminum Castings | USA | $5,600,000 | 4.9 | **MODERATE** | 79.7/100 |
| Malaysia Semicon Pte Ltd | Power ICs | Malaysia | $2,100,000 | 3.8 | **MODERATE** | 86.7/100 |
| Rheinmetall Precision GmbH | CNC Machined Parts | Germany | $3,800,000 | 2.4 | **LOW** | 91.1/100 |

**Active incidents:** 4
**HIGH severity incidents:** 2
```

### `supplier_scorecard` — Supplier scorecards

Use for exact supplier identity, category, geography, spend, tier, risk, health, dimension scores, statuses, and incidents.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Supplier Scorecards

> Synthetic evidence for procurement review; scores are not customer or third-party ratings.

### TechnoCore Semiconductor (Taiwan) (SUP-101)
- **Category:** Microcontrollers
- **Region:** Asia-Pacific (Taiwan)
- **Annual spend:** $4,800,000
- **Tier:** 1
- **Overall risk:** 8.2/10 (CRITICAL)
- **Composite health:** 68.5/100

| Dimension | Score | Status |
|-----------|-------|--------|
| Quality | 82/100 | Good |
| Delivery | 74/100 | Watch |
| Financial | 68/100 | Watch |
| Geopolitical | 42/100 | At Risk |

**Recent incidents (1):**
- [HIGH] 2026-02-28: Cross-strait military exercises caused 5-day port closure; delayed 3 shipments

### Shenzhen Electronics Co. (SUP-102)
- **Category:** Passive Components
- **Region:** Asia-Pacific (China)
- **Annual spend:** $3,200,000
- **Tier:** 1
- **Overall risk:** 6.5/10 (HIGH)
- **Composite health:** 66.2/100

| Dimension | Score | Status |
|-----------|-------|--------|
| Quality | 71/100 | Watch |
| Delivery | 78/100 | Watch |
| Financial | 55/100 | At Risk |
| Geopolitical | 58/100 | At Risk |

**Recent incidents (2):**
- [MEDIUM] 2026-03-05: Quality excursion: capacitor lot C-4410 failed incoming inspection (2.3% defect rate vs 0.5% spec)
- [LOW] 2026-03-12: New export control regulations announced; compliance review underway

### Malaysia Semicon Pte Ltd (SUP-103)
- **Category:** Power ICs
- **Region:** Asia-Pacific (Malaysia)
- **Annual spend:** $2,100,000
- **Tier:** 1
- **Overall risk:** 3.8/10 (MODERATE)
- **Composite health:** 86.7/100

| Dimension | Score | Status |
|-----------|-------|--------|
| Quality | 91/100 | Good |
| Delivery | 88/100 | Good |
| Financial | 84/100 | Good |
| Geopolitical | 82/100 | Good |

### Midwest Casting & Forge (SUP-104)
- **Category:** Aluminum Castings
- **Region:** North America (USA)
- **Annual spend:** $5,600,000
- **Tier:** 1
- **Overall risk:** 4.9/10 (MODERATE)
- **Composite health:** 79.7/100

| Dimension | Score | Status |
|-----------|-------|--------|
| Quality | 88/100 | Good |
| Delivery | 65/100 | Watch |
| Financial | 72/100 | Watch |
| Geopolitical | 95/100 | Good |

**Recent incidents (1):**
- [HIGH] 2026-03-10: Equipment failure at foundry; force majeure declared, 7-day production halt

### Rheinmetall Precision GmbH (SUP-105)
- **Category:** CNC Machined Parts
- **Region:** Europe (Germany)
- **Annual spend:** $3,800,000
- **Tier:** 2
- **Overall risk:** 2.4/10 (LOW)
- **Composite health:** 91.1/100

| Dimension | Score | Status |
|-----------|-------|--------|
| Quality | 95/100 | Good |
| Delivery | 91/100 | Good |
| Financial | 89/100 | Good |
| Geopolitical | 88/100 | Good |

```

### `disruption_alerts` — Active disruption alerts

Use for exact severity, date, supplier, incident description, exposed spend, category, and backup availability.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Active Disruption Alerts

> Recorded synthetic incidents only; validate against approved sources before action.

| Severity | Date | Supplier | Description |
|----------|------|----------|-------------|
| **HIGH** | 2026-02-28 | TechnoCore Semiconductor (Ta (SUP-101) | Cross-strait military exercises caused 5-day port closure; delayed 3 shipments |
| **HIGH** | 2026-03-10 | Midwest Casting & Forge (SUP-104) | Equipment failure at foundry; force majeure declared, 7-day production halt |
| **MEDIUM** | 2026-03-05 | Shenzhen Electronics Co. (SUP-102) | Quality excursion: capacitor lot C-4410 failed incoming inspection (2.3% defect rate vs 0.5% spec) |
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

Use for exact backup names, lead times, synthetic qualification states, premiums, modeled diversification cost, and procurement-review language.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Alternative Sourcing Options

> Synthetic recommendation only. No supplier was contacted, qualified, selected, or awarded business.

### Alternatives for TechnoCore Semiconductor (Taiwan) (Microcontrollers)
- **Current spend:** $4,800,000
- **Current risk:** 8.2/10

| Alternative Supplier | Lead Time | Qual Status | Cost Premium |
|---------------------|-----------|-------------|--------------|
| Samsung Foundry (Korea) | 12 weeks | In Progress | +8% |
| GlobalFoundries (USA) | 16 weeks | Not Started | +15% |

**Review option:** Ask authorized procurement owners whether to assess Samsung Foundry (Korea) (12-week lead; synthetic status: In Progress)

### Alternatives for Shenzhen Electronics Co. (Passive Components)
- **Current spend:** $3,200,000
- **Current risk:** 6.5/10

| Alternative Supplier | Lead Time | Qual Status | Cost Premium |
|---------------------|-----------|-------------|--------------|
| Murata Electronics (Japan) | 6 weeks | Qualified | +5% |
| Vishay Intertechnology (USA) | 4 weeks | Qualified | +12% |

**Review option:** Ask authorized procurement owners to evaluate Murata Electronics (Japan) (synthetic status: qualified; +5% premium; 6-week lead)

### Alternatives for Midwest Casting & Forge (Aluminum Castings)
- **Current spend:** $5,600,000
- **Current risk:** 4.9/10

| Alternative Supplier | Lead Time | Qual Status | Cost Premium |
|---------------------|-----------|-------------|--------------|
| Alcoa Precision Castings (USA) | 8 weeks | In Progress | +6% |

**Review option:** Ask authorized procurement owners whether to assess Alcoa Precision Castings (USA) (8-week lead; synthetic status: In Progress)

**Estimated annual cost of full diversification:** $880,000
**Spend represented by the modeled review scope:** $8,000,000

This agent does not contact suppliers, change allocations, place orders, or approve qualification.
```

## Authorization and no-side-effect boundary

Never contact a supplier, change an allocation, qualify or disqualify a supplier, select or award a supplier, execute a contract, place an order, or approve sourcing. Authorized procurement owners must use approved procurement and supplier-management tools for any action.

Always distinguish: **source record**, **derived synthetic analysis**,
**recommendation**, **required human approval**, and **external action not performed**.
If a requested fact is absent from the complete records, say it is not present in
the fixed synthetic snapshot rather than inventing it.
