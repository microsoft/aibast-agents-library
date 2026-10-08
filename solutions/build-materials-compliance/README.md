# Build Materials Compliance Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/manufacturing_stacks/build_materials_compliance_stack/build_materials_compliance_agent.py` |
| Deployment recipe | `solutions/build-materials-compliance/deployment.json` |
| Approved-slide map | `solutions/build-materials-compliance/evals/onepager-map.json` |
| Source audit | `solutions/build-materials-compliance/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/build-materials-compliance/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/build-materials-compliance.json` |
| Synthetic knowledge | `solutions/build-materials-compliance/manual/knowledge/` |
| Uploadable skills | `solutions/build-materials-compliance/manual/skills/` |

## Scope

Keep grant-funded construction bills of materials compliant every week: flag items that newly fall out of the program's materials sourcing rule with cited evidence, find same-specification compliant alternates, watch vendor certificates, and keep the audit evidence package ready. The hero scenario is Tailspin Civil Works, a fictional infrastructure contractor.

Implemented operations: `weekly_changes`, `compliance_check`, `compliant_alternates`, `vendor_watch`, `audit_evidence`, `action_drafts`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, and rule values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Paste `manual/GLOBAL-INSTRUCTIONS.md` as the agent instructions, upload both Markdown files in `manual/knowledge/`, then upload the 6 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/build-materials-compliance/field-guide.html` |
| Evidence report | `solutions/build-materials-compliance/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/build-materials-compliance/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/build-materials-compliance/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/build-materials-compliance/quest.html` |
| Literal browser tutorial | `solutions/build-materials-compliance/manual-tutorial.html` |
| Raw export manifest | `solutions/build-materials-compliance/export-manifest.json` |
| Source bundle | `solutions/build-materials-compliance/exports/build-materials-compliance-source.zip` |
| Manual evidence | `solutions/build-materials-compliance/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/build-materials-compliance/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/build-materials-compliance/exports/build-materials-compliance-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/build-materials-compliance/exports/build-materials-compliance-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/build-materials-compliance/exports/build-materials-compliance-solution-export.json` |

**Scaffold status:** 118 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
