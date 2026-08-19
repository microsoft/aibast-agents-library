# RAPP UI Autosteer — `rapp-ui-autosteer/1.0`

**RAPP UI Autosteer** is the standard Frontier pattern for making any
application **AI-steerable through its own user interface**: scan the app's
HTML/UI surface, inject the minimal controller layer it is missing, embed it in
a rapplication iframe, and drive it over an explicit message bus — so the AI
operates the app exactly as a person would (same screens, same controls, same
feedback), while everything it does stays observable and evidence-backed.

This is a protocol, not a library. A rapplication conforms by implementing the
five stages and the laws below. Amend this document only in the same commit as
the behavior it standardizes (the `beta/CONSTITUTION.md` rule).

## Definitions

- **Twin** — an isolated Brainstem worker hatched by the Frontier
  (`beta/electron/twin-manager.mjs`), bound to its own `127.0.0.1:<port>`. That
  loopback origin is "the app's own origin" throughout this document.
- **Engine** — the twin's `*_agent.py`, the deterministic code behind its `/chat`.
- **Live-state sidecar** — a file the engine writes next to itself (into its own
  `AGENTS_PATH` dir) named `<name>_live_state.py` — NOT `*_agent.py`, so the
  kernel never imports it: first line a `#` comment, then exactly one JSON
  object; written atomically (`tmp` + `os.replace`, mode 0600) on every engine
  action. The kernel serves it at `GET /agents/export/<name>_live_state.py` —
  free for loopback callers, and gated for any LAN caller by the per-install
  `X-Brainstem-Secret` (only relevant when `BRAINSTEM_LAN_MODE` is on; the
  route is **not** "loopback-only", it is loopback-free and secret-gated).
- **Autosteer bus (AgenticDrive)** — the postMessage wire specified in stage 4.

Proven implementations in this tree (read them before writing a new one):

| Tier | Where the controllers enter | How the app is served | Reference |
|------|-----------------------------|-----------------------|-----------|
| **A — generation-time** | The rapplication generates the app; the bus is baked into the generated code | A local server the rapplication starts (static files + a same-origin `/chat` proxy, e.g. the studio's generated `serve.py`) | `beta/frontier/rapplications/agentic-app-studio/agentic_app_studio_agent.py` (`LOCAL_APP_HTML`); parent side in its `ui.html` |
| **B — wrap-time** | An existing app is carried (e.g. inside an `.egg`); a **copy** is surgically patched with the shims it needs | Injected over the twin's own frame (`document.write` at the twin origin) or its pop-out window | the AIdeate workshop egg pattern: AI calls re-pointed to the twin's `/chat`, live-state poller added, original app untouched |
| **C — host-injection** | The Frontier host injects a capability marker into every rapplication frame it renders | n/a (instrumentation only) | `instrumentRappUi()` / `injectFrameUi()` in `beta/electron/main.mjs` |

## The five stages

### 1. SCAN — map the operable surface
Read the app's HTML/DOM and enumerate what a person can do with it: forms,
buttons, inputs, navigation, and the feedback each action produces. Produce a
**drive map**: `intent → { control (stable selector), action, completion signal }`.
Prefer stable `id`s and `data-*` attributes; if the app lacks them, the inject
stage adds them to the copy rather than relying on brittle positional selectors.

### 2. PLAN — decide the minimal additions
For each intent, ask: can it be exercised and *observed* through the DOM alone?
Anything that cannot — async completions with no signal, internal state with no
readout, remote calls that must be re-pointed to local services — becomes a
**controller addition**. Minimal means minimal: the bus mirrors the human
surface; it never adds capabilities the UI doesn't have.

### 3. INJECT — deliver the controllers
Pick the tier. In every tier:
- the **injected bytes themselves** carry a banner comment naming what was
  added and why (source-file comments in the injector do not count — the
  declaration travels with the code);
- injection lands in a **copy, generated output, or frame** — never the user's
  original files;
- injected code runs at the app's own origin so `/chat` and asset fetches stay
  same-origin.

### 4. DRIVE — the Autosteer bus (AgenticDrive)

**Addressing.** A parent drives a specific app by posting to that iframe's
`contentWindow` (the frame *