# Contract Risk Review solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/professional_services_stacks/contract_risk_review_stack/contract_risk_review_agent.py` |
| Deployment recipe | `solutions/contract-risk-review/deployment.json` |
| Live behavior gate | `tests/demo_cases/contract-risk-review.json` |
| PowerPoint evidence map | `solutions/contract-risk-review/evals/onepager-map.json` |
| Strict-isolation transcripts | `solutions/contract-risk-review/evals/transcripts.json` |
| Manual knowledge | `solutions/contract-risk-review/manual/knowledge/` |
| Manual skills | `solutions/contract-risk-review/manual/skills/` |

## Implemented scope

The package demonstrates portfolio risk triage, clause-level analysis,
internal-policy screening, and counsel-review negotiation briefs. The source
uses fictional agreements and fixed findings. It does not edit, approve, sign,
or transmit contracts and does not provide legal advice.

Upload both knowledge files and the four `SKILL.md` files to reproduce the
deterministic pilot in Copilot Studio. Production use requires approved
SharePoint and Microsoft Word connections plus legal review of every output.

The canonical transcript artifact was captured with only
`ContractRiskReviewAgent` discoverable and records all four persona cases as
passing.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/contract-risk-review/field-guide.html` |
| Evidence report | `solutions/contract-risk-review/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/contract-risk-review/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/contract-risk-review/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/contract-risk-review/quest.html` |
| Literal browser tutorial | `solutions/contract-risk-review/manual-tutorial.html` |
| Raw export manifest | `solutions/contract-risk-review/export-manifest.json` |
| Source bundle | `solutions/contract-risk-review/exports/contract-risk-review-source.zip` |
| Manual evidence | `solutions/contract-risk-review/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/contract-risk-review/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/contract-risk-review/exports/contract-risk-review-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/contract-risk-review/exports/contract-risk-review-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/contract-risk-review/exports/contract-risk-review-solution-export.json` |

**Scaffold status:** 82 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
