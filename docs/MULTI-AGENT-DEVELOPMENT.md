# Developing with several AI agents at once

This repository is often changed by more than one AI agent at the same time, alongside people.
These rules keep their work from overwriting each other while it still ships and is tested together.
They apply to every agent and every person working on the staging ring.

The model is the one large open-source projects use: each change on its own topic branch, joined
only in one integration branch, and tested there (the Linux kernel's `linux-next` works this way).

## 1. One worktree per change

- Each agent works in its own git worktree, on its own branch, one pull request per worktree.
- Never let two agents edit the same folder.
- Keep worktrees in a lasting location next to the main clone (for example
  `../aibast-agents-library-wt-<topic>`), not in a temporary folder that a restart can clear.
- The main clone stays on the production branch and is not edited by agents.

## 2. Staging is the only place work meets

- Changes reach `staging` only by pull request, merged with a merge commit after the checks pass.
- Never push directly to `staging` or `main`. Never force-push a shared branch.
- Before starting, and again right before pushing, fetch `staging` and rebase onto it.

## 3. Look before touching shared files

- Before editing a shared file, list the open pull requests into `staging` and check them for the same files.
- Shared files include the Pages build, `registry.json` and its builder, `api/`, `state/`,
  `solutions/catalog.json`, and the tests.
- If another open pull request touches the same file, keep your change small and rebase after it merges. Don't race it.
- Prefer adding a new module that the shared builder calls over editing the builder itself.

## 4. Generated files are rebuilt, never merged by hand

- `registry.json`, everything under `api/`, the metrics snapshots and other generated output follow one rule.
- After a rebase, rerun the build step and commit its output.
- Never resolve a conflict in a generated file by hand.

## 5. Small pull requests with one concern

- One topic per pull request, with a plain title and a body that says what changed and how it was verified.
- Include the evidence as counts, for example "384 of 384 scenarios played"; say "unverified" for anything not exercised.

## 6. Test together, report rather than revert

- After any merge to `staging`, rerun the live checks on the staging site.
- If one change breaks another, report it on the pull request that caused it, or open an issue.
- Do not revert another agent's work on your own.
- A failing check is information. Fix the cause; never skip or weaken a check to get green.

## 7. Never in any branch

- No secrets, keys, tokens or passwords.
- No customer data or personal information.
- No content from outside this repository's own sources.

## Quick checklist for an agent

1. Create a worktree and topic branch from the latest `staging`.
2. List the open pull requests into `staging` and note any shared files they touch.
3. Make the change, and rebuild any generated files.
4. Run the tests. Record the results as N of M.
5. Fetch and rebase onto `staging`, rebuild generated files, and push the branch.
6. Open the pull request. Merge with a merge commit once the checks pass.
7. Verify the result on the live staging site, then remove the worktree.
