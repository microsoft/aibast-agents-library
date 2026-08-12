# Utility Billing and Assistance Agent package

This package audits the approved one-pager promise against the portable agent at `agents/@aibast-agents-library/slg_government_stacks/utility_billing_assistance_stack/utility_billing_assistance_agent.py`.

## Included surfaces

- `evals/source-audit.json` — promise-to-source audit and safety findings
- `evals/transcripts.json` — canonical strict-isolation Brainstem captures
- `evals/onepager-map.json` — approved slide hash and operation coverage
- `deployment.json` — local Brainstem and future connector recipe
- `catalog-entry.json` — qualitative, hand-authored catalog copy
- `architecture.md` — read/write boundary and production seams
- `manual/knowledge/` — two synthetic upload files
- `manual/skills/` — one uploadable `SKILL.md` for each operation
- `tests/demo_cases/utility-billing-assistance.json` — one persona case per operation

## Scope and safety

The local agent uses fictional records and produces decision support only. It does not perform live dispatch, field action, permit submission, regulator filing, billing adjustment, emissions attestation, supplier activation, shipment rerouting, or inventory movement. Production writes require an authenticated connector, explicit human approval, authorization checks, and an audit record.

## Operations

- `billing_inquiry`
- `usage_analysis`
- `payment_plan`
- `assistance_programs`

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/utility-billing-assistance/field-guide.html` |
| Evidence report | `solutions/utility-billing-assistance/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/utility-billing-assistance/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/utility-billing-assistance/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/utility-billing-assistance/quest.html` |
| Literal browser tutorial | `solutions/utility-billing-assistance/manual-tutorial.html` |
| Raw export manifest | `solutions/utility-billing-assistance/export-manifest.json` |
| Source bundle | `solutions/utility-billing-assistance/exports/utility-billing-assistance-source.zip` |
| Manual evidence | `solutions/utility-billing-assistance/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/utility-billing-assistance/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/utility-billing-assistance/exports/utility-billing-assistance-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/utility-billing-assistance/exports/utility-billing-assistance-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/utility-billing-assistance/exports/utility-billing-assistance-solution-export.json` |

**Scaffold status:** 93 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
