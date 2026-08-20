# Chat look — "works like my phone" by default, Business as a toggle

Kody, 2026-08-20: *"make the full feel work like iMessage, then the nice business UI as an
optional toggle from its current state. It's a UI/UX thing — then we don't have to even train
people because they just know how it works because it works like my phone. Nothing else should
change — just the theming."*

Two looks, one toggle, Frontier only (the Grail kernel UI is never edited; the Frontier's frame
bridge restyles it from inside the iframe; the Surgeon panel is ours). **Theming only**: no new
cues, no new behavior, no changed functionality — the one behavioral piece is the typing-bubble
delivery Kody asked for separately (hold the reply, show typing, pop the whole message).

| | **Messages** (default) | **Business** (today's look) |
|---|---|---|
| Bubbles | user right, blue, with tail; assistant left, gray, with tail; no avatars in the thread; consecutive messages from one side group tightly (tail on the last only) | as today |
| Shape / type | 18 px radius, system font, 15–16 px | as today |
| Arrival | the reply is held while it is produced; a gray **typing bubble with three dots pulsing in sequence** (opacity — no bounce) stays up the whole time, including agent tool rounds; then the complete message **pops** in one paint with a short scale-in | token streaming |
| Composer | the same field and button, styled as a rounded pill and a round up-arrow send button — same behavior | as today |
| Markdown | unchanged (headings, lists, code render inside the bubble) | unchanged |
| Agent activity | unchanged disclosure, styled to the bubble | unchanged |
| Motion | respects `prefers-reduced-motion` (no pulse, no scale-in) | — |
| Colors | dark: user `#0A84FF`, assistant `#3A3A3C`; light: `#007AFF`, `#E9E9EB`; follows the app theme | as today |

Explicitly **not** part of this: delivered/read receipts, timestamps, disabling the composer,
sounds, or any change to menus, commands, agent logs, exports, or the kernel.

## The toggle

- **Where**: the three-dot **RAPP Brainstem Frontier** dropdown in the Brainstem toolbar gains
  *Chat look ▸ Messages / Business*; the native application menu mirrors it.
- **Persistence**: `settings.json` in the beta home (`chatLook: "messages" | "business"`), read
  at startup, changed over the existing trusted IPC, applied live to the Brainstem frame and the
  Surgeon panel without a reload. Env override for scripts and tests:
  `RAPP_CHAT_LOOK=business|messages`. `RAPP_CHAT_TYPING=0` still disables the hold/pop alone.
- **Default**: Messages. Business is exactly the current rendering — the toggle restores it
  byte-for-byte (no CSS injected, no stream hold).

## How it is built (Frontier only)

- **Brainstem frame**: the bridge injects one `<style>` block and sets `data-rapp-look` on the
  frame's `<html>`; selectors target the Grail's existing classes (`.msg.user`, `.msg.assistant`,
  `.bubble`, `.avatar`, `.typing-indicator .typing span`, `#input`, `#send`). The stream hold is
  the bridge's `/chat/stream` buffering. Nothing in `rapp_brainstem/` changes; a bare Brainstem
  outside the Frontier looks as it always did.
- **Surgeon panel**: the same rules on our own markup; the typing delivery state machine pops
  complete replies.
- **Twin tiles**: same look where they render chat.

## Done means

The regression harness's `/drive` timeline for a long reply reports *typing bubble visible →
distinct reply sizes observed while arriving: 1* under Messages and *many* under Business; the
toggle round-trips; screenshots of both looks are attached to the PR.
