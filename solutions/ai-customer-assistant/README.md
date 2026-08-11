# Customer Escalations Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/general_stacks/ai_customer_assistant_stack/ai_customer_assistant_agent.py` |
| Deployment recipe | `solutions/ai-customer-assistant/deployment.json` |
| Approved-slide map | `solutions/ai-customer-assistant/evals/onepager-map.json` |
| Source audit | `solutions/ai-customer-assistant/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/ai-customer-assistant/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/ai-customer-assistant.json` |
| Synthetic knowledge | `solutions/ai-customer-assistant/manual/knowledge/` |
| Uploadable skills | `solutions/ai-customer-assistant/manual/skills/` |

## Scope

A read-only customer-escalation briefing that joins fictional case, knowledge, routing, and satisfaction evidence without sending a message or changing a case.

Implemented operations: `handle_inquiry`, `knowledge_search`, `escalation_routing`, `satisfaction_survey`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## No-install first look

Non-technical sellers can begin with the
[10-minute no-install preview](FIELD-GUIDE.md#start-here--10-minute-no-install-preview).
It surfaces one approved Copilot Studio screenshot for each locked case, the
exact `must_include`/`must_not_include` validation log, and a real Draft
confirmation. This path is read-only evidence review; it is not a hosted
sandbox, live deployment, or customer proof.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 4 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/ai-customer-assistant/field-guide.html` |
| Evidence report | `solutions/ai-customer-assistant/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/ai-customer-assistant/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/ai-customer-assistant/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/ai-customer-assistant/quest.html` |
| Literal browser tutorial | `solutions/ai-customer-assistant/manual-tutorial.html` |
| Raw export manifest | `solutions/ai-customer-assistant/export-manifest.json` |
| Source bundle | `solutions/ai-customer-assistant/exports/ai-customer-assistant-source.zip` |
| Manual evidence | `solutions/ai-customer-assistant/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/ai-customer-assistant/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/ai-customer-assistant/exports/ai-customer-assistant-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/ai-customer-assistant/exports/ai-customer-assistant-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/ai-customer-assistant/exports/ai-customer-assistant-solution-export.json` |

**Scaffold status:** 93 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
