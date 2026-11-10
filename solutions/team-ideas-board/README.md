# Team Ideas Board solution package

Built on the Copilot Studio Gallery solution `team-ideas-board` (MIT). Their package stays theirs and unchanged; this is the AIBAST layered version with synthetic data.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/general_stacks/team_ideas_board_stack/team_ideas_board_agent.py` |
| Deployment recipe | `solutions/team-ideas-board/deployment.json` |
| Strict isolated transcripts | `solutions/team-ideas-board/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/team-ideas-board.json` |
| Synthetic knowledge | `solutions/team-ideas-board/manual/knowledge/` |
| Uploadable skills | `solutions/team-ideas-board/manual/skills/` |

## Scope

Help a team keep one shared list of improvement ideas: show the ideas grouped by status, search them, filter them by priority, and check that a new idea uses the board's allowed status and priority before anyone adds it.

Hero scenario: a team with six ideas on its shared list, from a quieter start to Mondays to one place for team decisions.

Implemented operations: `board` and `check`. The package contains two locked persona-language cases and two uploadable skills.

## Approval boundary

This package is synthetic and read-only. It does not add, change or delete an idea on a real list. Every idea is fictional evidence rather than a customer outcome.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload each `SKILL.md` file in `manual/skills/`. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/team-ideas-board/field-guide.html` |
| Evidence report | `solutions/team-ideas-board/evidence-report.html` |
| AIBAST Easy Mode skill | `skills/aibast-easy-mode/SKILL.md` |
| Easy Mode guide | `solutions/team-ideas-board/EASY-MODE.md` |
| Guided Easy/Manual quest | `solutions/team-ideas-board/quest.html` |
| Literal browser tutorial | `solutions/team-ideas-board/manual-tutorial.html` |
| Raw export manifest | `solutions/team-ideas-board/export-manifest.json` |
| Source bundle | [`team-ideas-board-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/team-ideas-board-source.zip) (release asset) |
| Manual evidence | `solutions/team-ideas-board/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/team-ideas-board/screenshots/manual/browserfilm.json` |

**Scaffold status:** 75 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
