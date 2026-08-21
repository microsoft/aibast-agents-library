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

## The relay: start fast, finish well

The two contracts above assume you must choose. You do not.

**Start speaking immediately in the fast voice, and let VibeVoice take the baton mid-utterance.**
Both engines are given the same text at the same moment. The fast one begins at once, so speech
starts with no wait at all. Behind it the good voice is **cooking in** — being generated while the
first one talks — and the instant its audio is ready, playback hands off at the next word boundary,
into the same sentence, already in progress. The listener hears a reply that starts instantly and
gets better while it is still being spoken.

**The bar for the seam is a radio one.** A late-night DJ crossfading between tracks is exactly the
effect: you notice that what you are hearing got *better*, never that something *switched*. A seam
audible as a seam is a bug; a seam audible as an upgrade is the whole feature. That framing also
sets the target for the good voice itself — the warmth and evenness of a late-night radio voice is
what "better" means here, not simply a higher sample rate.

This is the best of the trade rather than a compromise between its halves: latency is paid by the
fast voice, quality is delivered by the good one, and the seam is a single word.

### How the handoff works

1. **One text, two synthesizers.** Both receive the identical string. If the text changes — a
   streamed reply that revised itself — the relay is off; see the rules below.
2. **The fast voice starts immediately** and reports where it is: which word is being spoken now.
3. **VibeVoice returns audio with word-level timings.** When it lands, find the word the fast voice
   is about to speak, seek to that word's offset in the VibeVoice audio, and swap.
4. **Swap at a word boundary, never inside a word**, with a short crossfade (tens of milliseconds)
   so the change of voice is a change of voice and not a click.
5. **Every word is spoken exactly once.** The handoff may not repeat the word it lands on, and may
   not skip it. That is the whole correctness condition — a listener who hears "the the" or loses a
   word learns to distrust the voice.

If VibeVoice cannot give word-level timings, hand off at the next **sentence** boundary instead.
That is a longer wait for a better seam, and it is a perfectly good implementation — a relay that
only changes voice between sentences is still a relay.

### Rules that keep it honest

- **The relay never stalls speech.** If VibeVoice is late, the fast voice simply finishes the
  utterance and the next one starts the race again. Nothing waits, nothing is dropped.
- **If VibeVoice arrives before playback starts**, skip the relay and play it from the beginning.
- **If the text changed after the fast voice began**, do not hand off. A seamless voice saying
  different words is worse than a consistent poor one — the relay may improve how a sentence sounds,
  never what it says.
- **The change is allowed to be audible.** It signals the good voice arrived, and pretending
  otherwise would require making the fast voice worse or the good one blander.
- **The text reply is still never held back.** The relay is about speech; reading never waits on it.

### What it changes above

The voice-message idiom stays right for the case where there is no fast voice to open with — a long
reply, or a person who wants only the good voice. Where speech should begin at once, the relay is
the better default, because it removes the wait without giving up the voice.

## If it were audio-bound

Everything above assumes text is carrying the conversation and voice is an extra channel. Take the
text away — an audio-only conversation, on the radio — and the same design becomes strict rather
than optional. That case is worth designing for directly, for two reasons: it is the honest test of
whether the voice path is any good, and it is the situation of anyone who cannot see the screen.

What changes when audio is the only channel:

- **Dead air is the failure mode, not latency.** A station never goes silent while the next thing is
  cued; something is always on air. That is precisely what the fast voice is for, and why the good
  one cooks in behind it rather than in front of it. "Wait three seconds for a better voice" is a
  reasonable trade when you can read in the meantime and an unacceptable one when you cannot.
- **The seam has no safety net.** With text on screen, a dropped or duplicated word is recoverable —
  the reader just looks. In audio it is simply lost. The word-exactly-once rule stops being
  fastidiousness and becomes the correctness condition.
- **Interruption must work mid-utterance.** A listener cannot skim ahead or stop reading; the only
  way out of a long answer is to talk over it. Speech must stop the instant the person speaks, which
  is the two-player law in another medium: the person wins the moment they act.
- **Pacing carries meaning.** Pauses, emphasis and speed are the audio equivalent of paragraphs and
  headings. A handoff that preserves the words but resets the prosody mid-sentence will still sound
  wrong, so continuity is a property of delivery, not only of text.

**Design the voice path as though it were audio-bound, and the text-bound case gets it for free.**
The reverse does not hold: a voice built assuming someone can always read the screen fails the
person who cannot.

## What this rules out

- Holding the text reply until the audio is ready.
- Presenting a slow voice as though it were a live one.
- Turning chat voice on by default because narration sounded good — they are different contracts,
  and only one of them has someone waiting.
- A relay that repeats or drops the word it hands off on, or that hands off into different text.
- Making the fast voice deliberately worse so the upgrade sounds bigger.
- Any voice path that only works because the listener can also read the screen.
