# RAPP Brainstem Beta Launcher

See [`GOLDEN_PATH.md`](GOLDEN_PATH.md) for the guiding product path:
learn AI, teach it back immediately as a working capability, and keep that
portable skill for life.

This opt-in beta applies the launcher architecture used by Skill Recorder to
RAPP Brainstem:

- chat remains the universal control surface for people and other AIs;
- the beta composes global and routed single-file agents into an isolated
  worker `AGENTS_PATH`, then invokes them through the unchanged `/chat`;
- the included `BrainstemUiDriver` agent can operate the actual visible
  frontend with an animated cursor, clicks, typing, narration, and waits so the
  user can watch or follow along;
- an Electron desktop window owns the local UI;
- the GitHub Copilot CLI is bundled through `@github/copilot-sdk` and connected
  over stdio with a bounded startup timeout;
- the launcher starts unchanged Brainstem workers on loopback ports with
  content-addressed, hardlinked agent compositions;
- app shutdown disposes the bundled Copilot client and every worker it owns.

The beta and the regular installer use the same global runtime:

```text
~/.brainstem/
|- src/rapp_brainstem/   shared server, agents, soul, auth, and memories
|- venv/                 shared Python environment
`- beta-launcher/
   |- routing/           RAPPID, stack, egg, object, and composition state
   |- recordings/        captured teaching demos
   `- src/               beta-only Electron, Copilot CLI, and launcher source
```

The regular installer may keep serving `http://localhost:7071`. The beta uses
isolated loopback workers and embeds their unchanged Brainstem UI between a
live Explorer and GitHub Copilot Brain Surgeon.

## What it is for

Use this beta as a builder-operated rapid proof harness for the customer
question: **"Can AI do this?"**

It is also the teaching path: learn the AI pattern on real work, have Copilot
turn that learning into an agent immediately, inspect and test it visibly, and
keep the resulting skill as a portable RAPP capability.

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

The product direction is to take the user out of repetitive execution without
taking them out of understanding: the user drives by chatting, the Brainstem
delegates to agents, and visible UI actions show exactly what is being done.

## Brain Surgeon: GitHub Copilot without requiring VS Code

The beta ports the proven vBrainstem Brain Surgeon pattern into the desktop
client. Open the **GitHub Copilot** tab on the right edge to reveal the full
Copilot coding-agent loop side-by-side with the live Brainstem.

This is not a second Brainstem or a simplified chatbot. It is GitHub Copilot
Agent mode with its normal file, shell, search, edit, and test loop. The beta
adds RAPP-specific tools so that loop can:

- visibly type into the same Brainstem composer a person uses;
- submit through the same `/chat` and `/chat/stream` contract;
- inspect the same replies and `agent_logs`;
- author a single-file agent and compose it into exactly one isolated chat worker;
- remove that temporary source and bytecode when the request closes;
- operate the visible interface with an animated cursor;
- attach screenshots and recorded WebM demonstrations.

The nontechnical golden path is therefore one window: tell the Brain Surgeon
what outcome you need, watch it build or route the capability, and see the
Brainstem execute it. VS Code and GitHub CLI remain available for experts, but
they are no longer prerequisites for using GitHub Copilot as the Brainstem's
builder.

If the user gets stuck, another AI can visibly take over the same Brain Surgeon
or Brainstem chat, perform the next steps in the beta client, show the evidence,
and hand control back without losing context.

External AIs and CLIs can enter the same visible loop:

```bash
brainstem-surgeon "Build and test the capability I need"
brainstem-walkthrough
```

That command opens the right-hand panel if needed, visibly types the task into
GitHub Copilot, and waits for its answer. The recursive control path is:

```text
external AI / CLI
  -> visible Brain Surgeon chat
  -> full GitHub Copilot coding-agent loop
  -> visible Brainstem chat (/chat)
  -> one-turn routed composition and result
```

`brainstem-walkthrough` runs the complete autonomous five-minute teaching path:
it opens the Explorer, guides Brain Surgeon through identity and stack
orientation, records the shell, hotloads a one-turn teaching agent through the
center Brainstem chat, verifies cleanup, checks GitHub updates, captures the
evidence, and reports the saved WebM and screenshot. Every run is fully decoded,
sampled at five points, and added to
`~/.brainstem/beta-launcher/walkthroughs/index.html`, including failed and
historical recordings, so improvements can be watched in order.

To decode and add recordings created before this evidence index existed:

```bash
npm run walkthrough:ingest
```

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

## Check for updates

Open the three-dot **RAPP Brainstem Beta** dropdown in the Brainstem toolbar and
choose **Check for updates**. The native application menu also exposes
**Check for Updates...**. The launcher compares its installed commit with the
latest commit on the configured GitHub branch (`main` by default).

When an update is available, **Update and Restart** runs the existing beta
installer against that exact commit. This refreshes both the desktop launcher
and the shared Brainstem source, runs the beta checks, and reopens the app.
Tracked local changes in the beta checkout block the update instead of being
discarded.

## Drive the beta through chat

The source checkout includes `scripts/brainstem_ui_driver_agent.py`. The
`drive:e2e` harness sends that source through the visible GitHub Copilot Brain
Surgeon chat. Brain Surgeon supplies it to `delegate_to_brainstem` as a one-turn
ephemeral agent, and `BetaRouteManager` materializes it beside the selected
RAPPID stack without changing the shared Brainstem kernel. The agent does not
expose arbitrary JavaScript; it uses a token-authenticated loopback bridge with
bounded actions such as inspect, click, type, press, wait, read, and screenshot.

Run the update-control E2E demonstration while the beta client is open:

```bash
npm run drive:e2e
```

The harness visibly asks Brain Surgeon to hot-load the driver, type its
instruction into the Brainstem chat, send it through `/chat`, and watch the
agent animate the real dropdown. The temporary routed worker records the
window, attaches the playable WebM plus a final screenshot to chat, then is
stopped and removed in a guaranteed cleanup path.

For any workflow, the agent can use the same three-stage pattern:

1. `start_recording`
2. `run` the visible clicks, typing, waits, and reads
3. `stop_recording`

The recording is saved under `~/.brainstem/beta-launcher/recordings/` and shown
with playback controls in the agent activity attached to the chat response.

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
