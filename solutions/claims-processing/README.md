# Claims Processing Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/claims_processing_stack/claims_processing_agent.py` |
| Deployment recipe | `solutions/claims-processing/deployment.json` |
| Locked behavior cases | `tests/demo_cases/claims-processing.json` |
| Approved one-pager map | `solutions/claims-processing/evals/onepager-map.json` |
| Source capability audit | `solutions/claims-processing/evals/source-audit.json` |
| Strict-isolation transcripts | `solutions/claims-processing/evals/transcripts.json` |
| Uploadable synthetic knowledge | `solutions/claims-processing/manual/knowledge/` |
| Uploadable operation skills | `solutions/claims-processing/manual/skills/` |

## Implemented scope

- `claim_intake` — Claims intake triage.
- `adjudication_review` — Claim-file readiness.
- `fraud_flag` — SIU indicator review.
- `settlement_recommendation` — Policy-term settlement estimate.

## Evidence and safety boundary

The approved one-pager `39. Claims Processing Agent one-pager.pptx` is the evidence source for this package. Each advertised promise maps to source behavior and locked persona-language cases in `evals/onepager-map.json`. All records, identifiers, dates, amounts, scores, statuses, and outcomes are synthetic.

This package provides decision support only. It gives no legal, regulatory, insurance, lending, tax, investment, or financial advice; makes no approval or transaction claim; and requires explicit authorized human review before any external action.

## Manual Copilot Studio preparation

Upload the two Markdown files in `manual/knowledge/`, then upload one `SKILL.md` for each of the 4 operations in `manual/skills/`. Bind only approved least-privilege connections. Validate all locked cases and stop before publish. No Copilot Studio project, tutorial, screenshot, or bundle is included.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/claims-processing/field-guide.html` |
| Evidence report | `solutions/claims-processing/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/claims-processing/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/claims-processing/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/claims-processing/quest.html` |
| Literal browser tutorial | `solutions/claims-processing/manual-tutorial.html` |
| Raw export manifest | `solutions/claims-processing/export-manifest.json` |
| Source bundle | `solutions/claims-processing/exports/claims-processing-source.zip` |
| Manual evidence | `solutions/claims-processing/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/claims-processing/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/claims-processing/exports/claims-processing-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/claims-processing/exports/claims-processing-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/claims-processing/exports/claims-processing-solution-export.json` |

**Scaffold status:** 92 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
