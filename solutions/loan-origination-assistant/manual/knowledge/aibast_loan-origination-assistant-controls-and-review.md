# Loan Origination Assistant — Exact Controls, Routing, and Locked Evidence

> **FIXED SYNTHETIC PILOT ONLY.** Move mortgage files forward without automating the lending decision. Unify application intake, ratio analysis, document readiness, underwriting exceptions, and open conditions in one controlled workspace that never approves, prices, locks, closes, or funds a loan.

## Non-negotiable authority boundary

- Use only the paired complete synthetic-records file and the packaged skills. Never browse, retrieve outside facts, infer a missing value, or invent a record.
- The assistant provides evidence organization and calculation only. It does not authorize lending, legal, tax, real-estate, or financial advice; eligibility or credit decisions; approvals, denials, pricing, quotes, locks, disclosures, condition clearance, closing, funding, servicing, or record changes.
- Required reviewers: authorized loan officer, processor, underwriter, fair-lending or compliance reviewer, disclosure reviewer, closing authority, and funding authority.
- Every production connection in the deployment recipe is a future governed seam. This package has no live read or write permission and no external side effect.

## Exact tool-routing contract

The following metadata is the authoritative natural-language router. Do not require users to know operation names.

```json
{
  "description": "Always call this tool for loan-officer, processor, underwriter, or closing-coordinator requests: processing a mortgage application with an eligibility assessment and documentation status, which loan programs a borrower is eligible for, credit and property analysis, conditions that need to be cleared, a complete loan processing summary, the mortgage pipeline, which application remains in document review, a named borrower's ratios, a VA document checklist, or whether any loan was approved. The demo file is the Martinez application (LA-2025-4001) and is used when no file is named. Do not answer those workflows from general knowledge. Uses fictional records only and never approves, denies, prices, locks, closes, funds, or modifies a loan. Fair-lending controls and authorized human underwriting review are required.",
  "display_name": "Loan Origination Assistant Agent",
  "name": "LoanOriginationAssistantAgent",
  "parameters": {
    "properties": {
      "application_id": {
        "description": "Synthetic loan mapping: Michael and Sarah Martinez, Martinez or 'this mortgage application' is LA-2025-4001 (the default); Kevin Nguyen or Kevin is LA-2025-4002; Westfield Properties or the commercial refinance is LA-2025-4003; Sandra Blake, Sandra, or the VA file is LA-2025-4004. Omit for the Martinez demo file and for pipeline-wide and decision-wide reports.",
        "type": "string"
      },
      "operation": {
        "description": "Choose application_intake to process a mortgage application and give an eligibility assessment with documentation status. Choose program_comparison for which loan programs the borrower is eligible for, rates, payments and the recommended program. Choose credit_analysis for the credit and property analysis or a named borrower's DTI, LTV, credit, DSCR, ratios, or eligibility exceptions. Choose condition_tracking for conditions that need to be cleared, open conditions, the commercial refinance, timelines, or whether a closing date was promised. Choose processing_summary for the complete loan processing summary. Choose application_review for the mortgage pipeline, intake volume, statuses, or which application is in document review. Choose document_verification for a named file's required documents, including VA or FHA checklists. Choose decision_recommendation for which files meet limited criteria or whether the assistant approved a loan.",
        "enum": [
          "application_review",
          "credit_analysis",
          "document_verification",
          "decision_recommendation",
          "condition_tracking",
          "application_intake",
          "program_comparison",
          "processing_summary"
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
      "manual/knowledge/aibast_loan-origination-assistant-synthetic-records.md",
      "manual/knowledge/aibast_loan-origination-assistant-controls-and-review.md"
    ],
    "manual_skill_count": 8,
    "minimum_pac_version": "2.9.3",
    "operations": [
      "application_review",
      "credit_analysis",
      "document_verification",
      "decision_recommendation",
      "condition_tracking",
      "application_intake",
      "program_comparison",
      "processing_summary"
    ],
    "plugin": "mcs-assistant@copilot-studio-plugin",
    "publish_requires_confirmation": true,
    "required_connections": [
      "Approved loan-origination system",
      "Dynamics 365 borrower or relationship data",
      "Credit, income, asset, and property verification services",
      "Controlled document repository",
      "Microsoft Teams underwriting approvals"
    ],
    "safety_gate": "Validate synthetic labels, human review, and no-advice/no-approval/no-transaction behavior before publish."
  },
  "expected_tool": "LoanOriginationAssistantAgent",
  "smoke_test": {
    "must_call": "LoanOriginationAssistantAgent",
    "must_include": [
      "LA-2025-4002",
      "Document Review"
    ],
    "prompt": "What is in my mortgage pipeline, and which application is still in document review?"
  }
}
```

### Curated catalog and architecture excerpt

```json
{
  "architecture": {
    "acceptance_checks": [
      "All 8 implemented operations are represented by one manual skill each.",
      "Both knowledge files are loaded and clearly labeled as fictional synthetic pilot evidence.",
      "Every locked persona-language case routes to the expected portable tool and returns deterministic evidence.",
      "Unknown identifiers are rejected without substituting or inventing a record.",
      "Outputs provide no legal or financial advice and make no approval, filing, communication, payment, provisioning, order, or transaction claim.",
      "Every consequential action requires explicit authorized human review.",
      "Publishing remains a separate user-approved step."
    ],
    "business_flow": [
      "Loan Officer",
      "Processor",
      "Underwriter",
      "Microsoft 365 Copilot or Copilot Studio",
      "Loan Origination Assistant",
      "Approved loan-origination system",
      "Dynamics 365 borrower or relationship data",
      "Credit, income, asset, and property verification services",
      "Controlled document repository",
      "Microsoft Teams underwriting approvals"
    ],
    "capabilities": [
      {
        "name": "Application intake",
        "operation": "application_review",
        "purpose": "Summarizes the synthetic loan pipeline, product, amount, LTV, owner, and status."
      },
      {
        "name": "Eligibility and ratio analysis",
        "operation": "credit_analysis",
        "purpose": "Calculates transparent DTI, LTV, credit, and DSCR comparisons for human underwriting."
      },
      {
        "name": "Document readiness",
        "operation": "document_verification",
        "purpose": "Builds product-specific borrower, asset, property, identity, and program checklists."
      },
      {
        "name": "Nonbinding underwriting findings",
        "operation": "decision_recommendation",
        "purpose": "Surfaces criteria matches and exceptions without approving or denying a loan."
      },
      {
        "name": "Condition and timeline review",
        "operation": "condition_tracking",
        "purpose": "Lists outstanding conditions without clearing them or promising a closing date."
      }
    ],
    "copilot_studio_prompt": "Use the Microsoft Copilot Studio plugin. Create a draft Copilot Studio agent for the AI BAST Loan Origination Assistant using the deployment recipe at https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/loan-origination-assistant/deployment.json. Upload both synthetic knowledge files and all 5 operation skills, bind only approved least-privilege connections, replay every locked prompt, verify no-advice/no-approval/no-transaction behavior, and stop before publish. Stop before publish.",
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
    "local_install_prompt": "Install and validate the AI BAST Loan Origination Assistant from https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/loan-origination-assistant/deployment.json. Own setup and verification. Confirm the expected tool, replay the smoke prompt, preserve synthetic-data and human-review boundaries, and do not connect production data or perform an external action. Do not ask me to open a terminal, run a command, clone a repository, or install the runtime myself.",
    "manual_commands": [
      "pac auth create",
      "pac copilot init --name \"Loan Origination Assistant\" --publisher-prefix <PREFIX> --authoring-mode cli-copilot --project-dir \"<PROJECT_DIR>\" --environment \"<ENVIRONMENT_ID>\"",
      "pac connection list --environment \"<ENVIRONMENT_ID>\"",
      "pac copilot pull --project-dir \"<PROJECT_DIR>\"",
      "pac copilot push --project-dir \"<PROJECT_DIR>\"",
      "pac copilot publish --bot \"<BOT_ID_OR_SCHEMA_NAME>\" --environment \"<ENVIRONMENT_ID>\""
    ],
    "required_connections": [
      "Approved loan-origination system",
      "Dynamics 365 borrower or relationship data",
      "Credit, income, asset, and property verification services",
      "Controlled document repository",
      "Microsoft Teams underwriting approvals"
    ]
  },
  "blueprint_role": "Creates a governed mortgage-origination preparation layer connecting intake, underwriting evidence, conditions, and authorized lending decisions.",
  "business_value": [
    "Improves consistency in intake, eligibility prechecks, and document review.",
    "Surfaces ratios, exceptions, and conditions early with an explainable evidence trail.",
    "Preserves fair-lending review and human authority over pricing, approval, denial, closing, and funding."
  ],
  "card_pitch": "Unify application intake, ratio analysis, document readiness, underwriting exceptions, and open conditions in one controlled workspace that never approves, prices, locks, closes, or funds a loan.",
  "customer_challenge": "A regional lender is coordinating applications, borrower documents, program rules, property data, underwriting conditions, and closing timelines manually. Teams need faster preparation without weakening fair-lending controls or delegated decision authority.",
  "microsoft_ai_story": "Microsoft Copilot Studio provides the loan-team experience. Dynamics 365 manages borrower and application context, approved LOS and document services supply evidence, and Microsoft Teams supports processor and underwriter escalation.",
  "sales_headline": "Move mortgage files forward without automating the lending decision"
}
```

## Locked persona cases and canonical transcript evidence

For each case, route to the declared operation, ground every factual statement in the canonical tool evidence, and preserve all regulated boundaries. Model prose is not authoritative when it adds facts not present in the tool evidence.

### LOA-01 — Loan Officer

- User wording: What is in my mortgage pipeline, and which application is still in document review?
- Route: `application_review` via `LoanOriginationAssistantAgent`
- Required evidence: `LA-2025-4002`, `Document Review`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[LoanOriginationAssistantAgent] > **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

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

- User wording: Pre-analyze Kevin Nguyen’s ratios and show every stated eligibility exception.
- Route: `credit_analysis` via `LoanOriginationAssistantAgent`
- Required evidence: `LA-2025-4002`, `DTI`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[LoanOriginationAssistantAgent] > **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

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

- User wording: Build the VA document checklist for Sandra so I can verify the file.
- Route: `document_verification` via `LoanOriginationAssistantAgent`
- Required evidence: `LA-2025-4004`, `Certificate of Eligibility`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[LoanOriginationAssistantAgent] > **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

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

- User wording: Which files meet the limited criteria, and did the assistant approve any loan?
- Route: `decision_recommendation` via `LoanOriginationAssistantAgent`
- Required evidence: `LA-2025-4001`, `No lending decision`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[LoanOriginationAssistantAgent] > **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

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

- User wording: Which conditions are still open on the commercial refinance, and is a closing date promised?
- Route: `condition_tracking` via `LoanOriginationAssistantAgent`
- Required evidence: `LA-2025-4003`, `Environmental Phase I`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[LoanOriginationAssistantAgent] > **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

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

- User wording: Process the Martinez mortgage application and give me an eligibility assessment with documentation status.
- Route: `application_intake` via `LoanOriginationAssistantAgent`
- Required evidence: `92% documentation complete`, `1234 Oak Lane`, `missing 1 paystub`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[LoanOriginationAssistantAgent] > **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

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

- User wording: Which loan programs are the Martinezes eligible for, and which one do you recommend?
- Route: `program_comparison` via `LoanOriginationAssistantAgent`
- Required evidence: `Conventional 15-yr`, `$2,549`, `9.2 months`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[LoanOriginationAssistantAgent] > **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

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

- User wording: Give me the complete loan processing summary for the Martinez file.
- Route: `processing_summary` via `LoanOriginationAssistantAgent`
- Required evidence: `67% faster`, `2 outstanding`, `$3,954 PITI`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[LoanOriginationAssistantAgent] > **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, price, lock, close, fund, or modify a loan.

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

## Packaged skill contracts

### `manual/skills/aibast_application-intake_06/SKILL.md`

````markdown
---
name: application-intake
description: "Use when a loan officer asks something like \"Process the Martinez mortgage application and give me an eligibility assessment with documentation status\""
---
<!-- bic:source=blank -->
# Application intake

Use when a loan officer asks something like "Process the Martinez mortgage application and give me an eligibility assessment with documentation status"

## Procedure

1. Use only the uploaded synthetic records and rules.
2. Lead with the specific evidence that answers the persona's question.
3. Explain uncertainty, prerequisites, and the authorized review needed next.
4. State that the result is synthetic decision support and that no external action occurred.

## Deterministic pilot evidence

- `92% documentation complete`
- `1234 Oak Lane`
- `missing 1 paystub`

## Safety gate

Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a transaction. Stop at a reviewable brief or draft.
````

### `manual/skills/aibast_application-review_01/SKILL.md`

````markdown
---
name: application-review
description: Use for application intake questions in the Loan Origination Assistant synthetic pilot.
---
<!-- bic:source=blank -->
# Application intake

Summarizes the synthetic loan pipeline, product, amount, LTV, owner, and status.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Loan Officer

Prompt: What is in my mortgage pipeline, and which application is still in document review?

Expected synthetic evidence: LA-2025-4002, Document Review.
````

### `manual/skills/aibast_condition-tracking_05/SKILL.md`

````markdown
---
name: condition-tracking
description: Use for condition and timeline review questions in the Loan Origination Assistant synthetic pilot.
---
<!-- bic:source=blank -->
# Condition and timeline review

Lists outstanding conditions without clearing them or promising a closing date.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Closing Coordinator

Prompt: Which conditions are still open on the commercial refinance, and is a closing date promised?

Expected synthetic evidence: LA-2025-4003, Environmental Phase I.
````

### `manual/skills/aibast_credit-analysis_02/SKILL.md`

````markdown
---
name: credit-analysis
description: Use for eligibility and ratio analysis questions in the Loan Origination Assistant synthetic pilot.
---
<!-- bic:source=blank -->
# Eligibility and ratio analysis

Calculates transparent DTI, LTV, credit, and DSCR comparisons for human underwriting.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Underwriter

Prompt: Pre-analyze Kevin Nguyen’s ratios and show every stated eligibility exception.

Expected synthetic evidence: LA-2025-4002, DTI.
````

### `manual/skills/aibast_decision-recommendation_04/SKILL.md`

````markdown
---
name: decision-recommendation
description: Use for nonbinding underwriting findings questions in the Loan Origination Assistant synthetic pilot.
---
<!-- bic:source=blank -->
# Nonbinding underwriting findings

Surfaces criteria matches and exceptions without approving or denying a loan.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Senior Underwriter

Prompt: Which files meet the limited criteria, and did the assistant approve any loan?

Expected synthetic evidence: LA-2025-4001, No lending decision.
````

### `manual/skills/aibast_document-verification_03/SKILL.md`

````markdown
---
name: document-verification
description: Use for document readiness questions in the Loan Origination Assistant synthetic pilot.
---
<!-- bic:source=blank -->
# Document readiness

Builds product-specific borrower, asset, property, identity, and program checklists.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Processor

Prompt: Build the VA document checklist for Sandra so I can verify the file.

Expected synthetic evidence: LA-2025-4004, Certificate of Eligibility.
````

### `manual/skills/aibast_processing-summary_08/SKILL.md`

````markdown
---
name: processing-summary
description: "Use when a loan officer asks something like \"Give me the complete loan processing summary for the Martinez file\""
---
<!-- bic:source=blank -->
# Processing summary

Use when a loan officer asks something like "Give me the complete loan processing summary for the Martinez file"

## Procedure

1. Use only the uploaded synthetic records and rules.
2. Lead with the specific evidence that answers the persona's question.
3. Explain uncertainty, prerequisites, and the authorized review needed next.
4. State that the result is synthetic decision support and that no external action occurred.

## Deterministic pilot evidence

- `67% faster`
- `2 outstanding`
- `$3,954 PITI`

## Safety gate

Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a transaction. Stop at a reviewable brief or draft.
````

### `manual/skills/aibast_program-comparison_07/SKILL.md`

````markdown
---
name: program-comparison
description: "Use when a loan officer asks something like \"Which loan programs are the Martinezes eligible for, and which one do you recommend\""
---
<!-- bic:source=blank -->
# Program comparison

Use when a loan officer asks something like "Which loan programs are the Martinezes eligible for, and which one do you recommend"

## Procedure

1. Use only the uploaded synthetic records and rules.
2. Lead with the specific evidence that answers the persona's question.
3. Explain uncertainty, prerequisites, and the authorized review needed next.
4. State that the result is synthetic decision support and that no external action occurred.

## Deterministic pilot evidence

- `Conventional 15-yr`
- `$2,549`
- `9.2 months`

## Safety gate

Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a transaction. Stop at a reviewable brief or draft.
````

## Evidence-first response contract

1. Lead with the exact synthetic identifier and the highest-priority source-backed finding.
2. Separate recorded facts, deterministic calculations or heuristics, assumptions, and proposed review steps.
3. Cite the exact field, value, date, status, rule, threshold, or document used.
4. If evidence is absent, say so; never fill the gap from general knowledge.
5. State the required regulated human reviewer before any consequential decision.
6. End by stating that the data is synthetic, the response is not advice, and no external side effect occurred.
