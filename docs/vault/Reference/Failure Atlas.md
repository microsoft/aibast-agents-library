---
title: Failure Atlas
section: Reference
status: published
hook: When a frame is refused, which check failed and what usually caused it?
source: "book/B-glossary-and-failure-atlas.md §B.2, §B.3"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Failure Atlas

A consumer checks every incoming frame in a fixed order.
The **Failure Atlas** maps each check to the failure it usually catches.
Use it to find *where* a frame was refused, then fix the producer.

## The one rule to remember

**The step is a refusal location, not a repair instruction.**

- Correct the producer, or perform an authorized migration.
- Do not change the received frame until it passes.
- When evidence is missing or unverifiable, the consumer **fails closed**. It never turns "could not check" into a pass.

## Frame verification steps

| Step | Consumer checks | Typical failure |
|---|---|---|
| `1` | exact keys, types, grammar, registry values, fixed UTC | dialect, missing/null confusion, malformed field |
| `1a` | `stream_id` equals the stream of record | cross-stream replay |
| `2` | recomputed particle equals `payload_hash` | payload changed |
| `3` | recomputed wave equals `frame_hash` | envelope changed |
| `4` | genesis or contiguous particle chain and nondecreasing UTC | gap, fork, wrong parent, time reversal |
| `5` | swarm `prev_wave` rule; null elsewhere | wrong wire discipline |
| `6` | required/present signature, key binding, tenure, tombstone | missing authorship or unauthorized signer |

## Reading each step in plain words

- **Step 1 — shape.** The frame must have exactly the right fields, types and formats. Extra fields, a different encoding, or a null where a value belongs all fail here. See [[The Frame]] and [[Canonicalization]].
- **Step 1a — right stream.** A valid frame copied into a different stream is refused.
- **Step 2 — payload.** The consumer re-hashes the payload. A mismatch with `payload_hash` means the payload changed. See [[Content Addressing]].
- **Step 3 — envelope.** The consumer re-hashes the unsigned envelope. A mismatch with `frame_hash` means something in the envelope changed. See [[The Wire]].
- **Step 4 — chain.** The frame must be a genesis, or link to the previous frame's particle, with time that does not go backward. Gaps, forks and wrong parents fail here.
- **Step 5 — wire discipline.** Swarm (`net:*`) streams must link `prev_wave`. Other streams must leave it null.
- **Step 6 — signature and authority.** A required signature must be present, bound to a registered key, within its tenure, and not revoked by a tombstone. See [[Trust and Signatures]] and [[The Registry]].

## A common failure outside the frame: the wrong space

Every rapp/1 hash belongs to a named **address space**.
A bare 64-hex digest has no meaning on its own.
Hashing the right bytes in the wrong space gives a different, non-matching address.

| Space | Function |
|---|---|
| `rapp/1:particle` | frame payload address |
| `rapp/1:wave` | unsigned frame-envelope address |
| `rapp/1:rappid` | identity tail |
| `rapp/1:egg` | packed file address inside an egg |
| `rapp/1:egg-manifest` | whole egg identity |
| `rapp/1:seal` | retired-head seal |

When a digest does not match, first ask: **in which space?**

## Related

- [[The Frame]]
- [[Conformance Classes]]
- [[Conformance and Drift]]
- [[Security Considerations]]
- [[Glossary]]
