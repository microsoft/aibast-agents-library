# Predictive Asset Maintenance Intelligence Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/energy_stacks/grid_asset_maintenance_stack/grid_asset_maintenance_agent.py` |
| Deployment recipe | `solutions/grid-asset-maintenance/deployment.json` |
| Approved-slide map | `solutions/grid-asset-maintenance/evals/onepager-map.json` |
| Source audit | `solutions/grid-asset-maintenance/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/grid-asset-maintenance/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/grid-asset-maintenance.json` |
| Synthetic knowledge | `solutions/grid-asset-maintenance/manual/knowledge/` |
| Uploadable skills | `solutions/grid-asset-maintenance/manual/skills/` |

## Scope

Help an electricity distribution company move its grid assets from reactive to condition-based maintenance: rank power transformers, switchgear, underground cables and overhead lines by failure probability over 30, 90 and 180 days with the anomaly behind each risk, draft the preventive work order with asset history, materials, long-lead parts to order and the crew and outage pre-plan, check a completed job's field record before the asset register and the ERP fixed asset register are updated, and give leadership fleet health by asset class with the replacement pipeline and capital by year.

Hero scenario: A distribution company's reliability engineers, maintenance planners and asset managers, where Power Automate brings the condition-monitoring feed into Dataverse, Copilot Studio explains and ranks the risk, Dynamics 365 Field Service carries the work orders, Power Apps captures the field record, and Power BI shows fleet health.

Implemented operations: `risk_ranking`, `work_order_draft`, `register_update`, `replacement_plan`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

This template is grid-specific. The general Predictive Maintenance Agent (`maintenance-scheduling`) schedules production-line maintenance in manufacturing, and the Asset Maintenance Forecast Agent covers a wind-farm fleet; this one covers transmission and distribution assets, the asset register and the replacement program.

## Approval boundary

This package is synthetic and read-only. It does not connect to utility systems or execute external actions. The utility, substations, assets, people, crews, work orders, measurements and capital figures are fictional evidence rather than customer outcomes. Failure probabilities are decision support, not a safety determination. Production connections require least-privilege access, approved data handling, and a human approval step: the maintenance planner approves every work order, the reliability engineer approves every register update, the control engineer owns every switching and outage plan, and the investment committee approves the replacement program.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 4 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/grid-asset-maintenance/field-guide.html` |
| Evidence report | `solutions/grid-asset-maintenance/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/grid-asset-maintenance/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/grid-asset-maintenance/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/grid-asset-maintenance/quest.html` |
| Literal browser tutorial | `solutions/grid-asset-maintenance/manual-tutorial.html` |
| Raw export manifest | `solutions/grid-asset-maintenance/export-manifest.json` |
| Source bundle | [`grid-asset-maintenance-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/grid-asset-maintenance-source.zip) (release asset) |
| Manual evidence | `solutions/grid-asset-maintenance/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/grid-asset-maintenance/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/grid-asset-maintenance/exports/grid-asset-maintenance-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/grid-asset-maintenance/exports/grid-asset-maintenance-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/grid-asset-maintenance/exports/grid-asset-maintenance-solution-export.json` |

**Scaffold status:** 98 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
