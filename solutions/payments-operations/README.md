# Payments Operations Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/payments_operations_stack/payments_operations_agent.py` |
| Deployment recipe | `solutions/payments-operations/deployment.json` |
| Approved-slide map | `solutions/payments-operations/evals/onepager-map.json` |
| Source audit | `solutions/payments-operations/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/payments-operations/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/payments-operations.json` |
| Synthetic knowledge | `solutions/payments-operations/manual/knowledge/` |
| Uploadable skills | `solutions/payments-operations/manual/skills/` |

## Scope

Help payments operations teams clear the daily release queue faster by validating payments against scheme rules, planning exception repairs, reviewing pre-release risk, reconciling settlement accounts, and answering status questions with evidence, while every release decision stays with an authorized analyst.

Hero scenario: A regional bank's payments operations desk at the fictional Woodgrove Bank.

Implemented operations: `queue_overview`, `validate_payment`, `repair_plan`, `release_risk_review`, `reconcile_settlement`, `payment_status`, `daily_kpi_brief`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, and statuses are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 7 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/payments-operations/field-guide.html` |
| Evidence report | `solutions/payments-operations/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/payments-operations/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/payments-operations/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/payments-operations/quest.html` |
| Literal browser tutorial | `solutions/payments-operations/manual-tutorial.html` |
| Raw export manifest | `solutions/payments-operations/export-manifest.json` |
| Source bundle | `solutions/payments-operations/exports/payments-operations-source.zip` |
| Manual evidence | `solutions/payments-operations/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/payments-operations/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/payments-operations/exports/payments-operations-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/payments-operations/exports/payments-operations-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/payments-operations/exports/payments-operations-solution-export.json` |

**Scaffold status:** 126 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
