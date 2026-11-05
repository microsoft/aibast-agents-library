---
title: Identity and the Rappid
section: Protocol
status: published
hook: What is a rappid, how is it minted, and when may it ever change?
source: "SPEC.md §6; book/04-identity.md; book/A-reference-manual.md §A.3; conformance/vectors.json (6_rappid)"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Identity and the Rappid

A **rappid** is the permanent name of a running Brainstem, a door or an object.
It is **minted once** and then never changes.
It is never computed from the thing's name or content, so renaming or editing never changes who it is.

## The shape

```
rappid:@<owner>/<slug>:<64 lowercase hex>
```

Example (the stream id used in the conformance frame vectors):

```
rappid:@kody/twin:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

- **`owner`** — the **lowercase** GitHub login, 1–39 characters. Display casing is presentation, never identity.
- **`slug`** — 1–100 characters.
- Both use lowercase letters and digits, with single hyphens between them (no leading, trailing or doubled hyphen).
- **`hash`** — exactly 64 lowercase hex characters.

Longer parts **MUST** be refused. The grammar is case-sensitive.

## Invalid examples

From the conformance vectors, each of these is refused:

| Value (tail shortened here) | Problem |
|---|---|
| `rappid:@Kody/x:aaaa…` | uppercase owner |
| `rappid:@kody/x:AAAA…` | uppercase hash |
| `rappid:@-kody/x:aaaa…` | leading hyphen |
| `rappid:@kody--w/x:aaaa…` | doubled hyphen |
| `rappid:v2:kody/x:aaaa…` | legacy form |

Legacy forms such as `rappid:<slug>:<hash>`, `rappid:v2:…` and bare UUIDs **MUST** be migrated out, not read forever.

## Minting: exactly once

The 64-hex tail is minted once per identity, in one of two ways:

- **Keyless:** `tail = Hb("rapp/1:rappid", uuid4_octets)` — the 16 binary octets of a UUIDv4 (RFC 9562).
- **Keyed:** `tail = Hb("rapp/1:rappid", SPKI_DER)` — the DER public key (RFC 5280) of the master key.
  It must be an Ed25519 key or a P-256 (prime256v1) key with an uncompressed point.

See [[Content Addressing]] for `Hb` and [[Trust and Signatures]] for keys.

## The one prohibited shortcut

A producer **MUST NOT** derive the tail from owner, slug or any name.
`sha256("owner/slug")` is explicitly prohibited (drift ID-01/C3).
If the tail came from the name, anyone who knew the name could compute the identity.

## Reading an existing identity

- On reading a stored `rappid.json`, an implementation **MUST reuse** the stored tail.
- It **MUST NOT** re-mint.
- `canonicalize_rappid(s)` restructures a legacy form into the current grammar, **keeping the existing hash**.
- If the tail is not exactly 64 lowercase hex (for example a legacy 32-hex tail), the result is **provisional**.
  A provisional id lives only inside the reading process. It must never appear in an emitted frame, `stream_id`, egg or registry entry.

## Re-anchoring: the only re-mint

A **re-anchor** mints one fresh tail and records the old id in `_migrated_from`.
It is lawful only in these cases:

- `upgrade` — a provisional 128-bit id becomes a 256-bit id;
- `rotation` — an uncompromised key rotation (the **old** key signs, proving continuity);
- `compromise` — a key compromise (a tombstone for the old id is registered in the same append);
- `tag-migrate` — a pre-rev-3 keyed tail made with un-tagged `sha256(SPKI)`.

A self-asserted `_migrated_from` is **not enough**.
The re-anchor must be an owner-signed **re-anchor record** in [[The Registry]]:
`{old_rappid, new_rappid, case, utc, sig, old_key_sig?}`.

## Stream ids and kinds

A rappid also names streams of [[The Frame|frames]]:

- **body stream** — the rappid itself;
- **memory stream** — `<rappid>:<instance>`: the full rappid, a colon, then an instance label (lowercase, 1–64 characters);
- **swarm stream** — `net:<label>`.

A `kind` is two labels joined by a dot, such as `body.pulse`.
Its family is set by the registry, never inferred from its prefix.

## Related

- [[Content Addressing]]
- [[Trust and Signatures]]
- [[The Registry]]
- [[The Frame]]
- [[Glossary]]
