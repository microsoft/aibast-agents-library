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

## Downtown Flagship (`STR-001`)

| SKU | Product | On-Hand | Safety Stock | Status | Days of Supply |
|-----|---------|---------|--------------|--------|----------------|
| SKU-1001 | Classic Denim Jacket | 74 | 30 | HEALTHY | 11.9 |
| SKU-1002 | Wireless Earbuds Pro | 132 | 50 | HEALTHY | 13.5 |
| SKU-1003 | Organic Cotton T-Shirt | 210 | 80 | HEALTHY | 14.5 |
| SKU-1004 | Smart Fitness Tracker | 45 | 20 | HEALTHY | 14.5 |
| SKU-1005 | Premium Running Shoes | 38 | 15 | HEALTHY | 14.1 |
| SKU-1006 | Stainless Water Bottle | 195 | 70 | HEALTHY | 16.2 |
| SKU-1007 | Leather Crossbody Bag | 61 | 25 | HEALTHY | 13.9 |
| SKU-1008 | UV Protection Sunglasses | 88 | 35 | HEALTHY | 12.1 |

## Northshore Mall (`STR-002`)

| SKU | Product | On-Hand | Safety Stock | Status | Days of Supply |
|-----|---------|---------|--------------|--------|----------------|
| SKU-1001 | Classic Denim Jacket | 35 | 15 | HEALTHY | 5.6 |
| SKU-1002 | Wireless Earbuds Pro | 67 | 30 | HEALTHY | 6.8 |
| SKU-1003 | Organic Cotton T-Shirt | 98 | 45 | HEALTHY | 6.8 |
| SKU-1004 | Smart Fitness Tracker | 22 | 10 | HEALTHY | 7.1 |
| SKU-1005 | Premium Running Shoes | 14 | 8 | HEALTHY | 5.2 |
| SKU-1006 | Stainless Water Bottle | 110 | 40 | HEALTHY | 9.2 |
| SKU-1007 | Leather Crossbody Bag | 29 | 12 | HEALTHY | 6.6 |
| SKU-1008 | UV Protection Sunglasses | 53 | 20 | HEALTHY | 7.3 |

## Oakbrook Center (`STR-003`)

| SKU | Product | On-Hand | Safety Stock | Status | Days of Supply |
|-----|---------|---------|--------------|--------|----------------|
| SKU-1001 | Classic Denim Jacket | 18 | 10 | HEALTHY | 2.9 |
| SKU-1002 | Wireless Earbuds Pro | 41 | 20 | HEALTHY | 4.2 |
| SKU-1003 | Organic Cotton T-Shirt | 65 | 30 | HEALTHY | 4.5 |
| SKU-1004 | Smart Fitness Tracker | 9 | 5 | HEALTHY | 2.9 |
| SKU-1005 | Premium Running Shoes | 7 | 5 | LOW | 2.6 |
| SKU-1006 | Stainless Water Bottle | 72 | 25 | HEALTHY | 6.0 |
| SKU-1007 | Leather Crossbody Bag | 15 | 8 | HEALTHY | 3.4 |
| SKU-1008 | UV Protection Sunglasses | 30 | 12 | HEALTHY | 4.1 |

## Michigan Ave Express (`STR-004`)

| SKU | Product | On-Hand | Safety Stock | Status | Days of Supply |
|-----|---------|---------|--------------|--------|----------------|
| SKU-1001 | Classic Denim Jacket | 12 | 8 | LOW | 1.9 |
| SKU-1002 | Wireless Earbuds Pro | 28 | 15 | HEALTHY | 2.9 |
| SKU-1003 | Organic Cotton T-Shirt | 44 | 20 | HEALTHY | 3.0 |
| SKU-1004 | Smart Fitness Tracker | 6 | 4 | LOW | 1.9 |
| SKU-1005 | Premium Running Shoes | 5 | 3 | HEALTHY | 1.9 |
| SKU-1006 | Stainless Water Bottle | 55 | 20 | HEALTHY | 4.6 |
| SKU-1007 | Leather Crossbody Bag | 8 | 5 | HEALTHY | 1.8 |
| SKU-1008 | UV Protection Sunglasses | 19 | 10 | HEALTHY | 2.6 |

**Total Network Inventory:** 26,315 units across 6 locations
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

| Location | SKU | Product | On-Hand | Safety Stock | Status | Action Required |
|----------|-----|---------|---------|--------------|--------|-----------------|

**Total Alerts:** 0
**Review guidance:** Use `Review replenishment candidate` for an out-of-stock item and `Review transfer candidate` for a critical item; neither phrase executes an inventory change.

## Low-Stock Warnings

- **Oakbrook Center** / Premium Running Shoes: 2.6 days remaining
- **Michigan Ave Express** / Classic Denim Jacket: 1.9 days remaining
- **Michigan Ave Express** / Smart Fitness Tracker: 1.9 days remaining

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

**Target:** 14-day supply at each store

## Downtown Flagship (`STR-001`)

| SKU | Product | Current | Target | Replenish Qty | Source | Lead Time | Est. Cost |
|-----|---------|---------|--------|---------------|--------|-----------|-----------|
| SKU-1001 | Classic Denim Jacket | 74 | 86 | 12 | WH-CENTRAL | 1d | $414.00 |
| SKU-1002 | Wireless Earbuds Pro | 132 | 137 | 5 | WH-CENTRAL | 1d | $93.75 |
| SKU-1008 | UV Protection Sunglasses | 88 | 102 | 14 | WH-CENTRAL | 1d | $172.20 |

## Northshore Mall (`STR-002`)

| SKU | Product | Current | Target | Replenish Qty | Source | Lead Time | Est. Cost |
|-----|---------|---------|--------|---------------|--------|-----------|-----------|
| SKU-1001 | Classic Denim Jacket | 35 | 86 | 51 | WH-CENTRAL | 1d | $1,759.50 |
| SKU-1002 | Wireless Earbuds Pro | 67 | 137 | 70 | WH-CENTRAL | 1d | $1,312.50 |
| SKU-1003 | Organic Cotton T-Shirt | 98 | 203 | 105 | WH-CENTRAL | 1d | $861.00 |
| SKU-1004 | Smart Fitness Tracker | 22 | 43 | 21 | WH-CENTRAL | 1d | $882.00 |
| SKU-1005 | Premium Running Shoes | 14 | 37 | 23 | WH-CENTRAL | 1d | $1,265.00 |
| SKU-1006 | Stainless Water Bottle | 110 | 168 | 58 | WH-CENTRAL | 1d | $394.40 |
| SKU-1007 | Leather Crossbody Bag | 29 | 61 | 32 | WH-CENTRAL | 1d | $880.00 |
| SKU-1008 | UV Protection Sunglasses | 53 | 102 | 49 | WH-CENTRAL | 1d | $602.70 |

## Oakbrook Center (`STR-003`)

| SKU | Product | Current | Target | Replenish Qty | Source | Lead Time | Est. Cost |
|-----|---------|---------|--------|---------------|--------|-----------|-----------|
| SKU-1001 | Classic Denim Jacket | 18 | 86 | 68 | WH-CENTRAL | 2d | $2,346.00 |
| SKU-1002 | Wireless Earbuds Pro | 41 | 137 | 96 | WH-CENTRAL | 2d | $1,800.00 |
| SKU-1003 | Organic Cotton T-Shirt | 65 | 203 | 138 | WH-CENTRAL | 2d | $1,131.60 |
| SKU-1004 | Smart Fitness Tracker | 9 | 43 | 34 | WH-CENTRAL | 2d | $1,428.00 |
| SKU-1005 | Premium Running Shoes | 7 | 37 | 30 | WH-CENTRAL | 2d | $1,650.00 |
| SKU-1006 | Stainless Water Bottle | 72 | 168 | 96 | WH-CENTRAL | 2d | $652.80 |
| SKU-1007 | Leather Crossbody Bag | 15 | 61 | 46 | WH-CENTRAL | 2d | $1,265.00 |
| SKU-1008 | UV Protection Sunglasses | 30 | 102 | 72 | WH-CENTRAL | 2d | $885.60 |

## Michigan Ave Express (`STR-004`)

| SKU | Product | Current | Target | Replenish Qty | Source | Lead Time | Est. Cost |
|-----|---------|---------|--------|---------------|--------|-----------|-----------|
| SKU-1001 | Classic Denim Jacket | 12 | 86 | 74 | WH-CENTRAL | 1d | $2,553.00 |
| SKU-1002 | Wireless Earbuds Pro | 28 | 137 | 109 | WH-CENTRAL | 1d | $2,043.75 |
| SKU-1003 | Organic Cotton T-Shirt | 44 | 203 | 159 | WH-CENTRAL | 1d | $1,303.80 |
| SKU-1004 | Smart Fitness Tracker | 6 | 43 | 37 | WH-CENTRAL | 1d | $1,554.00 |
| SKU-1005 | Premium Running Shoes | 5 | 37 | 32 | WH-CENTRAL | 1d | $1,760.00 |
| SKU-1006 | Stainless Water Bottle | 55 | 168 | 113 | WH-CENTRAL | 1d | $768.40 |
| SKU-1007 | Leather Crossbody Bag | 8 | 61 | 53 | WH-CENTRAL | 1d | $1,457.50 |
| SKU-1008 | UV Protection Sunglasses | 19 | 102 | 83 | WH-CENTRAL | 1d | $1,020.90 |

**Estimated Total Replenishment Cost:** $32,257.40
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

**SKU:** SKU-1001 — Classic Denim Jacket
**Total Network Inventory:** 2,409 units

| Channel | Weight | Allocated Units | Daily Demand Avg | Days Coverage |
|---------|--------|-----------------|------------------|---------------|
| In Store | 45% | 1,086 | 320 | 3.4 |
| Online Ship | 30% | 722 | 215 | 3.4 |
| Bopis | 15% | 361 | 108 | 3.3 |
| Marketplace | 10% | 240 | 72 | 3.3 |

## Allocation Recommendations

- **In-Store Scenario:** Model a larger share for flagship and mall demand
- **Online Buffer:** Model a three-day planning buffer for e-commerce
- **BOPIS Buffer:** Model a pickup buffer; do not reserve units
- **Marketplace Review:** Model a cap to reduce channel conflict
```
