# RAPP Brainstem Frontier

See [`GOLDEN_PATH.md`](GOLDEN_PATH.md) for the guiding product path:
learn AI, teach it back immediately as a working capability, and keep that
portable skill for life.

This opt-in Frontier experience applies the launcher architecture used by Skill Recorder to
RAPP Brainstem:

- chat remains the universal control surface for people and other AIs;
- Frontier composes global and routed single-file agents into an isolated
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

Frontier and the regular installer use the same global runtime:

```text
~/.brainstem/
|- src/rapp_brainstem/   shared server, agents, soul, auth, and memories
|- venv/                 shared Python environment
`- beta-launcher/
   |- routing/           RAPPID, stack, egg, object, and composition state
   |- recordings/        captured teaching demos
   `- src/               Frontier-only Electron, Copilot CLI, and launcher source
```

The regular installer may keep serving `http://localhost:7071`. Frontier uses
isolated loopback workers and embeds their unchanged Brainstem UI between a
live Explorer and GitHub Copilot Brain Surgeon.

## What it is for

Use Frontier as a builder-operated rapid proof harness for the customer
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

Frontier ports the proven vBrainstem Brain Surgeon pattern into the desktop
client. Open the **GitHub Copilot** tab on the right edge to reveal the full
Copilot coding-agent loop side-by-side with the live Brainstem.

This is not a second Brainstem or a simplified chatbot. It is GitHub Copilot
Agent mode with its normal file, shell, search, edit, and test loop. Frontier
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
or Brainstem chat, perform the next steps in Frontier, show the evidence,
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

## Show Mode — describe it, or show it

Some customers can describe their process; some would rather show it. **Show
Mode** (Frontier-tagged) turns a live recording, a video, a set of screenshots,
or a transcript into a single-file agent you hotload and **test in your own
Brainstem first**, then promote into Copilot Studio, Scout, Cowork, Foundry, or
custom Azure code — the tested bytes are the bytes that ship.

Open it from the **Show Mode: click-through preview** pill in the Brain Surgeon,
from the first-run intro card, or as a shareable page at `/beta/show-mode.html`.
The step-by-step walkthrough with screenshots is in
[`docs/show-mode/`](docs/show-mode/README.md).

An AI can drive the whole loop for a user through chat and let them watch. Ask
the Brain Surgeon (or the center Brainstem) to "use AI force mode" to operate the
Brainstem for you, or to `show_mode_click_through` — while it drives, the window
edges glow and a tag reads *AI force mode · an AI is driving this Brainstem —
you're watching*, so it is always clear an AI, not a hand, is at the controls.
`npm run show-mode:capture` walks the preview and saves one screenshot per step
(add `-- --force` to light force mode for a live demo).

## Install

The Download Center at `/beta/` provides operating-system and architecture
selection, release details, downloadable source commands, and installation
guidance. It resolves the latest published `brainstem-beta-v*` release from
the repository serving the Pages site, so Microsoft production and fork
staging remain separate. Microsoft is the default for local previews.

Source commands are enabled only after the selected release resolves to a
40-character commit. Both the installer URL and `BRAINSTEM_BETA_COMMIT` use that
same displayed commit; downloaded commands do not resolve “latest” again.
An optional `?tag=brainstem-beta-v<version>` selects one release. If that release
is missing or cannot be verified, the page does not substitute another release.
Repository query overrides are rejected on public sites; localhost permits
them only with a visible untrusted-test warning.

If the default live release check fails, the page offers inspectable source
resolvers, not a claim that a release or package is available. Those resolvers
check the latest published Frontier release in the same repository when run.
Without JavaScript, the source resolvers and installation details remain
available, but query-string tag selection is not applied: those resolvers
explicitly select the latest release. The Pages build includes
`download-center.js` and renders the fork's no-JavaScript links and resolver
defaults into its artifact without modifying the checked-in installers.

Packaged `.exe` or `.dmg` downloads are conditional, never guessed from a
filename or substituted from another repository. The page requires an immutable
GitHub release and exactly one fenced `rapp-frontier-release-manifest` using
`rapp-brainstem-frontier-release-manifest/v1`. Its artifact entries must match
the uploaded asset names, platforms, architectures, positive sizes, and GitHub
SHA-256 digests, and record matching release, signing, runtime, and gate
metadata. The attached manifest must match the fenced JSON bytes and its
GitHub digest. Missing or inconsistent metadata withholds packaged downloads;
source-only releases are identified without claiming that binaries exist.

These are manifest checks, not independent verification of an application
signature, native installation, or acceptance run. This page does not publish
packages or add a signing, packaged-bootstrap, or binary-update pipeline.
The current source-only release procedure remains in [`RELEASING.md`](RELEASING.md).

### Windows 11 x64

Run this in PowerShell:

```powershell
irm https://microsoft.github.io/aibast-agents-library/beta/frontier.ps1 | iex
```

The Download Center does not offer Windows ARM64 installers. Native dependency
and package validation is required before advertising that platform.

### macOS or Linux

```bash
curl -fsSL https://microsoft.github.io/aibast-agents-library/beta/frontier.sh | bash
```

The same one-liner is used every time: first install, update, repair, and launch.
The bootstrap resolves the latest published Frontier release to its immutable
40-character commit before running the platform installer.

After the first install, launch **RAPP Brainstem Frontier** from Applications,
Launchpad, the Linux app menu, the Windows Desktop/Start Menu, or run:

```bash
brainstem-frontier
```

## Check for updates

Open the three-dot **RAPP Brainstem Frontier** dropdown in the Brainstem toolbar and
choose **Check for updates**. The native application menu also exposes
**Check for Updates...**. The launcher compares its installed commit with the
latest commit on the configured GitHub branch (`main` by default).

When an update is available, **Update and Restart** runs the existing Frontier
installer against that exact commit. This refreshes both the desktop launcher
and the shared Brainstem source, runs the Frontier checks, and reopens the app.
Tracked local changes in the Frontier checkout block the update instead of being
discarded.

## Drive Frontier through chat

The source checkout includes `scripts/brainstem_ui_driver_agent.py`. The
`drive:e2e` harness sends that source through the visible GitHub Copilot Brain
Surgeon chat. Brain Surgeon supplies it to `delegate_to_brainstem` as a one-turn
ephemeral agent, and `BetaRouteManager` materializes it beside the selected
RAPPID stack without changing the shared Brainstem kernel. The agent does not
expose arbitrary JavaScript; it uses a token-authenticated loopback bridge with
bounded actions such as inspect, click, type, press, wait, read, and screenshot.

Run the update-control E2E demonstration while Frontier is open:

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
`rapp_brainstem/`. Frontier uses a second shallow partial sparse checkout
restricted to `beta/` plus the small `tools/rapp1` conformance fixture needed
by its release tests. Neither checkout downloads `solutions/`.

Both installers default to:

```text
https://github.com/microsoft/aibast-agents-library.git
```

The `BRAINSTEM_BETA_REPO_URL` and `BRAINSTEM_BETA_REF` environment variables
exist only for fork staging and release-candidate verification.

Release procedure and source-only publication rules are documented in
[`RELEASING.md`](RELEASING.md).

## Frontier limitations

- This is an unsigned source-built Frontier preview, not an officially supported Microsoft
  desktop application. Managed-device controls may block Electron or downloaded
  source.
- Initial source installation still needs network access and may open a console
  while dependencies are assembled. Normal chat launch uses the desktop app and
  does not require a terminal.
- Brainstem's in-app GitHub device-code flow remains the authentication fallback.
  The launcher never stores GitHub or Copilot tokens itself.

## Uninstall the launcher

Removing Frontier does not remove the shared Brainstem or user data.

```bash
rm -rf ~/.brainstem/beta-launcher
rm -f ~/.local/bin/brainstem-frontier ~/.local/bin/brainstem-beta
rm -rf "$HOME/Applications/RAPP Brainstem Frontier.app"
rm -f "${XDG_DATA_HOME:-$HOME/.local/share}/applications/rapp-brainstem-frontier.desktop"
```

On Windows, remove the two **RAPP Brainstem Frontier** shortcuts and delete:

```text
%USERPROFILE%\.brainstem\beta-launcher
```
