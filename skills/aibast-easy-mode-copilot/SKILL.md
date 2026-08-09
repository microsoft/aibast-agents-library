---
name: aibast-easy-mode-copilot
description: Run supported AIBAST workshops directly through GitHub Copilot Agent mode.
---

# AIBAST Easy Mode — GitHub Copilot

Once this file is dragged into GitHub Copilot Chat in VS Code, run the complete
Easy Mode harness directly in Copilot. This skill owns discovery, local testing,
Draft deployment, Preview validation, and evidence capture.

## Public source

- Repository: `kody-w/aibast-agents-library`
- Workshop branch: `easy-mode-copilot-chat-pilot`
- Registry path: `registry.json`

Resolve the branch through the GitHub API and pin one immutable commit SHA
before downloading anything.

Persist the active run in `.aibast/easy-mode-state.json`, including solution,
revision, local test results, Copilot Studio identity, status, and
`published: false`.

## Build and test

When the user says `Give me <solution> using Easy Mode and test it for me`:

1. Resolve the requested solution from immutable `registry.json`.
2. Fetch its `deployment.json`, `export-manifest.json`, portable `*_agent.py`,
   `tests/demo_cases/<slug>.json`, reviewed instructions, knowledge, skills,
   Copilot Studio source, and every tool named by the manifest.
3. Verify the portable source SHA.
4. Create an isolated workspace with only required files and BasicAgent.
5. Import the class named by `deployment.json`.
6. Execute every locked case with its operation and arguments.
7. Validate every `must_include` and `must_not_include` marker.
8. Persist `status: tested`.
9. Return the verdict and:
   `Deploy it into Copilot Studio for me.`

## Deploy

When the user says `Deploy it into Copilot Studio for me`:

1. Resolve `it` from `.aibast/easy-mode-state.json`.
2. Resolve the active PAC environment without asking when one is selected.
3. Fetch and run the reviewed promotion tool.
4. If the recorded schema exists, clone and reconnect automatically.
5. Assemble exact instructions, knowledge, skills, and model.
6. Remove web search and unapproved tools.
7. Push the Draft. Never invoke publish.
8. Open the real Draft and run every locked case in a fresh Preview chat.
9. Validate all markers and capture evidence.
10. Persist `status: complete` and report exact totals and `published: false`.

## Rules

- Own all terminal, file, PAC CLI, browser, and evidence work.
- Never ask the user for URLs, environment IDs, commands, or test markers.
- Never mix assets from different Git revisions.
- Never invent a missing result or success-shaped fallback.
- Never retry until a response happens to pass.
- Stop at Draft. Never publish.
