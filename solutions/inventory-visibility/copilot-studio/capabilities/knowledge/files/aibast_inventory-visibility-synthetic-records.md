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

## Complete deterministic record sets

### `STORES`

```json
{
  "STR-001": {
    "name": "Downtown Flagship",
    "city": "Chicago",
    "state": "IL",
    "type": "flagship",
    "capacity_sqft": 42000
  },
  "STR-002": {
    "name": "Northshore Mall",
    "city": "Evanston",
    "state": "IL",
    "type": "mall",
    "capacity_sqft": 18500
  },
  "STR-003": {
    "name": "Oakbrook Center",
    "city": "Oak Brook",
    "state": "IL",
    "type": "outlet",
    "capacity_sqft": 12000
  },
  "STR-004": {
    "name": "Michigan Ave Express",
    "city": "Chicago",
    "state": "IL",
    "type": "express",
    "capacity_sqft": 6500
  }
}
```

### `WAREHOUSES`

```json
{
  "WH-CENTRAL": {
    "name": "Central Distribution Center",
    "city": "Romeoville",
    "state": "IL",
    "capacity_pallets": 22000
  },
  "WH-EAST": {
    "name": "East Regional Warehouse",
    "city": "Indianapolis",
    "state": "IN",
    "capacity_pallets": 14000
  }
}
```

### `SKUS`

```json
{
  "SKU-1001": {
    "name": "Classic Denim Jacket",
    "category": "Apparel",
    "unit_cost": 34.5,
    "retail_price": 89.99
  },
  "SKU-1002": {
    "name": "Wireless Earbuds Pro",
    "category": "Electronics",
    "unit_cost": 18.75,
    "retail_price": 59.99
  },
  "SKU-1003": {
    "name": "Organic Cotton T-Shirt",
    "category": "Apparel",
    "unit_cost": 8.2,
    "retail_price": 29.99
  },
  "SKU-1004": {
    "name": "Smart Fitness Tracker",
    "category": "Electronics",
    "unit_cost": 42.0,
    "retail_price": 129.99
  },
  "SKU-1005": {
    "name": "Premium Running Shoes",
    "category": "Footwear",
    "unit_cost": 55.0,
    "retail_price": 149.99
  },
  "SKU-1006": {
    "name": "Stainless Water Bottle",
    "category": "Accessories",
    "unit_cost": 6.8,
    "retail_price": 24.99
  },
  "SKU-1007": {
    "name": "Leather Crossbody Bag",
    "category": "Accessories",
    "unit_cost": 27.5,
    "retail_price": 79.99
  },
  "SKU-1008": {
    "name": "UV Protection Sunglasses",
    "category": "Accessories",
    "unit_cost": 12.3,
    "retail_price": 44.99
  }
}
```

### `INVENTORY`

```json
{
  "STR-001": {
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
    "SKU-1001": 12,
    "SKU-1002": 28,
    "SKU-1003": 44,
    "SKU-1004": 6,
    "SKU-1005": 5,
    "SKU-1006": 55,
    "SKU-1007": 8,
    "SKU-1008": 19
  },
  "WH-CENTRAL": {
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
    "SKU-1001": 820,
    "SKU-1002": 1100,
    "SKU-1003": 2200,
    "SKU-1004": 410,
    "SKU-1005": 350,
    "SKU-1006": 2600,
    "SKU-1007": 530,
    "SKU-1008": 900
  }
}
```

### `SAFETY_STOCK`

```json
{
  "STR-001": {
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
    "SKU-1001": 8,
    "SKU-1002": 15,
    "SKU-1003": 20,
    "SKU-1004": 4,
    "SKU-1005": 3,
    "SKU-1006": 20,
    "SKU-1007": 5,
    "SKU-1008": 10
  }
}
```

### `LEAD_TIMES_DAYS`

```json
{
  "WH-CENTRAL": {
    "STR-001": 1,
    "STR-002": 1,
    "STR-003": 2,
    "STR-004": 1
  },
  "WH-EAST": {
    "STR-001": 2,
    "STR-002": 2,
    "STR-003": 3,
    "STR-004": 2
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
  "SKU-1001": 6.2,
  "SKU-1002": 9.8,
  "SKU-1003": 14.5,
  "SKU-1004": 3.1,
  "SKU-1005": 2.7,
  "SKU-1006": 12.0,
  "SKU-1007": 4.4,
  "SKU-1008": 7.3
}
```

## Record-use boundary

Never reserve, promise, transfer, replenish, allocate, sell, or purchase stock. Every quantity is a synthetic snapshot requiring system-of-record verification and authorized approval.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
