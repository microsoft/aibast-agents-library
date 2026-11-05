---
title: Protocol at a Glance
section: Protocol
status: published
hook: What is rapp/1, and what does it promise in one page?
source: "SPEC.md §1, §3; book/01-a-tutorial-introduction.md"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Protocol at a Glance

**rapp/1** is the shared set of rules that lets any two RAPP systems agree on the same data, byte for byte.
Its one promise: **the same concept has the same bytes everywhere.**
If two independent implementations follow the rules, they interoperate with no side agreement.

## The five building blocks

The specification defines five primitives. Everything else is built on them.

- **Canonicalization** — one exact byte form for any JSON value. See [[Canonicalization]].
- **Content addressing** — a tagged SHA-256 hash of those bytes. See [[Content Addressing]].
- **Identity** — the **rappid**, a name minted once and never derived from content. See [[Identity and the Rappid]].
- **The frame** — one immutable, hash-linked event record. See [[The Frame]].
- **The egg** — the packaging format. See [[The Egg]].

All of them ride **one wire**: either `POST /chat`, or a signed append-only frame. See [[The Wire]].

## The growth rule

Implementations add **agents**, **cartridges** and registered `kind`s.
They never add new endpoints and never add new envelopes.
This keeps every tier speaking the same shape.

## Key words

- **frame** — one immutable, content-addressed event.
- **stream** — an append-only, hash-chained sequence of frames that share one `stream_id`.
- **particle / wave** — a frame's two addresses: the payload hash and the whole-frame hash.
- **canonical form** — the one RFC 8785 byte string for a value.
- **legacy form** — any other historical encoding. Legacy is drift and must be migrated out.
- **Grail kernel** — a byte-pinned runtime. Its `grail_id` is `"grail:" || Hb("rapp/1:grail", kernel_bytes)`.

More terms are in the [[Glossary]].

## A complete example in three calls

The tutorial chapter shows the smallest working program, using the reference `rapp.py`:

```python
import rapp as R

stream = R.mint_rappid("kody", "hello")          # 1. an identity for the stream
frame = R.build_frame(                             # 2. a record in that stream
    kind="note.write",
    stream_id=stream,
    seq=0,
    utc="2026-07-15T12:00:00.000Z",
    payload={"text": "hello, frame"},
    prev=None,
)
ok, step, why = R.verify_frame(frame, head=None, stream_id_of_record=stream)  # 3. check it
print("OK" if ok else f"FAILED at {step}: {why}")
```

Mint an identity. Build a frame. Verify it. That is a complete transaction.

## Where authority lives

- The normative text is carried by an append-only chain, `anchor/chain.jsonl`.
- Its hashes prove **integrity**, not authority.
- `SPEC.md` is the byte-exact human-readable view of that chain.
- The durable identity of a protocol revision is the selected chain-frame hash, not a path or a `rev-N` label.

For where this vault's copy comes from, see [[Sources and Provenance]].

## Requirements language

**MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHOULD** and **MAY** follow RFC 2119 / RFC 8174 when written in bold capitals.

## Related

- [[Protocol Layers]]
- [[The Frame]]
- [[The Wire]]
- [[Conformance Classes]]
- [[Implementing the Protocol]]
- [[Sources and Provenance]]
