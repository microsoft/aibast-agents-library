# License Renewal and Expansion Agent — Complete Fixed Synthetic Source Records

> **FIXED SYNTHETIC DEMO DATA ONLY.** This file is a complete serialization of the deterministic datasets used by the locked cases. It contains no live customer, CRM, email, meeting, product, competitive, subscription, or commercial data. Do not browse, enrich, substitute, infer, or invent records.

## Source and capture scope

- Deterministic source: `agents/@aibast-agents-library/software_dp_stacks/license_renewal_expansion_stack/license_renewal_expansion_agent.py`
- Strict transcript evidence: `solutions/license-renewal-expansion/evals/transcripts.json`
- Transcript captured at: `2026-10-07T01:20:20.693447+00:00`
- Strict isolation: `true`
- Supported source: this uploaded fixed snapshot only

If a requested identifier or fact is absent below, state that it is absent from the fixed synthetic snapshot.

## Dataset index

| Source constant | Records or fields |
| --- | ---: |
| `LICENSE_AGREEMENTS` | 6 |
| `EXPANSION_PRICING` | 5 |
| `SWITCHING_COST_ASSUMPTIONS` | 3 |
| `ACCOUNT_DETAILS` | 1 |
| `RENEWAL_TERMS` | 5 |
| `EXECUTIVE_BRIEF` | 3 |
| `CONCESSION_POLICY` | 5 |
| `APPROVAL_ROUTING` | 4 |
| `NEGOTIATION_STRATEGY` | 3 |
| `DEAL_OUTLOOK` | 3 |

## Exact dataset `LICENSE_AGREEMENTS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "LIC-3000": {
    "arr": 1000000,
    "churn_signals": [
      "Competitor offer: FinTech Solutions at a 30% discount"
    ],
    "contract_start": "2025-04-30",
    "csm": "Dana Reeves",
    "customer": "GlobalBank",
    "expansion_signals": [
      "Waitlist demand: 500 users",
      "12 of 15 modules actively used"
    ],
    "health_score": 87,
    "nps_score": 72,
    "plan": "Enterprise",
    "renewal_date": "2026-04-30",
    "seats": 2000,
    "seats_used": 1987,
    "support_tickets_90d": 3,
    "usage_trend": "increasing"
  },
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
  "data_migration": 180000,
  "integration_rebuild": 200000,
  "user_retraining": 120000
}
```

## Exact dataset `ACCOUNT_DETAILS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "LIC-3000": {
    "api_calls_month": "2.3M",
    "api_growth_mom_pct": 15,
    "competitor": {
      "discount_pct": 30,
      "feature_parity_pct": 78,
      "integration_time": "4-6 months",
      "migration_offer": 0,
      "vendor": "FinTech Solutions"
    },
    "decision_maker": "VP of Technology",
    "documented_savings": 4200000,
    "modules_total": 15,
    "modules_used": 12,
    "switching_detail": {
      "data_migration": "6-week project",
      "integration_rebuild": "8 custom connections",
      "user_retraining": "2,000 users, plus productivity loss"
    },
    "waitlist_users": 500
  }
}
```

## Exact dataset `RENEWAL_TERMS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "counter_strategy": [
    "Match their 30% discount on renewal",
    "Add premium support ($60K value) at no charge",
    "Lock a 3-year term for stability",
    "Include an executive roadmap session"
  ],
  "matched_discount_pct": 30,
  "multi_year_discount_pct": 10,
  "premium_support_value": 60000,
  "term_years": 3
}
```

## Exact dataset `EXECUTIVE_BRIEF`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "objection_handlers": 12,
  "slides": [
    "Title - GlobalBank strategic partnership renewal",
    "Partnership Value - $4.2M savings delivered",
    "Usage Success - 99.4% adoption, 12 modules active",
    "Growth Support - 500 new seats for waitlisted teams",
    "Competitive Comparison - TCO analysis showing $500K switching cost",
    "Proposal Summary - 2,500 seats, 3-year commitment",
    "Roadmap Preview - features launching in the next 12 months",
    "Next Steps - executive decision 30 days before expiry"
  ],
  "talking_points": [
    "You've realized $4.2M in savings - 5x your investment",
    "Switching costs $500K+ before any productivity loss",
    "We're matching their price AND adding premium support",
    "A 3-year term locks in today's pricing against inflation"
  ]
}
```

## Exact dataset `CONCESSION_POLICY`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "approver": "Pre-approved policy for a 3-year term",
    "floor": "30%",
    "lever": "Discount",
    "target": "25%"
  },
  {
    "approver": "None (standard)",
    "floor": "1 year",
    "lever": "Term",
    "target": "3 years"
  },
  {
    "approver": "Finance",
    "floor": "Net 60",
    "lever": "Payment",
    "target": "Annual upfront"
  },
  {
    "approver": "VP Sales",
    "floor": "Included",
    "lever": "Premium support",
    "target": "Included"
  },
  {
    "approver": "VP Sales",
    "floor": "$0",
    "lever": "Implementation",
    "target": "$0 for new modules"
  }
]
```

## Exact dataset `APPROVAL_ROUTING`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  "Finance: request confirmation of the 30% discount for a 3-year term",
  "Legal: contract template ready for review; redlines pending",
  "VP Sales: implementation waiver to request",
  "CFO: required only if the discount exceeds 35%"
]
```

## Exact dataset `NEGOTIATION_STRATEGY`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  "Lead with value ($4.2M savings)",
  "Anchor on a 25% discount, concede to 30%",
  "Trade discount for a longer term or upfront payment"
]
```

## Exact dataset `DEAL_OUTLOOK`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "next_steps": [
    "Executive meeting: request for next week",
    "Decision timeline: 30 days before expiration"
  ],
  "win_probability_after_pct": 78,
  "win_probability_before_pct": 52
}
```

## Demo walkthrough (video scenario)

The strategic account GlobalBank (`LIC-3000`) renews on 2026-04-30, 45 days after the fixed demo date `DEMO_AS_OF`
(2026-03-16), with 2,000 seats at $1.0M ARR, 1,987 active users (99.4%), 500 waitlisted users, health 87, NPS 72 and
a competitor (FinTech Solutions) offering 30% off. Account operations default to GlobalBank; no identifier is needed.

| Turn | User prompt | Operation | Key values |
|---|---|---|---|
| 1 | GlobalBank license expires in 45 days. Currently 2,000 seats at $1M ARR. Usage shows they need 500 more seats. Competitor offering 30% discount. | `account_health` | Account Analysis: GlobalBank; $1.0M (2,000 seats); 99.4% (1,987 users); 500 users waitlisted; 87/100; FinTech Solutions 30% discount; $4.2M savings; 12 of 15 modules; 2.3M API calls/month (+15% MoM); NPS 72 |
| 2 | Yes, show me the competitive defense strategy. | `competitive_defense` | Competitive Defense Strategy; price 30% lower vs match + value-add; migration $0 offered vs $500K actual; parity 78% vs 100%; integration 4-6 months vs done; data migration $180K, retraining $120K, integration rebuild $200K, total ~$500K; counter-strategy (match 30%, premium support $60K free, 3-year term, roadmap session) |
| 3 | Yes, build the renewal and expansion proposal. | `renewal_proposal` | $500 list -> $350/seat; base 2,000 x $350 = $700K; expansion 500 x $350 = $175K; premium support $60K value included; $875K for 2,500 seats; 3-year term additional 10% = $787.5K/year; ROI 5.3x on $4.2M savings |
| 4 | Yes, create the executive presentation with talking points. | `executive_brief` | Draft Executive Presentation; 8 slides; Key Talking Points; 12 objection handlers |
| 5 | Yes, show me negotiation strategy and what approvals I need. | `negotiation_plan` | Negotiation Boundaries (discount floor 30%, target 25%; term 1 -> 3 years; payment Net 60 vs annual upfront; premium support; implementation $0); Internal Approvals to Request (Finance, Legal, VP Sales, CFO only above 35%); strategy |
| 6 | Yes, send the proposal and summarize our renewal strategy. | `deal_summary` | Proposal ready to send (not sent); ARR $1.0M -> $787.5K (-21%); seats 2,000 -> 2,500 (+25%); 1 -> 3 years; TCV $2.36M; modeled win probability 78% (up from 52%) |

The video rounds $787,500 to $787K and shows "Net: $1.2M > $787K (-34%)"; the agent computes the list value of 2,500
seats ($1,250K) against $787.5K (37% effective discount) and the ARR change against the current $1.0M (-21%).
Approvals are listed as requests to route, never as granted, and the proposal is never sent by the agent.
## Data-use boundary

Every identifier, company, person, date, count, price, amount, score, percentage, probability, benchmark, signal, claim, and projection above is synthetic. No outreach may be sent; no CRM, forecast, owner, task, alert, workflow, meeting, proposal, approval, pricing, subscription, renewal, product entitlement, or customer communication may be created, changed, activated, or delivered from this evidence.
