# Financial Regulatory Compliance solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/regulatory_compliance_fs_stack/regulatory_compliance_fs_agent.py` |
| Hand-authored catalog copy | `solutions/catalog.json` |
| Deployment recipe | `solutions/fs-regulatory-compliance/deployment.json` |
| Live behavior gate | `tests/demo_cases/fs-regulatory-compliance.json` |
| PowerPoint evidence | `state/onepager_content.json` |
| Source audit | `solutions/fs-regulatory-compliance/evals/source-audit.json` |
| Canonical transcripts | `solutions/fs-regulatory-compliance/evals/transcripts.json` |
| Copilot Studio Preview evidence | `solutions/fs-regulatory-compliance/evals/copilot-studio-preview-evidence.json` |
| Copilot Studio source | `solutions/fs-regulatory-compliance/copilot-studio/` |
| Customer field guide | `solutions/fs-regulatory-compliance/FIELD-GUIDE.md` |
| Easy/Manual quest | `solutions/fs-regulatory-compliance/quest.html` |
| Manual browser tutorial | `solutions/fs-regulatory-compliance/manual-tutorial.html` |
| Export manifest | `solutions/fs-regulatory-compliance/export-manifest.json` |
| Manual knowledge | `solutions/fs-regulatory-compliance/manual/knowledge/` |
| Manual skills | `solutions/fs-regulatory-compliance/manual/skills/` |
| Manual evidence | `solutions/fs-regulatory-compliance/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/fs-regulatory-compliance/screenshots/manual/manual-build-walkthrough.gif` |
| Copilot-assisted browserfilm | `solutions/fs-regulatory-compliance/screenshots/assisted/copilot-assisted-walkthrough.gif` |

## Pilot scope

This package demonstrates five implemented workflows:

1. whole-desk compliance readiness;
2. transaction-reporting and best-execution surveillance;
3. algorithm-documentation review;
4. correction and submission preparation with an approval gate; and
5. trader-certification tracking and enrollment planning.

The local agent uses fictional records and relative dates so it runs without
customer systems. The manual knowledge files freeze the canonical
2026-08-07 snapshot used by the captured transcripts.

## Required proof

The approved one-pager advertises automated monitoring, documentation review,
remediation, reporting, and certification readiness. Each promise is mapped to
source behavior and at least one locked case under `evals/onepager-map.json`.
All five cases were captured with only `FSRegulatoryCompliance` discoverable.

Published value claims remain qualitative. Exact identifiers, dates,
percentages, notionals, and counts in this package are synthetic demo evidence,
not customer outcomes or regulatory advice.

## Manual Copilot Studio preparation

Upload both Markdown files in `manual/knowledge/`, then upload the five
`SKILL.md` files in `manual/skills/`. The recommended production pattern adds
approved order-management, reporting-mechanism, learning-management, and
Microsoft Teams connections. The Easy and manual Copilot Studio agents are initialized, validated in
Preview, and remain Draft.

The manual tutorial contains 26 captured browser actions and five passing
Preview cases for `Regulatory Manual Build`.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/fs-regulatory-compliance/field-guide.html` |
| Evidence report | `solutions/fs-regulatory-compliance/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/fs-regulatory-compliance/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/fs-regulatory-compliance/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/fs-regulatory-compliance/quest.html` |
| Literal browser tutorial | `solutions/fs-regulatory-compliance/manual-tutorial.html` |
| Raw export manifest | `solutions/fs-regulatory-compliance/export-manifest.json` |
| Source bundle | `solutions/fs-regulatory-compliance/exports/fs-regulatory-compliance-source.zip` |
| Manual evidence | `solutions/fs-regulatory-compliance/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/fs-regulatory-compliance/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/fs-regulatory-compliance/exports/fs-regulatory-compliance-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/fs-regulatory-compliance/exports/fs-regulatory-compliance-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/fs-regulatory-compliance/exports/fs-regulatory-compliance-solution-export.json` |

**Scaffold status:** 114 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
