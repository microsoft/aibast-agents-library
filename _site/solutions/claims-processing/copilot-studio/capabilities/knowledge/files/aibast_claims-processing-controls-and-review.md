# Claims Processing Agent — Exact Controls, Routing, and Locked Evidence

> **FIXED SYNTHETIC PILOT ONLY.** Prepare every claim for the right human review. Bring intake, policy terms, documents, fraud indicators, and nonbinding settlement estimates into one adjuster workspace without claiming approval, denial, payment, or coverage action.

## Non-negotiable authority boundary

- Use only the paired complete synthetic-records file and the packaged skills. Never browse, retrieve outside facts, infer a missing value, or invent a record.
- The assistant provides evidence organization and calculation only. It does not authorize legal, insurance, coverage, settlement, or financial advice; fraud, liability, causation, coverage, approval, denial, reserve, settlement, payment, outreach, referral, or record-change decisions.
- Required reviewers: authorized claims adjuster, claims manager, SIU investigator, legal or compliance reviewer, coverage authority, and payment authority.
- Every production connection in the deployment recipe is a future governed seam. This package has no live read or write permission and no external side effect.

## Exact tool-routing contract

The following metadata is the authoritative natural-language router. Do not require users to know operation names.

```json
{
  "description": "Use for claims-adjuster, claims-manager, SIU, or claims-operations requests. Call this tool when the user asks to process the incoming claims queue and separate immediate attention from auto-adjudication, for fraud detection results and high-risk claims, to auto-adjudicate the eligible claims, for the complex claims prepared for adjusters, for processing metrics and improvements, for a summary of today's work, which incoming claim needs specialized handling, what is missing from a named claimant's file before evaluation, which claim crosses an SIU threshold, whether a fraud score proves fraud, or for policy-term estimates and approval/payment status boundaries. Always call this tool for those claims-workflow requests rather than answering from general knowledge, including when the user asks whether any claim was approved or paid. Uses fictional records only; a fraud flag is not proof, and the tool never approves, denies, reserves, settles, pays, or changes a claim. Authorized adjuster review is required.",
  "display_name": "Claims Processing Agent",
  "name": "ClaimsProcessingAgent",
  "parameters": {
    "properties": {
      "claim_id": {
        "description": "Use the synthetic claim identifier when the user names a file or claimant: the complex water-damage file is CLM-78445; Margaret Sullivan is CLM-2025-7001; David Park is CLM-2025-7002; Apex Commercial Properties is CLM-2025-7003; Jennifer Liu or the theft file is CLM-2025-7004. Omit only for whole-queue reports.",
        "type": "string"
      },
      "operation": {
        "description": "Choose claim_intake to process the incoming claims queue, immediate attention vs auto-adjudication, specialized handling, routing, or workload questions. Choose adjudication_review for the complex claims prepared for adjuster review (default CLM-78445), a named claim or claimant, missing documents, file completeness, policy evidence, adjuster notes, or what is needed before evaluation. Choose fraud_flag for fraud detection results, high-risk claims, SIU thresholds, fraud indicators, referrals, or whether a score proves fraud. Choose auto_adjudication to auto-adjudicate the eligible claims and show the results (recommended outcomes awaiting adjuster sign-off). Choose processing_metrics for metrics and where we can improve. Choose session_summary to summarize everything accomplished today. Choose settlement_recommendation for nonbinding policy-term estimates or questions asking whether any claim was approved, denied, settled, or paid; this operation returns the source-backed boundary that no approval or payment occurred.",
        "enum": [
          "claim_intake",
          "adjudication_review",
          "fraud_flag",
          "settlement_recommendation",
          "auto_adjudication",
          "processing_metrics",
          "session_summary"
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
      "manual/knowledge/aibast_claims-processing-synthetic-records.md",
      "manual/knowledge/aibast_claims-processing-controls-and-review.md"
    ],
    "manual_skill_count": 7,
    "minimum_pac_version": "2.9.3",
    "operations": [
      "claim_intake",
      "adjudication_review",
      "fraud_flag",
      "settlement_recommendation",
      "auto_adjudication",
      "processing_metrics",
      "session_summary"
    ],
    "plugin": "mcs-assistant@copilot-studio-plugin",
    "publish_requires_confirmation": true,
    "required_connections": [
      "Dynamics 365 claims case data",
      "Policy-administration system",
      "SharePoint or approved claims document repository",
      "SIU case workflow",
      "Microsoft Teams adjuster approvals"
    ],
    "safety_gate": "Validate synthetic labels, human review, and no-advice/no-approval/no-transaction behavior before publish.",
    "validated_manual": {
      "bot_id": "72ff18d3-f6ba-45c9-a85f-3ef0cbf472be",
      "display_name": "Claims Processing Manual",
      "environment_id": "ee67a404-325c-e726-a18a-886fe708ca0b",
      "environment_name": "kodyv8",
      "knowledge_files": 2,
      "model": "Sonnet46",
      "preview_cases_passed": 4,
      "preview_cases_total": 4,
      "published": false,
      "skills": 4,
      "status": "Draft",
      "web_search_removed": true
    },
    "validated_pilot": {
      "bot_id": "561829d3-0ef5-4e70-a518-65bcce23f89a",
      "changes_pushed": 7,
      "display_name": "Claims Processing Pilot",
      "environment_id": "ee67a404-325c-e726-a18a-886fe708ca0b",
      "environment_name": "kodyv8",
      "knowledge_files": 2,
      "model": "Sonnet46",
      "preview_cases_passed": 4,
      "preview_cases_total": 4,
      "published": false,
      "schema_name": "aibast_ClaimsProcessingPilot",
      "skills": 4,
      "status": "Draft"
    }
  },
  "expected_tool": "ClaimsProcessingAgent",
  "smoke_test": {
    "must_call": "ClaimsProcessingAgent",
    "must_include": [
      "CLM-2025-7003",
      "Investigation"
    ],
    "prompt": "Which incoming claim needs specialized handling first, and where should it be reviewed?"
  }
}
```

### Curated catalog and architecture excerpt

```json
{
  "architecture": {
    "acceptance_checks": [
      "All 7 implemented operations are represented by one manual skill each.",
      "Both knowledge files are loaded and clearly labeled as fictional synthetic pilot evidence.",
      "Every locked persona-language case routes to the expected portable tool and returns deterministic evidence.",
      "Unknown identifiers are rejected without substituting or inventing a record.",
      "Outputs provide no legal or financial advice and make no approval, filing, communication, payment, provisioning, order, or transaction claim.",
      "Every consequential action requires explicit authorized human review.",
      "Publishing remains a separate user-approved step."
    ],
    "business_flow": [
      "Claims Adjuster",
      "Claims Manager",
      "SIU Investigator",
      "Operations Leader",
      "Microsoft 365 Copilot or Copilot Studio",
      "Claims Processing Agent",
      "Dynamics 365 claims case data",
      "Policy-administration system",
      "SharePoint or approved claims document repository",
      "SIU case workflow",
      "Microsoft Teams adjuster approvals"
    ],
    "capabilities": [
      {
        "name": "Claims intake triage",
        "operation": "claim_intake",
        "purpose": "Summarizes fictional claims by loss, amount, status, and fraud-review score."
      },
      {
        "name": "Claim-file readiness",
        "operation": "adjudication_review",
        "purpose": "Combines policy terms, loss evidence, documents, and adjuster notes for human review."
      },
      {
        "name": "SIU indicator review",
        "operation": "fraud_flag",
        "purpose": "Surfaces explainable fraud indicators without declaring fraud or changing coverage."
      },
      {
        "name": "Policy-term settlement estimate",
        "operation": "settlement_recommendation",
        "purpose": "Calculates a nonbinding coverage-limit and deductible estimate without approving, denying, reserving, settling, or paying."
      },
      {
        "name": "Auto-adjudication recommendations",
        "operation": "auto_adjudication",
        "purpose": "Recommends approve, deny or needs-info outcomes for eligible claims with efficiency and quality metrics; adjusters release them."
      },
      {
        "name": "Processing metrics and improvements",
        "operation": "processing_metrics",
        "purpose": "Compares before/after cycle time, auto-adjudication rate, cost per claim and CSAT and lists optimization opportunities."
      },
      {
        "name": "Session summary",
        "operation": "session_summary",
        "purpose": "Summarizes today's processing, fraud, complex-file and efficiency results without claiming any payment."
      }
    ],
    "copilot_studio_prompt": "Use the Microsoft Copilot Studio plugin. Create a draft Copilot Studio agent for the AI BAST Claims Processing Agent using the deployment recipe at https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/claims-processing/deployment.json. Upload both synthetic knowledge files and all 4 operation skills, bind only approved least-privilege connections, replay every locked prompt, verify no-advice/no-approval/no-transaction behavior, and stop before publish. Stop before publish.",
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
    "local_install_prompt": "Install and validate the AI BAST Claims Processing Agent from https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/claims-processing/deployment.json. Own setup and verification. Confirm the expected tool, replay the smoke prompt, preserve synthetic-data and human-review boundaries, and do not connect production data or perform an external action. Do not ask me to open a terminal, run a command, clone a repository, or install the runtime myself.",
    "manual_commands": [
      "pac auth create",
      "pac copilot init --name \"Claims Processing Agent\" --publisher-prefix <PREFIX> --authoring-mode cli-copilot --project-dir \"<PROJECT_DIR>\" --environment \"<ENVIRONMENT_ID>\"",
      "pac connection list --environment \"<ENVIRONMENT_ID>\"",
      "pac copilot pull --project-dir \"<PROJECT_DIR>\"",
      "pac copilot push --project-dir \"<PROJECT_DIR>\"",
      "pac copilot publish --bot \"<BOT_ID_OR_SCHEMA_NAME>\" --environment \"<ENVIRONMENT_ID>\""
    ],
    "required_connections": [
      "Dynamics 365 claims case data",
      "Policy-administration system",
      "SharePoint or approved claims document repository",
      "SIU case workflow",
      "Microsoft Teams adjuster approvals"
    ]
  },
  "blueprint_role": "Creates a governed claims-preparation layer connecting intake, policy evidence, SIU review, adjudication, and authorized claim decisions.",
  "business_value": [
    "Improves consistency in claim intake and file-readiness review.",
    "Connects fraud indicators to source evidence without presenting a score as proof.",
    "Keeps approval, denial, reserving, settlement, and payment with authorized claims professionals."
  ],
  "card_pitch": "Bring intake, policy terms, documents, fraud indicators, and nonbinding settlement estimates into one adjuster workspace without claiming approval, denial, payment, or coverage action.",
  "customer_challenge": "An insurer is processing claims through separate intake, policy, document, SIU, and adjudication systems. Adjusters spend time rebuilding files while automated scoring can be mistaken for a coverage or fraud decision.",
  "microsoft_ai_story": "Microsoft Copilot Studio provides the adjuster-facing experience. Dynamics 365 manages the claim, SharePoint or an approved content service stores evidence, policy administration supplies terms, and Microsoft Teams supports adjuster and SIU review.",
  "sales_headline": "Prepare every claim for the right human review"
}
```

## Locked persona cases and canonical transcript evidence

For each case, route to the declared operation, ground every factual statement in the canonical tool evidence, and preserve all regulated boundaries. Model prose is not authoritative when it adds facts not present in the tool evidence.

### CLP-01 — Claims Operations Leader

- User wording: Process the incoming claims queue and identify which ones need immediate attention vs auto-adjudication.
- Route: `claim_intake` via `ClaimsProcessingAgent`
- Required evidence: `2,847`, `1,936`, `34 claims with regulatory deadlines`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[ClaimsProcessingAgent] > **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

# Claims Intake Dashboard

I've analyzed today's 2,847 incoming claims. 68% qualify for auto-adjudication, saving 5,807 adjuster hours.

## Claims Queue Analysis

| Category | Claims | % of Total | Recommended Action |
|---|---|---|---|
| Auto-adjudicate | 1,936 | 68% | Instant processing (recommendation for sign-off) |
| Standard review | 624 | 22% | Adjuster queue |
| Complex/High-value | 198 | 7% | Senior adjuster |
| Fraud investigation | 89 | 3% | SIU referral |

## Priority Flags Detected

- 34 claims with regulatory deadlines in 48 hours
- 18 claims from VIP policyholders
- 12 claims with litigation potential
- 8 catastrophe-related claims (expedited handling)

## Auto-Adjudication Eligible

- Simple auto claims under $5,000
- Routine medical with matching codes
- Property claims with verified estimates
- Average processing: 4 minutes vs 3 days

Next step: see the fraud detection results?

## Sample Claim Files

**Total Claims:** 5
**Total Claimed:** $696,700
**Avg Fraud Score:** 27.6

| Claim ID | Claimant | Policy Type | Loss | Amount | Status | Fraud |
|---|---|---|---|---|---|---|
| CLM-78445 | Homeowner policyholder (water loss) | Homeowners | Water Damage | $127,000 | Complex Prepared | 8 |
| CLM-2025-7001 | Margaret Sullivan | Homeowners | Water Damage | $28,500 | Under Review | 12 |
| CLM-2025-7002 | David Park | Auto | Collision | $14,200 | Ready For Adjuster Review | 5 |
| CLM-2025-7003 | Apex Commercial Properties | Commercial Property | Fire Damage | $485,000 | Investigation | 68 |
| CLM-2025-7004 | Jennifer Liu | Homeowners | Theft | $42,000 | Pending Documentation | 45 |

## Status Distribution

- Complex Prepared: 1
- Under Review: 1
- Ready For Adjuster Review: 1
- Investigation: 1
- Pending Documentation: 1
```

### CLP-02 — Claims Adjuster

- User wording: What is missing from Jennifer Liu’s theft file before I can evaluate it?
- Route: `adjudication_review` via `ClaimsProcessingAgent`
- Required evidence: `CLM-2025-7004`, `Receipts or appraisals`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[ClaimsProcessingAgent] > **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

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

## Missing Before Evaluation

- [ ] Itemized list of stolen items
- [ ] Receipts or appraisals

## Adjuster Notes

- Police report filed but no suspects identified
- Itemized list of stolen items requested
- Receipts or appraisals needed for jewelry and collectibles
```

### CLP-03 — SIU Investigator

- User wording: Yes, show me the fraud detection results and high-risk claims.
- Route: `fraud_flag` via `ClaimsProcessingAgent`
- Required evidence: `89 suspicious claims`, `CLM-78234`, `$890K`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[ClaimsProcessingAgent] > **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

# Fraud Detection Report

Fraud analysis identified 89 suspicious claims worth $2.4M. 12 are high-confidence fraud referrals (a flag is not proof of fraud).

| Risk Level | Claims | Total Value | Action |
|---|---|---|---|
| High (80%+) | 12 | $890K | SIU immediate |
| Medium (50-79%) | 41 | $1.1M | Enhanced review |
| Low (25-49%) | 36 | $420K | Flag for adjuster |

## Top High-Risk Claims

| Claim # | Type | Fraud Indicators |
|---|---|---|
| CLM-78234 | Auto | Staged accident pattern |
| CLM-78156 | Medical | Provider billing anomaly |
| CLM-78089 | Property | Recent policy change |

## CLM-78234 Deep Analysis (SIU evidence package draft)

- Claimant filed 3 claims in 18 months
- Accident location matches known staging area
- Body shop on fraud watch list
- Similar claims from same intersection

**Estimated Fraud Savings:** $890K prevented if high-risk confirmed (estimate).

Next step: proceed with auto-adjudication recommendations for eligible claims?

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

- User wording: Show the policy-term estimates and state clearly whether any claim was approved or paid.
- Route: `settlement_recommendation` via `ClaimsProcessingAgent`
- Required evidence: `CLM-2025-7002`, `No approval`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[ClaimsProcessingAgent] > **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

# Policy-Term Settlement Estimates for Adjuster Review

| Claim ID | Claimant | Claimed | Deductible | Fraud Score | Review Estimate |
|---|---|---|---|---|---|
| CLM-78445 | Homeowner policyholder (water loss) | $127,000 | $2,500 | 8 | $124,500 |
| CLM-2025-7001 | Margaret Sullivan | $28,500 | $1,500 | 12 | $27,000 |
| CLM-2025-7002 | David Park | $14,200 | $500 | 5 | $13,700 |
| CLM-2025-7003 | Apex Commercial Properties | $485,000 | $10,000 | 68 | Hold pending SIU |
| CLM-2025-7004 | Jennifer Liu | $42,000 | $2,000 | 45 | $40,000 |

**Total Claimed:** $696,700
**Aggregate Review Estimate (excluding SIU holds):** $205,200

Fraud scores do not reduce or eliminate coverage. An authorized adjuster must validate coverage, causation, documentation, exclusions, jurisdictional rules, and SIU findings. No approval, denial, settlement, reserve, or payment has occurred.
```

### CLP-05 — Claims Manager

- User wording: Yes, auto-adjudicate the eligible claims and show me the results.
- Route: `auto_adjudication` via `ClaimsProcessingAgent`
- Required evidence: `1,724`, `$290,350`, `sign-off`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[ClaimsProcessingAgent] > **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

# Auto-Adjudication Recommendations

1,936 eligible claims evaluated against the guidelines. Outcomes below are recommendations; release requires authorized adjuster sign-off.

| Recommended Outcome | Claims | Total Value | Avg Time |
|---|---|---|---|
| Approve | 1,724 | $4.2M | 3.8 min |
| Deny | 142 | $380K | 2.1 min |
| Needs info | 70 | $290K | 4.2 min |

## Approval Breakdown

- Auto physical damage: 892 claims ($1.8M)
- Medical routine: 534 claims ($1.6M)
- Property minor: 298 claims ($800K)

## Denial Reasons

- Coverage exclusion: 68 claims
- Policy lapsed: 42 claims
- Duplicate submission: 32 claims

## Efficiency Gains

- Traditional processing: 5,808 hours
- AI processing: 18 minutes
- Hours saved: 5,807 (99.98%)
- Cost savings: $290,350 (at $50/hour)

## Quality Metrics

- Auto-decision accuracy: 99.2%
- Within payment guidelines: 100%

No approval, denial, or payment has occurred; adjusters release the recommendations.

Next step: review the complex claims prepared for adjusters?
```

### CLP-06 — Claims Operations Leader

- User wording: Yes, show me the metrics and where we can improve further.
- Route: `processing_metrics` via `ClaimsProcessingAgent`
- Required evidence: `5.2 days`, `+467%`, `Mobile photo AI assessment`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[ClaimsProcessingAgent] > **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

# Claims Processing Metrics

Cycle time improved 57%. Additional optimization can reduce cycle time to about 4 days.

| Metric | Before AI | With AI | Change |
|---|---|---|---|
| Avg cycle time | 12 days | 5.2 days | -57% |
| Auto-adjudication | 12% | 68% | +467% |
| Cost per claim | $142 | $48 | -66% |
| Customer satisfaction | 3.2/5 | 4.4/5 | +38% |

## Optimization Opportunities

| Improvement | Impact | Effort |
|---|---|---|
| Expand auto-adjudication rules | +8% auto rate | Medium |
| Mobile photo AI assessment | -1 day cycle | Low |
| Real-time status updates | +0.3 CSAT | Low |
| Provider network integration | -2 days medical | High |

Next step: summarize everything accomplished today?
```

### CLP-07 — Claims Operations Leader

- User wording: Yes, summarize everything we accomplished today.
- Route: `session_summary` via `ClaimsProcessingAgent`
- Required evidence: `2,847 total`, `5,807 adjuster hours`, `$290,350`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[ClaimsProcessingAgent] > **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

# Claims Processing Session Summary

| Accomplishment | Result |
|---|---|
| Claims processed | 2,847 total |
| Auto-adjudication recommendations | 1,936 (68%) in 18 minutes |
| Fraud identified | 89 claims, $2.4M flagged for SIU review |
| Complex prepared | 198 claims with AI analysis |
| Payments recommended | $4.2M awaiting adjuster release |

## Efficiency Gains

| Metric | Value |
|---|---|
| Hours saved | 5,807 adjuster hours |
| Cost savings | $290,350 today |
| Cycle time reduction | 57% (12 to 5.2 days) |

No approval, denial, settlement, or payment has occurred; each needs authorized adjuster sign-off.
```
## Status Distribution

- Under Review: 1
- Ready For Adjuster Review: 1
- Investigation: 1
- Pending Documentation: 1
```

### CLP-02 — Claims Adjuster

- User wording: What is missing from Jennifer Liu’s theft file before I can evaluate it?
- Route: `adjudication_review` via `ClaimsProcessingAgent`
- Required evidence: `CLM-2025-7004`, `Receipts or appraisals`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[ClaimsProcessingAgent] > **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

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

- User wording: Which claim crosses the SIU review threshold, and does that prove fraud?
- Route: `fraud_flag` via `ClaimsProcessingAgent`
- Required evidence: `CLM-2025-7003`, `SIU Referrals`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[ClaimsProcessingAgent] > **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

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
[ClaimsProcessingAgent] > **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

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

- User wording: Show the policy-term estimates and state clearly whether any claim was approved or paid.
- Route: `settlement_recommendation` via `ClaimsProcessingAgent`
- Required evidence: `CLM-2025-7002`, `No approval`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[ClaimsProcessingAgent] > **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, reserve, or change a claim.

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

## Packaged skill contracts

### `manual/skills/aibast_adjudication-review_02/SKILL.md`

````markdown
---
name: adjudication-review
description: Use for claim-file readiness questions in the Claims Processing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Claim-file readiness

Combines policy terms, loss evidence, documents, and adjuster notes for human review.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Claims Adjuster

Prompt: What is missing from Jennifer Liu’s theft file before I can evaluate it?

Expected synthetic evidence: CLM-2025-7004, Receipts or appraisals.
````

### `manual/skills/aibast_auto-adjudication_05/SKILL.md`

````markdown
---
name: auto-adjudication
description: "Use when a claims manager asks something like \"Yes, auto-adjudicate the eligible claims and show me the results\""
---
<!-- bic:source=blank -->
# Auto adjudication

Use when a claims manager asks something like "Yes, auto-adjudicate the eligible claims and show me the results"

## Procedure

1. Use only the uploaded synthetic records and rules.
2. Lead with the specific evidence that answers the persona's question.
3. Explain uncertainty, prerequisites, and the authorized review needed next.
4. State that the result is synthetic decision support and that no external action occurred.

## Deterministic pilot evidence

- `1,724`
- `$290,350`
- `sign-off`

## Safety gate

Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a transaction. Stop at a reviewable brief or draft.
````

### `manual/skills/aibast_claim-intake_01/SKILL.md`

````markdown
---
name: claim-intake
description: Use for claims intake triage questions in the Claims Processing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Claims intake triage

Summarizes fictional claims by loss, amount, status, and fraud-review score.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Claims Operations Leader

Prompt: Process the incoming claims queue and identify which ones need immediate attention vs auto-adjudication.

Expected synthetic evidence: 2,847, 1,936, 34 claims with regulatory deadlines.
````

### `manual/skills/aibast_fraud-flag_03/SKILL.md`

````markdown
---
name: fraud-flag
description: Use for siu indicator review questions in the Claims Processing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# SIU indicator review

Surfaces explainable fraud indicators without declaring fraud or changing coverage.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: SIU Investigator

Prompt: Yes, show me the fraud detection results and high-risk claims.

Expected synthetic evidence: 89 suspicious claims, CLM-78234, $890K.
````

### `manual/skills/aibast_processing-metrics_06/SKILL.md`

````markdown
---
name: processing-metrics
description: "Use when a claims operations leader asks something like \"Yes, show me the metrics and where we can improve further\""
---
<!-- bic:source=blank -->
# Processing metrics

Use when a claims operations leader asks something like "Yes, show me the metrics and where we can improve further"

## Procedure

1. Use only the uploaded synthetic records and rules.
2. Lead with the specific evidence that answers the persona's question.
3. Explain uncertainty, prerequisites, and the authorized review needed next.
4. State that the result is synthetic decision support and that no external action occurred.

## Deterministic pilot evidence

- `5.2 days`
- `+467%`
- `Mobile photo AI assessment`

## Safety gate

Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a transaction. Stop at a reviewable brief or draft.
````

### `manual/skills/aibast_session-summary_07/SKILL.md`

````markdown
---
name: session-summary
description: "Use when a claims operations leader asks something like \"Yes, summarize everything we accomplished today\""
---
<!-- bic:source=blank -->
# Session summary

Use when a claims operations leader asks something like "Yes, summarize everything we accomplished today"

## Procedure

1. Use only the uploaded synthetic records and rules.
2. Lead with the specific evidence that answers the persona's question.
3. Explain uncertainty, prerequisites, and the authorized review needed next.
4. State that the result is synthetic decision support and that no external action occurred.

## Deterministic pilot evidence

- `2,847 total`
- `5,807 adjuster hours`
- `$290,350`

## Safety gate

Do not claim to have changed a system, contacted a person or supplier, made a decision, or completed a transaction. Stop at a reviewable brief or draft.
````

### `manual/skills/aibast_settlement-recommendation_04/SKILL.md`

````markdown
---
name: settlement-recommendation
description: Use for policy-term settlement estimate questions in the Claims Processing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Policy-term settlement estimate

Calculates a nonbinding coverage-limit and deductible estimate without approving, denying, reserving, settling, or paying.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Claims Manager

Prompt: Show the policy-term estimates and state clearly whether any claim was approved or paid.

Expected synthetic evidence: CLM-2025-7002, No approval.
````
## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Claims Adjuster

Prompt: What is missing from Jennifer Liu’s theft file before I can evaluate it?

Expected synthetic evidence: CLM-2025-7004, Receipts or appraisals.
````

### `manual/skills/aibast_claim-intake_01/SKILL.md`

````markdown
---
name: claim-intake
description: Use for claims intake triage questions in the Claims Processing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Claims intake triage

Summarizes fictional claims by loss, amount, status, and fraud-review score.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Claims Operations Leader

Prompt: Which incoming claim needs specialized handling first, and where should it be reviewed?

Expected synthetic evidence: CLM-2025-7003, Investigation.
````

### `manual/skills/aibast_fraud-flag_03/SKILL.md`

````markdown
---
name: fraud-flag
description: Use for siu indicator review questions in the Claims Processing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# SIU indicator review

Surfaces explainable fraud indicators without declaring fraud or changing coverage.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: SIU Investigator

Prompt: Which claim crosses the SIU review threshold, and does that prove fraud?

Expected synthetic evidence: CLM-2025-7003, SIU Referrals.
````

### `manual/skills/aibast_settlement-recommendation_04/SKILL.md`

````markdown
---
name: settlement-recommendation
description: Use for policy-term settlement estimate questions in the Claims Processing Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Policy-term settlement estimate

Calculates a nonbinding coverage-limit and deductible estimate without approving, denying, reserving, settling, or paying.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Claims Manager

Prompt: Show the policy-term estimates and state clearly whether any claim was approved or paid.

Expected synthetic evidence: CLM-2025-7002, No approval.
````

## Evidence-first response contract

1. Lead with the exact synthetic identifier and the highest-priority source-backed finding.
2. Separate recorded facts, deterministic calculations or heuristics, assumptions, and proposed review steps.
3. Cite the exact field, value, date, status, rule, threshold, or document used.
4. If evidence is absent, say so; never fill the gap from general knowledge.
5. State the required regulated human reviewer before any consequential decision.
6. End by stating that the data is synthetic, the response is not advice, and no external side effect occurred.
