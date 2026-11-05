---
title: Content Addressing
section: Protocol
status: published
hook: How does rapp/1 hash things, and why is every hash tagged with a space?
source: "SPEC.md §5; book/03-content-addressing.md; book/A-reference-manual.md §A.2; conformance/vectors.json (5_hash)"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Content Addressing

In rapp/1, a thing's address is a **hash of its content**.
Every hash is **domain-separated**: a short tag naming its purpose is mixed in first.
So the same bytes used for two different purposes get two different addresses, and they can never be confused.

## The two hash functions

```
H(space, v) = lowercase_hex( SHA-256( utf8(space) || 0x0A || canonical(v) ) )     ; v a value (§4)
Hb(space, b) = lowercase_hex( SHA-256( utf8(space) || 0x0A || b ) )                ; b raw octets
```

- **`H`** hashes a JSON value, after [[Canonicalization]].
- **`Hb`** hashes raw bytes.
- The tag (`space`) is followed by one newline byte (`0x0A`), then the content.

## The fixed list of spaces

Each tag is used by **exactly one** of the two functions:

| Function | Spaces |
|---|---|
| `H` | `rapp/1:particle`, `rapp/1:wave`, `rapp/1:egg-manifest`, `rapp/1:sealed-aad`, `rapp/1:sealed-key-request` |
| `Hb` | `rapp/1:egg`, `rapp/1:rappid`, `rapp/1:grail`, `rapp/1:seal` |

An implementation **MUST refuse** to hash under any other tag, or with the wrong function.

## Worked example

From the conformance vectors, for the value `{"x": 1}`:

| Space | Hash |
|---|---|
| `H` `rapp/1:particle` | `2ba28c1fad4d0fbea812dddc74f13e3d097099fb07ce621fd208282ade5e5fc3` |
| `H` `rapp/1:wave` | `ab18eb8ab68a6093376335930413afb8b92f81a4da863708bbde8e1a875874e8` |
| `H` `rapp/1:egg-manifest` | `8c774ac7a755e62e80ce5791f60acc0673212cd05ba5cb1add656e06f58f18aa` |

Same value, three spaces, three unrelated addresses.

## Output rules

- Always exactly **64 lowercase hex** characters.
- **Never truncated. Never uppercased.**
- Two values are the same object **iff** their same-space hashes are equal.

## Addresses are pairs

- A bare 64-hex string means something **only within its space**.
- An implementation **MUST NOT** treat a hash from one space as an object of another.
- Content-addressed stores **MUST** key by `(space, hash)`.

## Labels are not identity

A `name/X.Y` label is never identity. **Only a hash is.**
Names for long-lived things are a separate concept: see [[Identity and the Rappid]].

## Security assumption

SHA-256 collision resistance (FIPS 180-4) is a security assumption of the standard.
See [[Security Considerations]].

## Where these hashes show up

- `rapp/1:particle` and `rapp/1:wave` — the two hashes in every frame. See [[The Frame]].
- `rapp/1:rappid` — minting identity tails. See [[Identity and the Rappid]].
- `rapp/1:egg` and `rapp/1:egg-manifest` — packages. See [[The Egg]].
- `rapp/1:grail` — the `grail_id` of a pinned kernel. See [[Distros and Pinning]].

## Related

- [[Canonicalization]]
- [[The Frame]]
- [[Identity and the Rappid]]
- [[The Egg]]
- [[Security Considerations]]
