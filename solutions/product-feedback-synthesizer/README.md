# Product Feedback Synthesizer Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/software_dp_stacks/product_feedback_synthesizer_stack/product_feedback_synthesizer_agent.py` |
| Deployment recipe | `solutions/product-feedback-synthesizer/deployment.json` |
| Approved-slide map | `solutions/product-feedback-synthesizer/evals/onepager-map.json` |
| Source audit | `solutions/product-feedback-synthesizer/evals/source-audit.json` |
| Persona-language cases | `tests/demo_cases/product-feedback-synthesizer.json` |
| Synthetic knowledge | `solutions/product-feedback-synthesizer/manual/knowledge/` |
| Uploadable skills | `solutions/product-feedback-synthesizer/manual/skills/` |

## Scope

A synthetic feedback synthesis surface that organizes channels, sentiment, requests, and impact signals as review candidates without creating tickets or making roadmap commitments.

Implemented operations: `feedback_summary`, `feature_requests`, `sentiment_analysis`, `roadmap_impact`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 4 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/product-feedback-synthesizer/field-guide.html` |
| Evidence report | `solutions/product-feedback-synthesizer/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/product-feedback-synthesizer/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/product-feedback-synthesizer/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/product-feedback-synthesizer/quest.html` |
| Literal browser tutorial | `solutions/product-feedback-synthesizer/manual-tutorial.html` |
| Raw export manifest | `solutions/product-feedback-synthesizer/export-manifest.json` |
| Source bundle | `solutions/product-feedback-synthesizer/exports/product-feedback-synthesizer-source.zip` |
| Manual evidence | `solutions/product-feedback-synthesizer/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/product-feedback-synthesizer/screenshots/manual/browserfilm.json` |

**Scaffold status:** 69 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
