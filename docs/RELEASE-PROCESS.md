# Release process: the staging ring

This repository ships a local AI runtime and its installer to a very large
audience through a one-line command. A broken `main` is a broken install for
everyone who runs it next. The process below is how changes reach production
without that happening, and it is deliberately simple enough to copy.

## The ring

| Ring | Repository and branch | What it serves | Who moves it |
|---|---|---|---|
| Production | `microsoft/aibast-agents-library` `main` | https://microsoft.github.io/aibast-agents-library and the public one-liner | a human, by merging one promotion pull request |
| Staging | A maintainer's fork, `staging` | The fork's Pages site and a staging one-liner that installs that fork's staging kernel | maintainers, by pull request into `staging` |
| Mirror | The same fork, `main` | nothing; a fast-forward copy of production | the sync workflow only |
| Kernel | The Grail source recorded in [`rapp/GRAIL-SPECIES.json`](../rapp/GRAIL-SPECIES.json) | the Brainstem runtime and installer this repository vendors | kernel-sync pull requests, one way, into staging |

The kernel is vendored, never forked. Every divergence from the pinned Grail
commit is listed in [`rapp/KERNEL-DRIFT.md`](../rapp/KERNEL-DRIFT.md) and the
species contract in [GRAIL-SPECIES.md](GRAIL-SPECIES.md) fails CI if the
runtime stops being compatible with the Grail. A fix that belongs to every
Brainstem user goes to the Grail first and comes back through a kernel sync.

## Gates

Every push to `staging` runs:

1. **preflight** (`.github/workflows/preflight.yml`): unit tests, contract
   checks, and the fresh, upgrade, and re-run one-liner on Linux, macOS, and
   Windows against the candidate tree.
2. **Pages deploy** (`pages.yml`): builds the slim static site, runs the
   artifact tests, and publishes staging Pages. The staging build renders the
   installers so their defaults point at the staging repository and branch;
   ring rendering does not modify the repository's installer sources.
3. **Ring one-liner smoke** (`ring-smoke.yml`): after each Pages deploy, and
   every six hours, clean runners on all three operating systems run the
   published one-liner exactly as a user would, with no environment overrides.
   It asserts the served installer targets this ring, the installed kernel
   tree equals the ring head, the kernel is the same species as the pinned
   Grail, and the server answers on `/health/public`.

The same smoke runs on production against the public Pages URL. A failure
opens an issue labelled `incident` automatically and closes it on recovery, so
a broken installer is known within hours instead of from a user report.

### Content scale

Hosted content is expected to keep growing. Preflight checks out the complete
candidate tree at depth one rather than downloading every branch's history.
The two page-preservation audits fetch their exact pinned commits with blob
filtering, retrieving historical file contents only as those audits need them.
Upgrade scenarios explicitly fetch one production-baseline snapshot and import
it into their local test origin; fresh scenarios need only the candidate.
These bounds do not remove repository content or skip source, media, or
installer checks. Pages remains a separate allowlisted artifact with its
existing size and link-integrity gates.

## Sync

`sync-upstream.yml` runs daily on the staging fork. It refuses to run if the
mirror branch has grown commits of its own, fast-forwards the mirror from
production, merges the mirror into `staging`, and dispatches the gates. A merge
conflict fails the run and changes nothing; resolve it locally and push.

## Promotion

1. Run `tools/promotion_check.sh` from the fork checkout. It infers the fork
   from `origin`; set `FORK=OWNER/REPOSITORY` to select it explicitly. It reports
   GREEN only when `staging`
   contains production and the ring head has a successful preflight, Pages
   deploy, and smoke. It never opens the pull request.
2. Open one pull request from `<fork-owner>:staging` to `microsoft:main`. Production
   preflight runs on it.
3. Merge. The next sync brings the merge back to the mirror and `staging`.
4. Add the release to [RELEASES.md](RELEASES.md) with the pull request, the
   gate evidence, and, over the following days, every issue reported against
   it. `tools/release_ledger.py <pr-number>` drafts the entry.

Kernel updates follow the same path, with one extra step: refresh
`rapp/GRAIL-SPECIES.json` and the drift ledger in the same pull request.

## Microsoft release identity

Current source downloads, support links, and production documentation target
`microsoft/aibast-agents-library`. Do not publish personal promotion or hardcode
a maintainer's fork into those surfaces. Staging derives its repository and
Pages identity from the selected fork; tests use synthetic fork owners.

Review external content dependencies separately. Do not rename a real upstream
repository to a nonexistent Microsoft repository, remove required attribution,
or rewrite a historical result as though it ran in production. An immutable
input link may move to a verified Microsoft URL only when its commit, bytes,
and SHA-256 remain unchanged.

## Workshop source integrity

Merge source improvements without transferring old native acceptance to new
bytes. Keep hash-pinned and hand-reviewed policies unchanged unless an explicit
new input revision is being prepared. Preserve incoming changes to those
policies and their screenshots as dated references rather than silently
replacing the source behind an existing result.

`tools/normalize_manual_instructions.py` normalizes routing to names read from
the packaged `SKILL.md` files. It must not copy `must_include` answers from
evaluation cases into policy, invent a skill name, or bulk-rewrite protected
input revisions. After a routing change, regenerate the native source mirror,
learner pages, and source bundle. Passing source checks is not native
Copilot Studio acceptance.

## What must never happen

- A direct push to either `main`. Production moves by promotion pull request;
  the mirror moves by fast-forward sync. Both branches block force pushes and deletion.
- A kernel edit that does not exist in the Grail and is not in the drift ledger.
- A release without a ledger entry. The ledger is how the next release learns
  from this one.
