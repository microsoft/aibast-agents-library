# Supply Risk Monitoring Agent solution package

| Surface | Location |
| --- | --- |
| Deterministic portable agent | `agents/@aibast-agents-library/manufacturing_stacks/supplier_risk_monitoring_stack/supplier_risk_monitoring_agent.py` |
| Deployment recipe | `solutions/supplier-risk-monitoring/deployment.json` |
| One-pager evidence map | `solutions/supplier-risk-monitoring/evals/onepager-map.json` |
| Source audit | `solutions/supplier-risk-monitoring/evals/source-audit.json` |
| Persona-language cases | `tests/demo_cases/supplier-risk-monitoring.json` |
| Uploadable knowledge | `solutions/supplier-risk-monitoring/manual/knowledge/` |
| Uploadable skills | `solutions/supplier-risk-monitoring/manual/skills/` |

## Pilot scope

This package covers supplier risk dashboard, supplier scorecards, disruption alerts, alternative sourcing review. It uses a fixed fictional snapshot so every identifier, date, quantity, percentage, score, duration, and cost is synthetic pilot evidence rather than a customer result.

## Safety boundary

The local agent is recommendation-only. The agent recommends review options only and never contacts, qualifies, selects, or orders from suppliers. Production action requires the approved systems and authorization controls listed in `deployment.json`.

## One-pager evidence

`evals/onepager-map.json` maps each approved one-pager opportunity statement to deterministic operations and persona-language cases. Promises that imply live monitoring or operational execution are represented as production seams, not as completed local side effects.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload one `SKILL.md` file per operation from `manual/skills/`. Keep the agent in Draft until customer data connections, identity, authorization, review, and audit controls are validated.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/supplier-risk-monitoring/FIELD-GUIDE.md` |
| Guided Easy/Hard quest | `solutions/supplier-risk-monitoring/quest.html` |
| Literal browser tutorial | `solutions/supplier-risk-monitoring/manual-tutorial.html` |
| Raw export manifest | `solutions/supplier-risk-monitoring/export-manifest.json` |
| Source bundle | `solutions/supplier-risk-monitoring/exports/supplier-risk-monitoring-source.zip` |
| Manual evidence | `solutions/supplier-risk-monitoring/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/supplier-risk-monitoring/screenshots/manual/browserfilm.json` |

**Scaffold status:** 60 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
