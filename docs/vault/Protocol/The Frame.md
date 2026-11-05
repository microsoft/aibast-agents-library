---
title: The Frame
section: Protocol
status: published
hook: What is a rapp/1 frame, what are its eleven fields, and how is it verified?
source: "SPEC.md §7; book/05-the-frame.md; book/A-reference-manual.md §A.4; conformance/vectors.json (7_frame)"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# The Frame

A **frame** is one immutable record of one event.
Every event in rapp/1 uses this same envelope, with **exactly eleven fields**.
Frames link to the frame before them by hash, so any change to history is detectable.

## The eleven fields

The genesis (first) frame from the conformance vectors:

```json
{
  "frame_hash": "7f1828db28378b29b976b2763f36154bd432ccf1cfa5bf25e913583db86a010b",
  "kind": "body.pulse",
  "payload": {
    "hello": "world"
  },
  "payload_hash": "dccd124a460d7f7a6ab23b15df476f1f65fa19b8979f0ab70c656e55c67beb05",
  "prev": null,
  "prev_wave": null,
  "seq": 0,
  "sig": null,
  "spec": "rapp/1",
  "stream_id": "rappid:@kody/twin:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "utc": "2026-07-15T00:00:00.000Z"
}
```

The next frame in that stream has `seq` `1`, `payload` `{"n": 2}`, and `prev` equal to the genesis `payload_hash` (`dccd124a…`).

## Field rules

- **`spec`** — always the exact string `rapp/1`. Legacy tokens `rapp-frame/2.0` and `2.1` must not be emitted.
- **All eleven keys are always present.** None missing, none extra.
  A field that does not apply is `null`, never omitted, because JCS hashes `null` and an absent key differently.
- **`payload`** — always a JSON object (possibly `{}`).
- **`seq`** — a `uint53`: 0, 1, 2… up to 2^53−1, contiguous.
- **`utc`** — exactly `YYYY-MM-DDTHH:MM:SS.mmmZ` (24 bytes, three fractional digits, ASCII digits only, no offset, seconds never `60`).
- Size limits from [[Canonicalization]] apply: at most 1 MiB, depth 64.

## Two hashes: particle and wave

Each frame carries two addresses, computed in this order (see [[Content Addressing]]):

1. **particle** — `payload_hash = H("rapp/1:particle", payload)`. The chain link.
2. **wave** — `frame_hash = H("rapp/1:wave", frame \ {frame_hash, sig})`. The frame with only those two keys removed.

Because `payload_hash` is inside the wave, `frame_hash` also attests the payload.

## Chaining

- **Genesis:** `seq` = 0 and `prev` = `null`.
- **Later frames:** `seq` = previous + 1, and `prev` = previous `payload_hash`.
- **`prev_wave`** is non-null **only** on a swarm stream (`net:…`) past genesis. Then it equals the previous `frame_hash`.
- A frame never changes. A new state is a new frame.

## Kinds and families

Every `kind` belongs to one family through [[The Registry]]:

| family | example kinds | stream form |
|---|---|---|
| `memory` | `memory.chat-turn`, `memory.save` | memory stream |
| `swarm` | `swarm.guidance`, `swarm.echo` | swarm stream |
| `body` | `body.pulse`, `body.twin-pulse` | body stream |

New events are new registered kinds on the **same** envelope — never a new frame type.

## Verification checklist

A consumer checks in order and **refuses on the first failure** (never repairs):

1. **Shape and types** — eleven keys, correct grammars, registered kind matching the stream form.
1a. **Stream binding** — `stream_id` equals the stream being read.
2. **Particle** — recompute `payload_hash`.
3. **Wave** — recompute `frame_hash`.
4. **Chain** — `seq`, `prev`, and `utc` not earlier than the head.
5. **Wire** — `prev_wave` rule above.
6. **Signature** — if `sig` is set, verify it; an unsigned swarm frame is refused. See [[Trust and Signatures]].

Steps 1–5 never change their answer. Only step 6 can, if a key is later revoked.

The vectors include tampered frames that keep their original hashes on purpose.
For example, changing `"hello": "world"` to `"hello": "evil"` fails at **step 2**.

## Heads and forks

- A stream's **head** is its highest verified frame.
- A consumer refuses any **rollback** to a lower `seq`, or a different `frame_hash` at a verified `seq`.
- Two valid frames with the same `stream_id`, `seq` and `prev` are a **fork**. Both branches are refused past that point. Only the owner resolves it.

## Re-genesis

To move a chain to a new form without editing it, the owner seals the old head, emits a new signed `*.re-genesis` frame at `seq` 0, and registers it as the new genesis.
The old frames are kept bit-exact under `legacy/`. See [[Versioning and Evolution]].

## Related

- [[Content Addressing]]
- [[Identity and the Rappid]]
- [[The Wire]]
- [[Trust and Signatures]]
- [[The Registry]]
- [[Failure Atlas]]
