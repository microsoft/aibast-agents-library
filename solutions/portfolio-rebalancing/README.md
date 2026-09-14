# Portfolio Rebalancing Agent solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/financial_services_stacks/portfolio_rebalancing_stack/portfolio_rebalancing_agent.py` |
| Deployment recipe | `solutions/portfolio-rebalancing/deployment.json` |
| Locked behavior cases | `tests/demo_cases/portfolio-rebalancing.json` |
| Approved one-pager map | `solutions/portfolio-rebalancing/evals/onepager-map.json` |
| Source capability audit | `solutions/portfolio-rebalancing/evals/source-audit.json` |
| Historical source-only transcripts | `solutions/portfolio-rebalancing/evals/transcripts.json` |
| Uploadable synthetic knowledge | `solutions/portfolio-rebalancing/manual/knowledge/` |
| Uploadable operation skills | `solutions/portfolio-rebalancing/manual/skills/` |

## Implemented scope

- `portfolio_analysis` — Portfolio drift analysis.
- `rebalance_recommendation` — Rebalancing candidates.
- `tax_impact` — Illustrative tax impact.
- `tax_loss_harvest` — Tax-loss-harvesting candidates.
- `retirement_scenario` — Retirement scenario inputs.
- `execution_plan` — Human-controlled implementation checklist.

## Current native Manual evidence — 2026-09-13

**The r5 native regression passed all six locked cases; the workshop is still
partial, not certified.** The parent submitted each unchanged prompt once in
its own fresh native Preview conversation on one frozen build. The saved
global policy and all six complete skill bodies, names and descriptions matched
after leaving through Agents and reopening at 03:59:19.049Z. Final exact-name
search found one Draft at 04:56:03.052Z; reopening at 04:56:08.534Z correlated
the same tested identity, name/model and inactive Save. No Publish was used.

The current personally reviewed references cover **steps 2–6 and 14–22**.
Steps 2–5 show the saved name, complete policy and empty Tools after reopening;
they do not record a new naming, paste or removal action. Step 6 pairs the
actual earlier controls-file staging with that same source's later **Ready**
status. No new upload occurred. Blank-agent **step 1** and upload **steps 7–13
remain open**; final inventory and source tests cannot
substitute for their live evidence and personal review. Fresh-from-empty
construction is not claimed. See the [dated review](evals/manual-pilot-review.json),
[accepted native matrix](evals/manual-build-evidence.json) and
[visual scope](evals/visual-checkpoints.json). The six response boards contain
labeled crops of multiple actual views, not single historical JPEGs or a new
continuous walkthrough. Private full-window originals are not distributed.

R1/r2/r3/r4 failures remain separate from r5; r4 closed with five passes and
PRB-03 failed for unprovided account-category examples. R5 changed only the tax
skill/native mirror and the two controls copies relative to r4. Historical
August metadata is preserved [verbatim as history](evals/history/2026-08/index.json);
assisted/Easy and Brainstem records are not native Manual r5 passes.

## Evidence and safety boundary

The approved one-pager `Portfolio Rebalancing Agent one-pager.pptx` is the advertised-scope source for this package. Each promise maps to source behavior and locked persona-language cases in `evals/onepager-map.json`. Portfolio business records, identifiers, dates, amounts and outcomes are synthetic; the dated native review records describe actual pilot observations.

Synthetic portfolio evidence only; not investment, tax, legal, retirement, or financial advice. No order or transaction occurred. Licensed human review required.

## Manual Copilot Studio preparation

Start with the [Manual tutorial](manual-tutorial.html). On a new learner build,
upload the two exact Markdown knowledge files and one `SKILL.md` for each skill
below. When resuming an owned **Portfolio Rebalancing Manual** Draft, reopen it,
compare the complete saved sources and replace only mismatches; do not create
a duplicate agent or duplicate attachments.

Use **Claude Sonnet 4.6**, six skills, two knowledge files, **zero configured
Tools**, and remove default web search. Do not bind production connections.
Native built-in skill and knowledge activity is allowed; production connector
seams in `deployment.json` are future integration work, not Manual prerequisites.

| Upload folder | Exact frontmatter `name` |
| --- | --- |
| `aibast_execution-plan_06` | `execution-plan` |
| `aibast_portfolio-analysis_01` | `portfolio-analysis` |
| `aibast_rebalance-recommendation_02` | `rebalance-recommendation` |
| `aibast_retirement-scenario_05` | `retirement-scenario` |
| `aibast_tax-impact_03` | `tax-impact` |
| `aibast_tax-loss-harvest_04` | `tax-loss-harvest` |

Match each frontmatter description and full body, not just the folder/name.
Verify complete knowledge filenames after ingestion. **Save, leave through
Agents, reopen the same Draft**, then compare the full global policy and all
six skills. Run each unchanged locked prompt once using **New chat**. Grade the
completed final answer, actual skill/knowledge activity, citations and full
safety boundary, not debug reasoning. Preserve failures rather than rerolling
unchanged prompts. Confirm the same Draft afterward. **Do not Publish.**

## Download scope

The [r5 manual-input ZIP](exports/portfolio-rebalancing-source.zip) contains
exactly the [nine frozen inputs and their hashes](evals/manual-inputs-r5.json),
plus its export README. It is deliberately **not a standalone workshop, runtime
or native import**: guides and the reviewed PNG references are separate
site assets, not ZIP contents. The native source project, tutorials, evidence
and historical captures do exist in this package.

The unchanged August native import archive has five entries, **zero skills
and zero knowledge files**. It cannot reproduce this six-skill/two-file Manual
build and is withheld from current reproduction downloads; no complete native
export was fabricated. Source links retain canonical generator URLs; the Pages
build supplies its actual repository/ref for excluded downloads. Release
verification must fetch the published URLs and compare all nine input hashes;
local file availability alone is not public-delivery evidence.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/portfolio-rebalancing/field-guide.html` |
| Evidence report | `solutions/portfolio-rebalancing/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/portfolio-rebalancing/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/portfolio-rebalancing/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Manual quest | `solutions/portfolio-rebalancing/quest.html` |
| Literal browser tutorial | `solutions/portfolio-rebalancing/manual-tutorial.html` |
| Raw export manifest | `solutions/portfolio-rebalancing/export-manifest.json` |
| Source bundle | `solutions/portfolio-rebalancing/exports/portfolio-rebalancing-source.zip` |
| Manual evidence | `solutions/portfolio-rebalancing/evals/manual-build-evidence.json` |
| Manual reviewed reference set | `solutions/portfolio-rebalancing/screenshots/manual/repaired-r5/browserfilm.json` |
| Historical Copilot Studio solution ZIP — not current source | `solutions/portfolio-rebalancing/exports/portfolio-rebalancing-copilot-studio-solution.zip` |
| Copilot Studio deployment settings | `solutions/portfolio-rebalancing/exports/portfolio-rebalancing-deployment-settings.json` |
| Copilot Studio export metadata | `solutions/portfolio-rebalancing/exports/portfolio-rebalancing-solution-export.json` |

**Scaffold status:** 74 resources ready; 0 pending. Pending assets are not evidence and must not be claimed as captured. Resource readiness means file availability, not workshop acceptance. On 2026-09-13, all six unchanged locked prompts passed once each in separate fresh native Preview conversations on one saved/reopened frozen r5 Manual build. Full policy and all six skill names, descriptions and bodies matched; the same agent remained Draft after regression. Reviewed references cover steps 2-6 and 14-22. Steps 2-5 are explicitly post-reopen saved-state readbacks. Step 6 combines the actual earlier r5 file-staging capture with the same source's later Ready status. No new upload or regression occurred. Blank-agent step 1 and upload steps 7-13 remain open. The workshop is partial, not certified.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
