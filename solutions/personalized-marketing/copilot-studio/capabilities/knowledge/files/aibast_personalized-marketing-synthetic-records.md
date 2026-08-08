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
| `PM-02` | Campaign Manager | `campaign_design` | `{"campaign_id":"CAMP-WINBACK"}` |
| `PM-03` | Campaign Manager | `content_personalization` | `{"segment_id":"SEG-NEW"}` |
| `PM-04` | Marketing Director | `performance_analysis` | `{}` |

## Complete deterministic record sets

### `CUSTOMER_SEGMENTS`

```json
{
  "SEG-LOYAL": {
    "name": "Loyal Advocates",
    "size": 42850,
    "avg_annual_spend": 1875.0,
    "avg_orders_per_year": 18.3,
    "avg_basket_size": 102.46,
    "preferred_channels": [
      "in_store",
      "mobile_app"
    ],
    "top_categories": [
      "Apparel",
      "Footwear",
      "Accessories"
    ],
    "churn_risk": 0.04,
    "lifetime_value": 11250.0,
    "engagement_score": 92
  },
  "SEG-ATRISK": {
    "name": "At-Risk Churners",
    "size": 18420,
    "avg_annual_spend": 620.0,
    "avg_orders_per_year": 5.1,
    "avg_basket_size": 121.57,
    "preferred_channels": [
      "email",
      "desktop_web"
    ],
    "top_categories": [
      "Electronics",
      "Home"
    ],
    "churn_risk": 0.38,
    "lifetime_value": 3720.0,
    "engagement_score": 31
  },
  "SEG-NEW": {
    "name": "New Explorers",
    "size": 27600,
    "avg_annual_spend": 340.0,
    "avg_orders_per_year": 3.8,
    "avg_basket_size": 89.47,
    "preferred_channels": [
      "social_media",
      "mobile_app"
    ],
    "top_categories": [
      "Apparel",
      "Beauty",
      "Accessories"
    ],
    "churn_risk": 0.22,
    "lifetime_value": 2040.0,
    "engagement_score": 58
  },
  "SEG-HIGHVAL": {
    "name": "High-Engagement Members",
    "size": 8750,
    "avg_annual_spend": 4200.0,
    "avg_orders_per_year": 24.6,
    "avg_basket_size": 170.73,
    "preferred_channels": [
      "in_store",
      "mobile_app",
      "email"
    ],
    "top_categories": [
      "Premium Apparel",
      "Footwear",
      "Jewelry"
    ],
    "churn_risk": 0.06,
    "lifetime_value": 33600.0,
    "engagement_score": 97
  },
  "SEG-DORMANT": {
    "name": "Dormant Lapsed",
    "size": 34200,
    "avg_annual_spend": 85.0,
    "avg_orders_per_year": 0.8,
    "avg_basket_size": 106.25,
    "preferred_channels": [
      "email"
    ],
    "top_categories": [
      "Home",
      "Electronics"
    ],
    "churn_risk": 0.72,
    "lifetime_value": 510.0,
    "engagement_score": 9
  }
}
```

### `CAMPAIGN_TEMPLATES`

```json
{
  "CAMP-WINBACK": {
    "name": "Win-Back Journey",
    "type": "automated_email",
    "target_segment": "SEG-DORMANT",
    "stages": 4,
    "duration_days": 28,
    "offer_concept": "Optional incentive concept, subject to policy and approval",
    "subject_lines": [
      "Draft A: Reconnect with recent category interests",
      "Draft B: Explore what is new",
      "Draft C: Optional value reminder",
      "Draft D: Close the sequence respectfully"
    ],
    "historical_open_rate": 0.18,
    "historical_click_rate": 0.04,
    "historical_conversion_rate": 0.012
  },
  "CAMP-LOYALTY": {
    "name": "Loyalty Tier Upgrade",
    "type": "multi_channel",
    "target_segment": "SEG-LOYAL",
    "stages": 3,
    "duration_days": 14,
    "offer_concept": "Early-access concept; no benefit is issued",
    "subject_lines": [
      "Draft A: Review progress toward the next tier",
      "Draft B: Explain an optional approved benefit",
      "Draft C: Acknowledge a verified tier change"
    ],
    "historical_open_rate": 0.42,
    "historical_click_rate": 0.15,
    "historical_conversion_rate": 0.08
  },
  "CAMP-NEWWELCOME": {
    "name": "New Customer Welcome",
    "type": "automated_email",
    "target_segment": "SEG-NEW",
    "stages": 5,
    "duration_days": 30,
    "offer_concept": "Welcome-value concept, subject to policy and approval",
    "subject_lines": [
      "Draft A: Welcome and explain available categories",
      "Draft B: Introduce popular products",
      "Draft C: Offer optional curated ideas",
      "Draft D: Invite the shopper to set preferences",
      "Draft E: Explain the rewards program without enrollment"
    ],
    "historical_open_rate": 0.35,
    "historical_click_rate": 0.11,
    "historical_conversion_rate": 0.055
  },
  "CAMP-VIP": {
    "name": "VIP Exclusive Preview",
    "type": "multi_channel",
    "target_segment": "SEG-HIGHVAL",
    "stages": 2,
    "duration_days": 7,
    "offer_concept": "Private-preview concept; no access or discount is granted",
    "subject_lines": [
      "Draft A: Preview a collection for an eligible aggregate audience",
      "Draft B: Close the preview sequence without urgency pressure"
    ],
    "historical_open_rate": 0.58,
    "historical_click_rate": 0.24,
    "historical_conversion_rate": 0.14
  }
}
```

### `AB_TEST_RESULTS`

```json
{
  "ABT-001": {
    "campaign": "CAMP-WINBACK",
    "variant_a": {
      "subject": "We miss you \u2014 here is 20% off",
      "open_rate": 0.18,
      "click_rate": 0.04,
      "conversions": 82
    },
    "variant_b": {
      "subject": "Come back for something special",
      "open_rate": 0.21,
      "click_rate": 0.05,
      "conversions": 107
    },
    "winner": "B",
    "confidence": 0.94,
    "sample_size": 8500
  },
  "ABT-002": {
    "campaign": "CAMP-LOYALTY",
    "variant_a": {
      "subject": "You are almost Gold status!",
      "open_rate": 0.42,
      "click_rate": 0.15,
      "conversions": 341
    },
    "variant_b": {
      "subject": "Unlock Gold rewards today",
      "open_rate": 0.39,
      "click_rate": 0.13,
      "conversions": 298
    },
    "winner": "A",
    "confidence": 0.91,
    "sample_size": 6200
  },
  "ABT-003": {
    "campaign": "CAMP-VIP",
    "variant_a": {
      "subject": "VIP Only: private sale starts now",
      "open_rate": 0.58,
      "click_rate": 0.24,
      "conversions": 215
    },
    "variant_b": {
      "subject": "Your private collection awaits",
      "open_rate": 0.61,
      "click_rate": 0.27,
      "conversions": 248
    },
    "winner": "B",
    "confidence": 0.88,
    "sample_size": 3400
  }
}
```

### `CONTENT_BLOCKS`

```json
{
  "hero_banner": {
    "SEG-LOYAL": {
      "headline": "Thank You for Being a Loyal Customer",
      "cta": "Shop Your Rewards"
    },
    "SEG-ATRISK": {
      "headline": "We Have Something Special for You",
      "cta": "Rediscover Your Favorites"
    },
    "SEG-NEW": {
      "headline": "Welcome to the Family",
      "cta": "Start Shopping"
    },
    "SEG-HIGHVAL": {
      "headline": "Exclusive Access Just for You",
      "cta": "View Private Collection"
    },
    "SEG-DORMANT": {
      "headline": "It Has Been a While \u2014 Come Back",
      "cta": "See What Is New"
    }
  },
  "product_recs": {
    "SEG-LOYAL": [
      "Classic Denim Jacket",
      "Premium Running Shoes",
      "Leather Crossbody Bag"
    ],
    "SEG-ATRISK": [
      "Wireless Earbuds Pro",
      "Smart Fitness Tracker"
    ],
    "SEG-NEW": [
      "Organic Cotton T-Shirt",
      "Stainless Water Bottle",
      "UV Protection Sunglasses"
    ],
    "SEG-HIGHVAL": [
      "Limited Edition Blazer",
      "Designer Handbag",
      "Artisan Watch"
    ],
    "SEG-DORMANT": [
      "Best Sellers Bundle",
      "Gift Card"
    ]
  }
}
```

## Record-use boundary

Never identify or sensitively profile a person; send or schedule outreach; create, apply, or promise an offer; enroll a member; issue a reward; alter a cart; or complete a purchase.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
