# Store Associate Copilot — Complete Synthetic Records

> **SYNTHETIC, READ-ONLY PILOT DATA.** Every identifier, name, date, status,
> quantity, amount, preference, interaction, order, cart, case, campaign, and
> metric below is fictional. It is reference evidence, not a live-system value
> or authorization to take action.

## Authoritative provenance

- Deterministic source: `agents/@aibast-agents-library/retail_cpg_stacks/store_associate_copilot_stack/store_associate_copilot_agent.py`
- Locked case contract: `tests/demo_cases/store-associate-copilot.json`
- Captured evidence: `solutions/store-associate-copilot/evals/transcripts.json`
- The JSON blocks below are exact literals copied from the deterministic source.
- Preserve identifiers, spelling, capitalization, dates, statuses, and numeric values.
- If production data differs, stop and verify in the authorized system of record.

## Locked-case source selections

| Case | Persona | Operation | Exact arguments |
|---|---|---|---|
| `SA-01` | Store Associate | `product_lookup` | `{"sku_id":"SKU-1005"}` |
| `SA-02` | Store Associate | `customer_assist` | `{"scenario":"complaint_handling"}` |
| `SA-03` | Floor Specialist | `task_checklist` | `{"shift":"opening"}` |
| `SA-04` | Sales Manager | `performance_dashboard` | `{}` |

## Complete deterministic record sets

### `PRODUCT_CATALOG`

```json
{
  "SKU-1001": {
    "name": "Classic Denim Jacket",
    "category": "Apparel",
    "brand": "Heritage Line",
    "retail_price": 89.99,
    "sizes": [
      "XS",
      "S",
      "M",
      "L",
      "XL",
      "XXL"
    ],
    "colors": [
      "Indigo Wash",
      "Light Blue",
      "Black"
    ],
    "materials": "100% cotton denim, brass buttons",
    "care": "Machine wash cold, tumble dry low",
    "location_aisle": "A3",
    "location_shelf": "Top rack",
    "on_hand": 74,
    "upc": "0-12345-67890-1",
    "features": [
      "Adjustable waist tabs",
      "Two chest pockets",
      "Vintage fade finish"
    ]
  },
  "SKU-1002": {
    "name": "Wireless Earbuds Pro",
    "category": "Electronics",
    "brand": "SoundWave",
    "retail_price": 59.99,
    "sizes": [
      "One Size"
    ],
    "colors": [
      "Matte Black",
      "Pearl White",
      "Navy"
    ],
    "materials": "ABS plastic, silicone ear tips",
    "care": "Wipe with dry cloth. Do not submerge.",
    "location_aisle": "E1",
    "location_shelf": "Locked case",
    "on_hand": 132,
    "upc": "0-12345-67890-2",
    "features": [
      "Active noise cancellation",
      "8-hour battery",
      "IPX4 water resistant",
      "Bluetooth 5.3"
    ]
  },
  "SKU-1003": {
    "name": "Organic Cotton T-Shirt",
    "category": "Apparel",
    "brand": "EcoBasics",
    "retail_price": 29.99,
    "sizes": [
      "XS",
      "S",
      "M",
      "L",
      "XL"
    ],
    "colors": [
      "White",
      "Heather Grey",
      "Black",
      "Sage Green",
      "Dusty Rose"
    ],
    "materials": "100% GOTS-certified organic cotton",
    "care": "Machine wash cold with like colors",
    "location_aisle": "A1",
    "location_shelf": "Mid rack",
    "on_hand": 210,
    "upc": "0-12345-67890-3",
    "features": [
      "Pre-shrunk",
      "Tagless comfort label",
      "Reinforced shoulder seams"
    ]
  },
  "SKU-1004": {
    "name": "Smart Fitness Tracker",
    "category": "Electronics",
    "brand": "FitPulse",
    "retail_price": 129.99,
    "sizes": [
      "S/M Band",
      "L/XL Band"
    ],
    "colors": [
      "Midnight Black",
      "Arctic White",
      "Forest Green"
    ],
    "materials": "Aluminum case, fluoroelastomer band",
    "care": "Rinse with fresh water after swimming",
    "location_aisle": "E2",
    "location_shelf": "Display stand",
    "on_hand": 45,
    "upc": "0-12345-67890-4",
    "features": [
      "Heart rate monitor",
      "GPS tracking",
      "Sleep analysis",
      "7-day battery",
      "5ATM water resistant"
    ]
  },
  "SKU-1005": {
    "name": "Premium Running Shoes",
    "category": "Footwear",
    "brand": "StrideMax",
    "retail_price": 149.99,
    "sizes": [
      "7",
      "7.5",
      "8",
      "8.5",
      "9",
      "9.5",
      "10",
      "10.5",
      "11",
      "12",
      "13"
    ],
    "colors": [
      "Cloud White/Grey",
      "Black/Volt",
      "Navy/Orange"
    ],
    "materials": "Engineered mesh upper, EVA foam midsole, rubber outsole",
    "care": "Spot clean with damp cloth. Air dry only.",
    "location_aisle": "F1",
    "location_shelf": "Wall display",
    "on_hand": 38,
    "upc": "0-12345-67890-5",
    "features": [
      "Responsive cushioning",
      "Breathable knit upper",
      "Reflective accents",
      "Carbon fiber plate"
    ]
  },
  "SKU-1006": {
    "name": "Stainless Water Bottle",
    "category": "Accessories",
    "brand": "HydroKeep",
    "retail_price": 24.99,
    "sizes": [
      "20oz",
      "32oz"
    ],
    "colors": [
      "Brushed Steel",
      "Matte Black",
      "Ocean Blue",
      "Coral"
    ],
    "materials": "18/8 stainless steel, BPA-free lid",
    "care": "Hand wash recommended. Dishwasher safe (top rack).",
    "location_aisle": "C2",
    "location_shelf": "End cap",
    "on_hand": 195,
    "upc": "0-12345-67890-6",
    "features": [
      "Double-wall vacuum insulation",
      "24h cold / 12h hot",
      "Leak-proof lid",
      "Wide mouth"
    ]
  },
  "SKU-1007": {
    "name": "Leather Crossbody Bag",
    "category": "Accessories",
    "brand": "UrbanCraft",
    "retail_price": 79.99,
    "sizes": [
      "One Size"
    ],
    "colors": [
      "Cognac",
      "Black",
      "Olive"
    ],
    "materials": "Full-grain leather, brass hardware",
    "care": "Condition with leather balm quarterly",
    "location_aisle": "B2",
    "location_shelf": "Display hooks",
    "on_hand": 61,
    "upc": "0-12345-67890-7",
    "features": [
      "Adjustable strap",
      "RFID-blocking pocket",
      "Three compartments",
      "YKK zippers"
    ]
  },
  "SKU-1008": {
    "name": "UV Protection Sunglasses",
    "category": "Accessories",
    "brand": "ClearView",
    "retail_price": 44.99,
    "sizes": [
      "Standard",
      "Wide"
    ],
    "colors": [
      "Tortoise",
      "Matte Black",
      "Crystal Clear"
    ],
    "materials": "Acetate frame, polarized CR-39 lenses",
    "care": "Clean with included microfiber cloth. Store in case.",
    "location_aisle": "B1",
    "location_shelf": "Rotating display",
    "on_hand": 88,
    "upc": "0-12345-67890-8",
    "features": [
      "100% UV400 protection",
      "Polarized lenses",
      "Spring hinges",
      "Scratch-resistant coating"
    ]
  },
  "SKU-1009": {
    "name": "Performance Yoga Mat",
    "category": "Fitness",
    "brand": "ZenGrip",
    "retail_price": 54.99,
    "sizes": [
      "68x24 in",
      "72x26 in"
    ],
    "colors": [
      "Midnight Purple",
      "Sage",
      "Charcoal"
    ],
    "materials": "Natural rubber base, polyurethane top layer",
    "care": "Wipe with damp cloth after use. Air dry flat.",
    "location_aisle": "F2",
    "location_shelf": "Standing rack",
    "on_hand": 42,
    "upc": "0-12345-67890-9",
    "features": [
      "Non-slip grip",
      "6mm thickness",
      "Alignment lines",
      "Carrying strap included"
    ]
  },
  "SKU-1010": {
    "name": "Aromatherapy Candle Set",
    "category": "Home",
    "brand": "Luminary",
    "retail_price": 34.99,
    "sizes": [
      "3-pack (4oz each)"
    ],
    "colors": [
      "Lavender/Eucalyptus/Vanilla"
    ],
    "materials": "Soy wax, cotton wicks, essential oils",
    "care": "Trim wick to 1/4 inch before lighting. Burn max 4 hours.",
    "location_aisle": "D1",
    "location_shelf": "Feature table",
    "on_hand": 67,
    "upc": "0-12345-67891-0",
    "features": [
      "Clean-burning soy wax",
      "40-hour burn time per candle",
      "Reusable glass jars",
      "No synthetic fragrances"
    ]
  }
}
```

### `CUSTOMER_INTERACTION_SCRIPTS`

```json
{
  "greeting": {
    "scenario": "Customer enters the store",
    "script": "Draft: Welcome the shopper and ask what category they would like help finding.",
    "follow_up": "If they mention a product category, guide them to the correct aisle.",
    "tips": [
      "Make eye contact",
      "Smile genuinely",
      "Keep a comfortable distance"
    ]
  },
  "upsell": {
    "scenario": "Customer is ready to purchase a single item",
    "script": "Draft: If useful, mention one relevant complementary item without pressure.",
    "follow_up": "If interested, walk them to the complementary item. If not, respect their decision.",
    "tips": [
      "Suggest only relevant items",
      "Limit to one upsell attempt",
      "Focus on value not price"
    ]
  },
  "complaint_handling": {
    "scenario": "Customer has a complaint or issue",
    "script": "Draft: Acknowledge the concern, restate it, and explain that an authorized associate will review options.",
    "follow_up": "Listen fully, repeat back the issue, offer a concrete solution within your authority.",
    "tips": [
      "Never argue",
      "Acknowledge their frustration",
      "Offer alternatives if first solution is declined"
    ]
  },
  "size_help": {
    "scenario": "Customer needs sizing assistance",
    "script": "Draft: Ask which size the shopper would like checked; do not infer body characteristics.",
    "follow_up": "Check fitting room availability. Bring two sizes if customer is between sizes.",
    "tips": [
      "Be sensitive about sizing",
      "Suggest trying multiple sizes",
      "Check stock for requested size first"
    ]
  },
  "return_at_counter": {
    "scenario": "Customer wants to make a return at the register",
    "script": "Draft: Ask whether proof of purchase is available and explain that return eligibility requires authorized review.",
    "follow_up": "Verify return eligibility per policy. Process efficiently and offer exchange if applicable.",
    "tips": [
      "Stay positive and empathetic",
      "Explain policy clearly",
      "Thank them regardless of outcome"
    ]
  }
}
```

### `DAILY_TASK_LIST`

```json
{
  "opening": [
    {
      "task": "Unlock entrance doors and disable alarm",
      "priority": "critical",
      "est_minutes": 2
    },
    {
      "task": "Power on POS terminals and verify connectivity",
      "priority": "critical",
      "est_minutes": 5
    },
    {
      "task": "Walk floor to check overnight display condition",
      "priority": "high",
      "est_minutes": 10
    },
    {
      "task": "Restock fitting rooms with hangers",
      "priority": "medium",
      "est_minutes": 5
    },
    {
      "task": "Review daily promotions and update signage",
      "priority": "high",
      "est_minutes": 15
    },
    {
      "task": "Check inventory alerts and pull items for floor replenishment",
      "priority": "high",
      "est_minutes": 20
    }
  ],
  "midday": [
    {
      "task": "Restock high-traffic areas and end caps",
      "priority": "high",
      "est_minutes": 20
    },
    {
      "task": "Process online pickup orders (BOPIS)",
      "priority": "critical",
      "est_minutes": 15
    },
    {
      "task": "Clean fitting rooms and return abandoned items",
      "priority": "medium",
      "est_minutes": 10
    },
    {
      "task": "Rotate break schedule for floor coverage",
      "priority": "high",
      "est_minutes": 5
    },
    {
      "task": "Check and respond to customer service queue",
      "priority": "high",
      "est_minutes": 10
    }
  ],
  "closing": [
    {
      "task": "Process remaining BOPIS orders for next-day pickup",
      "priority": "critical",
      "est_minutes": 15
    },
    {
      "task": "Reconcile POS drawers and prepare deposit",
      "priority": "critical",
      "est_minutes": 20
    },
    {
      "task": "Tidy all displays and return misplaced merchandise",
      "priority": "high",
      "est_minutes": 25
    },
    {
      "task": "Vacuum high-traffic aisles",
      "priority": "medium",
      "est_minutes": 15
    },
    {
      "task": "Set alarm and lock all entrances",
      "priority": "critical",
      "est_minutes": 3
    }
  ]
}
```

### `ASSOCIATE_PERFORMANCE`

```json
{
  "ASC-101": {
    "name": "Opening Senior Associate Cohort",
    "role": "Senior Associate",
    "shift": "opening",
    "units_sold_today": 23,
    "revenue_today": 1847.5,
    "transactions_today": 14,
    "avg_basket": 131.96,
    "upsell_rate": 0.35,
    "csat_score": 4.8,
    "tasks_completed": 11,
    "tasks_total": 12,
    "hours_this_week": 32.5
  },
  "ASC-102": {
    "name": "Midday Associate Cohort",
    "role": "Associate",
    "shift": "midday",
    "units_sold_today": 17,
    "revenue_today": 1295.8,
    "transactions_today": 11,
    "avg_basket": 117.8,
    "upsell_rate": 0.22,
    "csat_score": 4.5,
    "tasks_completed": 8,
    "tasks_total": 10,
    "hours_this_week": 28.0
  },
  "ASC-103": {
    "name": "Closing Associate Cohort",
    "role": "Associate",
    "shift": "closing",
    "units_sold_today": 12,
    "revenue_today": 985.4,
    "transactions_today": 9,
    "avg_basket": 109.49,
    "upsell_rate": 0.18,
    "csat_score": 4.3,
    "tasks_completed": 7,
    "tasks_total": 9,
    "hours_this_week": 24.0
  },
  "ASC-104": {
    "name": "Opening Lead Associate Cohort",
    "role": "Lead Associate",
    "shift": "opening",
    "units_sold_today": 29,
    "revenue_today": 2410.3,
    "transactions_today": 18,
    "avg_basket": 133.91,
    "upsell_rate": 0.4,
    "csat_score": 4.9,
    "tasks_completed": 12,
    "tasks_total": 12,
    "hours_this_week": 36.0
  }
}
```

### `COMPLEMENTARY_PRODUCTS`

```json
{
  "SKU-1001": [
    "SKU-1003",
    "SKU-1008"
  ],
  "SKU-1002": [
    "SKU-1004",
    "SKU-1006"
  ],
  "SKU-1003": [
    "SKU-1001",
    "SKU-1008"
  ],
  "SKU-1004": [
    "SKU-1005",
    "SKU-1009"
  ],
  "SKU-1005": [
    "SKU-1006",
    "SKU-1009"
  ],
  "SKU-1006": [
    "SKU-1009",
    "SKU-1005"
  ],
  "SKU-1007": [
    "SKU-1008",
    "SKU-1001"
  ],
  "SKU-1008": [
    "SKU-1007",
    "SKU-1001"
  ],
  "SKU-1009": [
    "SKU-1006",
    "SKU-1004"
  ],
  "SKU-1010": [
    "SKU-1009",
    "SKU-1006"
  ]
}
```

## Record-use boundary

Never promise or reserve inventory; apply a promotion or loyalty benefit; send a message; make an employment decision; process a return or refund; prepare a transaction; or complete a purchase.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
