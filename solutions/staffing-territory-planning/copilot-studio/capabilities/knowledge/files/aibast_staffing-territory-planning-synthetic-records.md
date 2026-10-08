# Staffing Territory Planning — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Contoso Staffing, the North Valley territory, the metros Harbor City, Millbrook, Granite Ridge and Ashford Junction, Dana Whitfield, and the competitors Fabrikam Workforce, Northwind Staffing and Litware Talent are fictional. Every spend, revenue, share, recruiter count and trend is invented. Never match them to a real organization,
> person, product or market, and never treat them as live data.

## Complete synthetic records

## Snapshot

| Field | Value |
|---|---|
| Firm | Contoso Staffing |
| Territory | North Valley territory |
| Prepared for | Dana Whitfield, regional sales director |
| Data period | trailing 12 months to June 30 |
| Service lines | Light Industrial; Office and Admin; IT and Engineering; Healthcare Support |
| Coverage-gap rule | at least $9.0M addressable spend and our share under 5% |

## Addressable spend and our revenue by metro and service line ($ millions per year)

| Metro | Line | Addressable | Our revenue | Our share | Open spend |
|---|---|---|---|---|---|
| Harbor City | Light Industrial | 48.0 | 6.2 | 12.9% | 41.8 |
| Harbor City | Office and Admin | 22.0 | 2.9 | 13.2% | 19.1 |
| Harbor City | IT and Engineering | 31.0 | 1.1 | 3.5% | 29.9 |
| Harbor City | Healthcare Support | 14.0 | 0.4 | 2.9% | 13.6 |
| Millbrook | Light Industrial | 26.0 | 4.1 | 15.8% | 21.9 |
| Millbrook | Office and Admin | 9.0 | 1.2 | 13.3% | 7.8 |
| Millbrook | IT and Engineering | 6.0 | 0.0 | 0.0% | 6.0 |
| Millbrook | Healthcare Support | 11.0 | 0.9 | 8.2% | 10.1 |
| Granite Ridge | Light Industrial | 18.0 | 0.8 | 4.4% | 17.2 |
| Granite Ridge | Office and Admin | 7.0 | 0.6 | 8.6% | 6.4 |
| Granite Ridge | IT and Engineering | 12.0 | 0.0 | 0.0% | 12.0 |
| Granite Ridge | Healthcare Support | 9.0 | 0.0 | 0.0% | 9.0 |
| Ashford Junction | Light Industrial | 14.0 | 2.0 | 14.3% | 12.0 |
| Ashford Junction | Office and Admin | 5.0 | 0.7 | 14.0% | 4.3 |
| Ashford Junction | IT and Engineering | 3.0 | 0.0 | 0.0% | 3.0 |
| Ashford Junction | Healthcare Support | 6.0 | 0.5 | 8.3% | 5.5 |

## Metro totals

| Metro | Addressable | Our revenue | Our share | Recruiters | Spend per recruiter | Active clients |
|---|---|---|---|---|---|---|
| Harbor City | $115.0M | $10.6M | 9.2% | 9 | $12.8M | 64 |
| Millbrook | $52.0M | $6.2M | 11.9% | 5 | $10.4M | 38 |
| Granite Ridge | $46.0M | $1.4M | 3.0% | 1 | $46.0M | 9 |
| Ashford Junction | $28.0M | $3.2M | 11.4% | 2 | $14.0M | 17 |
| Territory | $241.0M | $21.4M | 8.9% | 17 | $14.2M | 128 |

Granite Ridge market sizing: $46.0M addressable, $1.4M our revenue, 3.0% share, $44.6M open spend; largest open spend Light Industrial ($17.2M).

## Coverage gaps (5 gaps, $81.7M open spend)

| Rank | Metro | Line | Addressable | Our share | Open spend |
|---|---|---|---|---|---|
| 1 | Harbor City | IT and Engineering | $31.0M | 3.5% | $29.9M |
| 2 | Granite Ridge | Light Industrial | $18.0M | 4.4% | $17.2M |
| 3 | Harbor City | Healthcare Support | $14.0M | 2.9% | $13.6M |
| 4 | Granite Ridge | IT and Engineering | $12.0M | 0.0% | $12.0M |
| 5 | Granite Ridge | Healthcare Support | $9.0M | 0.0% | $9.0M |

## Competitor share of addressable spend (fictional firms)

| Competitor | Harbor City | Millbrook | Granite Ridge | Ashford Junction |
|---|---|---|---|---|
| Fabrikam Workforce | 18.0% | 12.0% | 21.0% | 9.0% |
| Northwind Staffing | 11.0% | 15.0% | 6.0% | 14.0% |
| Litware Talent | 7.0% | 4.0% | 17.0% | 3.0% |

Our rank (of 4 firms): Harbor City 3 of 4; Millbrook 3 of 4; Granite Ridge 4 of 4; Ashford Junction 2 of 4.

## Labor trends

| Line | Job postings (YoY) | Median wage (YoY) | Time to fill |
|---|---|---|---|
| Light Industrial | +6% | +4.2% | 9 days |
| Office and Admin | -3% | +2.1% | 12 days |
| IT and Engineering | +11% | +5.8% | 31 days |
| Healthcare Support | +8% | +4.9% | 18 days |

## Draft quarterly plan (derived)

- Top 3 opportunities: Harbor City IT and Engineering ($29.9M open); Granite Ridge Light Industrial ($17.2M open); Harbor City Healthcare Support ($13.6M open).
- Top 2 risks: Granite Ridge has 1 recruiter for $46.0M of spend while Fabrikam Workforce and Litware Talent hold 38.0% of it; Office and Admin postings are down 3%, exposing Harbor City office revenue ($2.9M).
- Recommendations: add 2 IT and Engineering recruiters across Harbor City and Granite Ridge; move 1 light-industrial recruiter from Harbor City to Granite Ridge; re-price IT and Engineering bill rates for the 5.8% wage movement.
- Priority action: approve the 2 IT and Engineering recruiter requisitions this quarter (a leadership decision).

## Locked-case evidence contract

Each locked case below calls exactly one operation. The agent output must contain every listed evidence string.

| Case | Persona | Operation | Prompt | Must include |
|---|---|---|---|---|
| STP-01 | Regional Sales Director | territory_snapshot | Give me a snapshot of my North Valley territory. | $241.0M; Granite Ridge; Spend per recruiter |
| STP-02 | Regional Sales Director | market_sizing | How big is the staffing market in Granite Ridge? | Market Sizing: Granite Ridge; $44.6M; Largest open spend |
| STP-03 | Sales Operations Analyst | coverage_gaps | Where are our biggest coverage gaps? | 5 gaps; $81.7M open spend; IT and Engineering |
| STP-04 | Branch Manager | competitive_landscape | Who are we up against in each metro? | Fabrikam Workforce; 4 of 4; Litware Talent |
| STP-05 | Regional Sales Director | labor_trends | What labor market trends should I plan around? | 31 days; +11%; Planning implication |
| STP-06 | Regional Sales Director | territory_plan | Draft my quarterly territory plan. | Priority action; Top 3 opportunities; no headcount, quota or account change was made |

## Reference outputs (exact agent output for each locked case)

### STP-01 — Territory snapshot (`{"operation": "territory_snapshot"}`)

````markdown
**Territory Snapshot: Contoso Staffing North Valley territory**

Prepared for Dana Whitfield, regional sales director | Data: trailing 12 months to June 30

| Metro | Addressable spend | Our revenue | Our share | Recruiters | Spend per recruiter | Active clients |
|---|---|---|---|---|---|---|
| Harbor City | $115.0M | $10.6M | 9.2% | 9 | $12.8M | 64 |
| Millbrook | $52.0M | $6.2M | 11.9% | 5 | $10.4M | 38 |
| Granite Ridge | $46.0M | $1.4M | 3.0% | 1 | $46.0M | 9 |
| Ashford Junction | $28.0M | $3.2M | 11.4% | 2 | $14.0M | 17 |
| **Territory** | **$241.0M** | **$21.4M** | **8.9%** | **17** | **$14.2M** | **128** |

**Read:** Granite Ridge carries $46.0M of spend with 1 recruiter, more than three times the territory's spend per recruiter.

**Next step:** size the Granite Ridge market, then review coverage gaps.

Synthetic planning snapshot only. This agent does not change headcount, quotas, account assignments or CRM records; the plan is a draft for sales leadership to decide.

Source: [Synthetic Territory + Labor Market Snapshot]
Agents: StaffingTerritoryPlanningAgent
````

### STP-02 — Market sizing (`{"operation": "market_sizing", "metro": "Granite Ridge"}`)

````markdown
**Market Sizing: Granite Ridge**

| Service line | Addressable spend | Our revenue | Our share | Open spend |
|---|---|---|---|---|
| Light Industrial | $18.0M | $0.8M | 4.4% | $17.2M |
| Office and Admin | $7.0M | $0.6M | 8.6% | $6.4M |
| IT and Engineering | $12.0M | $0.0M | 0.0% | $12.0M |
| Healthcare Support | $9.0M | $0.0M | 0.0% | $9.0M |
| **Total** | **$46.0M** | **$1.4M** | **3.0%** | **$44.6M** |

**Largest open spend:** Light Industrial ($17.2M).

Addressable spend is the synthetic annual temporary-labor spend; open spend is addressable spend not yet won by Contoso Staffing.

Synthetic planning snapshot only. This agent does not change headcount, quotas, account assignments or CRM records; the plan is a draft for sales leadership to decide.

Source: [Synthetic Territory + Labor Market Snapshot]
Agents: StaffingTerritoryPlanningAgent
````

### STP-03 — Coverage gaps (`{"operation": "coverage_gaps"}`)

````markdown
**Coverage Gaps: North Valley territory**

Rule: a service line with at least $9.0M addressable spend where our share is under 5%.

| Rank | Metro | Service line | Addressable | Our revenue | Our share | Open spend |
|---|---|---|---|---|---|---|
| 1 | Harbor City | IT and Engineering | $31.0M | $1.1M | 3.5% | $29.9M |
| 2 | Granite Ridge | Light Industrial | $18.0M | $0.8M | 4.4% | $17.2M |
| 3 | Harbor City | Healthcare Support | $14.0M | $0.4M | 2.9% | $13.6M |
| 4 | Granite Ridge | IT and Engineering | $12.0M | $0.0M | 0.0% | $12.0M |
| 5 | Granite Ridge | Healthcare Support | $9.0M | $0.0M | 0.0% | $9.0M |

**5 gaps, $81.7M open spend.** The two largest are IT and Engineering in Harbor City and Light Industrial in Granite Ridge.

**Next step:** check who holds these markets today before deciding where to add recruiters.

Synthetic planning snapshot only. This agent does not change headcount, quotas, account assignments or CRM records; the plan is a draft for sales leadership to decide.

Source: [Synthetic Territory + Labor Market Snapshot]
Agents: StaffingTerritoryPlanningAgent
````

### STP-04 — Competitive landscape (`{"operation": "competitive_landscape"}`)

````markdown
**Competitive Landscape: North Valley territory**

| Metro | Share leader | Contoso Staffing share | Our rank |
|---|---|---|---|
| Harbor City | Fabrikam Workforce (18.0%) | 9.2% | 3 of 4 |
| Millbrook | Northwind Staffing (15.0%) | 11.9% | 3 of 4 |
| Granite Ridge | Fabrikam Workforce (21.0%) | 3.0% | 4 of 4 |
| Ashford Junction | Northwind Staffing (14.0%) | 11.4% | 2 of 4 |

**Competitor profiles (synthetic):**
- Fabrikam Workforce: volume light-industrial player; leads Harbor City and Granite Ridge.
- Northwind Staffing: strongest in Millbrook and Ashford Junction office and admin.
- Litware Talent: IT and engineering specialist; 17.0% of Granite Ridge.

**Read:** we rank last in Granite Ridge, where Litware Talent's IT focus meets our zero IT revenue.

Synthetic planning snapshot only. This agent does not change headcount, quotas, account assignments or CRM records; the plan is a draft for sales leadership to decide.

Source: [Synthetic Territory + Labor Market Snapshot]
Agents: StaffingTerritoryPlanningAgent
````

### STP-05 — Labor trends (`{"operation": "labor_trends"}`)

````markdown
**Labor Trends: North Valley territory**

| Service line | Job postings (YoY) | Median wage (YoY) | Time to fill |
|---|---|---|---|
| Light Industrial | +6% | +4.2% | 9 days |
| Office and Admin | -3% | +2.1% | 12 days |
| IT and Engineering | +11% | +5.8% | 31 days |
| Healthcare Support | +8% | +4.9% | 18 days |

**Read:** IT and Engineering postings are up 11% with a 31-day time to fill, the slowest fill and fastest growth; Office and Admin postings are down 3%.

**Planning implication:** recruiter capacity for IT and Engineering is the constraint; bill rates should reflect the 5.8% wage movement.

Synthetic planning snapshot only. This agent does not change headcount, quotas, account assignments or CRM records; the plan is a draft for sales leadership to decide.

Source: [Synthetic Territory + Labor Market Snapshot]
Agents: StaffingTerritoryPlanningAgent
````

### STP-06 — Draft territory plan (`{"operation": "territory_plan"}`)

````markdown
**Draft Quarterly Territory Plan: North Valley territory** (draft for sales leadership review)

**Territory snapshot:** $241.0M addressable spend, $21.4M our revenue (8.9% share), 17 recruiters.

**Top 3 opportunities:**
1. Harbor City IT and Engineering: $29.9M open spend at 3.5% share.
2. Granite Ridge Light Industrial: $17.2M open spend at 4.4% share.
3. Harbor City Healthcare Support: $13.6M open spend at 2.9% share.

**Top 2 risks:**
1. Granite Ridge has 1 recruiter for $46.0M of spend; Fabrikam Workforce and Litware Talent hold 38.0% of it.
2. Office and Admin postings are down 3%; Harbor City office revenue ($2.9M) is exposed.

**3 recommendations:**
1. Add 2 IT and Engineering recruiters split across Harbor City and Granite Ridge (31-day time to fill).
2. Move 1 light-industrial recruiter from Harbor City to Granite Ridge to work its $17.2M open spend.
3. Re-price IT and Engineering bill rates for the 5.8% wage movement before Q3 renewals.

**Priority action:** approve the 2 IT and Engineering recruiter requisitions this quarter.

Status: Draft - no headcount, quota or account change was made.

Synthetic planning snapshot only. This agent does not change headcount, quotas, account assignments or CRM records; the plan is a draft for sales leadership to decide.

Source: [Synthetic Territory + Labor Market Snapshot]
Agents: StaffingTerritoryPlanningAgent
````
