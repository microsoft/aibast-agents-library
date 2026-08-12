# Personalized Shopping Assistant solution package

Grounded in the approved **Personalized Shopping Agent** slide and deterministic
`solutions.json` record. This source-assets-only package includes no Studio
project, tutorial, screenshots, capture, or bundle.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/b2c_sales_stacks/personalized_shopping_assistant_stack/personalized_shopping_assistant_agent.py` |
| Deployment recipe | `deployment.json` |
| Source audit | `evals/source-audit.json` |
| Promise map | `evals/onepager-map.json` |
| Manual global instructions | `manual/GLOBAL-INSTRUCTIONS.md` |
| Knowledge and skills | `manual/` |
| Persona-language cases | `tests/demo_cases/personalized-shopping-assistant.json` |

The agent uses synthetic, explicitly provided style preferences and makes draft
recommendations only. It never reserves inventory, applies benefits, returns
items, refunds funds, creates orders, or completes purchases.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/personalized-shopping-assistant/field-guide.html` |
| Evidence report | `solutions/personalized-shopping-assistant/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/personalized-shopping-assistant/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/personalized-shopping-assistant/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/personalized-shopping-assistant/quest.html` |
| Literal browser tutorial | `solutions/personalized-shopping-assistant/manual-tutorial.html` |
| Raw export manifest | `solutions/personalized-shopping-assistant/export-manifest.json` |
| Source bundle | `solutions/personalized-shopping-assistant/exports/personalized-shopping-assistant-source.zip` |
| Manual evidence | `solutions/personalized-shopping-assistant/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/personalized-shopping-assistant/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/personalized-shopping-assistant/exports/personalized-shopping-assistant-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/personalized-shopping-assistant/exports/personalized-shopping-assistant-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/personalized-shopping-assistant/exports/personalized-shopping-assistant-solution-export.json` |

**Scaffold status:** 90 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
