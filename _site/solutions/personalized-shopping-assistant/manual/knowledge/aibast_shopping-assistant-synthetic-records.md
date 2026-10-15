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
| `PSA-01` | Personal Shopper | `product_recommendations` | `{"customer_id":"SHOP-001","occasion":"business dinner with clients"}` |
| `PSA-02` | Clienteling Specialist | `style_profile` | `{"customer_id":"SHOP-002"}` |
| `PSA-03` | Retail Manager | `inventory_check` | `{"sku":"SKU-2003"}` |
| `PSA-04` | Personal Shopper | `outfit_builder` | `{"customer_id":"SHOP-001"}` |
| `PSA-05` | Personal Shopper | `pricing_offer` | `{"customer_id":"SHOP-001"}` |
| `PSA-06` | Clienteling Specialist | `session_summary` | `{"customer_id":"SHOP-001"}` |

## Complete deterministic record sets

### `PRODUCT_CATALOG`

```json
{
  "SKU-2001": {
    "name": "Wool crepe blazer",
    "brand": "Theory",
    "piece": "Blazer",
    "price": 375,
    "size_type": "numeric",
    "color": "navy",
    "stock": {
      "store": {
        "4": 2,
        "6": 3,
        "8": 2
      },
      "warehouse": {
        "6": 5
      },
      "downtown": {
        "6": 1
      }
    }
  },
  "SKU-2002": {
    "name": "Silk shell top",
    "brand": "Vince",
    "piece": "Top",
    "price": 195,
    "size_type": "top",
    "color": "navy",
    "stock": {
      "store": {
        "XS": 1,
        "S": 4,
        "M": 3
      },
      "warehouse": {
        "S": 6
      },
      "downtown": {
        "S": 2
      }
    }
  },
  "SKU-2003": {
    "name": "Tailored ankle pant",
    "brand": "Equipment",
    "piece": "Pants",
    "price": 285,
    "size_type": "bottom",
    "color": "black",
    "stock": {
      "store": {
        "27": 2,
        "28": 1,
        "29": 2
      },
      "warehouse": {
        "28": 0
      },
      "downtown": {
        "28": 0
      }
    }
  },
  "SKU-2004": {
    "name": "Midi sheath dress",
    "brand": "Theory",
    "piece": "Dress",
    "price": 345,
    "size_type": "numeric",
    "color": "burgundy",
    "stock": {
      "store": {
        "4": 1,
        "6": 2,
        "8": 1
      },
      "warehouse": {
        "6": 3
      },
      "downtown": {
        "6": 1
      }
    }
  },
  "SKU-2005": {
    "name": "Classic leather pump",
    "brand": "Store label",
    "piece": "Shoes",
    "price": 295,
    "size_type": "shoe",
    "color": "black",
    "stock": {
      "store": {
        "7": 2,
        "8": 0,
        "9": 1
      },
      "warehouse": {
        "8": 0
      },
      "downtown": {
        "8": 0
      }
    },
    "alternative": "SKU-2006"
  },
  "SKU-2006": {
    "name": "Block heel",
    "brand": "Stuart Weitzman",
    "piece": "Shoes",
    "price": 315,
    "size_type": "shoe",
    "color": "black",
    "stock": {
      "store": {
        "8": 2
      },
      "warehouse": {
        "8": 4
      },
      "downtown": {
        "8": 1
      }
    },
    "note": "Same height, similar style"
  },
  "SKU-2007": {
    "name": "Leather tote",
    "brand": "Store label",
    "piece": "Bag",
    "price": 425,
    "size_type": "one_size",
    "color": "cognac",
    "stock": {
      "store": {
        "One size": 3
      },
      "warehouse": {
        "One size": 4
      },
      "downtown": {
        "One size": 1
      }
    }
  },
  "SKU-2008": {
    "name": "Pointed kitten heel",
    "brand": "Store label",
    "piece": "Shoes",
    "price": 265,
    "size_type": "shoe",
    "color": "nude",
    "stock": {
      "store": {
        "8": 3
      },
      "warehouse": {
        "8": 2
      },
      "downtown": {
        "8": 1
      }
    }
  },
  "SKU-2009": {
    "name": "Gold bar necklace",
    "brand": "Store label",
    "piece": "Jewelry",
    "price": 125,
    "size_type": "one_size",
    "color": "gold",
    "stock": {
      "store": {
        "One size": 5
      },
      "warehouse": {
        "One size": 6
      },
      "downtown": {
        "One size": 2
      }
    }
  },
  "SKU-2010": {
    "name": "Tailored jumpsuit",
    "brand": "Vince",
    "piece": "Jumpsuit",
    "price": 395,
    "size_type": "numeric",
    "color": "black",
    "stock": {
      "store": {
        "4": 1,
        "6": 0
      },
      "warehouse": {
        "6": 3
      },
      "downtown": {
        "6": 1
      }
    }
  },
  "SKU-2011": {
    "name": "Leather waist belt",
    "brand": "Store label",
    "piece": "Belt",
    "price": 145,
    "size_type": "one_size",
    "color": "black",
    "stock": {
      "store": {
        "One size": 4
      },
      "warehouse": {
        "One size": 3
      },
      "downtown": {
        "One size": 1
      }
    }
  },
  "SKU-2012": {
    "name": "Statement gold earrings",
    "brand": "Store label",
    "piece": "Earrings",
    "price": 85,
    "size_type": "one_size",
    "color": "gold",
    "stock": {
      "store": {
        "One size": 6
      },
      "warehouse": {
        "One size": 4
      },
      "downtown": {
        "One size": 2
      }
    }
  },
  "SKU-2013": {
    "name": "Evening leather clutch",
    "brand": "Store label",
    "piece": "Clutch",
    "price": 295,
    "size_type": "one_size",
    "color": "black",
    "stock": {
      "store": {
        "One size": 2
      },
      "warehouse": {
        "One size": 2
      },
      "downtown": {
        "One size": 1
      }
    }
  }
}
```

### `CUSTOMER_PREFERENCES`

```json
{
  "SHOP-001": {
    "name": "Jennifer Hayes",
    "alias": "jennifer",
    "profile": [
      [
        "Style archetype",
        "Modern Classic"
      ],
      [
        "Color palette",
        "Neutrals, navy, burgundy"
      ],
      [
        "Fit preference",
        "Tailored, not tight"
      ],
      [
        "Price range",
        "$150-400 per piece"
      ],
      [
        "Preferred brands",
        "Theory, Vince, Equipment"
      ]
    ],
    "sizes": {
      "top": "S",
      "numeric": "6",
      "bottom": "28",
      "shoe": "8"
    },
    "size_rows": [
      [
        "Tops",
        "6 / Small",
        "Prefers relaxed fit"
      ],
      [
        "Bottoms",
        "28/6",
        "High-rise preferred"
      ],
      [
        "Dresses",
        "6",
        "Midi length"
      ],
      [
        "Shoes",
        "8",
        "Comfortable heels only"
      ]
    ],
    "purchase_patterns": [
      [
        "Last purchase",
        "3 weeks ago (silk blouse)"
      ],
      [
        "Avg items/visit",
        "2.4"
      ],
      [
        "Return rate",
        "8% (well below average)"
      ],
      [
        "Total spend (YTD)",
        "$4,200"
      ]
    ],
    "purchase_brands": [
      "Vince",
      "Theory",
      "Stuart Weitzman"
    ],
    "style_notes": "Loves structured pieces, avoids prints, prefers investment pieces over trends",
    "loyalty_tier": "Platinum",
    "points_balance_value": 42
  },
  "SHOP-002": {
    "name": "Synthetic Shopper B",
    "alias": "shopper b",
    "profile": [
      [
        "Style archetype",
        "Relaxed Minimal"
      ],
      [
        "Color palette",
        "Black, white, camel"
      ],
      [
        "Fit preference",
        "Easy, unstructured"
      ],
      [
        "Price range",
        "$80-250 per piece"
      ],
      [
        "Preferred brands",
        "Vince"
      ]
    ],
    "sizes": {
      "top": "M",
      "numeric": "8",
      "bottom": "29",
      "shoe": "9"
    },
    "size_rows": [
      [
        "Tops",
        "8 / Medium",
        "Prefers easy fit"
      ],
      [
        "Bottoms",
        "29/8",
        "Mid-rise preferred"
      ],
      [
        "Dresses",
        "8",
        "Knee length"
      ],
      [
        "Shoes",
        "9",
        "Flats preferred"
      ]
    ],
    "purchase_patterns": [
      [
        "Last purchase",
        "2 months ago (knit top)"
      ],
      [
        "Avg items/visit",
        "1.6"
      ],
      [
        "Return rate",
        "12%"
      ],
      [
        "Total spend (YTD)",
        "$1,150"
      ]
    ],
    "purchase_brands": [
      "Vince"
    ],
    "style_notes": "Prefers comfort and simple shapes",
    "loyalty_tier": "Gold",
    "points_balance_value": 15
  }
}
```

### `OCCASIONS`

```json
{
  "business_dinner": {
    "label": "Business dinner with clients",
    "requirements": [
      [
        "Dress code",
        "Business elegant"
      ],
      [
        "Impression",
        "Polished, confident"
      ],
      [
        "Comfort level",
        "Seated dining, standing cocktails"
      ],
      [
        "Her preference",
        "Structured, not stuffy"
      ]
    ],
    "picks": [
      [
        "SKU-2001",
        96,
        "Blazer: Her favorite Theory brand, structured silhouette she loves"
      ],
      [
        "SKU-2002",
        94,
        "Shell: Navy (her color), pairs with blazer"
      ],
      [
        "SKU-2003",
        92,
        "Pants: High-rise she prefers, versatile neutral"
      ],
      [
        "SKU-2004",
        91,
        "Dress option: One-piece alternative, midi length"
      ]
    ],
    "avoid": [
      "Prints (she avoids)",
      "Fitted dresses (prefers relaxed)",
      "Trendy pieces (wants investment value)"
    ]
  }
}
```

### `OUTFIT_TEMPLATES`

```json
{
  "business_dinner": [
    {
      "number": 1,
      "name": "Power Suiting",
      "pieces": [
        [
          "Blazer",
          "SKU-2001"
        ],
        [
          "Top",
          "SKU-2002"
        ],
        [
          "Pants",
          "SKU-2003"
        ],
        [
          "Shoes",
          "SKU-2005"
        ],
        [
          "Bag",
          "SKU-2007"
        ]
      ],
      "recommended": true
    },
    {
      "number": 2,
      "name": "Elegant Simplicity",
      "pieces": [
        [
          "Dress",
          "SKU-2004"
        ],
        [
          "Blazer",
          "SKU-2001"
        ],
        [
          "Shoes",
          "SKU-2008"
        ],
        [
          "Jewelry",
          "SKU-2009"
        ]
      ],
      "recommended": false
    },
    {
      "number": 3,
      "name": "Modern Edge",
      "pieces": [
        [
          "Jumpsuit",
          "SKU-2010"
        ],
        [
          "Belt",
          "SKU-2011"
        ],
        [
          "Earrings",
          "SKU-2012"
        ],
        [
          "Clutch",
          "SKU-2013"
        ]
      ],
      "recommended": false
    }
  ]
}
```

### `LOYALTY_PROGRAM`

```json
{
  "Platinum": {
    "discount_pct": 10,
    "bundle_pct": 5,
    "bundle_min_pieces": 3,
    "free_alterations_value": 35
  },
  "Gold": {
    "discount_pct": 5,
    "bundle_pct": 5,
    "bundle_min_pieces": 3,
    "free_alterations_value": 0
  }
}
```

### `FOLLOW_UP_TRIGGERS`

```json
[
  [
    "New Theory arrivals",
    "Notification",
    "Automatic"
  ],
  [
    "Pants low stock",
    "Alert",
    "If not purchased"
  ],
  [
    "Wishlist items on sale",
    "Email",
    "When discounted"
  ]
]
```

## Record-use boundary

Never infer body, health, identity, wealth, or another sensitive trait; reserve stock; apply a loyalty benefit or offer; process a return or refund; create an order; or complete a purchase.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
