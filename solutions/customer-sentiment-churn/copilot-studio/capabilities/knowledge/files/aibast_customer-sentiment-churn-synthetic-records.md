# Customer Sentiment and Churn Prediction Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/customer_sentiment_churn_stack/customer_sentiment_churn_agent.py`
- Source SHA-256: `f1313fa0dbbe637f3031d4789da99b312bbb274616cf231e5fb1e831c2b5064d`
- Expected tool: `CustomerSentimentChurnAgent`
- Snapshot behavior: fixed to the packaged source revision; no live connection or current-data claim.

## Complete deterministic source records

The following objects reproduce every packaged identifier, name, value, amount, date, status, rule, threshold, mapping, and relationship used by the agent. Keys and values are exact.

### `CUSTOMER_INTERACTIONS`

```json
{
  "CUST-8001": {
    "annual_revenue": 12000,
    "behavior_signals": [
      "Competitor app download (Summit National Bank)",
      "Reduced logins"
    ],
    "churn_probability_pct": 84,
    "complaint_count_12m": 1,
    "deposits": 890000,
    "digital_engagement_score": 28,
    "last_survey": "2025-02-01",
    "monthly_transactions": 22,
    "name": "Robert Martinez",
    "nps_score": 4,
    "primary_signal": "competitor app",
    "products": [
      "checking",
      "savings",
      "investment"
    ],
    "recent_contact": "Asked about wire fees",
    "recent_interactions": [
      {
        "channel": "phone",
        "date": "2025-03-05",
        "sentiment": "negative",
        "type": "fee_inquiry"
      },
      {
        "channel": "survey",
        "date": "2025-02-01",
        "sentiment": "negative",
        "type": "feedback"
      }
    ],
    "segment": "affluent",
    "survey_verbatim": "Your app is years behind",
    "tenure_years": 12
  },
  "CUST-8002": {
    "annual_revenue": 5000,
    "behavior_signals": [
      "Fee disputes",
      "Repeated complaints"
    ],
    "churn_probability_pct": 64,
    "complaint_count_12m": 5,
    "deposits": 280000,
    "digital_engagement_score": 35,
    "last_survey": "2025-01-15",
    "monthly_transactions": 15,
    "name": "Marcus Johnson",
    "nps_score": 4,
    "primary_signal": "5 complaints",
    "products": [
      "checking",
      "credit_card"
    ],
    "recent_contact": "Fee dispute in chat",
    "recent_interactions": [
      {
        "channel": "phone",
        "date": "2025-03-01",
        "sentiment": "negative",
        "type": "complaint"
      },
      {
        "channel": "chat",
        "date": "2025-02-10",
        "sentiment": "negative",
        "type": "fee_dispute"
      },
      {
        "channel": "phone",
        "date": "2025-01-25",
        "sentiment": "negative",
        "type": "complaint"
      }
    ],
    "segment": "mass_market",
    "survey_verbatim": "Too many surprise fees",
    "tenure_years": 3
  },
  "CUST-8003": {
    "annual_revenue": 8000,
    "behavior_signals": [
      "Direct deposit changed",
      "Rate comparison visits"
    ],
    "churn_probability_pct": 78,
    "complaint_count_12m": 0,
    "deposits": 450000,
    "digital_engagement_score": 61,
    "last_survey": "2024-11-20",
    "monthly_transactions": 18,
    "name": "Sarah Thompson",
    "nps_score": 6,
    "primary_signal": "deposit changed",
    "products": [
      "checking",
      "savings",
      "mortgage"
    ],
    "recent_contact": "Asked about CD rates",
    "recent_interactions": [
      {
        "channel": "branch",
        "date": "2025-03-02",
        "sentiment": "neutral",
        "type": "rate_inquiry"
      },
      {
        "channel": "mobile",
        "date": "2025-02-18",
        "sentiment": "neutral",
        "type": "deposit_change"
      }
    ],
    "segment": "affluent",
    "survey_verbatim": "Savings rate is not competitive",
    "tenure_years": 9
  },
  "CUST-8004": {
    "annual_revenue": 6000,
    "behavior_signals": [
      "3 complaints in 90 days",
      "Balance decline >30%"
    ],
    "churn_probability_pct": 76,
    "complaint_count_12m": 3,
    "deposits": 340000,
    "digital_engagement_score": 44,
    "last_survey": "2025-02-25",
    "monthly_transactions": 14,
    "name": "James Lee",
    "nps_score": 3,
    "primary_signal": "3 complaints",
    "products": [
      "checking",
      "savings",
      "auto_loan"
    ],
    "recent_contact": "Third complaint about a delayed transfer",
    "recent_interactions": [
      {
        "channel": "phone",
        "date": "2025-03-08",
        "sentiment": "negative",
        "type": "complaint"
      },
      {
        "channel": "branch",
        "date": "2025-02-20",
        "sentiment": "negative",
        "type": "complaint"
      },
      {
        "channel": "chat",
        "date": "2025-01-30",
        "sentiment": "negative",
        "type": "complaint"
      }
    ],
    "segment": "emerging_affluent",
    "survey_verbatim": "Nobody follows up on my issues",
    "tenure_years": 6
  },
  "CUST-8005": {
    "annual_revenue": 4000,
    "behavior_signals": [
      "Reduced logins",
      "Competitor app download (Summit National Bank)"
    ],
    "churn_probability_pct": 62,
    "complaint_count_12m": 1,
    "deposits": 220000,
    "digital_engagement_score": 52,
    "last_survey": "2025-02-20",
    "monthly_transactions": 30,
    "name": "Priya Sharma",
    "nps_score": 7,
    "primary_signal": "reduced logins",
    "products": [
      "checking",
      "savings",
      "credit_card"
    ],
    "recent_contact": "Mobile check deposit issue",
    "recent_interactions": [
      {
        "channel": "mobile",
        "date": "2025-02-28",
        "sentiment": "neutral",
        "type": "transfer"
      },
      {
        "channel": "email",
        "date": "2025-02-05",
        "sentiment": "negative",
        "type": "inquiry"
      }
    ],
    "segment": "emerging_affluent",
    "survey_verbatim": "Mobile deposits keep failing",
    "tenure_years": 5
  }
}
```

### `CHURN_INDICATORS`

```json
{
  "declining_transactions": {
    "description": "Monthly transactions below half of the segment average",
    "threshold": 0.5,
    "weight": 20
  },
  "high_complaints": {
    "description": "3+ complaints in last 12 months",
    "threshold": 3,
    "weight": 20
  },
  "low_engagement": {
    "description": "Digital engagement score below 30",
    "threshold": 30,
    "weight": 15
  },
  "low_nps": {
    "description": "NPS score below 5 indicates detractor status",
    "threshold": 5,
    "weight": 25
  },
  "single_product": {
    "description": "Only one active product",
    "threshold": 1,
    "weight": 10
  },
  "stale_survey": {
    "description": "Last survey response over 90 days before the demo date",
    "threshold": 90,
    "weight": 10
  }
}
```

### `RETENTION_ACTIONS`

```json
{
  "complaint_resolution": {
    "cost": 50,
    "description": "Escalate to service recovery team",
    "success_rate": 65
  },
  "fee_waiver": {
    "cost": 72,
    "description": "Waive monthly maintenance fees for 6 months",
    "success_rate": 45
  },
  "loyalty_bonus": {
    "cost": 100,
    "description": "Credit loyalty bonus to account",
    "success_rate": 50
  },
  "personal_outreach": {
    "cost": 25,
    "description": "Schedule call with relationship manager",
    "success_rate": 55
  },
  "product_bundle": {
    "cost": 200,
    "description": "Offer discounted product bundle with waived fees",
    "success_rate": 60
  },
  "rate_upgrade": {
    "cost": 150,
    "description": "Offer premium savings rate for 12 months",
    "success_rate": 35
  }
}
```

### `SEGMENT_BENCHMARKS`

```json
{
  "affluent": {
    "avg_nps": 8.2,
    "avg_products": 4.1,
    "avg_tenure": 10,
    "avg_transactions": 55
  },
  "emerging_affluent": {
    "avg_nps": 7.0,
    "avg_products": 3.2,
    "avg_tenure": 5,
    "avg_transactions": 35
  },
  "mass_market": {
    "avg_nps": 6.5,
    "avg_products": 2.0,
    "avg_tenure": 4,
    "avg_transactions": 20
  },
  "small_business": {
    "avg_nps": 6.8,
    "avg_products": 3.0,
    "avg_tenure": 5,
    "avg_transactions": 90
  }
}
```

### `PORTFOLIO_SUMMARY`

```json
{
  "customers": 180000,
  "negative_drivers": [
    {
      "driver": "Digital banking",
      "mentions": 2400
    },
    {
      "driver": "Fee transparency",
      "mentions": 1800
    },
    {
      "driver": "Wait times",
      "mentions": 1200
    }
  ],
  "negative_trend_pct": 18,
  "risk_tiers": [
    {
      "annual_revenue": 2800000,
      "customers": 840,
      "tier": "Critical (>80%)"
    },
    {
      "annual_revenue": 5400000,
      "customers": 1560,
      "tier": "High (60-80%)"
    }
  ],
  "sentiment": {
    "Detractors": 27000,
    "Passives": 81000,
    "Promoters": 72000
  }
}
```

### `EARLY_WARNING`

```json
{
  "alerts_today": [
    {
      "alert": "Competitor app detected",
      "customers": 47
    },
    {
      "alert": "External transfers >$10K",
      "customers": 23
    },
    {
      "alert": "Direct deposit changed",
      "customers": 12
    }
  ],
  "combinations": [
    {
      "churn_rate_pct": 89,
      "combination": "Competitor app + balance decline"
    },
    {
      "churn_rate_pct": 82,
      "combination": "Deposit change + reduced logins"
    },
    {
      "churn_rate_pct": 67,
      "combination": "2+ complaints"
    }
  ],
  "lead_time": "30-60 days before leaving",
  "signals": [
    {
      "churn_rate_pct": 72,
      "customers": 3400,
      "signal": "Reduced logins"
    },
    {
      "churn_rate_pct": 68,
      "customers": 1200,
      "signal": "Competitor app download"
    },
    {
      "churn_rate_pct": 78,
      "customers": 890,
      "signal": "Direct deposit change"
    },
    {
      "churn_rate_pct": 54,
      "customers": 2100,
      "signal": "Balance decline >30%"
    }
  ]
}
```

### `RETENTION_STRATEGIES`

```json
{
  "CUST-8001": {
    "approach": "VP-level personal call",
    "channel": "Phone",
    "due": "Today 2 PM",
    "incentive": "Waive fees 12 months",
    "incentive_value": 480,
    "message": "We heard your app feedback",
    "offer": "Private beta access to the new mobile app",
    "owner": "VP Chen",
    "strategy": "Tech preview + fee waiver",
    "success_pct": 72,
    "talk_track": "Mr. Martinez, valued clients like you deserve our best. I saw your app feedback - I'd like you to be among the first to try our completely redesigned app.",
    "urgency": "Within 24 hours"
  },
  "CUST-8002": {
    "approach": "Relationship manager call",
    "channel": "Phone",
    "due": "Day 3",
    "incentive": "Waive monthly maintenance fees for 6 months",
    "incentive_value": 72,
    "message": "We reviewed your fees and complaints",
    "offer": "Complaint resolution with a fee review",
    "owner": "RM Patel",
    "strategy": "Fee review + service recovery",
    "success_pct": 55,
    "talk_track": "Mr. Johnson, I reviewed your recent fee disputes and want to walk you through what we can fix.",
    "urgency": "Within 3 days"
  },
  "CUST-8003": {
    "approach": "Relationship review with senior RM",
    "channel": "Video call",
    "due": "Tomorrow",
    "incentive": "Premium rate for 12 months",
    "incentive_value": 150,
    "message": "Let's make sure your savings work as hard as you do",
    "offer": "Premium savings rate review",
    "owner": "Sr. RM Johnson",
    "strategy": "Rate match + review",
    "success_pct": 65,
    "talk_track": "Ms. Thompson, I'd like to review your savings and deposit setup with you this week.",
    "urgency": "Within 48 hours"
  },
  "CUST-8004": {
    "approach": "In-person service recovery meeting",
    "channel": "In-person",
    "due": "Tomorrow",
    "incentive": "Service recovery escalation",
    "incentive_value": 50,
    "message": "We let you down and we will fix it",
    "offer": "Dedicated relationship manager",
    "owner": "Sr. RM Williams",
    "strategy": "Service recovery",
    "success_pct": 70,
    "talk_track": "Mr. Lee, I'm your dedicated contact from today, and I'll personally close out your open issues.",
    "urgency": "Within 48 hours"
  },
  "CUST-8005": {
    "approach": "Mobile app support session",
    "channel": "Phone + email",
    "due": "Day 3",
    "incentive": "Discounted product bundle with waived fees",
    "incentive_value": 200,
    "message": "Let's fix mobile deposits for you",
    "offer": "Guided setup of the new mobile app",
    "owner": "RM Garcia",
    "strategy": "Digital rescue",
    "success_pct": 60,
    "talk_track": "Ms. Sharma, I'd like to help you get mobile deposits working the way they should.",
    "urgency": "Within 3 days"
  }
}
```

### `OUTREACH_TRACKING`

```json
{
  "escalations": [
    "No contact in 48 hours -> alert manager",
    "Declines offer -> escalate to VP",
    "Balance withdrawal -> immediate notification"
  ],
  "tracking": [
    "Contact attempts: real-time",
    "Outcomes: RM updates",
    "Offer acceptance: immediate",
    "Account activity: 30-day monitoring"
  ]
}
```

### `REPLACEMENT_COST`

```json
{
  "top5_if_lost": 16000
}
```

### Demo walkthrough (video scenario)

A regional bank with 180K customers. Every operation has demo defaults; customer names resolve to IDs (Robert
Martinez CUST-8001, Marcus Johnson CUST-8002, Sarah Thompson CUST-8003, James Lee CUST-8004, Priya Sharma CUST-8005).

| Turn | User prompt | Operation | Key values |
|---|---|---|---|
| 1 | Analyze customer sentiment across our banking portfolio and identify accounts at highest churn risk | `sentiment_dashboard` | 180K customers analyzed; Promoters 72,000 (40%), Passives 81,000 (45%), Detractors 27,000 (15%); 2,400 high churn risk = $8.2M; Critical (>80%) 840 / $2.8M / $3,333 avg; High (60-80%) 1,560 / $5.4M / $3,462 avg; drivers digital banking 2,400, fee transparency 1,800, wait times 1,200; Negative sentiment up 18% |
| 2 | Yes, what are the early warning signals we should watch for? | `early_warning_signals` | Reduced logins 3,400 / 72%; competitor app download 1,200 / 68%; direct deposit change 890 / 78%; balance decline >30% 2,100 / 54%; combinations 89% / 82% / 67%; alerts today 47 / 23 / 12; Robert Martinez ($890K), Sarah Thompson ($450K), James Lee ($340K) |
| 3 | Yes, show me profiles of our highest-value at-risk customers | `churn_prediction` | Robert Martinez priority 1: $890K deposits, $12K revenue, 84% (critical), competitor app + reduced logins, detractor 4/10 "Your app is years behind", asked about wire fees; top 5 combined $2.18M deposits, $35K revenue; replacement cost $16K |
| 4 | Yes, what retention strategies should we use for each? | `retention_actions` | Martinez: VP-level call, "We heard your app feedback", private beta, 12-month fee waiver ($480), within 24 hours, 72%; table for all 5 (Thompson rate match + review, Lee service recovery + dedicated RM) and a draft talk track |
| 5 | Yes, assign the outreach and set up tracking | `outreach_plan` | Proposed: Martinez VP Chen phone today 2 PM; Thompson Sr. RM Johnson video call tomorrow; Lee Sr. RM Williams in person tomorrow; tracking and escalation rules; nothing sent |

The video's critical-tier average reads $3,340; $2.8M / 840 is $3,333, which the agent shows. The video's "Top 5"
table shows three rows; the agent lists all five. "Outreach deployed" in the video is a proposed plan here.
## Locked-case deterministic outputs

These are direct `perform()` results for the locked operation and arguments. Preserve the headings, identifiers, values, and boundary language.

### CSC-01 — Customer Success Lead

- Prompt: Analyze customer sentiment across our banking portfolio and identify accounts at highest churn risk.
- Operation: `sentiment_dashboard`
- Arguments: `{}`
- Required factual anchors: `180K customers analyzed`, `$8.2M`, `Negative sentiment up 18%`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Customer Sentiment Dashboard

180K customers analyzed. 2,400 high churn risk representing $8.2M annual revenue.

| Sentiment | Customers | % |
|---|---|---|
| Promoters | 72,000 | 40% |
| Passives | 81,000 | 45% |
| Detractors | 27,000 | 15% |

## High Risk

- **Critical (>80%):** 840 customers, $2.8M revenue, $3,333 avg
- **High (60-80%):** 1,560 customers, $5.4M revenue, $3,462 avg

**Top Negative Drivers:** Digital banking (2,400 mentions), Fee transparency (1,800 mentions), Wait times (1,200 mentions).

**Alert:** Negative sentiment up 18% this month.

## Highest-Value At-Risk Sample (interaction sentiment)

Sample interactions analyzed: 12 (Positive 0, Neutral 3, Negative 9)

| Customer | Segment | NPS | Churn Probability | Recent Sentiment |
|---|---|---|---|---|
| Robert Martinez (CUST-8001) | Affluent | 4 | 84% (critical) | Negative |
| Sarah Thompson (CUST-8003) | Affluent | 6 | 78% (high) | Neutral |
| James Lee (CUST-8004) | Emerging Affluent | 3 | 76% (high) | Negative |
| Marcus Johnson (CUST-8002) | Mass Market | 4 | 64% (high) | Negative |
| Priya Sharma (CUST-8005) | Emerging Affluent | 7 | 62% (high) | Neutral |

Next step: see the early warning signals?
```

### CSC-02 — Retention Specialist

- Prompt: Show me profiles of our highest-value at-risk customers.
- Operation: `churn_prediction`
- Arguments: `{}`
- Required factual anchors: `Robert Martinez`, `$2.18M`, `prioritize review`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Churn Prediction Report: Highest-Value At-Risk Customers

Top 5 at-risk profiles prepared.

### Robert Martinez (CUST-8001) - Priority 1

- $890K deposits, $12K annual revenue
- Risk: 84% (critical); review score 60/100
- Signals: Competitor app download (Summit National Bank), Reduced logins
- Last survey: Detractor (4/10) - "Your app is years behind"
- Recent contact: Asked about wire fees
- Segment: Affluent, tenure 12 years, products: checking, savings, investment

## Top 5 Summary

| Priority | Customer | Deposits | Revenue | Risk | Key Signal |
|---|---|---|---|---|---|
| 1 | R. Martinez (CUST-8001) | $890K | $12K | 84% | competitor app |
| 2 | S. Thompson (CUST-8003) | $450K | $8K | 78% | deposit changed |
| 3 | J. Lee (CUST-8004) | $340K | $6K | 76% | 3 complaints |
| 4 | M. Johnson (CUST-8002) | $280K | $5K | 64% | 5 complaints |
| 5 | P. Sharma (CUST-8005) | $220K | $4K | 62% | reduced logins |

**Combined Risk:** $2.18M deposits, $35K annual revenue at risk. Replacement cost if lost: $16K.

## Churn Indicators Reference

- **Low Nps** (weight: 25): NPS score below 5 indicates detractor status
- **Declining Transactions** (weight: 20): Monthly transactions below half of the segment average
- **High Complaints** (weight: 20): 3+ complaints in last 12 months
- **Low Engagement** (weight: 15): Digital engagement score below 30
- **Single Product** (weight: 10): Only one active product
- **Stale Survey** (weight: 10): Last survey response over 90 days before the demo date

These scores prioritize review; they do not predict an individual outcome.

Next step: generate retention strategies?
```

### CSC-03 — Relationship Manager

- Prompt: Prepare options for Marcus that I can review before anyone contacts him or changes a fee.
- Operation: `retention_actions`
- Arguments: `{"customer_id": "CUST-8002"}`
- Required factual anchors: `Marcus Johnson`, `No customer was contacted`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Retention Action Recommendations

### Marcus Johnson (CUST-8002) Strategy

- Approach: Relationship manager call
- Message: "We reviewed your fees and complaints"
- Offer: Complaint resolution with a fee review
- Incentive: Waive monthly maintenance fees for 6 months ($72 value)
- Urgency: Within 3 days
- Success probability (modeled): 55%
- Draft talk track: "Mr. Johnson, I reviewed your recent fee disputes and want to walk you through what we can fix."


## Available Actions Catalog

| Action | Description | Cost | Success Rate |
|---|---|---|---|
| Fee Waiver | Waive monthly maintenance fees for 6 months | $72 | 45% |
| Rate Upgrade | Offer premium savings rate for 12 months | $150 | 35% |
| Personal Outreach | Schedule call with relationship manager | $25 | 55% |
| Product Bundle | Offer discounted product bundle with waived fees | $200 | 60% |
| Loyalty Bonus | Credit loyalty bonus to account | $100 | 50% |
| Complaint Resolution | Escalate to service recovery team | $50 | 65% |

Every option requires relationship-manager review, policy validation, customer consent where applicable, and approved execution. No customer was contacted and no offer was made.

Next step: assign the outreach and set up tracking?
```

### CSC-04 — Head of Customer Experience

- Prompt: Which segment is under its experience benchmark, and what should we investigate?
- Operation: `segment_analysis`
- Arguments: `{}`
- Required factual anchors: `Mass Market`, `benchmark`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Segment Analysis

## Segment Benchmarks

| Segment | Avg NPS | Avg Products | Avg Tenure | Avg Transactions |
|---|---|---|---|---|
| Affluent | 8.2 | 4.1 | 10 yrs | 55/mo |
| Emerging Affluent | 7.0 | 3.2 | 5 yrs | 35/mo |
| Mass Market | 6.5 | 2.0 | 4 yrs | 20/mo |
| Small Business | 6.8 | 3.0 | 5 yrs | 90/mo |

## Current Customer Performance vs Benchmark

### Affluent (2 customers)

- NPS: 5.0 (benchmark: 8.2)
- Products: 3.0 (benchmark: 4.1)

### Emerging Affluent (2 customers)

- NPS: 5.0 (benchmark: 7.0)
- Products: 3.0 (benchmark: 3.2)

### Mass Market (1 customers)

- NPS: 4.0 (benchmark: 6.5)
- Products: 2.0 (benchmark: 2.0)

```

### CSC-05 — Retention Specialist

- Prompt: Yes, what are the early warning signals we should watch for?
- Operation: `early_warning_signals`
- Arguments: `{}`
- Required factual anchors: `Reduced logins`, `89% churn`, `Robert Martinez`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Early Warning Signals

4 key predictive signals identified, shown 30-60 days before leaving.

| Signal | Customers | Churn Rate |
|---|---|---|
| Reduced logins | 3,400 | 72% |
| Competitor app download | 1,200 | 68% |
| Direct deposit change | 890 | 78% |
| Balance decline >30% | 2,100 | 54% |

## Critical Combinations

- Competitor app + balance decline: 89% churn
- Deposit change + reduced logins: 82% churn
- 2+ complaints: 67% churn

## Real-Time Alerts Today

- 47 customers: Competitor app detected
- 23 customers: External transfers >$10K
- 12 customers: Direct deposit changed

**High-Value at Risk:** Robert Martinez ($890K, competitor app), Sarah Thompson ($450K, deposit changed), James Lee ($340K, 3 complaints)

Next step: profile the highest-value at-risk customers?
```

### CSC-06 — Customer Success Lead

- Prompt: Yes, assign the outreach and set up tracking.
- Operation: `outreach_plan`
- Arguments: `{}`
- Required factual anchors: `VP Chen`, `Escalation Rules`, `No customer was contacted`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Proposed Outreach Assignments and Tracking

Outreach plan ready for the manager to confirm: all 5 high-priority customers have a proposed owner, channel and due time.

| Customer | Assigned To | Channel | Due |
|---|---|---|---|
| R. Martinez (CUST-8001) | VP Chen | Phone | Today 2 PM |
| S. Thompson (CUST-8003) | Sr. RM Johnson | Video call | Tomorrow |
| J. Lee (CUST-8004) | Sr. RM Williams | In-person | Tomorrow |
| M. Johnson (CUST-8002) | RM Patel | Phone | Day 3 |
| P. Sharma (CUST-8005) | RM Garcia | Phone + email | Day 3 |

**Prepared for release (not sent):** customer briefs and talk tracks drafted, offers queued for approval, calendar holds proposed.

## Tracking

- Contact attempts: real-time
- Outcomes: RM updates
- Offer acceptance: immediate
- Account activity: 30-day monitoring

## Escalation Rules

- No contact in 48 hours -> alert manager
- Declines offer -> escalate to VP
- Balance withdrawal -> immediate notification

No customer was contacted, no offer was made, and no assignment, brief or calendar hold was sent; the manager confirms the plan in the CRM.
```
## Sentiment Distribution

- **Positive:** 2 (20.0%)
- **Neutral:** 4 (40.0%)
- **Negative:** 4 (40.0%)

## Customer NPS Scores

| Customer | Segment | NPS | Products | Complaints (12m) |
|---|---|---|---|---|
| Elizabeth Warren-Hayes (CUST-8001) | Affluent | 9 | 4 | 0 |
| Marcus Johnson (CUST-8002) | Mass Market | 4 | 2 | 5 |
| Priya Sharma (CUST-8003) | Emerging Affluent | 7 | 4 | 1 |
| Gerald Thompson (CUST-8004) | Mass Market | 3 | 1 | 2 |
| Diana Castellano (CUST-8005) | Small Business | 6 | 3 | 3 |
```

### CSC-02 — Retention Specialist

- Prompt: Who should my team review first today, and what evidence drove the priority?
- Operation: `churn_prediction`
- Arguments: `{}`
- Required factual anchors: `CUST-8004`, `prioritize review`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Churn Prediction Report

| Customer | Segment | Churn Score | NPS | Transactions | Complaints |
|---|---|---|---|---|---|
| Elizabeth Warren-Hayes (CUST-8001) | Affluent | 0 (Low) | 9 | 48 | 0 |
| Marcus Johnson (CUST-8002) | Mass Market | 45 (Medium) | 4 | 15 | 5 |
| Priya Sharma (CUST-8003) | Emerging Affluent | 0 (Low) | 7 | 32 | 1 |
| Gerald Thompson (CUST-8004) | Mass Market | 70 (High) | 3 | 4 | 2 |
| Diana Castellano (CUST-8005) | Small Business | 20 (Low) | 6 | 120 | 3 |

## High-Risk Customers

### Gerald Thompson (CUST-8004) — Score: 70

- Segment: Mass Market
- Tenure: 8 years
- Products: checking
- Recent sentiment: neutral


## Churn Indicators Reference

- **Low Nps** (weight: 25): NPS score below 5 indicates detractor status
- **Declining Transactions** (weight: 20): Monthly transactions below segment average
- **High Complaints** (weight: 20): 3+ complaints in last 12 months
- **Low Engagement** (weight: 15): Digital engagement score below 30
- **Single Product** (weight: 10): Only one active product
- **Stale Survey** (weight: 10): Last survey response over 90 days ago

These scores prioritize review; they do not predict an individual outcome.
```

### CSC-03 — Relationship Manager

- Prompt: Prepare options for Marcus that I can review before anyone contacts him or changes a fee.
- Operation: `retention_actions`
- Arguments: `{}`
- Required factual anchors: `Marcus Johnson`, `No customer was contacted`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Retention Action Recommendations

## Available Actions

| Action | Description | Cost | Success Rate |
|---|---|---|---|
| Fee Waiver | Waive monthly maintenance fees for 6 months | $72 | 45% |
| Rate Upgrade | Offer premium savings rate for 12 months | $150 | 35% |
| Personal Outreach | Schedule call with relationship manager | $25 | 55% |
| Product Bundle | Offer discounted product bundle with waived fees | $200 | 60% |
| Loyalty Bonus | Credit loyalty bonus to account | $100 | 50% |
| Complaint Resolution | Escalate to service recovery team | $50 | 65% |

## Recommended Actions by Customer

### Marcus Johnson (CUST-8002) — Churn Score: 45

1. **Complaint Resolution** — Escalate to service recovery team
2. **Personal Outreach** — Schedule call with relationship manager
3. **Product Bundle** — Offer discounted product bundle with waived fees

### Gerald Thompson (CUST-8004) — Churn Score: 70

2. **Personal Outreach** — Schedule call with relationship manager
3. **Product Bundle** — Offer discounted product bundle with waived fees


Every option requires relationship-manager review, policy validation, customer consent where applicable, and approved execution. No customer was contacted and no offer was made.
```

### CSC-04 — Head of Customer Experience

- Prompt: Which segment is under its experience benchmark, and what should we investigate?
- Operation: `segment_analysis`
- Arguments: `{}`
- Required factual anchors: `Mass Market`, `benchmark`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Segment Analysis

## Segment Benchmarks

| Segment | Avg NPS | Avg Products | Avg Tenure | Avg Transactions |
|---|---|---|---|---|
| Affluent | 8.2 | 4.1 | 10 yrs | 55/mo |
| Emerging Affluent | 7.0 | 3.2 | 5 yrs | 35/mo |
| Mass Market | 6.5 | 2.0 | 4 yrs | 20/mo |
| Small Business | 6.8 | 3.0 | 5 yrs | 90/mo |

## Current Customer Performance vs Benchmark

### Affluent (1 customers)

- NPS: 9.0 (benchmark: 8.2)
- Products: 4.0 (benchmark: 4.1)

### Mass Market (2 customers)

- NPS: 3.5 (benchmark: 6.5)
- Products: 1.5 (benchmark: 2.0)

### Emerging Affluent (1 customers)

- NPS: 7.0 (benchmark: 7.0)
- Products: 4.0 (benchmark: 3.2)

### Small Business (1 customers)

- NPS: 6.0 (benchmark: 6.8)
- Products: 3.0 (benchmark: 3.0)

```

## Evidence boundary

This snapshot does not authorize claims about a real person, protected-trait inference, deterministic churn predictions, customer contact, offers, fee changes, account actions, or external record changes. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
