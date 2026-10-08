# Benefits Enrollment Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/human_resources_stacks/benefits_enrollment_assistant_stack/benefits_enrollment_assistant_agent.py` |
| Deployment recipe | `solutions/benefits-enrollment-assistant/deployment.json` |
| Approved-slide map | `solutions/benefits-enrollment-assistant/evals/onepager-map.json` |
| Source audit | `solutions/benefits-enrollment-assistant/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/benefits-enrollment-assistant/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/benefits-enrollment-assistant.json` |
| Synthetic knowledge | `solutions/benefits-enrollment-assistant/manual/knowledge/` |
| Uploadable skills | `solutions/benefits-enrollment-assistant/manual/skills/` |

## Scope

Guide employees through open enrollment and life-event benefit changes by explaining the enrollment window and change rules, comparing plan costs for their coverage tier, checking whether their providers are in network, tracking required documents, and preparing a draft election, while eligibility decisions and submissions stay with the employee and benefits staff.

Hero scenario: A mid-size employer's benefits team during open enrollment at the fictional Tailwind Traders.

Implemented operations: `enrollment_window`, `life_event_change`, `compare_plans`, `provider_network`, `document_checklist`, `election_draft`, `deadline_reminders`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, and statuses are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 7 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/benefits-enrollment-assistant/field-guide.html` |
| Evidence report | `solutions/benefits-enrollment-assistant/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/benefits-enrollment-assistant/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/benefits-enrollment-assistant/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/benefits-enrollment-assistant/quest.html` |
| Literal browser tutorial | `solutions/benefits-enrollment-assistant/manual-tutorial.html` |
| Raw export manifest | `solutions/benefits-enrollment-assistant/export-manifest.json` |
| Source bundle | `solutions/benefits-enrollment-assistant/exports/benefits-enrollment-assistant-source.zip` |
| Manual evidence | `solutions/benefits-enrollment-assistant/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/benefits-enrollment-assistant/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/benefits-enrollment-assistant/exports/benefits-enrollment-assistant-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/benefits-enrollment-assistant/exports/benefits-enrollment-assistant-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/benefits-enrollment-assistant/exports/benefits-enrollment-assistant-solution-export.json` |

**Scaffold status:** 126 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
