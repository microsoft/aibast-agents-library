# Content Launch Clearance Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/telecom_media_gaming_stacks/content_launch_clearance_stack/content_launch_clearance_agent.py` |
| Deployment recipe | `solutions/content-launch-clearance/deployment.json` |
| Approved-slide map | `solutions/content-launch-clearance/evals/onepager-map.json` |
| Source audit | `solutions/content-launch-clearance/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/content-launch-clearance/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/content-launch-clearance.json` |
| Synthetic knowledge | `solutions/content-launch-clearance/manual/knowledge/` |
| Uploadable skills | `solutions/content-launch-clearance/manual/skills/` |

## Scope

Help programming, distribution, and rights teams confirm where, when, and on which platform a title can launch by citing the exact contract clause behind each clearance answer, showing the distribution window and any holdback that blocks an earlier date, and checking what is still missing before rights approval, while every approval stays with the rights team.

Hero scenario: A global media company's programming, distribution, and rights teams.

Implemented operations: `launch_clearance`, `distribution_window`, `approval_readiness`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, and statuses are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 3 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/content-launch-clearance/field-guide.html` |
| Evidence report | `solutions/content-launch-clearance/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/content-launch-clearance/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/content-launch-clearance/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/content-launch-clearance/quest.html` |
| Literal browser tutorial | `solutions/content-launch-clearance/manual-tutorial.html` |
| Raw export manifest | `solutions/content-launch-clearance/export-manifest.json` |
| Source bundle | `solutions/content-launch-clearance/exports/content-launch-clearance-source.zip` |
| Manual evidence | `solutions/content-launch-clearance/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/content-launch-clearance/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/content-launch-clearance/exports/content-launch-clearance-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/content-launch-clearance/exports/content-launch-clearance-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/content-launch-clearance/exports/content-launch-clearance-solution-export.json` |

**Scaffold status:** 90 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
