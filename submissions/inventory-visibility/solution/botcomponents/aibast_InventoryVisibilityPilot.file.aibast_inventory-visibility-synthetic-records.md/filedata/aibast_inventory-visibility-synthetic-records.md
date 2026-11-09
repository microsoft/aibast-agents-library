# Inventory Visibility — Complete Synthetic Records

> **SYNTHETIC, READ-ONLY PILOT DATA.** Every identifier, name, date, status,
> quantity, amount, preference, interaction, order, cart, case, campaign, and
> metric below is fictional. It is reference evidence, not a live-system value
> or authorization to take action.

## Authoritative provenance

- Deterministic source: `agents/@aibast-agents-library/retail_cpg_stacks/inventory_visibility_stack/inventory_visibility_agent.py`
- Locked case contract: `tests/demo_cases/inventory-visibility.json`
- Captured evidence: `solutions/inventory-visibility/evals/transcripts.json`
- The JSON blocks below are exact literals copied from the deterministic source.
- Preserve identifiers, spelling, capitalization, dates, statuses, and numeric values.
- If production data differs, stop and verify in the authorized system of record.

## Locked-case source selections

| Case | Persona | Operation | Exact arguments |
|---|---|---|---|
| `IV-01` | Inventory Planner | `inventory_dashboard` | `{"location_id":"STR-001"}` |
| `IV-02` | Store Manager | `stock_alerts` | `{}` |
| `IV-03` | Inventory Planner | `replenishment_plan` | `{}` |
| `IV-04` | Category Manager | `channel_allocation` | `{"sku_id":"SKU-1003"}` |
| `IV-05` | Inventory Planner | `transfer_plan` | `{}` |
| `IV-06` | Inventory Planner | `network_health` | `{}` |
| `IV-07` | Inventory Planner | `automation_recommendations` | `{}` |
| `IV-08` | Inventory Planner | `investment_proposal` | `{}` |

## Demo scenario (video walkthrough)

A regional retailer runs 51 locations: 47 stores, 3 warehouses and an e-commerce reserve. The six detailed stores
are Seattle Flagship (`STR-001`), Bellevue Store (`STR-002`), Northgate Store (`STR-003`), Renton Store (`STR-004`),
Portland Flagship (`STR-005`) and Portland Mall (`STR-006`); the other 41 stores are rolled up in `NETWORK_ROLLUP`.
The hero item is the Alpine Pro Winter Jacket (`SKU-2001`, retail $170). Days of supply use each store's own daily
sales (`DAILY_SELL_THROUGH` is per store). Every operation has demo defaults; no identifier is needed.

| Turn | User prompt | Operation | Key values |
|---|---|---|---|
| 1 | Show me real-time inventory status for our top-selling winter jackets across all locations | `inventory_dashboard` | 51 locations; Stores (47) 1,847 58% Unbalanced; Warehouses (3) 940 29% Healthy; In-transit 285 9% Active; E-comm reserve 128 4% Low; total 3,200; Portland Flagship 0 units (sold out 3 days ago); Portland Mall 3 units (selling 8/day); Seattle stores 247 units excess (selling 4/day); transfer 120 units Seattle -> Portland = $18,400 recovered sales |
| 2 | Yes, create the reallocation plan with cost and timing details | `transfer_plan` | Draft Reallocation Plan; Phase 1 Emergency: 40 units Seattle Flagship -> Portland Flagship, overnight van $340, pickup 6 PM tonight, arrival tomorrow 7 AM, $6,800 (3-day window); Phase 2 Strategic: 80 units from 3 Seattle suburban stores, regular delivery truck $180, $11,600 (week-long window); total 120 units, $520, $18,400, ROI 35:1; Seattle keeps 127 units (31 days of supply at 4/day) |
| 3 | Approved. Execute both phases and show me system-wide inventory health | `network_health` | Transfer release packet (ready for release, nothing has moved); Stock balance score 72/100; days of supply 43; overstock $2.8M; stockouts 147/month; Slow movers; 8 SKUs with similar imbalances; $84,200 recovery; $3,400 transport; ROI 25:1 |
| 4 | Yes, optimize all 8 and show me the warehouse automation recommendations | `automation_recommendations` | 8 SKU transfers drafted, 680 across 15 routes, $84,200, $3,400; RFID Tracking $85K (87% accuracy, picking +34%, $127,000/year, payback 8 months); Auto-Replenishment $45K (stockouts -62%, $142,000/year, 3.8 months); Predictive Allocation $32K ($71,000/year, 5.4 months); total $340,000 |
| 5 | Yes, create the investment proposal with 3-year financial projections | `investment_proposal` | Draft Investment Proposal; total $162K; $340K per year; cumulative $1,020,000; net $858,000; ROI 530% (858,000 / 162,000; the video rounds to 531%); payback 5.7 months; accuracy 87% -> 99.8% |

Approvals in turns 3 and 4 never move stock or notify stores: the agent returns a release-ready packet for an
authorized planner, and the proposal is a draft ready for the user to share with the CFO and operations team.
The plan leaves Seattle with 127 units, which is 31 days of supply at the 4/day Seattle rate (the video says an
8-week supply; the data keeps the arithmetic consistent).

## Complete deterministic record sets

### `STORES`

```json
{
  "STR-001": {
    "name": "Seattle Flagship",
    "city": "Seattle",
    "state": "WA",
    "region": "Seattle",
    "type": "flagship",
    "capacity_sqft": 42000
  },
  "STR-002": {
    "name": "Bellevue Store",
    "city": "Bellevue",
    "state": "WA",
    "region": "Seattle",
    "type": "suburban",
    "capacity_sqft": 18500
  },
  "STR-003": {
    "name": "Northgate Store",
    "city": "Seattle",
    "state": "WA",
    "region": "Seattle",
    "type": "suburban",
    "capacity_sqft": 12000
  },
  "STR-004": {
    "name": "Renton Store",
    "city": "Renton",
    "state": "WA",
    "region": "Seattle",
    "type": "suburban",
    "capacity_sqft": 9500
  },
  "STR-005": {
    "name": "Portland Flagship",
    "city": "Portland",
    "state": "OR",
    "region": "Portland",
    "type": "flagship",
    "capacity_sqft": 38000
  },
  "STR-006": {
    "name": "Portland Mall",
    "city": "Portland",
    "state": "OR",
    "region": "Portland",
    "type": "mall",
    "capacity_sqft": 16000
  }
}
```

### `WAREHOUSES`

```json
{
  "WH-CENTRAL": {
    "name": "Central Distribution Center",
    "city": "Kent",
    "state": "WA",
    "capacity_pallets": 22000
  },
  "WH-EAST": {
    "name": "East Regional Warehouse",
    "city": "Spokane",
    "state": "WA",
    "capacity_pallets": 14000
  },
  "WH-SOUTH": {
    "name": "South Regional Warehouse",
    "city": "Salem",
    "state": "OR",
    "capacity_pallets": 12000
  }
}
```

### `SKUS`

```json
{
  "SKU-2001": {
    "name": "Alpine Pro Winter Jacket",
    "category": "Outerwear",
    "unit_cost": 78.0,
    "retail_price": 170.0,
    "aliases": [
      "winter jacket",
      "alpine",
      "jacket"
    ]
  },
  "SKU-1001": {
    "name": "Classic Denim Jacket",
    "category": "Apparel",
    "unit_cost": 34.5,
    "retail_price": 89.99,
    "aliases": [
      "denim"
    ]
  },
  "SKU-1002": {
    "name": "Wireless Earbuds Pro",
    "category": "Electronics",
    "unit_cost": 18.75,
    "retail_price": 59.99,
    "aliases": [
      "earbuds"
    ]
  },
  "SKU-1003": {
    "name": "Organic Cotton T-Shirt",
    "category": "Apparel",
    "unit_cost": 8.2,
    "retail_price": 29.99,
    "aliases": [
      "t-shirt",
      "tee"
    ]
  },
  "SKU-1004": {
    "name": "Smart Fitness Tracker",
    "category": "Electronics",
    "unit_cost": 42.0,
    "retail_price": 129.99,
    "aliases": [
      "fitness tracker"
    ]
  },
  "SKU-1005": {
    "name": "Premium Running Shoes",
    "category": "Footwear",
    "unit_cost": 55.0,
    "retail_price": 149.99,
    "aliases": [
      "running shoes",
      "shoes"
    ]
  },
  "SKU-1006": {
    "name": "Stainless Water Bottle",
    "category": "Accessories",
    "unit_cost": 6.8,
    "retail_price": 24.99,
    "aliases": [
      "water bottle"
    ]
  },
  "SKU-1007": {
    "name": "Leather Crossbody Bag",
    "category": "Accessories",
    "unit_cost": 27.5,
    "retail_price": 79.99,
    "aliases": [
      "crossbody",
      "bag"
    ]
  },
  "SKU-1008": {
    "name": "UV Protection Sunglasses",
    "category": "Accessories",
    "unit_cost": 12.3,
    "retail_price": 44.99,
    "aliases": [
      "sunglasses"
    ]
  }
}
```

### `INVENTORY`

```json
{
  "STR-001": {
    "SKU-2001": 97,
    "SKU-1001": 74,
    "SKU-1002": 132,
    "SKU-1003": 210,
    "SKU-1004": 45,
    "SKU-1005": 38,
    "SKU-1006": 195,
    "SKU-1007": 61,
    "SKU-1008": 88
  },
  "STR-002": {
    "SKU-2001": 52,
    "SKU-1001": 35,
    "SKU-1002": 67,
    "SKU-1003": 98,
    "SKU-1004": 22,
    "SKU-1005": 14,
    "SKU-1006": 110,
    "SKU-1007": 29,
    "SKU-1008": 53
  },
  "STR-003": {
    "SKU-2001": 50,
    "SKU-1001": 18,
    "SKU-1002": 41,
    "SKU-1003": 65,
    "SKU-1004": 9,
    "SKU-1005": 7,
    "SKU-1006": 72,
    "SKU-1007": 15,
    "SKU-1008": 30
  },
  "STR-004": {
    "SKU-2001": 48,
    "SKU-1001": 12,
    "SKU-1002": 28,
    "SKU-1003": 44,
    "SKU-1004": 6,
    "SKU-1005": 5,
    "SKU-1006": 55,
    "SKU-1007": 8,
    "SKU-1008": 19
  },
  "STR-005": {
    "SKU-2001": 0,
    "SKU-1001": 74,
    "SKU-1002": 132,
    "SKU-1003": 210,
    "SKU-1004": 45,
    "SKU-1005": 38,
    "SKU-1006": 195,
    "SKU-1007": 61,
    "SKU-1008": 88
  },
  "STR-006": {
    "SKU-2001": 3,
    "SKU-1001": 35,
    "SKU-1002": 67,
    "SKU-1003": 98,
    "SKU-1004": 22,
    "SKU-1005": 14,
    "SKU-1006": 110,
    "SKU-1007": 29,
    "SKU-1008": 53
  },
  "WH-CENTRAL": {
    "SKU-2001": 420,
    "SKU-1001": 1450,
    "SKU-1002": 2300,
    "SKU-1003": 3800,
    "SKU-1004": 780,
    "SKU-1005": 620,
    "SKU-1006": 4100,
    "SKU-1007": 950,
    "SKU-1008": 1700
  },
  "WH-EAST": {
    "SKU-2001": 310,
    "SKU-1001": 820,
    "SKU-1002": 1100,
    "SKU-1003": 2200,
    "SKU-1004": 410,
    "SKU-1005": 350,
    "SKU-1006": 2600,
    "SKU-1007": 530,
    "SKU-1008": 900
  },
  "WH-SOUTH": {
    "SKU-2001": 210,
    "SKU-1001": 560,
    "SKU-1002": 740,
    "SKU-1003": 1500,
    "SKU-1004": 280,
    "SKU-1005": 240,
    "SKU-1006": 1700,
    "SKU-1007": 360,
    "SKU-1008": 610
  }
}
```

### `SAFETY_STOCK`

```json
{
  "STR-001": {
    "SKU-2001": 12,
    "SKU-1001": 30,
    "SKU-1002": 50,
    "SKU-1003": 80,
    "SKU-1004": 20,
    "SKU-1005": 15,
    "SKU-1006": 70,
    "SKU-1007": 25,
    "SKU-1008": 35
  },
  "STR-002": {
    "SKU-2001": 6,
    "SKU-1001": 15,
    "SKU-1002": 30,
    "SKU-1003": 45,
    "SKU-1004": 10,
    "SKU-1005": 8,
    "SKU-1006": 40,
    "SKU-1007": 12,
    "SKU-1008": 20
  },
  "STR-003": {
    "SKU-2001": 6,
    "SKU-1001": 10,
    "SKU-1002": 20,
    "SKU-1003": 30,
    "SKU-1004": 5,
    "SKU-1005": 5,
    "SKU-1006": 25,
    "SKU-1007": 8,
    "SKU-1008": 12
  },
  "STR-004": {
    "SKU-2001": 6,
    "SKU-1001": 8,
    "SKU-1002": 15,
    "SKU-1003": 20,
    "SKU-1004": 4,
    "SKU-1005": 3,
    "SKU-1006": 20,
    "SKU-1007": 5,
    "SKU-1008": 10
  },
  "STR-005": {
    "SKU-2001": 24,
    "SKU-1001": 30,
    "SKU-1002": 50,
    "SKU-1003": 80,
    "SKU-1004": 20,
    "SKU-1005": 15,
    "SKU-1006": 70,
    "SKU-1007": 25,
    "SKU-1008": 35
  },
  "STR-006": {
    "SKU-2001": 24,
    "SKU-1001": 15,
    "SKU-1002": 30,
    "SKU-1003": 45,
    "SKU-1004": 10,
    "SKU-1005": 8,
    "SKU-1006": 40,
    "SKU-1007": 12,
    "SKU-1008": 20
  }
}
```

### `LEAD_TIMES_DAYS`

```json
{
  "WH-CENTRAL": {
    "STR-001": 1,
    "STR-002": 1,
    "STR-003": 1,
    "STR-004": 1,
    "STR-005": 2,
    "STR-006": 2
  },
  "WH-EAST": {
    "STR-001": 2,
    "STR-002": 2,
    "STR-003": 2,
    "STR-004": 2,
    "STR-005": 3,
    "STR-006": 3
  },
  "WH-SOUTH": {
    "STR-001": 2,
    "STR-002": 2,
    "STR-003": 2,
    "STR-004": 2,
    "STR-005": 1,
    "STR-006": 1
  }
}
```

### `CHANNEL_DEMAND`

```json
{
  "in_store": {
    "weight": 0.45,
    "daily_units_avg": 320
  },
  "online_ship": {
    "weight": 0.3,
    "daily_units_avg": 215
  },
  "bopis": {
    "weight": 0.15,
    "daily_units_avg": 108
  },
  "marketplace": {
    "weight": 0.1,
    "daily_units_avg": 72
  }
}
```

### `DAILY_SELL_THROUGH`

```json
{
  "STR-001": {
    "SKU-2001": 1.6,
    "SKU-1001": 6.0,
    "SKU-1002": 10.0,
    "SKU-1003": 16.0,
    "SKU-1004": 4.0,
    "SKU-1005": 3.0,
    "SKU-1006": 14.0,
    "SKU-1007": 5.0,
    "SKU-1008": 7.0
  },
  "STR-002": {
    "SKU-2001": 0.8,
    "SKU-1001": 3.0,
    "SKU-1002": 6.0,
    "SKU-1003": 9.0,
    "SKU-1004": 2.0,
    "SKU-1005": 1.6,
    "SKU-1006": 8.0,
    "SKU-1007": 2.4,
    "SKU-1008": 4.0
  },
  "STR-003": {
    "SKU-2001": 0.8,
    "SKU-1001": 2.0,
    "SKU-1002": 4.0,
    "SKU-1003": 6.0,
    "SKU-1004": 1.0,
    "SKU-1005": 1.0,
    "SKU-1006": 5.0,
    "SKU-1007": 1.6,
    "SKU-1008": 2.4
  },
  "STR-004": {
    "SKU-2001": 0.8,
    "SKU-1001": 1.6,
    "SKU-1002": 3.0,
    "SKU-1003": 4.0,
    "SKU-1004": 0.8,
    "SKU-1005": 0.6,
    "SKU-1006": 4.0,
    "SKU-1007": 1.0,
    "SKU-1008": 2.0
  },
  "STR-005": {
    "SKU-2001": 8.0,
    "SKU-1001": 6.0,
    "SKU-1002": 10.0,
    "SKU-1003": 16.0,
    "SKU-1004": 4.0,
    "SKU-1005": 3.0,
    "SKU-1006": 14.0,
    "SKU-1007": 5.0,
    "SKU-1008": 7.0
  },
  "STR-006": {
    "SKU-2001": 8.0,
    "SKU-1001": 3.0,
    "SKU-1002": 6.0,
    "SKU-1003": 9.0,
    "SKU-1004": 2.0,
    "SKU-1005": 1.6,
    "SKU-1006": 8.0,
    "SKU-1007": 2.4,
    "SKU-1008": 4.0
  }
}
```

### `NETWORK_ROLLUP`

```json
{
  "SKU-2001": {
    "other_stores": {
      "count": 41,
      "units": 1597
    },
    "in_transit": 285,
    "ecomm_reserve": 128,
    "ecomm_reserve_target": 200,
    "sold_out_days": {
      "STR-005": 3
    }
  }
}
```

### `NEAREST_SOURCE`

```json
{
  "STR-005": {
    "source": "STR-001",
    "miles": 174
  },
  "STR-006": {
    "source": "STR-001",
    "miles": 176
  }
}
```

### `TRANSFER_PHASES`

```json
[
  {
    "phase": "Phase 1: Emergency (Next 12 Hours)",
    "moves": [
      {
        "from": "STR-001",
        "to": "STR-005",
        "units": 40
      }
    ],
    "transport": "Overnight van",
    "cost": 340,
    "pickup": "6 PM tonight",
    "arrival": "Tomorrow 7 AM",
    "recovery": 6800,
    "window": "3-day window"
  },
  {
    "phase": "Phase 2: Strategic (24-48 Hours)",
    "moves": [
      {
        "from": "STR-002",
        "to": "STR-006",
        "units": 27
      },
      {
        "from": "STR-003",
        "to": "STR-006",
        "units": 27
      },
      {
        "from": "STR-004",
        "to": "STR-005",
        "units": 26
      }
    ],
    "transport": "Regular delivery truck",
    "cost": 180,
    "pickup": "Tomorrow morning route",
    "arrival": "Day after tomorrow",
    "recovery": 11600,
    "window": "week-long window"
  }
]
```

### `NETWORK_HEALTH`

```json
{
  "locations": 51,
  "stock_balance_score": 72,
  "days_of_supply": 43,
  "stockout_incidents_per_month": 147,
  "overstock_by_category": {
    "Outerwear": 920000,
    "Apparel": 740000,
    "Electronics": 610000,
    "Footwear": 330000,
    "Accessories": 200000
  },
  "slow_movers": [
    {
      "sku": "SKU-1006",
      "weeks_of_supply": 19,
      "note": "summer item carried into winter"
    },
    {
      "sku": "SKU-1008",
      "weeks_of_supply": 17,
      "note": "seasonal demand down 40% since September"
    },
    {
      "sku": "SKU-1003",
      "weeks_of_supply": 14,
      "note": "base tee overbought for fall"
    }
  ],
  "seasonal_pattern": "Outerwear demand runs 2.1x the annual average from November to January; summer accessories run 0.4x."
}
```

### `IMBALANCES`

```json
[
  {
    "sku": "SKU-1001",
    "route": "Spokane -> Seattle",
    "units": 95,
    "routes": 2,
    "recovery": 11400,
    "transport": 460
  },
  {
    "sku": "SKU-1002",
    "route": "Seattle -> Portland",
    "units": 120,
    "routes": 2,
    "recovery": 14600,
    "transport": 520
  },
  {
    "sku": "SKU-1003",
    "route": "Portland -> Tacoma",
    "units": 140,
    "routes": 2,
    "recovery": 6300,
    "transport": 380
  },
  {
    "sku": "SKU-1004",
    "route": "Seattle -> Eugene",
    "units": 60,
    "routes": 2,
    "recovery": 13900,
    "transport": 410
  },
  {
    "sku": "SKU-1005",
    "route": "Bellevue -> Portland",
    "units": 55,
    "routes": 2,
    "recovery": 12500,
    "transport": 400
  },
  {
    "sku": "SKU-1006",
    "route": "Salem -> Seattle",
    "units": 90,
    "routes": 2,
    "recovery": 4100,
    "transport": 330
  },
  {
    "sku": "SKU-1007",
    "route": "Seattle -> Spokane",
    "units": 65,
    "routes": 2,
    "recovery": 10600,
    "transport": 450
  },
  {
    "sku": "SKU-1008",
    "route": "Portland -> Boise",
    "units": 55,
    "routes": 1,
    "recovery": 10800,
    "transport": 450
  }
]
```

### `AUTOMATION_OPTIONS`

```json
[
  {
    "priority": 1,
    "name": "RFID Tracking",
    "investment": 85000,
    "annual_benefit": 127000,
    "benefit_type": "Labor Savings",
    "benefit_label": "Annual labor savings",
    "highlights": [
      "Real-time location accuracy: 87% today, 99.8% with RFID",
      "Picking speed: +34%"
    ]
  },
  {
    "priority": 2,
    "name": "Auto-Replenishment",
    "investment": 45000,
    "annual_benefit": 142000,
    "benefit_type": "Stockout Reduction",
    "benefit_label": "Annual savings",
    "highlights": [
      "Eliminate manual reorder points",
      "Stockouts: -62%"
    ]
  },
  {
    "priority": 3,
    "name": "Predictive Allocation",
    "investment": 32000,
    "annual_benefit": 71000,
    "benefit_type": "Revenue Protection",
    "benefit_label": "Revenue protection",
    "highlights": [
      "AI-driven transfers (prevent imbalances)"
    ]
  }
]
```

### `INVENTORY_ACCURACY`

```json
{
  "current_pct": 87,
  "target_pct": 99.8
}
```
## Record-use boundary

Never reserve, promise, transfer, replenish, allocate, sell, or purchase stock. Every quantity is a synthetic snapshot requiring system-of-record verification and authorized approval.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
