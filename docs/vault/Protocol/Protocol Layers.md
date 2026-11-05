---
title: Protocol Layers
section: Protocol
status: published
hook: How is rapp/1 split into layers, and what may each layer do?
source: "SPEC.md §1.1"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Protocol Layers

rapp/1 is organized as **five layers**, stacked like a network protocol.
Each layer has **exactly one canonical form**.
A higher layer **must not** redefine a lower one.

## The stack

From the specification, verbatim:

```
  L5  EGG        cartridge packaging (§9)          — MIME-multipart analogue
  L4  FRAME      universal event envelope (§7)     — the IP packet of RAPP
  L3  WIRE       transport: /chat + frames (§8)    — HTTP-analogue single method
  L2  IDENTITY   rappid namespace + trust (§6,§10) — URI + PKI analogue
  L1  ADDRESS    canonicalization + hash (§4,§5)   — the git object model
```

## Each layer in one line

- **L1 Address** — turn a value into one exact byte string, then hash it in a tagged space.
  See [[Canonicalization]] and [[Content Addressing]].
- **L2 Identity** — name things with a **rappid**, and prove authorship with signatures.
  See [[Identity and the Rappid]] and [[Trust and Signatures]].
- **L3 Wire** — move data: synchronous `POST /chat`, or an asynchronous append-only frame.
  See [[The Wire]].
- **L4 Frame** — the one universal event envelope, with exactly eleven keys.
  See [[The Frame]].
- **L5 Egg** — package a cartridge for transport and install.
  See [[The Egg]].

## The two rules that hold the stack together

1. **No redefinition downward.** A frame cannot invent its own hashing. An egg cannot invent its own identity.
   Each layer uses the one form the layer below defines.
2. **One canonical form per layer.** There is one byte form, one hash rule, one identity grammar,
   one envelope, one wire, one package format.

## Why this matters in practice

- Two implementations that agree on L1 compute the **same hash** for the same value.
- Because frames reuse L1, they can be checked by anyone with the bytes.
- Because the wire is one shape, a local Brainstem, a cloud endpoint and a managed studio all speak the same contract.
  See [[The Brainstem Kernel]].
- New capability is a new agent or a new registered `kind` — never a new layer, endpoint or envelope.

## How the layers relate to change

Changes are governed by [[Versioning and Evolution]].
A revision that changes the frame's key set, a field grammar or a hash rule must change the `spec` token.
Adding new registered `kind`s keeps the token.

## Related

- [[Protocol at a Glance]]
- [[Content Addressing]]
- [[The Frame]]
- [[The Wire]]
- [[The Egg]]
- [[Versioning and Evolution]]
