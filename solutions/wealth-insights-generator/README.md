# Wealth Insights Generator Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/wealth_insights_generator_stack/wealth_insights_generator_agent.py` |
| Deployment recipe | `solutions/wealth-insights-generator/deployment.json` |
| Locked behavior cases | `tests/demo_cases/wealth-insights-generator.json` |
| Approved one-pager map | `solutions/wealth-insights-generator/evals/onepager-map.json` |
| Source capability audit | `solutions/wealth-insights-generator/evals/source-audit.json` |
| Strict-isolation transcripts | `solutions/wealth-insights-generator/evals/transcripts.json` |
| Uploadable synthetic knowledge | `solutions/wealth-insights-generator/manual/knowledge/` |
| Uploadable operation skills | `solutions/wealth-insights-generator/manual/skills/` |

## Implemented scope

- `market_brief` — Fixed market snapshot.
- `client_insights` — Unified wealth insights.
- `opportunity_alerts` — Planning-gap signals.
- `performance_attribution` — Performance context.
- `meeting_brief` — Advisor meeting preparation.

## Evidence and safety boundary

The approved one-pager `42. Wealth Insights Generator Agent one-pager.pptx` is the evidence source for this package. Each advertised promise maps to source behavior and locked persona-language cases in `evals/onepager-map.json`. All records, identifiers, dates, amounts, scores, statuses, and outcomes are synthetic.

This package provides decision support only. It gives no legal, regulatory, insurance, lending, tax, investment, or financial advice; makes no approval or transaction claim; and requires explicit authorized human review before any external action.

## Manual Copilot Studio preparation

Upload the two Markdown files in `manual/knowledge/`, then upload one `SKILL.md` for each of the 5 operations in `manual/skills/`. Bind only approved least-privilege connections. Validate all locked cases and stop before publish. No Copilot Studio project, tutorial, screenshot, or bundle is included.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/wealth-insights-generator/field-guide.html` |
| Evidence report | `solutions/wealth-insights-generator/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/wealth-insights-generator/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/wealth-insights-generator/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/wealth-insights-generator/quest.html` |
| Literal browser tutorial | `solutions/wealth-insights-generator/manual-tutorial.html` |
| Raw export manifest | `solutions/wealth-insights-generator/export-manifest.json` |
| Source bundle | `solutions/wealth-insights-generator/exports/wealth-insights-generator-source.zip` |
| Manual evidence | `solutions/wealth-insights-generator/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/wealth-insights-generator/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/wealth-insights-generator/exports/wealth-insights-generator-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/wealth-insights-generator/exports/wealth-insights-generator-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/wealth-insights-generator/exports/wealth-insights-generator-solution-export.json` |

**Scaffold status:** 91 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
