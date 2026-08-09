# Cross-Selling Opportunities Agent solution package

## Purpose
Helps sales teams review product-ownership gaps, affinity assumptions, and prioritized expansion options without presenting modeled response or value as achieved conversion or revenue.

## Architecture
Single-file portable agent with four explicit operations, allow-listed customer routing, deterministic errors, synthetic-only data_source selection, and a shared evidence boundary.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/general_stacks/cross_selling_opportunities_stack/cross_selling_agent.py` |
| Deployment recipe | `solutions/cross-selling/deployment.json` |
| Canonical capture contract | `tests/demo_cases/cross-selling.json` |
| Package case mirror | `solutions/cross-selling/evals/demo-cases.json` |
| Strict isolation transcripts | `solutions/cross-selling/evals/transcripts.json` |
| Approved one-pager map | `solutions/cross-selling/evals/onepager-map.json` |
| Synthetic records | `solutions/cross-selling/manual/knowledge/aibast_cross-selling-synthetic-records.md` |
| Operating rules | `solutions/cross-selling/manual/knowledge/aibast_cross-selling-operating-rules.md` |
| Uploadable operation skills | `solutions/cross-selling/manual/skills/*/SKILL.md` |

## Operations
- `opportunity_scan` — Scan the synthetic CUST-001 ownership record for evidence-backed product gaps.
- `product_affinity` — Review the synthetic affinity rules and benchmark assumptions without treating them as observed conversion performance.
- `recommendation_engine` — Draft prioritized product recommendations for CUST-001 without sending outreach.
- `revenue_impact` — Compare the portfolio's synthetic cross-sell value scenarios without making revenue or margin claims.

## Package state
- Source routing is locked to bundled synthetic evidence.
- There is one locked persona demo case and one uploadable skill per operation.
- All 4 locked cases passed in strict Brainstem isolation with only the expected portable agent loaded.
- No Copilot Studio project, tutorial, screenshot, export bundle, publication, or external connector has been created.
- Human approval remains required before any pricing, proposal, outreach, CRM write, task, alert, forecast, or customer communication action.

## Evidence boundary
All exact names, dates, counts, values, scores, percentages, pricing, ARR, margins, conversion assumptions, and projections are synthetic. They demonstrate deterministic package behavior and do not represent measured customer outcomes, realized revenue, or commitments.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/cross-selling/FIELD-GUIDE.md` |
| Guided Easy/Hard quest | `solutions/cross-selling/quest.html` |
| Literal browser tutorial | `solutions/cross-selling/manual-tutorial.html` |
| Raw export manifest | `solutions/cross-selling/export-manifest.json` |
| Source bundle | `solutions/cross-selling/exports/cross-selling-source.zip` |
| Manual evidence | `solutions/cross-selling/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/cross-selling/screenshots/manual/browserfilm.json` |

**Scaffold status:** 60 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
