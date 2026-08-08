# Returns and Complaints Resolution — Complete Synthetic Records

> **SYNTHETIC, READ-ONLY PILOT DATA.** Every identifier, name, date, status,
> quantity, amount, preference, interaction, order, cart, case, campaign, and
> metric below is fictional. It is reference evidence, not a live-system value
> or authorization to take action.

## Authoritative provenance

- Deterministic source: `agents/@aibast-agents-library/retail_cpg_stacks/returns_complaints_resolution_stack/returns_complaints_resolution_agent.py`
- Locked case contract: `tests/demo_cases/returns-complaints-resolution.json`
- Captured evidence: `solutions/returns-complaints-resolution/evals/transcripts.json`
- The JSON blocks below are exact literals copied from the deterministic source.
- Preserve identifiers, spelling, capitalization, dates, statuses, and numeric values.
- If production data differs, stop and verify in the authorized system of record.

## Locked-case source selections

| Case | Persona | Operation | Exact arguments |
|---|---|---|---|
| `RCR-01` | Customer Service Agent | `return_processing` | `{"return_id":"RET-4001"}` |
| `RCR-02` | Customer Service Agent | `complaint_classification` | `{"complaint_text":"The synthetic item stopped working after a week."}` |
| `RCR-03` | Customer Service Agent | `resolution_recommendation` | `{"return_id":"RET-4001"}` |
| `RCR-04` | Quality Team | `trend_analysis` | `{}` |

## Complete deterministic record sets

### `RETURN_REQUESTS`

```json
{
  "RET-4001": {
    "order_id": "ORD-88712",
    "case_label": "Synthetic size-mismatch case",
    "product": "Classic Denim Jacket",
    "sku": "SKU-1001",
    "purchase_price": 89.99,
    "purchase_date": "2026-02-14",
    "request_date": "2026-03-02",
    "reason": "wrong_size",
    "condition": "unworn_tags_attached",
    "channel": "online",
    "status": "pending_review",
    "notes": "Ordered size M, needs size L. Willing to exchange."
  },
  "RET-4002": {
    "order_id": "ORD-89234",
    "case_label": "Synthetic device-defect case",
    "product": "Smart Fitness Tracker",
    "sku": "SKU-1004",
    "purchase_price": 129.99,
    "purchase_date": "2026-01-20",
    "request_date": "2026-03-10",
    "reason": "defective",
    "condition": "non_functional",
    "channel": "in_store",
    "status": "policy_match_candidate",
    "notes": "Heart rate sensor stopped working after 3 weeks. Under warranty."
  },
  "RET-4003": {
    "order_id": "ORD-87455",
    "case_label": "Synthetic description-mismatch case",
    "product": "Premium Running Shoes",
    "sku": "SKU-1005",
    "purchase_price": 149.99,
    "purchase_date": "2026-02-28",
    "request_date": "2026-03-08",
    "reason": "not_as_described",
    "condition": "lightly_used",
    "channel": "online",
    "status": "pending_review",
    "notes": "Color shown online was navy but received was dark grey."
  },
  "RET-4004": {
    "order_id": "ORD-90100",
    "case_label": "Synthetic changed-mind case",
    "product": "Wireless Earbuds Pro",
    "sku": "SKU-1002",
    "purchase_price": 59.99,
    "purchase_date": "2026-03-01",
    "request_date": "2026-03-12",
    "reason": "changed_mind",
    "condition": "opened_unused",
    "channel": "online",
    "status": "pending_review",
    "notes": "Found a better deal elsewhere. Wants full refund."
  },
  "RET-4005": {
    "order_id": "ORD-86321",
    "case_label": "Synthetic warranty-escalation case",
    "product": "Leather Crossbody Bag",
    "sku": "SKU-1007",
    "purchase_price": 79.99,
    "purchase_date": "2025-12-18",
    "request_date": "2026-03-14",
    "reason": "defective",
    "condition": "damaged",
    "channel": "in_store",
    "status": "escalated",
    "notes": "Strap broke after normal use. Outside 60-day window but claims manufacturing defect."
  },
  "RET-4006": {
    "order_id": "ORD-91005",
    "case_label": "Synthetic wrong-item case",
    "product": "UV Protection Sunglasses",
    "sku": "SKU-1008",
    "purchase_price": 44.99,
    "purchase_date": "2026-03-05",
    "request_date": "2026-03-15",
    "reason": "wrong_item",
    "condition": "unopened",
    "channel": "online",
    "status": "policy_match_candidate",
    "notes": "Received aviator style instead of ordered wayfarer style."
  }
}
```

### `COMPLAINT_CATEGORIES`

```json
{
  "product_quality": {
    "label": "Product Quality",
    "severity_weight": 0.85,
    "avg_resolution_hours": 36,
    "escalation_rate": 0.15,
    "keywords": [
      "defective",
      "broken",
      "poor quality",
      "fell apart",
      "not durable"
    ],
    "monthly_volume": 142
  },
  "order_fulfillment": {
    "label": "Order Fulfillment",
    "severity_weight": 0.7,
    "avg_resolution_hours": 24,
    "escalation_rate": 0.08,
    "keywords": [
      "wrong item",
      "missing",
      "late delivery",
      "not received",
      "damaged in shipping"
    ],
    "monthly_volume": 98
  },
  "pricing_billing": {
    "label": "Pricing & Billing",
    "severity_weight": 0.65,
    "avg_resolution_hours": 18,
    "escalation_rate": 0.05,
    "keywords": [
      "overcharged",
      "wrong price",
      "coupon not applied",
      "double charged"
    ],
    "monthly_volume": 67
  },
  "service_experience": {
    "label": "Service Experience",
    "severity_weight": 0.6,
    "avg_resolution_hours": 48,
    "escalation_rate": 0.22,
    "keywords": [
      "rude staff",
      "long wait",
      "unhelpful",
      "no response",
      "poor communication"
    ],
    "monthly_volume": 53
  }
}
```

### `RESOLUTION_PLAYBOOKS`

```json
{
  "full_refund": {
    "label": "Full Refund",
    "applicable_reasons": [
      "defective",
      "wrong_item",
      "not_as_described"
    ],
    "applicable_conditions": [
      "non_functional",
      "unopened",
      "damaged"
    ],
    "max_days_since_purchase": 90,
    "cost_impact": "high",
    "csat_impact": "high",
    "steps": [
      "Review the synthetic eligibility evidence",
      "Draft a full-refund option for authorized approval",
      "List any return-shipping requirements without generating a label",
      "Draft neutral confirmation language without sending it",
      "State that no refund or return is processed by this agent"
    ]
  },
  "exchange": {
    "label": "Product Exchange",
    "applicable_reasons": [
      "wrong_size",
      "wrong_item",
      "not_as_described"
    ],
    "applicable_conditions": [
      "unworn_tags_attached",
      "unopened",
      "opened_unused"
    ],
    "max_days_since_purchase": 60,
    "cost_impact": "medium",
    "csat_impact": "very_high",
    "steps": [
      "Review the requested replacement and verify availability separately",
      "Draft exchange eligibility for authorized approval",
      "List logistics considerations without creating shipments",
      "Draft tracking-language requirements without sending a message",
      "State that no exchange or reservation is performed"
    ]
  },
  "store_credit": {
    "label": "Store Credit",
    "applicable_reasons": [
      "changed_mind",
      "wrong_size"
    ],
    "applicable_conditions": [
      "opened_unused",
      "lightly_used",
      "unworn_tags_attached"
    ],
    "max_days_since_purchase": 45,
    "cost_impact": "low",
    "csat_impact": "moderate",
    "steps": [
      "Review whether the condition appears to meet the synthetic policy",
      "Draft a store-credit option without issuing value or a bonus",
      "Require authorized review before any loyalty-account change",
      "Draft disclosure language without sending a message"
    ]
  },
  "warranty_replacement": {
    "label": "Warranty Replacement",
    "applicable_reasons": [
      "defective"
    ],
    "applicable_conditions": [
      "non_functional",
      "damaged"
    ],
    "max_days_since_purchase": 365,
    "cost_impact": "medium",
    "csat_impact": "high",
    "steps": [
      "Review whether the synthetic record is within the warranty period",
      "List the documentation an authorized reviewer should inspect",
      "Draft a manufacturer-claim summary without submitting it",
      "List replacement considerations without reserving or shipping stock",
      "State that no return label or replacement is created"
    ]
  },
  "partial_refund": {
    "label": "Partial Refund",
    "applicable_reasons": [
      "not_as_described",
      "changed_mind"
    ],
    "applicable_conditions": [
      "lightly_used"
    ],
    "max_days_since_purchase": 30,
    "cost_impact": "medium",
    "csat_impact": "moderate",
    "steps": [
      "Review item-condition evidence and model a policy range",
      "Identify any disclosed fee rule for authorized review",
      "Draft a partial-refund option without processing funds",
      "Draft timeline language without notifying a customer"
    ]
  }
}
```

### `TREND_DATA`

```json
{
  "months": [
    "2025-10",
    "2025-11",
    "2025-12",
    "2026-01",
    "2026-02",
    "2026-03"
  ],
  "total_returns": [
    312,
    345,
    498,
    387,
    328,
    360
  ],
  "return_rate_pct": [
    4.1,
    4.5,
    6.2,
    5.0,
    4.3,
    4.7
  ],
  "top_return_reasons": {
    "wrong_size": [
      98,
      112,
      160,
      125,
      105,
      115
    ],
    "defective": [
      72,
      68,
      95,
      82,
      71,
      78
    ],
    "changed_mind": [
      65,
      78,
      130,
      88,
      70,
      80
    ],
    "not_as_described": [
      45,
      52,
      68,
      55,
      48,
      52
    ],
    "wrong_item": [
      32,
      35,
      45,
      37,
      34,
      35
    ]
  },
  "avg_resolution_hours": [
    28.5,
    30.2,
    38.7,
    32.1,
    27.8,
    29.4
  ],
  "csat_score": [
    4.1,
    4.0,
    3.6,
    3.9,
    4.2,
    4.1
  ],
  "refund_total_usd": [
    18720.0,
    21450.0,
    34200.0,
    24800.0,
    19650.0,
    22100.0
  ]
}
```

## Record-use boundary

Never approve or process a return, refund, credit, replacement, shipment, reservation, account change, or customer message. Never accuse a person of fraud or misconduct.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
