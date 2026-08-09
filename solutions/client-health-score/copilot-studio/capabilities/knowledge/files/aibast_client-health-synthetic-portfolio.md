# Client Health Score — Complete Synthetic Portfolio Records

> SYNTHETIC PILOT DATA. All clients, values, scores, trends, interactions, and
> labels are fictional. This is a frozen portfolio snapshot, not live CRM data.

## Complete client records

| ID | Client | Annual value | Health | NPS | Margin | Utilization | Billing | Escalations 90d | Exec meetings 90d | Q1 | Q2 | Q3 | Q4 | Segment |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| CL-301 | TechCorp Industries | $2,400,000 | 42 | -15 | 18.2% | 64% | declining | 4 | 0 | 8.2 | 7.4 | 6.1 | 5.1 | CRITICAL |
| CL-302 | Global Finance Corp | $1,500,000 | 58 | -20 | 22.5% | 45% | flat | 2 | 1 | 7.8 | 7.2 | 6.5 | 6.0 | AT_RISK |
| CL-303 | Healthcare Solutions Inc | $1,200,000 | 61 | +5 | 26.0% | 72% | flat | 3 | 1 | 8.0 | 7.8 | 7.0 | 6.8 | AT_RISK |
| CL-304 | Apex Manufacturing | $3,200,000 | 91 | +45 | 31.4% | 88% | growing | 0 | 3 | 8.5 | 8.8 | 9.0 | 9.1 | HEALTHY |
| CL-305 | National Logistics Group | $2,800,000 | 84 | +38 | 28.7% | 82% | growing | 1 | 2 | 7.9 | 8.2 | 8.5 | 8.6 | HEALTHY |
| CL-306 | Silverline Retail | $1,900,000 | 75 | +22 | 24.1% | 76% | flat | 1 | 2 | 7.5 | 7.6 | 7.8 | 7.9 | HEALTHY |
| CL-307 | Pinnacle Energy | $3,600,000 | 94 | +52 | 33.0% | 91% | growing | 0 | 4 | 8.8 | 9.0 | 9.2 | 9.3 | HEALTHY |
| CL-308 | Metro Transit Authority | $2,100,000 | 81 | +30 | 27.3% | 79% | growing | 0 | 2 | 7.6 | 7.9 | 8.1 | 8.3 | HEALTHY |

## Portfolio totals

- Portfolio value: $18,700,000
- At-risk value: $5,100,000 (27.3%)
- Average health score: 73.2/100
- Distribution: 1 critical, 2 at-risk, 5 healthy

## Churn Indicator rule

| Health score | Synthetic indicator |
|---|---:|
| 45 or below | 78% |
| 46 through 60 | 45% |
| 61 through 70 | 20% |
| 71 through 80 | 10% |
| Above 80 | 3% |

These are deterministic scenario indicators, not validated predictions or
statements that churn will occur.

## Engagement Analysis and exact red flags

- **TechCorp Industries:** `No executive contact in 90 days`;
  `4 escalations in 90 days`; `Declining billing trend`.
- **Global Finance Corp:** `Low utilization (45%) -- may not see value`.
- **Healthcare Solutions Inc:** `3 escalations in 90 days`.

No other client produces an engagement red flag in the packaged rules.

## Client Satisfaction Trends

Trend is improving when Q4 is more than 0.3 above Q1, declining when Q4 is
more than 0.3 below Q1, and otherwise stable.

### Declining Accounts Requiring Attention

- TechCorp Industries: dropped 3.1 points over 4 quarters; NPS -15; trend DOWN.
- Global Finance Corp: dropped 1.8 points over 4 quarters; NPS -20; trend DOWN.
- Healthcare Solutions Inc: dropped 1.2 points over 4 quarters; NPS +5; trend
  DOWN.

Apex Manufacturing, National Logistics Group, Silverline Retail, Pinnacle
Energy, and Metro Transit Authority have trend UP.
