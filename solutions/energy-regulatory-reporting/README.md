# Regulatory Reporting Agent package

This package audits the approved one-pager promise against the portable agent at `agents/@aibast-agents-library/energy_stacks/regulatory_reporting_stack/regulatory_reporting_agent.py`.

## Included surfaces

- `evals/source-audit.json` — promise-to-source audit and safety findings
- `evals/transcripts.json` — canonical strict-isolation Brainstem captures
- `evals/onepager-map.json` — approved slide hash and operation coverage
- `deployment.json` — local Brainstem and future connector recipe
- `catalog-entry.json` — qualitative, hand-authored catalog copy
- `architecture.md` — read/write boundary and production seams
- `manual/knowledge/` — two synthetic upload files
- `manual/skills/` — one uploadable `SKILL.md` for each operation
- `tests/demo_cases/energy-regulatory-reporting.json` — one persona case per operation

## Scope and safety

The local agent uses fictional records and produces decision support only. It does not perform live dispatch, field action, permit submission, regulator filing, billing adjustment, emissions attestation, supplier activation, shipment rerouting, or inventory movement. Production writes require an authenticated connector, explicit human approval, authorization checks, and an audit record.

## Operations

- `report_status`
- `data_validation`
- `submission_tracker`
- `audit_readiness`

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/energy-regulatory-reporting/field-guide.html` |
| Evidence report | `solutions/energy-regulatory-reporting/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/energy-regulatory-reporting/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/energy-regulatory-reporting/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/energy-regulatory-reporting/quest.html` |
| Literal browser tutorial | `solutions/energy-regulatory-reporting/manual-tutorial.html` |
| Raw export manifest | `solutions/energy-regulatory-reporting/export-manifest.json` |
| Source bundle | `solutions/energy-regulatory-reporting/exports/energy-regulatory-reporting-source.zip` |
| Manual evidence | `solutions/energy-regulatory-reporting/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/energy-regulatory-reporting/screenshots/manual/browserfilm.json` |

**Scaffold status:** 69 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
