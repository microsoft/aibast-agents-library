---
title: Conformance and Drift
section: Building
status: published
hook: How do you prove an implementation conforms to rapp/1, and how do you find and fix drift in real artifacts?
source: "book/10-conformance-and-drift.md §10.1-§10.9; SPEC.md §11; rapp/KERNEL-DRIFT.md; docs/GRAIL-SPECIES.md"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Conformance and Drift

**Conformance** means an implementation passes fixed protocol tests.
**Drift** means real, published artifacts no longer match the current rules.
You need two separate checks: stable controlled vectors, and a fresh audit of what is actually published.

## The answer in brief

- **Controlled vectors** hold the implementation still. They never depend on remote state.
- A **real-world harness** reads current artifacts and reports clean, drift, or not inspected.
- A red report describes work to do. Fix the artifacts, never teach the checker to accept old forms.
- Fail closed: "could not look" is never "no drift".

## Controlled vectors

The upstream reference suite runs with:

```bash
python3 conformance.py
```

At the pinned commit it reports 23 controlled checks. (The book's figure of 22 predates V11.) They map to earlier rules:

- V1/V1b — [[Canonicalization]];
- V2 — domain separation in [[Content Addressing]];
- V3 — mint-once [[Identity and the Rappid|identity]];
- V4–V9 — building and verifying [[The Frame|frames]];
- V10 — the sealed-artifact profile;
- V11 — rev-17 regression suites (errata E-1..E-23).

Green here is not a generic clean build. It is a set of protocol claims exercised against fixed inputs.
A controlled suite must not start failing just because someone migrated a public repository.

## The real-world harness

A separate harness refreshes the live repositories and walks every frame and identity record. For each frame chain it asks:

1. Does the reference canonicalizer reproduce the stored address?
2. Does each `prev` link equal the previous payload address?
3. Does the full envelope pass `verify_frame` against its real head and stream?

Refreshing is part of the test. A report from a stale cache is a snapshot pretending to be live.

## A worked case: from eight drifts to zero

The first audit found 32 historical frames whose canonical bytes the reference reproduced exactly, but whose envelopes failed at step 1.

| Historical field | Current field |
|---|---|
| `twin_id` | `stream_id` |
| `ts` | `utc` |
| `sha256` | `payload_hash` |
| `parent_sha` | `prev` |
| absent | `frame_hash` |
| absent | `prev_wave` |

It also found short provisional identity tails and old schema labels: eight drifts in total.
After owner-authorized re-anchoring and migration, the audit reported 46 of 46 current envelopes accepted and zero drift.
It went green because the artifacts changed, not because the verifier learned to read the old form.

## Reading a red report

| Failure | Correct response |
|---|---|
| canonical bytes differ | replace the canonicalizer; regenerate unpublished output |
| same bytes, wrong domain-tagged hash | migrate through the current producer; do not alias hashes |
| rappid grammar or tail fails | owner-authorized re-anchor |
| frame step 1/1a fails | reject; re-genesis if committed history is immutable |
| frame step 2/3 fails | reject as corruption or tampering |
| frame step 4/5 fails | surface fork or drift; never reparent automatically |
| frame step 6 fails | refresh registry, then reject if still invalid |
| egg integrity/viability fails | reject the whole egg |

The rule is **reject first, migrate deliberately**. See [[Failure Atlas]].

## From finding to convergence

1. Capture the failing artifacts and exact checker output.
2. Classify every mismatch by normative section.
3. Identify the current owner and authority record.
4. Generate conformant artifacts without changing published addressed bytes.
5. Re-anchor identity or re-genesis history when authorized.
6. Update the append-only [[The Registry|registry]].
7. Rerun both the controlled suite and the live harness.
8. Retire old live forms, keeping only sealed history where required.

## Drift in this library

The same discipline governs how this library ships the Brainstem kernel.
`tests/test_grail_species.py` is the hard gate: it fails CI if the shipped kernel breaks the pinned Grail shape.
`rapp/KERNEL-DRIFT.md` is the explanation: every file that differs from the pinned commit is listed with a reason and a disposition, and a check fails when one is missing.
In release pipelines, the upstream specification makes `kernel-drift` a release-blocking finding (see [[RAPP CICD]]).

## Related

- [[Implementing the Protocol]]
- [[Conformance Classes]]
- [[Failure Atlas]]
- [[Distros and Pinning]]
- [[Versioning and Evolution]]
- [[Sources and Provenance]]
