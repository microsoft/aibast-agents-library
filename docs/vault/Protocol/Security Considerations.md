---
title: Security Considerations
section: Protocol
status: published
hook: Which threats does rapp/1 defend against, which ones do hashes alone not stop, and what control covers each?
source: SPEC.md §14; book/09-registry-evolution-and-security.md §9.8
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Security Considerations

rapp/1's **security model** has two parts.
Content addressing protects bytes that never change. Signed, authenticated state protects facts that can change, such as which head is current or which key is revoked.
This note lists the known threats and the control for each.

## The short version

- History is safe **given a trusted head**. Hashes do not tell you which head is current.
- Every hash lives in a named space, so equal hex in different spaces never means the same thing.
- Keys come from the signed registry, never from the sender.
- Revocation is checked at verification time, against a fresh registry.
- Archives are checked before anything is extracted.
- The Grail kernel bytes are pinned and tested in the exact release artifact.

## What hashes catch, and what they do not

| Threat | Hashes catch it? | Required control |
|---|---:|---|
| mirror changes an object | yes | recompute same-space address |
| mirror serves an old but valid head | no | persisted head + current genesis registry |
| attacker replays stream A into stream B | not by hash alone | §7.5 step 1a binding |
| attacker swaps a signing key | no | registry SPKI lookup + rappid tail check |
| mirror hides a key tombstone | no | registry sequence and freshness |
| producer future-dates a frame | no | receipt-time skew policy; re-genesis if bricked |
| archive uses `../` paths | no | §9 path grammar and entry-set verification |

## The considerations, one by one

**Integrity.** Every object is domain-separated and content-addressed. A hostile mirror cannot change bytes without breaking the hash. See [[Content Addressing]].

**Head freshness is not self-certifying.** A mirror may serve a stale or forked head. Consumers apply the monotonic-head rule. Swarm heads **should** be owner-signed. See [[The Frame]].

**Cross-stream replay.** A genesis has `seq`=0 and `prev`=null, so without stream binding it could replay as another stream. Step 1a binding is mandatory.

**Address-space confusion.** Domain tags make a particle, wave, egg, or rappid tail with equal hex non-interchangeable. Stores key by `(space, hash)`.

**Canonicalization attacks.** The I-JSON input profile — no duplicate keys, no lone surrogates, exact binary64, no normalization ambiguity — removes hash-splitting vectors. See [[Canonicalization]].

**Identity forgery and key compromise.** Authorship needs a keyed rappid plus a valid signature. Rotation is a verifiable re-anchor; a self-asserted `_migrated_from` is refused. Compromise is a registry tombstone enforced at verify time. See [[Trust and Signatures]].

Because a tombstone compares against the frame's producer-set `utc`, a compromised key can still stamp frames just below `revoked_utc`. After a compromise the owner **should** advance affected stream heads, or re-genesis, past `revoked_utc`.

**Root of trust.** The registry is signed by the owner, anchored to the out-of-band `estate_owner` fingerprint, `registry_seq`-monotonic, and freshness-checked. A stale registry silently un-revokes keys and hides re-geneses. See [[The Registry]].

**Producer-controlled `utc`.** A future-dated head can block a stream (later successors look earlier) and bias UTC-first merges. A consumer **should** refuse a frame whose `utc` is more than 300 seconds past receipt time. Adversarial merges **should** rank by `min(utc, first-seen)`. A blocked stream converges by re-genesis. See [[Versioning and Evolution]].

**Archive paths.** Egg consumers enforce path grammar and the exact entry set **before** extracting. An unenforced path grammar defends nothing. See [[The Egg]].

**Sealed-artifact limits.** A public mirror sees ciphertext and metadata. AES-GCM protects confidentiality only while the key stays secret. A recipient who has lawfully decrypted can copy the plaintext. Revocation stops future key release, not prior possession. These postures are non-conformant:

- shared passwords;
- embedded master keys;
- moving-branch URLs;
- nonce reuse under one key;
- claims that bytecode cannot be inspected after decryption.

**Kernel substitution.** Testing different bytes and restoring the Grail only after approval creates an untested release. The release-shaped artifact must contain the pinned bytes before its tests and approval. A digest mismatch is a blocking `kernel-drift` finding. See [[The Brainstem Kernel]].

**Kernel registry rollback.** Persisting only `registry_seq` does not protect an activated Grail declaration from a malicious higher-sequence registry. Consumers also persist every activated `grail-kernel` entry and reject its later removal, mutation, or duplication. See [[Conformance Classes]].

## The principle

Use content addressing for immutable bytes. Use explicit, authenticated state for facts that can change. When in doubt, fail closed: refuse first, migrate deliberately.

## How this maps to the production guide

Security sign-off in the production guide happens at [[Step 12 Security Sign-off]]. This note describes the protocol-level controls only; it is not a substitute for that review.

## Related

- [[Trust and Signatures]]
- [[The Registry]]
- [[The Egg]]
- [[Failure Atlas]]
- [[Step 12 Security Sign-off]]
- [[Conformance Classes]]
