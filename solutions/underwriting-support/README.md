# Underwriting Support Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/underwriting_support_stack/underwriting_support_agent.py` |
| Deployment recipe | `solutions/underwriting-support/deployment.json` |
| Locked behavior cases | `tests/demo_cases/underwriting-support.json` |
| Approved one-pager map | `solutions/underwriting-support/evals/onepager-map.json` |
| Source capability audit | `solutions/underwriting-support/evals/source-audit.json` |
| Strict-isolation transcripts | `solutions/underwriting-support/evals/transcripts.json` |
| Uploadable synthetic knowledge | `solutions/underwriting-support/manual/knowledge/` |
| Uploadable operation skills | `solutions/underwriting-support/manual/skills/` |

## Implemented scope

- `risk_evaluation` — Submission risk evaluation.
- `pricing_recommendation` — Illustrative pricing-factor review.
- `guideline_check` — Guideline and document alignment.
- `exception_review` — Exception review queue.

## Evidence and safety boundary

The approved one-pager `33. Underwriting Support Agent one-pager.pptx` is the evidence source for this package. Each advertised promise maps to source behavior and locked persona-language cases in `evals/onepager-map.json`. All records, identifiers, dates, amounts, scores, statuses, and outcomes are synthetic.

This package provides decision support only. It gives no legal, regulatory, insurance, lending, tax, investment, or financial advice; makes no approval or transaction claim; and requires explicit authorized human review before any external action.

## Manual Copilot Studio preparation

Upload the two Markdown files in `manual/knowledge/`, then upload one `SKILL.md` for each of the 4 operations in `manual/skills/`. Bind only approved least-privilege connections. Validate all locked cases and stop before publish. No Copilot Studio project, tutorial, screenshot, or bundle is included.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/underwriting-support/field-guide.html` |
| Evidence report | `solutions/underwriting-support/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/underwriting-support/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/underwriting-support/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/underwriting-support/quest.html` |
| Literal browser tutorial | `solutions/underwriting-support/manual-tutorial.html` |
| Raw export manifest | `solutions/underwriting-support/export-manifest.json` |
| Source bundle | `solutions/underwriting-support/exports/underwriting-support-source.zip` |
| Manual evidence | `solutions/underwriting-support/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/underwriting-support/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/underwriting-support/exports/underwriting-support-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/underwriting-support/exports/underwriting-support-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/underwriting-support/exports/underwriting-support-solution-export.json` |

**Scaffold status:** 90 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
