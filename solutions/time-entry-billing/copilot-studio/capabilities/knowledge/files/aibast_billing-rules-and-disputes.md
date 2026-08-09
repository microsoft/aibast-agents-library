# Time Entry and Billing — Complete Synthetic Rules, Outputs, and Disputes

> SYNTHETIC INTERNAL POLICY. No accounting, PSA, ERP, invoice, email, or client
> system is connected.

## Time-entry audit rules

1. Every billable entry requires a factual description and approval.
2. An empty description produces `Missing description`.
3. Hours above the configured 10-hour daily limit produce
   `Exceeds 10-hour daily limit`.
4. A rate may equal the configured standard or overtime rate. Any other
   billable rate is a non-standard-rate flag.
5. The deterministic flagged entries are:
   - TE-9004 — Michael Chen — 2026-03-11 — 8.0 hours — $260 —
     `Missing description`.
   - TE-9011 — Elena Vasquez — 2026-03-12 — 11.0 hours — $412 —
     `Exceeds 10-hour daily limit`.
6. Budget status is CRITICAL at or above 95%, WARNING at or above 80%, and OK
   below 80%. The canonical `Budget Alert` results are TechCorp Transformation
   WARNING, Atlas Security Audit WARNING, and all other packaged client
   projects OK.

## Unbilled Hours Report rules

- A billable entry is unbilled when it is not approved.
- TE-9004 is worth $2,080.00 and must say
  `Needs approval; missing description`.
- TE-9011 is worth $4,532.00 and must say `Needs approval`.
- Combined unbilled value is $6,612.00.
- Outstanding invoice rows are INV-2026-203, INV-2026-204, and INV-2026-205.

## Billing Summary canonical breakdown

### By Project

| Project | Hours | Billable value |
|---|---:|---:|
| TechCorp Transformation | 28.5 | $9,344.50 |
| Apex Analytics Platform | 15.5 | $4,030.00 |
| Pinnacle Energy ERP | 18.0 | $5,580.00 |
| Atlas Security Audit | 14.5 | $4,205.00 |
| Metro Transit Portal | 8.0 | $1,320.00 |

### By Consultant

| Consultant | Hours | Billable value | Average rate |
|---|---:|---:|---:|
| Elena Vasquez | 28.5 | $9,344.50 | $327.88 |
| Priya Sharma | 18.0 | $5,580.00 | $310.00 |
| Lisa Tanaka | 14.5 | $4,205.00 | $290.00 |
| Michael Chen | 15.5 | $4,030.00 | $260.00 |
| Amanda Foster | 8.0 | $1,320.00 | $165.00 |

Amounts are not posted revenue.

## Invoice Preparation rules

Only approved billable T&M entries may appear under
`Invoices Ready to Generate`.

| Project | Client | Included entries | Hours | Draft invoice amount |
|---|---|---:|---:|---:|
| TechCorp Transformation | TechCorp Industries | 2 | 17.5 | $4,812.50 |
| Apex Analytics Platform | Apex Manufacturing | 1 | 7.5 | $1,950.00 |
| Atlas Security Audit | Atlas Financial Group | 2 | 14.5 | $4,205.00 |
| Metro Transit Portal | Metro Transit Authority | 1 | 8.0 | $1,320.00 |

- Grand total ready to invoice: $12,287.50.
- Pending approval and excluded: $6,612.00.
- **Fixed-fee hold:** Pinnacle Energy ERP time is retained as delivery
  evidence; invoice value requires the contractual milestone schedule.
- This is draft support only; no invoice was generated, posted, or sent.

## Complete disputes

### DSP-301 / TE-9004 / Apex Manufacturing

- Status: `evidence_required`
- Reason: Work description is missing, so the client cannot validate the
  charge.
- Evidence gap: Project assignment and time record exist; consultant narrative
  and manager approval are missing.
- Recommended Resolution Path: Return to Michael Chen for a factual
  description, then route to the project manager for approval.

### DSP-302 / TE-9011 / TechCorp Industries

- Status: `approval_required`
- Reason: Premium-rate migration work requires written cutover authorization.
- Evidence gap: The entry uses the configured overtime rate, but approval is
  not attached.
- Recommended Resolution Path: Attach the approved cutover authorization and
  obtain billing-manager sign-off before invoicing.

## Required response headings and decision boundaries

- `Unbilled Hours Report`
- `Outstanding Invoices`
- `Billing Summary`
- `By Project`
- `By Consultant`
- `Time Entry Audit Report`
- `Budget Alert`
- `Invoice Preparation`
- `Invoices Ready to Generate`
- `Fixed-fee hold`
- `Disputed Hours Resolution Brief`
- `Recommended Resolution Path`

Never invent a narrative, alter hours, classify work, grant approval, post or
recognize revenue, generate or send an invoice, waive a charge, or contact a
client without authorized review.
