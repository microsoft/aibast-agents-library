# Staffing Territory Planning Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/professional_services_stacks/staffing_territory_planning_stack/staffing_territory_planning_agent.py` |
| Deployment recipe | `solutions/staffing-territory-planning/deployment.json` |
| Approved-slide map | `solutions/staffing-territory-planning/evals/onepager-map.json` |
| Source audit | `solutions/staffing-territory-planning/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/staffing-territory-planning/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/staffing-territory-planning.json` |
| Synthetic knowledge | `solutions/staffing-territory-planning/manual/knowledge/` |
| Uploadable skills | `solutions/staffing-territory-planning/manual/skills/` |

## Scope

A staffing territory-planning demonstration over a fixed synthetic snapshot: territory snapshot, market sizing, coverage gaps, competitive landscape, labor trends and a draft quarterly plan, with every headcount, quota and account decision left to sales leadership.

Implemented operations: `territory_snapshot`, `market_sizing`, `coverage_gaps`, `competitive_landscape`, `labor_trends`, `territory_plan`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 6 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/staffing-territory-planning/field-guide.html` |
| Evidence report | `solutions/staffing-territory-planning/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/staffing-territory-planning/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/staffing-territory-planning/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/staffing-territory-planning/quest.html` |
| Literal browser tutorial | `solutions/staffing-territory-planning/manual-tutorial.html` |
| Raw export manifest | `solutions/staffing-territory-planning/export-manifest.json` |
| Source bundle | `solutions/staffing-territory-planning/exports/staffing-territory-planning-source.zip` |
| Manual evidence | `solutions/staffing-territory-planning/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/staffing-territory-planning/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/staffing-territory-planning/exports/staffing-territory-planning-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/staffing-territory-planning/exports/staffing-territory-planning-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/staffing-territory-planning/exports/staffing-territory-planning-solution-export.json` |

**Scaffold status:** 118 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
