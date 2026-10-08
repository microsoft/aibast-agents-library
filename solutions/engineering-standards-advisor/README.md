# Engineering Standards Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/energy_stacks/engineering_standards_advisor_stack/engineering_standards_advisor_agent.py` |
| Deployment recipe | `solutions/engineering-standards-advisor/deployment.json` |
| Approved-slide map | `solutions/engineering-standards-advisor/evals/onepager-map.json` |
| Source audit | `solutions/engineering-standards-advisor/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/engineering-standards-advisor/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/engineering-standards-advisor.json` |
| Synthetic knowledge | `solutions/engineering-standards-advisor/manual/knowledge/` |
| Uploadable skills | `solutions/engineering-standards-advisor/manual/skills/` |

## Scope

Give designers and field crews vetted values with exact citations, clearly labeled interpretations when no vetted value exists, and a review loop that lets standards engineers turn good interpretations into vetted guidance.

Implemented operations: `vetted_lookup`, `interpretation`, `flag_for_review`, `review_queue`, `quick_reference`, `scope_job`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 6 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/engineering-standards-advisor/field-guide.html` |
| Evidence report | `solutions/engineering-standards-advisor/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/engineering-standards-advisor/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/engineering-standards-advisor/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/engineering-standards-advisor/quest.html` |
| Literal browser tutorial | `solutions/engineering-standards-advisor/manual-tutorial.html` |
| Raw export manifest | `solutions/engineering-standards-advisor/export-manifest.json` |
| Source bundle | `solutions/engineering-standards-advisor/exports/engineering-standards-advisor-source.zip` |
| Manual evidence | `solutions/engineering-standards-advisor/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/engineering-standards-advisor/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/engineering-standards-advisor/exports/engineering-standards-advisor-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/engineering-standards-advisor/exports/engineering-standards-advisor-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/engineering-standards-advisor/exports/engineering-standards-advisor-solution-export.json` |

**Scaffold status:** 118 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
