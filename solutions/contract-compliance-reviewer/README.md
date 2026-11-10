# Contract Compliance Reviewer solution package

Built on the Copilot Studio Gallery solution `contract-compliance-reviewer` (MIT). Their package stays theirs and unchanged; this is the AIBAST layered version with synthetic data.

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/professional_services_stacks/contract_compliance_reviewer_stack/contract_compliance_reviewer_agent.py` |
| Deployment recipe | `solutions/contract-compliance-reviewer/deployment.json` |
| Strict isolated transcripts | `solutions/contract-compliance-reviewer/evals/transcripts.json` |
| Persona-language cases | `tests/demo_cases/contract-compliance-reviewer.json` |
| Synthetic knowledge | `solutions/contract-compliance-reviewer/manual/knowledge/` |
| Uploadable skills | `solutions/contract-compliance-reviewer/manual/skills/` |

## Scope

Give a contract a first-pass review for a legal team: find where it contradicts itself, and check it against the organization's contract policies, while every finding stays with a qualified legal professional to confirm.

Hero scenario: Alder Grove Clinics, a fictional group of outpatient clinics, reviewing a supplier services agreement.

Implemented operations: `consistency_review`, `policy_check`. The package contains one locked persona-language case and one uploadable skill for every exposed operation.

## Approval boundary

This package is synthetic and read-only. It does not connect to contract systems, change or sign a contract, or give legal advice. Every identifier, clause and policy is fictional evidence rather than a customer outcome.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the 2 `SKILL.md` files in `manual/skills/`. Keep the agent in Draft and stop before publish until an authorized reviewer validates every operation and guardrail.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/contract-compliance-reviewer/field-guide.html` |
| Evidence report | `solutions/contract-compliance-reviewer/evidence-report.html` |
| AIBAST Easy Mode skill | `skills/aibast-easy-mode/SKILL.md` |
| Easy Mode guide | `solutions/contract-compliance-reviewer/EASY-MODE.md` |
| Guided Easy/Manual quest | `solutions/contract-compliance-reviewer/quest.html` |
| Literal browser tutorial | `solutions/contract-compliance-reviewer/manual-tutorial.html` |
| Raw export manifest | `solutions/contract-compliance-reviewer/export-manifest.json` |
| Source bundle | [`contract-compliance-reviewer-source.zip`](https://github.com/microsoft/aibast-agents-library/releases/download/solution-bundles/contract-compliance-reviewer-source.zip) (release asset) |
| Manual evidence | `solutions/contract-compliance-reviewer/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/contract-compliance-reviewer/screenshots/manual/browserfilm.json` |

**Scaffold status:** 75 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
