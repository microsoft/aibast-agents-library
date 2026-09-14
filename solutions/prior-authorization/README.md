# Prior Authorization Agent solution package

## Purpose
Give utilization teams a read-only synthetic inventory of request evidence, policy checklist context, recorded workflow state, and reconsideration material—without predicting, submitting, granting, or denying authorization.

## Safety boundary
This customer package is synthetic and read-only. It provides evidence or drafts only: no diagnosis or treatment advice, no eligibility or authorization outcome beyond source evidence, no scheduling, messaging, submission, or record change. Qualified clinical, utilization, quality, or operational reviewers own every downstream decision. Use minimum-necessary information.

## Package map

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/healthcare_stacks/prior_authorization_stack/prior_authorization_agent.py` |
| Deployment recipe | `solutions/prior-authorization/deployment.json` |
| Locked persona cases | `tests/demo_cases/prior-authorization.json` |
| Approved one-pager map | `solutions/prior-authorization/evals/onepager-map.json` |
| Source audit | `solutions/prior-authorization/evals/source-audit.json` |
| Historical isolated source transcripts | `solutions/prior-authorization/evals/transcripts.json` |
| Current native Manual evidence | `solutions/prior-authorization/evals/manual-build-evidence.json` |
| Dated pilot review and prior failures | `solutions/prior-authorization/evals/manual-pilot-review.json` |
| Global instructions | `solutions/prior-authorization/manual/GLOBAL-INSTRUCTIONS.md` |
| Synthetic knowledge | `solutions/prior-authorization/manual/knowledge/` |
| Uploadable operation skills | `solutions/prior-authorization/manual/skills/*/SKILL.md` |

## Operations
- `request_evidence` — Inventories synthetic request evidence without submitting or deciding the request.
- `criteria_evidence` — Presents synthetic checklist items for qualified utilization review.
- `status_summary` — Transcribes a synthetic workflow state without making an authorization outcome.
- `appeal_evidence_packet` — Prepares a minimum-necessary outline without filing or recommending an appeal.

## Package state
- One locked persona case and one uploadable skill exist per operation.
- Exactly two synthetic manual knowledge files are included.
- All four unchanged locked cases passed once each in separate fresh native Preview conversations on the saved/reopened shared-grounding-r4 build using Claude Sonnet 4.6.
- All 18 student checkpoints have personally reviewed reference media. Initial construction, later replacements, persistence checks and final Draft confirmation retain their actual scopes; the reference set is not a continuous fresh-build film.
- Use the seven frozen native inputs and locked cases in the Manual source ZIP with the separately published tutorial. The ZIP is not a standalone guide or native import package.
- Historical source/assisted evidence and the incomplete five-entry native import archive are retained as history, not current Manual acceptance. No live connection, native publication or production certification is claimed.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/prior-authorization/field-guide.html` |
| Evidence report | `solutions/prior-authorization/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/prior-authorization/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/prior-authorization/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/prior-authorization/quest.html` |
| Literal browser tutorial | `solutions/prior-authorization/manual-tutorial.html` |
| Raw export manifest | `solutions/prior-authorization/export-manifest.json` |
| Source bundle | `solutions/prior-authorization/exports/prior-authorization-source.zip` |
| Manual evidence | `solutions/prior-authorization/evals/manual-build-evidence.json` |
| Manual reviewed reference set | `solutions/prior-authorization/screenshots/manual/shared-grounding-r4/browserfilm.json` |
| Historical Copilot Studio solution ZIP — not current source | `solutions/prior-authorization/exports/prior-authorization-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/prior-authorization/exports/prior-authorization-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/prior-authorization/exports/prior-authorization-solution-export.json` |

**Scaffold status:** 78 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation. Resource readiness means file availability, not workshop acceptance. On 2026-09-13, all four unchanged locked prompts passed once each in separate fresh native Preview conversations on one fully saved/reopened r4 Manual build using Claude Sonnet 4.6. The complete policy, all four definitions and both Ready sources matched. All 18 student checkpoints have personally reviewed references with their actual construction, replacement and readback scopes; they are not a continuous fresh-build film. The same agent remained Draft. No native publication, live integration or production certification is claimed.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
