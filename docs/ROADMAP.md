# Roadmap

Tracked as GitHub milestones on the staging fork,
https://github.com/kody-w/aibast-agents-library/milestones, where staging work
happens. Production issues stay on the Microsoft repository. This page is the
narrative; the milestones are the source of truth for status.

| Milestone | Outcome | Status |
|---|---|---|
| M1 Staging ring live | Fork `main` mirrors production automatically; `staging` serves the fork Pages; every staging push is preflighted, deployed, and smoked | in progress |
| M2 Vendored one-liner on staging | The staging Pages one-liner installs this repository's own kernel at the staging ref on clean Linux, macOS, and Windows runners | in progress |
| M3 Grail species regression | Species contract and drift ledger in CI; installer fixes that belong upstream returned to the Grail | in progress |
| M4 Academy promotion | Microsoft AI Academy promoted from staging to production after soaking on the ring | queued |
| M5 v1 GA blockers | Upstream licensing, Discussions and metrics token on the Microsoft repository, Microsoft-owned auth worker | queued |

Principles that do not change between milestones:

- The kernel is vendored from the Grail and updated one way. This repository
  grows around it, never inside it. See [RELEASE-PROCESS.md](RELEASE-PROCESS.md).
- Production moves only by a human-merged promotion pull request.
- Every release has a ledger entry with its post-release issues. See [RELEASES.md](RELEASES.md).
- Production is monitored by the same one-liner smoke users would run, every
  six hours, and a failure files an incident automatically.
