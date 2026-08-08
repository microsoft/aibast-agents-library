# Wealth Insights Generator Agent — Exact Controls, Routing, and Locked Evidence

> **FIXED SYNTHETIC PILOT ONLY.** Turn fragmented wealth signals into an advisor-ready conversation. Connect managed and held-away assets, planning gaps, life events, performance context, and meeting preparation in one governed workspace that never presents synthetic data as current advice.

## Non-negotiable authority boundary

- Use only the paired complete synthetic-records file and the packaged skills. Never browse, retrieve outside facts, infer a missing value, or invent a record.
- The assistant provides evidence organization and calculation only. It does not authorize current-market claims; investment, tax, legal, estate, retirement, or financial advice; suitability findings; performance promises; outreach, CRM changes, live aggregation, opportunity creation, orders, or transactions.
- Required reviewers: licensed wealth advisor, client, relationship manager, compliance reviewer, qualified tax or legal specialist, estate-planning specialist, and authorized trading owner.
- Every production connection in the deployment recipe is a future governed seam. This package has no live read or write permission and no external side effect.

## Exact tool-routing contract

The following metadata is the authoritative natural-language router. Do not require users to know operation names.

```json
{
  "description": "Always call this tool for wealth-advisor, relationship-manager, advisory-director, or portfolio-strategist requests about the fixed market snapshot, which household has the largest held-away opportunity, high-priority planning signals, a client below benchmark, or a meeting brief for the Kensington household. Do not answer those workflows from general knowledge. Uses fictional records and fixed synthetic snapshots only. Never presents current market data or personal financial, tax, legal, or estate-planning advice, sends outreach, or performs a transaction. Licensed-advisor and customer review are required.",
  "display_name": "Wealth Insights Generator Agent",
  "name": "WealthInsightsGeneratorAgent",
  "parameters": {
    "properties": {
      "client_id": {
        "description": "Synthetic client mapping: Harrison Family Trust is WM-001; Dr. Anita Rao is WM-002; George and Martha Kensington, the Kensington household, or the largest held-away opportunity is WM-003; Tidewater Ventures is WM-004. Omit for market, opportunity, attribution, and book-wide reports.",
        "type": "string"
      },
      "operation": {
        "description": "Choose market_brief for the fixed market snapshot, morning huddle, index context, or whether data is current. Choose client_insights for unified managed and held-away wealth, the household with the largest held-away opportunity, life events, or next reviews. Choose opportunity_alerts for high-priority planning signals or advisor-review opportunities. Choose performance_attribution for a client below benchmark, alpha, strategy benchmarks, or an attribution label. Choose meeting_brief for the Kensington household or draft preparation material without advice or outreach.",
        "enum": [
          "market_brief",
          "client_insights",
          "opportunity_alerts",
          "performance_attribution",
          "meeting_brief"
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
      "manual/knowledge/aibast_wealth-insights-generator-synthetic-records.md",
      "manual/knowledge/aibast_wealth-insights-generator-controls-and-review.md"
    ],
    "manual_skill_count": 5,
    "minimum_pac_version": "2.9.3",
    "operations": [
      "market_brief",
      "client_insights",
      "opportunity_alerts",
      "performance_attribution",
      "meeting_brief"
    ],
    "plugin": "mcs-assistant@copilot-studio-plugin",
    "publish_requires_confirmation": true,
    "required_connections": [
      "Dynamics 365 wealth-management CRM",
      "Approved portfolio aggregation and held-away asset data",
      "Financial planning and performance systems",
      "Outlook",
      "Microsoft Teams specialist review"
    ],
    "safety_gate": "Validate synthetic labels, human review, and no-advice/no-approval/no-transaction behavior before publish."
  },
  "expected_tool": "WealthInsightsGeneratorAgent",
  "smoke_test": {
    "must_call": "WealthInsightsGeneratorAgent",
    "must_include": [
      "NASDAQ Composite",
      "Fixed Synthetic"
    ],
    "prompt": "Give me the fixed market snapshot for the morning huddle and label whether it is current data."
  }
}
```

### Curated catalog and architecture excerpt

```json
{
  "architecture": {
    "acceptance_checks": [
      "All 5 implemented operations are represented by one manual skill each.",
      "Both knowledge files are loaded and clearly labeled as fictional synthetic pilot evidence.",
      "Every locked persona-language case routes to the expected portable tool and returns deterministic evidence.",
      "Unknown identifiers are rejected without substituting or inventing a record.",
      "Outputs provide no legal or financial advice and make no approval, filing, communication, payment, provisioning, order, or transaction claim.",
      "Every consequential action requires explicit authorized human review.",
      "Publishing remains a separate user-approved step."
    ],
    "business_flow": [
      "Wealth Advisor",
      "Relationship Manager",
      "Advisory Director",
      "Microsoft 365 Copilot or Copilot Studio",
      "Wealth Insights Generator Agent",
      "Dynamics 365 wealth-management CRM",
      "Approved portfolio aggregation and held-away asset data",
      "Financial planning and performance systems",
      "Outlook",
      "Microsoft Teams specialist review"
    ],
    "capabilities": [
      {
        "name": "Fixed market snapshot",
        "operation": "market_brief",
        "purpose": "Presents a clearly labeled synthetic market snapshot rather than current market data."
      },
      {
        "name": "Unified wealth insights",
        "operation": "client_insights",
        "purpose": "Combines managed and held-away synthetic assets, performance, reviews, and life events."
      },
      {
        "name": "Planning-gap signals",
        "operation": "opportunity_alerts",
        "purpose": "Prioritizes reviewable relationship and planning signals without giving advice or contacting a client."
      },
      {
        "name": "Performance context",
        "operation": "performance_attribution",
        "purpose": "Compares synthetic portfolio performance with fixed strategy benchmarks."
      },
      {
        "name": "Advisor meeting preparation",
        "operation": "meeting_brief",
        "purpose": "Drafts review material and discussion prompts for licensed-advisor validation."
      }
    ],
    "copilot_studio_prompt": "Use the Microsoft Copilot Studio plugin. Create a draft Copilot Studio agent for the AI BAST Wealth Insights Generator Agent using the deployment recipe at https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/wealth-insights-generator/deployment.json. Upload both synthetic knowledge files and all 5 operation skills, bind only approved least-privilege connections, replay every locked prompt, verify no-advice/no-approval/no-transaction behavior, and stop before publish. Stop before publish.",
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
    "local_install_prompt": "Install and validate the AI BAST Wealth Insights Generator Agent from https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/solutions/wealth-insights-generator/deployment.json. Own setup and verification. Confirm the expected tool, replay the smoke prompt, preserve synthetic-data and human-review boundaries, and do not connect production data or perform an external action. Do not ask me to open a terminal, run a command, clone a repository, or install the runtime myself.",
    "manual_commands": [
      "pac auth create",
      "pac copilot init --name \"Wealth Insights Generator Agent\" --publisher-prefix <PREFIX> --authoring-mode cli-copilot --project-dir \"<PROJECT_DIR>\" --environment \"<ENVIRONMENT_ID>\"",
      "pac connection list --environment \"<ENVIRONMENT_ID>\"",
      "pac copilot pull --project-dir \"<PROJECT_DIR>\"",
      "pac copilot push --project-dir \"<PROJECT_DIR>\"",
      "pac copilot publish --bot \"<BOT_ID_OR_SCHEMA_NAME>\" --environment \"<ENVIRONMENT_ID>\""
    ],
    "required_connections": [
      "Dynamics 365 wealth-management CRM",
      "Approved portfolio aggregation and held-away asset data",
      "Financial planning and performance systems",
      "Outlook",
      "Microsoft Teams specialist review"
    ]
  },
  "blueprint_role": "Creates a governed wealth-intelligence layer connecting relationship context, aggregated assets, planning evidence, meeting preparation, and licensed-advisor review.",
  "business_value": [
    "Improves visibility into total-wealth and planning-gap signals.",
    "Accelerates advisor preparation with explainable client and performance context.",
    "Keeps advice, outreach, suitability judgments, and transactions with licensed professionals."
  ],
  "card_pitch": "Connect managed and held-away assets, planning gaps, life events, performance context, and meeting preparation in one governed workspace that never presents synthetic data as current advice.",
  "customer_challenge": "A wealth firm has portfolio, relationship, held-away asset, planning, and life-event context spread across systems. Advisors spend time researching while incomplete data can lead to generic or premature guidance.",
  "microsoft_ai_story": "Microsoft Copilot Studio gives advisors a governed conversational layer. Dynamics 365 supplies relationship context, approved portfolio aggregation contributes managed and held-away assets, Outlook supports controlled preparation, and Microsoft Teams enables specialist review.",
  "sales_headline": "Turn fragmented wealth signals into an advisor-ready conversation"
}
```

## Locked persona cases and canonical transcript evidence

For each case, route to the declared operation, ground every factual statement in the canonical tool evidence, and preserve all regulated boundaries. Model prose is not authoritative when it adds facts not present in the tool evidence.

### WIG-01 — Advisory Director

- User wording: Give me the fixed market snapshot for the morning huddle and label whether it is current data.
- Route: `market_brief` via `WealthInsightsGeneratorAgent`
- Required evidence: `NASDAQ Composite`, `Fixed Synthetic`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[WealthInsightsGeneratorAgent] > **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Fixed Synthetic Market Snapshot

## Index Performance

| Index | Current | YTD Return | P/E | Yield |
|---|---|---|---|---|
| S&P 500 | 5,285.42 | +4.8% | 22.1 | 1.35% |
| NASDAQ Composite | 16,742.15 | +6.2% | 28.5 | 0.72% |
| Dow Jones Industrial | 39,180.50 | +3.1% | 19.8 | 1.82% |
| MSCI EAFE | 2,385.70 | +5.5% | 15.2 | 2.95% |
| Bloomberg US Agg Bond | 98.45 | +1.2% | N/A | 4.45% |
| 10-Year Treasury | 4.28 | +0.0% | N/A | 4.28% |
| Gold (per oz) | 2,185.30 | +8.1% | N/A | N/A |

## Key Observations

- Equity markets continue positive YTD momentum; NASDAQ leading at +6.2%
- International developed markets (EAFE) outperforming on weaker dollar
- Fixed income subdued with 10-Year Treasury at 4.28%
- Gold rally continues (+8.1% YTD) on geopolitical uncertainty

**Total Practice AUM:** $29,800,000
```

### WIG-02 — Wealth Advisor

- User wording: Which household has the largest held-away opportunity and what life event needs validation?
- Route: `client_insights` via `WealthInsightsGeneratorAgent`
- Required evidence: `WM-003`, `Held Away`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[WealthInsightsGeneratorAgent] > **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Client Insights Report

**Total AUM:** $29,800,000
**Average Alpha:** 0.7%

| Client | Managed AUM | Held Away | Strategy | YTD | Alpha | Health | Next Review |
|---|---|---|---|---|---|---|---|
| Harrison Family Trust (WM-001) | $8,500,000 | $620,000 | Balanced Growth | +5.2% | +1.1% | Strong | 2025-04-15 |
| Dr. Anita Rao (WM-002) | $3,200,000 | $1,100,000 | Aggressive Growth | +7.8% | +1.6% | Strong | 2025-06-01 |
| George & Martha Kensington (WM-003) | $12,400,000 | $1,850,000 | Capital Preservation | +2.1% | +0.3% | Satisfactory | 2025-04-01 |
| Tidewater Ventures LLC (WM-004) | $5,700,000 | $900,000 | Alternative Focused | +3.9% | -0.2% | Attention Needed | 2025-05-15 |

## Life Events & Planning Needs

### Harrison Family Trust (WM-001)

- Daughter starting college Fall 2025

### Dr. Anita Rao (WM-002)

- Planning practice sale in 2-3 years

### George & Martha Kensington (WM-003)

- Estate plan revision needed
- RMD optimization

### Tidewater Ventures LLC (WM-004)

- Considering real estate exit strategy

```

### WIG-03 — Relationship Manager

- User wording: Which clients have high-priority planning signals for advisor review?
- Route: `opportunity_alerts` via `WealthInsightsGeneratorAgent`
- Required evidence: `Harrison Family Trust`, `Dr. Anita Rao`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[WealthInsightsGeneratorAgent] > **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Opportunity Alerts

## High Priority

### Harrison Family Trust — Education Funding

- **Description:** 529 plan contribution deadline approaching; daughter's college enrollment Fall 2025
- **Recommended Action:** Schedule meeting to review education funding plan

### Dr. Anita Rao — Liquidity Event

- **Description:** Practice sale in 2-3 years; begin pre-sale tax and asset protection planning
- **Recommended Action:** Engage tax advisor for sale structuring

## Medium Priority

### George & Martha Kensington — Estate Planning

- **Description:** Estate plan last updated 2019; tax law changes require revision
- **Recommended Action:** Coordinate with estate attorney for plan update

### George & Martha Kensington — Rmd Optimization

- **Description:** Client age 74; review Qualified Charitable Distribution strategy
- **Recommended Action:** Model QCD scenarios vs standard RMD

### Tidewater Ventures LLC — Reallocation

- **Description:** Portfolio underperforming benchmark; alternative allocation review needed
- **Recommended Action:** Prepare alternative manager review presentation

**Total Alerts:** 5
```

### WIG-04 — Portfolio Strategist

- User wording: Which synthetic client is below its benchmark, and what does the attribution label say?
- Route: `performance_attribution` via `WealthInsightsGeneratorAgent`
- Required evidence: `Tidewater Ventures`, `Underperformance`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[WealthInsightsGeneratorAgent] > **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Performance Attribution

## Strategy Benchmarks

| Strategy | Benchmark | 1-Year | 3-Year | 5-Year |
|---|---|---|---|---|
| Balanced Growth | 60/40 Balanced | 12.5% | 8.2% | 9.1% |
| Aggressive Growth | 80/20 Growth | 18.2% | 10.5% | 11.8% |
| Capital Preservation | 20/80 Conservative | 5.8% | 3.9% | 4.5% |
| Alternative Focused | HFRI Fund Weighted | 8.4% | 6.1% | 7.2% |

## Client Performance vs Benchmark

| Client | Strategy | YTD | Benchmark | Alpha | Attribution |
|---|---|---|---|---|---|
| Harrison Family Trust | Balanced Growth | +5.2% | +4.1% | +1.1% | Selection + Allocation |
| Dr. Anita Rao | Aggressive Growth | +7.8% | +6.2% | +1.6% | Selection + Allocation |
| George & Martha Kensington | Capital Preservation | +2.1% | +1.8% | +0.3% | Allocation |
| Tidewater Ventures LLC | Alternative Focused | +3.9% | +4.1% | -0.2% | Underperformance |

**AUM-Weighted Alpha:** +0.57%
```

### WIG-05 — Wealth Advisor

- User wording: Prepare my review brief for the Kensington household without turning it into advice or outreach.
- Route: `meeting_brief` via `WealthInsightsGeneratorAgent`
- Required evidence: `George & Martha Kensington`, `preparation material`
- Prohibited stall or unsafe phrases: `I do not have access`, `I can approve`, `I executed`, `I submitted`

#### Canonical strict-isolation tool evidence

```text
[WealthInsightsGeneratorAgent] > **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or financial advice; no outreach or transaction has occurred.

# Draft Advisor Meeting Brief: George & Martha Kensington

- **Managed AUM:** $12,400,000
- **Held-away assets in synthetic snapshot:** $1,850,000
- **Risk profile:** Conservative
- **Next review:** 2025-04-01

## Validate With the Client

- Estate plan revision needed
- RMD optimization

## Discussion Prompts

- Estate plan last updated 2019; tax law changes require revision
- Client age 74; review Qualified Charitable Distribution strategy

This is preparation material, not a recommendation or customer communication. The advisor must validate facts, suitability, consent, and approved disclosures.
```

## Packaged skill contracts

### `manual/skills/aibast_client-insights_02/SKILL.md`

````markdown
---
name: client-insights
description: Use for unified wealth insights questions in the Wealth Insights Generator Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Unified wealth insights

Combines managed and held-away synthetic assets, performance, reviews, and life events.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Wealth Advisor

Prompt: Which household has the largest held-away opportunity and what life event needs validation?

Expected synthetic evidence: WM-003, Held Away.
````

### `manual/skills/aibast_market-brief_01/SKILL.md`

````markdown
---
name: market-brief
description: Use for fixed market snapshot questions in the Wealth Insights Generator Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Fixed market snapshot

Presents a clearly labeled synthetic market snapshot rather than current market data.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Advisory Director

Prompt: Give me the fixed market snapshot for the morning huddle and label whether it is current data.

Expected synthetic evidence: NASDAQ Composite, Fixed Synthetic.
````

### `manual/skills/aibast_meeting-brief_05/SKILL.md`

````markdown
---
name: meeting-brief
description: Use for advisor meeting preparation questions in the Wealth Insights Generator Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Advisor meeting preparation

Drafts review material and discussion prompts for licensed-advisor validation.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Wealth Advisor

Prompt: Prepare my review brief for the Kensington household without turning it into advice or outreach.

Expected synthetic evidence: George & Martha Kensington, preparation material.
````

### `manual/skills/aibast_opportunity-alerts_03/SKILL.md`

````markdown
---
name: opportunity-alerts
description: Use for planning-gap signals questions in the Wealth Insights Generator Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Planning-gap signals

Prioritizes reviewable relationship and planning signals without giving advice or contacting a client.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Relationship Manager

Prompt: Which clients have high-priority planning signals for advisor review?

Expected synthetic evidence: Harrison Family Trust, Dr. Anita Rao.
````

### `manual/skills/aibast_performance-attribution_04/SKILL.md`

````markdown
---
name: performance-attribution
description: Use for performance context questions in the Wealth Insights Generator Agent synthetic pilot.
---
<!-- bic:source=blank -->
# Performance context

Compares synthetic portfolio performance with fixed strategy benchmarks.

## Procedure

1. Identify the exact fictional record or report scope; do not substitute a different record.
2. Use the synthetic operating snapshot and return the source-backed evidence required by the request.
3. Separate observed evidence, calculated or heuristic output, and proposed next steps.
4. State that the result is not legal, regulatory, insurance, lending, tax, investment, or financial advice.
5. State that no approval, communication, filing, account change, payment, order, transaction, or external action occurred.
6. Name the authorized human review required before action.

## Locked example

Persona: Portfolio Strategist

Prompt: Which synthetic client is below its benchmark, and what does the attribution label say?

Expected synthetic evidence: Tidewater Ventures, Underperformance.
````

## Evidence-first response contract

1. Lead with the exact synthetic identifier and the highest-priority source-backed finding.
2. Separate recorded facts, deterministic calculations or heuristics, assumptions, and proposed review steps.
3. Cite the exact field, value, date, status, rule, threshold, or document used.
4. If evidence is absent, say so; never fill the gap from general knowledge.
5. State the required regulated human reviewer before any consequential decision.
6. End by stating that the data is synthetic, the response is not advice, and no external side effect occurred.
