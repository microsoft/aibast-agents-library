# Fraud Detection and Alert Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/fraud_detection_alert_stack/fraud_detection_alert_agent.py` |
| Deployment recipe | `solutions/fraud-detection-alert/deployment.json` |
| Locked behavior cases | `tests/demo_cases/fraud-detection-alert.json` |
| Approved one-pager map | `solutions/fraud-detection-alert/evals/onepager-map.json` |
| Source capability audit | `solutions/fraud-detection-alert/evals/source-audit.json` |
| Strict-isolation transcripts | `solutions/fraud-detection-alert/evals/transcripts.json` |
| Uploadable synthetic knowledge | `solutions/fraud-detection-alert/manual/knowledge/` |
| Uploadable operation skills | `solutions/fraud-detection-alert/manual/skills/` |

## Implemented scope

- `alert_triage` — Alert triage.
- `transaction_analysis` — Transaction evidence review.
- `pattern_detection` — Fraud-pattern hypotheses.
- `investigation_summary` — Case preparation and routing.

## Evidence and safety boundary

The approved one-pager `38. Fraud Detection and Alert Agent one-pager.pptx` is the evidence source for this package. Each advertised promise maps to source behavior and locked persona-language cases in `evals/onepager-map.json`. All records, identifiers, dates, amounts, scores, statuses, and outcomes are synthetic.

This package provides decision support only. It gives no legal, regulatory, insurance, lending, tax, investment, or financial advice; makes no approval or transaction claim; and requires explicit authorized human review before any external action.

## Manual Copilot Studio preparation

Upload the two Markdown files in `manual/knowledge/`, then upload one `SKILL.md` for each of the 4 operations in `manual/skills/`. Bind only approved least-privilege connections. Validate all locked cases and stop before publish. No Copilot Studio project, tutorial, screenshot, or bundle is included.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/fraud-detection-alert/FIELD-GUIDE.md` |
| Guided Easy/Hard quest | `solutions/fraud-detection-alert/quest.html` |
| Literal browser tutorial | `solutions/fraud-detection-alert/manual-tutorial.html` |
| Raw export manifest | `solutions/fraud-detection-alert/export-manifest.json` |
| Source bundle | `solutions/fraud-detection-alert/exports/fraud-detection-alert-source.zip` |
| Manual evidence | `solutions/fraud-detection-alert/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/fraud-detection-alert/screenshots/manual/browserfilm.json` |

**Scaffold status:** 60 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
