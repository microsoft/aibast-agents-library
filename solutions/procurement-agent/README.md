# Procurement Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/general_stacks/procurement_agent_stack/procurement_agent.py` |
| Deployment recipe | `solutions/procurement-agent/deployment.json` |
| Approved-slide map | `solutions/procurement-agent/evals/onepager-map.json` |
| Source audit | `solutions/procurement-agent/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/procurement-agent/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/procurement-agent.json` |
| Synthetic knowledge | `solutions/procurement-agent/manual/knowledge/` |
| Uploadable skills | `solutions/procurement-agent/manual/skills/` |

## Scope

A synthetic purchasing review surface for requests, vendor evidence, approval thresholds, and spend controls that never creates a PO or commits a supplier.

Implemented operations: `purchase_request`, `vendor_comparison`, `approval_routing`, `spend_analysis`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 4 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/procurement-agent/FIELD-GUIDE.md` |
| Guided Easy/Hard quest | `solutions/procurement-agent/quest.html` |
| Literal browser tutorial | `solutions/procurement-agent/manual-tutorial.html` |
| Raw export manifest | `solutions/procurement-agent/export-manifest.json` |
| Source bundle | `solutions/procurement-agent/exports/procurement-agent-source.zip` |
| Manual evidence | `solutions/procurement-agent/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/procurement-agent/screenshots/manual/browserfilm.json` |

**Scaffold status:** 60 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
