# Win/Loss Analysis Agent solution package

## Purpose
Turns structured closed-deal evidence into trend, root-cause, counter-strategy, and leadership-review artifacts while preventing scenario values from being represented as realized performance.

## Architecture
Single portable Python agent with six deterministic operations, an allow-listed quarter, synthetic-only source routing, and a common evidence boundary for all analysis and scenario outputs.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/b2b_sales_stacks/win_loss_analysis_stack/win_loss_analysis_agent.py` |
| Deployment recipe | `solutions/win-loss-analysis/deployment.json` |
| Canonical capture contract | `tests/demo_cases/win-loss-analysis.json` |
| Package case mirror | `solutions/win-loss-analysis/evals/demo-cases.json` |
| Strict isolation transcripts | `solutions/win-loss-analysis/evals/transcripts.json` |
| Approved one-pager map | `solutions/win-loss-analysis/evals/onepager-map.json` |
| Synthetic records | `solutions/win-loss-analysis/manual/knowledge/aibast_win-loss-analysis-synthetic-records.md` |
| Operating rules | `solutions/win-loss-analysis/manual/knowledge/aibast_win-loss-analysis-operating-rules.md` |
| Uploadable operation skills | `solutions/win-loss-analysis/manual/skills/*/SKILL.md` |

## Operations
- `win_loss_overview` — Compare the bundled synthetic Q3 and Q2 win/loss patterns.
- `root_cause_analysis` — Identify evidence-backed synthetic loss drivers and buyer-feedback themes.
- `counter_strategies` — Draft counter-strategy and talk-track options for enablement review.
- `revenue_impact` — Model synthetic intervention scenarios without presenting them as realized or committed revenue.
- `board_presentation` — Draft a board-level narrative that labels all exact values as synthetic scenarios.
- `action_summary` — Summarize findings and candidate next steps without activating programs or approvals.

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
| Customer field guide | `solutions/win-loss-analysis/FIELD-GUIDE.md` |
| Guided Easy/Hard quest | `solutions/win-loss-analysis/quest.html` |
| Literal browser tutorial | `solutions/win-loss-analysis/manual-tutorial.html` |
| Raw export manifest | `solutions/win-loss-analysis/export-manifest.json` |
| Source bundle | `solutions/win-loss-analysis/exports/win-loss-analysis-source.zip` |
| Manual evidence | `solutions/win-loss-analysis/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/win-loss-analysis/screenshots/manual/browserfilm.json` |

**Scaffold status:** 70 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
