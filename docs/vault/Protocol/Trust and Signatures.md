---
title: Trust and Signatures
section: Protocol
status: published
hook: What does a rapp/1 signature prove, how is it checked, and how do key rotation and revocation work?
source: SPEC.md §10; book/08-trust-and-signatures.md; book/A-reference-manual.md §A.7
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Trust and Signatures

A **signature** in rapp/1 is a statement by a key about a frame or egg whose bytes are already fixed by hashes.
Hashes prove the bytes are unchanged. A signature adds **who** stands behind them.
A signature only counts when the key is found in the estate's signed registry and was in force at the time.

## The short version

- Integrity comes from hash links, not signatures. See [[Content Addressing]].
- `sig` is optional on memory and body streams, and **required** on swarm streams.
- If `sig` is present, it must verify completely. A bad signature is never treated as "unsigned".
- The public key comes from the registry, never from the sender. See [[The Registry]].
- Rotation and revocation are time-scoped: old valid history stays valid.
- An unsigned frame makes no authorship claim.

## Four claims, four checks

| Claim | Evidence | What it does **not** prove |
|---|---|---|
| these are the original payload bytes | recomputed `payload_hash` | who produced them |
| this is the original frame envelope | recomputed `frame_hash` | that it is the current head |
| this key signed this frame | valid §10 JWS | that the key was authorized at that time |
| this key was authoritative then | verified, fresh registry + succession records | that a newer head does not exist |

The first two are local and need no network. The last two cross a trust boundary.

## The exact signature format

rapp/1 uses JWS Compact Serialization with a **detached, unencoded payload** (RFC 7515 Appendix F plus RFC 7797).

The protected header has **exactly** four members, no others:

```json
{
  "alg": "EdDSA",
  "b64": false,
  "crit": ["b64"],
  "kid": "rappid:@owner/agent:<64hex>"
}
```

- `alg` is `EdDSA` (Ed25519) or `ES256`.
- `kid` is the signer's rappid. See [[Identity and the Rappid]].
- The header bytes must be `canonical(header)`. See [[Canonicalization]].

Signing input and stored form:

```text
signing input = BASE64URL(canonical(header)) || "." || canonical(frame \ {sig})
sig           = BASE64URL(canonical(header)) || ".." || BASE64URL(signature)
```

The empty middle segment marks that the payload travels outside the string. ES256 signers **should** sign deterministically (RFC 6979) so signed files stay byte-reproducible. Ed25519 is deterministic already.

Because `sig` is never part of `frame_hash`, re-signing does not change the frame's identity. See [[The Frame]].

## Key discovery

A signature can be mathematically valid under any key an attacker supplies. So the verifier must answer: is this the key bound to `kid`?

A complete check has four stages:

1. Parse the JWS and require the exact header shape.
2. Get the signer's SPKI from a verified, fresh registry `spki` entry.
3. Check `Hb("rapp/1:rappid", SPKI_DER)` equals the rappid's tail.
4. Verify the signature over the exact canonical signing input.

Refuse on a missing registry entry, a tail mismatch, an unsupported algorithm, an extra header member, stale revocation state, or a bad signature.

The `rappid.json` published at an agent's door is source material for the registry entry. It is **not** a verification source.

## Rotation and compromise

- **Rotation** creates a new keyed rappid and a registry `re-anchor` record. A verifier refuses a `sig` by the old rappid on any frame with `utc` at or after the re-anchor time. Earlier frames still verify.
- **Compromise** is declared by an owner-signed **tombstone** `{rappid, revoked_utc}`. A verifier refuses any `sig` by that key on a frame whose `utc` is at or after `revoked_utc`, checking tombstones at verification time.
- To stop a key without rotating, the owner registers a tombstone.
- "Owner-signed" means the `kid` is the registry's estate owner in effect at that time. See [[The Registry]].

**Known limit:** frame `utc` is set by the producer. A stolen key can backdate frames to just before `revoked_utc`. After a compromise, the owner **should** advance or re-genesis affected stream heads past that point. See [[Versioning and Evolution]].

## What the reference profile covers

The small stdlib reference (`rapp.py`) enforces the presence rule for swarm frames. Vector V9 in `conformance.py` proves an unsigned swarm frame is refused.

It does **not** perform Ed25519/ES256 verification, registry key discovery, rotation, or tombstone checks. A full **Consumer** must. See [[Conformance Classes]].

## Review questions

Ask these about any signed design, in order:

1. Which exact bytes are signed?
2. Can two serializations of the same value give different signing inputs?
3. Where does the verifier get the public key?
4. What binds that key to the claimed identity?
5. What says the key was authoritative at the frame's `utc`?
6. What stops a stale registry from silently un-revoking it?

If any answer is "the sender tells us", verification is not complete.

## Related

- [[Identity and the Rappid]]
- [[The Registry]]
- [[The Frame]]
- [[Security Considerations]]
- [[Conformance Classes]]
