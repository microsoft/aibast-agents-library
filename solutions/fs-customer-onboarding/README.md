# Customer Onboarding Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/customer_onboarding_fs_stack/customer_onboarding_fs_agent.py` |
| Deployment recipe | `solutions/fs-customer-onboarding/deployment.json` |
| Locked behavior cases | `tests/demo_cases/fs-customer-onboarding.json` |
| Approved one-pager map | `solutions/fs-customer-onboarding/evals/onepager-map.json` |
| Source capability audit | `solutions/fs-customer-onboarding/evals/source-audit.json` |
| Strict-isolation transcripts | `solutions/fs-customer-onboarding/evals/transcripts.json` |
| Uploadable synthetic knowledge | `solutions/fs-customer-onboarding/manual/knowledge/` |
| Uploadable operation skills | `solutions/fs-customer-onboarding/manual/skills/` |

## Implemented scope

- `kyc_verification` — KYC evidence review.
- `account_setup` — Account setup preparation.
- `document_checklist` — Document readiness.
- `onboarding_status` — Onboarding pipeline.

## Evidence and safety boundary

The approved one-pager `Customer Onboarding Agent one-pager.pptx` is the evidence source for this package. Each advertised promise maps to source behavior and locked persona-language cases in `evals/onepager-map.json`. All records, identifiers, dates, amounts, scores, statuses, and outcomes are synthetic.

This package provides decision support only. It gives no legal, regulatory, insurance, lending, tax, investment, or financial advice; makes no approval or transaction claim; and requires explicit authorized human review before any external action.

## Manual Copilot Studio preparation

Upload the two Markdown files in `manual/knowledge/`, then upload one `SKILL.md` for each of the 4 operations in `manual/skills/`. Bind only approved least-privilege connections. Validate all locked cases and stop before publish. No Copilot Studio project, tutorial, screenshot, or bundle is included.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/fs-customer-onboarding/field-guide.html` |
| Evidence report | `solutions/fs-customer-onboarding/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/fs-customer-onboarding/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/fs-customer-onboarding/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/fs-customer-onboarding/quest.html` |
| Literal browser tutorial | `solutions/fs-customer-onboarding/manual-tutorial.html` |
| Raw export manifest | `solutions/fs-customer-onboarding/export-manifest.json` |
| Source bundle | `solutions/fs-customer-onboarding/exports/fs-customer-onboarding-source.zip` |
| Manual evidence | `solutions/fs-customer-onboarding/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/fs-customer-onboarding/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/fs-customer-onboarding/exports/fs-customer-onboarding-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/fs-customer-onboarding/exports/fs-customer-onboarding-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/fs-customer-onboarding/exports/fs-customer-onboarding-solution-export.json` |

**Scaffold status:** 92 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
