# Client Health Score — Complete Synthetic Portfolio Records

> SYNTHETIC PILOT DATA. All clients, values, scores, trends, interactions, and
> labels are fictional. This is a frozen portfolio snapshot, not live CRM data.

## Complete client records

| ID | Client | Annual value | Health | Health last quarter | NPS | Margin | Utilization | Billing | Escalations 90d | Exec meetings 90d | Q1 | Q2 | Q3 | Q4 | Segment |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| CL-301 | TechCorp Industries | $2,400,000 | 42 | 60 | -15 | 18.2% | 64% | declining | 4 | 0 | 8.4 | 8.3 | 8.2 | 5.1 | CRITICAL |
| CL-302 | Global Finance Corp | $1,500,000 | 58 | 64 | -20 | 22.5% | 45% | flat | 2 | 1 | 7.8 | 7.2 | 6.5 | 6.0 | AT_RISK |
| CL-303 | Healthcare Solutions Inc | $1,200,000 | 61 | 66 | +5 | 26.0% | 72% | flat | 3 | 1 | 8.0 | 7.8 | 7.0 | 6.8 | AT_RISK |
| CL-304 | Apex Manufacturing | $3,200,000 | 85 | 86 | +45 | 31.4% | 88% | growing | 0 | 3 | 8.5 | 8.8 | 9.0 | 9.1 | HEALTHY |
| CL-305 | National Logistics Group | $2,800,000 | 80 | 81 | +38 | 28.7% | 82% | growing | 1 | 2 | 7.9 | 8.2 | 8.5 | 8.6 | HEALTHY |
| CL-306 | Silverline Retail | $1,900,000 | 73 | 75 | +22 | 24.1% | 76% | flat | 1 | 2 | 7.5 | 7.6 | 7.8 | 7.9 | HEALTHY |
| CL-307 | Pinnacle Energy | $3,600,000 | 88 | 88 | +52 | 33.0% | 91% | growing | 0 | 4 | 8.8 | 9.0 | 9.2 | 9.3 | HEALTHY |
| CL-308 | Metro Transit Authority | $2,100,000 | 77 | 79 | +30 | 27.3% | 79% | growing | 0 | 2 | 7.6 | 7.9 | 8.1 | 8.3 | HEALTHY |
| CL-309 | Northwind Advisory Partners | $2,000,000 | 72 | 74 | +18 | 23.8% | 74% | flat | 1 | 2 | 7.4 | 7.5 | 7.5 | 7.6 | HEALTHY |
| CL-310 | Summit Insurance Group | $1,600,000 | 74 | 77 | +20 | 25.2% | 78% | flat | 0 | 2 | 7.6 | 7.7 | 7.8 | 7.8 | HEALTHY |

## Portfolio totals

- Portfolio value: $22,300,000 ($22.3M) across 10 clients
- At-risk value: $5,100,000 ($5.1M, 23% of portfolio): Critical $2.4M (TechCorp), At risk $2.7M (Global Finance + Healthcare Solutions)
- Healthy: 7 clients, $17.2M (monitor)
- Average health score: 71/100, last quarter 75/100 (down 4 points QoQ)
- TechCorp Industries dropped from 60/100 to 42/100 in 90 days; churn indicator 78% without intervention

## Churn Indicator rule

| Health score | Synthetic indicator |
|---|---:|
| 45 or below | 78% |
| 46 through 60 | 45% |
| 61 through 70 | 20% |
| 71 through 80 | 10% |
| Above 80 | 3% |

These are deterministic scenario indicators, not validated predictions or statements that churn will occur.

## Risk factors, retention playbook and outreach records

- TechCorp: executive contact none in 3 months (CTO departed); project satisfaction 5.1/10 (was 8.2 last quarter); invoice $340K outstanding - 67 days overdue; competitive threat: major consulting firm spotted on-site last week; CTO John Davis left 3 months ago, replacement not briefed; last project had deliverable delays.
- Global Finance Corp: using only 45% of contracted hours; renewal 90 days away; NPS -20 (was +15 last quarter); non-renewal likely.
- Healthcare Solutions Inc: 47 open support tickets (backlog); new CTO skeptical of our value; risk of budget cut or replacement.
- TechCorp 30-day plan: investment $600K (credits + resources), success probability 73%; $4.2M savings delivered, 34% efficiency; the $50K credit and the CEO-to-CEO call are proposals that need approval.
- Outreach: Tuesday Sarah Mitchell (CTO), Wednesday CFO, Thursday Morgan Lee (COO), Friday CEO; materials: executive briefing decks, success dashboards, ROI documentation. ROI if successful: (50% margin x $2.4M x 2 years - $600K) / $600K = 300% over 2 years.

### `CLIENTS`

```json
{
  "CL-301": {
    "name": "TechCorp Industries",
    "annual_value": 2400000,
    "nps": -15,
    "project_margin_pct": 18.2,
    "utilization_pct": 64,
    "billing_trend": "declining",
    "escalations_90d": 4,
    "exec_meetings_90d": 0,
    "satisfaction_scores": [
      8.4,
      8.3,
      8.2,
      5.1
    ],
    "health_score": 42,
    "health_score_prior": 60,
    "risk_label": "CRITICAL"
  },
  "CL-302": {
    "name": "Global Finance Corp",
    "annual_value": 1500000,
    "nps": -20,
    "project_margin_pct": 22.5,
    "utilization_pct": 45,
    "billing_trend": "flat",
    "escalations_90d": 2,
    "exec_meetings_90d": 1,
    "satisfaction_scores": [
      7.8,
      7.2,
      6.5,
      6.0
    ],
    "health_score": 58,
    "health_score_prior": 64,
    "risk_label": "AT_RISK"
  },
  "CL-303": {
    "name": "Healthcare Solutions Inc",
    "annual_value": 1200000,
    "nps": 5,
    "project_margin_pct": 26.0,
    "utilization_pct": 72,
    "billing_trend": "flat",
    "escalations_90d": 3,
    "exec_meetings_90d": 1,
    "satisfaction_scores": [
      8.0,
      7.8,
      7.0,
      6.8
    ],
    "health_score": 61,
    "health_score_prior": 66,
    "risk_label": "AT_RISK"
  },
  "CL-304": {
    "name": "Apex Manufacturing",
    "annual_value": 3200000,
    "nps": 45,
    "project_margin_pct": 31.4,
    "utilization_pct": 88,
    "billing_trend": "growing",
    "escalations_90d": 0,
    "exec_meetings_90d": 3,
    "satisfaction_scores": [
      8.5,
      8.8,
      9.0,
      9.1
    ],
    "health_score": 85,
    "health_score_prior": 86,
    "risk_label": "HEALTHY"
  },
  "CL-305": {
    "name": "National Logistics Group",
    "annual_value": 2800000,
    "nps": 38,
    "project_margin_pct": 28.7,
    "utilization_pct": 82,
    "billing_trend": "growing",
    "escalations_90d": 1,
    "exec_meetings_90d": 2,
    "satisfaction_scores": [
      7.9,
      8.2,
      8.5,
      8.6
    ],
    "health_score": 80,
    "health_score_prior": 81,
    "risk_label": "HEALTHY"
  },
  "CL-306": {
    "name": "Silverline Retail",
    "annual_value": 1900000,
    "nps": 22,
    "project_margin_pct": 24.1,
    "utilization_pct": 76,
    "billing_trend": "flat",
    "escalations_90d": 1,
    "exec_meetings_90d": 2,
    "satisfaction_scores": [
      7.5,
      7.6,
      7.8,
      7.9
    ],
    "health_score": 73,
    "health_score_prior": 75,
    "risk_label": "HEALTHY"
  },
  "CL-307": {
    "name": "Pinnacle Energy",
    "annual_value": 3600000,
    "nps": 52,
    "project_margin_pct": 33.0,
    "utilization_pct": 91,
    "billing_trend": "growing",
    "escalations_90d": 0,
    "exec_meetings_90d": 4,
    "satisfaction_scores": [
      8.8,
      9.0,
      9.2,
      9.3
    ],
    "health_score": 88,
    "health_score_prior": 88,
    "risk_label": "HEALTHY"
  },
  "CL-308": {
    "name": "Metro Transit Authority",
    "annual_value": 2100000,
    "nps": 30,
    "project_margin_pct": 27.3,
    "utilization_pct": 79,
    "billing_trend": "growing",
    "escalations_90d": 0,
    "exec_meetings_90d": 2,
    "satisfaction_scores": [
      7.6,
      7.9,
      8.1,
      8.3
    ],
    "health_score": 77,
    "health_score_prior": 79,
    "risk_label": "HEALTHY"
  },
  "CL-309": {
    "name": "Northwind Advisory Partners",
    "annual_value": 2000000,
    "nps": 18,
    "project_margin_pct": 23.8,
    "utilization_pct": 74,
    "billing_trend": "flat",
    "escalations_90d": 1,
    "exec_meetings_90d": 2,
    "satisfaction_scores": [
      7.4,
      7.5,
      7.5,
      7.6
    ],
    "health_score": 72,
    "health_score_prior": 74,
    "risk_label": "HEALTHY"
  },
  "CL-310": {
    "name": "Summit Insurance Group",
    "annual_value": 1600000,
    "nps": 20,
    "project_margin_pct": 25.2,
    "utilization_pct": 78,
    "billing_trend": "flat",
    "escalations_90d": 0,
    "exec_meetings_90d": 2,
    "satisfaction_scores": [
      7.6,
      7.7,
      7.8,
      7.8
    ],
    "health_score": 74,
    "health_score_prior": 77,
    "risk_label": "HEALTHY"
  }
}
```

### `STAKEHOLDERS`

```json
{
  "CL-301": {
    "executive_sponsor": "Morgan Lee, COO",
    "new_cto": "Sarah Mitchell, CTO (new; not yet briefed on our value delivery)",
    "account_owner": "Rachel Adams",
    "delivery_lead": "Elena Vasquez",
    "next_engagement": "Executive review with new CTO Sarah Mitchell"
  },
  "CL-302": {
    "executive_sponsor": "Jordan Patel, CFO",
    "account_owner": "Marcus Reed",
    "delivery_lead": "Michael Chen",
    "next_engagement": "Value realization workshop"
  },
  "CL-303": {
    "executive_sponsor": "Taylor Brooks, CIO",
    "account_owner": "Nina Shah",
    "delivery_lead": "Priya Sharma",
    "next_engagement": "Escalation closure and roadmap review"
  }
}
```

### `RISK_FACTORS`

```json
{
  "CL-301": {
    "summary": "executive turnover, quality issues, overdue invoices, and competitor presence",
    "executive_contact": "None in 3 months (CTO departed)",
    "satisfaction_prior": 8.2,
    "invoice_outstanding": 340000,
    "invoice_days_overdue": 67,
    "competitive_threat": "Major consulting firm spotted on-site last week",
    "key_stakeholder": "CTO John Davis left 3 months ago, replacement not briefed on our value delivery",
    "quality": "Last project had deliverable delays",
    "issue": "Executive turnover and deliverable delays",
    "renewal_days": 0,
    "nps_prior": 10,
    "open_tickets": 9,
    "outlook": "Churn without intervention"
  },
  "CL-302": {
    "summary": "low use of contracted hours and a falling NPS ahead of renewal",
    "executive_contact": "1 meeting in 90 days",
    "satisfaction_prior": 6.5,
    "invoice_outstanding": 0,
    "invoice_days_overdue": 0,
    "competitive_threat": "None observed",
    "key_stakeholder": "CFO Jordan Patel owns the renewal decision",
    "quality": "No open quality issue",
    "issue": "Using only 45% of contracted hours",
    "renewal_days": 90,
    "nps_prior": 15,
    "open_tickets": 6,
    "outlook": "Non-renewal likely"
  },
  "CL-303": {
    "summary": "a support backlog and a new CTO who is skeptical of our value",
    "executive_contact": "1 meeting in 90 days",
    "satisfaction_prior": 7.0,
    "invoice_outstanding": 0,
    "invoice_days_overdue": 0,
    "competitive_threat": "None observed",
    "key_stakeholder": "New CTO: Skeptical of our value",
    "quality": "Support backlog",
    "issue": "47 open support tickets (backlog)",
    "renewal_days": 150,
    "nps_prior": 12,
    "open_tickets": 47,
    "outlook": "Budget cut or replacement"
  }
}
```

### `RETENTION_PLAYBOOK`

```json
{
  "client": "CL-301",
  "basis": "our successful turnaround playbook",
  "weeks": [
    {
      "week": "Week 1: Stabilization",
      "actions": [
        "Day 1: CEO to CEO call (proposed; confirm on your CEO's calendar)",
        "Day 2: Resolve invoice dispute ($50K credit proposed, requires finance approval)",
        "Days 3-5: Deploy SWAT team to fix quality issues"
      ]
    },
    {
      "week": "Week 2: Trust Rebuild",
      "actions": [
        "Executive review with new CTO Sarah Mitchell",
        "Present historical value: $4.2M savings delivered",
        "ROI dashboard: 34% efficiency improvements"
      ]
    },
    {
      "week": "Week 3: Value Demonstration",
      "actions": [
        "Quick wins: 2-3 immediate improvements",
        "Success metrics: Real-time dashboard",
        "Stakeholder mapping: 4 key executives"
      ]
    },
    {
      "week": "Week 4: Future Security",
      "actions": [
        "Revised contract terms",
        "Quarterly business reviews formalized",
        "Executive sponsor program"
      ]
    }
  ],
  "investment": 600000,
  "investment_note": "credits + resources",
  "success_probability_pct": 73,
  "value_delivered": 4200000,
  "efficiency_gain_pct": 34,
  "retained_margin_pct": 50,
  "roi_years": 2
}
```

### `OUTREACH_SEQUENCE`

```json
[
  {
    "day": "Tuesday",
    "who": "Sarah Mitchell (CTO)",
    "name": "Sarah Mitchell",
    "focus": "Technical deep dive",
    "show": [
      "$4.2M cost savings we delivered",
      "34% efficiency improvements"
    ],
    "goal": "Rebuild technical credibility"
  },
  {
    "day": "Wednesday",
    "who": "CFO",
    "focus": "ROI review",
    "show": [
      "Financial impact metrics",
      "Invoice dispute resolution"
    ],
    "goal": "Close the invoice dispute"
  },
  {
    "day": "Thursday",
    "who": "Morgan Lee (COO)",
    "focus": "Process optimization results",
    "show": [
      "Operational improvements",
      "Future roadmap"
    ],
    "goal": "Agree the delivery roadmap"
  },
  {
    "day": "Friday",
    "who": "CEO",
    "focus": "Strategic partnership discussion",
    "show": [
      "Long-term value proposition"
    ],
    "goal": "Commitment to improved delivery"
  }
]
```

### `OUTREACH_MATERIALS`

```json
[
  "Executive briefing decks",
  "Success dashboards",
  "ROI documentation"
]
```
