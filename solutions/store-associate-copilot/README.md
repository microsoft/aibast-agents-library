# Retail Store Associate Copilot solution package

Grounded in the approved **Retail Store Associate Copilot** slide and
`solutions.json`. This source-assets-only package intentionally excludes
Copilot Studio projects, tutorials, screenshots, captures, and bundles.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/retail_cpg_stacks/store_associate_copilot_stack/store_associate_copilot_agent.py` |
| Deployment recipe | `deployment.json` |
| Source audit | `evals/source-audit.json` |
| Promise map | `evals/onepager-map.json` |
| Manual global instructions | `manual/GLOBAL-INSTRUCTIONS.md` |
| Knowledge and skills | `manual/` |
| Persona-language cases | `tests/demo_cases/store-associate-copilot.json` |

The agent returns synthetic product snapshots, draft customer language,
planning checklists, and role-cohort coaching signals. It does not reserve
inventory, apply promotions, send messages, process returns, or transact.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/store-associate-copilot/FIELD-GUIDE.md` |
| Guided Easy/Hard quest | `solutions/store-associate-copilot/quest.html` |
| Literal browser tutorial | `solutions/store-associate-copilot/manual-tutorial.html` |
| Raw export manifest | `solutions/store-associate-copilot/export-manifest.json` |
| Source bundle | `solutions/store-associate-copilot/exports/store-associate-copilot-source.zip` |
| Manual evidence | `solutions/store-associate-copilot/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/store-associate-copilot/screenshots/manual/browserfilm.json` |

**Scaffold status:** 60 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
