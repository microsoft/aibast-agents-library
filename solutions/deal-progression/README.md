# Deal Progression Agent solution package

## Purpose
Helps sales leaders review pipeline health, isolate stalled-deal evidence, and prepare consistent intervention options without turning analysis into an automated CRM action.

## Architecture
Single portable Python agent with an explicit operation enum, synthetic-only data_source route, deterministic dispatch, and a shared evidence boundary appended to every successful operation.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/b2b_sales_stacks/deal_progression_stack/deal_progression_agent.py` |
| Deployment recipe | `solutions/deal-progression/deployment.json` |
| Canonical capture contract | `tests/demo_cases/deal-progression.json` |
| Package case mirror | `solutions/deal-progression/evals/demo-cases.json` |
| Strict isolation transcripts | `solutions/deal-progression/evals/transcripts.json` |
| Approved one-pager map | `solutions/deal-progression/evals/onepager-map.json` |
| Synthetic records | `solutions/deal-progression/manual/knowledge/aibast_deal-progression-synthetic-records.md` |
| Operating rules | `solutions/deal-progression/manual/knowledge/aibast_deal-progression-operating-rules.md` |
| Uploadable operation skills | `solutions/deal-progression/manual/skills/*/SKILL.md` |

## Operations
- `pipeline_health` — Review the synthetic pipeline and show which opportunities need attention without changing the forecast.
- `stalled_deals` — Diagnose the synthetic stalled deals and show the evidence behind each blocker.
- `action_plans` — Draft reviewable action plans for the synthetic stalled deals; do not assign tasks.
- `acceleration` — Compare synthetic acceleration options and clearly separate scenario value from forecast commitments.
- `assign_tasks` — Prepare a draft task-mapping plan for manager review; do not create assignments or alerts.
- `executive_summary` — Summarize the synthetic pipeline analysis and draft next steps for a leadership review.

## Package state
- Source routing is locked to bundled synthetic evidence.
- There is one locked persona demo case and one uploadable skill per operation.
- All 6 locked cases passed in strict Brainstem isolation with only the expected portable agent loaded.
- No Copilot Studio project, tutorial, screenshot, export bundle, publication, or external connector has been created.
- Human approval remains required before any pricing, proposal, outreach, CRM write, task, alert, forecast, or customer communication action.

## Evidence boundary
All exact names, dates, counts, values, scores, percentages, pricing, ARR, margins, conversion assumptions, and projections are synthetic. They demonstrate deterministic package behavior and do not represent measured customer outcomes, realized revenue, or commitments.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/deal-progression/field-guide.html` |
| Evidence report | `solutions/deal-progression/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/deal-progression/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/deal-progression/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/deal-progression/quest.html` |
| Literal browser tutorial | `solutions/deal-progression/manual-tutorial.html` |
| Raw export manifest | `solutions/deal-progression/export-manifest.json` |
| Source bundle | `solutions/deal-progression/exports/deal-progression-source.zip` |
| Manual evidence | `solutions/deal-progression/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/deal-progression/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/deal-progression/exports/deal-progression-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/deal-progression/exports/deal-progression-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/deal-progression/exports/deal-progression-solution-export.json` |

**Scaffold status:** 109 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
