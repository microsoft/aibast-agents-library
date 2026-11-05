---
title: The Registry
section: Protocol
status: published
hook: What is the estate registry, why is it the root of trust, and how does a consumer know it is genuine and current?
source: SPEC.md §13; book/09-registry-evolution-and-security.md §9.1-9.5, §9.9
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# The Registry

The **registry** is one signed, append-only document per estate. It records which keys belong to which identities, which event kinds and egg variants are allowed, where each stream starts, and who the owner is.
Because everything else resolves through it, it is the estate's **root of trust**.
A consumer accepts it only if it is signed by the owner, never older than the last one seen, and fresh enough.

## The short version

- Document schema: `schema:"rapp/1-registry"`, from an owner-controlled `canonical_source`.
- One bootstrap value, shared out-of-band once: the `estate_owner` rappid.
- Signed by the estate owner; refused if unsigned or not verifying.
- `registry_seq` only goes up. Lower values are refused (no rollback).
- Entries are never removed or renamed. Retirement is `deprecated:true`.

## What the registry does

- binds keyed rappids to public keys (see [[Trust and Signatures]]);
- registers frame kinds and their stream families (see [[The Frame]]);
- records the current genesis of every stream;
- carries key tombstones and identity re-anchors (see [[Identity and the Rappid]]);
- names the estate owner and that owner's succession;
- pins the estate's adopted protocol revision and its master plan;
- pins the Grail kernel (see [[The Brainstem Kernel]]).

An unsigned mutable registry would let an attacker swap a key, hide a tombstone, authorize a forged genesis, or redefine a kind. So the registry must authenticate itself.

## The bootstrap axiom

A keyed rappid's tail is `Hb("rapp/1:rappid", SPKI_DER)`. So the `estate_owner` rappid **is** a key fingerprint.

It is distributed once through a trusted channel (QR, invite, documentation), like a root certificate. The owner's public key may travel with the registry. It is accepted only if hashing it reproduces the trusted tail.

## Signed, monotonic, fresh

The safe retrieval path:

```text
out-of-band estate_owner rappid
        │
        ▼
SPKI tail check
        │
        ▼
registry signature
        │
        ▼
registry_seq monotonicity + freshness policy
        │
        ▼
keys, kinds, genesis records, succession, tombstones
```

- **Signature:** a detached §10 JWS `sig` over `canonical(registry \ {sig})`, `kid` = the `estate_owner` rappid.
- **No rollback:** persist the highest `registry_seq` verified; refuse any lower one.
- **Freshness:** get the registry from `canonical_source` or a provenance-stamped mirror. Refresh before trust-sensitive decisions. Report an over-age registry as **stale**, not **clean**.

Rollback resistance is not freshness. A hostile mirror can keep serving the highest sequence it has seen while hiding a newer one.

## Owner succession is historical

"Owner-signed" means signed by the owner **in effect at the artifact's `utc`**, through the re-anchor records. It is not always today's owner.

```text
──────────── A tenure ────────────│──────────── B tenure ────────────>
                                 2026-08-01
```

A frame signed by key A in July stays valid after rotation to B. One signed by A in August does not.

Root-key compromise of the estate owner can only be recovered by distributing a new trust anchor out-of-band. It cannot be expressed inside the registry it signs.

## Entry types

Every entry is a canonical value and append-only.

| Entry | What it records |
|---|---|
| `protocol` | estate adoption pin: spec repository, path, hash; never power to redefine a protocol |
| `kind` | one event kind and its stream family |
| `egg-variant` | one allowed egg variant (see [[The Egg]]) |
| `error-code` | one machine-readable `/chat` failure code (see [[The Wire]]) |
| `genesis` | the starting frame for a stream; exactly one non-deprecated per `stream_id` |
| `spki` | the public key for a keyed rappid |
| `tombstone` | owner-signed key revocation, `{rappid, revoked_utc, sig}` |
| `re-anchor` | identity continuity: `upgrade`, `rotation`, `compromise`, or `tag-migrate` |
| `grail-kernel` | the pinned Grail kernel bytes, by `grail_id`, SHA-256, and size |
| `estate_owner` | the owner currently in force (exactly one non-deprecated) |
| `master-plan` | the governing estate plan |

`egg-variant` and `error-code` are **closed namespaces**: an unregistered value is not conformant. Closed lists let the envelope stay stable while vocabulary grows on purpose. See [[Versioning and Evolution]].

A `rotation` re-anchor also needs `old_key_sig`, a signature by the old key.

## Operator checklist

Before calling an estate clean:

```text
[ ] current registry signature verifies from the pinned estate_owner rappid
[ ] registry_seq is not below the last accepted sequence
[ ] registry age satisfies the local freshness policy
[ ] every stream descends from its sole non-deprecated genesis
[ ] every signed frame resolves a matching SPKI and valid tenure
[ ] tombstones and re-anchors are applied at the frame's utc
[ ] no live frame points into sealed legacy history
[ ] every untrusted egg passed path, entry-set, hash, and variant checks
```

Unknown does not become pass. Stale does not become clean.

## Related

- [[Trust and Signatures]]
- [[Identity and the Rappid]]
- [[Versioning and Evolution]]
- [[Security Considerations]]
- [[Distros and Pinning]]
