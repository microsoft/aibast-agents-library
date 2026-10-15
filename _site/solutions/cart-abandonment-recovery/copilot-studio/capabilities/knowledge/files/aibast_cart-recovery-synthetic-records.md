# Cart Abandonment Recovery — Complete Synthetic Records

> **SYNTHETIC, READ-ONLY PILOT DATA.** Every identifier, name, date, status,
> quantity, amount, preference, interaction, order, cart, case, campaign, and
> metric below is fictional. It is reference evidence, not a live-system value
> or authorization to take action.

## Authoritative provenance

- Deterministic source: `agents/@aibast-agents-library/b2c_sales_stacks/cart_abandonment_recovery_stack/cart_abandonment_recovery_agent.py`
- Locked case contract: `tests/demo_cases/cart-abandonment-recovery.json`
- Captured evidence: `solutions/cart-abandonment-recovery/evals/transcripts.json`
- The JSON blocks below are exact literals copied from the deterministic source.
- Preserve identifiers, spelling, capitalization, dates, statuses, and numeric values.
- If production data differs, stop and verify in the authorized system of record.

## Locked-case source selections

| Case | Persona | Operation | Exact arguments |
|---|---|---|---|
| `CAR-01` | Marketing Manager | `abandonment_analysis` | `{}` |
| `CAR-02` | Digital Marketing Lead | `recovery_campaign` | `{}` |
| `CAR-03` | Growth Manager | `incentive_optimization` | `{}` |
| `CAR-04` | Growth Manager | `conversion_tracking` | `{}` |
| `CAR-05` | Marketing Manager | `recovery_strategies` | `{}` |
| `CAR-06` | Growth Manager | `recovery_forecast` | `{}` |
| `CAR-07` | Growth Manager | `optimization_recommendations` | `{}` |

## Complete deterministic record sets

### `ABANDONED_CARTS`

```json
{
  "CART-20001": {
    "shopper_label": "Sarah M",
    "contactable": true,
    "segment": "vip",
    "items": [
      {
        "name": "Designer Leather Tote",
        "sku": "BAG-4421",
        "price": 489.0,
        "qty": 1
      },
      {
        "name": "Leather Crossbody Bag",
        "sku": "BAG-1102",
        "price": 403.0,
        "qty": 1
      }
    ],
    "cart_value": 892.0,
    "abandoned_at": "2025-03-05T14:22:00",
    "page_exit": "shipping_options",
    "device": "mobile",
    "prior_purchases": 14,
    "recovery_status": "draft_stage_1_ready"
  },
  "CART-20002": {
    "shopper_label": "James K",
    "contactable": true,
    "segment": "repeat_buyer",
    "items": [
      {
        "name": "Weekender Duffel",
        "sku": "BAG-3305",
        "price": 399.0,
        "qty": 1
      },
      {
        "name": "Leather Wallet",
        "sku": "ACC-1140",
        "price": 248.0,
        "qty": 1
      }
    ],
    "cart_value": 647.0,
    "abandoned_at": "2025-03-05T09:15:00",
    "page_exit": "payment",
    "device": "desktop",
    "prior_purchases": 5,
    "recovery_status": "not_contacted"
  },
  "CART-20003": {
    "shopper_label": "Emily R",
    "contactable": true,
    "segment": "repeat_buyer",
    "items": [
      {
        "name": "Travel Backpack",
        "sku": "BAG-7720",
        "price": 289.0,
        "qty": 1
      },
      {
        "name": "Packing Cube Set",
        "sku": "ACC-5501",
        "price": 245.0,
        "qty": 1
      }
    ],
    "cart_value": 534.0,
    "abandoned_at": "2025-03-05T18:45:00",
    "page_exit": "shipping_options",
    "device": "desktop",
    "prior_purchases": 3,
    "recovery_status": "not_contacted"
  },
  "CART-20004": {
    "shopper_label": "Guest shopper",
    "contactable": false,
    "segment": "guest",
    "items": [
      {
        "name": "Canvas Tote",
        "sku": "BAG-2201",
        "price": 129.99,
        "qty": 1
      }
    ],
    "cart_value": 129.99,
    "abandoned_at": "2025-03-05T11:30:00",
    "page_exit": "cart_page",
    "device": "mobile",
    "prior_purchases": 0,
    "recovery_status": "unrecoverable"
  }
}
```

### `RECOVERY_CAMPAIGNS`

```json
{
  "email_1": {
    "name": "Draft Email Reminder",
    "delay_hours": 1,
    "subject": "Draft: neutral cart reminder",
    "incentive": null,
    "avg_open_rate": 45.2,
    "avg_conversion": 8.5
  },
  "sms_1": {
    "name": "Draft SMS Reminder",
    "delay_hours": 2,
    "subject": "Draft: concise cart reminder",
    "incentive": null,
    "avg_open_rate": 98.0,
    "avg_conversion": 4.8
  },
  "retargeting_ad": {
    "name": "Draft Retargeting Concept",
    "delay_hours": 6,
    "subject": "Draft: consented product reminder concept",
    "incentive": null,
    "avg_open_rate": 0,
    "avg_conversion": 2.1
  },
  "email_2": {
    "name": "Draft Follow-Up",
    "delay_hours": 24,
    "subject": "Draft: availability-neutral follow-up",
    "incentive": null,
    "avg_open_rate": 38.1,
    "avg_conversion": 5.2
  },
  "email_3": {
    "name": "Draft Value Option",
    "delay_hours": 72,
    "subject": "Draft: approved value option, if eligible",
    "incentive": "Optional incentive concept",
    "avg_open_rate": 42.8,
    "avg_conversion": 12.1
  }
}
```

### `INCENTIVE_OPTIONS`

```json
{
  "percent_off_10": {
    "description": "10% off cart total",
    "cost_margin_impact": 10.0,
    "flat_cost": 0,
    "conversion_lift": 35.0
  },
  "percent_off_15": {
    "description": "15% off cart total",
    "cost_margin_impact": 15.0,
    "flat_cost": 0,
    "conversion_lift": 48.0
  },
  "free_shipping": {
    "description": "Free standard shipping",
    "cost_margin_impact": 0.0,
    "flat_cost": 12,
    "conversion_lift": 28.0
  },
  "dollar_off_20": {
    "description": "$20 off orders over $150",
    "cost_margin_impact": 0.0,
    "flat_cost": 20,
    "conversion_lift": 22.0
  },
  "gift_with_purchase": {
    "description": "Free accessory with order",
    "cost_margin_impact": 6.0,
    "flat_cost": 0,
    "conversion_lift": 18.0
  }
}
```

### `CONVERSION_METRICS`

```json
{
  "overall_abandonment_rate": 71.4,
  "recovery_rate": 12.8,
  "avg_recovered_value": 187.5,
  "total_abandoned_30d": 4250,
  "total_recovered_30d": 544,
  "total_recovered_revenue_30d": 102000
}
```

### `TODAY_SEGMENTS`

```json
[
  {
    "segment": "VIP",
    "carts": 34,
    "value": 18400,
    "recovery_pct": 45
  },
  {
    "segment": "Repeat buyers",
    "carts": 89,
    "value": 24200,
    "recovery_pct": 38
  },
  {
    "segment": "New visitors",
    "carts": 412,
    "value": 52800,
    "recovery_pct": 22
  },
  {
    "segment": "Other shoppers",
    "carts": 312,
    "value": 31600,
    "recovery_pct": 28
  }
]
```

### `ABANDON_REASONS`

```json
[
  {
    "reason": "shipping cost",
    "pct": 42
  },
  {
    "reason": "comparison shopping",
    "pct": 28
  },
  {
    "reason": "payment friction",
    "pct": 18
  },
  {
    "reason": "other",
    "pct": 12
  }
]
```

### `RECOVERY_STRATEGIES`

```json
[
  {
    "audience": "Sarah M. ($892 VIP)",
    "offer": "\"Your favorite bags are 40% off\" + double points",
    "channel": "Email + SMS"
  },
  {
    "audience": "High-Value (8,400)",
    "offer": "VIP early access + 3X points",
    "channel": "Email"
  },
  {
    "audience": "Point Expiry (12,000)",
    "offer": "\"Use before they expire\" + 25% bonus",
    "channel": "Email + push"
  },
  {
    "audience": "Lapsed Browsers (13,600)",
    "offer": "Items viewed + 20% off + free shipping",
    "channel": "Email + retargeting"
  }
]
```

### `CAMPAIGN_AUDIENCES`

```json
[
  {
    "campaign": "High-value win-back",
    "members": 8400
  },
  {
    "campaign": "Point expiry alert",
    "members": 12000
  },
  {
    "campaign": "Lapsed browser",
    "members": 13600
  }
]
```

### `MULTI_TOUCH_SEQUENCES`

```json
[
  {
    "segment": "VIP",
    "steps": [
      "Personal note",
      "SMS 1hr",
      "Express shipping 4hr",
      "Call 24hr ($500+)"
    ]
  },
  {
    "segment": "Repeat",
    "steps": [
      "Points reminder",
      "Push 2hr",
      "Free shipping hint 12hr"
    ]
  },
  {
    "segment": "New",
    "steps": [
      "Welcome 10% off",
      "Retargeting",
      "Social proof 24hr"
    ]
  }
]
```

### `BENCHMARKS`

```json
{
  "industry_recovery_pct": 18,
  "target_recovery_pct": 27,
  "optimized_recovery_pct": 35,
  "monthly_recovered_current": 172000,
  "monthly_recovered_optimized": 228000
}
```

### `OPTIMIZATIONS`

```json
[
  {
    "opportunity": "Exit intent popup",
    "monthly_impact": 18000
  },
  {
    "opportunity": "SMS all segments",
    "monthly_impact": 12000
  },
  {
    "opportunity": "Dynamic pricing",
    "monthly_impact": 8000
  },
  {
    "opportunity": "Lower shipping ($75>$65)",
    "monthly_impact": 6000
  },
  {
    "opportunity": "Express wallet checkout",
    "monthly_impact": 4000
  }
]
```

### `OPTIMIZATION_NOTES`

```json
{
  "quick_win": "Exit intent popup - \"Wait! 10% off\" - 8-12% conversion, same-day implementation",
  "insight": "42% abandon at shipping reveal - lower threshold or flat $5 rate"
}
```

## Record-use boundary

Never identify or contact a shopper; send or schedule a message; create, issue, or apply an offer; change a cart; reserve an item; or complete a purchase.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
