---
title: Conformance Classes
section: Protocol
status: published
hook: What does an implementation have to do to claim it conforms to rapp/1, and what extra rules apply to the Grail kernel and production operations?
source: SPEC.md §11; book/10-conformance-and-drift.md; book/A-reference-manual.md §A.8
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# Conformance Classes

A **conformance class** is a named role an implementation can claim: **Producer**, **Consumer**, or **Router/Mirror**.
Each role has a fixed list of duties. Claiming a role means doing all of them, with no legacy forms and no silent repairs.
Two extra rule sets cover the pinned Grail kernel and production operations.

## The three classes

**Producer** emits only:

- §4 canonical JSON bytes (see [[Canonicalization]]);
- §5 domain-separated full SHA-256 addresses (see [[Content Addressing]]);
- rappids minted per §6.2 (see [[Identity and the Rappid]]);
- eleven-key frames (see [[The Frame]]);
- `rapp/1-egg` variants (see [[The Egg]]);
- and **no legacy form**.

**Consumer**:

- runs the full §7.5 frame checklist, including step 1a stream binding;
- runs §9.3 egg verification;
- runs §10 signature, key-discovery, and tombstone checks (see [[Trust and Signatures]]);
- canonicalizes legacy ids on read;
- refuses on any failure, and never repairs, reparents, or rolls back.

**Router/Mirror**:

- invents no endpoints beyond the [[The Wire|wire]];
- declares that the upstream RAPP/1 specification governs protocol semantics;
- serves only provenance-stamped, hash-matching mirrors.

## The Grail kernel pin (§11.1)

An estate declares its Grail kernel through one `grail-kernel` registry entry. See [[The Registry]] and [[The Brainstem Kernel]].

- The Grail is identified by `grail_id`, never by a branch, tag, repository name, or product label.
- Every ring and stage — development, qualification, Preprod, installation, production — compares the candidate's Grail bytes to the pinned SHA-256 and length.
- A missing, changed, substituted, or unmeasured Grail byte is `kernel-drift` and **must** fail closed. Approval or urgency cannot waive it.
- A pipeline **must not** test a different file and then restore the pinned file. The release-shaped artifact itself must pass the gates.
- New behavior **must** live outside the Grail kernel. If it cannot, the implementation reports an incompatibility. It never edits the Grail and keeps the same identity.
- Different kernel bytes are a different Grail, with a new `grail_id`. A successor may name a `predecessor` but never overwrites the old one.
- Once activated, the full canonical entry is persisted. Later removal or mutation is a permanent `kernel-drift` refusal.

This is why downstream work pins the kernel and builds around it. See [[Distros and Pinning]].

## Operational conformance profiles (§11.2)

rapp/1 is the **substrate**. Two **operational profiles** sit on top of it.
They say how a production AI changes without changing the substrate or the serving system under users.
They are rapp/1 **applications**, not new wire versions.

- **RAPP CI/CD** (`rapp-cicd/1`, `protocols/rapp-cicd/1/SPEC.md`) — immutable release capsules, ordered qualification evidence, exact-candidate promotion, Preprod, and rollback/restore proof. See [[RAPP CICD]].
- **RAPP Deploy** (`rapp-deploy/1`, `protocols/rapp-deploy/1/SPEC.md`) — isolated serving/candidate lineages, cellular rollout, progressive exposure, expiring AI-health evidence, quarantine, and exact rollback. See [[RAPP Deploy]].

§11.2 names only these two. [[RAPP Work]] (`rapp-work/1`) is a separate operations note that binds a work organization to its catalog, releases, and rollback targets.

Rules that bind both profiles:

1. Payloads **MUST** be §4 canonical I-JSON, identified by `H("rapp/1:particle", payload)`.
2. Authoritative payloads **MUST** travel in signed rapp/1 frames using a registered compatible kind. Local unsigned files are drafts, fixtures, or caches and cannot authorize promotion or traffic.
3. They **MUST NOT** add a transport endpoint beside §8 `POST /chat`, redefine any rapp/1 primitive, or weaken §11.1.
4. An estate activates a profile through an authenticated §13.3 `protocol` registry entry pinning exact repository, path, and SHA-256. A moving branch is discovery, never authority.
5. A claim of **RAPP production conformance** requires both profiles. Core Producer, Consumer, and Router/Mirror implementations stay conformant without them.
6. Fixed envelope keys carry the safety invariants. Policy-defined check identifiers, component kinds, health objectives, and resilience controls are extension points; adding one changes neither the profile token nor the rapp/1 wire.
7. A consumer **MUST** refuse unknown **required** policy semantics. It may preserve and relay unknown optional evidence, but never count it as meeting a requirement it does not implement.

The reference validators are `rapp_cicd.py` and `rapp_deploy.py`; controlled profile vectors are in `operations_conformance.py`. JSON Schemas define structure; the validators enforce ordering, identity, temporal, and cross-document rules a schema cannot express.

## Proving it: the controlled suite

`conformance.py` is the executable form of the core rules:

```bash
python3 conformance.py
```

It ends with a line like:

```text
  ── 23 controlled checks | 23 PASS | 0 FAIL
```

- V1/V1b: canonicalization. V2: domain separation. V3: mint-once identity.
- V4–V9: frame build and verification steps, including unsigned swarm refusal.
- V10: the sealed-artifact profile.
- V11: the rev-17 regression suites (erratum `E-1`..`E-23`).

The suite uses **fixed inputs**. A live public observation follows it, but is non-gating. Mutable remote state belongs to the estate audit (`realcheck.py`). See [[Conformance and Drift]].

Passing the small vectors proves the byte primitives. It does **not** waive the full trust checks a Consumer owes.

## Fail closed

A checker must tell apart **clean**, **drift**, and **not inspected**. A checker that greens because it could not reach a repository has said "no drift" when it means "I did not look."

## Related

- [[Implementing the Protocol]]
- [[Conformance and Drift]]
- [[The Brainstem Kernel]]
- [[RAPP CICD]]
- [[RAPP Deploy]]
- [[RAPP Work]]
- [[Failure Atlas]]
