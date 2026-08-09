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
