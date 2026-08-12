# Loan Origination Assistant solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/loan_origination_assistant_stack/loan_origination_assistant_agent.py` |
| Deployment recipe | `solutions/loan-origination-assistant/deployment.json` |
| Locked behavior cases | `tests/demo_cases/loan-origination-assistant.json` |
| Approved one-pager map | `solutions/loan-origination-assistant/evals/onepager-map.json` |
| Source capability audit | `solutions/loan-origination-assistant/evals/source-audit.json` |
| Strict-isolation transcripts | `solutions/loan-origination-assistant/evals/transcripts.json` |
| Uploadable synthetic knowledge | `solutions/loan-origination-assistant/manual/knowledge/` |
| Uploadable operation skills | `solutions/loan-origination-assistant/manual/skills/` |

## Implemented scope

- `application_review` — Application intake.
- `credit_analysis` — Eligibility and ratio analysis.
- `document_verification` — Document readiness.
- `decision_recommendation` — Nonbinding underwriting findings.
- `condition_tracking` — Condition and timeline review.

## Evidence and safety boundary

The approved one-pager `40. Loan Origination Assistant one-pager.pptx` is the evidence source for this package. Each advertised promise maps to source behavior and locked persona-language cases in `evals/onepager-map.json`. All records, identifiers, dates, amounts, scores, statuses, and outcomes are synthetic.

This package provides decision support only. It gives no legal, regulatory, insurance, lending, tax, investment, or financial advice; makes no approval or transaction claim; and requires explicit authorized human review before any external action.

## Manual Copilot Studio preparation

Upload the two Markdown files in `manual/knowledge/`, then upload one `SKILL.md` for each of the 5 operations in `manual/skills/`. Bind only approved least-privilege connections. Validate all locked cases and stop before publish. No Copilot Studio project, tutorial, screenshot, or bundle is included.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/loan-origination-assistant/field-guide.html` |
| Evidence report | `solutions/loan-origination-assistant/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/loan-origination-assistant/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/loan-origination-assistant/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/loan-origination-assistant/quest.html` |
| Literal browser tutorial | `solutions/loan-origination-assistant/manual-tutorial.html` |
| Raw export manifest | `solutions/loan-origination-assistant/export-manifest.json` |
| Source bundle | `solutions/loan-origination-assistant/exports/loan-origination-assistant-source.zip` |
| Manual evidence | `solutions/loan-origination-assistant/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/loan-origination-assistant/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/loan-origination-assistant/exports/loan-origination-assistant-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/loan-origination-assistant/exports/loan-origination-assistant-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/loan-origination-assistant/exports/loan-origination-assistant-solution-export.json` |

**Scaffold status:** 97 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
