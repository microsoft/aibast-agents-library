# Supplier Claim Engagement Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/retail_cpg_stacks/supplier_claim_engagement_stack/supplier_claim_engagement_agent.py` |
| Deployment recipe | `solutions/supplier-claim-engagement/deployment.json` |
| Approved-slide map | `solutions/supplier-claim-engagement/evals/onepager-map.json` |
| Source audit | `solutions/supplier-claim-engagement/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/supplier-claim-engagement/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/supplier-claim-engagement.json` |
| Synthetic knowledge | `solutions/supplier-claim-engagement/manual/knowledge/` |
| Uploadable skills | `solutions/supplier-claim-engagement/manual/skills/` |

## Scope

Help retail claims teams recover more from suppliers by triaging damage, shortage, quality, and pricing claims, assembling evidence packs, drafting supplier claim notices, tracking response deadlines, and evaluating supplier responses, while every send, credit acceptance, and escalation stays with an authorized coordinator.

Hero scenario: A regional grocery retailer's supplier claims team at the fictional Fabrikam Grocers.

Implemented operations: `claims_queue`, `triage_claim`, `evidence_pack`, `draft_supplier_claim`, `sla_tracker`, `supplier_response`, `escalation_brief`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, and statuses are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 7 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/supplier-claim-engagement/field-guide.html` |
| Evidence report | `solutions/supplier-claim-engagement/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/supplier-claim-engagement/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/supplier-claim-engagement/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/supplier-claim-engagement/quest.html` |
| Literal browser tutorial | `solutions/supplier-claim-engagement/manual-tutorial.html` |
| Raw export manifest | `solutions/supplier-claim-engagement/export-manifest.json` |
| Source bundle | `solutions/supplier-claim-engagement/exports/supplier-claim-engagement-source.zip` |
| Manual evidence | `solutions/supplier-claim-engagement/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/supplier-claim-engagement/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/supplier-claim-engagement/exports/supplier-claim-engagement-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/supplier-claim-engagement/exports/supplier-claim-engagement-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/supplier-claim-engagement/exports/supplier-claim-engagement-solution-export.json` |

**Scaffold status:** 126 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
