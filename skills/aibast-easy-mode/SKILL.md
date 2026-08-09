---
name: aibast-easy-mode
description: Run any supported AIBAST workshop from GitHub Copilot Agent mode. Default to the Brainstem personless harness, or run the Copilot-only comparison when the user explicitly asks for it.
---

# AIBAST Easy Mode

This file is the shared entry point for both Easy Mode lanes. Once the user
drags `SKILL.md` into GitHub Copilot Chat in VS Code, own the rest of the
workshop without asking them for repository URLs, terminal commands,
environment IDs, test markers, or deployment mechanics.

## Mode selection

- **Default:** Brainstem + Copilot personless harness.
- **Copilot-only comparison:** use only when the user explicitly says
  `without Brainstem`, `Copilot only`, or equivalent.
- Persist the selected mode and active solution in
  `.aibast/easy-mode-state.json`.
- When the user later says `Deploy it into Copilot Studio for me`, resolve `it`
  from state. Never ask them to repeat the solution name.
- Stop at Copilot Studio **Draft**. Never publish.

## Public source

- Repository: `kody-w/aibast-agents-library`
- Workshop branch: `easy-mode-copilot-chat-pilot`
- Registry path: `registry.json`

Resolve the branch through the GitHub API and pin one immutable commit SHA
before downloading anything. Use the registry and files from that same
revision. Never mix mutable branch-cached assets.

## Shared rules

- Discover and retrieve every public asset yourself.
- Own terminal commands, file operations, PAC CLI calls, browser actions, and
  evidence collection.
- Never ask the user to open a terminal, run a command, find a URL, clone a
  repository, or install a dependency themselves.
- Never invent a missing file, connection, test result, or production outcome.
- Stop loudly on integrity or execution failures. Do not produce a
  success-shaped fallback.
- Never retry until a response happens to pass.
- Completion requires local locked cases, real Copilot Studio Preview cases,
  Draft state, and `published: false`.

# Default lane — Brainstem + Copilot

Use this lane whenever the user asks for Easy Mode without an explicit
Copilot-only qualifier. Treat Brainstem as the learner's personal, on-device
training AI: it persists the workshop state, hot-loads specialized instructors,
and works alongside GitHub Copilot while Copilot remains the familiar work
surface.

## Start or acquire the engine

1. Check `http://localhost:7071/health`.
2. If Brainstem is not running, start it yourself:
   - prefer `~/.copilot/bin/brainstem start` when available
   - otherwise run the public Brainstem installer and start it
3. Resolve `@aibast-agents-library/easy-mode` from the immutable
   `registry.json`.
4. Download the exact `_file`, verify `_sha256`, and import it through
   `POST http://localhost:7071/agents/import`.
5. Confirm `/health` lists `AIBASTEasyModeAgent`.

## Build and test

When the user says `Give me <solution> using Easy Mode and test it for me`:

1. Send the same request to `POST http://localhost:7071/chat`.
2. Continue executing every handoff Brainstem returns.
3. Brainstem's Easy Mode agent must:
   - remember the active solution
   - hot-load the task-specific workshop cartridge
   - verify its pinned hash
   - hot-load the business agent
   - run every locked local case
4. Return only the verdict and the next short message:
   `Deploy it into Copilot Studio for me.`

## Deploy

When the user says `Deploy it into Copilot Studio for me`:

1. Send that exact request to Brainstem `/chat`.
2. Continue through every returned handoff without asking the user to steer.
3. Use the real Copilot Studio front door or configured browser tools for
   Preview validation.
4. Return the captured evidence to Brainstem using the callback schema it
   provides.
5. Do not stop until Brainstem returns `status: complete`.
6. Report the final Brainstem verdict, including case totals and
   `published: false`.

# Comparison lane — GitHub Copilot only

Use this lane only when the user explicitly asks for Easy Mode without
Brainstem. The same attached skill becomes the harness, but Copilot performs
the engine work directly.

## Persistent state

Record:

- `mode: copilot-only`
- immutable source revision
- active solution package name and slug
- deployment recipe and portable source
- local case totals and results
- Copilot Studio project, environment, schema, and bot ID
- current status: `tested`, `awaiting_front_door_validation`, or `complete`
- `published: false`

## Build and test directly

1. Resolve the requested solution from immutable `registry.json`.
2. Fetch:
   - `deployment.json`
   - `export-manifest.json`
   - the portable `*_agent.py`
   - `tests/demo_cases/<slug>.json`
   - reviewed instructions, knowledge, skills, Copilot Studio source, and any
     tool named by the manifest
3. Verify the portable source SHA from registry or transcript evidence.
4. Create an isolated workspace with only the required source and shared
   BasicAgent dependency.
5. Import the class named by `deployment.json`.
6. Execute every locked case with its operation and arguments.
7. Check every `must_include` and `must_not_include` marker.
8. Persist `status: tested` and the active solution.
9. Return the verdict and:
   `Deploy it into Copilot Studio for me.`

## Deploy directly

1. Resolve the active solution from state.
2. Resolve the active PAC environment without asking when one is selected.
3. Fetch and run the reviewed promotion tool.
4. If the recorded schema already exists, clone and reconnect automatically.
5. Assemble exact instructions, knowledge, skills, and model.
6. Remove web search and unapproved tools.
7. Push the Draft. Never invoke publish.
8. Open the real Copilot Studio Draft and run every locked case in a fresh
   Preview conversation.
9. Validate required and forbidden markers and capture evidence.
10. Persist `status: complete` and report the verdict.

# Completion contract

Both lanes are complete only when:

- every downloaded asset comes from one immutable revision
- the source hash matches
- every local locked case passes
- the Copilot Studio source is synchronized
- every real Preview case passes
- the agent remains Draft
- `published` is exactly `false`
