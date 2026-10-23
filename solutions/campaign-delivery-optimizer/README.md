# Campaign Delivery Optimizer Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/telecom_media_gaming_stacks/campaign_delivery_optimizer_stack/campaign_delivery_optimizer_agent.py` |
| Deployment recipe | `solutions/campaign-delivery-optimizer/deployment.json` |
| Approved-slide map | `solutions/campaign-delivery-optimizer/evals/onepager-map.json` |
| Source audit | `solutions/campaign-delivery-optimizer/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/campaign-delivery-optimizer/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/campaign-delivery-optimizer.json` |
| Synthetic knowledge | `solutions/campaign-delivery-optimizer/manual/knowledge/` |
| Uploadable skills | `solutions/campaign-delivery-optimizer/manual/skills/` |

## Scope

Help ad sales and ad operations teams keep every advertiser campaign on plan by tracking weekly delivered reach against plan, finding placements with extra reach to close a delivery gap, and drafting the recommendation for the sales lead to approve, while nothing is booked or shared with an advertiser without a person's approval.

Hero scenario: A national media company's ad sales and ad operations teams.

Implemented operations: `campaign_risk`, `available_reach`, `approval_recommendation`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, and statuses are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 3 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/campaign-delivery-optimizer/field-guide.html` |
| Evidence report | `solutions/campaign-delivery-optimizer/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/campaign-delivery-optimizer/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/campaign-delivery-optimizer/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/campaign-delivery-optimizer/quest.html` |
| Literal browser tutorial | `solutions/campaign-delivery-optimizer/manual-tutorial.html` |
| Raw export manifest | `solutions/campaign-delivery-optimizer/export-manifest.json` |
| Source bundle | `solutions/campaign-delivery-optimizer/exports/campaign-delivery-optimizer-source.zip` |
| Manual evidence | `solutions/campaign-delivery-optimizer/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/campaign-delivery-optimizer/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/campaign-delivery-optimizer/exports/campaign-delivery-optimizer-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/campaign-delivery-optimizer/exports/campaign-delivery-optimizer-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/campaign-delivery-optimizer/exports/campaign-delivery-optimizer-solution-export.json` |

**Scaffold status:** 90 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
