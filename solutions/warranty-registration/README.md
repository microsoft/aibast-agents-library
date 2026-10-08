# Warranty and Registration Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/manufacturing_stacks/warranty_registration_stack/warranty_registration_agent.py` |
| Deployment recipe | `solutions/warranty-registration/deployment.json` |
| Approved-slide map | `solutions/warranty-registration/evals/onepager-map.json` |
| Source audit | `solutions/warranty-registration/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/warranty-registration/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/warranty-registration.json` |
| Synthetic knowledge | `solutions/warranty-registration/manual/knowledge/` |
| Uploadable skills | `solutions/warranty-registration/manual/skills/` |

## Scope

A dealer-facing warranty and registration demonstration over a fixed synthetic snapshot: coverage overview, claim pre-checks, unit records, serial checks, registration drafts and extended-coverage offers, with every claim, registration and offer left for an authorized person to submit.

Implemented operations: `coverage_overview`, `claim_precheck`, `unit_record`, `validate_serial`, `registration_draft`, `extension_offers`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to customer systems or execute external actions. Exact identifiers, dates, names, amounts, scores, and policy values are fictional evidence rather than customer outcomes. Production connections require least-privilege access, approved data handling, and a human authorization gate.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 6 `SKILL.md` files in `manual/skills/`. Bind only approved production connections after security and business-owner review. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/warranty-registration/field-guide.html` |
| Evidence report | `solutions/warranty-registration/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/warranty-registration/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/warranty-registration/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/warranty-registration/quest.html` |
| Literal browser tutorial | `solutions/warranty-registration/manual-tutorial.html` |
| Raw export manifest | `solutions/warranty-registration/export-manifest.json` |
| Source bundle | `solutions/warranty-registration/exports/warranty-registration-source.zip` |
| Manual evidence | `solutions/warranty-registration/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/warranty-registration/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/warranty-registration/exports/warranty-registration-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/warranty-registration/exports/warranty-registration-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/warranty-registration/exports/warranty-registration-solution-export.json` |

**Scaffold status:** 117 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
