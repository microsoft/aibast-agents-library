# Customer Sentiment and Churn Prediction Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/customer_sentiment_churn_stack/customer_sentiment_churn_agent.py` |
| Deployment recipe | `solutions/customer-sentiment-churn/deployment.json` |
| Locked behavior cases | `tests/demo_cases/customer-sentiment-churn.json` |
| Approved one-pager map | `solutions/customer-sentiment-churn/evals/onepager-map.json` |
| Source capability audit | `solutions/customer-sentiment-churn/evals/source-audit.json` |
| Strict-isolation transcripts | `solutions/customer-sentiment-churn/evals/transcripts.json` |
| Uploadable synthetic knowledge | `solutions/customer-sentiment-churn/manual/knowledge/` |
| Uploadable operation skills | `solutions/customer-sentiment-churn/manual/skills/` |

## Implemented scope

- `sentiment_dashboard` — Cross-channel sentiment view.
- `churn_prediction` — Churn-review prioritization.
- `retention_actions` — Retention option preparation.
- `segment_analysis` — Segment context.

## Evidence and safety boundary

The approved one-pager `37. Customer Sentiment and Churn Prediction Agent one-pager.pptx` is the evidence source for this package. Each advertised promise maps to source behavior and locked persona-language cases in `evals/onepager-map.json`. All records, identifiers, dates, amounts, scores, statuses, and outcomes are synthetic.

This package provides decision support only. It gives no legal, regulatory, insurance, lending, tax, investment, or financial advice; makes no approval or transaction claim; and requires explicit authorized human review before any external action.

## Manual Copilot Studio preparation

Upload the two Markdown files in `manual/knowledge/`, then upload one `SKILL.md` for each of the 4 operations in `manual/skills/`. Bind only approved least-privilege connections. Validate all locked cases and stop before publish. No Copilot Studio project, tutorial, screenshot, or bundle is included.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/customer-sentiment-churn/field-guide.html` |
| Evidence report | `solutions/customer-sentiment-churn/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/customer-sentiment-churn/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/customer-sentiment-churn/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/customer-sentiment-churn/quest.html` |
| Literal browser tutorial | `solutions/customer-sentiment-churn/manual-tutorial.html` |
| Raw export manifest | `solutions/customer-sentiment-churn/export-manifest.json` |
| Source bundle | `solutions/customer-sentiment-churn/exports/customer-sentiment-churn-source.zip` |
| Manual evidence | `solutions/customer-sentiment-churn/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/customer-sentiment-churn/screenshots/manual/browserfilm.json` |

**Scaffold status:** 69 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
