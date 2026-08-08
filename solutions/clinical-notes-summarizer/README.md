# Clinical Notes Summarizer Agent solution package

## Purpose
Give clinical teams consistent synthetic encounter, medication, problem-list, and referral-context drafts while keeping diagnosis, treatment, clearance, urgency, scheduling, and record changes with qualified humans.

## Safety boundary
This customer package is synthetic and read-only. It provides evidence or drafts only: no diagnosis or treatment advice, no eligibility or authorization outcome beyond source evidence, no scheduling, messaging, submission, or record change. Qualified clinical, utilization, quality, or operational reviewers own every downstream decision. Use minimum-necessary information.

## Package map

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/healthcare_stacks/clinical_notes_summarizer_stack/clinical_notes_summarizer_agent.py` |
| Deployment recipe | `solutions/clinical-notes-summarizer/deployment.json` |
| Locked persona cases | `tests/demo_cases/clinical-notes-summarizer.json` |
| Approved one-pager map | `solutions/clinical-notes-summarizer/evals/onepager-map.json` |
| Source audit | `solutions/clinical-notes-summarizer/evals/source-audit.json` |
| Strict isolated transcripts | `solutions/clinical-notes-summarizer/evals/transcripts.json` |
| Global instructions | `solutions/clinical-notes-summarizer/manual/GLOBAL-INSTRUCTIONS.md` |
| Synthetic knowledge | `solutions/clinical-notes-summarizer/manual/knowledge/` |
| Uploadable operation skills | `solutions/clinical-notes-summarizer/manual/skills/*/SKILL.md` |

## Operations
- `encounter_summary` — Extracts synthetic encounter facts without clinical inference.
- `medication_inventory` — Lists source-recorded synthetic medications for clinician or pharmacist reconciliation.
- `problem_list_extract` — Extracts source-coded problems without confirming or changing a diagnosis.
- `referral_context` — Summarizes source-recorded referral context without placing or scheduling it.

## Package state
- One locked persona case and one uploadable skill exist per operation.
- Exactly two synthetic manual knowledge files are included.
- All four locked cases passed a strict single-agent isolation capture.
- No global Brainstem capture, Copilot Studio project, tutorial, screenshot, export bundle, publication, or live connector is included.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/clinical-notes-summarizer/FIELD-GUIDE.md` |
| Guided Easy/Hard quest | `solutions/clinical-notes-summarizer/quest.html` |
| Literal browser tutorial | `solutions/clinical-notes-summarizer/manual-tutorial.html` |
| Raw export manifest | `solutions/clinical-notes-summarizer/export-manifest.json` |
| Source bundle | `solutions/clinical-notes-summarizer/exports/clinical-notes-summarizer-source.zip` |
| Manual evidence | `solutions/clinical-notes-summarizer/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/clinical-notes-summarizer/screenshots/manual/browserfilm.json` |

**Scaffold status:** 60 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
