# First-Time Fix Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/telecom_media_gaming_stacks/first_time_fix_stack/first_time_fix_agent.py` |
| Deployment recipe | `solutions/first-time-fix/deployment.json` |
| Approved-slide map | `solutions/first-time-fix/evals/onepager-map.json` |
| Source audit | `solutions/first-time-fix/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/first-time-fix/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/first-time-fix.json` |
| Synthetic knowledge | `solutions/first-time-fix/manual/knowledge/` |
| Uploadable skills | `solutions/first-time-fix/manual/skills/` |

## Scope

Help contact center and field service teams resolve connection issues on the first call by guiding the right fix for each customer's service, checking local network work and past visits before a technician is sent, and preparing the technician's job when a visit is needed, while every booking stays with a person to confirm.

Hero scenario: A regional broadband provider's contact center and field service team.

Implemented operations: `guided_fix`, `local_work_check`, `visit_history`, `technician_booking`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, and statuses are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 4 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/first-time-fix/field-guide.html` |
| Evidence report | `solutions/first-time-fix/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/first-time-fix/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/first-time-fix/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/first-time-fix/quest.html` |
| Literal browser tutorial | `solutions/first-time-fix/manual-tutorial.html` |
| Raw export manifest | `solutions/first-time-fix/export-manifest.json` |
| Source bundle | `solutions/first-time-fix/exports/first-time-fix-source.zip` |
| Manual evidence | `solutions/first-time-fix/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/first-time-fix/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/first-time-fix/exports/first-time-fix-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/first-time-fix/exports/first-time-fix-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/first-time-fix/exports/first-time-fix-solution-export.json` |

**Scaffold status:** 98 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
