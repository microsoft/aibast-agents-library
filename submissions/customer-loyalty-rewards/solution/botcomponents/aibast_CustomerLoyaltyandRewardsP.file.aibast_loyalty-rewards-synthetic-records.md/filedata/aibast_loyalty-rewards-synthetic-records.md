# Customer Loyalty and Rewards — Complete Synthetic Records

> **SYNTHETIC, READ-ONLY PILOT DATA.** Every identifier, name, date, status,
> quantity, amount, preference, interaction, order, cart, case, campaign, and
> metric below is fictional. It is reference evidence, not a live-system value
> or authorization to take action.

## Authoritative provenance

- Deterministic source: `agents/@aibast-agents-library/b2c_sales_stacks/customer_loyalty_rewards_stack/customer_loyalty_rewards_agent.py`
- Locked case contract: `tests/demo_cases/customer-loyalty-rewards.json`
- Captured evidence: `solutions/customer-loyalty-rewards/evals/transcripts.json`
- The JSON blocks below are exact literals copied from the deterministic source.
- Preserve identifiers, spelling, capitalization, dates, statuses, and numeric values.
- If production data differs, stop and verify in the authorized system of record.

## Locked-case source selections

| Case | Persona | Operation | Exact arguments |
|---|---|---|---|
| `CLR-01` | Loyalty Program Director | `loyalty_dashboard` | `{}` |
| `CLR-02` | CRM Manager | `points_summary` | `{"member_id":"LM-10002"}` |
| `CLR-03` | Marketing Leader | `reward_recommendations` | `{}` |
| `CLR-04` | Loyalty Program Director | `tier_analysis` | `{}` |
| `CLR-05` | Marketing Leader | `churn_risk_segments` | `{}` |
| `CLR-06` | Marketing Leader | `top_at_risk_members` | `{}` |
| `CLR-07` | Marketing Leader | `winback_offers` | `{}` |
| `CLR-08` | Marketing Leader | `campaign_plan` | `{}` |
| `CLR-09` | Marketing Leader | `program_improvements` | `{}` |
| `CLR-10` | Marketing Leader | `campaign_summary` | `{}` |

## Complete deterministic record sets

### `LOYALTY_MEMBERS`

```json
{
  "LM-10001": {
    "name": "Synthetic Platinum Member",
    "tier": "platinum",
    "points_balance": 48250,
    "points_earned_ytd": 12400,
    "points_redeemed_ytd": 8000,
    "member_since": "2018-03-15",
    "total_spend_ytd": 6200,
    "engagement_score": 92,
    "preferred_rewards": [
      "travel",
      "dining"
    ]
  },
  "LM-10002": {
    "name": "Synthetic Gold Member",
    "tier": "gold",
    "points_balance": 22100,
    "points_earned_ytd": 6800,
    "points_redeemed_ytd": 2500,
    "member_since": "2020-08-22",
    "total_spend_ytd": 3400,
    "engagement_score": 75,
    "preferred_rewards": [
      "merchandise",
      "gift_cards"
    ]
  },
  "LM-10003": {
    "name": "Synthetic Silver Member",
    "tier": "silver",
    "points_balance": 8450,
    "points_earned_ytd": 3200,
    "points_redeemed_ytd": 0,
    "member_since": "2023-01-10",
    "total_spend_ytd": 1600,
    "engagement_score": 58,
    "preferred_rewards": [
      "discounts"
    ]
  },
  "LM-10004": {
    "name": "Synthetic Bronze Member",
    "tier": "bronze",
    "points_balance": 2100,
    "points_earned_ytd": 900,
    "points_redeemed_ytd": 0,
    "member_since": "2024-06-05",
    "total_spend_ytd": 450,
    "engagement_score": 32,
    "preferred_rewards": [
      "discounts",
      "free_shipping"
    ]
  }
}
```

### `TIER_STRUCTURE`

```json
{
  "bronze": {
    "min_spend": 0,
    "points_multiplier": 1.0,
    "perks": [
      "Birthday bonus points",
      "Member-only sales access"
    ],
    "next_tier": "silver",
    "spend_to_next": 1000
  },
  "silver": {
    "min_spend": 1000,
    "points_multiplier": 1.25,
    "perks": [
      "Bronze perks",
      "Free standard shipping",
      "Early access to new products"
    ],
    "next_tier": "gold",
    "spend_to_next": 3000
  },
  "gold": {
    "min_spend": 3000,
    "points_multiplier": 1.5,
    "perks": [
      "Silver perks",
      "Free express shipping",
      "Exclusive gold events",
      "Annual gift"
    ],
    "next_tier": "platinum",
    "spend_to_next": 6000
  },
  "platinum": {
    "min_spend": 6000,
    "points_multiplier": 2.0,
    "perks": [
      "Gold perks",
      "Personal shopping advisor",
      "Free returns",
      "VIP lounge access",
      "Quarterly bonus"
    ],
    "next_tier": null,
    "spend_to_next": 0
  }
}
```

### `REDEMPTION_CATALOG`

```json
{
  "travel_voucher_500": {
    "name": "$500 Travel Voucher",
    "points_cost": 25000,
    "category": "travel",
    "value": 500
  },
  "dining_card_100": {
    "name": "$100 Dining Gift Card",
    "points_cost": 5000,
    "category": "dining",
    "value": 100
  },
  "merch_headphones": {
    "name": "Premium Wireless Headphones",
    "points_cost": 15000,
    "category": "merchandise",
    "value": 249
  },
  "gift_card_50": {
    "name": "$50 Store Gift Card",
    "points_cost": 2500,
    "category": "gift_cards",
    "value": 50
  },
  "discount_20pct": {
    "name": "20% Off Next Purchase",
    "points_cost": 3000,
    "category": "discounts",
    "value": 0
  },
  "free_shipping_3mo": {
    "name": "Free Shipping for 3 Months",
    "points_cost": 1500,
    "category": "free_shipping",
    "value": 30
  }
}
```

### `ENGAGEMENT_ACTIVITIES`

```json
[
  {
    "activity": "Purchase",
    "points": "2 per $1 spent",
    "frequency": "per_transaction"
  },
  {
    "activity": "Product Review",
    "points": "100 bonus",
    "frequency": "per_review"
  },
  {
    "activity": "Referral Signup",
    "points": "500 bonus",
    "frequency": "per_referral"
  },
  {
    "activity": "Birthday",
    "points": "Double points for birthday month",
    "frequency": "annual"
  },
  {
    "activity": "Social Share",
    "points": "50 bonus",
    "frequency": "per_share"
  },
  {
    "activity": "App Download",
    "points": "250 one-time bonus",
    "frequency": "once"
  }
]
```

### `PROGRAM_SEGMENTS`

```json
[
  {
    "segment": "Engaged",
    "members": 124000,
    "churn_risk_pct": 5
  },
  {
    "segment": "Active",
    "members": 198000,
    "churn_risk_pct": 12
  },
  {
    "segment": "At-risk",
    "members": 34000,
    "churn_risk_pct": 68
  },
  {
    "segment": "Dormant",
    "members": 94000,
    "churn_risk_pct": 89
  }
]
```

### `AT_RISK_SUMMARY`

```json
{
  "rule": "60+ days no purchase",
  "unredeemed_points": 108000000,
  "points_expiring_30_days": 42000000,
  "patterns": [
    "High balances + no redemption",
    "Sudden disengagement",
    "Browse-no-buy"
  ]
}
```

### `AT_RISK_MEMBERS`

```json
{
  "LM-20001": {
    "name": "Linda M.",
    "tier": "Gold",
    "points_balance": 12400,
    "days_since_purchase": 72,
    "annual_value": 21000,
    "interests": "designer accessories",
    "points_expiring": 8000,
    "expiring_in_days": 21,
    "behavior": "waits for sales",
    "trigger": "Her favorite brand just went on sale - she doesn't know yet",
    "offer": "\"Your favorite bags are 40% off\" + double points + \"8K points expire in 21 days\""
  },
  "LM-20002": {
    "name": "Kevin R.",
    "tier": "Gold",
    "points_balance": 8900,
    "days_since_purchase": 65,
    "annual_value": 15000,
    "interests": "outdoor gear",
    "points_expiring": 3000,
    "expiring_in_days": 30,
    "behavior": "browses new arrivals without buying",
    "trigger": "Three viewed items are back in stock",
    "offer": "\"Your saved items are back\" + 20% off + free shipping"
  },
  "LM-20003": {
    "name": "Sarah T.",
    "tier": "Silver",
    "points_balance": 7200,
    "days_since_purchase": 81,
    "annual_value": 12000,
    "interests": "home decor",
    "points_expiring": 2500,
    "expiring_in_days": 28,
    "behavior": "high balance, never redeemed",
    "trigger": "Her balance now covers a $100 home reward",
    "offer": "\"Don't lose $50\" + 25% bonus points if redeemed this week"
  }
}
```

### `WINBACK_SEGMENTS`

```json
[
  {
    "segment": "High-Value",
    "campaign": "High-value win-back",
    "members": 8400,
    "offer": "VIP early access + 3X points for 14 days",
    "channel": "Email + app push"
  },
  {
    "segment": "Point Expiry",
    "campaign": "Point expiry alert",
    "members": 12000,
    "offer": "\"Don't lose $X\" + 25% bonus if redeemed this week",
    "channel": "SMS + email"
  },
  {
    "segment": "Lapsed Browsers",
    "campaign": "Lapsed browser",
    "members": 13600,
    "offer": "Items they viewed + 20% off + free shipping",
    "channel": "Email + retargeting"
  }
]
```

### `CAMPAIGN_PROJECTION`

```json
{
  "window_days": 14,
  "reengagement_pct": 24,
  "avg_order_value": 60,
  "points_redeemed": 32000000,
  "ltv_protected": 1400000,
  "campaign_cost": 8400
}
```

### `PROGRAM_IMPROVEMENTS`

```json
[
  {
    "improvement": "Dynamic point expiry",
    "impact": "+$340K/yr",
    "priority": "High"
  },
  {
    "improvement": "Tier advancement alerts",
    "impact": "+18% engagement",
    "priority": "High"
  },
  {
    "improvement": "Personalized rewards",
    "impact": "+24% redemption",
    "priority": "High"
  },
  {
    "improvement": "Expiry reminder cadence (30/14/7 days)",
    "impact": "+12% redemption",
    "priority": "High"
  }
]
```

### Program text constants and computed figures

- `QUICK_WIN`: Tier alerts this week ("You're 200 points from Gold!") - low effort, +18% near-tier purchases
- `DYNAMIC_EXPIRY`: Rolling expiry with activity extension -> 40% dormancy reduction
- `NEXT_STEPS`: Monitor daily, implement tier alerts this week, plan personalized rewards pilot
- Program members: 124,000 + 198,000 + 34,000 + 94,000 = 450,000 (450K members); 34,000 at risk.
- At-risk unredeemed points: 108M points at $0.02 = $2,160,000, shown rounded down as $2.1M; 42M points
  expiring in 30 days = $840K expiring in 30 days.
- Top at-risk members: Linda M. ($21,000) + Kevin R. ($15,000) + Sarah T. ($12,000) = $48K annual value.
  Linda M. profile: Gold status, designer accessories, 8K points expiring in 21 days, waits for sales; trigger:
  her favorite brand just went on sale. Her offer: "Your favorite bags are 40% off" + double points +
  "8K points expire in 21 days".
- Win-back segments: High-Value 8,400 + Point Expiry 12,000 + Lapsed Browsers 13,600 = 34,000 members.
- Campaign projection (14 days): 34,000 x 24% = 8,160 re-engaged x $60 average order = $489,600 revenue
  ($489K); 32M points redeemed x $0.02 = $640K liability reduced; $1.4M LTV protected; campaign cost $8,400;
  ROI 489,600 / 8,400 = 58:1. Every campaign status is "Ready to launch (your approval)".
- Session summary: Members analyzed 450K; At-risk identified 34K ($2.1M points); Campaigns ready to launch
  3 segments (34K members); Expected revenue $489,600; LTV protected $1.4M; ROI 58:1.

## Record-use boundary

Never identify or contact a real member; enroll a member; add, subtract, expire, transfer, or redeem points; change a tier; create an offer; issue a reward; refund funds; create an order; or complete a purchase.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
