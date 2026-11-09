# ORDER: one Easy Mode skill (retire the two-lane choice by aliasing)

## Intent
Kody's ruling (2026-11-08): "one mode going forward... one skill.md in the workshops as well so they
don't even need to know about the brainstem + copilot or just copilot... the skill should do both."
The single skill already exists at `skills/aibast-easy-mode/SKILL.md` (written by the cortex; do NOT
rewrite its prose; you may fix a typo). Your job is the mechanical convergence: every learner-facing
surface names ONE skill and ONE set of two short messages; the old two lane skills, the two per-solution
lane pages and the global engine switch keep working as aliases (old URLs and file paths never break),
but nothing new points at them. Tests and audit tools pin the new truth.

Style rule for anything a learner reads: no lane words ("lane", "Copilot-only", "Copilot + Brainstem",
"personless", "skeptic comparison"), no "engine" choice language. Plain business words.

## Inputs to study (read first)
- `skills/aibast-easy-mode/SKILL.md` (the one skill), `skills/aibast-easy-mode-brainstem/SKILL.md`,
  `skills/aibast-easy-mode-copilot/SKILL.md`
- `tools/scaffold_solution_journey.py` (generator of every per-solution page): `easy_mode_skill_path`,
  `render_personless_easy_markdown`, `render_easy_copilot_chat_markdown`, `render_lane_learning_steps`,
  `render_quest` (lane containers `data-easy-lane`, `engine-label`, the `aibast:workshop-engine`
  storage key in `WORKSHOP_STORAGE_SCRIPT` and the quest script), `render_field_guide`,
  `render_field_guide_html`, the README resource rows (~line 4890), the per-solution writes (~5013).
- `solutions/_shared/workshop-settings.html` (global engine switch page)
- `tools/audit_workshop_course_rollout.py` (requires both lane containers today: ~837-900, 1567, 1792)
  and `tools/apply_workshop_course_rollout.py`, `tools/audit_achievement_points.py`
- `scripts/build_pages_site.py` RING_SKILL_PATHS (~line 96)
- tests: `tests/test_easy_mode_skill.py`, `tests/test_scaffold_solution_journey.py`,
  `tests/test_workshop_course_rollout.py`, `tests/test_professional_services_solutions.py`,
  `tests/test_fs_regulatory_compliance_tutorial_package.py`, `tests/test_inventory_rebalancing_journey.py`,
  `tests/test_product_line_journey.py`, `tests/test_achievement_points.py`, `tests/test_library_workshop_entry.py`
- `docs/rapp-guide.html` / `index.html` / `academy.html`: grep for `easy-mode-brainstem|easy-mode-copilot|Copilot-only|Copilot + Brainstem`
  and converge any learner-facing mention.

## Rules / do-not-touch
- Do not edit `rapp_brainstem/`, `install.sh`, `install.ps1`, `docs/install.*`, `skill.md` (root),
  `docs/start/skill.md`, `docs/installer.html`, `docs/index.html` (another job owns those).
- Do not edit `skills/aibast-easy-mode/SKILL.md` prose beyond typos.
- Delete nothing. Old paths become aliases:
  - `skills/aibast-easy-mode-brainstem/SKILL.md` and `skills/aibast-easy-mode-copilot/SKILL.md`: keep
    their frontmatter `name:`; replace the body with a short alias notice: "This file is an alias of
    `aibast-easy-mode`. Read https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/skills/aibast-easy-mode/SKILL.md
    and follow it; it does everything this file used to do and decides the engine itself." Keep the
    frontmatter description accurate (say it is an alias). The copilot alias must not contain the
    word "brainstem" in any case (keep that invariant).
  - Per solution: generate ONE new `solutions/<slug>/EASY-MODE.md` (one skill, the two short messages,
    what happens, Draft-only boundary). `EASY-MODE-PERSONLESS.md` and `EASY-MODE-COPILOT-CHAT.md` are
    regenerated as 3-6 line aliases pointing at `EASY-MODE.md` (keep the file names and the two short
    messages inside them so old links and old tests that only check the messages still work).
  - `solutions/_shared/workshop-settings.html`: keep the page and the `aibast:workshop-engine` key
    tolerated (never crash a saved value), but the page says there is one mode now and nothing to
    choose; remove the chooser controls.
- Quest page (`render_quest` + `render_lane_learning_steps`): ONE learning path, prefix `easy`,
  one `download="SKILL.md"` button for `skills/aibast-easy-mode/SKILL.md`, no `data-easy-lane`
  containers, no `engine-label` spans, no lane notice/comparison note. Achievement checkpoints keep
  the same groups (`onboarding`, `local-proof`, `draft-builder`, ...) with prefix `easy`; the quest
  script must still read an old saved `aibast:workshop-engine` value without error and ignore it.
  Keep the Easy/Manual tab switch exactly as is. Keep `tools/audit_achievement_points.py` green
  (update its expectations if they count per-lane checkpoints).
- Field guide (md + html), README resource rows, export manifests, `scripts/build_pages_site.py`
  RING_SKILL_PATHS, `tools/audit_workshop_course_rollout.py`, `tools/apply_workshop_course_rollout.py`:
  one skill (`skills/aibast-easy-mode/SKILL.md`), one guide (`EASY-MODE.md`); the aliases may still be
  listed as "alias of" rows but not as choices. The ring builder must render the new skill's
  `- Repository:`/`- Workshop branch:` lines like it does the old ones (add the path; keep the old two).
- Tests: rewrite the pinned assertions to the new truth (one skill, one lane, aliases present and
  pointing correctly, `brainstem` absent from the copilot alias, no `data-easy-lane`, exactly one
  `download="SKILL.md"` in quest, prompt counts recomputed). Add `tests/test_one_easy_mode.py` that
  pins: the one skill's frontmatter name, "Pick the engine" section, both engines' build/test and
  deploy steps, `published: false`, `Never publish`, `Never ask the user to choose an engine`;
  both alias skills point at the new path; every `solutions/*/EASY-MODE.md` names the new skill and
  the two short messages; no `solutions/*/quest.html` contains `data-easy-lane`.
- Regenerate all 72 solutions with `python tools/scaffold_solution_journey.py <slug>` (use
  `~/.brainstem/venv/bin/python`; it is idempotent today: proven on win-loss-analysis, 0 diff lines).
  If a slug refuses without `--allow-pending`, report it; do not pass `--allow-pending` silently.
- Then `~/.brainstem/venv/bin/python scripts/apply_design_tokens.py` (stamps regenerated pages) and
  `--check` must be clean.
- Commit on the current branch `feat/one-easy-mode` in this worktree in 2-4 logical commits
  (skill aliases + generator; tests; regenerated solutions; tooling). Do NOT push.

## Acceptance checks (run verbatim, paste outputs in the report)
1. `~/.brainstem/venv/bin/python -m pytest tests -q -p no:cacheprovider 2>&1 | tail -3`  -> all pass (today: 2894 passed, 2 skipped).
2. `~/.brainstem/venv/bin/python scripts/apply_design_tokens.py --check | tail -1`
3. `~/.brainstem/venv/bin/python tools/audit_workshop_course_rollout.py 2>&1 | tail -5` (find its real CLI first; report what it prints)
4. `~/.brainstem/venv/bin/python tools/audit_achievement_points.py 2>&1 | tail -3`
5. `grep -rl 'data-easy-lane' solutions/*/quest.html | wc -l` -> 0
6. `grep -L 'skills/aibast-easy-mode/SKILL.md' solutions/*/EASY-MODE.md | wc -l` -> 0
7. `grep -rn -i 'copilot-only\|Copilot + Brainstem\|personless\|skeptic comparison' solutions/*/quest.html solutions/*/EASY-MODE.md solutions/*/field-guide.html solutions/*/FIELD-GUIDE.md solutions/*/README.md | wc -l` -> 0
8. `grep -ci brainstem skills/aibast-easy-mode-copilot/SKILL.md` -> 0
9. `for s in $(ls -d solutions/*/deployment.json | cut -d/ -f2); do ~/.brainstem/venv/bin/python tools/scaffold_solution_journey.py $s >/dev/null || echo FAIL $s; done; git status --short | wc -l` -> second regeneration is a no-op (0 after commit)
10. `git log --oneline fork/staging..HEAD`

## Done-when + report
All ten checks pass with the outputs pasted verbatim. End with:
- what changed (files/dirs, counts),
- the ten outputs,
- FLAGS / SURPRISES: anything you had to guess, any test you weakened rather than re-pinned (name it),
  any learner-facing sentence you wrote (list them; the cortex rewrites prose),
- `Resume:` line.
