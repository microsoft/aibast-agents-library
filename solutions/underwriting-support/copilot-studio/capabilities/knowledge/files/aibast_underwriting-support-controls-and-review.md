# Underwriting Support Agent — Exact Controls, Routing, and Locked Evidence

> **FIXED SYNTHETIC PILOT ONLY.** Make underwriting evidence consistent before a coverage decision. Give underwriters a single review surface for submission risk, rating factors, guideline checks, and exceptions while keeping quoting, binding, approval, and decline authority with humans.

## Non-negotiable authority boundary

- Use only the paired complete synthetic-records file and the packaged skills. Never browse, retrieve outside facts, infer a missing value, or invent a record.
- The assistant provides evidence organization and calculation only. It does not authorize legal, insurance, actuarial, pricing, or financial advice; quotes, binders, approvals, declines, policy issuance, coverage changes, or promised terms.
- Required reviewers: authorized underwriter, senior authority holder, actuarial or pricing reviewer, legal reviewer, and compliance reviewer.
- Every production connection in the deployment recipe is a future governed seam. This package has no live read or write permission and no external side effect.

## Exact tool-routing contract

The following metadata is the authoritative natural-language router. Do not require users to know operation names.

```json
{
  "description": "Always call this tool for underwriter, pricing-analyst, risk-analyst, or senior-underwriter requests about which submission needs the most experienced underwriter, rating factors and loss evidence, guideline exceptions or missing evidence, or preparing an exception file and checking whether a coverage decision occurred. Do not answer those workflows from general knowledge. For 'Which submission needs the most experienced underwriter, and why?', call risk_evaluation with no application_id; the synthetic queue returns UW-2025-103 as Substandard. For 'Which applications are outside a stated guideline or missing required evidence?', call guideline_check with no application_id; it returns UW-2025-103 and High-Risk Specialty. For an exception file and whether a coverage decision was made, call exception_review; it returns UW-2025-103 and the No approval boundary. Uses fictional records only and never binds, quotes, approves, declines, or changes coverage. All conclusions are nonbinding decision support for an authorized underwriter and require explicit human review.",
  "display_name": "Underwriting Support Agent",
  "name": "UnderwritingSupportAgent",
  "parameters": {
    "properties": {
      "application_id": {
        "description": "Synthetic application mapping: Riverside Manufacturing is UW-2025-101; Sarah Mitchell is UW-2025-102; Downtown Medical Associates, the orthopedic submission, highest-risk submission, or exception file is UW-2025-103; Harbor View Restaurant Group is UW-2025-104. Omit for queue-wide and guideline-wide reports.",
        "type": "string"
      },
      "operation": {
        "description": "Choose risk_evaluation for the submission queue, highest-risk case, which submission needs an experienced underwriter, risk scores, or tiers; omit application_id for that queue-wide request so UW-2025-103 and its Substandard tier are returned. Choose pricing_recommendation for rating factors, indicated premium, loss evidence, or Riverside without issuing a quote. Choose guideline_check for applications outside a stated guideline, required documents, inspections, or missing evidence; omit application_id so the queue includes UW-2025-103 and High-Risk Specialty. Choose exception_review for the exception file, senior review paths, or whether any coverage decision was made; the output states No approval.",
        "enum": [
          "risk_evaluation",
          "pricing_recommendation",
          "guideline_check",
          "exception_review"
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
      "manual/knowledge/aibast_underwriting-support-synthetic-records.md",
      "manual/knowledge/aibast_underwriting-support-controls-and-review.md"
    ],
    "manual_skill_count": 4,
    "minimum_pac_version": "2.9.3",
    "operations": [
      "risk_evaluation",
      "pricing_recommendation",
      "guideline_check",
      "exception_review"
    ],
    "plugin": "mcs-assistant@copilot-studio-plugin",
    "publish_requires_confirmation": true,
    "required_connections": [
      "Dynamics 365 insurance submission data",
      "Approved underwriting document repository",
      "Rating and policy-administration services",
      "Microsoft Teams referrals and approvals"
    ],
    "safety_gate": "Validate synthetic labels, human review, and no-advice/no-approval/no-transaction behavior before publish."
  },
  "expected_tool": "UnderwritingSupportAgent",
  "smoke_test": {
    "must_call": "UnderwritingSupportAgent",
    "must_include": [
      "UW-2025-103",
      "Substandard"
    ],
    "prompt": "Which submission needs the most experienced underwriter, and why?"
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
      "Underwriter",
      "Risk Analyst",
      "Microsoft 365 Copilot or Copilot Studio",
      "Underwriting Support Agent",
      "Dynamics 365 insurance submission data",
      "Approved underwriting document repository",
      "Rating and policy-administration services",
      "Microsoft Teams referrals and approvals"
    ],
    "capabilities": [
      {
        "name": "Submission risk evaluation",
        "operation": "risk_evaluation",
        "purpose": "Summarizes submission risk scores, tiers, and current review status."
      },
      {
        "name": "Illustrative pricing-factor review",
        "operation": "pricing_recommendation",
        "purpose": "Displays synthetic rating inputs and loss history without quoting or binding coverage."
      },
      {
        "name": "Guideline and document alignment",
        "operation": "guideline_check",
        "purpose": "Checks coverage limits, required documents, inspections, and stated risk rules."
      },
      {
        "name": "Exception review queue",
        "operation": "exception_review",
        "purpose": "Prepares exceptions and human review paths without approving or declining risk."
      }
    ],
    "copilot_studio_prompt": "Use the Microsoft Copilot Studio plugin. Create a draft Copilot Studio agent for the AI BAST Underwriting Support Agent using the deployment recipe at https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/underwriting-support/deployment.json. Upload both synthetic knowledge files and all 4 operation skills, bind only approved least-privilege connections, replay every locked prompt, verify no-advice/no-approval/no-transaction behavior, and stop before publish. Stop before publish.",
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
    "local_install_prompt": "Install and validate the AI BAST Underwriting Support Agent from https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/underwriting-support/deployment.json. Own setup and verification. Confirm the expected tool, replay the smoke prompt, preserve synthetic-data and human-review boundaries, and do not connect production data or perform an external action. Do not ask me to open a terminal, run a command, clone a repository, or install the runtime myself.",
    "manual_commands": [
      "pac auth create",
      "pac copilot init --name \"Underwriting Support Agent\" --publisher-prefix <PREFIX> --authoring-mode cli-copilot --project-dir \"<PROJECT_DIR>\" --environment \"<ENVIRONMENT_ID>\"",
      "pac connection list --environment \"<ENVIRONMENT_ID>\"",
      "pac copilot pull --project-dir \"<PROJECT_DIR>\"",
      "pac copilot push --project-dir \"<PROJECT_DIR>\"",
      "pac copilot publish --bot \"<BOT_ID_OR_SCHEMA_NAME>\" --environment \"<ENVIRONMENT_ID>\""
    ],
    "required_connections": [
      "Dynamics 365 insurance submission data",
      "Approved underwriting document repository",
      "Rating and policy-administration services",
      "Microsoft Teams referrals and approvals"
    ]
  },
  "blueprint_role": "Creates an explainable underwriting preparation layer connecting submission evidence, rating rules, authority limits, and human decision controls.",
  "business_value": [
    "Improves consistency in submission and guideline review.",
    "Accelerates preparation of explainable pricing-factor and exception evidence.",
    "Keeps all quote, bind, approve, and decline decisions with authorized underwriters."
  ],
  "card_pitch": "Give underwriters a single review surface for submission risk, rating factors, guideline checks, and exceptions while keeping quoting, binding, approval, and decline authority with humans.",
  "customer_challenge": "A commercial carrier is reviewing applications, loss history, rating factors, coverage limits, and authority rules manually. Review quality varies and senior underwriters spend time rebuilding evidence instead of judging complex risk.",
  "microsoft_ai_story": "Microsoft Copilot Studio provides the underwriter experience. Dynamics 365 holds submissions, approved document repositories supply evidence, rating services contribute controlled factors, and Microsoft Teams supports referral and authority workflows.",
  "sales_headline": "Make underwriting evidence consistent before a coverage decision"
}
```

## Locked persona cases and canonical transcript evidence

For each case, route to the declared operation, ground every factual statement in the canonical tool evidence, and preserve all regulated boundaries. Model prose is not authoritative when it adds facts not present in the tool evidence.

### UWS-01 — Underwriter

- User wording: Which submission needs the most experienced underwriter, and why?
- Route: `risk_evaluation` via `UnderwritingSupportAgent`
- Required evidence: `UW-2025-103`, `Substandard`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[UnderwritingSupportAgent] > **SYNTHETIC DEMO DATA — UNDERWRITER REVIEW REQUIRED.** Fictional submissions and rating assumptions only. This is not legal, insurance, or financial advice and does not bind, quote, approve, decline, or modify coverage.

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

- User wording: Walk me through the rating factors and loss evidence for Riverside without issuing a quote.
- Route: `pricing_recommendation` via `UnderwritingSupportAgent`
- Required evidence: `UW-2025-101`, `Indicated Premium`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
Agent 'UnderwritingSupport Agent' not found.
[UnderwritingSupportAgent] > **SYNTHETIC DEMO DATA — UNDERWRITER REVIEW REQUIRED.** Fictional submissions and rating assumptions only. This is not legal, insurance, or financial advice and does not bind, quote, approve, decline, or modify coverage.

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

- User wording: Which applications are outside a stated guideline or missing required evidence?
- Route: `guideline_check` via `UnderwritingSupportAgent`
- Required evidence: `UW-2025-103`, `High-Risk Specialty`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
Agent 'UnderwritingSupport' not found.
[UnderwritingSupportAgent] > **SYNTHETIC DEMO DATA — UNDERWRITER REVIEW REQUIRED.** Fictional submissions and rating assumptions only. This is not legal, insurance, or financial advice and does not bind, quote, approve, decline, or modify coverage.

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

- User wording: Prepare the exception file I need to review and state whether any coverage decision was made.
- Route: `exception_review` via `UnderwritingSupportAgent`
- Required evidence: `UW-2025-103`, `No approval`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
Agent 'UnderwritingSupport Agent' not found.
[UnderwritingSupportAgent] > **SYNTHETIC DEMO DATA — UNDERWRITER REVIEW REQUIRED.** Fictional submissions and rating assumptions only. This is not legal, insurance, or financial advice and does not bind, quote, approve, decline, or modify coverage.

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

## Packaged skill contracts

### `manual/skills/aibast_exception-review_04/SKILL.md`

````markdown
---
name: exception-review
description: Use for exception review queue questions in the Underwriting Support Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Exception review queue

Prepares exceptions and human review paths without approving or declining risk.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Senior Underwriter

Prompt: Prepare the exception file I need to review and state whether any coverage decision was made.

Expected synthetic evidence: UW-2025-103, No approval.
````

### `manual/skills/aibast_guideline-check_03/SKILL.md`

````markdown
---
name: guideline-check
description: Use for guideline and document alignment questions in the Underwriting Support Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Guideline and document alignment

Checks coverage limits, required documents, inspections, and stated risk rules.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Risk Analyst

Prompt: Which applications are outside a stated guideline or missing required evidence?

Expected synthetic evidence: UW-2025-103, High-Risk Specialty.
````

### `manual/skills/aibast_pricing-recommendation_02/SKILL.md`

````markdown
---
name: pricing-recommendation
description: Use for illustrative pricing-factor review questions in the Underwriting Support Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Illustrative pricing-factor review

Displays synthetic rating inputs and loss history without quoting or binding coverage.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.
7. Lead the answer with `UW-2025-101` and label the pricing result
   `Indicated Premium`.

## Locked example

Persona: Pricing Analyst

Prompt: Walk me through the rating factors and loss evidence for Riverside without issuing a quote.

Expected synthetic evidence: UW-2025-101, Indicated Premium.
````

### `manual/skills/aibast_risk-evaluation_01/SKILL.md`

````markdown
---
name: risk-evaluation
description: Use for submission risk evaluation questions in the Underwriting Support Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Submission risk evaluation

Summarizes submission risk scores, tiers, and current review status.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.
7. Lead the answer with the exact evidence line `UW-2025-103 — Substandard`.

## Locked example

Persona: Underwriter

Prompt: Which submission needs the most experienced underwriter, and why?

Expected synthetic evidence: UW-2025-103, Substandard.
````

## Evidence-first response contract

1. Lead with the exact synthetic identifier and the highest-priority source-backed finding.
2. Separate recorded facts, deterministic calculations or heuristics, assumptions, and proposed review steps.
3. Cite the exact field, value, date, status, rule, threshold, or document used.
4. If evidence is absent, say so; never fill the gap from general knowledge.
5. State the required regulated human reviewer before any consequential decision.
6. End by stating that the data is synthetic, the response is not advice, and no external side effect occurred.
