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

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 4 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/ai-customer-assistant/FIELD-GUIDE.md` |
| Guided Easy/Hard quest | `solutions/ai-customer-assistant/quest.html` |
| Literal browser tutorial | `solutions/ai-customer-assistant/manual-tutorial.html` |
| Raw export manifest | `solutions/ai-customer-assistant/export-manifest.json` |
| Source bundle | `solutions/ai-customer-assistant/exports/ai-customer-assistant-source.zip` |
| Manual evidence | `solutions/ai-customer-assistant/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/ai-customer-assistant/screenshots/manual/browserfilm.json` |

**Scaffold status:** 61 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
