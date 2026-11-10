# ORDER F: the Windows 11 practice computer becomes the stage of "Get an agent running"

Branch feat/start-rethink (checked out; it holds round 4 plus a draft start.html with a small walkthrough window).
Owner's words: "what happened to the full windows 11 os concept. for the full tutorial end to end so we can even
simulate them bringing up the terminal and pasting the one liner". Owner's pick: "practice computer is the stage,
watch mode plus click-through".

## What exists (read first, completely)
- docs/practice/windows.html: a pretend Windows 11 desktop with 8 click-through steps (Start, Find PowerShell, Paste
  the line, Sign in, Say hello, Browse the library, Open VS Code, Copilot sets it up). Owner-authored: do not restyle
  or reword it; reuse it.
- start.html (this branch): header, agent picker, three numbered steps with the copy line, "What you need", details,
  #office-hours, and a small `.walk` window whose script (`play`, `story`) plays the Copilot chat conversation and a
  Copilot Studio scene for the chosen agent. The conversation wording is taken from solutions/<slug>/SKILL.md and
  must stay truthful to it.
- tools/first_minute_check.py (J1-J35) and its tests: the judge. solutions/_shared/solution-journey.js: getLine().

## Build
1. ONE desktop engine, two hosts. Move the practice computer's desktop (markup, styles, step logic) into shared
   files (for example solutions/_shared/practice/desktop.{css,js}) that BOTH docs/practice/windows.html and
   start.html load. docs/practice/windows.html must look and behave exactly as today (prove with before/after
   screenshots of all 8 steps and an automated click-through of all 8). No second copy of the desktop.
2. On start.html the desktop replaces the small `.walk` window as the stage: it fills the width of the main column
   above the fold on desktop (the page is a thin frame around it), with the three numbered steps + Copy beside it
   (>= 1100px) or under it. Phone (<= 900px): steps and Copy first (Copy must stay on the first screen at 390x844
   and 360x640), the desktop below at full width, readable (no 6px text: on narrow screens show the active window
   maximised inside the desktop rather than shrinking the whole desktop).
3. Two modes, one control row under the stage: "Watch" (default; plays by itself, a visible pointer moves and
   clicks, captions in plain words) and "Try it yourself" (the existing click-through with its "Show me where").
   Pause / Play again. Under prefers-reduced-motion: no autoplay, no moving pointer; steps advance on click.
4. Two chapters, shown as two labelled groups in the step list:
   Chapter A "Set up your computer" = the existing 8 steps unchanged (terminal, the one-liner, sign in, say hello,
   VS Code). Chapter B "Get your agent" (new, 4 steps) for the agent chosen in the picker:
   B1 open GitHub Copilot chat in the pretend VS Code; B2 the setup line (exactly getLine() for that agent) is
   pasted and sent; B3 Copilot's conversation, in the words already in start.html's `play` (sign in with your
   Microsoft account, "I will add <agent> to your Copilot Studio, with sample data. Go ahead?", "Yes", "Done...");
   B4 a pretend Edge window opens Copilot Studio, the agent's test chat shows that agent's first sample question
   and an answer placeholder labelled as sample data.
   A visitor arriving on start.html starts at Chapter B by default with a visible, quiet control
   "Start from the beginning (set up your computer)" that plays Chapter A first. Changing the picker restarts
   Chapter B with the new agent's line and question.
5. Put the path back: the practice computer must be reachable in one click from start.html (the "Try it yourself"
   mode is that) and from docs/installer.html (keep its existing link).
6. Judge: ADD checks (do not change J1-J35 or targets):
   J36 `stage_is_desktop`: start.html shows the pretend desktop (taskbar + Start button visible) occupying at
   least 55% of the viewport width at 1440x900; exactly one desktop engine file is loaded by both pages.
   J37 `watch_mode_plays`: with no interaction, within 25s Chapter B reaches the Copilot Studio scene and shows the
   chosen agent's name and first sample question; the pasted line equals the copy block's text.
   J38 `try_mode_completes`: in "Try it yourself", an automated click-through using only the highlighted targets
   completes Chapter A's 8 steps and Chapter B's 4 steps.
   J39 `practice_page_unchanged`: docs/practice/windows.html click-through of its 8 steps still completes and its
   visible step texts equal the texts recorded from fork/staging (record them in the test).
   J40 `stage_phone_readable`: at 390x844 the smallest visible text inside the stage is >= 11 CSS px effective.
   J41 `reduced_motion_stage`: under reduced motion nothing advances for 6s without a click.
   Show them failing before, passing after. `--gate` must exit 0 with J1-J41.
## Rules
Hand-authored static files, no new dependencies, no emoji, professional Microsoft tone, no real Windows or Microsoft
logo artwork beyond what windows.html already draws. No time claims. Do not touch rapp_brainstem/, install.*,
docs/install.*. Update (never delete or weaken) tests that pin things you changed on purpose and list them.
Regenerate generated files CI checks. Commit after each numbered item passes. Never push.
## Acceptance (paste verbatim)
1. FAIL table for J36-J41 before; 2. `~/.cache/aibast-reshoot/venv/bin/python tools/first_minute_check.py --gate` exit 0;
3. `~/.cache/aibast-reshoot/venv/bin/python -m pytest tests -q` last line; 4. screenshots in ./_shots/stage/: start.html
1440x900 at Chapter B steps 1-4, Chapter A terminal step with the one-liner pasted, 390x844 first screen and stage,
practice page before/after for 2 steps; 5. `git log --oneline fork/staging..HEAD`.
## Report
What was built, how the desktop was shared, tests changed and why, "flags / surprises".
