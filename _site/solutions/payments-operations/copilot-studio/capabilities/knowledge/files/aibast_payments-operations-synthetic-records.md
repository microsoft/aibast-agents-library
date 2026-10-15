# Payments Operations — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Woodgrove Bank and every payment, originator, beneficiary, rail limit, reference, risk signal, settlement break, and KPI value are invented. The fixed value date is Mar 12, 2026; the prior business day is Mar 11, 2026. Never match them to a real organization, person, or live record.

## Complete synthetic records

Every value the agent uses, exactly as bundled in the portable agent source.

### Bank

```json
"Woodgrove Bank"
```

### Value Date

```json
"Mar 12, 2026"
```

### Prior Date

```json
"Mar 11, 2026"
```

### Rails

```json
{
 "Domestic Instant": {
  "max": 1000000,
  "currencies": [
   "USD"
  ],
  "cutoff": "24x7"
 },
 "Domestic Batch": {
  "max": 5000000,
  "currencies": [
   "USD"
  ],
  "cutoff": "17:00"
 },
 "Domestic High-Value": {
  "max": 50000000,
  "currencies": [
   "USD"
  ],
  "cutoff": "18:00"
 },
 "Cross-Border Wire": {
  "max": 50000000,
  "currencies": [
   "USD",
   "EUR",
   "GBP",
   "JPY"
  ],
  "cutoff": "16:00"
 }
}
```

### Payments

```json
{
 "PAY-3101": {
  "id": "PAY-3101",
  "ref": "E2E-88410",
  "rail": "Domestic Instant",
  "amount": 4850.0,
  "currency": "USD",
  "originator": "Fourth Coffee",
  "beneficiary": "Coho Winery",
  "account": true,
  "stage": "settled",
  "avg": 5200.0,
  "new_beneficiary": false,
  "hour": 9,
  "screen_score": 0.12
 },
 "PAY-3102": {
  "id": "PAY-3102",
  "ref": "E2E-88411",
  "rail": "Domestic Batch",
  "amount": 126400.0,
  "currency": "USD",
  "originator": "Adventure Works",
  "beneficiary": "Adventure Works payroll",
  "account": true,
  "stage": "released",
  "avg": 124000.0,
  "new_beneficiary": false,
  "hour": 7,
  "screen_score": 0.05
 },
 "PAY-3103": {
  "id": "PAY-3103",
  "ref": "E2E-88412",
  "rail": "Cross-Border Wire",
  "amount": 48200.0,
  "currency": "EUR",
  "originator": "Wide World Importers",
  "beneficiary": "Lucerne Publishing",
  "account": true,
  "stage": "scheme_ack",
  "avg": 45000.0,
  "new_beneficiary": false,
  "hour": 8,
  "screen_score": 0.22
 },
 "PAY-3104": {
  "id": "PAY-3104",
  "ref": "E2E-88413",
  "rail": "Domestic High-Value",
  "amount": 2750000.0,
  "currency": "USD",
  "originator": "Alpine Ski House",
  "beneficiary": "Wingtip Toys",
  "account": true,
  "stage": "held_for_review",
  "avg": 310000.0,
  "new_beneficiary": true,
  "hour": 23,
  "screen_score": 0.41
 },
 "PAY-3105": {
  "id": "PAY-3105",
  "ref": "E2E-88414",
  "rail": "Domestic Instant",
  "amount": 1240000.0,
  "currency": "USD",
  "originator": "Proseware",
  "beneficiary": "Trey Research",
  "account": false,
  "stage": "exception",
  "avg": 980000.0,
  "new_beneficiary": false,
  "hour": 10,
  "screen_score": 0.08
 },
 "PAY-3106": {
  "id": "PAY-3106",
  "ref": "E2E-88415",
  "rail": "Cross-Border Wire",
  "amount": 212500.0,
  "currency": "USD",
  "originator": "Margie's Travel",
  "beneficiary": "Litware",
  "account": true,
  "stage": "validated",
  "avg": 198000.0,
  "new_beneficiary": false,
  "hour": 9,
  "screen_score": 0.18
 },
 "PAY-3107": {
  "id": "PAY-3107",
  "ref": "E2E-88410",
  "rail": "Domestic Batch",
  "amount": 18900.0,
  "currency": "USD",
  "originator": "Fourth Coffee",
  "beneficiary": "Coho Winery",
  "account": true,
  "stage": "exception",
  "avg": 5200.0,
  "new_beneficiary": false,
  "hour": 11,
  "screen_score": 0.12
 },
 "PAY-3108": {
  "id": "PAY-3108",
  "ref": "E2E-88417",
  "rail": "Domestic Instant",
  "amount": 920.0,
  "currency": "USD",
  "originator": "Graphic Design Institute",
  "beneficiary": "Lucerne Publishing",
  "account": true,
  "stage": "settled",
  "avg": 1100.0,
  "new_beneficiary": false,
  "hour": 10,
  "screen_score": 0.03
 }
}
```

### Stage Label

```json
{
 "settled": "Settled",
 "released": "Released to scheme",
 "scheme_ack": "Scheme acknowledged",
 "validated": "Validated, awaiting release",
 "held_for_review": "Held for analyst review",
 "exception": "Exception queue"
}
```

### Status Timeline

```json
{
 "PAY-3103": [
  [
   "Ingested",
   "08:02"
  ],
  [
   "Validated",
   "08:03"
  ],
  [
   "Screened",
   "08:05"
  ],
  [
   "Risk checked",
   "08:06"
  ],
  [
   "Released to scheme",
   "08:15"
  ],
  [
   "Scheme acknowledged",
   "08:21"
  ]
 ]
}
```

### Status Expected

```json
{
 "PAY-3103": "Settlement expected by 15:00 on Mar 12, 2026 (beneficiary bank cutoff)"
}
```

### Repair Playbook

```json
{
 "AMOUNT_OVER_RAIL_LIMIT": "Re-route to a rail whose limit covers the amount, or split below the rail limit with originator approval",
 "BENEFICIARY_ACCOUNT_MISSING": "Request the beneficiary account number from the originator through the approved channel",
 "CURRENCY_NOT_ON_RAIL": "Re-route to a rail that carries the currency, or convert before submission with originator approval",
 "DUPLICATE_REFERENCE": "Confirm with the originator whether this is a true duplicate before any resubmission"
}
```

### Priority

```json
{
 "DUPLICATE_REFERENCE": "P1"
}
```

### Screen Threshold

```json
0.85
```

### Recon

```json
{
 "account": "WGB-SETTLE-USD-01",
 "value_date": "Mar 11, 2026",
 "statement_items": 240,
 "matched": 236,
 "breaks": [
  {
   "id": "BRK-01",
   "type": "Amount mismatch",
   "delta": 1250.0,
   "ref": "PAY-2987"
  },
  {
   "id": "BRK-02",
   "type": "Missing on internal ledger",
   "delta": -18400.0,
   "ref": "Statement line 118"
  },
  {
   "id": "BRK-03",
   "type": "Missing on bank statement",
   "delta": 7615.5,
   "ref": "PAY-3011"
  },
  {
   "id": "BRK-04",
   "type": "Amount mismatch",
   "delta": -312.4,
   "ref": "PAY-3046"
  }
 ]
}
```

### Kpi

```json
[
 {
  "rail": "Domestic Instant",
  "volume": 182400,
  "exceptions": 1094
 },
 {
  "rail": "Domestic Batch",
  "volume": 96250,
  "exceptions": 1155
 },
 {
  "rail": "Domestic High-Value",
  "volume": 4120,
  "exceptions": 103
 },
 {
  "rail": "Cross-Border Wire",
  "volume": 7830,
  "exceptions": 352
 }
]
```

### Default Payment

```json
{
 "validate_payment": "PAY-3105",
 "repair_plan": "PAY-3105",
 "release_risk_review": "PAY-3104",
 "payment_status": "PAY-3103"
}
```

## Exact responses for every locked case

### PO-01 — Release queue overview

Prompt: "What's in this morning's payment release queue, and which payments need attention?"

Operation: `queue_overview`; arguments: `{"operation": "queue_overview"}`

**Release Queue: Woodgrove Bank, value date Mar 12, 2026**

| Payment | Originator | Rail | Amount | Stage |
|---|---|---|---|---|
| PAY-3101 | Fourth Coffee | Domestic Instant | USD 4,850.00 | Settled |
| PAY-3102 | Adventure Works | Domestic Batch | USD 126,400.00 | Released to scheme |
| PAY-3103 | Wide World Importers | Cross-Border Wire | EUR 48,200.00 | Scheme acknowledged |
| PAY-3104 | Alpine Ski House | Domestic High-Value | USD 2,750,000.00 | Held for analyst review |
| PAY-3105 | Proseware | Domestic Instant | USD 1,240,000.00 | Exception queue |
| PAY-3106 | Margie's Travel | Cross-Border Wire | USD 212,500.00 | Validated, awaiting release |
| PAY-3107 | Fourth Coffee | Domestic Batch | USD 18,900.00 | Exception queue |
| PAY-3108 | Graphic Design Institute | Domestic Instant | USD 920.00 | Settled |

| Stage | Payments |
|---|---|
| Settled | 2 |
| Released to scheme | 1 |
| Scheme acknowledged | 1 |
| Held for analyst review | 1 |
| Exception queue | 2 |
| Validated, awaiting release | 1 |

**Queue value:** USD 4,353,570.00 plus EUR 48,200.00 across 8 payments.

**Needs attention (3):**
- **PAY-3104** (Held for analyst review): risk band High
- **PAY-3105** (Exception queue): AMOUNT_OVER_RAIL_LIMIT; BENEFICIARY_ACCOUNT_MISSING
- **PAY-3107** (Exception queue): DUPLICATE_REFERENCE

**Next step:** start with PAY-3105 validation, then the PAY-3104 risk review.

Synthetic payments evidence only. This agent does not release, hold, repair, return, or resubmit a payment, contact a customer, or post to a ledger; every decision stays with an authorized payments analyst.

Source: [Synthetic Woodgrove Bank Payments Snapshot]
Agents: PaymentsOperationsAgent

### PO-02 — Scheme-rule validation

Prompt: "Why did payment PAY-3105 fail validation?"

Operation: `validate_payment`; arguments: `{"operation": "validate_payment", "payment_id": "PAY-3105"}`

**Validation: PAY-3105 — Fail**

| Field | Value |
|---|---|
| Originator | Proseware |
| Beneficiary | Trey Research |
| Rail | Domestic Instant |
| Amount | USD 1,240,000.00 |

| Scheme Rule | Result | Detail |
|---|---|---|
| Amount within rail limit | Fail | limit USD 1,000,000.00 |
| Currency carried by rail | Pass | USD |
| Beneficiary account present | Fail | required on every rail |
| Unique end-to-end reference | Pass | E2E-88414 |

**Failure codes (2):**
- `AMOUNT_OVER_RAIL_LIMIT`: Domestic Instant limit is USD 1,000,000.00; payment is USD 1,240,000.00
- `BENEFICIARY_ACCOUNT_MISSING`: Beneficiary account number is blank

**Next step:** ask for the repair plan before any resubmission.

Synthetic payments evidence only. This agent does not release, hold, repair, return, or resubmit a payment, contact a customer, or post to a ledger; every decision stays with an authorized payments analyst.

Source: [Synthetic Woodgrove Bank Payments Snapshot]
Agents: PaymentsOperationsAgent

### PO-03 — Exception repair plan

Prompt: "What's the repair plan for PAY-3105? Don't change anything yet."

Operation: `repair_plan`; arguments: `{"operation": "repair_plan", "payment_id": "PAY-3105"}`

**Repair Plan Draft: PAY-3105 — Not Executed**

| Detail | Value |
|---|---|
| Priority | P2 |
| Failure codes | AMOUNT_OVER_RAIL_LIMIT, BENEFICIARY_ACCOUNT_MISSING |
| Current rail | Domestic Instant |
| Rails that accept this amount and currency | Domestic Batch, Domestic High-Value |
| Assigned queue | Payments repair analysts |

**Proposed repair steps:**
1. **AMOUNT_OVER_RAIL_LIMIT** — Re-route to a rail whose limit covers the amount, or split below the rail limit with originator approval.
2. **BENEFICIARY_ACCOUNT_MISSING** — Request the beneficiary account number from the originator through the approved channel.

**Draft note to originator (Proseware):** "Your payment PAY-3105 for USD 1,240,000.00 could not be processed as submitted. To complete it we need: approval to re-route to Domestic Batch or Domestic High-Value; the beneficiary account number."

Status: Draft for analyst review. No repair, re-route, or message was executed.

Synthetic payments evidence only. This agent does not release, hold, repair, return, or resubmit a payment, contact a customer, or post to a ledger; every decision stays with an authorized payments analyst.

Source: [Synthetic Woodgrove Bank Payments Snapshot]
Agents: PaymentsOperationsAgent

### PO-04 — Pre-release risk review

Prompt: "Is the 2.75 million dollar payment PAY-3104 to Wingtip Toys safe to release?"

Operation: `release_risk_review`; arguments: `{"operation": "release_risk_review", "payment_id": "PAY-3104"}`

**Pre-Release Risk Review: PAY-3104**

| Check | Result |
|---|---|
| Originator -> Beneficiary | Alpine Ski House -> Wingtip Toys |
| Amount | USD 2,750,000.00 on Domestic High-Value |
| Watchlist screening | Clear (best match score 0.41, threshold 0.85) |
| Risk score | 0.85 |
| Risk band | High |

**Risk drivers:**
- Amount is 8.9 times the originator's 90-day average (USD 310,000.00)
- First payment from this originator to this beneficiary
- Submitted out of hours (23:00 local)
- High-value payment above USD 1,000,000.00

**Recommended handling:** Hold for analyst review and call-back to the originator. The release decision belongs to an authorized analyst; the payment was not released or held by this agent.

Synthetic payments evidence only. This agent does not release, hold, repair, return, or resubmit a payment, contact a customer, or post to a ledger; every decision stays with an authorized payments analyst.

Source: [Synthetic Woodgrove Bank Payments Snapshot]
Agents: PaymentsOperationsAgent

### PO-05 — Settlement reconciliation

Prompt: "Reconcile yesterday's USD settlement account. Which breaks are still open?"

Operation: `reconcile_settlement`; arguments: `{"operation": "reconcile_settlement"}`

**Settlement Reconciliation: WGB-SETTLE-USD-01, value date Mar 11, 2026**

| Measure | Value |
|---|---|
| Statement items | 240 |
| Matched | 236 (98.3%) |
| Open breaks | 4 |
| Net difference | USD -9,846.90 |
| Gross break value | USD 27,577.90 |

| Break | Type | Delta | Reference |
|---|---|---|---|
| BRK-01 | Amount mismatch | USD +1,250.00 | PAY-2987 |
| BRK-02 | Missing on internal ledger | USD -18,400.00 | Statement line 118 |
| BRK-03 | Missing on bank statement | USD +7,615.50 | PAY-3011 |
| BRK-04 | Amount mismatch | USD -312.40 | PAY-3046 |

**Work first:** BRK-02 (missing on internal ledger, USD -18,400.00) is the largest break.

Proposed adjustments are drafts only; no ledger entry was posted.

Synthetic payments evidence only. This agent does not release, hold, repair, return, or resubmit a payment, contact a customer, or post to a ledger; every decision stays with an authorized payments analyst.

Source: [Synthetic Woodgrove Bank Payments Snapshot]
Agents: PaymentsOperationsAgent

### PO-06 — Payment status answer

Prompt: "A relationship manager is asking where PAY-3103 is. What should I tell them?"

Operation: `payment_status`; arguments: `{"operation": "payment_status", "payment_id": "PAY-3103"}`

**Payment Status: PAY-3103**

| Detail | Value |
|---|---|
| Current stage | Scheme acknowledged |
| Rail | Cross-Border Wire |
| Amount | EUR 48,200.00 |
| Originator -> Beneficiary | Wide World Importers -> Lucerne Publishing |
| Expected | Settlement expected by 15:00 on Mar 12, 2026 (beneficiary bank cutoff) |

| Stage | Time (Mar 12, 2026) |
|---|---|
| Ingested | 08:02 |
| Validated | 08:03 |
| Screened | 08:05 |
| Risk checked | 08:06 |
| Released to scheme | 08:15 |
| Scheme acknowledged | 08:21 |

**Draft reply to the relationship manager (not sent):** "PAY-3103 for EUR 48,200.00 is at stage 'Scheme acknowledged'. Settlement expected by 15:00 on Mar 12, 2026 (beneficiary bank cutoff). I will confirm once settlement is reported."

Synthetic payments evidence only. This agent does not release, hold, repair, return, or resubmit a payment, contact a customer, or post to a ledger; every decision stays with an authorized payments analyst.

Source: [Synthetic Woodgrove Bank Payments Snapshot]
Agents: PaymentsOperationsAgent

### PO-07 — Daily payments KPI brief

Prompt: "Give me yesterday's payments KPI brief by rail."

Operation: `daily_kpi_brief`; arguments: `{"operation": "daily_kpi_brief"}`

**Daily Payments KPI Brief: Woodgrove Bank, Mar 11, 2026**

| Rail | Volume | Exceptions | Straight-Through Rate |
|---|---|---|---|
| Domestic Instant | 182,400 | 1,094 | 99.40% |
| Domestic Batch | 96,250 | 1,155 | 98.80% |
| Domestic High-Value | 4,120 | 103 | 97.50% |
| Cross-Border Wire | 7,830 | 352 | 95.50% |
| **Total** | **290,600** | **2,704** | **99.07%** |

**Watch item:** Cross-Border Wire has the lowest straight-through rate (95.50%).
**Today's open items:** 2 exceptions (PAY-3105, PAY-3107), 1 payment held for review (PAY-3104), 4 settlement breaks on WGB-SETTLE-USD-01.

Draft brief for the payments operations lead; nothing was distributed.

Synthetic payments evidence only. This agent does not release, hold, repair, return, or resubmit a payment, contact a customer, or post to a ledger; every decision stays with an authorized payments analyst.

Source: [Synthetic Woodgrove Bank Payments Snapshot]
Agents: PaymentsOperationsAgent

## Locked-case evidence contract

| Case | Persona | Prompt | Operation | Must include |
|---|---|---|---|---|
| PO-01 | Payments Operations Lead | What's in this morning's payment release queue, and which payments need attention? | `queue_overview` | Release Queue; PAY-3105; Needs attention |
| PO-02 | Payments Analyst | Why did payment PAY-3105 fail validation? | `validate_payment` | AMOUNT_OVER_RAIL_LIMIT; BENEFICIARY_ACCOUNT_MISSING; Scheme Rule |
| PO-03 | Payments Repair Analyst | What's the repair plan for PAY-3105? Don't change anything yet. | `repair_plan` | Not Executed; Domestic High-Value; Draft for analyst review |
| PO-04 | Payments Analyst | Is the 2.75 million dollar payment PAY-3104 to Wingtip Toys safe to release? | `release_risk_review` | Risk band; 8.9 times; Watchlist screening |
| PO-05 | Reconciliation Analyst | Reconcile yesterday's USD settlement account. Which breaks are still open? | `reconcile_settlement` | WGB-SETTLE-USD-01; BRK-02; 9,846.90 |
| PO-06 | Payments Operations Lead | A relationship manager is asking where PAY-3103 is. What should I tell them? | `payment_status` | Scheme acknowledged; 15:00; not sent |
| PO-07 | Head of Payments Operations | Give me yesterday's payments KPI brief by rail. | `daily_kpi_brief` | 99.07%; Cross-Border Wire; nothing was distributed |

The response for each case must contain every must-include value and must not contain: I do not have access; I cannot help.
