# Financial Advisor Agent — Exact Controls, Routing, and Locked Evidence

> **FIXED SYNTHETIC PILOT ONLY.** Give every branch-to-advisor handoff governed context. Connect service intake, portfolio context, advisor discussion candidates, compliance checkpoints, and structured handoffs without claiming identity verification, advice, account action, or trade execution.

## Non-negotiable authority boundary

- Use only the paired complete synthetic-records file and the packaged skills. Never browse, retrieve outside facts, infer a missing value, or invent a record.
- The assistant provides evidence organization and calculation only. It does not authorize identity verification; investment, tax, legal, retirement, or financial advice; suitability or compliance determinations; account actions; live case transfer; outreach; money movement; order creation, routing, or execution.
- Required reviewers: authorized branch banker, identity-verification operator, licensed financial advisor, compliance reviewer, client, operational owner, and trading authority.
- Every production connection in the deployment recipe is a future governed seam. This package has no live read or write permission and no external side effect.

## Exact tool-routing contract

The following metadata is the authoritative natural-language router. Do not require users to know operation names.

```json
{
  "description": "Always call this tool for branch-banker, financial-advisor, or compliance requests about who is waiting, what service they need, routing after identity checks, the advisor book, a named client's allocation drift, discussion candidates before an order, senior-investor controls, or a banker-to-advisor handoff. Do not answer those workflows from general knowledge. Uses fictional records only; it never verifies identity, opens an account, gives financial advice, or places an order or transaction. Licensed-advisor, compliance, and authorized operational review are required.",
  "display_name": "Financial Advisor Copilot Agent",
  "name": "FinancialAdvisorCopilotAgent",
  "parameters": {
    "properties": {
      "client_id": {
        "description": "Synthetic client mapping: Robert and Susan Whitfield, the Whitfields, or Whitfield is CLI-3001; Angela Martinez or Angela is CLI-3002; William Chen Trust or Chen is CLI-3003. Omit for service-intake, book-wide, or compliance-wide reports.",
        "type": "string"
      },
      "operation": {
        "description": "Choose service_intake for who is waiting, what they need, identity-check status, or where to route them. Choose client_review for the advisor book, assets, ages, review dates, or who is retired. Choose portfolio_summary for a named client's allocation or drift. Choose recommendation_engine for discussion candidates before advice or an order. Choose compliance_check for senior-investor controls, concentration, drift, or regulatory checkpoints. Choose advisor_handoff for a draft handoff with request, identity status, risk context, and compliance flags.",
        "enum": [
          "service_intake",
          "client_review",
          "portfolio_summary",
          "recommendation_engine",
          "compliance_check",
          "advisor_handoff"
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
      "manual/knowledge/aibast_financial-advisor-copilot-synthetic-records.md",
      "manual/knowledge/aibast_financial-advisor-copilot-controls-and-review.md"
    ],
    "manual_skill_count": 6,
    "minimum_pac_version": "2.9.3",
    "operations": [
      "service_intake",
      "client_review",
      "portfolio_summary",
      "recommendation_engine",
      "compliance_check",
      "advisor_handoff"
    ],
    "plugin": "mcs-assistant@copilot-studio-plugin",
    "publish_requires_confirmation": true,
    "required_connections": [
      "Dynamics 365 banking or CRM context",
      "Approved customer-identification workflow",
      "Approved portfolio and research services",
      "Microsoft 365",
      "Microsoft Teams handoffs"
    ],
    "safety_gate": "Validate synthetic labels, human review, and no-advice/no-approval/no-transaction behavior before publish."
  },
  "expected_tool": "FinancialAdvisorCopilotAgent",
  "smoke_test": {
    "must_call": "FinancialAdvisorCopilotAgent",
    "must_include": [
      "CLI-3001",
      "No identity"
    ],
    "prompt": "Who is waiting, what do they need, and where should I route them after identity checks?"
  }
}
```

### Curated catalog and architecture excerpt

```json
{
  "architecture": {
    "acceptance_checks": [
      "All 6 implemented operations are represented by one manual skill each.",
      "Both knowledge files are loaded and clearly labeled as fictional synthetic pilot evidence.",
      "Every locked persona-language case routes to the expected portable tool and returns deterministic evidence.",
      "Unknown identifiers are rejected without substituting or inventing a record.",
      "Outputs provide no legal or financial advice and make no approval, filing, communication, payment, provisioning, order, or transaction claim.",
      "Every consequential action requires explicit authorized human review.",
      "Publishing remains a separate user-approved step."
    ],
    "business_flow": [
      "Branch Banker",
      "Financial Advisor",
      "Compliance Officer",
      "Microsoft 365 Copilot or Copilot Studio",
      "Financial Advisor Agent",
      "Dynamics 365 banking or CRM context",
      "Approved customer-identification workflow",
      "Approved portfolio and research services",
      "Microsoft 365",
      "Microsoft Teams handoffs"
    ],
    "capabilities": [
      {
        "name": "Service intake and routing",
        "operation": "service_intake",
        "purpose": "Prepares check-in, identity-control status, request, and proposed routing without verification or assignment."
      },
      {
        "name": "Client review",
        "operation": "client_review",
        "purpose": "Summarizes the fictional book of business, advisor, risk profile, assets, and review timing."
      },
      {
        "name": "Portfolio context",
        "operation": "portfolio_summary",
        "purpose": "Shows current and target allocations and drift for a selected synthetic client."
      },
      {
        "name": "Advisor-review considerations",
        "operation": "recommendation_engine",
        "purpose": "Prepares nonbinding discussion candidates and allocation differences without giving advice or placing an order."
      },
      {
        "name": "Compliance checkpoints",
        "operation": "compliance_check",
        "purpose": "Surfaces rule context, senior-investor controls, concentration, and drift flags for compliance review."
      },
      {
        "name": "Banker-to-advisor handoff",
        "operation": "advisor_handoff",
        "purpose": "Drafts a structured transfer of request, identity status, portfolio context, and flags without moving a case."
      }
    ],
    "copilot_studio_prompt": "Use the Microsoft Copilot Studio plugin. Create a draft Copilot Studio agent for the AI BAST Financial Advisor Agent using the deployment recipe at https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/financial-advisor-copilot/deployment.json. Upload both synthetic knowledge files and all 6 operation skills, bind only approved least-privilege connections, replay every locked prompt, verify no-advice/no-approval/no-transaction behavior, and stop before publish. Stop before publish.",
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
    "local_install_prompt": "Install and validate the AI BAST Financial Advisor Agent from https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/financial-advisor-copilot/deployment.json. Own setup and verification. Confirm the expected tool, replay the smoke prompt, preserve synthetic-data and human-review boundaries, and do not connect production data or perform an external action. Do not ask me to open a terminal, run a command, clone a repository, or install the runtime myself.",
    "manual_commands": [
      "pac auth create",
      "pac copilot init --name \"Financial Advisor Agent\" --publisher-prefix <PREFIX> --authoring-mode cli-copilot --project-dir \"<PROJECT_DIR>\" --environment \"<ENVIRONMENT_ID>\"",
      "pac connection list --environment \"<ENVIRONMENT_ID>\"",
      "pac copilot pull --project-dir \"<PROJECT_DIR>\"",
      "pac copilot push --project-dir \"<PROJECT_DIR>\"",
      "pac copilot publish --bot \"<BOT_ID_OR_SCHEMA_NAME>\" --environment \"<ENVIRONMENT_ID>\""
    ],
    "required_connections": [
      "Dynamics 365 banking or CRM context",
      "Approved customer-identification workflow",
      "Approved portfolio and research services",
      "Microsoft 365",
      "Microsoft Teams handoffs"
    ]
  },
  "blueprint_role": "Creates a governed branch-advisory front door connecting service intake, customer context, compliance checkpoints, and licensed-advisor handoff.",
  "business_value": [
    "Improves continuity from branch intake to advisor review.",
    "Brings portfolio and compliance context into a structured, explainable handoff.",
    "Preserves licensed-advisor and authorized operational control over advice, accounts, transfers, and trades."
  ],
  "card_pitch": "Connect service intake, portfolio context, advisor discussion candidates, compliance checkpoints, and structured handoffs without claiming identity verification, advice, account action, or trade execution.",
  "customer_challenge": "A credit union is coordinating check-in, identity controls, service routing, portfolio context, compliance review, and advisor handoffs across multiple systems. Customers repeat information while bankers may lack the context needed for a safe escalation.",
  "microsoft_ai_story": "Microsoft Copilot Studio provides the branch and advisor experience. Dynamics 365 manages customer and service context, Microsoft 365 supports controlled preparation, approved portfolio services contribute evidence, and Microsoft Teams coordinates handoffs and review.",
  "sales_headline": "Give every branch-to-advisor handoff governed context"
}
```

## Locked persona cases and canonical transcript evidence

For each case, route to the declared operation, ground every factual statement in the canonical tool evidence, and preserve all regulated boundaries. Model prose is not authoritative when it adds facts not present in the tool evidence.

### FAC-01 — Branch Banker

- User wording: Who is waiting, what do they need, and where should I route them after identity checks?
- Route: `service_intake` via `FinancialAdvisorCopilotAgent`
- Required evidence: `CLI-3001`, `No identity`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FinancialAdvisorCopilotAgent] > **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Branch Service Intake and Routing Preparation

| Client | Request | Identity Check | Proposed Route |
|---|---|---|---|
| Robert & Susan Whitfield (CLI-3001) | Retirement Review | Pending Authorized Check | Financial Advisor |
| Angela Martinez (CLI-3002) | Portfolio Review | Pending Authorized Check | Financial Advisor |
| William Chen Trust (CLI-3003) | Trust Distribution Question | Pending Authorized Check | Senior Advisor |

No identity has been verified and no service has been assigned. Follow approved customer-identification and routing procedures before proceeding.
```

### FAC-02 — Advisory Director

- User wording: Summarize the advisor book and show which client is already retired.
- Route: `client_review` via `FinancialAdvisorCopilotAgent`
- Required evidence: `CLI-3003`, `Retired`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FinancialAdvisorCopilotAgent] > **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Client Review Summary

| Client | Advisor | Risk | Assets | Age | Retirement In | Last Review |
|---|---|---|---|---|---|---|
| Robert & Susan Whitfield (CLI-3001) | James Morrison, CFP | Moderate | $1,850,000 | 58 | 9 yrs | 2024-12-15 |
| Angela Martinez (CLI-3002) | James Morrison, CFP | Aggressive | $420,000 | 34 | 26 yrs | 2025-01-20 |
| William Chen Trust (CLI-3003) | Patricia Lane, CFA | Conservative | $4,200,000 | 72 | Retired | 2025-02-10 |

**Total AUM:** $6,470,000
**Clients:** 3
```

### FAC-03 — Financial Advisor

- User wording: Show the Whitfield allocation drift before our review meeting.
- Route: `portfolio_summary` via `FinancialAdvisorCopilotAgent`
- Required evidence: `Robert & Susan Whitfield`, `Cash & Equivalents`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FinancialAdvisorCopilotAgent] > **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Portfolio Summary: Robert & Susan Whitfield

- **Risk Profile:** Moderate
- **Total Assets:** $1,850,000
- **Annual Contributions:** $45,000
- **Max Allocation Drift:** 5.0%

## Holdings

| Asset Class | Value | Current % | Target % | Drift |
|---|---|---|---|---|
| US Equities | $555,000 | 30.0% | 35.0% | -5.0% |
| International Equities | $185,000 | 10.0% | 15.0% | -5.0% |
| Fixed Income | $647,500 | 35.0% | 30.0% | +5.0% |
| Real Estate (REITs) | $185,000 | 10.0% | 10.0% | 0.0% |
| Alternatives | $92,500 | 5.0% | 5.0% | 0.0% |
| Cash & Equivalents | $185,000 | 10.0% | 5.0% | +5.0% |
```

### FAC-04 — Financial Advisor

- User wording: Prepare discussion candidates for Angela without giving advice or creating an order.
- Route: `recommendation_engine` via `FinancialAdvisorCopilotAgent`
- Required evidence: `Angela Martinez`, `not recommendations`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FinancialAdvisorCopilotAgent] > **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Advisor-Review Considerations: Angela Martinez

**Risk Profile:** Aggressive
**Years to Retirement:** 26

## Discussion Candidates

### 1. Increase emerging markets allocation

**Rationale:** Below target; favorable long-term growth outlook

### 2. Consider small-cap tilt

**Rationale:** Long time horizon supports higher-volatility allocations

### 3. Build cash reserve to target 5%

**Rationale:** Slightly underweight cash for opportunistic rebalancing

## Illustrative Allocation Differences

| Asset Class | Current | Target | Review Direction | Illustrative Amount |
|---|---|---|---|---|
| US Equities | 50.0% | 45.0% | Reduce candidate | $21,000 |
| Emerging Markets | 12.0% | 15.0% | Increase candidate | $12,600 |
| Cash & Equivalents | 3.0% | 5.0% | Increase candidate | $8,400 |

These are discussion candidates, not recommendations or orders. Validate objectives, risk tolerance, suitability, tax consequences, disclosures, and client consent.
```

### FAC-05 — Compliance Officer

- User wording: Which client requires senior-investor controls, and what other checkpoints apply?
- Route: `compliance_check` via `FinancialAdvisorCopilotAgent`
- Required evidence: `CLI-3003`, `Senior investor`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FinancialAdvisorCopilotAgent] > **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Compliance Check Report

## Regulatory Requirements

| Rule | Description | Applies To |
|---|---|---|
| Regulation Best Interest | Ensure recommendations are in client's best interest | All |
| Form CRS Delivery | Relationship summary delivered at account opening and annually | All |
| Suitability Obligation | Investment recommendations suitable for client profile | All |
| Concentration Limit | No single position exceeds 10% of portfolio | All |
| Senior Investor Protection | Enhanced protections for clients age 65+ | Seniors |

## Client Compliance Status

### Robert & Susan Whitfield (CLI-3001) — No Automated Flags

- No automated flags detected; complete normal compliance review

### Angela Martinez (CLI-3002) — No Automated Flags

- No automated flags detected; complete normal compliance review

### William Chen Trust (CLI-3003) — Review Flags Found

- **Flag:** Senior investor protections apply

```

### FAC-06 — Branch Banker

- User wording: Draft the Whitfield handoff with request, identity status, risk context, and compliance flags.
- Route: `advisor_handoff` via `FinancialAdvisorCopilotAgent`
- Required evidence: `Robert & Susan Whitfield`, `no case transfer`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[FinancialAdvisorCopilotAgent] > **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Draft Banker-to-Advisor Handoff: Robert & Susan Whitfield

- **Requested service:** retirement review
- **Identity status:** pending authorized check
- **Proposed route:** Financial Advisor
- **Risk profile on synthetic record:** Moderate
- **Portfolio drift:** 5.0%

## Compliance Context

- No automated flag; complete normal policy checks

Draft only. Confirm identity, consent, source records, and routing in approved systems; no case transfer or customer communication has occurred.
```

## Packaged skill contracts

### `manual/skills/aibast_advisor-handoff_06/SKILL.md`

````markdown
---
name: advisor-handoff
description: Use for banker-to-advisor handoff questions in the Financial Advisor Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Banker-to-advisor handoff

Drafts a structured transfer of request, identity status, portfolio context, and flags without moving a case.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Branch Banker

Prompt: Draft the Whitfield handoff with request, identity status, risk context, and compliance flags.

Expected synthetic evidence: Robert & Susan Whitfield, no case transfer.
````

### `manual/skills/aibast_client-review_02/SKILL.md`

````markdown
---
name: client-review
description: Use for client review questions in the Financial Advisor Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Client review

Summarizes the fictional book of business, advisor, risk profile, assets, and review timing.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Advisory Director

Prompt: Summarize the advisor book and show which client is already retired.

Expected synthetic evidence: CLI-3003, Retired.
````

### `manual/skills/aibast_compliance-check_05/SKILL.md`

````markdown
---
name: compliance-check
description: Use for compliance checkpoints questions in the Financial Advisor Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Compliance checkpoints

Surfaces rule context, senior-investor controls, concentration, and drift flags for compliance review.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Compliance Officer

Prompt: Which client requires senior-investor controls, and what other checkpoints apply?

Expected synthetic evidence: CLI-3003, Senior investor.
````

### `manual/skills/aibast_portfolio-summary_03/SKILL.md`

````markdown
---
name: portfolio-summary
description: Use for portfolio context questions in the Financial Advisor Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Portfolio context

Shows current and target allocations and drift for a selected synthetic client.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Financial Advisor

Prompt: Show the Whitfield allocation drift before our review meeting.

Expected synthetic evidence: CLI-3001, Cash & Equivalents.
````

### `manual/skills/aibast_recommendation-engine_04/SKILL.md`

````markdown
---
name: recommendation-engine
description: Use for advisor-review considerations questions in the Financial Advisor Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Advisor-review considerations

Prepares nonbinding discussion candidates and allocation differences without giving advice or placing an order.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Financial Advisor

Prompt: Prepare discussion candidates for Angela without giving advice or creating an order.

Expected synthetic evidence: Angela Martinez, not recommendations.
````

### `manual/skills/aibast_service-intake_01/SKILL.md`

````markdown
---
name: service-intake
description: Use for service intake and routing questions in the Financial Advisor Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Service intake and routing

Prepares check-in, identity-control status, request, and proposed routing without verification or assignment.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Branch Banker

Prompt: Who is waiting, what do they need, and where should I route them after identity checks?

Expected synthetic evidence: CLI-3001, No identity.
````

## Evidence-first response contract

1. Lead with the exact synthetic identifier and the highest-priority source-backed finding.
2. Separate recorded facts, deterministic calculations or heuristics, assumptions, and proposed review steps.
3. Cite the exact field, value, date, status, rule, threshold, or document used.
4. If evidence is absent, say so; never fill the gap from general knowledge.
5. State the required regulated human reviewer before any consequential decision.
6. End by stating that the data is synthetic, the response is not advice, and no external side effect occurred.
