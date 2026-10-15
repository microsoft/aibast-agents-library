# Public Correspondence Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/slg_government_stacks/public_correspondence_response_stack/public_correspondence_response_agent.py` |
| Deployment recipe | `solutions/public-correspondence-response/deployment.json` |
| Approved-slide map | `solutions/public-correspondence-response/evals/onepager-map.json` |
| Source audit | `solutions/public-correspondence-response/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/public-correspondence-response/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/public-correspondence-response.json` |
| Synthetic knowledge | `solutions/public-correspondence-response/manual/knowledge/` |
| Uploadable skills | `solutions/public-correspondence-response/manual/skills/` |

## Scope

Give correspondence officers one queue for letters, emails, web forms and phone notes, a breakdown of every separate question, cited approved answers, and a clear referral for anything new, while officers stay in control of every reply.

Implemented operations: `inbox_queue`, `break_down_enquiry`, `find_precedents`, `route_and_refer`, `draft_response`, `library_update`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 6 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/public-correspondence-response/field-guide.html` |
| Evidence report | `solutions/public-correspondence-response/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/public-correspondence-response/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/public-correspondence-response/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/public-correspondence-response/quest.html` |
| Literal browser tutorial | `solutions/public-correspondence-response/manual-tutorial.html` |
| Raw export manifest | `solutions/public-correspondence-response/export-manifest.json` |
| Source bundle | `solutions/public-correspondence-response/exports/public-correspondence-response-source.zip` |
| Manual evidence | `solutions/public-correspondence-response/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/public-correspondence-response/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/public-correspondence-response/exports/public-correspondence-response-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/public-correspondence-response/exports/public-correspondence-response-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/public-correspondence-response/exports/public-correspondence-response-solution-export.json` |

**Scaffold status:** 118 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
