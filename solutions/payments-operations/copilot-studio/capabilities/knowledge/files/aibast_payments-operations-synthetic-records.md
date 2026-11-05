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

### Sanctions Sla Hours

```json
4
```

### Sanctions Alerts

```json
[
 {
  "alert": "SAN-7712",
  "payment": "PAY-3121",
  "amount": 86400.0,
  "currency": "EUR",
  "rail": "Cross-Border Wire",
  "party": "Beneficiary: Tailspin Freight GmbH",
  "entry": "Tailspin Freight Holdings (synthetic list entry)",
  "flag": "Name similarity reported by the screening service",
  "age_hours": 3.2,
  "analyst": "Unassigned",
  "compare": [
   "Registered address and country",
   "Company registration number",
   "Ownership on file"
  ]
 },
 {
  "alert": "SAN-7709",
  "payment": "PAY-3119",
  "amount": 12750.0,
  "currency": "USD",
  "rail": "Cross-Border Wire",
  "party": "Originator: Bellows Marine Supply",
  "entry": "Bellow Marine Services (synthetic list entry)",
  "flag": "Name and country reported by the screening service",
  "age_hours": 1.5,
  "analyst": "R. Castillo",
  "compare": [
   "Country of incorporation",
   "Vessel or trade references in the payment narrative",
   "Prior cleared alerts for this customer"
  ]
 },
 {
  "alert": "SAN-7714",
  "payment": "PAY-3124",
  "amount": 4300.0,
  "currency": "GBP",
  "rail": "Cross-Border Wire",
  "party": "Beneficiary: A. Moreno",
  "entry": "A. Moreno (synthetic list entry)",
  "flag": "Name match reported by the screening service",
  "age_hours": 0.6,
  "analyst": "Unassigned",
  "compare": [
   "Date of birth on file",
   "Nationality on file",
   "Beneficiary bank country"
  ]
 }
]
```

### Limit Warn Pct

```json
80
```

### Nostro Buffer Pct

```json
10
```

### Correspondents

```json
[
 {
  "bank": "Fabrikam Bank (Frankfurt)",
  "nostro": "WGB-NOSTRO-EUR-01",
  "currency": "EUR",
  "limit": 25000000.0,
  "used": 21900000.0,
  "opening": 6200000.0,
  "inflows": 3100000.0,
  "outflows": 8400000.0,
  "min_balance": 1000000.0
 },
 {
  "bank": "Contoso Trust (London)",
  "nostro": "WGB-NOSTRO-GBP-01",
  "currency": "GBP",
  "limit": 15000000.0,
  "used": 7800000.0,
  "opening": 4100000.0,
  "inflows": 900000.0,
  "outflows": 2600000.0,
  "min_balance": 500000.0
 },
 {
  "bank": "Northwind Bank (Tokyo)",
  "nostro": "WGB-NOSTRO-JPY-01",
  "currency": "JPY",
  "limit": 2000000000.0,
  "used": 2010000000.0,
  "opening": 310000000.0,
  "inflows": 40000000.0,
  "outflows": 120000000.0,
  "min_balance": 50000000.0
 }
]
```

### Verify Flags

```json
{
 "PAY-3130": {
  "id": "PAY-3130",
  "customer": "Fourth Coffee",
  "amount": 64800.0,
  "currency": "USD",
  "rail": "Domestic High-Value",
  "beneficiary": "Coho Winery (new account)",
  "flag": "Beneficiary account details changed by an email request two days before payment",
  "flag_source": "Fraud monitoring service",
  "contact_on_file": "Treasury contact, mobile ending 4417",
  "release_cutoff": "18:00"
 }
}
```

### Default Verify

```json
"PAY-3130"
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

### PO-08 — Sanctions review queue

Prompt: "Which sanctions alerts should I review first, and what do I compare?"

Operation: `sanctions_review_queue`; arguments: `{"operation": "sanctions_review_queue"}`

**Sanctions Review Queue: Woodgrove Bank, value date Mar 12, 2026**

| Alert | Payment | Amount | Screened party | Flagged against | Reason given by screening | Time left in 4 h SLA | Analyst |
|---|---|---|---|---|---|---|---|
| SAN-7712 | PAY-3121 | EUR 86,400.00 | Beneficiary: Tailspin Freight GmbH | Tailspin Freight Holdings (synthetic list entry) | Name similarity reported by the screening service | 0.8 h | Unassigned |
| SAN-7709 | PAY-3119 | USD 12,750.00 | Originator: Bellows Marine Supply | Bellow Marine Services (synthetic list entry) | Name and country reported by the screening service | 2.5 h | R. Castillo |
| SAN-7714 | PAY-3124 | GBP 4,300.00 | Beneficiary: A. Moreno | A. Moreno (synthetic list entry) | Name match reported by the screening service | 3.4 h | Unassigned |

**Open alerts:** 3, 2 unassigned. The payments stay held until a compliance analyst records a decision.

**Review first:** SAN-7712 (PAY-3121) has 0.8 h left. Evidence for the analyst to compare against the flagged entry:
- Registered address and country
- Company registration number
- Ownership on file

Flags are shown exactly as the screening service raised them; this agent does no matching of its own and does not clear, confirm, release or report any alert. The compliance analyst decides.

Synthetic payments evidence only. This agent does not release, hold, repair, return, or resubmit a payment, contact a customer, or post to a ledger; every decision stays with an authorized payments analyst.

Source: [Synthetic Woodgrove Bank Payments Snapshot]
Agents: PaymentsOperationsAgent

### PO-09 — Correspondent limits and nostro funding

Prompt: "Are we close to any correspondent limits today, and do any nostro accounts need funding?"

Operation: `correspondent_limits`; arguments: `{"operation": "correspondent_limits"}`

**Correspondent Limits and Nostro Funding: Woodgrove Bank, value date Mar 12, 2026**

| Correspondent | Limit use | Status | Projected nostro close | Minimum balance | Funding needed |
|---|---|---|---|---|---|
| Fabrikam Bank (Frankfurt) | EUR 21,900,000.00 of EUR 25,000,000.00 (87.6%) | Watch | EUR 900,000.00 | EUR 1,000,000.00 | EUR 200,000.00 |
| Contoso Trust (London) | GBP 7,800,000.00 of GBP 15,000,000.00 (52.0%) | Within limit | GBP 2,400,000.00 | GBP 500,000.00 | None |
| Northwind Bank (Tokyo) | JPY 2,010,000,000.00 of JPY 2,000,000,000.00 (100.5%) | Breach | JPY 230,000,000.00 | JPY 50,000,000.00 | None |

Projected close = opening balance + expected inflows - scheduled outflows.

**Needs action:**
- **Fabrikam Bank (Frankfurt):** limit used 87.6%, above the 80% watch level; route large EUR payments with care.
- **WGB-NOSTRO-EUR-01:** projected close EUR 900,000.00 is below the EUR 1,000,000.00 minimum plus 10% buffer. Draft funding request to treasury: EUR 200,000.00.
- **Northwind Bank (Tokyo):** limit used 100.5%; new JPY payments through this correspondent need a limit decision from treasury before release.

Drafts for treasury; no funds were moved, no limit was changed and no payment was held.

Synthetic payments evidence only. This agent does not release, hold, repair, return, or resubmit a payment, contact a customer, or post to a ledger; every decision stays with an authorized payments analyst.

Source: [Synthetic Woodgrove Bank Payments Snapshot]
Agents: PaymentsOperationsAgent

### PO-10 — Customer verification draft

Prompt: "PAY-3130 to Coho Winery was flagged. How should we verify it with the customer?"

Operation: `customer_verification`; arguments: `{"operation": "customer_verification", "payment_id": "PAY-3130"}`

**Customer Verification Draft: PAY-3130**

| Detail | Value |
|---|---|
| Customer | Fourth Coffee |
| Payment | USD 64,800.00 on Domestic High-Value to Coho Winery (new account) |
| Flag | Beneficiary account details changed by an email request two days before payment |
| Raised by | Fraud monitoring service (synthetic flag, shown as provided) |
| Release cutoff | 18:00 |

**Verification journey (draft):**
1. Contact the customer through the Treasury contact, mobile ending 4417; never use contact details from the email request or the payment instruction.
2. Ask the customer to confirm, in their own words, that they requested this payment, the amount, and the beneficiary.
3. Ask how the new beneficiary account details reached them and whether they confirmed them with the beneficiary by phone.
4. Record the answers on the case for the payments analyst.

**Draft in-app message:** "We are holding payment PAY-3130 for USD 64,800.00 to check it with you. We will call your registered number ending 4417. We will never ask for passwords or codes."

**After verification:** the payments analyst decides whether to release or keep the hold; this agent makes no fraud assessment of its own. The payment was not released or held and the customer was not contacted.

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
| PO-08 | Compliance Analyst | Which sanctions alerts should I review first, and what do I compare? | `sanctions_review_queue` | SAN-7712; 0.8 h; The compliance analyst decides |
| PO-09 | Treasury Analyst | Are we close to any correspondent limits today, and do any nostro accounts need funding? | `correspondent_limits` | Northwind Bank (Tokyo); Breach; EUR 200,000.00 |
| PO-10 | Payments Analyst | PAY-3130 to Coho Winery was flagged. How should we verify it with the customer? | `customer_verification` | Fourth Coffee; ending 4417; the payments analyst decides |

The response for each case must contain every must-include value and must not contain: I do not have access; I cannot help.
