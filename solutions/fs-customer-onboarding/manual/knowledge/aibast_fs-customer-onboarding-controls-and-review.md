# Customer Onboarding Agent — Exact Controls, Routing, and Locked Evidence

> **FIXED SYNTHETIC PILOT ONLY.** Move every onboarding file to the next controlled review. Give onboarding, relationship, and compliance teams one governed view of KYC evidence, missing documents, service-setup preparation, and application ownership without claiming an identity check or account activation occurred.

## Non-negotiable authority boundary

- Use only the paired complete synthetic-records file and the packaged skills. Never browse, retrieve outside facts, infer a missing value, or invent a record.
- The assistant provides evidence organization and calculation only. It does not authorize identity verification, sanctions or PEP clearance, KYC approval, applicant approval or rejection, customer outreach, account opening, product provisioning, or any external record change.
- Required reviewers: authorized onboarding specialist, relationship owner, KYC/AML compliance reviewer, identity-verification reviewer, and account-provisioning operator.
- Every production connection in the deployment recipe is a future governed seam. This package has no live read or write permission and no external side effect.

## Exact tool-routing contract

The following metadata is the authoritative natural-language router. Do not require users to know operation names.

```json
{
  "description": "Always call this tool for onboarding-specialist, relationship-manager, or compliance requests about enhanced due diligence, KYC or PEP checks, which file is ready for account setup review, a business onboarding document list for Blackwood, beneficial ownership, or where the onboarding queue is stuck. Do not answer those workflows from general knowledge. Uses fictional records only; it never verifies identity, approves an applicant, opens or provisions an account, or provides legal, compliance, or financial advice. Every result requires authorized human review.",
  "display_name": "FS Customer Onboarding Agent",
  "name": "FSCustomerOnboardingAgent",
  "parameters": {
    "properties": {
      "application_id": {
        "description": "Synthetic application mapping: Sarah Chen is APP-6001; Blackwood Capital Partners, Blackwood, or the business onboarding file is APP-6002; Ahmed Al-Rashid or the enhanced-due-diligence case is APP-6003; Maria Fontaine or the setup-ready basic-savings file is APP-6004. Omit only for whole-pipeline reports.",
        "type": "string"
      },
      "operation": {
        "description": "Choose kyc_verification for screening and verification evidence; account_setup for a review-ready service configuration plan or which setup-ready file and product are being prepared; document_checklist for a named applicant's required documents, a business onboarding list, Blackwood, or beneficial ownership evidence; onboarding_status for queue status, bottlenecks, owners, and the whole pipeline.",
        "enum": [
          "kyc_verification",
          "account_setup",
          "document_checklist",
          "onboarding_status"
        ],
        "type": "string"
      }
    },
    "required": [
      "operation"
    ],
    "type": "object"
  }
}
```

## Deployment and architecture contract

### Deployment recipe excerpt

```json
{
  "copilot_studio": {
    "authoring_mode": "manual-upload",
    "manual_knowledge_files": [
      "manual/knowledge/aibast_fs-customer-onboarding-synthetic-records.md",
      "manual/knowledge/aibast_fs-customer-onboarding-controls-and-review.md"
    ],
    "manual_skill_count": 4,
    "minimum_pac_version": "2.9.3",
    "operations": [
      "kyc_verification",
      "account_setup",
      "document_checklist",
      "onboarding_status"
    ],
    "plugin": "mcs-assistant@copilot-studio-plugin",
    "publish_requires_confirmation": true,
    "required_connections": [
      "Dynamics 365 onboarding or CRM case data",
      "SharePoint controlled-document library",
      "Approved identity and sanctions-screening services",
      "Core-banking provisioning workflow",
      "Microsoft Teams approvals"
    ],
    "safety_gate": "Validate synthetic labels, human review, and no-advice/no-approval/no-transaction behavior before publish."
  },
  "expected_tool": "FSCustomerOnboardingAgent",
  "smoke_test": {
    "must_call": "FSCustomerOnboardingAgent",
    "must_include": [
      "APP-6003",
      "PEP"
    ],
    "prompt": "What is holding up the enhanced due diligence case, and which checks need my review?"
  }
}
```

### Curated catalog and architecture excerpt

```json
{
  "architecture": {
    "acceptance_checks": [
      "All 4 implemented operations are represented by one manual skill each.",
      "Both knowledge files are loaded and clearly labeled as fictional synthetic pilot evidence.",
      "Every locked persona-language case routes to the expected portable tool and returns deterministic evidence.",
      "Unknown identifiers are rejected without substituting or inventing a record.",
      "Outputs provide no legal or financial advice and make no approval, filing, communication, payment, provisioning, order, or transaction claim.",
      "Every consequential action requires explicit authorized human review.",
      "Publishing remains a separate user-approved step."
    ],
    "business_flow": [
      "Onboarding Specialist",
      "Relationship Manager",
      "Compliance Officer",
      "Microsoft 365 Copilot or Copilot Studio",
      "Customer Onboarding Agent",
      "Dynamics 365 onboarding or CRM case data",
      "SharePoint controlled-document library",
      "Approved identity and sanctions-screening services",
      "Core-banking provisioning workflow",
      "Microsoft Teams approvals"
    ],
    "capabilities": [
      {
        "name": "KYC evidence review",
        "operation": "kyc_verification",
        "purpose": "Summarizes identity, sanctions, PEP, adverse-media, and enhanced-due-diligence evidence without verifying a real person."
      },
      {
        "name": "Account setup preparation",
        "operation": "account_setup",
        "purpose": "Builds a review-ready service configuration reference without opening or provisioning an account."
      },
      {
        "name": "Document readiness",
        "operation": "document_checklist",
        "purpose": "Creates an applicant-specific KYC document checklist for authorized review."
      },
      {
        "name": "Onboarding pipeline",
        "operation": "onboarding_status",
        "purpose": "Surfaces application status, risk tier, owner, and next-review context across the synthetic pipeline."
      }
    ],
    "copilot_studio_prompt": "Use the Microsoft Copilot Studio plugin. Create a draft Copilot Studio agent for the AI BAST Customer Onboarding Agent using the deployment recipe at https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/fs-customer-onboarding/deployment.json. Upload both synthetic knowledge files and all 4 operation skills, bind only approved least-privilege connections, replay every locked prompt, verify no-advice/no-approval/no-transaction behavior, and stop before publish. Stop before publish.",
    "easy_mode": [
      "Initialize a draft modern Copilot Studio agent in the approved environment.",
      "Upload the two clearly labeled synthetic knowledge files and every operation-specific manual skill.",
      "Bind approved least-privilege connection references only; keep consequential actions behind explicit approval.",
      "Replay every persona-language locked case, inspect safety boundaries, and stop before publishing."
    ],
    "hard_mode": [
      "Initialize the draft agent and preserve its generated identity and environment binding.",
      "Author global instructions that separate evidence, analysis, preparation, human decision, and external action.",
      "Upload the two synthetic knowledge files and one SKILL.md per implemented operation.",
      "Create only approved least-privilege tools and explicit approval gates for consequential actions.",
      "Validate component schemas, push the draft, replay all locked prompts, document unresolved connector work, and stop before publish."
    ],
    "local_install_prompt": "Install and validate the AI BAST Customer Onboarding Agent from https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/fs-customer-onboarding/deployment.json. Own setup and verification. Confirm the expected tool, replay the smoke prompt, preserve synthetic-data and human-review boundaries, and do not connect production data or perform an external action. Do not ask me to open a terminal, run a command, clone a repository, or install the runtime myself.",
    "manual_commands": [
      "pac auth create",
      "pac copilot init --name \"Customer Onboarding Agent\" --publisher-prefix <PREFIX> --authoring-mode cli-copilot --project-dir \"<PROJECT_DIR>\" --environment \"<ENVIRONMENT_ID>\"",
      "pac connection list --environment \"<ENVIRONMENT_ID>\"",
      "pac copilot pull --project-dir \"<PROJECT_DIR>\"",
      "pac copilot push --project-dir \"<PROJECT_DIR>\"",
      "pac copilot publish --bot \"<BOT_ID_OR_SCHEMA_NAME>\" --environment \"<ENVIRONMENT_ID>\""
    ],
    "required_connections": [
      "Dynamics 365 onboarding or CRM case data",
      "SharePoint controlled-document library",
      "Approved identity and sanctions-screening services",
      "Core-banking provisioning workflow",
      "Microsoft Teams approvals"
    ]
  },
  "blueprint_role": "Creates a controlled onboarding front door that connects customer intake, KYC evidence, compliance review, service configuration, and human approval.",
  "business_value": [
    "Improves visibility into KYC evidence, missing documents, and application ownership.",
    "Reduces avoidable handoff friction by presenting one review-ready onboarding record.",
    "Preserves control boundaries by separating preparation from identity verification, approval, and account provisioning."
  ],
  "card_pitch": "Give onboarding, relationship, and compliance teams one governed view of KYC evidence, missing documents, service-setup preparation, and application ownership without claiming an identity check or account activation occurred.",
  "customer_challenge": "A financial institution is coordinating identity evidence, sanctions and PEP review, document collection, product setup, and customer updates across disconnected systems. Manual handoffs create delays while making it difficult to prove that required checks occurred before activation.",
  "microsoft_ai_story": "Microsoft Copilot Studio provides the governed conversational layer. Dynamics 365 holds the onboarding case, SharePoint stores controlled documents, and Microsoft Teams supports reviewer escalation and approval. Approved identity, screening, and core-banking connectors remain behind explicit authorization gates.",
  "sales_headline": "Move every onboarding file to the next controlled review"
}
```

## Locked persona cases and canonical transcript evidence

For each case, route to the declared operation, ground every factual statement in the canonical tool evidence, and preserve all regulated boundaries. Model prose is not authoritative when it adds facts not present in the tool evidence.

### FCO-01 — Compliance Officer

- User wording: What is holding up the enhanced due diligence case, and which checks need my review?
- Route: `kyc_verification` via `FSCustomerOnboardingAgent`
- Required evidence: `APP-6003`, `PEP`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FSCustomerOnboardingAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

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
[FSCustomerOnboardingAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

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

- User wording: Which approved-looking file is ready for account setup review, and what product is being prepared?
- Route: `account_setup` via `FSCustomerOnboardingAgent`
- Required evidence: `APP-6004`, `Basic Savings`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FSCustomerOnboardingAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

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

- User wording: Give me the business onboarding document list for Blackwood before I call them.
- Route: `document_checklist` via `FSCustomerOnboardingAgent`
- Required evidence: `APP-6002`, `Beneficial ownership`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FSCustomerOnboardingAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

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

- User wording: Where is the onboarding queue stuck, and who owns each application?
- Route: `onboarding_status` via `FSCustomerOnboardingAgent`
- Required evidence: `APP-6001`, `APP-6003`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FSCustomerOnboardingAgent] > **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. This output is operational decision support, not legal, compliance, or financial advice. It does not verify a real identity, approve an application, provision an account, or complete a transaction.

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

## Packaged skill contracts

### `manual/skills/aibast_account-setup_02/SKILL.md`

````markdown
---
name: account-setup
description: Use for account setup preparation questions in the Customer Onboarding Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Account setup preparation

Builds a review-ready service configuration reference without opening or provisioning an account.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Onboarding Specialist

Prompt: Which approved-looking file is ready for account setup review, and what product is being prepared?

Expected synthetic evidence: APP-6004, Basic Savings.
````

### `manual/skills/aibast_document-checklist_03/SKILL.md`

````markdown
---
name: document-checklist
description: Use for document readiness questions in the Customer Onboarding Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Document readiness

Creates an applicant-specific KYC document checklist for authorized review.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Relationship Manager

Prompt: Give me the business onboarding document list for Blackwood before I call them.

Expected synthetic evidence: APP-6002, Beneficial ownership.
````

### `manual/skills/aibast_kyc-verification_01/SKILL.md`

````markdown
---
name: kyc-verification
description: Use for kyc evidence review questions in the Customer Onboarding Agent synthetic pilot.
---
<!-- bic:source=blank -->
# KYC evidence review

Summarizes identity, sanctions, PEP, adverse-media, and enhanced-due-diligence evidence without verifying a real person.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Compliance Officer

Prompt: What is holding up the enhanced due diligence case, and which checks need my review?

Expected synthetic evidence: APP-6003, PEP.
````

### `manual/skills/aibast_onboarding-status_04/SKILL.md`

````markdown
---
name: onboarding-status
description: Use for onboarding pipeline questions in the Customer Onboarding Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Onboarding pipeline

Surfaces application status, risk tier, owner, and next-review context across the synthetic pipeline.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Head of Onboarding

Prompt: Where is the onboarding queue stuck, and who owns each application?

Expected synthetic evidence: APP-6001, APP-6003.
````

## Evidence-first response contract

1. Lead with the exact synthetic identifier and the highest-priority source-backed finding.
2. Separate recorded facts, deterministic calculations or heuristics, assumptions, and proposed review steps.
3. Cite the exact field, value, date, status, rule, threshold, or document used.
4. If evidence is absent, say so; never fill the gap from general knowledge.
5. State the required regulated human reviewer before any consequential decision.
6. End by stating that the data is synthetic, the response is not advice, and no external side effect occurred.
