# Emissions Tracking Agent package

This package audits the approved one-pager promise against the portable agent at `agents/@aibast-agents-library/energy_stacks/emission_tracking_stack/emission_tracking_agent.py`.

## Included surfaces

- `evals/source-audit.json` — promise-to-source audit and safety findings
- `evals/transcripts.json` — canonical strict-isolation Brainstem captures
- `evals/onepager-map.json` — approved slide hash and operation coverage
- `deployment.json` — local Brainstem and future connector recipe
- `catalog-entry.json` — qualitative, hand-authored catalog copy
- `architecture.md` — read/write boundary and production seams
- `manual/knowledge/` — two synthetic upload files
- `manual/skills/` — one uploadable `SKILL.md` for each operation
- `tests/demo_cases/emission-tracking.json` — one persona case per operation

## Scope and safety

The local agent uses fictional records and produces decision support only. It does not perform live dispatch, field action, permit submission, regulator filing, billing adjustment, emissions attestation, supplier activation, shipment rerouting, or inventory movement. Production writes require an authenticated connector, explicit human approval, authorization checks, and an audit record.

## Operations

- `emissions_dashboard`
- `compliance_status`
- `reduction_plan`
- `carbon_offset_analysis`

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/emission-tracking/field-guide.html` |
| Evidence report | `solutions/emission-tracking/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/emission-tracking/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/emission-tracking/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/emission-tracking/quest.html` |
| Literal browser tutorial | `solutions/emission-tracking/manual-tutorial.html` |
| Raw export manifest | `solutions/emission-tracking/export-manifest.json` |
| Source bundle | `solutions/emission-tracking/exports/emission-tracking-source.zip` |
| Manual evidence | `solutions/emission-tracking/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/emission-tracking/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/emission-tracking/exports/emission-tracking-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/emission-tracking/exports/emission-tracking-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/emission-tracking/exports/emission-tracking-solution-export.json` |

**Scaffold status:** 94 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
