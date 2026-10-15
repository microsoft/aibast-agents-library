# Order Entry Validation Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/manufacturing_stacks/order_entry_validation_stack/order_entry_validation_agent.py` |
| Deployment recipe | `solutions/order-entry-validation/deployment.json` |
| Approved-slide map | `solutions/order-entry-validation/evals/onepager-map.json` |
| Source audit | `solutions/order-entry-validation/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/order-entry-validation/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/order-entry-validation.json` |
| Synthetic knowledge | `solutions/order-entry-validation/manual/knowledge/` |
| Uploadable skills | `solutions/order-entry-validation/manual/skills/` |

## Scope

Turn inbound customer purchase orders into validated draft sales orders: extract every PO field, check prices and terms against the accepted quote, catch invalid product configurations, classify the order, and hand a specialist a draft with each exception called out before entry. The hero scenario is Proseware Instruments, a fictional maker of portable gas analyzers.

Implemented operations: `order_queue`, `extract_po`, `quote_validation`, `configuration_check`, `order_classification`, `draft_sales_order`, `queue_review`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, and rule values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Paste `manual/GLOBAL-INSTRUCTIONS.md` as the agent instructions, upload both Markdown files in `manual/knowledge/`, then upload the 7 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/order-entry-validation/field-guide.html` |
| Evidence report | `solutions/order-entry-validation/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/order-entry-validation/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/order-entry-validation/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/order-entry-validation/quest.html` |
| Literal browser tutorial | `solutions/order-entry-validation/manual-tutorial.html` |
| Raw export manifest | `solutions/order-entry-validation/export-manifest.json` |
| Source bundle | `solutions/order-entry-validation/exports/order-entry-validation-source.zip` |
| Manual evidence | `solutions/order-entry-validation/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/order-entry-validation/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/order-entry-validation/exports/order-entry-validation-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/order-entry-validation/exports/order-entry-validation-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/order-entry-validation/exports/order-entry-validation-solution-export.json` |

**Scaffold status:** 126 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
