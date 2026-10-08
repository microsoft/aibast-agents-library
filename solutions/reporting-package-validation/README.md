# Reporting Package Validation Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/reporting_package_validation_stack/reporting_package_validation_agent.py` |
| Deployment recipe | `solutions/reporting-package-validation/deployment.json` |
| Approved-slide map | `solutions/reporting-package-validation/evals/onepager-map.json` |
| Source audit | `solutions/reporting-package-validation/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/reporting-package-validation/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/reporting-package-validation.json` |
| Synthetic knowledge | `solutions/reporting-package-validation/manual/knowledge/` |
| Uploadable skills | `solutions/reporting-package-validation/manual/skills/` |

## Scope

Validate a month-end reporting package before anyone builds the executive pack: file intake with source lineage, integrity checks that separate missing data from a reported zero, division variance against budget with explanation thresholds, driver bridge reconciliation, an owner-routed exception queue, and a draft executive summary. The agent is read-only; it never posts a journal, edits a submission, releases the package, or sends commentary.

Implemented operations: `package_intake`, `integrity_checks`, `variance_analysis`, `driver_reconciliation`, `exception_queue`, `executive_summary`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence for Proseware Holdings rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 6 `SKILL.md` files in `manual/skills/`. Paste `manual/GLOBAL-INSTRUCTIONS.md` as the agent instructions. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/reporting-package-validation/field-guide.html` |
| Evidence report | `solutions/reporting-package-validation/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/reporting-package-validation/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/reporting-package-validation/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/reporting-package-validation/quest.html` |
| Literal browser tutorial | `solutions/reporting-package-validation/manual-tutorial.html` |
| Raw export manifest | `solutions/reporting-package-validation/export-manifest.json` |
| Source bundle | `solutions/reporting-package-validation/exports/reporting-package-validation-source.zip` |
| Manual evidence | `solutions/reporting-package-validation/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/reporting-package-validation/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/reporting-package-validation/exports/reporting-package-validation-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/reporting-package-validation/exports/reporting-package-validation-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/reporting-package-validation/exports/reporting-package-validation-solution-export.json` |

**Scaffold status:** 118 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
