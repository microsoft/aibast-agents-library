# Roadmap

Track issues and pull requests in the
[Microsoft repository](https://github.com/microsoft/aibast-agents-library/issues).
Forks provide staging environments, not a separate product roadmap. The table
below describes release objectives, not a live completion-status snapshot;
use the linked issues, pull requests, and release gates for current status.

| Objective | Outcome |
|---|---|
| M1 Staging ring live | Fork `main` mirrors production automatically; `staging` serves the fork Pages; every staging push is preflighted, deployed, and smoked |
| M2 Vendored one-liner on staging | The staging Pages one-liner installs this repository's own kernel at the staging ref on clean Linux, macOS, and Windows runners |
| M3 Grail species regression | Species contract and drift ledger in CI; installer fixes that belong upstream returned to the Grail |
| M4 Academy promotion | Microsoft AI Academy promoted from staging to production after soaking on the ring |
| M5 v1 GA blockers | Upstream licensing, Discussions and metrics token on the Microsoft repository, Microsoft-owned auth worker |

Principles that do not change between milestones:

- The kernel is vendored from the Grail and updated one way. This repository
  grows around it, never inside it. See [RELEASE-PROCESS.md](RELEASE-PROCESS.md).
- Production moves only by a human-merged promotion pull request.
- Every release has a ledger entry with its post-release issues. See [RELEASES.md](RELEASES.md).
- Production is monitored by the same one-liner smoke users would run, every
  six hours, and a failure files an incident automatically.
