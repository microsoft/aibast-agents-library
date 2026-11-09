# Customer Onboarding Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/customer_onboarding_fs_stack/customer_onboarding_fs_agent.py`
- Source SHA-256: `0181993a2d3c59f39e1499e1051494313237750c4224ca055c616118c80c8284`
- Expected tool: `FSCustomerOnboardingAgent`
- Snapshot behavior: fixed to the packaged source revision; no live connection or current-data claim.

## Complete deterministic source records

The following objects reproduce every packaged identifier, name, value, amount, date, status, rule, threshold, mapping, and relationship used by the agent. Keys and values are exact.

### `CUSTOMER_APPLICATIONS`

```json
{
  "APP-6001": {
    "account_requested": "premium_checking",
    "applicant": "Elena Brooks",
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
  },
  "APP-6005": {
    "account_requested": "commercial_banking_suite",
    "annual_revenue_potential": 8000000,
    "applicant": "Nexus Industries Inc.",
    "application_type": "business",
    "crm_case": "ONB-2025-4782",
    "estimated_assets": 12000000,
    "priority": "HIGH - Strategic relationship",
    "products_requested": [
      "Treasury management",
      "Credit line",
      "Foreign exchange (FX)"
    ],
    "relationship_manager": "Jessica Nguyen",
    "risk_rating": "low",
    "status": "kyc_in_progress",
    "submitted": "2025-03-10"
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
  },
  "APP-6005": {
    "articles_of_incorporation": "complete",
    "corporate_registration": "complete",
    "enhanced_due_diligence": "in_progress",
    "financial_statements": "complete",
    "ofac_screening": "clear"
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
  "commercial_banking_suite": {
    "apy": 0.2,
    "features": [
      "Commercial DDA",
      "Treasury management (ACH, wires, positive pay)",
      "Credit line",
      "FX spot and forward contracts"
    ],
    "min_deposit": 25000,
    "monthly_fee": 150
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

### `CORPORATE_PROFILES`

```json
{
  "APP-6005": {
    "annual_revenue": 125000000,
    "corporate_registration": "Verified via Secretary of State database",
    "credit_rating": "BBB+ (S&P equivalent)",
    "ein": "88-1234567",
    "enhanced_due_diligence": "In progress (high-value client)",
    "financial_statements": "3 years reviewed - strong financials",
    "incorporation": "Delaware C-Corp",
    "industry": "Advanced Manufacturing (NAICS 332710)",
    "legal_entity": "Nexus Industries Inc.",
    "ofac_screening": "CLEAR - no matches",
    "sector": "advanced manufacturing",
    "years_in_business": 17
  }
}
```

### `BENEFICIAL_OWNERS`

```json
{
  "APP-6005": [
    {
      "name": "Sarah Morrison",
      "note": "Government-issued ID verified",
      "ownership_pct": 45,
      "status": "verified"
    },
    {
      "name": "David Park",
      "note": "Government-issued ID verified",
      "ownership_pct": 30,
      "status": "verified"
    },
    {
      "name": "Marcus Chen",
      "note": "Passport verification processing, expected within 2 hours",
      "ownership_pct": 25,
      "status": "pending"
    }
  ]
}
```

### `DOCUMENT_STATUS`

```json
{
  "APP-6005": [
    {
      "document": "Corporate resolution",
      "note": "Received and verified",
      "status": "received"
    },
    {
      "document": "Articles of Incorporation",
      "note": "Authenticated",
      "status": "received"
    },
    {
      "document": "Financial statements",
      "note": "3 years reviewed (2022-2024)",
      "status": "received"
    },
    {
      "document": "Certificate of Good Standing",
      "note": "Received from Delaware",
      "status": "received"
    },
    {
      "document": "Operating agreement",
      "note": "Received and reviewed",
      "status": "received"
    },
    {
      "document": "Insurance certificates",
      "note": "D&O and liability verified",
      "status": "received"
    },
    {
      "document": "EIN verification letter",
      "note": "Matches EIN 88-1234567",
      "status": "received"
    },
    {
      "document": "Government ID for authorized signers",
      "note": "3 signers on file",
      "status": "received"
    },
    {
      "document": "Business license",
      "note": "Current",
      "status": "received"
    },
    {
      "document": "Beneficial ownership certification form",
      "note": "Awaiting Marcus Chen",
      "status": "pending"
    },
    {
      "document": "W-9 tax form",
      "note": "Pending signature",
      "status": "pending"
    },
    {
      "document": "Board authorization",
      "note": "Pending for online banking access",
      "status": "pending"
    }
  ]
}
```

### `PROVISIONING_PLANS`

```json
{
  "APP-6005": [
    {
      "detail": "Commercial DDA ****7823 reserved",
      "item": "Operating account",
      "status": "ready"
    },
    {
      "detail": "ACH, wires, positive pay configured",
      "item": "Treasury management",
      "status": "ready"
    },
    {
      "detail": "$5M pre-approved; credit committee review Day 2 (tomorrow) 2 PM; expected approval (strong financials)",
      "item": "Credit line",
      "status": "pending"
    },
    {
      "detail": "Spot and forward contracts, $10M monthly aggregate limit",
      "item": "FX services",
      "status": "ready"
    },
    {
      "detail": "3 admin users configured; corporate mobile app access",
      "item": "Online and mobile banking",
      "status": "ready"
    }
  ]
}
```

### `ONBOARDING_TIMELINES`

```json
{
  "APP-6005": {
    "business_days": 5,
    "industry_days_high": 21,
    "industry_days_low": 15,
    "steps": [
      [
        "Day 1 (Today)",
        "Complete beneficial ownership verification"
      ],
      [
        "Day 2 (Tomorrow)",
        "Credit committee review at 2 PM"
      ],
      [
        "Day 3",
        "Signature cards and service agreements"
      ],
      [
        "Day 4",
        "Final compliance sign-offs and testing"
      ],
      [
        "Day 5",
        "Full account activation - go live"
      ],
      [
        "Week 2",
        "Relationship manager introduction call"
      ]
    ],
    "success_probability_pct": 95
  }
}
```

### `RISK_NOTES`

```json
{
  "APP-6005": {
    "financials": "Strong financial position with positive cash flow (credit rating BBB+)",
    "industry_risk": "Moderate-low for advanced manufacturing",
    "minor_note": "International suppliers in Asia may require occasional OFAC screening on wire transfers; standard for the industry and handled by routine wire screening",
    "screening": "All screening results clean (OFAC, PEP, EU sanctions)",
    "summary": "No significant red flags detected"
  }
}
```

## Demo scenario: Nexus Industries Inc. corporate onboarding (APP-6005, default record)

The guided conversation, in order: "I need to onboard a new corporate client, Nexus Industries, for commercial banking services. They require treasury management, a credit line, and foreign exchange capabilities. This is a high-priority relationship worth potentially $8M in annual revenue." (`initiate_onboarding`); "What's the company profile? Have you verified their legitimacy?" (`kyc_verification`, APP-6005); "What about beneficial ownership? We need to be compliant with FinCEN rules." (`beneficial_ownership`); "Good. What documentation have we collected so far?" (`document_checklist`, APP-6005); "What's the status on product setup? Can we provision accounts now?" (`account_setup`); "When can they actually start using the account? What's the timeline?" (`onboarding_timeline`); "Are there any risks or red flags I should be aware of?" (`risk_assessment`); "Excellent. Send me a status summary and alert me when they're fully activated." (`status_summary`).

| Fact | Value |
|---|---|
| Client | Nexus Industries Inc., Delaware C-Corp, EIN 88-1234567 |
| Industry | Advanced Manufacturing (NAICS 332710); 17 years in business; $125M annual revenue; credit rating BBB+ |
| Products requested | Treasury management, Credit line, Foreign exchange (FX) |
| Revenue potential / priority | $8M potential annual revenue; HIGH - Strategic relationship; CRM case ONB-2025-4782 |
| KYC progress | 80.0% (4 of 5 checks complete/clear; enhanced due diligence in progress) |
| Beneficial owners | Sarah Morrison 45% verified; David Park 30% verified; Marcus Chen 25% pending (passport, within 2 hours); 2 of 3 Verified; CIP 67% (2 / 3) |
| Documentation | 75% Complete: 9 of 12 received; pending: beneficial ownership certification form (Marcus Chen), W-9 signature, board authorization for online banking |
| Provisioning plan | 80% prepared (4 of 5 items ready): operating account ****7823 commercial DDA; treasury ACH, wires, positive pay; $5M credit line pre-approved, credit committee Day 2 (tomorrow) 2 PM; FX spot and forward, $10M monthly limit; 3 online-banking admin users. Prepared for an authorized operator; nothing is provisioned by the agent |
| Timeline | 5-Day Fast Track: Day 1 beneficial ownership, Day 2 credit committee review at 2 PM, Day 3 signature cards, Day 4 compliance sign-offs, Day 5 go live, Week 2 RM introduction call; industry average 15-21 days, 67% faster ((15 - 5) / 15); success probability 95% |
| Risk | No significant red flags; industry risk moderate-low; minor note: Asian suppliers may need occasional OFAC screening on wire transfers |
| Status summary | Shareable table of all workstreams; the agent cannot send alerts later (No message was sent) |

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

# Product Provisioning Plan: APP-6005 Nexus Industries Inc.

**Status:** 80% prepared for authorized provisioning

| Product | Prepared configuration | Status |
|---|---|---|
| Operating account | Commercial DDA ****7823 reserved | Ready |
| Treasury management | ACH, wires, positive pay configured | Ready |
| Credit line | $5M pre-approved; credit committee review Day 2 (tomorrow) 2 PM; expected approval (strong financials) | Pending |
| FX services | Spot and forward contracts, $10M monthly aggregate limit | Ready |
| Online and mobile banking | 3 admin users configured; corporate mobile app access | Ready |

Everything except the credit line is ready for an authorized provisioning operator to activate in the core banking system; the credit line waits for the credit committee.

# Account Setup Preparation Reference

| Account Type | Min Deposit | Monthly Fee | APY | Features |
|---|---|---|---|---|
| Basic Savings | $25 | $0 | 0.5% | Online banking, Mobile deposit, ATM access |
| Premium Checking | $1,000 | $12 | 0.15% | No ATM fees, Overdraft protection, Bill pay |
| Commercial Checking | $5,000 | $25 | 0.1% | Treasury management, ACH origination, Wire transfers |
| Wealth Management | $250,000 | $0 | 1.25% | Dedicated advisor, Investment management, Trust services |
| Commercial Banking Suite | $25,000 | $150 | 0.2% | Commercial DDA, Treasury management (ACH, wires, positive pay), Credit line |

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

**Applications:** 5
**Total Estimated Assets:** $20,465,000

## Pipeline Status

- Kyc In Progress: 2
- Document Review: 1
- Enhanced Due Diligence: 1
- Setup Review Ready: 1

## Application Details

| App ID | Applicant | Account | Risk | Est. Assets | Status | RM |
|---|---|---|---|---|---|---|
| APP-6001 | Elena Brooks | Premium Checking | Low | $250,000 | Kyc In Progress | Michael Torres |
| APP-6002 | Blackwood Capital Partners LLC | Commercial Checking | Medium | $2,400,000 | Document Review | Jessica Nguyen |
| APP-6003 | Ahmed Al-Rashid | Wealth Management | High | $5,800,000 | Enhanced Due Diligence | Jessica Nguyen |
| APP-6004 | Maria Fontaine | Basic Savings | Low | $15,000 | Setup Review Ready | Michael Torres |
| APP-6005 | Nexus Industries Inc. | Commercial Banking Suite | Low | $12,000,000 | Kyc In Progress | Jessica Nguyen |
```

### FCO-05 — Relationship Manager

- Prompt: I need to onboard a new corporate client, Nexus Industries, for commercial banking: treasury management, a credit line and FX. It's a high-priority relationship worth about $8M a year.
- Operation: `initiate_onboarding`
- Arguments: `{}`
- Required factual anchors: `Nexus Industries Inc.`, `ONB-2025-4782`, `KYC Verification In Progress`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

Initiating corporate onboarding for Nexus Industries Inc. with the full commercial banking suite: KYC verification, corporate registration data, OFAC and sanctions screening, and product provisioning are prepared as parallel workstreams for authorized reviewers.

# Onboarding Initiated

| Detail | Value |
|---|---|
| Status | KYC Verification In Progress |
| Client Name | Nexus Industries Inc. |
| Onboarding Type | Corporate - Commercial Banking |
| Products Requested | Treasury management, Credit line, Foreign exchange (FX) |
| Estimated Annual Revenue | $8M potential |
| Priority Level | HIGH - Strategic relationship |
| CRM Case | ONB-2025-4782 |
| Relationship Manager | Jessica Nguyen |

## Parallel workstreams
- KYC and company verification (corporate registration, financial statements)
- OFAC and sanctions screening (entity and owners)
- Beneficial ownership (FinCEN) verification
- Product provisioning plan: treasury management, credit line, FX

Next: ask for the company profile to review the legitimacy evidence.
```

### FCO-06 — Compliance Officer

- Prompt: What about beneficial ownership on the Nexus file? We need to be compliant with FinCEN rules.
- Operation: `beneficial_ownership`
- Arguments: `{}`
- Required factual anchors: `Marcus Chen`, `2 of 3 Verified`, `67%`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

The company has 3 beneficial owners with 25%+ ownership. 2 are verified in the synthetic record; Marcus Chen is pending.

# Beneficial Ownership (FinCEN)

**Status:** 2 of 3 Verified - 1 Pending

| Owner | Ownership | Status | Note |
|---|---|---|---|
| Owner 1 - Sarah Morrison | 45% | Verified | Government-issued ID verified |
| Owner 2 - David Park | 30% | Verified | Government-issued ID verified |
| Owner 3 - Marcus Chen | 25% | Pending | Passport verification processing, expected within 2 hours |

- ID verification method: Government-issued ID + facial recognition
- PEP screening: All 3 cleared - no PEP matches
- Sanctions screening: All 3 cleared - no OFAC/EU matches
- Expected completion: Within 2 hours (passport processing)
- FinCEN compliance: On track for full compliance once the pending owner is verified
- CIP status: Customer Identification Program 67% complete

A KYC/AML reviewer confirms each owner before the file is cleared.
```

### FCO-07 — Relationship Manager

- Prompt: When can Nexus actually start using the account? What's the timeline?
- Operation: `onboarding_timeline`
- Arguments: `{}`
- Required factual anchors: `5-Day Fast Track`, `Credit committee review at 2 PM`, `67% faster`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

Timeline to full activation is 5 business days.

# Onboarding Timeline

**Status:** 5-Day Fast Track

| When | Step |
|---|---|
| Day 1 (Today) | Complete beneficial ownership verification |
| Day 2 (Tomorrow) | Credit committee review at 2 PM |
| Day 3 | Signature cards and service agreements |
| Day 4 | Final compliance sign-offs and testing |
| Day 5 | Full account activation - go live |
| Week 2 | Relationship manager introduction call |

- Industry average: 15-21 days (this plan is 67% faster)
- Client communication: daily status updates, sent by the relationship manager
- Success probability: 95% (strong financials + near-complete docs)

The relationship manager schedules the week-2 introduction call; no meeting has been booked.
```

### FCO-08 — Compliance Officer

- Prompt: Are there any risks or red flags I should be aware of for Nexus Industries?
- Operation: `risk_assessment`
- Arguments: `{}`
- Required factual anchors: `No significant red flags`, `Moderate-low`, `OFAC screening on wire transfers`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

No significant red flags detected.

# Risk Review: Nexus Industries Inc.

| Area | Finding |
|---|---|
| Screening | All screening results clean (OFAC, PEP, EU sanctions) |
| Financial position | Strong financial position with positive cash flow (credit rating BBB+) |
| Industry risk | Moderate-low for advanced manufacturing |
| Overall risk rating | Low |

**Minor note:** International suppliers in Asia may require occasional OFAC screening on wire transfers; standard for the industry and handled by routine wire screening.

A KYC/AML compliance reviewer confirms the risk rating before activation.
```

### FCO-09 — Head of Onboarding

- Prompt: Send me a status summary for the Nexus onboarding.
- Operation: `status_summary`
- Arguments: `{}`
- Required factual anchors: `Status Summary`, `ONB-2025-4782`, `No message was sent`

```text
> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

# Status Summary: Nexus Industries Inc. (ONB-2025-4782)

Ready for you to share with stakeholders:

| Workstream | Status |
|---|---|
| KYC and company verification | 80.0% (enhanced due diligence in progress) |
| Beneficial ownership (FinCEN) | 2 of 3 verified; CIP 67% |
| Documentation | 75% complete; pending: Beneficial ownership certification form, W-9 tax form, Board authorization |
| Product provisioning plan | 80% prepared; credit line awaits credit committee Day 2 (tomorrow) 2 PM |
| Timeline | 5-day fast track; full activation Day 5 |
| Risk | No significant red flags detected; overall low |

**Activation alert:** this agent cannot watch the file or notify you later. Set a reminder for Day 5 (full activation) or ask me for the status again. No message was sent.
```

## Evidence boundary

This snapshot does not authorize identity verification, sanctions or PEP clearance, KYC approval, applicant approval or rejection, customer outreach, account opening, product provisioning, or any external record change. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
