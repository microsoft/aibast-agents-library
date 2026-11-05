---
title: Versioning and Evolution
section: Protocol
status: published
hook: How does rapp/1 change over time without breaking verification of anything already published?
source: SPEC.md §12; book/09-registry-evolution-and-security.md §9.6-9.7
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Versioning and Evolution

rapp/1 is a **living standard**: it is revised in place, not split into parallel versions.
The core **wire is frozen**. Anything verified under `rapp/1` keeps verifying forever.
New vocabulary grows through the registry; a shape change would need a new token, `rapp/2`.

## The short version

- One label never means two shapes. A shape change moves the token.
- Published content-addressed artifacts are **immutable**.
- Within an estate there is no permanent backward compatibility for its own retired forms: a change is a **total migration** plus deletion of the old form.
- Immutable chains change through **re-genesis**, never by editing old bytes.
- Every protocol revision is one appended frame on the specification's own chain.

## What is frozen

No revision may change a form a `rapp/1` artifact is verified by:

- canonicalization (§4) — see [[Canonicalization]];
- the hash function and its tags (§5) — see [[Content Addressing]];
- the rappid grammar and mint (§6.1, §6.2) — see [[Identity and the Rappid]];
- the eleven-key envelope and its two addresses (§7.1, §7.3) — see [[The Frame]];
- the consumer checklist (§7.5);
- the two wire forms and the `/chat` shapes (§8) — see [[The Wire]];
- the egg container and address (§9.1) — see [[The Egg]].

A change to any of these is not a revision. It moves the token to `rapp/2`, specified beside the current document. A consumer **must not** refuse a `rapp/1` artifact because a later token exists.

The reason: these frozen forms are what a stranger's implementation, written once and never updated, relies on.

## What still grows under rapp/1

- registered kinds;
- egg variants;
- error codes;
- registry entry types;
- vocabulary;
- subordinate profiles (see [[Conformance Classes]]);
- the registry itself (see [[The Registry]]).

A new registered `kind` uses the existing eleven-field frame. A changed key set, field grammar, or hash rule needs a new token.

## Why no permanent dialects

Every legacy reader path doubles the producer/consumer combinations that can disagree. rapp/1 chooses convergence: one current form. Old immutable history is kept only when it has been sealed through re-genesis.

## Re-genesis: change without rewriting history

Re-genesis is one owner-authorized operation that moves a stream to a new live chain while keeping the old bytes intact.

1. **Seal the old head.** `seal = Hb("rapp/1:seal", head_octets)`, over the exact retained octets.
2. **Emit a new genesis.** `seq` 0, `prev` null, the family's registered kind (`memory.re-genesis`, `swarm.re-genesis`, or `body.re-genesis`), owner-signed. The payload is exactly:

   ```json
   {"migrated_from":{"stream_id":<old>,"terminal_seal":<seal>,"terminal_seq":<n>}}
   ```

3. **Register it.** Append a `genesis` registry entry and flag every prior `genesis` for that `stream_id` as `deprecated`. This append is the linearization point. A concurrent second registration fails closed.
4. **Retire the old frames** under `legacy/`, bit-exact. They are never served as current, never extended, and no live frame may point at them.

A consumer refuses an unsigned or non-owner re-genesis frame. Only the registry-published genesis lets a consumer reset its remembered head to zero; anything else is a rollback attack.

Re-genesis is not an automatic repair. A checker may identify the need and prepare evidence. It must not invent authority.

## How the specification itself is revised

The upstream specification's revisions live in an append-only chain, `anchor/chain.jsonl`.

- Every protocol adjustment appends exactly one frame, kind `body.pulse`, with contiguous `seq`.
- The frame's `frame_hash` is the revision's durable identity. Names like `rev-14` are lookup labels only.
- From rev-14 on, the full normative text travels inside the frame, with its `sha256` and byte length.
- Verification starts from a frozen, content-addressed bootstrap profile, `rapp-anchor-bootstrap/1`.
- Each frame is also published at `anchor/frames/<frame_hash>.json`.
- `orient.json` is only a beacon to the head and must be regenerated from the verified chain.

Hashes in this chain prove byte integrity and linear history. They do **not** prove who ratified a change. Authority comes from owner-ratified acceptance onto the protected canonical branch. The chain and beacon are unsigned, and implementations must not fabricate a signature for them. See [[Sources and Provenance]].

## The DOGG specification revision chain (§12.2)

The specification is itself a **DOGG**: a public, re-pullable chain anyone can fetch and check.
A **revision** is one appended frame. Its `frame_hash` is its identity.
A copy whose hashes verify is **not** automatically authoritative. A verified fork is still a fork.

Technical detail, from SPEC.md §12.2:

- Each adjustment appends exactly one successor frame: `spec` stays `"rapp/1"`, eleven envelope keys, kind `body.pulse`, the bootstrap-pinned anchor `stream_id`, contiguous `seq`, `prev` naming the predecessor's `payload_hash`, and `prev_wave` and `sig` both `null`.
- Frames through rev-13 keep immutable pointer fields (`canonical_repo`, `commit`, `normative_path`, `normative_sha256`, `normative_bytes`). A resolver fetches only a commit-pinned copy and refuses a length or hash mismatch. These pointer payloads must not be emitted for rev-14 or later.
- From rev-14, the payload carries `schema:"rapp-spec-revision/1"`, a unique `revision`, `previous_revision`, `previous_normative_sha256`, a `publication` object, and a `normative` object holding the exact text, its `sha256` and `bytes`. The `publication` metadata must not be read as a signature or an authenticated registry.
- `anchor/index.json` is a generated index with no authority of its own. Resolution by revision label is a view; `rev-5` resolves to the greatest matching `seq`.
- A consumer verifies from the bootstrap-pinned genesis and refuses a fork or duplicate `seq`, duplicate hashes, an unsupported schema, a pointer-only frame after rev-13, normative hash or length drift, or an object absent from the selected chain.
- The authority linearization point is owner-ratified acceptance of a commit onto protected canonical main. A stale competing append rebases and regenerates; force-push or history replacement is prohibited.

## For downstream estates

This repository pins one exact upstream commit, recorded in each note's `upstream_commit`. Retiring a name follows the same idea: migrate deliberately, keep history, never break what is already published. See [[Distros and Pinning]] and [[Conformance and Drift]].

## Related

- [[The Registry]]
- [[The Frame]]
- [[Conformance Classes]]
- [[Conformance and Drift]]
- [[Sources and Provenance]]
- [[Distros and Pinning]]
