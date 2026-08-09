# Portfolio Rebalancing Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/portfolio_rebalancing_stack/portfolio_rebalancing_agent.py` |
| Deployment recipe | `solutions/portfolio-rebalancing/deployment.json` |
| Locked behavior cases | `tests/demo_cases/portfolio-rebalancing.json` |
| Approved one-pager map | `solutions/portfolio-rebalancing/evals/onepager-map.json` |
| Source capability audit | `solutions/portfolio-rebalancing/evals/source-audit.json` |
| Strict-isolation transcripts | `solutions/portfolio-rebalancing/evals/transcripts.json` |
| Uploadable synthetic knowledge | `solutions/portfolio-rebalancing/manual/knowledge/` |
| Uploadable operation skills | `solutions/portfolio-rebalancing/manual/skills/` |

## Implemented scope

- `portfolio_analysis` — Portfolio drift analysis.
- `rebalance_recommendation` — Rebalancing candidates.
- `tax_impact` — Illustrative tax impact.
- `tax_loss_harvest` — Tax-loss-harvesting candidates.
- `retirement_scenario` — Retirement scenario inputs.
- `execution_plan` — Human-controlled implementation checklist.

## Evidence and safety boundary

The approved one-pager `Portfolio Rebalancing Agent one-pager.pptx` is the evidence source for this package. Each advertised promise maps to source behavior and locked persona-language cases in `evals/onepager-map.json`. All records, identifiers, dates, amounts, scores, statuses, and outcomes are synthetic.

This package provides decision support only. It gives no legal, regulatory, insurance, lending, tax, investment, or financial advice; makes no approval or transaction claim; and requires explicit authorized human review before any external action.

## Manual Copilot Studio preparation

Upload the two Markdown files in `manual/knowledge/`, then upload one `SKILL.md` for each of the 6 operations in `manual/skills/`. Bind only approved least-privilege connections. Validate all locked cases and stop before publish. No Copilot Studio project, tutorial, screenshot, or bundle is included.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/portfolio-rebalancing/FIELD-GUIDE.md` |
| Guided Easy/Hard quest | `solutions/portfolio-rebalancing/quest.html` |
| Literal browser tutorial | `solutions/portfolio-rebalancing/manual-tutorial.html` |
| Raw export manifest | `solutions/portfolio-rebalancing/export-manifest.json` |
| Source bundle | `solutions/portfolio-rebalancing/exports/portfolio-rebalancing-source.zip` |
| Manual evidence | `solutions/portfolio-rebalancing/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/portfolio-rebalancing/screenshots/manual/browserfilm.json` |

**Scaffold status:** 70 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
