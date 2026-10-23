# Live Event Launch Planner Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/telecom_media_gaming_stacks/live_event_launch_planner_stack/live_event_launch_planner_agent.py` |
| Deployment recipe | `solutions/live-event-launch-planner/deployment.json` |
| Approved-slide map | `solutions/live-event-launch-planner/evals/onepager-map.json` |
| Source audit | `solutions/live-event-launch-planner/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/live-event-launch-planner/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/live-event-launch-planner.json` |
| Synthetic knowledge | `solutions/live-event-launch-planner/manual/knowledge/` |
| Uploadable skills | `solutions/live-event-launch-planner/manual/skills/` |

## Scope

Help live operations, community, and marketing teams launch seasonal in-game events from one plan by building the timeline from communications approval to launch day, compiling readiness across teams with owners and status, and checking player announcements before publishing, while nothing is published or sent without a person's approval.

Hero scenario: A global game studio's live operations, community, and marketing teams.

Implemented operations: `launch_timeline`, `readiness_checklist`, `announcement_check`, `launch_summary`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, and statuses are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 4 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/live-event-launch-planner/field-guide.html` |
| Evidence report | `solutions/live-event-launch-planner/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/live-event-launch-planner/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/live-event-launch-planner/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/live-event-launch-planner/quest.html` |
| Literal browser tutorial | `solutions/live-event-launch-planner/manual-tutorial.html` |
| Raw export manifest | `solutions/live-event-launch-planner/export-manifest.json` |
| Source bundle | `solutions/live-event-launch-planner/exports/live-event-launch-planner-source.zip` |
| Manual evidence | `solutions/live-event-launch-planner/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/live-event-launch-planner/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/live-event-launch-planner/exports/live-event-launch-planner-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/live-event-launch-planner/exports/live-event-launch-planner-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/live-event-launch-planner/exports/live-event-launch-planner-solution-export.json` |

**Scaffold status:** 98 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
