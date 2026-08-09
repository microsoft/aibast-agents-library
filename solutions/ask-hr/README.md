# Ask HR Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/human_resources_stacks/ask_hr_stack/ask_hr_agent.py` |
| Deployment recipe | `solutions/ask-hr/deployment.json` |
| Approved-slide map | `solutions/ask-hr/evals/onepager-map.json` |
| Source audit | `solutions/ask-hr/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/ask-hr/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/ask-hr.json` |
| Synthetic knowledge | `solutions/ask-hr/manual/knowledge/` |
| Uploadable skills | `solutions/ask-hr/manual/skills/` |

## Scope

A privacy-conscious HR self-service demonstration for fictional balances and published policy examples, with draft previews and mandatory human review for eligibility or transactions.

Implemented operations: `leave_balance`, `submit_time_off`, `parental_leave`, `health_insurance`, `remote_work`, `benefits_summary`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 6 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/ask-hr/field-guide.html` |
| Evidence report | `solutions/ask-hr/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/ask-hr/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/ask-hr/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/ask-hr/quest.html` |
| Literal browser tutorial | `solutions/ask-hr/manual-tutorial.html` |
| Raw export manifest | `solutions/ask-hr/export-manifest.json` |
| Source bundle | `solutions/ask-hr/exports/ask-hr-source.zip` |
| Manual evidence | `solutions/ask-hr/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/ask-hr/screenshots/manual/browserfilm.json` |

**Scaffold status:** 80 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
