# Personalized Marketing — Complete Synthetic Records

> **SYNTHETIC, READ-ONLY PILOT DATA.** Every identifier, name, date, status,
> quantity, amount, preference, interaction, order, cart, case, campaign, and
> metric below is fictional. It is reference evidence, not a live-system value
> or authorization to take action.

## Authoritative provenance

- Deterministic source: `agents/@aibast-agents-library/retail_cpg_stacks/personalized_marketing_stack/personalized_marketing_agent.py`
- Locked case contract: `tests/demo_cases/personalized-marketing.json`
- Captured evidence: `solutions/personalized-marketing/evals/transcripts.json`
- The JSON blocks below are exact literals copied from the deterministic source.
- Preserve identifiers, spelling, capitalization, dates, statuses, and numeric values.
- If production data differs, stop and verify in the authorized system of record.

## Locked-case source selections

| Case | Persona | Operation | Exact arguments |
|---|---|---|---|
| `PM-01` | Marketing Director | `customer_segmentation` | `{}` |
| `PM-02` | Campaign Manager | `campaign_design` | `{}` |
| `PM-03` | Campaign Manager | `content_personalization` | `{"segment_id":"SEG-VIP"}` |
| `PM-04` | Marketing Director | `performance_analysis` | `{}` |
| `PM-05` | Campaign Manager | `campaign_workflow` | `{}` |
| `PM-06` | Marketing Director | `revenue_projection` | `{}` |
| `PM-07` | Marketing Director | `executive_brief` | `{}` |

## Demo scenario: holiday email promotion

- 240,000 active customers in five aggregate segments: VIP Shoppers 12,400 ($340 avg order, 68% open, 12.4%
  conversion); Frequent Buyers 38,200 ($185, 52%, 9.6%); Seasonal Shoppers 67,800 ($210, 44%, 7.2%); Lapsed
  Customers 84,300 ($165, 28%, 3.1%); New Subscribers 37,300 ($0, 71%, 15.8%). Holiday potential totals $8.4M.
  Highest ROI: VIP Shoppers; fastest growth: New Subscribers. Recommended strategy: multi-wave, VIPs first.
- Waves (proposed offers, not issued): Wave 1 VIP (Launch Day) "Early Access - 30% Off Everything" $1.42M;
  Wave 2 Frequent Buyers (Day 2) "Your Favorites Are On Sale" $2.17M; Wave 3 Seasonal (Day 5) "Holiday Gifts -
  Free Shipping" $1.98M; Wave 4 New Subscribers (Day 7) "Welcome Gift - 40% Off First Purchase" $1.24M; Wave 5
  Lapsed (Day 10) "We Saved You a Gift - Free Shipping" $1.31M. Total $8.12M from a $47K investment (ROI 173:1).
- VIP creative: Variant A Product Focus (Shop My Picks), Variant B Urgency Focus (Activate My VIP Access),
  Variant C Rewards Focus (Claim VIP Rewards); split 33% / 33% / 34%, 12 hours, winner by open rate + revenue.
- Draft launch: Tomorrow 8:00 AM PST, 12,400 VIPs, winner at 8:00 PM; workflow Hour 0 send, Hour 12 winner,
  Hour 24 browse abandonment, Hour 48 cart abandonment (10% additional discount), Hour 72 final call. Nothing is
  scheduled or sent until approved.
- VIP revenue scenarios: Conservative 68% / 24% / 12.4%, $340 avg order, $1.42M; Expected 72% / 28% / 14.2%,
  $380, $1.78M; Optimistic 78% / 32% / 16.8%, $420, $2.11M; ROI Range 30:1 to 45:1 on $47K. Opens, clicks and
  launch-email orders are computed from 12,400 VIPs and the rates (8,432 / 2,024 / 251 in the baseline).

## Complete deterministic record sets

### `CUSTOMER_SEGMENTS`

```json
{
  "SEG-VIP": {
    "name": "VIP Shoppers",
    "short": "VIPs",
    "size": 12400,
    "avg_order": 340,
    "open_rate": 68,
    "conversion_rate": 12.4,
    "holiday_potential": 1480000,
    "top_categories": [
      "Premium Apparel",
      "Footwear",
      "Accessories"
    ]
  },
  "SEG-FREQUENT": {
    "name": "Frequent Buyers",
    "short": "frequent buyers",
    "size": 38200,
    "avg_order": 185,
    "open_rate": 52,
    "conversion_rate": 9.6,
    "holiday_potential": 2260000,
    "top_categories": [
      "Apparel",
      "Home",
      "Beauty"
    ]
  },
  "SEG-SEASONAL": {
    "name": "Seasonal Shoppers",
    "short": "seasonal shoppers",
    "size": 67800,
    "avg_order": 210,
    "open_rate": 44,
    "conversion_rate": 7.2,
    "holiday_potential": 2060000,
    "top_categories": [
      "Gifts",
      "Toys",
      "Electronics"
    ]
  },
  "SEG-LAPSED": {
    "name": "Lapsed Customers",
    "short": "lapsed customers",
    "size": 84300,
    "avg_order": 165,
    "open_rate": 28,
    "conversion_rate": 3.1,
    "holiday_potential": 1320000,
    "top_categories": [
      "Home",
      "Electronics"
    ]
  },
  "SEG-NEW": {
    "name": "New Subscribers",
    "short": "new subscribers",
    "size": 37300,
    "avg_order": 0,
    "open_rate": 71,
    "conversion_rate": 15.8,
    "holiday_potential": 1280000,
    "top_categories": [
      "Apparel",
      "Beauty",
      "Accessories"
    ]
  }
}
```

### `HOLIDAY_WAVES`

```json
{
  "WAVE-1": {
    "segment": "SEG-VIP",
    "day": 0,
    "day_label": "Launch Day",
    "theme": "Early Access - 30% Off Everything",
    "personalization": "Past purchase categories featured",
    "expected_revenue": 1420000
  },
  "WAVE-2": {
    "segment": "SEG-FREQUENT",
    "day": 2,
    "day_label": "Day 2",
    "theme": "Your Favorites Are On Sale",
    "personalization": "AI-recommended products based on browsing",
    "expected_revenue": 2170000
  },
  "WAVE-3": {
    "segment": "SEG-SEASONAL",
    "day": 5,
    "day_label": "Day 5",
    "theme": "Holiday Gifts - Free Shipping",
    "personalization": "Gift guides by top category",
    "expected_revenue": 1980000
  },
  "WAVE-4": {
    "segment": "SEG-NEW",
    "day": 7,
    "day_label": "Day 7",
    "theme": "Welcome Gift - 40% Off First Purchase",
    "personalization": "Signup-preference categories",
    "expected_revenue": 1240000
  },
  "WAVE-5": {
    "segment": "SEG-LAPSED",
    "day": 10,
    "day_label": "Day 10",
    "theme": "We Saved You a Gift - Free Shipping",
    "personalization": "Last purchased category",
    "expected_revenue": 1310000
  }
}
```

### `CAMPAIGN_ECONOMICS`

```json
{
  "campaign": "Holiday Promotion",
  "investment": 47000,
  "investment_note": "creative + platform + labor",
  "personalization_lift_pct": 15.8
}
```

### `VIP_VARIANTS`

```json
{
  "A": {
    "focus": "Product Focus",
    "hero_image": "Best-selling items from the customer's purchase history",
    "subject_line": "{FirstName}, Your Favorites Are 30% Off (VIP Early Access)",
    "cta": "Shop My Picks"
  },
  "B": {
    "focus": "Urgency Focus",
    "hero_image": "Countdown timer + exclusive badge",
    "subject_line": "24-Hour VIP Access Starts Now - 30% Off",
    "cta": "Activate My VIP Access"
  },
  "C": {
    "focus": "Rewards Focus",
    "hero_image": "Double points badge + tier benefits",
    "subject_line": "Earn 3X Points + 30% Off (VIP Exclusive)",
    "cta": "Claim VIP Rewards"
  }
}
```

### `AB_TEST_SETUP`

```json
{
  "campaign_name": "Early Access VIP - 30% Off Everything",
  "split": [
    33,
    33,
    34
  ],
  "duration_hours": 12,
  "winner_metric": "open rate + revenue",
  "sample_first_name": "Sarah"
}
```

### `AUTOMATION_WORKFLOW`

```json
{
  "launch_label": "Tomorrow",
  "launch_hour": 8,
  "timezone": "PST",
  "follow_up_hours": 48,
  "steps": [
    {
      "hour": 0,
      "step": "Initial send with variant testing"
    },
    {
      "hour": 12,
      "step": "Winner declared, send winning variant to remaining audience"
    },
    {
      "hour": 24,
      "step": "Browse abandonment email (personalized products)"
    },
    {
      "hour": 48,
      "step": "Cart abandonment email (10% additional discount)"
    },
    {
      "hour": 72,
      "step": "Final call email (last chance messaging)"
    }
  ],
  "tracking": [
    "Real-time dashboard monitoring open/click/revenue",
    "Milestone alerts to the campaign channel",
    "Optimization recommendations based on early performance"
  ]
}
```

### `REVENUE_SCENARIOS`

```json
[
  {
    "name": "Conservative (Baseline)",
    "open_rate": 68,
    "click_rate": 24,
    "conversion_rate": 12.4,
    "avg_order": 340,
    "avg_order_note": "",
    "revenue": 1420000
  },
  {
    "name": "Expected (Hit Benchmarks)",
    "open_rate": 72,
    "click_rate": 28,
    "conversion_rate": 14.2,
    "avg_order": 380,
    "avg_order_note": " (upsell success)",
    "revenue": 1780000
  },
  {
    "name": "Optimistic (Beat Benchmarks)",
    "open_rate": 78,
    "click_rate": 32,
    "conversion_rate": 16.8,
    "avg_order": 420,
    "avg_order_note": " (premium mix)",
    "revenue": 2110000
  }
]
```

### `AB_TEST_RESULTS`

```json
{
  "ABT-001": {
    "campaign": "Last year's VIP early access",
    "variant_a": {
      "subject": "VIP Only: private sale starts now",
      "open_rate": 0.58,
      "click_rate": 0.24,
      "conversions": 215
    },
    "variant_b": {
      "subject": "Your favorites, VIP early access",
      "open_rate": 0.64,
      "click_rate": 0.27,
      "conversions": 248
    },
    "winner": "B",
    "confidence": 0.94,
    "sample_size": 11800
  },
  "ABT-002": {
    "campaign": "Last year's frequent-buyer sale",
    "variant_a": {
      "subject": "Your favorites are on sale",
      "open_rate": 0.49,
      "click_rate": 0.15,
      "conversions": 341
    },
    "variant_b": {
      "subject": "Holiday deals picked for you",
      "open_rate": 0.46,
      "click_rate": 0.13,
      "conversions": 298
    },
    "winner": "A",
    "confidence": 0.91,
    "sample_size": 36000
  },
  "ABT-003": {
    "campaign": "Generic vs personalized holiday email",
    "variant_a": {
      "subject": "Holiday sale: shop now",
      "open_rate": 0.31,
      "click_rate": 0.08,
      "conversions": 190
    },
    "variant_b": {
      "subject": "Gifts picked from your favorite categories",
      "open_rate": 0.36,
      "click_rate": 0.1,
      "conversions": 220
    },
    "winner": "B",
    "confidence": 0.88,
    "sample_size": 24000
  }
}
```

### `CONTENT_BLOCKS`

```json
{
  "hero_banner": {
    "SEG-VIP": {
      "headline": "VIP Early Access - 30% Off Everything",
      "cta": "Shop My Picks"
    },
    "SEG-FREQUENT": {
      "headline": "Your Favorites Are On Sale",
      "cta": "See My Favorites"
    },
    "SEG-SEASONAL": {
      "headline": "Holiday Gifts - Free Shipping",
      "cta": "Shop Gift Guides"
    },
    "SEG-LAPSED": {
      "headline": "We Saved You a Gift",
      "cta": "See What Is New"
    },
    "SEG-NEW": {
      "headline": "Welcome Gift - 40% Off First Purchase",
      "cta": "Start Shopping"
    }
  },
  "product_recs": {
    "SEG-VIP": [
      "Limited Edition Blazer",
      "Designer Handbag",
      "Artisan Watch"
    ],
    "SEG-FREQUENT": [
      "Classic Denim Jacket",
      "Premium Running Shoes",
      "Cozy Throw Blanket"
    ],
    "SEG-SEASONAL": [
      "Holiday Gift Set",
      "Wireless Earbuds Pro",
      "Board Game Bundle"
    ],
    "SEG-LAPSED": [
      "Best Sellers Bundle",
      "Gift Card"
    ],
    "SEG-NEW": [
      "Organic Cotton T-Shirt",
      "Stainless Water Bottle",
      "UV Protection Sunglasses"
    ]
  }
}
```

## Record-use boundary

Never identify or sensitively profile a person; send or schedule outreach; create, apply, or promise an offer; enroll a member; issue a reward; alter a cart; or complete a purchase.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
