---
title: The Egg
section: Protocol
status: published
hook: How does rapp/1 package a whole agent, application, or space so anyone can verify it before using it?
source: SPEC.md §9; book/07-the-egg.md; book/A-reference-manual.md §A.6
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# The Egg

An **egg** is a single package that carries a unit of RAPP work: a full Brainstem instance, one rapplication, a session, or a signed invite.
Every egg has the same small manifest, a content address, and strict rules a receiver checks **before** it unpacks anything.
If any check fails, the whole egg is refused.

## The short version

- One spec of record: §9 of the upstream RAPP/1 specification. No other document may re-specify eggs.
- One manifest shape, with exactly seven members.
- Seven registered **variants**. The variant changes the viability rules, not the manifest shape.
- One address for the whole egg. Signing it does not change that address.
- Receivers check **integrity first, then viability**, and refuse the whole egg on any failure.

## The seven variants

| `variant` | Container | What it packs |
|---|---|---|
| `organism` | stored ZIP | wire value for a full Brainstem instance; must include `rappid.json` and `soul.md` |
| `rapplication` | stored ZIP | one rapp; must include `rappid.json` and exactly one root `agent.py` |
| `session` | JSON | one runtime plus transcript; `payload` = `{runtime, transcript}` |
| `invite` | JSON | a QR-sized signed pointer to a neighborhood or estate; no packed files |
| `neighborhood` | stored ZIP | one sub-egg per member, named `<owner>--<slug>.egg` |
| `estate` | stored ZIP | one sub-egg per neighborhood |
| `sealed` | stored ZIP | exactly `ciphertext.bin`, plus the `rapp-sealed-artifact/1` payload |

Adding a new package kind is a registry and standard change. It is not permission to invent a new format name. See [[The Registry]].

## The manifest

Every egg has exactly this manifest (example from the book; `organism` is the wire value for the full-Brainstem variant):

```json
{
  "schema": "rapp/1-egg",
  "variant": "organism",
  "rappid": "rappid:@owner/agent:<64hex>",
  "created_utc": "2026-08-20T12:00:00.000Z",
  "contents": [
    {"path": "rappid.json", "hash": "<64hex>"},
    {"path": "soul.md", "hash": "<64hex>"}
  ],
  "payload": {},
  "sig": null
}
```

- `contents` lists every packed file **except** `manifest.json`, exactly once, sorted by the UTF-8 bytes of `path`.
- For the JSON variants (`session`, `invite`), `contents` is exactly `[]`.
- `path` is a relative POSIX path: no `.` or `..` segment, no leading `/`, no backslash, no drive letter, no reserved Windows names such as `CON` or `NUL`.
- For `organism` and `rapplication` eggs, the packed `rappid.json` must carry the same `rappid` as the manifest.

## Two addresses

The egg uses two separate hash spaces (see [[Content Addressing]]):

```text
one packed file:
    Hb("rapp/1:egg", file_octets)

the egg as a whole:
    H("rapp/1:egg-manifest", manifest without sig)
```

`sig` is left out of the egg address. Signing or re-signing authenticates the same package. It never creates a new package identity.

## Deterministic containers

- JSON variants are serialized as exactly `canonical(manifest)` (see [[Canonicalization]]).
- ZIP variants use compression method `stored` for **every** entry. No deflate, because deflate output depends on the library.
- `manifest.json` comes first, then the files in `contents` order.
- Timestamps are fixed to `1980-01-01 00:00:00`; the UTF-8 filename flag is set; no extra fields; no ZIP64.

Result: two conformant packers given the same manifest and files emit byte-identical eggs.

## Verify integrity, then viability

A consumer works in this order and refuses the whole egg on any failure:

1. The manifest satisfies every §9.1 rule: exact members, path grammar, no duplicates, sort order, and the archive entry set equals `contents` plus `manifest.json`.
2. Every `contents[].hash` recomputes.
3. The variant's structural rules hold (required files, payload fields, sub-eggs).

The order matters. Code that extracts `../../outside` and only later notices the bad path has already lost. The path rules are the defense against archive path escapes. See [[Security Considerations]].

A non-null `sig` must verify. The `invite` and `sealed` variants **require** a signature. See [[Trust and Signatures]].

## Hatching: artifact versus instance

An egg names an **artifact**. A hatch creates an **instance**.
The artifact name stays the same on every hatch. Each instance gets its own new name.
The instance may note which egg it came from. That note is history only, never permission.

Detail (§9.4):

- The `rappid` in a packed egg's `rappid.json` names the **artifact**. Every hatch of the same egg reads the **same** artifact identity. Re-minting it on hatch is prohibited.
- A consumer that turns an egg into a live installation **MUST** mint a **fresh** identity for the instance, exactly once, at first boot, from entropy. It must never be derived from the artifact identity, host name, or path.
- Two instances of one egg share the artifact identity and **MUST NOT** share an instance identity.
- The instance identity document **SHOULD** record `grown_from`: the §9.1 egg address (64 lowercase hex) of the source egg.
- `grown_from` is written at mint time and is **immutable** after that. It is `null` when the source is unknown. A producer **MUST NOT** fabricate it.
- `grown_from` is **lineage, not inheritance**. It confers no authority, no trust, and no signing key material. A reader treats it as an unverified assertion unless the named egg is available and its address recomputes.
- A newly authored artifact built from existing RAPP objects **MAY** record `crossed_from` in its packaged `rappid.json`: a sorted, duplicate-free array of `{space, hash}`, where `space` is `"rapp/1:particle"` or `"rapp/1:egg-manifest"`. One parent is an **offspring**; two or more is a **cross**. The new artifact mints its own rappid, and `crossed_from` is lineage only.

See [[Identity and the Rappid]].

## The sealed variant

`sealed` lets a public mirror carry **encrypted bytes** without carrying the key.
The public bytes are ciphertext, **not access control**.
To use the artifact, a recipient asks a named key service, which may release a key wrapped for that one device.

Detail (§9.2.1):

- A producer **MUST** use a random 256-bit data-encryption key (DEK) per artifact. It **MUST NOT** embed the DEK or a shared master key in the egg, client, or URL, and **MUST NOT** put a password in a URL.
- The ZIP holds exactly one file: `ciphertext.bin` = AES-256-GCM ciphertext followed by the 16-byte tag. Its length is exactly `plaintext_bytes + 16`.
- `payload` has exactly the members `schema` (`rapp-sealed-artifact/1`), `cipher` (`A256GCM`), `nonce` (12 bytes, unpadded base64url), `plaintext_commitment`, `plaintext_bytes` (integer, 0 through `2^30`), `media_type`, `key_id`, `key_service_rappid`, `key_service_url`, `access` (always `scoped-key-release`), and `aad_hash`.
- `plaintext_commitment` is an HKDF-derived HMAC over the plaintext, keyed from the DEK with info string `rapp/1:sealed-commitment`, so it cannot be tested without the DEK.
- `aad_hash = H("rapp/1:sealed-aad", descriptor)`, and `canonical(descriptor)` is the AES-GCM additional authenticated data. The descriptor binds the artifact rappid, `created_utc`, `key_id`, commitment, size, and media type.
- The manifest signature is **REQUIRED**, with `kid` exactly equal to `manifest.rappid`. See [[Trust and Signatures]].
- `key_service_url` is an absolute HTTPS `POST /chat` URL ending in `/chat`. The URL is location, not authority: responses are accepted only when signatures bind to `key_service_rappid`.
- The request (`rapp-sealed-key-request/1`) is signed by the recipient and names `egg_hash`, `key_id`, the recipient key, a nonce, and an expiry. The release (`rapp-sealed-key-release/1`) is signed by the service and returns `wrapped_key_jwe` using `ECDH-ES+A256KW` with `A256GCM`. The service **MUST NOT** return a global raw DEK.
- A mirror URL **SHOULD** be immutable (pin a commit, not a moving branch). URL secrecy is never assumed.
- Revocation stops future key release. It cannot erase ciphertext or plaintext already decrypted, and a product **MUST** say so plainly and **MUST NOT** claim decrypted bytecode cannot be inspected.

## Try it

From the upstream repository root, the book's checkpoint packs and verifies an egg with the reference profile:

```bash
python3 - <<'PY'
import rapp as R

rid = R.mint_rappid("reader", "first-instance")
files = {
    "rappid.json": ('{"rappid":"' + rid + '"}').encode(),
    "soul.md": b"# A small, portable Brainstem\n",
}

blob = R.pack_egg(
    variant="organism",
    rappid=rid,
    created_utc="2026-08-20T12:00:00.000Z",
    files=files,
)
ok, step, why = R.verify_egg(blob)
manifest, unpacked = R.read_egg(blob)

print("bytes:", len(blob))
print("address:", R.egg_address(manifest))
print("files:", sorted(unpacked))
print("verify:", ok, step, why)
PY
```

Adding a file named `../escape` must make `verify_egg` refuse the whole package.

## Related

- [[The Frame]]
- [[Content Addressing]]
- [[Identity and the Rappid]]
- [[Trust and Signatures]]
- [[The Registry]]
- [[Failure Atlas]]
