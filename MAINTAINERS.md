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

One setting decides it: `source.repo` in `rapp/GRAIL-SPECIES.json`. The species and installer tools read it
(an environment value `GRAIL_SOURCE_REPO` overrides it for a single run). To move to a company-owned copy of
the Grail, change that one value in a kernel-sync pull request; nothing else needs editing.
