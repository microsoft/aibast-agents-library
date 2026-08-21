# Voice in the Frontier — two contracts, not one

Voice shows up in two places that look similar and are not. Treating them as one problem is how
voice features get slow, or bad, or both.

| | **Narration** | **Chat voice** |
|---|---|---|
| What it is | the Frontier saying what it is doing while someone watches | the Brainstem's reply, spoken |
| Who is waiting | nobody — the work proceeds regardless | a person, mid-conversation |
| The trade | **quality over latency** | latency is the whole problem |
| Default | on in Show Mode, off otherwise | **off** |

Both use **VibeVoice**, and both are an opt-in Sense under `CONSTITUTION.md` Article II: installed
on first enable, removable without trace, on-device.

## Narration: latency is free, so spend it on quality

Narration describes work that is already happening. It may lag the action by a moment without
costing anyone anything, so it takes the good voice. It also keeps the screen free — the reason to
narrate aloud rather than draw more on the display is that a person can then look somewhere else
and still follow along.

## Chat voice: it is a voice *message*, not a live voice

VibeVoice is too slow to answer conversationally. The fix is not a worse voice — it is to stop
pretending the reply is live.

People already know what a voice message is. It arrives from the person you are talking with, you
can see it coming, you do not expect it instantly, and it plays when it lands. That idiom fits the
latency exactly, and it is honest: the voice really is still being made.

So when chat voice is enabled:

- **The text reply is never held back.** It lands at full speed. The voice is an additional channel
  that catches up — nobody waits on audio to read an answer.
- **The arriving voice is visible in the transcript**, in the same idiom a messaging app uses for a
  voice message still coming through. The wait is shown, not hidden behind a spinner that implies
  something is wrong.
- **It plays itself when it is complete.** No second click to collect a thing you already asked for.
- **It is off by default**, and the control that turns it on says plainly what it changes: replies
  will also arrive as voice messages, shortly after the text.

The point of the affordance is expectation, not decoration. A delay a person understands is not a
delay they mind; the same seconds spent behind a silent spinner read as the product being broken.

## What this rules out

- Holding the text reply until the audio is ready.
- Presenting a slow voice as though it were a live one.
- Turning chat voice on by default because narration sounded good — they are different contracts,
  and only one of them has someone waiting.
