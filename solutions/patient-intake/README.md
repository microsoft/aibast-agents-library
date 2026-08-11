# Patient Intake and Scheduling Agent solution package

## Purpose
Give patient-access teams a safe, read-only view of synthetic intake completeness, recorded coverage evidence, candidate availability, and pre-visit follow-up—without booking care or changing a record.

## Safety boundary
This customer package is synthetic and read-only. It provides evidence or drafts only: no diagnosis or treatment advice, no eligibility or authorization outcome beyond source evidence, no scheduling, messaging, submission, or record change. Qualified clinical, utilization, quality, or operational reviewers own every downstream decision. Use minimum-necessary information.

## Package map

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/healthcare_stacks/patient_intake_stack/patient_intake_agent.py` |
| Deployment recipe | `solutions/patient-intake/deployment.json` |
| Locked persona cases | `tests/demo_cases/patient-intake.json` |
| Approved one-pager map | `solutions/patient-intake/evals/onepager-map.json` |
| Source audit | `solutions/patient-intake/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/patient-intake/evals/transcripts.json` |
| Global instructions | `solutions/patient-intake/manual/GLOBAL-INSTRUCTIONS.md` |
| Synthetic knowledge | `solutions/patient-intake/manual/knowledge/` |
| Uploadable operation skills | `solutions/patient-intake/manual/skills/*/SKILL.md` |

## Operations
- `intake_readiness` — Summarizes present and missing synthetic intake evidence for staff confirmation.
- `coverage_evidence` — Transcribes source-recorded synthetic coverage evidence without determining eligibility.
- `appointment_availability` — Shows candidate synthetic source slots without holding, booking, or changing an appointment.
- `pre_visit_summary` — Drafts a minimum-necessary readiness handoff for authorized patient-access review.

## Package state
- One locked persona case and one uploadable skill exist per operation.
- Exactly two synthetic manual knowledge files are included.
- All four locked cases passed a strict single-agent isolation capture.
- No global Brainstem capture, Copilot Studio project, tutorial, screenshot, export bundle, publication, or live connector is included.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/patient-intake/field-guide.html` |
| Evidence report | `solutions/patient-intake/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/patient-intake/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/patient-intake/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/patient-intake/quest.html` |
| Literal browser tutorial | `solutions/patient-intake/manual-tutorial.html` |
| Raw export manifest | `solutions/patient-intake/export-manifest.json` |
| Source bundle | `solutions/patient-intake/exports/patient-intake-source.zip` |
| Manual evidence | `solutions/patient-intake/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/patient-intake/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/patient-intake/exports/patient-intake-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/patient-intake/exports/patient-intake-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/patient-intake/exports/patient-intake-solution-export.json` |

**Scaffold status:** 93 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
