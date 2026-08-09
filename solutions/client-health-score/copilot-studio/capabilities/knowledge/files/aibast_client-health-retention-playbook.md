# Client Health Score — Complete Synthetic Retention Rules and Playbooks

> SYNTHETIC PLANNING DATA. No CRM, email, calendar, collaboration, renewal, or
> client system is connected.

## At-Risk Client Report

| Client | ID | Health | Segment | Annual value | Churn probability | NPS | Trend | Escalations 90d | Exec meetings 90d |
|---|---|---:|---|---:|---:|---:|---|---:|---:|
| TechCorp Industries | CL-301 | 42/100 | CRITICAL | $2,400,000 | 78% | -15 | declining | 4 | 0 |
| Global Finance Corp | CL-302 | 58/100 | AT_RISK | $1,500,000 | 45% | -20 | declining | 2 | 1 |
| Healthcare Solutions Inc | CL-303 | 61/100 | AT_RISK | $1,200,000 | 20% | +5 | declining | 3 | 1 |

- Clients at risk: 3
- Total value at risk: $5,100,000

## Deterministic Recommended retention actions

Apply these conditions exactly:

- If executive meetings in 90 days equal 0: `Schedule executive sponsor
  meeting within 7 days`.
- If escalations in 90 days are at least 3: `Deploy SWAT team to resolve open
  issues`.
- If utilization is below 60%: `Review scope alignment; client may not be
  extracting full value`.
- If NPS is below 0: `Conduct root-cause analysis on negative NPS drivers`.
- Every at-risk client: `Prepare value-delivered summary (ROI documentation)`.

Therefore:

- TechCorp Industries receives executive sponsor meeting, SWAT team,
  root-cause analysis, and value-delivered summary recommendations.
- Global Finance Corp receives scope-alignment review, root-cause analysis, and
  value-delivered summary recommendations.
- Healthcare Solutions Inc receives SWAT team and value-delivered summary
  recommendations.

## Complete stakeholder records

| Client | ID | Executive sponsor | Account owner | Delivery lead | Next engagement |
|---|---|---|---|---|---|
| TechCorp Industries | CL-301 | Morgan Lee, COO | Rachel Adams | Elena Vasquez | Executive recovery review |
| Global Finance Corp | CL-302 | Jordan Patel, CFO | Marcus Reed | Michael Chen | Value realization workshop |
| Healthcare Solutions Inc | CL-303 | Taylor Brooks, CIO | Nina Shah | Priya Sharma | Escalation closure and roadmap review |

## Account Retention Playbooks

Every playbook includes:

- Prepare open-issue summary, value-delivered evidence, and decision log.
- **Approval gate:** account owner reviews the plan before any client outreach.

### TechCorp Industries — CRITICAL

- Priority: propose an executive sponsor meeting within seven days.
- Recovery: assign an approved escalation owner and review closure evidence
  weekly.
- Trust: validate negative feedback themes before proposing corrective
  commitments.

### Global Finance Corp — AT_RISK

- Trust: validate negative feedback themes before proposing corrective
  commitments.

### Healthcare Solutions Inc — AT_RISK

- Recovery: assign an approved escalation owner and review closure evidence
  weekly.

## Required response headings and decision boundaries

- `Client Health Dashboard`
- `Churn Indicator`
- `Engagement Analysis`
- `Engagement Red Flags`
- `Client Satisfaction Trends`
- `Declining Accounts Requiring Attention`
- `At-Risk Client Report`
- `Recommended retention actions`
- `Account Retention Playbooks`
- `Approval gate`

Churn indicators are not certainties. Recommendations require account-owner
approval. Never create a meeting, send a message, make a concession, promise
remediation, change a renewal, or update CRM.
