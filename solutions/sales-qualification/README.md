# Sales Qualification Agent solution package

## Purpose
Creates a consistent qualification review from enrichment through scoring, draft outreach, routing recommendations, and SLA planning while preserving manager and seller control.

## Architecture
Portable agent with six allow-listed operations, enum-constrained tier filters, synthetic-only source routing, deterministic dispatch, cached scoring, and explicit read-only output boundaries.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/b2b_sales_stacks/sales_qualification_stack/sales_qualification_agent.py` |
| Deployment recipe | `solutions/sales-qualification/deployment.json` |
| Canonical capture contract | `tests/demo_cases/sales-qualification.json` |
| Package case mirror | `solutions/sales-qualification/evals/demo-cases.json` |
| Approved one-pager map | `solutions/sales-qualification/evals/onepager-map.json` |
| Synthetic records | `solutions/sales-qualification/manual/knowledge/aibast_sales-qualification-synthetic-records.md` |
| Operating rules | `solutions/sales-qualification/manual/knowledge/aibast_sales-qualification-operating-rules.md` |
| Uploadable operation skills | `solutions/sales-qualification/manual/skills/*/SKILL.md` |

## Operations
- `score_leads` — Score and segment the bundled synthetic leads using the documented ICP model.
- `bant_analysis` — Review BANT evidence for the top synthetic leads and surface missing qualification data.
- `create_outreach` — Draft outreach ideas for synthetic hot leads; do not send or schedule any communication.
- `assign_leads` — Recommend lead routing for manager review without assigning CRM owners.
- `setup_tracking` — Draft an SLA tracking and escalation plan without activating alerts or automations.
- `qualification_report` — Summarize the synthetic qualified pipeline and recommended review actions without conversion claims.

## Package state
- Source routing is locked to bundled synthetic evidence.
- There is one locked persona demo case and one uploadable skill per operation.
- No Copilot Studio project, tutorial, screenshot, transcript capture, export bundle, publication, or external connector has been created.
- Human approval remains required before any pricing, proposal, outreach, CRM write, task, alert, forecast, or customer communication action.

## Evidence boundary
All exact names, dates, counts, values, scores, percentages, pricing, ARR, margins, conversion assumptions, and projections are synthetic. They demonstrate deterministic package behavior and do not represent measured customer outcomes, realized revenue, or commitments.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/sales-qualification/field-guide.html` |
| Evidence report | `solutions/sales-qualification/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/sales-qualification/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/sales-qualification/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/sales-qualification/quest.html` |
| Literal browser tutorial | `solutions/sales-qualification/manual-tutorial.html` |
| Raw export manifest | `solutions/sales-qualification/export-manifest.json` |
| Source bundle | `solutions/sales-qualification/exports/sales-qualification-source.zip` |
| Manual evidence | `solutions/sales-qualification/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/sales-qualification/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/sales-qualification/exports/sales-qualification-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/sales-qualification/exports/sales-qualification-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/sales-qualification/exports/sales-qualification-solution-export.json` |

**Scaffold status:** 108 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
