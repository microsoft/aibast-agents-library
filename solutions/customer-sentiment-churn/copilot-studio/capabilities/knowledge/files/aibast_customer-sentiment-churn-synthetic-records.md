# Customer Sentiment and Churn Prediction Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/customer_sentiment_churn_stack/customer_sentiment_churn_agent.py`
- Source SHA-256: `c6c5c2c62e315d5110c4eb199fb6b85712ce454b1ac4a362cefc4166206b47fc`
- Expected tool: `CustomerSentimentChurnAgent`
- Snapshot behavior: fixed to the packaged source revision; no live connection or current-data claim.

## Complete deterministic source records

The following objects reproduce every packaged identifier, name, value, amount, date, status, rule, threshold, mapping, and relationship used by the agent. Keys and values are exact.

### `CUSTOMER_INTERACTIONS`

```json
{
  "CUST-8001": {
    "complaint_count_12m": 0,
    "digital_engagement_score": 72,
    "last_survey": "2025-02-01",
    "monthly_transactions": 48,
    "name": "Elizabeth Warren-Hayes",
    "nps_score": 9,
    "products": [
      "checking",
      "savings",
      "mortgage",
      "investment"
    ],
    "recent_interactions": [
      {
        "channel": "branch",
        "date": "2025-02-15",
        "sentiment": "positive",
        "type": "inquiry"
      },
      {
        "channel": "phone",
        "date": "2025-01-20",
        "sentiment": "neutral",
        "type": "account_service"
      }
    ],
    "segment": "affluent",
    "tenure_years": 12
  },
  "CUST-8002": {
    "complaint_count_12m": 5,
    "digital_engagement_score": 35,
    "last_survey": "2025-01-15",
    "monthly_transactions": 15,
    "name": "Marcus Johnson",
    "nps_score": 4,
    "products": [
      "checking",
      "credit_card"
    ],
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
    "tenure_years": 3
  },
  "CUST-8003": {
    "complaint_count_12m": 1,
    "digital_engagement_score": 88,
    "last_survey": "2025-02-20",
    "monthly_transactions": 32,
    "name": "Priya Sharma",
    "nps_score": 7,
    "products": [
      "checking",
      "savings",
      "credit_card",
      "auto_loan"
    ],
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
        "sentiment": "positive",
        "type": "inquiry"
      }
    ],
    "segment": "emerging_affluent",
    "tenure_years": 5
  },
  "CUST-8004": {
    "complaint_count_12m": 2,
    "digital_engagement_score": 12,
    "last_survey": "2024-11-01",
    "monthly_transactions": 4,
    "name": "Gerald Thompson",
    "nps_score": 3,
    "products": [
      "checking"
    ],
    "recent_interactions": [
      {
        "channel": "branch",
        "date": "2024-12-15",
        "sentiment": "neutral",
        "type": "withdrawal"
      }
    ],
    "segment": "mass_market",
    "tenure_years": 8
  },
  "CUST-8005": {
    "complaint_count_12m": 3,
    "digital_engagement_score": 55,
    "last_survey": "2025-01-10",
    "monthly_transactions": 120,
    "name": "Diana Castellano",
    "nps_score": 6,
    "products": [
      "business_checking",
      "business_credit",
      "merchant_services"
    ],
    "recent_interactions": [
      {
        "channel": "phone",
        "date": "2025-02-20",
        "sentiment": "negative",
        "type": "fee_dispute"
      },
      {
        "channel": "branch",
        "date": "2025-01-30",
        "sentiment": "neutral",
        "type": "inquiry"
      }
    ],
    "segment": "small_business",
    "tenure_years": 6
  }
}
```

### `CHURN_INDICATORS`

```json
{
  "declining_transactions": {
    "description": "Monthly transactions below segment average",
    "threshold": 10,
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
    "description": "Last survey response over 90 days ago",
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

## Locked-case deterministic outputs

These are direct `perform()` results for the locked operation and arguments. Preserve the headings, identifiers, values, and boundary language.

### CSC-01 — Customer Success Lead

- Prompt: What are customers telling us across channels, and which relationship needs attention first?
- Operation: `sentiment_dashboard`
- Arguments: `{}`
- Required factual anchors: `CUST-8002`, `Negative`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional customer signals only. Scores are prioritization heuristics, not facts about a real person; no outreach, offer, fee change, or account action has occurred.

# Customer Sentiment Dashboard

**Average NPS:** 5.8
**Total Interactions Analyzed:** 10

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
