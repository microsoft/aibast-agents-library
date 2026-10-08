# Utility Billing and Assistance Agent — Deterministic Rules, Controls, and Locked Evidence

> Use this file with the complete synthetic records. It contains the exact computation rules, output contracts, locked prompts, and canonical strict-isolation tool outputs needed to reproduce the pilot without access to the Python source.

## Deterministic operation rules

1. Accounts resolve from an account ID or a street address (`782 Maple Drive` -> `RES-782MD`); with no account the demo account RES-782MD is used. Unknown IDs return no substitute account.
2. `billing_inquiry` for a smart-meter account shows the current bill and gallons, the typical month, the percentage increase ((current - typical) / typical, rounded: 389%), meter, status and tenure; other accounts show balances and total due = current + past due.
3. `usage_analysis` with daily smart-meter reads finds the leak window (days above 3x the 150 gallon/day baseline): Mar 10-13, 17,500 gallons, 17,500 / 96 hours = 182 gallons per hour. Monthly-only accounts compare the latest month with the average of the first two months for both trend and leak flag (>= 120% = REVIEW POSSIBLE LEAK).
4. `leak_adjustment` (Municipal Code 18.42, one-time): excess = current - typical gallons (17,500); standard charge on the excess = current bill - typical bill ($136.30); adjusted = excess x $2.20 per 1,000 water-only, sewer waived ($38.50); credit $97.80; new bill $86.70 (53%). Draft pending billing-specialist approval.
5. `payment_plan` divides the past-due balance, or for RES-782MD the adjusted bill, across 3, 6, 9 and 12 months; recommended 6 months at 0% interest, first payment April 15 ($14.45).
6. `assistance_programs` screens income against 80% of the $47,650 area median income: LIWAP up to $150/year and LIHEAP one-time $200 when qualified; senior discount also needs age 65+. It uses the account's income on file (RES-782MD: $32,400 = 68% of AMI, total potential relief $350).
6b. `income_screen` applies the same 80% AMI screen to a supplied annual income (and age for the senior discount); the household size only adds the FPL reference line.
7. `application_packet` drafts the payment plan and the LIWAP application: documents, pre-filled fields, 14-day response deadline, online portal.
8. `repair_assistance` returns the Water Conservation Assistance Program items, a proposed (not booked) appointment, $85 value and 6,000 gallons/month savings.
9. `resolution_summary` assembles the package (email and postal mail once approved): credit, plan, LIWAP, LIHEAP, repair, total relief = credit + LIWAP + LIHEAP ($447.80) plus $85 repairs, and a 30-day follow-up.
10. No leak diagnosis, bill adjustment, final eligibility determination, enrollment, payment arrangement, repair order, customer notice, or account change occurs.

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
  "captured_model": "claude-sonnet-5"
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
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[UtilityBillingAssistanceAgent] # Usage Analysis: ACCT-90003

**Customer:** Robert & Linda Thompson
**Usage Trend (vs. first-two-month baseline):** Significantly Increasing

| Period | Water (gal) | Sewer (gal) | Amount |
|---|---|---|---|
| 2024-09 | 8,500 | 7,650 | $145.20 |
| 2024-10 | 9,200 | 8,280 | $152.80 |
| 2024-11 | 12,400 | 11,160 | $198.50 |
| 2024-12 | 14,800 | 13,320 | $232.10 |
| 2025-01 | 13,200 | 11,880 | $215.40 |
| 2025-02 | 11,500 | 10,350 | $189.80 |

## Leak screening

- **Anomaly indicator:** REVIEW POSSIBLE LEAK
- **Baseline used:** 8,850 gallons
- **Latest usage:** 11,500 gallons
- Draft policy estimate: run the leak adjustment once an inspection confirms the excess volume (no hourly smart-meter data on file).

> Screening only. This is not a leak diagnosis, bill adjustment, repair order, or customer notice.
[UtilityBillingAssistanceAgent] # Leak Adjustment Calculation: ACCT-90003

ACCT-90003 has no smart-meter leak window on file; a field inspection is required before a Municipal Code 18.42 adjustment can be calculated.

> Draft for authorized utility staff. No bill was adjusted, no credit applied, no plan created, no application submitted, no repair scheduled, and nothing was sent to the customer.
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
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[UtilityBillingAssistanceAgent] # Draft Payment Plan Options: ACCT-90003

**Past Due Balance:** $489.20

**Recommended:** 6 months at $81.53/month (0% interest), first payment April 15

| Installments | Monthly Payment | Total |
|---|---|---|
| 3 months | $163.07 | $489.20 |
| 6 months | $81.53 | $489.20 |
| 9 months | $54.36 | $489.20 |
| 12 months | $40.77 | $489.20 |

## Payment Plan Requirements

- Any residential customer with a balance due
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
  "prompt": "What assistance programs could help the Maple Drive resident on a fixed income, and do they qualify?",
  "canonical_kwargs": {
    "operation": "assistance_programs",
    "account_id": "RES-782MD"
  },
  "must_include": [
    "POTENTIALLY ELIGIBLE",
    "No eligibility determination",
    "enrollment"
  ],
  "expected_agent": "UtilityBillingAssistanceAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[UtilityBillingAssistanceAgent] # Utility Assistance Programs - Preliminary Screening

| Program | Eligibility | Benefit |
|---|---|---|
| Low-Income Water Assistance Program (LIWAP) | Household income at or below 80% of area median income | Up to $150/year utility credit |
| LIHEAP Emergency Utility Fund | Household income at or below 80% of area median income | One-time $200 grant |
| Senior Citizen Rate Discount | Age 65+ and income at or below 80% of area median income | 25% rate discount |
| Extended Payment Arrangement | Any residential customer with a balance due | Up to 12 interest-free installments |

Area median income (synthetic): $47,650; programs use the 80% AMI limit.

## Eligibility status: RES-782MD (782 Maple Drive) - POTENTIALLY ELIGIBLE - qualifies for multiple programs

- **Household Income:** $32,400 (estimated from property tax records)
- **Area Median Income:** 68% of AMI - qualifies
- **LIWAP Eligibility:** Up to $150/year utility credit
- **LIHEAP Emergency Fund:** One-time $200 grant available
- **Payment Plan Option:** 6 months at $14.45/month (0% interest)
- **Senior Discount:** Not applicable (resident age 42)
- **Total Potential Relief:** $350 ($150 + $200)

Next: set up the payment plan and start the LIWAP application?

> Screening only. No eligibility determination, application, enrollment, payment plan, or repair appointment has been completed.
```

### UTILITY_BILLING_ASSISTANCE-05 — Leak Adjustment Analyst — `leak_adjustment`

```json
{
  "case_id": "UTILITY_BILLING_ASSISTANCE-05",
  "persona": "Leak Adjustment Analyst",
  "operation": "leak_adjustment",
  "prompt": "Does the Maple Drive household qualify for a leak credit, and how much would it be?",
  "canonical_kwargs": {
    "operation": "leak_adjustment",
    "account_id": "RES-782MD"
  },
  "must_include": [
    "Municipal Code 18.42",
    "$97.80",
    "No bill was adjusted"
  ],
  "expected_agent": "UtilityBillingAssistanceAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[UtilityBillingAssistanceAgent] # Billing Inquiry: RES-782MD

**Account Usage Analysis - Status: Investigating Consumption Anomaly**

- **Account Number:** RES-782MD
- **Property Address:** 782 Maple Drive (single-family residence)
- **Current Bill Amount:** $184.50 for 22,000 gallons (Feb 24 - Mar 28)
- **Typical Monthly:** $48.20 for 4,500 gallons
- **Percentage Increase:** 389% above 12-month baseline
- **Meter Type:** Smart meter - hourly data available
- **Account Status:** Current - no payment issues
- **Customer Tenure:** 8 years at this address

Next: pull the hourly smart-meter data to see when the water was used?

> Read-only synthetic account view. No balance, payment, service, or account record was changed.
[UtilityBillingAssistanceAgent] # Leak Adjustment Calculation: RES-782MD

**Status:** Qualifies under Municipal Code 18.42 - draft credit pending billing-specialist approval (not applied)

**Policy:** One-time leak adjustment per household. Excess volume above the 12-month typical usage is re-billed at the water-only rate and sewer charges on the excess are waived, because the leaked water did not enter the sewer system.

- **Excess Water Volume:** 17,500 gallons above the 12-month baseline
- **Standard charge on the excess:** $136.30 (water + sewer)
- **Adjusted charge:** $38.50 at the water-only rate of $2.20 per 1,000 gallons (sewer waived)
- **Credit Amount:** $97.80
- **New Bill Total:** $86.70 (from $184.50, 53% reduction)
- **Repair Proof Required:** within 30 days (receipt or invoice)
- **Policy Limitation:** one-time use only

Next: check assistance programs if the adjusted bill is still hard to pay?

> Draft for authorized utility staff. No bill was adjusted, no credit applied, no plan created, no application submitted, no repair scheduled, and nothing was sent to the customer.
```

### UTILITY_BILLING_ASSISTANCE-06 — Enrollment Specialist — `application_packet`

```json
{
  "case_id": "UTILITY_BILLING_ASSISTANCE-06",
  "persona": "Enrollment Specialist",
  "operation": "application_packet",
  "prompt": "Get the payment plan and the water-assistance application ready for the Maple Drive resident. What paperwork do they need?",
  "canonical_kwargs": {
    "operation": "application_packet",
    "account_id": "RES-782MD"
  },
  "must_include": [
    "$14.45",
    "Proof of income",
    "14-day response deadline"
  ],
  "expected_agent": "UtilityBillingAssistanceAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[UtilityBillingAssistanceAgent] # Payment Plan and LIWAP Application Packet (Draft): RES-782MD

**Payment plan - ready for billing staff to set up in the billing system:**
- 6 months at $14.45/month (0% interest) on $86.70, first payment April 15

**LIWAP application - documents the resident needs:**
- Proof of income - recent pay stubs or last year's tax return
- Copy of lease or property deed showing residency

**Pre-filled application fields:**
- Account: RES-782MD; service address: 782 Maple Drive
- Household income (estimate): $32,400 (estimated from property tax records; resident confirms)

**Delivery:** application forms ready to email with a 14-day response deadline; the resident submits everything through the online assistance portal.

Next: check repair assistance to fix the leak?

> Draft for authorized utility staff. No bill was adjusted, no credit applied, no plan created, no application submitted, no repair scheduled, and nothing was sent to the customer.
```

### UTILITY_BILLING_ASSISTANCE-07 — Water Conservation Coordinator — `repair_assistance`

```json
{
  "case_id": "UTILITY_BILLING_ASSISTANCE-07",
  "persona": "Water Conservation Coordinator",
  "operation": "repair_assistance",
  "prompt": "Can we help the Maple Drive resident fix the leak at no cost?",
  "canonical_kwargs": {
    "operation": "repair_assistance",
    "account_id": "RES-782MD"
  },
  "must_include": [
    "Water Conservation Assistance Program",
    "Toilet flapper",
    "not booked"
  ],
  "expected_agent": "UtilityBillingAssistanceAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[UtilityBillingAssistanceAgent] # Leak Adjustment Calculation: RES-782MD

**Status:** Qualifies under Municipal Code 18.42 - draft credit pending billing-specialist approval (not applied)

**Policy:** One-time leak adjustment per household. Excess volume above the 12-month typical usage is re-billed at the water-only rate and sewer charges on the excess are waived, because the leaked water did not enter the sewer system.

- **Excess Water Volume:** 17,500 gallons above the 12-month baseline
- **Standard charge on the excess:** $136.30 (water + sewer)
- **Adjusted charge:** $38.50 at the water-only rate of $2.20 per 1,000 gallons (sewer waived)
- **Credit Amount:** $97.80
- **New Bill Total:** $86.70 (from $184.50, 53% reduction)
- **Repair Proof Required:** within 30 days (receipt or invoice)
- **Policy Limitation:** one-time use only

Next: check assistance programs if the adjusted bill is still hard to pay?

> Draft for authorized utility staff. No bill was adjusted, no credit applied, no plan created, no application submitted, no repair scheduled, and nothing was sent to the customer.
[UtilityBillingAssistanceAgent] # Water Conservation Assistance Program: RES-782MD

**Status:** Customer qualifies - free services available

- **Free Repairs Offered:** Toilet flapper, faucet aerators, leak detection
- **Additional Items:** Low-flow showerhead, leak detection dye tablets
- **Proposed Appointment:** Tuesday, April 2 (1:00-3:00 PM window) - confirm availability with the resident (not booked)
- **Service Provider:** City Maintenance - licensed plumber
- **Estimated Water Savings:** 6,000 gallons/month after repairs
- **Program Value:** $85 in free parts and labor
- **Eligibility:** Income-qualified residents (based on LIWAP income qualification)

Next: prepare the complete assistance package for the resident?

> Draft for authorized utility staff. No bill was adjusted, no credit applied, no plan created, no application submitted, no repair scheduled, and nothing was sent to the customer.
```

### UTILITY_BILLING_ASSISTANCE-08 — Customer Resolution Manager — `resolution_summary`

```json
{
  "case_id": "UTILITY_BILLING_ASSISTANCE-08",
  "persona": "Customer Resolution Manager",
  "operation": "resolution_summary",
  "prompt": "Pull everything together for the Maple Drive resident so we can send it and close out the account notes.",
  "canonical_kwargs": {
    "operation": "resolution_summary",
    "account_id": "RES-782MD"
  },
  "must_include": [
    "Complete Assistance Package (Draft)",
    "$447.80",
    "nothing was sent"
  ],
  "expected_agent": "UtilityBillingAssistanceAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[UtilityBillingAssistanceAgent] # Complete Assistance Package (Draft): RES-782MD

Package for the customer at 782 Maple Drive, ready to send by email and postal mail once a billing specialist approves.

**Account actions to record after approval:**
- $97.80 leak adjustment credit (Municipal Code 18.42); new bill $86.70
- 6-month payment plan at $14.45/month starting April 15
- LIWAP application in progress (documents due within 14 days)
- LIHEAP emergency fund information provided
- Free plumbing repair appointment proposed for Tuesday, April 2 (1:00-3:00 PM window)

**Total customer financial relief:** $447.80 ($97.80 credit + $150 LIWAP + $200 LIHEAP), plus $85 in free repairs
**Follow-up:** flag the account for a 30-day follow-up (repair proof due)

> Draft for authorized utility staff. No bill was adjusted, no credit applied, no plan created, no application submitted, no repair scheduled, and nothing was sent to the customer.
```

### UTILITY_BILLING_ASSISTANCE-09 — Eligibility Screener — `income_screen`

```json
{
  "case_id": "UTILITY_BILLING_ASSISTANCE-09",
  "persona": "Eligibility Screener",
  "operation": "income_screen",
  "prompt": "Screen a two-person household earning 25000 with a 70-year-old applicant.",
  "canonical_kwargs": {
    "operation": "income_screen",
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
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[UtilityBillingAssistanceAgent] # Utility Assistance Programs - Preliminary Screening

| Program | Eligibility | Benefit |
|---|---|---|
| Low-Income Water Assistance Program (LIWAP) | Household income at or below 80% of area median income | Up to $150/year utility credit |
| LIHEAP Emergency Utility Fund | Household income at or below 80% of area median income | One-time $200 grant |
| Senior Citizen Rate Discount | Age 65+ and income at or below 80% of area median income | 25% rate discount |
| Extended Payment Arrangement | Any residential customer with a balance due | Up to 12 interest-free installments |

Area median income (synthetic): $47,650; programs use the 80% AMI limit.

## Applicant screening

- Household income: $25,000 = 52% of AMI
- Federal poverty level reference (2-person household): $21,150
- LIWAP / LIHEAP income screen: POTENTIALLY ELIGIBLE
- Senior discount screen: POTENTIALLY ELIGIBLE

> Screening only. No eligibility determination, application, enrollment, payment plan, or repair appointment has been completed.
```

## Response completion checklist

- The selected operation matches the persona question.
- Every required identifier and value appears exactly as recorded.
- The relevant synthetic-data limitation is explicit.
- The authorized reviewer and no-write boundary are explicit.
- No unsupported live-system action or customer outcome is claimed.
