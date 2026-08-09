# Field Service Dispatch Agent package

This package audits the approved one-pager promise against the portable agent at `agents/@aibast-agents-library/energy_stacks/field_service_dispatch_stack/field_service_dispatch_agent.py`.

## Included surfaces

- `evals/source-audit.json` — promise-to-source audit and safety findings
- `evals/transcripts.json` — canonical strict-isolation Brainstem captures
- `evals/onepager-map.json` — approved slide hash and operation coverage
- `deployment.json` — local Brainstem and future connector recipe
- `catalog-entry.json` — qualitative, hand-authored catalog copy
- `architecture.md` — read/write boundary and production seams
- `manual/knowledge/` — two synthetic upload files
- `manual/skills/` — one uploadable `SKILL.md` for each operation
- `tests/demo_cases/field-service-dispatch.json` — one persona case per operation

## Scope and safety

The local agent uses fictional records and produces decision support only. It does not perform live dispatch, field action, permit submission, regulator filing, billing adjustment, emissions attestation, supplier activation, shipment rerouting, or inventory movement. Production writes require an authenticated connector, explicit human approval, authorization checks, and an audit record.

## Operations

- `dispatch_dashboard`
- `route_optimization`
- `technician_assignment`
- `emergency_response`

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/field-service-dispatch/field-guide.html` |
| Evidence report | `solutions/field-service-dispatch/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/field-service-dispatch/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/field-service-dispatch/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/field-service-dispatch/quest.html` |
| Literal browser tutorial | `solutions/field-service-dispatch/manual-tutorial.html` |
| Raw export manifest | `solutions/field-service-dispatch/export-manifest.json` |
| Source bundle | `solutions/field-service-dispatch/exports/field-service-dispatch-source.zip` |
| Manual evidence | `solutions/field-service-dispatch/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/field-service-dispatch/screenshots/manual/browserfilm.json` |

**Scaffold status:** 69 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
