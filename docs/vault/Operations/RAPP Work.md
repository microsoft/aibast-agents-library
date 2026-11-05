---
title: RAPP Work
section: Operations
status: published
hook: How does rapp/1 bind a work organization to its catalog, releases, migrations, and rollback targets without granting hidden authority?
source: "protocols/rapp-work/1/SPEC.md §1-§10"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# RAPP Work

**RAPP Work** (`rapp-work/1`) is the rule set for running a work organization on rapp/1.
It records what the organization advertises, which releases it trusts, how workspaces move, and what it rolls back to.
It is purely additive: it changes no rapp/1 byte, hash, signature, egg, or endpoint.

## The answer in brief

- A **catalog** says what exists. It never grants permission to run it.
- A **migration** always creates a new target. It never upgrades in place.
- A **rollback target** is an exact, already authorized release.
- Every authoritative record is **signed**, even where base rapp/1 would allow an unsigned frame.
- Observations are **bounded** to 128 and never silently deleted.

## Foundation and registration

Every authoritative RAPP Work payload is canonical I-JSON, identified by `H("rapp/1:particle", payload)`, carried in the eleven-key frame (see [[The Frame]]), signed, and appended to the organization's body stream.

An adopting estate appends one `protocol` entry pinning this specification, plus seven `kind` entries in [[The Registry]]:

| Kind | Only permitted payload schema |
| --- | --- |
| `work.organization` | `rapp-work/1-organization` |
| `work.catalog` | `rapp-work/1-catalog` |
| `work.vector` | `rapp-work/1-vector` |
| `work.migration` | `rapp-work/1-migration` |
| `work.receipt` | `rapp-work/1-receipt` |
| `work.observation` | `rapp-work/1-observation` |
| `work.rollback` | `rapp-work/1-rollback` |

The set is closed. The registry also pins `rapp-hive/1`, [[RAPP CICD|rapp-cicd/1]], and [[RAPP Deploy|rapp-deploy/1]].

## The organization

`rapp-work/1-organization` is the first record of a work body stream. It binds `organization_rappid`, `owner_rappid`, one `world_id`, one `hive_rappid`, the `release_scope`, an exact `policy_sha256`, and `created_utc`.

A name, repository, URL, or local path cannot derive or replace these identities (see [[Identity and the Rappid]]).

## Catalogs are discovery, not authority

A catalog is an append-only list of up to 256 items. Each item has a `kind` (`plugin`, `skill`, `static-api`, or `portable-neuron`), a typed rapp/1 address, a locator, and `authority:"discovery-only"`.

Signing a catalog proves what was advertised. It does not grant execution, installation, tool, network, or publication rights.
Portable Neurons are accepted only as inert data, never as instructions.

## The Hive vector

`rapp-work/1-vector` records which authenticated Hive state the organization accepted:

```json
{
  "registry_seq": 8,
  "registry_hash": "<64 lowercase hex>",
  "hive_rappid": "<RAPPID>",
  "mother_head_frame_hash": "<64 lowercase hex>",
  "catalog_hash": "<64 lowercase hex>"
}
```

Consumers keep the accepted vector as a **high-water mark**:

- a lower sequence is rollback;
- different hashes at the same sequence are a fork;
- resetting retained state is not recovery.

Git ancestry, a newer timestamp, or a moving branch cannot substitute for this check.

## Rollback targets

`rapp-work/1-rollback` binds one authorized [[RAPP CICD]] release by its particle hash, artifact SHA-256, Grail id, state-schema SHA-256, source snapshot, restore evidence, and an immutable Git descriptor.
The hashes are the authority; the Git descriptor is only a locator.
A branch, moving tag, or `main` raw URL is refused as a rollback target.

## Create-only migration

`rapp-work/1-migration` records an immutable intent with `mode:"create-only"`.
It binds the source workspace and snapshot, a fresh target workspace, the target release, the accepted vector, selected catalog items, and the rollback record.

- The migration id is a particle hash of the organization, source, target, and target release.
- Exact replay is idempotent. A second, different payload under the same id is refused.
- Old keys, private history, prompts, and unlisted state are not imported.

## Receipts and recovery

Receipts are `migration-completed`, `catalog-verified`, or `release-verified`, and are always signed.
Before any mutation, recovery checks that the intent is unchanged, the receipt and signer are authorized, all evidence verifies, the source is unchanged, bindings are exact, and the target key is in verified custody.
Nothing may be regenerated to make a check pass.

## Observations

A `rapp-work/1-observation` binds one release, one deploy plan, the accepted vector, evidence, and a verdict.
A `healthy` verdict requires authorized [[RAPP Deploy]] health evidence.
The reference profile keeps at most 128 observations; at the bound a new one is refused, never overwritten.

## Conformance

Conformance covers the seven schemas, signed registry kinds, high-water persistence, create-only migration, custody preflight, inert discovery data, and the observation bound, and includes passing `python3 work_conformance.py`.
JSON Schema, a Git commit, a raw URL, or an unsigned receipt is never authority.

## Related

- [[RAPP CICD]]
- [[RAPP Deploy]]
- [[The Registry]]
- [[Trust and Signatures]]
- [[Security Considerations]]
- [[Sources and Provenance]]
