# Asset Maintenance Forecast Agent package

This package audits the approved one-pager promise against the portable agent at `agents/@aibast-agents-library/energy_stacks/asset_maintenance_forecast_stack/asset_maintenance_forecast_agent.py`.

## Included surfaces

- `evals/source-audit.json` — promise-to-source audit and safety findings
- `evals/transcripts.json` — canonical strict-isolation Brainstem captures
- `evals/onepager-map.json` — approved slide hash and operation coverage
- `deployment.json` — local Brainstem and future connector recipe
- `catalog-entry.json` — qualitative, hand-authored catalog copy
- `architecture.md` — read/write boundary and production seams
- `manual/knowledge/` — two synthetic upload files
- `manual/skills/` — one uploadable `SKILL.md` for each operation
- `tests/demo_cases/asset-maintenance-forecast.json` — one persona case per operation

## Scope and safety

The local agent uses fictional records and produces decision support only. It does not perform live dispatch, field action, permit submission, regulator filing, billing adjustment, emissions attestation, supplier activation, shipment rerouting, or inventory movement. Production writes require an authenticated connector, explicit human approval, authorization checks, and an audit record.

## Operations

- `maintenance_forecast`
- `asset_health`
- `budget_projection`
- `work_order_plan`

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/asset-maintenance-forecast/field-guide.html` |
| Evidence report | `solutions/asset-maintenance-forecast/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/asset-maintenance-forecast/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/asset-maintenance-forecast/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/asset-maintenance-forecast/quest.html` |
| Literal browser tutorial | `solutions/asset-maintenance-forecast/manual-tutorial.html` |
| Raw export manifest | `solutions/asset-maintenance-forecast/export-manifest.json` |
| Source bundle | `solutions/asset-maintenance-forecast/exports/asset-maintenance-forecast-source.zip` |
| Manual evidence | `solutions/asset-maintenance-forecast/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/asset-maintenance-forecast/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/asset-maintenance-forecast/exports/asset-maintenance-forecast-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/asset-maintenance-forecast/exports/asset-maintenance-forecast-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/asset-maintenance-forecast/exports/asset-maintenance-forecast-solution-export.json` |

**Scaffold status:** 93 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
