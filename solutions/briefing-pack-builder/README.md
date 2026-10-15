# Briefing Pack Builder Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/slg_government_stacks/briefing_pack_builder_stack/briefing_pack_builder_agent.py` |
| Deployment recipe | `solutions/briefing-pack-builder/deployment.json` |
| Approved-slide map | `solutions/briefing-pack-builder/evals/onepager-map.json` |
| Source audit | `solutions/briefing-pack-builder/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/briefing-pack-builder/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/briefing-pack-builder.json` |
| Synthetic knowledge | `solutions/briefing-pack-builder/manual/knowledge/` |
| Uploadable skills | `solutions/briefing-pack-builder/manual/skills/` |

## Scope

A government briefing demonstration over a fixed synthetic content set: briefing formats, content scan, figure check, cited draft brief, gap report and approval route, with every figure confirmation, review and sign-off left to officers.

Implemented operations: `list_templates`, `content_scan`, `figure_check`, `draft_brief`, `gap_report`, `approval_route`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 6 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/briefing-pack-builder/field-guide.html` |
| Evidence report | `solutions/briefing-pack-builder/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/briefing-pack-builder/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/briefing-pack-builder/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/briefing-pack-builder/quest.html` |
| Literal browser tutorial | `solutions/briefing-pack-builder/manual-tutorial.html` |
| Raw export manifest | `solutions/briefing-pack-builder/export-manifest.json` |
| Source bundle | `solutions/briefing-pack-builder/exports/briefing-pack-builder-source.zip` |
| Manual evidence | `solutions/briefing-pack-builder/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/briefing-pack-builder/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/briefing-pack-builder/exports/briefing-pack-builder-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/briefing-pack-builder/exports/briefing-pack-builder-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/briefing-pack-builder/exports/briefing-pack-builder-solution-export.json` |

**Scaffold status:** 118 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
