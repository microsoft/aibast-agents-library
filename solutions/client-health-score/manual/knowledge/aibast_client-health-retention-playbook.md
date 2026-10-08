# Client Health Score — Retention Playbook and Locked Responses

> SYNTHETIC PILOT DATA. Every response below is decision support; no client is contacted, no meeting or message is created, and no CRM record changes.

## Routing

| Case | Persona | Operation | Prompt | Required evidence |
|---|---|---|---|---|
| CHS-01 | Client Success Leader | `health_dashboard` | Which relationships are healthy, at risk, or critical, and where should my team focus first? | TechCorp Industries; Churn Indicator; CRITICAL; $22.3M |
| CHS-02 | Account Manager | `engagement_analysis` | What engagement signals are weakening across the portfolio, especially executive contact and escalations? | No executive contact in 90 days; Declining billing trend; TechCorp Industries |
| CHS-03 | Client Experience Director | `satisfaction_trend` | Which client satisfaction trends are moving the wrong way, and what evidence supports that view? | Declining Accounts Requiring Attention; TechCorp Industries; Global Finance Corp |
| CHS-04 | Client Success Leader | `at_risk_clients` | Give me the accounts that need intervention now, the risk drivers, and the first recovery actions. | TechCorp Industries; Global Finance Corp; Healthcare Solutions Inc; 47 open support tickets |
| CHS-05 | Account Manager | `retention_plan` | Build the stakeholder map and executive engagement plan for each account that needs a turnaround. | Morgan Lee; Value realization workshop; Approval gate; Sarah Mitchell |
| CHS-06 | Account Manager | `risk_analysis` | What's driving TechCorp's health score down so fast? | 78%; $340K outstanding; John Davis |
| CHS-07 | Account Manager | `stakeholder_outreach` | Who is the first executive we need to reach at TechCorp, and in what order should we meet the others? | Sarah Mitchell; Tuesday; ROI documentation |
| CHS-08 | Client Success Leader | `qbr_summary` | Wrap up my quarterly business review prep with a summary of the portfolio, the risks and the retention plan. | $17.2M; 300%; ready for you to send |

Demo phrasing: "prep for our quarterly business review ... health scores" -> `health_dashboard`; "TechCorp risk analysis" -> `risk_analysis`; "other at-risk clients" -> `at_risk_clients`; "retention roadmap for TechCorp" -> `retention_plan`; "first stakeholder we need to reach" -> `stakeholder_outreach`; "schedule the meetings and summarize" -> `qbr_summary` (invites are drafts).

## Required response headings and decision boundaries

- Present every plan, credit, call, invite and message as a draft for account-owner approval.
- Never state that a meeting was scheduled, a message was sent, a credit was approved, or a CRM record changed.

## Locked responses

### CHS-01 `health_dashboard`

```markdown
## Client Health Dashboard

I've analyzed your $22.3M consulting portfolio and identified critical risk requiring immediate intervention - TechCorp Industries at 42/100 with $2.4M at risk.

### Portfolio Health Overview

| Status | Clients | Annual Value | Action |
|--------|--------:|-------------:|--------|
| CRITICAL | 1 | $2.4M | Immediate |
| At Risk | 2 | $2.7M | 30-day plan |
| Healthy | 7 | $17.2M | Monitor |

### Key Metrics

- **Portfolio value:** $22,300,000 ($22.3M annually)
- **Avg health score:** 71/100 (down 4 points QoQ)
- **At-risk value:** $5,100,000 ($5.1M, 23% of portfolio)
- **Immediate action:** TechCorp Industries

**TechCorp Alert:** Dropped from 60/100 to 42/100 in 90 days with multiple risk factors converging.

| Client | Annual Value | Health | Churn Indicator | NPS | Margin | Util % | Risk |
|--------|-------------|--------|-----------------|-----|--------|--------|------|
| TechCorp Industries | $2,400,000 | 42/100 | 78% | -15 | 18.2% | 64% | **CRITICAL** |
| Global Finance Corp | $1,500,000 | 58/100 | 45% | -20 | 22.5% | 45% | **AT_RISK** |
| Healthcare Solutions Inc | $1,200,000 | 61/100 | 20% | +5 | 26.0% | 72% | **AT_RISK** |
| Northwind Advisory Partners | $2,000,000 | 72/100 | 10% | +18 | 23.8% | 74% | **HEALTHY** |
| Silverline Retail | $1,900,000 | 73/100 | 10% | +22 | 24.1% | 76% | **HEALTHY** |
| Summit Insurance Group | $1,600,000 | 74/100 | 10% | +20 | 25.2% | 78% | **HEALTHY** |
| Metro Transit Authority | $2,100,000 | 77/100 | 10% | +30 | 27.3% | 79% | **HEALTHY** |
| National Logistics Group | $2,800,000 | 80/100 | 10% | +38 | 28.7% | 82% | **HEALTHY** |
| Apex Manufacturing | $3,200,000 | 85/100 | 3% | +45 | 31.4% | 88% | **HEALTHY** |
| Pinnacle Energy | $3,600,000 | 88/100 | 3% | +52 | 33.0% | 91% | **HEALTHY** |

**Distribution:** 1 critical, 2 at-risk, 7 healthy

Source: [D365 CE + Client Success Platform + Project Ops]

> Synthetic scenario indicators, not validated predictions or live CRM scores.

Next: want to see what's driving TechCorp down?
```

### CHS-02 `engagement_analysis`

```markdown
## Engagement Analysis

| Client | Exec Meetings (90d) | Escalations (90d) | Billing Trend | Utilization |
|--------|--------------------:|------------------:|---------------|-------------|
| TechCorp Industries | 0 **LOW** | 4 | declining | 64% |
| Global Finance Corp | 1 | 2 | flat | 45% |
| Healthcare Solutions Inc | 1 | 3 | flat | 72% |
| Apex Manufacturing | 3 | 0 | growing | 88% |
| National Logistics Group | 2 | 1 | growing | 82% |
| Silverline Retail | 2 | 1 | flat | 76% |
| Pinnacle Energy | 4 | 0 | growing | 91% |
| Metro Transit Authority | 2 | 0 | growing | 79% |
| Northwind Advisory Partners | 2 | 1 | flat | 74% |
| Summit Insurance Group | 2 | 0 | flat | 78% |

### Engagement Red Flags

**TechCorp Industries:**
- No executive contact in 90 days
- 4 escalations in 90 days
- Declining billing trend

**Global Finance Corp:**
- Low utilization (45%) -- may not see value

**Healthcare Solutions Inc:**
- 3 escalations in 90 days

> Synthetic engagement data. No client record, task, meeting, or message was created.
```

### CHS-03 `satisfaction_trend`

```markdown
## Client Satisfaction Trends

| Client | Q1 | Q2 | Q3 | Q4 | Trend | NPS |
|--------|-----|-----|-----|-----|-------|-----|
| TechCorp Industries | 8.4 | 8.3 | 8.2 | 5.1 | **DOWN** | -15 |
| Global Finance Corp | 7.8 | 7.2 | 6.5 | 6.0 | **DOWN** | -20 |
| Healthcare Solutions Inc | 8.0 | 7.8 | 7.0 | 6.8 | **DOWN** | +5 |
| Apex Manufacturing | 8.5 | 8.8 | 9.0 | 9.1 | **UP** | +45 |
| National Logistics Group | 7.9 | 8.2 | 8.5 | 8.6 | **UP** | +38 |
| Silverline Retail | 7.5 | 7.6 | 7.8 | 7.9 | **UP** | +22 |
| Pinnacle Energy | 8.8 | 9.0 | 9.2 | 9.3 | **UP** | +52 |
| Metro Transit Authority | 7.6 | 7.9 | 8.1 | 8.3 | **UP** | +30 |
| Northwind Advisory Partners | 7.4 | 7.5 | 7.5 | 7.6 | **FLAT** | +18 |
| Summit Insurance Group | 7.6 | 7.7 | 7.8 | 7.8 | **FLAT** | +20 |

### Declining Accounts Requiring Attention

- **TechCorp Industries**: dropped 3.3 points over 4 quarters (NPS: -15)
- **Global Finance Corp**: dropped 1.8 points over 4 quarters (NPS: -20)
- **Healthcare Solutions Inc**: dropped 1.2 points over 4 quarters (NPS: +5)

> Synthetic survey history; validate source quality before client action.
```

### CHS-04 `at_risk_clients`

```markdown
## At-Risk Client Report

**Clients at risk:** 3
**Total value at risk:** $5,100,000

### TechCorp Industries -- Health: 42/100 (CRITICAL)
- **Contract value:** $2,400,000 annually
- **Issue:** Executive turnover and deliverable delays
- **NPS score:** -15 (was +10 last quarter)
- **Open support tickets:** 9
- **Key stakeholder:** CTO John Davis left 3 months ago, replacement not briefed on our value delivery
- **Risk:** Churn without intervention (churn indicator 78%)
- **Satisfaction trend:** declining; escalations (90d): 4; exec meetings (90d): 0

**Recommended retention actions:**
- Schedule executive sponsor meeting within 7 days
- Deploy SWAT team to resolve open issues
- Conduct root-cause analysis on negative NPS drivers
- Prepare value-delivered summary (ROI documentation)

### Global Finance Corp -- Health: 58/100 (AT_RISK)
- **Contract value:** $1,500,000 annually
- **Issue:** Using only 45% of contracted hours
- **Renewal:** 90 days away
- **NPS score:** -20 (was +15 last quarter)
- **Open support tickets:** 6
- **Key stakeholder:** CFO Jordan Patel owns the renewal decision
- **Risk:** Non-renewal likely (churn indicator 45%)
- **Satisfaction trend:** declining; escalations (90d): 2; exec meetings (90d): 1

**Recommended retention actions:**
- Review scope alignment; client may not be extracting full value
- Conduct root-cause analysis on negative NPS drivers
- Prepare value-delivered summary (ROI documentation)

### Healthcare Solutions Inc -- Health: 61/100 (AT_RISK)
- **Contract value:** $1,200,000 annually
- **Issue:** 47 open support tickets (backlog)
- **Renewal:** 150 days away
- **NPS score:** +5 (was +12 last quarter)
- **Open support tickets:** 47
- **Key stakeholder:** New CTO: Skeptical of our value
- **Risk:** Budget cut or replacement (churn indicator 20%)
- **Satisfaction trend:** declining; escalations (90d): 3; exec meetings (90d): 1

**Recommended retention actions:**
- Deploy SWAT team to resolve open issues
- Prepare value-delivered summary (ROI documentation)

### Combined Portfolio Risk

- Total at risk: $5.1M (23% of portfolio)
- Critical: $2.4M (TechCorp)
- At risk: $2.7M (Global + Healthcare)

Source: [Utilization Data + Support System + Surveys]

> Synthetic indicators. Recommendations require account-owner approval; churn indicators are not certainties.
```

### CHS-05 `retention_plan`

```markdown
## Account Retention Playbooks

I've built a 30-day TechCorp retention plan based on our successful turnaround playbook. Week 1 focuses on immediate stabilization.

### TechCorp Industries 30-Day Retention Plan (draft)

**Week 1: Stabilization**
- Day 1: CEO to CEO call (proposed; confirm on your CEO's calendar)
- Day 2: Resolve invoice dispute ($50K credit proposed, requires finance approval)
- Days 3-5: Deploy SWAT team to fix quality issues

**Week 2: Trust Rebuild**
- Executive review with new CTO Sarah Mitchell
- Present historical value: $4.2M savings delivered
- ROI dashboard: 34% efficiency improvements

**Week 3: Value Demonstration**
- Quick wins: 2-3 immediate improvements
- Success metrics: Real-time dashboard
- Stakeholder mapping: 4 key executives

**Week 4: Future Security**
- Revised contract terms
- Quarterly business reviews formalized
- Executive sponsor program

**Investment:** $600K (credits + resources) | **Success probability:** 73% with full execution

### Stakeholder Maps

#### TechCorp Industries — CRITICAL
- **Executive sponsor:** Morgan Lee, COO
- **New executive:** Sarah Mitchell, CTO (new; not yet briefed on our value delivery)
- **Account owner:** Rachel Adams
- **Delivery lead:** Elena Vasquez
- **Next engagement:** Executive review with new CTO Sarah Mitchell
- **Priority:** propose an executive sponsor meeting within seven days.
- **Recovery:** assign an approved escalation owner and review closure evidence weekly.
- **Trust:** validate negative feedback themes before proposing corrective commitments.
- **Approval gate:** account owner reviews the plan before any client outreach.

#### Global Finance Corp — AT_RISK
- **Executive sponsor:** Jordan Patel, CFO
- **Account owner:** Marcus Reed
- **Delivery lead:** Michael Chen
- **Next engagement:** Value realization workshop
- **Trust:** validate negative feedback themes before proposing corrective commitments.
- **Approval gate:** account owner reviews the plan before any client outreach.

#### Healthcare Solutions Inc — AT_RISK
- **Executive sponsor:** Taylor Brooks, CIO
- **Account owner:** Nina Shah
- **Delivery lead:** Priya Sharma
- **Next engagement:** Escalation closure and roadmap review
- **Recovery:** assign an approved escalation owner and review closure evidence weekly.
- **Approval gate:** account owner reviews the plan before any client outreach.

Source: [Retention Playbook + Historical Success]

> Synthetic draft planning artifact only; no meeting, message, concession, renewal, or CRM update has been created.

Next: who's the first stakeholder we need to reach?
```

### CHS-06 `risk_analysis`

```markdown
## TechCorp Industries - Risk Analysis

TechCorp has multiple converging risk factors - executive turnover, quality issues, overdue invoices, and competitor presence. Churn probability: 78% without intervention.

**Health Score:** 42/100 (down 18 points in 90 days) | **Contract Value:** $2.4M annually

### Critical Risk Factors

- **Executive contact:** None in 3 months (CTO departed)
- **Project satisfaction:** 5.1/10 (was 8.2 last quarter)
- **Invoice status:** $340K outstanding - 67 days overdue
- **Competitive threat:** Major consulting firm spotted on-site last week

**Key Stakeholder:** CTO John Davis left 3 months ago, replacement not briefed on our value delivery

**Quality Issues:** Last project had deliverable delays, causing satisfaction to drop from 8.2 to 5.1

Source: [CRM Activity + Project Metrics + AR]

> Synthetic risk indicators; churn probability is decision support, not a prediction.

Next: what about the other at-risk clients?
```

### CHS-07 `stakeholder_outreach`

```markdown
## Stakeholder Outreach Plan

Sarah Mitchell, their new CTO, is priority - she wasn't briefed on our $4.2M value delivery. I've mapped a 4-day executive touchpoint sequence.

**Tuesday - Sarah Mitchell (CTO)**
- Focus: Technical deep dive
- Show: $4.2M cost savings we delivered
- Show: 34% efficiency improvements
- Goal: Rebuild technical credibility

**Wednesday - CFO**
- Focus: ROI review
- Show: Financial impact metrics
- Show: Invoice dispute resolution
- Goal: Close the invoice dispute

**Thursday - Morgan Lee (COO)**
- Focus: Process optimization results
- Show: Operational improvements
- Show: Future roadmap
- Goal: Agree the delivery roadmap

**Friday - CEO**
- Focus: Strategic partnership discussion
- Show: Long-term value proposition
- Goal: Commitment to improved delivery

**Materials Prepared (drafts):** Executive briefing decks, Success dashboards, ROI documentation

Source: [Stakeholder Analysis + Historical Data]

> Synthetic draft sequence; no invitation or message has been sent.

Next: want me to prepare the meeting invites and a session summary?
```

### CHS-08 `qbr_summary`

```markdown
## QBR Session Summary

All 4 stakeholder meetings are drafted as calendar invites, ready for you to send. Here's your complete portfolio analysis and retention plan:

- **Portfolio analysis** - $22.3M value, 71/100 avg score (down 4 points)
- **Risk identification** - $5.1M at risk across 3 clients (23% exposure)
- **TechCorp deep-dive** - 42/100 critical, 78% churn probability
- **Multi-client assessment** - Global 58/100, Healthcare 61/100
- **Retention roadmap** - 30-day TechCorp plan, 73% success probability
- **Outreach ready** - 4 executive meetings drafted, materials prepared

### Value at Stake

- Critical: $2.4M (TechCorp)
- At Risk: $2.7M (Global + Healthcare)
- Healthy: $17.2M (monitor status)

**Retention Investment:** $600K for TechCorp | **ROI if successful:** 300% over 2 years (50% margin on $2.4M a year retained)

**Ready for your approval:** calendar invites, briefing decks, success dashboards, escalation process, CEO briefing for the Day 1 call.

Source: [All Connected Systems]

> Synthetic summary; no meeting, message, concession, renewal, or CRM update has been created.
```
