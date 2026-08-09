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

## Complete deterministic record sets

### `ABANDONED_CARTS`

```json
{
  "CART-20001": {
    "shopper_label": "Synthetic returning-shopper cart",
    "contactable": true,
    "segment": "returning_shopper",
    "items": [
      {
        "name": "Wireless Noise-Canceling Headphones",
        "sku": "ELEC-4421",
        "price": 249.99,
        "qty": 1
      },
      {
        "name": "Premium Headphone Case",
        "sku": "ACC-1102",
        "price": 34.99,
        "qty": 1
      }
    ],
    "cart_value": 284.98,
    "abandoned_at": "2025-03-04T14:22:00",
    "page_exit": "shipping_options",
    "device": "mobile",
    "prior_purchases": 8,
    "recovery_status": "draft_stage_1_ready"
  },
  "CART-20002": {
    "shopper_label": "Synthetic first-session cart",
    "contactable": true,
    "segment": "new_visitor",
    "items": [
      {
        "name": "Smart Home Hub Pro",
        "sku": "SMRT-3305",
        "price": 179.99,
        "qty": 1
      },
      {
        "name": "Smart Bulb 4-Pack",
        "sku": "SMRT-1140",
        "price": 59.99,
        "qty": 2
      }
    ],
    "cart_value": 299.97,
    "abandoned_at": "2025-03-05T09:15:00",
    "page_exit": "account_creation",
    "device": "desktop",
    "prior_purchases": 0,
    "recovery_status": "not_contacted"
  },
  "CART-20003": {
    "shopper_label": "Synthetic established-shopper cart",
    "contactable": true,
    "segment": "established_shopper",
    "items": [
      {
        "name": "4K OLED Smart TV 65-inch",
        "sku": "TV-7720",
        "price": 1299.99,
        "qty": 1
      },
      {
        "name": "Soundbar System",
        "sku": "AUD-5501",
        "price": 449.99,
        "qty": 1
      },
      {
        "name": "HDMI Cable 6ft",
        "sku": "ACC-0042",
        "price": 14.99,
        "qty": 2
      }
    ],
    "cart_value": 1779.96,
    "abandoned_at": "2025-03-05T18:45:00",
    "page_exit": "payment",
    "device": "desktop",
    "prior_purchases": 12,
    "recovery_status": "not_contacted"
  },
  "CART-20004": {
    "shopper_label": "Synthetic guest cart",
    "contactable": false,
    "segment": "guest",
    "items": [
      {
        "name": "Running Shoes Pro X",
        "sku": "SHOE-2201",
        "price": 129.99,
        "qty": 1
      }
    ],
    "cart_value": 129.99,
    "abandoned_at": "2025-03-06T11:30:00",
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
  }
}
```

### `INCENTIVE_OPTIONS`

```json
{
  "percent_off_10": {
    "description": "10% off cart total",
    "cost_margin_impact": 10.0,
    "conversion_lift": 35.0
  },
  "percent_off_15": {
    "description": "15% off cart total",
    "cost_margin_impact": 15.0,
    "conversion_lift": 48.0
  },
  "free_shipping": {
    "description": "Free standard shipping",
    "cost_margin_impact": 5.5,
    "conversion_lift": 28.0
  },
  "dollar_off_20": {
    "description": "$20 off orders over $150",
    "cost_margin_impact": 8.0,
    "conversion_lift": 22.0
  },
  "gift_with_purchase": {
    "description": "Free accessory with order",
    "cost_margin_impact": 6.0,
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

## Record-use boundary

Never identify or contact a shopper; send or schedule a message; create, issue, or apply an offer; change a cart; reserve an item; or complete a purchase.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
