# Order Status Communications Agent solution package

| Surface | Location |
| --- | --- |
| Deterministic portable agent | `agents/@aibast-agents-library/manufacturing_stacks/order_status_communication_stack/order_status_communication_agent.py` |
| Deployment recipe | `solutions/order-status-communication/deployment.json` |
| One-pager evidence map | `solutions/order-status-communication/evals/onepager-map.json` |
| Source audit | `solutions/order-status-communication/evals/source-audit.json` |
| Persona-language cases | `tests/demo_cases/order-status-communication.json` |
| Uploadable knowledge | `solutions/order-status-communication/manual/knowledge/` |
| Uploadable skills | `solutions/order-status-communication/manual/skills/` |

## Pilot scope

This package covers order status lookup, shipment tracking, internal delay review, customer update drafts. It uses a fixed fictional snapshot so every identifier, date, quantity, percentage, score, duration, and cost is synthetic pilot evidence rather than a customer result.

## Safety boundary

The local agent is recommendation-only. The agent drafts only; it never changes orders, schedules, shipments, recovery plans, or sends customer updates. Production action requires the approved systems and authorization controls listed in `deployment.json`.

## One-pager evidence

`evals/onepager-map.json` maps each approved one-pager opportunity statement to deterministic operations and persona-language cases. Promises that imply live monitoring or operational execution are represented as production seams, not as completed local side effects.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload one `SKILL.md` file per operation from `manual/skills/`. Keep the agent in Draft until customer data connections, identity, authorization, review, and audit controls are validated.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/order-status-communication/field-guide.html` |
| Evidence report | `solutions/order-status-communication/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/order-status-communication/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/order-status-communication/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/order-status-communication/quest.html` |
| Literal browser tutorial | `solutions/order-status-communication/manual-tutorial.html` |
| Raw export manifest | `solutions/order-status-communication/export-manifest.json` |
| Source bundle | `solutions/order-status-communication/exports/order-status-communication-source.zip` |
| Manual evidence | `solutions/order-status-communication/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/order-status-communication/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/order-status-communication/exports/order-status-communication-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/order-status-communication/exports/order-status-communication-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/order-status-communication/exports/order-status-communication-solution-export.json` |

**Scaffold status:** 93 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
