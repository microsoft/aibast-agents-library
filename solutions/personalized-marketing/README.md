# Personalized Marketing solution package

This lightweight package is grounded in the approved **Personalized Marketing
Agent** one-pager and the deterministic `solutions.json` record. It contains no
Copilot Studio project, tutorial, screenshots, transcript capture, or bundle.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/retail_cpg_stacks/personalized_marketing_stack/personalized_marketing_agent.py` |
| Deployment recipe | `deployment.json` |
| Source audit | `evals/source-audit.json` |
| One-pager promise map | `evals/onepager-map.json` |
| Manual global instructions | `manual/GLOBAL-INSTRUCTIONS.md` |
| Synthetic knowledge | `manual/knowledge/` |
| Uploadable operation skills | `manual/skills/` |
| Persona-language cases | `tests/demo_cases/personalized-marketing.json` |

## Safety boundary

The agent uses aggregate synthetic commercial signals and excludes demographic
attributes. It produces review-ready segments, campaign concepts, content
drafts, and measurement scenarios only. It never sends a message, creates an
offer, launches a campaign, issues a reward, or completes a purchase.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/personalized-marketing/FIELD-GUIDE.md` |
| Guided Easy/Hard quest | `solutions/personalized-marketing/quest.html` |
| Literal browser tutorial | `solutions/personalized-marketing/manual-tutorial.html` |
| Raw export manifest | `solutions/personalized-marketing/export-manifest.json` |
| Source bundle | `solutions/personalized-marketing/exports/personalized-marketing-source.zip` |
| Manual evidence | `solutions/personalized-marketing/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/personalized-marketing/screenshots/manual/browserfilm.json` |

**Scaffold status:** 60 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
