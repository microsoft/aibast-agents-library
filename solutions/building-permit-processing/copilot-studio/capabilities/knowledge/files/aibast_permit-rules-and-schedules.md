# Building Permit Pilot — Synthetic Rules and Schedules

> SYNTHETIC PILOT DATA. These are fictional standards, schedules, and
> procedures. They are not an adopted municipal code or fee resolution.

## Statutory review targets

| Permit type | Target |
|---|---:|
| new_construction | 30 days |
| residential_addition | 15 days |
| commercial_alteration | 21 days |
| institutional | 45 days |

## Review routing

| Permit type | Desks in order |
|---|---|
| new_construction | Planning → Zoning → Structural → Fire/Life Safety → Public Works |
| residential_addition | Zoning → Structural |
| commercial_alteration | Zoning → Building → Fire/Life Safety |
| institutional | Planning → Zoning → Structural → Fire/Life Safety → Public Works → Health |

## Required intake documents

| Permit type | Required documents |
|---|---|
| new_construction | site_plan, structural_calcs, mep_drawings, title_report |
| residential_addition | site_plan, structural_calcs |
| commercial_alteration | site_plan, mep_drawings |
| institutional | site_plan, structural_calcs, mep_drawings, title_report, traffic_study |

## Duplicate rule

A new submission is a duplicate when another non-approved application has the
same parcel and the same applicant. Recommend that staff not accept it as a new
application and direct the applicant to the existing permit. Do not claim that
the duplicate was closed or changed.

## Zoning reference standards

| District | Maximum height | Front | Side | Rear | Lot coverage | Parking |
|---|---|---:|---:|---:|---:|---|
| R-1 (Single Family Residential) | 35 ft / 2.5 stories | 25 ft | 5 ft | 20 ft | 40% | 2 spaces per unit |
| MU-2 (Mixed Use) | 55 ft / 4 stories | 0 ft | 0 ft | 10 ft | 80% | 1 space per unit + 1 per 500 sq ft commercial |
| I-1 (Light Industrial) | 45 ft / 3 stories | 20 ft | 10 ft | 15 ft | 60% | 1 per 1,000 sq ft |
| PF (Public Facilities) | 50 ft / 3 stories | 30 ft | 15 ft | 20 ft | 50% | Per use determination |

Quote these standards as written. They are not compliance determinations.

## Review checklist templates

Every checklist begins with these five common items, in order:

1. Verify application completeness
2. Confirm property ownership / authorization
3. Zoning compliance verification
4. Setback and height compliance
5. Parking requirement verification

Then append the permit-type items:

- `new_construction`: Structural engineering review; Fire and life safety
  review; Accessibility (ADA) compliance; Stormwater management plan; Utility
  connection approvals; Environmental review (CEQA/NEPA if applicable).
- `residential_addition`: Structural adequacy of existing foundation; Egress
  requirements met; Energy code compliance (Title 24).
- `commercial_alteration`: Electrical load calculation review; Fire alarm
  system impact assessment; Structural load verification.
- `institutional`: Structural engineering review; Fire and life safety review;
  ADA accessibility compliance; School facility standards (DSA if applicable);
  Seismic compliance verification; Hazardous materials assessment.

Totals are 11 items for new construction, 8 for residential addition, 8 for
commercial alteration, and 11 for institutional.

## Synthetic fee schedule

For each category:
`amount = base + (valuation / 1000) × per-thousand rate`, rounded to cents.

| Category | Base | Rate per $1,000 |
|---|---:|---:|
| Plan Review | $250.00 | $4.50 |
| Building Permit | $150.00 | $8.75 |
| Electrical | $75.00 | $1.25 |
| Plumbing | $75.00 | $1.25 |
| Mechanical | $75.00 | $1.00 |
| Fire Review | $200.00 | $2.00 |
| Technology Surcharge | $25.00 | $0.50 |

All seven categories apply in this pilot. The total identity is
`$850 + (valuation / 1000) × $19.25`.

### Precomputed permit totals

| Permit | Valuation | Estimated total |
|---|---:|---:|
| BP-2025-0101 | $4,200,000 | $81,700.00 |
| BP-2025-0102 | $185,000 | $4,411.25 |
| BP-2025-0103 | $320,000 | $7,010.00 |
| BP-2025-0104 | $6,800,000 | $131,750.00 |
| BP-2025-0105 | $4,200,000 | $81,700.00 |
| BP-2025-0106 | $540,000 | $11,245.00 |
