# Care Gap Closure Agent solution package

## Purpose
Help quality and care-coordination teams inspect synthetic measure evidence, organize operational review cohorts, and draft unsent outreach while preserving clinical eligibility and privacy review.

## Safety boundary
This customer package is synthetic and read-only. It provides evidence or drafts only: no diagnosis or treatment advice, no eligibility or authorization outcome beyond source evidence, no scheduling, messaging, submission, or record change. Qualified clinical, utilization, quality, or operational reviewers own every downstream decision. Use minimum-necessary information.

## Choose your start

### No-install evidence preview

Use this path when a seller does not have PAC CLI, the Copilot Studio plugin,
or permission to create an agent:

1. Open `quest.html` and stay in Easy mode.
2. Review the approved annotated case captures and the Draft confirmation.
3. Compare each visible anchor with the locked marker checklist in
   `evidence-report.html`.

This is a read-only review of recorded synthetic evidence. It is not a live
sandbox, a current-tenant test, or proof that anything was deployed. Do not
mark build or deployment checkpoints complete unless you performed them.

### Guided Draft build

For the hands-on path, the learner only attaches the Easy-mode skill and sends
the two workshop messages. The skill owns plugin and PAC CLI checks. If a
preflight check fails, stop and hand the exact message to a facilitator; the
learner should not troubleshoot a terminal during the workshop.

## Nontechnical preflight

- I can open GitHub Copilot Chat in VS Code and select Agent mode.
- I am signed in with GitHub Copilot access.
- For the hands-on path, I can access the intended Copilot Studio environment.
- I know this workshop stops at **Draft** and never publishes.
- I will use synthetic information only.

## What a passing run looks like

- Local proof: all 4 locked cases pass.
- Preview proof: all 4 locked cases pass in fresh conversations.
- Identity: `Care Gap Closure Pilot`.
- Inventory: Claude Sonnet 4.6, 2 knowledge files, and 4 skills.
- Publication gate: **Draft** and `published: false`.

Local achievement labels such as **Local proof**, **Draft builder**,
**Preview proven**, and **Workshop complete** help track progress on this
device. They are self-reported and never replace the evidence checklist.

## Feedback without GitHub

Use the page's **Report an issue** button when GitHub is an approved channel.
Otherwise copy this into an internal chat, email, or ticket:

```text
Workshop: Care Gap Closure Agent
Mode and step:
Expected visible anchor:
What appeared instead:
Screenshot or evidence path:
No credentials, tokens, customer data, or patient information included: yes/no
```

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
- Real Easy- and Manual-mode browser evidence, a Draft Copilot Studio source
  package, tutorials, and an export bundle are included.
- No publication, live connector, customer data, or production write is
  included.

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
| Guided Easy/Manual quest | `solutions/care-gap-closure/quest.html` |
| Literal browser tutorial | `solutions/care-gap-closure/manual-tutorial.html` |
| Raw export manifest | `solutions/care-gap-closure/export-manifest.json` |
| Source bundle | `solutions/care-gap-closure/exports/care-gap-closure-source.zip` |
| Manual evidence | `solutions/care-gap-closure/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/care-gap-closure/screenshots/manual/browserfilm.json` |
| Copilot Studio solution ZIP | `solutions/care-gap-closure/exports/care-gap-closure-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/care-gap-closure/exports/care-gap-closure-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/care-gap-closure/exports/care-gap-closure-solution-export.json` |

**Scaffold status:** 95 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
