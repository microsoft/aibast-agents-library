# Discount Finder Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/general_stacks/procurement_support_stack/procurement_support_agent.py` |
| Deployment recipe | `solutions/procurement-support/deployment.json` |
| Approved-slide map | `solutions/procurement-support/evals/onepager-map.json` |
| Source audit | `solutions/procurement-support/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/procurement-support/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/procurement-support.json` |
| Synthetic knowledge | `solutions/procurement-support/manual/knowledge/` |
| Uploadable skills | `solutions/procurement-support/manual/skills/` |

## Scope

A discount-finder review that surfaces synthetic contract tiers, dated pricing signals, consolidation candidates, and timing tradeoffs without contacting suppliers or placing orders.

Implemented operations: `savings_scan`, `time_sensitive_deals`, `consolidation_analysis`, `purchase_timing`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 4 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/procurement-support/field-guide.html` |
| Evidence report | `solutions/procurement-support/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/procurement-support/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/procurement-support/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/procurement-support/quest.html` |
| Literal browser tutorial | `solutions/procurement-support/manual-tutorial.html` |
| Raw export manifest | `solutions/procurement-support/export-manifest.json` |
| Source bundle | `solutions/procurement-support/exports/procurement-support-source.zip` |
| Manual evidence | `solutions/procurement-support/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/procurement-support/screenshots/manual/browserfilm.json` |

**Scaffold status:** 69 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
