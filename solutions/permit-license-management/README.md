# Permit Management Agent package

This package audits the approved one-pager promise against the portable agent at `agents/@aibast-agents-library/energy_stacks/permit_license_management_stack/permit_license_management_agent.py`.

## Included surfaces

- `evals/source-audit.json` — promise-to-source audit and safety findings
- `evals/transcripts.json` — canonical strict-isolation Brainstem captures
- `evals/onepager-map.json` — approved slide hash and operation coverage
- `deployment.json` — local Brainstem and future connector recipe
- `catalog-entry.json` — qualitative, hand-authored catalog copy
- `architecture.md` — read/write boundary and production seams
- `manual/knowledge/` — two synthetic upload files
- `manual/skills/` — one uploadable `SKILL.md` for each operation
- `tests/demo_cases/permit-license-management.json` — one persona case per operation

## Scope and safety

The local agent uses fictional records and produces decision support only. It does not perform live dispatch, field action, permit submission, regulator filing, billing adjustment, emissions attestation, supplier activation, shipment rerouting, or inventory movement. Production writes require an authenticated connector, explicit human approval, authorization checks, and an audit record.

## Operations

- `permit_inventory`
- `renewal_calendar`
- `compliance_gaps`
- `application_status`

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/permit-license-management/field-guide.html` |
| Evidence report | `solutions/permit-license-management/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/permit-license-management/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/permit-license-management/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/permit-license-management/quest.html` |
| Literal browser tutorial | `solutions/permit-license-management/manual-tutorial.html` |
| Raw export manifest | `solutions/permit-license-management/export-manifest.json` |
| Source bundle | `solutions/permit-license-management/exports/permit-license-management-source.zip` |
| Manual evidence | `solutions/permit-license-management/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/permit-license-management/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/permit-license-management/exports/permit-license-management-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/permit-license-management/exports/permit-license-management-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/permit-license-management/exports/permit-license-management-solution-export.json` |

**Scaffold status:** 92 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
