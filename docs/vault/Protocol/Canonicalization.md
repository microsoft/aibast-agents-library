---
title: Canonicalization
section: Protocol
status: published
hook: How does rapp/1 turn any JSON value into one exact byte string?
source: "SPEC.md §4; book/02-canonicalization.md; book/A-reference-manual.md §A.1; conformance/vectors.json (4_canonical, 4_refuse)"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Canonicalization

**Canonicalization** turns a JSON value into **one exact byte string**.
The same value always gives the same bytes, on every machine.
Every hash in rapp/1 is computed over these bytes, so this is the foundation of the whole protocol.

## The rule in one line

`canonical(v)` is the UTF-8 byte string produced by **RFC 8785 JCS** (JSON Canonicalization Scheme) for the value `v`.
It is defined only over I-JSON (RFC 7493).

JCS fixes:

- **member-name order** (by UTF-16 code unit),
- **string escaping**,
- **number format** (ECMAScript `Number::toString`).

There is **no insignificant whitespace** and **no byte-order mark** in the output.

## Example

From the conformance vectors. The input value:

```json
{
  "a": [3, 2],
  "b": 1,
  "c": { "x": 2, "y": 1 }
}
```

has the canonical form:

```
{"a":[3,2],"b":1,"c":{"x":2,"y":1}}
```

Whitespace is gone. Array order is kept. Object keys are always emitted in sorted order.

## What gets refused

An implementation **MUST refuse, never repair**, a value that contains, at any depth:

- **duplicate member names** in one object;
- an **unpaired UTF-16 surrogate**, or a **Unicode noncharacter** (U+FDD0–U+FDEF, or any code point whose low 16 bits are FFFE or FFFF);
- a **number that does not survive the binary64 round-trip**;
- a canonical form **over 1 MiB**, or nesting **deeper than 64** (the root is depth 1).

Refusal is whole, never partial. Input must also be well-formed UTF-8:

- a leading **byte-order mark is refused** (not stripped);
- UTF-16 and UTF-32 input is **never transcoded**.

Refused inputs from the conformance vectors:

| JSON text | Why |
|---|---|
| `{"a":1,"a":2}` | duplicate member name |
| `{"n": 9007199254740993}` | integer does not survive binary64 round-trip |
| `{"n": 1e999}` | non-finite after parse |
| `"\ud800"` | unpaired UTF-16 surrogate |

By contrast, `0.1` is accepted, because it round-trips.

## No normalization

- RAPP applies **no Unicode normalization** when hashing, storing or re-emitting an existing value.
- Strings are kept verbatim. Equality is **code-point equality**.
- A producer creating a **new** human or identifier string (slug, kind, label, `payload` object key) **MUST** emit it in **NFC**.
- A producer building a frame or packing an egg **MUST refuse** a `payload` member name that is not in NFC, or that contains an unassigned code point.
- Consumers do not test frame contents for NFC (egg paths are the exception — see [[The Egg]]).

## Why "refuse, do not repair"

If a reader silently fixes bad input, two readers can fix it differently.
Then the same input produces two different hashes, and the protocol's core promise breaks.
Refusal keeps every conformant implementation in agreement.
See the [[Failure Atlas]] for related failures.

## Migration note

The upstream specification records drift C4: an older `canonicalize()` (sorted-key `JSON.stringify`) matches JCS only for string-only payloads.
It **MUST** be replaced by the JCS implementation of record, imported rather than re-typed.

## Related

- [[Content Addressing]]
- [[Protocol Layers]]
- [[The Frame]]
- [[Conformance and Drift]]
- [[Implementing the Protocol]]
