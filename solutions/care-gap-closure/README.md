# Care Gap Closure Agent solution package

## Purpose
Help quality and care-coordination teams inspect synthetic measure evidence, organize operational review cohorts, and draft unsent outreach while preserving clinical eligibility and privacy review.

## Safety boundary
This customer package is synthetic and read-only. It provides evidence or drafts only: no diagnosis or treatment advice, no eligibility or authorization outcome beyond source evidence, no scheduling, messaging, submission, or record change. Qualified clinical, utilization, quality, or operational reviewers own every downstream decision. Use minimum-necessary information.

## Package map

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/healthcare_stacks/care_gap_closure_stack/care_gap_closure_agent.py` |
| Deployment recipe | `solutions/care-gap-closure/deployment.json` |
| Locked persona cases | `tests/demo_cases/care-gap-closure.json` |
| Approved one-pager map | `solutions/care-gap-closure/evals/onepager-map.json` |
| Source audit | `solutions/care-gap-closure/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/care-gap-closure/evals/transcripts.json` |
| Global instructions | `solutions/care-gap-closure/manual/GLOBAL-INSTRUCTIONS.md` |
| Synthetic knowledge | `solutions/care-gap-closure/manual/knowledge/` |
| Uploadable operation skills | `solutions/care-gap-closure/manual/skills/*/SKILL.md` |

## Operations
- `gap_analysis` — Summarizes aggregate synthetic source counts and limitations without deciding measure eligibility.
- `cohort_review` — Organizes operational evidence-review cohorts without clinical risk scoring.
- `outreach_draft` — Drafts privacy-aware language but does not contact anyone.
- `quality_dashboard` — Shows source-completeness signals for quality and clinical validation.

## Package state
- One locked persona case and one uploadable skill exist per operation.
- Exactly two synthetic manual knowledge files are included.
- All four locked cases passed a strict single-agent isolation capture.
- No global Brainstem capture, Copilot Studio project, tutorial, screenshot, export bundle, publication, or live connector is included.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/care-gap-closure/field-guide.html` |
| Evidence report | `solutions/care-gap-closure/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/care-gap-closure/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/care-gap-closure/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/care-gap-closure/quest.html` |
| Literal browser tutorial | `solutions/care-gap-closure/manual-tutorial.html` |
| Raw export manifest | `solutions/care-gap-closure/export-manifest.json` |
| Source bundle | `solutions/care-gap-closure/exports/care-gap-closure-source.zip` |
| Manual evidence | `solutions/care-gap-closure/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/care-gap-closure/screenshots/manual/browserfilm.json` |

**Scaffold status:** 69 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
