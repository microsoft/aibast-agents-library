# Returns and Complaints Resolution solution package

Grounded in the approved **Returns and Complaints Resolution Agent** slide and
deterministic `solutions.json` record. This source-assets-only package excludes
Studio projects, tutorials, screenshots, captures, and bundles.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/retail_cpg_stacks/returns_complaints_resolution_stack/returns_complaints_resolution_agent.py` |
| Deployment recipe | `deployment.json` |
| Source audit | `evals/source-audit.json` |
| Promise map | `evals/onepager-map.json` |
| Manual global instructions | `manual/GLOBAL-INSTRUCTIONS.md` |
| Knowledge and skills | `manual/` |
| Persona-language cases | `tests/demo_cases/returns-complaints-resolution.json` |

All cases are anonymous and synthetic. The agent drafts review summaries,
classifications, and options only. It never approves or processes a return,
refund, credit, replacement, shipment, reservation, or customer message.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/returns-complaints-resolution/field-guide.html` |
| Evidence report | `solutions/returns-complaints-resolution/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/returns-complaints-resolution/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/returns-complaints-resolution/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/returns-complaints-resolution/quest.html` |
| Literal browser tutorial | `solutions/returns-complaints-resolution/manual-tutorial.html` |
| Raw export manifest | `solutions/returns-complaints-resolution/export-manifest.json` |
| Source bundle | `solutions/returns-complaints-resolution/exports/returns-complaints-resolution-source.zip` |
| Manual evidence | `solutions/returns-complaints-resolution/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/returns-complaints-resolution/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/returns-complaints-resolution/exports/returns-complaints-resolution-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/returns-complaints-resolution/exports/returns-complaints-resolution-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/returns-complaints-resolution/exports/returns-complaints-resolution-solution-export.json` |

**Scaffold status:** 92 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
