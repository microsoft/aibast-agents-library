---
name: aibast-easy-mode
description: Run any supported AIBAST workshop for a person from one line in GitHub Copilot Chat. The skill sets up and uses the person's Brainstem when it can, runs directly in Copilot when it cannot, and the person never has to choose.
---

# AIBAST Easy Mode

Once you have read this file (the person sent one line naming its public URL;
nothing was downloaded or attached), you own the whole workshop: discovery,
local testing, Draft deployment, Preview validation, and the evidence verdict.
If the line that pointed you here also named a solution or workshop ("…and run
the X workshop for me"), treat that as the first request and start at once.

There is one mode. The person never picks "with Brainstem" or "Copilot only";
you decide the engine yourself in the first minute (see "Pick the engine") and
never mention the choice unless they ask.

## Public source

- Repository: `microsoft/aibast-agents-library`
- Workshop branch: `main`
- Registry path: `registry.json`

Resolve the branch through the GitHub API and pin one immutable commit SHA
before downloading anything.

Persist the active run in `.aibast/easy-mode-state.json`, including solution,
revision, engine (`brainstem` or `copilot`), local test results, Copilot
Studio identity, status, and `published: false`. When the direct engine is
used, also persist the Copilot Studio plugin repository, installed plugin ID,
resolved revision or installed version, PAC CLI version, and verification
status.

## Pick the engine (you, silently, in the first minute)

Brainstem is the person's personal, on-device training AI. It works alongside
Copilot, remembers the workshop, and hot-loads specialized instructors while
Copilot remains the familiar work surface. Prefer it; fall back without fuss.

1. Check `http://localhost:7071/health`. If it answers, the engine is
   `brainstem`. Go to "Show it in VS Code".
2. If it does not answer, start or install it yourself and wait up to two
   minutes for `/health`:
   - prefer `~/.copilot/bin/brainstem start`, then `brainstem` on the PATH
   - otherwise the public installer:
     Mac or Linux `curl -fsSL https://microsoft.github.io/aibast-agents-library/install.sh | bash`,
     Windows (PowerShell) `irm https://microsoft.github.io/aibast-agents-library/install.ps1 | iex`
   - if `/health` reports Copilot is not signed in, open
     `http://localhost:7071/login` for the person and say: "Sign in with your
     GitHub account, then tell me when you're done."
3. If `/health` still does not answer (no permission to install, the port is
   held by something else, the installer failed), the engine is `copilot`.
   Record why in the state file in one line and continue. Never ask the
   person to fix it and never stop here.

## Show it in VS Code (engine `brainstem`, when you are running in VS Code)

Put the Brainstem's own folder in the Explorer so the person sees their AI as
files they own: run `code --add ~/.brainstem/src/rapp_brainstem` (Windows:
`code --add %USERPROFILE%\.brainstem\src\rapp_brainstem`), or the VS Code
command **Workspaces: Add Folder to Workspace** with that folder. Then open
`http://localhost:7071` in VS Code's built-in browser beside this chat: use
your open-browser tool if you have one, otherwise the VS Code command
**Simple Browser: Show** with that address. Say in one sentence: "This is your
Brainstem; `soul.md` is its personality and every `*_agent.py` in `agents/` is
a skill." Outside VS Code, open it in the person's normal browser instead.

## Choose from the library

When the user asks what is available, or asks for a workshop without naming
one (for example `Show me the AIBAST library, then give me the workshop I pick
using Easy Mode and test it for me`):

1. Fetch `registry.json` from the pinned commit.
2. List every entry whose `_catalog_kind` is `solution`, grouped by
   `category` written as a plain industry name, one line per workshop:
   `display_name — description`. Do not paste JSON or file paths.
3. Ask one question: which workshop they want. Accept a number, a name, or a
   description, resolve it to exactly one registry entry, and confirm the
   `display_name` back to them.
4. Continue as `Give me <solution> using Easy Mode and test it for me` with
   that entry.

Never choose for the user, and never download a workshop before they choose.

## Build and test

When the user says `Give me <solution> using Easy Mode and test it for me`:

With engine `brainstem`:

1. Resolve `@aibast-agents-library/workshop` from the immutable registry.
2. Download its exact `_file`, verify `_sha256`, and import it through
   `POST http://localhost:7071/agents/import`.
3. Send the user's request to `POST http://localhost:7071/chat`.
4. Continue executing every Brainstem handoff without asking the user to steer.
5. Brainstem's generic workshop engine must discover the requested package,
   hot-load the business agent, and run every locked local case.

With engine `copilot`:

1. Run the repository-owned, fail-closed setup step
   `python3 tools/easy_mode_preflight.py --json` and require `passed: true`.
   Stop when it exits nonzero or reports `passed: false`, and report the
   remediation it printed. Record the installed plugin/version and PAC CLI
   version in `.aibast/easy-mode-state.json`.
2. Resolve the requested solution from immutable `registry.json`.
3. Fetch its `deployment.json`, `export-manifest.json`, portable `*_agent.py`,
   `tests/demo_cases/<slug>.json`, reviewed instructions, knowledge, skills,
   Copilot Studio source, and every tool named by the manifest.
4. Verify the portable source SHA.
5. Create an isolated workspace with only required files and BasicAgent.
6. Import the class named by `deployment.json`.
7. Execute every locked case with its operation and arguments.
8. Validate every `must_include` and `must_not_include` marker.

Either way: persist `status: tested`, return the verdict with exact case
totals, and offer the next message:
`Deploy it into Copilot Studio for me.`

## Required Copilot Studio plugin (engine `copilot`, before any deployment)

The preflight owns plugin discovery, installation, and PAC remediation. Its
explicitly reviewed CLI sequence is:

1. Check whether the `mcs-assistant` Copilot Studio capabilities are already
   available.
2. If they are missing, execute these GitHub Copilot plugin-manager commands
   in order:

   ```bash
   copilot plugin marketplace add microsoft/copilot-studio-plugin
   copilot plugin install mcs-assistant@copilot-studio-plugin
   ```

3. Recheck `copilot plugin list`, then resolve
   `microsoft/copilot-studio-plugin` through the GitHub API and record
   its immutable default-branch commit SHA or the installed plugin version in
   `.aibast/easy-mode-state.json`.
4. Inspect `pac --version`, including version output from a nonzero exit. The
   plugin requires a Power Platform CLI version newer than 2.9.3. When PAC is
   too old and .NET is available, run:

   ```bash
   dotnet tool update --global Microsoft.PowerApps.CLI.Tool
   ```

   Recheck PAC and otherwise stop with the reported remediation.
5. Verify the installed plugin exposes the Copilot Studio manage, describe,
   initialize, and architect capabilities. Do not continue to deployment when
   any required capability is unavailable.

Use only `microsoft/copilot-studio-plugin` and the installed ID
`mcs-assistant@copilot-studio-plugin`. Do not substitute a fork or execute
unreviewed plugin source directly. The plugin is experimental, so validate all
generated YAML and stop on schema or PAC validation errors.

## Deploy

When the user says `Deploy it into Copilot Studio for me`:

With engine `brainstem`:

1. Send that exact request to Brainstem `/chat`.
2. Resolve `it` from Brainstem's persisted active workshop.
3. Continue every returned handoff.
4. Use the real Copilot Studio front door for Preview validation.
5. Return captured evidence to Brainstem using its callback schema.
6. Do not stop until Brainstem reports `status: complete`.

With engine `copilot`:

1. Resolve `it` from `.aibast/easy-mode-state.json`.
2. Re-verify `mcs-assistant@copilot-studio-plugin`, its recorded revision or
   version, and the required PAC CLI version.
3. Resolve the active PAC environment without asking when one is selected.
4. Use the plugin's read-only describer for an existing agent and its
   deterministic initializer only when a new target project is required.
5. Use the plugin architect to assemble or migrate the exact reviewed
   instructions, knowledge, skills, model, and modern agentic-loop YAML.
6. If the recorded schema exists, use the plugin manager to clone and
   reconnect automatically, then pull and reconcile it.
7. Remove web search and unapproved tools, then validate the generated source
   and PAC project before any remote write.
8. Use the plugin manager to push the Draft. Never invoke publish.
9. Open the real Draft and run every locked case in a fresh Preview chat.
10. Validate all markers and capture evidence.

Either way: persist `status: complete` and report exact totals, the engine
used, plugin provenance when the direct engine deployed, and
`published: false`.

## Rules

- Own all terminal, file, PAC CLI, browser, and evidence work.
- Never ask the user for URLs, environment IDs, commands, or test markers.
- Never ask the user to choose an engine, a lane, or a mode.
- Never mix assets from different Git revisions.
- Never deploy through the direct engine without the verified Microsoft
  Copilot Studio plugin and supported PAC CLI.
- Never invent a missing result or success-shaped fallback.
- Never retry until a response happens to pass.
- Stop at Draft. Never publish.
