# Building Permit Processing solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/slg_government_stacks/building_permit_processing_stack/building_permit_processing_agent.py` |
| Hand-authored catalog copy | `solutions/catalog.json` |
| Deployment recipe | `solutions/building-permit-processing/deployment.json` |
| Guided field quest | `solutions/building-permit-processing/quest.html` |
| Manual build tutorial | `solutions/building-permit-processing/manual-tutorial.html` |
| Raw export manifest | `solutions/building-permit-processing/export-manifest.json` |
| Complete source bundle | `solutions/building-permit-processing/exports/building-permit-processing-source.zip` |
| Copilot Studio source | `solutions/building-permit-processing/copilot-studio/` |
| Uploadable manual skills | `solutions/building-permit-processing/manual/skills/` |
| Live behavior gate | `tests/demo_cases/building-permit-processing.json` |
| Isolated Brainstem proof | `solutions/building-permit-processing/evals/transcripts.json` |
| Copilot Studio proof | `solutions/building-permit-processing/evals/copilot-studio-transcripts.json` |
| Manual Preview proof | `solutions/building-permit-processing/evals/manual-build-evidence.json` |
| Deployment evidence | `solutions/building-permit-processing/evals/deployment-evidence.json` |
| PowerPoint evidence | `state/onepager_content.json` |
| Shared demo player | `solutions/_shared/m365-copilot-demo.html` |

## Required proof

The one-pager advertises intake validation, review routing, applicant updates,
and inspector access. Each promise must pass through the isolated Brainstem
before a canonical transcript is accepted under `evals/`.

Copilot Studio deployment is blocked until the exact transcript corpus passes
again in the target environment.

## Pilot status

- Fresh global Brainstem install: passed
- Isolated source-agent cases: 5/5 passed
- Copilot Studio project push to kodyv8: passed
- Copilot Studio published runtime cases: 5/5 passed
- Copilot-assisted walkthrough: 8 real browser frames
- Manual AI-skeptic walkthrough: 24 real browser frames and Preview parity
- Manual duplicate agent: Draft by design; not published
- Public-main no-terminal recipe: must be rerun after these package paths and
  fixed agent source are merged

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/building-permit-processing/field-guide.html` |
| Evidence report | `solutions/building-permit-processing/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/building-permit-processing/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/building-permit-processing/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/building-permit-processing/quest.html` |
| Literal browser tutorial | `solutions/building-permit-processing/manual-tutorial.html` |
| Raw export manifest | `solutions/building-permit-processing/export-manifest.json` |
| Source bundle | `solutions/building-permit-processing/exports/building-permit-processing-source.zip` |
| Manual evidence | `solutions/building-permit-processing/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/building-permit-processing/screenshots/manual/browserfilm.json` |

**Scaffold status:** 82 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
