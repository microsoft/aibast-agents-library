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
| `SA-05` | Store Associate | `accessory_recommendations` | `{"sku_id":"SKU-1005"}` |
| `SA-06` | Store Associate | `product_compare` | `{"compare_with":"SoundMax Pro","sku_id":"SKU-1005"}` |
| `SA-07` | Store Associate | `prepare_transaction` | `{"addons":"warranty and cleaning kit","loyalty_tier":"Gold"}` |

## Complete deterministic record sets

### `PRODUCT_CATALOG`

```json
{
  "SKU-1005": {
    "key": "techpro",
    "name": "TechPro X-Series Wireless Headphones",
    "short_name": "TechPro X-Series",
    "category": "Headphones",
    "type": "product",
    "brand": "TechPro",
    "retail_price": 199.99,
    "regular_price": 249.99,
    "promotion": "Save $50 (regular $249.99), ends Sunday",
    "store": "Bellevue",
    "on_hand": 14,
    "battery_hours": 38,
    "battery_detail": "38 hours continuous",
    "anc_db": 42,
    "noise_cancellation": "Active ANC, -42dB",
    "sound_quality": "Premium",
    "warranty": "2 years standard",
    "colors": [
      "Matte Black",
      "Silver"
    ],
    "location_aisle": "E1",
    "location_shelf": "Headphone wall",
    "upc": "0-12345-67890-5",
    "selling_points": [
      "Industry-leading 38hr battery (vs competitors 24-30hr)",
      "Multi-device pairing (3 devices simultaneously)",
      "Foldable design with premium case included"
    ],
    "rating": 4.7,
    "review_count": 847,
    "review_summary": "Praised for comfort and battery life",
    "review_quote": "Amazing battery",
    "best_for": [
      "Long flights",
      "all-day use",
      "budget-conscious"
    ]
  },
  "SKU-1006": {
    "key": "soundmax",
    "name": "SoundMax Pro Wireless Headphones",
    "short_name": "SoundMax Pro",
    "category": "Headphones",
    "type": "product",
    "brand": "SoundMax",
    "retail_price": 229.99,
    "regular_price": 229.99,
    "promotion": "",
    "store": "Bellevue",
    "on_hand": 3,
    "battery_hours": 30,
    "battery_detail": "30 hours continuous",
    "anc_db": 48,
    "noise_cancellation": "Active ANC, -48dB",
    "sound_quality": "Audiophile",
    "warranty": "1 year standard",
    "colors": [
      "Graphite"
    ],
    "location_aisle": "E1",
    "location_shelf": "Headphone wall",
    "upc": "0-12345-67890-6",
    "selling_points": [
      "Audiophile-grade drivers",
      "Strongest noise cancellation in the store (-48dB)"
    ],
    "rating": 4.8,
    "review_count": 623,
    "review_summary": "Praised for sound quality",
    "review_quote": "Best sound ever",
    "best_for": [
      "Music enthusiasts",
      "home listening",
      "best audio"
    ]
  },
  "SKU-1002": {
    "key": "earbuds",
    "name": "SoundWave Wireless Earbuds Pro",
    "short_name": "Wireless Earbuds Pro",
    "category": "Earbuds",
    "type": "product",
    "brand": "SoundWave",
    "retail_price": 59.99,
    "regular_price": 59.99,
    "promotion": "",
    "store": "Bellevue",
    "on_hand": 132,
    "battery_hours": 8,
    "battery_detail": "8 hours (32 with case)",
    "anc_db": 30,
    "noise_cancellation": "Active ANC, -30dB",
    "sound_quality": "Standard",
    "warranty": "1 year standard",
    "colors": [
      "Matte Black",
      "Pearl White",
      "Navy"
    ],
    "location_aisle": "E1",
    "location_shelf": "Locked case",
    "upc": "0-12345-67890-2",
    "selling_points": [
      "IPX4 water resistant",
      "Bluetooth 5.3"
    ],
    "rating": 4.4,
    "review_count": 1210,
    "review_summary": "Praised for fit and value",
    "review_quote": "Great value",
    "best_for": [
      "Workouts",
      "commuting",
      "pocket size"
    ]
  },
  "SKU-1011": {
    "key": "warranty",
    "name": "Extended Warranty (3-year)",
    "short_name": "Extended Warranty",
    "category": "Protection Plan",
    "type": "warranty",
    "brand": "TechPro",
    "retail_price": 39.99,
    "regular_price": 39.99,
    "note": "3-year coverage, 87% attach rate",
    "on_hand": 999,
    "location_aisle": "Register",
    "location_shelf": "Added at checkout",
    "upc": "0-12345-67891-1"
  },
  "SKU-1012": {
    "key": "cleaning",
    "name": "Premium Cleaning Kit",
    "short_name": "Premium Cleaning Kit",
    "category": "Accessories",
    "type": "accessory",
    "brand": "TechPro",
    "retail_price": 24.99,
    "regular_price": 24.99,
    "note": "Branded TechPro, high margin",
    "on_hand": 40,
    "location_aisle": "E2",
    "location_shelf": "Accessory pegs",
    "upc": "0-12345-67891-2"
  },
  "SKU-1013": {
    "key": "adapter",
    "name": "Travel Adapter",
    "short_name": "Travel Adapter",
    "category": "Accessories",
    "type": "accessory",
    "brand": "TechPro",
    "retail_price": 19.99,
    "regular_price": 19.99,
    "note": "USB-C fast charging",
    "on_hand": 55,
    "location_aisle": "E2",
    "location_shelf": "Accessory pegs",
    "upc": "0-12345-67891-3"
  },
  "SKU-1014": {
    "key": "cushion",
    "name": "Replacement Cushions",
    "short_name": "Replacement Cushions",
    "category": "Accessories",
    "type": "accessory",
    "brand": "TechPro",
    "retail_price": 34.99,
    "regular_price": 34.99,
    "note": "Memory foam upgrade",
    "on_hand": 22,
    "location_aisle": "E2",
    "location_shelf": "Accessory pegs",
    "upc": "0-12345-67891-4"
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
  "SKU-1005": [
    "SKU-1011",
    "SKU-1012",
    "SKU-1013",
    "SKU-1014"
  ],
  "SKU-1006": [
    "SKU-1011",
    "SKU-1013"
  ],
  "SKU-1002": [
    "SKU-1011"
  ]
}
```

### `COMMISSION_RATES_BP`

```json
{
  "product": 800,
  "warranty": 1800,
  "accessory": 1200
}
```

### `CHECKOUT_TERMS`

```json
{
  "loyalty_discount_bp": {
    "Gold": 500,
    "Silver": 300,
    "Bronze": 0
  },
  "sales_tax_bp": 850,
  "financing_months": 6,
  "financing_apr": "0% APR",
  "store_card_bonus_points": 500,
  "default_loyalty_tier": "Gold",
  "conversion_tip": "Mention the cleaning kit extends cushion life - drives 65% conversion"
}
```

### `ADDON_BUNDLES`

```json
{
  "warranty and cleaning kit": [
    "SKU-1011",
    "SKU-1012"
  ],
  "warranty": [
    "SKU-1011"
  ],
  "cleaning kit": [
    "SKU-1012"
  ],
  "all add-ons": [
    "SKU-1011",
    "SKU-1012",
    "SKU-1013",
    "SKU-1014"
  ],
  "none": []
}
```

## Record-use boundary

Never promise or reserve inventory; apply a promotion or loyalty benefit; send a message; make an employment decision; process a return or refund; ring up a transaction (a prepared cart is a draft the associate rings up at the register); or complete a purchase.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
