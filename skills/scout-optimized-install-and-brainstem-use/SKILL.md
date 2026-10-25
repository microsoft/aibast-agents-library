---
name: scout-optimized-install-and-brainstem-use
description: Install, repair, start, open, and use the local RAPP Brainstem entirely through Microsoft Scout without asking the user to operate a terminal.
---

# Scout-Optimized Install and Brainstem Use

Use this skill when a Microsoft Scout user asks to install, update, repair,
start, open, or use the local RAPP Brainstem, including requests that reference
`https://aka.ms/rappinstall`.

Scout owns the shell and browser work. Do not ask the user to open Terminal,
PowerShell, or run an installer command.

## Safety and scope

- A request to install, update, reinstall, or repair is approval for that
  operation.
- Before changing the machine, explain that installation may write under
  `~/.brainstem`, `~/.local`, `~/.copilot`, and Copilot plugin configuration.
- Preserve the user's soul, agents, memories, environment configuration, and
  local data through the installer's update and repair paths.
- Treat local Brainstem GitHub Copilot authentication and Microsoft 365
  authentication as separate domains. Installing Brainstem does not grant MSX
  or Microsoft 365 access.
- A local install request never authorizes Azure deployment. If
  `https://aka.ms/rappinstall` resolves to content describing Azure resources,
  do not run the Azure deployment commands.

## Install or repair

1. Open `https://aka.ms/rappinstall` in the visible browser and inspect the
   resolved HTTPS location.
2. Check `http://localhost:7071/health`.
3. If Brainstem is healthy, record its version and loaded agents. Update or
   repair it only when the user requested that operation.
4. If installation is required, use the AIBAST local installer:
   - macOS or Linux:
     `curl -fsSL https://microsoft.github.io/aibast-agents-library/install.sh | bash`
   - Windows PowerShell:
     `irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.ps1 | iex`
5. Prefer `~/.copilot/bin/brainstem start` when the policy-clean launcher is
   available. Otherwise start the installed Brainstem launcher.
6. Poll `http://localhost:7071/health` with a bounded wait. An installer exit
   code without a healthy endpoint is not success.

The installers own prerequisite discovery and the isolated Python environment.
Do not tell the user to install Python, Git, GitHub CLI, Homebrew, or another
package manager unless the installer returns an explicit unrecoverable error.

## Authentication

When Brainstem requires GitHub Copilot authentication:

1. Open the Brainstem login flow visibly in the user's browser.
2. Let the user complete the GitHub device-code approval.
3. Recheck `/health` and exercise `/chat`; do not infer authentication from the
   browser redirect alone.

Never claim this GitHub authentication also authenticates Microsoft 365.

## RAR integration

When the Copilot CLI supports plugins, install or refresh the RAR projection:

```text
copilot plugin marketplace add kody-w/RAR
copilot plugin install rapp@rar
```

Start a new Scout or Copilot conversation before checking that `rapp-skills`
was discovered.

## Open and use Brainstem

After health is green:

1. Open `http://localhost:7071` in the user's normal browser, not only in an
   automation-only browser context:
   - macOS: `open http://localhost:7071`
   - Windows: `Start-Process http://localhost:7071`
   - Linux: `xdg-open http://localhost:7071`
2. Send a real request through `POST http://localhost:7071/chat` using the JSON
   field `user_input`.
3. Require HTTP success and a non-empty `response` field.
4. Report the observed version, loaded agents, browser URL, and chat result.

## Acceptance contract

The workflow is complete only when:

- `/health` returns HTTP 200 with `status: "ok"`;
- the response identifies the installed version and loaded agents;
- a real `/chat` request returns its answer in `response`;
- the Brainstem chat is open in the user's normal browser;
- RAR is installed and a new conversation discovers `rapp-skills`, when the
  host supports Copilot plugins; and
- no Azure resources were provisioned.
