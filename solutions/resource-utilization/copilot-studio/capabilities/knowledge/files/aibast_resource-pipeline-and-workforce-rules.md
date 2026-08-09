# Resource Utilization — Complete Synthetic Pipeline and Workforce Rules

> SYNTHETIC PLANNING DATA. Every probability, role, match, cost, and benefit is
> fictional and is not committed work, staffing, revenue, or forecast.

## Upcoming Project Endings

The capacity forecast includes project endings on or before 2026-06-30:

| Consultant | Project | End Date | Level | Skills shown |
|---|---|---|---|---|
| Lisa Tanaka | Atlas Security Audit | 2026-04-10 | Senior | Cybersecurity, Identity |
| Amanda Foster | Metro Transit Portal | 2026-05-01 | Mid | UX Design, Research |
| Michael Chen | Apex Analytics Platform | 2026-05-15 | Senior | Data Engineering, Databricks |
| Elena Vasquez | TechCorp Transformation | 2026-06-30 | Senior | Cloud Architecture, Azure |

## Complete Pipeline Demand

| Opportunity | Start | Duration | Probability | Exact role needs |
|---|---|---:|---:|---|
| FinanceHub Cloud Migration | 2026-04-01 | 6 months | 85% | 1 Senior Cloud Architecture; 2 Mid DevOps |
| Healthcare Digital Transformation | 2026-04-15 | 12 months | 75% | 1 Manager Program Management; 2 Mid Data Analytics; 1 Junior Business Analysis |
| Retail Analytics Platform | 2026-05-01 | 8 months | 60% | 1 Senior AI/ML; 1 Mid Data Engineering |
| Government Cyber Assessment | 2026-04-01 | 3 months | 90% | 2 Senior Cybersecurity; 1 Mid Compliance |

- Total roles in pipeline: 12
- Bench available: 5

## Deterministic matching rules

1. Consider only consultants whose status is `bench`.
2. Require both exact level and a case-insensitive skill match.
3. Limit matches to the requested count for that need.
4. Do not double-count a consultant in projected utilization.

## Bench-to-Pipeline Matches

| Consultant | Consultant ID | Project | Skill Match | Level | Probability | Start |
|---|---|---|---|---|---:|---|
| David Okafor | CON-404 | Healthcare Digital Transformation | Data Analytics | Mid | 75% | 2026-04-15 |
| James Wright | CON-406 | Healthcare Digital Transformation | Business Analysis | Junior | 75% | 2026-04-15 |
| Chen Wei | CON-410 | Retail Analytics Platform | AI/ML | Senior | 60% | 2026-05-01 |

- Bench cost saved if the three unique matches are approved and deployed:
  $46,000/month.
- Current firm utilization: 43.8%.
- Projected after deployment: 69.6%.
- Target: 85%.

## Unmatched Bench Resources

| Consultant | ID | Level | Skills shown | Deterministic recommendation |
|---|---|---|---|---|
| Sarah Kim | CON-405 | Mid | Cloud Architecture, AWS | Upskill to cloud/AI |
| Robert Garcia | CON-408 | Mid | ERP, D365 | Upskill to cloud/AI |

## Strategic Workforce Plan

### Upskilling Pathways

| Consultant | ID | Path | Duration | Training cost | Target demand | Monthly scenario value |
|---|---|---|---:|---:|---|---:|
| Robert Garcia | CON-408 | D365 integration accelerator | 4 weeks | $3,200 | FinanceHub Cloud Migration integration work | $31,200 |

**Synthetic payback scenario for Robert Garcia:** 0.1 months after billable
deployment begins.

### Innovation and Capability-Building Options

- Robert Garcia: contribute to the D365 integration accelerator while
  completing the pathway.
- Sarah Kim: document reusable Terraform patterns between pipeline staffing
  decisions.
- Chen Wei: prototype an internal AI delivery playbook if the retail
  opportunity does not proceed.

## Required response headings and decision boundaries

- `Resource Utilization Dashboard`
- `Firm utilization`
- `Utilization by Level`
- `Capacity Forecast (Next 90 Days)`
- `Upcoming Project Endings`
- `Pipeline Demand`
- `Total roles in pipeline`
- `Bench Analysis`
- `Skill Inventory on Bench`
- `Staffing Recommendations`
- `Bench-to-Pipeline Matches`
- `Unmatched Bench Resources`
- `Strategic Workforce Plan`
- `Synthetic payback scenario`
- `Innovation and Capability-Building Options`

Every staffing recommendation requires resource-manager confirmation. Never
assign, reserve, deploy, hire, terminate, contact, or change an employment,
project, utilization, training, or revenue record.
