# Loan Origination Assistant — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/loan_origination_assistant_stack/loan_origination_assistant_agent.py`
- Source SHA-256: `c85fb1844a55344306be2bef47eee104dfb66a589befadcd48214785df6a89a5`
- Expected tool: `LoanOriginationAssistantAgent`
- Snapshot behavior: fixed to the packaged source revision; no live connection or current-data claim.

## Complete deterministic source records

The following objects reproduce every packaged identifier, name, value, amount, date, status, rule, threshold, mapping, and relationship used by the agent. Keys and values are exact.

### `LOAN_APPLICATIONS`

```json
{
  "LA-2025-4001": {
    "annual_income": 142000,
    "applicant": "Thomas & Rebecca Harper",
    "credit_score": 762,
    "down_payment_pct": 20.0,
    "employment_years": 8,
    "loan_amount": 388000,
    "loan_officer": "Diana Cruz",
    "loan_type": "conventional_30yr",
    "monthly_debt": 1850,
    "property_address": "742 Evergreen Terrace, Springfield",
    "property_value": 485000,
    "purpose": "purchase",
    "status": "underwriting"
  },
  "LA-2025-4002": {
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
  "conventional_30yr": {
    "max_dti": 45,
    "max_ltv": 95,
    "min_credit": 620,
    "min_down_pct": 5
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
    "rate": 7.5
  },
  "conventional_30yr": {
    "apr": 7.012,
    "points": 0.5,
    "rate": 6.875
  },
  "fha_30yr": {
    "apr": 7.25,
    "mip_annual": 0.55,
    "mip_upfront": 1.75,
    "points": 0.0,
    "rate": 6.5
  },
  "va_30yr": {
    "apr": 6.485,
    "funding_fee": 2.15,
    "points": 0.0,
    "rate": 6.25
  }
}
```

### `CONDITIONS`

```json
{
  "LA-2025-4001": [
    "Final appraisal review",
    "Updated asset statement"
  ],
  "LA-2025-4002": [
    "Employment verification",
    "FHA case number",
    "Final appraisal"
  ],
  "LA-2025-4003": [
    "Environmental Phase I",
    "Current rent roll"
  ],
  "LA-2025-4004": [
    "Certificate of Eligibility validation",
    "Final insurance evidence"
  ]
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
| LA-2025-4001 | Thomas & Rebecca Harper | Conventional 30Yr | $388,000 | 80.0% | Underwriting | Diana Cruz |
| LA-2025-4002 | Kevin Nguyen | Fha 30Yr | $265,375 | 96.5% | Document Review | Mark Peterson |
| LA-2025-4003 | Westfield Properties LLC | Commercial 5Yr | $1,680,000 | 70.0% | Credit Review | Diana Cruz |
| LA-2025-4004 | Sandra Blake | Va 30Yr | $340,000 | 100.0% | Ready For Human Decision | Mark Peterson |

**Pipeline Volume:** $2,673,375
**Applications:** 4

## Rate Sheet

| Product | Rate | APR | Points |
|---|---|---|---|
| Conventional 30Yr | 6.875% | 7.012% | 0.5 |
| Fha 30Yr | 6.5% | 7.25% | 0.0 |
| Va 30Yr | 6.25% | 6.485% | 0.0 |
| Commercial 5Yr | 7.5% | 7.75% | 1.0 |
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
- **Loan Type:** Fha 30Yr
- **Credit Score:** 648
- **Annual Income:** $68,000
- **Monthly Debt:** $890
- **DTI Ratio:** 45.3%
- **LTV Ratio:** 96.5%
- **Down Payment:** 3.5%
- **Employment:** 3 years

## Criteria Comparison

| Metric | Actual | Required | Status |
|---|---|---|---|
| Credit Score | 648 | >= 580 | Pass |
| DTI | 45.3% | <= 50% | Pass |
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
**Loan Type:** Va 30Yr

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

## LA-2025-4001: Thomas & Rebecca Harper

- **Loan:** $388,000 (Conventional 30Yr)
- **Credit/DTI/LTV:** 762 / 37.2% / 80.0%
- **Review Finding:** Stated criteria met — human underwriting review
- **Rationale:** No exception found in the limited synthetic criteria

## LA-2025-4002: Kevin Nguyen

- **Loan:** $265,375 (Fha 30Yr)
- **Credit/DTI/LTV:** 648 / 45.3% / 96.5%
- **Review Finding:** Stated criteria met — human underwriting review
- **Rationale:** No exception found in the limited synthetic criteria

## LA-2025-4003: Westfield Properties LLC

- **Loan:** $1,680,000 (Commercial 5Yr)
- **Credit/DTI/LTV:** N/A / 115.2% / 70.0%
- **Review Finding:** Stated criteria met — human underwriting review
- **Rationale:** No exception found in the limited synthetic criteria

## LA-2025-4004: Sandra Blake

- **Loan:** $340,000 (Va 30Yr)
- **Credit/DTI/LTV:** 710 / 34.7% / 100.0%
- **Review Finding:** Stated criteria met — human underwriting review
- **Rationale:** No exception found in the limited synthetic criteria

No lending decision has been made. Validate source documents, program rules, fair-lending controls, disclosures, and delegated authority before any customer communication or action.
```

### LOA-05 — Closing Coordinator

- Prompt: Which conditions are still open on the commercial refinance, and is a closing date promised?
- Operation: `condition_tracking`
- Arguments: `{}`
- Required factual anchors: `LA-2025-4003`, `Environmental Phase I`

```text
> **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

# Outstanding Conditions and Timeline Review

## LA-2025-4001: Thomas & Rebecca Harper

- [ ] Final appraisal review
- [ ] Updated asset statement
- Owner and due date: assign in the approved loan-origination system

## LA-2025-4002: Kevin Nguyen

- [ ] Employment verification
- [ ] FHA case number
- [ ] Final appraisal
- Owner and due date: assign in the approved loan-origination system

## LA-2025-4003: Westfield Properties LLC

- [ ] Environmental Phase I
- [ ] Current rent roll
- Owner and due date: assign in the approved loan-origination system

## LA-2025-4004: Sandra Blake

- [ ] Certificate of Eligibility validation
- [ ] Final insurance evidence
- Owner and due date: assign in the approved loan-origination system

No condition was cleared and no closing date is promised.
```

## Evidence boundary

This snapshot does not authorize lending, legal, tax, real-estate, or financial advice; eligibility or credit decisions; approvals, denials, pricing, quotes, locks, disclosures, condition clearance, closing, funding, servicing, or record changes. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
