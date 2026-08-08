# Customer Onboarding Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/customer_onboarding_fs_stack/customer_onboarding_fs_agent.py`
- Source SHA-256: `d2cd60c21ae267c2969f79396bfcc35eeb269419665152e426531107034d87c6`
- Expected tool: `FSCustomerOnboardingAgent`
- Snapshot behavior: fixed to the packaged source revision; no live connection or current-data claim.

## Complete deterministic source records

The following objects reproduce every packaged identifier, name, value, amount, date, status, rule, threshold, mapping, and relationship used by the agent. Keys and values are exact.

### `CUSTOMER_APPLICATIONS`

```json
{
  "APP-6001": {
    "account_requested": "premium_checking",
    "applicant": "Sarah Chen",
    "application_type": "individual",
    "estimated_assets": 250000,
    "relationship_manager": "Michael Torres",
    "risk_rating": "low",
    "status": "kyc_in_progress",
    "submitted": "2025-02-20"
  },
  "APP-6002": {
    "account_requested": "commercial_checking",
    "applicant": "Blackwood Capital Partners LLC",
    "application_type": "business",
    "estimated_assets": 2400000,
    "relationship_manager": "Jessica Nguyen",
    "risk_rating": "medium",
    "status": "document_review",
    "submitted": "2025-02-25"
  },
  "APP-6003": {
    "account_requested": "wealth_management",
    "applicant": "Ahmed Al-Rashid",
    "application_type": "individual",
    "estimated_assets": 5800000,
    "relationship_manager": "Jessica Nguyen",
    "risk_rating": "high",
    "status": "enhanced_due_diligence",
    "submitted": "2025-03-01"
  },
  "APP-6004": {
    "account_requested": "basic_savings",
    "applicant": "Maria Fontaine",
    "application_type": "individual",
    "estimated_assets": 15000,
    "relationship_manager": "Michael Torres",
    "risk_rating": "low",
    "status": "setup_review_ready",
    "submitted": "2025-03-05"
  }
}
```

### `KYC_DOCUMENTS`

```json
{
  "business": [
    {
      "document": "Articles of Incorporation / Formation",
      "required": true
    },
    {
      "document": "EIN verification letter",
      "required": true
    },
    {
      "document": "Certificate of Good Standing",
      "required": true
    },
    {
      "document": "Operating Agreement / Bylaws",
      "required": true
    },
    {
      "document": "Beneficial ownership declaration (FinCEN BOI)",
      "required": true
    },
    {
      "document": "Government ID for all authorized signers",
      "required": true
    },
    {
      "document": "Business license",
      "required": false
    },
    {
      "document": "Financial statements (last 2 years)",
      "required": false
    }
  ],
  "individual": [
    {
      "document": "Government-issued photo ID",
      "required": true
    },
    {
      "document": "Social Security Number verification",
      "required": true
    },
    {
      "document": "Proof of address (utility bill or bank statement)",
      "required": true
    },
    {
      "document": "W-9 Tax Form",
      "required": true
    },
    {
      "document": "Source of funds documentation",
      "required": false
    }
  ]
}
```

### `VERIFICATION_STATUS`

```json
{
  "APP-6001": {
    "address_verification": "pending",
    "adverse_media": "clear",
    "id_verification": "complete",
    "ofac_screening": "clear",
    "pep_screening": "clear",
    "ssn_verification": "complete"
  },
  "APP-6002": {
    "adverse_media": "clear",
    "beneficial_ownership": "in_progress",
    "ein_verification": "complete",
    "id_verification": "complete",
    "ofac_screening": "clear",
    "pep_screening": "clear"
  },
  "APP-6003": {
    "address_verification": "complete",
    "adverse_media": "review_needed",
    "id_verification": "complete",
    "ofac_screening": "clear",
    "pep_screening": "flagged",
    "source_of_wealth": "pending",
    "ssn_verification": "complete"
  },
  "APP-6004": {
    "address_verification": "complete",
    "adverse_media": "clear",
    "id_verification": "complete",
    "ofac_screening": "clear",
    "pep_screening": "clear",
    "ssn_verification": "complete"
  }
}
```

### `ACCOUNT_TYPES`

```json
{
  "basic_savings": {
    "apy": 0.5,
    "features": [
      "Online banking",
      "Mobile deposit",
      "ATM access"
    ],
    "min_deposit": 25,
    "monthly_fee": 0
  },
  "commercial_checking": {
    "apy": 0.1,
    "features": [
      "Treasury management",
      "ACH origination",
      "Wire transfers",
      "Merchant services"
    ],
    "min_deposit": 5000,
    "monthly_fee": 25
  },
  "premium_checking": {
    "apy": 0.15,
    "features": [
      "No ATM fees",
      "Overdraft protection",
      "Bill pay",
      "Cashback rewards"
    ],
    "min_deposit": 1000,
    "monthly_fee": 12
  },
  "wealth_management": {
    "apy": 1.25,
    "features": [
      "Dedicated advisor",
      "Investment management",
      "Trust services",
      "Concierge banking"
    ],
    "min_deposit": 250000,
    "monthly_fee": 0
  }
}
```

## Locked-case deterministic outputs

These are direct `perform()` results for the locked operation and arguments. Preserve the headings, identifiers, values, and boundary language.

### FCO-01 — Compliance Officer

- Prompt: What is holding up the enhanced due diligence case, and which checks need my review?
- Operation: `kyc_verification`
- Arguments: `{"application_id": "APP-6003"}`
- Required factual anchors: `APP-6003`, `PEP`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

# KYC Verification: APP-6003

- **Applicant:** Ahmed Al-Rashid
- **Type:** Individual
- **Risk Rating:** High
- **KYC Progress:** 57.1%

## Verification Checks

| Check | Status |
|---|---|
| Id Verification | Complete |
| Ssn Verification | Complete |
| Address Verification | Complete |
| Ofac Screening | Clear |
| Pep Screening | Flagged |
| Adverse Media | Review Needed |
| Source Of Wealth | Pending |

## Enhanced Due Diligence Required

- Source of wealth verification
- PEP relationship documentation
- Enhanced transaction monitoring parameters
```

### FCO-02 — Onboarding Specialist

- Prompt: Which approved-looking file is ready for account setup review, and what product is being prepared?
- Operation: `account_setup`
- Arguments: `{}`
- Required factual anchors: `APP-6004`, `Basic Savings`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

# Account Setup Preparation Reference

| Account Type | Min Deposit | Monthly Fee | APY | Features |
|---|---|---|---|---|
| Basic Savings | $25 | $0 | 0.5% | Online banking, Mobile deposit, ATM access |
| Premium Checking | $1,000 | $12 | 0.15% | No ATM fees, Overdraft protection, Bill pay |
| Commercial Checking | $5,000 | $25 | 0.1% | Treasury management, ACH origination, Wire transfers |
| Wealth Management | $250,000 | $0 | 1.25% | Dedicated advisor, Investment management, Trust services |

## Applications Ready for Authorized Setup Review

### APP-6004: Maria Fontaine

- **Account:** Basic Savings
- **Min Deposit:** $25
- **Features:** Online banking, Mobile deposit, ATM access


No account has been opened or provisioned. An authorized onboarding reviewer must validate KYC evidence, product eligibility, disclosures, and customer consent before action.
```

### FCO-03 — Relationship Manager

- Prompt: Give me the business onboarding document list for Blackwood before I call them.
- Operation: `document_checklist`
- Arguments: `{"application_id": "APP-6002"}`
- Required factual anchors: `APP-6002`, `Beneficial ownership`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

# Document Checklist: APP-6002

**Applicant:** Blackwood Capital Partners LLC
**Type:** Business

## Required Documents

- [ ] Articles of Incorporation / Formation (Required)
- [ ] EIN verification letter (Required)
- [ ] Certificate of Good Standing (Required)
- [ ] Operating Agreement / Bylaws (Required)
- [ ] Beneficial ownership declaration (FinCEN BOI) (Required)
- [ ] Government ID for all authorized signers (Required)
- [ ] Business license (Optional)
- [ ] Financial statements (last 2 years) (Optional)

## Compliance Notes

- All documents must be current (within 90 days)
- Copies must be certified or notarized for business accounts
- BSA/AML requirements apply to all account openings
- CIP (Customer Identification Program) verification mandatory
```

### FCO-04 — Head of Onboarding

- Prompt: Where is the onboarding queue stuck, and who owns each application?
- Operation: `onboarding_status`
- Arguments: `{}`
- Required factual anchors: `APP-6001`, `APP-6003`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

# Customer Onboarding Pipeline

**Applications:** 4
**Total Estimated Assets:** $8,465,000

## Pipeline Status

- Kyc In Progress: 1
- Document Review: 1
- Enhanced Due Diligence: 1
- Setup Review Ready: 1

## Application Details

| App ID | Applicant | Account | Risk | Est. Assets | Status | RM |
|---|---|---|---|---|---|---|
| APP-6001 | Sarah Chen | Premium Checking | Low | $250,000 | Kyc In Progress | Michael Torres |
| APP-6002 | Blackwood Capital Partners LLC | Commercial Checking | Medium | $2,400,000 | Document Review | Jessica Nguyen |
| APP-6003 | Ahmed Al-Rashid | Wealth Management | High | $5,800,000 | Enhanced Due Diligence | Jessica Nguyen |
| APP-6004 | Maria Fontaine | Basic Savings | Low | $15,000 | Setup Review Ready | Michael Torres |
```

## Evidence boundary

This snapshot does not authorize identity verification, sanctions or PEP clearance, KYC approval, applicant approval or rejection, customer outreach, account opening, product provisioning, or any external record change. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
