# Solution Design Review Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/professional_services_stacks/solution_design_review_stack/solution_design_review_agent.py` |
| Deployment recipe | `solutions/solution-design-review/deployment.json` |
| Approved-slide map | `solutions/solution-design-review/evals/onepager-map.json` |
| Source audit | `solutions/solution-design-review/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/solution-design-review/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/solution-design-review.json` |
| Synthetic knowledge | `solutions/solution-design-review/manual/knowledge/` |
| Uploadable skills | `solutions/solution-design-review/manual/skills/` |

## Scope

Help architects draft and self-check a solution design document before the architecture review board: intake of the template, discovery notes and initiative brief, an architecture vision, the current-state baseline, the non-functional requirements matrix with owners and gaps, the target design with its inventory changes, and a readiness check with a confidence score and severity-ranked gaps. The agent is read-only; it never submits to the review board, changes an inventory record, or approves a design.

Implemented operations: `design_intake`, `architecture_vision`, `current_state`, `requirements_matrix`, `target_design`, `readiness_check`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence for Northwind Traders rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 6 `SKILL.md` files in `manual/skills/`. Paste `manual/GLOBAL-INSTRUCTIONS.md` as the agent instructions. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/solution-design-review/field-guide.html` |
| Evidence report | `solutions/solution-design-review/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/solution-design-review/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/solution-design-review/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/solution-design-review/quest.html` |
| Literal browser tutorial | `solutions/solution-design-review/manual-tutorial.html` |
| Raw export manifest | `solutions/solution-design-review/export-manifest.json` |
| Source bundle | `solutions/solution-design-review/exports/solution-design-review-source.zip` |
| Manual evidence | `solutions/solution-design-review/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/solution-design-review/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/solution-design-review/exports/solution-design-review-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/solution-design-review/exports/solution-design-review-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/solution-design-review/exports/solution-design-review-solution-export.json` |

**Scaffold status:** 118 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
