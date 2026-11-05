---
title: Glossary
section: Reference
status: published
hook: What does each rapp/1 term mean, in plain words?
source: "book/B-glossary-and-failure-atlas.md §B.1, §B.2, §B.4; SPEC.md §3 Terminology"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Glossary

This is the **vocabulary of rapp/1** in one place.
Each term gets a short, plain definition.
The specification text stays authoritative; see [[Sources and Provenance]].

## Identity terms

- **rappid** — the permanent name of a running brainstem, object or door. Format: `rappid:@<owner>/<slug>:<64-lowercase-hex>`. The tail is minted once from UUIDv4 octets or a public key (SPKI DER), never from the owner/slug name. See [[Identity and the Rappid]].
- **identity** — continuity across changing content. In rapp/1, identity is the minted tail of a rappid, not the readable owner/slug.
- **provisional identity** — an older rappid whose tail is not 64 lowercase hex characters. It can be read but must not be emitted. Upgrading it requires owner-authorized re-anchoring.
- **re-anchor** — an owner-authorized identity change for exactly one allowed case: provisional upgrade, key rotation, key compromise, or pre-standard key-tag migration.
- **tombstone** — an owner-signed registry record that revokes a keyed rappid from `revoked_utc` forward.

## Data and hashing terms

- **canonical form** — the one RFC 8785 JCS byte representation of an admissible I-JSON value. See [[Canonicalization]].
- **I-JSON** — the interoperable JSON profile from RFC 7493 that canonicalization is built on.
- **JCS** — JSON Canonicalization Scheme, RFC 8785. It fixes member order, escaping, number form and whitespace.
- **legacy form** — any historical encoding that is not the current canonical form. Live legacy is drift and must be migrated. Sealed re-genesis history is kept as evidence, not as a second dialect.
- **content address** — a SHA-256 digest computed in a named rapp/1 domain. It changes if the content changes. See [[Content Addressing]].
- **domain separation** — prefixing hash input with an exact space tag and a newline, so the same bytes in different roles get different addresses.
- **address space** — a named domain in which a hash has meaning. rapp/1 stores and looks up by `(space, hash)`, never by a bare 64-hex string.

## Event terms

- **frame** — the closed eleven-field event envelope. It carries a payload particle, a whole-frame wave, chain links and an optional signature. See [[The Frame]].
- **particle** — `H("rapp/1:particle", payload)`, stored as `payload_hash`. It addresses what happened.
- **wave** — `H("rapp/1:wave", frame - {frame_hash, sig})`, stored as `frame_hash`. It addresses the exact unsigned envelope. See [[The Wire]].
- **stream** — an append-only sequence of frames sharing one `stream_id`.
- **biography stream** — a stream identified directly by a rappid. It chains particles through `prev`; `prev_wave` is null.
- **swarm stream** — a shared `net:*` stream. It chains particles through `prev` and waves through `prev_wave`, and every frame must be signed.
- **worldline** — the particle-linked history of a brainstem or stream.
- **genesis** — the sequence-zero frame the live chain descends from.
- **head** — the highest verified frame descending from the registered genesis. Consumers keep heads to detect rollback.
- **re-genesis** — the owner-authorized operation that seals an old chain, publishes a new sequence-zero frame, updates the registry and retires the old bytes under `legacy/`.
- **kind** — a registered `noun.verb` event name.

## Packaging and trust terms

- **egg** — a `rapp/1-egg` manifest plus, for tree variants, deterministic stored-ZIP contents. It packages a brainstem, rapplication, session, invite, neighborhood, estate, or sealed ciphertext artifact. See [[The Egg]].
- **registry** — the signed, append-only estate root of trust for keys, kinds, genesis records, re-anchors, tombstones, owner succession and canonical-source pointers. See [[The Registry]].
- **estate** — a governed collection of brainstems and neighborhoods sharing one registry and owner succession.
- **authorship** — the claim that a key signed an artifact. It needs a valid signature, and does not by itself prove the key was authorized. See [[Trust and Signatures]].
- **authority** — the right of a signer to decide at a given time. It comes from the registry and its owner-succession records.
- **integrity** — evidence that bytes or chain links have not changed. Integrity does not imply authorship.
- **freshness** — confidence that signed mutable state is recent enough. A valid registry signature proves authenticity, not freshness.
- **fail closed** — refuse, or report unknown, when evidence is missing, malformed, stale or unverifiable. Never turn "could not check" into a pass.

## Roles

- **producer** — emits only current canonical values, addresses, identities, frames and egg variants.
- **consumer** — validates frames, eggs, signatures, registry state and all refusal conditions before accepting input.
- **router/mirror** — transports or serves artifacts without inventing endpoints or rewriting addressed bytes.

See [[Conformance Classes]] for how these roles are tested.

## Runtime and release terms

- **Grail kernel** — an estate-declared, byte-pinned runtime. Its `grail_id` is `"grail:" || Hb("rapp/1:grail", kernel_bytes)`. Once activated, those bytes are permanent; capabilities grow outside them. See [[The Brainstem Kernel]].
- **release capsule** — the canonical `rapp-cicd/1-release` payload naming one immutable candidate. See [[RAPP CICD]].
- **serving lineage** — the sequence of release identities that have received user traffic.
- **deployment cell** — an independently observable and isolatable runtime failure domain, governed by `rapp-deploy/1`. See [[RAPP Deploy]].

## Address spaces

| Space | Function | Input |
|---|---|---|
| `rapp/1:particle` | frame payload address | canonical value via `H` |
| `rapp/1:wave` | unsigned frame-envelope address | canonical value via `H` |
| `rapp/1:rappid` | identity tail | UUID or SPKI octets via `Hb` |
| `rapp/1:egg` | packed file address inside an egg | raw octets via `Hb` |
| `rapp/1:egg-manifest` | whole egg identity | manifest without `sig` via `H` |
| `rapp/1:seal` | retired-head seal | exact retained head octets via `Hb` |

A bare digest should always prompt one question: **in which space?**

## Notation

| Notation | Meaning |
|---|---|
| `canonical(v)` | UTF-8 JCS serialization of admissible value `v` |
| `H(space, v)` | SHA-256 of `utf8(space) + 0x0A + canonical(v)` |
| `Hb(space, b)` | SHA-256 of `utf8(space) + 0x0A + raw octets b` |
| `x - {a,b}` | object `x` with exactly members `a` and `b` removed |
| `64hex` | exactly 64 lowercase hexadecimal characters |
| `uint53` | integer from 0 through 2^53−1 |
| SPKI DER | canonical DER encoding of a SubjectPublicKeyInfo public key |

## Related

- [[Failure Atlas]]
- [[Protocol at a Glance]]
- [[Content Addressing]]
- [[The Frame]]
- [[Identity and the Rappid]]
- [[Sources and Provenance]]
