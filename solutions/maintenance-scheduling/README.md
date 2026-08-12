# Maintenance Scheduling Agent solution package

| Surface | Location |
| --- | --- |
| Deterministic portable agent | `agents/@aibast-agents-library/manufacturing_stacks/maintenance_scheduling_stack/maintenance_scheduling_agent.py` |
| Deployment recipe | `solutions/maintenance-scheduling/deployment.json` |
| One-pager evidence map | `solutions/maintenance-scheduling/evals/onepager-map.json` |
| Source audit | `solutions/maintenance-scheduling/evals/source-audit.json` |
| Persona-language cases | `tests/demo_cases/maintenance-scheduling.json` |
| Uploadable knowledge | `solutions/maintenance-scheduling/manual/knowledge/` |
| Uploadable skills | `solutions/maintenance-scheduling/manual/skills/` |

## Pilot scope

This package covers maintenance overview, predictive alerts, proposed work plan, downtime analysis. It uses a fixed fictional snapshot so every identifier, date, quantity, percentage, score, duration, and cost is synthetic pilot evidence rather than a customer result.

## Safety boundary

The local agent is recommendation-only. The agent never controls equipment or creates, assigns, schedules, or dispatches maintenance work. Production action requires the approved systems and authorization controls listed in `deployment.json`.

## One-pager evidence

`evals/onepager-map.json` maps each approved one-pager opportunity statement to deterministic operations and persona-language cases. Promises that imply live monitoring or operational execution are represented as production seams, not as completed local side effects.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload one `SKILL.md` file per operation from `manual/skills/`. Keep the agent in Draft until customer data connections, identity, authorization, review, and audit controls are validated.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/maintenance-scheduling/field-guide.html` |
| Evidence report | `solutions/maintenance-scheduling/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/maintenance-scheduling/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/maintenance-scheduling/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/maintenance-scheduling/quest.html` |
| Literal browser tutorial | `solutions/maintenance-scheduling/manual-tutorial.html` |
| Raw export manifest | `solutions/maintenance-scheduling/export-manifest.json` |
| Source bundle | `solutions/maintenance-scheduling/exports/maintenance-scheduling-source.zip` |
| Manual evidence | `solutions/maintenance-scheduling/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/maintenance-scheduling/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/maintenance-scheduling/exports/maintenance-scheduling-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/maintenance-scheduling/exports/maintenance-scheduling-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/maintenance-scheduling/exports/maintenance-scheduling-solution-export.json` |

**Scaffold status:** 85 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
