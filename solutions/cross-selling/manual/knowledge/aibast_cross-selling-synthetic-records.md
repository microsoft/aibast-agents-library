# Cross Selling Opportunities Agent — Complete Fixed Synthetic Source Records

> **FIXED SYNTHETIC DEMO DATA ONLY.** This file is a complete serialization of the deterministic datasets used by the locked cases. It contains no live customer, CRM, email, meeting, product, competitive, subscription, or commercial data. Do not browse, enrich, substitute, infer, or invent records.

## Source and capture scope

- Deterministic source: `agents/@aibast-agents-library/general_stacks/cross_selling_opportunities_stack/cross_selling_agent.py`
- Strict transcript evidence: `solutions/cross-selling/evals/transcripts.json`
- Transcript captured at: `2026-08-08T04:36:33.425660+00:00`
- Strict isolation: `true`
- Supported source: this uploaded fixed snapshot only

If a requested identifier or fact is absent below, state that it is absent from the fixed synthetic snapshot.

## Dataset index

| Source constant | Records or fields |
| --- | ---: |
| `_PRODUCT_CATALOG` | 8 |
| `_CUSTOMER_OWNERSHIP` | 5 |
| `_AFFINITY_RULES` | 8 |
| `_CROSS_SELL_SUCCESS_RATES` | 3 |

## Exact dataset `_PRODUCT_CATALOG`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "ANLYT-100": {
    "annual_price": 12000,
    "category": "Analytics",
    "margin_pct": 82,
    "name": "Analytics Standard"
  },
  "ANLYT-200": {
    "annual_price": 28000,
    "category": "Analytics",
    "margin_pct": 85,
    "name": "Analytics Pro"
  },
  "INTGR-100": {
    "annual_price": 18000,
    "category": "Integration",
    "margin_pct": 78,
    "name": "Integration Hub"
  },
  "PLAT-100": {
    "annual_price": 24000,
    "category": "Platform",
    "margin_pct": 72,
    "name": "Core Platform"
  },
  "PLAT-200": {
    "annual_price": 60000,
    "category": "Platform",
    "margin_pct": 75,
    "name": "Enterprise Platform"
  },
  "SECUR-100": {
    "annual_price": 15000,
    "category": "Security",
    "margin_pct": 80,
    "name": "Security Suite"
  },
  "SUPRT-100": {
    "annual_price": 8000,
    "category": "Support",
    "margin_pct": 90,
    "name": "Premium Support"
  },
  "TRAIN-100": {
    "annual_price": 5000,
    "category": "Services",
    "margin_pct": 65,
    "name": "Training Package"
  }
}
```

## Exact dataset `_CUSTOMER_OWNERSHIP`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "CUST-001": {
    "arr": 84000,
    "budget_window": "Annual planning review next quarter",
    "buying_signals": [
      "Requested advanced analytics comparison"
    ],
    "contact": "Sandra Lee",
    "health_score": 92,
    "name": "Meridian Corp",
    "products": [
      "PLAT-200",
      "ANLYT-100",
      "SUPRT-100"
    ],
    "segment": "Enterprise",
    "tenure_months": 24,
    "usage_signals": [
      "Analytics export volume rising",
      "Security admin workflow used weekly"
    ]
  },
  "CUST-002": {
    "arr": 42000,
    "budget_window": "Department planning review this quarter",
    "buying_signals": [
      "Asked about support coverage"
    ],
    "contact": "Marco Torres",
    "health_score": 78,
    "name": "Atlas Digital",
    "products": [
      "PLAT-100",
      "INTGR-100"
    ],
    "segment": "Mid-Market",
    "tenure_months": 18,
    "usage_signals": [
      "Integration jobs approaching synthetic capacity threshold"
    ]
  },
  "CUST-003": {
    "arr": 60000,
    "budget_window": "Post-implementation value review",
    "buying_signals": [
      "Feature request references analytics and security"
    ],
    "contact": "Dr. Amy Patel",
    "health_score": 85,
    "name": "Pinnacle Health",
    "products": [
      "PLAT-200"
    ],
    "segment": "Enterprise",
    "tenure_months": 6,
    "usage_signals": [
      "Core workflow adoption broadening across teams"
    ]
  },
  "CUST-004": {
    "arr": 24000,
    "budget_window": "Retail planning cycle later this year",
    "buying_signals": [
      "Requested integration roadmap"
    ],
    "contact": "Kevin O'Neill",
    "health_score": 65,
    "name": "Greenleaf Retail",
    "products": [
      "PLAT-100"
    ],
    "segment": "Mid-Market",
    "tenure_months": 12,
    "usage_signals": [
      "Reporting exports remain manual",
      "Support usage increasing"
    ]
  },
  "CUST-005": {
    "arr": 113000,
    "budget_window": "Enterprise agreement review",
    "buying_signals": [
      "Asked about premium support coverage"
    ],
    "contact": "Rachel Kim",
    "health_score": 96,
    "name": "Beacon Financial",
    "products": [
      "PLAT-200",
      "ANLYT-200",
      "INTGR-100",
      "SECUR-100"
    ],
    "segment": "Enterprise",
    "tenure_months": 36,
    "usage_signals": [
      "Broad adoption across owned products"
    ]
  }
}
```

## Exact dataset `_AFFINITY_RULES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "affinity_score": 0.85,
    "avg_time_to_close_days": 35,
    "if_owns": "PLAT-100",
    "recommend": "ANLYT-100",
    "success_rate": 0.42
  },
  {
    "affinity_score": 0.72,
    "avg_time_to_close_days": 45,
    "if_owns": "PLAT-100",
    "recommend": "INTGR-100",
    "success_rate": 0.38
  },
  {
    "affinity_score": 0.91,
    "avg_time_to_close_days": 28,
    "if_owns": "PLAT-200",
    "recommend": "ANLYT-200",
    "success_rate": 0.55
  },
  {
    "affinity_score": 0.78,
    "avg_time_to_close_days": 30,
    "if_owns": "PLAT-200",
    "recommend": "SECUR-100",
    "success_rate": 0.48
  },
  {
    "affinity_score": 0.88,
    "avg_time_to_close_days": 21,
    "if_owns": "ANLYT-100",
    "recommend": "ANLYT-200",
    "success_rate": 0.62
  },
  {
    "affinity_score": 0.67,
    "avg_time_to_close_days": 40,
    "if_owns": "INTGR-100",
    "recommend": "SECUR-100",
    "success_rate": 0.35
  },
  {
    "affinity_score": 0.82,
    "avg_time_to_close_days": 14,
    "if_owns": "PLAT-200",
    "recommend": "SUPRT-100",
    "success_rate": 0.65
  },
  {
    "affinity_score": 0.7,
    "avg_time_to_close_days": 21,
    "if_owns": "PLAT-100",
    "recommend": "SUPRT-100",
    "success_rate": 0.5
  }
]
```

## Exact dataset `_CROSS_SELL_SUCCESS_RATES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "Enterprise": {
    "avg_deal_cycle_days": 28,
    "avg_expansion_pct": 35,
    "avg_success_rate": 0.52
  },
  "Mid-Market": {
    "avg_deal_cycle_days": 42,
    "avg_expansion_pct": 25,
    "avg_success_rate": 0.38
  },
  "SMB": {
    "avg_deal_cycle_days": 55,
    "avg_expansion_pct": 18,
    "avg_success_rate": 0.28
  }
}
```

## Data-use boundary

Every identifier, company, person, date, count, price, amount, score, percentage, probability, benchmark, signal, claim, and projection above is synthetic. No outreach may be sent; no CRM, forecast, owner, task, alert, workflow, meeting, proposal, approval, pricing, subscription, renewal, product entitlement, or customer communication may be created, changed, activated, or delivered from this evidence.
