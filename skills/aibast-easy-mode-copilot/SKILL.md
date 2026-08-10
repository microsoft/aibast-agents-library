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
`published: false`. Also persist the Copilot Studio plugin repository,
installed plugin ID, resolved revision or installed version, PAC CLI version,
and verification status.

## Required local Copilot Studio plugin

Before resolving or deploying a workshop, run the repository-owned,
fail-closed setup step:

```bash
python3 tools/easy_mode_preflight.py --json
```

Stop when it exits nonzero or reports `passed: false`. Record the reported
installed plugin/version and PAC CLI version in
`.aibast/easy-mode-state.json`.

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

## Build and test

When the user says `Give me <solution> using Easy Mode and test it for me`:

1. Run `python3 tools/easy_mode_preflight.py --json` and require
   `passed: true`.
2. Resolve the requested solution from immutable `registry.json`.
3. Fetch its `deployment.json`, `export-manifest.json`, portable `*_agent.py`,
   `tests/demo_cases/<slug>.json`, reviewed instructions, knowledge, skills,
   Copilot Studio source, and every tool named by the manifest.
4. Verify the portable source SHA.
5. Create an isolated workspace with only required files and BasicAgent.
6. Import the class named by `deployment.json`.
7. Execute every locked case with its operation and arguments.
8. Validate every `must_include` and `must_not_include` marker.
9. Persist `status: tested`.
10. Return the verdict and:
   `Deploy it into Copilot Studio for me.`

## Deploy

When the user says `Deploy it into Copilot Studio for me`:

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
11. Persist `status: complete` and report exact totals, plugin provenance, and
    `published: false`.

## Rules

- Own all terminal, file, PAC CLI, browser, and evidence work.
- Never ask the user for URLs, environment IDs, commands, or test markers.
- Never mix assets from different Git revisions.
- Never deploy without the verified Microsoft Copilot Studio plugin and
  supported PAC CLI.
- Never invent a missing result or success-shaped fallback.
- Never retry until a response happens to pass.
- Stop at Draft. Never publish.
