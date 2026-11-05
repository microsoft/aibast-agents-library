---
title: RAPP CICD
section: Operations
status: published
hook: How does one exact AI release candidate earn promotion toward production under rapp/1?
source: "protocols/rapp-cicd/1/SPEC.md §1-§9; SPEC.md §11.1-§11.2"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# RAPP CICD

**RAPP CI/CD** (`rapp-cicd/1`) is the rule set for moving one release from development to production.
It makes "production ready" a checkable statement about **one exact candidate**.
Change any byte, prompt, model or policy, and it is a new release that must qualify again.

## The answer in brief

- A release is described once, in a **release capsule**, before testing starts.
- A **policy** lists the stages in order and the checks each stage needs.
- Each stage produces **evidence** about that exact candidate.
- A **promotion** decision moves it one stage forward, holds it, or rejects it.
- Approval never repairs failed evidence. An owner can stop a passing candidate, but cannot promote a failing one.

The profile does not prescribe GitHub Actions, a cloud provider, a branch model, or ring names.

## Foundation

RAPP CI/CD sits under rapp/1. An implementation must:

- use rapp/1 canonical I-JSON for every payload (see [[Canonicalization]]);
- identify each payload by `H("rapp/1:particle", payload)` (see [[Content Addressing]]);
- carry authoritative payloads in a signed rapp/1 frame (see [[The Frame]] and [[Trust and Signatures]]);
- add no transport endpoint beside `POST /chat` (see [[The Wire]]);
- resolve `release_scope` and the Grail binding from authenticated, owner-controlled policy.

A local unsigned file is a draft, fixture, or cache. It cannot authorize promotion.

## The four payloads

| schema | purpose |
|---|---|
| `rapp-cicd/1-release` | immutable identity of one release candidate |
| `rapp-cicd/1-policy` | ordered promotion path and required evidence |
| `rapp-cicd/1-evidence` | result of one stage against that exact candidate |
| `rapp-cicd/1-promotion` | explicit decision to advance, hold, or reject |

All four are closed. Unknown keys and missing keys are refused.

## The release capsule

The capsule binds source commit and tree, the exact artifact, the runtime entry point, and the Grail kernel.
It must contain exactly one immutable `kernel` component whose digest equals `grail.sha256`.
It must list every behavior-affecting agent, adapter, model, policy, configuration, state schema, tool, and knowledge source.

`lineage.mode` is `seed`, `offspring`, or `cross`.
Naming parents is informational only; the new release inherits no authority from them.

Example from the specification:

```json
{
  "schema": "rapp-cicd/1-release",
  "release_scope": "https://example.com/releases/product",
  "created_utc": "2026-08-30T12:54:20.000Z",
  "source": {
    "repository": "https://github.com/example/product",
    "object_format": "sha1",
    "commit": "0123456789012345678901234567890123456789",
    "tree": "abcdefabcdefabcdefabcdefabcdefabcdefabcd"
  },
  "artifact": {
    "sha256": "<64 lowercase hex>",
    "size_bytes": 1234,
    "media_type": "application/zip",
    "entrypoint": "src/main.py"
  },
  "grail": {
    "grail_id": "grail:<64 lowercase hex>",
    "path": "rapp_brainstem/brainstem.py",
    "sha256": "<64 lowercase hex>",
    "size_bytes": 154059
  },
  "components": [
    {
      "kind": "kernel",
      "name": "grail-brainstem",
      "version": "v0.6.16",
      "sha256": "<same digest as grail.sha256>",
      "mutable": false
    }
  ],
  "lineage": {
    "mode": "seed",
    "parents": []
  }
}
```

The capsule's Grail fields must equal the activated `grail-kernel` entry from a trusted registry verifier (see [[The Registry]]).
Comparing them only against other candidate-supplied fields is circular and nonconformant.

## The promotion path

Stages follow one order of semantic classes:

`development -> test -> canary -> qualification+ -> preprod -> production`

`qualification` may repeat. Every other class appears exactly once.
Each stage declares `required_checks`, `minimum_soak_seconds`, `maximum_evidence_age_seconds`, and `approval` (`automatic` or `owner`).

- **Canary** must include `grail-kernel`, `product`, `autonomous`, and `security-smoke`.
- **Preprod** must include fourteen checks, among them `exact-candidate`, `security`, `privacy`, `tenant-isolation`, `rollback-rehearsal`, and `restore-rehearsal`, and must have a non-zero soak.
- **Production** must require owner approval.

Preprod is a gate, not a ring. It rebuilds the exact candidate in a production-shaped environment and accepts no patches.

## Evidence and promotion rules

Evidence forms a hash-linked chain that follows the policy.
A missing predecessor, skipped or reordered stage, stale candidate, changed artifact, or changed Grail is a refusal.

- Evidence must come from a **trusted evaluator** outside the candidate's control.
- Secrets, credentials, and raw customer content must not appear in evidence; store a digest or access-controlled reference.
- An unavailable check counts as failed, never as skipped-success.

A `promote` decision is valid only for the next stage, with passing, fresh evidence, a complete evidence prefix, and an authorized signer.

## Release-blocking findings

`kernel-drift`, `artifact-drift`, `policy-drift`, `environment-drift`, `stage-skip`, `missing-evidence`, `failed-check`, `stale-evidence`, `untrusted-evaluator`, `state-incompatible`, `rollback-unproven`, `restore-unproven`.

A red gate is a finding. Bypassing it, muting it, or retrying until green without keeping the failures is nonconformant.

## Conformance

Payload validators prove shape and hashes but grant no authority.
`authorize_promotion_frame` additionally verifies the frame, signature, Grail binding, and signer.
A claim of RAPP CI/CD conformance includes passing `python3 operations_conformance.py`.
A claim of **RAPP production conformance** needs both this profile and [[RAPP Deploy]] (see [[Conformance Classes]]).

## Related

- [[RAPP Deploy]]
- [[RAPP Work]]
- [[Distros and Pinning]]
- [[Conformance and Drift]]
- [[Step 13 Production Deployment]]
- [[Sources and Provenance]]
