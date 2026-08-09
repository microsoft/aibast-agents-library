# Financial Advisor Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/financial_advisor_copilot_stack/financial_advisor_copilot_agent.py` |
| Deployment recipe | `solutions/financial-advisor-copilot/deployment.json` |
| Locked behavior cases | `tests/demo_cases/financial-advisor-copilot.json` |
| Approved one-pager map | `solutions/financial-advisor-copilot/evals/onepager-map.json` |
| Source capability audit | `solutions/financial-advisor-copilot/evals/source-audit.json` |
| Strict-isolation transcripts | `solutions/financial-advisor-copilot/evals/transcripts.json` |
| Uploadable synthetic knowledge | `solutions/financial-advisor-copilot/manual/knowledge/` |
| Uploadable operation skills | `solutions/financial-advisor-copilot/manual/skills/` |

## Implemented scope

- `service_intake` — Service intake and routing.
- `client_review` — Client review.
- `portfolio_summary` — Portfolio context.
- `recommendation_engine` — Advisor-review considerations.
- `compliance_check` — Compliance checkpoints.
- `advisor_handoff` — Banker-to-advisor handoff.

## Evidence and safety boundary

The approved one-pager `50. Financial Advisor Agent one-pager.pptx` is the evidence source for this package. Each advertised promise maps to source behavior and locked persona-language cases in `evals/onepager-map.json`. All records, identifiers, dates, amounts, scores, statuses, and outcomes are synthetic.

This package provides decision support only. It gives no legal, regulatory, insurance, lending, tax, investment, or financial advice; makes no approval or transaction claim; and requires explicit authorized human review before any external action.

## Manual Copilot Studio preparation

Upload the two Markdown files in `manual/knowledge/`, then upload one `SKILL.md` for each of the 6 operations in `manual/skills/`. Bind only approved least-privilege connections. Validate all locked cases and stop before publish. No Copilot Studio project, tutorial, screenshot, or bundle is included.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/financial-advisor-copilot/FIELD-GUIDE.md` |
| Guided Easy/Hard quest | `solutions/financial-advisor-copilot/quest.html` |
| Literal browser tutorial | `solutions/financial-advisor-copilot/manual-tutorial.html` |
| Raw export manifest | `solutions/financial-advisor-copilot/export-manifest.json` |
| Source bundle | `solutions/financial-advisor-copilot/exports/financial-advisor-copilot-source.zip` |
| Manual evidence | `solutions/financial-advisor-copilot/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/financial-advisor-copilot/screenshots/manual/browserfilm.json` |

**Scaffold status:** 70 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
