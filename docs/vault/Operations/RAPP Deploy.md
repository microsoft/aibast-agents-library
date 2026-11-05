---
title: RAPP Deploy
section: Operations
status: published
hook: How does a qualified rapp/1 release reach users safely and stay provably healthy afterward?
source: "protocols/rapp-deploy/1/SPEC.md §1-§11; SPEC.md §11.2"
upstream_commit: 0b24e7d60786d39d97265338add9ca784bf5a7ab
---

# RAPP Deploy

**RAPP Deploy** (`rapp-deploy/1`) is the rule set for giving a qualified release real user traffic.
Traffic grows in small, observed steps across isolated **cells**.
Health must be proven again and again, not once. Any doubt means hold, roll back, or quarantine.

## The answer in brief

- The unit of change is one immutable [[RAPP CICD]] release.
- The unit of safety is one isolated **deployment cell**.
- Exposure grows in **waves**, from zero-traffic shadow to global.
- Health evidence **expires**. Expired evidence cannot authorize more rollout.
- Rollback targets an **exact release hash**, never a mutable tag.

## Foundation

RAPP Deploy inherits every rapp/1 and RAPP CI/CD refusal. It adds no endpoint.
It defines three closed payloads:

| schema | purpose |
|---|---|
| `rapp-deploy/1-plan` | topology, waves, health budgets, state, data, and recovery |
| `rapp-deploy/1-health` | one candidate-bound observation window in one cell |
| `rapp-deploy/1-decision` | advance, complete, hold, rollback, or quarantine |

Authoritative payloads travel in signed rapp/1 frames (see [[The Frame]] and [[Trust and Signatures]]).
An authorized plan binds a signed, fresh promotion to Production, the full evidence prefix, the authenticated Grail declaration, and a previously authorized rollback release.

## Serving and candidate lineages

Two lineages stay separate:

- **serving lineage** — the immutable release users talk to now;
- **candidate lineage** — an isolated release under qualification or progressive exposure.

`candidate_isolated` must be true and `in_place_mutation` must be false.
The running service may append user state. It may not rewrite its code, model selection, agents, prompts, tools, policies, or schemas under an existing release identity.

## Cells and topology

Every plan uses `topology.mode: "cellular"`.

| class | minimum topology |
|---|---|
| `single-cell` | one cell |
| `multi-cell` | two cells in two failure domains |
| `planetary` | three cells, two regions, three failure domains |

A planetary deployment must be able to stop routing to one cell without stopping healthy cells.

## Waves

Traffic is counted in integer basis points.

- Start with `shadow` at zero user traffic.
- Increase strictly; never remove an exposed cell.
- End with `global` at 10,000 basis points across every cell.
- Planetary plans add `canary` (at most 100) and `regional` (at most 5,000).

Each wave sets a minimum observation time and a minimum number of healthy windows per cell.

## The health contract

The plan lists integer objectives, each with unit, comparison, and threshold. The minimum set covers:

- availability, error rate, p95 latency;
- quality score, safety violations, tool success;
- resource saturation, knowledge age, cost per request.

The core also requires exact artifact identity, exact Grail identity, state integrity, model identity, behavioral-baseline compatibility, and tool-contract compatibility.

The verdict is derived. An observation cannot label itself healthy when a budget failed.
A model provider, tool, or knowledge source can change without a commit, so health evidence expires after `max_evidence_age_seconds`.

## State, data, and resilience

- State uses `none`, `expand-contract`, or `dual-read-write`, and must stay backward compatible during rollout.
- Any migration needs a content-addressed rollback snapshot.
- Acknowledged user work must not be lost by rollback. If that cannot be proven, rollout is refused.
- Tenant isolation is mandatory. Raw prompts, memories, credentials, and regulated data are not deployment evidence.
- Every deployment needs circuit breakers, rate limits, load shedding, an independent kill switch, automatic pause, and automatic rollback.
- Provider failure is `fail-closed` or `degrade-explicitly`. A silent, success-shaped fallback is forbidden.

## Decisions

A decision is `advance`, `complete`, `hold`, `rollback`, or `quarantine`.
Decisions form their own hash chain; health windows form a per-cell chain that cannot overlap or restart.
A decision that cites any unhealthy or stale observation can never authorize `advance` or `complete`.

## Health after launch

Production is a continuously renewed health claim. Implementations must keep emitting health windows, requalify when evidence expires, rehearse rollback, restore, failover, and capacity, enforce error budgets, and retire releases only through explicit migration.

## Conformance

`validate_plan_payload`, `validate_health`, and `validate_decision` prove content relationships.
`authorize_plan_frame` and `authorize_decision_frame` add signatures and signer authority.
Conformance includes passing `python3 operations_conformance.py`.
Claim `planetary` only when every planetary requirement is proven by current evidence.

## Related

- [[RAPP CICD]]
- [[RAPP Work]]
- [[Step 13 Production Deployment]]
- [[Step 14 Post-Deployment Review]]
- [[Security Considerations]]
- [[Sources and Provenance]]
