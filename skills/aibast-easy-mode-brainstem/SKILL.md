---
name: aibast-easy-mode-brainstem
description: Run supported AIBAST workshops through Brainstem, the learner's personal on-device training AI working alongside GitHub Copilot.
---

# AIBAST Easy Mode — with Brainstem

Once this file is dragged into GitHub Copilot Chat in VS Code, use the
Brainstem personless harness for every Easy Mode request. The user never needs
to say “with Brainstem”; this skill selection already made that choice.

Brainstem is the learner's personal, on-device training AI. Copilot remains the
familiar work surface while Brainstem persists workshop state, hot-loads
specialized instructors, and returns the final evidence verdict.

## Public source

- Repository: `kody-w/aibast-agents-library`
- Workshop branch: `easy-mode-copilot-chat-pilot`
- Registry path: `registry.json`

Resolve the branch through the GitHub API and pin one immutable commit SHA
before downloading anything.

## Build and test

When the user says `Give me <solution> using Easy Mode and test it for me`:

1. Check `http://localhost:7071/health`.
2. If Brainstem is not running, start it yourself:
   - prefer `~/.copilot/bin/brainstem start`
   - otherwise use the public Brainstem installer and start it
3. Resolve `@aibast-agents-library/workshop` from the immutable registry.
4. Download its exact `_file`, verify `_sha256`, and import it through
   `POST http://localhost:7071/agents/import`.
5. Send the user's request to `POST http://localhost:7071/chat`.
6. Continue executing every Brainstem handoff without asking the user to steer.
7. Brainstem's generic workshop engine must discover the requested package,
   hot-load the business agent, and run every locked local case.
8. Return the verdict and:
   `Deploy it into Copilot Studio for me.`

## Deploy

When the user says `Deploy it into Copilot Studio for me`:

1. Send that exact request to Brainstem `/chat`.
2. Resolve `it` from Brainstem's persisted active workshop.
3. Continue every returned handoff.
4. Use the real Copilot Studio front door for Preview validation.
5. Return captured evidence to Brainstem using its callback schema.
6. Do not stop until Brainstem reports `status: complete`.
7. Report exact case totals and `published: false`.

## Rules

- Own all terminal, file, PAC CLI, browser, and evidence work.
- Never ask the user for URLs, environment IDs, commands, or test markers.
- Never mix assets from different Git revisions.
- Never invent a missing result or success-shaped fallback.
- Never retry until a response happens to pass.
- Stop at Draft. Never publish.
