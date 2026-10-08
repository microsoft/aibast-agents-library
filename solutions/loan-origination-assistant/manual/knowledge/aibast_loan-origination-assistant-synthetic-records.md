# Loan Origination Assistant — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/loan_origination_assistant_stack/loan_origination_assistant_agent.py`
- Source SHA-256: `d3e2afe777a589b97855fc4a0f84de71270741611e881dfe7d133cb01ded5dec`
- Expected tool: `LoanOriginationAssistantAgent`
- Snapshot behavior: fixed to the packaged source revision; no live connection or current-data claim.

## Demo file walkthrough (LA-2025-4001, the default file)

The demo loan officer works the Martinez purchase file. When no file is named, every file-level operation uses LA-2025-4001.

| Step | Operation | Key values |
|---|---|---|
| 1. Process the application | `application_intake` | Michael & Sarah Martinez; 1234 Oak Lane, $485K purchase; $388K loan (20% down); scores 742 / 738; documents Income 90% (missing 1 paystub), Assets 100%, Credit 100%, Property 80% (appraisal ordered, 5 days); 22 of 24 documents = 92% documentation complete; Michael 8 yrs, Sarah 5 yrs; $145K assets verified |
| 2. Eligible programs | `program_comparison` | Conventional 30-yr 6.875% $2,549 P&I fit 98% (recommended); Conventional 15-yr 6.375% $3,353 fit 95%; FHA 30-yr 7.125% $2,614 fit 100%; no PMI; DTI 28% vs 43% max; reserves 9.2 months vs 6; 15-day close possible |
| 3. Credit and property | `credit_analysis` | Scores 742 / 738; 0 late payments; utilization 18%; DTI front 28% / back 36%; income $14,200/month; PITI $3,954 (P&I $2,549 + taxes/insurance $1,405); reserves $75K after close (9.2 months); AVM $490K-$510K; LTV 80%; single-family, good condition; Low risk |
| 4. Conditions | `condition_tracking` | Recent paystub Outstanding 2 days; Appraisal Ordered 3 days; Insurance quote Submitted, under review; Title work Ordered 5 days; 2 outstanding items; projected 15-day close if the paystub arrives within 48 hours |
| 5. Processing summary | `processing_summary` | 92% documentation; Conventional 30-yr 6.875%; 98% eligibility fit; 2 outstanding; 15-day close, 67% faster than the 45-day standard; $388K at 6.875%; $2,549 P&I ($3,954 PITI); DTI 28%; risk Low |

Calculations: P&I is the standard amortization payment on the loan amount at the program rate and term. Front DTI = PITI / monthly income; back DTI = (PITI + $1,158 other debts) / monthly income. Reserves after close = $145,000 verified assets - cash to close $70,000 ($97,000 down + $10,000 closing costs - $37,000 earnest money already deposited) = $75,000; reserve months = $75,000 / ($3,954 PITI + $1,158 debts + $3,040 living expenses) = 9.2. The demo video showed $2,554 / $3,348 / $2,618 monthly payments; the computed amortization values $2,549 / $3,353 / $2,614 are used here. Eligibility fit is an underwriting-guideline match score, not an approval prediction.

## Complete deterministic source records

The following objects reproduce every packaged identifier, name, value, amount, date, status, rule, threshold, mapping, and relationship used by the agent. Keys and values are exact.

### `LOAN_APPLICATIONS`

```json
{
  "LA-2025-4001": {
    "alias": "martinez",
    "annual_income": 170400,
    "applicant": "Michael & Sarah Martinez",
    "assets_verified": 145000,
    "avm_high": 510000,
    "avm_low": 490000,
    "closing_costs": 10000,
    "credit_score": 742,
    "credit_scores": [
      742,
      738
    ],
    "documents": [
      [
        "Income",
        9,
        10,
        "missing 1 paystub"
      ],
      [
        "Assets",
        5,
        5,
        "complete"
      ],
      [
        "Credit",
        4,
        4,
        "complete"
      ],
      [
        "Property",
        4,
        5,
        "appraisal ordered, 5 days"
      ]
    ],
    "down_payment_pct": 20.0,
    "earnest_money_deposited": 37000,
    "employment": [
      [
        "Michael",
        8
      ],
      [
        "Sarah",
        5
      ]
    ],
    "employment_years": 8,
    "late_payments": 0,
    "living_expenses_monthly": 3040,
    "loan_amount": 388000,
    "loan_officer": "Diana Cruz",
    "loan_type": "conventional_30yr",
    "monthly_debt": 1158,
    "program_fit": [
      [
        "conventional_30yr",
        98
      ],
      [
        "conventional_15yr",
        95
      ],
      [
        "fha_30yr",
        100
      ]
    ],
    "projected_close_days": 15,
    "property_address": "1234 Oak Lane",
    "property_type": "Single-family, good condition",
    "property_value": 485000,
    "purpose": "purchase",
    "recommended_program": "conventional_30yr",
    "standard_close_days": 45,
    "status": "underwriting",
    "taxes_insurance_monthly": 1405,
    "utilization_pct": 18
  },
  "LA-2025-4002": {
    "alias": "nguyen",
    "annual_income": 68000,
    "applicant": "Kevin Nguyen",
    "credit_score": 648,
    "down_payment_pct": 3.5,
    "employment_years": 3,
    "loan_amount": 265375,
    "loan_officer": "Mark Peterson",
    "loan_type": "fha_30yr",
    "monthly_debt": 890,
    "property_address": "1200 Oak Park Ave, Unit 4B",
    "property_value": 275000,
    "purpose": "purchase",
    "status": "document_review"
  },
  "LA-2025-4003": {
    "alias": "westfield",
    "annual_income": 580000,
    "applicant": "Westfield Properties LLC",
    "credit_score": 0,
    "down_payment_pct": 30.0,
    "dscr": 1.42,
    "employment_years": 0,
    "loan_amount": 1680000,
    "loan_officer": "Diana Cruz",
    "loan_type": "commercial_5yr",
    "monthly_debt": 22000,
    "property_address": "8800 Industrial Blvd",
    "property_value": 2400000,
    "purpose": "refinance",
    "status": "credit_review"
  },
  "LA-2025-4004": {
    "alias": "blake",
    "annual_income": 95000,
    "applicant": "Sandra Blake",
    "credit_score": 710,
    "down_payment_pct": 0.0,
    "employment_years": 12,
    "loan_amount": 340000,
    "loan_officer": "Mark Peterson",
    "loan_type": "va_30yr",
    "monthly_debt": 650,
    "property_address": "555 Freedom Way",
    "property_value": 340000,
    "purpose": "purchase",
    "status": "ready_for_human_decision"
  }
}
```

### `APPROVAL_CRITERIA`

```json
{
  "commercial_5yr": {
    "max_dti": 0,
    "max_ltv": 80,
    "min_credit": 0,
    "min_down_pct": 20,
    "min_dscr": 1.25
  },
  "conventional_15yr": {
    "max_dti": 43,
    "max_ltv": 95,
    "min_credit": 620,
    "min_down_pct": 5,
    "min_reserve_months": 6
  },
  "conventional_30yr": {
    "max_dti": 43,
    "max_ltv": 95,
    "min_credit": 620,
    "min_down_pct": 5,
    "min_reserve_months": 6
  },
  "fha_30yr": {
    "max_dti": 50,
    "max_ltv": 96.5,
    "min_credit": 580,
    "min_down_pct": 3.5
  },
  "va_30yr": {
    "max_dti": 60,
    "max_ltv": 100,
    "min_credit": 580,
    "min_down_pct": 0
  }
}
```

### `DOCUMENT_REQUIREMENTS`

```json
{
  "assets": [
    "Bank statements (last 2 months)",
    "Investment account statements",
    "Gift letter (if applicable)"
  ],
  "commercial_specific": [
    "Business tax returns (3 years)",
    "Profit & loss statement",
    "Rent roll",
    "Environmental Phase I"
  ],
  "fha_specific": [
    "FHA case number assignment",
    "HUD-1 settlement statement"
  ],
  "identity": [
    "Government-issued photo ID",
    "Social Security verification"
  ],
  "income": [
    "W-2 forms (last 2 years)",
    "Pay stubs (last 30 days)",
    "Tax returns (last 2 years)",
    "Employment verification letter"
  ],
  "property": [
    "Purchase agreement",
    "Appraisal report",
    "Title search",
    "Homeowners insurance quote"
  ],
  "va_specific": [
    "Certificate of Eligibility (COE)",
    "DD-214 or active duty proof"
  ]
}
```

### `RATE_SHEET`

```json
{
  "commercial_5yr": {
    "apr": 7.75,
    "points": 1.0,
    "rate": 7.5,
    "years": 5
  },
  "conventional_15yr": {
    "apr": 6.498,
    "points": 0.5,
    "rate": 6.375,
    "years": 15
  },
  "conventional_30yr": {
    "apr": 7.012,
    "points": 0.5,
    "rate": 6.875,
    "years": 30
  },
  "fha_30yr": {
    "apr": 7.25,
    "mip_annual": 0.55,
    "mip_upfront": 1.75,
    "points": 0.0,
    "rate": 7.125,
    "years": 30
  },
  "va_30yr": {
    "apr": 6.485,
    "funding_fee": 2.15,
    "points": 0.0,
    "rate": 6.25,
    "years": 30
  }
}
```

### `CONDITIONS`

```json
{
  "LA-2025-4001": [
    {
      "action": "Borrower upload",
      "condition": "Recent paystub",
      "due": "2 days",
      "outstanding": true,
      "status": "Outstanding"
    },
    {
      "action": "Inspector scheduled",
      "condition": "Appraisal",
      "due": "3 days",
      "outstanding": true,
      "status": "Ordered"
    },
    {
      "action": "Meets requirements",
      "condition": "Insurance quote",
      "due": "Under review",
      "outstanding": false,
      "status": "Submitted"
    },
    {
      "action": "In progress",
      "condition": "Title work",
      "due": "5 days",
      "outstanding": false,
      "status": "Ordered"
    }
  ],
  "LA-2025-4002": [
    {
      "action": "Processor follow-up",
      "condition": "Employment verification",
      "due": "Assign in LOS",
      "outstanding": true,
      "status": "Open"
    },
    {
      "action": "Processor follow-up",
      "condition": "FHA case number",
      "due": "Assign in LOS",
      "outstanding": true,
      "status": "Open"
    },
    {
      "action": "Order appraisal",
      "condition": "Final appraisal",
      "due": "Assign in LOS",
      "outstanding": true,
      "status": "Open"
    }
  ],
  "LA-2025-4003": [
    {
      "action": "Order report",
      "condition": "Environmental Phase I",
      "due": "Assign in LOS",
      "outstanding": true,
      "status": "Open"
    },
    {
      "action": "Borrower upload",
      "condition": "Current rent roll",
      "due": "Assign in LOS",
      "outstanding": true,
      "status": "Open"
    }
  ],
  "LA-2025-4004": [
    {
      "action": "Processor follow-up",
      "condition": "Certificate of Eligibility validation",
      "due": "Assign in LOS",
      "outstanding": true,
      "status": "Open"
    },
    {
      "action": "Borrower upload",
      "condition": "Final insurance evidence",
      "due": "Assign in LOS",
      "outstanding": true,
      "status": "Open"
    }
  ]
}
```

### `PROGRAM_NAMES`

```json
{
  "commercial_5yr": "Commercial 5-yr",
  "conventional_15yr": "Conventional 15-yr",
  "conventional_30yr": "Conventional 30-yr",
  "fha_30yr": "FHA 30-yr",
  "va_30yr": "VA 30-yr"
}
```

## Locked-case deterministic outputs

These are direct `perform()` results for the locked operation and arguments. Preserve the headings, identifiers, values, and boundary language.

### LOA-01 — Loan Officer

- Prompt: What is in my mortgage pipeline, and which application is still in document review?
- Operation: `application_review`
- Arguments: `{}`
- Required factual anchors: `LA-2025-4002`, `Document Review`

```text
> **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

# Loan Application Pipeline

| App ID | Applicant | Type | Amount | LTV | Status | LO |
|---|---|---|---|---|---|---|
| LA-2025-4001 | Michael & Sarah Martinez | Conventional 30-yr | $388,000 | 80.0% | Underwriting | Diana Cruz |
| LA-2025-4002 | Kevin Nguyen | FHA 30-yr | $265,375 | 96.5% | Document Review | Mark Peterson |
| LA-2025-4003 | Westfield Properties LLC | Commercial 5-yr | $1,680,000 | 70.0% | Credit Review | Diana Cruz |
| LA-2025-4004 | Sandra Blake | VA 30-yr | $340,000 | 100.0% | Ready For Human Decision | Mark Peterson |

**Pipeline Volume:** $2,673,375
**Applications:** 4

## Rate Sheet

| Product | Rate | APR | Points |
|---|---|---|---|
| Conventional 30-yr | 6.875% | 7.012% | 0.5 |
| Conventional 15-yr | 6.375% | 6.498% | 0.5 |
| FHA 30-yr | 7.125% | 7.25% | 0.0 |
| VA 30-yr | 6.25% | 6.485% | 0.0 |
| Commercial 5-yr | 7.5% | 7.75% | 1.0 |
```

### LOA-02 — Underwriter

- Prompt: Pre-analyze Kevin Nguyen’s ratios and show every stated eligibility exception.
- Operation: `credit_analysis`
- Arguments: `{"application_id": "LA-2025-4002"}`
- Required factual anchors: `LA-2025-4002`, `DTI`

```text
> **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

# Credit Analysis: LA-2025-4002

- **Applicant:** Kevin Nguyen
- **Loan Type:** FHA 30-yr
- **Credit Score:** 648
- **Annual Income:** $68,000
- **Monthly Debt:** $890
- **DTI Ratio:** 47.3%
- **LTV Ratio:** 96.5%
- **Down Payment:** 3.5%
- **Employment:** 3 years

## Criteria Comparison

| Metric | Actual | Required | Status |
|---|---|---|---|
| Credit Score | 648 | >= 580 | Pass |
| DTI | 47.3% | <= 50% | Pass |
| LTV | 96.5% | <= 96.5% | Pass |

**All criteria met.**
```

### LOA-03 — Processor

- Prompt: Build the VA document checklist for Sandra so I can verify the file.
- Operation: `document_verification`
- Arguments: `{"application_id": "LA-2025-4004"}`
- Required factual anchors: `LA-2025-4004`, `Certificate of Eligibility`

```text
> **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

# Document Verification: LA-2025-4004

**Applicant:** Sandra Blake
**Loan Type:** VA 30-yr

## Income

- [ ] W-2 forms (last 2 years)
- [ ] Pay stubs (last 30 days)
- [ ] Tax returns (last 2 years)
- [ ] Employment verification letter

## Assets

- [ ] Bank statements (last 2 months)
- [ ] Investment account statements
- [ ] Gift letter (if applicable)

## Property

- [ ] Purchase agreement
- [ ] Appraisal report
- [ ] Title search
- [ ] Homeowners insurance quote

## Identity

- [ ] Government-issued photo ID
- [ ] Social Security verification

## Va Specific

- [ ] Certificate of Eligibility (COE)
- [ ] DD-214 or active duty proof

```

### LOA-04 — Senior Underwriter

- Prompt: Which files meet the limited criteria, and did the assistant approve any loan?
- Operation: `decision_recommendation`
- Arguments: `{}`
- Required factual anchors: `LA-2025-4001`, `No lending decision`

```text
> **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

# Loan Eligibility Findings for Underwriter Review

## LA-2025-4001: Michael & Sarah Martinez

- **Loan:** $388,000 (Conventional 30-yr)
- **Credit / ratio / LTV:** 742 / DTI 36.0% / 80.0%
- **Review Finding:** Stated criteria met — human underwriting review
- **Rationale:** No exception found in the limited synthetic criteria

## LA-2025-4002: Kevin Nguyen

- **Loan:** $265,375 (FHA 30-yr)
- **Credit / ratio / LTV:** 648 / DTI 47.3% / 96.5%
- **Review Finding:** Condition or exception review required
- **Rationale:** LTV 96.5% leaves little equity; confirm mortgage insurance; DTI 47.3% above the 43% guideline; document compensating factors

## LA-2025-4003: Westfield Properties LLC

- **Loan:** $1,680,000 (Commercial 5-yr)
- **Credit / ratio / LTV:** N/A / DSCR 1.42 / 70.0%
- **Review Finding:** Stated criteria met — human underwriting review
- **Rationale:** No exception found in the limited synthetic criteria

## LA-2025-4004: Sandra Blake

- **Loan:** $340,000 (VA 30-yr)
- **Credit / ratio / LTV:** 710 / DTI 34.7% / 100.0%
- **Review Finding:** Stated criteria met — human underwriting review
- **Rationale:** No exception found in the limited synthetic criteria

No lending decision has been made. Validate source documents, program rules, fair-lending controls, disclosures, and delegated authority before any customer communication or action.
```

### LOA-05 — Closing Coordinator

- Prompt: Which conditions are still open on the commercial refinance, and is a closing date promised?
- Operation: `condition_tracking`
- Arguments: `{"application_id": "LA-2025-4003"}`
- Required factual anchors: `LA-2025-4003`, `Environmental Phase I`

```text
> **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

# Conditions: LA-2025-4003 Westfield Properties LLC

**2 outstanding items.**

| Condition | Status | Due | Action |
|---|---|---|---|
| Environmental Phase I | Open | Assign in LOS | Order report |
| Current rent roll | Open | Assign in LOS | Borrower upload |

Owner and due date: assign in the approved loan-origination system.

No condition was cleared, no update was posted, and no closing date is promised.

Source: [LOS + Document Management] Agents: ConditionTrackingAgent
```

### LOA-06 — Loan Officer

- Prompt: Process the Martinez mortgage application and give me an eligibility assessment with documentation status.
- Operation: `application_intake`
- Arguments: `{"application_id": "LA-2025-4001"}`
- Required factual anchors: `92% documentation complete`, `1234 Oak Lane`, `missing 1 paystub`

```text
> **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

# Application Processed: Michael & Sarah Martinez (LA-2025-4001)

**92% documentation complete.**

| Field | Details |
|---|---|
| Borrowers | Michael & Sarah Martinez |
| Property | 1234 Oak Lane, $485K purchase |
| Loan amount | $388K (20% down) |
| Credit scores | 742 / 738 (excellent) |
| Program | Conventional 30-yr |

**Document Status:**

| Category | Complete | Note |
|---|---|---|
| Income | 90% | missing 1 paystub |
| Assets | 100% | complete |
| Credit | 100% | complete |
| Property | 80% | appraisal ordered, 5 days |
| **Overall** | **92%** | |

**Application Strength:** Excellent credit, stable employment (Michael 8 yrs, Sarah 5 yrs), assets $145K verified. No red flags in the stated criteria.

**Next step:** run eligibility and program matching (program comparison).

Eligibility assessment is guidance for underwriter review; no lending decision has been made.

Source: [LOS + Document Portal + Credit] Agents: ApplicationIntakeAgent, DocumentProcessingAgent
```

### LOA-07 — Loan Officer

- Prompt: Which loan programs are the Martinezes eligible for, and which one do you recommend?
- Operation: `program_comparison`
- Arguments: `{"application_id": "LA-2025-4001"}`
- Required factual anchors: `Conventional 15-yr`, `$2,549`, `9.2 months`

```text
> **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

# Eligibility Analyzed: Michael & Sarah Martinez (LA-2025-4001)

Qualifies for 3 programs; Conventional 30-yr recommended.

| Program | Rate | Monthly P&I | Eligibility fit |
|---|---|---|---|
| Conventional 30-yr | 6.875% | $2,549 | 98% (recommended) |
| Conventional 15-yr | 6.375% | $3,353 | 95% |
| FHA 30-yr | 7.125% | $2,614 | 100% |

**Recommended: Conventional 30-yr**

- Best rate/payment balance
- No PMI (20% down)
- DTI: 28% (well below 43% max)
- Reserves: 9.2 months (exceeds 6-month requirement)

**Minor Conditions:** recent paystub, appraisal
**Fast-Track Eligible:** strong profile qualifies for expedited underwriting (15-day close possible, projected, not promised).

Eligibility fit is an underwriting-guideline match score for underwriter review, not an approval prediction; rates are synthetic and nothing is priced or locked.

Source: [Underwriting Guidelines + AUS] Agents: EligibilityAssessmentAgent, DocumentProcessingAgent

**Next step:** run comprehensive credit and property analysis.
```

### LOA-08 — Loan Officer

- Prompt: Give me the complete loan processing summary for the Martinez file.
- Operation: `processing_summary`
- Arguments: `{"application_id": "LA-2025-4001"}`
- Required factual anchors: `67% faster`, `2 outstanding`, `$3,954 PITI`

```text
> **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

# Loan Processing Summary: Michael & Sarah Martinez (LA-2025-4001)

Session complete. 15-day close projected.

| Accomplishment | Result |
|---|---|
| Application processed | 92% documentation complete |
| Program selected | Conventional 30-yr, 6.875% |
| Eligibility confirmed | 98% eligibility fit (underwriter review pending) |
| Conditions | 2 outstanding, on track |
| Timeline | 15-day close (67% faster than the 45-day standard) |

**Loan Details:**

- Amount: $388K at 6.875%
- Payment: $2,549 P&I ($3,954 PITI)
- DTI: 28% (excellent)
- Risk: Low

**Remaining steps:** Recent paystub (2 days); Appraisal (3 days).

**Efficiency Gains:** document processing by AI extraction (minutes vs hours); program comparison and condition tracking in one session.

The timeline is a projection; no lending decision has been made and no closing date is promised.

Source: [LOS + Underwriting + Condition Tracking] Agents: LoanOriginationAssistantAgent
```

## Evidence boundary

This snapshot does not authorize lending, legal, tax, real-estate, or financial advice; eligibility or credit decisions; approvals, denials, pricing, quotes, locks, disclosures, condition clearance, closing, funding, servicing, or record changes. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
