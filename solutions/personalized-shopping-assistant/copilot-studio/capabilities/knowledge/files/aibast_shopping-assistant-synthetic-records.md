# Personalized Shopping Assistant — Complete Synthetic Records

> **SYNTHETIC, READ-ONLY PILOT DATA.** Every identifier, name, date, status,
> quantity, amount, preference, interaction, order, cart, case, campaign, and
> metric below is fictional. It is reference evidence, not a live-system value
> or authorization to take action.

## Authoritative provenance

- Deterministic source: `agents/@aibast-agents-library/b2c_sales_stacks/personalized_shopping_assistant_stack/personalized_shopping_assistant_agent.py`
- Locked case contract: `tests/demo_cases/personalized-shopping-assistant.json`
- Captured evidence: `solutions/personalized-shopping-assistant/evals/transcripts.json`
- The JSON blocks below are exact literals copied from the deterministic source.
- Preserve identifiers, spelling, capitalization, dates, statuses, and numeric values.
- If production data differs, stop and verify in the authorized system of record.

## Locked-case source selections

| Case | Persona | Operation | Exact arguments |
|---|---|---|---|
| `PSA-01` | Personal Shopper | `product_recommendations` | `{"customer_id":"SHOP-001"}` |
| `PSA-02` | Clienteling Specialist | `style_profile` | `{"customer_id":"SHOP-002"}` |
| `PSA-03` | Retail Manager | `inventory_check` | `{"sku":"SKU-1003"}` |
| `PSA-04` | Personal Shopper | `outfit_builder` | `{"customer_id":"SHOP-001"}` |

## Complete deterministic record sets

### `PRODUCT_CATALOG`

```json
{
  "SKU-1001": {
    "name": "Classic Oxford Shirt \u2014 White",
    "category": "tops",
    "subcategory": "shirts",
    "price": 68.0,
    "brand": "Heritage Co.",
    "sizes": [
      "S",
      "M",
      "L",
      "XL"
    ],
    "colors": [
      "white",
      "blue",
      "pink"
    ],
    "style_tags": [
      "classic",
      "business",
      "smart_casual"
    ],
    "rating": 4.7,
    "stock": {
      "S": 12,
      "M": 25,
      "L": 18,
      "XL": 8
    }
  },
  "SKU-1002": {
    "name": "Slim Fit Chinos \u2014 Navy",
    "category": "bottoms",
    "subcategory": "pants",
    "price": 79.0,
    "brand": "Heritage Co.",
    "sizes": [
      "30",
      "32",
      "34",
      "36"
    ],
    "colors": [
      "navy",
      "khaki",
      "olive"
    ],
    "style_tags": [
      "classic",
      "smart_casual",
      "weekend"
    ],
    "rating": 4.5,
    "stock": {
      "30": 6,
      "32": 15,
      "34": 20,
      "36": 10
    }
  },
  "SKU-1003": {
    "name": "Merino Wool Crew Sweater",
    "category": "tops",
    "subcategory": "sweaters",
    "price": 125.0,
    "brand": "Alpine Knits",
    "sizes": [
      "S",
      "M",
      "L",
      "XL"
    ],
    "colors": [
      "charcoal",
      "burgundy",
      "forest"
    ],
    "style_tags": [
      "classic",
      "smart_casual",
      "layering"
    ],
    "rating": 4.8,
    "stock": {
      "S": 4,
      "M": 10,
      "L": 8,
      "XL": 3
    }
  },
  "SKU-1004": {
    "name": "Leather Chelsea Boots",
    "category": "footwear",
    "subcategory": "boots",
    "price": 195.0,
    "brand": "Cobblestone",
    "sizes": [
      "8",
      "9",
      "10",
      "11",
      "12"
    ],
    "colors": [
      "brown",
      "black"
    ],
    "style_tags": [
      "classic",
      "smart_casual",
      "evening"
    ],
    "rating": 4.6,
    "stock": {
      "8": 5,
      "9": 8,
      "10": 12,
      "11": 7,
      "12": 3
    }
  },
  "SKU-1005": {
    "name": "Quilted Vest",
    "category": "outerwear",
    "subcategory": "vests",
    "price": 110.0,
    "brand": "Northfield",
    "sizes": [
      "S",
      "M",
      "L",
      "XL"
    ],
    "colors": [
      "navy",
      "olive",
      "black"
    ],
    "style_tags": [
      "casual",
      "outdoor",
      "layering"
    ],
    "rating": 4.4,
    "stock": {
      "S": 2,
      "M": 7,
      "L": 5,
      "XL": 9
    }
  },
  "SKU-1006": {
    "name": "Silk Pocket Square",
    "category": "accessories",
    "subcategory": "pocket_squares",
    "price": 35.0,
    "brand": "Heritage Co.",
    "sizes": [
      "OS"
    ],
    "colors": [
      "navy_paisley",
      "burgundy_dot",
      "green_stripe"
    ],
    "style_tags": [
      "classic",
      "business",
      "evening"
    ],
    "rating": 4.9,
    "stock": {
      "OS": 30
    }
  },
  "SKU-1007": {
    "name": "Performance Running Shoe",
    "category": "footwear",
    "subcategory": "athletic",
    "price": 145.0,
    "brand": "Stride Labs",
    "sizes": [
      "8",
      "9",
      "10",
      "11",
      "12"
    ],
    "colors": [
      "white_grey",
      "black_red"
    ],
    "style_tags": [
      "athletic",
      "casual",
      "performance"
    ],
    "rating": 4.7,
    "stock": {
      "8": 10,
      "9": 15,
      "10": 20,
      "11": 12,
      "12": 6
    }
  },
  "SKU-1008": {
    "name": "Linen Blazer \u2014 Unstructured",
    "category": "outerwear",
    "subcategory": "blazers",
    "price": 225.0,
    "brand": "Riviera Style",
    "sizes": [
      "S",
      "M",
      "L",
      "XL"
    ],
    "colors": [
      "tan",
      "light_blue"
    ],
    "style_tags": [
      "smart_casual",
      "evening",
      "summer"
    ],
    "rating": 4.3,
    "stock": {
      "S": 3,
      "M": 6,
      "L": 4,
      "XL": 2
    }
  }
}
```

### `CUSTOMER_PREFERENCES`

```json
{
  "SHOP-001": {
    "name": "Synthetic Shopper A",
    "size_top": "L",
    "size_bottom": "34",
    "size_shoe": "10",
    "style_preference": [
      "classic",
      "smart_casual"
    ],
    "brand_affinity": [
      "Heritage Co.",
      "Alpine Knits"
    ],
    "color_preference": [
      "navy",
      "charcoal",
      "white"
    ],
    "budget_range": {
      "min": 50,
      "max": 250
    },
    "purchase_history": [
      "SKU-1001",
      "SKU-1002",
      "SKU-1006"
    ]
  },
  "SHOP-002": {
    "name": "Synthetic Shopper B",
    "size_top": "S",
    "size_bottom": "30",
    "size_shoe": "8",
    "style_preference": [
      "casual",
      "outdoor",
      "athletic"
    ],
    "brand_affinity": [
      "Northfield",
      "Stride Labs"
    ],
    "color_preference": [
      "olive",
      "black",
      "white_grey"
    ],
    "budget_range": {
      "min": 30,
      "max": 175
    },
    "purchase_history": [
      "SKU-1005",
      "SKU-1007"
    ]
  }
}
```

### `OUTFIT_TEMPLATES`

```json
{
  "business_casual": {
    "name": "Business Casual",
    "pieces": [
      "tops:shirts",
      "bottoms:pants",
      "footwear:boots",
      "accessories:pocket_squares"
    ]
  },
  "weekend_smart": {
    "name": "Weekend Smart",
    "pieces": [
      "tops:sweaters",
      "bottoms:pants",
      "footwear:boots"
    ]
  },
  "active_weekend": {
    "name": "Active Weekend",
    "pieces": [
      "outerwear:vests",
      "footwear:athletic"
    ]
  },
  "evening_out": {
    "name": "Evening Out",
    "pieces": [
      "outerwear:blazers",
      "tops:shirts",
      "bottoms:pants",
      "footwear:boots"
    ]
  }
}
```

## Record-use boundary

Never infer body, health, identity, wealth, or another sensitive trait; reserve stock; apply a loyalty benefit or offer; process a return or refund; create an order; or complete a purchase.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
