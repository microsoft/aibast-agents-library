# Building Permit Pilot — Synthetic Records

> SYNTHETIC PILOT DATA. All entities and dates are fictional. The fixed snapshot
> date is 2026-08-07. Do not recalculate relative dates from the current date.

## Permit applications

| Permit ID | Applicant | Address | Parcel | Type | Description | Submitted | Age | Valuation | Zoning | Status | Reviewer | Cycle |
|---|---|---|---|---|---|---|---:|---:|---|---|---|---:|
| BP-2025-0101 | Greenfield Development LLC | 4520 Oak Ridge Blvd | 045-221-009 | new_construction | 3-story mixed-use building — 12 residential units, ground floor retail | 2026-06-20 | 48 days | $4,200,000 | MU-2 (Mixed Use) | plan_review | Karen Whitfield | 2 |
| BP-2025-0102 | Johnson Family Trust | 812 Maple Street | 023-114-003 | residential_addition | 650 sq ft second-story addition to single-family residence | 2026-07-26 | 12 days | $185,000 | R-1 (Single Family Residential) | approved | Tom Delgado | 1 |
| BP-2025-0103 | Sunrise Solar Inc. | 1100 Industrial Pkwy | 067-340-015 | commercial_alteration | Rooftop solar installation — 240 panel array on warehouse | 2026-07-12 | 26 days | $320,000 | I-1 (Light Industrial) | inspection_scheduled | Karen Whitfield | 1 |
| BP-2025-0104 | Metro School District | 2200 Education Way | 034-502-001 | institutional | New gymnasium and cafeteria wing — 18,000 sq ft | 2026-06-05 | 63 days | $6,800,000 | PF (Public Facilities) | corrections_required | Tom Delgado | 3 |
| BP-2025-0105 | Greenfield Development LLC | 4520 Oak Ridge Blvd | 045-221-009 | new_construction | 3-story mixed-use building — 12 residential units, ground floor retail | 2026-08-04 | 3 days | $4,200,000 | MU-2 (Mixed Use) | intake | Unassigned | 0 |
| BP-2025-0106 | Ridgeline Restaurants Inc. | 77 Harbor Way | 012-088-024 | commercial_alteration | Tenant improvement — restaurant fit-out with commercial kitchen | 2026-08-06 | 1 day | $540,000 | MU-2 (Mixed Use) | intake | Unassigned | 0 |

There are 6 applications totaling $16,245,000 in declared valuation. Five are
open; BP-2025-0102 is approved and excluded from the open backlog.

## Fixed review-clock state

| Permit | Target | Snapshot state | Days over | Complaint risk |
|---|---:|---|---:|---:|
| BP-2025-0104 | 45 days | Overdue | 18 | 100/100 |
| BP-2025-0101 | 30 days | Overdue | 18 | 66/100 |
| BP-2025-0103 | 21 days | Overdue | 5 | 25/100 |
| BP-2025-0105 | 30 days | On track | 0 | 0/100 |
| BP-2025-0106 | 21 days | On track | 0 | 0/100 |

The complaint-risk formula represented by this fixed result is:
`max(0, days_over) × 2 + review_cycle × 15`, plus 20 when the status is
`corrections_required`, capped at 100. Approved permits score 0.

## Intake records and duplicate finding

BP-2025-0105 has `site_plan` and `structural_calcs`. It is missing
`mep_drawings` and `title_report`. It is a duplicate of BP-2025-0101 because
the applicant and parcel match an application already in plan review.

BP-2025-0106 has `site_plan`, `structural_calcs`, `mep_drawings`, and
`title_report`. It is complete for commercial-alteration intake. It routes in
this order: Zoning → Building → Fire/Life Safety. Its fixed 21-day target date
is 2026-08-28.

## Applicant update state

- BP-2025-0104 — Metro School District: correction cycle 3; outstanding items
  are with Tom Delgado; 18 days overdue.
- BP-2025-0101 — Greenfield Development LLC: plan review with Karen Whitfield;
  18 days overdue.
- BP-2025-0103 — Sunrise Solar Inc.: next inspection is Electrical Rough-In on
  2026-08-17 with Dave Martinez; 5 days overdue against the review target.
- BP-2025-0105 — Greenfield Development LLC: MEP drawings and title report are
  missing; the review clock has not started.
- BP-2025-0106 — Ridgeline Restaurants Inc.: intake is complete and it is ready
  to enter review; 21-day target date 2026-08-28.

## Inspector roster

| Inspector | Specialty | Available slots | Service zone |
|---|---|---:|---|
| Dave Martinez | Electrical | 3 | East |
| Lisa Park | Structural | 2 | East |
| Carlos Reyes | Plumbing/Mechanical | 4 | West |
| Ann Kowalski | Fire/Life Safety | 2 | All |

## Inspection board

BP-2025-0103 at 1100 Industrial Pkwy is the solar job.

| Inspection | Inspector | Date | Status |
|---|---|---|---|
| Electrical Rough-In | Dave Martinez | 2026-08-17 | Scheduled |
| Structural Mounting | Lisa Park | 2026-08-19 | Scheduled |
| Final Electrical | Dave Martinez | 2026-08-02 | Pending |

No other permit has an inspection in this synthetic schedule.
