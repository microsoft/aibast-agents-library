---
name: workshop-nightly-pilot
version: 1.0.0
description: Pilot an AIBAST industry-solution workshop end-to-end in a live Copilot Studio environment -- build the agent, run every demo prompt fresh, capture real screenshots, fix annotation boxes, file real product bugs -- then rotate to the next solution. Designed to be re-run nightly against all solutions/* workshops.
homepage: https://microsoft.github.io/aibast-agents-library/
metadata: {"emoji":"","category":"qa","repo":"https://github.com/microsoft/aibast-agents-library"}
---

# Workshop Nightly Pilot

This is the repeatable runbook for testing an AIBAST workshop **like a student, against the real
product**, not just reviewing existing screenshots. It was built by piloting
`solutions/account-intelligence` end-to-end (see PR #206 and issue #204), which found a real,
reproducible Copilot Studio bug (AI-02/AI-06 skipped knowledge retrieval on the first turn of a
fresh chat, then passed on retry). Every subsequent solution should get the same treatment.

**Why this exists**: annotation-box QA (fixing misaligned green highlight boxes on existing
screenshots) is a *different, smaller* job than this one. That pass was done across all 51 other
solutions in PRs #207-#216 and only touched already-`reusable` screenshots. It never rebuilt an
agent, never re-ran a demo prompt, and never caught a live product regression. This skill is what
actually re-validates the product, not just the pictures of it.

## Instructions for Copilot

Execute these steps autonomously. Pause only where marked ⏸.

### Step 0: Load rotation state

Read `solutions/_shared/pilot-rotation-state.json`. It tracks, per solution: `status`
(`pending` / `piloted` / `no_checkpoints_file` / `blocked`), `reshoot_required_count` at last
scan, `last_piloted` date, `environment_agent_name` used, and `issues_filed`.

Pick the next batch to work (default `default_batch_size_per_run` from the state file, currently
2) using this order:
1. `status == "pending"`, highest `reshoot_required_count` first (biggest gaps get fixed sooner).
2. Skip `status == "no_checkpoints_file"` entries -- flag them in your report but do not invent a
   checkpoints file from scratch; that's a separate authoring task, not a pilot.
3. Once every `pending` entry has been piloted, reset the whole rotation: set every `piloted`
   entry back to `pending` (a fresh nightly regression pass), bump a `full_cycles_completed`
   counter at the top level, and start again from #1. This is what makes it a **nightly** loop
   instead of a one-time backlog burn-down.

### Step 1: Connect the browser ⏸

Browser automation tool policy requires explicit user browser selection before any browser
action -- call `list_connected_browsers`, then **you must ask the user** (via the ask-user
mechanism) to pick one from the full list, or to use the "confirm in every connected extension"
option. Do not skip this or guess a browser. If no user is available to answer (e.g. this is
running unattended overnight), stop here, leave the current solution's state entry unchanged, and
end the run -- do not proceed with browser automation without an explicit selection.

### Step 2: Build or resume the agent in Copilot Studio

Target environment: `4d056638-8d62-e0b7-aa17-c549d01f711b` (same one used for
account-intelligence; reuse it unless told otherwise).

For the chosen solution, open `solutions/<name>/quest.html` and follow its manual-mode build
steps (name, global instructions, knowledge uploads, skill uploads) **exactly as a student would**,
using the real customer-facing agent name from the solution's metadata -- never a test/`WSTEST-`
prefix, since these become real workshop screenshots.

Known environment quirks (from the account-intelligence pilot, still true as of 2026-09):
- **Typing collisions**: the `computer` "type" action can land in the wrong field when two text
  areas are close together (e.g. title vs. instructions). Prefer `form_input` for plain inputs;
  for rich-text panels, scope a JS `Range`/`Selection` to the specific DOM element before typing.
- **File uploads**: `file_upload` no longer accepts host filesystem paths, even under this
  session's own `files/` folder, despite its schema still listing `paths`. Use
  `javascript_tool` instead: read the file, base64-encode it, then in-page do
  `atob(base64) → Uint8Array → new File([bytes], name, {type}) → new DataTransfer().items.add(file)
  → input.files = dt.files → dispatch 'change'/'input' events` on the actual file `<input>`
  located via `find`. This has been the reliable method across all pilots so far.
- **Chat auto-scroll race**: the Preview chat pane can auto-scroll to bottom on a re-render
  unrelated to your actions. A `scroll` immediately followed by `screenshot` in the *same* tool
  call can still show the wrong position on the *next* call. **Reliable fix**: `find` the target
  heading/text to get a stable element ref, then `scroll_to` with that ref, then screenshot in the
  same or immediately following call. Do not trust a screenshot taken after a bare `scroll`.

### Step 3: Run every demo prompt fresh, more than once

For every locked demo prompt (the assisted-mode `easy-*` cases and the hard-mode `hard-step-*`
manual cases), run it **twice**: once starting a brand-new chat (`New chat`), and once more
immediately after. Account-intelligence's real bug (AI-02, AI-06) only showed up on the *first*
message of a *fresh* chat and disappeared on retry -- a single run would have missed it entirely.
If a case fails on the first try but passes on retry, that is not noise -- it is a real,
reproducible product bug. File it as a GitHub issue (see `gh issue create --repo
microsoft/aibast-agents-library`) with the exact repro steps, screenshots of both the failing and
passing runs, and a title following the pattern of issue #204.

### Step 4: Capture and annotate screenshots

For every checkpoint in `solutions/<name>/evals/visual-checkpoints.json` (both `easy-*` assisted
cases and `hard-step-*` manual cases), capture a fresh screenshot showing the real, current state
of the product -- not a reused old one. Replace the `source` file.

Annotation house style (established across account-intelligence and PRs #207-#216, keep it
consistent):
- Box: `rounded_rectangle`, outline `(22, 163, 74)` / `#16A34A`, width 3, radius 6.
- Label pill: same green, filled, radius 6, white bold text, font
  `/System/Library/Fonts/Supplemental/Arial Bold.ttf`, normally ~15pt with ~10px/~6px padding.
- Pill placement: fully **above** the box with a small gap, touching or barely overlapping only
  the box's own top border -- never over any other text or UI. If the whitespace gap above the
  box is too small (a very common case right after a heading with little breathing room), shrink
  to an ~11-12pt font with ~1-3px padding and re-measure the actual gap (end of the text line
  above, to the top of the box) before placing it. If there's still no room above, place it
  directly below the box using the same tight-fit measurement against whatever comes next.
- Never let a box border cross through the text it's supposed to highlight (STRIKETHROUGH), never
  let a box float over blank space that doesn't contain the claimed content (FLOATING), and never
  let the label claim something the image doesn't actually show (SEMANTIC_MISMATCH -- e.g. boxing
  a generic page header present in every screenshot and claiming it proves a save happened).
- To measure text bounds precisely: convert the raw screenshot to grayscale, threshold `<140`,
  and scan rows/columns for dark-pixel counts in the region you've already visually identified.
  This is a ruler for coordinates you already know are right from looking at the image -- never a
  substitute for looking at the image yourself, before and after the fix.
- **Always re-view the regenerated PNG yourself before moving on.** Declaring a fix without
  re-viewing it caused multiple false "done" reports during the account-intelligence pass -- do
  not repeat that mistake here.

Update the capture's `boxes`, `status` (`reshoot_required` → `reusable` once verified), and
`note` field in `visual-checkpoints.json` to match exactly what the new PNG shows.

### Step 5: Commit, PR, and update rotation state

- Work in an isolated git worktree branched directly from a freshly-fetched `origin/main` (never
  local `main` -- this repo's shared checkouts have had divergent/stale local history before;
  always verify you're not pulling in unrelated commits before pushing).
- One commit per solution touched. Push to a branch named
  `workshop-pilot/nightly-<solution>-<yyyy-mm-dd>` and open a PR scoped to just that solution.
- Update `solutions/_shared/pilot-rotation-state.json` for every solution you touched this run:
  set `status: "piloted"`, `last_piloted` to today's date, `environment_agent_name` to the real
  agent name used, `reshoot_required_count` to the new (should-be-zero-or-lower) count, and append
  any filed issue URLs to `issues_filed`. Commit this state update as part of the same PR (or a
  small follow-up commit on `main` directly if the rotation file itself has no merge conflicts --
  use judgment, but don't leave the tracker stale).

### Step 6: Report

Summarize, per solution piloted this run: how many checkpoints were re-captured, how many
annotation defects were fixed, any product bugs found and their issue links, and the PR URL. Note
which solutions remain `pending` and roughly how many nights at the current batch size it will
take to finish a full cycle.

## Scheduling this nightly

A recurring schedule should invoke this skill once every 24 hours with a prompt like:

> Load the workshop-nightly-pilot skill from
> `solutions/_shared/workshop-nightly-pilot-skill.md` and run it now: pick the next batch from
> `solutions/_shared/pilot-rotation-state.json`, pilot each live, fix screenshots, file any real
> bugs found, commit/PR, update the rotation state, then stop and report.

If no browser is available when the schedule fires (Step 1 pause), the run should end early
without corrupting the rotation state, and simply try again at the next scheduled tick.
