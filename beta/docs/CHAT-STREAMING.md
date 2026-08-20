# Chat streaming — keep the stream, fix how it looks and moves

Decision (Kody, 2026-08-20), after seeing hold-and-pop live: *"go back to streaming… that does
feel right. I don't want my AI to be typing. I want it to stream in. Just make the streaming
UI/UX of how it is displayed and animated — that's what I need fixed."*

Token streaming is the product. What was wrong is the kernel UI's presentation of it, which the
Frontier fixes from inside the frame — the kernel (`rapp_brainstem/`) is never edited, and a bare
Brainstem outside the Frontier looks as it always did.

## What the kernel does, and what the Frontier changes

| Kernel today | Frontier (`RAPP_CHAT_STREAM=smooth`, default) |
|---|---|
| each 80 ms flush re-renders the bubble and **wipes** the new text in with a masked vertical reveal (`.stream-mask`, `.stream-revealing`, 560 ms) and a 360 ms slide-up on first appearance | mask and wipe off; a 160 ms opacity-only arrival; text simply grows |
| tokens arrive in bursts as the model emits them | the bridge paces them evenly — word-sized pieces at a steady ~30 ms cadence, first piece immediate, lag capped under ~1 s, byte-for-byte identical text and event order |
| bubble width jumps at 1,200 characters (`.msg.wide`) | the width change glides (240 ms) |
| typing dots bounce ("the worm") | dots pulse by opacity, no movement |
| no cue that text is still arriving | a quiet caret at the tail while the reply streams; gone when it completes |
| — | `prefers-reduced-motion`: no caret blink, no fades, static dots |

The Surgeon panel (our own renderer) uses the same pacing and caret. Markdown, agent activity,
menus, commands, and the kernel are unchanged.

## Modes

`RAPP_CHAT_STREAM=smooth` (default) · `raw` (the kernel's native presentation, nothing injected)
· `hold` (buffer the whole reply and show it at once after a typing bubble — built and tested,
kept as an option, **never the default**; `RAPP_CHAT_TYPING=1` is an alias).

## Done means

The regression harness's `/drive` timeline for a long reply shows the reply growing in many
even steps under `smooth` (no step larger than a few words, first text within ~100 ms of the
kernel's first token), the caret present while `stream-arriving` and gone after, the injected
style present only under `smooth`, and `raw` byte-identical to the kernel's own behavior.
