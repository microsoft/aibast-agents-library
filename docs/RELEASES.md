# Release ledger

One entry per promotion to production, newest first. Each records what shipped,
the evidence it was gated on, and every issue reported after it. Entries are
written at promotion time and amended as post-release issues arrive; nothing is
deleted. Draft a new entry with `python tools/release_ledger.py <pr-number>`.

Post-release issues carry the `post-release` label; automatically filed smoke
failures also carry `incident`.

---

## 2026-10-16 — every demo plays its own agent; build-time GitHub snapshot

**Shipped:** [#243](https://github.com/microsoft/aibast-agents-library/pull/243)
demo links resolve to each agent's own recorded scenario through the generated
`solutions/_shared/demo-scenarios.json` (349 of 359 catalog links recorded; the
rest say "This demo isn't recorded yet"); a build-time snapshot of the GitHub
data the pages read (`scripts/snapshot_github_data.py`, `--overlay` on
`build_pages_site.py`); same-origin reads in the download center and metrics
page. Merge commit `90588550`.

**Gates:** staging preflight, Deploy Academy Pages and Ring one-liner smoke;
full suite; browser pass on staging (two `solution.html` regressions found and
fixed before promotion). On production after merge: 360 of 360 demo links play
the right agent; 13 of 13 critical paths load.

**Post-release:**
- `api/v1/github/*` returned 404 on production: production Pages serves the
  `main` branch, not the Actions artifact, so the overlay never reached it and
  the download center kept falling back to `api.github.com`. Disposition: the
  metrics workflow commits the snapshot to the branch;
  [#244](https://github.com/microsoft/aibast-agents-library/pull/244).

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
