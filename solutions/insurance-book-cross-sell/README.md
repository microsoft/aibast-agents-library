# Book of Business Cross-Sell Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/insurance_book_cross_sell_stack/insurance_book_cross_sell_agent.py` |
| Deployment recipe | `solutions/insurance-book-cross-sell/deployment.json` |
| Approved-slide map | `solutions/insurance-book-cross-sell/evals/onepager-map.json` |
| Source audit | `solutions/insurance-book-cross-sell/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/insurance-book-cross-sell/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/insurance-book-cross-sell.json` |
| Synthetic knowledge | `solutions/insurance-book-cross-sell/manual/knowledge/` |
| Uploadable skills | `solutions/insurance-book-cross-sell/manual/skills/` |

## Scope

Turn a broker's book of business into a confirmed, routed cross-sell plan: classify every line, match it to the underwriting units with appetite, find the white space, and draft the unit and broker confirmations before anything reaches a seller's pipeline. The hero scenario is Northwind Mutual, a fictional multi-unit commercial insurer.

Implemented operations: `book_summary`, `classify_lines`, `appetite_match`, `unit_confirmation`, `broker_confirmation`, `routing_plan`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, and rule values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Paste `manual/GLOBAL-INSTRUCTIONS.md` as the agent instructions, upload both Markdown files in `manual/knowledge/`, then upload the 6 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/insurance-book-cross-sell/field-guide.html` |
| Evidence report | `solutions/insurance-book-cross-sell/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/insurance-book-cross-sell/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/insurance-book-cross-sell/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/insurance-book-cross-sell/quest.html` |
| Literal browser tutorial | `solutions/insurance-book-cross-sell/manual-tutorial.html` |
| Raw export manifest | `solutions/insurance-book-cross-sell/export-manifest.json` |
| Source bundle | `solutions/insurance-book-cross-sell/exports/insurance-book-cross-sell-source.zip` |
| Manual evidence | `solutions/insurance-book-cross-sell/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/insurance-book-cross-sell/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/insurance-book-cross-sell/exports/insurance-book-cross-sell-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/insurance-book-cross-sell/exports/insurance-book-cross-sell-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/insurance-book-cross-sell/exports/insurance-book-cross-sell-solution-export.json` |

**Scaffold status:** 118 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
