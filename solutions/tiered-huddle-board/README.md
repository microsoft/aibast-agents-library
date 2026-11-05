# Tiered Huddle Board Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/healthcare_stacks/tiered_huddle_board_stack/tiered_huddle_board_agent.py` |
| Deployment recipe | `solutions/tiered-huddle-board/deployment.json` |
| Approved-slide map | `solutions/tiered-huddle-board/evals/onepager-map.json` |
| Source audit | `solutions/tiered-huddle-board/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/tiered-huddle-board/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/tiered-huddle-board.json` |
| Synthetic knowledge | `solutions/tiered-huddle-board/manual/knowledge/` |
| Uploadable skills | `solutions/tiered-huddle-board/manual/skills/` |

## Scope

Help a hospital run its daily tiered huddles from one live board: every lane from Tier 1 through the Executive tier with each issue's clock, what is past target and what is waiting on the person asking, an escalation draft that restarts the clock at the next tier's target with the reason the next tier reads first and the people to page by name, a closure check that keeps mitigated issues open until the person who raised them confirms the fix held, and the decisions the 10:30 leadership huddle needs today.

Hero scenario: A community hospital's nurse managers, department directors and leadership team, working one board where Copilot is the conversational surface and Dataverse holds the issues, tiers, clocks and paging roster.

Implemented operations: `board_view`, `escalation_draft`, `closure_check`, `leadership_decisions`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to hospital systems or execute external actions. The hospital, units, issues, people, roles, tickets, clocks and decisions are fictional evidence rather than customer outcomes, and the board holds operational issues, never patient records. Production connections require least-privilege access, approved data handling, and a human confirmation step: the issue owner confirms every escalation, the person who raised an issue confirms every closure, and the leadership huddle records every decision.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 4 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/tiered-huddle-board/field-guide.html` |
| Evidence report | `solutions/tiered-huddle-board/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/tiered-huddle-board/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/tiered-huddle-board/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/tiered-huddle-board/quest.html` |
| Literal browser tutorial | `solutions/tiered-huddle-board/manual-tutorial.html` |
| Raw export manifest | `solutions/tiered-huddle-board/export-manifest.json` |
| Source bundle | [`tiered-huddle-board-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/tiered-huddle-board-source.zip) (release asset) |
| Manual evidence | `solutions/tiered-huddle-board/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/tiered-huddle-board/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/tiered-huddle-board/exports/tiered-huddle-board-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/tiered-huddle-board/exports/tiered-huddle-board-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/tiered-huddle-board/exports/tiered-huddle-board-solution-export.json` |

**Scaffold status:** 98 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
