# RAPP Brainstem Beta Launcher

This opt-in beta applies the launcher architecture used by Skill Recorder to
RAPP Brainstem:

- an Electron desktop window owns the local UI;
- the GitHub Copilot CLI is bundled through `@github/copilot-sdk` and connected
  over stdio with a bounded startup timeout;
- the launcher starts Brainstem as a hidden child process when port 7071 is not
  already serving it;
- an existing global Brainstem is reused rather than duplicated;
- app shutdown disposes the bundled Copilot client and only stops a Brainstem
  process that the app itself started.

The beta and the regular installer use the same global runtime:

```text
~/.brainstem/
|- src/rapp_brainstem/   shared server, agents, soul, auth, and memories
|- venv/                 shared Python environment
`- beta-launcher/        beta-only Electron, Copilot CLI, and launcher source
```

Both launch paths serve the same chat at `http://localhost:7071`. The desktop
toolbar retains **Open in VS Code**, which opens the shared
`~/.brainstem/src/rapp_brainstem` directory.

## What it is for

Use this beta as a builder-operated rapid proof harness for the customer
question: **"Can AI do this?"**

It is best when the use case is still a transcript, problem statement,
screenshot, sample document, or expected outcome. GitHub Copilot builds and
repairs the code; Brainstem is the visible test UI where you hot-load agents,
inspect tool calls, validate memory, and prove the behavior. A successful proof
produces portable single-file agents, evidence, known production gaps, and a
clear recommendation for Scout, Copilot Studio, Foundry, custom code, or no-go.

Do not position the local prototype as production. Use synthetic or approved
data, validate with a human, and move real identity, connectors, governance,
telemetry, and scale into the selected production platform.

The launcher shows this guidance on first run and keeps it available through
the **What is this?** button.

## Install

The dedicated GitHub Pages installer is published at `/beta/`. It resolves the
latest `brainstem-beta-v*` release from the fork serving the page, so staging
and production remain separate.

### Windows 11

Download [`install.cmd`](install.cmd), then double-click it. The bootstrap runs
inside the installer, creates Desktop and Start Menu shortcuts, and does not
require the user to open PowerShell to launch chat afterward.

### macOS or Linux

```bash
curl -fsSL https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/beta/install.sh | bash
```

Published releases use the Skill Recorder commit-pinned source pattern. Replace
the placeholders with the repository and full 40-character commit from the
release notes:

```bash
repo="microsoft/aibast-agents-library"
commit="<40-character-release-commit>"
curl -fsSL "https://raw.githubusercontent.com/$repo/$commit/beta/install.sh" \
  | BRAINSTEM_BETA_REPO_URL="https://github.com/$repo.git" \
    BRAINSTEM_BETA_COMMIT="$commit" bash
```

The commit appears twice deliberately: it pins both the installer being run and
the launcher plus shared Brainstem source that the installer checks out.
`BRAINSTEM_BETA_REF` remains available for mutable fork-branch testing; release
instructions use `BRAINSTEM_BETA_COMMIT`.

After the first install, launch **RAPP Brainstem Beta** from Applications,
Launchpad, the Linux app menu, the Windows Desktop/Start Menu, or run:

```bash
brainstem-beta
```

## Download boundary

The global runtime clone uses a shallow partial sparse checkout restricted to
`rapp_brainstem/`. The beta launcher uses a second shallow partial sparse
checkout restricted to `beta/`. Neither checkout downloads `solutions/`.

Both installers default to:

```text
https://github.com/microsoft/aibast-agents-library.git
```

The `BRAINSTEM_BETA_REPO_URL` and `BRAINSTEM_BETA_REF` environment variables
exist only for fork staging and release-candidate verification.

Release procedure and source-only publication rules are documented in
[`RELEASING.md`](RELEASING.md).

## Beta limitations

- This is an unsigned source-built beta, not an officially supported Microsoft
  desktop application. Managed-device controls may block Electron or downloaded
  source.
- Initial source installation still needs network access and may open a console
  while dependencies are assembled. Normal chat launch uses the desktop app and
  does not require a terminal.
- Brainstem's in-app GitHub device-code flow remains the authentication fallback.
  The launcher never stores GitHub or Copilot tokens itself.

## Uninstall the launcher

Removing the beta launcher does not remove the shared Brainstem or user data.

```bash
rm -rf ~/.brainstem/beta-launcher
rm -f ~/.local/bin/brainstem-beta
rm -rf "$HOME/Applications/RAPP Brainstem Beta.app"
rm -f "${XDG_DATA_HOME:-$HOME/.local/share}/applications/rapp-brainstem-beta.desktop"
```

On Windows, remove the two **RAPP Brainstem Beta** shortcuts and delete:

```text
%USERPROFILE%\.brainstem\beta-launcher
```
