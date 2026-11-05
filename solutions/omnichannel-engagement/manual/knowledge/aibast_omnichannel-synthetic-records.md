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

## Demo scenario (aligned with the product video)

A national apparel retailer's contact center picks up one customer's journey (default customer `CUST-SM-001`,
Sarah Mitchell, Gold tier, $2,400 LTV; consented service record only):

1. Journey across 5 channels: 3 days ago mobile app checkout started / payment declined; 2 days ago chat sizing
   question / disconnected; yesterday email cart reminder / no action; today phone support call / currently holding.
   30-day preferences: mobile app 12 (primary), website 8 (secondary), chat 3 (frustrated). $289 cart (Alpine Parka),
   3 days old.
2. Unresolved: "Does Alpine Parka run true to size?" (disconnected) and "Do you have it in navy?" (never answered);
   sizing and color unanswered, payment card declined; 18 minutes trying to buy; draft opening line; ready answers:
   runs one size small, navy in stock S-XL.
3. Channel strategy: mobile push 82% open, SMS 76% response, email 34% open, chat avoid; now phone -> SMS confirmation;
   future SMS order updates, mobile push promotions at 10 AM, phone callback for service; peak engagement 7-9 PM.
4. Proactive plan (drafts): after purchase, upcoming offers, win-back sequence (hour 1, hour 4, day 2, day 5).
5. Handoff package: quick context, transfer context, script, attach CRM note, cart link, conversation summary.

## Locked-case source selections

| Case | Persona | Operation | Exact arguments |
|---|---|---|---|
| `OCE-01` | Customer Experience Leader | `channel_performance` | `{}` |
| `OCE-02` | Contact Center Supervisor | `journey_analysis` | `{}` |
| `OCE-03` | Digital Engagement Manager | `engagement_optimization` | `{}` |
| `OCE-04` | Digital Engagement Manager | `campaign_attribution` | `{}` |
| `OCE-05` | Contact Center Supervisor | `customer_journey` | `{}` |
| `OCE-06` | Contact Center Supervisor | `unresolved_issues` | `{}` |
| `OCE-07` | Digital Engagement Manager | `channel_recommendation` | `{}` |
| `OCE-08` | Digital Engagement Manager | `proactive_plan` | `{}` |
| `OCE-09` | Customer Experience Leader | `handoff_package` | `{}` |

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

### `CUSTOMERS`

```json
{
  "CUST-SM-001": {
    "name": "Sarah Mitchell",
    "tier": "Gold",
    "lifetime_value": 2400,
    "cart": {
      "item": "Alpine Parka",
      "value": 289,
      "age_days": 3
    },
    "timeline": [
      {
        "day": "3 days ago",
        "channel": "Mobile app",
        "action": "Checkout started",
        "issue": "Payment declined"
      },
      {
        "day": "2 days ago",
        "channel": "Chat",
        "action": "Sizing question",
        "issue": "Disconnected"
      },
      {
        "day": "Yesterday",
        "channel": "Email",
        "action": "Cart reminder",
        "issue": "No action"
      },
      {
        "day": "Today",
        "channel": "Phone",
        "action": "Support call",
        "issue": "Currently holding"
      }
    ],
    "channel_counts_30d": [
      {
        "channel": "Mobile app",
        "interactions": 12,
        "note": "primary"
      },
      {
        "channel": "Website",
        "interactions": 8,
        "note": "secondary"
      },
      {
        "channel": "Chat",
        "interactions": 3,
        "note": "frustrated"
      }
    ],
    "chat_questions": [
      {
        "question": "Does Alpine Parka run true to size?",
        "outcome": "Agent: \"Let me check...\" (disconnected)"
      },
      {
        "question": "Do you have it in navy?",
        "outcome": "Never answered"
      }
    ],
    "issues": [
      {
        "issue": "Sizing guidance",
        "status": "Unanswered",
        "impact": "Blocking purchase"
      },
      {
        "issue": "Color availability",
        "status": "Unanswered",
        "impact": "Blocking purchase"
      },
      {
        "issue": "Payment",
        "status": "Card declined",
        "impact": "Needs resolution"
      }
    ],
    "minutes_trying": 18,
    "channel_engagement": [
      {
        "channel": "Mobile push",
        "engagement": "82% open",
        "best_for": "Urgent updates"
      },
      {
        "channel": "SMS",
        "engagement": "76% response",
        "best_for": "Order status"
      },
      {
        "channel": "Email",
        "engagement": "34% open",
        "best_for": "Avoid urgency"
      },
      {
        "channel": "Chat",
        "engagement": "Frustrated",
        "best_for": "Avoid short-term"
      }
    ],
    "peak_engagement": "7-9 PM",
    "signals": "Responds to urgency, values fit guidance"
  }
}
```

### `PRODUCT_FACTS`

```json
{
  "Alpine Parka": {
    "fit": "runs one size small",
    "colors": "Navy in stock, S-XL"
  }
}
```

### `PROACTIVE_PLAN`

```json
{
  "after_purchase": [
    "Order complete: Size guide via SMS",
    "Delivery day: Styling tips via mobile push (82% engagement)",
    "7 days post: Review request in-app"
  ],
  "upcoming": [
    "3 days: Winter accessories bundle offer",
    "6 weeks: Birthday loyalty bonus",
    "8 weeks: Spring preview early access"
  ],
  "win_back": [
    "Hour 1: SMS \"Your coat is waiting\"",
    "Hour 4: Mobile push \"Low stock\"",
    "Day 2: SMS 10% off code",
    "Day 5: Personal stylist call"
  ],
  "avoid": "Email campaigns (34% open), chat offers (negative history), generic messaging"
}
```

### `HANDOFF_CONTEXT`

```json
{
  "transfer": [
    "Payments: Card decline history, alternatives",
    "Styling: Size preferences, past purchases",
    "Store pickup: Location, inventory",
    "Loyalty: Points, tier benefits"
  ],
  "script": "I'm connecting you with [Name]. I've shared your complete history - no need to repeat anything.",
  "attachments": "CRM note, cart link, conversation summary"
}
```

## Record-use boundary

Never stitch identities across devices; infer sensitive traits; contact a person; send or schedule a message; create an offer, code, or reward; transfer a customer; or complete a purchase.

Use these records only to produce drafts, explanations, comparisons, and
recommendations for human review. Do not treat a synthetic status, balance,
quantity, eligibility result, or recommendation as an executed action.
