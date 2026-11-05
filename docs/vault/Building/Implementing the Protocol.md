---
title: Implementing the Protocol
section: Building
status: published
hook: In what order should you build a rapp/1 implementation, and how do you know it is done?
source: "book/11-implementing-rapp.md §11.1-§11.11; SPEC.md §11"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Implementing the Protocol

To build a rapp/1 implementation, **build from the bottom up**.
Start with exact values and bytes, then hashes, identity, frames, eggs, and finally signatures and the registry.
Each layer relies on the one below having exactly one answer.

## The build order

```text
safe I-JSON parser
      ↓
canonical bytes
      ↓
H / Hb and typed addresses
      ↓
rappid mint and load
      ↓
frame build and verification
      ↓
egg pack and verification
      ↓
JWS, registry, succession, and current heads
```

Starting with `/chat`, ZIP, or signatures tends to hide lower-layer ambiguity behind a convenient API.

## 1. State your claim

Pick a [[Conformance Classes|conformance class]]: **producer**, **consumer**, or **router/mirror**.
One program can be more than one, but say so explicitly. A producer that builds valid frames is not automatically a full consumer.

Write the target at the top of the port:

```text
Target: RAPP rev-7 Producer + byte-core Consumer
Implemented: §§4–7, §9 integrity/viability
External adapters required: §10 JWS, §13 registry and freshness
```

## 2. Accept only admissible values

The parser must reject:

- duplicate object member names;
- unpaired UTF-16 surrogates;
- numbers outside the binary64 round-trip domain;
- values deeper than 64 levels;
- canonical output larger than 1 MiB.

A production port imports a tested RFC 8785 (JCS) implementation or proves its own with edge vectors. Compare UTF-8 **bytes**, not pretty-printed strings. See [[Canonicalization]].

## 3. Keep the address space in the type

```python
def H(space, value):
    preimage = space.encode() + b"\x0a" + canonical(value).encode("utf-8")
    return hashlib.sha256(preimage).hexdigest()
```

A bare digest should never travel without its space. Use separate constructors for values (`H`) and raw bytes (`Hb`), and no helper that guesses. See [[Content Addressing]].

## 4. Separate mint from load

Use two visibly different operations: `mint_rappid(...)` creates a new identity; `load_rappid(...)` reuses a stored one.
Never write `get_or_create_rappid`. A failed read would quietly become a new identity. See [[Identity and the Rappid]].

## 5. Make frame building pure

The builder takes explicit inputs. It does not read the clock, load the head, or publish.
Compute in one direction: validate, compute `payload_hash`, assemble, compute the wave, attach `frame_hash`, sign later if required.
Never mutate a built frame. See [[The Frame]].

## 6. Keep verification pure and ordered

```text
verify(candidate, head, stream_of_record, registry_snapshot)
    → accepted
    → refused(step, reason)
```

The verifier never repairs, persists, or reparents. Step order is observable behavior: shape before hashing, particle before wave, chain before trust. Keep a negative suite in every port; see [[Failure Atlas]].

## 7. Treat append as a transaction

Two writers can both read head 7 and build different frame 8s. Write the frame object first, then move the head with a compare-and-swap against the head you read.
If the swap fails, do not silently rebuild on the new head.

## 8. Verify eggs before extracting

Pack, read, verify, then extract. Check every path and the entry set before writing anything. `zip.extractall()` must never be the parser. See [[The Egg]].

## 9. Wrap cryptography narrowly

Do not implement Ed25519, ES256, DER, or JWS yourself. A thin rapp/1 adapter owns the protected header, signing input, allowed algorithms, `kid` parsing, and registry key lookup; a maintained library does the math. See [[Trust and Signatures]].

## 10. Test across languages

Record, for every positive fixture: input value, canonical UTF-8 hex, space tag, preimage hex, expected digest, and expected frame or manifest. For every negative fixture, record the refusal step and reason.
Accepting extra forms is as nonconformant as rejecting valid ones.

## Definition of done

```text
[ ] parser enforces the RAPP I-JSON input domain
[ ] canonical bytes match an independent implementation
[ ] address values always retain their spaces
[ ] mint and load are separate identity operations
[ ] builder emits exactly eleven frame keys
[ ] verifier observes the complete ordered checklist
[ ] append uses an atomic remembered-head comparison
[ ] egg verification precedes extraction
[ ] JWS adapter uses the exact protected header and signing input
[ ] registry sequence, freshness, succession, and tombstones are enforced
[ ] controlled positive and negative vectors pass
[ ] at least one independently produced artifact round-trips
```

The last item is the one most often skipped. Test with an implementation someone else wrote.

## Related

- [[Conformance Classes]]
- [[Conformance and Drift]]
- [[Protocol Layers]]
- [[Failure Atlas]]
- [[The Frame]]
- [[Sources and Provenance]]
