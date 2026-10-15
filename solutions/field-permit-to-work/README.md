# Field Permit to Work Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/energy_stacks/field_permit_to_work_stack/field_permit_to_work_agent.py` |
| Deployment recipe | `solutions/field-permit-to-work/deployment.json` |
| Approved-slide map | `solutions/field-permit-to-work/evals/onepager-map.json` |
| Source audit | `solutions/field-permit-to-work/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/field-permit-to-work/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/field-permit-to-work.json` |
| Synthetic knowledge | `solutions/field-permit-to-work/manual/knowledge/` |
| Uploadable skills | `solutions/field-permit-to-work/manual/skills/` |

## Scope

Give permit coordinators and authorized persons a drafted risk assessment, an isolation check against the live switching state, visible sign-off timing, crew acknowledgements and close-out reconciliation, while every safety decision stays with authorized people.

Implemented operations: `permit_queue`, `risk_assessment`, `isolation_check`, `authorization_route`, `crew_briefing`, `clearance_check`, `safety_kpis`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 7 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/field-permit-to-work/field-guide.html` |
| Evidence report | `solutions/field-permit-to-work/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/field-permit-to-work/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/field-permit-to-work/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/field-permit-to-work/quest.html` |
| Literal browser tutorial | `solutions/field-permit-to-work/manual-tutorial.html` |
| Raw export manifest | `solutions/field-permit-to-work/export-manifest.json` |
| Source bundle | `solutions/field-permit-to-work/exports/field-permit-to-work-source.zip` |
| Manual evidence | `solutions/field-permit-to-work/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/field-permit-to-work/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/field-permit-to-work/exports/field-permit-to-work-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/field-permit-to-work/exports/field-permit-to-work-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/field-permit-to-work/exports/field-permit-to-work-solution-export.json` |

**Scaffold status:** 126 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
