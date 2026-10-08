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
- Current sample billable share: 50.0%.
- Projected after deployment: 80.0% (named sample: 5 billable + 3 matched of 10).
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

**Synthetic payback scenario for Robert Garcia:** about 3 days of billable deployment after the pathway.

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

## Deployment pipeline (firm-wide)

23 consultants can deploy immediately through confirmed projects and high-probability pipeline - that's 88% of the
26-person target (23 / 26).

| Tier | Project | Staffing | Consultants |
|---|---|---|---|
| Week 1 Confirmed Starts | TechCorp transformation | 4 senior + 3 mid-level | 7 |
| Week 1 Confirmed Starts | FinanceHub cloud migration | 3 cloud architects | 3 |
| Week 1 Confirmed Starts | RetailCo analytics | 2 data analysts | 2 |
| Week 1 Confirmed Starts | Manufacturing ERP | 3 consultants | 3 |
| High Probability (75%+) | Healthcare digital | 3 mid-level (proposal stage) | 3 |
| High Probability (75%+) | Energy modernization | 2 senior (verbal approval) | 2 |
| High Probability (75%+) | Logistics optimization | 3 analysts (contract review) | 3 |
| Innovation Projects (billable to R&D) | Internal tools development | 3 consultants | 3 |
| Innovation Projects (billable to R&D) | Methodology enhancement | 2 consultants | 2 |
| Innovation Projects (billable to R&D) | Accelerator creation | 2 consultants | 2 |

Total: 30 deployed vs 26 needed = 4 buffer (projected utilization 87%); upskilling track: 4 near certification.

## Upskilling strategy: cloud-architect shadow model

- 5 mid-level infrastructure consultants 80% through cloud certifications: 3 completing cloud certifications
  (12-18 days), 2 completing platform certifications (12-18 days); All have 5+ years infrastructure experience.
- Shadow Model: pair with billable senior cloud architects now; bill at $175/hr (mid-level) immediately; upgrade to
  $250/hr (architect) in 30 days post-cert.
- Client Acceptance: 3 clients pre-approved shadow arrangements.
- Financial Impact: training investment $15K ($15,000, already budgeted); ROI: 580% over 12 months.

## Session summary and dashboard specification

- Session Summary: gap analysis (72% -> 85% requires 26, identified 34 viable); bench breakdown ($264K senior cost
  drain); deployment plan (15 confirmed + 8 pipeline + 7 innovation = 30 total); upskilling (5 cloud architects via
  shadow model in 30 days); financial model ($1.68M monthly, $5.0M quarterly); executive dashboard with weekly
  red/yellow/green status.
- Dashboard Specification (draft for Power BI, not deployed): firm utilization green >= 85%, yellow 80-84%, red < 80%;
  consultants deployed vs plan green >= 30, yellow 26-29, red < 26; bench cost green <= $450K, red > $840K. Monday
  report to leadership is a draft for the user to schedule.

## Locked-case evidence contract

| Case | Persona | Operation | Locked prompt | Required evidence |
|---|---|---|---|---|
| RU-01 | Operations Leader | `utilization_dashboard` | Where are we under target today, and which parts of the workforce are sitting available? | Firm utilization; Bench; Utilization by Level |
| RU-02 | Resource Manager | `capacity_forecast` | What capacity is coming free, and how does it line up with the opportunities expected over the next quarter? | Upcoming Project Endings; Pipeline Demand; Total roles in pipeline |
| RU-03 | Finance Director | `bench_analysis` | Show me who is on the bench, the skills we are carrying, and the cost exposure we need to address. | David Okafor; Robert Garcia; Skill Inventory on Bench |
| RU-04 | Resource Manager | `staffing_recommendation` | Which available consultants fit the strongest pipeline needs, and who still needs another path? | Bench-to-Pipeline Matches; Unmatched Bench Resources; Robert Garcia |
| RU-05 | Operations Leader | `workforce_plan` | Give me an upskilling and internal-innovation plan for the people we cannot place directly, including the business case. | D365 integration accelerator; Synthetic payback scenario; Innovation and Capability-Building Options |
| RU-06 | Operations Leader | `optimization_plan` | Our board wants utilization up to 85% by next quarter. We have 200 consultants currently at 72% billable. I need an optimization plan that shows how we get there without compromising quality. | 144 (72%); $840K; 34 of the 56 |
| RU-07 | Finance Director | `financial_impact` | What is the complete financial impact of this plan by month, quarter, and year? | $1.68M; $20.2M; 8.5% -> 14.2% |
| RU-08 | Operations Leader | `executive_summary` | Create a tracking dashboard and summarize what we accomplished. | Session Summary; Dashboard Specification; red/yellow/green |
