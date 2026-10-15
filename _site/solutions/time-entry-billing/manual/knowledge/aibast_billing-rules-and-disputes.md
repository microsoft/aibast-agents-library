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

### DSP-303 / 78 hrs (period) / MegaCorp Systems

- Status: `client_review_pending`
- Disputed Amount: $23,400 (78 hrs @ $300/hr); Resource: Sarah Chen - Senior Cloud Architect
- Reason: Client claims the architecture work is out of scope for Phase 2.
- Evidence: SOW Section 3.4 "Technical architecture guidance" covers this work; 4 meeting minutes showing client requests; 7 email threads requesting architecture input; Phase 2 deliverables require architecture decisions.
- Root cause: New client PM not briefed on SOW terms
- Recommended Resolution Path: Send the drafted email with SOW references after review; delivery lead to call the PMO director.
- Win probability: 85% (strong contractual basis)

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

## Locked-case evidence contract

| Case | Persona | Operation | Locked prompt | Required evidence |
|---|---|---|---|---|
| TEB-01 | Billing Manager | `unbilled_report` | What billable work is still blocked from this close, and what has to happen before it can move? | TE-9004; TE-9011; Needs approval |
| TEB-02 | Finance Vice President | `billing_summary` | Give me the month-end billing rollup by project and consultant without treating it as posted revenue. | By Project; By Consultant; not posted revenue |
| TEB-03 | Billing Compliance Lead | `time_entry_audit` | Which time cards would fail our billing review because of narrative, hours, rate, or budget concerns? | Missing description; Exceeds 10-hour daily limit; Budget Alert |
| TEB-04 | Billing Manager | `invoice_preparation` | Prepare the invoice support that is actually ready, and keep anything without the right approval or milestone evidence out. | Invoices Ready to Generate; Fixed-fee hold; no invoice was generated |
| TEB-05 | Client Finance Partner | `dispute_resolution` | What evidence is missing on the disputed hours, and what is the safest resolution path before we go back to the clients? | DSP-301; DSP-302; authorized review |
| TEB-06 | Finance Vice President | `month_end_close` | Month-end close is here. We have 15,000 hours logged across all projects that need to be reviewed, approved, and converted to client invoices by tomorrow morning. Can you process the full billing cycle? | 15,247; $2,847,500; 267 hours |
| TEB-07 | Billing Manager | `flagged_review` | Break down the hours that were flagged for review before final approval. | MegaCorp Systems; $892K; 5 projects over 95% budget consumed |
| TEB-08 | Finance Vice President | `budget_overruns` | Show me the budget overruns and write-off exposure. | FinanceHub; RetailCo; $47K recoverable |
| TEB-09 | Billing Manager | `final_invoices` | Bill RetailCo $15K, approve everything else, and generate the final invoices and revenue report. | $2,839,300; $157,800; Deferred: $427,000 |
