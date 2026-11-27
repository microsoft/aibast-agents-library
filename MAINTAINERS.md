# Maintainers

Two named owners for each critical area, so a kernel sync or a release never waits on one person.

| Area | What it covers | Owners |
|---|---|---|
| Kernel sync | `rapp_brainstem/`, `rapp/GRAIL-SPECIES.json`, `rapp/KERNEL-DRIFT.md`, the kernel-sync pull requests | Kody Wildfeuer; second owner: to be named |
| Installers | `install.sh`, `install.ps1`, `install.cmd`, `docs/install.*`, the installer side-by-side check | Kody Wildfeuer; second owner: to be named |
| Promotion | the pull request from staging to `microsoft:main` and the release ledger in `docs/RELEASES.md` | Kody Wildfeuer; second owner: to be named |
| Catalog | `agents/@aibast-agents-library/`, `registry.json`, `solutions/` | Kody Wildfeuer; second owner: to be named |

Rules:
- A kernel sync or a promotion is merged by an owner of that area, after its checks pass.
- An owner who opened a change does not approve it alone once a second owner is named.
- Change this file through a pull request.

## Where kernel updates come from

This repository is the Microsoft-owned copy of the Grail: `rapp_brainstem/` and the installers are the
Grail kernel, vendored and pinned by commit, with only the differences listed in `rapp/KERNEL-DRIFT.md`.
Users install from here and never from the upstream Grail.

The upstream it syncs from is one setting, `source.repo` in `rapp/GRAIL-SPECIES.json` (an environment
value `GRAIL_SOURCE_REPO` overrides it for one run). `.github/workflows/kernel-sync.yml` checks it daily
and prepares a sync for an owner to review and merge.
