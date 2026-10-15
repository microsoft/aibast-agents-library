# M&A Target Sourcing Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/ma_target_sourcing_stack/ma_target_sourcing_agent.py` |
| Deployment recipe | `solutions/ma-target-sourcing/deployment.json` |
| Approved-slide map | `solutions/ma-target-sourcing/evals/onepager-map.json` |
| Source audit | `solutions/ma-target-sourcing/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/ma-target-sourcing/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/ma-target-sourcing.json` |
| Synthetic knowledge | `solutions/ma-target-sourcing/manual/knowledge/` |
| Uploadable skills | `solutions/ma-target-sourcing/manual/skills/` |

## Scope

Turn an acquisition thesis into a transparent, cited target shortlist: screening criteria, a weighted ranking of a synthetic market universe, target dossiers with sources and diligence questions, a weighting challenge, evidence-gap review, and an investment committee screening memo draft. The agent is read-only; it never contacts a target, updates a CRM, shares a document, or makes an investment decision.

Implemented operations: `build_thesis`, `screen_targets`, `target_dossier`, `challenge_ranking`, `evidence_gaps`, `ic_memo_draft`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence for Fabrikam Information Services rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 6 `SKILL.md` files in `manual/skills/`. Paste `manual/GLOBAL-INSTRUCTIONS.md` as the agent instructions. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/ma-target-sourcing/field-guide.html` |
| Evidence report | `solutions/ma-target-sourcing/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/ma-target-sourcing/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/ma-target-sourcing/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/ma-target-sourcing/quest.html` |
| Literal browser tutorial | `solutions/ma-target-sourcing/manual-tutorial.html` |
| Raw export manifest | `solutions/ma-target-sourcing/export-manifest.json` |
| Source bundle | `solutions/ma-target-sourcing/exports/ma-target-sourcing-source.zip` |
| Manual evidence | `solutions/ma-target-sourcing/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/ma-target-sourcing/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/ma-target-sourcing/exports/ma-target-sourcing-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/ma-target-sourcing/exports/ma-target-sourcing-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/ma-target-sourcing/exports/ma-target-sourcing-solution-export.json` |

**Scaffold status:** 118 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
