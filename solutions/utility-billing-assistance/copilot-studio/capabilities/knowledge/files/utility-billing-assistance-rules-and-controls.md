# Utility Billing and Assistance Agent — Deterministic Rules, Controls, and Locked Evidence

> Use this file with the complete synthetic records. It contains the exact computation rules, output contracts, locked prompts, and canonical strict-isolation tool outputs needed to reproduce the pilot without access to the Python source.

## Deterministic operation rules

1. `billing_inquiry` emits `# Billing Inquiry: <account>` and calculates total due as current charges + past due. Unknown IDs return no substitute account.
2. Usage trend compares the latest month with the average of all prior months: above 120% is significantly increasing, above 105% slightly increasing, below 80% significantly decreasing, below 95% slightly decreasing, otherwise stable.
3. `usage_analysis` uses the first two months as the leak baseline. A possible leak is flagged when latest usage is at least 120% of baseline.
4. Draft leak credit is excess gallons / 1,000 multiplied by the residential highest-tier rate ($14.00) and the 50% policy rate. ACCT-90003 baseline is 8,850 gallons, latest is 11,500, and draft credit is $18.55.
5. `payment_plan` divides exact past-due balance across 3, 6, 9, and 12 months, rounded to cents; current charges continue accruing.
6. `assistance_programs` uses the exact 2025 FPL reference table. LIHWAP screen is income at or below 150% FPL. Senior screen also requires age 65+ and income at or below 200% FPL.
7. No leak diagnosis, bill adjustment, final eligibility determination, enrollment, payment arrangement, repair order, customer notice, or account change occurs.

## Shared authorization controls

1. Use only the uploaded synthetic records and operation skills.
2. Lead with the exact source-backed identifier, value, status, and output heading.
3. Preserve uncertainty and distinguish screening, recommendation, estimate, or draft from an authorized decision.
4. Never invent a missing record, value, approval, notification, filing, assignment, transaction, or side effect.
5. Production reads require approved least-privilege connections. Any future write requires role authorization, current-state validation, explicit human confirmation, error handling, and immutable audit logging.
6. Public value statements remain qualitative; exact numbers are synthetic evidence only.

## Locked persona cases and canonical tool evidence

### UTILITY_BILLING_ASSISTANCE-01 — Customer Service Representative — `billing_inquiry`

```json
{
  "case_id": "UTILITY_BILLING_ASSISTANCE-01",
  "persona": "Customer Service Representative",
  "operation": "billing_inquiry",
  "prompt": "Explain ACCT-90003 balances without changing the account.",
  "canonical_kwargs": {
    "operation": "billing_inquiry",
    "account_id": "ACCT-90003"
  },
  "must_include": [
    "ACCT-90003",
    "$489.20",
    "No balance"
  ],
  "expected_agent": "UtilityBillingAssistanceAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[UtilityBillingAssistanceAgent] # Billing Inquiry: ACCT-90003

- **Customer:** Robert & Linda Thompson
- **Address:** 887 Willow Creek Dr
- **Account Type:** Residential
- **Services:** Water, Sewer, Stormwater, Trash
- **Status:** Delinquent
- **Current Charges:** $245.80
- **Past Due:** $489.20
- **Total Due:** $735.00
- **Auto-Pay:** No
- **Last Payment:** $135.00 on 2024-11-18

> Read-only synthetic account view. No balance, payment, service, or account record was changed.
```

### UTILITY_BILLING_ASSISTANCE-02 — Billing Specialist — `usage_analysis`

```json
{
  "case_id": "UTILITY_BILLING_ASSISTANCE-02",
  "persona": "Billing Specialist",
  "operation": "usage_analysis",
  "prompt": "Does ACCT-90003 show a possible leak and what draft adjustment evidence is needed?",
  "canonical_kwargs": {
    "operation": "usage_analysis",
    "account_id": "ACCT-90003"
  },
  "must_include": [
    "REVIEW POSSIBLE LEAK",
    "Draft policy estimate",
    "not a leak diagnosis"
  ],
  "expected_agent": "UtilityBillingAssistanceAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[UtilityBillingAssistanceAgent] # Usage Analysis: ACCT-90003

**Customer:** Robert & Linda Thompson
**Usage Trend:** Stable

| Period | Water (gal) | Sewer (gal) | Amount |
|---|---|---|---|
| 2024-09 | 8,500 | 7,650 | $145.20 |
| 2024-10 | 9,200 | 8,280 | $152.80 |
| 2024-11 | 12,400 | 11,160 | $198.50 |
| 2024-12 | 14,800 | 13,320 | $232.10 |
| 2025-01 | 13,200 | 11,880 | $215.40 |
| 2025-02 | 11,500 | 10,350 | $189.80 |

**Avg Monthly Water Usage:** 11,600 gallons
**Avg Monthly Bill:** $188.97

## Leak-adjustment screening

- **Anomaly indicator:** REVIEW POSSIBLE LEAK
- **Baseline used:** 8,850 gallons
- **Latest usage:** 11,500 gallons
- **Draft policy estimate:** $18.55, pending repair evidence and billing-specialist approval
- Required: Documented repair invoice or utility inspection
- Required: No unresolved leak adjustment in the prior 24 months
- Required: Billing specialist approval

## Rate Structure

### Water Residential

Base Charge: $18.50

- 0-3,000 gal: $4.25/1,000 gal
- 3,001-6,000 gal: $6.50/1,000 gal
- 6,001-10,000 gal: $9.75/1,000 gal
- Over 10,000 gal: $14.00/1,000 gal

### Water Commercial

Base Charge: $45.00

- 0-10,000 gal: $5.80/1,000 gal
- 10,001-50,000 gal: $5.25/1,000 gal
- Over 50,000 gal: $4.90/1,000 gal

### Sewer

Base: $12.75, Rate: $5.10/1,000 gal

### Stormwater


### Trash



> Screening and estimate only. This is not a leak diagnosis, bill adjustment, repair order, or customer notice.
```

### UTILITY_BILLING_ASSISTANCE-03 — Revenue Services Supervisor — `payment_plan`

```json
{
  "case_id": "UTILITY_BILLING_ASSISTANCE-03",
  "persona": "Revenue Services Supervisor",
  "operation": "payment_plan",
  "prompt": "Show ACCT-90003 payment-plan options, but do not set one up.",
  "canonical_kwargs": {
    "operation": "payment_plan",
    "account_id": "ACCT-90003"
  },
  "must_include": [
    "12 months",
    "No payment arrangement was created"
  ],
  "expected_agent": "UtilityBillingAssistanceAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[UtilityBillingAssistanceAgent] # Draft Payment Plan Options: ACCT-90003

**Customer:** Robert & Linda Thompson
**Past Due Balance:** $489.20

## Installment Options

| Installments | Monthly Payment | Total |
|---|---|---|
| 3 months | $163.07 | $489.20 |
| 6 months | $81.53 | $489.20 |
| 9 months | $54.36 | $489.20 |
| 12 months | $40.77 | $489.20 |

*Note: Current charges continue to accrue during payment plan.*

## Payment Plan Requirements

- Any customer with past-due balance over $100
- Maximum installments: 12
- Documents required: Signed payment agreement

> Options only. No payment arrangement was created; authorized billing staff and the customer must approve it.
```

### UTILITY_BILLING_ASSISTANCE-04 — Assistance Coordinator — `assistance_programs`

```json
{
  "case_id": "UTILITY_BILLING_ASSISTANCE-04",
  "persona": "Assistance Coordinator",
  "operation": "assistance_programs",
  "prompt": "Screen a two-person household earning 25000 with a 70-year-old applicant.",
  "canonical_kwargs": {
    "operation": "assistance_programs",
    "household_size": 2,
    "annual_income": 25000,
    "age": 70
  },
  "must_include": [
    "POTENTIALLY ELIGIBLE",
    "No eligibility determination",
    "enrollment"
  ],
  "expected_agent": "UtilityBillingAssistanceAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[UtilityBillingAssistanceAgent] # Utility Assistance Programs — Preliminary Screening

## Low-Income Household Water Assistance Program

- **Eligibility:** Household income at or below 150% FPL
- **Maximum Benefit:** $1,500
- **Status:** Accepting Applications
- **Documents Required:**
  - Proof of income
  - Utility bill
  - ID
  - Household size verification

## Senior Citizen Rate Discount

- **Eligibility:** Age 65+ and income at or below 200% FPL
- **Discount:** 25%
- **Status:** Accepting Applications
- **Documents Required:**
  - Proof of age
  - Proof of income
  - Utility account number

## COVID-19 Arrearage Forgiveness Program

- **Eligibility:** Past-due balance accrued during March 2020 - December 2023
- **Maximum Benefit:** $3,000
- **Status:** Limited Funds
- **Documents Required:**
  - Utility account statement
  - Income verification

## Extended Payment Arrangement

- **Eligibility:** Any customer with past-due balance over $100
- **Status:** Always Available
- **Documents Required:**
  - Signed payment agreement

## Federal Poverty Level Reference (2025)

| Household Size | 100% FPL | 150% FPL | 200% FPL |
|---|---|---|---|
| 1 | $15,650 | $23,475 | $31,300 |
| 2 | $21,150 | $31,725 | $42,300 |
| 3 | $26,650 | $39,975 | $53,300 |
| 4 | $32,150 | $48,225 | $64,300 |
| 5 | $37,650 | $56,475 | $75,300 |

## Applicant screening

- LIHWAP income screen: POTENTIALLY ELIGIBLE
- Senior discount screen: POTENTIALLY ELIGIBLE

> Screening only. No eligibility determination, application, enrollment, payment plan, or repair appointment has been completed.
```

## Response completion checklist

- The selected operation matches the persona question.
- Every required identifier and value appears exactly as recorded.
- The relevant synthetic-data limitation is explicit.
- The authorized reviewer and no-write boundary are explicit.
- No unsupported live-system action or customer outcome is claimed.
