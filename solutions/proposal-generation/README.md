# Proposal Generation Agent solution package

## Purpose
Gives bid teams a repeatable path from requirement extraction through a proposal outline while keeping pricing, references, approvals, and customer delivery under human control.

## Architecture
Portable Python agent with six explicit operations, a synthetic-only source route, allow-listed RFP names, deterministic unknown-input errors, and an output-level evidence boundary.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/b2b_sales_stacks/proposal_generation_stack/proposal_generation_agent.py` |
| Deployment recipe | `solutions/proposal-generation/deployment.json` |
| Canonical capture contract | `tests/demo_cases/proposal-generation.json` |
| Package case mirror | `solutions/proposal-generation/evals/demo-cases.json` |
| Strict isolation transcripts | `solutions/proposal-generation/evals/transcripts.json` |
| Approved one-pager map | `solutions/proposal-generation/evals/onepager-map.json` |
| Synthetic records | `solutions/proposal-generation/manual/knowledge/aibast_proposal-generation-synthetic-records.md` |
| Operating rules | `solutions/proposal-generation/manual/knowledge/aibast_proposal-generation-operating-rules.md` |
| Uploadable operation skills | `solutions/proposal-generation/manual/skills/*/SKILL.md` |

## Operations
- `analyze_rfp` — Analyze the Meridian Healthcare synthetic RFP and produce a traceable requirement checklist.
- `executive_summary` — Draft a synthetic executive summary aligned to stated buyer priorities for human review.
- `solution_pricing` — Compare the synthetic solution and pricing assumptions without approving a price or concession.
- `references_positioning` — Draft reference and competitive positioning options using synthetic evidence only.
- `compile_proposal` — Prepare a reviewable proposal package outline; do not claim a final document was generated or approved.
- `delivery_summary` — Summarize draft proposal readiness and human-governed next-step options without sending anything.

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
| Customer field guide | `solutions/proposal-generation/field-guide.html` |
| Evidence report | `solutions/proposal-generation/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/proposal-generation/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/proposal-generation/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/proposal-generation/quest.html` |
| Literal browser tutorial | `solutions/proposal-generation/manual-tutorial.html` |
| Raw export manifest | `solutions/proposal-generation/export-manifest.json` |
| Source bundle | `solutions/proposal-generation/exports/proposal-generation-source.zip` |
| Manual evidence | `solutions/proposal-generation/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/proposal-generation/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/proposal-generation/exports/proposal-generation-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/proposal-generation/exports/proposal-generation-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/proposal-generation/exports/proposal-generation-solution-export.json` |

**Scaffold status:** 110 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
