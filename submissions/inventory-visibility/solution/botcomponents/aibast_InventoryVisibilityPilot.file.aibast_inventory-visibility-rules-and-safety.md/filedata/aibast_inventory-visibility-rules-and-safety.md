# Inventory Visibility — Exact Rules, Headings, and Safety

> **COPILOT STUDIO KNOWLEDGE CONTRACT.** Use this file with the companion
> complete synthetic-records file. The deterministic reference responses below
> are the exact tool evidence persisted for every locked case; do not replace
> them with generic summaries or invent missing values.

## Approved personas and language focus

| Persona | Required focus |
|---|---|
| Inventory Planner | network balance, replenishment scenarios, and planning assumptions |
| Store Manager | store-level exceptions and practical review priorities |
| Category Manager | category health, availability patterns, and tradeoffs |

## Exact routing and evidence contract

| Case | Route to operation | Persona | Exact arguments | Required transcript evidence |
|---|---|---|---|---|
| `IV-01` | `inventory_dashboard` | Inventory Planner | `{"location_id":"STR-001"}` | `Prepared for:** Inventory Planner`; `Inventory Visibility Snapshot`; `no stock is reserved` |
| `IV-02` | `stock_alerts` | Store Manager | `{}` | `Prepared for:** Store Manager`; `Draft Stock Review`; `Review transfer candidate` |
| `IV-03` | `replenishment_plan` | Inventory Planner | `{}` | `Draft Replenishment Plan`; `14-day supply`; `Estimated Total Replenishment Cost` |
| `IV-04` | `channel_allocation` | Category Manager | `{"sku_id":"SKU-1003"}` | `Prepared for:** Category Manager`; `Channel Allocation Scenario`; `do not reserve units` |
| `IV-05` | `transfer_plan` | Inventory Planner | `{}` | `Draft Reallocation Plan`; `$18,400`; `35:1` |
| `IV-06` | `network_health` | Inventory Planner | `{}` | `Stock balance score`; `$84,200`; `Slow movers` |
| `IV-07` | `automation_recommendations` | Inventory Planner | `{}` | `RFID Tracking`; `680 across 15 routes`; `$340,000` |
| `IV-08` | `investment_proposal` | Inventory Planner | `{}` | `Draft Investment Proposal`; `$858,000`; `5.7 months` |

Routing rules:

- Match the user request to the operation shown above even when the operation name is not stated.
- Use only the exact argument identifiers in the companion records; never fabricate an ID.
- Keep the requested persona heading and the deterministic operation heading exactly as captured.
- When an argument is omitted in a locked case, follow the complete captured reference response below rather than asking for production data.
- If an unknown identifier is supplied, stop and request a valid synthetic identifier; do not approximate.

## Exact no-side-effect boundary

> Synthetic inventory snapshot. Read-only recommendations only; no stock is reserved, transferred, replenished, allocated, promised, or purchased. Verify all quantities in the system of record before action.

Never reserve, promise, transfer, replenish, allocate, sell, or purchase stock. Every quantity is a synthetic snapshot requiring system-of-record verification and authorized approval.

Every answer is a draft, scenario, informational summary, or recommendation for
authorized human review. Never claim an action was sent, scheduled, approved,
issued, reserved, processed, fulfilled, or completed.

## Locked deterministic reference responses

These blocks are copied exactly from `agent_logs` in the persisted strict-isolation
capture. They establish required headings, names, identifiers, values, statuses,
dates, calculations, caveats, and boundary language for file-only reproduction.

### `IV-01` — `inventory_dashboard`

- Persona: **Inventory Planner**
- Prompt: As Inventory Planner, summarize the store snapshot and verification boundary.
- Exact arguments: `{"location_id":"STR-001"}`

```markdown
[inventory-visibility-agent] **Prepared for:** Inventory Planner
**Role focus:** network balance, replenishment scenarios, and planning assumptions

> Synthetic inventory snapshot. Read-only recommendations only; no stock is reserved, transferred, replenished, allocated, promised, or purchased. Verify all quantities in the system of record before action.

# Inventory Visibility Snapshot

Real-time inventory analyzed across all 51 locations. Critical allocation imbalance detected - Seattle overstock while Portland is out of stock.

**Alpine Pro Winter Jacket (SKU-2001) - All Locations:**

| Location Type | Units | % Total | Status |
|---|---|---|---|
| Stores (47) | 1,847 | 58% | Unbalanced |
| Warehouses (3) | 940 | 29% | Healthy |
| In-transit | 285 | 9% | Active |
| E-comm reserve | 128 | 4% | Low |
| **Total** | **3,200** | 100% | |

**Critical Issues:**
- Portland Flagship - 0 units (sold out 3 days ago)
- Portland Mall - 3 units (selling 8/day)
- Seattle stores - 247 units excess (selling 4/day)

**Opportunity:** Transfer 120 units Seattle -> Portland = $18,400 recovered sales

Source: [Real-Time Inventory + POS Data + Demand Forecast]

Next step: should I create the reallocation plan?
```

### `IV-02` — `stock_alerts`

- Persona: **Store Manager**
- Prompt: As Store Manager, identify urgent review candidates without issuing transfer or replenishment commands.
- Exact arguments: `{}`

```markdown
[inventory-visibility-agent] **Prepared for:** Store Manager
**Role focus:** store-level exceptions and practical review priorities

> Synthetic inventory snapshot. Read-only recommendations only; no stock is reserved, transferred, replenished, allocated, promised, or purchased. Verify all quantities in the system of record before action.

# Draft Stock Review

## Critical & Out-of-Stock Candidates

| Location | SKU | Product | On-Hand | Safety Stock | Daily Sales | Status | Nearest Available | Action Required |
|----------|-----|---------|---------|--------------|-------------|--------|-------------------|-----------------|
| Portland Flagship | SKU-2001 | Alpine Pro Winter Jacket | 0 | 24 | 8/day | OUT_OF_STOCK | Seattle Flagship (97 units, 174 mi) | Review replenishment candidate |
| Portland Mall | SKU-2001 | Alpine Pro Winter Jacket | 3 | 24 | 8/day | CRITICAL | Seattle Flagship (97 units, 176 mi) | Review transfer candidate |

**Total Alerts:** 2
**Review guidance:** Use `Review replenishment candidate` for an out-of-stock item and `Review transfer candidate` for a critical item; neither phrase executes an inventory change. Same-day transfers from the nearest available store are drafted with the reallocation plan.

## Overstock Sources

- **Seattle Flagship** / Alpine Pro Winter Jacket: 97 units, 60.6 days of supply
- **Bellevue Store** / Alpine Pro Winter Jacket: 52 units, 65.0 days of supply
- **Northgate Store** / Alpine Pro Winter Jacket: 50 units, 62.5 days of supply
- **Renton Store** / Alpine Pro Winter Jacket: 48 units, 60.0 days of supply

## Low-Stock Warnings

- **Northgate Store** / Premium Running Shoes: 7.0 days remaining
- **Renton Store** / Classic Denim Jacket: 7.5 days remaining
- **Renton Store** / Smart Fitness Tracker: 7.5 days remaining

**Low-Stock Warnings:** 3
```

### `IV-03` — `replenishment_plan`

- Persona: **Inventory Planner**
- Prompt: As Inventory Planner, show the fourteen-day replenishment scenario and its assumptions.
- Exact arguments: `{}`

```markdown
[inventory-visibility-agent] **Prepared for:** Inventory Planner
**Role focus:** network balance, replenishment scenarios, and planning assumptions

> Synthetic inventory snapshot. Read-only recommendations only; no stock is reserved, transferred, replenished, allocated, promised, or purchased. Verify all quantities in the system of record before action.

# Draft Replenishment Plan

**Target:** 14-day supply at each store (each store's own daily sales)

| Store | SKU | Product | Current | Target | Replenish Qty | Source | Lead Time | Est. Cost |
|-------|-----|---------|---------|--------|---------------|--------|-----------|-----------|
| Seattle Flagship | SKU-1001 | Classic Denim Jacket | 74 | 84 | 10 | WH-CENTRAL | 1d | $345.00 |
| Seattle Flagship | SKU-1002 | Wireless Earbuds Pro | 132 | 140 | 8 | WH-CENTRAL | 1d | $150.00 |
| Seattle Flagship | SKU-1003 | Organic Cotton T-Shirt | 210 | 224 | 14 | WH-CENTRAL | 1d | $114.80 |
| Seattle Flagship | SKU-1004 | Smart Fitness Tracker | 45 | 56 | 11 | WH-CENTRAL | 1d | $462.00 |
| Seattle Flagship | SKU-1005 | Premium Running Shoes | 38 | 42 | 4 | WH-CENTRAL | 1d | $220.00 |
| Seattle Flagship | SKU-1006 | Stainless Water Bottle | 195 | 196 | 1 | WH-CENTRAL | 1d | $6.80 |
| Seattle Flagship | SKU-1007 | Leather Crossbody Bag | 61 | 70 | 9 | WH-CENTRAL | 1d | $247.50 |
| Seattle Flagship | SKU-1008 | UV Protection Sunglasses | 88 | 98 | 10 | WH-CENTRAL | 1d | $123.00 |
| Bellevue Store | SKU-1001 | Classic Denim Jacket | 35 | 42 | 7 | WH-CENTRAL | 1d | $241.50 |
| Bellevue Store | SKU-1002 | Wireless Earbuds Pro | 67 | 84 | 17 | WH-CENTRAL | 1d | $318.75 |
| Bellevue Store | SKU-1003 | Organic Cotton T-Shirt | 98 | 126 | 28 | WH-CENTRAL | 1d | $229.60 |
| Bellevue Store | SKU-1004 | Smart Fitness Tracker | 22 | 28 | 6 | WH-CENTRAL | 1d | $252.00 |
| Bellevue Store | SKU-1005 | Premium Running Shoes | 14 | 22 | 8 | WH-CENTRAL | 1d | $440.00 |
| Bellevue Store | SKU-1006 | Stainless Water Bottle | 110 | 112 | 2 | WH-CENTRAL | 1d | $13.60 |
| Bellevue Store | SKU-1007 | Leather Crossbody Bag | 29 | 33 | 4 | WH-CENTRAL | 1d | $110.00 |
| Bellevue Store | SKU-1008 | UV Protection Sunglasses | 53 | 56 | 3 | WH-CENTRAL | 1d | $36.90 |
| Northgate Store | SKU-1001 | Classic Denim Jacket | 18 | 28 | 10 | WH-CENTRAL | 1d | $345.00 |
| Northgate Store | SKU-1002 | Wireless Earbuds Pro | 41 | 56 | 15 | WH-CENTRAL | 1d | $281.25 |
| Northgate Store | SKU-1003 | Organic Cotton T-Shirt | 65 | 84 | 19 | WH-CENTRAL | 1d | $155.80 |
| Northgate Store | SKU-1004 | Smart Fitness Tracker | 9 | 14 | 5 | WH-CENTRAL | 1d | $210.00 |
| Northgate Store | SKU-1005 | Premium Running Shoes | 7 | 14 | 7 | WH-CENTRAL | 1d | $385.00 |
| Northgate Store | SKU-1007 | Leather Crossbody Bag | 15 | 22 | 7 | WH-CENTRAL | 1d | $192.50 |
| Northgate Store | SKU-1008 | UV Protection Sunglasses | 30 | 33 | 3 | WH-CENTRAL | 1d | $36.90 |
| Renton Store | SKU-1001 | Classic Denim Jacket | 12 | 22 | 10 | WH-CENTRAL | 1d | $345.00 |
| Renton Store | SKU-1002 | Wireless Earbuds Pro | 28 | 42 | 14 | WH-CENTRAL | 1d | $262.50 |
| Renton Store | SKU-1003 | Organic Cotton T-Shirt | 44 | 56 | 12 | WH-CENTRAL | 1d | $98.40 |
| Renton Store | SKU-1004 | Smart Fitness Tracker | 6 | 11 | 5 | WH-CENTRAL | 1d | $210.00 |
| Renton Store | SKU-1005 | Premium Running Shoes | 5 | 8 | 3 | WH-CENTRAL | 1d | $165.00 |
| Renton Store | SKU-1006 | Stainless Water Bottle | 55 | 56 | 1 | WH-CENTRAL | 1d | $6.80 |
| Renton Store | SKU-1007 | Leather Crossbody Bag | 8 | 14 | 6 | WH-CENTRAL | 1d | $165.00 |
| Renton Store | SKU-1008 | UV Protection Sunglasses | 19 | 28 | 9 | WH-CENTRAL | 1d | $110.70 |
| Portland Flagship | SKU-2001 | Alpine Pro Winter Jacket | 0 | 112 | 112 | WH-SOUTH | 1d | $8,736.00 |
| Portland Flagship | SKU-1001 | Classic Denim Jacket | 74 | 84 | 10 | WH-SOUTH | 1d | $345.00 |
| Portland Flagship | SKU-1002 | Wireless Earbuds Pro | 132 | 140 | 8 | WH-SOUTH | 1d | $150.00 |
| Portland Flagship | SKU-1003 | Organic Cotton T-Shirt | 210 | 224 | 14 | WH-SOUTH | 1d | $114.80 |
| Portland Flagship | SKU-1004 | Smart Fitness Tracker | 45 | 56 | 11 | WH-SOUTH | 1d | $462.00 |
| Portland Flagship | SKU-1005 | Premium Running Shoes | 38 | 42 | 4 | WH-SOUTH | 1d | $220.00 |
| Portland Flagship | SKU-1006 | Stainless Water Bottle | 195 | 196 | 1 | WH-SOUTH | 1d | $6.80 |
| Portland Flagship | SKU-1007 | Leather Crossbody Bag | 61 | 70 | 9 | WH-SOUTH | 1d | $247.50 |
| Portland Flagship | SKU-1008 | UV Protection Sunglasses | 88 | 98 | 10 | WH-SOUTH | 1d | $123.00 |
| Portland Mall | SKU-2001 | Alpine Pro Winter Jacket | 3 | 112 | 109 | WH-SOUTH | 1d | $8,502.00 |
| Portland Mall | SKU-1001 | Classic Denim Jacket | 35 | 42 | 7 | WH-SOUTH | 1d | $241.50 |
| Portland Mall | SKU-1002 | Wireless Earbuds Pro | 67 | 84 | 17 | WH-SOUTH | 1d | $318.75 |
| Portland Mall | SKU-1003 | Organic Cotton T-Shirt | 98 | 126 | 28 | WH-SOUTH | 1d | $229.60 |
| Portland Mall | SKU-1004 | Smart Fitness Tracker | 22 | 28 | 6 | WH-SOUTH | 1d | $252.00 |
| Portland Mall | SKU-1005 | Premium Running Shoes | 14 | 22 | 8 | WH-SOUTH | 1d | $440.00 |
| Portland Mall | SKU-1006 | Stainless Water Bottle | 110 | 112 | 2 | WH-SOUTH | 1d | $13.60 |
| Portland Mall | SKU-1007 | Leather Crossbody Bag | 29 | 33 | 4 | WH-SOUTH | 1d | $110.00 |
| Portland Mall | SKU-1008 | UV Protection Sunglasses | 53 | 56 | 3 | WH-SOUTH | 1d | $36.90 |

**Estimated Total Replenishment Cost:** $26,830.75
Scheduled replenishment is a draft for planner approval; no purchase or transfer order is created.
```

### `IV-04` — `channel_allocation`

- Persona: **Category Manager**
- Prompt: As Category Manager, compare the channel planning scenario without reserving any stock.
- Exact arguments: `{"sku_id":"SKU-1003"}`

```markdown
[inventory-visibility-agent] **Prepared for:** Category Manager
**Role focus:** category health, availability patterns, and tradeoffs

> Synthetic inventory snapshot. Read-only recommendations only; no stock is reserved, transferred, replenished, allocated, promised, or purchased. Verify all quantities in the system of record before action.

# Channel Allocation Scenario

**SKU:** SKU-2001 — Alpine Pro Winter Jacket
**Total Network Inventory:** 1,190 units (detailed stores and warehouses)

| Channel | Weight | Allocated Units | Daily Demand Avg | Days Coverage |
|---------|--------|-----------------|------------------|---------------|
| In Store | 45% | 536 | 320 | 1.7 |
| Online Ship | 30% | 357 | 215 | 1.7 |
| Bopis | 15% | 178 | 108 | 1.6 |
| Marketplace | 10% | 119 | 72 | 1.7 |

## Allocation Recommendations

- **In-Store Scenario:** Model a larger share for flagship and mall demand
- **Online Buffer:** Model a three-day planning buffer for e-commerce
- **BOPIS Buffer:** Model a pickup buffer; do not reserve units
- **Marketplace Review:** Model a cap to reduce channel conflict
```

### `IV-05` — `transfer_plan`

- Persona: **Inventory Planner**
- Prompt: Yes, create the reallocation plan with cost and timing details.
- Exact arguments: `{}`

```markdown
[inventory-visibility-agent] **Prepared for:** Inventory Planner
**Role focus:** network balance, replenishment scenarios, and planning assumptions

> Synthetic inventory snapshot. Read-only recommendations only; no stock is reserved, transferred, replenished, allocated, promised, or purchased. Verify all quantities in the system of record before action.

# Draft Reallocation Plan: Seattle -> Portland

Reallocation plan for the Alpine Pro Winter Jacket, optimized for 36-hour execution with minimal disruption and strong ROI.

## Phase 1: Emergency (Next 12 Hours)

- Move 40 units from Seattle Flagship to Portland Flagship
- Transport: Overnight van ($340)
- Pickup: 6 PM tonight; Arrival: Tomorrow 7 AM
- Revenue recovery: $6,800 (3-day window)

## Phase 2: Strategic (24-48 Hours)

- Move 80 units from 3 Seattle suburban stores
  - Bellevue Store -> Portland Mall: 27 units
  - Northgate Store -> Portland Mall: 27 units
  - Renton Store -> Portland Flagship: 26 units
- Transport: Regular delivery truck ($180)
- Pickup: Tomorrow morning route; Arrival: Day after tomorrow
- Revenue recovery: $11,600 (week-long window)

## Total Plan

| Metric | Value |
|---|---|
| Units transferred | 120 |
| Transportation cost | $520 |
| Revenue recovered | $18,400 |
| ROI | 35:1 |

**Impact on Seattle:** still leaves 127 units (31 days of supply at the current 4/day rate).

Source: [Logistics Network + Cost Calculator + Demand Model]

This is a draft plan: nothing has moved and no van or truck is booked. Next step: approve it so an authorized planner can release both phases.
```

### `IV-06` — `network_health`

- Persona: **Inventory Planner**
- Prompt: Approved. Execute both phases and show me system-wide inventory health.
- Exact arguments: `{}`

```markdown
[inventory-visibility-agent] **Prepared for:** Inventory Planner
**Role focus:** network balance, replenishment scenarios, and planning assumptions

> Synthetic inventory snapshot. Read-only recommendations only; no stock is reserved, transferred, replenished, allocated, promised, or purchased. Verify all quantities in the system of record before action.

# Transfer Release Packet and System-Wide Inventory Health

Transfer packet ready for release: the Seattle van pickup slot is 6 PM tonight. System-wide analysis shows 8 more allocation opportunities.

## Transfer Status (ready for you to release; nothing has moved yet)

- Phase 1: Overnight van, pickup 6 PM tonight, 40 units, arrival Tomorrow 7 AM - Ready for release
- Phase 2: Regular delivery truck, pickup Tomorrow morning route, 80 units, arrival Day after tomorrow - Ready for release
- Store systems: new quantities staged for 120 units (applied on release)
- E-commerce: Portland inventory becomes visible online once the transfer is received

## System-Wide Inventory Health

| Metric | Current |
|---|---|
| Stock balance score | 72/100 |
| Days of supply | 43 days |
| Overstock value | $2.8M |
| Stockout incidents | 147/month |

**Overstock by category:** Outerwear $920,000; Apparel $740,000; Electronics $610,000; Footwear $330,000; Accessories $200,000

**Slow movers:** Stainless Water Bottle (19 weeks of supply, summer item carried into winter); UV Protection Sunglasses (17 weeks of supply, seasonal demand down 40% since September); Organic Cotton T-Shirt (14 weeks of supply, base tee overbought for fall)

**Seasonal demand:** Outerwear demand runs 2.1x the annual average from November to January; summer accessories run 0.4x.

## Additional Opportunities

- 8 SKUs with similar imbalances
- Combined recovery potential: $84,200
- Transport investment: $3,400
- Total ROI: 25:1

Source: [Inventory Optimization Engine + All Locations]

Next step: optimize all 8 opportunities?
```

### `IV-07` — `automation_recommendations`

- Persona: **Inventory Planner**
- Prompt: Yes, optimize all 8 and show me the warehouse automation recommendations.
- Exact arguments: `{}`

```markdown
[inventory-visibility-agent] **Prepared for:** Inventory Planner
**Role focus:** network balance, replenishment scenarios, and planning assumptions

> Synthetic inventory snapshot. Read-only recommendations only; no stock is reserved, transferred, replenished, allocated, promised, or purchased. Verify all quantities in the system of record before action.

# Optimization Queue and Warehouse Automation Recommendations

All 8 SKU reallocations drafted for the next 72 hours. Warehouse automation analysis reveals $340K annual savings opportunity.

## Optimization Queue (draft for release)

| SKU | Product | Route | Units | Recovery | Transport |
|---|---|---|---|---|---|
| SKU-1001 | Classic Denim Jacket | Spokane -> Seattle | 95 | $11,400 | $460 |
| SKU-1002 | Wireless Earbuds Pro | Seattle -> Portland | 120 | $14,600 | $520 |
| SKU-1003 | Organic Cotton T-Shirt | Portland -> Tacoma | 140 | $6,300 | $380 |
| SKU-1004 | Smart Fitness Tracker | Seattle -> Eugene | 60 | $13,900 | $410 |
| SKU-1005 | Premium Running Shoes | Bellevue -> Portland | 55 | $12,500 | $400 |
| SKU-1006 | Stainless Water Bottle | Salem -> Seattle | 90 | $4,100 | $330 |
| SKU-1007 | Leather Crossbody Bag | Seattle -> Spokane | 65 | $10,600 | $450 |
| SKU-1008 | UV Protection Sunglasses | Portland -> Boise | 55 | $10,800 | $450 |

- 8 SKU transfers drafted across a 3-day window
- Total units moving: 680 across 15 routes
- Combined revenue recovery: $84,200
- Transport investment: $3,400
- Store notifications drafted for release by the planner; none sent

## Warehouse Automation Recommendations

**Priority 1: RFID Tracking ($85K investment)**
- Real-time location accuracy: 87% today, 99.8% with RFID
- Picking speed: +34%
- Annual labor savings: $127,000/year
- Payback: 8 months

**Priority 2: Auto-Replenishment ($45K investment)**
- Eliminate manual reorder points
- Stockouts: -62%
- Annual savings: $142,000/year
- Payback: 3.8 months

**Priority 3: Predictive Allocation ($32K investment)**
- AI-driven transfers (prevent imbalances)
- Revenue protection: $71,000/year
- Payback: 5.4 months

**Total annual savings opportunity:** $340,000

Source: [Warehouse Operations + Technology Assessment]

Next step: generate the investment proposal?
```

### `IV-08` — `investment_proposal`

- Persona: **Inventory Planner**
- Prompt: Yes, create the investment proposal with 3-year financial projections.
- Exact arguments: `{}`

```markdown
[inventory-visibility-agent] **Prepared for:** Inventory Planner
**Role focus:** network balance, replenishment scenarios, and planning assumptions

> Synthetic inventory snapshot. Read-only recommendations only; no stock is reserved, transferred, replenished, allocated, promised, or purchased. Verify all quantities in the system of record before action.

# Draft Investment Proposal: Inventory Automation

## Investment Required

- RFID Tracking: $85K
- Auto-Replenishment: $45K
- Predictive Allocation: $32K
- **Total: $162K**

## Annual Benefits

| Year | Labor Savings | Stockout Reduction | Revenue Protection | Total |
|---|---|---|---|---|
| Year 1 | $127K | $142K | $71K | $340K |
| Year 2 | $127K | $142K | $71K | $340K |
| Year 3 | $127K | $142K | $71K | $340K |

## 3-Year Summary

- Cumulative benefits: $1,020,000
- Net value: $858,000
- ROI: 530%
- Payback: 5.7 months

## Operational Improvements

- Inventory accuracy: 87% -> 99.8%
- Stockouts: -62%
- Manual reorders: Eliminated

Source: [Financial Planning + Technology ROI Models]

Draft ready for you to share with the CFO and operations team in Microsoft Teams; nothing has been sent.
```
