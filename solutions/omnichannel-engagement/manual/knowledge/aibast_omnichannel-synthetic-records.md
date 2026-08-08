# Omnichannel Engagement — Complete Synthetic Records

> **SYNTHETIC, READ-ONLY PILOT DATA.** Every identifier, name, date, status,
> quantity, amount, preference, interaction, order, cart, case, campaign, and
> metric below is fictional. It is reference evidence, not a live-system value
> or authorization to take action.

## Authoritative provenance

- Deterministic source: `agents/@aibast-agents-library/b2c_sales_stacks/omnichannel_engagement_stack/omnichannel_engagement_agent.py`
- Locked case contract: `tests/demo_cases/omnichannel-engagement.json`
- Captured evidence: `solutions/omnichannel-engagement/evals/transcripts.json`
- The JSON blocks below are exact literals copied from the deterministic source.
- Preserve identifiers, spelling, capitalization, dates, statuses, and numeric values.
- If production data differs, stop and verify in the authorized system of record.

## Locked-case source selections

| Case | Persona | Operation | Exact arguments |
|---|---|---|---|
| `OCE-01` | Customer Experience Leader | `channel_performance` | `{}` |
| `OCE-02` | Contact Center Supervisor | `journey_analysis` | `{}` |
| `OCE-03` | Digital Engagement Manager | `engagement_optimization` | `{}` |
| `OCE-04` | Digital Engagement Manager | `campaign_attribution` | `{}` |

## Complete deterministic record sets

### `CHANNELS`

```json
{
  "email": {
    "sessions_30d": 145000,
    "conversions_30d": 4350,
    "revenue_30d": 870000,
    "cost_30d": 12500,
    "avg_order_value": 200.0,
    "bounce_rate": 18.5
  },
  "sms": {
    "sessions_30d": 62000,
    "conversions_30d": 1860,
    "revenue_30d": 325500,
    "cost_30d": 8200,
    "avg_order_value": 175.0,
    "bounce_rate": 5.2
  },
  "social_media": {
    "sessions_30d": 230000,
    "conversions_30d": 2760,
    "revenue_30d": 552000,
    "cost_30d": 45000,
    "avg_order_value": 200.0,
    "bounce_rate": 42.0
  },
  "web_organic": {
    "sessions_30d": 480000,
    "conversions_30d": 9600,
    "revenue_30d": 1920000,
    "cost_30d": 18000,
    "avg_order_value": 200.0,
    "bounce_rate": 35.0
  },
  "web_paid": {
    "sessions_30d": 185000,
    "conversions_30d": 5550,
    "revenue_30d": 1110000,
    "cost_30d": 95000,
    "avg_order_value": 200.0,
    "bounce_rate": 28.0
  },
  "mobile_app": {
    "sessions_30d": 310000,
    "conversions_30d": 12400,
    "revenue_30d": 2480000,
    "cost_30d": 22000,
    "avg_order_value": 200.0,
    "bounce_rate": 12.0
  },
  "in_store": {
    "sessions_30d": 95000,
    "conversions_30d": 28500,
    "revenue_30d": 5700000,
    "cost_30d": 180000,
    "avg_order_value": 200.0,
    "bounce_rate": 0
  }
}
```

### `CUSTOMER_JOURNEYS`

```json
{
  "journey_discovery": {
    "name": "Discovery to Purchase",
    "touchpoints": [
      "social_media_ad",
      "website_browse",
      "email_signup",
      "email_promo",
      "website_purchase"
    ],
    "avg_days": 14,
    "conversion_rate": 3.2,
    "avg_touchpoints": 5
  },
  "journey_repeat": {
    "name": "Repeat Purchase",
    "touchpoints": [
      "email_promo",
      "mobile_app_browse",
      "mobile_app_purchase"
    ],
    "avg_days": 3,
    "conversion_rate": 18.5,
    "avg_touchpoints": 3
  },
  "journey_winback": {
    "name": "Win-Back",
    "touchpoints": [
      "email_winback",
      "sms_offer",
      "website_browse",
      "website_purchase"
    ],
    "avg_days": 21,
    "conversion_rate": 8.4,
    "avg_touchpoints": 4
  },
  "journey_impulse": {
    "name": "Impulse Purchase",
    "touchpoints": [
      "social_media_ad",
      "website_purchase"
    ],
    "avg_days": 0,
    "conversion_rate": 1.8,
    "avg_touchpoints": 2
  }
}
```

### `CAMPAIGN_RESULTS`

```json
{
  "CAMP-301": {
    "name": "Spring Collection Launch",
    "channel": "email",
    "sent": 250000,
    "opens": 62500,
    "clicks": 18750,
    "conversions": 2250,
    "revenue": 450000,
    "cost": 5000
  },
  "CAMP-302": {
    "name": "Flash Sale \u2014 48 Hours",
    "channel": "sms",
    "sent": 120000,
    "opens": 115200,
    "clicks": 24000,
    "conversions": 3600,
    "revenue": 540000,
    "cost": 6000
  },
  "CAMP-303": {
    "name": "Influencer Partnership",
    "channel": "social_media",
    "sent": 0,
    "opens": 0,
    "clicks": 85000,
    "conversions": 1700,
    "revenue": 340000,
    "cost": 35000
  },
  "CAMP-304": {
    "name": "Google Shopping Ads",
    "channel": "web_paid",
    "sent": 0,
    "opens": 0,
    "clicks": 45000,
    "conversions": 2700,
    "revenue": 540000,
    "cost": 42000
  },
  "CAMP-305": {
    "name": "App Push \u2014 Loyalty Members",
    "channel": "mobile_app",
    "sent": 85000,
    "opens": 42500,
    "clicks": 17000,
    "conversions": 5100,
    "revenue": 765000,
    "cost": 2000
  }
}
```

## Record-use boundary

Never stitch identities; infer sensitive traits; identify or contact a person; send or schedule a message; create an offer or reward; or complete a purchase.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
