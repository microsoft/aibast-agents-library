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

## Record-use boundary

Never identify or contact a real member; enroll a member; add, subtract, expire, transfer, or redeem points; change a tier; create an offer; issue a reward; refund funds; create an order; or complete a purchase.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
