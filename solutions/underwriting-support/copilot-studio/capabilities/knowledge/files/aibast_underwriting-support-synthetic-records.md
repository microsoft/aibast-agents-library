# Underwriting Support Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/underwriting_support_stack/underwriting_support_agent.py`
- Source SHA-256: `2e6378aa40236659e8615d65bf40254427d19ee762f851191b35aa2c0e4c8ff3`
- Expected tool: `UnderwritingSupportAgent`
- Snapshot behavior: fixed to the packaged source revision; no live connection or current-data claim.

## Complete deterministic source records

The following objects reproduce every packaged identifier, name, value, amount, date, status, rule, threshold, mapping, and relationship used by the agent. Keys and values are exact.

### `APPLICATIONS`

```json
{
  "UW-2025-101": {
    "applicant": "Riverside Manufacturing Inc.",
    "construction": "fire_resistive",
    "coverage_requested": 5000000,
    "line_of_business": "commercial_property",
    "loss_history": [
      {
        "amount": 125000,
        "status": "closed",
        "type": "fire",
        "year": 2022
      },
      {
        "amount": 18500,
        "status": "closed",
        "type": "water_damage",
        "year": 2023
      }
    ],
    "premium_indicated": 42500,
    "property_type": "manufacturing_facility",
    "protection_class": 3,
    "risk_score": 62,
    "square_footage": 85000,
    "status": "under_review",
    "underwriter": "Patricia Graham",
    "year_built": 1998
  },
  "UW-2025-102": {
    "applicant": "Sarah Mitchell",
    "coverage_requested": 500000,
    "credit_score": 745,
    "driver_age": 34,
    "driving_record": {
      "accidents": 0,
      "violations": 0,
      "years_licensed": 16
    },
    "line_of_business": "personal_auto",
    "loss_history": [],
    "premium_indicated": 2400,
    "risk_score": 22,
    "status": "ready_for_underwriter_review",
    "underwriter": "James Chen",
    "vehicle": "2024 Toyota RAV4"
  },
  "UW-2025-103": {
    "applicant": "Downtown Medical Associates",
    "claims_history": [
      {
        "allegation": "surgical_complication",
        "amount": 450000,
        "status": "closed_record",
        "year": 2021
      },
      {
        "allegation": "misdiagnosis",
        "amount": 0,
        "status": "dismissed",
        "year": 2023
      }
    ],
    "coverage_requested": 3000000,
    "line_of_business": "professional_liability",
    "practitioners": 6,
    "premium_indicated": 67000,
    "risk_score": 75,
    "specialty": "orthopedic_surgery",
    "status": "exception_review",
    "underwriter": "Patricia Graham",
    "years_in_practice": 12
  },
  "UW-2025-104": {
    "annual_revenue": 8500000,
    "applicant": "Harbor View Restaurant Group",
    "business_type": "restaurant_chain",
    "coverage_requested": 2000000,
    "employees": 120,
    "line_of_business": "general_liability",
    "locations": 4,
    "loss_history": [
      {
        "amount": 35000,
        "status": "open",
        "type": "slip_and_fall",
        "year": 2024
      }
    ],
    "premium_indicated": 18500,
    "risk_score": 48,
    "status": "pending_info",
    "underwriter": "James Chen"
  }
}
```

### `UNDERWRITING_GUIDELINES`

```json
{
  "commercial_property": {
    "max_building_age": 50,
    "max_coverage": 25000000,
    "max_loss_ratio": 60,
    "min_protection_class": 8,
    "prohibited_risks": [
      "cannabis_operations",
      "fireworks_storage"
    ],
    "required_inspections": [
      "fire_protection",
      "electrical",
      "roof_condition"
    ]
  },
  "general_liability": {
    "max_coverage": 5000000,
    "max_loss_ratio": 65,
    "min_years_business": 2,
    "required_documents": [
      "financial_statements",
      "safety_program",
      "certificates_of_insurance"
    ]
  },
  "personal_auto": {
    "max_accidents_3yr": 2,
    "max_coverage": 1000000,
    "max_violations_3yr": 3,
    "min_credit_score": 550,
    "min_driver_age": 16,
    "required_documents": [
      "MVR",
      "prior_insurance_dec"
    ]
  },
  "professional_liability": {
    "high_risk_specialties": [
      "neurosurgery",
      "orthopedic_surgery",
      "obstetrics"
    ],
    "max_claims_5yr": 3,
    "max_coverage": 10000000,
    "min_years_practice": 3,
    "required_documents": [
      "CV",
      "board_certifications",
      "claims_history"
    ]
  }
}
```

### `PRICING_MODELS`

```json
{
  "commercial_property": {
    "base_rate_per_100": 0.85,
    "construction_factor": {
      "fire_resistive": 0.8,
      "frame": 1.35,
      "masonry": 1.0
    },
    "protection_class_factor": {
      "1": 0.75,
      "2": 0.8,
      "3": 0.9,
      "4": 1.0,
      "5": 1.1
    }
  },
  "general_liability": {
    "base_rate_per_1000_revenue": 2.15,
    "industry_factor": {
      "construction": 1.8,
      "office": 0.7,
      "restaurant_chain": 1.35,
      "retail": 1.1
    }
  },
  "personal_auto": {
    "age_factor": {
      "16": 2.5,
      "25": 1.3,
      "30": 1.0,
      "50": 0.95,
      "65": 1.05
    },
    "base_premium": 1200,
    "credit_factor": {
      "500": 1.6,
      "600": 1.25,
      "700": 1.0,
      "800": 0.85
    }
  },
  "professional_liability": {
    "base_rate_per_practitioner": 8500,
    "specialty_factor": {
      "family_medicine": 0.6,
      "neurosurgery": 2.8,
      "obstetrics": 2.4,
      "orthopedic_surgery": 2.1
    }
  }
}
```

## Locked-case deterministic outputs

These are direct `perform()` results for the locked operation and arguments. Preserve the headings, identifiers, values, and boundary language.

### UWS-01 — Underwriter

- Prompt: Which submission needs the most experienced underwriter, and why?
- Operation: `risk_evaluation`
- Arguments: `{}`
- Required factual anchors: `UW-2025-103`, `Substandard`

```text
> **SYNTHETIC DEMO DATA — UNDERWRITER REVIEW REQUIRED.** Fictional submissions and rating assumptions only. This is not legal, insurance, or financial advice and does not bind, quote, approve, decline, or modify coverage.

# Underwriting Risk Evaluation

| App ID | Applicant | LOB | Coverage | Risk Score | Tier | Status |
|---|---|---|---|---|---|---|
| UW-2025-101 | Riverside Manufacturing Inc. | Commercial Property | $5,000,000 | 62 | Substandard | Under Review |
| UW-2025-102 | Sarah Mitchell | Personal Auto | $500,000 | 22 | Preferred | Ready For Underwriter Review |
| UW-2025-103 | Downtown Medical Associates | Professional Liability | $3,000,000 | 75 | Substandard | Exception Review |
| UW-2025-104 | Harbor View Restaurant Group | General Liability | $2,000,000 | 48 | Standard | Pending Info |

## Risk Tier Definitions

- **Preferred** (0-30): Best rates, minimal restrictions
- **Standard** (31-55): Standard rates and terms
- **Substandard** (56-75): Rate surcharge or coverage restrictions
- **Outside Stated Appetite** (76+): Requires authorized underwriting review
```

### UWS-02 — Pricing Analyst

- Prompt: Walk me through the rating factors and loss evidence for Riverside without issuing a quote.
- Operation: `pricing_recommendation`
- Arguments: `{"application_id": "UW-2025-101"}`
- Required factual anchors: `UW-2025-101`, `Indicated Premium`

```text
> **SYNTHETIC DEMO DATA — UNDERWRITER REVIEW REQUIRED.** Fictional submissions and rating assumptions only. This is not legal, insurance, or financial advice and does not bind, quote, approve, decline, or modify coverage.

# Illustrative Pricing-Factor Review: UW-2025-101

- **Applicant:** Riverside Manufacturing Inc.
- **LOB:** Commercial Property
- **Coverage:** $5,000,000
- **Indicated Premium:** $42,500
- **Risk Score:** 62 (Substandard)

## Pricing Model Factors

- **Base Rate Per 100:** 0.85
### Construction Factor

- fire_resistive: 0.8
- masonry: 1.0
- frame: 1.35
### Protection Class Factor

- 1: 0.75
- 2: 0.8
- 3: 0.9
- 4: 1.0
- 5: 1.1

## Loss History

| Year | Type/Allegation | Amount | Status |
|---|---|---|---|
| 2022 | Fire | $125,000 | Closed |
| 2023 | Water Damage | $18,500 | Closed |
```

### UWS-03 — Risk Analyst

- Prompt: Which applications are outside a stated guideline or missing required evidence?
- Operation: `guideline_check`
- Arguments: `{}`
- Required factual anchors: `UW-2025-103`, `High-Risk Specialty`

```text
> **SYNTHETIC DEMO DATA — UNDERWRITER REVIEW REQUIRED.** Fictional submissions and rating assumptions only. This is not legal, insurance, or financial advice and does not bind, quote, approve, decline, or modify coverage.

# Underwriting Guideline Check

## UW-2025-101: Riverside Manufacturing Inc. — No Stated Exception

- **LOB:** Commercial Property
- **Max Coverage:** $25,000,000
- **Required Inspections:** fire_protection, electrical, roof_condition

## UW-2025-102: Sarah Mitchell — No Stated Exception

- **LOB:** Personal Auto
- **Max Coverage:** $1,000,000
- **Required Documents:** MVR, prior_insurance_dec

## UW-2025-103: Downtown Medical Associates — Exceptions Noted

- **LOB:** Professional Liability
- **Max Coverage:** $10,000,000
- **Required Documents:** CV, board_certifications, claims_history

**Violations:**

- High-risk specialty: Orthopedic Surgery

## UW-2025-104: Harbor View Restaurant Group — No Stated Exception

- **LOB:** General Liability
- **Max Coverage:** $5,000,000
- **Required Documents:** financial_statements, safety_program, certificates_of_insurance

```

### UWS-04 — Senior Underwriter

- Prompt: Prepare the exception file I need to review and state whether any coverage decision was made.
- Operation: `exception_review`
- Arguments: `{}`
- Required factual anchors: `UW-2025-103`, `No approval`

```text
> **SYNTHETIC DEMO DATA — UNDERWRITER REVIEW REQUIRED.** Fictional submissions and rating assumptions only. This is not legal, insurance, or financial advice and does not bind, quote, approve, decline, or modify coverage.

# Exception Review Queue

## UW-2025-103: Downtown Medical Associates

- **LOB:** Professional Liability
- **Coverage:** $3,000,000
- **Premium:** $67,000
- **Risk Score:** 75 (Substandard)
- **Underwriter:** Patricia Graham

### Guideline Exceptions

- High-risk specialty: Orthopedic Surgery

### Human Review Paths

1. Validate missing evidence and authority limits
2. Obtain actuarial or senior-underwriter review of rating assumptions
3. Document whether the risk falls within stated appetite
4. Request additional information before any coverage decision

No approval, decline, quote, or binder has been issued.
```

## Evidence boundary

This snapshot does not authorize legal, insurance, actuarial, pricing, or financial advice; quotes, binders, approvals, declines, policy issuance, coverage changes, or promised terms. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
