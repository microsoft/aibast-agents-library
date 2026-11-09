# Cross Selling Opportunities Agent — Complete Fixed Synthetic Source Records

> **FIXED SYNTHETIC DEMO DATA ONLY.** This file is a complete serialization of the deterministic datasets used by the locked cases. It contains no live customer, CRM, email, meeting, product, competitive, subscription, or commercial data. Do not browse, enrich, substitute, infer, or invent records.

## Source and capture scope

- Deterministic source: `agents/@aibast-agents-library/general_stacks/cross_selling_opportunities_stack/cross_selling_agent.py`
- Strict transcript evidence: `solutions/cross-selling/evals/transcripts.json`
- Transcript captured at: `2026-08-08T04:36:33.425660+00:00`
- Strict isolation: `true`
- Supported source: this uploaded fixed snapshot only

If a requested identifier or fact is absent below, state that it is absent from the fixed synthetic snapshot.

## Demo scenario (aligned with the product video)

A SaaS company's sales leader analyzes the top 100 enterprise accounts (default; no account name needed):

1. Portfolio scan: $3.2M total expansion ARR — High Priority 12 accounts / $1.4M / avg $117K; Medium Priority 20 /
   $1.2M / $60K; Nurture 68 / $0.6M / $9K. Quick wins: 32 accounts with active buying signals, 8 exceeded usage limits
   this quarter, 5 requested features in products they don't own. Top signal: 12 accounts use CRM but not Analytics;
   94% of similar companies have both.
2. Top 5 opportunities = $547K: Acme Corp (CRM, Marketing -> Analytics Suite, $120K), TechCo Industries (Basic Plan ->
   Enterprise + Security, $115K), GlobalRetail Inc (CRM -> Full Platform, $108K), Meridian Finance (Analytics -> CRM +
   Integrations, $104K), Apex Manufacturing (Marketing -> CRM + Analytics, $100K). #1 Acme Corp deep dive: spend
   $85K/year, heavy data exports (no analytics), champion VP Marketing, trigger requested custom reports last week, next
   step schedule analytics demo.
3. Engagement strategies (drafts, not sent): Acme value-led demo, champion VP Marketing (Sarah Chen), end of quarter
   budget, talking points (50K records exported monthly; similar customers saw 340% ROI in 6 months; competitor TechGiant
   uses our full suite — synthetic examples to verify); TechCo usage-based upgrade, exceeded limits 3 consecutive months,
   hit limits 12 times, Security add-on for the compliance audit. Outreach sequence: Day 1 email, Day 3 LinkedIn, Day 5
   calendar invite.
4. Revenue impact: $2.1M realizable this quarter — Month 1 32 quick wins / 12-15 deals / $540K; Month 2 20 medium / 8-10
   deals / $720K; Month 3 12 high-value / 5-6 deals / $840K; close rates 45% / 38% / 50%; pipeline $1.8M -> $5.0M
   (+178%); quota coverage 2.8x vs 1.2x; 12 accounts need SE support, 8 need an executive sponsor intro.
5. Draft account assignments: James Wilson 8 accounts $680K Enterprise/Security; Lisa Chen 7 / $520K Analytics/Data;
   Mike Torres 9 / $490K Marketing/CRM; Sarah Kim 8 / $410K Manufacturing (32 accounts, $2.1M). This week (drafts ready
   for the leader to send): 32 quick-win emails, 12 SE demos, Friday executive intros; recommended (not enabled)
   triggers; team briefing proposed for tomorrow 9 AM.

Locked case prompts: see the companion operating rules (CS-01 to CS-07) for each prompt and its exact output.

## Dataset index

| Source constant | Records or fields |
| --- | ---: |
| `_PORTFOLIO` | 4 |
| `_CUSTOMER_OWNERSHIP` | 5 |
| `_AFFINITY_RULES` | 6 |
| `_CROSS_SELL_SUCCESS_RATES` | 3 |
| `_FORECAST` | 6 |
| `_REPS` | 4 |
| `_OUTREACH_SEQUENCE` | 3 |
| `_OPERATIONS` | 7 |

## Exact dataset `_PORTFOLIO`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "accounts": 100,
  "quick_wins": [
    "32 accounts showing active buying signals",
    "8 accounts exceeded usage limits this quarter",
    "5 accounts requested features in products they don't own"
  ],
  "segments": [
    {
      "accounts": 12,
      "potential_arr": 1400000,
      "segment": "High Priority"
    },
    {
      "accounts": 20,
      "potential_arr": 1200000,
      "segment": "Medium Priority"
    },
    {
      "accounts": 68,
      "potential_arr": 600000,
      "segment": "Nurture"
    }
  ],
  "top_signal": {
    "crm_without_analytics": 12,
    "peer_pct_with_both": 94
  }
}
```

## Exact dataset `_CUSTOMER_OWNERSHIP`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "CUST-001": {
    "approach": "Value-led demo showcasing ROI",
    "budget_window": "End of quarter budget available",
    "champion": "VP Marketing (Sarah Chen)",
    "current_products": [
      "CRM",
      "Marketing"
    ],
    "current_spend": 85000,
    "health_score": 91,
    "name": "Acme Corp",
    "next_step": "Schedule analytics demo",
    "owner": "Lisa Chen",
    "recommended": [
      {
        "arr": 120000,
        "product": "Analytics Suite"
      }
    ],
    "relationship": "strong relationship",
    "talking_points": [
      "You're exporting 50K records monthly - Analytics automates this",
      "Similar customers saw 340% ROI in 6 months",
      "Your competitor TechGiant uses our full suite"
    ],
    "trigger": "Requested custom reports last week",
    "usage": "Heavy data exports (no analytics)",
    "usage_fact": "exporting 50K records monthly"
  },
  "CUST-002": {
    "approach": "Usage-based upgrade conversation",
    "budget_window": "Compliance audit budget this quarter",
    "champion": "Director of IT",
    "current_products": [
      "Basic Plan"
    ],
    "current_spend": 48000,
    "health_score": 86,
    "name": "TechCo Industries",
    "next_step": "Usage review and Enterprise upgrade proposal",
    "owner": "James Wilson",
    "recommended": [
      {
        "arr": 85000,
        "product": "Enterprise"
      },
      {
        "arr": 30000,
        "product": "Security"
      }
    ],
    "relationship": "engaged",
    "talking_points": [
      "You've hit limits 12 times - Enterprise removes caps",
      "Security add-on addresses your compliance audit needs"
    ],
    "trigger": "Exceeded limits 3 consecutive months",
    "usage": "Exceeded plan limits 3 consecutive months (12 limit hits)",
    "usage_fact": "hit limits 12 times"
  },
  "CUST-003": {
    "approach": "Platform consolidation conversation",
    "budget_window": "Annual planning next month",
    "champion": "VP Sales Operations",
    "current_products": [
      "CRM"
    ],
    "current_spend": 60000,
    "health_score": 84,
    "name": "GlobalRetail Inc",
    "next_step": "Full Platform walkthrough",
    "owner": "Mike Torres",
    "recommended": [
      {
        "arr": 108000,
        "product": "Full Platform"
      }
    ],
    "relationship": "strong relationship",
    "talking_points": [
      "Your CRM is used across every region - the Full Platform connects marketing to it",
      "One platform replaces the spreadsheet campaign process"
    ],
    "trigger": "Asked about marketing automation in last QBR",
    "usage": "CRM used by all regional sales teams; marketing runs on spreadsheets",
    "usage_fact": "CRM adoption across all regions"
  },
  "CUST-004": {
    "approach": "Integration-led conversation",
    "budget_window": "New fiscal year budget",
    "champion": "Head of Revenue Operations",
    "current_products": [
      "Analytics"
    ],
    "current_spend": 52000,
    "health_score": 82,
    "name": "Meridian Finance",
    "next_step": "Integration discovery call",
    "owner": "James Wilson",
    "recommended": [
      {
        "arr": 76000,
        "product": "CRM"
      },
      {
        "arr": 28000,
        "product": "Integrations"
      }
    ],
    "relationship": "engaged",
    "talking_points": [
      "You upload CRM data manually every week - native CRM + Integrations removes that step",
      "Analytics customers who add CRM get one revenue view"
    ],
    "trigger": "Requested a CRM connector in a support ticket",
    "usage": "Analytics dashboards fed by manual CRM uploads",
    "usage_fact": "uploading CRM data manually every week"
  },
  "CUST-005": {
    "approach": "Lead-to-revenue demo",
    "budget_window": "Mid-year budget review",
    "champion": "Marketing Director",
    "current_products": [
      "Marketing"
    ],
    "current_spend": 40000,
    "health_score": 80,
    "name": "Apex Manufacturing",
    "next_step": "Lead-to-revenue demo",
    "owner": "Sarah Kim",
    "recommended": [
      {
        "arr": 62000,
        "product": "CRM"
      },
      {
        "arr": 38000,
        "product": "Analytics"
      }
    ],
    "relationship": "engaged",
    "talking_points": [
      "Your campaign leads leave the platform - CRM keeps them connected",
      "Analytics shows which campaigns turn into revenue"
    ],
    "trigger": "Feature request for lead scoring",
    "usage": "Campaign leads tracked outside the platform",
    "usage_fact": "tracking campaign leads in spreadsheets"
  }
}
```

## Exact dataset `_AFFINITY_RULES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "affinity_score": 0.94,
    "avg_time_to_close_days": 30,
    "if_owns": "CRM",
    "recommend": "Analytics Suite",
    "success_rate": 0.5
  },
  {
    "affinity_score": 0.88,
    "avg_time_to_close_days": 21,
    "if_owns": "Basic Plan",
    "recommend": "Enterprise",
    "success_rate": 0.45
  },
  {
    "affinity_score": 0.81,
    "avg_time_to_close_days": 30,
    "if_owns": "Enterprise",
    "recommend": "Security",
    "success_rate": 0.48
  },
  {
    "affinity_score": 0.79,
    "avg_time_to_close_days": 45,
    "if_owns": "Analytics",
    "recommend": "CRM",
    "success_rate": 0.38
  },
  {
    "affinity_score": 0.76,
    "avg_time_to_close_days": 40,
    "if_owns": "Marketing",
    "recommend": "CRM",
    "success_rate": 0.38
  },
  {
    "affinity_score": 0.72,
    "avg_time_to_close_days": 28,
    "if_owns": "CRM",
    "recommend": "Integrations",
    "success_rate": 0.45
  }
]
```

## Exact dataset `_CROSS_SELL_SUCCESS_RATES`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "High-value": {
    "avg_deal_cycle_days": 60,
    "avg_success_rate": 0.5,
    "basis": "strong signals"
  },
  "Medium priority": {
    "avg_deal_cycle_days": 45,
    "avg_success_rate": 0.38,
    "basis": "historical"
  },
  "Quick wins": {
    "avg_deal_cycle_days": 21,
    "avg_success_rate": 0.45,
    "basis": "historical"
  }
}
```

## Exact dataset `_FORECAST`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
{
  "coverage_after": "2.8x",
  "coverage_before": "1.2x",
  "current_pipeline": 1800000,
  "exec_sponsor_accounts": 8,
  "months": [
    {
      "arr": 540000,
      "close_rate": "Quick wins: 45% close rate (historical)",
      "closes": "12-15 deals",
      "month": "Month 1",
      "opportunities": "32 quick wins"
    },
    {
      "arr": 720000,
      "close_rate": "Medium priority: 38% close rate",
      "closes": "8-10 deals",
      "month": "Month 2",
      "opportunities": "20 medium"
    },
    {
      "arr": 840000,
      "close_rate": "High-value: 50% close rate (strong signals)",
      "closes": "5-6 deals",
      "month": "Month 3",
      "opportunities": "12 high-value"
    }
  ],
  "se_support_accounts": 12
}
```

## Exact dataset `_REPS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  {
    "accounts": 8,
    "arr": 680000,
    "rep": "James Wilson",
    "specialty": "Enterprise/Security"
  },
  {
    "accounts": 7,
    "arr": 520000,
    "rep": "Lisa Chen",
    "specialty": "Analytics/Data"
  },
  {
    "accounts": 9,
    "arr": 490000,
    "rep": "Mike Torres",
    "specialty": "Marketing/CRM"
  },
  {
    "accounts": 8,
    "arr": 410000,
    "rep": "Sarah Kim",
    "specialty": "Manufacturing"
  }
]
```

## Exact dataset `_OUTREACH_SEQUENCE`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  "Day 1: Personalized email with usage insights",
  "Day 3: LinkedIn touchpoint",
  "Day 5: Calendar invite for value demo"
]
```

## Exact dataset `_OPERATIONS`

The JSON below preserves every source identifier, name, value, label, signal, assumption, and relationship. A source `set` or tuple is represented as a JSON array without changing its members.

```json
[
  "opportunity_scan",
  "product_affinity",
  "recommendation_engine",
  "revenue_impact",
  "portfolio_scan",
  "top_opportunities",
  "account_assignments"
]
```

## Data-use boundary

Every identifier, company, person, date, count, price, amount, score, percentage, probability, benchmark, signal, claim, and projection above is synthetic. No outreach may be sent; no CRM, forecast, owner, task, alert, workflow, meeting, proposal, approval, pricing, subscription, renewal, product entitlement, or customer communication may be created, changed, activated, or delivered from this evidence.
