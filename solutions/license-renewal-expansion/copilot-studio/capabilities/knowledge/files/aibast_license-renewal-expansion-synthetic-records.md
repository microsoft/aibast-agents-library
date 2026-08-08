# License Renewal and Expansion Agent — Complete Fixed Synthetic Source Records

> **FIXED SYNTHETIC DEMO DATA ONLY.** This file is a complete serialization of the deterministic datasets used by the locked cases. It contains no live customer, CRM, email, meeting, product, competitive, subscription, or commercial data. Do not browse, enrich, substitute, infer, or invent records.

## Source and capture scope

- Deterministic source: `agents/@aibast-agents-library/software_dp_stacks/license_renewal_expansion_stack/license_renewal_expansion_agent.py`
- Strict transcript evidence: `solutions/license-renewal-expansion/evals/transcripts.json`
- Transcript captured at: `2026-08-08T04:40:03.765297+00:00`
- Strict isolation: `true`
- Supported source: this uploaded fixed snapshot only

If a requested identifier or fact is absent below, state that it is absent from the fixed synthetic snapshot.

## Dataset index

| Source constant | Records or fields |
| --- | ---: |
| `LICENSE_AGREEMENTS` | 5 |
| `EXPANSION_PRICING` | 5 |
| `SWITCHING_COST_ASSUMPTIONS` | 4 |

## Exact dataset `LICENSE_AGREEMENTS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "LIC-3001": {
    "arr": 288000,
    "churn_signals": [],
    "contract_start": "2025-04-30",
    "csm": "Dana Reeves",
    "customer": "Pinnacle Insurance Corp",
    "expansion_signals": [
      "API usage +45% QoQ",
      "Requested SSO for 3 subsidiaries"
    ],
    "health_score": 88,
    "nps_score": 72,
    "plan": "Enterprise",
    "renewal_date": "2026-04-30",
    "seats": 150,
    "seats_used": 142,
    "support_tickets_90d": 4,
    "usage_trend": "increasing"
  },
  "LIC-3002": {
    "arr": 72000,
    "churn_signals": [
      "Usage down 32%",
      "Executive sponsor departed",
      "Competitor eval detected"
    ],
    "contract_start": "2025-05-15",
    "csm": "James Okafor",
    "customer": "ClearView Analytics",
    "expansion_signals": [],
    "health_score": 29,
    "nps_score": 34,
    "plan": "Professional",
    "renewal_date": "2026-05-15",
    "seats": 30,
    "seats_used": 18,
    "support_tickets_90d": 18,
    "usage_trend": "declining"
  },
  "LIC-3003": {
    "arr": 192000,
    "churn_signals": [
      "Budget freeze mentioned in QBR"
    ],
    "contract_start": "2025-06-01",
    "csm": "Dana Reeves",
    "customer": "Redwood Supply Chain",
    "expansion_signals": [
      "Inquired about analytics add-on"
    ],
    "health_score": 62,
    "nps_score": 65,
    "plan": "Enterprise",
    "renewal_date": "2026-06-01",
    "seats": 80,
    "seats_used": 79,
    "support_tickets_90d": 7,
    "usage_trend": "stable"
  },
  "LIC-3004": {
    "arr": 360000,
    "churn_signals": [],
    "contract_start": "2025-04-15",
    "csm": "James Okafor",
    "customer": "Skyline Hospitality Group",
    "expansion_signals": [
      "Opening 12 new locations",
      "Requested bulk seat pricing",
      "Custom integration POC"
    ],
    "health_score": 94,
    "nps_score": 85,
    "plan": "Enterprise",
    "renewal_date": "2026-04-15",
    "seats": 250,
    "seats_used": 248,
    "support_tickets_90d": 2,
    "usage_trend": "increasing"
  },
  "LIC-3005": {
    "arr": 54000,
    "churn_signals": [
      "Primary admin inactive 45 days",
      "Missed last 2 QBRs"
    ],
    "contract_start": "2025-07-01",
    "csm": "Dana Reeves",
    "customer": "Granite Construction Co",
    "expansion_signals": [],
    "health_score": 35,
    "nps_score": 41,
    "plan": "Professional",
    "renewal_date": "2026-07-01",
    "seats": 20,
    "seats_used": 12,
    "support_tickets_90d": 11,
    "usage_trend": "declining"
  }
}
```

## Exact dataset `EXPANSION_PRICING`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "additional_seats": {
    "min_qty": 10,
    "unit_price": 120
  },
  "analytics_addon": {
    "description": "Advanced analytics module",
    "price": 24000
  },
  "api_premium": {
    "description": "Premium API tier with higher rate limits",
    "price": 18000
  },
  "custom_integration": {
    "description": "Custom integration package",
    "price": 36000
  },
  "sso_subsidiary": {
    "description": "SSO extension per subsidiary",
    "price": 12000
  }
}
```

## Exact dataset `SWITCHING_COST_ASSUMPTIONS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "data_migration": 45000,
  "parallel_run": 24000,
  "reimplementation": 60000,
  "user_retraining": 18000
}
```

## Data-use boundary

Every identifier, company, person, date, count, price, amount, score, percentage, probability, benchmark, signal, claim, and projection above is synthetic. No outreach may be sent; no CRM, forecast, owner, task, alert, workflow, meeting, proposal, approval, pricing, subscription, renewal, product entitlement, or customer communication may be created, changed, activated, or delivered from this evidence.
