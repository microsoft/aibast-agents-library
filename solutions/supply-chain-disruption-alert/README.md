# Supply Chain Disruption Alert Agent package

This package audits the approved one-pager promise against the portable agent at `agents/@aibast-agents-library/retail_cpg_stacks/supply_chain_disruption_alert_stack/supply_chain_disruption_alert_agent.py`.

## Included surfaces

- `evals/source-audit.json` — promise-to-source audit and safety findings
- `evals/transcripts.json` — canonical strict-isolation Brainstem captures
- `evals/onepager-map.json` — approved slide hash and operation coverage
- `deployment.json` — local Brainstem and future connector recipe
- `catalog-entry.json` — qualitative, hand-authored catalog copy
- `architecture.md` — read/write boundary and production seams
- `manual/knowledge/` — two synthetic upload files
- `manual/skills/` — one uploadable `SKILL.md` for each operation
- `tests/demo_cases/supply-chain-disruption-alert.json` — one persona case per operation

## Scope and safety

The local agent uses fictional records and produces decision support only. It does not perform live dispatch, field action, permit submission, regulator filing, billing adjustment, emissions attestation, supplier activation, shipment rerouting, or inventory movement. Production writes require an authenticated connector, explicit human approval, authorization checks, and an audit record.

## Operations

- `disruption_dashboard`
- `risk_assessment`
- `mitigation_plan`
- `supplier_alternatives`

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/supply-chain-disruption-alert/field-guide.html` |
| Evidence report | `solutions/supply-chain-disruption-alert/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/supply-chain-disruption-alert/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/supply-chain-disruption-alert/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/supply-chain-disruption-alert/quest.html` |
| Literal browser tutorial | `solutions/supply-chain-disruption-alert/manual-tutorial.html` |
| Raw export manifest | `solutions/supply-chain-disruption-alert/export-manifest.json` |
| Source bundle | `solutions/supply-chain-disruption-alert/exports/supply-chain-disruption-alert-source.zip` |
| Manual evidence | `solutions/supply-chain-disruption-alert/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/supply-chain-disruption-alert/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/supply-chain-disruption-alert/exports/supply-chain-disruption-alert-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/supply-chain-disruption-alert/exports/supply-chain-disruption-alert-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/supply-chain-disruption-alert/exports/supply-chain-disruption-alert-solution-export.json` |

**Scaffold status:** 92 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
