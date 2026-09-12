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

Use `manual-tutorial.html` to upload the exact policy, both knowledge files and
all four skills. This manual lane has no tools or production connections.
Save, leave and reopen the Draft to verify persistence before running each
unchanged locked prompt in a fresh Preview conversation. Stop before publish.

## Preservation review — 2026-09-12

The [pilot review](evals/manual-pilot-review.json) corroborates four saved
repaired response findings, not whole-workshop acceptance. The final browser
policy and two repaired skills are preserved in `manual/` and mirrored in
native source. The controls knowledge file was reconciled afterward and needs
fresh live regression. Portable application-scope and missing-ID defects,
full evaluator coverage, and per-step visual gates remain open.

The [as-of progress snapshot](../../state/manual_workshop_pilot_2026-09-12.json)
preserves the captured status distribution without upgrading inherited reports.
Historical failures remain failures; old screenshots are not proof of these
repairs. The source ZIP is an explicit public-safe manual review subset, **not**
a native import package. The historical native ZIP omits the workshop skills
and knowledge and does not reproduce the manual build.

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
| Historical Copilot Studio solution ZIP — source repair pending | `solutions/fs-customer-onboarding/exports/fs-customer-onboarding-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/fs-customer-onboarding/exports/fs-customer-onboarding-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/fs-customer-onboarding/exports/fs-customer-onboarding-solution-export.json` |

**Scaffold status:** 74 resources ready; 0 pending. Pending assets are not evidence and must not be claimed as captured. Current manual Preview and saved-instruction verification remain pending.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
