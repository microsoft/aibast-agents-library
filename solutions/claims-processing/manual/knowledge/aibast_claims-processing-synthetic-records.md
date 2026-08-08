# Claims Processing Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/claims_processing_stack/claims_processing_agent.py`
- Source SHA-256: `1239dd5f2cbf012c08e7413bfd6051f92441d00f4ff1f2b3a4be9ca69c309403`
- Expected tool: `ClaimsProcessingAgent`
- Snapshot behavior: fixed to the packaged source revision; no live connection or current-data claim.

## Complete deterministic source records

The following objects reproduce every packaged identifier, name, value, amount, date, status, rule, threshold, mapping, and relationship used by the agent. Keys and values are exact.

### `CLAIMS`

```json
{
  "CLM-2025-7001": {
    "adjuster": "Brian Keller",
    "claimant": "Margaret Sullivan",
    "claimed_amount": 28500,
    "date_filed": "2025-01-18",
    "date_of_loss": "2025-01-15",
    "description": "Burst pipe in upstairs bathroom caused water damage to ceiling, walls, and flooring in two rooms",
    "fraud_score": 12,
    "loss_type": "water_damage",
    "policy_number": "HO-445892",
    "policy_type": "homeowners",
    "status": "under_review",
    "supporting_docs": [
      "photos",
      "plumber_invoice",
      "repair_estimate"
    ]
  },
  "CLM-2025-7002": {
    "adjuster": "Sandra Ortiz",
    "claimant": "David Park",
    "claimed_amount": 14200,
    "date_filed": "2025-02-09",
    "date_of_loss": "2025-02-08",
    "description": "Rear-end collision at intersection of 5th Ave and Main St, other driver cited",
    "fraud_score": 5,
    "loss_type": "collision",
    "policy_number": "AU-331205",
    "policy_type": "auto",
    "status": "ready_for_adjuster_review",
    "supporting_docs": [
      "police_report",
      "photos",
      "body_shop_estimate",
      "medical_records"
    ]
  },
  "CLM-2025-7003": {
    "adjuster": "Brian Keller",
    "claimant": "Apex Commercial Properties",
    "claimed_amount": 485000,
    "date_filed": "2025-02-24",
    "date_of_loss": "2025-02-22",
    "description": "Electrical fire in warehouse section B, significant inventory and structural damage",
    "fraud_score": 68,
    "loss_type": "fire_damage",
    "policy_number": "CP-778341",
    "policy_type": "commercial_property",
    "status": "investigation",
    "supporting_docs": [
      "fire_report",
      "photos",
      "inventory_list",
      "financial_statements"
    ]
  },
  "CLM-2025-7004": {
    "adjuster": "Sandra Ortiz",
    "claimant": "Jennifer Liu",
    "claimed_amount": 42000,
    "date_filed": "2025-03-02",
    "date_of_loss": "2025-03-01",
    "description": "Home burglary — electronics, jewelry, and collectibles stolen",
    "fraud_score": 45,
    "loss_type": "theft",
    "policy_number": "HO-557210",
    "policy_type": "homeowners",
    "status": "pending_documentation",
    "supporting_docs": [
      "police_report",
      "photos"
    ]
  }
}
```

### `POLICY_DETAILS`

```json
{
  "AU-331205": {
    "coverage_limit": 100000,
    "deductible": 500,
    "effective": "2024-11-01",
    "expiry": "2025-11-01",
    "premium_annual": 1800
  },
  "CP-778341": {
    "coverage_limit": 2000000,
    "deductible": 10000,
    "effective": "2024-09-01",
    "expiry": "2025-09-01",
    "premium_annual": 18500
  },
  "HO-445892": {
    "coverage_limit": 350000,
    "deductible": 1500,
    "effective": "2024-07-01",
    "expiry": "2025-07-01",
    "premium_annual": 2400
  },
  "HO-557210": {
    "coverage_limit": 400000,
    "deductible": 2000,
    "effective": "2025-01-01",
    "expiry": "2026-01-01",
    "premium_annual": 2800
  }
}
```

### `FRAUD_INDICATORS`

```json
{
  "claim_timing": {
    "description": "Claim filed shortly after policy inception or increase in coverage",
    "weight": 12
  },
  "delayed_reporting": {
    "description": "Significant delay between loss event and claim filing",
    "weight": 8
  },
  "documentation_gaps": {
    "description": "Missing or incomplete supporting documentation",
    "weight": 15
  },
  "excessive_amount": {
    "description": "Claimed amount significantly exceeds typical loss for category",
    "weight": 20
  },
  "financial_stress": {
    "description": "Claimant shows signs of recent financial distress",
    "weight": 15
  },
  "inconsistent_narrative": {
    "description": "Inconsistencies between claimant statement and evidence",
    "weight": 18
  },
  "prior_claims_history": {
    "description": "Multiple prior claims on same or similar policies",
    "weight": 10
  },
  "witness_issues": {
    "description": "Lack of independent witnesses or corroborating evidence",
    "weight": 12
  }
}
```

### `ADJUSTER_NOTES`

```json
{
  "CLM-2025-7001": [
    "Initial inspection completed 01/20 — damage consistent with pipe burst",
    "Plumber confirms corrosion in copper fitting",
    "Estimate from licensed contractor received"
  ],
  "CLM-2025-7002": [
    "Police report confirms other party at fault",
    "Body shop estimate within market range",
    "Medical records show minor soft tissue injury"
  ],
  "CLM-2025-7003": [
    "Fire marshal report pending",
    "Financial statements show declining revenue for 3 quarters",
    "Inventory list lacks purchase receipts for high-value items",
    "SIU referral initiated"
  ],
  "CLM-2025-7004": [
    "Police report filed but no suspects identified",
    "Itemized list of stolen items requested",
    "Receipts or appraisals needed for jewelry and collectibles"
  ]
}
```

## Locked-case deterministic outputs

These are direct `perform()` results for the locked operation and arguments. Preserve the headings, identifiers, values, and boundary language.

### CLP-01 — Claims Operations Leader

- Prompt: Which incoming claim needs specialized handling first, and where should it be reviewed?
- Operation: `claim_intake`
- Arguments: `{}`
- Required factual anchors: `CLM-2025-7003`, `Investigation`

```text
> **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

# Claims Intake Dashboard

**Total Claims:** 4
**Total Claimed:** $569,700
**Avg Fraud Score:** 32.5

| Claim ID | Claimant | Policy Type | Loss | Amount | Status | Fraud |
|---|---|---|---|---|---|---|
| CLM-2025-7001 | Margaret Sullivan | Homeowners | Water Damage | $28,500 | Under Review | 12 |
| CLM-2025-7002 | David Park | Auto | Collision | $14,200 | Ready For Adjuster Review | 5 |
| CLM-2025-7003 | Apex Commercial Properties | Commercial Property | Fire Damage | $485,000 | Investigation | 68 |
| CLM-2025-7004 | Jennifer Liu | Homeowners | Theft | $42,000 | Pending Documentation | 45 |

## Status Distribution

- Under Review: 1
- Ready For Adjuster Review: 1
- Investigation: 1
- Pending Documentation: 1
```

### CLP-02 — Claims Adjuster

- Prompt: What is missing from Jennifer Liu’s theft file before I can evaluate it?
- Operation: `adjudication_review`
- Arguments: `{"claim_id": "CLM-2025-7004"}`
- Required factual anchors: `CLM-2025-7004`, `Receipts or appraisals`

```text
> **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

# Adjudication Review: CLM-2025-7004

- **Claimant:** Jennifer Liu
- **Policy:** HO-557210 (Homeowners)
- **Date of Loss:** 2025-03-01
- **Loss Type:** Theft
- **Description:** Home burglary — electronics, jewelry, and collectibles stolen
- **Claimed Amount:** $42,000
- **Adjuster:** Sandra Ortiz
- **Fraud Score:** 45/100

## Policy Details

- Coverage Limit: $400,000
- Deductible: $2,000
- Effective: 2025-01-01 to 2026-01-01

## Supporting Documents

- [x] Police Report
- [x] Photos

## Adjuster Notes

- Police report filed but no suspects identified
- Itemized list of stolen items requested
- Receipts or appraisals needed for jewelry and collectibles
```

### CLP-03 — SIU Investigator

- Prompt: Which claim crosses the SIU review threshold, and does that prove fraud?
- Operation: `fraud_flag`
- Arguments: `{}`
- Required factual anchors: `CLM-2025-7003`, `SIU Referrals`

```text
> **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

# Fraud Detection Report

## Fraud Indicator Reference

| Indicator | Weight | Description |
|---|---|---|
| Financial Stress | 15 | Claimant shows signs of recent financial distress |
| Claim Timing | 12 | Claim filed shortly after policy inception or increase in coverage |
| Excessive Amount | 20 | Claimed amount significantly exceeds typical loss for category |
| Inconsistent Narrative | 18 | Inconsistencies between claimant statement and evidence |
| Prior Claims History | 10 | Multiple prior claims on same or similar policies |
| Delayed Reporting | 8 | Significant delay between loss event and claim filing |
| Witness Issues | 12 | Lack of independent witnesses or corroborating evidence |
| Documentation Gaps | 15 | Missing or incomplete supporting documentation |

## Flagged Claims (score >= 30)

| Claim ID | Claimant | Amount | Fraud Score | Status |
|---|---|---|---|---|
| CLM-2025-7003 | Apex Commercial Properties | $485,000 | 68 | Investigation |
| CLM-2025-7004 | Jennifer Liu | $42,000 | 45 | Pending Documentation |

## SIU Referrals (score >= 60)

- **CLM-2025-7003:** Apex Commercial Properties — $485,000 (score: 68)
```

### CLP-04 — Claims Manager

- Prompt: Show the policy-term estimates and state clearly whether any claim was approved or paid.
- Operation: `settlement_recommendation`
- Arguments: `{}`
- Required factual anchors: `CLM-2025-7002`, `No approval`

```text
> **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

# Policy-Term Settlement Estimates for Adjuster Review

| Claim ID | Claimant | Claimed | Deductible | Fraud Score | Review Estimate |
|---|---|---|---|---|---|
| CLM-2025-7001 | Margaret Sullivan | $28,500 | $1,500 | 12 | $27,000 |
| CLM-2025-7002 | David Park | $14,200 | $500 | 5 | $13,700 |
| CLM-2025-7003 | Apex Commercial Properties | $485,000 | $10,000 | 68 | $475,000 |
| CLM-2025-7004 | Jennifer Liu | $42,000 | $2,000 | 45 | $40,000 |

**Total Claimed:** $569,700
**Aggregate Review Estimate:** $555,700

Fraud scores do not reduce or eliminate coverage. An authorized adjuster must validate coverage, causation, documentation, exclusions, jurisdictional rules, and SIU findings. No approval, denial, settlement, reserve, or payment has occurred.
```

## Evidence boundary

This snapshot does not authorize legal, insurance, coverage, settlement, or financial advice; fraud, liability, causation, coverage, approval, denial, reserve, settlement, payment, outreach, referral, or record-change decisions. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
