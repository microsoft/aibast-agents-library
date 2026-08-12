# License Renewal and Expansion Agent solution package

## Purpose
Provides a shared renewal-risk and expansion-planning view for account, customer-success, and sales leaders while keeping pricing, negotiation, and customer engagement human governed.

## Architecture
Portable Python agent with four operations, deterministic license filtering, synthetic-only source routing, explicit unknown-ID errors, and a standard no-side-effect evidence boundary.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/software_dp_stacks/license_renewal_expansion_stack/license_renewal_expansion_agent.py` |
| Deployment recipe | `solutions/license-renewal-expansion/deployment.json` |
| Canonical capture contract | `tests/demo_cases/license-renewal-expansion.json` |
| Package case mirror | `solutions/license-renewal-expansion/evals/demo-cases.json` |
| Strict isolation transcripts | `solutions/license-renewal-expansion/evals/transcripts.json` |
| Approved one-pager map | `solutions/license-renewal-expansion/evals/onepager-map.json` |
| Synthetic records | `solutions/license-renewal-expansion/manual/knowledge/aibast_license-renewal-expansion-synthetic-records.md` |
| Operating rules | `solutions/license-renewal-expansion/manual/knowledge/aibast_license-renewal-expansion-operating-rules.md` |
| Uploadable operation skills | `solutions/license-renewal-expansion/manual/skills/*/SKILL.md` |

## Operations
- `renewal_pipeline` — Review the synthetic renewal pipeline and risk bands without changing CRM or forecast records.
- `expansion_opportunities` — Identify synthetic demand signals and draft expansion options for authorized review.
- `churn_risk` — Assess synthetic churn signals and evidence without initiating customer outreach.
- `revenue_impact` — Compare synthetic renewal, expansion, and churn scenarios without making revenue commitments.

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
| Customer field guide | `solutions/license-renewal-expansion/field-guide.html` |
| Evidence report | `solutions/license-renewal-expansion/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/license-renewal-expansion/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/license-renewal-expansion/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/license-renewal-expansion/quest.html` |
| Literal browser tutorial | `solutions/license-renewal-expansion/manual-tutorial.html` |
| Raw export manifest | `solutions/license-renewal-expansion/export-manifest.json` |
| Source bundle | `solutions/license-renewal-expansion/exports/license-renewal-expansion-source.zip` |
| Manual evidence | `solutions/license-renewal-expansion/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/license-renewal-expansion/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/license-renewal-expansion/exports/license-renewal-expansion-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/license-renewal-expansion/exports/license-renewal-expansion-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/license-renewal-expansion/exports/license-renewal-expansion-solution-export.json` |

**Scaffold status:** 95 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
