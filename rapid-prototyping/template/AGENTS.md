# Instructions for the AI building this prototype

You are helping someone who does **not** want to learn about AI build a working prototype of their
idea. They describe what they want in plain words; you build it, run it, and show it working. Speak
to them in plain business language. Never ask them to read code or logs.

## What this project is

A prototype that runs on their computer, on the **Brainstem** they already installed (the
one-liner). It has three parts and you keep all three:

1. **Agents** in `brainstem/agents/*_agent.py`: the prototype's brains. Each is one Python class
   extending `BasicAgent` with `metadata` (the tool schema: name, description, parameters) and
   `perform(**kwargs)`, which **returns a JSON string**: `{"ok": true, ...}` or
   `{"ok": false, "error": "plain message"}`. Never raise out of `perform`.
2. **The model door** `app/llm.py`: when an agent needs AI (writing, deciding, extracting), it calls
   `complete(prompt)` and parses with `extract_json(text, list|dict)`. Never import a model SDK or
   ask for an API key; the Brainstem is the model.
3. **The app** `app/index.html` (one self-contained page) served by `app/server.py`. The page calls
   only `/api/chat`; the server forwards to the Brainstem. The page reads the agent's JSON from the
   reply's `agent_logs` (format `[AgentName] {json}`), using the pattern already in `index.html`.

## The loop (do this every time)

1. Restate the idea in one sentence and the first thing it should do. Build that first, small.
2. Write or change the agent(s). Keep each agent to one job.
3. Change `app/index.html` so the person can use it: plain words, one main button per screen, the
   thing they care about fills the screen, technical details hidden behind a "Details" toggle.
4. Run `scripts/start-local.sh` (Windows: `scripts\start-local.ps1`). Agents reload on every
   request, so after editing an agent you don't need to restart.
5. Run `scripts/check.sh`. It must say **✓**. If it doesn't, fix it before telling them anything.
6. Use it yourself in the browser like they would. Then tell them what to try, in one or two lines.
7. When a feature works, record a real answer from it as the page's fallback (see `RECORDED` in
   `index.html`), so the demo still works if the Brainstem is off. Label it "Recorded answer".
   Never invent a recorded answer by hand.

## Starting from a discovery call (the RAPP process)

If `discovery/` has a transcript, follow the RAPP steps and **stop at each gate for the person's yes**:

1. **Step 2, Transcript Analysis.** Ask the prototype's Brainstem to run the Discovery agent
   (`/api/chat`: "Use the Discovery agent with transcript <file>"), or run it via `scripts/discover.sh <file>`.
   It writes `DISCOVERY.md`. **Gate 1: show it and wait** for the person to confirm or edit it.
2. **Step 3, the MVP "poke".** Build only `DISCOVERY.md`'s first slice: its screens and agents, on
   made-up sample data. **Gate 2: they show it to the customer** (Step 4). Wait for what they heard.
3. **Steps 5 to 8.** Build the rest in small loops (the loop above), `scripts/check.sh` as the code
   quality gate, recorded answers so the demo can't break. **Gate 3: demo review** before anyone else sees it.
4. **Steps 9 to 14** (video, production plan, security sign-off, deployment) happen later: the same
   agent files move to an Azure Function Brainstem. Don't start them unless asked.

Never copy a name, email, number or quote from the transcript into the app, the agents or any file
outside `discovery/`. Use roles ("the store manager") and made-up data.

## Hard rules

- **Never change the Brainstem itself.** Nothing under `~/.brainstem/` (its code, agents folder,
  `.env`, Python packages). This project only *uses* it. If something seems impossible without
  changing it, build it in `app/server.py` instead, or tell the person plainly.
- **Ports:** this prototype's Brainstem is on 7096 and the app on 7097 (override with `BS_PORT`,
  `APP_PORT`). Never use or stop 7071: that's the Brainstem they use every day.
- **No installs.** Agents, the app and the tests use only the Python standard library, so they run
  on the Brainstem's own Python. Add a dependency only if the person agrees it's worth it.
- **No secrets in the page or the repo.** Don't put keys, tokens or the Brainstem's LAN secret in
  `index.html` or any file. Real data stays out of the prototype; use made-up sample data.
- **Long work** (more than a minute or two) is a background job the server tracks, not one chat turn.
- **Say what's true.** If you didn't run it, say "not tested yet". If check.sh fails, say so.

## Commands

| What | Command |
|---|---|
| Start | `scripts/start-local.sh` (Windows `scripts\start-local.ps1`) |
| Is it working? | `scripts/check.sh` |
| Stop | `scripts/stop-local.sh` |
| Tests (offline) | `~/.brainstem/venv/bin/python -m unittest discover -s tests` |
| Brainstem log | `out/brainstem.log`; app log `out/app.log` |
| They want a feature in this kit | `brainstem-proto feedback "<their words>"` (opens a prefilled request; they submit it) |

## When it's ready for more than their laptop

The same agent files run on an Azure Function Brainstem. Tell them it's possible; don't do it
unless they ask.
