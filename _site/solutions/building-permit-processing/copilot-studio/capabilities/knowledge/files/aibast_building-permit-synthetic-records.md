# Building Permit Pilot — Synthetic Records

> SYNTHETIC PILOT DATA. All entities and dates are fictional. The fixed snapshot
> date is 2026-08-07. Do not recalculate relative dates from the current date.

## Permit applications

| Permit ID | Applicant | Address | Parcel | Type | Description | Submitted | Age | Valuation | Zoning | Status | Reviewer | Cycle |
|---|---|---|---|---|---|---|---:|---:|---|---|---|---:|
| BP-2025-0101 | Greenfield Development LLC | 4520 Oak Ridge Blvd | 045-221-009 | new_construction | 3-story mixed-use building — 12 residential units, ground floor retail | 2026-06-20 | 48 days | $4,200,000 | MU-2 (Mixed Use) | plan_review | Karen Whitfield | 2 |
| BP-2025-0102 | Whitaker Family Trust | 812 Maple Street | 023-114-003 | residential_addition | 650 sq ft second-story addition to single-family residence | 2026-07-26 | 12 days | $185,000 | R-1 (Single Family Residential) | approved | Tom Delgado | 1 |
| BP-2025-0103 | Sunrise Solar Inc. | 1100 Industrial Pkwy | 067-340-015 | commercial_alteration | Rooftop solar installation — 240 panel array on warehouse | 2026-07-12 | 26 days | $320,000 | I-1 (Light Industrial) | inspection_scheduled | Karen Whitfield | 1 |
| BP-2025-0104 | Metro School District | 2200 Education Way | 034-502-001 | institutional | New gymnasium and cafeteria wing — 18,000 sq ft | 2026-06-05 | 63 days | $6,800,000 | PF (Public Facilities) | corrections_required | Tom Delgado | 3 |
| BP-2025-0105 | Greenfield Development LLC | 4520 Oak Ridge Blvd | 045-221-009 | new_construction | 3-story mixed-use building — 12 residential units, ground floor retail | 2026-08-04 | 3 days | $4,200,000 | MU-2 (Mixed Use) | intake | Unassigned | 0 |
| BP-2025-0106 | Ridgeline Restaurants Inc. | 77 Harbor Way | 012-088-024 | commercial_alteration | Tenant improvement — restaurant fit-out with commercial kitchen | 2026-08-06 | 1 day | $540,000 | MU-2 (Mixed Use) | intake | Unassigned | 0 |
| BP-2024-3847 | Johnson Residence | 123 Oak Lane | 031-207-018 | residential_addition | 400 sq ft master bedroom + bathroom addition | 2026-08-07 | 0 days (received 15 minutes ago) | $68,000 | R-2 (HOA Residential) | intake | Unassigned | 0 |

There are 7 applications totaling $16,313,000 in declared valuation. Six are
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

## BPP-01 Locked Response

For the exact prompt `Which permit applications have been sitting too long,
and which resident is going to complain first?`, reproduce only the following
reviewed response:

### Permit Backlog and Complaint Risk

**First intervention:** BP-2025-0104 — Metro School District. It is the
highest-priority backlog item and the applicant most likely to call first. The
application is 63 days old against a 45-day target, 18 days overdue, in
correction cycle 3, assigned to Tom Delgado, with complaint risk 100/100.

**Recommended next step:** An authorized reviewer drafts the cycle-3 correction
list and chooses a specific re-review date. This is a recommendation only; no
message, permit update, assignment, or system action occurred.

| Priority | Permit | Applicant | Snapshot state |
|---:|---|---|---|
| 1 | BP-2025-0104 | Metro School District | 18 days overdue |
| 2 | BP-2025-0101 | Greenfield Development LLC | 18 days overdue |
| 3 | BP-2025-0103 | Sunrise Solar Inc. | 5 days overdue |

> Synthetic pilot data as of 2026-08-07; no live municipal system was accessed or changed.

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
- BP-2024-3847 — Johnson Residence: we need hoa_approval before the review
  clock can start.

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
| Final Electrical | Dave Martinez | 2026-08-25 | Pending |

No other permit has an inspection in this synthetic schedule.

## New residential addition walkthrough — BP-2024-3847

BP-2024-3847 is the new residential application ("Johnson", "Johnson Residence", "the Johnson addition" or
"Oak Lane"). It is the default record for the five walkthrough skills; no permit ID is needed. Whitaker Family
Trust (BP-2025-0102, 812 Maple Street) is a different, already approved permit.

### Application intake (BPP-06)

Prompt: "A new residential addition application just came in. Process it and tell me if it is complete."

- New Permit Application — Received 15 minutes ago. Project: Residential Addition. Applicant: Johnson Residence
  (123 Oak Lane). Contractor: Premier Builders LLC (License #BLD-48291). Scope: 400 sq ft master bedroom +
  bathroom addition. Zoning: R-2 (HOA Residential).

| Required Item | Status | Notes |
|---|---|---|
| Site plan | Complete | Verified dimensions |
| Structural drawings | Complete | Stamped by PE |
| Property survey | Complete | Updated 3 months ago |
| Proof of insurance | Complete | Valid through next year |
| HOA approval | Missing | Required for this zone |

- Fee Calculated: $847 (based on $68K project value): $100 + 68 × $10.25 = $797 building permit + $50 technology
  surcharge.
- Recommended action: Application on hold — HOA approval letter needed before plan review begins.

### Code compliance review (BPP-07)

Prompt: "Run the code compliance check on the Johnson addition plans."

Permit #BP-2024-3847 — Plan Review (2.4 minutes). Checked against 247 code requirements across building,
electrical, plumbing, and zoning codes. R-2 (HOA Residential) limits: setbacks 15 ft, lot coverage 35%,
height 25 ft; code rules: bedroom egress 5.7 sq ft minimum opening, 2 bathroom GFCI outlets (NEC 210.8).

| Check | Result | Detail |
|---|---|---|
| Setback requirements | Met | 15 ft all sides (min 15 ft) |
| Lot coverage | Met | 28% (max 35% allowed) |
| Height restrictions | Met | 18 ft (max 25 ft allowed) |
| Egress windows | Flag | Bedroom needs 5.7 sq ft min opening |
| GFCI outlets | Flag | Bathroom plan shows only 1 (need 2) |
| Structural loads | Met | Within limits (stamped by engineer) |

Flags Requiring Correction (2): Egress window specification unclear (provide manufacturer cut sheet); Add
second GFCI outlet near vanity per NEC 210.8. Estimated Resubmission Impact: 1-2 days. These are findings for
the examiner, not a code-compliance certification.

### Plan review routing (BPP-08)

Prompt: "Route the Johnson addition for expert plan review."

| Plans examiner | Title | Specialization | Workload | Avg review | Availability |
|---|---|---|---:|---:|---|
| Mike Chen | Senior Plans Examiner | residential_addition | 8 | 1.2 days | Can start today |
| Tom Delgado | Plans Examiner | residential_addition | 15 | 2.1 days | Next opening in 2 days |
| Karen Whitfield | Senior Plans Examiner | commercial_alteration | 11 | 1.8 days | Can start tomorrow |

- Recommended Primary Reviewer: Mike Chen, Senior Plans Examiner (residential additions; lowest workload,
  8 permits, moderate; 1.2 days average; can start today).
- Review Packet: complete application with markup highlights; code compliance checklist (2 items flagged);
  property history (no prior violations); zoning verification certificate; HOA approval letter (just received).
- Parallel Review: Electrical — Sarah Martinez (same-day review); Plumbing — David Park (same-day review).
- Draft Applicant Notification (not sent): "Your plans are under review. We found 2 minor items needing
  clarification. Reviewer will contact you within 1 business day."

### Approval workflow tracking (BPP-09)

Prompt: "Track the approval workflow for the Johnson addition."

Permit #BP-2024-3847 — Day 3 of Processing. Timeline: Application received (Day 1, done); Completeness verified
(Day 1, done); Code compliance scan (Day 1, done); Plans review assigned (Day 2, done); Corrections requested
(Day 2, current); Revised plans (pending); Final approval (pending); Permit issuance (pending).

- Reviewer Feedback (received today): "Plans look good overall. Need manufacturer specs on egress window and
  updated electrical plan showing second bathroom GFCI. Once resubmitted, can approve same day."
- Contractor Response: Revised plans submitted 2 hours ago.
- Auto-Validation: Both corrections addressed (2 of 2).
- Next Step: Final review scheduled (tomorrow 9 AM).

### Permit issuance package (BPP-10)

Prompt: "Show me the permit issuance package for the Johnson addition."

- Permit #BP-2024-3847 — approved in final review; ready for the building official to issue.
- Total Processing Time: 4.5 days (vs. 18-day baseline) = 75% faster processing; 96% satisfaction rate.
- Permit Package: digital permit card (QR code for inspections); approved plans (digitally stamped); inspection
  schedule (4 required inspections); contractor safety checklist; job site posting requirements.

| Inspection | Timing | Proposed inspector |
|---|---|---|
| Foundation | after excavation | Lisa Park |
| Framing | before drywall | Lisa Park |
| Rough electrical/plumbing | before walls | Dave Martinez |
| Final | before occupancy | Carlos Reyes |

- Draft Citizen Notification (ready to send): "Your permit is approved! Digital permit and plans available in
  your portal. Schedule inspections 24 hours in advance through our mobile app."
- The agent never issues the permit, books an inspection, or sends the notification; staff do.
