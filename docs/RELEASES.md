# Release ledger

One entry per promotion to production, newest first. Each records what shipped,
the evidence it was gated on, and every issue reported after it. Entries are
written at promotion time and amended as post-release issues arrive; nothing is
deleted. Draft a new entry with `python tools/release_ledger.py <pr-number>`.

Post-release issues carry the `post-release` label; automatically filed smoke
failures also carry `incident`.

---

## 2026-11-13 — Cowork plugin downloads, shared demo player bar, counted downloads

**Shipped:** [#278](https://github.com/microsoft/aibast-agents-library/pull/278)
from `kody-w:staging`, merge commit `6fb35af4`, then
[#279](https://github.com/microsoft/aibast-agents-library/pull/279), merge
commit `063e3a91`. Every solution gains a "Download Cowork plugin" button: one
plugin holding one skill and the solution's synthetic data, built by
`tools/build_cowork_plugins.py`. All three demo views share one player bar,
which restores Pause, Back and Next on the Microsoft 365 Copilot and Copilot
Studio views; long Cowork answers no longer show under the message box; the
installer page is wider. The metrics page counts Cowork plugin and Copilot
Studio solution downloads, and both download buttons point at the
`solution-bundles` release so each download is counted. Staging pull requests
#575, #576, #578, #580, #581, #582, #583, #585, #586 (production sync) in
#278; #587, #588 and #589 (production syncs) in #279.

**Gates:** preflight on each pull request. The whole test suite ran on the
staging head before each promotion (3331 passed, 1 skipped before #279).
`tools/promotion_check.sh` reported GREEN on the staging head `e4f40ebb`:
[preflight](https://github.com/kody-w/aibast-agents-library/actions/runs/43360511294),
[Pages deploy](https://github.com/kody-w/aibast-agents-library/actions/runs/43360511284),
[one-liner smoke](https://github.com/kody-w/aibast-agents-library/actions/runs/43360713263);
and again on `ae6299d9`:
[preflight](https://github.com/kody-w/aibast-agents-library/actions/runs/43376790660),
[Pages deploy](https://github.com/kody-w/aibast-agents-library/actions/runs/43376790515),
[one-liner smoke](https://github.com/kody-w/aibast-agents-library/actions/runs/43376956876).
After #278, production showed the player bar and Next in 3 of 3 demo views,
and 72 of 72 Cowork plugins and 72 of 72 Copilot Studio solutions on the
`solution-bundles` release matched the repository. After #279, both download
buttons on one solution (Maintenance Scheduling Agent) on production resolved
to the release and returned 200; the other 71 solutions' buttons were not
pressed.

**Post-release:**
- After #278 the two download buttons on production worked but fetched the
  repository copies, so downloads were not counted. The fix on staging
  rewrote the links while building the Pages site, and production Pages
  serves the branch without that build. Fixed by putting the release links
  in the page source (staging #587) and shipped in #279 the same day.
- On staging the Cowork plugin link returned 404 at first, because the built
  site carries no zip files. Fixed before the promotion (staging #583).
- The promotion check for #279 was red twice because the daily metrics
  snapshot had landed on production in between; each needed a
  production-into-staging sync (#588, #589).
- A demo button for a scenario with no recording opens a view without the
  player bar. Tracked in the library backlog.

**Lessons:** staging Pages is built by a workflow and production Pages serves
the branch as it is, so a fix made only in the build step never reaches
production; put it in the page source and check it on the production page.
Promote soon after a sync, and not near the daily snapshot time (05:20 UTC),
or the ring falls behind again.

---

## 2026-11-12 — Why page, any-AI guide, Cowork demo frame

**Shipped:** [#275](https://github.com/microsoft/aibast-agents-library/pull/275)
from `kody-w:staging`, merge commit `e7ee1596`. `why.html` is trimmed back to
"why use a Brainstem" and explains the one plain `skill.md` any AI can be
handed; the new `docs/any-ai/` guide (page, `SKILL.md`, `kernel.py`) brings a
library agent to an AI by name and checks its fingerprint; all 72 Cowork demos
get a frame modeled on the product (start screen, "Working on it" trail,
Workspace steps, Plugins, dark player bar). Staging pull requests #571, #572,
#573 (production sync).

**Gates:** preflight on each pull request. `tools/promotion_check.sh` reported
GREEN on the staging head `2f359c4f`:
[preflight](https://github.com/kody-w/aibast-agents-library/actions/runs/43148813045),
[Pages deploy](https://github.com/kody-w/aibast-agents-library/actions/runs/43148813019),
[one-liner smoke](https://github.com/kody-w/aibast-agents-library/actions/runs/43148954263).
After the merge, production Pages served the new Why section, the any-AI guide
files and the Cowork frame (each fetched and returned 200). The any-AI guide
was exercised with one AI, one run; other AIs are untried.

**Post-release:**
- The Cowork frame change hid Pause, Back and Next on the Microsoft 365
  Copilot and Copilot Studio demo views: every view was treated as drawing
  its own player bar, and only Cowork did. Found the next day by
  `tests/test_first_minute_check.py`, which had not been run before the
  merge. Fixed on staging by drawing one shared player bar on all three
  views (staging #576, #578) and shipped in the next release.
- Long Cowork answers showed through between the message box and the player
  bar. Fixed on staging (#580).
- [#276](https://github.com/microsoft/aibast-agents-library/issues/276) and
  [#277](https://github.com/microsoft/aibast-agents-library/issues/277):
  the scheduled one-liner smoke was skipped once and cancelled once, and
  each was filed as a failure. Both closed themselves when the next run
  passed on all runners. No installer change was involved.
- The earlier promotion pull request #274 had already been merged from an
  older staging head, so this release needed a production-into-staging sync
  (#573) and a new pull request.

**Lessons:** run the whole test suite, browser tests included, on the staging
head before a promotion, not only the tests near the change; a shared demo
page has three views, and a change made for one must be looked at in all
three. Before reporting a promotion as carrying a change, check that the
change's commit is an ancestor of the merged head.

---

## 2026-11-09 — Get help form, Copilot prompts per tier, VS Code end state

**Shipped:** [#269](https://github.com/microsoft/aibast-agents-library/pull/269)
from `kody-w:staging`, merge commit `c49bafcc`. Get help in the Brainstem chat,
the installers and the docs opens the library's Microsoft Form pre-filled with
the error and context (nothing private; the person only presses Submit) instead
of a GitHub issue; the installer page carries one Copilot Chat prompt per tier
and its VS Code preview shows the real end state (`rapp_brainstem` in the
Explorer, the Brainstem in the Simple Browser, Copilot Chat on the right);
`skill.md` gains the tier router, Ask-the-user pauses and the VS Code end-state
step. Staging pull requests #484, #485, #486.

**Gates:** preflight on each pull request. `tools/promotion_check.sh` reported
GREEN on the staging head `af6e7bfb`:
[preflight](https://github.com/kody-w/aibast-agents-library/actions/runs/42546044109),
[Pages deploy](https://github.com/kody-w/aibast-agents-library/actions/runs/42546044083),
[one-liner smoke](https://github.com/kody-w/aibast-agents-library/actions/runs/42546147560).
After the merge, production Pages served the new installer page and the
help-form links (checked 01:48 UTC).

**Post-release:**
- Installer Assets
  [run](https://github.com/microsoft/aibast-agents-library/actions/runs/42547316395)
  failed its byte-identical check for `install.ps1` one second after
  replacing the asset; the download matched `main` when checked by hand a
  minute later (same md5, 77,892 bytes). Same failure on #268. A read-after-
  write race on the release CDN, not drift. Fixed by retrying the check for
  up to two minutes before reporting drift (this entry's pull request).

**Lessons:** a verify step that reads back what it just published must wait
for the publish to converge; one read is a coin flip, not a check.

---

## 2026-11-08 — installer: a running Brainstem is success, not a conflict

**Shipped:** [#268](https://github.com/microsoft/aibast-agents-library/pull/268)
from `kody-w:staging`, merge commit `5e710607`. Re-running the one-liner while
a Brainstem is already running on port 7071 reports "Your Brainstem is already
running", opens it and ends with the two lines a newcomer needs; a different
program on the port gets one plain sentence instead of a stack of errors;
install failures print the pre-filled help link. Staging pull requests #481,
#482, #483.

**Gates:** preflight on each pull request. `tools/promotion_check.sh` reported
GREEN on the staging head:
[preflight](https://github.com/kody-w/aibast-agents-library/actions/runs/42534206828),
[Pages deploy](https://github.com/kody-w/aibast-agents-library/actions/runs/42534206834),
[one-liner smoke](https://github.com/kody-w/aibast-agents-library/actions/runs/42534310140).
After the merge, both production installers served the new text (23:31 UTC)
and the Mac one-liner was run against a running Brainstem on a real machine
(1 of 1: reused, not killed).

**Post-release:**
- Installer Assets
  [run](https://github.com/microsoft/aibast-agents-library/actions/runs/42535421881)
  failed the byte-identical check for `install.ps1` right after replacing the
  asset. Same cause and fix as in the 2026-11-09 entry.

**Lessons:** the second run of an installer is the common case, not an edge
case; test it on a machine that already has the thing installed.

---

## 2026-10-23 — Telecom, Media & Gaming solutions, registry installs from chat, office hours rename

**Shipped:** [#248](https://github.com/microsoft/aibast-agents-library/pull/248)
four Telecom, Media & Gaming solutions (slots 67-70) and the Telecom, Media &
Gaming industry, with registry and academy rebuilt from source;
[#250](https://github.com/microsoft/aibast-agents-library/pull/250) Brainstem
chat installs agents from the AIBAST registry and counts each install, the
request form falls back to "My use case" for solutions not yet on it, and the
installer page gains the office hours sign-up;
[#251](https://github.com/microsoft/aibast-agents-library/pull/251) office hours
renamed to "AIBAST agents and prototyping office hours". Merge commits
`62e45abd`, `3516b50a`, `c4261844`. All three promoted from `kody-w:staging`.

**Gates:** preflight on each pull request. For #251, 14 of 14 pull request
checks passed and `tools/promotion_check.sh` reported GREEN on the staging head
`0e06cd7d`: [preflight](https://github.com/kody-w/aibast-agents-library/actions/runs/40009456951),
[Pages deploy](https://github.com/kody-w/aibast-agents-library/actions/runs/40009456963),
[one-liner smoke](https://github.com/kody-w/aibast-agents-library/actions/runs/40009731531).
After the merge, the production installer page served the new heading.

**Post-release:**
- [#252](https://github.com/microsoft/aibast-agents-library/issues/252) incident
  filed two minutes after #251 merged. The smoke job in
  [the run](https://github.com/microsoft/aibast-agents-library/actions/runs/40022609752)
  was skipped, not failed, but the incident job still filed the issue.
  [Recovered](https://github.com/microsoft/aibast-agents-library/actions/runs/40027418822)
  on `c4261844`: the published one-liner installed and answered on all runners.
  Closed. Disposition: the incident job should not file when the smoke job is skipped.
- Agent installs fetched through jsDelivr are partly refused because the
  package at the pinned commit exceeds the CDN's 50 MB limit (3 of 39 sampled
  agent files). Installs fall back to raw GitHub and succeed, but those are not
  counted. Open.

**Lessons:** treat a skipped smoke as "no result", never as a failure, or a
merge right after a deploy files a false incident. A CDN mirror has size
limits that only appear on a cold cache; measure a sample of files before
relying on it for counts.

---

## 2026-09-02 — installer download counting

**Shipped:** [#194](https://github.com/microsoft/aibast-agents-library/pull/194)
rolling `installers` release so installs are GitHub-recorded downloads;
[#195](https://github.com/microsoft/aibast-agents-library/pull/195) verify
published assets match `main`, daily republish;
[#196](https://github.com/microsoft/aibast-agents-library/pull/196) upload only
on change, accumulate counts across counter resets. Merge commits `c60521e2`,
`ff504344`, `508ba51d`.

**Gates:** production preflight on each pull request.

**Post-release:**
- The `Installer Assets` workflow fails daily on forks: its final step
  dispatches the metrics workflow, which forks keep disabled. Observed on the
  staging fork 2026-09-03 and 2026-09-04. Disposition: guard release publishing
  and the dispatch with `github.repository`, tracked with the ring plumbing.
- Metrics snapshot pushes race the installer-assets commits and fail on
  non-fast-forward; [#197](https://github.com/microsoft/aibast-agents-library/pull/197)
  (rebase-and-retry) open.
- [#200](https://github.com/microsoft/aibast-agents-library/issues/200) make the
  install short link agent-friendly and add a paste-only setup entry point. Open.

**Lessons:** a scheduled job that writes to `main` needs a repository guard so
forks do not run it, and a rebase-retry so two writers do not fail each other.

---

## 2026-08-17 to 2026-08-19 — Frontier beta wave and CI hardening

**Shipped:** [#170](https://github.com/microsoft/aibast-agents-library/pull/170),
[#171](https://github.com/microsoft/aibast-agents-library/pull/171),
[#172](https://github.com/microsoft/aibast-agents-library/pull/172) Windows
installer and Frontier gate fixes; [#174](https://github.com/microsoft/aibast-agents-library/pull/174)
Show Mode; [#175](https://github.com/microsoft/aibast-agents-library/pull/175)
multi-chat Brain Surgeon; [#176](https://github.com/microsoft/aibast-agents-library/pull/176)
RAPPlication twins; [#178](https://github.com/microsoft/aibast-agents-library/pull/178)
preflight green on `main`; [#179](https://github.com/microsoft/aibast-agents-library/pull/179)
Windows delayed expansion in commit verification; [#180](https://github.com/microsoft/aibast-agents-library/pull/180)
all Actions pinned to commit SHAs. Pre-releases `brainstem-beta-v0.1.0-beta.5`, `beta.6`.

**Gates:** preflight per pull request; Frontier test gate made Windows-safe in the same wave.

**Post-release:**
- [#177](https://github.com/microsoft/aibast-agents-library/issues/177) automate
  Frontier release promotion so the public bootstrap cannot stay on a broken beta. Open.
- [#187](https://github.com/microsoft/aibast-agents-library/issues/187) `.DS_Store`
  tracked at the repository root. Open.
- [#190](https://github.com/microsoft/aibast-agents-library/issues/190) Pages
  read the GitHub API per visitor and hit rate limits for real audiences. Open.
- Windows one-liner startup stall, fix in
  [#192](https://github.com/microsoft/aibast-agents-library/pull/192). Open.
- Isolated Brainstem homes ignored by the installer, fix in
  [#188](https://github.com/microsoft/aibast-agents-library/pull/188). Open.

**Lessons:** `main` was red for a period before #178; preflight must be green
on `main` at all times or a promotion cannot be judged. A public bootstrap that
points at a moving tag needs a promotion gate (#177), which the staging ring now provides.

---

## 2026-08-12 — first staging promotion

**Shipped:** [#163](https://github.com/microsoft/aibast-agents-library/pull/163)
"Staging", merge commit `c4cf1871`; pre-release `brainstem-beta-v0.1.0-beta.4`;
`agent-downloads` release.

**Post-release:**
- [#165](https://github.com/microsoft/aibast-agents-library/issues/165) Frontier
  commit verification fails when Git is under Program Files. Closed by #170.
- [#167](https://github.com/microsoft/aibast-agents-library/issues/167) Frontier
  Windows install fails when Git is under Program Files. Open.
- [#166](https://github.com/microsoft/aibast-agents-library/issues/166),
  [#169](https://github.com/microsoft/aibast-agents-library/issues/169)
  achievement-progress reports. Closed.

**Lessons:** Windows paths with spaces broke two separate code paths. Windows
runs in every gate from this point on.

---

## 2026-08-09 to 2026-08-10 — industry learning journeys

**Shipped:** [#17](https://github.com/microsoft/aibast-agents-library/pull/17)
51 end-to-end industry agent learning journeys; [#18](https://github.com/microsoft/aibast-agents-library/pull/18)
workshop achievements.

**Post-release:** none recorded.

---

## 2026-07-20 — Brainstem kernel 0.6.16

**Shipped:** [#16](https://github.com/microsoft/aibast-agents-library/pull/16)
sync Brainstem v0.6.16 without clobbering AIBAST surfaces (`f7c7e804`).

**Post-release:** none recorded. This is the kernel the species contract is pinned to.

---

## Earlier kernel syncs

- 2026-07-03 [#15](https://github.com/microsoft/aibast-agents-library/pull/15)
  Brainstem v0.6.3 bug fixes, stray reference repoint, AIBAST disclaimer.
- 2026-05-27 [#13](https://github.com/microsoft/aibast-agents-library/pull/13)
  Brainstem v0.6.0, Windows install and encoding fixes.
- 2026-03-19 [#11](https://github.com/microsoft/aibast-agents-library/pull/11)
  first Brainstem merge into the library.

Device-code sign-in stalls (the `/login` flow) recurred across these syncs and
drove the auth-chain rework recorded in `CLAUDE.md`; the one-liner smoke now
starts the server on every run so a regression there is caught before promotion.
