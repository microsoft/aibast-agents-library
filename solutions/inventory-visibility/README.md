# Inventory Visibility solution package

Grounded in the approved **Inventory Visibility Agent** slide and deterministic
`solutions.json` record. This package contains portable source, knowledge,
skills, and evaluation mapping only—no Studio project, tutorial, screenshots,
capture, or bundle.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/retail_cpg_stacks/inventory_visibility_stack/inventory_visibility_agent.py` |
| Deployment recipe | `deployment.json` |
| Source audit | `evals/source-audit.json` |
| Promise map | `evals/onepager-map.json` |
| Manual global instructions | `manual/GLOBAL-INSTRUCTIONS.md` |
| Knowledge and skills | `manual/` |
| Persona-language cases | `tests/demo_cases/inventory-visibility.json` |

Every quantity is synthetic and read-only. The agent never reserves, transfers,
replenishes, allocates, promises, or purchases inventory.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/inventory-visibility/field-guide.html` |
| Evidence report | `solutions/inventory-visibility/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/inventory-visibility/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/inventory-visibility/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/inventory-visibility/quest.html` |
| Literal browser tutorial | `solutions/inventory-visibility/manual-tutorial.html` |
| Raw export manifest | `solutions/inventory-visibility/export-manifest.json` |
| Source bundle | `solutions/inventory-visibility/exports/inventory-visibility-source.zip` |
| Manual evidence | `solutions/inventory-visibility/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/inventory-visibility/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/inventory-visibility/exports/inventory-visibility-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/inventory-visibility/exports/inventory-visibility-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/inventory-visibility/exports/inventory-visibility-solution-export.json` |

**Scaffold status:** 87 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
