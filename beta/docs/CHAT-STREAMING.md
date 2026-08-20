# Frontier chat streaming

Frontier keeps the unchanged Brainstem `/chat/stream` contract while offering
three independent delivery modes through `RAPP_CHAT_STREAM`:

| Mode | Behavior |
|------|----------|
| `smooth` (default) | Frontier renders a provisional assistant bubble while holding the kernel wire, then replays the original SSE bytes at the terminal event and hands off once to the kernel's stable final bubble. |
| `raw` | The native response object and stream pass through untouched. Frontier adds no delivery behavior. |
| `hold` | The kernel typing indicator remains until the upstream stream ends, then Frontier replays the buffered response as one delivery. `RAPP_CHAT_TYPING=1` remains an alias. |

Chat look is separate. `RAPP_CHAT_LOOK=messages|business` changes styling, not
delivery semantics.

## Why smooth owns the provisional render

Smooth v1 paced SSE deltas into the kernel, but wire timing was not the visual
bottleneck. The kernel schedules a render every 80 ms, then
`renderStreamedText` returns early while `hasUnresolvedMarkdown(nextTree)` is
true (`rapp_brainstem/index.html:2904-2943`). A heading, list, emphasis span,
link, or fence can therefore hold several paced deltas until the Markdown tree
becomes structurally complete. The subsequent block morph and masked reveal
make those delayed deltas arrive as a lump. The `.wide` layout also changes at
1,200 characters (`rapp_brainstem/index.html:2925`).

Smooth v2 leaves that renderer unchanged and moves only the in-progress visual
render into the Frontier bridge:

| What the kernel does | What Frontier changes in `smooth` |
|----------------------|-----------------------------------|
| Creates the request response slot and typing indicator. | Claims the current typing indicator, hides it with an injected class, and inserts a structurally matching `.msg.assistant` marked `data-rapp-provisional="1"` in the same response slot. |
| Receives SSE deltas and waits for structurally resolved Markdown before updating its stream bubble. | Buffers the original SSE chunks so the kernel receives zero bytes before a terminal event. Incoming delta text instead feeds a word-granular adaptive screen pacer. |
| Schedules stream work every 80 ms. | Re-renders the complete growing provisional source on animation frames, with the first word immediate, incoming-rate EMA, about one second maximum lag, and a terminal drain bounded to 300 ms. |
| Uses `marked.parse`, Markdown normalization, and `sanitizeMarkdownFragment`. | Uses the reachable page `marked.parse` and `sanitizeMarkdownFragment`. The kernel's `normalizeMd` is function-local, so Frontier applies the same Unicode-bullet normalization. A strict tag, attribute, and URL allowlist is the sanitizer fallback; raw model Markdown is never assigned to `innerHTML`. |
| Removes its stream bubble and appends the stable assistant bubble at completion (`rapp_brainstem/index.html:3057-3059`). | Replays the original SSE bytes in order, hides the kernel replay bubble while the provisional is active, observes the response slot for the stable bubble, disables its arrival animation, measures the height delta, and removes the provisional exactly once. |
| Renders agent activity and error behavior. | Leaves final agent activity to the kernel. An upstream error releases the buffered wire immediately and removes the provisional; abort/navigation also cancels upstream and removes it. |

The provisional keeps the existing quiet caret, `.wide` transition, measured
footer clearance, and tail follower. The follower yields when the user
deliberately scrolls away.

## Automated contract

`tests/frame-bridge-typing.test.mjs` runs the injected bridge in `node:vm` with a
minimal response-slot DOM. It proves zero kernel bytes before terminal, at least
40 monotonically growing provisional renders for a 1,600-character burst,
byte-identical ordered replay, exactly one handoff and removal, bounded handoff
height measurement, error and abort cleanup, raw response identity, and
unchanged hold behavior.

`tests/stream-render-pacing.test.mjs` uses a fake animation-frame clock to prove
word and multibyte preservation, rate adaptation, bounded lag, terminal drain,
and cancellation.
